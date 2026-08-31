"""Natal Decode cache refresh (1.3.124).

GET never rebuilds. Client force_refresh is ignored.
Ops one-shot: generate_natal_decode_depth_v0(ops_force=True).

Default is inventory. Pass --apply to rebuild named users.
Runs inside the API container (NullPool) so ops does not starve requests.
"""
from __future__ import annotations

import argparse
import json
from time import perf_counter

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from todayflow_backend.core.config import settings
from todayflow_backend.db import models
from todayflow_backend.services.core_profile import get_core_profile_service
from todayflow_backend.services.natal_decode_depth_v0 import (
    DECODE_VERSION,
    generate_natal_decode_depth_v0,
    list_latest_natal_decode_by_user,
)


def _ops_sessionmaker():
    eng = create_engine(settings.database_url, poolclass=NullPool, future=True, echo=False)
    return sessionmaker(bind=eng, expire_on_commit=False, autoflush=False), eng


def _parse_user_ids(raw: str | None) -> list[int]:
    if not raw:
        return []
    out: list[int] = []
    for part in raw.split(","):
        part = part.strip()
        if not part:
            continue
        out.append(int(part))
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Inventory / refresh natal decode cache to live fingerprint")
    parser.add_argument("--apply", action="store_true", help="Rebuild named users (default: list only)")
    parser.add_argument("--user-ids", default="", help="Comma-separated user ids to refresh")
    parser.add_argument("--stale-limit", type=int, default=0, help="If no --user-ids, refresh first N stale users")
    parser.add_argument("--locale", default="ru")
    args = parser.parse_args()

    Session, eng = _ops_sessionmaker()
    db = Session()
    try:
        inventory = list_latest_natal_decode_by_user(db)
        print(
            json.dumps(
                {
                    "target_version": DECODE_VERSION,
                    "users": len(inventory),
                    "stale": sum(1 for row in inventory if row["state"] == "stale"),
                    "current": sum(1 for row in inventory if row["state"] == "current"),
                    "invalid": sum(1 for row in inventory if row["state"] == "invalid"),
                    "rows": inventory,
                },
                ensure_ascii=False,
            ),
            flush=True,
        )
        if not args.apply:
            print("dry-run (pass --apply to rebuild)", flush=True)
            return

        wanted = _parse_user_ids(args.user_ids)
        if not wanted and args.stale_limit > 0:
            wanted = [int(row["user_id"]) for row in inventory if row["state"] == "stale"][
                : max(0, args.stale_limit)
            ]
        if not wanted:
            print("no user ids to refresh", flush=True)
            return

        before = {int(row["user_id"]): row for row in inventory}
        svc = get_core_profile_service()
        for uid in wanted:
            user = db.get(models.User, uid)
            if user is None:
                print(json.dumps({"user_id": uid, "ok": False, "error": "missing_user"}), flush=True)
                continue
            t0 = perf_counter()
            core = svc.build_cached_or_baseline(db, user)
            core_payload = core if isinstance(core, dict) else {}
            natal_summary = (
                core_payload.get("natal_summary")
                if isinstance(core_payload.get("natal_summary"), dict)
                else None
            )
            try:
                result = generate_natal_decode_depth_v0(
                    db,
                    user_id=int(uid),
                    core_profile_payload=core_payload,
                    natal_summary=natal_summary,
                    locale=args.locale,
                    ops_force=True,
                )
            except Exception as exc:
                db.rollback()
                print(
                    json.dumps(
                        {
                            "user_id": uid,
                            "ok": False,
                            "error": type(exc).__name__,
                            "msg": str(exc)[:240],
                            "elapsed_ms": int((perf_counter() - t0) * 1000),
                        },
                        ensure_ascii=False,
                    ),
                    flush=True,
                )
                continue
            prev = before.get(int(uid)) or {}
            identity = result.get("identity_core") if isinstance(result.get("identity_core"), dict) else {}
            print(
                json.dumps(
                    {
                        "user_id": uid,
                        "ok": str(result.get("status") or "") == "grounded",
                        "elapsed_ms": int((perf_counter() - t0) * 1000),
                        "before_version": prev.get("body_version"),
                        "after_version": result.get("version"),
                        "before_thesis": prev.get("thesis_key"),
                        "after_thesis": identity.get("thesis_key"),
                        "thesis_unchanged": str(prev.get("thesis_key") or "")
                        == str(identity.get("thesis_key") or ""),
                        "prompt_version": result.get("prompt_version"),
                        "status": result.get("status"),
                        "reason": result.get("reason"),
                        "access": result.get("access"),
                        "writes_character_engine": result.get("writes_character_engine"),
                        "sections": len(result.get("sections") or [])
                        if isinstance(result.get("sections"), list)
                        else 0,
                    },
                    ensure_ascii=False,
                ),
                flush=True,
            )
    finally:
        db.close()
        eng.dispose()


if __name__ == "__main__":
    main()

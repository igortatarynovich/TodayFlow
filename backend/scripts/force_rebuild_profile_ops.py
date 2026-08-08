"""Force-publish core profile (Character Engine LLM cascade) for primary accounts.

Runs as a second Python process inside the API container. Uses NullPool so ops
does not open a competing QueuePool (12+18) that starves interactive requests.
One short-lived session per user — never hold a connection across LLM waits.
"""
from __future__ import annotations

from time import perf_counter

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from todayflow_backend.core.config import settings
from todayflow_backend.db import models
from todayflow_backend.services.core_profile import get_core_profile_service

USER_IDS = [1, 2]


def _ops_sessionmaker():
    eng = create_engine(settings.database_url, poolclass=NullPool, future=True, echo=False)
    return sessionmaker(bind=eng, expire_on_commit=False, autoflush=False), eng


def main() -> None:
    Session, eng = _ops_sessionmaker()
    svc = get_core_profile_service()
    try:
        for uid in USER_IDS:
            db = Session()
            try:
                user = db.get(models.User, uid)
                if user is None:
                    print(f"user {uid}: MISSING", flush=True)
                    continue
                t0 = perf_counter()
                print(f"--- publish profile user={uid} email={user.email} ---", flush=True)
                try:
                    payload = svc.build(db, user, publish_portrait=True)
                except Exception as exc:
                    print(
                        {
                            "user_id": uid,
                            "ok": False,
                            "error": type(exc).__name__,
                            "msg": str(exc)[:300],
                            "elapsed_ms": int((perf_counter() - t0) * 1000),
                        },
                        flush=True,
                    )
                    db.rollback()
                    continue

                contract = payload.get("profile_contract_v1") if isinstance(payload, dict) else None
                ce = payload.get("character_engine_v1") if isinstance(payload, dict) else None
                gm = (contract or {}).get("generation_meta") if isinstance(contract, dict) else None
                steps = gm.get("steps") if isinstance(gm, dict) else None
                models_used: list[str] = []
                if isinstance(steps, list):
                    for step in steps:
                        if isinstance(step, dict) and step.get("model"):
                            models_used.append(str(step["model"]))
                identity = ""
                if isinstance(contract, dict):
                    ic = contract.get("identity_core")
                    if isinstance(ic, dict):
                        identity = str(ic.get("summary") or ic.get("logline") or "")[:160]
                    elif isinstance(ic, str):
                        identity = ic[:160]
                print(
                    {
                        "user_id": uid,
                        "ok": True,
                        "elapsed_ms": int((perf_counter() - t0) * 1000),
                        "profile_hash": (payload or {}).get("profile_hash"),
                        "contract_status": (contract or {}).get("status") if isinstance(contract, dict) else None,
                        "ce_status": (ce or {}).get("status") if isinstance(ce, dict) else None,
                        "models": models_used or None,
                        "identity_preview": identity,
                    },
                    flush=True,
                )
            finally:
                db.close()
    finally:
        eng.dispose()
    print("DONE", flush=True)


if __name__ == "__main__":
    main()

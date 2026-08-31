"""Delete production users that are not the two live testers.

Keeps:
  victoria.tatarynovich@gmail.com
  pakistandiller@gmail.com

Deletes everyone else (including RFC 2606 @example.com fixtures).
Ops cleanup for Cost Containment — not a semantic pass.
"""

from __future__ import annotations

import argparse
import json

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker

from todayflow_backend.core.config import settings

KEEP_EMAILS = (
    "victoria.tatarynovich@gmail.com",
    "pakistandiller@gmail.com",
)


def _keep_sql(keep_ids: list[int]) -> str:
    if not keep_ids:
        raise SystemExit("refusing: keep set empty")
    return ",".join(str(int(i)) for i in keep_ids)


def main() -> None:
    parser = argparse.ArgumentParser(description="Purge users except the two live testers")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    eng = create_engine(settings.database_url, future=True)
    Session = sessionmaker(bind=eng, expire_on_commit=False)
    db = Session()
    try:
        rows = db.execute(text("SELECT id, email, created_at FROM users ORDER BY id")).mappings().all()
        keep_ids = [int(r["id"]) for r in rows if str(r["email"] or "").strip().lower() in KEEP_EMAILS]
        drop = [dict(r) for r in rows if int(r["id"]) not in keep_ids]
        print(
            json.dumps(
                {
                    "keep_emails": list(KEEP_EMAILS),
                    "keep_ids": keep_ids,
                    "drop_count": len(drop),
                    "drop": [{"id": r["id"], "email": r["email"]} for r in drop],
                },
                ensure_ascii=False,
                default=str,
            ),
            flush=True,
        )
        if not args.apply:
            print("dry-run (pass --apply to delete)", flush=True)
            return
        keep = _keep_sql(keep_ids)
        # Grandchild rows have no user_id but FK to user-owned parents.
        db.execute(
            text(
                "DELETE FROM cached_natal_charts WHERE astro_profile_id IN "
                f"(SELECT id FROM astro_profiles WHERE user_id NOT IN ({keep}))"
            )
        )
        db.execute(
            text(
                "DELETE FROM subscription_history WHERE subscription_id IN "
                f"(SELECT id FROM subscriptions WHERE user_id NOT IN ({keep}))"
            )
        )
        db.execute(
            text(
                "DELETE FROM challenge_task_completions WHERE participant_id IN "
                f"(SELECT id FROM challenge_participants WHERE user_id NOT IN ({keep}))"
            )
        )
        db.flush()
        insp = inspect(eng)
        jobs: list[tuple[str, str]] = []
        for table_name in insp.get_table_names():
            if table_name == "users":
                continue
            for col in insp.get_columns(table_name):
                cname = str(col["name"])
                if cname in {"user_id", "claimed_user_id"}:
                    jobs.append((table_name, cname))
        pending = list(jobs)
        for _pass in range(10):
            if not pending:
                break
            leftover: list[tuple[str, str]] = []
            for table_name, col in pending:
                try:
                    db.execute(
                        text(
                            f"DELETE FROM {table_name} "
                            f"WHERE {col} IS NOT NULL AND {col} NOT IN ({keep})"
                        )
                    )
                    db.flush()
                except Exception as exc:
                    db.rollback()
                    leftover.append((table_name, col))
                    print(f"retry later {table_name}.{col}: {exc}", flush=True)
            pending = leftover
        if pending:
            raise SystemExit(f"could not clear child tables: {pending}")
        db.execute(text(f"DELETE FROM users WHERE id NOT IN ({keep})"))
        db.commit()
        left = db.execute(text("SELECT id, email FROM users ORDER BY id")).mappings().all()
        print(json.dumps({"remaining": [dict(r) for r in left]}, ensure_ascii=False), flush=True)
    finally:
        db.close()
        eng.dispose()


if __name__ == "__main__":
    main()

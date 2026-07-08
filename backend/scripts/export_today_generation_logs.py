#!/usr/bin/env python3
"""Export Today-related generation_logs to JSONL for TL-0A corpus (raw only, no quality scoring).

Usage:
  DATABASE_URL=postgresql+psycopg://... PYTHONPATH=backend/src \\
    backend/.venv/bin/python backend/scripts/export_today_generation_logs.py \\
    --out docs/datasets/raw/generation_logs_ru_v0.jsonl

Dry-run (summary only, no file):
  ... export_today_generation_logs.py --dry-run

Incremental / sample:
  ... export_today_generation_logs.py --since 2026-06-01
  ... export_today_generation_logs.py --sample 100 --dry-run

Then merge into corpus:
  PYTHONPATH=backend/src backend/.venv/bin/python backend/scripts/today_language_corpus_v0.py \\
    --logs-dir docs/datasets/raw
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from collections import Counter
from dataclasses import dataclass, field
from datetime import date, datetime, time
from decimal import Decimal
from pathlib import Path
from typing import Any, Iterator
from uuid import UUID

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Engine

_REPO_ROOT = Path(__file__).resolve().parents[2]

_PREFERRED_COLUMNS: tuple[str, ...] = (
    "id",
    "created_at",
    "user_id",
    "module",
    "surface",
    "kind",
    "flow",
    "source",
    "model",
    "locale",
    "status",
    "error_message",
    "used_fallback",
    "duration_ms",
    "input_payload",
    "output_payload",
    "normalized_response",
    "raw_response",
    "final_text",
    "narrative",
    "guide",
    "system_prompt",
    "user_prompt",
)

_TODAY_MODULE_PREFIXES = ("today",)
_TODAY_MODULE_EXACT = frozenset(
    {
        "today_narrative",
        "daily_recommendation",
        "daily_foundation",
        "forecast",
    }
)
_TODAY_SURFACES = frozenset(
    {
        "guide",
        "day_layer",
        "spheres",
        "evening",
        "deepen",
        "today_contract",
        "morning_ritual",
    }
)

_SUCCESS_STATUSES = frozenset({"success", "ok", "completed"})

_EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
_PHONE_RE = re.compile(r"(?<!\d)(?:\+?\d[\d\s\-()]{7,}\d)(?!\d)")
_CYRILLIC_RE = re.compile(r"[А-Яа-яЁё]")

_PII_KEY_RE = re.compile(
    r"(email|e_mail|phone|mobile|telegram|whatsapp|password|token|secret|"
    r"birth_?date|birthday|address|passport|inn|snils|first_?name|last_?name|"
    r"full_?name|display_?name|user_?name|nickname|login)",
    re.I,
)


@dataclass
class ExportStats:
    db_rows_read: int = 0
    skipped_status: int = 0
    skipped_not_today: int = 0
    skipped_not_ru: int = 0
    exported: int = 0
    scanned_ru: int = 0
    scanned_today: int = 0
    exported_ru: int = 0
    exported_today: int = 0
    exported_used_fallback: int = 0
    by_module: Counter[str] = field(default_factory=Counter)
    by_surface: Counter[str] = field(default_factory=Counter)
    exported_status: Counter[str] = field(default_factory=Counter)
    scanned_status: Counter[str] = field(default_factory=Counter)

    @property
    def skipped_total(self) -> int:
        return self.skipped_status + self.skipped_not_today + self.skipped_not_ru


def _load_database_url(explicit: str | None) -> str:
    url = (explicit or os.environ.get("DATABASE_URL") or "").strip()
    if url:
        return url
    env_file = _REPO_ROOT / "backend" / ".env"
    if env_file.is_file():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("DATABASE_URL="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    print("ERROR: DATABASE_URL is not set.", file=sys.stderr)
    sys.exit(1)


def _json_default(value: Any) -> Any:
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    raise TypeError(f"not JSON serializable: {type(value)!r}")


def _parse_json_value(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, (dict, list)):
        return value
    if isinstance(value, str):
        s = value.strip()
        if not s:
            return None
        try:
            return json.loads(s)
        except json.JSONDecodeError:
            return value
    return value


def _mask_string(s: str) -> str:
    out = _EMAIL_RE.sub("[email redacted]", s)
    out = _PHONE_RE.sub("[phone redacted]", out)
    return out


def _mask_pii(value: Any, *, key: str | None = None) -> Any:
    if key and _PII_KEY_RE.search(key):
        if isinstance(value, str):
            return "[redacted]"
        if value is not None:
            return "[redacted]"
    if isinstance(value, str):
        return _mask_string(value)
    if isinstance(value, list):
        return [_mask_pii(v) for v in value]
    if isinstance(value, dict):
        masked: dict[str, Any] = {}
        for k, v in value.items():
            if k in ("user_id",) and isinstance(v, int):
                masked[k] = _hash_user_id(v)
                continue
            masked[k] = _mask_pii(v, key=k)
        return masked
    return value


def _hash_user_id(user_id: int) -> str:
    digest = hashlib.sha256(f"user:{user_id}".encode()).hexdigest()[:12]
    return f"user_hash_{digest}"


def _available_columns(engine: Engine, table: str = "generation_logs") -> set[str]:
    try:
        insp = inspect(engine)
        if table not in insp.get_table_names():
            return set()
        return {c["name"] for c in insp.get_columns(table)}
    except Exception as exc:
        print(f"WARN: column introspection failed: {exc}", file=sys.stderr)
        return set()


def _select_columns(available: set[str]) -> list[str]:
    cols = [c for c in _PREFERRED_COLUMNS if c in available]
    if "id" not in cols and "id" in available:
        cols.insert(0, "id")
    if "created_at" not in cols and "created_at" in available:
        cols.append("created_at")
    if "module" not in cols and "module" in available:
        cols.append("module")
    return cols


def _is_today_row(row: dict[str, Any]) -> bool:
    module = str(row.get("module") or "").lower()
    surface = str(row.get("surface") or "").lower()
    if module in _TODAY_MODULE_EXACT or any(module.startswith(p) for p in _TODAY_MODULE_PREFIXES):
        return True
    return surface in _TODAY_SURFACES


def _row_has_ru_text(row: dict[str, Any]) -> bool:
    locale = str(row.get("locale") or "").lower()
    if locale.startswith("ru"):
        return True
    blob = json.dumps(row, ensure_ascii=False, default=_json_default)
    return bool(_CYRILLIC_RE.search(blob))


def _normalize_status(raw: Any) -> str:
    s = str(raw or "unknown").strip().lower() or "unknown"
    if s in _SUCCESS_STATUSES:
        return "success"
    if s in ("error", "failed", "failure"):
        return "failed"
    return s


def _is_success_status(raw: Any) -> bool:
    return _normalize_status(raw) == "success"


def _build_output_record(row: dict[str, Any], *, include_prompts: bool) -> dict[str, Any]:
    rec: dict[str, Any] = {
        "export_version": "0.1",
        "export_kind": "generation_log",
    }

    for key in (
        "id",
        "created_at",
        "module",
        "surface",
        "kind",
        "flow",
        "source",
        "model",
        "locale",
        "status",
        "error_message",
        "used_fallback",
        "duration_ms",
    ):
        if key in row and row[key] is not None:
            rec[key] = row[key]

    if "user_id" in row and row["user_id"] is not None:
        try:
            rec["user_id_hash"] = _hash_user_id(int(row["user_id"]))
        except (TypeError, ValueError):
            rec["user_id_hash"] = "[redacted]"

    normalized = _parse_json_value(row.get("normalized_response"))
    output_payload = _parse_json_value(row.get("output_payload"))
    if output_payload is None:
        output_payload = normalized

    if "input_payload" in row:
        rec["input_payload"] = _mask_pii(_parse_json_value(row.get("input_payload")))

    if output_payload is not None:
        rec["output_payload"] = _mask_pii(output_payload)
    if normalized is not None:
        rec["normalized_response"] = _mask_pii(normalized)

    for extra in ("final_text", "narrative", "guide"):
        if extra in row and row[extra] is not None:
            rec[extra] = _mask_pii(_parse_json_value(row.get(extra)))

    if row.get("raw_response") is not None:
        raw = str(row["raw_response"])
        if len(raw) > 12000:
            raw = raw[:12000] + "…[truncated]"
        rec["raw_response"] = _mask_string(raw)

    if include_prompts:
        for key in ("system_prompt", "user_prompt"):
            if key in row and row[key] is not None:
                val = str(row[key])
                if len(val) > 8000:
                    val = val[:8000] + "…[truncated]"
                rec[key] = _mask_string(val)

    return rec


def _parse_since(value: str) -> datetime:
    """Parse --since as YYYY-MM-DD (start of day) or ISO datetime."""
    raw = value.strip()
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", raw):
        d = date.fromisoformat(raw)
        return datetime.combine(d, time.min)
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00")).replace(tzinfo=None)
    except ValueError as exc:
        print(f"ERROR: invalid --since {value!r}; use YYYY-MM-DD or ISO datetime.", file=sys.stderr)
        sys.exit(1)


def _resolve_row_limit(sample: int | None, limit: int | None) -> int | None:
    if sample is not None and limit is not None:
        print("WARN: both --sample and --limit set; using --sample.", file=sys.stderr)
    if sample is not None:
        if sample < 1:
            print("ERROR: --sample must be >= 1.", file=sys.stderr)
            sys.exit(1)
        return sample
    return limit


def _fetch_rows(
    engine: Engine,
    *,
    row_limit: int | None,
    since: datetime | None,
    available: set[str],
) -> Iterator[dict[str, Any]]:
    cols = _select_columns(available)
    if not cols:
        print("ERROR: no exportable columns on generation_logs.", file=sys.stderr)
        sys.exit(1)

    for col in ("normalized_response", "input_payload", "module"):
        if col not in available:
            print(f"WARN: column generation_logs.{col} missing — continuing.", file=sys.stderr)

    select_sql = ", ".join(f'"{c}"' if engine.dialect.name == "postgresql" else c for c in cols)
    query = f"SELECT {select_sql} FROM generation_logs"
    clauses: list[str] = []
    params: dict[str, Any] = {}

    if since is not None:
        if "created_at" not in available:
            print("WARN: --since ignored; generation_logs.created_at column missing.", file=sys.stderr)
        else:
            clauses.append("created_at >= :since_ts")
            params["since_ts"] = since

    if clauses:
        query += " WHERE " + " AND ".join(clauses)

    if "created_at" in available:
        query += " ORDER BY created_at DESC"
    elif "id" in available:
        query += " ORDER BY id DESC"

    if row_limit is not None:
        query += " LIMIT :row_limit"
        params["row_limit"] = row_limit

    with engine.connect() as conn:
        result = conn.execute(text(query), params)
        keys = list(result.keys())
        for db_row in result:
            yield dict(zip(keys, db_row))


def _print_summary(
    stats: ExportStats,
    *,
    dry_run: bool,
    out_path: Path,
    filters: dict[str, Any],
) -> None:
    exported_success = stats.exported_status.get("success", 0)
    exported_failed = stats.exported_status.get("failed", 0)
    exported_other = stats.exported - exported_success - exported_failed

    scanned_success = stats.scanned_status.get("success", 0)
    scanned_failed = stats.scanned_status.get("failed", 0)
    scanned_other = stats.db_rows_read - scanned_success - scanned_failed

    lines = [
        "=== generation_logs export summary ===",
        f"mode: {'dry-run (no file written)' if dry_run else 'write'}",
        f"out: {out_path}",
        f"filters: {json.dumps(filters, ensure_ascii=False)}",
        "",
        f"db_rows_read:     {stats.db_rows_read}",
        f"exported:         {stats.exported}",
        f"skipped_total:    {stats.skipped_total}",
        f"  skipped_status:     {stats.skipped_status}",
        f"  skipped_not_today:  {stats.skipped_not_today}",
        f"  skipped_not_ru:     {stats.skipped_not_ru}",
        "",
        f"scanned_ru:       {stats.scanned_ru}",
        f"scanned_today:    {stats.scanned_today}",
        f"exported_ru:      {stats.exported_ru}",
        f"exported_today:   {stats.exported_today}",
        "",
        f"exported used_fallback=true: {stats.exported_used_fallback}",
        "",
        "exported status:",
        f"  success: {exported_success}",
        f"  failed:  {exported_failed}",
        f"  other:   {exported_other}",
        "",
        "scanned status (before export filters):",
        f"  success: {scanned_success}",
        f"  failed:  {scanned_failed}",
        f"  other:   {scanned_other}",
        "",
        "by module (exported):",
    ]
    if stats.by_module:
        for mod, count in stats.by_module.most_common():
            lines.append(f"  {mod}: {count}")
    else:
        lines.append("  (none)")

    lines.append("")
    lines.append("by surface (exported):")
    if stats.by_surface:
        for surface, count in stats.by_surface.most_common():
            lines.append(f"  {surface}: {count}")
    else:
        lines.append("  (none)")

    if stats.exported == 0:
        lines.append("")
        lines.append("hint: no rows exported — try --all-modules, --all-locales, or --include-failed")

    print("\n".join(lines), file=sys.stderr)


def export_logs(
    *,
    database_url: str,
    out_path: Path,
    row_limit: int | None,
    since: datetime | None,
    today_only: bool,
    ru_only: bool,
    status_ok_only: bool,
    include_prompts: bool,
    dry_run: bool,
) -> ExportStats:
    engine = create_engine(database_url)
    available = _available_columns(engine)
    if not available:
        print("ERROR: table generation_logs not found or has no readable columns.", file=sys.stderr)
        sys.exit(1)

    stats = ExportStats()
    handle = None if dry_run else out_path.open("w", encoding="utf-8")
    if not dry_run:
        out_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        for row in _fetch_rows(engine, row_limit=row_limit, since=since, available=available):
            stats.db_rows_read += 1

            status_bucket = _normalize_status(row.get("status"))
            stats.scanned_status[status_bucket] += 1

            if _row_has_ru_text(row):
                stats.scanned_ru += 1
            if _is_today_row(row):
                stats.scanned_today += 1

            if status_ok_only and not _is_success_status(row.get("status")):
                stats.skipped_status += 1
                continue

            if today_only and not _is_today_row(row):
                stats.skipped_not_today += 1
                continue

            if ru_only and not _row_has_ru_text(row):
                stats.skipped_not_ru += 1
                continue

            record = _build_output_record(row, include_prompts=include_prompts)
            if handle is not None:
                handle.write(json.dumps(record, ensure_ascii=False, default=_json_default) + "\n")

            stats.exported += 1
            if _row_has_ru_text(row):
                stats.exported_ru += 1
            if _is_today_row(row):
                stats.exported_today += 1

            mod = str(record.get("module") or "(none)")
            surface = str(record.get("surface") or "(none)")
            stats.by_module[mod] += 1
            stats.by_surface[surface] += 1

            exp_status = _normalize_status(record.get("status"))
            stats.exported_status[exp_status] += 1

            if record.get("used_fallback") is True:
                stats.exported_used_fallback += 1
    finally:
        if handle is not None:
            handle.close()

    return stats


def main() -> None:
    parser = argparse.ArgumentParser(description="Export generation_logs to JSONL (raw, PII-masked)")
    parser.add_argument(
        "--out",
        type=Path,
        default=_REPO_ROOT / "docs" / "datasets" / "raw" / "generation_logs_ru_v0.jsonl",
        help="Output JSONL path",
    )
    parser.add_argument("--database-url", default=None, help="Override DATABASE_URL env")
    parser.add_argument(
        "--since",
        default=None,
        metavar="DATE",
        help="Export rows with created_at >= DATE (YYYY-MM-DD or ISO datetime)",
    )
    parser.add_argument(
        "--sample",
        type=int,
        default=None,
        metavar="N",
        help="Newest N rows from DB (ORDER BY created_at DESC LIMIT N); deterministic, not random",
    )
    parser.add_argument("--limit", type=int, default=None, help="Alias for --sample (deprecated)")
    parser.add_argument("--dry-run", action="store_true", help="Summary only; do not write output file")
    parser.add_argument("--all-modules", action="store_true", help="Do not filter to Today modules/surfaces")
    parser.add_argument("--all-locales", action="store_true", help="Do not require ru locale or Cyrillic in payload")
    parser.add_argument("--include-failed", action="store_true", help="Include non-success status rows")
    parser.add_argument("--include-prompts", action="store_true", help="Include masked system_prompt/user_prompt")
    args = parser.parse_args()

    database_url = _load_database_url(args.database_url)
    since = _parse_since(args.since) if args.since else None
    row_limit = _resolve_row_limit(args.sample, args.limit)
    filters = {
        "today_only": not args.all_modules,
        "ru_only": not args.all_locales,
        "status_ok_only": not args.include_failed,
        "since": args.since,
        "sample": args.sample,
        "limit": args.limit,
        "row_limit": row_limit,
        "include_prompts": args.include_prompts,
    }

    stats = export_logs(
        database_url=database_url,
        out_path=args.out,
        row_limit=row_limit,
        since=since,
        today_only=not args.all_modules,
        ru_only=not args.all_locales,
        status_ok_only=not args.include_failed,
        include_prompts=args.include_prompts,
        dry_run=args.dry_run,
    )

    _print_summary(stats, dry_run=args.dry_run, out_path=args.out, filters=filters)

    if not args.dry_run:
        print(f"Wrote {stats.exported} rows → {args.out}", file=sys.stderr)


if __name__ == "__main__":
    main()

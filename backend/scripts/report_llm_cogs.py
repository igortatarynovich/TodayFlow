#!/usr/bin/env python3
"""Aggregate llm_usage_v1 events into AI COGS tables.

Primary views after 24h:
  1. feature × trigger × model × retry_reason
  2. top-20 operation_id by estimated cost

Reads JSONL or docker/backend log lines containing ``llm_usage_v1 {json}``.

Usage:
  PYTHONPATH=backend/src backend/.venv/bin/python backend/scripts/report_llm_cogs.py \\
    --jsonl /tmp/todayflow_llm_usage.jsonl

  docker compose -f docker-compose.prod.yml logs backend --since 24h \\
    | PYTHONPATH=backend/src backend/.venv/bin/python backend/scripts/report_llm_cogs.py --stdin
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


def _extract_event(line: str) -> dict[str, Any] | None:
    text = (line or "").strip()
    if not text:
        return None
    marker = "llm_usage_v1"
    if text.startswith("{"):
        try:
            obj = json.loads(text)
        except json.JSONDecodeError:
            return None
        return obj if obj.get("event") == marker else None
    idx = text.find(marker)
    if idx < 0:
        return None
    rest = text[idx + len(marker) :].strip()
    if not rest.startswith("{"):
        return None
    try:
        obj = json.loads(rest)
    except json.JSONDecodeError:
        return None
    return obj if isinstance(obj, dict) else None


def _load(path: Path | None, use_stdin: bool) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    if use_stdin:
        for line in sys.stdin:
            ev = _extract_event(line)
            if ev:
                events.append(ev)
        return events
    if path is None:
        return events
    if not path.is_file():
        print(f"no file: {path}", file=sys.stderr)
        return events
    for line in path.read_text(encoding="utf-8").splitlines():
        ev = _extract_event(line)
        if ev:
            events.append(ev)
    return events


def _blank(val: Any, fallback: str = "-") -> str:
    text = str(val or "").strip()
    return text if text else fallback


def _agg_matrix(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    buckets: dict[tuple[str, str, str, str], dict[str, Any]] = defaultdict(
        lambda: {
            "calls": 0,
            "ok": 0,
            "retries": 0,
            "input": 0,
            "output": 0,
            "reasoning": 0,
            "cached": 0,
            "cost": 0.0,
        }
    )
    for ev in events:
        key = (
            _blank(ev.get("feature"), "unlabeled"),
            _blank(ev.get("trigger"), "unknown"),
            _blank(ev.get("model"), "unknown"),
            _blank(ev.get("retry_reason"), "-"),
        )
        row = buckets[key]
        row["calls"] += 1
        if ev.get("ok"):
            row["ok"] += 1
        if ev.get("retry_reason") or int(ev.get("attempt") or 0) > 0:
            row["retries"] += 1
        row["input"] += int(ev.get("input_tokens") or 0)
        row["output"] += int(ev.get("output_tokens") or 0)
        row["reasoning"] += int(ev.get("reasoning_tokens") or 0)
        row["cached"] += int(ev.get("cached_tokens") or 0)
        row["cost"] += float(ev.get("estimated_cost_usd") or 0.0)
    out = []
    for (feature, trigger, model, retry_reason), row in buckets.items():
        out.append(
            {
                "feature": feature,
                "trigger": trigger,
                "model": model,
                "retry_reason": retry_reason,
                **row,
            }
        )
    out.sort(key=lambda r: r["cost"], reverse=True)
    return out


def _agg_operations(events: list[dict[str, Any]], *, limit: int = 20) -> list[dict[str, Any]]:
    buckets: dict[str, dict[str, Any]] = {}
    for ev in events:
        op_id = _blank(ev.get("operation_id"), "")
        if not op_id:
            continue
        row = buckets.get(op_id)
        if row is None:
            row = {
                "operation_id": op_id,
                "operation": _blank(ev.get("operation"), "-"),
                "trigger": _blank(ev.get("trigger"), "unknown"),
                "user_id": ev.get("user_id"),
                "calls": 0,
                "features": set(),
                "models": set(),
                "retry_reasons": set(),
                "input": 0,
                "output": 0,
                "reasoning": 0,
                "cost": 0.0,
            }
            buckets[op_id] = row
        row["calls"] += 1
        row["features"].add(_blank(ev.get("feature"), "unlabeled"))
        row["models"].add(_blank(ev.get("model"), "unknown"))
        if ev.get("retry_reason"):
            row["retry_reasons"].add(str(ev.get("retry_reason")))
        row["input"] += int(ev.get("input_tokens") or 0)
        row["output"] += int(ev.get("output_tokens") or 0)
        row["reasoning"] += int(ev.get("reasoning_tokens") or 0)
        row["cost"] += float(ev.get("estimated_cost_usd") or 0.0)
        if ev.get("operation"):
            row["operation"] = str(ev.get("operation"))
    out = []
    for row in buckets.values():
        out.append(
            {
                **{k: v for k, v in row.items() if k not in {"features", "models", "retry_reasons"}},
                "features": sorted(row["features"]),
                "models": sorted(row["models"]),
                "retry_reasons": sorted(row["retry_reasons"]),
            }
        )
    out.sort(key=lambda r: r["cost"], reverse=True)
    return out[: max(1, int(limit))]


def _agg_triggers(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    buckets: dict[str, dict[str, Any]] = defaultdict(
        lambda: {"calls": 0, "cost": 0.0, "output": 0}
    )
    for ev in events:
        trig = _blank(ev.get("trigger"), "unknown")
        buckets[trig]["calls"] += 1
        buckets[trig]["cost"] += float(ev.get("estimated_cost_usd") or 0.0)
        buckets[trig]["output"] += int(ev.get("output_tokens") or 0)
    out = [{"trigger": k, **v} for k, v in buckets.items()]
    out.sort(key=lambda r: r["cost"], reverse=True)
    return out


def _short(text: str, width: int) -> str:
    if len(text) <= width:
        return text
    return "…" + text[-(width - 1) :]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--jsonl", type=Path, default=None)
    ap.add_argument("--stdin", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--top-ops", type=int, default=20)
    args = ap.parse_args()

    path = args.jsonl
    if path is None and not args.stdin:
        env = (os.environ.get("LLM_USAGE_LOG_PATH") or "").strip()
        path = Path(env) if env else Path("/tmp/todayflow_llm_usage.jsonl")

    events = _load(path, args.stdin)
    matrix = _agg_matrix(events)
    ops = _agg_operations(events, limit=args.top_ops)
    triggers = _agg_triggers(events)
    total_cost = sum(r["cost"] for r in matrix)
    total_out = sum(r["output"] for r in matrix)
    summary = {
        "events": len(events),
        "output_tokens": total_out,
        "estimated_cost_usd": round(total_cost, 4),
        "by_trigger": triggers,
        "matrix": matrix,
        "top_operations": ops,
    }
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2, default=str))
        return 0

    print(
        f"events={len(events)}  output_tokens={total_out}  "
        f"estimated_cost=${total_cost:.4f}"
    )
    print("\n== trigger ==")
    print(f"{'Trigger':<12} {'Calls':>8} {'Output':>12} {'Cost':>10}")
    for r in triggers:
        print(f"{r['trigger']:<12} {r['calls']:>8} {r['output']:>12} ${r['cost']:>9.4f}")

    print("\n== feature × trigger × model × retry_reason ==")
    print(
        f"{'Feature':<24} {'Trig':<10} {'Retry':<16} {'Calls':>6} "
        f"{'Out':>10} {'Rsn':>10} {'Cost':>10}"
    )
    for r in matrix:
        print(
            f"{_short(r['feature'], 24):<24} {_short(r['trigger'], 10):<10} "
            f"{_short(r['retry_reason'], 16):<16} {r['calls']:>6} "
            f"{r['output']:>10} {r['reasoning']:>10} ${r['cost']:>9.4f}"
        )

    print(f"\n== top {args.top_ops} operation_id ==")
    print(f"{'Operation':<22} {'Trig':<10} {'Calls':>6} {'Cost':>10}  id")
    for r in ops:
        print(
            f"{_short(r['operation'], 22):<22} {_short(r['trigger'], 10):<10} "
            f"{r['calls']:>6} ${r['cost']:>9.4f}  {r['operation_id']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

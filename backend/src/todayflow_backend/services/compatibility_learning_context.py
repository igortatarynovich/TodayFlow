"""Recent Compatibility learning signals from `meaning_events` (PIM give/take loop)."""

from __future__ import annotations

from collections import Counter
from datetime import date, timedelta
from typing import Any

from sqlalchemy.orm import Session

from todayflow_backend.db import models
from todayflow_backend.services.compatibility_attachment_reference_v0 import (
    build_attachment_reference_context,
)

_COMPATIBILITY_EVENT_TYPES = frozenset(
    {
        "compatibility_echo",
        "compatibility_scenario_switch",
        "compatibility_deep_open",
        "compatibility_view",
        "compatibility_topic_select",
    }
)

_DEEP_BLOCK_KEYS = frozenset({"emotions", "communication", "conflicts", "sexuality", "long_term"})


def _payload_dict(raw: Any) -> dict[str, Any]:
    return raw if isinstance(raw, dict) else {}


def _payload_str(payload: dict[str, Any], *keys: str) -> str:
    for key in keys:
        val = payload.get(key)
        if val is None:
            continue
        s = str(val).strip()
        if s and s.lower() != "null":
            return s[:120]
    return ""


def build_compatibility_learning_context(
    db: Session,
    *,
    user_id: int,
    reference_date: date | None = None,
    window_days: int = 60,
    limit: int = 80,
) -> dict[str, Any] | None:
    """Compact slice for LLM / dynamics — recent echoes and scenario preferences."""
    ref = reference_date or date.today()
    wd = max(14, min(90, int(window_days)))
    start = ref - timedelta(days=wd - 1)

    rows = (
        db.query(models.MeaningEvent.event_type, models.MeaningEvent.payload)
        .filter(
            models.MeaningEvent.user_id == user_id,
            models.MeaningEvent.local_date >= start,
            models.MeaningEvent.local_date <= ref,
            models.MeaningEvent.event_type.in_(tuple(_COMPATIBILITY_EVENT_TYPES)),
        )
        .order_by(models.MeaningEvent.id.desc())
        .limit(max(20, min(200, int(limit))))
        .all()
    )
    if not rows:
        return None

    format_c: Counter[str] = Counter()
    echo_c: Counter[str] = Counter()
    block_fb: dict[str, str] = {}
    scenario_switches = 0
    deep_opens = 0
    echo_total = 0

    for et, raw_payload in rows:
        pl = _payload_dict(raw_payload)
        et_s = str(et)

        fmt = _payload_str(pl, "format_id", "scenario_id", "to_scenario_id")
        if fmt:
            format_c[fmt] += 1

        if et_s == "compatibility_echo":
            echo_total += 1
            echo_val = _payload_str(pl, "echo")
            if echo_val:
                echo_c[echo_val] += 1
            block_key = _payload_str(pl, "block_key")
            echo_val = _payload_str(pl, "echo")
            if block_key in _DEEP_BLOCK_KEYS and echo_val in {"yes", "partial", "no"} and block_key not in block_fb:
                block_fb[block_key] = echo_val
        elif et_s == "compatibility_scenario_switch":
            scenario_switches += 1
        elif et_s == "compatibility_deep_open":
            deep_opens += 1

    hints: list[str] = []
    if format_c:
        top_fmt, top_cnt = format_c.most_common(1)[0]
        if top_cnt >= 2:
            hints.append(f"Чаще исследует сценарий «{top_fmt}» ({top_cnt} раз).")
    if echo_total >= 3:
        yes_n = echo_c.get("yes", 0)
        partial_n = echo_c.get("partial", 0)
        no_n = echo_c.get("no", 0)
        hints.append(f"Отметки по разбору: точно {yes_n}, частично {partial_n}, мимо {no_n}.")
    if scenario_switches >= 2:
        hints.append("Активно переключает сценарии исследования пары.")

    attachment_reference = build_attachment_reference_context(block_fb, locale="ru")

    out: dict[str, Any] = {
        "contract_version": "compatibility_learning_context_v0",
        "window_days": wd,
        "echo_count": echo_total,
        "scenario_switches": scenario_switches,
        "deep_opens": deep_opens,
        "top_format_ids": [{"id": k, "count": c} for k, c in format_c.most_common(5)],
        "recent_block_feedback": block_fb,
        "pattern_hints": hints[:4],
    }
    if attachment_reference:
        out["attachment_reference"] = attachment_reference
    return out

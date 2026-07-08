"""Knowledge freshness scoring for context selection (rule-based, not ML)."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

FRESHNESS_BREAKPOINTS_DAYS: list[tuple[int, float]] = [
    (0, 1.0),
    (7, 0.9),
    (30, 0.6),
    (90, 0.3),
]

FRESHNESS_FLOOR = 0.1


def _parse_iso(ts: str) -> datetime:
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def days_since_confirmation(
    active_knowledge: dict[str, Any],
    *,
    now: datetime | None = None,
) -> int | None:
    reference = active_knowledge.get("last_confirmed_at") or active_knowledge.get(
        "created_at"
    )
    if not isinstance(reference, str):
        return None
    current = now or datetime.now(UTC)
    delta = current - _parse_iso(reference)
    return max(0, delta.days)


def compute_freshness_score(
    active_knowledge: dict[str, Any],
    *,
    now: datetime | None = None,
) -> float:
    """
    Rule-based freshness from last_confirmed_at.

    today=1.0, 7d=0.9, 30d=0.6, 90d=0.3; linear interpolate; floor 0.1.
    """
    days = days_since_confirmation(active_knowledge, now=now)
    if days is None:
        return FRESHNESS_FLOOR

    if days <= FRESHNESS_BREAKPOINTS_DAYS[0][0]:
        return FRESHNESS_BREAKPOINTS_DAYS[0][1]

    for (prev_days, prev_score), (next_days, next_score) in zip(
        FRESHNESS_BREAKPOINTS_DAYS,
        FRESHNESS_BREAKPOINTS_DAYS[1:],
        strict=False,
    ):
        if days <= next_days:
            span = next_days - prev_days
            if span <= 0:
                return next_score
            ratio = (days - prev_days) / span
            return prev_score + (next_score - prev_score) * ratio

    last_days, last_score = FRESHNESS_BREAKPOINTS_DAYS[-1]
    if days <= last_days * 2:
        ratio = (days - last_days) / max(last_days, 1)
        return max(FRESHNESS_FLOOR, last_score * (1.0 - 0.5 * min(ratio, 1.0)))

    return FRESHNESS_FLOOR

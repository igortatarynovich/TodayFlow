from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Literal

from sqlalchemy import and_
from sqlalchemy.orm import Session

from todayflow_backend.db import models as db_models

RingName = Literal["Mind", "Body", "Love", "Wealth", "Purpose", "Energy"]
ConfidenceLevel = Literal["low", "medium", "high"]

RING_ORDER: tuple[RingName, ...] = ("Mind", "Body", "Love", "Wealth", "Purpose", "Energy")
RING_WEIGHTS_V1: dict[RingName, float] = {
    "Mind": 0.20,
    "Body": 0.15,
    "Love": 0.15,
    "Wealth": 0.15,
    "Purpose": 0.20,
    "Energy": 0.15,
}

RING_EVENT_WEIGHTS: dict[RingName, dict[str, float]] = {
    "Mind": {
        "self_awareness_question": 0.18,
        "reflection_answer": 0.20,
        "guidance_ask": 0.18,
        "practice_completed": 0.16,
        "diary_entry": 0.10,
        "compatibility_view": 0.08,
        "tarot_selected": 0.06,
        "number_selected": 0.05,
        "mood_selected": 0.06,
        "head_topic_selected": 0.06,
        "sphere_opened": 0.06,
        "sphere_feedback": 0.05,
        "evening_reflection_submitted": 0.08,
        "today_micro_reflection": 0.04,
        "today_narrative_depth_changed": 0.04,
        "today_guide_why_opened": 0.03,
        "today_day_history_first_visible": 0.025,
    },
    "Body": {
        "habit_completed": 0.26,
        "ascetic_step_done": 0.18,
        "cycle_log": 0.22,
        "practice_completed": 0.14,
        "consistency_bonus": 0.10,
        "focus_started": 0.06,
        "focus_completed": 0.08,
        "habit_created": 0.06,
        "today_habit_toggle": 0.04,
    },
    "Love": {
        "diary_entry": 0.20,
        "reflection_answer": 0.16,
        "compatibility_view": 0.28,
        "compatibility_encyclopedia_view": 0.06,
        "compatibility_topic_select": 0.12,
        "compatibility_echo": 0.22,
        "compatibility_scenario_switch": 0.10,
        "compatibility_deep_open": 0.06,
        "guidance_ask": 0.16,
        "affirmation_done": 0.10,
        "sphere_opened": 0.06,
        "sphere_feedback": 0.10,
    },
    "Wealth": {
        "habit_completed": 0.26,
        "ascetic_step_done": 0.18,
        "guidance_ask": 0.22,
        "practice_completed": 0.14,
        "consistency_bonus": 0.10,
        "goal_created": 0.06,
        "habit_created": 0.06,
        "support_selected": 0.06,
    },
    "Purpose": {
        "guidance_ask": 0.22,
        "diary_entry": 0.18,
        "self_awareness_question": 0.20,
        "practice_completed": 0.18,
        "reflection_answer": 0.08,
        "action_option_selected": 0.08,
        "head_topic_selected": 0.06,
    },
    "Energy": {
        "affirmation_done": 0.22,
        "cycle_log": 0.22,
        "practice_completed": 0.20,
        "habit_completed": 0.16,
        "consistency_bonus": 0.10,
        "focus_started": 0.06,
        "focus_completed": 0.08,
        "today_ring_open": 0.04,
    },
}


@dataclass(frozen=True)
class RingSnapshotItem:
    ring: RingName
    score: int
    trend_7d: int
    confidence: ConfidenceLevel
    top_contributors: list[str]


@dataclass(frozen=True)
class MeaningProgressSnapshot:
    ring_scores: dict[RingName, int]
    ring_confidence: ConfidenceLevel
    active_days: int
    rings: list[RingSnapshotItem]


def confidence_label(events_count: int) -> ConfidenceLevel:
    if events_count >= 30:
        return "high"
    if events_count >= 10:
        return "medium"
    return "low"


def build_meaning_progress_snapshot(
    *,
    db: Session,
    user_id: int,
    target_date: date,
    window_days: int = 28,
) -> MeaningProgressSnapshot:
    start_date = target_date - timedelta(days=max(1, window_days) - 1)
    prev_start = start_date - timedelta(days=7)
    prev_end = start_date - timedelta(days=1)

    events = (
        db.query(
            db_models.MeaningEvent.event_type,
            db_models.MeaningEvent.local_date,
            db_models.MeaningEvent.quality_score,
        )
        .filter(
            and_(
                db_models.MeaningEvent.user_id == user_id,
                db_models.MeaningEvent.local_date >= start_date,
                db_models.MeaningEvent.local_date <= target_date,
            )
        )
        .all()
    )
    prev_events = (
        db.query(
            db_models.MeaningEvent.event_type,
            db_models.MeaningEvent.local_date,
            db_models.MeaningEvent.quality_score,
        )
        .filter(
            and_(
                db_models.MeaningEvent.user_id == user_id,
                db_models.MeaningEvent.local_date >= prev_start,
                db_models.MeaningEvent.local_date <= prev_end,
            )
        )
        .all()
    )

    active_days = {row[1] for row in events if row[1]}
    rings: list[RingSnapshotItem] = []
    ring_scores: dict[RingName, int] = {}
    conf = confidence_label(len(events))
    for ring in RING_ORDER:
        score, top = _ring_score_for_events(ring=ring, events=events)
        prev_score, _ = _ring_score_for_events(ring=ring, events=prev_events)
        ring_scores[ring] = score
        rings.append(
            RingSnapshotItem(
                ring=ring,
                score=score,
                trend_7d=score - prev_score,
                confidence=conf,
                top_contributors=top,
            )
        )

    return MeaningProgressSnapshot(
        ring_scores=ring_scores,
        ring_confidence=conf,
        active_days=len(active_days),
        rings=rings,
    )


def compute_consistency_bonus(*, daily_streak: int, active_days_28: int) -> int:
    streak_bonus = min(3, max(0, daily_streak // 7))
    cadence_bonus = 2 if active_days_28 >= 20 else 1 if active_days_28 >= 12 else 0
    return min(5, streak_bonus + cadence_bonus)


def build_growth_index_from_rings(
    *,
    ring_scores: dict[RingName, int],
    confidence: ConfidenceLevel,
    consistency_bonus: int,
) -> int:
    weighted = 0.0
    for ring, weight in RING_WEIGHTS_V1.items():
        weighted += max(0, min(100, int(ring_scores.get(ring, 0)))) * weight
    index = int(round(weighted + consistency_bonus))
    if confidence == "low":
        index = min(index, 65)
    return max(0, min(100, index))


def resolve_archetype_level(*, evolution_index: int, confidence: ConfidenceLevel, active_days_28: int) -> str:
    gated_index = evolution_index
    if confidence == "low":
        gated_index = min(gated_index, 49)
    elif confidence == "medium":
        gated_index = min(gated_index, 84)

    if active_days_28 < 7:
        gated_index = min(gated_index, 49)
    elif active_days_28 < 14:
        gated_index = min(gated_index, 64)
    elif active_days_28 < 21:
        gated_index = min(gated_index, 74)

    for level in reversed(archetype_levels()):
        if gated_index >= level["evolution_min"]:
            return str(level["name"])
    return "Seeker"


def build_archetype_progress(*, evolution_index: int, confidence: ConfidenceLevel, active_days_28: int) -> dict:
    levels = archetype_levels()
    current_idx = 0
    for idx, level in enumerate(levels):
        if evolution_index >= int(level["evolution_min"]):
            current_idx = idx

    current = levels[current_idx]
    next_level = levels[current_idx + 1] if current_idx + 1 < len(levels) else None
    if not next_level:
        return {
            "current": current["name"],
            "next": None,
            "progress_pct": 100,
            "requirements": {"evolution_min": current["evolution_min"], "daily_streak_min": 0, "reflection_min": 0},
            "confidence": confidence,
            "active_days_28": active_days_28,
        }

    current_floor = int(current["evolution_min"])
    next_floor = int(next_level["evolution_min"])
    range_size = max(1, next_floor - current_floor)
    progress_pct = int(round(min(100.0, max(0.0, ((evolution_index - current_floor) / range_size) * 100))))
    return {
        "current": current["name"],
        "next": next_level["name"],
        "progress_pct": progress_pct,
        "requirements": {"evolution_min": next_level["evolution_min"], "daily_streak_min": 0, "reflection_min": 0},
        "confidence": confidence,
        "active_days_28": active_days_28,
    }


def archetype_levels() -> list[dict]:
    return [
        {"name": "Seeker", "evolution_min": 0},
        {"name": "Initiate", "evolution_min": 35},
        {"name": "Observer", "evolution_min": 50},
        {"name": "Alchemist", "evolution_min": 65},
        {"name": "Oracle", "evolution_min": 75},
        {"name": "Architect", "evolution_min": 85},
    ]


def _ring_score_for_events(
    *,
    ring: RingName,
    events: list[tuple[str, date, float]],
) -> tuple[int, list[str]]:
    weights = RING_EVENT_WEIGHTS[ring]
    points = 0.0
    contributors: dict[str, float] = {}
    for event_type, _local_date, quality_score in events:
        event_weight = weights.get(event_type, 0.0)
        if event_weight <= 0.0:
            continue
        event_points = event_weight * max(0.0, min(1.0, float(quality_score or 0.0)))
        points += event_points
        contributors[event_type] = contributors.get(event_type, 0.0) + event_points
    score = min(100, int(round((points / 392.0) * 100)))
    top = [k for k, _ in sorted(contributors.items(), key=lambda item: item[1], reverse=True)[:3]]
    return score, top

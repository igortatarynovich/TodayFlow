"""E1.7 — Calendar Intelligence consumer policies (apply B1.12 visibility caps to E artifacts)."""

from __future__ import annotations

import copy
from datetime import UTC, date, datetime, timedelta
from typing import Any
from uuid import uuid4

from todayflow_backend.services.evolution_calendar_runtime_policy_v1 import (
    CALENDAR_DEPTH_BASIC,
    CALENDAR_DEPTH_FULL,
    CALENDAR_DEPTH_NONE,
    CALENDAR_DEPTH_ORDER,
    CALENDAR_DEPTH_STANDARD,
    EVOLUTION_CALENDAR_RUNTIME_POLICY_V1_CONTRACT,
    VIEW_CYCLE,
    VIEW_DAY,
    VIEW_MONTH,
    VIEW_RHYTHM,
    validate_evolution_calendar_runtime_policy_v1,
)

CALENDAR_INTELLIGENCE_CONSUMER_POLICY_V1_CONTRACT = "calendar_intelligence_consumer_policy_v1"
CALENDAR_INTELLIGENCE_CONSUMER_POLICY_V1_VERSION = "1.0.0"

ARTIFACT_DAY_RECORD = "day_record"
ARTIFACT_MONTH_MAP = "month_map"
ARTIFACT_RHYTHM_CANDIDATE = "rhythm_candidate"
ARTIFACT_RHYTHM_PATTERN = "rhythm_pattern"
ARTIFACT_RHYTHM_KNOWLEDGE_CANDIDATE = "rhythm_knowledge_candidate"
ARTIFACT_PROGRESSION_CONTEXT = "progression_context"

ALLOWED_ARTIFACT_KINDS = frozenset(
    {
        ARTIFACT_DAY_RECORD,
        ARTIFACT_MONTH_MAP,
        ARTIFACT_RHYTHM_CANDIDATE,
        ARTIFACT_RHYTHM_PATTERN,
        ARTIFACT_RHYTHM_KNOWLEDGE_CANDIDATE,
        ARTIFACT_PROGRESSION_CONTEXT,
    }
)

VISIBILITY_VISIBLE = "visible"
VISIBILITY_REDACTED = "redacted"
VISIBILITY_BLOCKED = "blocked"

ALLOWED_VISIBILITY_RESULTS = frozenset(
    {
        VISIBILITY_VISIBLE,
        VISIBILITY_REDACTED,
        VISIBILITY_BLOCKED,
    }
)

BLOCK_INVALID_CALENDAR_RUNTIME_POLICY = "invalid_calendar_runtime_policy"
BLOCK_VIEW_NOT_ALLOWED = "view_not_allowed"
BLOCK_MONTH_MAP_NOT_ALLOWED = "month_map_not_allowed"
BLOCK_RHYTHM_VISIBILITY_NOT_ALLOWED = "rhythm_visibility_not_allowed"
BLOCK_CYCLE_VISIBILITY_NOT_ALLOWED = "cycle_visibility_not_allowed"
BLOCK_HISTORY_WINDOW_EXCEEDED = "history_window_exceeded"
BLOCK_ARTIFACT_NOT_VISIBLE = "artifact_not_visible"

CALENDAR_INTELLIGENCE_CONSUMER_POLICY_V1_KEYS = frozenset(
    {
        "contract_version",
        "policy_id",
        "source_calendar_runtime_policy_id",
        "calendar_depth",
        "allowed_views",
        "history_window_days",
        "day_record_visibility_allowed",
        "month_map_visibility_allowed",
        "cycle_overlay_visibility_allowed",
        "rhythm_pattern_visibility_allowed",
        "rhythm_candidate_visibility_allowed",
        "bridge_output_visibility_allowed",
        "blocked_artifact_effects",
        "read_only",
        "calendar_mutation_allowed",
        "insight_generation_allowed",
        "recommendation_allowed",
        "profile_update_allowed",
        "memory_update_allowed",
        "created_at",
        "version",
    }
)

FORBIDDEN_CONSUMER_POLICY_FIELDS = frozenset(
    {
        "insight",
        "insight_text",
        "calendar_insight",
        "recommendation",
        "recommendation_id",
        "llm_output",
        "llm_call",
        "commerce",
        "calendar_event",
        "events",
        "score",
        "stage_update",
        "promoted_stage",
        "profile_update",
        "memory_write",
        "targeting",
        "purchase",
    }
)


class CalendarIntelligenceConsumerPolicyError(ValueError):
    """Raised when calendar consumer policy inputs or payload are invalid."""


def _utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def generate_calendar_intelligence_consumer_policy_id() -> str:
    return f"cicp-{uuid4()}"


def _depth_at_least(calendar_depth: str, minimum: str) -> bool:
    depth = calendar_depth if calendar_depth in CALENDAR_DEPTH_ORDER else CALENDAR_DEPTH_NONE
    floor = minimum if minimum in CALENDAR_DEPTH_ORDER else CALENDAR_DEPTH_NONE
    return CALENDAR_DEPTH_ORDER[depth] >= CALENDAR_DEPTH_ORDER[floor]


def _derive_visibility_flags(runtime_policy: dict[str, Any]) -> dict[str, bool]:
    allowed_views = set(runtime_policy.get("allowed_views") or [])
    calendar_depth = str(runtime_policy.get("calendar_depth") or CALENDAR_DEPTH_NONE)

    day_record_allowed = VIEW_DAY in allowed_views
    month_map_allowed = bool(runtime_policy.get("monthly_map_allowed")) and VIEW_MONTH in allowed_views
    cycle_overlay_allowed = bool(runtime_policy.get("cycle_visibility_allowed")) and VIEW_CYCLE in allowed_views
    rhythm_pattern_allowed = bool(runtime_policy.get("rhythm_insights_allowed")) and VIEW_RHYTHM in allowed_views
    rhythm_candidate_allowed = month_map_allowed and _depth_at_least(calendar_depth, CALENDAR_DEPTH_STANDARD)
    bridge_output_allowed = rhythm_pattern_allowed or _depth_at_least(calendar_depth, CALENDAR_DEPTH_FULL)

    return {
        "day_record_visibility_allowed": day_record_allowed,
        "month_map_visibility_allowed": month_map_allowed,
        "cycle_overlay_visibility_allowed": cycle_overlay_allowed,
        "rhythm_pattern_visibility_allowed": rhythm_pattern_allowed,
        "rhythm_candidate_visibility_allowed": rhythm_candidate_allowed,
        "bridge_output_visibility_allowed": bridge_output_allowed,
    }


def build_calendar_intelligence_consumer_policy_v1(
    evolution_calendar_runtime_policy: dict[str, Any] | None = None,
    *,
    policy_id: str | None = None,
    created_at: str | None = None,
) -> dict[str, Any]:
    """
    Derive Branch E consumer visibility policy from B1.12 evolution calendar runtime policy.

    Caps visibility only — does not generate insights or mutate calendar data.
    """
    if evolution_calendar_runtime_policy is None:
        return _idle_consumer_policy(
            blocked_artifact_effects=[BLOCK_INVALID_CALENDAR_RUNTIME_POLICY],
            policy_id=policy_id,
            created_at=created_at,
        )

    if (
        evolution_calendar_runtime_policy.get("contract_version")
        != EVOLUTION_CALENDAR_RUNTIME_POLICY_V1_CONTRACT
    ):
        return _idle_consumer_policy(
            blocked_artifact_effects=[BLOCK_INVALID_CALENDAR_RUNTIME_POLICY],
            policy_id=policy_id,
            created_at=created_at,
        )

    validation_errors = validate_evolution_calendar_runtime_policy_v1(
        evolution_calendar_runtime_policy
    )
    if validation_errors:
        return _idle_consumer_policy(
            blocked_artifact_effects=[BLOCK_INVALID_CALENDAR_RUNTIME_POLICY],
            policy_id=policy_id,
            created_at=created_at,
        )

    visibility = _derive_visibility_flags(evolution_calendar_runtime_policy)
    blocked = list(evolution_calendar_runtime_policy.get("blocked_calendar_effects") or [])

    policy = {
        "contract_version": CALENDAR_INTELLIGENCE_CONSUMER_POLICY_V1_CONTRACT,
        "policy_id": policy_id or generate_calendar_intelligence_consumer_policy_id(),
        "source_calendar_runtime_policy_id": evolution_calendar_runtime_policy.get("policy_id"),
        "calendar_depth": evolution_calendar_runtime_policy.get("calendar_depth"),
        "allowed_views": list(evolution_calendar_runtime_policy.get("allowed_views") or []),
        "history_window_days": int(evolution_calendar_runtime_policy.get("history_window_days") or 0),
        "blocked_artifact_effects": blocked,
        "read_only": True,
        "calendar_mutation_allowed": False,
        "insight_generation_allowed": False,
        "recommendation_allowed": False,
        "profile_update_allowed": False,
        "memory_update_allowed": False,
        "created_at": created_at or _utc_now_iso(),
        "version": CALENDAR_INTELLIGENCE_CONSUMER_POLICY_V1_VERSION,
        **visibility,
    }

    errors = validate_calendar_intelligence_consumer_policy_v1(policy)
    if errors:
        raise CalendarIntelligenceConsumerPolicyError("; ".join(errors))

    return policy


def _idle_consumer_policy(
    *,
    blocked_artifact_effects: list[str],
    policy_id: str | None = None,
    created_at: str | None = None,
) -> dict[str, Any]:
    policy = {
        "contract_version": CALENDAR_INTELLIGENCE_CONSUMER_POLICY_V1_CONTRACT,
        "policy_id": policy_id or generate_calendar_intelligence_consumer_policy_id(),
        "source_calendar_runtime_policy_id": None,
        "calendar_depth": CALENDAR_DEPTH_NONE,
        "allowed_views": [],
        "history_window_days": 0,
        "day_record_visibility_allowed": False,
        "month_map_visibility_allowed": False,
        "cycle_overlay_visibility_allowed": False,
        "rhythm_pattern_visibility_allowed": False,
        "rhythm_candidate_visibility_allowed": False,
        "bridge_output_visibility_allowed": False,
        "blocked_artifact_effects": blocked_artifact_effects,
        "read_only": True,
        "calendar_mutation_allowed": False,
        "insight_generation_allowed": False,
        "recommendation_allowed": False,
        "profile_update_allowed": False,
        "memory_update_allowed": False,
        "created_at": created_at or _utc_now_iso(),
        "version": CALENDAR_INTELLIGENCE_CONSUMER_POLICY_V1_VERSION,
    }
    errors = validate_calendar_intelligence_consumer_policy_v1(policy)
    if errors:
        raise CalendarIntelligenceConsumerPolicyError("; ".join(errors))
    return policy


def validate_calendar_intelligence_consumer_policy_v1(policy: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    if policy.get("contract_version") != CALENDAR_INTELLIGENCE_CONSUMER_POLICY_V1_CONTRACT:
        errors.append("invalid contract_version")

    for key in CALENDAR_INTELLIGENCE_CONSUMER_POLICY_V1_KEYS:
        if key not in policy:
            errors.append(f"missing field: {key}")

    forbidden = set(policy.keys()) & FORBIDDEN_CONSUMER_POLICY_FIELDS
    if forbidden:
        errors.append(f"forbidden fields: {sorted(forbidden)}")

    if policy.get("read_only") is not True:
        errors.append("read_only must be true")
    if policy.get("calendar_mutation_allowed") is not False:
        errors.append("calendar_mutation_allowed must be false")
    if policy.get("insight_generation_allowed") is not False:
        errors.append("insight_generation_allowed must be false")
    if policy.get("recommendation_allowed") is not False:
        errors.append("recommendation_allowed must be false")
    if policy.get("profile_update_allowed") is not False:
        errors.append("profile_update_allowed must be false")
    if policy.get("memory_update_allowed") is not False:
        errors.append("memory_update_allowed must be false")

    depth = policy.get("calendar_depth")
    if depth not in CALENDAR_DEPTH_ORDER:
        errors.append("invalid calendar_depth")

    for flag in (
        "day_record_visibility_allowed",
        "month_map_visibility_allowed",
        "cycle_overlay_visibility_allowed",
        "rhythm_pattern_visibility_allowed",
        "rhythm_candidate_visibility_allowed",
        "bridge_output_visibility_allowed",
    ):
        if not isinstance(policy.get(flag), bool):
            errors.append(f"{flag} must be boolean")

    return errors


def _artifact_visibility_allowed(
    consumer_policy: dict[str, Any],
    artifact_kind: str,
) -> tuple[bool, list[str]]:
    reasons: list[str] = []

    if artifact_kind not in ALLOWED_ARTIFACT_KINDS:
        return False, ["invalid artifact_kind"]

    if artifact_kind == ARTIFACT_DAY_RECORD:
        allowed = bool(consumer_policy.get("day_record_visibility_allowed"))
        if not allowed:
            reasons.append(BLOCK_VIEW_NOT_ALLOWED)
        return allowed, reasons

    if artifact_kind == ARTIFACT_MONTH_MAP:
        allowed = bool(consumer_policy.get("month_map_visibility_allowed"))
        if not allowed:
            reasons.append(BLOCK_MONTH_MAP_NOT_ALLOWED)
        return allowed, reasons

    if artifact_kind == ARTIFACT_RHYTHM_CANDIDATE:
        allowed = bool(consumer_policy.get("rhythm_candidate_visibility_allowed"))
        if not allowed:
            reasons.append(BLOCK_RHYTHM_VISIBILITY_NOT_ALLOWED)
        return allowed, reasons

    if artifact_kind == ARTIFACT_RHYTHM_PATTERN:
        allowed = bool(consumer_policy.get("rhythm_pattern_visibility_allowed"))
        if not allowed:
            reasons.append(BLOCK_RHYTHM_VISIBILITY_NOT_ALLOWED)
        return allowed, reasons

    if artifact_kind in {ARTIFACT_RHYTHM_KNOWLEDGE_CANDIDATE, ARTIFACT_PROGRESSION_CONTEXT}:
        allowed = bool(consumer_policy.get("bridge_output_visibility_allowed"))
        if not allowed:
            reasons.append(BLOCK_ARTIFACT_NOT_VISIBLE)
        return allowed, reasons

    return False, [BLOCK_ARTIFACT_NOT_VISIBLE]


def evaluate_calendar_artifact_visibility_v1(
    consumer_policy: dict[str, Any],
    artifact_kind: str,
) -> tuple[str, list[str]]:
    """Return visibility result for an artifact kind under consumer policy."""
    errors = validate_calendar_intelligence_consumer_policy_v1(consumer_policy)
    if errors:
        return VISIBILITY_BLOCKED, [BLOCK_INVALID_CALENDAR_RUNTIME_POLICY, *errors[:2]]

    allowed, reasons = _artifact_visibility_allowed(consumer_policy, artifact_kind)
    if not allowed:
        return VISIBILITY_BLOCKED, reasons
    return VISIBILITY_VISIBLE, []


def _parse_iso_date(value: str) -> date:
    return date.fromisoformat(value[:10])


def _filter_day_records_by_history_window(
    day_records: list[dict[str, Any]],
    *,
    history_window_days: int,
    reference_date: date,
) -> tuple[list[dict[str, Any]], list[str]]:
    if history_window_days <= 0:
        return [], [BLOCK_HISTORY_WINDOW_EXCEEDED]

    earliest = reference_date - timedelta(days=history_window_days - 1)
    kept: list[dict[str, Any]] = []
    removed = False
    for record in day_records:
        record_date = record.get("date")
        if not isinstance(record_date, str):
            continue
        parsed = _parse_iso_date(record_date)
        if parsed < earliest or parsed > reference_date:
            removed = True
            continue
        kept.append(record)

    reasons = [BLOCK_HISTORY_WINDOW_EXCEEDED] if removed else []
    return kept, reasons


def _redact_month_map(
    month_map: dict[str, Any],
    consumer_policy: dict[str, Any],
    *,
    reference_date: date,
) -> tuple[dict[str, Any], str, list[str]]:
    reasons: list[str] = []
    redacted = copy.deepcopy(month_map)

    window_days = int(consumer_policy.get("history_window_days") or 0)
    day_records = redacted.get("day_records")
    if isinstance(day_records, list):
        filtered, window_reasons = _filter_day_records_by_history_window(
            day_records,
            history_window_days=window_days,
            reference_date=reference_date,
        )
        redacted["day_records"] = filtered
        reasons.extend(window_reasons)

    if not consumer_policy.get("cycle_overlay_visibility_allowed"):
        overlays = redacted.get("cycle_overlays") or []
        if overlays:
            redacted["cycle_overlays"] = []
            reasons.append(BLOCK_CYCLE_VISIBILITY_NOT_ALLOWED)

    result = VISIBILITY_REDACTED if reasons else VISIBILITY_VISIBLE
    return redacted, result, reasons


def apply_calendar_consumer_policy_v1(
    consumer_policy: dict[str, Any],
    artifact_kind: str,
    artifact: dict[str, Any],
    *,
    reference_date: date | None = None,
) -> dict[str, Any]:
    """
    Apply E1.7 visibility caps to one Calendar Intelligence artifact.

    Returns visible/redacted/blocked artifact payload without generating insight.
    """
    ref_date = reference_date or datetime.now(UTC).date()
    visibility, reasons = evaluate_calendar_artifact_visibility_v1(consumer_policy, artifact_kind)

    if visibility == VISIBILITY_BLOCKED:
        return {
            "result": VISIBILITY_BLOCKED,
            "artifact_kind": artifact_kind,
            "artifact": None,
            "reasons": reasons,
        }

    if artifact_kind == ARTIFACT_MONTH_MAP:
        redacted, result, redact_reasons = _redact_month_map(
            artifact,
            consumer_policy,
            reference_date=ref_date,
        )
        return {
            "result": result,
            "artifact_kind": artifact_kind,
            "artifact": redacted,
            "reasons": redact_reasons,
        }

    if artifact_kind == ARTIFACT_DAY_RECORD:
        window_days = int(consumer_policy.get("history_window_days") or 0)
        record_date = artifact.get("date")
        if isinstance(record_date, str):
            parsed = _parse_iso_date(record_date)
            earliest = ref_date - timedelta(days=max(window_days - 1, 0))
            if parsed < earliest or parsed > ref_date:
                return {
                    "result": VISIBILITY_BLOCKED,
                    "artifact_kind": artifact_kind,
                    "artifact": None,
                    "reasons": [BLOCK_HISTORY_WINDOW_EXCEEDED],
                }

    return {
        "result": VISIBILITY_VISIBLE,
        "artifact_kind": artifact_kind,
        "artifact": copy.deepcopy(artifact),
        "reasons": [],
    }

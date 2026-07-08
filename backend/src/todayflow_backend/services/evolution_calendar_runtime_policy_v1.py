"""B1.12 — Evolution → Calendar consumer runtime policy (B1.7 calendar slice as depth cap)."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from todayflow_backend.services.evolution_effect_consumer_map_v1 import (
    CONSUMER_CALENDAR,
    EVOLUTION_EFFECT_CONSUMER_SLICE_V1_CONTRACT,
    validate_evolution_effect_consumer_slice_v1,
)
from todayflow_backend.services.evolution_effect_runtime_policy_v1 import (
    EVOLUTION_EFFECT_RUNTIME_POLICY_V1_CONTRACT,
)

EVOLUTION_CALENDAR_RUNTIME_POLICY_V1_VERSION = "1.0.0"

EVOLUTION_CALENDAR_RUNTIME_POLICY_V1_CONTRACT = "evolution_calendar_runtime_policy_v1"

CALENDAR_DEPTH_NONE = "none"
CALENDAR_DEPTH_BASIC = "basic"
CALENDAR_DEPTH_STANDARD = "standard"
CALENDAR_DEPTH_FULL = "full"

VIEW_DAY = "day"
VIEW_WEEK = "week"
VIEW_MONTH = "month"
VIEW_CYCLE = "cycle"
VIEW_RHYTHM = "rhythm"

CALENDAR_DEPTH_ORDER = {
    CALENDAR_DEPTH_NONE: 0,
    CALENDAR_DEPTH_BASIC: 1,
    CALENDAR_DEPTH_STANDARD: 2,
    CALENDAR_DEPTH_FULL: 3,
}

DEPTH_ALLOWED_VIEWS = {
    CALENDAR_DEPTH_NONE: {VIEW_DAY},
    CALENDAR_DEPTH_BASIC: {VIEW_DAY, VIEW_WEEK, VIEW_MONTH},
    CALENDAR_DEPTH_STANDARD: {VIEW_DAY, VIEW_WEEK, VIEW_MONTH, VIEW_CYCLE},
    CALENDAR_DEPTH_FULL: {VIEW_DAY, VIEW_WEEK, VIEW_MONTH, VIEW_CYCLE, VIEW_RHYTHM},
}

BLOCK_CALENDAR_SYSTEM_NOT_READY = "calendar_system_not_ready"
BLOCK_STAGE_DEPTH_TOO_LOW = "stage_depth_too_low"
BLOCK_CYCLE_VISIBILITY_NOT_ALLOWED = "cycle_visibility_not_allowed"
BLOCK_RHYTHM_INSIGHTS_NOT_ALLOWED = "rhythm_insights_not_allowed"
BLOCK_MONTHLY_MAP_NOT_ALLOWED = "monthly_map_not_allowed"
BLOCK_INVALID_EVOLUTION_SLICE = "invalid_evolution_slice"
BLOCK_FULL_POLICY_PASSED = "full_policy_passed"

STAGE_CALENDAR_PROFILES: dict[str, dict[str, Any]] = {
    "seeker": {
        "calendar_depth": CALENDAR_DEPTH_BASIC,
        "allowed_views": [VIEW_DAY],
        "history_window_days": 7,
        "cycle_visibility_allowed": False,
        "rhythm_insights_allowed": False,
        "monthly_map_allowed": False,
    },
    "observer": {
        "calendar_depth": CALENDAR_DEPTH_BASIC,
        "allowed_views": [VIEW_DAY, VIEW_WEEK],
        "history_window_days": 14,
        "cycle_visibility_allowed": False,
        "rhythm_insights_allowed": False,
        "monthly_map_allowed": False,
    },
    "practitioner": {
        "calendar_depth": CALENDAR_DEPTH_BASIC,
        "allowed_views": [VIEW_DAY, VIEW_WEEK, VIEW_MONTH],
        "history_window_days": 30,
        "cycle_visibility_allowed": True,
        "rhythm_insights_allowed": False,
        "monthly_map_allowed": True,
    },
    "explorer": {
        "calendar_depth": CALENDAR_DEPTH_STANDARD,
        "allowed_views": [VIEW_DAY, VIEW_WEEK, VIEW_MONTH, VIEW_CYCLE],
        "history_window_days": 60,
        "cycle_visibility_allowed": True,
        "rhythm_insights_allowed": False,
        "monthly_map_allowed": True,
    },
    "architect": {
        "calendar_depth": CALENDAR_DEPTH_FULL,
        "allowed_views": [VIEW_DAY, VIEW_WEEK, VIEW_MONTH, VIEW_CYCLE, VIEW_RHYTHM],
        "history_window_days": 90,
        "cycle_visibility_allowed": True,
        "rhythm_insights_allowed": True,
        "monthly_map_allowed": True,
    },
    "mentor": {
        "calendar_depth": CALENDAR_DEPTH_FULL,
        "allowed_views": [VIEW_DAY, VIEW_WEEK, VIEW_MONTH, VIEW_CYCLE, VIEW_RHYTHM],
        "history_window_days": 180,
        "cycle_visibility_allowed": True,
        "rhythm_insights_allowed": True,
        "monthly_map_allowed": True,
    },
    "master": {
        "calendar_depth": CALENDAR_DEPTH_FULL,
        "allowed_views": [VIEW_DAY, VIEW_WEEK, VIEW_MONTH, VIEW_CYCLE, VIEW_RHYTHM],
        "history_window_days": 365,
        "cycle_visibility_allowed": True,
        "rhythm_insights_allowed": True,
        "monthly_map_allowed": True,
    },
}

EVOLUTION_CALENDAR_RUNTIME_POLICY_V1_KEYS = frozenset(
    {
        "contract_version",
        "policy_id",
        "source_evolution_slice_id",
        "evolution_stage",
        "calendar_depth",
        "allowed_views",
        "history_window_days",
        "cycle_visibility_allowed",
        "rhythm_insights_allowed",
        "monthly_map_allowed",
        "blocked_calendar_effects",
        "read_only",
        "calendar_mutation_allowed",
        "profile_update_allowed",
        "memory_update_allowed",
        "created_at",
    }
)

FORBIDDEN_CALENDAR_POLICY_FIELDS = frozenset(
    {
        "insight",
        "calendar_insight",
        "insight_text",
        "recommendation",
        "llm_call",
        "commerce",
        "calendar_event",
        "events",
        "score",
        "stage_update",
        "promoted_stage",
        "mutation",
        "targeting",
        "purchase",
    }
)

CALENDAR_READINESS_KEY = "calendar_intelligence"


class EvolutionCalendarRuntimePolicyError(ValueError):
    """Raised when calendar runtime policy inputs or payload are invalid."""


def _utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def generate_calendar_runtime_policy_id() -> str:
    return f"ecrp-{uuid4()}"


def _is_valid_calendar_slice(evolution_slice: dict[str, Any]) -> tuple[bool, str | None]:
    if evolution_slice.get("contract_version") == EVOLUTION_EFFECT_RUNTIME_POLICY_V1_CONTRACT:
        return False, BLOCK_FULL_POLICY_PASSED
    if evolution_slice.get("contract_version") != EVOLUTION_EFFECT_CONSUMER_SLICE_V1_CONTRACT:
        return False, BLOCK_INVALID_EVOLUTION_SLICE
    if evolution_slice.get("consumer_id") != CONSUMER_CALENDAR:
        return False, BLOCK_INVALID_EVOLUTION_SLICE
    errors = validate_evolution_effect_consumer_slice_v1(
        evolution_slice,
        consumer_id=CONSUMER_CALENDAR,
    )
    if errors:
        return False, BLOCK_INVALID_EVOLUTION_SLICE
    return True, None


def _slice_calendar_tier(evolution_slice: dict[str, Any]) -> str:
    limits = evolution_slice.get("effect_limits") or {}
    unlock = (evolution_slice.get("allowed_effects") or {}).get("unlock_effects") or {}
    tier = limits.get("calendar_insight_tier")
    if tier is None:
        tier = unlock.get("calendar_insight_tier")
    if tier is None:
        return CALENDAR_DEPTH_NONE
    return str(tier)


def _slice_cycle_lengths(evolution_slice: dict[str, Any]) -> list[int]:
    limits = evolution_slice.get("effect_limits") or {}
    unlock = (evolution_slice.get("allowed_effects") or {}).get("unlock_effects") or {}
    raw = limits.get("cycle_lengths_available")
    if raw is None:
        raw = unlock.get("cycle_lengths_available")
    if not isinstance(raw, list):
        return []
    return [int(value) for value in raw]


def _min_calendar_depth(stage_depth: str, slice_tier: str) -> tuple[str, bool]:
    stage_depth = stage_depth if stage_depth in CALENDAR_DEPTH_ORDER else CALENDAR_DEPTH_NONE
    slice_tier = slice_tier if slice_tier in CALENDAR_DEPTH_ORDER else CALENDAR_DEPTH_NONE
    if CALENDAR_DEPTH_ORDER[slice_tier] < CALENDAR_DEPTH_ORDER[stage_depth]:
        return slice_tier, True
    return stage_depth, False


def _calendar_system_ready(calendar_readiness: dict[str, bool] | None) -> bool:
    if calendar_readiness is None:
        return True
    return bool(calendar_readiness.get(CALENDAR_READINESS_KEY, False))


def _idle_policy(
    *,
    blocked_calendar_effects: list[str],
    policy_id: str | None = None,
    created_at: str | None = None,
) -> dict[str, Any]:
    return {
        "contract_version": EVOLUTION_CALENDAR_RUNTIME_POLICY_V1_CONTRACT,
        "policy_id": policy_id or generate_calendar_runtime_policy_id(),
        "source_evolution_slice_id": None,
        "evolution_stage": None,
        "calendar_depth": CALENDAR_DEPTH_NONE,
        "allowed_views": [],
        "history_window_days": 0,
        "cycle_visibility_allowed": False,
        "rhythm_insights_allowed": False,
        "monthly_map_allowed": False,
        "blocked_calendar_effects": blocked_calendar_effects,
        "read_only": True,
        "calendar_mutation_allowed": False,
        "profile_update_allowed": False,
        "memory_update_allowed": False,
        "created_at": created_at or _utc_now_iso(),
    }


def build_evolution_calendar_runtime_policy_v1(
    evolution_slice: dict[str, Any] | None = None,
    *,
    evolution_user_state: dict[str, Any] | None = None,
    calendar_readiness: dict[str, bool] | None = None,
    policy_id: str | None = None,
    created_at: str | None = None,
) -> dict[str, Any]:
    """
    Build read-only calendar depth/visibility policy from a B1.7 calendar slice.

    Evolution can cap calendar depth but cannot invent rhythm insights.
    """
    if evolution_slice is None:
        return _idle_policy(
            blocked_calendar_effects=[BLOCK_INVALID_EVOLUTION_SLICE],
            policy_id=policy_id,
            created_at=created_at,
        )

    valid, invalid_reason = _is_valid_calendar_slice(evolution_slice)
    if not valid:
        return _idle_policy(
            blocked_calendar_effects=[invalid_reason or BLOCK_INVALID_EVOLUTION_SLICE],
            policy_id=policy_id,
            created_at=created_at,
        )

    stage = str(evolution_slice.get("current_stage") or "seeker")
    if evolution_user_state is not None:
        stage = str(evolution_user_state.get("current_stage") or stage)

    profile = STAGE_CALENDAR_PROFILES.get(stage, STAGE_CALENDAR_PROFILES["seeker"])
    slice_tier = _slice_calendar_tier(evolution_slice)
    cycle_lengths = _slice_cycle_lengths(evolution_slice)

    blocked: list[str] = []

    calendar_depth, slice_capped = _min_calendar_depth(profile["calendar_depth"], slice_tier)
    if slice_capped:
        blocked.append(BLOCK_STAGE_DEPTH_TOO_LOW)

    depth_views = DEPTH_ALLOWED_VIEWS.get(calendar_depth, {VIEW_DAY})
    profile_views = set(profile["allowed_views"])
    allowed_views = sorted(profile_views & depth_views, key=profile["allowed_views"].index)

    history_window_days = int(profile["history_window_days"])

    cycle_visibility_allowed = bool(profile["cycle_visibility_allowed"])
    if cycle_visibility_allowed and VIEW_CYCLE not in allowed_views:
        cycle_visibility_allowed = False
        blocked.append(BLOCK_CYCLE_VISIBILITY_NOT_ALLOWED)
    if cycle_visibility_allowed and not cycle_lengths:
        cycle_visibility_allowed = False
        blocked.append(BLOCK_CYCLE_VISIBILITY_NOT_ALLOWED)

    rhythm_insights_allowed = bool(profile["rhythm_insights_allowed"])
    if rhythm_insights_allowed and (
        calendar_depth != CALENDAR_DEPTH_FULL or slice_tier != CALENDAR_DEPTH_FULL
    ):
        rhythm_insights_allowed = False
        blocked.append(BLOCK_RHYTHM_INSIGHTS_NOT_ALLOWED)
    if rhythm_insights_allowed and VIEW_RHYTHM not in allowed_views:
        rhythm_insights_allowed = False
        blocked.append(BLOCK_RHYTHM_INSIGHTS_NOT_ALLOWED)

    monthly_map_allowed = bool(profile["monthly_map_allowed"])
    if monthly_map_allowed and VIEW_MONTH not in allowed_views:
        monthly_map_allowed = False
        blocked.append(BLOCK_MONTHLY_MAP_NOT_ALLOWED)

    if not _calendar_system_ready(calendar_readiness):
        blocked.append(BLOCK_CALENDAR_SYSTEM_NOT_READY)
        calendar_depth = CALENDAR_DEPTH_NONE
        allowed_views = [VIEW_DAY] if VIEW_DAY in profile_views else []
        history_window_days = min(history_window_days, 7)
        cycle_visibility_allowed = False
        rhythm_insights_allowed = False
        monthly_map_allowed = False

    policy = {
        "contract_version": EVOLUTION_CALENDAR_RUNTIME_POLICY_V1_CONTRACT,
        "policy_id": policy_id or generate_calendar_runtime_policy_id(),
        "source_evolution_slice_id": evolution_slice.get("slice_id"),
        "evolution_stage": stage,
        "calendar_depth": calendar_depth,
        "allowed_views": allowed_views,
        "history_window_days": history_window_days,
        "cycle_visibility_allowed": cycle_visibility_allowed,
        "rhythm_insights_allowed": rhythm_insights_allowed,
        "monthly_map_allowed": monthly_map_allowed,
        "blocked_calendar_effects": blocked,
        "read_only": True,
        "calendar_mutation_allowed": False,
        "profile_update_allowed": False,
        "memory_update_allowed": False,
        "created_at": created_at or _utc_now_iso(),
    }

    errors = validate_evolution_calendar_runtime_policy_v1(policy)
    if errors:
        raise EvolutionCalendarRuntimePolicyError("; ".join(errors))

    return policy


def validate_evolution_calendar_runtime_policy_v1(policy: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    if policy.get("contract_version") != EVOLUTION_CALENDAR_RUNTIME_POLICY_V1_CONTRACT:
        errors.append("invalid contract_version")

    for key in EVOLUTION_CALENDAR_RUNTIME_POLICY_V1_KEYS:
        if key not in policy:
            errors.append(f"missing field: {key}")

    forbidden = set(policy.keys()) & FORBIDDEN_CALENDAR_POLICY_FIELDS
    if forbidden:
        errors.append(f"forbidden policy fields: {sorted(forbidden)}")

    if policy.get("read_only") is not True:
        errors.append("read_only must be true")
    if policy.get("calendar_mutation_allowed") is not False:
        errors.append("calendar_mutation_allowed must be false")
    if policy.get("profile_update_allowed") is not False:
        errors.append("profile_update_allowed must be false")
    if policy.get("memory_update_allowed") is not False:
        errors.append("memory_update_allowed must be false")

    depth = policy.get("calendar_depth")
    if depth not in CALENDAR_DEPTH_ORDER:
        errors.append("invalid calendar_depth")

    if not isinstance(policy.get("allowed_views"), list):
        errors.append("allowed_views must be array")
    if not isinstance(policy.get("blocked_calendar_effects"), list):
        errors.append("blocked_calendar_effects must be array")

    for view in policy.get("allowed_views") or []:
        if view not in {VIEW_DAY, VIEW_WEEK, VIEW_MONTH, VIEW_CYCLE, VIEW_RHYTHM}:
            errors.append(f"invalid allowed_view: {view}")

    return errors

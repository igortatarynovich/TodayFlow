"""B1.2 — Evolution user state contract (no promotion runtime)."""

from __future__ import annotations

import re
from typing import Any

from todayflow_backend.data.evolution_cd_loader import (
    get_evolution_path_theme,
    get_stage_gate_from_current_stage,
    load_evolution_cd_v1,
)
from todayflow_backend.data.evolution_cd_validator import CANONICAL_STAGE_ORDER

EVOLUTION_USER_STATE_V1_CONTRACT = "evolution_user_state_v1"
EVOLUTION_USER_STATE_V1_VERSION = "1.0.0"

ALLOWED_EVOLUTION_USER_STATE_STATUSES = frozenset({"active", "paused", "archived"})

STAGE_GATE_TARGET_V1_KEYS = frozenset({"gate_id", "from_stage", "to_stage"})

STAGE_GATE_ELIGIBILITY_V1_KEYS = frozenset(
    {
        "from_stage",
        "to_stage",
        "eligible",
        "requirements_snapshot",
        "progress_snapshot",
        "missing_requirements",
        "confidence",
        "promotion_allowed",
    }
)

PROGRESS_SNAPSHOT_V1_KEYS = frozenset(
    {
        "confirmed_patterns",
        "completed_cycles",
        "reflection_events",
        "active_days",
        "signal_counts",
        "confidence",
    }
)

REQUIREMENTS_SNAPSHOT_V1_KEYS = frozenset(
    {
        "gate_id",
        "required_signal_types",
        "minimum_confirmed_patterns",
        "minimum_completed_cycles",
        "minimum_reflection_events",
        "minimum_active_days",
        "minimum_confidence",
        "manual_review_required",
    }
)

EVOLUTION_USER_STATE_V1_KEYS = frozenset(
    {
        "contract_version",
        "user_id",
        "current_stage",
        "stage_started_at",
        "active_path_themes",
        "completed_path_themes",
        "current_stage_gate_target",
        "stage_gate_eligibility",
        "evolution_score_snapshot",
        "last_evaluated_at",
        "status",
        "version",
    }
)

FORBIDDEN_EVOLUTION_STATE_FIELDS = frozenset(
    {
        "achievement_id",
        "achievement_unlocked",
        "achievements",
        "commerce_hook",
        "commerce_purchase",
        "commerce_tier",
        "profile_update",
        "core_profile_update",
        "behavior_profile_update",
        "memory_write",
        "recommendation",
        "recommendation_id",
        "llm_context",
        "llm_call",
        "promoted_stage",
        "stage_promoted_at",
    }
)

FORBIDDEN_STAGE_SOURCE_PATTERN = re.compile(
    r"(achievement|commerce|unlock|purchase|reward|badge|payment|subscription)",
    re.I,
)


class EvolutionUserStateError(ValueError):
    """Raised when evolution user state inputs or payload are invalid."""


def build_stage_gate_eligibility_snapshot_v1(
    *,
    current_stage: str,
    progress_snapshot: dict[str, Any],
    cd: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    """
    Build read-only eligibility snapshot from CD gate + progress.

    Never promotes stage; promotion_allowed is always false in B1.2.
    """
    registry = cd if cd is not None else load_evolution_cd_v1()
    gate = get_stage_gate_from_current_stage(current_stage, registry)
    if gate is None:
        return None

    requirements_snapshot = {
        "gate_id": gate["gate_id"],
        "required_signal_types": list(gate["required_signal_types"]),
        "minimum_confirmed_patterns": gate["minimum_confirmed_patterns"],
        "minimum_completed_cycles": gate["minimum_completed_cycles"],
        "minimum_reflection_events": gate["minimum_reflection_events"],
        "minimum_active_days": gate["minimum_active_days"],
        "minimum_confidence": gate["minimum_confidence"],
        "manual_review_required": gate["manual_review_required"],
    }

    normalized_progress = _normalize_progress_snapshot(progress_snapshot)
    missing_requirements = _compute_missing_requirements(
        requirements_snapshot,
        normalized_progress,
    )
    confidence = float(normalized_progress["confidence"])
    eligible = len(missing_requirements) == 0

    eligibility = {
        "from_stage": current_stage,
        "to_stage": gate["to_stage"],
        "eligible": eligible,
        "requirements_snapshot": requirements_snapshot,
        "progress_snapshot": normalized_progress,
        "missing_requirements": missing_requirements,
        "confidence": confidence,
        "promotion_allowed": False,
    }

    errors = validate_stage_gate_eligibility_v1(eligibility, current_stage=current_stage)
    if errors:
        raise EvolutionUserStateError("; ".join(errors[:6]))
    return eligibility


def build_evolution_user_state_v1(
    *,
    user_id: str,
    current_stage: str,
    stage_started_at: str,
    active_path_themes: list[str],
    completed_path_themes: list[str],
    progress_snapshot: dict[str, Any],
    evolution_score_snapshot: int,
    last_evaluated_at: str,
    status: str = "active",
    cd: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build validated evolution user state referencing B1.1 CD."""
    registry = cd if cd is not None else load_evolution_cd_v1()

    gate = get_stage_gate_from_current_stage(current_stage, registry)
    gate_target = None
    if gate is not None:
        gate_target = {
            "gate_id": gate["gate_id"],
            "from_stage": gate["from_stage"],
            "to_stage": gate["to_stage"],
        }

    eligibility = build_stage_gate_eligibility_snapshot_v1(
        current_stage=current_stage,
        progress_snapshot=progress_snapshot,
        cd=registry,
    )

    state = {
        "contract_version": EVOLUTION_USER_STATE_V1_CONTRACT,
        "user_id": user_id,
        "current_stage": current_stage,
        "stage_started_at": stage_started_at,
        "active_path_themes": list(active_path_themes),
        "completed_path_themes": list(completed_path_themes),
        "current_stage_gate_target": gate_target,
        "stage_gate_eligibility": eligibility,
        "evolution_score_snapshot": evolution_score_snapshot,
        "last_evaluated_at": last_evaluated_at,
        "status": status,
        "version": EVOLUTION_USER_STATE_V1_VERSION,
    }

    errors = validate_evolution_user_state_v1(state, cd=registry)
    if errors:
        raise EvolutionUserStateError("; ".join(errors[:8]))
    return state


def validate_evolution_user_state_v1(
    state: dict[str, Any],
    *,
    cd: dict[str, Any] | None = None,
) -> list[str]:
    errors: list[str] = []

    if state.get("contract_version") != EVOLUTION_USER_STATE_V1_CONTRACT:
        errors.append("invalid contract_version")

    for key in EVOLUTION_USER_STATE_V1_KEYS:
        if key not in state:
            errors.append(f"missing field: {key}")

    errors.extend(_validate_forbidden_fields(state, recursive=True))

    registry = cd if cd is not None else load_evolution_cd_v1()
    stage_codes = set((registry.get("evolution_stages") or {}).keys())
    theme_codes = set((registry.get("evolution_path_themes") or {}).keys())

    current_stage = state.get("current_stage")
    if current_stage not in stage_codes:
        errors.append(f"unknown current_stage: {current_stage!r}")

    active = state.get("active_path_themes")
    completed = state.get("completed_path_themes")
    if not isinstance(active, list):
        errors.append("active_path_themes must be array")
        active = []
    if not isinstance(completed, list):
        errors.append("completed_path_themes must be array")
        completed = []

    if theme_codes:
        for theme in active:
            if theme not in theme_codes:
                errors.append(f"unknown active_path_theme: {theme!r}")
        for theme in completed:
            if theme not in theme_codes:
                errors.append(f"unknown completed_path_theme: {theme!r}")

    overlap = set(active) & set(completed)
    if overlap:
        errors.append(f"active and completed path themes overlap: {sorted(overlap)}")

    if state.get("status") not in ALLOWED_EVOLUTION_USER_STATE_STATUSES:
        errors.append("invalid status")

    score = state.get("evolution_score_snapshot")
    if not isinstance(score, int) or score < 0 or score > 1000:
        errors.append("evolution_score_snapshot must be int 0..1000")

    gate_target = state.get("current_stage_gate_target")
    if current_stage == "master":
        if gate_target is not None:
            errors.append("master stage must not have current_stage_gate_target")
    elif gate_target is None:
        if isinstance(current_stage, str) and current_stage in stage_codes:
            errors.append("current_stage_gate_target required for non-master stage")
    elif isinstance(gate_target, dict):
        if set(gate_target.keys()) != STAGE_GATE_TARGET_V1_KEYS:
            errors.append("current_stage_gate_target shape invalid")
        if gate_target.get("from_stage") != current_stage:
            errors.append("gate target from_stage must match current_stage")
        expected_next = _next_stage(current_stage)
        if expected_next is None or gate_target.get("to_stage") != expected_next:
            errors.append("current_stage_gate_target must be sequential")
    else:
        errors.append("current_stage_gate_target must be object or null")

    eligibility = state.get("stage_gate_eligibility")
    if current_stage == "master":
        if eligibility is not None:
            errors.append("master stage must not have stage_gate_eligibility")
    elif eligibility is None:
        errors.append("stage_gate_eligibility required for non-master stage")
    elif isinstance(eligibility, dict):
        errors.extend(
            validate_stage_gate_eligibility_v1(
                eligibility,
                current_stage=current_stage if isinstance(current_stage, str) else "",
            )
        )
        if gate_target is not None and eligibility.get("to_stage") != gate_target.get(
            "to_stage"
        ):
            errors.append("eligibility to_stage must match gate target")
    else:
        errors.append("stage_gate_eligibility must be object or null")

    if isinstance(current_stage, str) and current_stage in stage_codes:
        for theme in active:
            if theme not in theme_codes:
                continue
            theme_entry = get_evolution_path_theme(theme, registry)
            compatible = theme_entry.get("compatible_stages") or []
            if current_stage not in compatible:
                errors.append(
                    f"path theme {theme!r} not compatible with stage {current_stage!r}"
                )

    return errors


def validate_stage_gate_eligibility_v1(
    eligibility: dict[str, Any],
    *,
    current_stage: str,
) -> list[str]:
    errors: list[str] = []

    if set(eligibility.keys()) != STAGE_GATE_ELIGIBILITY_V1_KEYS:
        errors.append("stage_gate_eligibility shape invalid")

    if eligibility.get("promotion_allowed") is not False:
        errors.append("promotion_allowed must be false")

    if eligibility.get("from_stage") != current_stage:
        errors.append("eligibility from_stage must match current_stage")

    to_stage = eligibility.get("to_stage")
    expected_next = _next_stage(current_stage)
    if expected_next is None or to_stage != expected_next:
        errors.append("eligibility to_stage must be sequential next stage")

    if not isinstance(eligibility.get("eligible"), bool):
        errors.append("eligible must be bool")

    requirements = eligibility.get("requirements_snapshot")
    if not isinstance(requirements, dict):
        errors.append("requirements_snapshot must be object")
    elif set(requirements.keys()) != REQUIREMENTS_SNAPSHOT_V1_KEYS:
        errors.append("requirements_snapshot shape invalid")
    elif requirements:
        for sig in requirements.get("required_signal_types") or []:
            if isinstance(sig, str) and FORBIDDEN_STAGE_SOURCE_PATTERN.search(sig):
                errors.append(f"forbidden requirement signal: {sig!r}")

    progress = eligibility.get("progress_snapshot")
    if not isinstance(progress, dict):
        errors.append("progress_snapshot must be object")
    else:
        errors.extend(_validate_forbidden_fields(progress, recursive=True))
        if set(progress.keys()) != PROGRESS_SNAPSHOT_V1_KEYS:
            errors.append("progress_snapshot shape invalid")

    missing = eligibility.get("missing_requirements")
    if not isinstance(missing, list):
        errors.append("missing_requirements must be array")
    elif missing:
        for item in missing:
            if isinstance(item, str) and FORBIDDEN_STAGE_SOURCE_PATTERN.search(item):
                errors.append(f"forbidden missing_requirement: {item!r}")

    confidence = eligibility.get("confidence")
    if not isinstance(confidence, (int, float)) or confidence < 0 or confidence > 1:
        errors.append("confidence must be 0..1")

    return errors


def _next_stage(code: str) -> str | None:
    if code not in CANONICAL_STAGE_ORDER:
        return None
    index = CANONICAL_STAGE_ORDER.index(code)
    if index >= len(CANONICAL_STAGE_ORDER) - 1:
        return None
    return CANONICAL_STAGE_ORDER[index + 1]


def _normalize_progress_snapshot(progress_snapshot: dict[str, Any]) -> dict[str, Any]:
    signal_counts = progress_snapshot.get("signal_counts")
    if not isinstance(signal_counts, dict):
        signal_counts = {}
    normalized_signals: dict[str, int] = {}
    for key, value in signal_counts.items():
        if isinstance(key, str) and isinstance(value, int) and value >= 0:
            normalized_signals[key] = value

    confidence = progress_snapshot.get("confidence", 0.0)
    if not isinstance(confidence, (int, float)):
        confidence = 0.0

    return {
        "confirmed_patterns": _non_negative_int(progress_snapshot.get("confirmed_patterns")),
        "completed_cycles": _non_negative_int(progress_snapshot.get("completed_cycles")),
        "reflection_events": _non_negative_int(progress_snapshot.get("reflection_events")),
        "active_days": _non_negative_int(progress_snapshot.get("active_days")),
        "signal_counts": normalized_signals,
        "confidence": float(confidence),
    }


def _non_negative_int(value: Any) -> int:
    if isinstance(value, int) and value >= 0:
        return value
    return 0


def _compute_missing_requirements(
    requirements: dict[str, Any],
    progress: dict[str, Any],
) -> list[str]:
    missing: list[str] = []

    checks = (
        ("minimum_confirmed_patterns", "confirmed_patterns"),
        ("minimum_completed_cycles", "completed_cycles"),
        ("minimum_reflection_events", "reflection_events"),
        ("minimum_active_days", "active_days"),
    )
    for req_key, prog_key in checks:
        required = requirements.get(req_key, 0)
        actual = progress.get(prog_key, 0)
        if actual < required:
            missing.append(f"{prog_key}: need {required}, have {actual}")

    min_confidence = requirements.get("minimum_confidence", 0)
    if progress.get("confidence", 0) < min_confidence:
        missing.append(
            f"confidence: need {min_confidence}, have {progress.get('confidence', 0)}"
        )

    signal_counts = progress.get("signal_counts") or {}
    for signal_type in requirements.get("required_signal_types") or []:
        if signal_counts.get(signal_type, 0) < 1:
            missing.append(f"signal:{signal_type}")

    return missing


def _validate_forbidden_fields(
    payload: dict[str, Any],
    *,
    recursive: bool = False,
) -> list[str]:
    errors: list[str] = []
    for key, value in payload.items():
        if key in FORBIDDEN_EVOLUTION_STATE_FIELDS:
            errors.append(f"forbidden field: {key}")
        if FORBIDDEN_STAGE_SOURCE_PATTERN.search(key):
            errors.append(f"forbidden field name: {key}")
        if recursive and isinstance(value, dict):
            nested = _validate_forbidden_fields(value, recursive=True)
            errors.extend(nested)
    return errors

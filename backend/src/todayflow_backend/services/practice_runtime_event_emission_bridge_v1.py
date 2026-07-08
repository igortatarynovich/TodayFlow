"""C2.2 — Runtime event → emission bridge (C2.1 → C2.0 → B1.3)."""

from __future__ import annotations

from typing import Any

from todayflow_backend.services.practice_runtime_event_v1 import (
    validate_event_emission_path_v1,
    validate_practice_runtime_event_v1,
)
from todayflow_backend.services.practice_runtime_signal_emission_v1 import (
    FORBIDDEN_EMISSION_FIELDS,
    build_practice_runtime_signal_emission_v1,
    list_cd_allowed_signal_types,
    materialize_progression_signal_from_emission_v1,
)
from todayflow_backend.services.progression_signal_v1 import (
    FORBIDDEN_PROGRESSION_SIGNAL_FIELDS,
    VERIFICATION_STATUS_PENDING,
    VERIFICATION_STATUS_REJECTED,
    VERIFICATION_STATUS_VERIFIED,
)

BRIDGE_RESULT_EMISSION_CREATED = "emission_created"
BRIDGE_RESULT_REJECTED = "rejected"

MATERIALIZATION_RESULT_MATERIALIZED = "materialized"
MATERIALIZATION_RESULT_EMISSION_PENDING = "emission_pending"
MATERIALIZATION_RESULT_REJECTED = "rejected"


def _trace_from_event(event: dict[str, Any]) -> dict[str, Any]:
    return {
        "event_id": event.get("event_id"),
        "emission_id": None,
        "progression_signal_id": None,
    }


def _resolve_emittable_signal_type(event: dict[str, Any]) -> str | None:
    """Resolve signal type from event metadata. Returns None when conditions are not met."""
    event_kind = event.get("event_kind")
    metadata = event.get("metadata") or {}

    if event_kind == "ascetic_compliance_event":
        return None

    if event_kind == "practice_completed_event":
        return "practice_completed"

    if event_kind == "habit_streak_event":
        if metadata.get("threshold_met") is not True:
            return None
        return "habit_streak_confirmed"

    if event_kind == "goal_progress_event":
        progress = metadata.get("progress_value", 0)
        target = metadata.get("target_value", 1)
        if not isinstance(progress, int) or not isinstance(target, int) or progress < target:
            return None
        period_type = metadata.get("period_type")
        if period_type == "weekly":
            return "weekly_goal_completed"
        if period_type in {"milestone", "long_horizon"}:
            return "goal_milestone_reached"
        return None

    if event_kind == "ritual_streak_event":
        if metadata.get("threshold_met") is not True:
            return None
        return "ritual_streak_confirmed"

    if event_kind == "cycle_completion_event":
        rate = metadata.get("completion_rate", 0)
        threshold = metadata.get("required_threshold", 1)
        if not isinstance(rate, (int, float)) or not isinstance(threshold, (int, float)):
            return None
        if float(rate) < float(threshold):
            return None
        return "cycle_completed"

    return None


def try_build_emission_from_runtime_event_v1(
    event: dict[str, Any],
) -> dict[str, Any]:
    """
    Validate runtime event and build C2.0 emission when allowed.

    Bridge does not promote stage, mutate evolution state/score, or write profile/memory.
    """
    trace = _trace_from_event(event)

    validation_errors = validate_practice_runtime_event_v1(event)
    if validation_errors:
        return {
            "result": BRIDGE_RESULT_REJECTED,
            "emission": None,
            "reasons": validation_errors[:8],
            "trace": trace,
        }

    if event.get("runtime_entity_type") == "ascetic" or event.get("event_kind") == "ascetic_compliance_event":
        return {
            "result": BRIDGE_RESULT_REJECTED,
            "emission": None,
            "reasons": ["ascetic runtime events cannot emit signals in C2.2"],
            "trace": trace,
        }

    verification_status = event.get("verification_status")
    if verification_status == VERIFICATION_STATUS_REJECTED:
        return {
            "result": BRIDGE_RESULT_REJECTED,
            "emission": None,
            "reasons": ["rejected runtime events do not create emissions"],
            "trace": trace,
        }

    signal_type = _resolve_emittable_signal_type(event)
    if signal_type is None:
        return {
            "result": BRIDGE_RESULT_REJECTED,
            "emission": None,
            "reasons": ["runtime event does not resolve to an emittable signal type"],
            "trace": trace,
        }

    if verification_status == VERIFICATION_STATUS_VERIFIED:
        path_errors = validate_event_emission_path_v1(event)
        if path_errors:
            return {
                "result": BRIDGE_RESULT_REJECTED,
                "emission": None,
                "reasons": path_errors[:8],
                "trace": trace,
            }
    else:
        try:
            allowed = list_cd_allowed_signal_types(
                event["runtime_entity_type"],
                event["definition_code"],
            )
        except Exception as exc:
            return {
                "result": BRIDGE_RESULT_REJECTED,
                "emission": None,
                "reasons": [str(exc)],
                "trace": trace,
            }
        if signal_type not in allowed:
            return {
                "result": BRIDGE_RESULT_REJECTED,
                "emission": None,
                "reasons": [
                    f"signal type {signal_type!r} not allowed by CD for "
                    f"{event['runtime_entity_type']}:{event['definition_code']!r}"
                ],
                "trace": trace,
            }

    try:
        emission = build_practice_runtime_signal_emission_v1(
            user_id=event["user_id"],
            runtime_event_id=event["event_id"],
            runtime_entity_type=event["runtime_entity_type"],
            definition_code=event["definition_code"],
            emitted_signal_type=signal_type,
            verification_status=verification_status,
            confidence=float(event["confidence"]),
            occurred_at=event["occurred_at"],
        )
    except Exception as exc:
        return {
            "result": BRIDGE_RESULT_REJECTED,
            "emission": None,
            "reasons": [str(exc)],
            "trace": trace,
        }

    trace["emission_id"] = emission["emission_id"]
    return {
        "result": BRIDGE_RESULT_EMISSION_CREATED,
        "emission": emission,
        "reasons": [],
        "trace": trace,
    }


def try_materialize_progression_signal_from_runtime_event_v1(
    event: dict[str, Any],
    *,
    path_theme_code: str | None = None,
    evidence_count: int | None = None,
    evidence_window_days: int | None = None,
) -> dict[str, Any]:
    """
    Full path: event validation → emission → verified materialization → B1.3 signal.

    Pending events may yield emission_pending without progression signal.
    """
    trace = _trace_from_event(event)

    emission_outcome = try_build_emission_from_runtime_event_v1(event)
    if emission_outcome["result"] != BRIDGE_RESULT_EMISSION_CREATED:
        return {
            "result": MATERIALIZATION_RESULT_REJECTED,
            "emission": None,
            "progression_signal": None,
            "reasons": emission_outcome["reasons"],
            "trace": trace,
        }

    emission = emission_outcome["emission"]
    assert emission is not None
    trace["emission_id"] = emission["emission_id"]

    if emission["verification_status"] == VERIFICATION_STATUS_PENDING:
        return {
            "result": MATERIALIZATION_RESULT_EMISSION_PENDING,
            "emission": emission,
            "progression_signal": None,
            "reasons": [],
            "trace": trace,
        }

    if emission["verification_status"] == VERIFICATION_STATUS_REJECTED:
        return {
            "result": MATERIALIZATION_RESULT_REJECTED,
            "emission": None,
            "progression_signal": None,
            "reasons": ["rejected emission cannot materialize progression signal"],
            "trace": trace,
        }

    try:
        updated_emission, progression_signal = materialize_progression_signal_from_emission_v1(
            emission,
            path_theme_code=path_theme_code,
            evidence_count=evidence_count,
            evidence_window_days=evidence_window_days,
        )
    except Exception as exc:
        return {
            "result": MATERIALIZATION_RESULT_REJECTED,
            "emission": emission,
            "progression_signal": None,
            "reasons": [str(exc)],
            "trace": trace,
        }

    if progression_signal is None:
        return {
            "result": MATERIALIZATION_RESULT_REJECTED,
            "emission": updated_emission,
            "progression_signal": None,
            "reasons": ["verified emission did not materialize progression signal"],
            "trace": trace,
        }

    trace["progression_signal_id"] = progression_signal["progression_signal_id"]
    return {
        "result": MATERIALIZATION_RESULT_MATERIALIZED,
        "emission": updated_emission,
        "progression_signal": progression_signal,
        "reasons": [],
        "trace": trace,
    }


def validate_bridge_output_has_no_mutation_fields(
    emission: dict[str, Any] | None,
    progression_signal: dict[str, Any] | None,
) -> list[str]:
    """Guard that bridge outputs carry no promotion/profile/memory mutation fields."""
    errors: list[str] = []
    if emission:
        for key in emission:
            if key in FORBIDDEN_EMISSION_FIELDS:
                errors.append(f"emission forbidden field: {key}")
    if progression_signal:
        for key in progression_signal:
            if key in FORBIDDEN_PROGRESSION_SIGNAL_FIELDS:
                errors.append(f"progression_signal forbidden field: {key}")
    return errors

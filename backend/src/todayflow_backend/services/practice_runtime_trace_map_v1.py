"""C2.3 — Practice runtime trace map (audit layer: event → emission → signal → ES)."""

from __future__ import annotations

import re
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from todayflow_backend.services.evolution_score_v1 import EVOLUTION_SCORE_CALCULATION_V1_CONTRACT
from todayflow_backend.services.evolution_user_state_v1 import EVOLUTION_USER_STATE_V1_CONTRACT
from todayflow_backend.services.practice_runtime_event_v1 import PRACTICE_RUNTIME_EVENT_V1_CONTRACT
from todayflow_backend.services.practice_runtime_signal_emission_v1 import (
    PRACTICE_RUNTIME_SIGNAL_EMISSION_V1_CONTRACT,
)
from todayflow_backend.services.progression_signal_v1 import (
    PROGRESSION_SIGNAL_V1_CONTRACT,
    VERIFICATION_STATUS_REJECTED,
)

PRACTICE_RUNTIME_TRACE_MAP_V1_CONTRACT = "practice_runtime_trace_map_v1"
PRACTICE_RUNTIME_TRACE_MAP_V1_VERSION = "1.0.0"

TRACE_STATUS_COMPLETE = "complete"
TRACE_STATUS_PARTIAL = "partial"
TRACE_STATUS_FAILED = "failed"

ALLOWED_TRACE_STATUSES = frozenset(
    {
        TRACE_STATUS_COMPLETE,
        TRACE_STATUS_PARTIAL,
        TRACE_STATUS_FAILED,
    }
)

ALLOWED_MISSING_LINKS = frozenset(
    {
        "runtime_event",
        "emission",
        "progression_signal",
        "eligibility_snapshot",
        "evolution_score_snapshot",
    }
)

PRACTICE_RUNTIME_TRACE_MAP_V1_KEYS = frozenset(
    {
        "contract_version",
        "trace_map_id",
        "user_id",
        "runtime_event_id",
        "emission_id",
        "progression_signal_id",
        "eligibility_snapshot_id",
        "evolution_score_snapshot_id",
        "runtime_entity_type",
        "definition_code",
        "signal_type",
        "trace_status",
        "missing_links",
        "created_at",
        "mutation_allowed",
        "version",
    }
)

FORBIDDEN_TRACE_MAP_FIELDS = frozenset(
    {
        "promotion_allowed",
        "promoted_stage",
        "stage_promoted_at",
        "current_stage",
        "evolution_score",
        "evolution_state",
        "achievement_id",
        "reward_id",
        "profile_update",
        "memory_write",
        "commerce_hook",
    }
)

FORBIDDEN_TRACE_MAP_FIELD_PATTERN = re.compile(
    r"(achievement|commerce|unlock|purchase|reward|badge|payment|subscription|promotion|memory|profile|stage)",
    re.I,
)


class PracticeRuntimeTraceMapError(ValueError):
    """Raised when trace map inputs or payload are invalid."""


def _utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def resolve_eligibility_snapshot_id_from_user_state_v1(
    evolution_user_state: dict[str, Any],
) -> str | None:
    """Derive B1.2 eligibility snapshot ref from an existing user state artifact."""
    if evolution_user_state.get("contract_version") != EVOLUTION_USER_STATE_V1_CONTRACT:
        return None
    if evolution_user_state.get("stage_gate_eligibility") is None:
        return None
    user_id = evolution_user_state.get("user_id")
    evaluated_at = evolution_user_state.get("last_evaluated_at")
    if not isinstance(user_id, str) or not isinstance(evaluated_at, str):
        return None
    return f"eligibility_snapshot_v1:{user_id}:{evaluated_at}"


def resolve_evolution_score_snapshot_id_from_calculation_v1(
    evolution_score_calculation: dict[str, Any],
) -> str | None:
    """Derive B1.4 evolution score snapshot ref from an existing calculation artifact."""
    if evolution_score_calculation.get("contract_version") != EVOLUTION_SCORE_CALCULATION_V1_CONTRACT:
        return None
    user_id = evolution_score_calculation.get("user_id")
    calculated_at = evolution_score_calculation.get("calculated_at")
    if not isinstance(user_id, str) or not isinstance(calculated_at, str):
        return None
    return f"evolution_score_snapshot_v1:{user_id}:{calculated_at}"


def _failed_trace_reasons(
    event: dict[str, Any],
    emission: dict[str, Any] | None,
) -> list[str]:
    reasons: list[str] = []
    if event.get("verification_status") == VERIFICATION_STATUS_REJECTED:
        reasons.append("rejected_event")
    if event.get("runtime_entity_type") == "ascetic" or event.get("event_kind") == "ascetic_compliance_event":
        reasons.append("ascetic_blocked")
    if emission is None and not reasons:
        if event.get("verification_status") != VERIFICATION_STATUS_REJECTED:
            reasons.append("emission_blocked")
    return reasons


def _compute_missing_links(
    *,
    runtime_event_id: str | None,
    emission_id: str | None,
    progression_signal_id: str | None,
    eligibility_snapshot_id: str | None,
    evolution_score_snapshot_id: str | None,
) -> list[str]:
    missing: list[str] = []
    if not runtime_event_id:
        missing.append("runtime_event")
    if not emission_id:
        missing.append("emission")
    if not progression_signal_id:
        missing.append("progression_signal")
    if not eligibility_snapshot_id:
        missing.append("eligibility_snapshot")
    if not evolution_score_snapshot_id:
        missing.append("evolution_score_snapshot")
    return missing


def _compute_trace_status(
    failed_reasons: list[str],
    missing_links: list[str],
) -> str:
    if failed_reasons:
        return TRACE_STATUS_FAILED
    required = frozenset(
        {
            "emission",
            "progression_signal",
            "eligibility_snapshot",
            "evolution_score_snapshot",
        }
    )
    if required.isdisjoint(missing_links) and "runtime_event" not in missing_links:
        return TRACE_STATUS_COMPLETE
    return TRACE_STATUS_PARTIAL


def _resolve_signal_type(
    *,
    progression_signal: dict[str, Any] | None,
    emission: dict[str, Any] | None,
) -> str | None:
    if progression_signal is not None:
        signal_type = progression_signal.get("signal_type")
        if isinstance(signal_type, str):
            return signal_type
    if emission is not None:
        emitted = emission.get("emitted_signal_type")
        if isinstance(emitted, str):
            return emitted
    return None


def build_practice_runtime_trace_map_v1(
    *,
    event: dict[str, Any],
    emission: dict[str, Any] | None = None,
    progression_signal: dict[str, Any] | None = None,
    eligibility_snapshot_id: str | None = None,
    evolution_score_snapshot_id: str | None = None,
    trace_map_id: str | None = None,
    created_at: str | None = None,
) -> dict[str, Any]:
    """
    Link existing runtime artifacts into a read-only trace map.

    Does not create events, emissions, signals, eligibility, or score snapshots.
    """
    runtime_event_id = event.get("event_id")
    emission_id = emission.get("emission_id") if emission else None
    progression_signal_id = (
        progression_signal.get("progression_signal_id") if progression_signal else None
    )
    if emission is not None and emission.get("progression_signal_id") and progression_signal_id is None:
        progression_signal_id = emission.get("progression_signal_id")

    failed_reasons = _failed_trace_reasons(event, emission)
    missing_links = _compute_missing_links(
        runtime_event_id=runtime_event_id if isinstance(runtime_event_id, str) else None,
        emission_id=emission_id if isinstance(emission_id, str) else None,
        progression_signal_id=progression_signal_id if isinstance(progression_signal_id, str) else None,
        eligibility_snapshot_id=eligibility_snapshot_id,
        evolution_score_snapshot_id=evolution_score_snapshot_id,
    )
    trace_status = _compute_trace_status(failed_reasons, missing_links)

    trace_map = {
        "contract_version": PRACTICE_RUNTIME_TRACE_MAP_V1_CONTRACT,
        "trace_map_id": trace_map_id or str(uuid4()),
        "user_id": event.get("user_id"),
        "runtime_event_id": runtime_event_id,
        "emission_id": emission_id,
        "progression_signal_id": progression_signal_id,
        "eligibility_snapshot_id": eligibility_snapshot_id,
        "evolution_score_snapshot_id": evolution_score_snapshot_id,
        "runtime_entity_type": event.get("runtime_entity_type"),
        "definition_code": event.get("definition_code"),
        "signal_type": _resolve_signal_type(
            progression_signal=progression_signal,
            emission=emission,
        ),
        "trace_status": trace_status,
        "missing_links": missing_links,
        "created_at": created_at or _utc_now_iso(),
        "mutation_allowed": False,
        "version": PRACTICE_RUNTIME_TRACE_MAP_V1_VERSION,
    }

    errors = validate_practice_runtime_trace_map_v1(
        trace_map,
        event=event,
        emission=emission,
        progression_signal=progression_signal,
    )
    if errors:
        raise PracticeRuntimeTraceMapError("; ".join(errors[:8]))
    return trace_map


def validate_practice_runtime_trace_map_v1(
    trace_map: dict[str, Any],
    *,
    event: dict[str, Any] | None = None,
    emission: dict[str, Any] | None = None,
    progression_signal: dict[str, Any] | None = None,
) -> list[str]:
    errors: list[str] = []

    if trace_map.get("contract_version") != PRACTICE_RUNTIME_TRACE_MAP_V1_CONTRACT:
        errors.append("invalid contract_version")

    for key in PRACTICE_RUNTIME_TRACE_MAP_V1_KEYS:
        if key not in trace_map:
            errors.append(f"missing field: {key}")

    for key in trace_map:
        if key in FORBIDDEN_TRACE_MAP_FIELDS:
            errors.append(f"forbidden field: {key}")
        if FORBIDDEN_TRACE_MAP_FIELD_PATTERN.search(key):
            errors.append(f"forbidden field name: {key}")

    if trace_map.get("mutation_allowed") is not False:
        errors.append("mutation_allowed must be false")

    trace_status = trace_map.get("trace_status")
    if trace_status not in ALLOWED_TRACE_STATUSES:
        errors.append("invalid trace_status")

    missing_links = trace_map.get("missing_links")
    if not isinstance(missing_links, list):
        errors.append("missing_links must be array")
    else:
        for link in missing_links:
            if link not in ALLOWED_MISSING_LINKS:
                errors.append(f"invalid missing_link: {link!r}")

    expected_missing = _compute_missing_links(
        runtime_event_id=trace_map.get("runtime_event_id"),
        emission_id=trace_map.get("emission_id"),
        progression_signal_id=trace_map.get("progression_signal_id"),
        eligibility_snapshot_id=trace_map.get("eligibility_snapshot_id"),
        evolution_score_snapshot_id=trace_map.get("evolution_score_snapshot_id"),
    )
    if isinstance(missing_links, list) and missing_links != expected_missing:
        errors.append("missing_links must reflect absent artifact refs")

    if event is not None:
        if event.get("contract_version") != PRACTICE_RUNTIME_EVENT_V1_CONTRACT:
            errors.append("event contract_version invalid")
        if trace_map.get("runtime_event_id") != event.get("event_id"):
            errors.append("runtime_event_id must match event.event_id")
        if trace_map.get("user_id") != event.get("user_id"):
            errors.append("user_id must match event.user_id")
        if trace_map.get("runtime_entity_type") != event.get("runtime_entity_type"):
            errors.append("runtime_entity_type must match event")
        if trace_map.get("definition_code") != event.get("definition_code"):
            errors.append("definition_code must match event")

    if emission is not None:
        if emission.get("contract_version") != PRACTICE_RUNTIME_SIGNAL_EMISSION_V1_CONTRACT:
            errors.append("emission contract_version invalid")
        if trace_map.get("emission_id") != emission.get("emission_id"):
            errors.append("emission_id must match emission.emission_id")
        if event is not None and emission.get("runtime_event_id") != event.get("event_id"):
            errors.append("emission.runtime_event_id must match event.event_id")

    if progression_signal is not None:
        if progression_signal.get("contract_version") != PROGRESSION_SIGNAL_V1_CONTRACT:
            errors.append("progression_signal contract_version invalid")
        if trace_map.get("progression_signal_id") != progression_signal.get("progression_signal_id"):
            errors.append("progression_signal_id must match progression_signal")
        if event is not None and progression_signal.get("source_event_id") != event.get("event_id"):
            errors.append("progression_signal.source_event_id must match event.event_id")

    if trace_status == TRACE_STATUS_COMPLETE:
        for field in (
            "runtime_event_id",
            "emission_id",
            "progression_signal_id",
            "eligibility_snapshot_id",
            "evolution_score_snapshot_id",
            "signal_type",
        ):
            if not trace_map.get(field):
                errors.append(f"complete trace requires {field}")

    if trace_status == TRACE_STATUS_FAILED and event is not None:
        failed_reasons = _failed_trace_reasons(event, emission)
        if not failed_reasons:
            errors.append("failed trace_status requires failed event or blocked emission")

    return errors

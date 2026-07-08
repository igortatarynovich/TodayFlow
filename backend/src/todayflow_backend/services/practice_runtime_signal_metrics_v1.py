"""C2.4 — Practice runtime signal metrics (read-only observability over Branch C chain)."""

from __future__ import annotations

import re
from collections import Counter
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from todayflow_backend.services.practice_runtime_event_emission_bridge_v1 import (
    BRIDGE_RESULT_REJECTED,
)
from todayflow_backend.services.practice_runtime_event_v1 import PRACTICE_RUNTIME_EVENT_V1_CONTRACT
from todayflow_backend.services.practice_runtime_signal_emission_v1 import (
    PRACTICE_RUNTIME_SIGNAL_EMISSION_V1_CONTRACT,
)
from todayflow_backend.services.practice_runtime_trace_map_v1 import (
    PRACTICE_RUNTIME_TRACE_MAP_V1_CONTRACT,
    TRACE_STATUS_COMPLETE,
    TRACE_STATUS_FAILED,
    TRACE_STATUS_PARTIAL,
)
from todayflow_backend.services.progression_signal_v1 import (
    PROGRESSION_SIGNAL_V1_CONTRACT,
    VERIFICATION_STATUS_PENDING,
    VERIFICATION_STATUS_REJECTED,
    VERIFICATION_STATUS_VERIFIED,
)

PRACTICE_RUNTIME_SIGNAL_METRICS_V1_CONTRACT = "practice_runtime_signal_metrics_v1"
PRACTICE_RUNTIME_SIGNAL_METRICS_V1_VERSION = "1.0.0"

EVENT_METRICS_KEYS = frozenset(
    {
        "event_count",
        "verified_event_count",
        "pending_event_count",
        "rejected_event_count",
    }
)

EMISSION_METRICS_KEYS = frozenset(
    {
        "emission_count",
        "verified_emission_count",
        "pending_emission_count",
        "blocked_emission_count",
    }
)

SIGNAL_METRICS_KEYS = frozenset({"materialized_signal_count"})

TRACE_METRICS_KEYS = frozenset(
    {
        "complete_trace_count",
        "partial_trace_count",
        "failed_trace_count",
    }
)

DISTRIBUTIONS_KEYS = frozenset(
    {
        "signal_type_distribution",
        "runtime_entity_distribution",
        "definition_code_distribution",
        "blocked_reason_distribution",
    }
)

PRACTICE_RUNTIME_SIGNAL_METRICS_V1_KEYS = frozenset(
    {
        "contract_version",
        "metrics_id",
        "window_start",
        "window_end",
        "event_metrics",
        "emission_metrics",
        "signal_metrics",
        "trace_metrics",
        "distributions",
        "created_at",
        "read_only",
        "promotion_allowed",
        "profile_update_allowed",
        "memory_update_allowed",
        "version",
    }
)

FORBIDDEN_METRICS_FIELDS = frozenset(
    {
        "evolution_score",
        "evolution_state",
        "current_stage",
        "promoted_stage",
        "achievement_id",
        "reward_id",
        "memory_write",
        "profile_update",
        "recommendation_id",
        "commerce_hook",
    }
)

FORBIDDEN_METRICS_FIELD_PATTERN = re.compile(
    r"(achievement|commerce|unlock|purchase|reward|badge|payment|subscription|recommendation)",
    re.I,
)


class PracticeRuntimeSignalMetricsError(ValueError):
    """Raised when metrics inputs or payload are invalid."""


def _utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _timestamp_in_window(value: str | None, window_start: str, window_end: str) -> bool:
    if not isinstance(value, str) or not value:
        return False
    return window_start <= value <= window_end


def _filter_by_window(
    items: list[dict[str, Any]],
    *,
    timestamp_field: str,
    window_start: str,
    window_end: str,
) -> list[dict[str, Any]]:
    return [
        item
        for item in items
        if _timestamp_in_window(item.get(timestamp_field), window_start, window_end)
    ]


def _normalize_blocked_reason(reason: str) -> str:
    lower = reason.lower()
    if "ascetic" in lower:
        return "ascetic_blocked"
    if "rejected runtime events" in lower or reason == "rejected_event":
        return "rejected_event"
    if "does not resolve" in lower or reason == "emission_blocked":
        return "emission_blocked"
    if "not allowed" in lower:
        return "cd_signal_disallowed"
    if "invalid" in lower or "missing field" in lower:
        return "validation_failed"
    return reason if reason else "other_blocked"


def _collect_blocked_reasons(
    events: list[dict[str, Any]],
    emissions: list[dict[str, Any]],
    trace_maps: list[dict[str, Any]],
    bridge_outcomes: list[dict[str, Any]] | None,
) -> Counter[str]:
    reasons: Counter[str] = Counter()

    emission_event_ids = {
        emission.get("runtime_event_id")
        for emission in emissions
        if isinstance(emission.get("runtime_event_id"), str)
    }

    for event in events:
        if event.get("verification_status") == VERIFICATION_STATUS_REJECTED:
            reasons["rejected_event"] += 1
        elif event.get("runtime_entity_type") == "ascetic" or event.get("event_kind") == "ascetic_compliance_event":
            reasons["ascetic_blocked"] += 1
        elif event.get("event_id") not in emission_event_ids:
            if event.get("verification_status") != VERIFICATION_STATUS_PENDING:
                reasons["emission_blocked"] += 1

    for emission in emissions:
        if emission.get("verification_status") == VERIFICATION_STATUS_REJECTED:
            reasons["rejected_emission"] += 1

    for trace_map in trace_maps:
        if trace_map.get("trace_status") == TRACE_STATUS_FAILED:
            reasons["failed_trace"] += 1

    for outcome in bridge_outcomes or []:
        if outcome.get("result") != BRIDGE_RESULT_REJECTED:
            continue
        for reason in outcome.get("reasons") or []:
            if isinstance(reason, str):
                reasons[_normalize_blocked_reason(reason)] += 1

    return reasons


def build_practice_runtime_signal_metrics_v1(
    *,
    window_start: str,
    window_end: str,
    events: list[dict[str, Any]] | None = None,
    emissions: list[dict[str, Any]] | None = None,
    progression_signals: list[dict[str, Any]] | None = None,
    trace_maps: list[dict[str, Any]] | None = None,
    bridge_outcomes: list[dict[str, Any]] | None = None,
    metrics_id: str | None = None,
    created_at: str | None = None,
) -> dict[str, Any]:
    """
    Aggregate read-only metrics from existing Branch C runtime artifacts.

    Does not create signals, recalculate ES, mutate eligibility, or write profile/memory.
    """
    if window_start > window_end:
        raise PracticeRuntimeSignalMetricsError("window_start must be <= window_end")

    scoped_events = _filter_by_window(
        list(events or []),
        timestamp_field="occurred_at",
        window_start=window_start,
        window_end=window_end,
    )
    scoped_emissions = _filter_by_window(
        list(emissions or []),
        timestamp_field="occurred_at",
        window_start=window_start,
        window_end=window_end,
    )
    scoped_signals = _filter_by_window(
        list(progression_signals or []),
        timestamp_field="observed_at",
        window_start=window_start,
        window_end=window_end,
    )
    scoped_traces = _filter_by_window(
        list(trace_maps or []),
        timestamp_field="created_at",
        window_start=window_start,
        window_end=window_end,
    )

    event_metrics = {
        "event_count": len(scoped_events),
        "verified_event_count": sum(
            1 for event in scoped_events if event.get("verification_status") == VERIFICATION_STATUS_VERIFIED
        ),
        "pending_event_count": sum(
            1 for event in scoped_events if event.get("verification_status") == VERIFICATION_STATUS_PENDING
        ),
        "rejected_event_count": sum(
            1 for event in scoped_events if event.get("verification_status") == VERIFICATION_STATUS_REJECTED
        ),
    }

    rejected_emission_count = sum(
        1 for emission in scoped_emissions if emission.get("verification_status") == VERIFICATION_STATUS_REJECTED
    )
    emission_event_ids = {
        emission.get("runtime_event_id")
        for emission in scoped_emissions
        if isinstance(emission.get("runtime_event_id"), str)
    }
    if bridge_outcomes is not None:
        blocked_attempt_count = sum(
            1 for outcome in bridge_outcomes if outcome.get("result") == BRIDGE_RESULT_REJECTED
        )
    else:
        blocked_attempt_count = sum(
            1
            for event in scoped_events
            if event.get("event_id") not in emission_event_ids
            and event.get("verification_status") != VERIFICATION_STATUS_PENDING
        )

    emission_metrics = {
        "emission_count": len(scoped_emissions),
        "verified_emission_count": sum(
            1 for emission in scoped_emissions if emission.get("verification_status") == VERIFICATION_STATUS_VERIFIED
        ),
        "pending_emission_count": sum(
            1 for emission in scoped_emissions if emission.get("verification_status") == VERIFICATION_STATUS_PENDING
        ),
        "blocked_emission_count": rejected_emission_count + blocked_attempt_count,
    }

    signal_metrics = {
        "materialized_signal_count": len(scoped_signals),
    }

    trace_metrics = {
        "complete_trace_count": sum(
            1 for trace_map in scoped_traces if trace_map.get("trace_status") == TRACE_STATUS_COMPLETE
        ),
        "partial_trace_count": sum(
            1 for trace_map in scoped_traces if trace_map.get("trace_status") == TRACE_STATUS_PARTIAL
        ),
        "failed_trace_count": sum(
            1 for trace_map in scoped_traces if trace_map.get("trace_status") == TRACE_STATUS_FAILED
        ),
    }

    signal_type_distribution: Counter[str] = Counter()
    for signal in scoped_signals:
        signal_type = signal.get("signal_type")
        if isinstance(signal_type, str):
            signal_type_distribution[signal_type] += 1

    runtime_entity_distribution: Counter[str] = Counter()
    definition_code_distribution: Counter[str] = Counter()
    for event in scoped_events:
        entity = event.get("runtime_entity_type")
        code = event.get("definition_code")
        if isinstance(entity, str):
            runtime_entity_distribution[entity] += 1
        if isinstance(code, str):
            definition_code_distribution[code] += 1

    blocked_reason_distribution = _collect_blocked_reasons(
        scoped_events,
        scoped_emissions,
        scoped_traces,
        bridge_outcomes,
    )

    metrics = {
        "contract_version": PRACTICE_RUNTIME_SIGNAL_METRICS_V1_CONTRACT,
        "metrics_id": metrics_id or str(uuid4()),
        "window_start": window_start,
        "window_end": window_end,
        "event_metrics": event_metrics,
        "emission_metrics": emission_metrics,
        "signal_metrics": signal_metrics,
        "trace_metrics": trace_metrics,
        "distributions": {
            "signal_type_distribution": dict(sorted(signal_type_distribution.items())),
            "runtime_entity_distribution": dict(sorted(runtime_entity_distribution.items())),
            "definition_code_distribution": dict(sorted(definition_code_distribution.items())),
            "blocked_reason_distribution": dict(sorted(blocked_reason_distribution.items())),
        },
        "created_at": created_at or _utc_now_iso(),
        "read_only": True,
        "promotion_allowed": False,
        "profile_update_allowed": False,
        "memory_update_allowed": False,
        "version": PRACTICE_RUNTIME_SIGNAL_METRICS_V1_VERSION,
    }

    errors = validate_practice_runtime_signal_metrics_v1(metrics)
    if errors:
        raise PracticeRuntimeSignalMetricsError("; ".join(errors[:8]))
    return metrics


def validate_practice_runtime_signal_metrics_v1(metrics: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    if metrics.get("contract_version") != PRACTICE_RUNTIME_SIGNAL_METRICS_V1_CONTRACT:
        errors.append("invalid contract_version")

    for key in PRACTICE_RUNTIME_SIGNAL_METRICS_V1_KEYS:
        if key not in metrics:
            errors.append(f"missing field: {key}")

    for key in metrics:
        if key in FORBIDDEN_METRICS_FIELDS:
            errors.append(f"forbidden field: {key}")
        if FORBIDDEN_METRICS_FIELD_PATTERN.search(key):
            errors.append(f"forbidden field name: {key}")

    if metrics.get("read_only") is not True:
        errors.append("read_only must be true")
    if metrics.get("promotion_allowed") is not False:
        errors.append("promotion_allowed must be false")
    if metrics.get("profile_update_allowed") is not False:
        errors.append("profile_update_allowed must be false")
    if metrics.get("memory_update_allowed") is not False:
        errors.append("memory_update_allowed must be false")

    window_start = metrics.get("window_start")
    window_end = metrics.get("window_end")
    if not isinstance(window_start, str) or not isinstance(window_end, str):
        errors.append("window_start and window_end must be strings")
    elif window_start > window_end:
        errors.append("window_start must be <= window_end")

    event_metrics = metrics.get("event_metrics")
    if not isinstance(event_metrics, dict):
        errors.append("event_metrics must be object")
    elif set(event_metrics.keys()) != EVENT_METRICS_KEYS:
        errors.append("event_metrics shape invalid")
    elif isinstance(event_metrics, dict):
        total = event_metrics.get("event_count", 0)
        parts = (
            event_metrics.get("verified_event_count", 0)
            + event_metrics.get("pending_event_count", 0)
            + event_metrics.get("rejected_event_count", 0)
        )
        if isinstance(total, int) and isinstance(parts, int) and total != parts:
            errors.append("event_metrics counts must sum to event_count")

    emission_metrics = metrics.get("emission_metrics")
    if not isinstance(emission_metrics, dict):
        errors.append("emission_metrics must be object")
    elif set(emission_metrics.keys()) != EMISSION_METRICS_KEYS:
        errors.append("emission_metrics shape invalid")

    signal_metrics = metrics.get("signal_metrics")
    if not isinstance(signal_metrics, dict):
        errors.append("signal_metrics must be object")
    elif set(signal_metrics.keys()) != SIGNAL_METRICS_KEYS:
        errors.append("signal_metrics shape invalid")

    trace_metrics = metrics.get("trace_metrics")
    if not isinstance(trace_metrics, dict):
        errors.append("trace_metrics must be object")
    elif set(trace_metrics.keys()) != TRACE_METRICS_KEYS:
        errors.append("trace_metrics shape invalid")

    distributions = metrics.get("distributions")
    if not isinstance(distributions, dict):
        errors.append("distributions must be object")
    elif set(distributions.keys()) != DISTRIBUTIONS_KEYS:
        errors.append("distributions shape invalid")
    elif isinstance(distributions, dict):
        for key in DISTRIBUTIONS_KEYS:
            value = distributions.get(key)
            if not isinstance(value, dict):
                errors.append(f"distributions.{key} must be object")
            else:
                for dist_key, dist_val in value.items():
                    if not isinstance(dist_key, str):
                        errors.append(f"distributions.{key} keys must be strings")
                    if not isinstance(dist_val, int) or dist_val < 0:
                        errors.append(f"distributions.{key}.{dist_key} must be non-negative int")

    return errors


def validate_metrics_input_artifact(
    artifact: dict[str, Any],
    *,
    kind: str,
) -> list[str]:
    """Optional guard when aggregating known contract artifacts."""
    contracts = {
        "event": PRACTICE_RUNTIME_EVENT_V1_CONTRACT,
        "emission": PRACTICE_RUNTIME_SIGNAL_EMISSION_V1_CONTRACT,
        "progression_signal": PROGRESSION_SIGNAL_V1_CONTRACT,
        "trace_map": PRACTICE_RUNTIME_TRACE_MAP_V1_CONTRACT,
    }
    expected = contracts.get(kind)
    if expected is None:
        return [f"unknown artifact kind: {kind!r}"]
    if artifact.get("contract_version") != expected:
        return [f"invalid contract_version for {kind}"]
    return []

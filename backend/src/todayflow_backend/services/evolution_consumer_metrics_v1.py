"""B1.14 — Evolution consumer metrics (read-only observability over B1.8–B1.13 artifacts)."""

from __future__ import annotations

from collections import Counter
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from todayflow_backend.services.evolution_calendar_runtime_policy_v1 import (
    BLOCK_CALENDAR_SYSTEM_NOT_READY,
    EVOLUTION_CALENDAR_RUNTIME_POLICY_V1_CONTRACT,
)
from todayflow_backend.services.evolution_commerce_visibility_policy_v1 import (
    BLOCK_COMMERCE_NOT_READY,
    EVOLUTION_COMMERCE_VISIBILITY_POLICY_V1_CONTRACT,
)
from todayflow_backend.services.evolution_context_selector_wiring_v1 import (
    EXCLUSION_EVOLUTION_CAP,
)
from todayflow_backend.services.evolution_day_presentation_envelope_v1 import (
    EVOLUTION_DAY_PRESENTATION_ENVELOPE_V1_CONTRACT,
)
from todayflow_backend.services.evolution_effect_consumer_map_v1 import (
    CONSUMER_CALENDAR,
    CONSUMER_COMMERCE_VISIBILITY,
    CONSUMER_CONTEXT_SELECTOR,
    CONSUMER_DAY_ENGINE,
    CONSUMER_LLM_GATE,
    CONSUMER_PRACTICE_SELECTOR,
    list_registered_consumers_v1,
)
from todayflow_backend.services.evolution_practice_selector_filter_v1 import (
    EVOLUTION_PRACTICE_SELECTOR_FILTER_V1_CONTRACT,
)
from todayflow_backend.services.day_model_v1_llm_call_gate import (
    DAY_CONTENT_LLM_GATE_V1_CONTRACT,
    DECISION_NO_CALL,
)

EVOLUTION_CONSUMER_METRICS_V1_VERSION = "1.0.0"

EVOLUTION_CONSUMER_METRICS_V1_CONTRACT = "evolution_consumer_metrics_v1"

SLICE_APPLIED = "applied"
SLICE_IGNORED = "ignored"
SLICE_INVALID = "invalid"

EVOLUTION_CONSUMER_METRICS_V1_KEYS = frozenset(
    {
        "contract_version",
        "metrics_id",
        "window_start",
        "window_end",
        "consumer_counts",
        "slice_application_counts",
        "cap_counts",
        "block_reason_distribution",
        "stage_distribution",
        "readiness_blocks",
        "read_only",
        "promotion_allowed",
        "profile_update_allowed",
        "memory_update_allowed",
        "created_at",
    }
)

FORBIDDEN_METRICS_FIELDS = frozenset(
    {
        "recommendation",
        "sku",
        "product_id",
        "targeting",
        "stage_update",
        "promoted_stage",
        "score",
        "llm_call",
        "commerce_activation",
    }
)

REGISTERED_CONSUMERS = frozenset(list_registered_consumers_v1())


class EvolutionConsumerMetricsError(ValueError):
    """Raised when consumer metrics inputs or payload are invalid."""


def _utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def generate_evolution_consumer_metrics_id() -> str:
    return f"ecm-{uuid4()}"


def _empty_counter_dict(keys: frozenset[str] | set[str]) -> dict[str, int]:
    return {key: 0 for key in sorted(keys)}


def _cap_reason(artifact: dict[str, Any]) -> str | None:
    reason = artifact.get("cap_reason")
    if reason is None:
        reason = artifact.get("evolution_cap_reason")
    return str(reason) if reason is not None else None


def _classify_slice_application(consumer_id: str, artifact: dict[str, Any]) -> str:
    if consumer_id in {CONSUMER_LLM_GATE, CONSUMER_CONTEXT_SELECTOR}:
        if artifact.get("evolution_slice_applied") is True:
            return SLICE_APPLIED
        reason = _cap_reason(artifact) or ""
        if reason == "no_evolution_slice":
            return SLICE_IGNORED
        if reason.startswith("ignored:"):
            return SLICE_IGNORED
        if "invalid" in reason or "full_policy" in reason:
            return SLICE_INVALID
        return SLICE_IGNORED

    if consumer_id == CONSUMER_DAY_ENGINE:
        blocked = artifact.get("blocked_effects") or []
        if artifact.get("evolution_stage") and artifact.get("source_evolution_slice_id"):
            return SLICE_APPLIED
        if any(str(item).startswith("ignored:") for item in blocked):
            return SLICE_IGNORED
        if any("invalid" in str(item) or "full_policy" in str(item) for item in blocked):
            return SLICE_INVALID
        return SLICE_IGNORED

    if consumer_id == CONSUMER_PRACTICE_SELECTOR:
        if artifact.get("evolution_stage") and artifact.get("source_evolution_slice_id"):
            return SLICE_APPLIED
        return SLICE_IGNORED

    if consumer_id == CONSUMER_CALENDAR:
        blocked = artifact.get("blocked_calendar_effects") or []
        if artifact.get("evolution_stage") and artifact.get("source_evolution_slice_id"):
            return SLICE_APPLIED
        if "invalid_evolution_slice" in blocked or "full_policy_passed" in blocked:
            return SLICE_INVALID
        if not artifact.get("source_evolution_slice_id") and blocked:
            return SLICE_INVALID
        return SLICE_IGNORED

    if consumer_id == CONSUMER_COMMERCE_VISIBILITY:
        blocked = {entry.get("reason") for entry in artifact.get("blocked_surfaces") or []}
        if artifact.get("evolution_stage") and artifact.get("source_evolution_slice_id"):
            return SLICE_APPLIED
        if "invalid_evolution_slice" in blocked or "full_policy_passed" in blocked:
            return SLICE_INVALID
        return SLICE_IGNORED

    return SLICE_IGNORED


def _extract_stage(consumer_id: str, artifact: dict[str, Any], entry: dict[str, Any]) -> str | None:
    if entry.get("evolution_stage"):
        return str(entry["evolution_stage"])
    stage = artifact.get("evolution_stage")
    if stage:
        return str(stage)
    if consumer_id == CONSUMER_LLM_GATE and artifact.get("evolution_slice_applied"):
        return entry.get("source_stage")
    if consumer_id == CONSUMER_CONTEXT_SELECTOR and artifact.get("evolution_slice_applied"):
        return entry.get("source_stage")
    return None


def _collect_llm_gate_metrics(
    artifact: dict[str, Any],
    cap_counts: Counter[str],
    block_reasons: Counter[str],
) -> None:
    if artifact.get("contract_version") != DAY_CONTENT_LLM_GATE_V1_CONTRACT:
        return

    if artifact.get("evolution_slice_applied") is True:
        cap_counts["llm_slice_applied"] += 1

    blocked = artifact.get("blocked_escalations") or []
    for item in blocked:
        block_reasons[str(item)] += 1
        if str(item).startswith("model_tier:"):
            cap_counts["llm_tier_capped"] += 1
        if str(item).startswith("max_tokens:"):
            cap_counts["llm_tokens_capped"] += 1
        if str(item).startswith("context_depth:"):
            cap_counts["llm_context_depth_capped"] += 1
    if any(str(item) == "decision:call_llm->no_call" for item in blocked):
        cap_counts["llm_call_blocked_or_downgraded"] += 1
    elif artifact.get("decision") == DECISION_NO_CALL and artifact.get("evolution_slice_applied"):
        cap_counts["llm_call_blocked_or_downgraded"] += 1

    reason = _cap_reason(artifact)
    if reason:
        block_reasons[reason] += 1


def _collect_context_selector_metrics(
    artifact: dict[str, Any],
    cap_counts: Counter[str],
    block_reasons: Counter[str],
) -> None:
    if artifact.get("contract_version") not in {
        "knowledge_context_slice_v1",
        "day_context_slice_v1",
    }:
        return

    if artifact.get("evolution_slice_applied") is True:
        cap_counts["context_ak_cap_applied"] += 1

    selected = len(artifact.get("selected_facts") or [])
    cap_counts["context_facts_selected"] += selected

    for exclusion in artifact.get("excluded_facts") or []:
        if isinstance(exclusion, dict) and exclusion.get("reason") == EXCLUSION_EVOLUTION_CAP:
            cap_counts["context_facts_blocked_evolution_cap"] += 1
            block_reasons[EXCLUSION_EVOLUTION_CAP] += 1

    for item in artifact.get("blocked_expansions") or []:
        block_reasons[str(item)] += 1

    reason = _cap_reason(artifact)
    if reason:
        block_reasons[reason] += 1


def _collect_day_envelope_metrics(
    artifact: dict[str, Any],
    cap_counts: Counter[str],
    block_reasons: Counter[str],
) -> None:
    if artifact.get("contract_version") != EVOLUTION_DAY_PRESENTATION_ENVELOPE_V1_CONTRACT:
        return

    cap_counts["day_envelope_created"] += 1

    if artifact.get("answer_depth_cap") is not None:
        cap_counts["day_depth_cap_applied"] += 1
    if artifact.get("interpretation_cap") is not None:
        cap_counts["day_interpretation_cap_applied"] += 1
    if artifact.get("tone_policy") is not None:
        cap_counts["day_tone_policy_applied"] += 1

    for item in artifact.get("blocked_effects") or []:
        block_reasons[str(item)] += 1


def _collect_practice_selector_metrics(
    artifact: dict[str, Any],
    cap_counts: Counter[str],
    block_reasons: Counter[str],
) -> None:
    if artifact.get("contract_version") != EVOLUTION_PRACTICE_SELECTOR_FILTER_V1_CONTRACT:
        return

    cap_counts["practice_candidates_filtered_in"] += len(artifact.get("filtered_candidates") or [])
    cap_counts["practice_candidates_blocked_out"] += len(artifact.get("blocked_candidates") or [])

    for entry in artifact.get("blocked_candidates") or []:
        reason = entry.get("reason")
        if reason:
            block_reasons[str(reason)] += 1


def _collect_calendar_policy_metrics(
    artifact: dict[str, Any],
    cap_counts: Counter[str],
    block_reasons: Counter[str],
    readiness_blocks: Counter[str],
) -> None:
    if artifact.get("contract_version") != EVOLUTION_CALENDAR_RUNTIME_POLICY_V1_CONTRACT:
        return

    if artifact.get("calendar_depth"):
        cap_counts["calendar_depth_observed"] += 1

    for reason in artifact.get("blocked_calendar_effects") or []:
        block_reasons[str(reason)] += 1
        if reason == BLOCK_CALENDAR_SYSTEM_NOT_READY:
            readiness_blocks[BLOCK_CALENDAR_SYSTEM_NOT_READY] += 1


def _collect_commerce_visibility_metrics(
    artifact: dict[str, Any],
    cap_counts: Counter[str],
    block_reasons: Counter[str],
    readiness_blocks: Counter[str],
) -> None:
    if artifact.get("contract_version") != EVOLUTION_COMMERCE_VISIBILITY_POLICY_V1_CONTRACT:
        return

    if artifact.get("commerce_visibility_level"):
        cap_counts["commerce_visibility_observed"] += 1

    cap_counts["commerce_surfaces_allowed"] += len(artifact.get("allowed_surfaces") or [])
    cap_counts["commerce_surfaces_blocked"] += len(artifact.get("blocked_surfaces") or [])

    for entry in artifact.get("blocked_surfaces") or []:
        reason = entry.get("reason")
        if reason:
            block_reasons[str(reason)] += 1
            if reason == BLOCK_COMMERCE_NOT_READY:
                readiness_blocks[BLOCK_COMMERCE_NOT_READY] += 1


def _collect_consumer_artifact_metrics(
    consumer_id: str,
    artifact: dict[str, Any],
    *,
    cap_counts: Counter[str],
    block_reasons: Counter[str],
    readiness_blocks: Counter[str],
) -> None:
    if consumer_id == CONSUMER_LLM_GATE:
        _collect_llm_gate_metrics(artifact, cap_counts, block_reasons)
    elif consumer_id == CONSUMER_CONTEXT_SELECTOR:
        _collect_context_selector_metrics(artifact, cap_counts, block_reasons)
    elif consumer_id == CONSUMER_DAY_ENGINE:
        _collect_day_envelope_metrics(artifact, cap_counts, block_reasons)
    elif consumer_id == CONSUMER_PRACTICE_SELECTOR:
        _collect_practice_selector_metrics(artifact, cap_counts, block_reasons)
    elif consumer_id == CONSUMER_CALENDAR:
        _collect_calendar_policy_metrics(artifact, cap_counts, block_reasons, readiness_blocks)
    elif consumer_id == CONSUMER_COMMERCE_VISIBILITY:
        _collect_commerce_visibility_metrics(artifact, cap_counts, block_reasons, readiness_blocks)


def build_evolution_consumer_metrics_v1(
    consumer_artifacts: list[dict[str, Any]] | None = None,
    *,
    window_start: str,
    window_end: str,
    metrics_id: str | None = None,
    created_at: str | None = None,
) -> dict[str, Any]:
    """
    Aggregate read-only observability metrics from existing Evolution consumer artifacts.

    Metrics do not mutate policies, stage, score, or commerce targeting.
    """
    entries = consumer_artifacts or []

    consumer_counts = _empty_counter_dict(REGISTERED_CONSUMERS)
    slice_application_counts = _empty_counter_dict({SLICE_APPLIED, SLICE_IGNORED, SLICE_INVALID})
    cap_counts: Counter[str] = Counter()
    block_reasons: Counter[str] = Counter()
    stage_distribution: Counter[str] = Counter()
    readiness_blocks: Counter[str] = Counter()

    for entry in entries:
        if not isinstance(entry, dict):
            continue
        consumer_id = entry.get("consumer_id")
        artifact = entry.get("artifact")
        if consumer_id not in REGISTERED_CONSUMERS or not isinstance(artifact, dict):
            continue

        consumer_counts[consumer_id] += 1
        slice_application_counts[_classify_slice_application(consumer_id, artifact)] += 1

        stage = _extract_stage(consumer_id, artifact, entry)
        if stage:
            stage_distribution[stage] += 1

        _collect_consumer_artifact_metrics(
            consumer_id,
            artifact,
            cap_counts=cap_counts,
            block_reasons=block_reasons,
            readiness_blocks=readiness_blocks,
        )

    metrics = {
        "contract_version": EVOLUTION_CONSUMER_METRICS_V1_CONTRACT,
        "metrics_id": metrics_id or generate_evolution_consumer_metrics_id(),
        "window_start": window_start,
        "window_end": window_end,
        "consumer_counts": consumer_counts,
        "slice_application_counts": slice_application_counts,
        "cap_counts": dict(sorted(cap_counts.items())),
        "block_reason_distribution": dict(sorted(block_reasons.items())),
        "stage_distribution": dict(sorted(stage_distribution.items())),
        "readiness_blocks": dict(sorted(readiness_blocks.items())),
        "read_only": True,
        "promotion_allowed": False,
        "profile_update_allowed": False,
        "memory_update_allowed": False,
        "created_at": created_at or _utc_now_iso(),
    }

    errors = validate_evolution_consumer_metrics_v1(metrics)
    if errors:
        raise EvolutionConsumerMetricsError("; ".join(errors))

    return metrics


def validate_evolution_consumer_metrics_v1(metrics: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    if metrics.get("contract_version") != EVOLUTION_CONSUMER_METRICS_V1_CONTRACT:
        errors.append("invalid contract_version")

    for key in EVOLUTION_CONSUMER_METRICS_V1_KEYS:
        if key not in metrics:
            errors.append(f"missing field: {key}")

    forbidden = set(metrics.keys()) & FORBIDDEN_METRICS_FIELDS
    if forbidden:
        errors.append(f"forbidden metrics fields: {sorted(forbidden)}")

    if metrics.get("read_only") is not True:
        errors.append("read_only must be true")
    if metrics.get("promotion_allowed") is not False:
        errors.append("promotion_allowed must be false")
    if metrics.get("profile_update_allowed") is not False:
        errors.append("profile_update_allowed must be false")
    if metrics.get("memory_update_allowed") is not False:
        errors.append("memory_update_allowed must be false")

    for field in (
        "consumer_counts",
        "slice_application_counts",
        "cap_counts",
        "block_reason_distribution",
        "stage_distribution",
        "readiness_blocks",
    ):
        if not isinstance(metrics.get(field), dict):
            errors.append(f"{field} must be object")

    for consumer_id in REGISTERED_CONSUMERS:
        if consumer_id not in (metrics.get("consumer_counts") or {}):
            errors.append(f"consumer_counts missing {consumer_id}")

    for status in (SLICE_APPLIED, SLICE_IGNORED, SLICE_INVALID):
        if status not in (metrics.get("slice_application_counts") or {}):
            errors.append(f"slice_application_counts missing {status}")

    return errors

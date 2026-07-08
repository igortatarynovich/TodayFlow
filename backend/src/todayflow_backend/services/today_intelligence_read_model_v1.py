"""S1.1 — Today Intelligence Read Model (DayModel + A1 + B1.10; no API/UI/LLM/commerce)."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from todayflow_backend.services.day_model_v1_content_assembler import (
    DAY_CONTENT_PACKAGE_V1_CONTRACT,
)
from todayflow_backend.services.day_model_v1_content_mapper import (
    DAY_MODEL_CONTENT_MAPPING_V1_CONTRACT,
    INTERPRETATION_FIELD_PREFIXES,
)
from todayflow_backend.services.day_model_v1_day_engine_knowledge_wiring import (
    extract_day_model_core_snapshot,
)
from todayflow_backend.services.day_model_v1_hint_application import compute_state_snapshot_hash
from todayflow_backend.services.day_model_v1_interpreter import (
    DAY_MODEL_INTERPRETATION_V1_CONTRACT,
)
from todayflow_backend.services.day_model_v1_knowledge_context_selection import (
    KNOWLEDGE_CONTEXT_SLICE_V1_CONTRACT,
)
from todayflow_backend.services.day_model_v1_personalization_usage_gate import (
    PERSONALIZATION_USAGE_GATE_V1_CONTRACT,
    USAGE_DECISION_ALLOW,
)
from todayflow_backend.services.evolution_day_presentation_envelope_v1 import (
    ANSWER_DEPTH_DEEP,
    ANSWER_DEPTH_MINIMAL,
    ANSWER_DEPTH_NORMAL,
    EVOLUTION_DAY_PRESENTATION_ENVELOPE_V1_CONTRACT,
    TONE_NEUTRAL,
)

TODAY_INTELLIGENCE_READ_MODEL_V1_VERSION = "1.0.0"
TODAY_INTELLIGENCE_READ_MODEL_V1_CONTRACT = "today_intelligence_read_model_v1"

KNOWLEDGE_SUMMARY_STATUS_ACTIVE = "active"
KNOWLEDGE_SUMMARY_STATUS_EMPTY = "empty"
KNOWLEDGE_SUMMARY_STATUS_DENIED = "denied"

VISIBILITY_MINIMAL = "minimal"
VISIBILITY_STANDARD = "standard"
VISIBILITY_FULL = "full"

DEFAULT_AVAILABLE_SURFACES = ["day_guidance_card"]

ANSWER_DEPTH_TO_VISIBILITY: dict[str, str] = {
    ANSWER_DEPTH_MINIMAL: VISIBILITY_MINIMAL,
    ANSWER_DEPTH_NORMAL: VISIBILITY_STANDARD,
    ANSWER_DEPTH_DEEP: VISIBILITY_FULL,
}

TODAY_INTELLIGENCE_READ_MODEL_V1_KEYS = frozenset(
    {
        "contract_version",
        "read_model_id",
        "user_id",
        "date",
        "day_model_snapshot_id",
        "interpretation_id",
        "content_package_id",
        "knowledge_context_summary",
        "knowledge_fact_count",
        "personalization_active",
        "evolution_stage",
        "answer_depth_cap",
        "tone_policy",
        "primary_guidance_ref",
        "reflection_ref",
        "action_ref",
        "visibility_level",
        "available_surfaces",
        "source_versions",
        "generated_at",
    }
)

KNOWLEDGE_CONTEXT_SUMMARY_KEYS = frozenset({"status", "fact_types"})

SOURCE_VERSIONS_KEYS = frozenset(
    {
        "day_model",
        "interpretation",
        "content_mapping",
        "content_package",
        "knowledge_context_slice",
        "presentation_envelope",
        "personalization_gate",
    }
)

FORBIDDEN_OUTPUT_KEYS = frozenset(
    {
        "recommendation",
        "recommendations",
        "next_best_action",
        "commerce",
        "sku",
        "symbolic_product",
        "symbolic_products",
        "active_knowledge",
        "selected_facts",
        "excluded_facts",
        "claims",
        "claim",
        "confidence",
        "freshness_scores",
        "relevance_scores",
        "final_scores",
        "effect_limits",
        "allowed_effects",
        "consumer_slice",
        "full_policy",
        "progression_signal",
        "progression_signals",
        "rhythm_candidate",
        "rhythm_candidates",
        "rhythm_pattern",
        "rhythm_patterns",
        "mutation",
        "mutation_fields",
        "prompt",
        "prompt_data",
        "llm_trace",
        "llm_traces",
        "llm_output",
        "llm_response",
        "evaluation_id",
        "generation_id",
        "render_id",
        "package_id",
        "interpretation_cap",
        "blocked_effects",
        "knowledge_coexistence_trace",
        "surface_priority_hints",
        "envelope_id",
        "source_evolution_slice_id",
        "traceability",
        "conflict_resolutions",
        "exclusion_reasons",
        "ranking",
        "purchase_prompt",
        "offer",
        "pricing",
        "checkout",
    }
)


class TodayIntelligenceReadModelError(ValueError):
    """Raised when read model inputs or payload are invalid."""


def _utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def generate_read_model_id() -> str:
    return f"tirm-{uuid4()}"


def _artifact_snapshot_id(prefix: str, payload: dict[str, Any]) -> str:
    digest = compute_state_snapshot_hash(payload)
    return f"{prefix}-{digest[5:]}"


def _content_package_snapshot_id(content_package: dict[str, Any]) -> str:
    snapshot = {
        "contract_version": content_package.get("contract_version"),
        "metadata": content_package.get("metadata"),
        "degraded": content_package.get("degraded"),
    }
    return _artifact_snapshot_id("pkg", snapshot)


def _interpretation_snapshot_id(interpretation: dict[str, Any]) -> str:
    snapshot = {
        "contract_version": interpretation.get("contract_version"),
        "strategy": interpretation.get("strategy"),
        "opportunity_class": interpretation.get("opportunity_class"),
        "risk_class": interpretation.get("risk_class"),
        "tempo_instruction": interpretation.get("tempo_instruction"),
        "action_mode": interpretation.get("action_mode"),
        "reflection_mode": interpretation.get("reflection_mode"),
        "pressure_level": interpretation.get("pressure_level"),
        "confidence": interpretation.get("confidence"),
        "degraded": interpretation.get("degraded"),
    }
    return _artifact_snapshot_id("interp", snapshot)


def _build_knowledge_context_summary(
    *,
    context_slice: dict[str, Any] | None,
    personalization_gate: dict[str, Any] | None,
) -> tuple[dict[str, Any], int, bool]:
    personalization_active = (
        personalization_gate is not None
        and personalization_gate.get("decision") == USAGE_DECISION_ALLOW
    )

    if personalization_gate is not None and not personalization_active:
        return {"status": KNOWLEDGE_SUMMARY_STATUS_DENIED, "fact_types": []}, 0, False

    if not isinstance(context_slice, dict):
        return {"status": KNOWLEDGE_SUMMARY_STATUS_EMPTY, "fact_types": []}, 0, personalization_active

    selected = context_slice.get("selected_facts")
    if not isinstance(selected, list) or not selected:
        return {"status": KNOWLEDGE_SUMMARY_STATUS_EMPTY, "fact_types": []}, 0, personalization_active

    fact_types = sorted(
        {
            str(item.get("knowledge_type"))
            for item in selected
            if isinstance(item, dict) and item.get("knowledge_type")
        }
    )
    return (
        {"status": KNOWLEDGE_SUMMARY_STATUS_ACTIVE, "fact_types": fact_types},
        len(selected),
        personalization_active,
    )


def _build_evolution_fields(
    presentation_envelope: dict[str, Any] | None,
) -> tuple[str | None, str, str]:
    if not isinstance(presentation_envelope, dict):
        return None, ANSWER_DEPTH_MINIMAL, TONE_NEUTRAL

    stage = presentation_envelope.get("evolution_stage")
    depth = presentation_envelope.get("answer_depth_cap") or ANSWER_DEPTH_MINIMAL
    tone = presentation_envelope.get("tone_policy") or TONE_NEUTRAL
    return stage, str(depth), str(tone)


def _build_visibility(
    presentation_envelope: dict[str, Any] | None,
    *,
    answer_depth_cap: str,
) -> tuple[str, list[str]]:
    visibility_level = ANSWER_DEPTH_TO_VISIBILITY.get(answer_depth_cap, VISIBILITY_MINIMAL)
    if not isinstance(presentation_envelope, dict):
        return visibility_level, list(DEFAULT_AVAILABLE_SURFACES)

    hints = presentation_envelope.get("surface_priority_hints")
    if isinstance(hints, list) and hints:
        return visibility_level, [str(item) for item in hints]

    return visibility_level, list(DEFAULT_AVAILABLE_SURFACES)


def _content_key(field: str, value: str | None) -> str | None:
    if not value:
        return None
    prefix = INTERPRETATION_FIELD_PREFIXES.get(field)
    if not prefix:
        return None
    return f"{prefix}.{value}"


def _build_guidance_refs(
    *,
    content_mapping: dict[str, Any] | None,
    interpretation: dict[str, Any] | None,
) -> tuple[str | None, str | None, str | None]:
    if isinstance(content_mapping, dict):
        content_keys = content_mapping.get("content_keys") or {}
        primary = content_keys.get("strategy")
        action = content_keys.get("action_mode")
        optional = content_mapping.get("optional_slots") or {}
        reflection_keys = optional.get("reflection_hint") or []
        reflection = reflection_keys[0] if reflection_keys else content_keys.get("reflection_mode")
        return primary, reflection, action

    if isinstance(interpretation, dict):
        return (
            _content_key("strategy", interpretation.get("strategy")),
            _content_key("reflection_mode", interpretation.get("reflection_mode")),
            _content_key("action_mode", interpretation.get("action_mode")),
        )

    return None, None, None


def _build_source_versions(
    *,
    day_model: dict[str, Any] | None,
    interpretation: dict[str, Any] | None,
    content_mapping: dict[str, Any] | None,
    content_package: dict[str, Any] | None,
    context_slice: dict[str, Any] | None,
    presentation_envelope: dict[str, Any] | None,
    personalization_gate: dict[str, Any] | None,
) -> dict[str, str | None]:
    return {
        "day_model": day_model.get("contract_version") if isinstance(day_model, dict) else None,
        "interpretation": (
            interpretation.get("contract_version") if isinstance(interpretation, dict) else None
        ),
        "content_mapping": (
            content_mapping.get("contract_version") if isinstance(content_mapping, dict) else None
        ),
        "content_package": (
            content_package.get("contract_version") if isinstance(content_package, dict) else None
        ),
        "knowledge_context_slice": (
            context_slice.get("contract_version") if isinstance(context_slice, dict) else None
        ),
        "presentation_envelope": (
            presentation_envelope.get("contract_version")
            if isinstance(presentation_envelope, dict)
            else None
        ),
        "personalization_gate": (
            personalization_gate.get("contract_version")
            if isinstance(personalization_gate, dict)
            else None
        ),
    }


def _collect_forbidden_keys(value: Any, *, path: str = "") -> list[str]:
    hits: list[str] = []
    if isinstance(value, dict):
        for key, nested in value.items():
            key_path = f"{path}.{key}" if path else str(key)
            if key in FORBIDDEN_OUTPUT_KEYS:
                hits.append(key_path)
            hits.extend(_collect_forbidden_keys(nested, path=key_path))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            hits.extend(_collect_forbidden_keys(item, path=f"{path}[{index}]"))
    return hits


def build_today_intelligence_read_model_v1(
    *,
    user_id: str,
    date: str,
    day_model: dict[str, Any] | None = None,
    interpretation: dict[str, Any] | None = None,
    content_mapping: dict[str, Any] | None = None,
    content_package: dict[str, Any] | None = None,
    knowledge_context_slice: dict[str, Any] | None = None,
    personalization_gate: dict[str, Any] | None = None,
    presentation_envelope: dict[str, Any] | None = None,
    read_model_id: str | None = None,
    generated_at: str | None = None,
) -> dict[str, Any]:
    """
    Build a safe Today Intelligence read model from DayModel + A1 + B1.10 artifacts.

    Does not expose full policies, active knowledge claims, LLM traces, or commerce fields.
    """
    if not user_id:
        raise TodayIntelligenceReadModelError("user_id is required")
    if not date:
        raise TodayIntelligenceReadModelError("date is required")

    if day_model is None:
        raise TodayIntelligenceReadModelError("day_model is required")

    day_model_snapshot_id = compute_state_snapshot_hash(extract_day_model_core_snapshot(day_model))

    interpretation_id = (
        _interpretation_snapshot_id(interpretation) if isinstance(interpretation, dict) else None
    )
    content_package_id = (
        _content_package_snapshot_id(content_package)
        if isinstance(content_package, dict)
        else None
    )

    knowledge_context_summary, knowledge_fact_count, personalization_active = (
        _build_knowledge_context_summary(
            context_slice=knowledge_context_slice,
            personalization_gate=personalization_gate,
        )
    )

    evolution_stage, answer_depth_cap, tone_policy = _build_evolution_fields(presentation_envelope)
    visibility_level, available_surfaces = _build_visibility(
        presentation_envelope,
        answer_depth_cap=answer_depth_cap,
    )
    primary_guidance_ref, reflection_ref, action_ref = _build_guidance_refs(
        content_mapping=content_mapping,
        interpretation=interpretation,
    )

    read_model: dict[str, Any] = {
        "contract_version": TODAY_INTELLIGENCE_READ_MODEL_V1_CONTRACT,
        "read_model_id": read_model_id or generate_read_model_id(),
        "user_id": user_id,
        "date": date,
        "day_model_snapshot_id": day_model_snapshot_id,
        "interpretation_id": interpretation_id,
        "content_package_id": content_package_id,
        "knowledge_context_summary": knowledge_context_summary,
        "knowledge_fact_count": knowledge_fact_count,
        "personalization_active": personalization_active,
        "evolution_stage": evolution_stage,
        "answer_depth_cap": answer_depth_cap,
        "tone_policy": tone_policy,
        "primary_guidance_ref": primary_guidance_ref,
        "reflection_ref": reflection_ref,
        "action_ref": action_ref,
        "visibility_level": visibility_level,
        "available_surfaces": available_surfaces,
        "source_versions": _build_source_versions(
            day_model=day_model,
            interpretation=interpretation,
            content_mapping=content_mapping,
            content_package=content_package,
            context_slice=knowledge_context_slice,
            presentation_envelope=presentation_envelope,
            personalization_gate=personalization_gate,
        ),
        "generated_at": generated_at or _utc_now_iso(),
    }

    errors = validate_today_intelligence_read_model_v1(read_model)
    if errors:
        raise TodayIntelligenceReadModelError("; ".join(errors))

    return read_model


def build_today_intelligence_read_model_from_presentation_wiring_v1(
    *,
    user_id: str,
    date: str,
    day_model: dict[str, Any],
    interpretation: dict[str, Any] | None = None,
    content_mapping: dict[str, Any] | None = None,
    content_package: dict[str, Any] | None = None,
    knowledge_context_slice: dict[str, Any] | None = None,
    personalization_gate: dict[str, Any] | None = None,
    wired_guide_decision: dict[str, Any] | None = None,
    presentation_envelope: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Convenience builder when B1.10 envelope is attached to guide_decision."""
    envelope = presentation_envelope
    if envelope is None and isinstance(wired_guide_decision, dict):
        envelope = wired_guide_decision.get("evolution_day_presentation_envelope")

    return build_today_intelligence_read_model_v1(
        user_id=user_id,
        date=date,
        day_model=day_model,
        interpretation=interpretation,
        content_mapping=content_mapping,
        content_package=content_package,
        knowledge_context_slice=knowledge_context_slice,
        personalization_gate=personalization_gate,
        presentation_envelope=envelope if isinstance(envelope, dict) else None,
    )


def validate_today_intelligence_read_model_v1(read_model: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    if read_model.get("contract_version") != TODAY_INTELLIGENCE_READ_MODEL_V1_CONTRACT:
        errors.append("invalid contract_version")

    missing = TODAY_INTELLIGENCE_READ_MODEL_V1_KEYS - set(read_model.keys())
    if missing:
        errors.append(f"missing read model fields: {sorted(missing)}")

    extra = set(read_model.keys()) - TODAY_INTELLIGENCE_READ_MODEL_V1_KEYS
    if extra:
        errors.append(f"unexpected read model fields: {sorted(extra)}")

    summary = read_model.get("knowledge_context_summary")
    if not isinstance(summary, dict):
        errors.append("knowledge_context_summary must be object")
    else:
        summary_extra = set(summary.keys()) - KNOWLEDGE_CONTEXT_SUMMARY_KEYS
        if summary_extra:
            errors.append(f"unexpected knowledge_context_summary fields: {sorted(summary_extra)}")
        if summary.get("status") not in {
            KNOWLEDGE_SUMMARY_STATUS_ACTIVE,
            KNOWLEDGE_SUMMARY_STATUS_EMPTY,
            KNOWLEDGE_SUMMARY_STATUS_DENIED,
        }:
            errors.append("invalid knowledge_context_summary.status")
        fact_types = summary.get("fact_types")
        if not isinstance(fact_types, list):
            errors.append("knowledge_context_summary.fact_types must be array")
        elif any(not isinstance(item, str) for item in fact_types):
            errors.append("knowledge_context_summary.fact_types must contain strings only")

    if not isinstance(read_model.get("knowledge_fact_count"), int):
        errors.append("knowledge_fact_count must be int")
    elif read_model["knowledge_fact_count"] < 0:
        errors.append("knowledge_fact_count must be >= 0")

    if not isinstance(read_model.get("personalization_active"), bool):
        errors.append("personalization_active must be bool")

    if read_model.get("answer_depth_cap") not in {
        ANSWER_DEPTH_MINIMAL,
        ANSWER_DEPTH_NORMAL,
        ANSWER_DEPTH_DEEP,
    }:
        errors.append("invalid answer_depth_cap")

    if read_model.get("visibility_level") not in {
        VISIBILITY_MINIMAL,
        VISIBILITY_STANDARD,
        VISIBILITY_FULL,
    }:
        errors.append("invalid visibility_level")

    surfaces = read_model.get("available_surfaces")
    if not isinstance(surfaces, list) or not all(isinstance(item, str) for item in surfaces):
        errors.append("available_surfaces must be string array")

    source_versions = read_model.get("source_versions")
    if not isinstance(source_versions, dict):
        errors.append("source_versions must be object")
    else:
        source_extra = set(source_versions.keys()) - SOURCE_VERSIONS_KEYS
        if source_extra:
            errors.append(f"unexpected source_versions fields: {sorted(source_extra)}")

    forbidden = _collect_forbidden_keys(read_model)
    if forbidden:
        errors.append(f"forbidden fields exposed: {sorted(forbidden)}")

    return errors

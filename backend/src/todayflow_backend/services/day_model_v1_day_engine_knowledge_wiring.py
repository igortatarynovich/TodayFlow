"""A1.3 — Apply day engine knowledge hints to guide_decision with trace."""

from __future__ import annotations

import copy
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from todayflow_backend.services.day_model_v1_day_engine_knowledge_integration import (
    DAY_ENGINE_KNOWLEDGE_INPUT_V1_CONTRACT,
    HINT_CHANNEL_ACTION_MODE,
    HINT_CHANNEL_CONTENT_AFFINITY,
    HINT_CHANNEL_RESPONSE_STYLE,
    HINT_CHANNEL_RISK_SENSITIVITY,
    HINT_CHANNEL_TEMPO_ALIGNMENT,
    INTEGRATION_STATUS_READY,
    try_build_day_engine_knowledge_input_v1,
    validate_day_engine_knowledge_input_v1,
)
from todayflow_backend.services.day_model_v1_hint_application import compute_state_snapshot_hash
from todayflow_backend.services.day_model_v1_knowledge_context_selection import (
    select_knowledge_context_v1,
)

DAY_ENGINE_KNOWLEDGE_WIRING_RESULT_V1_CONTRACT = "day_engine_knowledge_wiring_result_v1"
WIRING_POLICY_VERSION = "1.0.0"

WIRING_STATUS_READY = "ready"

WIRING_RESULT_APPLIED = "applied"
WIRING_RESULT_REJECTED = "rejected"
WIRING_RESULT_NOOP = "noop"

GUIDE_DECISION_CONTRACT = "guide_decision_v0"
DAY_MODEL_CONTRACT = "day_model_v0"

PRESENTATION_LENGTH_SHORT = "short"
PRESENTATION_LENGTH_LONG = "long"
PRESENTATION_LENGTH_STANDARD = "standard"

MAX_DO_ITEMS_WITH_SINGLE_ACTION = 1
MAX_DO_ITEMS_DEFAULT = 3

DAY_ENGINE_KNOWLEDGE_WIRING_RESULT_V1_KEYS = frozenset(
    {
        "contract_version",
        "wiring_id",
        "integration_id",
        "context_slice_id",
        "applied",
        "before_snapshot_hash",
        "after_snapshot_hash",
        "guide_decision_with_knowledge",
        "knowledge_hints_applied",
        "presentation_adjustments",
        "traceability",
        "status",
        "created_at",
        "profile_update_allowed",
        "memory_update_allowed",
        "ranking_model_update_allowed",
    }
)


class DayEngineKnowledgeWiringError(ValueError):
    """Raised when knowledge wiring inputs or payload are invalid."""


def _utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def extract_guide_decision_wiring_snapshot(guide_decision: dict[str, Any]) -> dict[str, Any]:
    """Hash-relevant guide_decision fields for before/after trace."""
    anchors = guide_decision.get("anchors")
    return {
        "contract_version": guide_decision.get("contract_version"),
        "headline": guide_decision.get("headline"),
        "subline": guide_decision.get("subline"),
        "do_items": list(guide_decision.get("do_items") or []),
        "avoid_items": list(guide_decision.get("avoid_items") or []),
        "risk_line": guide_decision.get("risk_line"),
        "anchors": dict(anchors) if isinstance(anchors, dict) else {},
        "knowledge_hints": guide_decision.get("knowledge_hints"),
    }


def extract_day_model_core_snapshot(day_model: dict[str, Any]) -> dict[str, Any]:
    return {
        "contract_version": day_model.get("contract_version"),
        "vector": day_model.get("vector"),
        "tempo": day_model.get("tempo"),
        "risk": day_model.get("risk"),
        "strategy": day_model.get("strategy"),
        "scales": day_model.get("scales"),
        "gate": day_model.get("gate"),
    }


def build_knowledge_hints_layer(hints: list[dict[str, Any]]) -> dict[str, Any]:
    boosted_keys: list[str] = []
    response_styles: list[str] = []
    action_modes: list[str] = []
    tempo_values: list[str] = []
    risk_values: list[str] = []

    for hint in hints:
        channel = hint.get("hint_channel")
        value = str(hint.get("hint_value") or "")
        if channel == HINT_CHANNEL_CONTENT_AFFINITY and value:
            boosted_keys.append(value)
        elif channel == HINT_CHANNEL_RESPONSE_STYLE and value:
            response_styles.append(value)
        elif channel == HINT_CHANNEL_ACTION_MODE and value:
            action_modes.append(value)
        elif channel == HINT_CHANNEL_TEMPO_ALIGNMENT and value:
            tempo_values.append(value)
        elif channel == HINT_CHANNEL_RISK_SENSITIVITY and value:
            risk_values.append(value)

    presentation_length = PRESENTATION_LENGTH_STANDARD
    for style in response_styles:
        normalized = style.lower()
        if "short" in normalized:
            presentation_length = PRESENTATION_LENGTH_SHORT
            break
        if "long" in normalized:
            presentation_length = PRESENTATION_LENGTH_LONG

    recommended_action_count = MAX_DO_ITEMS_DEFAULT
    for mode in action_modes:
        normalized = mode.lower()
        if "single" in normalized or normalized in {"one", "one_step"}:
            recommended_action_count = MAX_DO_ITEMS_WITH_SINGLE_ACTION
            break

    return {
        "boosted_content_keys": boosted_keys,
        "preferred_response_styles": response_styles,
        "preferred_action_modes": action_modes,
        "tempo_alignment_values": tempo_values,
        "risk_sensitivity_values": risk_values,
        "presentation": {
            "length": presentation_length,
            "recommended_action_count": recommended_action_count,
        },
        "hint_count": len(hints),
    }


def build_presentation_adjustments(
    knowledge_hints: dict[str, Any],
    guide_decision: dict[str, Any],
) -> dict[str, Any]:
    presentation = knowledge_hints.get("presentation") or {}
    anchors = guide_decision.get("anchors") if isinstance(guide_decision.get("anchors"), dict) else {}

    adjustments: dict[str, Any] = {
        "do_items_trimmed": False,
        "presentation_length": presentation.get("length", PRESENTATION_LENGTH_STANDARD),
        "recommended_action_count": presentation.get("recommended_action_count", MAX_DO_ITEMS_DEFAULT),
    }

    tempo_hint = (knowledge_hints.get("tempo_alignment_values") or [None])[0]
    anchor_tempo = anchors.get("tempo")
    if tempo_hint and anchor_tempo:
        adjustments["tempo_alignment_note"] = (
            f"knowledge_tempo={tempo_hint},day_tempo={anchor_tempo}"
        )
        adjustments["tempo_aligned"] = str(tempo_hint).lower() == str(anchor_tempo).lower()
    else:
        adjustments["tempo_alignment_note"] = None
        adjustments["tempo_aligned"] = None

    risk_hint = (knowledge_hints.get("risk_sensitivity_values") or [None])[0]
    if risk_hint:
        adjustments["risk_framing"] = str(risk_hint).lower()

    return adjustments


def apply_presentation_adjustments(
    guide_decision: dict[str, Any],
    knowledge_hints: dict[str, Any],
    presentation_adjustments: dict[str, Any],
) -> dict[str, Any]:
    """Apply bounded presentation changes — does not mutate day_model core keys."""
    wired = copy.deepcopy(guide_decision)
    wired["knowledge_hints"] = knowledge_hints

    recommended = int(
        presentation_adjustments.get("recommended_action_count") or MAX_DO_ITEMS_DEFAULT
    )
    do_items = list(wired.get("do_items") or [])
    if len(do_items) > recommended:
        wired["do_items"] = do_items[:recommended]
        presentation_adjustments["do_items_trimmed"] = True
        presentation_adjustments["do_items_before_count"] = len(do_items)
        presentation_adjustments["do_items_after_count"] = recommended

    length = presentation_adjustments.get("presentation_length")
    if length == PRESENTATION_LENGTH_SHORT and isinstance(wired.get("subline"), str):
        subline = wired["subline"]
        if len(subline) > 280:
            wired["subline"] = subline[:277] + "..."
            presentation_adjustments["subline_clipped"] = True

    return wired


def build_knowledge_hints_applied(hints: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "knowledge_id": h.get("knowledge_id"),
            "claim": h.get("claim"),
            "hint_channel": h.get("hint_channel"),
            "application_mode": h.get("application_mode"),
            "influence_level": h.get("influence_level"),
        }
        for h in hints
    ]


def try_apply_day_engine_knowledge_v1(
    knowledge_input: dict[str, Any],
    guide_decision: dict[str, Any],
    *,
    day_model: dict[str, Any] | None = None,
    created_at: str | None = None,
    wiring_id: str | None = None,
) -> dict[str, Any]:
    """
    Wire knowledge hints into guide_decision with before/after trace.

    Does not mutate day_model. Does not persist learning.
    """
    reasons: list[str] = []

    if knowledge_input.get("contract_version") != DAY_ENGINE_KNOWLEDGE_INPUT_V1_CONTRACT:
        reasons.append("invalid knowledge_input contract_version")
    if knowledge_input.get("status") != INTEGRATION_STATUS_READY:
        reasons.append("knowledge_input status must be ready")

    input_errors = validate_day_engine_knowledge_input_v1(knowledge_input)
    reasons.extend(input_errors)

    if guide_decision.get("contract_version") != GUIDE_DECISION_CONTRACT:
        reasons.append("guide_decision contract_version must be guide_decision_v0")

    if day_model is not None and day_model.get("contract_version") != DAY_MODEL_CONTRACT:
        reasons.append("day_model contract_version must be day_model_v0")

    if reasons:
        return {
            "result": WIRING_RESULT_REJECTED,
            "reasons": reasons,
            "wiring_result": None,
        }

    hints = knowledge_input.get("hints") or []
    if not isinstance(hints, list):
        return {
            "result": WIRING_RESULT_REJECTED,
            "reasons": ["hints must be a list"],
            "wiring_result": None,
        }

    day_model_before = (
        extract_day_model_core_snapshot(day_model) if isinstance(day_model, dict) else None
    )

    before_hash = compute_state_snapshot_hash(extract_guide_decision_wiring_snapshot(guide_decision))

    if not hints:
        wired = copy.deepcopy(guide_decision)
        wired["knowledge_hints"] = build_knowledge_hints_layer([])
        after_hash = compute_state_snapshot_hash(extract_guide_decision_wiring_snapshot(wired))
        wiring_result = _build_wiring_result(
            knowledge_input=knowledge_input,
            guide_decision_with_knowledge=wired,
            applied=False,
            before_hash=before_hash,
            after_hash=after_hash,
            knowledge_hints_applied=[],
            presentation_adjustments={"noop": True},
            wiring_id=wiring_id,
            created_at=created_at,
        )
        return {
            "result": WIRING_RESULT_NOOP,
            "reasons": [],
            "wiring_result": wiring_result,
        }

    knowledge_hints = build_knowledge_hints_layer(hints)
    presentation_adjustments = build_presentation_adjustments(knowledge_hints, guide_decision)
    wired = apply_presentation_adjustments(
        guide_decision,
        knowledge_hints,
        presentation_adjustments,
    )

    if day_model_before is not None and isinstance(day_model, dict):
        after_day_model = extract_day_model_core_snapshot(day_model)
        if after_day_model != day_model_before:
            return {
                "result": WIRING_RESULT_REJECTED,
                "reasons": ["day_model core must remain unchanged"],
                "wiring_result": None,
            }

    after_hash = compute_state_snapshot_hash(extract_guide_decision_wiring_snapshot(wired))

    wiring_result = _build_wiring_result(
        knowledge_input=knowledge_input,
        guide_decision_with_knowledge=wired,
        applied=True,
        before_hash=before_hash,
        after_hash=after_hash,
        knowledge_hints_applied=build_knowledge_hints_applied(hints),
        presentation_adjustments=presentation_adjustments,
        wiring_id=wiring_id,
        created_at=created_at,
    )

    validation_errors = validate_day_engine_knowledge_wiring_result_v1(wiring_result)
    if validation_errors:
        return {
            "result": WIRING_RESULT_REJECTED,
            "reasons": validation_errors,
            "wiring_result": None,
        }

    return {
        "result": WIRING_RESULT_APPLIED,
        "reasons": [],
        "wiring_result": wiring_result,
    }


def try_wire_day_engine_knowledge_from_context_v1(
    knowledge_context_slice: dict[str, Any],
    guide_decision: dict[str, Any],
    *,
    day_model: dict[str, Any] | None = None,
    created_at: str | None = None,
) -> dict[str, Any]:
    """A1.1 → A1.2 → A1.3 pipeline in one call."""
    integration = try_build_day_engine_knowledge_input_v1(
        knowledge_context_slice,
        day_model_snapshot=extract_day_model_core_snapshot(day_model)
        if isinstance(day_model, dict)
        else None,
    )
    if integration.get("result") != "created":
        return {
            "result": WIRING_RESULT_REJECTED,
            "reasons": integration.get("reasons") or ["integration failed"],
            "knowledge_context_slice": knowledge_context_slice,
            "knowledge_input": None,
            "wiring_result": None,
        }

    knowledge_input = integration["knowledge_input"]
    assert knowledge_input is not None

    wiring = try_apply_day_engine_knowledge_v1(
        knowledge_input,
        guide_decision,
        day_model=day_model,
        created_at=created_at,
    )

    return {
        "result": wiring.get("result"),
        "reasons": wiring.get("reasons") or [],
        "knowledge_context_slice": knowledge_context_slice,
        "knowledge_input": knowledge_input,
        "wiring_result": wiring.get("wiring_result"),
    }


def _build_wiring_result(
    *,
    knowledge_input: dict[str, Any],
    guide_decision_with_knowledge: dict[str, Any],
    applied: bool,
    before_hash: str,
    after_hash: str,
    knowledge_hints_applied: list[dict[str, Any]],
    presentation_adjustments: dict[str, Any],
    wiring_id: str | None,
    created_at: str | None,
) -> dict[str, Any]:
    traceability = knowledge_input.get("traceability") or {}
    return {
        "contract_version": DAY_ENGINE_KNOWLEDGE_WIRING_RESULT_V1_CONTRACT,
        "wiring_id": wiring_id or generate_wiring_id(),
        "integration_id": knowledge_input.get("integration_id"),
        "context_slice_id": knowledge_input.get("context_slice_id"),
        "applied": applied,
        "before_snapshot_hash": before_hash,
        "after_snapshot_hash": after_hash,
        "guide_decision_with_knowledge": guide_decision_with_knowledge,
        "knowledge_hints_applied": knowledge_hints_applied,
        "presentation_adjustments": presentation_adjustments,
        "traceability": {
            "integration_id": knowledge_input.get("integration_id"),
            "context_slice_id": knowledge_input.get("context_slice_id"),
            "knowledge_ids": traceability.get("knowledge_ids") or [],
            "runtime_decision_ids": traceability.get("runtime_decision_ids") or [],
            "wiring_policy_version": WIRING_POLICY_VERSION,
            "integration_policy_version": knowledge_input.get("integration_policy_version"),
        },
        "status": WIRING_STATUS_READY,
        "created_at": created_at or _utc_now_iso(),
        "profile_update_allowed": False,
        "memory_update_allowed": False,
        "ranking_model_update_allowed": False,
    }


def generate_wiring_id() -> str:
    return f"dewr-{uuid4()}"


def validate_day_engine_knowledge_wiring_result_v1(wiring_result: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    if wiring_result.get("contract_version") != DAY_ENGINE_KNOWLEDGE_WIRING_RESULT_V1_CONTRACT:
        errors.append("invalid contract_version")

    for key in DAY_ENGINE_KNOWLEDGE_WIRING_RESULT_V1_KEYS:
        if key not in wiring_result:
            errors.append(f"missing field: {key}")

    if wiring_result.get("status") != WIRING_STATUS_READY:
        errors.append("status must be ready")

    for flag in (
        "profile_update_allowed",
        "memory_update_allowed",
        "ranking_model_update_allowed",
    ):
        if wiring_result.get(flag) is not False:
            errors.append(f"{flag} must be false")

    gd = wiring_result.get("guide_decision_with_knowledge")
    if isinstance(gd, dict):
        if gd.get("contract_version") != GUIDE_DECISION_CONTRACT:
            errors.append("guide_decision_with_knowledge invalid contract")
        if "knowledge_hints" not in gd:
            errors.append("guide_decision_with_knowledge missing knowledge_hints")

    before = wiring_result.get("before_snapshot_hash")
    after = wiring_result.get("after_snapshot_hash")
    if not isinstance(before, str) or not before:
        errors.append("before_snapshot_hash required")
    if not isinstance(after, str) or not after:
        errors.append("after_snapshot_hash required")

    return errors


def wire_active_knowledge_into_day_context_layers(
    layers: dict[str, Any],
    active_knowledge_list: list[dict[str, Any]],
    *,
    day_context: dict[str, Any] | None = None,
    goals: list[dict[str, Any]] | None = None,
    practices: list[dict[str, Any]] | None = None,
    evolution_stage: str | None = None,
    target_surface: str = "day_guidance_card",
) -> dict[str, Any]:
    """
    Run A1.1–A1.3 on existing DayContext layers; mutates layers in place.

    Adds knowledge_context_slice, day_engine_knowledge_input,
    day_engine_knowledge_wiring; replaces guide_decision when wired.
    """
    guide_decision = layers.get("guide_decision")
    day_model = layers.get("day_model")
    if not isinstance(guide_decision, dict):
        raise DayEngineKnowledgeWiringError("layers.guide_decision required")

    context_slice = select_knowledge_context_v1(
        active_knowledge_list,
        day_context=day_context,
        goals=goals,
        practices=practices,
        evolution_stage=evolution_stage,
        target_surface=target_surface,
    )

    pipeline = try_wire_day_engine_knowledge_from_context_v1(
        context_slice,
        guide_decision,
        day_model=day_model if isinstance(day_model, dict) else None,
    )

    layers["knowledge_context_slice"] = pipeline.get("knowledge_context_slice")
    layers["day_engine_knowledge_input"] = pipeline.get("knowledge_input")
    layers["day_engine_knowledge_wiring"] = pipeline.get("wiring_result")

    wiring_result = pipeline.get("wiring_result")
    if isinstance(wiring_result, dict):
        wired_gd = wiring_result.get("guide_decision_with_knowledge")
        if isinstance(wired_gd, dict):
            layers["guide_decision"] = wired_gd

    return pipeline

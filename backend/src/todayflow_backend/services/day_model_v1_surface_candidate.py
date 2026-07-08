"""P1.13 — Final surface candidate selection (deterministic / LLM / blocked, no UI or API)."""

from __future__ import annotations

from typing import Any

from todayflow_backend.services.day_model_v1_content_evaluator import (
    DAY_CONTENT_PACKAGE_EVALUATION_V1_CONTRACT,
)
from todayflow_backend.services.day_model_v1_content_renderer import (
    DAY_CONTENT_RENDER_V1_CONTRACT,
)
from todayflow_backend.services.day_model_v1_llm_call_gate import (
    DAY_CONTENT_LLM_GATE_V1_CONTRACT,
    DECISION_BLOCKED,
    DECISION_CALL_LLM,
    DECISION_NO_CALL,
)
from todayflow_backend.services.day_model_v1_llm_refinement_response import (
    DAY_LLM_REFINEMENT_RESPONSE_V1_CONTRACT,
    RESPONSE_STATUS_VALID,
)
from todayflow_backend.services.day_model_v1_llm_response_evaluation import (
    DAY_LLM_RESPONSE_EVALUATION_V1_CONTRACT,
    DATASET_STATUS_CANDIDATE,
    RECOMMENDATION_ACCEPT_CANDIDATE,
)

DAY_SURFACE_CANDIDATE_V1_CONTRACT = "day_surface_candidate_v1"

SELECTED_SOURCE_DETERMINISTIC = "deterministic"
SELECTED_SOURCE_LLM_REFINED = "llm_refined"
SELECTED_SOURCE_BLOCKED = "blocked"

LLM_QUALITY_THRESHOLD = 0.75

DAY_SURFACE_CANDIDATE_V1_KEYS = frozenset(
    {
        "contract_version",
        "surface",
        "selected_source",
        "display_text",
        "source_keys",
        "generation_id",
        "quality_score",
        "confidence",
        "degraded",
        "selection_reason",
        "used_llm",
        "dataset_candidate",
        "render_trace",
        "llm_trace",
    }
)


class DaySurfaceCandidateSelectionError(ValueError):
    """Raised when candidate selection inputs are invalid."""


def _require_inputs(
    render: dict[str, Any],
    evaluation: dict[str, Any],
    gate_decision: dict[str, Any],
    surface: str,
) -> None:
    if render.get("contract_version") != DAY_CONTENT_RENDER_V1_CONTRACT:
        raise DaySurfaceCandidateSelectionError("render has invalid contract_version")
    if evaluation.get("contract_version") != DAY_CONTENT_PACKAGE_EVALUATION_V1_CONTRACT:
        raise DaySurfaceCandidateSelectionError("evaluation has invalid contract_version")
    if gate_decision.get("contract_version") != DAY_CONTENT_LLM_GATE_V1_CONTRACT:
        raise DaySurfaceCandidateSelectionError("gate_decision has invalid contract_version")
    if not surface:
        raise DaySurfaceCandidateSelectionError("surface is required")


def _confidence_from_render(render: dict[str, Any], evaluation: dict[str, Any]) -> float:
    metadata = render.get("metadata") or {}
    interpretation = metadata.get("interpretation") or {}
    if interpretation.get("confidence") is not None:
        return float(interpretation["confidence"])
    if evaluation.get("confidence_score") is not None:
        return float(evaluation["confidence_score"])
    return 0.0


def _quality_from_evaluation(evaluation: dict[str, Any]) -> float:
    if evaluation.get("score") is not None:
        return float(evaluation["score"])
    if evaluation.get("confidence_score") is not None:
        return float(evaluation["confidence_score"])
    return 0.0


def _surface_entry(render: dict[str, Any], surface: str) -> dict[str, Any] | None:
    surfaces = render.get("surfaces") or {}
    target = surfaces.get(surface)
    return target if isinstance(target, dict) else None


def _deterministic_display_text(render_surface: dict[str, Any]) -> str | None:
    parts: list[str] = []
    for entry in render_surface.get("entries", []):
        if not isinstance(entry, dict):
            continue
        text = entry.get("display_text")
        if isinstance(text, str) and text.strip():
            parts.append(text.strip())
    if not parts:
        return None
    return " ".join(parts)


def _deterministic_source_keys(render_surface: dict[str, Any]) -> list[str]:
    keys = render_surface.get("source_keys")
    if isinstance(keys, list) and keys:
        return [str(key) for key in keys]
    collected: list[str] = []
    for entry in render_surface.get("entries", []):
        if isinstance(entry, dict) and entry.get("key"):
            collected.append(str(entry["key"]))
    return collected


def _surface_degraded(render: dict[str, Any], render_surface: dict[str, Any] | None) -> bool:
    if bool(render.get("degraded", False)):
        return True
    if render_surface and bool(render_surface.get("degraded", False)):
        return True
    metadata = render.get("metadata") or {}
    evaluation_meta = metadata.get("evaluation") or {}
    return bool(evaluation_meta.get("degraded", False))


def _build_render_trace(render_trace: dict[str, Any] | None) -> dict[str, Any]:
    trace = render_trace or {}
    return {
        "render_id": trace.get("render_id"),
        "package_id": trace.get("package_id"),
        "evaluation_id": trace.get("evaluation_id"),
    }


def _build_llm_trace(
    llm_trace: dict[str, Any] | None,
    *,
    llm_response_evaluation: dict[str, Any] | None,
    validated_llm_response: dict[str, Any] | None,
) -> dict[str, Any]:
    trace = llm_trace or {}
    generation_id = None
    evaluation_id = None
    if llm_response_evaluation:
        generation_id = llm_response_evaluation.get("generation_id")
        evaluation_id = llm_response_evaluation.get("llm_response_evaluation_id")
    return {
        "generation_id": trace.get("generation_id") or generation_id,
        "prompt_id": trace.get("prompt_id"),
        "context_slice_id": trace.get("context_slice_id"),
        "llm_response_evaluation_id": trace.get("llm_response_evaluation_id") or evaluation_id,
        "validated_response_status": (
            validated_llm_response.get("status") if validated_llm_response else None
        ),
    }


def _llm_eligible(
    *,
    gate_decision: dict[str, Any],
    surface: str,
    llm_response_evaluation: dict[str, Any] | None,
    validated_llm_response: dict[str, Any] | None,
    llm_quality_threshold: float,
) -> tuple[bool, str]:
    if gate_decision.get("decision") != DECISION_CALL_LLM:
        return False, "gate_not_call_llm"
    if gate_decision.get("surface") != surface:
        return False, "wrong_surface"
    if llm_response_evaluation is None or validated_llm_response is None:
        return False, "missing_llm_artifacts"
    if llm_response_evaluation.get("contract_version") != DAY_LLM_RESPONSE_EVALUATION_V1_CONTRACT:
        return False, "invalid_llm_evaluation_contract"
    if validated_llm_response.get("contract_version") != DAY_LLM_REFINEMENT_RESPONSE_V1_CONTRACT:
        return False, "invalid_validated_response_contract"
    if validated_llm_response.get("status") != RESPONSE_STATUS_VALID:
        return False, "invalid_response_status"
    if llm_response_evaluation.get("response_status") != RESPONSE_STATUS_VALID:
        return False, "invalid_evaluation_status"
    if llm_response_evaluation.get("recommendation") != RECOMMENDATION_ACCEPT_CANDIDATE:
        return False, "recommendation_not_accept"
    if llm_response_evaluation.get("usable_candidate") is not True:
        return False, "not_usable_candidate"
    refined = validated_llm_response.get("refined_text")
    if not isinstance(refined, str) or not refined.strip():
        return False, "empty_refined_text"
    quality = llm_response_evaluation.get("quality_score")
    if not isinstance(quality, (int, float)) or float(quality) < llm_quality_threshold:
        return False, "quality_below_threshold"
    return True, "llm_accepted"


def _dataset_candidate_flag(
    *,
    selected_source: str,
    llm_response_evaluation: dict[str, Any] | None,
) -> bool:
    if selected_source == SELECTED_SOURCE_LLM_REFINED:
        return True
    if llm_response_evaluation is None:
        return False
    return (
        llm_response_evaluation.get("recommendation") == RECOMMENDATION_ACCEPT_CANDIDATE
        and llm_response_evaluation.get("dataset_status") == DATASET_STATUS_CANDIDATE
    )


def _blocked_candidate(
    *,
    surface: str,
    selection_reason: str,
    render: dict[str, Any],
    evaluation: dict[str, Any],
    render_trace: dict[str, Any] | None,
    llm_trace: dict[str, Any] | None,
    llm_response_evaluation: dict[str, Any] | None,
    validated_llm_response: dict[str, Any] | None,
) -> dict[str, Any]:
    return {
        "contract_version": DAY_SURFACE_CANDIDATE_V1_CONTRACT,
        "surface": surface,
        "selected_source": SELECTED_SOURCE_BLOCKED,
        "display_text": None,
        "source_keys": [],
        "generation_id": (
            llm_response_evaluation.get("generation_id") if llm_response_evaluation else None
        ),
        "quality_score": 0.0,
        "confidence": _confidence_from_render(render, evaluation),
        "degraded": True,
        "selection_reason": selection_reason,
        "used_llm": False,
        "dataset_candidate": _dataset_candidate_flag(
            selected_source=SELECTED_SOURCE_BLOCKED,
            llm_response_evaluation=llm_response_evaluation,
        ),
        "render_trace": _build_render_trace(render_trace),
        "llm_trace": _build_llm_trace(
            llm_trace,
            llm_response_evaluation=llm_response_evaluation,
            validated_llm_response=validated_llm_response,
        ),
    }


def _deterministic_candidate(
    *,
    surface: str,
    selection_reason: str,
    render: dict[str, Any],
    evaluation: dict[str, Any],
    render_surface: dict[str, Any],
    render_trace: dict[str, Any] | None,
    llm_trace: dict[str, Any] | None,
    llm_response_evaluation: dict[str, Any] | None,
    validated_llm_response: dict[str, Any] | None,
) -> dict[str, Any]:
    return {
        "contract_version": DAY_SURFACE_CANDIDATE_V1_CONTRACT,
        "surface": surface,
        "selected_source": SELECTED_SOURCE_DETERMINISTIC,
        "display_text": _deterministic_display_text(render_surface),
        "source_keys": _deterministic_source_keys(render_surface),
        "generation_id": None,
        "quality_score": round(_quality_from_evaluation(evaluation), 4),
        "confidence": _confidence_from_render(render, evaluation),
        "degraded": _surface_degraded(render, render_surface),
        "selection_reason": selection_reason,
        "used_llm": False,
        "dataset_candidate": _dataset_candidate_flag(
            selected_source=SELECTED_SOURCE_DETERMINISTIC,
            llm_response_evaluation=llm_response_evaluation,
        ),
        "render_trace": _build_render_trace(render_trace),
        "llm_trace": _build_llm_trace(
            llm_trace,
            llm_response_evaluation=llm_response_evaluation,
            validated_llm_response=validated_llm_response,
        ),
    }


def _llm_refined_candidate(
    *,
    surface: str,
    selection_reason: str,
    render: dict[str, Any],
    evaluation: dict[str, Any],
    render_surface: dict[str, Any],
    llm_response_evaluation: dict[str, Any],
    validated_llm_response: dict[str, Any],
    render_trace: dict[str, Any] | None,
    llm_trace: dict[str, Any] | None,
) -> dict[str, Any]:
    return {
        "contract_version": DAY_SURFACE_CANDIDATE_V1_CONTRACT,
        "surface": surface,
        "selected_source": SELECTED_SOURCE_LLM_REFINED,
        "display_text": validated_llm_response["refined_text"],
        "source_keys": list(validated_llm_response.get("source_keys_used") or []),
        "generation_id": llm_response_evaluation.get("generation_id"),
        "quality_score": float(llm_response_evaluation["quality_score"]),
        "confidence": _confidence_from_render(render, evaluation),
        "degraded": _surface_degraded(render, render_surface),
        "selection_reason": selection_reason,
        "used_llm": True,
        "dataset_candidate": True,
        "render_trace": _build_render_trace(render_trace),
        "llm_trace": _build_llm_trace(
            llm_trace,
            llm_response_evaluation=llm_response_evaluation,
            validated_llm_response=validated_llm_response,
        ),
    }


def select_day_surface_candidate_v1(
    render: dict[str, Any],
    evaluation: dict[str, Any],
    gate_decision: dict[str, Any],
    *,
    surface: str,
    llm_response_evaluation: dict[str, Any] | None = None,
    validated_llm_response: dict[str, Any] | None = None,
    render_trace: dict[str, Any] | None = None,
    llm_trace: dict[str, Any] | None = None,
    llm_quality_threshold: float = LLM_QUALITY_THRESHOLD,
) -> dict[str, Any]:
    """
    P1.13 — select surface display candidate from deterministic render or LLM refinement.

    No public UI, API endpoint, text mutation, retry, dataset approval, or memory writes.
    """
    _require_inputs(render, evaluation, gate_decision, surface)

    decision = gate_decision.get("decision")

    if decision == DECISION_BLOCKED:
        candidate = _blocked_candidate(
            surface=surface,
            selection_reason=f"SELECT:blocked:{gate_decision.get('blocked_reason', 'gate')}",
            render=render,
            evaluation=evaluation,
            render_trace=render_trace,
            llm_trace=llm_trace,
            llm_response_evaluation=llm_response_evaluation,
            validated_llm_response=validated_llm_response,
        )
    elif decision == DECISION_NO_CALL:
        render_surface = _surface_entry(render, surface)
        if render_surface is None or not render.get("renderable", False):
            candidate = _blocked_candidate(
                surface=surface,
                selection_reason="SELECT:no_call:blocked_no_surface",
                render=render,
                evaluation=evaluation,
                render_trace=render_trace,
                llm_trace=llm_trace,
                llm_response_evaluation=llm_response_evaluation,
                validated_llm_response=validated_llm_response,
            )
        else:
            candidate = _deterministic_candidate(
                surface=surface,
                selection_reason="SELECT:no_call:deterministic",
                render=render,
                evaluation=evaluation,
                render_surface=render_surface,
                render_trace=render_trace,
                llm_trace=llm_trace,
                llm_response_evaluation=llm_response_evaluation,
                validated_llm_response=validated_llm_response,
            )
    elif decision == DECISION_CALL_LLM:
        if gate_decision.get("surface") != surface:
            render_surface = _surface_entry(render, surface)
            if render_surface is not None and _deterministic_display_text(render_surface):
                candidate = _deterministic_candidate(
                    surface=surface,
                    selection_reason="SELECT:call_llm:fallback_wrong_surface",
                    render=render,
                    evaluation=evaluation,
                    render_surface=render_surface,
                    render_trace=render_trace,
                    llm_trace=llm_trace,
                    llm_response_evaluation=llm_response_evaluation,
                    validated_llm_response=validated_llm_response,
                )
            else:
                candidate = _blocked_candidate(
                    surface=surface,
                    selection_reason="SELECT:call_llm:blocked_no_fallback",
                    render=render,
                    evaluation=evaluation,
                    render_trace=render_trace,
                    llm_trace=llm_trace,
                    llm_response_evaluation=llm_response_evaluation,
                    validated_llm_response=validated_llm_response,
                )
        else:
            eligible, reject_reason = _llm_eligible(
                gate_decision=gate_decision,
                surface=surface,
                llm_response_evaluation=llm_response_evaluation,
                validated_llm_response=validated_llm_response,
                llm_quality_threshold=llm_quality_threshold,
            )
            render_surface = _surface_entry(render, surface)
            if eligible and render_surface is not None:
                candidate = _llm_refined_candidate(
                    surface=surface,
                    selection_reason="SELECT:call_llm:llm_accepted",
                    render=render,
                    evaluation=evaluation,
                    render_surface=render_surface,
                    llm_response_evaluation=llm_response_evaluation,  # type: ignore[arg-type]
                    validated_llm_response=validated_llm_response,  # type: ignore[arg-type]
                    render_trace=render_trace,
                    llm_trace=llm_trace,
                )
            elif render_surface is not None and _deterministic_display_text(render_surface):
                reason_map = {
                    "invalid_response_status": "SELECT:call_llm:fallback_invalid_response",
                    "invalid_evaluation_status": "SELECT:call_llm:fallback_invalid_response",
                    "recommendation_not_accept": "SELECT:call_llm:fallback_invalid_response",
                    "not_usable_candidate": "SELECT:call_llm:fallback_invalid_response",
                    "empty_refined_text": "SELECT:call_llm:fallback_invalid_response",
                    "quality_below_threshold": "SELECT:call_llm:fallback_low_quality",
                    "missing_llm_artifacts": "SELECT:call_llm:fallback_deterministic",
                }
                selection_reason = reason_map.get(
                    reject_reason, "SELECT:call_llm:fallback_deterministic"
                )
                candidate = _deterministic_candidate(
                    surface=surface,
                    selection_reason=selection_reason,
                    render=render,
                    evaluation=evaluation,
                    render_surface=render_surface,
                    render_trace=render_trace,
                    llm_trace=llm_trace,
                    llm_response_evaluation=llm_response_evaluation,
                    validated_llm_response=validated_llm_response,
                )
            else:
                candidate = _blocked_candidate(
                    surface=surface,
                    selection_reason="SELECT:call_llm:blocked_no_fallback",
                    render=render,
                    evaluation=evaluation,
                    render_trace=render_trace,
                    llm_trace=llm_trace,
                    llm_response_evaluation=llm_response_evaluation,
                    validated_llm_response=validated_llm_response,
                )
    else:
        raise DaySurfaceCandidateSelectionError(f"unsupported gate decision: {decision!r}")

    errors = validate_day_surface_candidate_v1(candidate)
    if errors:
        raise DaySurfaceCandidateSelectionError("; ".join(errors))
    return candidate


def validate_day_surface_candidate_v1(candidate: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if candidate.get("contract_version") != DAY_SURFACE_CANDIDATE_V1_CONTRACT:
        errors.append("invalid contract_version")
    for key in DAY_SURFACE_CANDIDATE_V1_KEYS:
        if key not in candidate:
            errors.append(f"missing field: {key}")

    selected = candidate.get("selected_source")
    used_llm = candidate.get("used_llm")
    if selected == SELECTED_SOURCE_LLM_REFINED:
        if used_llm is not True:
            errors.append("llm_refined requires used_llm=true")
        if not candidate.get("display_text"):
            errors.append("llm_refined requires display_text")
        if not candidate.get("generation_id"):
            errors.append("llm_refined requires generation_id")
    elif selected == SELECTED_SOURCE_DETERMINISTIC:
        if used_llm is not False:
            errors.append("deterministic requires used_llm=false")
        if not candidate.get("display_text"):
            errors.append("deterministic requires display_text")
    elif selected == SELECTED_SOURCE_BLOCKED:
        if candidate.get("display_text") is not None:
            errors.append("blocked requires display_text=null")
        if used_llm is not False:
            errors.append("blocked requires used_llm=false")
    else:
        errors.append("invalid selected_source")

    if candidate.get("used_in_ui") is True if "used_in_ui" in candidate else False:
        errors.append("used_in_ui must not be true in P1.13")

    render_trace = candidate.get("render_trace")
    if not isinstance(render_trace, dict):
        errors.append("render_trace must be object")
    llm_trace = candidate.get("llm_trace")
    if not isinstance(llm_trace, dict):
        errors.append("llm_trace must be object")

    score = candidate.get("quality_score")
    if not isinstance(score, (int, float)) or score < 0 or score > 1:
        errors.append("quality_score must be in [0, 1]")

    return errors

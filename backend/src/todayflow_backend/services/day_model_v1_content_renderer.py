"""P1.6 — Deterministic renderer contract for approved day content packages."""

from __future__ import annotations

from typing import Any

from todayflow_backend.services.day_model_v1_content_assembler import (
    DAY_CONTENT_PACKAGE_V1_CONTRACT,
    ENTRY_OUTPUT_FIELDS,
)
from todayflow_backend.services.day_model_v1_content_evaluator import (
    DAY_CONTENT_PACKAGE_EVALUATION_V1_CONTRACT,
    RECOMMENDATION_BLOCK,
    RECOMMENDATION_USE,
    RECOMMENDATION_USE_WITH_CAUTION,
    RECOMMENDATION_VALUES,
)
from todayflow_backend.services.day_model_v1_interpreter import LOW_CONFIDENCE_THRESHOLD

DAY_CONTENT_RENDER_V1_CONTRACT = "day_content_render_v1"

RENDER_BLOCK_REASON = "blocked_by_evaluation"

REQUIRED_RENDER_SURFACES = (
    "today_hero",
    "day_guidance_card",
    "risk_card",
    "action_card",
    "tempo_card",
)

OPTIONAL_RENDER_SURFACES = ("reflection_card",)

DAY_CONTENT_RENDER_V1_KEYS = frozenset(
    {
        "contract_version",
        "renderable",
        "reason",
        "degraded",
        "mode",
        "surfaces",
        "metadata",
    }
)


class DayContentRenderError(ValueError):
    """Raised when render inputs are invalid."""


def _require_inputs(
    package: dict[str, Any],
    evaluation: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    if package.get("contract_version") != DAY_CONTENT_PACKAGE_V1_CONTRACT:
        raise DayContentRenderError(
            f"expected package contract_version={DAY_CONTENT_PACKAGE_V1_CONTRACT!r}, "
            f"got {package.get('contract_version')!r}"
        )
    if evaluation.get("contract_version") != DAY_CONTENT_PACKAGE_EVALUATION_V1_CONTRACT:
        raise DayContentRenderError(
            f"expected evaluation contract_version={DAY_CONTENT_PACKAGE_EVALUATION_V1_CONTRACT!r}, "
            f"got {evaluation.get('contract_version')!r}"
        )
    metadata = package.get("metadata")
    if not isinstance(metadata, dict):
        raise DayContentRenderError("package.metadata must be object")
    recommendation = evaluation.get("recommendation")
    if recommendation not in RECOMMENDATION_VALUES:
        raise DayContentRenderError(f"invalid evaluation.recommendation: {recommendation!r}")
    return metadata, recommendation


def _copy_entry(entry: dict[str, Any]) -> dict[str, Any]:
    missing = [field for field in ENTRY_OUTPUT_FIELDS if field not in entry]
    if missing:
        raise DayContentRenderError(f"content entry missing fields: {missing}")
    return {field: entry[field] for field in ENTRY_OUTPUT_FIELDS}


def _display_text(entry: dict[str, Any], *, caution: bool, prefer_short: bool = False) -> str:
    if caution or prefer_short:
        return str(entry["text_short"])
    return str(entry["text_medium"])


def _build_surface_entry(
    entry: dict[str, Any],
    *,
    caution: bool,
    prefer_short: bool = False,
) -> dict[str, Any]:
    copied = _copy_entry(entry)
    return {
        **copied,
        "display_text": _display_text(entry, caution=caution, prefer_short=prefer_short),
    }


def _build_surface(
    surface_id: str,
    entries: list[dict[str, Any]],
    *,
    caution: bool,
    prefer_short: bool = False,
    high_confidence_label: bool,
) -> dict[str, Any]:
    rendered_entries = [
        _build_surface_entry(entry, caution=caution, prefer_short=prefer_short) for entry in entries
    ]
    return {
        "surface_id": surface_id,
        "entries": rendered_entries,
        "source_keys": [entry["key"] for entry in rendered_entries],
        "degraded": caution,
        "high_confidence_label": high_confidence_label and not caution,
    }


def _build_metadata(
    package: dict[str, Any],
    metadata: dict[str, Any],
    evaluation: dict[str, Any],
) -> dict[str, Any]:
    return {
        "content_keys": dict(metadata.get("content_keys", {})),
        "interpretation": {
            "strategy": metadata.get("strategy"),
            "opportunity_class": metadata.get("opportunity_class"),
            "risk_class": metadata.get("risk_class"),
            "tempo_instruction": metadata.get("tempo_instruction"),
            "action_mode": metadata.get("action_mode"),
            "reflection_mode": metadata.get("reflection_mode"),
            "pressure_level": metadata.get("pressure_level"),
            "confidence": metadata.get("confidence"),
        },
        "evaluation": {
            "valid": evaluation.get("valid"),
            "score": evaluation.get("score"),
            "recommendation": evaluation.get("recommendation"),
            "degraded": evaluation.get("degraded"),
            "issues": list(evaluation.get("issues", [])),
            "completeness_score": evaluation.get("completeness_score"),
            "confidence_score": evaluation.get("confidence_score"),
            "conflict_score": evaluation.get("conflict_score"),
            "repetition_score": evaluation.get("repetition_score"),
        },
        "source_package_contract": package.get("contract_version"),
        "source_evaluation_contract": evaluation.get("contract_version"),
    }


def render_day_content_package_v1(
    package: dict[str, Any],
    evaluation: dict[str, Any],
) -> dict[str, Any]:
    """
    P1.6 — deterministic render surfaces from package + evaluation.

    Read-only: no LLM, registry lookup, package mutation, or new prose.
    """
    metadata, recommendation = _require_inputs(package, evaluation)
    render_metadata = _build_metadata(package, metadata, evaluation)

    if recommendation == RECOMMENDATION_BLOCK:
        return {
            "contract_version": DAY_CONTENT_RENDER_V1_CONTRACT,
            "renderable": False,
            "reason": RENDER_BLOCK_REASON,
            "degraded": True,
            "mode": "blocked",
            "surfaces": {},
            "metadata": render_metadata,
        }

    caution = recommendation == RECOMMENDATION_USE_WITH_CAUTION
    confidence = float(metadata.get("confidence", 0.0))
    high_confidence_label = (
        recommendation == RECOMMENDATION_USE and confidence >= LOW_CONFIDENCE_THRESHOLD
    )

    headline = package.get("headline")
    if not isinstance(headline, dict):
        raise DayContentRenderError("package.headline required for renderable package")

    guidance = package.get("guidance")
    if not isinstance(guidance, list) or not guidance:
        raise DayContentRenderError("package.guidance required for renderable package")

    for slot in ("risk_warning", "action_hint", "tempo_hint"):
        if not isinstance(package.get(slot), dict):
            raise DayContentRenderError(f"package.{slot} required for renderable package")

    surfaces: dict[str, Any] = {
        "today_hero": _build_surface(
            "today_hero",
            [headline],
            caution=caution,
            prefer_short=True,
            high_confidence_label=high_confidence_label,
        ),
        "day_guidance_card": _build_surface(
            "day_guidance_card",
            guidance,
            caution=caution,
            high_confidence_label=high_confidence_label,
        ),
        "risk_card": _build_surface(
            "risk_card",
            [package["risk_warning"]],
            caution=caution,
            high_confidence_label=high_confidence_label,
        ),
        "action_card": _build_surface(
            "action_card",
            [package["action_hint"]],
            caution=caution,
            high_confidence_label=high_confidence_label,
        ),
        "tempo_card": _build_surface(
            "tempo_card",
            [package["tempo_hint"]],
            caution=caution,
            high_confidence_label=high_confidence_label,
        ),
    }

    reflection = package.get("reflection_hint")
    if isinstance(reflection, dict):
        surfaces["reflection_card"] = _build_surface(
            "reflection_card",
            [reflection],
            caution=caution,
            high_confidence_label=high_confidence_label,
        )

    return {
        "contract_version": DAY_CONTENT_RENDER_V1_CONTRACT,
        "renderable": True,
        "reason": None,
        "degraded": caution or bool(package.get("degraded", False)),
        "mode": "use_with_caution" if caution else "use",
        "surfaces": surfaces,
        "metadata": render_metadata,
    }

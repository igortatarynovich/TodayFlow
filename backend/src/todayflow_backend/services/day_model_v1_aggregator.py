"""DayModel v1 — preview pass-through (P0.4–P0.8) and multi-source aggregation (P1.0)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from todayflow_backend.data.reference_machine_loader import (
    VECTOR_AXIS_KEYS,
    ReferenceMachineContract,
    ReferenceMachineNotFoundError,
    ReferenceMachineRecord,
    load_reference_machine_contract,
)

PREVIEW_CONTRACT_VERSION = "day_model_v1_preview"
DAY_MODEL_V1_CONTRACT_VERSION = "day_model_v1"
PREVIEW_MODE_TAROT_ONLY = "tarot_only"
PREVIEW_MODE_NUMEROLOGY_ONLY = "numerology_only"
PREVIEW_MODE_ASTROLOGY_ONLY = "astrology_only"
PREVIEW_MODE_MULTI_SOURCE = "multi_source"

VECTOR_DOMAIN_WEIGHTS: dict[str, float] = {
    "tarot": 0.4,
    "numerology": 0.3,
    "astrology": 0.3,
}

TEMPO_DOMAIN_WEIGHTS: dict[str, float] = {
    "tarot": 0.2,
    "numerology": 0.4,
    "astrology": 0.4,
}

TEMPO_SCORES: dict[str, float] = {
    "slow": 0.25,
    "steady": 0.5,
    "dynamic": 0.75,
    "fast": 1.0,
}

RISK_SCORES: dict[str, float] = {
    "low": 0.25,
    "medium": 0.5,
    "high": 1.0,
}

EMOTIONAL_LOAD_SCORES: dict[str, float] = {
    "calm": 0.25,
    "neutral": 0.5,
    "intense": 1.0,
}

ASTROLOGY_COMPOSE_PLANET_WEIGHT = 0.55

DAY_MODEL_V1_PREVIEW_KEYS = frozenset(
    {
        "contract_version",
        "mode",
        "entity_code",
        "vector",
        "tempo",
        "risk",
        "risk_modifier",
        "emotional_load",
        "confidence",
        "sources",
    }
)

DAY_MODEL_V1_KEYS = frozenset(
    {
        "contract_version",
        "mode",
        "vector",
        "tempo",
        "risk",
        "risk_modifier",
        "emotional_load",
        "confidence",
        "sources",
        "weights_used",
        "missing_sources",
        "degraded",
    }
)


class DayModelAggregationError(ValueError):
    """Raised when P1.0 aggregation inputs are incomplete or invalid."""


@dataclass(frozen=True)
class _DomainSlice:
    """Normalized machine slice for one contributing domain."""

    domain: str
    entity_codes: tuple[str, ...]
    contract: ReferenceMachineContract


def _preview_mode_for_domain(domain: str) -> str:
    if domain == "tarot":
        return PREVIEW_MODE_TAROT_ONLY
    if domain == "numerology":
        return PREVIEW_MODE_NUMEROLOGY_ONLY
    if domain == "astrology":
        return PREVIEW_MODE_ASTROLOGY_ONLY
    raise ValueError(f"Unsupported preview domain: {domain!r}")


def _round_axis(value: float) -> float:
    return round(float(value), 2)


def _score_to_nearest_enum(score: float, mapping: dict[str, float]) -> str:
    return min(mapping.keys(), key=lambda key: abs(mapping[key] - score))


def compose_astrology_atom_pair(
    planet_code: str,
    sign_code: str,
    *,
    w_planet: float = ASTROLOGY_COMPOSE_PLANET_WEIGHT,
) -> ReferenceMachineContract:
    """
    In-memory compose of two atomic astrology records (Rules layer — not Reference JSON).

    Used as the Astrology domain input for P1.0 aggregation.
    """
    w_sign = 1.0 - w_planet
    planet = load_reference_machine_contract("astrology", planet_code)
    sign = load_reference_machine_contract("astrology", sign_code)
    pm = planet.machine_contract
    sm = sign.machine_contract

    vector_axes = {
        axis: _round_axis(w_planet * getattr(pm.vector, axis) + w_sign * getattr(sm.vector, axis))
        for axis in VECTOR_AXIS_KEYS
    }

    from todayflow_backend.data.reference_machine_loader import VectorAxes

    tempo_score = (
        w_planet * TEMPO_SCORES[pm.tempo] + w_sign * TEMPO_SCORES[sm.tempo]
    )
    risk_score = w_planet * RISK_SCORES[pm.risk] + w_sign * RISK_SCORES[sm.risk]
    load_score = (
        w_planet * EMOTIONAL_LOAD_SCORES[pm.emotional_load]
        + w_sign * EMOTIONAL_LOAD_SCORES[sm.emotional_load]
    )

    return ReferenceMachineContract(
        vector=VectorAxes(**vector_axes),
        tempo=_score_to_nearest_enum(tempo_score, TEMPO_SCORES),
        risk=_score_to_nearest_enum(risk_score, RISK_SCORES),
        risk_modifier=_round_axis(w_planet * pm.risk_modifier + w_sign * sm.risk_modifier),
        emotional_load=_score_to_nearest_enum(load_score, EMOTIONAL_LOAD_SCORES),
        confidence=round(min(pm.confidence, sm.confidence), 2),
    )


def _weighted_mean(values: dict[str, float], weights: dict[str, float]) -> float:
    total_weight = sum(weights[key] for key in values)
    if total_weight <= 0:
        raise DayModelAggregationError("weights must sum to a positive value")
    return sum(values[key] * weights[key] for key in values) / total_weight


def _confidence_weighted_vector(
    slices: dict[str, _DomainSlice],
    weights: dict[str, float],
) -> dict[str, float]:
    vector: dict[str, float] = {}
    for axis in VECTOR_AXIS_KEYS:
        numerator = 0.0
        denominator = 0.0
        for domain, slice_ in slices.items():
            weight = weights[domain]
            confidence = slice_.contract.confidence
            numerator += weight * confidence * getattr(slice_.contract.vector, axis)
            denominator += weight * confidence
        if denominator <= 0:
            raise DayModelAggregationError(f"vector axis {axis!r}: zero confidence-weight sum")
        vector[axis] = _round_axis(numerator / denominator)
    return vector


def _aggregate_enum_via_scores(
    slices: dict[str, _DomainSlice],
    weights: dict[str, float],
    *,
    field: str,
    score_map: dict[str, float],
) -> str:
    scores = {
        domain: score_map[getattr(slice_.contract, field)]
        for domain, slice_ in slices.items()
    }
    weighted = _weighted_mean(scores, weights)
    return _score_to_nearest_enum(weighted, score_map)


def build_day_model_v1_preview_from_record(record: ReferenceMachineRecord) -> dict[str, Any]:
    """Map one ReferenceMachineRecord to a stable preview dict (no LLM, no multi-source)."""
    mc = record.machine_contract
    return {
        "contract_version": PREVIEW_CONTRACT_VERSION,
        "mode": _preview_mode_for_domain(record.domain),
        "entity_code": record.entity_code,
        "vector": mc.vector.as_dict(),
        "tempo": mc.tempo,
        "risk": mc.risk,
        "risk_modifier": mc.risk_modifier,
        "emotional_load": mc.emotional_load,
        "confidence": mc.confidence,
        "sources": [record.source_id],
    }


def aggregate_day_model_v1(
    *,
    tarot_entity_code: str,
    numerology_entity_code: str,
    astrology_planet_code: str,
    astrology_sign_code: str,
    require_all_domains: bool = True,
) -> dict[str, Any]:
    """
    P1.0 — weighted multi-source DayModel from Tarot + Numerology + composed Astrology atoms.

    No UI, LLM, check-in, behavior, or API wiring.
    """
    missing: list[str] = []
    if not tarot_entity_code:
        missing.append("tarot")
    if not numerology_entity_code:
        missing.append("numerology")
    if not astrology_planet_code or not astrology_sign_code:
        missing.append("astrology")

    if missing:
        if require_all_domains:
            raise DayModelAggregationError(
                f"DayModel v1 requires all three domains; missing: {', '.join(missing)}"
            )
        return {
            "contract_version": DAY_MODEL_V1_CONTRACT_VERSION,
            "mode": PREVIEW_MODE_MULTI_SOURCE,
            "vector": {axis: 0.0 for axis in VECTOR_AXIS_KEYS},
            "tempo": "steady",
            "risk": "medium",
            "risk_modifier": 0.0,
            "emotional_load": "neutral",
            "confidence": 0.0,
            "sources": [],
            "weights_used": {
                "vector": VECTOR_DOMAIN_WEIGHTS,
                "tempo": TEMPO_DOMAIN_WEIGHTS,
            },
            "missing_sources": missing,
            "degraded": True,
        }

    try:
        tarot = load_reference_machine_contract("tarot", tarot_entity_code)
        numerology = load_reference_machine_contract("numerology", numerology_entity_code)
        astro_contract = compose_astrology_atom_pair(astrology_planet_code, astrology_sign_code)
    except ReferenceMachineNotFoundError as exc:
        raise DayModelAggregationError(
            f"unknown reference machine source: domain={exc.domain!r} entity_code={exc.entity_code!r}"
        ) from exc

    slices: dict[str, _DomainSlice] = {
        "tarot": _DomainSlice("tarot", (tarot.entity_code,), tarot.machine_contract),
        "numerology": _DomainSlice(
            "numerology", (numerology.entity_code,), numerology.machine_contract
        ),
        "astrology": _DomainSlice(
            "astrology",
            (astrology_planet_code, astrology_sign_code),
            astro_contract,
        ),
    }

    vector = _confidence_weighted_vector(slices, VECTOR_DOMAIN_WEIGHTS)
    tempo = _aggregate_enum_via_scores(
        slices, TEMPO_DOMAIN_WEIGHTS, field="tempo", score_map=TEMPO_SCORES
    )
    risk = _aggregate_enum_via_scores(
        slices, VECTOR_DOMAIN_WEIGHTS, field="risk", score_map=RISK_SCORES
    )
    emotional_load = _aggregate_enum_via_scores(
        slices, VECTOR_DOMAIN_WEIGHTS, field="emotional_load", score_map=EMOTIONAL_LOAD_SCORES
    )
    risk_modifier = _round_axis(
        _weighted_mean(
            {domain: slice_.contract.risk_modifier for domain, slice_ in slices.items()},
            VECTOR_DOMAIN_WEIGHTS,
        )
    )
    confidence = round(
        _weighted_mean(
            {domain: slice_.contract.confidence for domain, slice_ in slices.items()},
            VECTOR_DOMAIN_WEIGHTS,
        ),
        2,
    )

    sources = [
        tarot.entity_code,
        numerology.entity_code,
        astrology_planet_code,
        astrology_sign_code,
    ]

    return {
        "contract_version": DAY_MODEL_V1_CONTRACT_VERSION,
        "mode": PREVIEW_MODE_MULTI_SOURCE,
        "vector": vector,
        "tempo": tempo,
        "risk": risk,
        "risk_modifier": risk_modifier,
        "emotional_load": emotional_load,
        "confidence": confidence,
        "sources": sources,
        "weights_used": {
            "vector": dict(VECTOR_DOMAIN_WEIGHTS),
            "tempo": dict(TEMPO_DOMAIN_WEIGHTS),
            "risk": dict(VECTOR_DOMAIN_WEIGHTS),
            "emotional_load": dict(VECTOR_DOMAIN_WEIGHTS),
            "confidence": dict(VECTOR_DOMAIN_WEIGHTS),
            "risk_modifier": dict(VECTOR_DOMAIN_WEIGHTS),
        },
        "missing_sources": [],
        "degraded": False,
    }


def aggregate_day_model_v1_preview_tarot(entity_code: str) -> dict[str, Any]:
    """Tarot-only P0.4 path."""
    record = load_reference_machine_contract("tarot", entity_code)
    return build_day_model_v1_preview_from_record(record)


def aggregate_day_model_v1_preview_numerology(entity_code: str) -> dict[str, Any]:
    """Numerology-only P0.5 path."""
    record = load_reference_machine_contract("numerology", entity_code)
    return build_day_model_v1_preview_from_record(record)


def aggregate_day_model_v1_preview_astrology(entity_code: str) -> dict[str, Any]:
    """Astrology-only P0.8 atomic preview."""
    record = load_reference_machine_contract("astrology", entity_code)
    return build_day_model_v1_preview_from_record(record)

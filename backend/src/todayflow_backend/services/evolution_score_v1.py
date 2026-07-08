"""B1.4 — Evolution Score calculation / ECC integration path (read-only, no promotion)."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from todayflow_backend.data.evolution_score_contract_loader import (
    ECC_COMPONENT_BUCKETS,
    EVOLUTION_SCORE_CONTRACT_V1,
    is_forbidden_ecc_input,
    load_evolution_score_contract_v1,
)
from todayflow_backend.services.evolution_user_state_v1 import build_evolution_user_state_v1
from todayflow_backend.services.progression_signal_v1 import (
    aggregate_eligibility_progress_from_signals_v1,
    validate_progression_signal_v1,
)

EVOLUTION_SCORE_CALCULATION_V1_CONTRACT = "evolution_score_calculation_v1"
EVOLUTION_SCORE_CALCULATION_V1_VERSION = "1.0.0"

ECC_COMPONENT_SCORE_KEYS = frozenset(
    {"practice", "goal", "rhythm", "reflection", "profile_quality", "account_age_floor"}
)

EVOLUTION_SCORE_CALCULATION_V1_KEYS = frozenset(
    {
        "contract_version",
        "user_id",
        "evolution_score",
        "previous_evolution_score",
        "period_normalized_score",
        "component_scores",
        "weights_snapshot",
        "verified_signal_count",
        "excluded_inputs",
        "cum_confidence_snapshot",
        "promotion_allowed",
        "api_exposure_allowed",
        "calculated_at",
        "ecc_version",
        "version",
    }
)

FORBIDDEN_ES_CALCULATION_FIELDS = frozenset(
    {
        "achievement_id",
        "commerce_purchase",
        "promoted_stage",
        "stage_promoted_at",
        "profile_update",
        "llm_call",
        "recommendation_id",
    }
)


class EvolutionScoreCalculationError(ValueError):
    """Raised when ES calculation inputs or payload are invalid."""


def _utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def calculate_evolution_score_v1(
    *,
    user_id: str,
    signals: list[dict[str, Any]],
    previous_evolution_score: int = 0,
    cum_confidence_snapshot: float = 1.0,
    account_age_floor: float = 0.0,
    contract: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Read-only ES calculation from verified B1.3 progression signals.

    Does not promote stage, expose API, or mutate Profile/CUM.
    """
    ecc = contract if contract is not None else load_evolution_score_contract_v1()
    weights = ecc.get("weights") or {}
    mapping = ecc.get("signal_bucket_mapping") or {}
    targets = ecc.get("bucket_targets") or {}

    bucket_counts: dict[str, int] = {b: 0 for b in ECC_COMPONENT_SCORE_KEYS if b != "account_age_floor"}
    excluded_inputs: list[str] = []
    verified_signal_count = 0

    for index, signal in enumerate(signals):
        if not isinstance(signal, dict):
            excluded_inputs.append(f"signals[{index}]: not an object")
            continue

        signal_type = signal.get("signal_type")
        if isinstance(signal_type, str) and is_forbidden_ecc_input(signal_type, ecc):
            excluded_inputs.append(f"signals[{index}]: forbidden signal_type {signal_type!r}")
            continue

        if validate_progression_signal_v1(signal):
            excluded_inputs.append(f"signals[{index}]: invalid progression signal")
            continue

        if signal.get("contributes_to_gate_eligibility") is not True:
            excluded_inputs.append(f"signals[{index}]: not eligible for gate contribution")
            continue

        if not isinstance(signal_type, str):
            excluded_inputs.append(f"signals[{index}]: missing signal_type")
            continue

        bucket = mapping.get(signal_type)
        if bucket not in bucket_counts:
            excluded_inputs.append(f"signals[{index}]: unmapped signal_type {signal_type!r}")
            continue

        bucket_counts[bucket] += 1
        verified_signal_count += 1

    if not isinstance(cum_confidence_snapshot, (int, float)):
        cum_confidence_snapshot = 1.0
    cum_confidence_snapshot = max(0.0, min(1.0, float(cum_confidence_snapshot)))

    if not isinstance(account_age_floor, (int, float)):
        account_age_floor = 0.0
    account_age_floor = max(0.0, min(1.0, float(account_age_floor)))

    component_scores: dict[str, float] = {}
    for bucket in ("practice", "goal", "rhythm", "reflection", "profile_quality"):
        target = targets.get(bucket, 1)
        if not isinstance(target, int) or target < 1:
            target = 1
        count = bucket_counts.get(bucket, 0)
        normalized = min(1.0, count / target)
        if bucket == "profile_quality":
            normalized = min(1.0, normalized * cum_confidence_snapshot)
        component_scores[bucket] = round(normalized, 4)

    component_scores["account_age_floor"] = round(account_age_floor, 4)

    period_normalized_score = 0.0
    for bucket, weight in weights.items():
        if bucket in component_scores and isinstance(weight, (int, float)):
            period_normalized_score += float(weight) * component_scores[bucket]
    period_normalized_score = round(min(1.0, period_normalized_score), 4)

    multiplier = int(ecc.get("period_score_multiplier", 100))
    max_score = int(ecc.get("max_evolution_score", 1000))
    min_score = int(ecc.get("min_evolution_score", 0))

    if not isinstance(previous_evolution_score, int) or previous_evolution_score < 0:
        previous_evolution_score = 0

    delta = round(period_normalized_score * multiplier)
    evolution_score = max(min_score, min(max_score, previous_evolution_score + delta))

    result = {
        "contract_version": EVOLUTION_SCORE_CALCULATION_V1_CONTRACT,
        "user_id": user_id,
        "evolution_score": evolution_score,
        "previous_evolution_score": previous_evolution_score,
        "period_normalized_score": period_normalized_score,
        "component_scores": component_scores,
        "weights_snapshot": dict(weights),
        "verified_signal_count": verified_signal_count,
        "excluded_inputs": excluded_inputs,
        "cum_confidence_snapshot": cum_confidence_snapshot,
        "promotion_allowed": False,
        "api_exposure_allowed": False,
        "calculated_at": _utc_now_iso(),
        "ecc_version": ecc.get("ecc_version", "1.0.0"),
        "version": EVOLUTION_SCORE_CALCULATION_V1_VERSION,
    }

    errors = validate_evolution_score_calculation_v1(result, contract=ecc)
    if errors:
        raise EvolutionScoreCalculationError("; ".join(errors[:8]))
    return result


def build_evolution_state_with_ecc_v1(
    *,
    user_id: str,
    current_stage: str,
    stage_started_at: str,
    active_path_themes: list[str],
    completed_path_themes: list[str],
    signals: list[dict[str, Any]],
    previous_evolution_score: int = 0,
    cum_confidence_snapshot: float = 1.0,
    account_age_floor: float = 0.0,
    last_evaluated_at: str | None = None,
    status: str = "active",
) -> tuple[dict[str, Any], dict[str, Any]]:
    """
    B1.4 integration path: signals → ES calculation → B1.2 user state.

    Returns (evolution_score_calculation, evolution_user_state).
    """
    score_calc = calculate_evolution_score_v1(
        user_id=user_id,
        signals=signals,
        previous_evolution_score=previous_evolution_score,
        cum_confidence_snapshot=cum_confidence_snapshot,
        account_age_floor=account_age_floor,
    )
    progress = aggregate_eligibility_progress_from_signals_v1(signals)
    state = build_evolution_user_state_v1(
        user_id=user_id,
        current_stage=current_stage,
        stage_started_at=stage_started_at,
        active_path_themes=active_path_themes,
        completed_path_themes=completed_path_themes,
        progress_snapshot=progress,
        evolution_score_snapshot=score_calc["evolution_score"],
        last_evaluated_at=last_evaluated_at or score_calc["calculated_at"],
        status=status,
    )
    return score_calc, state


def validate_evolution_score_calculation_v1(
    result: dict[str, Any],
    *,
    contract: dict[str, Any] | None = None,
) -> list[str]:
    errors: list[str] = []

    if result.get("contract_version") != EVOLUTION_SCORE_CALCULATION_V1_CONTRACT:
        errors.append("invalid contract_version")

    for key in EVOLUTION_SCORE_CALCULATION_V1_KEYS:
        if key not in result:
            errors.append(f"missing field: {key}")

    for key in result:
        if key in FORBIDDEN_ES_CALCULATION_FIELDS:
            errors.append(f"forbidden field: {key}")

    if result.get("promotion_allowed") is not False:
        errors.append("promotion_allowed must be false")

    if result.get("api_exposure_allowed") is not False:
        errors.append("api_exposure_allowed must be false")

    score = result.get("evolution_score")
    prev = result.get("previous_evolution_score")
    if not isinstance(score, int) or score < 0 or score > 1000:
        errors.append("evolution_score must be int 0..1000")
    if not isinstance(prev, int) or prev < 0 or prev > 1000:
        errors.append("previous_evolution_score must be int 0..1000")

    period = result.get("period_normalized_score")
    if not isinstance(period, (int, float)) or period < 0 or period > 1:
        errors.append("period_normalized_score must be 0..1")

    components = result.get("component_scores")
    if not isinstance(components, dict):
        errors.append("component_scores must be object")
    elif set(components.keys()) != ECC_COMPONENT_SCORE_KEYS:
        errors.append("component_scores shape invalid")
    else:
        for bucket, value in components.items():
            if not isinstance(value, (int, float)) or value < 0 or value > 1:
                errors.append(f"component_scores.{bucket} must be 0..1")

    weights = result.get("weights_snapshot")
    ecc = contract if contract is not None else load_evolution_score_contract_v1()
    if not isinstance(weights, dict):
        errors.append("weights_snapshot must be object")
    elif set(weights.keys()) != set((ecc.get("weights") or {}).keys()):
        errors.append("weights_snapshot must match ECC contract")

    cum = result.get("cum_confidence_snapshot")
    if not isinstance(cum, (int, float)) or cum < 0 or cum > 1:
        errors.append("cum_confidence_snapshot must be 0..1")

    excluded = result.get("excluded_inputs")
    if not isinstance(excluded, list):
        errors.append("excluded_inputs must be array")

    count = result.get("verified_signal_count")
    if not isinstance(count, int) or count < 0:
        errors.append("verified_signal_count must be non-negative int")

    return errors

"""B1.4 — Load and validate Evolution Score contract (ECC CD)."""

from __future__ import annotations

import json
import os
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

from todayflow_backend.data.evolution_cd_validator import ALLOWED_PROGRESSION_SIGNAL_TYPES
from todayflow_backend.data.reference_machine_loader import DATA_ROOT

EVOLUTION_SCORE_CONTRACT_V1 = "evolution_score_contract_v1"

ECC_COMPONENT_BUCKETS = frozenset(
    {
        "practice",
        "goal",
        "rhythm",
        "reflection",
        "profile_quality",
        "account_age_floor",
    }
)

EVOLUTION_SCORE_CONTRACT_V1_TOP_KEYS = frozenset(
    {
        "contract_version",
        "domain",
        "ecc_version",
        "version",
        "status",
        "description",
        "weights",
        "bucket_targets",
        "signal_bucket_mapping",
        "excluded_signal_types",
        "forbidden_input_patterns",
        "period_score_multiplier",
        "max_evolution_score",
        "min_evolution_score",
    }
)

EVOLUTION_SCORE_CONTRACT_PATH = (
    DATA_ROOT / "reference" / "evolution" / "evolution_score_contract_v1.json"
)


class EvolutionScoreContractError(Exception):
    """Raised when evolution score contract is missing or invalid."""


def clear_evolution_score_contract_cache() -> None:
    load_evolution_score_contract_v1.cache_clear()


@lru_cache(maxsize=1)
def load_evolution_score_contract_v1() -> dict[str, Any]:
    path = Path(
        os.getenv("TODAYFLOW_EVOLUTION_SCORE_CONTRACT_PATH", EVOLUTION_SCORE_CONTRACT_PATH)
    )
    if not path.is_file():
        raise EvolutionScoreContractError(f"evolution score contract not found: {path}")
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    errors = validate_evolution_score_contract_v1(payload)
    if errors:
        raise EvolutionScoreContractError("; ".join(errors[:8]))
    return payload


def validate_evolution_score_contract_v1(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    if payload.get("contract_version") != EVOLUTION_SCORE_CONTRACT_V1:
        errors.append("invalid contract_version")

    for key in EVOLUTION_SCORE_CONTRACT_V1_TOP_KEYS:
        if key not in payload:
            errors.append(f"missing top-level field: {key}")

    if payload.get("domain") != "evolution":
        errors.append("domain must be evolution")

    weights = payload.get("weights")
    if not isinstance(weights, dict):
        errors.append("weights must be object")
    else:
        if set(weights.keys()) != ECC_COMPONENT_BUCKETS:
            errors.append("weights keys must match ECC component buckets")
        total = sum(v for v in weights.values() if isinstance(v, (int, float)))
        if abs(total - 1.0) > 0.001:
            errors.append(f"weights must sum to 1.0, got {total}")

    mapping = payload.get("signal_bucket_mapping")
    if not isinstance(mapping, dict):
        errors.append("signal_bucket_mapping must be object")
    else:
        if set(mapping.keys()) != set(ALLOWED_PROGRESSION_SIGNAL_TYPES):
            errors.append("signal_bucket_mapping must cover all B1.1 progression signal types")
        for signal_type, bucket in mapping.items():
            if bucket not in ECC_COMPONENT_BUCKETS - {"account_age_floor"}:
                errors.append(f"invalid bucket for {signal_type!r}: {bucket!r}")

    targets = payload.get("bucket_targets")
    if isinstance(targets, dict):
        for bucket in ("practice", "goal", "rhythm", "reflection", "profile_quality"):
            val = targets.get(bucket)
            if not isinstance(val, int) or val < 1:
                errors.append(f"bucket_targets.{bucket} must be positive int")

    forbidden = payload.get("forbidden_input_patterns")
    if not isinstance(forbidden, list) or not forbidden:
        errors.append("forbidden_input_patterns required")

    multiplier = payload.get("period_score_multiplier")
    if not isinstance(multiplier, int) or multiplier < 1:
        errors.append("period_score_multiplier must be positive int")

    max_score = payload.get("max_evolution_score")
    min_score = payload.get("min_evolution_score")
    if not isinstance(max_score, int) or max_score != 1000:
        errors.append("max_evolution_score must be 1000")
    if not isinstance(min_score, int) or min_score != 0:
        errors.append("min_evolution_score must be 0")

    return errors


def is_forbidden_ecc_input(value: str, contract: dict[str, Any] | None = None) -> bool:
    payload = contract if contract is not None else load_evolution_score_contract_v1()
    patterns = payload.get("forbidden_input_patterns") or []
    lowered = value.lower()
    for pattern in patterns:
        if isinstance(pattern, str) and pattern.lower() in lowered:
            return True
    return bool(re.search(r"(achievement|commerce|login|tarot|purchase|subscription|llm|reward|badge)", lowered, re.I))

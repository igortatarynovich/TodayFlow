"""P1.5 — Evaluate day_content_package_v1 quality before downstream use."""

from __future__ import annotations

from collections import Counter
from typing import Any

from todayflow_backend.services.day_model_v1_content_assembler import (
    DAY_CONTENT_PACKAGE_V1_CONTRACT,
    REQUIRED_PACKAGE_SLOTS,
)
from todayflow_backend.services.day_model_v1_interpreter import LOW_CONFIDENCE_THRESHOLD

DAY_CONTENT_PACKAGE_EVALUATION_V1_CONTRACT = "day_content_package_evaluation_v1"

RECOMMENDATION_USE = "use"
RECOMMENDATION_USE_WITH_CAUTION = "use_with_caution"
RECOMMENDATION_BLOCK = "block"

RECOMMENDATION_VALUES = frozenset(
    {RECOMMENDATION_USE, RECOMMENDATION_USE_WITH_CAUTION, RECOMMENDATION_BLOCK}
)

ACTION_STRATEGIES = frozenset({"act", "decide"})
REPETITION_KEY_THRESHOLD = 2

DAY_CONTENT_PACKAGE_EVALUATION_V1_KEYS = frozenset(
    {
        "contract_version",
        "valid",
        "score",
        "completeness_score",
        "confidence_score",
        "conflict_score",
        "repetition_score",
        "degraded",
        "issues",
        "recommendation",
    }
)


class DayContentPackageEvaluationError(ValueError):
    """Raised when package input is not a valid day_content_package_v1."""


def _require_package(package: dict[str, Any]) -> dict[str, Any]:
    if package.get("contract_version") != DAY_CONTENT_PACKAGE_V1_CONTRACT:
        raise DayContentPackageEvaluationError(
            f"expected contract_version={DAY_CONTENT_PACKAGE_V1_CONTRACT!r}, "
            f"got {package.get('contract_version')!r}"
        )
    metadata = package.get("metadata")
    if not isinstance(metadata, dict):
        raise DayContentPackageEvaluationError("package.metadata must be object")
    return metadata


def _slot_filled(package: dict[str, Any], slot: str) -> bool:
    if slot == "guidance":
        guidance = package.get("guidance")
        return isinstance(guidance, list) and len(guidance) > 0
    return package.get(slot) is not None


def _collect_entry_keys(package: dict[str, Any]) -> list[str]:
    keys: list[str] = []
    headline = package.get("headline")
    if isinstance(headline, dict) and headline.get("key"):
        keys.append(str(headline["key"]))
    guidance = package.get("guidance")
    if isinstance(guidance, list):
        for entry in guidance:
            if isinstance(entry, dict) and entry.get("key"):
                keys.append(str(entry["key"]))
    for slot in ("risk_warning", "action_hint", "tempo_hint", "reflection_hint"):
        entry = package.get(slot)
        if isinstance(entry, dict) and entry.get("key"):
            keys.append(str(entry["key"]))
    return keys


def _check_completeness(
    package: dict[str, Any],
    issues: list[str],
) -> tuple[float, bool]:
    missing: list[str] = []
    for slot in REQUIRED_PACKAGE_SLOTS:
        if not _slot_filled(package, slot):
            missing.append(slot)
    for slot in missing:
        issues.append(f"E-COMPLETENESS:missing_slot:{slot}")
    score = (len(REQUIRED_PACKAGE_SLOTS) - len(missing)) / len(REQUIRED_PACKAGE_SLOTS)
    blocked = bool(missing)
    return score, blocked


def _check_confidence(metadata: dict[str, Any], issues: list[str]) -> tuple[float, bool]:
    confidence = float(metadata.get("confidence", 0.0))
    caution = confidence < LOW_CONFIDENCE_THRESHOLD
    if caution:
        issues.append(f"E-CONFIDENCE:low:{confidence}")
    return confidence, caution


def _check_conflicts(metadata: dict[str, Any], issues: list[str]) -> tuple[float, bool]:
    strategy = metadata.get("strategy")
    tempo = metadata.get("tempo_instruction")
    pressure = metadata.get("pressure_level")
    risk_class = metadata.get("risk_class")

    conflict_count = 0
    if strategy in ACTION_STRATEGIES and tempo == "slow_down":
        issues.append("E-CONFLICT:strategy_action+tempo_slow_down")
        conflict_count += 1
    if pressure == "high" and tempo == "accelerate":
        issues.append("E-CONFLICT:pressure_high+tempo_accelerate")
        conflict_count += 1
    if risk_class == "emotional_overload" and pressure == "high":
        issues.append("E-CONFLICT:emotional_overload+pressure_high")
        conflict_count += 1

    score = max(0.0, 1.0 - 0.25 * conflict_count)
    return score, conflict_count > 0


def _check_repetition(package: dict[str, Any], issues: list[str]) -> tuple[float, bool]:
    counts = Counter(_collect_entry_keys(package))
    repeated = {key: count for key, count in counts.items() if count > REPETITION_KEY_THRESHOLD}
    for key, count in sorted(repeated.items()):
        issues.append(f"E-REPETITION:duplicate_key:{key}:count={count}")
    score = max(0.0, 1.0 - 0.2 * len(repeated))
    return score, bool(repeated)


def _check_degraded_propagation(
    package: dict[str, Any],
    metadata: dict[str, Any],
    issues: list[str],
) -> bool:
    flags = {
        "package": bool(package.get("degraded", False)),
        "metadata": bool(metadata.get("degraded", False)),
        "interpretation": bool(metadata.get("interpretation_degraded", False)),
        "mapping": bool(metadata.get("mapping_degraded", False)),
        "resolution": bool(metadata.get("resolution_degraded", False)),
    }
    degraded = any(flags.values())
    if flags["package"]:
        issues.append("E-DEGRADED:package")
    if flags["metadata"]:
        issues.append("E-DEGRADED:metadata")
    if flags["interpretation"]:
        issues.append("E-DEGRADED:interpretation")
    if flags["mapping"]:
        issues.append("E-DEGRADED:mapping")
    if flags["resolution"]:
        issues.append("E-DEGRADED:resolution")
    missing_keys = metadata.get("missing_keys") or []
    missing_slots = metadata.get("missing_slots") or []
    if missing_keys:
        issues.append(f"E-DEGRADED:missing_keys:{len(missing_keys)}")
    if missing_slots:
        issues.append(f"E-DEGRADED:missing_slots:{','.join(missing_slots)}")
    return degraded


def _overall_score(
    *,
    completeness_score: float,
    confidence_score: float,
    conflict_score: float,
    repetition_score: float,
) -> float:
    score = (
        0.35 * completeness_score
        + 0.25 * confidence_score
        + 0.20 * conflict_score
        + 0.20 * repetition_score
    )
    return round(max(0.0, min(1.0, score)), 2)


def _recommendation(
    *,
    blocked: bool,
    caution: bool,
    has_conflicts: bool,
    has_repetition: bool,
    evaluation_degraded: bool,
) -> str:
    if blocked:
        return RECOMMENDATION_BLOCK
    if caution or evaluation_degraded or has_conflicts or has_repetition:
        return RECOMMENDATION_USE_WITH_CAUTION
    return RECOMMENDATION_USE


def evaluate_day_content_package_v1(package: dict[str, Any]) -> dict[str, Any]:
    """
    P1.5 — quality evaluation for assembled day content package.

    Read-only: does not modify package, registry, or generate narrative.
    """
    metadata = _require_package(package)
    issues: list[str] = []

    completeness_score, blocked = _check_completeness(package, issues)
    confidence_score, low_confidence = _check_confidence(metadata, issues)
    conflict_score, has_conflicts = _check_conflicts(metadata, issues)
    repetition_score, has_repetition = _check_repetition(package, issues)
    evaluation_degraded = _check_degraded_propagation(package, metadata, issues)

    recommendation = _recommendation(
        blocked=blocked,
        caution=low_confidence,
        has_conflicts=has_conflicts,
        has_repetition=has_repetition,
        evaluation_degraded=evaluation_degraded,
    )

    score = _overall_score(
        completeness_score=completeness_score,
        confidence_score=confidence_score,
        conflict_score=conflict_score,
        repetition_score=repetition_score,
    )

    valid = recommendation != RECOMMENDATION_BLOCK
    degraded = (
        evaluation_degraded
        or low_confidence
        or has_conflicts
        or has_repetition
        or blocked
        or bool(package.get("degraded", False))
    )

    return {
        "contract_version": DAY_CONTENT_PACKAGE_EVALUATION_V1_CONTRACT,
        "valid": valid,
        "score": score,
        "completeness_score": round(completeness_score, 2),
        "confidence_score": round(confidence_score, 2),
        "conflict_score": round(conflict_score, 2),
        "repetition_score": round(repetition_score, 2),
        "degraded": degraded,
        "issues": issues,
        "recommendation": recommendation,
    }

"""B1.1 — Validate Evolution CD reference (stages, path themes, stage gates)."""

from __future__ import annotations

import re
from typing import Any

EVOLUTION_CD_V1_CONTRACT = "evolution_cd_v1"

EXPECTED_STAGE_COUNT = 7

CANONICAL_STAGE_ORDER: tuple[str, ...] = (
    "seeker",
    "observer",
    "practitioner",
    "explorer",
    "architect",
    "mentor",
    "master",
)

ALLOWED_CD_STATUSES = frozenset({"draft", "active"})

ALLOWED_STAGE_DEPTHS = frozenset(
    {"minimal", "basic", "standard", "enhanced", "expert", "full"}
)
ALLOWED_LLM_BUDGET_TIERS = frozenset({"none", "low", "medium", "high"})
ALLOWED_COMMERCE_VISIBILITY = frozenset({"none", "soft", "full"})

ALLOWED_PATH_DOMAINS = frozenset(
    {"life_area", "behavior", "energy", "relationship", "money"}
)

ALLOWED_CYCLE_LENGTHS = frozenset({7, 21, 30, 90})

ALLOWED_PROGRESSION_SIGNAL_TYPES = frozenset(
    {
        "practice_completed",
        "habit_streak_confirmed",
        "goal_milestone_reached",
        "evening_reflection_confirmed",
        "cycle_completed",
        "confirmed_pattern",
        "ritual_streak_confirmed",
        "weekly_goal_completed",
    }
)

FORBIDDEN_GATE_SIGNAL_PATTERN = re.compile(
    r"(achievement|commerce|unlock|purchase|reward|badge|payment|subscription)",
    re.I,
)

EVOLUTION_STAGE_V1_KEYS = frozenset(
    {
        "code",
        "order",
        "title",
        "short_description",
        "core_question",
        "allowed_depth",
        "max_context_lines",
        "llm_budget_tier",
        "commerce_visibility",
        "status",
        "version",
    }
)

EVOLUTION_PATH_THEME_V1_KEYS = frozenset(
    {
        "code",
        "title",
        "domain",
        "description",
        "compatible_stages",
        "suggested_cycle_lengths",
        "allowed_progression_signal_types",
        "status",
        "version",
    }
)

STAGE_GATE_V1_KEYS = frozenset(
    {
        "gate_id",
        "from_stage",
        "to_stage",
        "required_signal_types",
        "minimum_confirmed_patterns",
        "minimum_completed_cycles",
        "minimum_reflection_events",
        "minimum_active_days",
        "minimum_confidence",
        "manual_review_required",
        "status",
        "version",
    }
)

EVOLUTION_CD_V1_TOP_KEYS = frozenset(
    {
        "contract_version",
        "domain",
        "version",
        "status",
        "description",
        "evolution_stages",
        "evolution_path_themes",
        "stage_gates",
    }
)


class EvolutionCdValidationError(Exception):
    """Raised when evolution CD payload fails validation."""


def validate_evolution_cd_v1(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    if payload.get("contract_version") != EVOLUTION_CD_V1_CONTRACT:
        errors.append("invalid contract_version")

    for key in EVOLUTION_CD_V1_TOP_KEYS:
        if key not in payload:
            errors.append(f"missing top-level field: {key}")

    if payload.get("domain") != "evolution":
        errors.append("domain must be evolution")

    stages = payload.get("evolution_stages")
    themes = payload.get("evolution_path_themes")
    gates = payload.get("stage_gates")

    stage_codes: set[str] = set()
    if isinstance(stages, dict):
        errors.extend(_validate_stages(stages, stage_codes))
    else:
        errors.append("evolution_stages must be object")

    theme_codes: set[str] = set()
    if isinstance(themes, dict):
        errors.extend(_validate_path_themes(themes, stage_codes, theme_codes))
    else:
        errors.append("evolution_path_themes must be object")

    if isinstance(gates, list):
        errors.extend(_validate_stage_gates(gates, stage_codes))
    else:
        errors.append("stage_gates must be array")

    return errors


def _validate_stages(stages: dict[str, Any], stage_codes: set[str]) -> list[str]:
    errors: list[str] = []
    if len(stages) != EXPECTED_STAGE_COUNT:
        errors.append(f"expected {EXPECTED_STAGE_COUNT} stages, got {len(stages)}")

    orders: dict[int, str] = {}
    for code, entry in stages.items():
        stage_codes.add(code)
        if not isinstance(entry, dict):
            errors.append(f"stage {code}: must be object")
            continue

        for field in EVOLUTION_STAGE_V1_KEYS:
            if field not in entry:
                errors.append(f"stage {code}: missing field {field!r}")

        if entry.get("code") != code:
            errors.append(f"stage {code}: code mismatch")

        order = entry.get("order")
        if not isinstance(order, int) or order < 1 or order > EXPECTED_STAGE_COUNT:
            errors.append(f"stage {code}: invalid order")
        elif order in orders:
            errors.append(f"duplicate stage order {order}: {orders[order]} and {code}")
        else:
            orders[order] = code

        if entry.get("allowed_depth") not in ALLOWED_STAGE_DEPTHS:
            errors.append(f"stage {code}: invalid allowed_depth")
        if entry.get("llm_budget_tier") not in ALLOWED_LLM_BUDGET_TIERS:
            errors.append(f"stage {code}: invalid llm_budget_tier")
        if entry.get("commerce_visibility") not in ALLOWED_COMMERCE_VISIBILITY:
            errors.append(f"stage {code}: invalid commerce_visibility")
        if entry.get("status") not in ALLOWED_CD_STATUSES:
            errors.append(f"stage {code}: invalid status")

        max_lines = entry.get("max_context_lines")
        if not isinstance(max_lines, int) or max_lines < 0 or max_lines > 10:
            errors.append(f"stage {code}: invalid max_context_lines")

    expected_by_order = list(CANONICAL_STAGE_ORDER)
    for idx, expected_code in enumerate(expected_by_order, start=1):
        actual = orders.get(idx)
        if actual != expected_code:
            errors.append(
                f"stage order {idx}: expected {expected_code!r}, got {actual!r}"
            )

    if set(stages.keys()) != set(CANONICAL_STAGE_ORDER):
        errors.append("stage codes must match canonical set")

    return errors


def _validate_path_themes(
    themes: dict[str, Any],
    stage_codes: set[str],
    theme_codes: set[str],
) -> list[str]:
    errors: list[str] = []

    for code, entry in themes.items():
        theme_codes.add(code)
        if not isinstance(entry, dict):
            errors.append(f"path_theme {code}: must be object")
            continue

        for field in EVOLUTION_PATH_THEME_V1_KEYS:
            if field not in entry:
                errors.append(f"path_theme {code}: missing field {field!r}")

        if entry.get("code") != code:
            errors.append(f"path_theme {code}: code mismatch")

        if entry.get("domain") not in ALLOWED_PATH_DOMAINS:
            errors.append(f"path_theme {code}: invalid domain")

        if entry.get("status") not in ALLOWED_CD_STATUSES:
            errors.append(f"path_theme {code}: invalid status")

        compatible = entry.get("compatible_stages")
        if not isinstance(compatible, list) or not compatible:
            errors.append(f"path_theme {code}: compatible_stages required")
        else:
            for stage in compatible:
                if stage not in stage_codes:
                    errors.append(
                        f"path_theme {code}: invalid compatible_stage {stage!r}"
                    )

        lengths = entry.get("suggested_cycle_lengths")
        if not isinstance(lengths, list) or not lengths:
            errors.append(f"path_theme {code}: suggested_cycle_lengths required")
        else:
            for length in lengths:
                if length not in ALLOWED_CYCLE_LENGTHS:
                    errors.append(
                        f"path_theme {code}: invalid cycle length {length!r}"
                    )

        signal_types = entry.get("allowed_progression_signal_types")
        if not isinstance(signal_types, list) or not signal_types:
            errors.append(f"path_theme {code}: allowed_progression_signal_types required")
        else:
            for sig in signal_types:
                if sig not in ALLOWED_PROGRESSION_SIGNAL_TYPES:
                    errors.append(
                        f"path_theme {code}: invalid signal type {sig!r}"
                    )

    if len(theme_codes) != len(themes):
        errors.append("path theme codes must be unique")

    return errors


def _validate_stage_gates(gates: list[Any], stage_codes: set[str]) -> list[str]:
    errors: list[str] = []
    expected_transitions = list(
        zip(CANONICAL_STAGE_ORDER[:-1], CANONICAL_STAGE_ORDER[1:], strict=True)
    )

    if len(gates) != len(expected_transitions):
        errors.append(
            f"expected {len(expected_transitions)} stage gates, got {len(gates)}"
        )

    gate_ids: set[str] = set()
    seen_transitions: list[tuple[str, str]] = []

    for index, gate in enumerate(gates):
        prefix = f"stage_gate[{index}]"
        if not isinstance(gate, dict):
            errors.append(f"{prefix}: must be object")
            continue

        for field in STAGE_GATE_V1_KEYS:
            if field not in gate:
                errors.append(f"{prefix}: missing field {field!r}")

        gate_id = gate.get("gate_id")
        if isinstance(gate_id, str):
            if gate_id in gate_ids:
                errors.append(f"duplicate gate_id {gate_id!r}")
            gate_ids.add(gate_id)

        from_stage = gate.get("from_stage")
        to_stage = gate.get("to_stage")
        if from_stage not in stage_codes:
            errors.append(f"{prefix}: invalid from_stage {from_stage!r}")
        if to_stage not in stage_codes:
            errors.append(f"{prefix}: invalid to_stage {to_stage!r}")

        if isinstance(from_stage, str) and isinstance(to_stage, str):
            seen_transitions.append((from_stage, to_stage))
            from_idx = (
                CANONICAL_STAGE_ORDER.index(from_stage)
                if from_stage in CANONICAL_STAGE_ORDER
                else -1
            )
            to_idx = (
                CANONICAL_STAGE_ORDER.index(to_stage)
                if to_stage in CANONICAL_STAGE_ORDER
                else -1
            )
            if from_idx < 0 or to_idx != from_idx + 1:
                errors.append(
                    f"{prefix}: gate must advance exactly one stage sequentially"
                )

        signals = gate.get("required_signal_types")
        if not isinstance(signals, list) or not signals:
            errors.append(f"{prefix}: required_signal_types required")
        else:
            for sig in signals:
                if sig not in ALLOWED_PROGRESSION_SIGNAL_TYPES:
                    errors.append(f"{prefix}: invalid signal type {sig!r}")
                if isinstance(sig, str) and FORBIDDEN_GATE_SIGNAL_PATTERN.search(sig):
                    errors.append(
                        f"{prefix}: forbidden signal type (achievement/commerce): {sig!r}"
                    )

        if gate.get("status") not in ALLOWED_CD_STATUSES:
            errors.append(f"{prefix}: invalid status")

        conf = gate.get("minimum_confidence")
        if not isinstance(conf, (int, float)) or conf < 0 or conf > 1:
            errors.append(f"{prefix}: minimum_confidence must be 0..1")

        for int_field in (
            "minimum_confirmed_patterns",
            "minimum_completed_cycles",
            "minimum_reflection_events",
            "minimum_active_days",
        ):
            val = gate.get(int_field)
            if not isinstance(val, int) or val < 0:
                errors.append(f"{prefix}: {int_field} must be non-negative int")

        if not isinstance(gate.get("manual_review_required"), bool):
            errors.append(f"{prefix}: manual_review_required must be bool")

    if seen_transitions != expected_transitions:
        errors.append(
            f"stage gates must follow sequential transitions: {expected_transitions}"
        )

    return errors

"""P1.11 — LLM refinement response contract and validator (no API call or auto-fix)."""

from __future__ import annotations

import re
from typing import Any

from todayflow_backend.services.day_model_v1_interpreter import (
    RISK_CLASS_VALUES,
    STRATEGY_VALUES,
    TEMPO_INSTRUCTION_VALUES,
)
from todayflow_backend.services.day_model_v1_llm_prompt import (
    DAY_LLM_PROMPT_V1_CONTRACT,
    validate_day_llm_prompt_v1,
)

DAY_LLM_REFINEMENT_RESPONSE_V1_CONTRACT = "day_llm_refinement_response_v1"

RESPONSE_STATUS_VALID = "valid"
RESPONSE_STATUS_INVALID = "invalid"

DAY_LLM_REFINEMENT_RESPONSE_V1_KEYS = frozenset(
    {
        "contract_version",
        "refined_text",
        "changed",
        "source_keys_used",
        "warnings",
        "status",
        "issues",
    }
)

RAW_RESPONSE_REQUIRED_FIELDS = frozenset(
    {"refined_text", "changed", "source_keys_used", "warnings"}
)

ASTROLOGY_PATTERNS = (
    re.compile(r"\bhoroscope\b", re.I),
    re.compile(r"\bzodiac\b", re.I),
    re.compile(r"\b(mars|venus|mercury|jupiter|saturn|uranus|neptune|pluto)\s+in\s+\w+", re.I),
    re.compile(r"\b(astrology|astrological|natal chart|birth chart)\b", re.I),
    re.compile(r"\bstars align\b", re.I),
)

TAROT_PATTERNS = (
    re.compile(r"\btarot\b", re.I),
    re.compile(r"\bmajor arcana\b", re.I),
    re.compile(r"\b(the )?(chariot|hermit|fool|magician|high priestess)\b", re.I),
)

NUMEROLOGY_PATTERNS = (
    re.compile(r"\bnumerology\b", re.I),
    re.compile(r"\blife path\b", re.I),
    re.compile(r"\bdestiny number\b", re.I),
)

DIAGNOSIS_PATTERNS = (
    re.compile(r"\bdiagnos", re.I),
    re.compile(r"\bdisorder\b", re.I),
    re.compile(r"\bclinical(ly)?\b", re.I),
)

PROMISE_OUTCOME_PATTERNS = (
    re.compile(r"\bguaranteed\b", re.I),
    re.compile(r"\byou will (succeed|win|get|receive)\b", re.I),
    re.compile(r"\boutcome is (certain|guaranteed)\b", re.I),
    re.compile(r"\bdestiny\b", re.I),
    re.compile(r"\bfate\b", re.I),
    re.compile(r"\bthe universe\b", re.I),
)

STRATEGY_SIGNALS = {
    "act": re.compile(r"\b(take action|act today|direct action|one clear step)\b", re.I),
    "reflect": re.compile(r"\b(reflect|step back|think before acting|make room to think)\b", re.I),
    "stabilize": re.compile(r"\b(steady|stabiliz|keep things steady)\b", re.I),
    "simplify": re.compile(r"\b(simplify|reduce scope|fewer moving parts)\b", re.I),
    "connect": re.compile(r"\b(connect with others|reach out|communication)\b", re.I),
    "plan": re.compile(r"\b(plan ahead|planning|map out)\b", re.I),
    "recover": re.compile(r"\b(recover|rest and reset|recharge)\b", re.I),
    "decide": re.compile(r"\b(decide|make a decision|choose one path)\b", re.I),
    "observe": re.compile(r"\b(observe|watch and wait|hold off)\b", re.I),
}

RISK_SIGNALS = {
    "overpressure": re.compile(r"\b(overpressure|too much pressure|overloaded)\b", re.I),
    "avoidance": re.compile(r"\b(avoidance|avoiding|procrastinat)\b", re.I),
    "conflict": re.compile(r"\b(conflict|confrontation|argument)\b", re.I),
    "scattered_focus": re.compile(r"\b(scattered|unfocused|too many threads)\b", re.I),
    "emotional_overload": re.compile(r"\b(emotional overload|overwhelmed emotionally)\b", re.I),
    "stagnation": re.compile(r"\b(stagnat|stuck|no progress)\b", re.I),
    "impulsivity": re.compile(r"\b(impulsiv|rash move|snap decision)\b", re.I),
}

TEMPO_SIGNALS = {
    "slow_down": re.compile(r"\b(slow down|slow pace|pause the pace)\b", re.I),
    "keep_steady": re.compile(r"\b(steady pace|keep steady|consistent pace)\b", re.I),
    "move": re.compile(r"\b(move forward|pick up pace|keep moving)\b", re.I),
    "accelerate": re.compile(r"\b(accelerate|speed up|move quickly|fast pace)\b", re.I),
}

DIMENSION_PREFIXES = {
    "strategy": "day.strategy.",
    "risk": "day.risk.",
    "tempo": "day.tempo.",
}


class DayModelLlmResponseValidationError(ValueError):
    """Raised when the prompt argument is invalid for response validation."""


def _require_valid_prompt(prompt: dict[str, Any]) -> None:
    if prompt.get("contract_version") != DAY_LLM_PROMPT_V1_CONTRACT:
        raise DayModelLlmResponseValidationError("prompt has invalid contract_version")
    errors = validate_day_llm_prompt_v1(prompt)
    if errors:
        raise DayModelLlmResponseValidationError("; ".join(errors))


def _baseline_text(prompt: dict[str, Any]) -> str:
    fragments = (prompt.get("input_payload") or {}).get("fragments") or []
    parts = [str(item.get("text", "")) for item in fragments if isinstance(item, dict)]
    return " ".join(parts)


def _allowed_source_keys(prompt: dict[str, Any]) -> set[str]:
    keys = (prompt.get("input_payload") or {}).get("source_keys") or []
    return {str(key) for key in keys}


def _baseline_dimension_values(source_keys: set[str], prefix: str, allowed: frozenset[str]) -> set[str]:
    values: set[str] = set()
    for key in source_keys:
        if key.startswith(prefix):
            value = key[len(prefix) :]
            if value in allowed:
                values.add(value)
    return values


def _detect_dimension_values(text: str, signals: dict[str, re.Pattern[str]]) -> set[str]:
    detected: set[str] = set()
    for value, pattern in signals.items():
        if pattern.search(text):
            detected.add(value)
    return detected


def _check_new_forbidden_patterns(
    text: str,
    baseline_text: str,
    patterns: tuple[re.Pattern[str], ...],
    issue_code: str,
    issues: list[str],
) -> None:
    for pattern in patterns:
        if pattern.search(text) and not pattern.search(baseline_text):
            issues.append(issue_code)
            return


def _check_always_forbidden_patterns(
    text: str,
    patterns: tuple[re.Pattern[str], ...],
    issue_code: str,
    issues: list[str],
) -> None:
    for pattern in patterns:
        if pattern.search(text):
            issues.append(issue_code)
            return


def _check_dimension_unchanged(
    text: str,
    baseline_values: set[str],
    signals: dict[str, re.Pattern[str]],
    issue_code: str,
    issues: list[str],
) -> None:
    if not baseline_values:
        return
    detected = _detect_dimension_values(text, signals)
    foreign = detected - baseline_values
    if foreign:
        issues.append(f"{issue_code}:{','.join(sorted(foreign))}")


def _normalize_raw_response(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, dict):
        return {}
    return raw


def validate_day_llm_refinement_response_v1(
    response: dict[str, Any],
    prompt: dict[str, Any],
) -> dict[str, Any]:
    """
    P1.11 — validate LLM refinement response against prompt constraints.

    Returns day_llm_refinement_response_v1 with status valid/invalid and machine-readable issues.
    Does not auto-fix, persist, or expose to UI.
    """
    _require_valid_prompt(prompt)

    raw = _normalize_raw_response(response)
    issues: list[str] = []

    if not RAW_RESPONSE_REQUIRED_FIELDS.issubset(raw.keys()):
        missing = sorted(RAW_RESPONSE_REQUIRED_FIELDS - set(raw.keys()))
        issues.append(f"E-RESP-WRONG_SHAPE:missing={','.join(missing)}")

    refined_text = raw.get("refined_text")
    if refined_text is None:
        issues.append("E-RESP-MISSING_REFINED_TEXT")
        refined_text = ""
    elif not isinstance(refined_text, str):
        issues.append("E-RESP-WRONG_SHAPE:refined_text_type")
        refined_text = str(refined_text)
    elif not refined_text.strip():
        issues.append("E-RESP-EMPTY_REFINED_TEXT")

    changed = raw.get("changed")
    if not isinstance(changed, bool):
        issues.append("E-RESP-WRONG_SHAPE:changed_type")
        changed = False

    source_keys_used = raw.get("source_keys_used")
    if not isinstance(source_keys_used, list):
        issues.append("E-RESP-WRONG_SHAPE:source_keys_used_type")
        source_keys_used = []
    else:
        source_keys_used = [str(key) for key in source_keys_used]

    warnings = raw.get("warnings")
    if not isinstance(warnings, list):
        issues.append("E-RESP-WARNINGS_NOT_LIST")
        warnings = []
    else:
        warnings = [str(item) for item in warnings]

    constraints = prompt.get("constraints") or {}
    max_length = constraints.get("max_length_chars")
    if isinstance(max_length, int) and max_length > 0 and len(refined_text) > max_length:
        issues.append(f"E-RESP-TOO_LONG:max={max_length}:actual={len(refined_text)}")

    allowed_keys = _allowed_source_keys(prompt)
    for key in source_keys_used:
        if key not in allowed_keys:
            issues.append(f"E-RESP-UNKNOWN_SOURCE_KEY:{key}")

    baseline_text = _baseline_text(prompt)
    text = refined_text

    _check_new_forbidden_patterns(text, baseline_text, ASTROLOGY_PATTERNS, "E-RESP-FORBIDDEN_ASTROLOGY", issues)
    _check_new_forbidden_patterns(text, baseline_text, TAROT_PATTERNS, "E-RESP-FORBIDDEN_TAROT", issues)
    _check_new_forbidden_patterns(text, baseline_text, NUMEROLOGY_PATTERNS, "E-RESP-FORBIDDEN_NUMEROLOGY", issues)
    _check_always_forbidden_patterns(text, DIAGNOSIS_PATTERNS, "E-RESP-FORBIDDEN_DIAGNOSIS", issues)
    _check_always_forbidden_patterns(text, PROMISE_OUTCOME_PATTERNS, "E-RESP-FORBIDDEN_PROMISE_OUTCOME", issues)

    _check_dimension_unchanged(
        text,
        _baseline_dimension_values(allowed_keys, DIMENSION_PREFIXES["strategy"], STRATEGY_VALUES),
        STRATEGY_SIGNALS,
        "E-RESP-STRATEGY_CHANGED",
        issues,
    )
    _check_dimension_unchanged(
        text,
        _baseline_dimension_values(allowed_keys, DIMENSION_PREFIXES["risk"], RISK_CLASS_VALUES),
        RISK_SIGNALS,
        "E-RESP-RISK_CHANGED",
        issues,
    )
    _check_dimension_unchanged(
        text,
        _baseline_dimension_values(allowed_keys, DIMENSION_PREFIXES["tempo"], TEMPO_INSTRUCTION_VALUES),
        TEMPO_SIGNALS,
        "E-RESP-TEMPO_CHANGED",
        issues,
    )

    status = RESPONSE_STATUS_VALID if not issues else RESPONSE_STATUS_INVALID

    return {
        "contract_version": DAY_LLM_REFINEMENT_RESPONSE_V1_CONTRACT,
        "refined_text": refined_text,
        "changed": changed,
        "source_keys_used": source_keys_used,
        "warnings": warnings,
        "status": status,
        "issues": issues,
    }

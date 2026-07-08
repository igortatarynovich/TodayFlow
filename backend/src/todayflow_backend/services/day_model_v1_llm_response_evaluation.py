"""P1.12 — LLM response evaluation and post-call record integration (no UI, retry, or LLM call)."""

from __future__ import annotations

import hashlib
from typing import Any

from todayflow_backend.services.day_model_v1_llm_prompt import (
    DAY_LLM_PROMPT_V1_CONTRACT,
    validate_day_llm_prompt_v1,
)
from todayflow_backend.services.day_model_v1_llm_refinement_response import (
    DAY_LLM_REFINEMENT_RESPONSE_V1_CONTRACT,
    RESPONSE_STATUS_INVALID,
    RESPONSE_STATUS_VALID,
    validate_day_llm_refinement_response_v1,
)
from todayflow_backend.services.day_model_v1_llm_request_record import (
    DAY_LLM_POSTCALL_RECORD_V1_CONTRACT,
    DAY_LLM_PRECALL_RECORD_V1_CONTRACT,
    validate_llm_postcall_record_v1,
)

DAY_LLM_RESPONSE_EVALUATION_V1_CONTRACT = "day_llm_response_evaluation_v1"

RECOMMENDATION_ACCEPT_CANDIDATE = "accept_candidate"
RECOMMENDATION_REJECT = "reject"

DATASET_STATUS_CANDIDATE = "candidate"
DATASET_STATUS_REJECTED = "rejected"

DAY_LLM_RESPONSE_EVALUATION_V1_KEYS = frozenset(
    {
        "contract_version",
        "llm_response_evaluation_id",
        "generation_id",
        "response_status",
        "quality_score",
        "safety_flags",
        "contract_issues",
        "usable_candidate",
        "dataset_status",
        "used_in_ui",
        "recommendation",
    }
)

FORBIDDEN_ISSUE_PREFIXES = (
    "E-RESP-FORBIDDEN_",
    "E-RESP-STRATEGY_CHANGED",
    "E-RESP-RISK_CHANGED",
    "E-RESP-TEMPO_CHANGED",
)

HARD_REJECT_ISSUE_PREFIXES = (
    "E-RESP-EMPTY_REFINED_TEXT",
    "E-RESP-MISSING_REFINED_TEXT",
    "E-RESP-TOO_LONG",
    "E-RESP-UNKNOWN_SOURCE_KEY",
    "E-RESP-WRONG_SHAPE",
)

QUALITY_BASE = 1.0
QUALITY_WARNING_PENALTY = 0.08
QUALITY_UNCHANGED_PENALTY = 0.05
QUALITY_REJECTED_SCORE = 0.0

ISSUE_TO_SAFETY_FLAG = {
    "E-RESP-FORBIDDEN_ASTROLOGY": "forbidden_astrology",
    "E-RESP-FORBIDDEN_TAROT": "forbidden_tarot",
    "E-RESP-FORBIDDEN_NUMEROLOGY": "forbidden_numerology",
    "E-RESP-FORBIDDEN_DIAGNOSIS": "forbidden_diagnosis",
    "E-RESP-FORBIDDEN_PROMISE_OUTCOME": "forbidden_promise_outcome",
    "E-RESP-STRATEGY_CHANGED": "strategy_changed",
    "E-RESP-RISK_CHANGED": "risk_changed",
    "E-RESP-TEMPO_CHANGED": "tempo_changed",
}


class DayModelLlmResponseEvaluationError(ValueError):
    """Raised when evaluation inputs are invalid."""


def derive_llm_response_evaluation_id(generation_id: str, prompt_id: str) -> str:
    payload = f"{generation_id}:{prompt_id}"
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]
    return f"llm-eval-{digest}"


def _require_validated_response(validated_response: dict[str, Any]) -> None:
    if validated_response.get("contract_version") != DAY_LLM_REFINEMENT_RESPONSE_V1_CONTRACT:
        raise DayModelLlmResponseEvaluationError(
            "validated_response has invalid contract_version"
        )


def _require_prompt(prompt: dict[str, Any]) -> None:
    if prompt.get("contract_version") != DAY_LLM_PROMPT_V1_CONTRACT:
        raise DayModelLlmResponseEvaluationError("prompt has invalid contract_version")
    errors = validate_day_llm_prompt_v1(prompt)
    if errors:
        raise DayModelLlmResponseEvaluationError("; ".join(errors))


def _issue_is_forbidden(issue: str) -> bool:
    return any(issue.startswith(prefix) for prefix in FORBIDDEN_ISSUE_PREFIXES)


def _issue_is_hard_reject(issue: str) -> bool:
    if _issue_is_forbidden(issue):
        return True
    return any(issue.startswith(prefix) for prefix in HARD_REJECT_ISSUE_PREFIXES)


def _safety_flags_from_issues(issues: list[str]) -> list[str]:
    flags: list[str] = []
    for issue in issues:
        base = issue.split(":", 1)[0]
        flag = ISSUE_TO_SAFETY_FLAG.get(base)
        if flag and flag not in flags:
            flags.append(flag)
    return sorted(flags)


def _compute_quality_score(
    *,
    response_status: str,
    issues: list[str],
    warnings: list[str],
    changed: bool,
) -> float:
    if response_status == RESPONSE_STATUS_INVALID or issues:
        return QUALITY_REJECTED_SCORE

    score = QUALITY_BASE
    if warnings:
        score -= QUALITY_WARNING_PENALTY * len(warnings)
    if not changed:
        score -= QUALITY_UNCHANGED_PENALTY
    return max(0.0, min(1.0, round(score, 4)))


def _should_reject(*, response_status: str, issues: list[str]) -> bool:
    if response_status == RESPONSE_STATUS_INVALID:
        return True
    return any(_issue_is_hard_reject(issue) for issue in issues)


def evaluate_day_llm_response_v1(
    validated_response: dict[str, Any],
    prompt: dict[str, Any],
    *,
    generation_id: str,
    llm_response_evaluation_id: str | None = None,
) -> dict[str, Any]:
    """
    P1.12 — evaluate validated LLM refinement response for dataset/UI candidacy.

    Does not modify refined_text, call LLM, expose UI, or approve final output.
    """
    _require_validated_response(validated_response)
    _require_prompt(prompt)

    if not generation_id or not str(generation_id).strip():
        raise DayModelLlmResponseEvaluationError("generation_id is required")
    if prompt.get("generation_id") != generation_id:
        raise DayModelLlmResponseEvaluationError(
            "generation_id must match prompt.generation_id"
        )

    response_status = validated_response.get("status", RESPONSE_STATUS_INVALID)
    issues = list(validated_response.get("issues") or [])
    warnings = list(validated_response.get("warnings") or [])
    changed = bool(validated_response.get("changed", False))

    reject = _should_reject(response_status=response_status, issues=issues)
    recommendation = RECOMMENDATION_REJECT if reject else RECOMMENDATION_ACCEPT_CANDIDATE
    usable_candidate = not reject
    dataset_status = DATASET_STATUS_REJECTED if reject else DATASET_STATUS_CANDIDATE

    evaluation = {
        "contract_version": DAY_LLM_RESPONSE_EVALUATION_V1_CONTRACT,
        "llm_response_evaluation_id": llm_response_evaluation_id
        or derive_llm_response_evaluation_id(generation_id, prompt["prompt_id"]),
        "generation_id": generation_id,
        "response_status": response_status,
        "quality_score": _compute_quality_score(
            response_status=response_status,
            issues=issues,
            warnings=warnings,
            changed=changed,
        ),
        "safety_flags": _safety_flags_from_issues(issues),
        "contract_issues": issues,
        "usable_candidate": usable_candidate,
        "dataset_status": dataset_status,
        "used_in_ui": False,
        "recommendation": recommendation,
    }

    eval_errors = validate_day_llm_response_evaluation_v1(evaluation)
    if eval_errors:
        raise DayModelLlmResponseEvaluationError("; ".join(eval_errors))
    return evaluation


def evaluate_raw_llm_response_v1(
    raw_response: dict[str, Any],
    prompt: dict[str, Any],
    *,
    generation_id: str,
    llm_response_evaluation_id: str | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Validate (P1.11) then evaluate (P1.12). Returns (validated_response, evaluation)."""
    validated = validate_day_llm_refinement_response_v1(raw_response, prompt)
    evaluation = evaluate_day_llm_response_v1(
        validated,
        prompt,
        generation_id=generation_id,
        llm_response_evaluation_id=llm_response_evaluation_id,
    )
    return validated, evaluation


def validate_day_llm_response_evaluation_v1(evaluation: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if evaluation.get("contract_version") != DAY_LLM_RESPONSE_EVALUATION_V1_CONTRACT:
        errors.append("invalid contract_version")
    for key in DAY_LLM_RESPONSE_EVALUATION_V1_KEYS:
        if key not in evaluation:
            errors.append(f"missing field: {key}")

    if evaluation.get("used_in_ui") is not False:
        errors.append("used_in_ui must be false in P1.12")

    response_status = evaluation.get("response_status")
    recommendation = evaluation.get("recommendation")
    usable = evaluation.get("usable_candidate")
    dataset_status = evaluation.get("dataset_status")

    if response_status == RESPONSE_STATUS_INVALID:
        if usable is not False:
            errors.append("invalid response must have usable_candidate=false")
        if dataset_status != DATASET_STATUS_REJECTED:
            errors.append("invalid response must have dataset_status=rejected")
        if recommendation != RECOMMENDATION_REJECT:
            errors.append("invalid response must recommend reject")
    elif response_status == RESPONSE_STATUS_VALID:
        if dataset_status != DATASET_STATUS_CANDIDATE:
            errors.append("valid response must have dataset_status=candidate")

    if recommendation == RECOMMENDATION_REJECT and usable is not False:
        errors.append("reject recommendation requires usable_candidate=false")
    if recommendation == RECOMMENDATION_ACCEPT_CANDIDATE and usable is not True:
        errors.append("accept_candidate requires usable_candidate=true")

    score = evaluation.get("quality_score")
    if not isinstance(score, (int, float)) or score < 0 or score > 1:
        errors.append("quality_score must be number in [0, 1]")

    flags = evaluation.get("safety_flags")
    if not isinstance(flags, list):
        errors.append("safety_flags must be list")

    issues = evaluation.get("contract_issues")
    if not isinstance(issues, list):
        errors.append("contract_issues must be list")

    return errors


def apply_response_evaluation_to_postcall_v1(
    postcall_record: dict[str, Any],
    evaluation: dict[str, Any],
    *,
    precall_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    P1.12 — attach evaluation fields to an existing post-call record (copy returned).

    Sets used_in_ui=false always. Does not mark post-call as final approval.
    """
    if postcall_record.get("contract_version") != DAY_LLM_POSTCALL_RECORD_V1_CONTRACT:
        raise DayModelLlmResponseEvaluationError("postcall_record has invalid contract_version")
    if evaluation.get("contract_version") != DAY_LLM_RESPONSE_EVALUATION_V1_CONTRACT:
        raise DayModelLlmResponseEvaluationError("evaluation has invalid contract_version")

    if postcall_record.get("generation_id") != evaluation.get("generation_id"):
        raise DayModelLlmResponseEvaluationError(
            "postcall generation_id must match evaluation.generation_id"
        )
    if precall_record is not None:
        if precall_record.get("contract_version") != DAY_LLM_PRECALL_RECORD_V1_CONTRACT:
            raise DayModelLlmResponseEvaluationError("precall_record has invalid contract_version")
        if precall_record.get("generation_id") != evaluation.get("generation_id"):
            raise DayModelLlmResponseEvaluationError(
                "precall generation_id must match evaluation.generation_id"
            )

    enriched = {
        **postcall_record,
        "llm_response_evaluation_id": evaluation["llm_response_evaluation_id"],
        "quality_score": evaluation["quality_score"],
        "safety_flags": list(evaluation.get("safety_flags") or []),
        "used_in_ui": False,
    }
    errors = validate_llm_postcall_record_v1(enriched, precall_record=precall_record)
    if errors:
        raise DayModelLlmResponseEvaluationError("; ".join(errors))
    return enriched


def build_llm_postcall_record_with_evaluation_v1(
    precall_record: dict[str, Any],
    *,
    raw_response: dict[str, Any],
    prompt: dict[str, Any],
    provider: str,
    model: str,
    input_tokens: int,
    output_tokens: int,
    cost_estimate: float,
    raw_response_text: str,
    finish_reason: str = "stop",
    postcall_status: str = "completed",
    error: str | None = None,
    llm_response_evaluation_id: str | None = None,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    """
    P1.12 — build post-call record enriched with response evaluation.

    No LLM call performed here; raw_response is caller-supplied (e.g. fixture).
    """
    from todayflow_backend.services.day_model_v1_llm_request_record import (
        build_llm_postcall_record_v1,
    )

    generation_id = precall_record["generation_id"]
    validated, evaluation = evaluate_raw_llm_response_v1(
        raw_response,
        prompt,
        generation_id=generation_id,
        llm_response_evaluation_id=llm_response_evaluation_id,
    )
    postcall = build_llm_postcall_record_v1(
        precall_record,
        provider=provider,
        model=model,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cost_estimate=cost_estimate,
        raw_response=raw_response_text,
        parsed_response=validated,
        finish_reason=finish_reason,
        status=postcall_status,
        error=error,
    )
    enriched = apply_response_evaluation_to_postcall_v1(
        postcall,
        evaluation,
        precall_record=precall_record,
    )
    return validated, evaluation, enriched

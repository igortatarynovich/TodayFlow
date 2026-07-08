"""A1.5 — Personalization usage gate (safe summary → LLM context boundary)."""

from __future__ import annotations

import re
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from todayflow_backend.services.day_model_v1_llm_call_gate import (
    CONTEXT_DEPTH_STANDARD,
    DAY_CONTENT_LLM_GATE_V1_CONTRACT,
    DECISION_CALL_LLM,
    NARRATIVE_SURFACES,
)
from todayflow_backend.services.day_model_v1_llm_context_slice import (
    MAX_SAFE_PERSONALIZATION_FACTS,
)
from todayflow_backend.services.day_model_v1_profile_knowledge_personalization import (
    PROFILE_KNOWLEDGE_PERSONALIZATION_V1_CONTRACT,
    get_safe_personalization_summary_from_layers,
)

PERSONALIZATION_USAGE_GATE_V1_CONTRACT = "personalization_usage_gate_decision_v1"
USAGE_GATE_POLICY_VERSION = "1.0.0"

USAGE_GATE_STATUS_READY = "ready"

USAGE_DECISION_ALLOW = "allow"
USAGE_DECISION_DENY = "deny"

USAGE_RESULT_ALLOWED = "allowed"
USAGE_RESULT_DENIED = "denied"

DENY_LLM_GATE_NOT_CALL = "llm_gate_not_call_llm"
DENY_CONTEXT_DEPTH_NOT_STANDARD = "context_depth_not_standard"
DENY_SURFACE_INELIGIBLE = "surface_not_eligible"
DENY_NO_PERSONALIZATION_SOURCE = "no_personalization_source"
DENY_EMPTY_SUMMARY = "empty_summary"
DENY_INVALID_SUMMARY = "invalid_summary_item"
DENY_INVALID_LLM_GATE = "invalid_llm_gate_decision"

FORBIDDEN_SUMMARY_PATTERN = re.compile(
    r"(personality|trait|diagnos|medical|financial|disorder|depression|anxiety|"
    r"introvert|extrovert|user_is|they_are)",
    re.I,
)

PERSONALIZATION_USAGE_GATE_V1_KEYS = frozenset(
    {
        "contract_version",
        "usage_gate_id",
        "surface",
        "decision",
        "reason",
        "allowed_fact_count",
        "safe_personalization_summary",
        "context_slice_id",
        "personalization_id",
        "llm_gate_context_depth",
        "traceability",
        "status",
        "created_at",
        "profile_update_allowed",
        "memory_update_allowed",
        "ranking_model_update_allowed",
    }
)


class PersonalizationUsageGateError(ValueError):
    """Raised when personalization usage gate inputs are invalid."""


def _utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _sanitize_summary_items(summary: list[str]) -> tuple[list[str], str | None]:
    cleaned: list[str] = []
    for item in summary:
        if not isinstance(item, str):
            return [], DENY_INVALID_SUMMARY
        text = item.strip()
        if not text:
            return [], DENY_INVALID_SUMMARY
        if FORBIDDEN_SUMMARY_PATTERN.search(text):
            return [], DENY_INVALID_SUMMARY
        if text not in cleaned:
            cleaned.append(text[:160])
        if len(cleaned) >= MAX_SAFE_PERSONALIZATION_FACTS:
            break
    return cleaned, None


def resolve_personalization_summary_input(
    *,
    safe_personalization_summary: list[str] | None = None,
    day_context_layers: dict[str, Any] | None = None,
    profile_knowledge_personalization: dict[str, Any] | None = None,
) -> tuple[list[str], dict[str, Any]]:
    """Resolve summary from explicit param, layers, or personalization contract."""
    trace: dict[str, Any] = {"source": "none"}

    if safe_personalization_summary is not None:
        trace["source"] = "explicit"
        return list(safe_personalization_summary), trace

    if isinstance(day_context_layers, dict):
        from_layers = get_safe_personalization_summary_from_layers(day_context_layers)
        if from_layers:
            trace["source"] = "day_context_layers"
            personalization = day_context_layers.get("profile_knowledge_personalization")
            if isinstance(personalization, dict):
                trace["personalization_id"] = personalization.get("personalization_id")
                trace["context_slice_id"] = personalization.get("context_slice_id")
            return from_layers, trace

    if isinstance(profile_knowledge_personalization, dict):
        if (
            profile_knowledge_personalization.get("contract_version")
            == PROFILE_KNOWLEDGE_PERSONALIZATION_V1_CONTRACT
        ):
            summary = profile_knowledge_personalization.get("safe_personalization_summary") or []
            if isinstance(summary, list) and summary:
                trace["source"] = "profile_knowledge_personalization"
                trace["personalization_id"] = profile_knowledge_personalization.get(
                    "personalization_id"
                )
                trace["context_slice_id"] = profile_knowledge_personalization.get(
                    "context_slice_id"
                )
                return list(summary), trace

    return [], trace


def try_decide_personalization_usage_v1(
    *,
    surface: str,
    llm_gate_decision: dict[str, Any],
    safe_personalization_summary: list[str] | None = None,
    day_context_layers: dict[str, Any] | None = None,
    profile_knowledge_personalization: dict[str, Any] | None = None,
    created_at: str | None = None,
    usage_gate_id: str | None = None,
) -> dict[str, Any]:
    """
    Decide whether safe_personalization_summary may enter P1.9 context slice.

    Gate only — no LLM call, no profile/memory reads beyond provided inputs.
    """
    if llm_gate_decision.get("contract_version") != DAY_CONTENT_LLM_GATE_V1_CONTRACT:
        return _denied(
            surface=surface,
            reason=DENY_INVALID_LLM_GATE,
            llm_gate_context_depth=None,
            usage_gate_id=usage_gate_id,
            created_at=created_at,
        )

    if llm_gate_decision.get("decision") != DECISION_CALL_LLM:
        return _denied(
            surface=surface,
            reason=DENY_LLM_GATE_NOT_CALL,
            llm_gate_context_depth=llm_gate_decision.get("allowed_context_depth"),
            usage_gate_id=usage_gate_id,
            created_at=created_at,
        )

    if surface not in NARRATIVE_SURFACES:
        return _denied(
            surface=surface,
            reason=DENY_SURFACE_INELIGIBLE,
            llm_gate_context_depth=llm_gate_decision.get("allowed_context_depth"),
            usage_gate_id=usage_gate_id,
            created_at=created_at,
        )

    context_depth = llm_gate_decision.get("allowed_context_depth")
    if context_depth != CONTEXT_DEPTH_STANDARD:
        return _denied(
            surface=surface,
            reason=DENY_CONTEXT_DEPTH_NOT_STANDARD,
            llm_gate_context_depth=context_depth,
            usage_gate_id=usage_gate_id,
            created_at=created_at,
        )

    if llm_gate_decision.get("surface") != surface:
        return _denied(
            surface=surface,
            reason=DENY_INVALID_LLM_GATE,
            llm_gate_context_depth=context_depth,
            usage_gate_id=usage_gate_id,
            created_at=created_at,
        )

    raw_summary, source_trace = resolve_personalization_summary_input(
        safe_personalization_summary=safe_personalization_summary,
        day_context_layers=day_context_layers,
        profile_knowledge_personalization=profile_knowledge_personalization,
    )

    if not raw_summary and source_trace.get("source") == "none":
        return _denied(
            surface=surface,
            reason=DENY_NO_PERSONALIZATION_SOURCE,
            llm_gate_context_depth=context_depth,
            usage_gate_id=usage_gate_id,
            created_at=created_at,
            traceability=source_trace,
        )

    cleaned, invalid_reason = _sanitize_summary_items(raw_summary)
    if invalid_reason:
        return _denied(
            surface=surface,
            reason=invalid_reason,
            llm_gate_context_depth=context_depth,
            usage_gate_id=usage_gate_id,
            created_at=created_at,
            traceability=source_trace,
        )

    if not cleaned:
        return _denied(
            surface=surface,
            reason=DENY_EMPTY_SUMMARY,
            llm_gate_context_depth=context_depth,
            usage_gate_id=usage_gate_id,
            created_at=created_at,
            traceability=source_trace,
        )

    usage_gate = _allowed(
        surface=surface,
        summary=cleaned,
        llm_gate_context_depth=context_depth,
        usage_gate_id=usage_gate_id,
        created_at=created_at,
        source_trace=source_trace,
    )

    validation_errors = validate_personalization_usage_gate_v1(usage_gate)
    if validation_errors:
        return {
            "result": USAGE_RESULT_DENIED,
            "reasons": validation_errors,
            "usage_gate": None,
        }

    return {
        "result": USAGE_RESULT_ALLOWED,
        "reasons": [],
        "usage_gate": usage_gate,
    }


def resolve_safe_personalization_for_context_slice(
    *,
    surface: str,
    llm_gate_decision: dict[str, Any],
    day_context_layers: dict[str, Any] | None = None,
    safe_personalization_summary: list[str] | None = None,
) -> tuple[list[str] | None, dict[str, Any] | None]:
    """
    A1.6 helper — returns summary for P1.9 when gate allows, else None.

    Explicit safe_personalization_summary bypasses gate (caller responsibility).
    """
    if safe_personalization_summary is not None:
        return safe_personalization_summary, None

    if day_context_layers is None:
        return None, None

    outcome = try_decide_personalization_usage_v1(
        surface=surface,
        llm_gate_decision=llm_gate_decision,
        day_context_layers=day_context_layers,
    )
    usage_gate = outcome.get("usage_gate")
    if outcome.get("result") != USAGE_RESULT_ALLOWED or usage_gate is None:
        return None, usage_gate

    summary = usage_gate.get("safe_personalization_summary")
    if isinstance(summary, list):
        return summary, usage_gate
    return None, usage_gate


def _allowed(
    *,
    surface: str,
    summary: list[str],
    llm_gate_context_depth: str | None,
    usage_gate_id: str | None,
    created_at: str | None,
    source_trace: dict[str, Any],
) -> dict[str, Any]:
    return {
        "contract_version": PERSONALIZATION_USAGE_GATE_V1_CONTRACT,
        "usage_gate_id": usage_gate_id or generate_usage_gate_id(),
        "surface": surface,
        "decision": USAGE_DECISION_ALLOW,
        "reason": "personalization_allowed",
        "allowed_fact_count": len(summary),
        "safe_personalization_summary": summary,
        "context_slice_id": source_trace.get("context_slice_id"),
        "personalization_id": source_trace.get("personalization_id"),
        "llm_gate_context_depth": llm_gate_context_depth,
        "traceability": {
            "source": source_trace.get("source"),
            "summary_source": source_trace.get("source"),
            "usage_gate_policy_version": USAGE_GATE_POLICY_VERSION,
        },
        "status": USAGE_GATE_STATUS_READY,
        "created_at": created_at or _utc_now_iso(),
        "profile_update_allowed": False,
        "memory_update_allowed": False,
        "ranking_model_update_allowed": False,
    }


def _denied(
    *,
    surface: str,
    reason: str,
    llm_gate_context_depth: str | None,
    usage_gate_id: str | None,
    created_at: str | None,
    traceability: dict[str, Any] | None = None,
) -> dict[str, Any]:
    usage_gate = {
        "contract_version": PERSONALIZATION_USAGE_GATE_V1_CONTRACT,
        "usage_gate_id": usage_gate_id or generate_usage_gate_id(),
        "surface": surface,
        "decision": USAGE_DECISION_DENY,
        "reason": reason,
        "allowed_fact_count": 0,
        "safe_personalization_summary": [],
        "context_slice_id": (traceability or {}).get("context_slice_id"),
        "personalization_id": (traceability or {}).get("personalization_id"),
        "llm_gate_context_depth": llm_gate_context_depth,
        "traceability": {
            **(traceability or {}),
            "usage_gate_policy_version": USAGE_GATE_POLICY_VERSION,
        },
        "status": USAGE_GATE_STATUS_READY,
        "created_at": created_at or _utc_now_iso(),
        "profile_update_allowed": False,
        "memory_update_allowed": False,
        "ranking_model_update_allowed": False,
    }
    return {
        "result": USAGE_RESULT_DENIED,
        "reasons": [reason],
        "usage_gate": usage_gate,
    }


def generate_usage_gate_id() -> str:
    return f"pug-{uuid4()}"


def validate_personalization_usage_gate_v1(usage_gate: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    if usage_gate.get("contract_version") != PERSONALIZATION_USAGE_GATE_V1_CONTRACT:
        errors.append("invalid contract_version")

    for key in PERSONALIZATION_USAGE_GATE_V1_KEYS:
        if key not in usage_gate:
            errors.append(f"missing field: {key}")

    if usage_gate.get("decision") not in {USAGE_DECISION_ALLOW, USAGE_DECISION_DENY}:
        errors.append("invalid decision")

    if usage_gate.get("status") != USAGE_GATE_STATUS_READY:
        errors.append("status must be ready")

    for flag in (
        "profile_update_allowed",
        "memory_update_allowed",
        "ranking_model_update_allowed",
    ):
        if usage_gate.get(flag) is not False:
            errors.append(f"{flag} must be false")

    if usage_gate.get("decision") == USAGE_DECISION_ALLOW:
        summary = usage_gate.get("safe_personalization_summary")
        if not isinstance(summary, list) or not summary:
            errors.append("allow requires non-empty safe_personalization_summary")
        elif len(summary) > MAX_SAFE_PERSONALIZATION_FACTS:
            errors.append("safe_personalization_summary exceeds max facts")

    if usage_gate.get("decision") == USAGE_DECISION_DENY:
        if usage_gate.get("allowed_fact_count", 0) != 0:
            errors.append("deny requires allowed_fact_count=0")

    return errors

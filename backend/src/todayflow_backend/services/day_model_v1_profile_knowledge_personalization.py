"""A1.4 — Profile Selector knowledge personalization from context slice."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from todayflow_backend.services.day_model_v1_knowledge_context_selection import (
    CONTEXT_SLICE_STATUS_READY,
    KNOWLEDGE_CONTEXT_SLICE_V1_CONTRACT,
)
from todayflow_backend.services.day_model_v1_llm_context_slice import (
    MAX_SAFE_PERSONALIZATION_FACTS,
)

PROFILE_KNOWLEDGE_PERSONALIZATION_V1_CONTRACT = "profile_knowledge_personalization_v1"
PERSONALIZATION_POLICY_VERSION = "1.0.0"

PERSONALIZATION_STATUS_READY = "ready"

PERSONALIZATION_RESULT_CREATED = "created"
PERSONALIZATION_RESULT_REJECTED = "rejected"
PERSONALIZATION_RESULT_EMPTY = "empty"

PROFILE_KNOWLEDGE_PERSONALIZATION_V1_KEYS = frozenset(
    {
        "contract_version",
        "personalization_id",
        "context_slice_id",
        "safe_personalization_summary",
        "fact_traces",
        "selection_policy_version",
        "traceability",
        "status",
        "created_at",
        "profile_update_allowed",
        "memory_update_allowed",
        "ranking_model_update_allowed",
    }
)

CLAIM_GLOSS_TEMPLATES: dict[str, str] = {
    "prefers_content_key_group": "Responds well to {value} content",
    "responds_to_surface": "Prefers {value} guidance format",
    "responds_to_action_mode": "Works best with {value} actions",
    "responds_to_tempo": "Aligned with {value} day tempo",
    "risk_response_tolerance": "Risk framing tolerance: {value}",
}


class ProfileKnowledgePersonalizationError(ValueError):
    """Raised when profile knowledge personalization inputs are invalid."""


def _utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _split_claim(claim: str) -> tuple[str, str]:
    if ":" not in claim:
        return claim, ""
    prefix, value = claim.split(":", 1)
    return prefix, value


def _humanize_value(value: str) -> str:
    cleaned = value.replace("_", " ").replace(".", " ").strip()
    return " ".join(cleaned.split())


def claim_to_safe_gloss(claim: str, *, knowledge_type: str | None = None) -> str:
    """Deterministic safe gloss for LLM — no traits, no diagnosis."""
    prefix, value = _split_claim(str(claim or ""))
    human_value = _humanize_value(value) or "this pattern"
    template = CLAIM_GLOSS_TEMPLATES.get(prefix)
    if template:
        return template.format(value=human_value)

    if knowledge_type:
        return f"Behavioral preference ({knowledge_type}): {human_value}"
    return f"Behavioral preference: {human_value}"


def build_safe_personalization_summary_from_selected_facts(
    selected_facts: list[dict[str, Any]],
    *,
    max_facts: int = MAX_SAFE_PERSONALIZATION_FACTS,
) -> tuple[list[str], list[dict[str, Any]]]:
    summary: list[str] = []
    traces: list[dict[str, Any]] = []

    for fact in selected_facts:
        if not isinstance(fact, dict):
            continue
        if len(summary) >= max_facts:
            break

        claim = str(fact.get("claim") or "")
        if not claim:
            continue

        gloss = claim_to_safe_gloss(
            claim,
            knowledge_type=str(fact.get("knowledge_type") or "") or None,
        )
        gloss = gloss.strip()[:160]
        if not gloss or gloss in summary:
            continue

        summary.append(gloss)
        traces.append(
            {
                "knowledge_id": fact.get("knowledge_id"),
                "claim": claim,
                "gloss": gloss,
                "freshness_score": fact.get("freshness_score"),
                "final_score": fact.get("final_score"),
            }
        )

    return summary, traces


def try_build_profile_knowledge_personalization_v1(
    knowledge_context_slice: dict[str, Any],
    *,
    created_at: str | None = None,
    personalization_id: str | None = None,
) -> dict[str, Any]:
    """Map Knowledge Context Slice → safe_personalization_summary for Profile Selector / LLM Gate."""
    reasons: list[str] = []

    if knowledge_context_slice.get("contract_version") != KNOWLEDGE_CONTEXT_SLICE_V1_CONTRACT:
        reasons.append("invalid context slice contract_version")

    if knowledge_context_slice.get("status") != CONTEXT_SLICE_STATUS_READY:
        reasons.append("context slice status must be ready")

    if knowledge_context_slice.get("profile_update_allowed") is not False:
        reasons.append("context slice profile_update_allowed must be false")

    if reasons:
        return {
            "result": PERSONALIZATION_RESULT_REJECTED,
            "reasons": reasons,
            "personalization": None,
        }

    selected_facts = knowledge_context_slice.get("selected_facts")
    if not isinstance(selected_facts, list):
        return {
            "result": PERSONALIZATION_RESULT_REJECTED,
            "reasons": ["selected_facts must be a list"],
            "personalization": None,
        }

    summary, traces = build_safe_personalization_summary_from_selected_facts(selected_facts)

    if not summary:
        personalization = _build_personalization_payload(
            knowledge_context_slice,
            summary=[],
            traces=[],
            personalization_id=personalization_id,
            created_at=created_at,
        )
        return {
            "result": PERSONALIZATION_RESULT_EMPTY,
            "reasons": [],
            "personalization": personalization,
        }

    personalization = _build_personalization_payload(
        knowledge_context_slice,
        summary=summary,
        traces=traces,
        personalization_id=personalization_id,
        created_at=created_at,
    )

    validation_errors = validate_profile_knowledge_personalization_v1(personalization)
    if validation_errors:
        return {
            "result": PERSONALIZATION_RESULT_REJECTED,
            "reasons": validation_errors,
            "personalization": None,
        }

    return {
        "result": PERSONALIZATION_RESULT_CREATED,
        "reasons": [],
        "personalization": personalization,
    }


def _build_personalization_payload(
    knowledge_context_slice: dict[str, Any],
    *,
    summary: list[str],
    traces: list[dict[str, Any]],
    personalization_id: str | None,
    created_at: str | None,
) -> dict[str, Any]:
    return {
        "contract_version": PROFILE_KNOWLEDGE_PERSONALIZATION_V1_CONTRACT,
        "personalization_id": personalization_id or generate_personalization_id(),
        "context_slice_id": knowledge_context_slice.get("context_slice_id"),
        "safe_personalization_summary": summary,
        "fact_traces": traces,
        "selection_policy_version": knowledge_context_slice.get("selection_policy_version"),
        "traceability": {
            "context_slice_id": knowledge_context_slice.get("context_slice_id"),
            "knowledge_ids": [t.get("knowledge_id") for t in traces if t.get("knowledge_id")],
            "selected_count": len(knowledge_context_slice.get("selected_facts") or []),
            "included_count": len(summary),
        },
        "status": PERSONALIZATION_STATUS_READY,
        "created_at": created_at or _utc_now_iso(),
        "profile_update_allowed": False,
        "memory_update_allowed": False,
        "ranking_model_update_allowed": False,
    }


def enrich_profile_selector_with_knowledge_v1(
    profile_selector: dict[str, Any],
    knowledge_context_slice: dict[str, Any],
) -> dict[str, Any]:
    """
    Attach safe_personalization_summary to Profile Selector output dict.

    Does not mutate knowledge_context_slice or raw profile sources.
    """
    enriched = dict(profile_selector)
    outcome = try_build_profile_knowledge_personalization_v1(knowledge_context_slice)

    if outcome["result"] == PERSONALIZATION_RESULT_REJECTED:
        enriched["safe_personalization_summary"] = []
        enriched["knowledge_personalization_error"] = outcome.get("reasons")
        return enriched

    personalization = outcome.get("personalization") or {}
    enriched["safe_personalization_summary"] = list(
        personalization.get("safe_personalization_summary") or []
    )
    enriched["knowledge_personalization"] = {
        "personalization_id": personalization.get("personalization_id"),
        "context_slice_id": personalization.get("context_slice_id"),
        "included_count": (personalization.get("traceability") or {}).get("included_count"),
    }
    return enriched


def wire_profile_knowledge_into_day_context_layers(layers: dict[str, Any]) -> dict[str, Any] | None:
    """Enrich layers.profile_selector from layers.knowledge_context_slice if present."""
    context_slice = layers.get("knowledge_context_slice")
    profile_selector = layers.get("profile_selector")
    if not isinstance(context_slice, dict) or not isinstance(profile_selector, dict):
        return None

    outcome = try_build_profile_knowledge_personalization_v1(context_slice)
    layers["profile_selector"] = enrich_profile_selector_with_knowledge_v1(
        profile_selector,
        context_slice,
    )
    layers["profile_knowledge_personalization"] = outcome.get("personalization")
    return outcome.get("personalization")


def get_safe_personalization_summary_from_layers(
    layers: dict[str, Any],
) -> list[str]:
    """Read summary for LLM context slice builder — Profile Selector first, then personalization layer."""
    profile_selector = layers.get("profile_selector")
    if isinstance(profile_selector, dict):
        summary = profile_selector.get("safe_personalization_summary")
        if isinstance(summary, list):
            return list(summary)[:MAX_SAFE_PERSONALIZATION_FACTS]

    personalization = layers.get("profile_knowledge_personalization")
    if isinstance(personalization, dict):
        summary = personalization.get("safe_personalization_summary")
        if isinstance(summary, list):
            return list(summary)[:MAX_SAFE_PERSONALIZATION_FACTS]

    return []


def generate_personalization_id() -> str:
    return f"pkp-{uuid4()}"


def validate_profile_knowledge_personalization_v1(personalization: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    if personalization.get("contract_version") != PROFILE_KNOWLEDGE_PERSONALIZATION_V1_CONTRACT:
        errors.append("invalid contract_version")

    for key in PROFILE_KNOWLEDGE_PERSONALIZATION_V1_KEYS:
        if key not in personalization:
            errors.append(f"missing field: {key}")

    if personalization.get("status") != PERSONALIZATION_STATUS_READY:
        errors.append("status must be ready")

    for flag in (
        "profile_update_allowed",
        "memory_update_allowed",
        "ranking_model_update_allowed",
    ):
        if personalization.get(flag) is not False:
            errors.append(f"{flag} must be false")

    summary = personalization.get("safe_personalization_summary")
    if not isinstance(summary, list):
        errors.append("safe_personalization_summary must be a list")
    elif len(summary) > MAX_SAFE_PERSONALIZATION_FACTS:
        errors.append("safe_personalization_summary exceeds max facts")

    for item in summary or []:
        if not isinstance(item, str) or not item.strip():
            errors.append("safe_personalization_summary items must be non-empty strings")

    return errors

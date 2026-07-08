"""A1.1 — Knowledge context selection (eligibility, freshness, relevance, conflict, cap)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
import time
from typing import Any
from uuid import uuid4

from todayflow_backend.services.day_model_v1_active_knowledge import (
    ACTIVE_KNOWLEDGE_STATUS,
    DAY_ACTIVE_KNOWLEDGE_V1_CONTRACT,
)
from todayflow_backend.services.day_model_v1_active_knowledge_runtime_gate import (
    DECISION_ALLOW,
    try_decide_active_knowledge_runtime_v1,
)
from todayflow_backend.services.day_model_v1_active_knowledge_usage_policy import (
    USAGE_CONTEXT_SELECTION,
    try_build_active_knowledge_usage_policy_v1,
)
from todayflow_backend.services.day_model_v1_knowledge_freshness import (
    compute_freshness_score,
)
from todayflow_backend.services.day_model_v1_knowledge_candidate import validate_claim

KNOWLEDGE_CONTEXT_SLICE_V1_CONTRACT = "knowledge_context_slice_v1"
SELECTION_POLICY_VERSION = "1.0.0"

CONTEXT_SLICE_STATUS_READY = "ready"

SOFT_CAP_DEFAULT = 3
HARD_CAP_DEFAULT = 5
MIN_SELECTION_SCORE = 0.25
EXPANSION_SCORE_THRESHOLD = 0.45

EXCLUSION_INELIGIBLE = "ineligible_runtime_gate"
EXCLUSION_BELOW_MIN_SCORE = "below_min_selection_score"
EXCLUSION_SOFT_CAP = "soft_cap_limit"
EXCLUSION_HARD_CAP = "hard_cap_limit"
EXCLUSION_CONFLICT_LOSER = "conflict_loser"
EXCLUSION_DUPLICATE_PREFIX = "duplicate_claim_prefix"

CONFLICT_RESOLUTION_FRESHER_WINS = "fresher_wins"
CONFLICT_RESOLUTION_CONFIDENCE_WINS = "confidence_wins"

EVOLUTION_STAGE_SEEKER = "seeker"
EVOLUTION_STAGE_OBSERVER = "observer"
EVOLUTION_STAGE_PRACTITIONER = "practitioner"

DAY_CONTEXT_SLICE_V1_KEYS = frozenset(
    {
        "contract_version",
        "context_slice_id",
        "target_surface",
        "selection_policy_version",
        "selected_facts",
        "excluded_facts",
        "exclusion_reasons",
        "freshness_scores",
        "relevance_scores",
        "final_scores",
        "conflict_resolutions",
        "soft_cap",
        "hard_cap",
        "traceability",
        "status",
        "created_at",
        "profile_update_allowed",
        "memory_update_allowed",
        "ranking_model_update_allowed",
    }
)


class KnowledgeContextSelectionError(ValueError):
    """Raised when context selection inputs or payload are invalid."""


@dataclass
class _ScoredKnowledge:
    active_knowledge: dict[str, Any]
    usage_policy: dict[str, Any]
    runtime_decision: dict[str, Any]
    freshness_score: float
    relevance_score: float
    final_score: float
    claim_prefix: str
    claim_value: str


def _utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _split_claim(claim: str) -> tuple[str, str]:
    if ":" not in claim:
        return claim, ""
    prefix, value = claim.split(":", 1)
    return prefix, value


def _claim_prefix(claim: str) -> str:
    return _split_claim(claim)[0]


def compute_relevance_score(
    active_knowledge: dict[str, Any],
    *,
    day_context: dict[str, Any] | None = None,
    goals: list[dict[str, Any]] | None = None,
    practices: list[dict[str, Any]] | None = None,
    evolution_stage: str | None = None,
) -> float:
    """Heuristic relevance 0..1 — no ML."""
    score = 0.5
    claim = str(active_knowledge.get("claim") or "")
    _, claim_value = _split_claim(claim)
    knowledge_type = active_knowledge.get("knowledge_type")

    ctx = day_context or {}
    content_keys = ctx.get("content_keys") or ctx.get("content_key_groups") or []
    if isinstance(content_keys, list) and claim_value:
        normalized = {str(k).lower() for k in content_keys}
        if claim_value.lower() in normalized or any(
            claim_value.lower() in str(k).lower() for k in content_keys
        ):
            score += 0.2

    surface = ctx.get("surface")
    if surface and claim_value and str(surface).lower() == claim_value.lower():
        score += 0.15

    tempo = ctx.get("tempo")
    if knowledge_type == "timing" and tempo and claim_value:
        if str(tempo).lower() == claim_value.lower():
            score += 0.15

    if goals:
        goal_tags = {
            str(g.get("tag") or g.get("domain") or "").lower()
            for g in goals
            if isinstance(g, dict)
        }
        if claim_value.lower() in goal_tags:
            score += 0.1

    if practices:
        for practice in practices:
            if not isinstance(practice, dict):
                continue
            tag = str(practice.get("tag") or practice.get("practice_id") or "").lower()
            if tag and tag in claim.lower():
                score += 0.1
                break
            if practice.get("completion_rate_high") and "action" in claim.lower():
                score += 0.05
                break

    if evolution_stage == EVOLUTION_STAGE_SEEKER:
        if knowledge_type in {"response_style", "behavior"}:
            score += 0.05
    elif evolution_stage in {EVOLUTION_STAGE_OBSERVER, EVOLUTION_STAGE_PRACTITIONER}:
        if knowledge_type in {"content_affinity", "timing"}:
            score += 0.05

    return min(1.0, max(0.0, score))


def compute_final_score(
    active_knowledge: dict[str, Any],
    *,
    freshness_score: float,
    relevance_score: float,
) -> float:
    confidence = float(active_knowledge.get("confidence", 0))
    return confidence * freshness_score * relevance_score


def filter_eligible_knowledge(
    active_knowledge_list: list[dict[str, Any]],
    *,
    target_surface: str,
    now: datetime | None = None,
) -> tuple[list[_ScoredKnowledge], list[dict[str, Any]]]:
    eligible: list[_ScoredKnowledge] = []
    excluded: list[dict[str, Any]] = []

    for active in active_knowledge_list:
        if active.get("contract_version") != DAY_ACTIVE_KNOWLEDGE_V1_CONTRACT:
            excluded.append(
                {
                    "knowledge_id": active.get("knowledge_id"),
                    "reason": EXCLUSION_INELIGIBLE,
                    "detail": "invalid contract_version",
                }
            )
            continue

        if active.get("status") != ACTIVE_KNOWLEDGE_STATUS:
            excluded.append(
                {
                    "knowledge_id": active.get("knowledge_id"),
                    "reason": EXCLUSION_INELIGIBLE,
                    "detail": "not active",
                }
            )
            continue

        claim = active.get("claim")
        if isinstance(claim, str) and validate_claim(claim):
            excluded.append(
                {
                    "knowledge_id": active.get("knowledge_id"),
                    "reason": EXCLUSION_INELIGIBLE,
                    "detail": "invalid claim",
                }
            )
            continue

        policy_outcome = try_build_active_knowledge_usage_policy_v1(active)
        policy = policy_outcome.get("usage_policy")
        if policy is None:
            excluded.append(
                {
                    "knowledge_id": active.get("knowledge_id"),
                    "reason": EXCLUSION_INELIGIBLE,
                    "detail": "usage policy missing",
                }
            )
            continue

        decision = try_decide_active_knowledge_runtime_v1(
            active,
            policy,
            surface=target_surface,
            requested_usage=USAGE_CONTEXT_SELECTION,
            now=now,
        )
        if decision.get("decision") != DECISION_ALLOW:
            excluded.append(
                {
                    "knowledge_id": active.get("knowledge_id"),
                    "reason": EXCLUSION_INELIGIBLE,
                    "detail": decision.get("reason", "deny"),
                }
            )
            continue

        prefix, value = _split_claim(str(claim or ""))
        eligible.append(
            _ScoredKnowledge(
                active_knowledge=active,
                usage_policy=policy,
                runtime_decision=decision,
                freshness_score=0.0,
                relevance_score=0.0,
                final_score=0.0,
                claim_prefix=prefix,
                claim_value=value,
            )
        )

    return eligible, excluded


def resolve_conflicts(
    ranked: list[_ScoredKnowledge],
) -> tuple[list[_ScoredKnowledge], list[dict[str, Any]], list[dict[str, Any]]]:
    """Same claim prefix with different values — keep fresher, then confidence."""
    by_prefix: dict[str, _ScoredKnowledge] = {}
    resolutions: list[dict[str, Any]] = []
    excluded: list[dict[str, Any]] = []

    for item in ranked:
        prefix = item.claim_prefix
        existing = by_prefix.get(prefix)
        if existing is None:
            by_prefix[prefix] = item
            continue

        if existing.claim_value == item.claim_value:
            loser = item if item.final_score <= existing.final_score else existing
            winner = existing if loser is item else item
            by_prefix[prefix] = winner
            excluded.append(
                {
                    "knowledge_id": loser.active_knowledge["knowledge_id"],
                    "claim": loser.active_knowledge.get("claim"),
                    "reason": EXCLUSION_DUPLICATE_PREFIX,
                    "detail": "duplicate claim value",
                }
            )
            continue

        if item.freshness_score > existing.freshness_score:
            winner, loser = item, existing
            resolution = CONFLICT_RESOLUTION_FRESHER_WINS
        elif item.freshness_score < existing.freshness_score:
            winner, loser = existing, item
            resolution = CONFLICT_RESOLUTION_FRESHER_WINS
        elif float(item.active_knowledge.get("confidence", 0)) > float(
            existing.active_knowledge.get("confidence", 0)
        ):
            winner, loser = item, existing
            resolution = CONFLICT_RESOLUTION_CONFIDENCE_WINS
        else:
            winner, loser = existing, item
            resolution = CONFLICT_RESOLUTION_CONFIDENCE_WINS

        by_prefix[prefix] = winner
        resolutions.append(
            {
                "claim_prefix": prefix,
                "winner_knowledge_id": winner.active_knowledge["knowledge_id"],
                "loser_knowledge_id": loser.active_knowledge["knowledge_id"],
                "resolution": resolution,
            }
        )
        excluded.append(
            {
                "knowledge_id": loser.active_knowledge["knowledge_id"],
                "claim": loser.active_knowledge.get("claim"),
                "reason": EXCLUSION_CONFLICT_LOSER,
                "detail": resolution,
            }
        )

    kept = sorted(by_prefix.values(), key=lambda x: x.final_score, reverse=True)
    return kept, excluded, resolutions


def apply_cap(
    ranked: list[_ScoredKnowledge],
    *,
    soft_cap: int,
    hard_cap: int,
) -> tuple[list[_ScoredKnowledge], list[dict[str, Any]]]:
    selected: list[_ScoredKnowledge] = []
    excluded: list[dict[str, Any]] = []

    for item in ranked:
        kid = item.active_knowledge["knowledge_id"]
        claim = item.active_knowledge.get("claim")

        if item.final_score < MIN_SELECTION_SCORE:
            excluded.append(
                {
                    "knowledge_id": kid,
                    "claim": claim,
                    "reason": EXCLUSION_BELOW_MIN_SCORE,
                    "detail": f"score={item.final_score:.3f}",
                }
            )
            continue

        if len(selected) >= hard_cap:
            excluded.append(
                {
                    "knowledge_id": kid,
                    "claim": claim,
                    "reason": EXCLUSION_HARD_CAP,
                    "detail": f"hard_cap={hard_cap}",
                }
            )
            continue

        if len(selected) >= soft_cap and item.final_score < EXPANSION_SCORE_THRESHOLD:
            excluded.append(
                {
                    "knowledge_id": kid,
                    "claim": claim,
                    "reason": EXCLUSION_SOFT_CAP,
                    "detail": f"soft_cap={soft_cap}",
                }
            )
            continue

        selected.append(item)

    return selected, excluded


def select_knowledge_context_v1(
    active_knowledge_list: list[dict[str, Any]],
    *,
    day_context: dict[str, Any] | None = None,
    goals: list[dict[str, Any]] | None = None,
    practices: list[dict[str, Any]] | None = None,
    evolution_stage: str | None = None,
    target_surface: str = "day_guidance_card",
    soft_cap: int = SOFT_CAP_DEFAULT,
    hard_cap: int = HARD_CAP_DEFAULT,
    now: datetime | None = None,
    created_at: str | None = None,
    context_slice_id: str | None = None,
) -> dict[str, Any]:
    """
    A1.1 — select knowledge facts for downstream context consumers.

    Pipeline: eligibility → freshness → relevance → conflict → cap.
    """
    if hard_cap < soft_cap:
        raise KnowledgeContextSelectionError("hard_cap must be >= soft_cap")

    selection_started = time.perf_counter()

    eligible, excluded_eligibility = filter_eligible_knowledge(
        active_knowledge_list,
        target_surface=target_surface,
        now=now,
    )

    scored: list[_ScoredKnowledge] = []
    for item in eligible:
        active = item.active_knowledge
        freshness = compute_freshness_score(active, now=now)
        relevance = compute_relevance_score(
            active,
            day_context=day_context,
            goals=goals,
            practices=practices,
            evolution_stage=evolution_stage,
        )
        final = compute_final_score(
            active,
            freshness_score=freshness,
            relevance_score=relevance,
        )
        item.freshness_score = freshness
        item.relevance_score = relevance
        item.final_score = final
        scored.append(item)

    scored.sort(key=lambda x: x.final_score, reverse=True)
    resolved, excluded_conflict, conflict_resolutions = resolve_conflicts(scored)
    selected, excluded_cap = apply_cap(resolved, soft_cap=soft_cap, hard_cap=hard_cap)

    all_excluded = excluded_eligibility + excluded_conflict + excluded_cap

    knowledge_ids = [s.active_knowledge["knowledge_id"] for s in selected]
    runtime_ids = [s.runtime_decision["runtime_decision_id"] for s in selected]

    freshness_scores = {
        s.active_knowledge["knowledge_id"]: s.freshness_score for s in scored
    }
    relevance_scores = {
        s.active_knowledge["knowledge_id"]: s.relevance_score for s in scored
    }
    final_scores = {s.active_knowledge["knowledge_id"]: s.final_score for s in scored}

    selected_facts = [
        {
            "knowledge_id": s.active_knowledge["knowledge_id"],
            "claim": s.active_knowledge["claim"],
            "knowledge_type": s.active_knowledge["knowledge_type"],
            "confidence": s.active_knowledge["confidence"],
            "freshness_score": s.freshness_score,
            "relevance_score": s.relevance_score,
            "final_score": s.final_score,
            "influence_level": s.runtime_decision.get("allowed_influence_level"),
            "last_confirmed_at": s.active_knowledge.get("last_confirmed_at"),
            "runtime_decision_id": s.runtime_decision.get("runtime_decision_id"),
        }
        for s in selected
    ]

    context_slice = {
        "contract_version": KNOWLEDGE_CONTEXT_SLICE_V1_CONTRACT,
        "context_slice_id": context_slice_id or generate_context_slice_id(),
        "target_surface": target_surface,
        "selection_policy_version": SELECTION_POLICY_VERSION,
        "selected_facts": selected_facts,
        "excluded_facts": all_excluded,
        "exclusion_reasons": sorted({e["reason"] for e in all_excluded}),
        "freshness_scores": freshness_scores,
        "relevance_scores": relevance_scores,
        "final_scores": final_scores,
        "conflict_resolutions": conflict_resolutions,
        "soft_cap": soft_cap,
        "hard_cap": hard_cap,
        "traceability": {
            "knowledge_ids": knowledge_ids,
            "runtime_decision_ids": runtime_ids,
            "pool_count": len(active_knowledge_list),
            "eligible_count": len(eligible),
            "selected_count": len(selected),
            "excluded_count": len(all_excluded),
            "selection_duration_ms": int((time.perf_counter() - selection_started) * 1000),
        },
        "status": CONTEXT_SLICE_STATUS_READY,
        "created_at": created_at or _utc_now_iso(),
        "profile_update_allowed": False,
        "memory_update_allowed": False,
        "ranking_model_update_allowed": False,
    }

    errors = validate_knowledge_context_slice_v1(context_slice)
    if errors:
        raise KnowledgeContextSelectionError("; ".join(errors))

    return context_slice


def generate_context_slice_id() -> str:
    return f"kctx-{uuid4()}"


def validate_knowledge_context_slice_v1(context_slice: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if context_slice.get("contract_version") != KNOWLEDGE_CONTEXT_SLICE_V1_CONTRACT:
        errors.append("invalid contract_version")

    for key in DAY_CONTEXT_SLICE_V1_KEYS:
        if key not in context_slice:
            errors.append(f"missing field: {key}")

    if context_slice.get("status") != CONTEXT_SLICE_STATUS_READY:
        errors.append("status must be ready")

    if context_slice.get("profile_update_allowed") is not False:
        errors.append("profile_update_allowed must be false")
    if context_slice.get("memory_update_allowed") is not False:
        errors.append("memory_update_allowed must be false")
    if context_slice.get("ranking_model_update_allowed") is not False:
        errors.append("ranking_model_update_allowed must be false")

    selected = context_slice.get("selected_facts")
    hard_cap = context_slice.get("hard_cap", HARD_CAP_DEFAULT)
    if isinstance(selected, list) and len(selected) > hard_cap:
        errors.append("selected_facts exceeds hard_cap")

    soft_cap = context_slice.get("soft_cap", SOFT_CAP_DEFAULT)
    if not isinstance(soft_cap, int) or not isinstance(hard_cap, int):
        errors.append("soft_cap and hard_cap must be integers")
    elif soft_cap > hard_cap:
        errors.append("soft_cap must be <= hard_cap")

    return errors

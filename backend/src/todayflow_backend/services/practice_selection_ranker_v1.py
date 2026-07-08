"""C1.8 — Practice Selection Ranker (deterministic score + trace, not recommendation)."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from todayflow_backend.data.practice_context_association_registry_loader import (
    load_practice_context_association_registry_v1,
)
from todayflow_backend.data.practice_definition_registry_loader import (
    load_practice_definition_registry_v1,
)
from todayflow_backend.data.practice_definition_registry_validator import (
    CANONICAL_PRACTICE_CATEGORIES,
)
from todayflow_backend.services.evolution_practice_selector_filter_v1 import (
    ENTITY_TYPE_PRACTICE,
    EVOLUTION_PRACTICE_SELECTOR_FILTER_V1_CONTRACT,
)

PRACTICE_SELECTION_RANKER_V1_VERSION = "1.0.0"

PRACTICE_SELECTION_CONTEXT_SNAPSHOT_V1_CONTRACT = (
    "practice_selection_context_snapshot_v1"
)

PRACTICE_SELECTION_RANK_RESULT_V1_CONTRACT = "practice_selection_rank_result_v1"

SELECTION_DECISION_TRACE_V1_CONTRACT = "selection_decision_trace_v1"

PRACTICE_SELECTION_RANK_OUTPUT_V1_CONTRACT = "practice_selection_rank_output_v1"

EFFORT_TO_COMPLEXITY = {
    "low": "beginner",
    "medium": "intermediate",
    "high": "advanced",
}

REASON_B1_11_CAP = "b1_11_cap"
REASON_NEGATIVE_ASSOCIATION = "negative_association"
REASON_DEFINITION_CONTRAINDICATION = "definition_contraindication"
REASON_SAFETY_CONTRAINDICATION = "safety_contraindication"
REASON_NO_POSITIVE_CONTEXT = "no_positive_context"

BLOCK_LEVELS = frozenset({"advisory", "moderate", "strict"})

FORBIDDEN_TRACE_PATTERN = re.compile(
    r"(user_id|profile_id|email|password|llm_output|prompt|recommendation|"
    r"medical|diagnos|psychological|assigned_practice|final_selection)",
    re.I,
)

PRACTICE_SELECTION_CONTEXT_SNAPSHOT_V1_KEYS = frozenset(
    {
        "contract_version",
        "strategy",
        "tempo",
        "risk",
        "emotional_load",
        "evolution_stage",
        "active_path_themes",
        "rhythm_pattern_types",
        "energy_state",
        "mood_state",
        "goal_categories",
        "knowledge_claim_prefixes",
    }
)

PRACTICE_SELECTION_RANK_RESULT_V1_KEYS = frozenset(
    {
        "contract_version",
        "rank_result_id",
        "ranked_candidates",
        "blocked_candidates",
        "alternatives_considered",
        "context_snapshot_hash",
        "association_registry_version",
        "filter_refs",
        "trace_id",
        "selection_performed",
        "recommendation_created",
        "created_at",
    }
)

RANKED_CANDIDATE_V1_KEYS = frozenset(
    {
        "practice_definition_code",
        "rank_score",
        "matched_associations",
        "supporting_context",
        "penalties",
        "contraindications",
        "final_status",
        "selection_allowed",
        "recommendation_allowed",
    }
)

BLOCKED_CANDIDATE_V1_KEYS = frozenset(
    {
        "practice_definition_code",
        "blocked_by",
        "negative_associations",
        "contraindication_level",
        "reason_code",
    }
)

SELECTION_DECISION_TRACE_V1_KEYS = frozenset(
    {
        "contract_version",
        "trace_id",
        "rank_result_id",
        "selected_because",
        "filtered_because",
        "blocked_because",
        "alternatives_considered",
        "top_candidate_reason",
        "why_not_top_alternatives",
        "context_snapshot_hash",
        "created_at",
    }
)

FORBIDDEN_OUTPUT_FIELDS = frozenset(
    {
        "user_id",
        "profile_id",
        "final_selection",
        "recommendation",
        "assigned_practice",
        "task",
        "prompt",
        "llm_output",
        "profile",
        "memory",
        "progression_signal",
    }
)


class PracticeSelectionRankerError(ValueError):
    """Raised when practice selection ranker inputs are invalid."""


def _utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def generate_rank_result_id() -> str:
    return f"psrr-{uuid4()}"


def generate_selection_trace_id() -> str:
    return f"sdt-{uuid4()}"


def validate_practice_selection_context_snapshot_v1(snapshot: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if snapshot.get("contract_version") != PRACTICE_SELECTION_CONTEXT_SNAPSHOT_V1_CONTRACT:
        errors.append("invalid context snapshot contract_version")

    for key in PRACTICE_SELECTION_CONTEXT_SNAPSHOT_V1_KEYS:
        if key not in snapshot:
            errors.append(f"missing context field: {key}")

    for list_field in (
        "active_path_themes",
        "rhythm_pattern_types",
        "goal_categories",
        "knowledge_claim_prefixes",
    ):
        value = snapshot.get(list_field)
        if not isinstance(value, list):
            errors.append(f"{list_field} must be array")

    forbidden = set(snapshot.keys()) & FORBIDDEN_OUTPUT_FIELDS
    if forbidden:
        errors.append(f"forbidden context fields: {sorted(forbidden)}")

    return errors


def hash_practice_selection_context_snapshot_v1(snapshot: dict[str, Any]) -> str:
    canonical = {
        key: snapshot[key]
        for key in sorted(PRACTICE_SELECTION_CONTEXT_SNAPSHOT_V1_KEYS)
        if key in snapshot and key != "contract_version"
    }
    payload = json.dumps(canonical, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def _active_context_pairs(snapshot: dict[str, Any]) -> set[tuple[str, str]]:
    pairs: set[tuple[str, str]] = set()

    singles = (
        ("daymodel_strategy", "strategy"),
        ("daymodel_tempo", "tempo"),
        ("daymodel_risk", "risk"),
        ("emotional_load", "emotional_load"),
        ("evolution_stage", "evolution_stage"),
        ("energy_state", "energy_state"),
        ("mood_state", "mood_state"),
    )
    for source_type, field in singles:
        value = snapshot.get(field)
        if isinstance(value, str) and value.strip():
            pairs.add((source_type, value.strip()))

    for ref in snapshot.get("active_path_themes") or []:
        if isinstance(ref, str) and ref.strip():
            pairs.add(("path_theme", ref.strip()))

    for ref in snapshot.get("rhythm_pattern_types") or []:
        if isinstance(ref, str) and ref.strip():
            pairs.add(("rhythm_pattern_type", ref.strip()))

    for ref in snapshot.get("goal_categories") or []:
        if isinstance(ref, str) and ref.strip():
            pairs.add(("goal_category", ref.strip()))

    for ref in snapshot.get("knowledge_claim_prefixes") or []:
        if isinstance(ref, str) and ref.strip():
            pairs.add(("knowledge_claim_prefix", ref.strip()))

    return pairs


def _association_matches_context(
    association: dict[str, Any],
    active_pairs: set[tuple[str, str]],
) -> bool:
    source_type = association.get("source_type")
    source_ref = association.get("source_ref")
    if not isinstance(source_type, str) or not isinstance(source_ref, str):
        return False
    return (source_type, source_ref) in active_pairs


def _association_contribution(association: dict[str, Any]) -> float:
    strength = float(association.get("strength") or 0)
    confidence = float(association.get("confidence") or 0)
    return strength * confidence


def _practice_codes_from_b1_11_filter(
    practice_selector_filter: dict[str, Any] | None,
) -> tuple[set[str], dict[str, str]]:
    """Return (allowed practice codes, blocked code -> b1_11 reason)."""
    if practice_selector_filter is None:
        return set(CANONICAL_PRACTICE_CATEGORIES), {}

    if (
        practice_selector_filter.get("contract_version")
        != EVOLUTION_PRACTICE_SELECTOR_FILTER_V1_CONTRACT
    ):
        raise PracticeSelectionRankerError("invalid practice_selector_filter contract")

    allowed: set[str] = set()
    blocked: dict[str, str] = {}

    for candidate in practice_selector_filter.get("filtered_candidates") or []:
        if not isinstance(candidate, dict):
            continue
        if candidate.get("entity_type") != ENTITY_TYPE_PRACTICE:
            continue
        code = candidate.get("code")
        if isinstance(code, str) and code:
            allowed.add(code)

    for candidate in practice_selector_filter.get("blocked_candidates") or []:
        if not isinstance(candidate, dict):
            continue
        if candidate.get("entity_type") not in {ENTITY_TYPE_PRACTICE, None}:
            entity_type = candidate.get("entity_type")
            if entity_type and entity_type != ENTITY_TYPE_PRACTICE:
                continue
        code = candidate.get("code")
        if isinstance(code, str) and code:
            blocked[code] = str(candidate.get("reason") or REASON_B1_11_CAP)

    return allowed, blocked


def _build_practice_candidates_for_b1_11(
    practice_definitions: dict[str, Any],
) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for code in CANONICAL_PRACTICE_CATEGORIES:
        definition = practice_definitions.get(code)
        if not isinstance(definition, dict):
            continue
        effort = str(definition.get("effort_level") or "low")
        duration = definition.get("duration_range") or {}
        max_minutes = int(duration.get("max_minutes") or 15)
        candidates.append(
            {
                "entity_type": ENTITY_TYPE_PRACTICE,
                "code": code,
                "complexity_level": EFFORT_TO_COMPLEXITY.get(effort, "beginner"),
                "path_themes": list(definition.get("compatible_paths") or []),
                "duration_minutes": max_minutes,
                "has_definition": True,
            }
        )
    return candidates


def _collect_safety_contraindications(
    safety_context: dict[str, Any] | None,
) -> set[str]:
    if not safety_context:
        return set()
    active = safety_context.get("active_contraindication_codes") or []
    if not isinstance(active, list):
        return set()
    return {str(item) for item in active if isinstance(item, str) and item.strip()}


def validate_practice_selection_rank_result_v1(result: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    if result.get("contract_version") != PRACTICE_SELECTION_RANK_RESULT_V1_CONTRACT:
        errors.append("invalid rank result contract_version")

    for key in PRACTICE_SELECTION_RANK_RESULT_V1_KEYS:
        if key not in result:
            errors.append(f"missing rank result field: {key}")

    if result.get("selection_performed") is not False:
        errors.append("selection_performed must be false")
    if result.get("recommendation_created") is not False:
        errors.append("recommendation_created must be false")

    forbidden = set(result.keys()) & FORBIDDEN_OUTPUT_FIELDS
    if forbidden:
        errors.append(f"forbidden rank result fields: {sorted(forbidden)}")

    for index, candidate in enumerate(result.get("ranked_candidates") or []):
        prefix = f"ranked_candidates[{index}]"
        if not isinstance(candidate, dict):
            errors.append(f"{prefix}: must be object")
            continue
        if set(candidate.keys()) != RANKED_CANDIDATE_V1_KEYS:
            errors.append(f"{prefix}: unexpected keys")
        if candidate.get("final_status") != "candidate":
            errors.append(f"{prefix}: final_status must be candidate")
        if candidate.get("selection_allowed") is not False:
            errors.append(f"{prefix}: selection_allowed must be false")
        if candidate.get("recommendation_allowed") is not False:
            errors.append(f"{prefix}: recommendation_allowed must be false")

    for index, blocked in enumerate(result.get("blocked_candidates") or []):
        prefix = f"blocked_candidates[{index}]"
        if not isinstance(blocked, dict):
            errors.append(f"{prefix}: must be object")
            continue
        if set(blocked.keys()) != BLOCKED_CANDIDATE_V1_KEYS:
            errors.append(f"{prefix}: unexpected keys")

    return errors


def validate_selection_decision_trace_v1(trace: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    if trace.get("contract_version") != SELECTION_DECISION_TRACE_V1_CONTRACT:
        errors.append("invalid trace contract_version")

    for key in SELECTION_DECISION_TRACE_V1_KEYS:
        if key not in trace:
            errors.append(f"missing trace field: {key}")

    forbidden = set(trace.keys()) & FORBIDDEN_OUTPUT_FIELDS
    if forbidden:
        errors.append(f"forbidden trace fields: {sorted(forbidden)}")

    for field, value in trace.items():
        if isinstance(value, str) and FORBIDDEN_TRACE_PATTERN.search(value):
            errors.append(f"trace field {field} contains forbidden language")

    return errors


def _score_practice(
    practice_code: str,
    *,
    associations: list[dict[str, Any]],
    active_pairs: set[tuple[str, str]],
    definition: dict[str, Any],
    safety_contras: set[str],
) -> tuple[float, dict[str, Any], dict[str, Any] | None]:
    matched_positive: list[dict[str, Any]] = []
    matched_negative: list[dict[str, Any]] = []
    supporting_context: list[str] = []
    penalties: list[dict[str, Any]] = []
    score = 0.0

    definition_contras = set(definition.get("contraindications") or [])
    active_definition_contras = sorted(definition_contras & safety_contras)
    if active_definition_contras:
        return (
            0.0,
            {},
            {
                "practice_definition_code": practice_code,
                "blocked_by": [REASON_SAFETY_CONTRAINDICATION],
                "negative_associations": [],
                "contraindication_level": "strict",
                "reason_code": REASON_DEFINITION_CONTRAINDICATION,
            },
        )

    for association in associations:
        if association.get("practice_definition_code") != practice_code:
            continue
        if not _association_matches_context(association, active_pairs):
            continue

        contrib = _association_contribution(association)
        ref_label = f"{association.get('source_type')}:{association.get('source_ref')}"
        entry = {
            "association_id": association.get("association_id"),
            "source_type": association.get("source_type"),
            "source_ref": association.get("source_ref"),
            "direction": association.get("direction"),
            "contribution": round(contrib, 4),
        }

        direction = association.get("direction")
        if direction == "negative":
            matched_negative.append(entry)
            level = str(association.get("contraindication_level") or "moderate")
            if level in {"moderate", "strict"}:
                return (
                    0.0,
                    {},
                    {
                        "practice_definition_code": practice_code,
                        "blocked_by": [REASON_NEGATIVE_ASSOCIATION],
                        "negative_associations": matched_negative,
                        "contraindication_level": level,
                        "reason_code": REASON_NEGATIVE_ASSOCIATION,
                    },
                )
            penalty = contrib * 0.75
            score -= penalty
            penalties.append(
                {
                    "reason": REASON_NEGATIVE_ASSOCIATION,
                    "association_id": association.get("association_id"),
                    "penalty": round(penalty, 4),
                }
            )
        else:
            matched_positive.append(entry)
            score += contrib
            supporting_context.append(ref_label)

    ranked_detail = {
        "practice_definition_code": practice_code,
        "rank_score": round(max(score, 0.0), 4),
        "matched_associations": matched_positive,
        "supporting_context": supporting_context,
        "penalties": penalties,
        "contraindications": active_definition_contras,
        "final_status": "candidate",
        "selection_allowed": False,
        "recommendation_allowed": False,
    }
    return max(score, 0.0), ranked_detail, None


def _build_trace(
    *,
    trace_id: str,
    rank_result_id: str,
    context_hash: str,
    ranked: list[dict[str, Any]],
    blocked: list[dict[str, Any]],
    created_at: str,
) -> dict[str, Any]:
    top = ranked[0] if ranked else None
    runner_up = ranked[1] if len(ranked) > 1 else None

    selected_because: list[str] = []
    if top:
        for assoc in top.get("matched_associations") or []:
            selected_because.append(
                f"{assoc.get('source_type')}:{assoc.get('source_ref')} "
                f"(+{assoc.get('contribution')})"
            )
        if not selected_because:
            selected_because.append(REASON_NO_POSITIVE_CONTEXT)

    filtered_because: list[dict[str, Any]] = []
    for candidate in ranked:
        if candidate.get("penalties"):
            filtered_because.append(
                {
                    "practice_definition_code": candidate.get("practice_definition_code"),
                    "penalties": candidate.get("penalties"),
                }
            )

    blocked_because = [
        {
            "practice_definition_code": item.get("practice_definition_code"),
            "reason_code": item.get("reason_code"),
            "blocked_by": item.get("blocked_by"),
        }
        for item in blocked
    ]

    alternatives = [c.get("practice_definition_code") for c in ranked] + [
        b.get("practice_definition_code") for b in blocked
    ]

    top_reason = None
    why_not: list[dict[str, Any]] = []
    if top:
        top_code = top.get("practice_definition_code")
        top_reason = (
            f"{top_code} ranked first with score {top.get('rank_score')} "
            f"via {len(top.get('matched_associations') or [])} positive association(s)"
        )
        if runner_up:
            runner_code = runner_up.get("practice_definition_code")
            reasons: list[str] = []
            score_gap = float(top.get("rank_score") or 0) - float(
                runner_up.get("rank_score") or 0
            )
            if score_gap > 0:
                reasons.append(f"score_gap={round(score_gap, 4)}")
            top_refs = {
                f"{a.get('source_type')}:{a.get('source_ref')}"
                for a in (top.get("matched_associations") or [])
            }
            runner_refs = {
                f"{a.get('source_type')}:{a.get('source_ref')}"
                for a in (runner_up.get("matched_associations") or [])
            }
            missing = sorted(top_refs - runner_refs)
            if missing:
                reasons.append(f"missing_context_matches={missing}")
            why_not.append(
                {
                    "practice_definition_code": runner_code,
                    "reasons": reasons or [REASON_NO_POSITIVE_CONTEXT],
                }
            )

    return {
        "contract_version": SELECTION_DECISION_TRACE_V1_CONTRACT,
        "trace_id": trace_id,
        "rank_result_id": rank_result_id,
        "selected_because": selected_because,
        "filtered_because": filtered_because,
        "blocked_because": blocked_because,
        "alternatives_considered": alternatives,
        "top_candidate_reason": top_reason,
        "why_not_top_alternatives": why_not,
        "context_snapshot_hash": context_hash,
        "created_at": created_at,
    }


def rank_practice_selection_v1(
    context_snapshot: dict[str, Any],
    *,
    practice_selector_filter: dict[str, Any] | None = None,
    safety_context: dict[str, Any] | None = None,
    associations_registry: dict[str, Any] | None = None,
    practice_definitions_registry: dict[str, Any] | None = None,
    created_at: str | None = None,
) -> dict[str, Any]:
    """
    Deterministic practice ranker: context + C1.7 associations + optional B1.11 caps.

    Returns practice_selection_rank_output_v1 with rank_result and selection_trace.
    Does not select, recommend, assign, or mutate profile/memory.
    """
    snapshot_errors = validate_practice_selection_context_snapshot_v1(context_snapshot)
    if snapshot_errors:
        raise PracticeSelectionRankerError("; ".join(snapshot_errors))

    assoc_registry = associations_registry or load_practice_context_association_registry_v1()
    defs_registry = practice_definitions_registry or load_practice_definition_registry_v1()
    practice_definitions = defs_registry.get("practice_definitions") or {}

    associations = list((assoc_registry.get("practice_context_associations") or {}).values())
    active_pairs = _active_context_pairs(context_snapshot)
    context_hash = hash_practice_selection_context_snapshot_v1(context_snapshot)
    timestamp = created_at or _utc_now_iso()

    b1_11_allowed, b1_11_blocked = _practice_codes_from_b1_11_filter(practice_selector_filter)
    safety_contras = _collect_safety_contraindications(safety_context)

    ranked_candidates: list[dict[str, Any]] = []
    blocked_candidates: list[dict[str, Any]] = []

    for practice_code in CANONICAL_PRACTICE_CATEGORIES:
        definition = practice_definitions.get(practice_code)
        if not isinstance(definition, dict):
            blocked_candidates.append(
                {
                    "practice_definition_code": practice_code,
                    "blocked_by": [REASON_B1_11_CAP],
                    "negative_associations": [],
                    "contraindication_level": "strict",
                    "reason_code": REASON_B1_11_CAP,
                }
            )
            continue

        if practice_code in b1_11_blocked:
            blocked_candidates.append(
                {
                    "practice_definition_code": practice_code,
                    "blocked_by": [REASON_B1_11_CAP],
                    "negative_associations": [],
                    "contraindication_level": "moderate",
                    "reason_code": REASON_B1_11_CAP,
                }
            )
            continue

        if practice_selector_filter is not None and practice_code not in b1_11_allowed:
            blocked_candidates.append(
                {
                    "practice_definition_code": practice_code,
                    "blocked_by": [REASON_B1_11_CAP],
                    "negative_associations": [],
                    "contraindication_level": "moderate",
                    "reason_code": REASON_B1_11_CAP,
                }
            )
            continue

        _score, ranked_detail, blocked_detail = _score_practice(
            practice_code,
            associations=associations,
            active_pairs=active_pairs,
            definition=definition,
            safety_contras=safety_contras,
        )
        if blocked_detail:
            blocked_candidates.append(blocked_detail)
        else:
            ranked_candidates.append(ranked_detail)

    ranked_candidates.sort(
        key=lambda item: (
            -float(item.get("rank_score") or 0),
            str(item.get("practice_definition_code")),
        )
    )

    trace_id = generate_selection_trace_id()
    rank_result_id = generate_rank_result_id()

    filter_refs: list[str] = []
    if practice_selector_filter is not None:
        filter_refs.append(str(practice_selector_filter.get("filter_id") or ""))

    rank_result = {
        "contract_version": PRACTICE_SELECTION_RANK_RESULT_V1_CONTRACT,
        "rank_result_id": rank_result_id,
        "ranked_candidates": ranked_candidates,
        "blocked_candidates": blocked_candidates,
        "alternatives_considered": [c["practice_definition_code"] for c in ranked_candidates]
        + [b["practice_definition_code"] for b in blocked_candidates],
        "context_snapshot_hash": context_hash,
        "association_registry_version": str(assoc_registry.get("version") or ""),
        "filter_refs": [ref for ref in filter_refs if ref],
        "trace_id": trace_id,
        "selection_performed": False,
        "recommendation_created": False,
        "created_at": timestamp,
    }

    trace = _build_trace(
        trace_id=trace_id,
        rank_result_id=rank_result_id,
        context_hash=context_hash,
        ranked=ranked_candidates,
        blocked=blocked_candidates,
        created_at=timestamp,
    )

    rank_errors = validate_practice_selection_rank_result_v1(rank_result)
    trace_errors = validate_selection_decision_trace_v1(trace)
    if rank_errors or trace_errors:
        raise PracticeSelectionRankerError("; ".join((rank_errors + trace_errors)[:8]))

    return {
        "contract_version": PRACTICE_SELECTION_RANK_OUTPUT_V1_CONTRACT,
        "rank_result": rank_result,
        "selection_trace": trace,
    }


def build_practice_selector_filter_from_context_v1(
    context_snapshot: dict[str, Any],
    *,
    evolution_slice: dict[str, Any] | None = None,
    practice_definitions_registry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Helper: build B1.11 filter for all C1.1 practice candidates from context paths."""
    from todayflow_backend.services.evolution_practice_selector_filter_v1 import (
        build_evolution_practice_selector_filter_v1,
    )

    defs_registry = practice_definitions_registry or load_practice_definition_registry_v1()
    practice_definitions = defs_registry.get("practice_definitions") or {}
    candidates = _build_practice_candidates_for_b1_11(practice_definitions)
    path_context = {
        "active_path_themes": list(context_snapshot.get("active_path_themes") or []),
    }
    return build_evolution_practice_selector_filter_v1(
        candidates,
        evolution_slice=evolution_slice,
        path_context=path_context,
    )

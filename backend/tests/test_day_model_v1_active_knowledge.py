"""P1.20 — Active knowledge confirmation gate tests."""

from __future__ import annotations

import copy

from todayflow_backend.services.day_model_v1_active_knowledge import (
    ACTIVATION_RESULT_ACTIVATED,
    ACTIVATION_RESULT_NOT_READY,
    ACTIVATION_RESULT_REJECTED,
    ACTIVATION_RESULT_REQUIRES_REVIEW,
    DAY_ACTIVE_KNOWLEDGE_V1_CONTRACT,
    DAY_ACTIVE_KNOWLEDGE_V1_KEYS,
    try_activate_knowledge_from_candidate_v1,
    validate_day_active_knowledge_v1,
)
from todayflow_backend.services.day_model_v1_knowledge_candidate import (
    DAY_KNOWLEDGE_CANDIDATE_V1_CONTRACT,
    KNOWLEDGE_TYPE_RESPONSE_STYLE,
)


def _strong_candidate(**overrides):
    base = {
        "contract_version": DAY_KNOWLEDGE_CANDIDATE_V1_CONTRACT,
        "knowledge_candidate_id": "kcand-strong-001",
        "source_pattern_id": "pat-strong-001",
        "knowledge_type": KNOWLEDGE_TYPE_RESPONSE_STYLE,
        "claim": "responds_to_surface:today_hero",
        "claim_strength": 0.8,
        "confidence": 0.8,
        "evidence_pattern_id": "pat-strong-001",
        "evidence_signal_ids": [f"lsig-{i}" for i in range(7)],
        "evidence_count": 7,
        "evidence_window_days": 21,
        "status": "candidate",
        "created_at": "2026-05-31T12:00:00Z",
        "requires_review": True,
        "profile_update_allowed": False,
        "memory_update_allowed": False,
        "ranking_update_allowed": False,
    }
    base.update(overrides)
    return base


def test_strong_candidate_activates_knowledge():
    candidate = _strong_candidate()
    outcome = try_activate_knowledge_from_candidate_v1(candidate, review_approved=True)
    assert outcome["result"] == ACTIVATION_RESULT_ACTIVATED
    active = outcome["active_knowledge"]
    assert active is not None
    assert active["status"] == "active"
    assert active["source_knowledge_candidate_id"] == candidate["knowledge_candidate_id"]
    assert active["claim"] == candidate["claim"]


def test_low_confidence_not_ready():
    candidate = _strong_candidate(confidence=0.7)
    outcome = try_activate_knowledge_from_candidate_v1(candidate, review_approved=True)
    assert outcome["result"] == ACTIVATION_RESULT_NOT_READY
    assert "confidence" in " ".join(outcome["reasons"])


def test_short_window_not_ready():
    candidate = _strong_candidate(evidence_window_days=14)
    outcome = try_activate_knowledge_from_candidate_v1(candidate, review_approved=True)
    assert outcome["result"] == ACTIVATION_RESULT_NOT_READY
    assert "evidence_window_days" in " ".join(outcome["reasons"])


def test_low_evidence_count_not_ready():
    candidate = _strong_candidate(
        evidence_count=5,
        evidence_signal_ids=[f"lsig-{i}" for i in range(5)],
    )
    outcome = try_activate_knowledge_from_candidate_v1(candidate, review_approved=True)
    assert outcome["result"] == ACTIVATION_RESULT_NOT_READY
    assert "evidence_count" in " ".join(outcome["reasons"])


def test_invalid_claim_rejected():
    candidate = _strong_candidate(claim="invalid claim prose")
    outcome = try_activate_knowledge_from_candidate_v1(candidate, review_approved=True)
    assert outcome["result"] == ACTIVATION_RESULT_REJECTED


def test_sensitive_claim_rejected():
    candidate = _strong_candidate(claim="personality_trait:disciplined")
    outcome = try_activate_knowledge_from_candidate_v1(candidate, review_approved=True)
    assert outcome["result"] == ACTIVATION_RESULT_REJECTED


def test_prose_claim_rejected():
    candidate = _strong_candidate(claim="User prefers hero surface")
    outcome = try_activate_knowledge_from_candidate_v1(candidate, review_approved=True)
    assert outcome["result"] == ACTIVATION_RESULT_REJECTED


def test_mutation_flags_always_false():
    outcome = try_activate_knowledge_from_candidate_v1(
        _strong_candidate(), review_approved=True
    )
    active = outcome["active_knowledge"]
    assert active is not None
    assert active["memory_update_allowed"] is False
    assert active["profile_update_allowed"] is False
    assert active["ranking_update_allowed"] is False


def test_evidence_trace_preserved():
    candidate = _strong_candidate()
    outcome = try_activate_knowledge_from_candidate_v1(candidate, review_approved=True)
    active = outcome["active_knowledge"]
    assert active is not None
    assert active["evidence_signal_ids"] == candidate["evidence_signal_ids"]
    assert active["evidence_count"] == candidate["evidence_count"]
    assert active["evidence_window_days"] == candidate["evidence_window_days"]
    assert active["source_pattern_id"] == candidate["source_pattern_id"]
    assert active["last_confirmed_at"] == active["created_at"]
    assert validate_day_active_knowledge_v1(active, knowledge_candidate=candidate) == []


def test_output_shape_stable():
    candidate = _strong_candidate()
    outcome = try_activate_knowledge_from_candidate_v1(candidate, review_approved=True)
    active = outcome["active_knowledge"]
    assert active is not None
    assert active["contract_version"] == DAY_ACTIVE_KNOWLEDGE_V1_CONTRACT
    assert set(active.keys()) == set(DAY_ACTIVE_KNOWLEDGE_V1_KEYS)
    forbidden = {"profile_update", "memory_write", "recommendation", "ukm_atom_id"}
    assert forbidden.isdisjoint(active.keys())


def test_requires_review_without_approval():
    candidate = _strong_candidate()
    outcome = try_activate_knowledge_from_candidate_v1(candidate, review_approved=False)
    assert outcome["result"] == ACTIVATION_RESULT_REQUIRES_REVIEW
    assert outcome["active_knowledge"] is None


def test_non_candidate_status_rejected():
    candidate = copy.deepcopy(_strong_candidate())
    candidate["status"] = "active"
    outcome = try_activate_knowledge_from_candidate_v1(candidate, review_approved=True)
    assert outcome["result"] == ACTIVATION_RESULT_REJECTED

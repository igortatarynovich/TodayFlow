"""P1.19 — Knowledge candidate from confirmed pattern tests."""

from __future__ import annotations

import copy

from todayflow_backend.services.day_model_v1_confirmed_pattern import (
    DAY_CONFIRMED_PATTERN_V1_CONTRACT,
    try_confirm_pattern_from_candidate_v1,
)
from todayflow_backend.services.day_model_v1_knowledge_candidate import (
    DAY_KNOWLEDGE_CANDIDATE_V1_CONTRACT,
    DAY_KNOWLEDGE_CANDIDATE_V1_KEYS,
    KNOWLEDGE_CANDIDATE_RESULT_CREATED,
    KNOWLEDGE_CANDIDATE_RESULT_REJECTED,
    KNOWLEDGE_TYPE_RESPONSE_STYLE,
    build_claim_from_pattern,
    try_build_knowledge_candidate_from_pattern_v1,
    validate_claim,
    validate_day_knowledge_candidate_v1,
)
from todayflow_backend.services.day_model_v1_pattern_candidate import (
    CANDIDATE_TYPE_SURFACE_PREFERENCE,
    try_aggregate_pattern_candidate_v1,
)
from todayflow_backend.services.day_model_v1_surface_learning_signal import (
    DAY_SURFACE_LEARNING_SIGNAL_V1_CONTRACT,
    SIGNAL_DIRECTION_POSITIVE,
)

AGG_KEY = "today_hero"
LONG_WINDOW_DATES = [
    "2026-05-01T12:00:00Z",
    "2026-05-05T12:00:00Z",
    "2026-05-10T12:00:00Z",
    "2026-05-15T12:00:00Z",
    "2026-05-16T12:00:00Z",
]


def _signal(signal_id: str, *, created_at: str):
    return {
        "contract_version": DAY_SURFACE_LEARNING_SIGNAL_V1_CONTRACT,
        "learning_signal_id": signal_id,
        "reaction_id": f"react-{signal_id}",
        "exposure_id": f"exp-{signal_id}",
        "audit_id": f"audit-{signal_id}",
        "surface": "today_hero",
        "signal_type": "useful",
        "signal_strength": 0.7,
        "signal_direction": SIGNAL_DIRECTION_POSITIVE,
        "evidence_type": "behavioral",
        "confidence": "medium-high",
        "source_keys": ["day.guidance.headline"],
        "selected_source": "deterministic",
        "used_llm": False,
        "dataset_candidate_effect": "keep_candidate",
        "created_at": created_at,
        "memory_update_allowed": False,
        "ranking_update_allowed": False,
    }


def _confirmed_pattern():
    signals = [
        _signal(f"lsig-{i}", created_at=created_at)
        for i, created_at in enumerate(LONG_WINDOW_DATES)
    ]
    candidate = try_aggregate_pattern_candidate_v1(
        signals,
        candidate_type=CANDIDATE_TYPE_SURFACE_PREFERENCE,
        aggregation_key=AGG_KEY,
    )
    assert candidate is not None
    outcome = try_confirm_pattern_from_candidate_v1(candidate)
    assert outcome["result"] == "confirmed"
    return outcome["pattern"]


def test_confirmed_pattern_creates_knowledge_candidate():
    pattern = _confirmed_pattern()
    outcome = try_build_knowledge_candidate_from_pattern_v1(pattern)
    assert outcome["result"] == KNOWLEDGE_CANDIDATE_RESULT_CREATED
    kc = outcome["knowledge_candidate"]
    assert kc is not None
    assert kc["status"] == "candidate"
    assert kc["source_pattern_id"] == pattern["pattern_id"]
    assert kc["knowledge_type"] == KNOWLEDGE_TYPE_RESPONSE_STYLE
    assert kc["claim"] == "responds_to_surface:today_hero"


def test_non_confirmed_pattern_rejected():
    pattern = copy.deepcopy(_confirmed_pattern())
    pattern["status"] = "pending"
    outcome = try_build_knowledge_candidate_from_pattern_v1(pattern)
    assert outcome["result"] == KNOWLEDGE_CANDIDATE_RESULT_REJECTED
    assert outcome["knowledge_candidate"] is None


def test_unsupported_pattern_type_rejected():
    pattern = copy.deepcopy(_confirmed_pattern())
    pattern["pattern_type"] = "personality_trait"
    outcome = try_build_knowledge_candidate_from_pattern_v1(pattern)
    assert outcome["result"] == KNOWLEDGE_CANDIDATE_RESULT_REJECTED


def test_low_confidence_rejected():
    pattern = copy.deepcopy(_confirmed_pattern())
    pattern["confidence"] = 0.4
    outcome = try_build_knowledge_candidate_from_pattern_v1(pattern)
    assert outcome["result"] == KNOWLEDGE_CANDIDATE_RESULT_REJECTED
    assert "confidence" in " ".join(outcome["reasons"])


def test_claim_machine_readable():
    pattern = _confirmed_pattern()
    claim = build_claim_from_pattern(pattern)
    assert claim is not None
    assert validate_claim(claim) == []
    assert claim.startswith("responds_to_surface:")


def test_prose_claim_invalid():
    assert "prose" in " ".join(validate_claim("User prefers structured guidance cards"))
    assert validate_claim("responds_to_surface:today hero") != []


def test_sensitive_claim_invalid():
    assert validate_claim("personality_trait:disciplined") != []
    assert validate_claim("responds_to_surface:anxiety_profile") != []


def test_no_mutation_flags():
    outcome = try_build_knowledge_candidate_from_pattern_v1(_confirmed_pattern())
    kc = outcome["knowledge_candidate"]
    assert kc is not None
    assert kc["memory_update_allowed"] is False
    assert kc["profile_update_allowed"] is False
    assert kc["ranking_update_allowed"] is False
    assert kc["requires_review"] is True


def test_evidence_trace_preserved():
    pattern = _confirmed_pattern()
    outcome = try_build_knowledge_candidate_from_pattern_v1(pattern)
    kc = outcome["knowledge_candidate"]
    assert kc is not None
    assert kc["evidence_pattern_id"] == pattern["pattern_id"]
    assert kc["evidence_signal_ids"] == pattern["evidence_signal_ids"]
    assert kc["evidence_count"] == pattern["evidence_count"]
    assert kc["evidence_window_days"] == pattern["evidence_window_days"]
    assert validate_day_knowledge_candidate_v1(kc, confirmed_pattern=pattern) == []


def test_output_shape_stable():
    outcome = try_build_knowledge_candidate_from_pattern_v1(_confirmed_pattern())
    kc = outcome["knowledge_candidate"]
    assert kc is not None
    assert kc["contract_version"] == DAY_KNOWLEDGE_CANDIDATE_V1_CONTRACT
    assert set(kc.keys()) == set(DAY_KNOWLEDGE_CANDIDATE_V1_KEYS)
    forbidden = {"knowledge_atom", "active_knowledge", "profile_update", "recommendation"}
    assert forbidden.isdisjoint(kc.keys())

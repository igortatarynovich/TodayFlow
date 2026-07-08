"""E1.6 — Calendar rhythm bridge tests."""

from __future__ import annotations

import copy
from datetime import UTC, datetime

from todayflow_backend.services.calendar_rhythm_bridge_v1 import (
    BRIDGE_RESULT_BRIDGED,
    BRIDGE_RESULT_NOT_READY,
    BRIDGE_RESULT_REJECTED,
    CALENDAR_EVOLUTION_PROGRESSION_CONTEXT_V1_CONTRACT,
    CALENDAR_EVOLUTION_PROGRESSION_CONTEXT_V1_KEYS,
    CALENDAR_RHYTHM_KNOWLEDGE_CANDIDATE_V1_CONTRACT,
    CALENDAR_RHYTHM_KNOWLEDGE_CANDIDATE_V1_KEYS,
    try_bridge_calendar_rhythm_pattern_v1,
    validate_calendar_evolution_progression_context_v1,
    validate_calendar_rhythm_knowledge_candidate_v1,
)
from todayflow_backend.services.calendar_rhythm_pattern_v1 import (
    try_confirm_rhythm_pattern_from_candidate_v1,
)
from todayflow_backend.services.calendar_rhythm_pattern_candidate_v1 import (
    CALENDAR_RHYTHM_PATTERN_CANDIDATE_V1_CONTRACT,
    CALENDAR_RHYTHM_PATTERN_CANDIDATE_V1_VERSION,
    CANDIDATE_TYPE_ENERGY_WEEKDAY,
)


def _strong_candidate(**overrides):
    base = {
        "contract_version": CALENDAR_RHYTHM_PATTERN_CANDIDATE_V1_CONTRACT,
        "candidate_id": "crpc-test-strong",
        "user_id": "user-1",
        "candidate_type": CANDIDATE_TYPE_ENERGY_WEEKDAY,
        "source_month_map_ids": ["cmm-test-1"],
        "source_day_record_ids": [f"cdr-{index}" for index in range(6)],
        "evidence_window_days": 28,
        "evidence_count": 6,
        "supporting_dates": [
            "2026-06-03",
            "2026-06-10",
            "2026-06-17",
            "2026-06-24",
            "2026-07-01",
            "2026-07-08",
        ],
        "dominant_value": "tuesday",
        "baseline_value": 5.0,
        "strength": 0.5,
        "confidence": 0.65,
        "status": "candidate",
        "created_at": "2026-06-01T12:00:00Z",
        "confirmation_allowed": False,
        "recommendation_allowed": False,
        "version": CALENDAR_RHYTHM_PATTERN_CANDIDATE_V1_VERSION,
    }
    base.update(overrides)
    return base


def _confirmed_pattern(**overrides):
    outcome = try_confirm_rhythm_pattern_from_candidate_v1(_strong_candidate())
    assert outcome["pattern"] is not None
    pattern = outcome["pattern"]
    pattern.update(overrides)
    return pattern


def test_strong_pattern_bridges() -> None:
    outcome = try_bridge_calendar_rhythm_pattern_v1(_confirmed_pattern())

    assert outcome["result"] == BRIDGE_RESULT_BRIDGED
    assert outcome["reasons"] == []
    assert outcome["knowledge_candidate"] is not None
    assert outcome["progression_context"] is not None
    assert outcome["knowledge_candidate"]["claim"] == "rhythm_energy_weekday:tuesday"
    assert outcome["progression_context"]["context_signal_code"] == "rhythm_energy_weekday"
    assert outcome["progression_context"]["evolution_bucket"] == "rhythm"


def test_expired_pattern_not_ready() -> None:
    outcome = try_bridge_calendar_rhythm_pattern_v1(
        _confirmed_pattern(expires_at="2020-01-01T00:00:00Z"),
        now=datetime(2026, 6, 1, tzinfo=UTC),
    )

    assert outcome["result"] == BRIDGE_RESULT_NOT_READY
    assert outcome["knowledge_candidate"] is None
    assert any("expired" in reason for reason in outcome["reasons"])


def test_unconfirmed_pattern_rejected() -> None:
    pattern = _confirmed_pattern(status="candidate")
    outcome = try_bridge_calendar_rhythm_pattern_v1(pattern)

    assert outcome["result"] == BRIDGE_RESULT_REJECTED
    assert outcome["knowledge_candidate"] is None


def test_invalid_pattern_rejected() -> None:
    pattern = _confirmed_pattern(contract_version="wrong")
    outcome = try_bridge_calendar_rhythm_pattern_v1(pattern)

    assert outcome["result"] == BRIDGE_RESULT_REJECTED
    assert outcome["reasons"]


def test_forbidden_fields_rejected_on_validate() -> None:
    outcome = try_bridge_calendar_rhythm_pattern_v1(_confirmed_pattern())
    knowledge = outcome["knowledge_candidate"]
    context = outcome["progression_context"]
    assert knowledge is not None and context is not None

    bad_knowledge = copy.deepcopy(knowledge)
    bad_knowledge["insight"] = "rest on tuesday"
    assert validate_calendar_rhythm_knowledge_candidate_v1(bad_knowledge)

    bad_context = copy.deepcopy(context)
    bad_context["recommendation"] = "take a break"
    assert validate_calendar_evolution_progression_context_v1(bad_context)


def test_bridge_preserves_evidence_refs() -> None:
    pattern = _confirmed_pattern()
    outcome = try_bridge_calendar_rhythm_pattern_v1(pattern)
    knowledge = outcome["knowledge_candidate"]
    context = outcome["progression_context"]
    assert knowledge is not None and context is not None

    assert knowledge["source_day_record_ids"] == pattern["source_day_record_ids"]
    assert knowledge["source_month_map_ids"] == pattern["source_month_map_ids"]
    assert knowledge["supporting_dates"] == pattern["supporting_dates"]
    assert context["source_day_record_ids"] == pattern["source_day_record_ids"]
    assert context["source_month_map_ids"] == pattern["source_month_map_ids"]


def test_knowledge_candidate_mutation_flags_false() -> None:
    knowledge = try_bridge_calendar_rhythm_pattern_v1(_confirmed_pattern())["knowledge_candidate"]
    assert knowledge is not None
    assert knowledge["profile_update_allowed"] is False
    assert knowledge["memory_update_allowed"] is False
    assert knowledge["ranking_update_allowed"] is False
    assert knowledge["requires_review"] is True


def test_progression_context_mutation_flags_false() -> None:
    context = try_bridge_calendar_rhythm_pattern_v1(_confirmed_pattern())["progression_context"]
    assert context is not None
    assert context["evolution_stage_update_allowed"] is False
    assert context["profile_update_allowed"] is False
    assert context["memory_update_allowed"] is False
    assert context["insight_allowed"] is False
    assert context["recommendation_allowed"] is False


def test_no_insight_or_recommendation_fields() -> None:
    outcome = try_bridge_calendar_rhythm_pattern_v1(_confirmed_pattern())
    for artifact in (outcome["knowledge_candidate"], outcome["progression_context"]):
        assert artifact is not None
        assert "insight" not in artifact
        assert "recommendation" not in artifact


def test_output_shape_stable() -> None:
    pattern = _confirmed_pattern()
    outcome = try_bridge_calendar_rhythm_pattern_v1(pattern)
    knowledge = outcome["knowledge_candidate"]
    context = outcome["progression_context"]
    assert knowledge is not None and context is not None

    assert knowledge["contract_version"] == CALENDAR_RHYTHM_KNOWLEDGE_CANDIDATE_V1_CONTRACT
    assert context["contract_version"] == CALENDAR_EVOLUTION_PROGRESSION_CONTEXT_V1_CONTRACT
    assert set(knowledge.keys()) == CALENDAR_RHYTHM_KNOWLEDGE_CANDIDATE_V1_KEYS
    assert set(context.keys()) == CALENDAR_EVOLUTION_PROGRESSION_CONTEXT_V1_KEYS
    assert validate_calendar_rhythm_knowledge_candidate_v1(knowledge, pattern=pattern) == []
    assert validate_calendar_evolution_progression_context_v1(context, pattern=pattern) == []


def test_weak_unconfirmed_candidate_path_rejected_before_bridge() -> None:
    weak = _strong_candidate(strength=0.2, confidence=0.3, evidence_count=2, evidence_window_days=10)
    confirm = try_confirm_rhythm_pattern_from_candidate_v1(weak)
    assert confirm["pattern"] is None
    assert confirm["result"] != BRIDGE_RESULT_BRIDGED

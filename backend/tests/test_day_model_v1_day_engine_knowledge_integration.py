"""A1.2 — Day Engine knowledge integration contract tests."""

from __future__ import annotations

from todayflow_backend.services.day_model_v1_day_engine_knowledge_integration import (
    APPLICATION_MODE_BOOST,
    APPLICATION_MODE_INCLUDE,
    APPLICATION_MODE_PRIORITIZE,
    CONSUMER_DAY_ENGINE,
    DAY_ENGINE_KNOWLEDGE_INPUT_V1_CONTRACT,
    DAY_ENGINE_KNOWLEDGE_INPUT_V1_KEYS,
    FORBIDDEN_INTEGRATION_OPERATIONS,
    HINT_CHANNEL_ACTION_MODE,
    HINT_CHANNEL_CONTENT_AFFINITY,
    HINT_CHANNEL_RESPONSE_STYLE,
    HINT_CHANNEL_RISK_SENSITIVITY,
    HINT_CHANNEL_TEMPO_ALIGNMENT,
    INTEGRATION_POLICY_VERSION,
    INTEGRATION_RESULT_CREATED,
    INTEGRATION_RESULT_REJECTED,
    MAX_HINTS_PER_CHANNEL,
    MAX_TOTAL_HINTS,
    map_fact_to_hint,
    try_build_day_engine_knowledge_input_v1,
    validate_day_engine_knowledge_input_v1,
)
from todayflow_backend.services.day_model_v1_knowledge_candidate import (
    KNOWLEDGE_TYPE_BEHAVIOR,
    KNOWLEDGE_TYPE_CONTENT_AFFINITY,
    KNOWLEDGE_TYPE_RESPONSE_STYLE,
    KNOWLEDGE_TYPE_TIMING,
)
from todayflow_backend.services.day_model_v1_knowledge_context_selection import (
    KNOWLEDGE_CONTEXT_SLICE_V1_CONTRACT,
    select_knowledge_context_v1,
)
from todayflow_backend.services.day_model_v1_active_knowledge import (
    DAY_ACTIVE_KNOWLEDGE_V1_CONTRACT,
)


def _active(**overrides):
    base = {
        "contract_version": DAY_ACTIVE_KNOWLEDGE_V1_CONTRACT,
        "knowledge_id": "know-test-001",
        "source_knowledge_candidate_id": "kcand-test-001",
        "knowledge_type": KNOWLEDGE_TYPE_CONTENT_AFFINITY,
        "claim": "prefers_content_key_group:day.guidance",
        "confidence": 0.8,
        "evidence_count": 7,
        "evidence_window_days": 21,
        "evidence_signal_ids": [f"lsig-{i}" for i in range(7)],
        "source_pattern_id": "pat-test-001",
        "status": "active",
        "created_at": "2026-05-31T12:00:00Z",
        "last_confirmed_at": "2026-05-31T12:00:00Z",
        "expires_at": None,
        "review_required": False,
        "profile_update_allowed": False,
        "memory_update_allowed": False,
        "ranking_update_allowed": False,
    }
    base.update(overrides)
    return base


def _context_slice(**overrides):
    base = select_knowledge_context_v1(
        [_active()],
        day_context={"content_keys": ["day.guidance"]},
        target_surface="day_guidance_card",
    )
    base.update(overrides)
    return base


def test_builds_from_valid_context_slice():
    outcome = try_build_day_engine_knowledge_input_v1(_context_slice())
    assert outcome["result"] == INTEGRATION_RESULT_CREATED
    inp = outcome["knowledge_input"]
    assert inp is not None
    assert inp["contract_version"] == DAY_ENGINE_KNOWLEDGE_INPUT_V1_CONTRACT
    assert inp["consumer"] == CONSUMER_DAY_ENGINE
    assert len(inp["hints"]) == 1
    assert inp["hints"][0]["hint_channel"] == HINT_CHANNEL_CONTENT_AFFINITY
    assert inp["hints"][0]["application_mode"] == APPLICATION_MODE_BOOST


def test_rejects_invalid_slice_contract():
    bad = _context_slice(contract_version="wrong")
    outcome = try_build_day_engine_knowledge_input_v1(bad)
    assert outcome["result"] == INTEGRATION_RESULT_REJECTED
    assert outcome["knowledge_input"] is None


def test_empty_slice_produces_empty_hints():
    empty = _context_slice(selected_facts=[])
    outcome = try_build_day_engine_knowledge_input_v1(empty)
    assert outcome["result"] == INTEGRATION_RESULT_CREATED
    inp = outcome["knowledge_input"]
    assert inp is not None
    assert inp["hints"] == []
    assert inp["influence_summary"]["max_influence_level"] == "none"


def test_maps_all_claim_prefix_channels():
    facts = [
        {
            "knowledge_id": "k1",
            "claim": "prefers_content_key_group:day.guidance",
            "knowledge_type": KNOWLEDGE_TYPE_CONTENT_AFFINITY,
            "influence_level": "medium",
        },
        {
            "knowledge_id": "k2",
            "claim": "responds_to_surface:short_action",
            "knowledge_type": KNOWLEDGE_TYPE_RESPONSE_STYLE,
            "influence_level": "medium",
        },
        {
            "knowledge_id": "k3",
            "claim": "responds_to_action_mode:single_step",
            "knowledge_type": KNOWLEDGE_TYPE_BEHAVIOR,
            "influence_level": "low",
        },
        {
            "knowledge_id": "k4",
            "claim": "responds_to_tempo:steady",
            "knowledge_type": KNOWLEDGE_TYPE_TIMING,
            "influence_level": "low",
        },
        {
            "knowledge_id": "k5",
            "claim": "risk_response_tolerance:low",
            "knowledge_type": KNOWLEDGE_TYPE_RESPONSE_STYLE,
            "influence_level": "low",
        },
    ]
    slice_out = _context_slice(selected_facts=facts)
    outcome = try_build_day_engine_knowledge_input_v1(slice_out)
    inp = outcome["knowledge_input"]
    assert inp is not None
    channels = {h["hint_channel"] for h in inp["hints"]}
    assert channels == {
        HINT_CHANNEL_CONTENT_AFFINITY,
        HINT_CHANNEL_RESPONSE_STYLE,
        HINT_CHANNEL_ACTION_MODE,
        HINT_CHANNEL_TEMPO_ALIGNMENT,
        HINT_CHANNEL_RISK_SENSITIVITY,
    }


def test_channel_cap_skips_excess():
    facts = [
        {
            "knowledge_id": f"k-{i}",
            "claim": f"prefers_content_key_group:day.topic{i}",
            "knowledge_type": KNOWLEDGE_TYPE_CONTENT_AFFINITY,
            "influence_level": "low",
            "final_score": 0.9 - i * 0.01,
        }
        for i in range(4)
    ]
    slice_out = _context_slice(selected_facts=facts)
    outcome = try_build_day_engine_knowledge_input_v1(slice_out)
    inp = outcome["knowledge_input"]
    assert inp is not None
    content_hints = inp["hint_channels"][HINT_CHANNEL_CONTENT_AFFINITY]
    assert len(content_hints) == MAX_HINTS_PER_CHANNEL
    assert len(inp["skipped_facts"]) == 2


def test_day_model_snapshot_hash_trace():
    snapshot = {
        "contract_version": "day_model_v0",
        "vector": {"direction": "growth"},
        "tempo": {"label": "steady"},
        "risk": {"summary": "test"},
        "scales": {"tempo": "steady"},
        "gate": {"vector_defined": True},
    }
    outcome = try_build_day_engine_knowledge_input_v1(
        _context_slice(),
        day_model_snapshot=snapshot,
    )
    inp = outcome["knowledge_input"]
    assert inp is not None
    assert inp["day_model_snapshot_hash"] is not None
    assert len(inp["day_model_snapshot_hash"]) == 64


def test_rejects_snapshot_with_forbidden_keys():
    snapshot = {
        "contract_version": "day_model_v0",
        "internal_profile": {"secret": "data"},
    }
    outcome = try_build_day_engine_knowledge_input_v1(
        _context_slice(),
        day_model_snapshot=snapshot,
    )
    assert outcome["result"] == INTEGRATION_RESULT_REJECTED


def test_knowledge_applied_always_false():
    inp = try_build_day_engine_knowledge_input_v1(_context_slice())["knowledge_input"]
    assert inp is not None
    assert inp["knowledge_applied"] is False


def test_mutation_flags_false():
    inp = try_build_day_engine_knowledge_input_v1(_context_slice())["knowledge_input"]
    assert inp is not None
    assert inp["profile_update_allowed"] is False
    assert inp["memory_update_allowed"] is False
    assert inp["ranking_model_update_allowed"] is False


def test_output_shape_stable():
    inp = try_build_day_engine_knowledge_input_v1(_context_slice())["knowledge_input"]
    assert inp is not None
    assert set(inp.keys()) == set(DAY_ENGINE_KNOWLEDGE_INPUT_V1_KEYS)
    assert validate_day_engine_knowledge_input_v1(inp) == []
    assert inp["integration_policy_version"] == INTEGRATION_POLICY_VERSION
    assert inp["traceability"]["integrated_count"] == len(inp["hints"])


def test_map_fact_to_hint_values():
    hint = map_fact_to_hint(
        {
            "knowledge_id": "k1",
            "claim": "responds_to_surface:short_action",
            "knowledge_type": KNOWLEDGE_TYPE_RESPONSE_STYLE,
        }
    )
    assert hint is not None
    assert hint["hint_value"] == "short_action"
    assert hint["application_mode"] == APPLICATION_MODE_PRIORITIZE


def test_tempo_hint_uses_include_mode():
    hint = map_fact_to_hint(
        {
            "knowledge_id": "k1",
            "claim": "responds_to_tempo:slow",
            "knowledge_type": KNOWLEDGE_TYPE_TIMING,
        }
    )
    assert hint is not None
    assert hint["hint_channel"] == HINT_CHANNEL_TEMPO_ALIGNMENT
    assert hint["application_mode"] == APPLICATION_MODE_INCLUDE


def test_forbidden_operations_documented():
    assert "override_daymodel" in FORBIDDEN_INTEGRATION_OPERATIONS
    assert "change_strategy" in FORBIDDEN_INTEGRATION_OPERATIONS


def test_total_cap_respected():
    facts = [
        {
            "knowledge_id": f"k-{i}",
            "claim": f"prefers_content_key_group:day.t{i % 2}",
            "knowledge_type": KNOWLEDGE_TYPE_CONTENT_AFFINITY,
            "influence_level": "low",
        }
        for i in range(8)
    ]
    slice_out = _context_slice(selected_facts=facts)
    outcome = try_build_day_engine_knowledge_input_v1(slice_out)
    inp = outcome["knowledge_input"]
    assert inp is not None
    assert len(inp["hints"]) <= MAX_TOTAL_HINTS

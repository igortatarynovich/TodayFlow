"""AMLL Gate v1 for Today narrative surfaces."""

from __future__ import annotations

import pytest

from todayflow_backend.services.today_narrative_llm_gate_v1 import (
    GATE_DECISION_CACHE_HIT,
    GATE_DECISION_CALL_LLM,
    GATE_DECISION_BLOCKED,
    GATE_DECISION_REUSE,
    GATE_DECISION_TEMPLATE,
    TODAY_NARRATIVE_LLM_GATE_V1_CONTRACT,
    build_cache_hit_gate_v1,
    decide_today_narrative_llm_call_v1,
    should_skip_llm_for_gate,
    validate_today_narrative_llm_gate_v1,
)


def test_cache_hit_gate_shape() -> None:
    gate = build_cache_hit_gate_v1(surface="guide", source_generation_log_id=42, context_slice_id="abc")
    assert gate["contract_version"] == TODAY_NARRATIVE_LLM_GATE_V1_CONTRACT
    assert gate["gate_decision"] == GATE_DECISION_CACHE_HIT
    assert gate["reuse_source_generation_id"] == 42
    assert gate["reason"] == "GATE:cache_hit:exact_context_match"
    assert not validate_today_narrative_llm_gate_v1(gate)


def test_cache_hit_gate_same_day_reuse_mode() -> None:
    gate = build_cache_hit_gate_v1(
        surface="guide",
        source_generation_log_id=7,
        context_slice_id="abc",
        match_mode="same_day_reuse",
    )
    assert gate["gate_decision"] == GATE_DECISION_CACHE_HIT
    assert gate["reason"] == "GATE:cache_hit:same_day_reuse"
    assert gate["cache_policy"] == "allow_similarity"
    assert gate["reuse_source_generation_id"] == 7
    assert not validate_today_narrative_llm_gate_v1(gate)


def test_call_llm_when_configured() -> None:
    gate = decide_today_narrative_llm_call_v1(
        surface="guide",
        llm_configured=True,
        user_context={"has_day_context": True, "context_slice_id": "sha256"},
        depth_level="normal",
    )
    assert gate["gate_decision"] == GATE_DECISION_CALL_LLM
    # Default LLM_QUALITY_MODE=rich → generous budget (legacy economize was 1750).
    assert gate["max_tokens"] >= 1750
    assert gate["save_required"] is True
    assert should_skip_llm_for_gate(gate) is False


def test_template_when_llm_not_configured() -> None:
    gate = decide_today_narrative_llm_call_v1(
        surface="spheres",
        llm_configured=False,
        user_context={"has_day_context": True},
    )
    assert gate["gate_decision"] == GATE_DECISION_TEMPLATE
    assert should_skip_llm_for_gate(gate) is True


def test_reuse_when_similarity_available() -> None:
    gate = decide_today_narrative_llm_call_v1(
        surface="evening",
        llm_configured=True,
        cache_status={"similarity_available": True, "reuse_source_generation_id": 99},
    )
    assert gate["gate_decision"] == GATE_DECISION_REUSE
    assert gate["reuse_source_generation_id"] == 99
    assert should_skip_llm_for_gate(gate) is True


def test_blocked_strict_cost_policy() -> None:
    gate = decide_today_narrative_llm_call_v1(
        surface="deepen",
        llm_configured=True,
        cost_policy={"mode": "strict", "llm_calls_allowed": False},
    )
    assert gate["gate_decision"] == GATE_DECISION_BLOCKED
    assert gate["blocked_reason"] == "cost_policy_strict"
    assert should_skip_llm_for_gate(gate) is True


def test_child_surface_standard_tier_in_rich_mode() -> None:
    gate = decide_today_narrative_llm_call_v1(
        surface="spheres",
        llm_configured=True,
        depth_level="normal",
    )
    # rich mode: no cheap-tier preference for child surfaces
    assert gate["allowed_model_tier"] == "standard"
    assert gate["max_tokens"] >= 800


def test_unsupported_surface_raises() -> None:
    with pytest.raises(Exception):
        decide_today_narrative_llm_call_v1(surface="unknown", llm_configured=True)

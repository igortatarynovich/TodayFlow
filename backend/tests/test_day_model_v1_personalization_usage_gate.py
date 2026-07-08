"""A1.5 — Personalization usage gate tests."""

from __future__ import annotations

from datetime import date

from todayflow_backend.services.day_context import build_day_context_v0
from todayflow_backend.services.day_model_v1_active_knowledge import (
    DAY_ACTIVE_KNOWLEDGE_V1_CONTRACT,
)
from todayflow_backend.services.day_model_v1_knowledge_candidate import (
    KNOWLEDGE_TYPE_RESPONSE_STYLE,
)
from todayflow_backend.services.day_model_v1_llm_call_gate import (
    CONTEXT_DEPTH_MINIMAL,
    CONTEXT_DEPTH_STANDARD,
    DAY_CONTENT_LLM_GATE_V1_CONTRACT,
    DECISION_CALL_LLM,
    DECISION_NO_CALL,
)
from todayflow_backend.services.day_model_v1_personalization_usage_gate import (
    DENY_CONTEXT_DEPTH_NOT_STANDARD,
    DENY_EMPTY_SUMMARY,
    DENY_LLM_GATE_NOT_CALL,
    DENY_NO_PERSONALIZATION_SOURCE,
    DENY_SURFACE_INELIGIBLE,
    PERSONALIZATION_USAGE_GATE_V1_CONTRACT,
    PERSONALIZATION_USAGE_GATE_V1_KEYS,
    USAGE_DECISION_ALLOW,
    USAGE_DECISION_DENY,
    USAGE_RESULT_ALLOWED,
    USAGE_RESULT_DENIED,
    try_decide_personalization_usage_v1,
    validate_personalization_usage_gate_v1,
)


def _llm_gate(**overrides):
    base = {
        "contract_version": DAY_CONTENT_LLM_GATE_V1_CONTRACT,
        "surface": "day_guidance_card",
        "decision": DECISION_CALL_LLM,
        "reason": "test",
        "allowed_context_depth": CONTEXT_DEPTH_STANDARD,
        "allowed_model_tier": "standard",
        "max_tokens": 256,
    }
    base.update(overrides)
    return base


def _active(**overrides):
    base = {
        "contract_version": DAY_ACTIVE_KNOWLEDGE_V1_CONTRACT,
        "knowledge_id": "know-test-001",
        "source_knowledge_candidate_id": "kcand-test-001",
        "knowledge_type": KNOWLEDGE_TYPE_RESPONSE_STYLE,
        "claim": "responds_to_surface:short_action",
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


def _day_context_layers():
    fusion = {
        "date": "2026-05-31",
        "scores": {"energy": 55},
        "cycle_context": {},
        "activity_context": {},
        "rhythm_context": {"goals": [], "habits": [], "ascetics": [], "diary": {}},
        "recommendations": [],
        "encouragement": "",
    }
    ctx = build_day_context_v0(
        target_date=date(2026, 5, 31),
        locale="ru",
        insight_depth_tier="free",
        core_profile=None,
        fusion_dump=fusion,
        active_knowledge_list=[_active()],
    )
    return ctx["layers"]


def test_allows_with_standard_depth_and_summary():
    outcome = try_decide_personalization_usage_v1(
        surface="day_guidance_card",
        llm_gate_decision=_llm_gate(),
        safe_personalization_summary=["Prefers short actionable guidance"],
    )
    assert outcome["result"] == USAGE_RESULT_ALLOWED
    gate = outcome["usage_gate"]
    assert gate is not None
    assert gate["decision"] == USAGE_DECISION_ALLOW
    assert gate["allowed_fact_count"] == 1


def test_denies_when_llm_gate_not_call():
    outcome = try_decide_personalization_usage_v1(
        surface="day_guidance_card",
        llm_gate_decision=_llm_gate(decision=DECISION_NO_CALL),
        safe_personalization_summary=["fact"],
    )
    assert outcome["result"] == USAGE_RESULT_DENIED
    assert outcome["usage_gate"]["reason"] == DENY_LLM_GATE_NOT_CALL


def test_denies_minimal_context_depth():
    outcome = try_decide_personalization_usage_v1(
        surface="day_guidance_card",
        llm_gate_decision=_llm_gate(allowed_context_depth=CONTEXT_DEPTH_MINIMAL),
        safe_personalization_summary=["fact"],
    )
    assert outcome["result"] == USAGE_RESULT_DENIED
    assert outcome["usage_gate"]["reason"] == DENY_CONTEXT_DEPTH_NOT_STANDARD


def test_denies_deterministic_surface():
    outcome = try_decide_personalization_usage_v1(
        surface="today_hero",
        llm_gate_decision=_llm_gate(surface="today_hero"),
        safe_personalization_summary=["fact"],
    )
    assert outcome["result"] == USAGE_RESULT_DENIED
    assert outcome["usage_gate"]["reason"] == DENY_SURFACE_INELIGIBLE


def test_denies_no_personalization_source():
    outcome = try_decide_personalization_usage_v1(
        surface="day_guidance_card",
        llm_gate_decision=_llm_gate(),
    )
    assert outcome["result"] == USAGE_RESULT_DENIED
    assert outcome["usage_gate"]["reason"] == DENY_NO_PERSONALIZATION_SOURCE


def test_denies_no_source_when_layers_have_no_personalization():
    fusion = {
        "date": "2026-05-31",
        "scores": {"energy": 55},
        "cycle_context": {},
        "activity_context": {},
        "rhythm_context": {"goals": [], "habits": [], "ascetics": [], "diary": {}},
        "recommendations": [],
        "encouragement": "",
    }
    ctx = build_day_context_v0(
        target_date=date(2026, 5, 31),
        locale="ru",
        insight_depth_tier="free",
        core_profile=None,
        fusion_dump=fusion,
        active_knowledge_list=[],
    )
    outcome = try_decide_personalization_usage_v1(
        surface="day_guidance_card",
        llm_gate_decision=_llm_gate(),
        day_context_layers=ctx["layers"],
    )
    assert outcome["result"] == USAGE_RESULT_DENIED
    assert outcome["usage_gate"]["reason"] == DENY_NO_PERSONALIZATION_SOURCE


def test_denies_empty_explicit_summary():
    outcome = try_decide_personalization_usage_v1(
        surface="day_guidance_card",
        llm_gate_decision=_llm_gate(),
        safe_personalization_summary=[],
    )
    assert outcome["result"] == USAGE_RESULT_DENIED
    assert outcome["usage_gate"]["reason"] == DENY_EMPTY_SUMMARY


def test_allows_from_day_context_layers():
    outcome = try_decide_personalization_usage_v1(
        surface="day_guidance_card",
        llm_gate_decision=_llm_gate(),
        day_context_layers=_day_context_layers(),
    )
    assert outcome["result"] == USAGE_RESULT_ALLOWED
    assert len(outcome["usage_gate"]["safe_personalization_summary"]) >= 1


def test_denies_sensitive_summary_text():
    outcome = try_decide_personalization_usage_v1(
        surface="day_guidance_card",
        llm_gate_decision=_llm_gate(),
        safe_personalization_summary=["User has depression trait pattern"],
    )
    assert outcome["result"] == USAGE_RESULT_DENIED


def test_output_shape_stable():
    gate = try_decide_personalization_usage_v1(
        surface="day_guidance_card",
        llm_gate_decision=_llm_gate(),
        safe_personalization_summary=["Prefers concise guidance"],
    )["usage_gate"]
    assert gate is not None
    assert set(gate.keys()) == set(PERSONALIZATION_USAGE_GATE_V1_KEYS)
    assert gate["contract_version"] == PERSONALIZATION_USAGE_GATE_V1_CONTRACT
    assert validate_personalization_usage_gate_v1(gate) == []


def test_mutation_flags_false():
    gate = try_decide_personalization_usage_v1(
        surface="day_guidance_card",
        llm_gate_decision=_llm_gate(),
        safe_personalization_summary=["fact"],
    )["usage_gate"]
    assert gate is not None
    assert gate["profile_update_allowed"] is False
    assert gate["memory_update_allowed"] is False
    assert gate["ranking_model_update_allowed"] is False


def test_deny_gate_shape_valid():
    gate = try_decide_personalization_usage_v1(
        surface="day_guidance_card",
        llm_gate_decision=_llm_gate(decision=DECISION_NO_CALL),
        safe_personalization_summary=["fact"],
    )["usage_gate"]
    assert gate is not None
    assert gate["decision"] == USAGE_DECISION_DENY
    assert gate["allowed_fact_count"] == 0

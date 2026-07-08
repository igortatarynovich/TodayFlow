"""A1.4 — Profile knowledge personalization tests."""

from __future__ import annotations

from datetime import date

from todayflow_backend.services.day_context import build_day_context_v0
from todayflow_backend.services.day_model_v1_active_knowledge import (
    DAY_ACTIVE_KNOWLEDGE_V1_CONTRACT,
)
from todayflow_backend.services.day_model_v1_knowledge_candidate import (
    KNOWLEDGE_TYPE_CONTENT_AFFINITY,
    KNOWLEDGE_TYPE_RESPONSE_STYLE,
)
from todayflow_backend.services.day_model_v1_knowledge_context_selection import (
    select_knowledge_context_v1,
)
from todayflow_backend.services.day_model_v1_profile_knowledge_personalization import (
    PERSONALIZATION_RESULT_CREATED,
    PERSONALIZATION_RESULT_EMPTY,
    PERSONALIZATION_RESULT_REJECTED,
    PROFILE_KNOWLEDGE_PERSONALIZATION_V1_CONTRACT,
    PROFILE_KNOWLEDGE_PERSONALIZATION_V1_KEYS,
    build_safe_personalization_summary_from_selected_facts,
    claim_to_safe_gloss,
    enrich_profile_selector_with_knowledge_v1,
    get_safe_personalization_summary_from_layers,
    try_build_profile_knowledge_personalization_v1,
    validate_profile_knowledge_personalization_v1,
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


def test_claim_to_safe_gloss_content_affinity():
    gloss = claim_to_safe_gloss(
        "prefers_content_key_group:day.guidance",
        knowledge_type="content_affinity",
    )
    assert "day guidance" in gloss.lower()
    assert "trait" not in gloss.lower()


def test_build_summary_from_selected_facts():
    facts = [
        {
            "knowledge_id": "k1",
            "claim": "responds_to_surface:short_action",
            "knowledge_type": "response_style",
        },
        {
            "knowledge_id": "k2",
            "claim": "responds_to_action_mode:single_step",
            "knowledge_type": "behavior",
        },
    ]
    summary, traces = build_safe_personalization_summary_from_selected_facts(facts)
    assert len(summary) == 2
    assert len(traces) == 2
    assert "short action" in summary[0].lower()


def test_build_personalization_from_context_slice():
    outcome = try_build_profile_knowledge_personalization_v1(_context_slice())
    assert outcome["result"] == PERSONALIZATION_RESULT_CREATED
    personalization = outcome["personalization"]
    assert personalization is not None
    assert personalization["contract_version"] == PROFILE_KNOWLEDGE_PERSONALIZATION_V1_CONTRACT
    assert len(personalization["safe_personalization_summary"]) == 1
    assert validate_profile_knowledge_personalization_v1(personalization) == []


def test_empty_slice_returns_empty_summary():
    empty = _context_slice(selected_facts=[])
    outcome = try_build_profile_knowledge_personalization_v1(empty)
    assert outcome["result"] == PERSONALIZATION_RESULT_EMPTY
    personalization = outcome["personalization"]
    assert personalization is not None
    assert personalization["safe_personalization_summary"] == []


def test_rejects_invalid_slice():
    outcome = try_build_profile_knowledge_personalization_v1(
        _context_slice(contract_version="wrong")
    )
    assert outcome["result"] == PERSONALIZATION_RESULT_REJECTED
    assert outcome["personalization"] is None


def test_enrich_profile_selector_attaches_summary():
    selector = {
        "task": "today_summary",
        "topic": "general",
        "relevant_profile": {},
        "generation_rules": {},
    }
    enriched = enrich_profile_selector_with_knowledge_v1(selector, _context_slice())
    assert "safe_personalization_summary" in enriched
    assert len(enriched["safe_personalization_summary"]) == 1
    assert enriched["knowledge_personalization"]["context_slice_id"] is not None


def test_get_summary_from_layers_prefers_profile_selector():
    layers = {
        "profile_selector": {"safe_personalization_summary": ["fact one", "fact two"]},
        "profile_knowledge_personalization": {
            "safe_personalization_summary": ["ignored"],
        },
    }
    assert get_safe_personalization_summary_from_layers(layers) == ["fact one", "fact two"]


def test_output_shape_stable():
    personalization = try_build_profile_knowledge_personalization_v1(_context_slice())[
        "personalization"
    ]
    assert personalization is not None
    assert set(personalization.keys()) == set(PROFILE_KNOWLEDGE_PERSONALIZATION_V1_KEYS)


def test_mutation_flags_false():
    personalization = try_build_profile_knowledge_personalization_v1(_context_slice())[
        "personalization"
    ]
    assert personalization is not None
    assert personalization["profile_update_allowed"] is False
    assert personalization["memory_update_allowed"] is False
    assert personalization["ranking_model_update_allowed"] is False


def test_day_context_profile_selector_has_safe_summary():
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
        active_knowledge_list=[
            _active(
                knowledge_type=KNOWLEDGE_TYPE_RESPONSE_STYLE,
                claim="responds_to_surface:short_action",
            )
        ],
    )
    ps = ctx["layers"]["profile_selector"]
    assert isinstance(ps.get("safe_personalization_summary"), list)
    assert len(ps["safe_personalization_summary"]) >= 1
    assert "profile_knowledge_personalization" in ctx["layers"]


def test_layers_summary_ready_for_llm_standard_depth():
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
    summary = get_safe_personalization_summary_from_layers(ctx["layers"])
    assert len(summary) >= 1
    assert all(isinstance(line, str) and line.strip() for line in summary)
    assert len(summary) <= 5


def test_summary_respects_max_five_facts():
    facts = [
        {
            "knowledge_id": f"k-{i}",
            "claim": f"prefers_content_key_group:day.topic{i}",
            "knowledge_type": "content_affinity",
        }
        for i in range(8)
    ]
    summary, _ = build_safe_personalization_summary_from_selected_facts(facts)
    assert len(summary) <= 5

"""DayContext v0 builder — структурные инварианты (полная JSON Schema — scripts/validate_day_context_contract.py)."""

from __future__ import annotations

from datetime import date

from todayflow_backend.profile_engine.models import ProfilePromptSurface, ProfileTaskType
from todayflow_backend.services.day_context import build_day_context_v0


def test_build_day_context_v0_minimal_structure():
    d = date(2026, 5, 3)
    fusion = {
        "date": d.isoformat(),
        "scores": {"energy": 1, "emotional_balance": 2, "focus": 3},
        "cycle_context": {},
        "activity_context": {},
        "rhythm_context": {
            "goals": [],
            "habits": [],
            "ascetics": [],
            "diary": {"has_entry_today": False, "entries_last_7_days": 0},
        },
        "recommendations": [],
        "encouragement": "ok",
    }
    ctx = build_day_context_v0(
        target_date=d,
        locale="ru",
        insight_depth_tier="free",
        core_profile=None,
        fusion_dump=fusion,
        ritual_context=None,
        ritual_context_fingerprint="abc",
    )
    assert ctx["contract_version"] == "day_context_v0"
    assert ctx["meta"]["target_date"] == "2026-05-03"
    assert ctx["meta"]["locale"] == "ru"
    assert ctx["meta"]["insight_depth_tier"] == "free"
    assert ctx["meta"]["depth_level"] == "normal"
    assert ctx["meta"]["ritual_context_fingerprint"] == "abc"
    assert "user_core" in ctx["layers"]
    assert ctx["layers"]["fusion"]["date"] == "2026-05-03"
    assert ctx["layers"]["fusion"]["rhythm_context"]["diary"]["entries_last_7_days"] == 0
    assert "ritual" not in ctx["layers"]
    dm = ctx["layers"].get("day_model")
    assert isinstance(dm, dict)
    assert dm.get("contract_version") == "day_model_v0"
    assert "vector" in dm and "gate" in dm
    gd = ctx["layers"].get("guide_decision")
    assert isinstance(gd, dict)
    assert gd.get("contract_version") == "guide_decision_v0"

    ps = ctx["layers"].get("profile_selector")
    assert isinstance(ps, dict)
    assert ps.get("task") == "today_summary"
    assert "relevant_profile" in ps and "generation_rules" in ps


def test_build_day_context_v0_coerces_partial_fusion():
    d = date(2026, 1, 15)
    ctx = build_day_context_v0(
        target_date=d,
        locale="en",
        insight_depth_tier="premium",
        core_profile={},
        fusion_dump={"encouragement": "x"},
        ritual_context={"mood": " calm ", "numerology_value": "7"},
    )
    f = ctx["layers"]["fusion"]
    assert f["date"] == "2026-01-15"
    assert isinstance(f["scores"], dict)
    assert isinstance(f["rhythm_context"], dict)
    assert isinstance(f["recommendations"], list)
    assert f["encouragement"] == "x"
    assert ctx["layers"]["ritual"]["mood"] == "calm"
    assert ctx["layers"]["ritual"]["numerology_value"] == "7"


def test_build_day_context_v0_behavior_patterns_layer():
    d = date(2026, 5, 3)
    fusion = {
        "date": d.isoformat(),
        "scores": {},
        "cycle_context": {},
        "activity_context": {},
        "rhythm_context": {"goals": [], "habits": [], "ascetics": [], "diary": {"has_entry_today": False, "entries_last_7_days": 0}},
        "recommendations": [],
        "encouragement": "ok",
    }
    bp = {
        "contract_version": "meaning_surface_patterns_v0",
        "window_days": 7,
        "window_start": "2026-04-27",
        "window_end": "2026-05-03",
        "total_events": 3,
        "by_event_type": [{"event_type": "mood_selected", "count": 3}],
        "tags": {"top_mood_ids": []},
        "pattern_hints": ["Тестовая подсказка."],
    }
    ctx = build_day_context_v0(
        target_date=d,
        locale="ru",
        insight_depth_tier="free",
        core_profile=None,
        fusion_dump=fusion,
        behavior_patterns=bp,
    )
    assert ctx["layers"]["behavior_patterns"] == bp


def test_build_day_context_v0_intent_layer_and_head_topic_ritual():
    d = date(2026, 5, 3)
    fusion = {
        "date": d.isoformat(),
        "scores": {},
        "cycle_context": {},
        "activity_context": {},
        "rhythm_context": {"goals": [], "habits": [], "ascetics": [], "diary": {"has_entry_today": False, "entries_last_7_days": 0}},
        "recommendations": [],
        "encouragement": "ok",
    }
    intent = {
        "contract_version": "intent_slice_v0",
        "morning_intention": "День спокойно",
        "morning_focus": None,
        "head_topic": "семья",
        "question_of_day_answer": None,
        "quick_decision_answer": None,
        "what_matters_line": "Цель/намерение на день: День спокойно Тема «в голове» после ритуала: семья",
    }
    ctx = build_day_context_v0(
        target_date=d,
        locale="ru",
        insight_depth_tier="free",
        core_profile=None,
        fusion_dump=fusion,
        ritual_context={"head_topic": "семья", "mood": "calm"},
        intent_slice=intent,
    )
    assert ctx["layers"]["intent"] == intent
    assert ctx["layers"]["ritual"]["head_topic"] == "семья"
    assert ctx["layers"]["ritual"]["mood"] == "calm"
    vp = ctx["layers"].get("visible_profile")
    assert isinstance(vp, dict)
    assert vp.get("contract_version") == "visible_profile_slice_v0"
    assert "День спокойно" in (vp.get("current_intention_or_goal_text") or "")


def test_build_day_context_v0_includes_history_slice():
    d = date(2026, 5, 4)
    fusion = {
        "date": d.isoformat(),
        "scores": {"energy": 48, "emotional_balance": 50, "focus": 51},
        "cycle_context": {},
        "activity_context": {},
        "rhythm_context": {"goals": [], "habits": [], "ascetics": [], "diary": {"has_entry_today": False, "entries_last_7_days": 0}},
        "recommendations": [],
        "encouragement": "ok",
    }
    hist = {
        "contract_version": "day_history_v0",
        "yesterday": {"date": "2026-05-03", "fusion_scores": {"energy": 50, "emotional_balance": 50, "focus": 50}, "day_flow": None},
        "fusion_scores_trailing_7d": [],
        "trailing_7d_summary": {},
        "fusion_score_delta_vs_yesterday": {"energy": 0, "emotional_balance": 0, "focus": 0},
    }
    ctx = build_day_context_v0(
        target_date=d,
        locale="ru",
        insight_depth_tier="free",
        core_profile=None,
        fusion_dump=fusion,
        history_slice=hist,
    )
    assert ctx["layers"]["history"] == hist


def test_build_day_context_v0_profile_selector_evening_task():
    d = date(2026, 5, 3)
    fusion = {
        "date": d.isoformat(),
        "scores": {},
        "cycle_context": {},
        "activity_context": {},
        "rhythm_context": {"goals": [], "habits": [], "ascetics": [], "diary": {"has_entry_today": False, "entries_last_7_days": 0}},
        "recommendations": [],
        "encouragement": "ok",
    }
    ctx = build_day_context_v0(
        target_date=d,
        locale="ru",
        insight_depth_tier="free",
        core_profile=None,
        fusion_dump=fusion,
        selector_surface=ProfilePromptSurface.EVENING,
        selector_task=ProfileTaskType.EVENING_REFLECTION,
    )
    ps = ctx["layers"]["profile_selector"]
    assert ps["task"] == "evening_reflection"


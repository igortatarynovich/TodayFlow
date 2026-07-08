from __future__ import annotations

from todayflow_backend.services.profile_prompt_slices_v0 import (
    build_internal_profile_slice_v0,
    build_visible_profile_slice_v0,
)


def test_visible_profile_includes_intent_and_ritual():
    fusion = {
        "scores": {"energy": 50},
        "rhythm_context": {"goals": [{"title": "Спорт 3 раза"}]},
    }
    vp = build_visible_profile_slice_v0(
        core_profile={"person": {"display_name": "Igor"}, "astro": {"sun_sign": "Virgo"}},
        intent_slice={
            "contract_version": "intent_slice_v0",
            "morning_intention": "найти 10 водителей",
            "morning_focus": "работа",
        },
        ritual={"mood": "тревожно", "head_topic": "money"},
        fusion_layer=fusion,
        locale="ru",
    )
    assert vp is not None
    assert vp["contract_version"] == "visible_profile_slice_v0"
    assert vp["display_name"] == "Igor"
    assert "найти 10 водителей" in vp.get("current_intention_or_goal_text", "")
    assert vp.get("recent_self_reported_mood") == "тревожно"


def test_internal_profile_none_when_no_signals():
    assert (
        build_internal_profile_slice_v0(
            core_profile=None,
            behavior_patterns=None,
            fusion_layer={"scores": {}},
        )
        is None
    )


def test_internal_profile_from_behavior_and_scores():
    ip = build_internal_profile_slice_v0(
        core_profile={"profile_version": 3},
        behavior_patterns={
            "contract_version": "meaning_surface_patterns_v0",
            "total_events": 10,
            "window_days": 28,
            "window_start": "2026-04-01",
            "window_end": "2026-05-03",
            "pattern_hints": ["Часто открывает сферу «work»."],
        },
        fusion_layer={"scores": {"energy": 44, "focus": 60}},
    )
    assert ip is not None
    assert ip["contract_version"] == "internal_profile_slice_v0"
    assert ip["source_profile_version"] == 3
    assert ip["app_rhythm_scores"]["energy"] == 44
    assert ip["surface_behavior_aggregates"]["total_events"] == 10

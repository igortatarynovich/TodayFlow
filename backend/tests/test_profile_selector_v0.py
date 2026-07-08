"""Profile Selector v0 — детерминированная маршрутизация без LLM."""

from __future__ import annotations

from todayflow_backend.profile_engine.models import (
    ProfileContextSelectorInput,
    ProfilePromptSurface,
    ProfileTaskType,
    ProfileTopicDomain,
    UserOperatingMode,
)
from todayflow_backend.profile_engine.selector import (
    infer_mode,
    narrative_surface_to_selector_params,
    resolve_task,
    resolve_topic,
    select_profile_context,
)


def test_resolve_task_explicit_overrides_surface_default():
    inp = ProfileContextSelectorInput(
        surface=ProfilePromptSurface.TODAY,
        task=ProfileTaskType.TODAY_ACTION,
        locale="ru",
    )
    assert resolve_task(inp) == ProfileTaskType.TODAY_ACTION


def test_resolve_topic_from_head_topic_slug():
    inp = ProfileContextSelectorInput(surface=ProfilePromptSurface.TODAY, locale="ru")
    ritual = {"head_topic": "love"}
    assert resolve_topic(inp, ritual) == ProfileTopicDomain.INTIMACY


def test_infer_mode_from_ritual_mood_anxious():
    inp = ProfileContextSelectorInput(surface=ProfilePromptSurface.TODAY, locale="ru")
    assert infer_mode(inp, {"mood": "anxious"}, None) == UserOperatingMode.ANXIETY


def test_narrative_surface_maps_guide_and_deepen_topic():
    s1, t1, top1 = narrative_surface_to_selector_params("guide")
    assert str(s1.value) == "guidance"
    assert t1 is not None and t1.value == "guidance_question"
    assert top1 is None
    s2, t2, top2 = narrative_surface_to_selector_params("deepen", deepen_topic="money")
    assert t2 is not None and t2.value == "today_spheres"
    assert top2 is not None and top2.value == "money"


def test_select_profile_context_anxious_short_generation_rules():
    inp = ProfileContextSelectorInput(surface=ProfilePromptSurface.TODAY, locale="ru")
    core = {
        "baseline": {"rhythm_style": "Утро — короткое планирование"},
        "interpretation": {"identity": "Тестовая линия"},
    }
    fusion = {
        "date": "2026-05-03",
        "scores": {"energy": 3, "focus": 3, "emotional_balance": 3},
        "cycle_context": {},
        "activity_context": {},
        "rhythm_context": {},
        "recommendations": [],
        "encouragement": "",
    }
    out = select_profile_context(
        inp,
        core_profile=core,
        fusion_dump=fusion,
        ritual_context={"mood": "anxious"},
        behavior_patterns=None,
    )
    assert out.task == ProfileTaskType.TODAY_SUMMARY
    assert out.current_mode == UserOperatingMode.ANXIETY
    assert out.generation_rules.depth == "short"
    assert "one concrete action" in out.generation_rules.must_include
    assert out.relevant_profile.get("action_fit") == "one_small_concrete_step"
    assert out.debug_trace is not None
    assert out.debug_trace.get("selector_rules_version") == "profile-selector-v1"

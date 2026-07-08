"""Profile Selector v1 — topic excerpts, day_history signals, eval harness."""

from __future__ import annotations

from datetime import date

from todayflow_backend.profile_engine.models import (
    ProfileContextSelectorInput,
    ProfilePromptSurface,
    ProfileTopicDomain,
)
from todayflow_backend.profile_engine.selector import select_profile_context
from todayflow_backend.profile_engine.selector_eval import (
    PROFILE_SELECTOR_EVAL_CASES,
    run_profile_selector_eval,
)
from todayflow_backend.services.day_context import build_day_context_v0


def test_topic_sphere_excerpt_from_life_areas():
    core = {
        "interpretation": {
            "life_areas": {
                "love": "В близости важна прямота и темп без давления.",
            }
        }
    }
    out = select_profile_context(
        ProfileContextSelectorInput(
            surface=ProfilePromptSurface.TODAY,
            topic=ProfileTopicDomain.INTIMACY,
            locale="ru",
        ),
        core_profile=core,
        fusion_dump={
            "date": "2026-07-03",
            "scores": {"energy": 3, "focus": 3, "emotional_balance": 3},
            "cycle_context": {},
            "activity_context": {},
            "rhythm_context": {},
            "recommendations": [],
            "encouragement": "",
        },
    )
    excerpt = out.relevant_profile.get("topic_sphere_excerpt") or ""
    assert "близост" in excerpt.lower()
    assert out.debug_trace is not None
    assert out.debug_trace.get("selector_rules_version") == "profile-selector-v1"


def test_day_history_signal_in_recent_signals():
    out = select_profile_context(
        ProfileContextSelectorInput(surface=ProfilePromptSurface.TODAY, locale="ru"),
        fusion_dump={
            "date": "2026-07-03",
            "scores": {"energy": 4, "focus": 3, "emotional_balance": 3},
            "cycle_context": {},
            "activity_context": {},
            "rhythm_context": {},
            "recommendations": [],
            "encouragement": "",
        },
        history_slice={
            "contract_version": "day_history_v0",
            "fusion_score_delta_vs_yesterday": {"energy": 1, "focus": 0, "emotional_balance": -1},
            "fusion_score_delta_trustworthy": True,
            "trailing_7d_summary": {"energy": {"avg": 52.5, "min": 40, "max": 60, "days": 7}},
            "trailing_7d_summary_trustworthy": True,
        },
    )
    assert any("day_history_delta:" in signal for signal in out.recent_signals)
    assert any("day_history_week_energy_avg:" in signal for signal in out.recent_signals)


def test_day_context_passes_history_into_profile_selector():
    ctx = build_day_context_v0(
        target_date=date(2026, 7, 3),
        locale="ru",
        insight_depth_tier="free",
        core_profile={
            "interpretation": {
                "life_areas": {"money": "Финансовая устойчивость растёт через ясные границы."}
            }
        },
        fusion_dump={
            "date": "2026-07-03",
            "scores": {"energy": 3, "focus": 3, "emotional_balance": 3},
            "cycle_context": {},
            "activity_context": {},
            "rhythm_context": {},
            "recommendations": [],
            "encouragement": "",
        },
        selector_topic=ProfileTopicDomain.MONEY,
        history_slice={
            "contract_version": "day_history_v0",
            "fusion_score_delta_vs_yesterday": {"energy": 0, "focus": 1, "emotional_balance": 0},
            "fusion_score_delta_trustworthy": True,
        },
    )
    ps = ctx["layers"]["profile_selector"]
    assert ps["debug_trace"]["selector_rules_version"] == "profile-selector-v1"
    assert "topic_sphere_excerpt" in ps["relevant_profile"]
    assert any("day_history_delta:" in signal for signal in ps["recent_signals"])


def test_profile_selector_eval_golden_cases_pass():
    results = run_profile_selector_eval(PROFILE_SELECTOR_EVAL_CASES)
    failures = [result for result in results if not result.passed]
    assert not failures, failures

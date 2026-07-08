"""DayModel v0 — детерминированные поля без LLM."""

from __future__ import annotations

from todayflow_backend.services.day_model_v0 import build_day_model_v0


def test_build_day_model_v0_direction_from_spine_axis_ru():
    foundation = {"spine": {"day_axis": "День про завершение одной линии", "first_move": "Закрыть задачу"}}
    ritual = {"mood": "спокойное", "numerology_value": "1"}
    out = build_day_model_v0(
        foundation=foundation,
        ritual=ritual,
        fusion_scores={"energy": 50},
        intent_slice=None,
        internal_profile=None,
        locale="ru",
    )
    assert out["contract_version"] == "day_model_v0"
    assert out["scales"]["direction"] == "completion"
    assert out["scales"]["action_type"] == "finish"
    assert out["scales"]["emotions"] == "stable"
    assert out["scales"]["tempo"] == "steady"
    assert "заверш" in out["vector"]["summary"].lower() or "линии" in out["vector"]["summary"].lower()


def test_build_day_model_v0_en_locale_and_fast_tempo():
    foundation = {"spine": {"best_mode": "steady maintenance today"}}
    out = build_day_model_v0(
        foundation=foundation,
        ritual={"mood": "calm"},
        fusion_scores={"energy": 80},
        intent_slice=None,
        internal_profile=None,
        locale="en",
    )
    assert out["locale_hint"] == "en"
    assert out["scales"]["tempo"] == "fast"
    assert out["scales"]["direction"] == "stabilization"


def test_build_day_model_v0_drops_garbage_first_move_for_one_focus():
    foundation = {
        "spine": {
            "day_axis": "Короткая ось дня без воды",
            "first_move": "смысл и коммуникация",
        }
    }
    out = build_day_model_v0(
        foundation=foundation,
        ritual=None,
        fusion_scores={"energy": 50},
        intent_slice=None,
        internal_profile=None,
        locale="ru",
    )
    assert "смысл" not in (out["strategy"].get("one_focus") or "").lower()
    assert "коммуникац" not in (out["strategy"].get("one_focus") or "").lower()


def test_build_day_model_v0_pattern_hint_in_risk():
    internal = {
        "contract_version": "internal_profile_slice_v0",
        "surface_behavior_aggregates": {
            "pattern_hints": ["Часто бросаешь на полпути."],
        },
    }
    out = build_day_model_v0(
        foundation=None,
        ritual=None,
        fusion_scores={},
        intent_slice=None,
        internal_profile=internal,
        locale="ru",
    )
    assert "полпути" in out["risk"]["summary"] or "Часто" in out["risk"]["summary"]


def test_build_day_model_v0_temporal_from_history():
    history = {
        "contract_version": "day_history_v0",
        "yesterday": {
            "date": "2026-05-09",
            "meaning_active": True,
            "meaning_completions_total": 2,
            "day_flow": {"evening_completed": True},
        },
        "fusion_score_delta_vs_yesterday": {"energy": 6, "emotional_balance": 0, "focus": 0},
        "fusion_score_delta_trustworthy": True,
        "trailing_7d_summary_trustworthy": True,
        "fusion_scores_trailing_7d": [
            {"date": "2026-05-09", "scores": {"energy": 60, "emotional_balance": 50, "focus": 50}},
            {"date": "2026-05-08", "scores": {"energy": 58, "emotional_balance": 50, "focus": 50}},
            {"date": "2026-05-07", "scores": {"energy": 57, "emotional_balance": 50, "focus": 50}},
            {"date": "2026-05-06", "scores": {"energy": 45, "emotional_balance": 50, "focus": 50}},
            {"date": "2026-05-05", "scores": {"energy": 44, "emotional_balance": 50, "focus": 50}},
            {"date": "2026-05-04", "scores": {"energy": 43, "emotional_balance": 50, "focus": 50}},
            {"date": "2026-05-03", "scores": {"energy": 42, "emotional_balance": 50, "focus": 50}},
        ],
    }
    out = build_day_model_v0(
        foundation={"spine": {"day_axis": "Один шаг"}},
        ritual=None,
        fusion_scores={"energy": 66},
        intent_slice=None,
        internal_profile=None,
        locale="ru",
        history_slice=history,
    )
    temporal = out.get("temporal")
    assert isinstance(temporal, dict)
    assert temporal.get("delta_trustworthy") is True
    assert temporal.get("energy_delta_vs_yesterday") == 6
    assert temporal.get("week_energy_trend") == "rising"
    assert temporal.get("yesterday_meaning_active") is True
    assert "Flow" in (temporal.get("summary") or "")

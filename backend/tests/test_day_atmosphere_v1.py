"""Tests for day_atmosphere_v1 deterministic mapper."""

from todayflow_backend.services.day_atmosphere_v1 import (
    DECOR_VARIANTS,
    VISUAL_MODES,
    build_day_atmosphere_v1,
    day_atmosphere_from_story,
    map_thesis_mode_to_visual,
    time_phase_from_hour,
)


def test_time_phase_from_hour_buckets():
    assert time_phase_from_hour(7) == "morning"
    assert time_phase_from_hour(13) == "day"
    assert time_phase_from_hour(19) == "evening"
    assert time_phase_from_hour(23) == "night"
    assert time_phase_from_hour(None) == "day"


def test_map_thesis_modes_closed():
    assert map_thesis_mode_to_visual("stability") == "grounded"
    assert map_thesis_mode_to_visual("recovery") == "renewal"
    assert map_thesis_mode_to_visual("opportunity") == "radiance"
    assert map_thesis_mode_to_visual("transition") == "flow"
    assert map_thesis_mode_to_visual("conflict") == "tension"
    assert map_thesis_mode_to_visual("pressure") == "tension"
    assert map_thesis_mode_to_visual("change") == "momentum"
    assert map_thesis_mode_to_visual("garbage") == "clarity"
    assert map_thesis_mode_to_visual(None) == "clarity"


def test_night_soft_path_to_depth():
    assert map_thesis_mode_to_visual("stability", time_phase="night") == "depth"
    assert map_thesis_mode_to_visual("recovery", time_phase="evening") == "depth"
    assert map_thesis_mode_to_visual("conflict", time_phase="night") == "tension"


def test_build_day_atmosphere_closed_fields():
    nest = build_day_atmosphere_v1(
        day_thesis={"mode": "conflict"},
        local_date="2026-08-03",
        hour=14,
    )
    assert nest["visual_mode"] in VISUAL_MODES
    assert nest["visual_mode"] == "tension"
    assert 0.0 <= nest["intensity"] <= 1.0
    assert 0.0 <= nest["warmth"] <= 1.0
    assert nest["motion"] in ("none", "low")
    assert nest["contrast"] in ("soft", "medium", "strong")
    assert nest["time_phase"] == "day"
    assert nest["decor_variant"] in DECOR_VARIANTS["tension"]


def test_decor_variant_stable_for_same_seed():
    a = build_day_atmosphere_v1(day_thesis={"mode": "flow"}, local_date="2026-08-03", hour=12)
    b = build_day_atmosphere_v1(day_thesis={"mode": "flow"}, local_date="2026-08-03", hour=12)
    assert a["decor_variant"] == b["decor_variant"]


def test_from_story_unavailable_returns_none():
    assert (
        day_atmosphere_from_story(
            {"interpretation_status": "unavailable", "day_thesis": {"mode": "conflict"}}
        )
        is None
    )


def test_from_story_with_thesis():
    nest = day_atmosphere_from_story(
        {"interpretation_status": "ok", "day_thesis": {"mode": "opportunity"}},
        local_date="2026-08-03",
        hour=10,
    )
    assert nest is not None
    assert nest["visual_mode"] == "radiance"
    assert nest["time_phase"] == "morning"


def test_day_story_to_today_contract_includes_atmosphere():
    from todayflow_backend.services.day_story_v1 import day_story_to_today_contract_v1

    story = {
        "interpretation_status": "ok",
        "theme": "Тема",
        "direction": "Направление дня с достаточным текстом",
        "story": "История дня с достаточным текстом для контракта.",
        "expect": "Ожидание с достаточным текстом",
        "trap": "Ловушка с достаточным текстом",
        "do": ["Сделать одно конкретное дело"],
        "avoid": ["Избежать одной конкретной ловушки"],
        "advantage": "Опора с достаточным текстом",
        "abstain": "Пауза с достаточным текстом",
        "today_move": "Ход дня с достаточным текстом",
        "global_period": "Период с достаточным текстом",
        "development_point": "Точка роста с достаточным текстом",
        "primary_action": "Действие с достаточным текстом",
        "day_thesis": {"mode": "transition", "label_ru": "Переход"},
        "domains": {
            "work": {
                "status": "статус работы достаточно длинный",
                "opportunity": "возможность работы достаточно длинная",
                "risk": "риск работы достаточно длинный",
                "action": "действие работы достаточно длинное",
            },
            "money": {
                "status": "статус денег достаточно длинный",
                "opportunity": "возможность денег достаточно длинная",
                "risk": "риск денег достаточно длинный",
                "action": "действие денег достаточно длинное",
            },
            "relationships": {
                "status": "статус отношений достаточно длинный",
                "opportunity": "возможность отношений достаточно длинная",
                "risk": "риск отношений достаточно длинный",
                "action": "действие отношений достаточно длинное",
            },
            "energy": {
                "status": "статус энергии достаточно длинный",
                "opportunity": "возможность энергии достаточно длинная",
                "risk": "риск энергии достаточно длинный",
                "action": "действие энергии достаточно длинное",
            },
        },
        "trace": {"domains_present": ["work", "money", "relationships", "energy"]},
    }
    contract = day_story_to_today_contract_v1(story, generation_id="test-gen")
    atm = contract.get("day_atmosphere")
    assert isinstance(atm, dict)
    assert atm["visual_mode"] == "flow"

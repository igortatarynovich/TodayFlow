from todayflow_backend.services.day_logic_shared_v0 import (
    clip_day_logic_text,
    foundation_spine_dict,
    fusion_energy_score_int,
    ritual_core_fields,
    spine_text_fields,
)


def test_clip_day_logic_text_truncates_with_ellipsis():
    # max_len includes the ellipsis character (same as legacy _clip in brief/model).
    assert clip_day_logic_text("abcd", 3) == "ab…"


def test_foundation_spine_dict_none_and_non_dict_spine():
    assert foundation_spine_dict(None) == {}
    assert foundation_spine_dict({"spine": "x"}) == {}
    assert foundation_spine_dict({"spine": {"day_axis": "A"}}) == {"day_axis": "A"}


def test_spine_text_fields_prefers_day_axis_over_best_mode():
    s = spine_text_fields({"day_axis": "X", "best_mode": "Y", "first_move": "m", "main_risk": "r", "do_not_enter": "d"})
    assert s["axis"] == "X"
    assert s["best_mode"] == "Y"


def test_fusion_energy_score_int_invalid_falls_back():
    assert fusion_energy_score_int(None) == 50
    assert fusion_energy_score_int({"energy": "x"}) == 50
    assert fusion_energy_score_int({"energy": 42}) == 42


def test_ritual_core_fields_normalizes():
    rc = ritual_core_fields({"tarot_name_ru": "  Star ", "numerology_value": 7, "mood": "ok"})
    assert rc["tarot_name_ru"] == "Star"
    assert rc["numerology_value"] == "7"

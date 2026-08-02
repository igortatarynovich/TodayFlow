"""number_base_v1 wired into numerology_explainer (prompt + fallback + alignment)."""

from __future__ import annotations

from todayflow_backend.core import numerology_explainer as explainer
from todayflow_backend.data import number_base_v1


def test_number_base_required_and_no_bogus_20():
    assert number_base_v1.validate_number_base_v1() == []
    assert number_base_v1.get_number_base(20) is None
    assert number_base_v1.get_number_base(7)
    assert number_base_v1.get_number_base(33)
    assert number_base_v1.get_number_base(13)
    row44 = number_base_v1.get_number_base(44)
    assert row44 and row44.get("in_use") is False


def test_format_base_prompt_block_includes_archetype():
    block = number_base_v1.format_base_prompt_block(7)
    assert block
    assert "Базовое значение числа" in block
    assert "Искатель" in block
    assert "наблюден" in block.lower() or "пауз" in block.lower()


def test_meaning_alignment_rejects_unrelated():
    assert number_base_v1.meaning_aligned_with_base(
        "Семёрка — пауза и глубина через наблюдение.", 7
    )
    assert not number_base_v1.meaning_aligned_with_base(
        "Число подчёркивает тему выбора, структуры и внимания.", 7
    )


def test_fallback_uses_number_base_not_generic():
    out = explainer._fallback_numerology_explanation(7, "day", {})
    assert out.get("meaning_source") == "number_base_v1"
    assert out["meaning"] == number_base_v1.get_number_base(7)["base_meaning"]
    assert "Искатель" in out["what_to_do"] or "наблюден" in out["meaning"].lower()
    # Must not be the old same-for-all template
    assert "подчеркивает тему выбора, структуры" not in out["meaning"]


def test_fallback_honest_when_unknown_value():
    out = explainer._fallback_numerology_explanation(20, "day", {})
    assert out.get("meaning_source") == "unavailable"
    assert out.get("meaning") == ""
    assert out.get("is_fallback") is True


def test_validator_rejects_unrelated_llm_meaning():
    ok = {
        "meaning": "Семёрка просит паузу и наблюдение, не давление.",
        "what_to_do": "Возьми один тихий час на разбор задачи без спешки сегодня.",
        "what_to_avoid": "Не дави на ответ и не заполняй паузу лишними действиями.",
        "possible_events": "Может всплыть разговор, где важнее слушать, чем убеждать сразу.",
        "how_day_looks": "День спокойнее, когда ты не торопишь вывод и даёшь себе время.",
        "why_this_number": "Число дня держит тему глубины и честного взгляда внутрь ситуации.",
    }
    assert explainer._is_valid_numerology_explanation(ok, 7)

    bad = dict(ok)
    bad["meaning"] = "Число подчёркивает тему выбора, структуры и того, как ты распоряжаешься вниманием."
    assert not explainer._is_valid_numerology_explanation(bad, 7)


def test_apply_base_meaning_overwrites():
    forced = explainer._apply_base_meaning({"meaning": "выдумка модели"}, 1)
    assert forced["meaning"] == number_base_v1.get_number_base(1)["base_meaning"]
    assert forced["meaning_source"] == "number_base_v1"

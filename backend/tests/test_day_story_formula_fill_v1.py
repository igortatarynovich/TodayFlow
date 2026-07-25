"""Editorial formula fill — empty/invalid only, never hard-overwrite good LLM prose."""

from __future__ import annotations

from todayflow_backend.services.day_story_v1 import _fill_editorial_formula_slots


def _base_thesis() -> dict:
    return {
        "family": "communication",
        "variant": "truth_without_filter",
        "mode": "conflict",
        "label_ru": "Прямота без фильтра",
        "driver_ids": ["merc-hard"],
        "composition_ids": [],
    }


def test_fill_preserves_good_llm_expect_and_trap():
    llm_expect = "На работе проще назвать проблему вслух, чем сгладить её до пустоты."
    llm_trap = "После резкого сообщения не отправляй второе «для ясности» в ту же минуту."
    story = {
        "day_thesis": _base_thesis(),
        "primary_conflict": "Прямота без фильтра",
        "expect": llm_expect,
        "trap": llm_trap,
        "abstain": llm_trap,
        "do": ["Скажи одно точное предложение и поставь точку."],
        "avoid": ["Не продолжай разбор полётов при свидетелях."],
        "today_move": "Скажи одно точное предложение и поставь точку.",
        "vibe_closing": "Короткий глаз в глаз; пауза после правды.",
    }
    out = _fill_editorial_formula_slots(story)
    assert out["expect"] == llm_expect
    assert out["trap"] == llm_trap
    assert out["do"][0].startswith("Скажи одно точное")
    assert out.get("editorial", {}).get("fill_mode") == "empty_or_invalid"
    assert "expect" not in (out.get("editorial") or {}).get("filled_slots", [])


def test_fill_replaces_empty_and_system_leak_slots():
    story = {
        "day_thesis": _base_thesis(),
        "primary_conflict": "Прямота без фильтра",
        "expect": "",
        "trap": "При твоём стиле («вы решаете…») «Двойка пентаклей» легко скатывается…",
        "do": [],
        "avoid": ["довериться потоку"],
        "today_move": "",
        "vibe_closing": "",
    }
    out = _fill_editorial_formula_slots(story)
    assert out["expect"]
    assert "при твоём стиле" not in out["trap"].lower().replace("ё", "е")
    assert len(out["do"]) >= 1
    assert len(out["avoid"]) >= 1
    filled = out.get("editorial", {}).get("filled_slots") or []
    assert "expect" in filled
    assert "trap" in filled

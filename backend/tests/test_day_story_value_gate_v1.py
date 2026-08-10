"""Tests for day_story value gate — hide system leaks and claim dumps."""

from __future__ import annotations

from todayflow_backend.services.day_story_value_gate_v1 import (
    apply_day_story_value_gate,
    day_story_passes_value_gate,
    find_value_gate_hits,
    scrub_user_facing_text,
)


def test_scrubs_system_leak_living_fluff():
    text = "Слой быстрых решений пока собран слабо. Чаще всего сейчас всплывает тема `focus`."
    assert find_value_gate_hits(text)
    assert scrub_user_facing_text(text) is None


def test_scrubs_truncated_style_trap():
    text = (
        "Осторожнее с темой «общий фон дня», если она начинает проживаться как хаос… "
        "При твоём стиле («вы решаете…») «Двойка пентаклей» легко скатывается…"
    )
    assert scrub_user_facing_text(text) is None


def test_scrubs_address_mix():
    text = "Ты сегодня яснее обычного: вам стоит сказать правду коротко."
    assert "address_mix_ty_vy" in find_value_gate_hits(text)


def test_allows_concrete_trap():
    text = (
        "После резкого сообщения захочется сразу отправить ещё одно, "
        "чтобы окончательно объяснить свою позицию."
    )
    assert scrub_user_facing_text(text) == text


def test_apply_clears_story_soup():
    story = {
        "day_thesis": {"label_ru": "Прямота без фильтра", "family": "communication", "variant": "truth_without_filter"},
        "primary_conflict": "Прямота без фильтра",
        "events_lead": "Меркурий в остром аспекте задаёт прямой тон разговорам.",
        "expect": "Короткий разговор внезапно станет серьёзным.",
        "trap": "После резкого сообщения захочется отправить ещё одно.",
        "story": (
            "Прямота без фильтра. Короткий разговор внезапно станет серьёзным. "
            "После резкого сообщения захочется отправить ещё одно. Сформулируй правду."
        ),
        "do": ["Сформулируй правду в одном предложении."],
        "avoid": ["Не отправляй второе эмоциональное сообщение."],
        "today_move": "Сформулируй правду в одном предложении.",
        "vibe_closing": "Честный глаз в глаз; пауза после правды.",
    }
    out = apply_day_story_value_gate(story)
    # Soup cleared; events_lead becomes the prose bridge.
    assert out.get("story") == out.get("events_lead")
    assert out["expect"]
    assert out["trap"]
    assert out["events_lead"]
    ok, hits = day_story_passes_value_gate(out)
    assert ok, hits


def test_textbook_house_hidden_for_profile():
    text = "Первый дом отвечает за первое впечатление и то, как вы входите в мир."
    assert scrub_user_facing_text(text) is None
    assert scrub_user_facing_text(text, allow_textbook=True) is not None


def test_scrubs_kitchen_tension_and_element_focus_catalog():
    assert find_value_gate_hits("Источники в основном согласованы.")
    assert scrub_user_facing_text("Источники в основном согласованы.") is None
    assert scrub_user_facing_text("Мышление и ясные формулировки") is None
    assert scrub_user_facing_text("Инициатива и действие") is None
    assert scrub_user_facing_text("Структура и устойчивость") is None
    assert scrub_user_facing_text("Эмпатия и внутренняя глубина") is None


def test_scrubs_profection_progression_solar_return_dump():
    dump = (
        "Создаёт напряжение, которое просит осознанного выбора — не автоматической реакции. "
        "Ещё активных личных транзитов: 2. Профекция года (возраст 36): 1-й дом, знак Водолей, "
        "управитель Сатурн — тело, самопрезентация. База — солнечный знак (нет времени/места для ASC). "
        "Секундарные прогрессии (день=год): прогресс. Солнце Овен 1.1°, Луна Козерог 28.6° "
        "(возраст 36.49 лет → дата 1990-03-21). Solar return 2026: карт…"
    )
    assert "kitchen_mechanism" in find_value_gate_hits(dump)
    assert scrub_user_facing_text(dump) is None

    story = {
        "expect": "Утром тело подаёт первые сигналы.",
        "trap": "Тянет компенсировать вторым кофе.",
        "do": ["Короткая телесная проверка."],
        "avoid": ["Не будить себя стимулом."],
        "day_personal": {"summary_ru": dump},
        "events_lead": "Луна в серпе просит меньше входящего.",
        "day_scenario": {
            "conflict": {
                "why_arose": "Луна — старый серп. Китайский управитель дня — вода.",
            }
        },
    }
    out = apply_day_story_value_gate(story)
    assert out["day_personal"]["summary_ru"] == ""
    assert out["day_scenario"]["conflict"]["why_arose"] == ""
    assert out["events_lead"]
    ok, hits = day_story_passes_value_gate(out)
    assert ok, hits


def test_scrubs_nested_personal_astrology_summary():
    dump = "Профекция года (возраст 36): управитель Сатурн. Solar return 2026."
    out = apply_day_story_value_gate(
        {
            "expect": "Утром тело подаёт первые сигналы.",
            "trap": "Тянет компенсировать вторым кофе.",
            "do": ["Короткая телесная проверка."],
            "day_personal": {
                "summary_ru": "",
                "personal_astrology": {"summary_ru": dump},
            },
        }
    )
    assert out["day_personal"]["personal_astrology"]["summary_ru"] == ""


def test_allows_soft_sky_meaning_without_mechanism():
    text = "Луна в серпе гасит лишний шум — день просит меньше входящего."
    assert scrub_user_facing_text(text) == text

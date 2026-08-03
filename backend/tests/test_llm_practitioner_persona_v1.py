"""Practitioner persona — Voice Canon §1 hard rule."""

from __future__ import annotations

from todayflow_backend.services.llm_practitioner_persona_v1 import (
    PERSONA_VERSION,
    practitioner_persona_system_addon,
    with_practitioner_persona,
)


def test_persona_lists_pro_crafts_and_friendly_informal() -> None:
    text = practitioner_persona_system_addon(locale="ru")
    assert PERSONA_VERSION == "llm_practitioner_persona_v1.2"
    assert PERSONA_VERSION in text
    low = text.lower()
    for craft in ("таролог", "нумеролог", "астролог", "друг"):
        assert craft in low or craft in text
    assert "профессиональн" in low
    assert "дружелюбн" in low
    assert "неформальн" in low
    assert "метафор" in low


def test_with_practitioner_persona_prefixes_once() -> None:
    base = "Ты пишешь JSON."
    once = with_practitioner_persona(base, locale="ru")
    twice = with_practitioner_persona(once, locale="ru")
    assert once.count("Practitioner voice") == 1
    assert twice == once
    assert once.endswith(base)
    assert "таролог" in once
    assert "друг" in once
    assert "неформальн" in once.lower()


def test_en_persona_lists_crafts() -> None:
    text = practitioner_persona_system_addon(locale="en")
    low = text.lower()
    for craft in ("tarot", "numerologist", "astrologer", "friend"):
        assert craft in low
    assert "professional" in low
    assert "informal" in low
    assert "friendly" in low

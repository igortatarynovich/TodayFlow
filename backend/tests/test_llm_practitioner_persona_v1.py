"""Practitioner persona — Voice Canon §1 hard rule."""

from __future__ import annotations

from todayflow_backend.services.llm_practitioner_persona_v1 import (
    PERSONA_VERSION,
    practitioner_persona_system_addon,
    with_practitioner_persona,
)


def test_persona_lists_all_crafts_and_friend() -> None:
    text = practitioner_persona_system_addon(locale="ru")
    assert PERSONA_VERSION in text
    for craft in ("таролог", "нумеролог", "астролог", "психолог", "сексолог", "друг"):
        assert craft in text.lower() or craft in text


def test_with_practitioner_persona_prefixes_once() -> None:
    base = "Ты пишешь JSON."
    once = with_practitioner_persona(base, locale="ru")
    twice = with_practitioner_persona(once, locale="ru")
    assert once.count("Practitioner voice") == 1
    assert twice == once
    assert once.endswith(base)
    assert "таролог" in once
    assert "сексолог" in once
    assert "друг" in once


def test_en_persona_lists_crafts() -> None:
    text = practitioner_persona_system_addon(locale="en")
    for craft in ("tarot", "numerologist", "astrologer", "psychologist", "sexologist", "friend"):
        assert craft in text.lower()

"""Practitioner persona prefix for LLM system prompts."""

from __future__ import annotations

from todayflow_backend.services.llm_practitioner_persona_v1 import (
    PERSONA_VERSION,
    with_practitioner_persona,
)


def test_persona_prefix_idempotent():
    base = "Ты пишешь JSON."
    once = with_practitioner_persona(base, locale="ru")
    twice = with_practitioner_persona(once, locale="ru")
    assert PERSONA_VERSION in once
    assert once.count(PERSONA_VERSION) == 1
    assert twice == once
    assert "таролог" in once.lower() or "тарол" in once.lower()
    assert "друг" in once.lower()


def test_persona_en():
    out = with_practitioner_persona("Return JSON only.", locale="en")
    assert PERSONA_VERSION in out
    assert "tarot" in out.lower()
    assert "friend" in out.lower()

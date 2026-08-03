"""Boundary-aware _clip for native voice fields (no mid-word ellipsis)."""

from __future__ import annotations

from todayflow_backend.services.day_scenario_native_llm_c1 import (
    _clip,
    normalize_native_scenario_llm_c1,
)


def test_clip_prefers_sentence_boundary() -> None:
    text = (
        "Первое законченное предложение про день. "
        "Второе тоже полное и довольно длинное продолжение мысли без обрыва."
    )
    out = _clip(text, 80)
    assert out.endswith(".")
    assert "…" not in out
    assert "предложени…" not in out
    assert out.startswith("Первое")


def test_clip_falls_back_to_word_boundary() -> None:
    # No sentence end inside budget — must not cut mid-word.
    text = "даёт разрешение его спокойно завершить накопленного опыта вместе"
    out = _clip(text, 40)
    assert "…" in out
    assert not out.rstrip("…").endswith(("ег", "вз", "завершит"))
    assert " " in out.rstrip("…") or len(out.rstrip("…")) < 40


def test_hook_heal_midword_ellipsis_stump() -> None:
    from todayflow_backend.services.hook_reveal_v1 import _bridge_from_voice
    from todayflow_backend.services.prose_clip_v1 import heal_ellipsis_midword

    broken = (
        "Карта не цепляется за сценарий, который уже отыгран, и даёт разрешение ег…"
    )
    assert heal_ellipsis_midword(broken).endswith("разрешение…")
    assert "ег…" not in heal_ellipsis_midword(broken)
    bridge = _bridge_from_voice({"link_to_conflict": broken, "human_meaning": ""})
    assert bridge.endswith("разрешение…")


def test_clip_short_unchanged() -> None:
    assert _clip("короткий текст", 240) == "короткий текст"


def test_voice_normalize_keeps_long_link_without_midword() -> None:
    link = (
        "Карта даёт разрешение его спокойно завершить через накопленный опыт, "
        "не торопя исход и не притворяясь, что всё уже решено заранее в пользу спешки. "
        "Именно поэтому сегодня важно не давить на финал, а удержать ясный темп и "
        "закончить один конкретный разговор без лишней драмы вокруг статуса."
    )
    assert len(link) > 240
    raw = {
        "schema_version": "day_scenario_native_llm_c1",
        "conflict": {"title": "Спешка или пауза"},
        "scenes": [],
        "interpretive_chorus": {
            "day_card": {
                "named_factor": "Отшельник",
                "human_meaning": link,
                "link_to_conflict": link,
                "archetype_role": "наблюдатель",
            }
        },
        "prop_material": {},
    }
    norm = normalize_native_scenario_llm_c1(raw)
    card = norm["interpretive_chorus"]["day_card"]
    assert "ег…" not in card["link_to_conflict"]
    assert "вз…" not in card["link_to_conflict"]
    assert len(card["link_to_conflict"]) <= 420
    assert len(card["human_meaning"]) <= 450
    # Most of the thought survives the old 240 ceiling.
    assert len(card["link_to_conflict"]) > 240
    assert card["link_to_conflict"].endswith((".", "…"))

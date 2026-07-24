"""Unit tests for Life Path co-voice visibility detector (no LLM)."""

from todayflow_backend.services.life_path_visibility_v0 import (
    detect_life_path_visibility,
    field_visible_for_life_path,
    themes_shift,
)


def test_lp9_completion_visible_and_distinct_from_lp6():
    text = "Дар завершать циклы и находить мудрость в прощании, чтобы освобождать место для нового."
    ok, detail = field_visible_for_life_path(text, 9)
    assert ok, detail
    assert "заверш" in " ".join(detail["claimed_stems"]) or "цикл" in " ".join(detail["claimed_stems"])


def test_lp9_compassion_in_action_visible():
    text = "Превращает сочувствие в поступки и умеет закрывать циклы."
    ok, detail = field_visible_for_life_path(text, 9)
    assert ok, detail


def test_lp6_care_not_counted_as_lp9():
    text = "Тянет на себя чужие проблемы и трудно сказать «не моя забота»."
    ok9, _ = field_visible_for_life_path(text, 9)
    ok6, detail6 = field_visible_for_life_path(text, 6)
    assert not ok9
    assert ok6, detail6


def test_detect_identity_payload_lp1():
    payload = {
        "recognition_line": "Ты идёшь своим путём.",
        "identity_core": "…",
        "strengths": ["Врождённое стремление к независимости и цельности."],
        "growth_zones": ["Ждёшь разрешения, вместо того чтобы начинать первым."],
    }
    det = detect_life_path_visibility(payload, 1)
    assert det["visible"] is True
    assert det["visible_fields"]


def test_themes_shift_between_lp9_and_lp1():
    a = {
        "recognition_line": "Чувствуешь вибрации.",
        "strengths": ["Дар завершать циклы и отпускать прошлое."],
        "growth_zones": ["Растворяешься в чужих переживаниях."],
    }
    c = {
        "recognition_line": "Чувствуешь вибрации.",
        "strengths": ["Стремление к независимости и быть первым."],
        "growth_zones": ["Ждёшь разрешения вместо действия."],
    }
    assert themes_shift(a, c, fields=("recognition_line", "strengths", "growth_zones"))

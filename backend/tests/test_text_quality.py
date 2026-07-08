"""Tests for text quality utilities and forecast quality gate."""

from todayflow_backend.core.text_quality import (
    contains_dead_pattern,
    has_action_verb,
    is_meaningful_sentence,
)
from todayflow_backend.data.quality_gate import validate_daily_forecast


def test_text_quality_rejects_dead_pattern() -> None:
    ok, reason = is_meaningful_sentence("Сделай паузу перед ответом в рабочем диалоге", min_words=4)
    assert ok is True
    assert reason is None
    ok_bad, reason_bad = is_meaningful_sentence("Сделай паузу и все будет хорошо", min_words=4)
    assert ok_bad is False
    assert reason_bad is not None
    assert contains_dead_pattern("Слушай себя и действуй осознанно") is True


def test_text_quality_accepts_contextual_focus_phrases() -> None:
    ok, reason = is_meaningful_sentence(
        "Сегодня держи один приоритет и не распыляйся на срочное вместо важного.",
        min_words=5,
    )
    assert ok is True
    assert reason is None
    ok_noise, _ = is_meaningful_sentence(
        "Отсечь лишний шум поможет короткий список из трёх задач на сегодня.",
        min_words=5,
    )
    assert ok_noise is True
    ok_rhythm, _ = is_meaningful_sentence(
        "На совещании держать ритм проще, если заранее назвать одну цель встречи.",
        min_words=5,
    )
    assert ok_rhythm is True


def test_text_quality_accepts_meaningful_sentence() -> None:
    ok, reason = is_meaningful_sentence(
        "Сформулируй один результат до обеда и убери задачу, которая не ведет к нему.",
        min_words=5,
    )
    assert ok is True
    assert reason is None
    assert has_action_verb("Запиши приоритет и закрой первый шаг за 20 минут.") is True


def _valid_forecast_payload() -> dict:
    return {
        "blocks": {
            "theme": "День требует ясного приоритета и управляемого ритма без хаотичных переключений.",
            "notice": [
                "Проверь, какие обязательства реально двигают цель, а какие создают только шум.",
                "Фиксируй договоренности письменно, чтобы сохранить фокус и ресурс.",
            ],
            "scene": [
                "В работе важен короткий цикл: задача, срок, проверка результата в конце блока.",
                "В общении с близкими сработает прямой разговор о границах и ожиданиях на день.",
            ],
            "micro_action": "Запиши главный результат дня и поставь таймер на первый фокус-блок.",
        },
        "markers": {
            "body": ["grounding"],
            "social": ["boundaries"],
            "domestic": ["routine"],
            "micro_action": ["timer"],
        },
        "tags": ["work"],
    }


def test_quality_gate_rejects_dead_micro_action() -> None:
    payload = _valid_forecast_payload()
    payload["blocks"]["micro_action"] = "Слушай себя."

    result = validate_daily_forecast(
        payload,
        body_markers={"grounding"},
        social_markers={"boundaries"},
        domestic_markers={"routine"},
        micro_action_markers={"timer"},
        banned_words=[],
        tags_allow_list=["work"],
    )
    assert result.ok is False
    assert any("micro_action" in err for err in result.errors)


def test_quality_gate_rejects_duplicate_lines() -> None:
    payload = _valid_forecast_payload()
    payload["blocks"]["scene"][1] = payload["blocks"]["scene"][0]

    result = validate_daily_forecast(
        payload,
        body_markers={"grounding"},
        social_markers={"boundaries"},
        domestic_markers={"routine"},
        micro_action_markers={"timer"},
        banned_words=[],
        tags_allow_list=["work"],
    )
    assert result.ok is False
    assert any("дублирование" in err for err in result.errors)


def test_narrative_surface_ru_gates_reject_banned_phrases() -> None:
    from todayflow_backend.services.today_narrative import (
        _day_layer_payload_concrete,
        _deepen_payload_concrete,
        _evening_payload_concrete,
    )

    day_ok = {
        "nudge_message": "Короткий шаг и фиксация",
        "personal_insight_title": "Один приоритет",
        "personal_insight_body": "Сегодня лучше закрыть одну линию, чем распылиться.",
        "question_of_day_prompt": "Где сейчас твой реальный ресурс?",
        "mini_decision_caption": "Лишний импульс — ответить всем сразу.",
        "personal_insight_chips": ["пауза", "граница"],
    }
    assert _day_layer_payload_concrete("ru", day_ok) is True
    day_bad = {**day_ok, "nudge_message": "Смысл и коммуникация сегодня главное"}
    assert _day_layer_payload_concrete("ru", day_bad) is False
    assert _day_layer_payload_concrete("en-US", day_bad) is True

    day_bad_title_rubric = {**day_ok, "personal_insight_title": "Картина дня"}
    assert _day_layer_payload_concrete("ru", day_bad_title_rubric) is False
    day_bad_title_short = {**day_ok, "personal_insight_title": "Коротко"}
    assert _day_layer_payload_concrete("ru", day_bad_title_short) is False

    ev_ok = {
        "panel_intro": "День можно закрыть спокойно",
        "outlook_preamble": "Отметь одно, что получилось",
        "closure_invitation": "Запиши строку для себя",
    }
    assert _evening_payload_concrete("ru", ev_ok) is True
    ev_bad = {**ev_ok, "panel_intro": "Тон близости и ресурс отношений"}
    assert _evening_payload_concrete("ru", ev_bad) is False

    dp_ok = {
        "title": "Линия дня",
        "body": "Пара абзацев про конкретный шаг без штампов.",
        "closing_line": "Завтра продолжим с тем же темпом.",
        "bullets": ["один пункт", "второй"],
    }
    assert _deepen_payload_concrete("ru", dp_ok) is True
    dp_bad = {**dp_ok, "title": "Пространство и контакт"}
    assert _deepen_payload_concrete("ru", dp_bad) is False


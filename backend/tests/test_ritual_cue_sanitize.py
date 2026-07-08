from todayflow_backend.services.ritual_cue_sanitize import (
    is_garbage_ritual_action_cue,
    is_ru_abstract_topic_headline,
    repair_ritual_do_not_enter_line,
    replace_quoted_en_slugs_for_ru_display,
    sanitize_daily_horoscope_payload,
    sanitize_daily_recommendations_payload,
    strip_llm_meta_commentary,
    strip_meta_from_guide_payload,
)


def test_repair_do_not_enter_quoted_general():
    raw = "Не заходить в линию 'general', если она начинает проживаться как хаос."
    out = repair_ritual_do_not_enter_line(raw)
    assert "general" not in out.lower()
    assert "хаос" in out.lower()


def test_o5_replace_quoted_mood_and_topic():
    assert "tired" not in replace_quoted_en_slugs_for_ru_display("Настроение «tired» — мягче темп.").lower()
    assert "устало" in replace_quoted_en_slugs_for_ru_display("Настроение «tired» — мягче темп.").lower()
    assert "general" not in replace_quoted_en_slugs_for_ru_display('Тема "general" важна.').lower()
    assert "общий фон дня" in replace_quoted_en_slugs_for_ru_display('Тема "general" важна.').lower()


def test_is_garbage_topic_not_action():
    assert is_garbage_ritual_action_cue("Смысл и коммуникация") is True
    assert is_garbage_ritual_action_cue("До обеда выбрать одну задачу и назвать её вслух") is False


def test_is_ru_abstract_topic_headline_o3():
    assert is_ru_abstract_topic_headline("  Смысл дня ") is True
    assert is_ru_abstract_topic_headline("Один шаг до обеда") is False


def test_sanitize_horoscope_spine_and_scenarios():
    payload = {
        "spine": {
            "first_move": "смысл и коммуникация",
            "do_not_enter": "Не заходить в линию 'general', если хаос.",
        },
        "scenarios": [{"slug": "love", "title": "", "summary": "x", "focus": "y"}],
    }
    out = sanitize_daily_horoscope_payload(payload)
    assert out["spine"]["first_move"] == ""
    assert "general" not in out["spine"]["do_not_enter"].lower()
    assert "хаос" in out["spine"]["do_not_enter"].lower()
    assert out["scenarios"][0]["title"] == "любовь и близость"


def test_sanitize_horoscope_spine_o5_quoted_mood_in_day_axis():
    payload = {
        "spine": {
            "day_axis": "С учётом настроения 'tired' держи темп ровнее.",
            "do_not_enter": "Без резких скачков.",
        }
    }
    out = sanitize_daily_horoscope_payload(payload)
    assert "tired" not in out["spine"]["day_axis"].lower()
    assert "устало" in out["spine"]["day_axis"].lower()


def test_sanitize_recommendations_drops_garbage_what_to_do():
    rec = {"what_to_do": "dialogue", "what_to_avoid": "спешка", "key_focus": "general"}
    out = sanitize_daily_recommendations_payload(rec)
    assert out["what_to_do"] == ""
    assert out["what_to_avoid"] == "спешка"


def test_strip_llm_meta_commentary_removes_meta_sentence():
    raw = (
        "Коротко: держи один фокус. Карта и число остаются в сводке — я не дублирую их большими блоками. "
        "Дальше — один шаг без распыления."
    )
    out = strip_llm_meta_commentary(raw)
    assert "не дублиру" not in out.lower()
    assert "карта и число остаются" not in out.lower()
    assert "один шаг" in out.lower()


def test_strip_llm_meta_commentary_o10_extra_patterns():
    raw = (
        "Сегодня мягкий темп. Как просили в промпте, не повторяю блок про карту. "
        "Сделай одну паузу перед ответом."
    )
    out = strip_llm_meta_commentary(raw)
    assert "промпт" not in out.lower()
    assert "не повторяю блок" not in out.lower()
    assert "паузу" in out.lower()


def test_strip_meta_from_guide_payload_pattern_insight():
    p = strip_meta_from_guide_payload(
        {
            "headline": "День спокойного шага",
            "pattern_insight": "Смысл ясен. Чтобы экран не перегружать, не повторяю карту.",
            "do_items": ["Сделай одно", "Отметь в Flow"],
        }
    )
    assert p["headline"] == "День спокойного шага"
    assert p.get("pattern_insight") == "Смысл ясен."
    assert p["do_items"][0] == "Сделай одно"


def test_strip_meta_from_guide_payload_core_message_extra_keys():
    p = strip_meta_from_guide_payload(
        {
            "core_message": {
                "body": "Опора дня ясна.",
                "main_text": "To avoid duplication, I skip the long chart paragraph. Дыши ровнее.",
            }
        }
    )
    cm = p["core_message"]
    assert isinstance(cm, dict)
    assert "avoid duplication" not in str(cm["main_text"]).lower()
    assert "дыш" in str(cm["main_text"]).lower()

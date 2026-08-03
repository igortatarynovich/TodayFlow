"""C3.1 editorial quality gate — abstract / universal / clone scenes."""

from __future__ import annotations

from todayflow_backend.services.day_scenario_editorial_gate_c31 import (
    DEFECT_ASTRO_JARGON_BARE,
    DEFECT_SCENE_ABSTRACT,
    DEFECT_SCENE_CLONE,
    DEFECT_SCENE_MISSING_EVERYDAY,
    DEFECT_SCENE_UNIVERSAL_ADVICE,
    DEFECT_THESIS_ECHO,
    editorial_has_critical,
    format_editorial_retry_feedback,
    run_editorial_quality_gate_c31,
    score_editorial_quality_c31,
)
from todayflow_backend.services.day_scenario_native_llm_c1 import (
    NATIVE_LLM_SCHEMA_VERSION,
    normalize_native_scenario_llm_c1,
)


def _good_scene(sphere: str, *, sid: str | None = None) -> dict:
    return {
        "scene_id": sid or f"scene.{sphere}",
        "sphere": sphere,
        "role_in_story": "primary" if sphere == "relationships" else "support",
        "setup": "В мессенджере спрашивают «всё ли в порядке?» именно когда хочется ответить «нормально».",
        "opportunity": "Написать коротко и честно: «Нужна минута — отвечу по делу».",
        "trap": "Согласиться ради тишины и потом злиться, что вас не поняли.",
        "recommended_action": "Открыть черновик сообщения и отправить после паузы в один абзац.",
        "avoid_action": "Не отвечать автоматическим «всё ок» без смысла.",
        "everyday_example": "Сообщение от партнёра в 21:40: вопрос «ты где?» — момент закрыться или назвать факт.",
        "evidence_refs": ["moon-pisces"],
        "chorus_refs": ["conflict", "day_card"],
    }


def _valid_native_good() -> dict:
    return {
        "schema_version": NATIVE_LLM_SCHEMA_VERSION,
        "interpretive_chorus": {
            "astrology": [
                {
                    "named_factor": "Луна в Рыбах",
                    "human_meaning": "Эмоциональный подтекст становится заметнее прямых слов.",
                    "link_to_conflict": "Поэтому хочется сгладить, хотя нужен короткий ясный ответ.",
                    "evidence_refs": ["moon-pisces"],
                }
            ],
            "day_card": {
                "named_factor": "Карта дня — Отшельник",
                "archetype_role": "Пауза перед ответом.",
                "link_to_conflict": "Архетип того же выбора: сначала понять, потом говорить.",
                "evidence_refs": ["day_card"],
            },
            "day_number": {
                "named_factor": "Число дня — 7",
                "tempo": "сначала понять",
                "style": "без спешки",
                "link_to_conflict": "Число задаёт ритм прохождения конфликта прояснения.",
                "evidence_refs": ["day_number"],
            },
            "natal": [],
        },
        "conflict": {
            "title": "Прояснение против сглаживания",
            "thesis": "Сегодня важнее назвать точно, чем сохранить ложную гармонию.",
            "force_a": "сгладить ради тишины",
            "force_b": "сказать коротко и честно",
            "why_today": "Луна в Рыбах усиливает эмоциональный подтекст.",
            "why_personal": "",
            "driver_refs": ["moon-pisces"],
            "evidence_refs": ["moon-pisces"],
        },
        "scenes": [
            _good_scene("relationships"),
            {
                **_good_scene("work_decisions"),
                "setup": "Коллега в чате просит «быстро окнуть» письмо, которое вы ещё не дочитали.",
                "opportunity": "Ответить: «Вернусь через 20 минут с точной правкой».",
                "trap": "Поставить «ок» и потом чинить чужие ожидания.",
                "recommended_action": "Одно сообщение с временем возврата.",
                "avoid_action": "Не ставить реакцию без чтения.",
                "everyday_example": "Рабочий чат, 11:15: «ок?» под длинным письмом.",
                "chorus_refs": ["conflict", "astrology"],
            },
        ],
        "prop_material": {
            "color_scene_candidates": ["scene.relationships"],
            "affirmation_tension": {
                "scene_id": "scene.relationships",
                "trap": "сгладить",
                "text": "Я могу сказать коротко и остаться в контакте.",
            },
        },
    }


def test_good_everyday_scenes_pass_editorial_gate():
    native = normalize_native_scenario_llm_c1(_valid_native_good())
    defects = run_editorial_quality_gate_c31(native, has_natal_evidence=True)
    critical = [d for d in defects if editorial_has_critical([d])]
    assert critical == [], defects
    score = score_editorial_quality_c31(defects)
    assert score["editorial_score"] >= 0.85


def test_abstract_sphere_scene_rejected():
    native = _valid_native_good()
    native["scenes"][0] = {
        "scene_id": "scene.relationships",
        "sphere": "relationships",
        "role_in_story": "primary",
        "setup": "В отношениях возможна напряжённость.",
        "opportunity": "Сохраняйте границы.",
        "trap": "Не распыляйтесь.",
        "recommended_action": "Слушайте себя.",
        "avoid_action": "Избегайте конфликтов.",
        "everyday_example": "Баланс важен.",
        "evidence_refs": ["moon-pisces"],
        "chorus_refs": ["conflict"],
    }
    defects = run_editorial_quality_gate_c31(
        normalize_native_scenario_llm_c1(native), has_natal_evidence=True
    )
    codes = {d["code"] for d in defects}
    assert DEFECT_SCENE_ABSTRACT in codes or DEFECT_SCENE_UNIVERSAL_ADVICE in codes or DEFECT_SCENE_MISSING_EVERYDAY in codes
    assert editorial_has_critical(defects)


def test_universal_advice_without_concrete_action_rejected():
    native = _valid_native_good()
    native["scenes"][0]["recommended_action"] = "Не торопитесь и сохраняйте баланс."
    native["scenes"][0]["opportunity"] = "Слушайте себя."
    native["scenes"][0]["everyday_example"] = "Будьте осторожны сегодня."
    defects = run_editorial_quality_gate_c31(
        normalize_native_scenario_llm_c1(native), has_natal_evidence=True
    )
    codes = {d["code"] for d in defects}
    assert (
        DEFECT_SCENE_UNIVERSAL_ADVICE in codes
        or DEFECT_SCENE_ABSTRACT in codes
        or DEFECT_SCENE_MISSING_EVERYDAY in codes
    )


def test_clone_scenes_rejected():
    native = _valid_native_good()
    clone = dict(native["scenes"][0])
    clone["scene_id"] = "scene.communication"
    clone["sphere"] = "communication"
    native["scenes"][1] = clone
    defects = run_editorial_quality_gate_c31(
        normalize_native_scenario_llm_c1(native), has_natal_evidence=True
    )
    assert any(d["code"] == DEFECT_SCENE_CLONE for d in defects)


def test_astro_jargon_without_translation_rejected():
    native = _valid_native_good()
    native["interpretive_chorus"]["astrology"] = [
        {
            "named_factor": "Луна в Рыбах в квадрате к Марсу",
            "human_meaning": "Квадрат. Трины. Ретроград.",
            "link_to_conflict": "Аспект дня.",
            "evidence_refs": ["moon-pisces"],
        }
    ]
    defects = run_editorial_quality_gate_c31(
        normalize_native_scenario_llm_c1(native), has_natal_evidence=True
    )
    assert any(d["code"] == DEFECT_ASTRO_JARGON_BARE for d in defects)


def test_astro_lived_metaphor_is_not_bare_jargon():
    """Rich human metaphor must not false-block (C3.6.2 shadow FP cases)."""
    native = _valid_native_good()
    native["interpretive_chorus"]["astrology"] = [
        {
            "named_factor": "Меркурий разворачивается в директное движение в знаке Лев",
            "human_meaning": (
                "Внешняя среда сегодня похожа на зал ожидания, где внезапно объявили посадку. "
                "Все разговоры, которые зависли в воздухе, получают резкий импульс к завершению. "
                "Появляется соблазн высказать всё, что накопилось, с королевской прямотой."
            ),
            "link_to_conflict": (
                "Этот разворот создаёт внешнее давление и сталкивает желание спокойно "
                "разобраться с лавиной нефильтрованных слов."
            ),
            "evidence_refs": ["mercury-direct"],
        }
    ]
    defects = run_editorial_quality_gate_c31(
        normalize_native_scenario_llm_c1(native), has_natal_evidence=True
    )
    codes = {d["code"] for d in defects}
    assert DEFECT_ASTRO_JARGON_BARE not in codes
    assert "CHORUS_UNTRANSLATED_JARGON" not in codes


def test_astro_echo_template_still_counts_as_bare_jargon():
    native = _valid_native_good()
    native["interpretive_chorus"]["astrology"] = [
        {
            "named_factor": "Меркурий разворачивается в директное движение в знаке Лев",
            "human_meaning": (
                "Меркурий разворачивается в директное движение в знаке Лев. "
                "Это подталкивает день к сюжету «Сгладить или сказать прямо»."
            ),
            "link_to_conflict": (
                "Объясняет, почему сегодня в центре «Сгладить или сказать прямо — "
                "пока меркурий разворачивается в директное движение»."
            ),
            "evidence_refs": ["mercury-direct"],
        }
    ]
    defects = run_editorial_quality_gate_c31(
        normalize_native_scenario_llm_c1(native), has_natal_evidence=True
    )
    assert any(d["code"] == DEFECT_ASTRO_JARGON_BARE for d in defects)


def test_thesis_echo_across_scenes_rejected():
    native = _valid_native_good()
    thesis = "Сегодня важнее назвать точно, чем сохранить ложную гармонию."
    native["conflict"]["thesis"] = thesis
    for sc in native["scenes"]:
        sc["setup"] = f"{thesis} {sc['setup']}"
        sc["opportunity"] = f"{thesis} ещё раз."
    defects = run_editorial_quality_gate_c31(
        normalize_native_scenario_llm_c1(native), has_natal_evidence=True
    )
    assert any(d["code"] == DEFECT_THESIS_ECHO for d in defects)


def test_retry_feedback_lists_defect_codes():
    native = _valid_native_good()
    native["scenes"][0]["setup"] = "В отношениях возможна напряжённость."
    native["scenes"][0]["everyday_example"] = "коротко"
    defects = run_editorial_quality_gate_c31(
        normalize_native_scenario_llm_c1(native), has_natal_evidence=True
    )
    feedback = format_editorial_retry_feedback(defects)
    assert "editorial quality gate" in feedback.lower() or "дефект" in feedback.lower()
    assert any(code in feedback for code in {d["code"] for d in defects})


def test_thin_template_everyday_is_missing_not_just_abstract():
    """Formulaic tips with bare keywords must fire SCENE_MISSING_EVERYDAY (C3.6.2 gap)."""
    native = _valid_native_good()
    native["scenes"][0]["everyday_example"] = "Сообщение: сначала смысл, потом скорость ответа."
    native["scenes"][1]["everyday_example"] = "Разговор, где важно не сгладить то, что лучше проговорить."
    defects = run_editorial_quality_gate_c31(
        normalize_native_scenario_llm_c1(native), has_natal_evidence=True
    )
    codes = {d["code"] for d in defects}
    assert DEFECT_SCENE_MISSING_EVERYDAY in codes


def test_guillemet_alone_does_not_count_as_lived_everyday():
    native = _valid_native_good()
    native["scenes"][0]["everyday_example"] = "Смена обстановки на час, если тянет «всё бросить»."
    defects = run_editorial_quality_gate_c31(
        normalize_native_scenario_llm_c1(native), has_natal_evidence=True
    )
    assert any(d["code"] == DEFECT_SCENE_MISSING_EVERYDAY for d in defects)


def test_seed_bank_binary_and_chorus_paste_emit_hard_codes():
    from todayflow_backend.services.day_scenario_editorial_gate_c31 import (
        DEFECT_SEED_BANK_BINARY_SHORT_NAME,
        DEFECT_SEED_CHORUS_PASTE,
    )
    from todayflow_backend.services.day_scenario_gate_maturity_c36 import (
        annotate_defects_with_maturity,
        should_retry_defects,
    )

    short = "Тащить старое или отпустить и восстановиться"
    native = _valid_native_good()
    native["conflict"]["title"] = short
    native["interpretive_chorus"]["astrology"][0]["human_meaning"] = (
        f"Убывающая луна. Это подталкивает день к сюжету «{short}»."
    )
    native["interpretive_chorus"]["day_card"]["link_to_conflict"] = (
        f"Архетип «Девятка жезлов» лучше всего описывает, какой ролью пройти «{short}»."
    )
    native["interpretive_chorus"]["day_number"]["link_to_conflict"] = (
        f"Число 21 окрашивает прохождение «{short}»: темп — выражение."
    )
    defects = run_editorial_quality_gate_c31(
        normalize_native_scenario_llm_c1(native), has_natal_evidence=True
    )
    codes = {d["code"] for d in defects}
    assert DEFECT_SEED_BANK_BINARY_SHORT_NAME in codes
    assert DEFECT_SEED_CHORUS_PASTE in codes
    annotated = annotate_defects_with_maturity(defects)
    assert should_retry_defects(annotated)
    feedback = format_editorial_retry_feedback(defects)
    assert "SEED-KILL" in feedback
    assert DEFECT_SEED_CHORUS_PASTE in feedback


def test_seed_leaks_are_hard_after_scenario_validate():
    """Mapped scenario with old bridges must hard-fail LLM accept path."""
    from todayflow_backend.services.day_scenario_gate_maturity_c36 import (
        is_hard_scenario_validate_error,
    )
    from todayflow_backend.services.day_scenario_v1 import (
        find_verbatim_seed_leaks_v1,
        validate_day_scenario_v1,
    )

    short = "Тащить старое или отпустить и восстановиться"
    scenario = {
        "contract_version": "day_scenario_v1",
        "conflict": {"short_name": short, "driver_ids": ["x"], "opposing_forces": {"a": "", "b": ""}},
        "foundation": {"ranked_drivers": [{"id": "x", "fact_ru": "Убывающая луна."}]},
        "chorus": {
            "astrology": [
                {
                    "human_meaning": f"Убывающая луна. Это подталкивает день к сюжету «{short}».",
                }
            ],
            "day_card": {
                "link_to_conflict": f"какой ролью пройти «{short}»",
                "must_not_invent_second_plot": True,
            },
            "day_number": {
                "link_to_conflict": f"Число 21 окрашивает прохождение «{short}»",
                "must_not_invent_second_plot": True,
            },
            "natal": [],
        },
        "scenes": [
            {
                "scene_id": "scene.relationships",
                "sphere": "relationships",
                "what_happens": "разговор",
                "opportunity": "сказать",
                "trap": "сгладить",
                "recommended_action": "написать",
                "do_not": "молчать",
            }
        ],
        "props": {},
    }
    leaks = find_verbatim_seed_leaks_v1(scenario)
    assert any("invented_bank_binary" in x or "seed_paste" in x or "verbatim_seed_leak" in x for x in leaks)
    errors = validate_day_scenario_v1(scenario)
    hard = [e for e in errors if is_hard_scenario_validate_error(e)]
    assert hard, f"expected hard seed errors, got errors={errors}"

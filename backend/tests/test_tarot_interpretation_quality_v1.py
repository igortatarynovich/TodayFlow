"""Offline quality checks for Tarot Context Pack + interpretation gates."""

from __future__ import annotations

from todayflow_backend.core import models
from todayflow_backend.services import tarot_interpretation_engine_v1 as engine
from todayflow_backend.services import tarot_interpretation_llm_v1 as tarot_llm


def _card(cid: int, orientation: str, pid: str, title: str) -> models.TarotSpreadCard:
    return models.TarotSpreadCard(
        card=models.TarotCard(id=cid, name=f"Card {cid}", keywords=[], upright="", reversed=""),
        orientation=orientation,
        position=models.TarotSpreadPosition(id=pid, title=title, prompt=title),
        meaning="",
    )


def test_context_pack_has_rich_meaning_range_for_major_and_minor():
    spread = models.TarotSpreadResult(
        spread_id="guidance_choice_two",
        title="Выбор",
        cards=[
            _card(18, "reversed", "a_gives", "Вариант A — что он даёт"),
            _card(22, "upright", "a_risk", "Вариант A — риск"),
            _card(15, "upright", "weights", "Что важно учитывать"),
            _card(0, "upright", "best_step", "Лучший следующий шаг"),
        ],
    )
    pack = engine.build_context_pack(
        spread,
        question="Стоит ли менять работу — или сначала прояснить здесь?",
        concern_domain="work",
        experience_slice={
            "decision_style": "Сверяется с телом, потом фиксирует выбор",
            "motivation": "Нужна стабильность без потери смысла",
            "identity_line": "Длинный натальный абзац не должен попасть первым",
        },
    )
    assert pack is not None
    assert pack["question_domain"] in {"work", "work_change", "decision"}
    qo = pack["question_ontology"]
    assert qo["question_type"] == "choice"
    assert qo["domain"] == "work"
    assert qo["must_show"] and qo["must_not_claim"]
    assert "decision_style" in pack["profile_relevant"]
    assert "identity_line" not in pack["profile_relevant"]

    moon = pack["cards"][0]["meaning_range"]
    for key in (
        "central_symbol",
        "light_side",
        "shadow_side",
        "upright_themes",
        "reversed_themes",
        "upright_meaning",
        "reversed_meaning",
    ):
        assert moon.get(key), key
    assert pack["cards"][0]["question_lens"]
    assert pack["cards"][1]["suit"] == "wands"
    assert pack["cards"][1]["meaning_range"].get("element") or pack["cards"][1]["suit_themes"]
    assert pack["cards"][3]["position_role"] == "next_step"
    step_sem = pack["cards"][3]["position_semantics"]
    assert step_sem["result_type"] == "concrete_action"
    assert step_sem["answers_question"]
    assert any("состоян" in d.lower() or "гарант" in d.lower() for d in step_sem["do_not"])
    risk_sem = pack["cards"][1]["position_semantics"]
    assert risk_sem["role_id"] == "risk"
    assert risk_sem["result_type"] == "concrete_risk"


def test_thin_fallback_is_honest_not_fake_synthesis():
    pack = {
        "question": "Что делать?",
        "cards": [
            {
                "name_ru": "Шут",
                "position_title": "Шаг",
                "orientation": "upright",
                "meaning_range": {
                    "central_symbol": "новый шаг",
                    "upright_themes": ["эксперимент", "открытость"],
                },
            }
        ],
    }
    fb = engine.thin_fallback_from_pack(pack)
    assert "Не удалось собрать полноценную интерпретацию" in fb["direct_answer"]
    assert "без персонального синтеза" in fb["direct_answer"]
    assert fb["direct_answer"] == fb["question_story"]


def test_quality_gates_reject_profile_paste_and_question_spam():
    pack = {
        "question": "Стоит ли менять работу?",
        "spread_kind": "general",
        "profile_relevant": {"decision_style": "Вы решаете через стратегический расчёт и долгую перспективу"},
        "profile_lens": "Вы решаете через стратегический расчёт и долгую перспективу",
        "cards": [
            {"name_ru": "Луна"},
            {"name_ru": "Дьявол"},
        ],
        "response_shape": {},
    }
    bad = {
        "symbols_overview": "Луна и Дьявол показывают туман и привязанность в рабочей теме без пустых формул здесь.",
        "question_story": (
            "По вопросу «Стоит ли менять работу?» видно напряжение. "
            "Вы решаете через стратегический расчёт и долгую перспективу — это цитата профиля."
        ),
        "direct_answer": "Стоит ли менять работу? Сначала проясни критерии.",
        "next_step": "Сделай один разговор с руководителем на этой неделе.",
    }
    assert tarot_llm.validate_interpretation(bad, pack=pack) is None

    good = {
        "symbols_overview": "Луна и Дьявол задают напряжение между неясностью и привычным удержанием.",
        "question_story": (
            "Вместе они показывают: решение осложняет не только роль, но и страх потерять стабильность, "
            "пока ожидания не отделены от фактов."
        ),
        "direct_answer": "Не увольняйся вслепую и не оставайся в бесконечной неопределённости — нужен срок проверки.",
        "next_step": "Запиши условия остаться и отправь один отклик на новую роль сегодня.",
    }
    assert tarot_llm.validate_interpretation(good, pack=pack) is not None


def test_quality_gates_require_choice_contrast():
    pack = {
        "question": "A или B?",
        "spread_kind": "choice",
        "profile_relevant": {},
        "cards": [{"name_ru": "Шут"}, {"name_ru": "Император"}, {"name_ru": "Луна"}, {"name_ru": "Дьявол"}],
        "response_shape": {"choice_compare": True},
    }
    weak = {
        "symbols_overview": "Шут и Император показывают старт и структуру; Луна и Дьявол добавляют туман и привязанность.",
        "question_story": "Карты говорят о выборе без ясного различия путей.",
        "direct_answer": "Нужна проверка фактов перед финальным решением.",
        "next_step": "Сделай один проверяемый шаг и зафиксируй срок решения.",
    }
    assert tarot_llm.validate_interpretation(weak, pack=pack) is None

    strong = {
        **weak,
        "question_story": (
            "Путь A через Шута быстрее открывает движение, путь B через Императора даёт порядок, "
            "но Луна и Дьявол показывают риск тумана и удержания."
        ),
        "option_a_note": "A быстрее снимает застой, но может быть импульсивным.",
        "option_b_note": "B сохраняет опору, но может затягивать прояснение.",
    }
    assert tarot_llm.validate_interpretation(strong, pack=pack) is not None


def test_quality_gates_accept_semantic_grounding_without_card_names():
    """Card-name ablation: scenes/conflicts may ground the answer without naming cards."""
    pack = {
        "question": "Почему я чувствую себя в ловушке мыслей?",
        "spread_kind": "general",
        "profile_relevant": {},
        "cards": [
            {
                "name_ru": "Восьмёрка Мечей",
                "meaning_range": {
                    "central_symbol": "связанность снаружи",
                    "core_scene": "ремни и верёвки вокруг тела",
                },
            },
            {
                "name_ru": "Девятка Мечей",
                "meaning_range": {
                    "central_symbol": "ночная тревога ума",
                    "core_scene": "война в голове вместо сна",
                },
            },
            {
                "name_ru": "Десятка Мечей",
                "meaning_range": {
                    "central_symbol": "дно и конец",
                    "core_scene": "финал истории на земле",
                },
            },
        ],
        "response_shape": {},
    }
    no_names = {
        "symbols_overview": (
            "Сначала связанность снаружи, потом ночная тревога ума — и рядом соблазн принять "
            "дно и конец за единственный выход."
        ),
        "question_story": (
            "Ловушка держится не только на верёвках: ум крутит войну в голове и путает усталость "
            "с финалом истории, будто дальше ничего нельзя."
        ),
        "direct_answer": (
            "Сначала отдели внешнюю связанность от ночной тревоги — дно ещё не приговор и не факт."
        ),
        "next_step": "Перед сном запиши одну мысль и один физический факт из комнаты.",
    }
    assert tarot_llm.validate_interpretation(no_names, pack=pack) is not None

    ungrounded = {
        "symbols_overview": "В раскладе много напряжения и общих слов без опоры на сцены карт.",
        "question_story": "Ситуация сложная, нужно просто понять себя глубже и не торопиться.",
        "direct_answer": "Сейчас важно действовать спокойнее и не делать резких выводов о будущем.",
        "next_step": "Сделай паузу и запиши, что чувствуешь сегодня вечером.",
    }
    assert tarot_llm.validate_interpretation(ungrounded, pack=pack) is None


def test_quality_gates_reject_antithesis_ne_a_formula():
    """Owner editorial: avoid «не X, а Y» rhetoric («не кричит, а греет»)."""
    pack = {
        "question": "Какое направление в работе сейчас заслуживает внимания?",
        "spread_kind": "general",
        "profile_relevant": {},
        "cards": [
            {
                "name_ru": "Девятка Жезлов",
                "meaning_range": {
                    "central_symbol": "усталый страж",
                    "core_scene": "держит финальный рубеж",
                },
            },
            {
                "name_ru": "Королева Жезлов",
                "meaning_range": {
                    "central_symbol": "живой огонь",
                    "core_scene": "теплое уверенное лидерство",
                },
            },
        ],
        "response_shape": {},
    }
    bad = {
        "symbols_overview": (
            "Усталый страж стоит рядом с живым огнём: измотанность держит финальный рубеж, "
            "а рядом зреет теплое уверенное лидерство."
        ),
        "question_story": (
            "Сейчас вы в режиме стража. Впереди маячит роль, где власть не кричит, а греет."
        ),
        "direct_answer": (
            "Внимания заслуживает направление, где вы строите культуру вокруг себя через доверие."
        ),
        "next_step": "Запиши три пункта, что тянешь в одиночку, и кому это можно передать.",
    }
    assert tarot_llm.quality_reject_reason(bad, pack) == "antithesis_formula"
    assert tarot_llm.validate_interpretation(bad, pack=pack) is None

    # «это не …, а …» — prompt ban only; hard gate would over-reject live answers.
    soft_eto = {
        **bad,
        "question_story": (
            "Сейчас вы в режиме стража у финального рубежа. Это не героический рывок, "
            "а переход к роли, где лидерство держится на тепле и доверии."
        ),
    }
    assert tarot_llm.quality_reject_reason(soft_eto, pack) is None

    good = {
        **bad,
        "question_story": (
            "Сейчас вы в режиме стража у финального рубежа. Впереди зреет роль тёплого "
            "уверенного лидерства, где власть держится на магнетизме и доверии."
        ),
    }
    assert tarot_llm.quality_reject_reason(good, pack) is None
    assert tarot_llm.validate_interpretation(good, pack=pack) is not None

    # Ordinary advice / noun contrast must not trip the voice gate.
    advice = {
        **bad,
        "question_story": (
            "Сейчас вы в режиме стража у финального рубежа. Важно не уходить сразу, "
            "а сначала прояснить критерии и закрыть старый перекос в оценке вклада."
        ),
    }
    assert tarot_llm.quality_reject_reason(advice, pack) is None
    noun = {
        **bad,
        "question_story": (
            "Сейчас вы в режиме стража. В центре не страх, а ясность выбора и опора на критерии."
        ),
    }
    assert tarot_llm.quality_reject_reason(noun, pack) is None


def test_clean_field_rejects_empty_solemnity_formulas():
    """Analytical voice: reject faux profundity / oracle mush."""
    assert tarot_llm._clean_field("Послание карт говорит о важном повороте судьбы прямо сейчас.", min_words=6) is None
    assert tarot_llm._clean_field(
        "Самый тяжёлый вес сейчас — привычная петля без названной выгоды и страха.",
        min_words=6,
    ) is None
    assert tarot_llm._clean_field(
        "Запиши три критерия решения и проверь их на одном рабочем эпизоде этой недели.",
        min_words=6,
    )


def test_choice_question_story_allows_moderate_length_from_eval_delta():
    """Live #2 reject: too_long:question_story at 900 — choice needs headroom."""
    pack = {
        "question": "Стоит ли менять работу — или сначала что-то прояснить здесь?",
        "spread_kind": "choice",
        "profile_relevant": {},
        "cards": [
            {
                "name_ru": "Луна",
                "meaning_range": {"central_symbol": "туман сомнений", "core_scene": "путь сквозь ночной берег"},
            },
            {
                "name_ru": "Рыцарь Жезлов",
                "meaning_range": {"central_symbol": "импульс движения", "core_scene": "конь уже в рыси"},
            },
            {
                "name_ru": "Император",
                "meaning_range": {"central_symbol": "порядок и опора", "core_scene": "трон и рамка правил"},
            },
            {
                "name_ru": "Повешенный",
                "meaning_range": {"central_symbol": "пауза взгляда", "core_scene": "висеть чтобы увидеть иначе"},
            },
        ],
        "response_shape": {"choice_compare": True},
    }
    pad = (
        "Сначала отделяй страх от фактов на берегу ночи, потом смотри на рысь коня, "
        "рамку правил на троне и цену паузы: спешка режет опору, застой размывает критерии, "
        "а разговор с коллегой и запись трёх условий дают проверяемую точку, не фатальный приговор. "
        "Добавь сравнение зарплаты, нагрузки и смысла задач без драмы; отметь, где туман сильнее фактов, "
        "и где импульс уже готов увести без карты маршрута."
    )
    story = (
        "Выбор держится на тумане сомнений против импульса движения: один путь манит сменой "
        "берега, другой требует сначала увидеть рамку правил на текущем месте. "
        "Пауза взгляда говорит: не сжигай мост, пока не отделён страх от факта. "
        + pad
        + " "
        + pad
    )
    fields = {
        "symbols_overview": (
            "Туман сомнений сталкивается с импульсом движения; рядом порядок и опора и пауза взгляда."
        ),
        "question_story": story,
        "direct_answer": "Сначала проясни критерии здесь, потом решай об уходе — не наоборот.",
        "next_step": "Запиши три критерия «остаться имеет смысл» и проверь один разговором на этой неделе.",
        "option_a_note": "Уйти быстрее снимает туман, но риск импульса без опоры.",
        "option_b_note": "Остаться даёт рамку, но может растянуть паузу без решения.",
    }
    assert 900 < len(fields["question_story"]) <= tarot_llm._FIELD_MAX_CHARS_CHOICE_STORY
    assert tarot_llm.validate_interpretation(fields, pack=pack) is not None

    too_long = {**fields, "question_story": fields["question_story"] + (" подробно" * 80)}
    assert tarot_llm.quality_reject_reason(too_long, pack) == "too_long:question_story"

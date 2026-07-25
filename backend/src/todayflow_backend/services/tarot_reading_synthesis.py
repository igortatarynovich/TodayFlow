"""Question-first tarot synthesis — Interpretation Engine v1 entry.

Canon: docs/tarot/TAROT_INTERPRETATION_ENGINE_V1.md
"""

from __future__ import annotations

import re
from typing import Any, TypedDict

from todayflow_backend.core import models
from todayflow_backend.services import tarot_interpretation_engine_v1 as engine

_HOLDING_POSITIONS = {"past", "you", "core", "obstacle", "block", "fear", "risk", "suppress", "reality"}
_SHIFTING_POSITIONS = {"present", "dynamic", "tension", "between", "heart", "mind", "works"}
_ATTENTION_POSITIONS = {"future", "outcome", "next_step", "advice", "exit", "integration", "step", "focus"}


class _ReadingBundle(TypedDict):
    answer: str
    story: str
    holding: str
    shifting: str
    attention: str
    today: str
    follow_up_prompt: str
    chips: list[tuple[str, str]]


_ENGLISH_NAME_RE = re.compile(
    r"\b(?:The\s+)?(?:Fool|Magician|High Priestess|Empress|Emperor|Hierophant|Lovers|Chariot|"
    r"Strength|Hermit|Wheel of Fortune|Justice|Hanged|Death|Temperance|Devil|Tower|Star|Moon|Sun|"
    r"Judgement|Judgment|World)\b",
    re.I,
)

_FOLLOW_UP_DEFAULT_PROMPT = "Что сейчас кажется самым важным?"


def _clean(text: str) -> str:
    if not text:
        return ""
    t = _ENGLISH_NAME_RE.sub("", text)
    for bad in (
        "диалог карт",
        "линия расклада",
        "справочное значение",
        "Сначала —",
        "Затем —",
        "Дальше —",
        "Похоже, дело не в одной цифре",
    ):
        t = t.replace(bad, "")
    return re.sub(r"\s{2,}", " ", t).strip()


def _norm_domain(concern_domain: str | None) -> str:
    return (concern_domain or "other").strip().lower()


def _q(question: str | None) -> str:
    return (question or "").strip().lower()


def _detect_theme(question: str | None, concern_domain: str | None) -> str:
    text = _q(question)
    domain = _norm_domain(concern_domain)

    if domain == "relationships" or any(w in text for w in ("отношен", "партнёр", "партнер", "близост", "любов")):
        if any(w in text for w in ("бывш", "ex", "расстал")):
            return "relationships_ex"
        if any(w in text for w in ("новый человек", "новым человек", "нового человек", "знаком")):
            return "relationships_new"
        if any(w in text for w in ("двумя", "выбор между", "кого выбрать")):
            return "relationships_choice"
        return "relationships"

    if domain == "work" or any(w in text for w in ("работ", "карьер", "коллег", "начальник", "увольн")):
        if any(w in text for w in ("уйти", "сменить", "менять работ", "увольн", "остаться")):
            return "work_change"
        if any(w in text for w in ("выгоран", "устал", "устала", "выматыва")):
            return "work_burnout"
        return "work"

    if domain == "money" or any(w in text for w in ("деньг", "доход", "трат", "вложен", "финанс")):
        return "money"

    if domain == "family" or any(w in text for w in ("семь", "родител", "ребён", "ребен", "дом")):
        return "family"

    if domain == "decision" or any(w in text for w in ("решени", "выбор", "стоит ли")):
        return "decision"

    if domain == "conflict" or any(w in text for w in ("конфликт", "ссор", "спор", "напряжен")):
        return "conflict"

    if domain == "growth" or any(w in text for w in ("рост", "путь", "смысл", "предназнач")):
        return "growth"

    if domain == "inner_state" or any(w in text for w in ("тревог", "пуст", "апати", "перегруз", "настроен")):
        return "inner_state"

    return "general"


def _detect_intent(question: str | None, theme: str) -> str:
    text = _q(question)

    if theme == "money" or any(w in text for w in ("деньг", "доход", "трат", "вложен", "финанс")):
        if any(w in text for w in ("спокойн", "тревож", "волну", "без паник")):
            return "money_calm"
        if any(w in text for w in ("крупн", "трат", "вложен", "покупк", "сделк")):
            return "money_decision"
        if any(w in text for w in ("доход", "заработ", "увелич", "больше денег")):
            return "money_income"
        if any(w in text for w in ("стабильн", "страх потер")):
            return "money_stability"
        return "money_general"

    if theme == "relationships_ex":
        return "relationships_ex"
    if theme == "relationships_new":
        return "relationships_new"
    if theme == "relationships_choice":
        return "relationships_choice"
    if theme == "relationships":
        return "relationships_general"

    if theme == "work_change":
        return "work_change"
    if theme == "work_burnout":
        return "work_burnout"
    if theme == "work":
        return "work_general"

    if theme == "decision":
        if any(w in text for w in ("страх ошиб", "боюсь", "ошиб")):
            return "decision_fear"
        if any(w in text for w in ("два", "между", "или")):
            return "decision_two_options"
        return "decision_general"

    if theme == "conflict":
        return "conflict_general"
    if theme == "family":
        return "family_general"
    if theme == "growth":
        return "growth_general"
    if theme == "inner_state":
        if any(w in text for w in ("тревог", "волну")):
            return "inner_anxiety"
        if any(w in text for w in ("пуст", "апати")):
            return "inner_empty"
        return "inner_general"

    return theme if theme != "general" else "general"


def _position_role(position_id: str) -> str:
    pid = position_id.strip().lower()
    if pid in _HOLDING_POSITIONS:
        return "holding"
    if pid in _SHIFTING_POSITIONS:
        return "shifting"
    if pid in _ATTENTION_POSITIONS:
        return "attention"
    return "neutral"


def _build_card_insights(cards: list[models.TarotSpreadCard]) -> list[models.TarotCardInsight] | None:
    return engine.build_card_insights(cards)


def _bundle_for_intent(intent: str) -> _ReadingBundle:
    bundles: dict[str, _ReadingBundle] = {
        "money_calm": {
            "answer": (
                "Сейчас ты ищешь решение, в котором почти не остаётся риска. "
                "Но спокойствие с деньгами приходит не тогда, когда исчезнут все сомнения — "
                "а тогда, когда ты примешь решение, с последствиями которого готов жить, даже если оно не идеально."
            ),
            "story": (
                "Сейчас тебя удерживает не отсутствие ответа, а желание найти вариант, "
                "в котором не придётся ничего потерять. Именно эта попытка избежать потерь "
                "и не даёт двигаться дальше. Постепенно внимание смещается с поиска идеального решения "
                "на готовность сделать первый осознанный шаг."
            ),
            "holding": (
                "Ты уже понимаешь, какое решение кажется тебе правильным. "
                "Но продолжаешь искать ещё одно подтверждение, надеясь, что оно полностью снимет тревогу."
            ),
            "shifting": (
                "Ты постепенно перестаёшь смотреть только на возможные потери "
                "и начинаешь замечать, что у каждого выбора есть не только цена, но и новые возможности."
            ),
            "attention": (
                "Обрати внимание, сколько времени занимает не само решение, "
                "а постоянное возвращение к одним и тем же мыслям. Иногда именно это забирает больше всего сил."
            ),
            "today": (
                "Выбери одно денежное решение, которое откладываешь уже больше недели. "
                "Не обязательно принимать его сегодня. Просто честно запиши, что именно тебя останавливает: "
                "нехватка информации или страх ошибиться."
            ),
            "follow_up_prompt": _FOLLOW_UP_DEFAULT_PROMPT,
            "chips": [
                ("keep", "Сохранить то, что уже есть"),
                ("income", "Увеличить доход"),
                ("worry_less", "Перестать постоянно переживать из-за денег"),
                ("delayed_step", "Сделать шаг, который давно откладываю"),
                ("unsure", "Пока не могу определить"),
            ],
        },
        "money_decision": {
            "answer": (
                "Сейчас ты ждёшь момента, когда решение станет очевидным само собой. "
                "Но ясность придёт не от новой информации — а от честного признания, "
                "чего ты боишься потерять, если выберешь любой из вариантов."
            ),
            "story": (
                "Ты уже собрал достаточно фактов. Дальше дело не в данных — "
                "а в том, готов ли ты принять цену выбора. "
                "Когда это становится видно, решение перестаёт казаться таким невозможным."
            ),
            "holding": "Ты откладываешь выбор, потому что ни один вариант не выглядит безопасным на сто процентов.",
            "shifting": "Ты начинаешь видеть: идеального варианта может не быть — но есть тот, с которым ты сможешь жить.",
            "attention": "Заметь, не подменяешь ли ты решение бесконечным «ещё немного подумаю».",
            "today": (
                "Выпиши два варианта и под каждым — одну вещь, которую ты теряешь, и одну, которую получаешь. "
                "Без оценок. Только факты."
            ),
            "follow_up_prompt": "Если бы страх ошибки исчез, что бы ты сделал первым?",
            "chips": [
                ("invest", "Инвестировал"),
                ("job_change", "Поменял работу"),
                ("launch", "Запустил проект"),
                ("ask_more", "Попросил больше"),
                ("unsure", "Пока не знаю"),
            ],
        },
        "money_general": {
            "answer": (
                "Сейчас дело не в том, чтобы найти «правильную» цифру. "
                "Дело в том, чтобы перестать ждать решения, которое полностью снимет тревогу — "
                "и выбрать тот шаг, который ты готов сделать уже сейчас."
            ),
            "story": (
                "Ты давно крутишь одни и те же мысли о деньгах. "
                "Это не лень и не слабость — это попытка не ошибиться. "
                "Но именно ожидание идеального момента и забирает больше энергии, чем сам выбор."
            ),
            "holding": "Ты уже ближе к ответу, чем думаешь — но всё ещё ждёшь знака, что можно не бояться.",
            "shifting": "Появляется готовность смотреть на деньги не как на экзамен, а как на управляемую часть жизни.",
            "attention": "Сколько раз за последнюю неделю ты возвращался к одному и тому же денежному вопросу?",
            "today": (
                "Выбери одно денежное решение, которое откладываешь. "
                "Запиши одной фразой, что тебя останавливает — страх или нехватка фактов."
            ),
            "follow_up_prompt": _FOLLOW_UP_DEFAULT_PROMPT,
            "chips": [
                ("keep", "Сохранить то, что уже есть"),
                ("income", "Увеличить доход"),
                ("worry_less", "Перестать постоянно переживать из-за денег"),
                ("delayed_step", "Сделать шаг, который давно откладываю"),
                ("unsure", "Пока не могу определить"),
            ],
        },
        "relationships_ex": {
            "answer": (
                "Ты возвращаешься к этой истории не потому, что между вами ещё всё возможно — "
                "а потому что внутри остались вопросы, на которые хочется получить ответ, "
                "который, возможно, уже не прозвучит с той стороны."
            ),
            "story": (
                "Ты ищешь не столько человека, сколько завершённость — ощущение, что всё было не зря "
                "и что смысл можно удержать. Но пока ты ждёшь внешнего объяснения, "
                "ты не слышишь то, что уже понял сам."
            ),
            "holding": "Тебя держит не любовь к прошлому — а незакрытый вопрос, который ты боишься задать себе.",
            "shifting": "Ты начинаешь видеть: отпустить — не значит предать себя или стереть то, что было важным.",
            "attention": "Заметь, сколько раз за день мысль возвращается к нему или к ней — и что ты ищешь в этот момент.",
            "today": (
                "Сегодня не ищи новых объяснений этой истории. "
                "Один раз остановись и назови вслух чувство, которое она вызывает сейчас — не тогда."
            ),
            "follow_up_prompt": "Что сейчас кажется самым важным?",
            "chips": [
                ("let_go", "Отпустить"),
                ("understand", "Понять, что произошло"),
                ("closure", "Получить завершение"),
                ("stop_waiting", "Перестать ждать"),
                ("unsure", "Пока не знаю"),
            ],
        },
        "relationships_general": {
            "answer": (
                "Сейчас важнее не угадать, что происходит у другого человека — "
                "а честно назвать, чего ты хочешь от близости и что уже не получаешь."
            ),
            "story": (
                "Ты ищешь знак, что можно доверять — или знак, что пора отпустить. "
                "Но ответ редко приходит извне. Он появляется, когда ты перестаёшь просить близость "
                "доказать то, что можешь подтвердить только сам."
            ),
            "holding": "Тебя удерживает ожидание, что другой человек снимет с тебя необходимость выбирать.",
            "shifting": "Ты начинаешь слышать, чего хочешь ты — не только что «должно» быть в паре.",
            "attention": "Обрати внимание: ты чаще ищешь подтверждение или честность?",
            "today": "Сформулируй одну фразу: чего ты хочешь от близости прямо сейчас — без ожидания ответа от другого.",
            "follow_up_prompt": _FOLLOW_UP_DEFAULT_PROMPT,
            "chips": [
                ("clarity", "Понять, что чувствую"),
                ("closeness", "Больше близости"),
                ("space", "Больше пространства"),
                ("honest_talk", "Честный разговор"),
                ("unsure", "Пока не знаю"),
            ],
        },
        "work_change": {
            "answer": (
                "Вопрос о смене работы сейчас не про правильный ответ — "
                "а про то, что ты устал жить в режиме «пока терпимо, значит, не время»."
            ),
            "story": (
                "Ты давно чувствуешь, что перерос текущую роль или среду — "
                "но боишься, что резкий шаг окажется ошибкой. "
                "Постепенно становится видно: не решение пугает, а отсутствие ясного критерия, зачем ты вообще там."
            ),
            "holding": "Тебя держит не сама работа — а страх, что после ухода окажется, что «надо было терпеть».",
            "shifting": "Ты начинаешь отделять «мне тяжело» от «мне здесь больше не на месте».",
            "attention": "Сколько недель ты уже думаешь об уходе — и что мешает назвать это вслух хотя бы себе?",
            "today": (
                "Запиши три вещи: что в работе тебя держит, что забирает силы, и что ты хочешь сохранить в следующей роли. "
                "Без решения об уходе."
            ),
            "follow_up_prompt": _FOLLOW_UP_DEFAULT_PROMPT,
            "chips": [
                ("stay", "Остаться и прояснить"),
                ("leave", "Уйти"),
                ("pivot", "Сменить направление"),
                ("rest", "Сначала восстановиться"),
                ("unsure", "Пока не знаю"),
            ],
        },
        "work_burnout": {
            "answer": (
                "Сейчас тебе нужен не новый план карьеры — а разрешение перестать тянуть на силе воли. "
                "Восстановление — это тоже решение, не пауза «для слабых»."
            ),
            "story": (
                "Ты долго откладывал отдых, потому что казалось, что иначе всё развалится. "
                "Но именно это «ещё немного» и довело до точки, где даже простые задачи даются тяжело."
            ),
            "holding": "Тебя держит убеждение, что о тебе судят по тому, сколько ты выдерживаешь.",
            "shifting": "Появляется мысль, что можно снизить темп — и мир от этого не рухнет.",
            "attention": "Когда ты в последний раз заканчивал день без ощущения, что недоделал что-то важное?",
            "today": "Сегодня выдели один час без задач и без оправданий. Только восстановление.",
            "follow_up_prompt": _FOLLOW_UP_DEFAULT_PROMPT,
            "chips": [
                ("rest", "Отдохнуть"),
                ("boundaries", "Поставить границы"),
                ("delegate", "Что-то отпустить"),
                ("change_pace", "Сменить темп"),
                ("unsure", "Пока не знаю"),
            ],
        },
        "work_general": {
            "answer": (
                "Сейчас важнее не ускорить карьерный ход — "
                "а честно назвать, что в работе тебя держит, а что уже только высасывает силы."
            ),
            "story": (
                "Ты ищешь направление, но пока не дал себе права признать, что устал от неопределённости. "
                "Когда это признаётся, следующий шаг обычно становится проще — не громче."
            ),
            "holding": "Тебя удерживает ожидание, что «правильная» возможность должна появиться сама.",
            "shifting": "Ты начинаешь видеть, что ясность приходит от честного критерия, а не от идеальной вакансии.",
            "attention": "Ты чаще думаешь о том, чего хочешь — или о том, от чего хочешь убежать?",
            "today": "Назови вслух одну вещь в работе, которая тебя держит, и одну — которая уже нет.",
            "follow_up_prompt": _FOLLOW_UP_DEFAULT_PROMPT,
            "chips": [
                ("direction", "Найти направление"),
                ("stability", "Сохранить стабильность"),
                ("change", "Что-то изменить"),
                ("rest", "Восстановиться"),
                ("unsure", "Пока не знаю"),
            ],
        },
        "decision_general": {
            "answer": (
                "Ты ищешь не лучший вариант — а гарантию, что не ошибёшься. "
                "Но такой гарантии нет. Есть только выбор, с которым ты сможешь жить дальше."
            ),
            "story": (
                "Ты уже знаешь больше, чем готов признать. "
                "Осталось перестать ждать, что кто-то или что-то снимет с тебя ответственность за выбор."
            ),
            "holding": "Тебя держит страх пожалеть — как будто сожаление хуже, чем бесконечное ожидание.",
            "shifting": "Ты начинаешь видеть разницу между «страшно» и «неправильно».",
            "attention": "Если бы никто не узнал о твоём решении — что бы ты выбрал?",
            "today": "Запиши, что ты потеряешь в каждом варианте — и что сохранишь. Без финального выбора.",
            "follow_up_prompt": _FOLLOW_UP_DEFAULT_PROMPT,
            "chips": [
                ("option_a", "Ближе первый вариант"),
                ("option_b", "Ближе второй вариант"),
                ("need_time", "Нужно время"),
                ("fear", "Страшно ошибиться"),
                ("unsure", "Пока не знаю"),
            ],
        },
        "decision_fear": {
            "answer": (
                "Ты боишься не столько ошибиться — сколько оказаться тем, кто «должен был знать лучше». "
                "Но правильных решений без цены не бывает."
            ),
            "story": (
                "Страх ошибки маскируется под осторожность. "
                "Но если честно посмотреть — ты уже давно знаешь, чего хочешь, просто не хочешь платить цену."
            ),
            "holding": "Тебя держит образ себя безупречного — тот, кто никогда не промахивается.",
            "shifting": "Ты начинаешь допускать, что ошибка — не приговор, а часть живого выбора.",
            "attention": "Что страшнее: ошибиться или так и не узнать, что было бы, если бы ты решился?",
            "today": "Назови вслух один страх, связанный с этим решением. Без анализа — только факт.",
            "follow_up_prompt": "Если бы страх ошибки исчез, что бы ты сделал первым?",
            "chips": [
                ("act", "Сделал бы шаг"),
                ("wait", "Подождал бы ещё"),
                ("ask_help", "Попросил бы совета"),
                ("rewrite", "Пересмотрел бы варианты"),
                ("unsure", "Пока не знаю"),
            ],
        },
        "conflict_general": {
            "answer": (
                "Конфликт держится не потому, что кто-то «неправ» — "
                "а потому что обе стороны защищают то, что для них важно, и пока не названо, что именно."
            ),
            "story": (
                "Ты споришь о форме — кто что сказал, кто начал — "
                "но суть обычно в потребности, которую стыдно или страшно озвучить."
            ),
            "holding": "Тебя удерживает желание, чтобы другой первым признал, что был неправ.",
            "shifting": "Ты начинаешь видеть: иногда важнее быть понятым, чем победить в споре.",
            "attention": "Что ты на самом деле защищаешь в этом конфликте — не позицию, а потребность?",
            "today": "Сформулируй одну фразу о том, что для тебя важно в этом конфликте — без обвинений.",
            "follow_up_prompt": _FOLLOW_UP_DEFAULT_PROMPT,
            "chips": [
                ("speak", "Сказать прямо"),
                ("pause", "Взять паузу"),
                ("understand", "Понять другую сторону"),
                ("protect", "Защитить себя"),
                ("unsure", "Пока не знаю"),
            ],
        },
        "family_general": {
            "answer": (
                "В семье сейчас важнее не «починить всё» — "
                "а понять, где тебе нужны границы, а где — мягкий контакт."
            ),
            "story": (
                "Ты давно несёшь роль, которая когда-то помогала выжить в семье — "
                "но сейчас она может забирать силы. Это не предательство родных, это взросление."
            ),
            "holding": "Тебя держит чувство долга — как будто твои границы означают равнодушие.",
            "shifting": "Ты начинаешь видеть, что можно любить и при этом не соглашаться на всё.",
            "attention": "В каких разговорах с близкими ты чаще всего теряешь себя?",
            "today": "Сформулируй одну границу одной спокойной фразой — без обвинений и оправданий.",
            "follow_up_prompt": _FOLLOW_UP_DEFAULT_PROMPT,
            "chips": [
                ("boundaries", "Прояснить границы"),
                ("talk", "Мягкий разговор"),
                ("distance", "Взять дистанцию"),
                ("care_self", "Позаботиться о себе"),
                ("unsure", "Пока не знаю"),
            ],
        },
        "growth_general": {
            "answer": (
                "Ты ищешь большой смысл — а сейчас нужен честный маленький шаг, "
                "который уже согласуется с тем, кем ты становишься."
            ),
            "story": (
                "Рост сейчас не про рывок. Он про то, чтобы перестать обесценивать то, "
                "что уже меняется — потому что это «недостаточно»."
            ),
            "holding": "Тебя держит сравнение с идеальной версией себя, которой «уже должно быть».",
            "shifting": "Ты начинаешь замечать реальные сдвиги — даже если они не выглядят эффектно.",
            "attention": "Что ты уже делаешь иначе, чем год назад — даже если это кажется мелочью?",
            "today": "Сделай один шаг в росте настолько маленький, что его нельзя отменить из страха.",
            "follow_up_prompt": _FOLLOW_UP_DEFAULT_PROMPT,
            "chips": [
                ("next_step", "Следующий шаг"),
                ("slow", "Замедлиться"),
                ("trust", "Довериться внутреннему"),
                ("new_view", "Новый взгляд"),
                ("unsure", "Пока не знаю"),
            ],
        },
        "inner_anxiety": {
            "answer": (
                "Тревога сейчас не про то, что случится что-то ужасное — "
                "а про то, что ты не контролируешь исход. И пытаешься компенсировать это мыслями."
            ),
            "story": (
                "Ты пытаешься просчитать всё заранее — но чем больше просчитываешь, тем меньше опоры. "
                "Тело уже знает, где перегруз. Уму просто сложнее это признать."
            ),
            "holding": "Тебя держит привычка жить в режиме «а что, если» — как будто от этого зависит безопасность.",
            "shifting": "Ты начинаешь замечать моменты, когда тревога — это сигнал, а не прогноз катастрофы.",
            "attention": "Когда тревога усиливается — ты ищешь контроль или опору?",
            "today": "Три раза за день остановись на 30 секунд и назови одно чувство. Без объяснений.",
            "follow_up_prompt": _FOLLOW_UP_DEFAULT_PROMPT,
            "chips": [
                ("rest", "Отдохнуть"),
                ("name_fear", "Назвать страх"),
                ("support", "Попросить опору"),
                ("slow_down", "Замедлиться"),
                ("unsure", "Пока не знаю"),
            ],
        },
        "inner_general": {
            "answer": (
                "Сейчас важнее не «исправить» состояние — "
                "а перестать требовать от себя, чтобы внутри сразу стало легко."
            ),
            "story": (
                "Ты устал быть сильным. Это не слабость — это сигнал, что ресурс на исходе, "
                "и тело просит честности раньше, чем разум готов признать."
            ),
            "holding": "Тебя держит ожидание, что «нормальный человек» должен справляться сам.",
            "shifting": "Появляется разрешение не дотягивать до идеала — хотя бы на сегодня.",
            "attention": "Что забирает больше сил: сама ситуация или то, как ты к себе относишься в ней?",
            "today": "Один раз в течение дня остановись и спроси себя: «чего мне сейчас на самом деле хочется?»",
            "follow_up_prompt": _FOLLOW_UP_DEFAULT_PROMPT,
            "chips": [
                ("rest", "Отдохнуть"),
                ("kindness", "Доброта к себе"),
                ("clarity", "Понять, что чувствую"),
                ("support", "Попросить опору"),
                ("unsure", "Пока не знаю"),
            ],
        },
        "general": {
            "answer": (
                "Ты ищешь ясный ответ снаружи — но сейчас важнее услышать то, "
                "что ты уже знаешь, и перестать требовать от этого идеальной формулировки."
            ),
            "story": (
                "Ты давно крутишь один и тот же вопрос. Это не слабость — "
                "это попытка не ошибиться. Но именно ожидание идеального ответа и забирает силы."
            ),
            "holding": "Тебя держит надежда, что появится вариант без потерь.",
            "shifting": "Ты начинаешь видеть, что движение возможно и без полной уверенности.",
            "attention": "Сколько раз за неделю ты возвращался к этому вопросу — и что искал в тот момент?",
            "today": "Запиши одной фразой, что ты уже понимаешь — без необходимости сразу действовать.",
            "follow_up_prompt": _FOLLOW_UP_DEFAULT_PROMPT,
            "chips": [
                ("clarity", "Стало понятнее"),
                ("same", "Пока без изменений"),
                ("new_questions", "Появились новые вопросы"),
                ("need_time", "Нужно время"),
            ],
        },
    }

    if intent in bundles:
        return bundles[intent]

    # Fallback chain: strip suffix, try theme
    base = intent.rsplit("_", 1)[0] if "_" in intent else intent
    for key in (intent, base, base + "_general", "general"):
        if key in bundles:
            return bundles[key]
    return bundles["general"]


def _compose_question_main_answer(
    question: str | None,
    card_insights: list[models.TarotCardInsight],
) -> str:
    q = (question or "").strip()
    if not card_insights:
        return _clean("Карты не дали конкретных линий — попробуй уточнить формулировку.")
    if len(card_insights) == 1:
        c = card_insights[0]
        lead = f"По твоему вопросу «{q}» — " if q else ""
        return _clean(
            f"{lead}{c.card_name_ru} в позиции «{c.position_label}» может означать: {c.line}."
        )
    a, b = card_insights[0], card_insights[1]
    lead = f"По твоему вопросу — " if q else ""
    return _clean(
        f"{lead}{a.card_name_ru} («{a.position_label}») указывает: {a.line}. "
        f"{b.card_name_ru} («{b.position_label}») добавляет: {b.line}."
    )


def _compose_question_story(
    question: str | None,
    card_insights: list[models.TarotCardInsight],
) -> str:
    """Relations between cards — not a dump of every position line."""
    if not card_insights:
        return ""
    if len(card_insights) == 1:
        c = card_insights[0]
        return _clean(f"Единственная опора расклада — {c.card_name_ru}: {c.line}.")
    head = card_insights[0]
    mid = card_insights[1]
    tail = card_insights[-1] if len(card_insights) > 2 else None
    parts = [
        f"{head.card_name_ru} задаёт тон («{head.position_label}»): {head.line}",
        f"{mid.card_name_ru} («{mid.position_label}») сдвигает картину: {mid.line}",
    ]
    if tail and tail is not mid and tail is not head:
        parts.append(
            f"Итог через {tail.card_name_ru} («{tail.position_label}»): {tail.line}"
        )
    body = ". ".join(parts)
    q = (question or "").strip()
    if q:
        return _clean(
            f"Карты отвечают на формулировку вопроса, а не на общий прогноз. {body}."
        )
    return _clean(f"Если читать расклад вместе: {body}.")


def _compose_question_insights(
    cards: list[models.TarotSpreadCard],
    card_insights: list[models.TarotCardInsight],
    *,
    question: str | None = None,
) -> tuple[str, str, str]:
    del question  # avoid repeating the question in every insight block
    holding = shifting = attention = ""

    for card, insight in zip(cards, card_insights):
        pos_id = (card.position.id if card.position else "").strip().lower()
        role = _position_role(pos_id)
        line = f"{insight.card_name_ru} («{insight.position_label}»): {insight.line}."
        if role == "holding" and not holding:
            holding = line
        elif role == "shifting" and not shifting:
            shifting = line
        elif role == "attention" and not attention:
            attention = line

    if not holding and card_insights:
        c = card_insights[0]
        holding = f"{c.card_name_ru}: {c.line}."
    if not shifting and len(card_insights) > 1:
        c = card_insights[1]
        shifting = f"{c.card_name_ru} («{c.position_label}»): {c.line}."
    if not attention and len(card_insights) > 2:
        c = card_insights[2]
        attention = f"{c.card_name_ru}: {c.line}."

    return _clean(holding), _clean(shifting), _clean(attention)


def _compose_card_context_reading(
    *,
    question: str | None,
    cards: list[models.TarotSpreadCard],
    card_insights: list[models.TarotCardInsight],
    bundle: _ReadingBundle,
) -> models.TarotSpreadReading:
    main_answer = _compose_question_main_answer(question, card_insights)
    story = _compose_question_story(question, card_insights)
    holding, shifting, attention = _compose_question_insights(
        cards, card_insights, question=question
    )

    anchor = card_insights[-1] if card_insights else None
    if anchor:
        today = (
            f"Сделай один шаг по линии {anchor.card_name_ru} "
            f"(«{anchor.position_label}»): заметь, где это откликается в жизни, "
            f"а не только в ожиданиях."
        )
    else:
        today = "Отметь, какая линия расклада откликается сильнее — и сделай один маленький шаг."

    chips = [models.TarotFollowUpChip(id=cid, label=label) for cid, label in bundle["chips"]]

    return models.TarotSpreadReading(
        meaning=main_answer,
        synthesis_why=story,
        insight_holding=holding,
        insight_shifting=shifting,
        insight_attention=attention,
        today_suggestion=today,
        follow_up_prompt=bundle["follow_up_prompt"],
        follow_up_chips=chips,
        card_insights=card_insights,
        manifestation="",
        caution="",
        next_step=today,
        actions_today=[today],
        self_question=None,
        profile_lens=None,
        profile_lens_applied=False,
    )


def _compose_choice_reading(
    *,
    question: str | None,
    cards: list[models.TarotSpreadCard],
    card_insights: list[models.TarotCardInsight],
    bundle: _ReadingBundle,
    concern_domain: str | None,
) -> tuple[models.TarotSpreadReading, dict[str, Any]]:
    built = engine.compose_choice_story(
        question=question,
        cards=cards,
        insights=card_insights,
        concern_domain=concern_domain,
    )
    chips = [models.TarotFollowUpChip(id=cid, label=label) for cid, label in bundle["chips"]]
    reading = models.TarotSpreadReading(
        meaning=built["direct_answer"],
        synthesis_why=built["story_narrative"],
        insight_holding=built["holding"],
        insight_shifting=built["shifting"],
        insight_attention=built["attention"],
        today_suggestion=built["today_suggestion"],
        follow_up_prompt=bundle["follow_up_prompt"],
        follow_up_chips=chips,
        card_insights=card_insights,
        manifestation="",
        caution="",
        next_step=built["today_suggestion"],
        actions_today=[built["today_suggestion"]],
        self_question=None,
        profile_lens=None,
        profile_lens_applied=False,
    )
    return reading, built["choice_story"]


def compose_question_first_reading(
    spread: models.TarotSpreadResult,
    *,
    question: str | None = None,
    concern_domain: str | None = None,
    consistency: dict | None = None,
    experience_slice: dict | None = None,
    core_profile: dict | None = None,
) -> models.TarotSpreadReading:
    """Compose reading. Attaches engine meta on the reading object for answer_v1 mapping."""
    del consistency  # orchestrator consistency is not Experience Contract SoI
    del core_profile  # Personal Model enters only via experience_slice
    cards = spread.cards or []
    theme = _detect_theme(question, concern_domain)
    intent = _detect_intent(question, theme)
    bundle = _bundle_for_intent(intent)

    unresolved = engine.collect_unresolved(cards)
    if unresolved:
        reading = engine.technical_fallback_reading(unresolved=unresolved)
        # Stash for tarot_answer_v1 (dynamic attrs — not in pydantic model).
        reading.__dict__["_engine_meta"] = {
            "synthesis_mode": engine.SYNTHESIS_MODE_BLOCKED,
            "synthesis_status": engine.STATUS_UNRESOLVED,
            "unresolved_cards": unresolved,
            "choice_story": None,
        }
        return reading

    card_insights = _build_card_insights(cards)
    assert card_insights is not None

    choice_story: dict[str, Any] | None = None
    if spread.spread_id in engine.CHOICE_SPREAD_IDS:
        reading, choice_story = _compose_choice_reading(
            question=question,
            cards=cards,
            card_insights=card_insights,
            bundle=bundle,
            concern_domain=concern_domain,
        )
    else:
        reading = _compose_card_context_reading(
            question=question,
            cards=cards,
            card_insights=card_insights,
            bundle=bundle,
        )

    today, lens, applied = engine.soft_profile_next_step(
        reading.today_suggestion or "",
        experience_slice,
    )
    if applied and lens:
        reading.profile_lens = lens
        reading.profile_lens_applied = True
        reading.today_suggestion = today
        reading.next_step = today
        reading.actions_today = [today]
        # Do NOT paste profile into insight_attention (canon §1).

    reading.__dict__["_engine_meta"] = {
        "synthesis_mode": engine.SYNTHESIS_MODE_OK,
        "synthesis_status": engine.STATUS_OK,
        "unresolved_cards": [],
        "choice_story": choice_story,
    }
    return reading

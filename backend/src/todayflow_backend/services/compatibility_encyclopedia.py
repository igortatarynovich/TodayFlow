"""Compatibility encyclopedia catalog — categories, readings, series with narrative intros."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

from todayflow_backend.services.compatibility_scenario_tone import (
    resolve_scenario_format,
    scenario_context_for_llm,
)

ENCYCLOPEDIA_VERSION = "encyclopedia-v1"


class EncyclopediaIntroBlock(BaseModel):
    kind: Literal["paragraph", "question", "bullet_list"] = "paragraph"
    text: str | None = None
    items: list[str] | None = None


class EncyclopediaAnalyzeParams(BaseModel):
    topic: str | None = None
    reading: str | None = None
    series: str | None = None


class EncyclopediaCategoryItem(BaseModel):
    id: str
    emoji: str
    title: str
    subtitle: str
    analyze_params: EncyclopediaAnalyzeParams
    intro_blocks: list[EncyclopediaIntroBlock] = Field(default_factory=list)


class EncyclopediaReadingItem(BaseModel):
    id: str
    title: str
    analyze_params: EncyclopediaAnalyzeParams
    intro_blocks: list[EncyclopediaIntroBlock] = Field(default_factory=list)


class EncyclopediaSeriesItem(BaseModel):
    id: str
    title: str
    subtitle: str
    analyze_params: EncyclopediaAnalyzeParams
    intro_blocks: list[EncyclopediaIntroBlock] = Field(default_factory=list)
    scenario_bullets: list[str] = Field(default_factory=list)


class EncyclopediaHero(BaseModel):
    eyebrow: str
    title: str
    lead: str


class CompatibilityEncyclopediaResponse(BaseModel):
    content_locale: str
    version: str
    hero: EncyclopediaHero
    categories: list[EncyclopediaCategoryItem]
    popular_readings: list[EncyclopediaReadingItem]
    series: list[EncyclopediaSeriesItem]
    entry_routes: dict[str, str]


def _loc(locale: str | None) -> str:
    base = (locale or "ru").strip().split("-")[0].lower()
    return "ru" if base == "ru" else "en"


def _t(ru: str, en: str, locale: str) -> str:
    return ru if locale == "ru" else en


def _p(text_ru: str, text_en: str, locale: str) -> EncyclopediaIntroBlock:
    return EncyclopediaIntroBlock(kind="paragraph", text=_t(text_ru, text_en, locale))


def _q(text_ru: str, text_en: str, locale: str) -> EncyclopediaIntroBlock:
    return EncyclopediaIntroBlock(kind="question", text=_t(text_ru, text_en, locale))


def _bullets(items_ru: list[str], items_en: list[str], locale: str) -> EncyclopediaIntroBlock:
    return EncyclopediaIntroBlock(kind="bullet_list", items=items_ru if locale == "ru" else items_en)


def build_compatibility_encyclopedia(locale: str | None = None) -> CompatibilityEncyclopediaResponse:
    loc = _loc(locale)

    hero = EncyclopediaHero(
        eyebrow=_t("Совместимость", "Compatibility", loc),
        title=_t(
            "Совместимость — это намного больше, чем любовь.",
            "Compatibility is much more than love.",
            loc,
        ),
        lead=_t(
            "Сегодня можно посмотреть, как два человека взаимодействуют в десятках жизненных ситуаций — от романтики до совместного бизнеса.",
            "See how two people interact across dozens of life situations — from romance to running a business together.",
            loc,
        ),
    )

    categories: list[EncyclopediaCategoryItem] = [
        EncyclopediaCategoryItem(
            id="love",
            emoji="❤️",
            title=_t("Любовь", "Love", loc),
            subtitle=_t("Притяжение, близость, романтика", "Attraction, closeness, romance", loc),
            analyze_params=EncyclopediaAnalyzeParams(topic="love"),
            intro_blocks=[
                _p(
                    "Любовная динамика — не один процент. Это то, как вы тянетесь друг к другу, где боитесь потерять контакт и что для каждого значит «быть рядом».",
                    "Romantic dynamics are not a single score. They are how you pull toward each other, where you fear losing contact, and what «being close» means to each of you.",
                    loc,
                ),
                _q("Что для тебя сейчас важнее — страсть или ощущение, что тебя выбирают?", "What matters more right now — passion or feeling chosen?", loc),
            ],
        ),
        EncyclopediaCategoryItem(
            id="living",
            emoji="🏡",
            title=_t("Совместная жизнь", "Living together", loc),
            subtitle=_t("Быт, дом, ритм двоих", "Home, routine, shared rhythm", loc),
            analyze_params=EncyclopediaAnalyzeParams(topic="living_together"),
            intro_blocks=[
                _p(
                    "Совместный быт быстро показывает, совпадают ли ваши ритмы: сон, деньги, порядок, тишина и право на личное пространство.",
                    "Shared life quickly reveals whether your rhythms match: sleep, money, order, silence, and the right to personal space.",
                    loc,
                ),
            ],
        ),
        EncyclopediaCategoryItem(
            id="work",
            emoji="💼",
            title=_t("Работа", "Work", loc),
            subtitle=_t("Роли, темп, решения", "Roles, pace, decisions", loc),
            analyze_params=EncyclopediaAnalyzeParams(topic="work"),
            intro_blocks=[
                _p(
                    "Рабочая совместимость — про ясные роли: кто инициирует, кто доводит до конца, как вы спорите о решениях и не смешиваете личное с профессиональным.",
                    "Work compatibility is about clear roles: who initiates, who finishes, how you argue about decisions without mixing personal and professional.",
                    loc,
                ),
            ],
        ),
        EncyclopediaCategoryItem(
            id="friendship",
            emoji="🤝",
            title=_t("Дружба", "Friendship", loc),
            subtitle=_t("Опора, доверие, лёгкость", "Support, trust, ease", loc),
            analyze_params=EncyclopediaAnalyzeParams(topic="friendship"),
            intro_blocks=[
                _p(
                    "Дружба держится на честности без давления: можно ли быть собой, не объясняя каждый шаг, и остаётся ли контакт живым без романтического сценария.",
                    "Friendship rests on honesty without pressure: can you be yourself without explaining every move, and does contact stay alive without a romantic script?",
                    loc,
                ),
            ],
        ),
        EncyclopediaCategoryItem(
            id="sex",
            emoji="🔥",
            title=_t("Секс", "Sex", loc),
            subtitle=_t("Желание, телесность, интим", "Desire, body, intimacy", loc),
            analyze_params=EncyclopediaAnalyzeParams(topic="sex"),
            intro_blocks=[
                _p(
                    "Интим — отдельный язык: темп, инициатива, безопасность и то, что остаётся невысказанным. Здесь важнее честность, чем «идеальная гармония».",
                    "Intimacy is its own language: pace, initiative, safety, and what stays unspoken. Honesty matters more than «perfect harmony» here.",
                    loc,
                ),
            ],
        ),
        EncyclopediaCategoryItem(
            id="money",
            emoji="💰",
            title=_t("Деньги", "Money", loc),
            subtitle=_t("Ресурсы, приоритеты, риски", "Resources, priorities, risks", loc),
            analyze_params=EncyclopediaAnalyzeParams(topic="money"),
            intro_blocks=[
                _p(
                    "Деньги в паре — почти всегда про безопасность и контроль. Кто тратит на импульс, кто копит «на чёрный день», и где вы договариваетесь, а где молчите.",
                    "Money in a pair is almost always about safety and control. Who spends on impulse, who saves for a rainy day, and where you negotiate versus stay silent.",
                    loc,
                ),
            ],
        ),
        EncyclopediaCategoryItem(
            id="parenting",
            emoji="👶",
            title=_t("Родительство", "Parenting", loc),
            subtitle=_t("Дети, границы, поддержка", "Children, boundaries, support", loc),
            analyze_params=EncyclopediaAnalyzeParams(topic="parenting"),
            intro_blocks=[
                _p(
                    "Родительство усиливает всё: усталость, ответственность, разные модели «как правильно». Здесь важны роли, а не только любовь к ребёнку.",
                    "Parenting amplifies everything: fatigue, responsibility, different models of «what's right». Roles matter here, not only love for the child.",
                    loc,
                ),
            ],
        ),
        EncyclopediaCategoryItem(
            id="travel",
            emoji="✈️",
            title=_t("Путешествия", "Travel", loc),
            subtitle=_t("Совместный ритм и свобода", "Shared rhythm and freedom", loc),
            analyze_params=EncyclopediaAnalyzeParams(topic="travel"),
            intro_blocks=[
                _p(
                    "Путешествие — мини-модель пары: планы, спонтанность, усталость, бюджет и «кому нужна тишина». Здесь быстро видно, кто ведёт, а кто подстраивается.",
                    "Travel is a mini-model of the pair: plans, spontaneity, fatigue, budget, and «who needs silence». You quickly see who leads and who adapts.",
                    loc,
                ),
            ],
        ),
        EncyclopediaCategoryItem(
            id="conflicts",
            emoji="⚡",
            title=_t("Конфликты", "Conflicts", loc),
            subtitle=_t("Ссоры, триггеры, примирение", "Fights, triggers, reconciliation", loc),
            analyze_params=EncyclopediaAnalyzeParams(topic="conflicts"),
            intro_blocks=[
                _p(
                    "Конфликт — не поломка. Это способ, которым пара пытается донести неудовлетворённую потребность. Важно не «кто прав», а что повторяется и как вы миритесь.",
                    "Conflict is not a breakdown. It is how a pair tries to convey an unmet need. What repeats and how you reconcile matters more than «who is right».",
                    loc,
                ),
            ],
        ),
        EncyclopediaCategoryItem(
            id="communication",
            emoji="🎭",
            title=_t("Общение", "Communication", loc),
            subtitle=_t("Слова, паузы, недосказанность", "Words, pauses, what stays unsaid", loc),
            analyze_params=EncyclopediaAnalyzeParams(topic="communication"),
            intro_blocks=[
                _p(
                    "Общение — не только слова. Это паузы, интонации, юмор вместо разговора и моменты, когда один говорит факты, а другой ждёт эмпатии.",
                    "Communication is not only words. It is pauses, tone, humor instead of talk, and moments when one speaks facts while the other waits for empathy.",
                    loc,
                ),
            ],
        ),
        EncyclopediaCategoryItem(
            id="emotional",
            emoji="🌙",
            title=_t("Эмоциональная связь", "Emotional bond", loc),
            subtitle=_t("Безопасность, уязвимость", "Safety, vulnerability", loc),
            analyze_params=EncyclopediaAnalyzeParams(topic="emotional"),
            intro_blocks=[
                _p(
                    "Эмоциональная близость — про безопасность: можно ли показать слабость, не потеряв уважение, и чувствует ли каждый, что его состояние замечают.",
                    "Emotional closeness is about safety: can you show weakness without losing respect, and does each person feel their state is noticed?",
                    loc,
                ),
            ],
        ),
        EncyclopediaCategoryItem(
            id="growth",
            emoji="📈",
            title=_t("Рост друг друга", "Mutual growth", loc),
            subtitle=_t("Вдохновение и развитие", "Inspiration and development", loc),
            analyze_params=EncyclopediaAnalyzeParams(topic="growth"),
            intro_blocks=[
                _p(
                    "Рост в паре — когда рядом хочется становиться больше, а не только удобнее. Здесь смотрим, кто вдохновляет, кто тормозит из страха перемен.",
                    "Growth in a pair is when you want to become more beside someone, not only more comfortable. We look at who inspires and who slows change from fear.",
                    loc,
                ),
            ],
        ),
    ]

    readings: list[EncyclopediaReadingItem] = [
        EncyclopediaReadingItem(
            id="opposites",
            title=_t("Почему противоположности притягиваются?", "Why do opposites attract?", loc),
            analyze_params=EncyclopediaAnalyzeParams(reading="opposites"),
            intro_blocks=[
                _p(
                    "Притяжение «противоположностей» часто про компенсацию: один несёт то, чего другому не хватает. Вопрос — это дополнение или вечный конфликт темпов.",
                    "«Opposite» attraction is often compensation: one carries what the other lacks. The question is complement or endless clash of rhythms.",
                    loc,
                ),
            ],
        ),
        EncyclopediaReadingItem(
            id="reconcile",
            title=_t("Кто чаще делает первый шаг после ссоры?", "Who reconciles first after a fight?", loc),
            analyze_params=EncyclopediaAnalyzeParams(reading="reconcile"),
            intro_blocks=[
                _p(
                    "Примирение — не слабость. Это стиль: кто быстрее не выдерживает дистанцию, кто ждёт жеста, кто уходит в молчание «пока не пройдёт».",
                    "Reconciliation is not weakness. It is a style: who can't stand distance, who waits for a gesture, who goes silent «until it passes».",
                    loc,
                ),
            ],
        ),
        EncyclopediaReadingItem(
            id="decisions",
            title=_t("Кто принимает решения?", "Who makes the decisions?", loc),
            analyze_params=EncyclopediaAnalyzeParams(reading="decisions"),
            intro_blocks=[_p("В каждой паре есть невидимый «дирижёр» — не всегда тот, кто громче.", "Every pair has an invisible «conductor» — not always the louder one.", loc)],
        ),
        EncyclopediaReadingItem(
            id="money_control",
            title=_t("Кто распоряжается деньгами?", "Who controls the money?", loc),
            analyze_params=EncyclopediaAnalyzeParams(reading="money_control"),
            intro_blocks=[_p("Деньги часто становятся языком власти или заботы — важно понять, какой это язык у вас.", "Money often becomes a language of power or care — it helps to see which yours is.", loc)],
        ),
        EncyclopediaReadingItem(
            id="fatigue",
            title=_t("Кто быстрее устаёт друг от друга?", "Who tires of the other first?", loc),
            analyze_params=EncyclopediaAnalyzeParams(reading="fatigue"),
            intro_blocks=[_p("Усталость от близости — сигнал о темпе, границах или нерешённом напряжении.", "Fatigue from closeness signals pace, boundaries, or unresolved tension.", loc)],
        ),
        EncyclopediaReadingItem(
            id="passion",
            title=_t("У кого выше страсть?", "Who carries more passion?", loc),
            analyze_params=EncyclopediaAnalyzeParams(reading="passion"),
            intro_blocks=[_p("Страсть неравномерна — важно, как пара переводит разницу в язык, а не в обиду.", "Passion is uneven — what matters is translating difference into language, not hurt.", loc)],
        ),
        EncyclopediaReadingItem(
            id="work_together",
            title=_t("Кто лучше работает вместе?", "Who works better together?", loc),
            analyze_params=EncyclopediaAnalyzeParams(reading="work_together"),
            intro_blocks=[_p("Совместная работа проверяет роли быстрее, чем романтические свидания.", "Working together tests roles faster than romantic dates.", loc)],
        ),
        EncyclopediaReadingItem(
            id="inspire",
            title=_t("Кто кого вдохновляет?", "Who inspires whom?", loc),
            analyze_params=EncyclopediaAnalyzeParams(reading="inspire"),
            intro_blocks=[_p("Вдохновение — когда рядом хочется расширяться, а не только успокаиваться.", "Inspiration is wanting to expand beside someone, not only be soothed.", loc)],
        ),
        EncyclopediaReadingItem(
            id="love_language",
            title=_t("Какой у пары язык любви?", "What is the pair's love language?", loc),
            analyze_params=EncyclopediaAnalyzeParams(reading="love_language"),
            intro_blocks=[_p("Язык любви — не абстракция, а конкретные жесты, которые каждый считывает как «меня выбирают».", "Love language is not abstract — it is the gestures each reads as «I am chosen».", loc)],
        ),
        EncyclopediaReadingItem(
            id="responsibility",
            title=_t("Кто берёт ответственность?", "Who takes responsibility?", loc),
            analyze_params=EncyclopediaAnalyzeParams(reading="responsibility"),
            intro_blocks=[_p("Ответственность в паре — кто закрывает хвосты, кто инициирует сложные разговоры.", "Responsibility in a pair — who closes loose ends, who starts hard talks.", loc)],
        ),
    ]

    series: list[EncyclopediaSeriesItem] = [
        EncyclopediaSeriesItem(
            id="living_together",
            title="Living Together",
            subtitle=_t("Быт, границы, ритм дома", "Home, boundaries, domestic rhythm", loc),
            analyze_params=EncyclopediaAnalyzeParams(series="living_together"),
            intro_blocks=[
                _p(
                    "Серия про совместный дом: не романтику на старте, а реальность — посуда, сон, гости, личное пространство.",
                    "A series on shared home: not opening romance, but reality — dishes, sleep, guests, personal space.",
                    loc,
                ),
            ],
            scenario_bullets=_t(
                ["Кто убирает «по настроению», а кому нужен порядок?", "Как делите тишину и шум?", "Где проходит граница «мой угол»?"],
                ["Who cleans «when they feel like it» versus who needs order?", "How do you split silence and noise?", "Where is the «my corner» boundary?"],
                loc,
            ),
        ),
        EncyclopediaSeriesItem(
            id="office",
            title="Office Compatibility",
            subtitle=_t("Работа, роли, давление", "Work, roles, pressure", loc),
            analyze_params=EncyclopediaAnalyzeParams(series="office"),
            intro_blocks=[_p("Офисная динамика: дедлайны, статус, критика и поддержка под нагрузкой.", "Office dynamics: deadlines, status, criticism and support under pressure.", loc)],
            scenario_bullets=_t(
                ["Кто берёт публичную часть, кто — детали?", "Как спорите, когда горят сроки?"],
                ["Who takes the public face, who the details?", "How do you argue when deadlines burn?"],
                loc,
            ),
        ),
        EncyclopediaSeriesItem(
            id="partner_in_crime",
            title="Partner in Crime",
            subtitle=_t("Авантюры, риск, азарт", "Adventures, risk, thrill", loc),
            analyze_params=EncyclopediaAnalyzeParams(series="partner_in_crime"),
            intro_blocks=[_p("Серия про пару-соучастника: риск, импульс, «давай попробуем» и цена безрассудства.", "The co-conspirator pair: risk, impulse, «let's try» and the cost of recklessness.", loc)],
            scenario_bullets=_t(["Где азарт сближает?", "Где нужен «взрослый тормоз»?"], ["Where does thrill bring you closer?", "Where do you need a «grown-up brake»?"], loc),
        ),
        EncyclopediaSeriesItem(
            id="vacation",
            title="Vacation Together",
            subtitle=_t("Отдых, свобода, ожидания", "Rest, freedom, expectations", loc),
            analyze_params=EncyclopediaAnalyzeParams(series="vacation"),
            intro_blocks=[_p("Отпуск показывает, совпадают ли ваши «хочу отдыхать».", "Vacation shows whether your «how I want to rest» align.", loc)],
            scenario_bullets=_t(["План vs спонтанность", "Бюджет и импульсные траты"], ["Plan vs spontaneity", "Budget and impulse spending"], loc),
        ),
        EncyclopediaSeriesItem(
            id="business",
            title="Business Partners",
            subtitle=_t("Деньги, решения, ответственность", "Money, decisions, accountability", loc),
            analyze_params=EncyclopediaAnalyzeParams(series="business"),
            intro_blocks=[_p("Бизнес-партнёрство — про договорённости, которые переживают стресс.", "Business partnership is about agreements that survive stress.", loc)],
            scenario_bullets=_t(["Кто финальное «да»?", "Как делите риск?"], ["Who gives final «yes»?", "How do you split risk?"], loc),
        ),
        EncyclopediaSeriesItem(
            id="conflict_style",
            title="Conflict Style",
            subtitle=_t("Ссоры, паузы, примирение", "Fights, pauses, reconciliation", loc),
            analyze_params=EncyclopediaAnalyzeParams(series="conflict_style"),
            intro_blocks=[_p("Стиль конфликта — ваш «родной язык ссоры» и путь обратно.", "Conflict style is your native «fight language» and the way back.", loc)],
            scenario_bullets=_t(["Кто эскалирует, кто замирает?", "Что помогает помириться?"], ["Who escalates, who freezes?", "What helps you reconcile?"], loc),
        ),
        EncyclopediaSeriesItem(
            id="parenting",
            title="Parenting",
            subtitle=_t("Дети, опора, границы", "Children, support, boundaries", loc),
            analyze_params=EncyclopediaAnalyzeParams(series="parenting"),
            intro_blocks=[_p("Родительство как серия — роли «строгий / мягкий», усталость, единый фронт.", "Parenting as a series — strict/soft roles, fatigue, united front.", loc)],
            scenario_bullets=_t(["Кто дисциплинирует?", "Как делите «выходной от детей»?"], ["Who disciplines?", "How do you split «time off from kids»?"], loc),
        ),
        EncyclopediaSeriesItem(
            id="money_together",
            title="Money Together",
            subtitle=_t("Бюджет, приоритеты, страхи", "Budget, priorities, fears", loc),
            analyze_params=EncyclopediaAnalyzeParams(series="money_together"),
            intro_blocks=[_p("Деньги вместе — про прозрачность, стыд и сценарии из семьи происхождения.", "Money together — transparency, shame, and scripts from family of origin.", loc)],
            scenario_bullets=_t(["Общий счёт или раздельный?", "Крупные траты — как согласуете?"], ["Joint or separate accounts?", "Large purchases — how do you agree?"], loc),
        ),
        EncyclopediaSeriesItem(
            id="love_languages",
            title="Love Languages",
            subtitle=_t("Как вы чувствуете близость", "How you feel closeness", loc),
            analyze_params=EncyclopediaAnalyzeParams(series="love_languages"),
            intro_blocks=[_p("Языки любви — не тест, а наблюдение: что каждый считает знаком «меня любят».", "Love languages are not a quiz — they are what each reads as «I am loved».", loc)],
            scenario_bullets=_t(["Слова, время, прикосновения, забота, подарки — что главное?"], ["Words, time, touch, care, gifts — what is primary?"], loc),
        ),
        EncyclopediaSeriesItem(
            id="emotional",
            title="Emotional Compatibility",
            subtitle=_t("Чувства, безопасность, дистанция", "Feelings, safety, distance", loc),
            analyze_params=EncyclopediaAnalyzeParams(series="emotional"),
            intro_blocks=[_p("Эмоциональная совместимость — насколько безопасно быть уязвимым рядом.", "Emotional compatibility — how safe it is to be vulnerable beside each other.", loc)],
            scenario_bullets=_t(["Кто первым называет чувство?", "Как вы переживаете дистанцию?"], ["Who names the feeling first?", "How do you handle distance?"], loc),
        ),
        EncyclopediaSeriesItem(
            id="apocalypse",
            title="Apocalypse",
            subtitle=_t("Кризис, стресс, выживание вместе", "Crisis, stress, surviving together", loc),
            analyze_params=EncyclopediaAnalyzeParams(series="apocalypse"),
            intro_blocks=[
                _p(
                    "Серия Apocalypse — не фатализм. Это «что с нами под максимальным стрессом»: переезд, потеря, болезнь, предательство.",
                    "Apocalypse is not fatalism. It is «what happens to us under maximum stress»: move, loss, illness, betrayal.",
                    loc,
                ),
            ],
            scenario_bullets=_t(["Кто держит фронт?", "Где ломается доверие?"], ["Who holds the front?", "Where does trust break?"], loc),
        ),
        EncyclopediaSeriesItem(
            id="after_wine",
            title=_t("После бокала вина", "After a Glass of Wine", loc),
            subtitle=_t("Честность, флирт и смешные решения", "Honesty, flirt, silly decisions", loc),
            analyze_params=EncyclopediaAnalyzeParams(series="after_wine"),
            intro_blocks=[
                _p(
                    "Это не про алкоголь как проблему — а про то, как пара меняется, когда фильтры ослабевают.",
                    "Not about alcohol as a problem — but how the pair shifts when filters loosen.",
                    loc,
                ),
            ],
            scenario_bullets=_t(
                ["Кто первым говорит лишнее?", "Кто потом всё объясняет?"],
                ["Who says too much first?", "Who explains it all later?"],
                loc,
            ),
        ),
        EncyclopediaSeriesItem(
            id="home_renovation",
            title=_t("Ремонт квартиры", "Apartment Renovation", loc),
            subtitle=_t("Плитка, сроки, нервы", "Tiles, deadlines, nerves", loc),
            analyze_params=EncyclopediaAnalyzeParams(series="home_renovation"),
            intro_blocks=[
                _p(
                    "Ремонт — стресс-тест пары: кто выбирает плитку три недели, кто сдаётся на второй день.",
                    "Renovation stress-tests a pair: who picks tile for three weeks, who quits on day two.",
                    loc,
                ),
            ],
            scenario_bullets=_t(
                ["Кто контролирует бюджет?", "Кто говорит «и так сойдёт»?"],
                ["Who controls the budget?", "Who says «good enough»?"],
                loc,
            ),
        ),
        EncyclopediaSeriesItem(
            id="best_friends",
            title=_t("Лучшие друзья", "Best Friends", loc),
            subtitle=_t("Без романтики — но с химией", "No romance — but chemistry", loc),
            analyze_params=EncyclopediaAnalyzeParams(series="best_friends"),
            intro_blocks=[
                _p(
                    "Что если между вами дружба, а не любовь? Смотрим опору, подколы и границы — без навязанного «вы пара».",
                    "What if it's friendship, not romance? Support, teasing, boundaries — without forced «you're a couple».",
                    loc,
                ),
            ],
            scenario_bullets=_t(
                ["Кто первым звонит в кризис?", "Где проходит граница «мы только друзья»?"],
                ["Who do you call first in crisis?", "Where is the «just friends» line?"],
                loc,
            ),
        ),
        EncyclopediaSeriesItem(
            id="rule_breaker",
            title=_t("Кто нарушит правила", "Who Breaks the Rules First", loc),
            subtitle=_t("Договорённости, сроки, «мы так решили»", "Agreements, deadlines, «we decided»", loc),
            analyze_params=EncyclopediaAnalyzeParams(series="rule_breaker"),
            intro_blocks=[
                _p(
                    "Игровой сценарий: кто первым нарушит правило — опоздание, трата, обещание. Ставки приняты.",
                    "Playful scenario: who breaks the rule first — lateness, spending, a promise. Bets are on.",
                    loc,
                ),
            ],
            scenario_bullets=_t(
                ["Кто «ещё пять минут»?", "Кто потом делает вид, что так и было?"],
                ["Who says «five more minutes»?", "Who pretends it was always the plan?"],
                loc,
            ),
        ),
    ]

    return CompatibilityEncyclopediaResponse(
        content_locale=loc,
        version=ENCYCLOPEDIA_VERSION,
        hero=hero,
        categories=categories,
        popular_readings=readings,
        series=series,
        entry_routes={
            "analyze": "/compatibility/analyze",
            "signs": "/compatibility/signs",
            "birthdates": "/compatibility/birthdates",
            "profiles": "/compatibility",
        },
    )


_TOPIC_CONTEXT: dict[str, str] = {
    "love": "in_relationship",
    "living_together": "in_relationship",
    "conflicts": "conflict_distance",
    "sex": "mutual_attraction",
    "friendship": "just_met",
    "work": "unspecified",
    "money": "in_relationship",
    "parenting": "in_relationship",
    "travel": "in_relationship",
    "communication": "unclear",
    "emotional": "in_relationship",
    "growth": "in_relationship",
}

_READING_CONTEXT: dict[str, str] = {
    "reconcile": "conflict_distance",
    "passion": "mutual_attraction",
    "opposites": "mutual_attraction",
}


def resolve_encyclopedia_selection(
    *,
    topic_id: str | None,
    reading_id: str | None,
    series_id: str | None,
    locale: str | None,
) -> dict[str, Any] | None:
    """Map encyclopedia selection to dynamics context: intro paragraphs, scenario, relationship hint."""
    loc = _loc(locale)
    catalog = build_compatibility_encyclopedia(loc)

    selection_label: str | None = None
    intro_blocks: list[EncyclopediaIntroBlock] = []
    scenario_bullets: list[str] = []
    relationship_context: str | None = None

    if topic_id:
        item = next((c for c in catalog.categories if c.id == topic_id), None)
        if not item and topic_id == "living":
            item = next((c for c in catalog.categories if c.id == "living"), None)
        if item:
            selection_label = item.title
            intro_blocks = item.intro_blocks
            relationship_context = _TOPIC_CONTEXT.get(topic_id) or _TOPIC_CONTEXT.get(item.analyze_params.topic or "")
    if reading_id:
        item = next((r for r in catalog.popular_readings if r.id == reading_id), None)
        if item:
            selection_label = item.title
            intro_blocks = item.intro_blocks or intro_blocks
            relationship_context = relationship_context or _READING_CONTEXT.get(reading_id)
    if series_id:
        item = next((s for s in catalog.series if s.id == series_id), None)
        if item:
            selection_label = item.title
            intro_blocks = item.intro_blocks or intro_blocks
            scenario_bullets = item.scenario_bullets

    if not selection_label and not intro_blocks and not scenario_bullets:
        return None

    tone_spec = resolve_scenario_format(
        topic_id=topic_id,
        reading_id=reading_id,
        series_id=series_id,
    )

    intro_paragraphs: list[str] = []
    for block in intro_blocks:
        if block.kind == "paragraph" and block.text:
            intro_paragraphs.append(block.text)
        elif block.kind == "question" and block.text:
            intro_paragraphs.append(block.text if block.text.endswith("?") else f"{block.text}?")
        elif block.kind == "bullet_list" and block.items:
            intro_paragraphs.append(" · ".join(block.items[:4]))

    return {
        "selection_id": topic_id or reading_id or series_id,
        "selection_kind": "topic" if topic_id else "reading" if reading_id else "series",
        "selection_label": selection_label,
        "relationship_context": relationship_context,
        "intro_paragraphs": intro_paragraphs,
        "scenario_bullets": scenario_bullets,
        "format_id": tone_spec.format_id,
        "tone_family": tone_spec.tone_family,
        "tone_mode": tone_spec.tone_mode,
        "scenario_context": scenario_context_for_llm(tone_spec, locale=loc),
    }


def apply_encyclopedia_to_product_surface(product_surface, selection: dict[str, Any] | None):
    """Prepend encyclopedia intro and inject scenario group into product surface (mutates copy)."""
    if not selection:
        return product_surface
    if selection.get("tone_mode") == "playful":
        # Playful scenarios use short stat-card UI — no long encyclopedia intros on the surface.
        return product_surface
    intro = selection.get("intro_paragraphs") or []
    if intro:
        existing = list(product_surface.overview_paragraphs or [])
        product_surface.overview_paragraphs = intro + existing
    bullets = selection.get("scenario_bullets") or []
    label = selection.get("selection_label") or "Scenario"
    if bullets:
        from todayflow_backend.services.sign_compatibility_product import SignCompatScenarioGroup

        scenario = SignCompatScenarioGroup(id=str(selection.get("selection_id") or "encyclopedia"), title=str(label), bullets=bullets)
        scenarios = list(product_surface.scenarios or [])
        product_surface.scenarios = [scenario] + scenarios
    return product_surface

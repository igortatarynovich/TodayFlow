"""State-cycle Practices catalog enrichment (need / format / outcome).

SoT overlay for GENERAL free practices + rich gap-fill library.
Canon: docs/practices/PRACTICES_SCREEN_V1.md (§1 needs, §2 formats, §3.3 outcome-first).

Public JSON (optional, backward compatible):
  need_ids: list[str]
  format_id: str | None
  outcome_label: str | None
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

STATE_CYCLE_NEED_IDS: tuple[str, ...] = (
    "calm",
    "focus",
    "recover",
    "body",
    "understand",
    "sleep",
)

STATE_CYCLE_FORMAT_IDS: tuple[str, ...] = (
    "meditation",
    "breath",
    "yoga",
    "stretch",
    "visualization",
    "affirmation",
    "reflection",
    "music",
    "sleep",
)

# Overlay for existing GENERAL practice ids.
STATE_CYCLE_META: dict[str, dict[str, Any]] = {
    "breathing-4-7-8": {
        "need_ids": ["calm", "sleep"],
        "format_id": "breath",
        "outcome_label": "Снизить тревожность",
    },
    "body-scan": {
        "need_ids": ["body", "calm", "recover"],
        "format_id": "meditation",
        "outcome_label": "Почувствовать тело",
    },
    "gratitude-list": {
        "need_ids": ["understand", "calm"],
        "format_id": "reflection",
        "outcome_label": "Заметить опору",
    },
    "box-breathing": {
        "need_ids": ["focus", "calm"],
        "format_id": "breath",
        "outcome_label": "Собрать внимание",
    },
    "morning-intention": {
        "need_ids": ["focus", "understand"],
        "format_id": "affirmation",
        "outcome_label": "Задать направление дня",
    },
    "loving-kindness-meditation": {
        "need_ids": ["calm", "recover", "understand"],
        "format_id": "meditation",
        "outcome_label": "Смягчить отношение к себе",
    },
    "alternate-nostril-breathing": {
        "need_ids": ["focus", "calm", "recover"],
        "format_id": "breath",
        "outcome_label": "Выровнять энергию",
    },
    "walking-meditation": {
        "need_ids": ["body", "focus", "calm"],
        "format_id": "meditation",
        "outcome_label": "Вернуться в шаг",
    },
    "kapalabhati-breathing": {
        "need_ids": ["recover", "focus"],
        "format_id": "breath",
        "outcome_label": "Пробудить ясность",
    },
    "mindful-eating": {
        "need_ids": ["body", "understand"],
        "format_id": "meditation",
        "outcome_label": "Замедлить контакт с едой",
    },
    "deep-breathing-relaxation": {
        "need_ids": ["calm", "recover", "sleep"],
        "format_id": "breath",
        "outcome_label": "Снять напряжение",
    },
}


def _new_practice(
    *,
    id: str,
    title: str,
    description: str,
    category: str,
    duration_minutes: int,
    tags: list[str],
    need_ids: list[str],
    format_id: str,
    outcome_label: str,
    instructions: list[str],
    difficulty: str = "beginner",
) -> dict[str, Any]:
    return {
        "id": id,
        "title": title,
        "description": description,
        "category": category,
        "duration_minutes": duration_minutes,
        "difficulty": difficulty,
        "is_free": True,
        "is_personalized": False,
        "access_level": "free",
        "tags": tags,
        "need_ids": need_ids,
        "format_id": format_id,
        "outcome_label": outcome_label,
        "instructions": instructions,
    }


# Rich free library: every need has several paths; every format has dedicated entries.
NEW_STATE_CYCLE_PRACTICES: list[dict[str, Any]] = [
    # —— calm ——
    _new_practice(
        id="tension-release-3",
        title="Снять напряжение",
        description="Короткое дыхание с мягким отпусканием плеч и челюсти",
        category="breathing",
        duration_minutes=7,
        tags=["спокойствие", "дыхание", "зажим"],
        need_ids=["calm"],
        format_id="breath",
        outcome_label="Отпустить зажим",
        instructions=[
            "Сядьте удобно, стопы на полу",
            "На вдохе слегка поднимите плечи",
            "На длинном выдохе опустите плечи и расслабьте челюсть",
            "Повторите 8–10 циклов",
            "В конце заметьте одно место, где стало мягче",
        ],
    ),
    _new_practice(
        id="hand-on-heart-calm",
        title="Ладонь на сердце",
        description="Мягкий контакт с телом, чтобы снизить внутренний шум",
        category="meditation",
        duration_minutes=4,
        tags=["спокойствие", "тело", "опора"],
        need_ids=["calm", "body"],
        format_id="meditation",
        outcome_label="Успокоить через контакт",
        instructions=[
            "Положите ладонь на грудь",
            "Почувствуйте тепло и дыхание под рукой",
            "Сделайте 8 медленных выдохов длиннее вдоха",
            "Скажите себе: «Я могу быть здесь мягко»",
        ],
    ),
    _new_practice(
        id="soft-gaze-pause",
        title="Мягкий взгляд",
        description="Пауза внимания: взгляд на одну точку без усилия",
        category="meditation",
        duration_minutes=3,
        tags=["спокойствие", "фокус", "пауза"],
        need_ids=["calm", "focus"],
        format_id="meditation",
        outcome_label="Остановить разгон",
        instructions=[
            "Выберите спокойную точку перед собой",
            "Смотрите мягко, не вглядываясь",
            "Когда мысли уводят — возвращайте взгляд",
            "Завершите одним длинным выдохом",
        ],
    ),
    _new_practice(
        id="volume-imagination",
        title="Объёмное воображение",
        description="Мягкая практика для развития креативности и внутреннего видения",
        category="meditation",
        duration_minutes=12,
        tags=["визуализация", "спокойствие", "воображение"],
        need_ids=["calm", "focus"],
        format_id="visualization",
        outcome_label="Убавить внутренний шум",
        instructions=[
            "Закройте глаза и представьте пространство вокруг себя",
            "Заметьте «громкость» внутреннего шума",
            "Медленно убавьте её с каждым выдохом",
            "Позвольте появиться одному спокойному образу",
            "Побудьте в нём 1–2 минуты",
        ],
    ),
    _new_practice(
        id="self-ground-affirmation",
        title="Опора в себе",
        description="Короткая аффирмация для мягкой устойчивости",
        category="affirmation",
        duration_minutes=3,
        tags=["аффирмация", "опора", "спокойствие"],
        need_ids=["calm", "recover"],
        format_id="affirmation",
        outcome_label="Вернуть опору",
        instructions=[
            "Поставьте стопы на пол",
            "Скажите тихо: «Я здесь. Я могу быть с собой мягко.»",
            "Повторите фразу 5 раз на выдохе",
            "Заметьте одно ощущение опоры в теле",
        ],
    ),
    # —— focus ——
    _new_practice(
        id="focus-return-4",
        title="Возврат фокуса",
        description="Короткая медитация возвращения внимания к одному якорю",
        category="meditation",
        duration_minutes=4,
        tags=["фокус", "медитация", "внимание"],
        need_ids=["focus"],
        format_id="meditation",
        outcome_label="Вернуть внимание",
        instructions=[
            "Выберите якорь: дыхание или точка на стене",
            "Держите внимание на якоре около минуты",
            "Когда ум уйдёт — мягко верните без оценки",
            "Завершите одним ясным намерением на следующий час",
        ],
    ),
    _new_practice(
        id="single-task-anchor",
        title="Один якорь задачи",
        description="Собрать внимание вокруг одной конкретной задачи",
        category="ritual",
        duration_minutes=5,
        tags=["фокус", "работа", "ясность"],
        need_ids=["focus"],
        format_id="affirmation",
        outcome_label="Выбрать одну задачу",
        instructions=[
            "Назовите одну задачу на ближайшие 25 минут",
            "Запишите её одной строкой",
            "Уберите лишние вкладки или предметы со стола",
            "Сделайте три спокойных вдоха и начните",
        ],
    ),
    _new_practice(
        id="desk-reset-breath",
        title="Сброс за столом",
        description="Дыхательный сброс, чтобы вернуться в работу без суеты",
        category="breathing",
        duration_minutes=3,
        tags=["фокус", "дыхание", "работа"],
        need_ids=["focus", "recover"],
        format_id="breath",
        outcome_label="Собраться за столом",
        instructions=[
            "Сядьте прямо, руки на столе",
            "Сделайте 4 вдоха носом и 6 медленных выдохов",
            "На выдохе мягко опустите плечи",
            "Откройте глаза и назовите следующий шаг",
        ],
    ),
    _new_practice(
        id="name-one-priority",
        title="Назвать приоритет",
        description="Рефлексия: что сейчас действительно важно",
        category="reflection",
        duration_minutes=6,
        tags=["фокус", "рефлексия", "приоритет"],
        need_ids=["focus", "understand"],
        format_id="reflection",
        outcome_label="Прояснить приоритет",
        instructions=[
            "Спросите себя: «Что важно именно сейчас?»",
            "Запишите три варианта без цензуры",
            "Вычеркните два менее важных",
            "Оставьте один и назовите первый шаг",
        ],
    ),
    # —— recover ——
    _new_practice(
        id="energy-reset-breath",
        title="Дыхание перезагрузки",
        description="Дыхательный сброс для восстановления ресурса",
        category="breathing",
        duration_minutes=4,
        tags=["восстановление", "дыхание", "энергия"],
        need_ids=["recover"],
        format_id="breath",
        outcome_label="Перезагрузить ресурс",
        instructions=[
            "Сделайте 4 спокойных вдоха носом",
            "На каждом выдохе чуть длиннее обычного",
            "Добавьте короткую паузу после выдоха",
            "Повторите 6–8 циклов",
        ],
    ),
    _new_practice(
        id="lie-down-restore",
        title="Лечь и восстановиться",
        description="Короткий отдых лёжа без экрана",
        category="ritual",
        duration_minutes=8,
        tags=["восстановление", "отдых", "тело"],
        need_ids=["recover", "body"],
        format_id="meditation",
        outcome_label="Дать телу отдых",
        instructions=[
            "Лягте на спину, телефон в стороне",
            "Положите руки на живот",
            "Дышите спокойно 6–8 минут",
            "Перед подъёмом потянитесь и откройте глаза медленно",
        ],
    ),
    _new_practice(
        id="tea-pause-5",
        title="Пауза с теплом",
        description="Ритуал восстановления через тёплый напиток и внимание",
        category="ritual",
        duration_minutes=5,
        tags=["восстановление", "ритуал", "тепло"],
        need_ids=["recover", "calm"],
        format_id="meditation",
        outcome_label="Согреть и замедлить",
        instructions=[
            "Возьмите тёплый напиток",
            "Почувствуйте тепло чашки в руках",
            "Сделайте пять медленных глотков без телефона",
            "Заметьте, где в теле стало спокойнее",
        ],
    ),
    _new_practice(
        id="calm-ambient-backdrop",
        title="Спокойный ambient",
        description="Музыкальная практика восстановления через ambient",
        category="meditation",
        duration_minutes=12,
        tags=["музыка", "восстановление", "ambient"],
        need_ids=["recover", "calm"],
        format_id="music",
        outcome_label="Восстановиться под музыку",
        instructions=[
            "Выберите спокойный ambient без резких пиков",
            "Сядьте или лягте, глаза можно закрыть",
            "Просто слушайте 8–12 минут",
            "В конце заметьте, стало ли телу легче",
        ],
    ),
    _new_practice(
        id="resource-inventory",
        title="Инвентарь ресурса",
        description="Короткая рефлексия: что уже даёт силы",
        category="reflection",
        duration_minutes=7,
        tags=["восстановление", "рефлексия", "ресурс"],
        need_ids=["recover", "understand"],
        format_id="reflection",
        outcome_label="Найти, что питает",
        instructions=[
            "Запишите три вещи, которые сегодня уже поддержали вас",
            "Отметьте одну, которую можно усилить вечером",
            "Вычеркните одно лишнее требование к себе",
            "Закройте список длинным выдохом",
        ],
    ),
    # —— body ——
    _new_practice(
        id="soft-stretch-reset",
        title="Мягкая растяжка",
        description="Лёгкая растяжка шеи, плеч и боков без усилия",
        category="ritual",
        duration_minutes=10,
        tags=["тело", "растяжка", "сброс"],
        need_ids=["body", "recover"],
        format_id="stretch",
        outcome_label="Размять тело",
        instructions=[
            "Встаньте устойчиво, стопы на ширине бёдер",
            "Медленно наклоните голову к одному плечу, затем к другому",
            "Поднимите руки и мягко потянитесь в сторону",
            "Скрутитесь мягко вправо и влево",
            "Завершите несколькими спокойными вдохами",
        ],
    ),
    _new_practice(
        id="gentle-yoga-flow",
        title="Мягкий йога-поток",
        description="Простой поток из кошки-коровы, наклона и позы ребёнка",
        category="ritual",
        duration_minutes=12,
        tags=["йога", "тело", "поток"],
        need_ids=["body", "calm"],
        format_id="yoga",
        outcome_label="Связать дыхание и движение",
        instructions=[
            "Встаньте на четвереньки",
            "Сделайте 6 циклов кошка–корова в ритме дыхания",
            "Перейдите в мягкий наклон вперёд стоя или сидя",
            "Завершите в позе ребёнка на 5–8 дыханий",
        ],
    ),
    _new_practice(
        id="feet-on-floor",
        title="Стопы на полу",
        description="Соматическая практика заземления через стопы",
        category="meditation",
        duration_minutes=4,
        tags=["тело", "заземление", "соматика"],
        need_ids=["body", "calm"],
        format_id="meditation",
        outcome_label="Почувствовать опору стоп",
        instructions=[
            "Сядьте или встаньте, стопы полностью на полу",
            "Перенесите внимание в пятки, затем в пальцы",
            "Слегка покачайтесь, чувствуя контакт",
            "Сделайте 6 дыханий с вниманием в стопах",
        ],
    ),
    _new_practice(
        id="jaw-shoulder-release",
        title="Челюсть и плечи",
        description="Точечная соматика для типичных зажимов",
        category="ritual",
        duration_minutes=5,
        tags=["тело", "зажим", "растяжка"],
        need_ids=["body", "calm"],
        format_id="stretch",
        outcome_label="Снять зажим лица и плеч",
        instructions=[
            "Мягко разожмите зубы и язык",
            "Сделайте круги плечами назад 5 раз",
            "Потяните ухо к плечу с обеих сторон",
            "Выдохните с лёгким звуком «ааа»",
        ],
    ),
    _new_practice(
        id="standing-sun-salute-lite",
        title="Лёгкое приветствие солнцу",
        description="Упрощённая йога-последовательность стоя",
        category="ritual",
        duration_minutes=9,
        tags=["йога", "тело", "утро"],
        need_ids=["body", "focus", "recover"],
        format_id="yoga",
        outcome_label="Разбудить тело движением",
        instructions=[
            "Встаньте прямо, руки вдоль тела",
            "На вдохе поднимите руки вверх",
            "На выдохе мягкий наклон вперёд",
            "Снова вверх на вдохе, руки к сердцу на выдохе",
            "Повторите 4–6 циклов",
        ],
    ),
    # —— understand ——
    _new_practice(
        id="clarity-three-questions",
        title="Три вопроса ясности",
        description="Короткая письменная рефлексия из трёх вопросов",
        category="reflection",
        duration_minutes=8,
        tags=["рефлексия", "ясность", "письмо"],
        need_ids=["understand"],
        format_id="reflection",
        outcome_label="Прояснить, что происходит",
        instructions=[
            "Откройте заметки или возьмите бумагу",
            "Ответьте: «Что я сейчас чувствую?»",
            "Ответьте: «Что мне сейчас нужно?»",
            "Ответьте: «Что я могу сделать маленьким шагом?»",
        ],
    ),
    _new_practice(
        id="mood-name-it",
        title="Назвать настроение",
        description="Дать имени эмоции — чтобы не тонуть в общем «плохо»",
        category="reflection",
        duration_minutes=4,
        tags=["рефлексия", "эмоции", "ясность"],
        need_ids=["understand", "calm"],
        format_id="reflection",
        outcome_label="Назвать, что чувствую",
        instructions=[
            "Спросите: «Какое одно слово описывает состояние?»",
            "Если слов несколько — выберите главное",
            "Запишите его",
            "Добавьте одну фразу: «Мне нужно…»",
        ],
    ),
    _new_practice(
        id="letter-to-self-short",
        title="Короткое письмо себе",
        description="Тёплый текст себе от поддерживающей части",
        category="reflection",
        duration_minutes=10,
        tags=["рефлексия", "письмо", "поддержка"],
        need_ids=["understand", "recover"],
        format_id="reflection",
        outcome_label="Поддержать себя словами",
        instructions=[
            "Напишите обращение: «Дорогой(ая)…»",
            "Опишите, что сегодня было трудным без обвинения",
            "Добавьте одну фразу поддержки, как другу",
            "Закройте письмо одним конкретным мягким шагом",
        ],
    ),
    _new_practice(
        id="boundary-check-3",
        title="Проверка границ",
        description="Три вопроса о том, где сейчас теряется энергия",
        category="reflection",
        duration_minutes=6,
        tags=["рефлексия", "границы", "ясность"],
        need_ids=["understand", "focus"],
        format_id="reflection",
        outcome_label="Увидеть, где утекает сила",
        instructions=[
            "Спросите: «Где я сейчас говорю «да» из усталости?»",
            "Спросите: «Что можно отложить без вреда?»",
            "Спросите: «Какая одна граница была бы доброй?»",
            "Запишите одну маленькую границу на сегодня",
        ],
    ),
    _new_practice(
        id="volumetric-digits",
        title="Объёмные цифры",
        description="Визуализация цифр дня для ясности и спокойного фокуса",
        category="meditation",
        duration_minutes=9,
        tags=["визуализация", "ясность", "фокус"],
        need_ids=["understand", "focus", "calm"],
        format_id="visualization",
        outcome_label="Увидеть день объёмно",
        instructions=[
            "Закройте глаза и представьте сегодняшнюю дату",
            "Сделайте цифры объёмными, мягко освещёнными",
            "Спросите: «Что в этом дне уже ясно?»",
            "Отпустите образ на длинном выдохе",
        ],
    ),
    # —— sleep ——
    _new_practice(
        id="evening-release",
        title="Вечернее отпускание",
        description="Ритуал отпускания дня перед сном",
        category="ritual",
        duration_minutes=7,
        tags=["сон", "вечер", "отпускание"],
        need_ids=["sleep", "calm"],
        format_id="sleep",
        outcome_label="Отпустить день",
        instructions=[
            "Приглушите свет",
            "Назовите одно, что сегодня можно отпустить",
            "Сделайте три длинных выдоха",
            "Представьте, что день мягко закрывается",
        ],
    ),
    _new_practice(
        id="bedtime-wind-down",
        title="Сонный ритуал",
        description="Короткий bedtime-ритуал: свет, дыхание, одна фраза отпускания",
        category="ritual",
        duration_minutes=5,
        tags=["сон", "ритуал", "вечер"],
        need_ids=["sleep"],
        format_id="sleep",
        outcome_label="Закрыть день ко сну",
        instructions=[
            "Выключите яркий свет",
            "Сделайте 5 медленных выдохов",
            "Скажите: «День закончен. Остальное — завтра.»",
            "Лягте и не берите телефон",
        ],
    ),
    _new_practice(
        id="bedtime-stretch",
        title="Растяжка перед сном",
        description="Лёгкая растяжка лёжа для подготовки ко сну",
        category="ritual",
        duration_minutes=8,
        tags=["сон", "растяжка", "вечер"],
        need_ids=["sleep", "body"],
        format_id="stretch",
        outcome_label="Подготовить тело ко сну",
        instructions=[
            "Лягте на спину",
            "Подтяните одно колено к груди, затем другое",
            "Мягко покачайтесь из стороны в сторону",
            "Растяните руки вверх и сделайте длинный выдох",
        ],
    ),
    _new_practice(
        id="sleep-sound-bed",
        title="Музыка для сна",
        description="Музыкальная практика: слушать спокойный звук лёжа",
        category="meditation",
        duration_minutes=15,
        tags=["сон", "музыка", "звук"],
        need_ids=["sleep"],
        format_id="music",
        outcome_label="Уснуть под звук",
        instructions=[
            "Лягте удобно и включите тихий спокойный трек",
            "Слушайте только звук, не анализируя",
            "Синхронизируйте дыхание с мягким ритмом",
            "Позвольте глазам закрыться сами",
        ],
    ),
    _new_practice(
        id="body-heavy-scan",
        title="Тяжесть тела ко сну",
        description="Скан тела с ощущением тяжести и тепла",
        category="meditation",
        duration_minutes=10,
        tags=["сон", "медитация", "тело"],
        need_ids=["sleep", "body"],
        format_id="meditation",
        outcome_label="Уложить тело в отдых",
        instructions=[
            "Лягте и закройте глаза",
            "Пройдитесь вниманием от стоп к лицу",
            "На каждом участке представьте тепло и тяжесть",
            "Отпустите контроль дыхания",
        ],
    ),
    _new_practice(
        id="worry-park-list",
        title="Парковка тревог",
        description="Выгрузить мысли на бумагу, чтобы отпустить их до утра",
        category="reflection",
        duration_minutes=6,
        tags=["сон", "рефлексия", "тревога"],
        need_ids=["sleep", "understand", "calm"],
        format_id="reflection",
        outcome_label="Отложить заботы до утра",
        instructions=[
            "Запишите всё, что крутится в голове, списком",
            "Рядом с пунктом поставьте «завтра» или «не срочно»",
            "Закройте блокнот",
            "Сделайте три длинных выдоха",
        ],
    ),
    _new_practice(
        id="dark-room-breath",
        title="Дыхание в темноте",
        description="Медленное дыхание в приглушённом свете для засыпания",
        category="breathing",
        duration_minutes=5,
        tags=["сон", "дыхание", "вечер"],
        need_ids=["sleep", "calm"],
        format_id="breath",
        outcome_label="Уснуть через дыхание",
        instructions=[
            "Приглушите свет или закройте глаза",
            "Вдох на 4, выдох на 6–8",
            "Повторите 10 циклов",
            "Не форсируйте сон — просто дышите",
        ],
    ),
    # —— more format depth ——
    _new_practice(
        id="affirmation-steady-day",
        title="Ровный день",
        description="Аффирмация собранности без давления на результат",
        category="affirmation",
        duration_minutes=3,
        tags=["аффирмация", "фокус", "день"],
        need_ids=["focus", "calm"],
        format_id="affirmation",
        outcome_label="Держать ровный темп",
        instructions=[
            "Встаньте или сядьте устойчиво",
            "Скажите: «Я иду в своём темпе. Одного шага достаточно.»",
            "Повторите 7 раз",
            "Назовите первый маленький шаг",
        ],
    ),
    _new_practice(
        id="nature-sound-restore",
        title="Звуки природы",
        description="Музыкальная практика восстановления на природных звуках",
        category="meditation",
        duration_minutes=10,
        tags=["музыка", "природа", "восстановление"],
        need_ids=["recover", "calm", "sleep"],
        format_id="music",
        outcome_label="Отдохнуть в звуке природы",
        instructions=[
            "Включите дождь, лес или волны на небольшой громкости",
            "Лягте или сядьте удобно",
            "Слушайте, отмечая только звук",
            "Через 8–10 минут мягко откройте глаза",
        ],
    ),
    _new_practice(
        id="hip-open-soft",
        title="Мягкое раскрытие бёдер",
        description="Растяжка бёдер сидя без усилия",
        category="ritual",
        duration_minutes=8,
        tags=["растяжка", "тело", "бёдра"],
        need_ids=["body", "recover"],
        format_id="stretch",
        outcome_label="Освободить низ тела",
        instructions=[
            "Сядьте удобно на пол или стул",
            "Положите лодыжку на противоположное колено, если комфортно",
            "Дышите в мягкое ощущение растяжения 1–2 минуты",
            "Смените сторону",
        ],
    ),
    _new_practice(
        id="seated-twist-yoga",
        title="Скрутка сидя",
        description="Мягкая йога-скрутка для спины и дыхания",
        category="ritual",
        duration_minutes=6,
        tags=["йога", "спина", "дыхание"],
        need_ids=["body", "focus"],
        format_id="yoga",
        outcome_label="Освободить спину",
        instructions=[
            "Сядьте прямо, стопы на полу или в удобной позе",
            "На выдохе мягко скрутитесь вправо",
            "Дышите 4 цикла, затем влево",
            "Вернитесь в центр и отпустите плечи",
        ],
    ),
    _new_practice(
        id="safe-place-visual",
        title="Безопасное место",
        description="Визуализация спокойного места для восстановления",
        category="meditation",
        duration_minutes=8,
        tags=["визуализация", "спокойствие", "безопасность"],
        need_ids=["calm", "recover", "sleep"],
        format_id="visualization",
        outcome_label="Вернуться в безопасный образ",
        instructions=[
            "Закройте глаза и выберите спокойное место",
            "Добавьте детали: свет, звук, температуру",
            "Побудьте там 4–6 минут",
            "Перед выходом поблагодарите это место",
        ],
    ),
]


def apply_state_cycle_catalog(general_practices: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Deep-copy GENERAL practices, apply STATE_CYCLE_META, append missing NEW entries."""
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for raw in general_practices:
        item = deepcopy(raw)
        pid = str(item.get("id") or "")
        meta = STATE_CYCLE_META.get(pid)
        if meta:
            item["need_ids"] = list(meta.get("need_ids") or [])
            item["format_id"] = meta.get("format_id")
            item["outcome_label"] = meta.get("outcome_label")
        seen.add(pid)
        out.append(item)
    for neu in NEW_STATE_CYCLE_PRACTICES:
        nid = str(neu.get("id") or "")
        if nid and nid not in seen:
            out.append(deepcopy(neu))
            seen.add(nid)
    return out


def practice_matches_need(practice: dict[str, Any], need_id: str) -> bool:
    need = (need_id or "").strip().lower()
    if not need or need not in STATE_CYCLE_NEED_IDS:
        return False
    ids = practice.get("need_ids") or []
    return need in [str(x).lower() for x in ids]


def practice_matches_format(practice: dict[str, Any], format_id: str) -> bool:
    fmt = (format_id or "").strip().lower()
    if not fmt or fmt not in STATE_CYCLE_FORMAT_IDS:
        return False
    return str(practice.get("format_id") or "").lower() == fmt


def rank_practices_for_need(practices: list[dict[str, Any]], need_id: str) -> list[dict[str, Any]]:
    """Primary need first, then secondary tagged, preserve relative order within buckets."""
    need = (need_id or "").strip().lower()
    primary: list[dict[str, Any]] = []
    secondary: list[dict[str, Any]] = []
    for p in practices:
        ids = [str(x).lower() for x in (p.get("need_ids") or [])]
        if not ids:
            continue
        if ids and ids[0] == need:
            primary.append(p)
        elif need in ids:
            secondary.append(p)
    return primary + secondary


def catalog_coverage(practices: list[dict[str, Any]]) -> dict[str, Any]:
    need_counts = {n: 0 for n in STATE_CYCLE_NEED_IDS}
    format_counts = {f: 0 for f in STATE_CYCLE_FORMAT_IDS}
    for p in practices:
        for n in p.get("need_ids") or []:
            key = str(n).lower()
            if key in need_counts:
                need_counts[key] += 1
        fmt = str(p.get("format_id") or "").lower()
        if fmt in format_counts:
            format_counts[fmt] += 1
    return {
        "total": len(practices),
        "tagged": sum(1 for p in practices if p.get("need_ids") or p.get("format_id")),
        "need_counts": need_counts,
        "format_counts": format_counts,
    }

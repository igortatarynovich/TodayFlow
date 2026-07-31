"""State-cycle Practices catalog enrichment (need / format / outcome).

SoT overlay for GENERAL free practices + gap-fill entries.
Canon: docs/practices/PRACTICES_SCREEN_V1.md (§1 needs, §2 formats).

Public JSON (optional, backward compatible):
  need_ids: list[str]
  format_id: str | None
  outcome_label: str | None
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

# Overlay for existing GENERAL practice ids (need_ids, format_id, outcome_label).
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
) -> dict[str, Any]:
    return {
        "id": id,
        "title": title,
        "description": description,
        "category": category,
        "duration_minutes": duration_minutes,
        "difficulty": "beginner",
        "is_free": True,
        "is_personalized": False,
        "access_level": "free",
        "tags": tags,
        "need_ids": need_ids,
        "format_id": format_id,
        "outcome_label": outcome_label,
        "instructions": instructions,
    }


# Gap-fill free practices for stretch / yoga / visualization / music / sleep / reflection / affirmation.
NEW_STATE_CYCLE_PRACTICES: list[dict[str, Any]] = [
    _new_practice(
        id="tension-release-3",
        title="Сброс напряжения 3 минуты",
        description="Короткое дыхание с мягким отпусканием плеч и челюсти",
        category="breathing",
        duration_minutes=3,
        tags=["спокойствие", "дыхание", "быстро"],
        need_ids=["calm"],
        format_id="breath",
        outcome_label="Отпустить зажим",
        instructions=[
            "Сядьте или встаньте удобно",
            "На вдохе слегка поднимите плечи",
            "На длинном выдохе опустите плечи и расслабьте челюсть",
            "Повторите 6–8 циклов",
        ],
    ),
    _new_practice(
        id="soft-stretch-reset",
        title="Мягкая растяжка-сброс",
        description="Лёгкая растяжка шеи, плеч и боков без усилия",
        category="ritual",
        duration_minutes=7,
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
        id="volume-imagination",
        title="Воображение громкости",
        description="Визуализация: убавить внутренний шум как регулятор громкости",
        category="meditation",
        duration_minutes=5,
        tags=["визуализация", "спокойствие", "воображение"],
        need_ids=["calm", "focus"],
        format_id="visualization",
        outcome_label="Убавить внутренний шум",
        instructions=[
            "Закройте глаза и представьте регулятор громкости",
            "Заметьте, на каком уровне сейчас внутренний шум",
            "Медленно «убавьте» на несколько делений с каждым выдохом",
            "Оставайтесь в тишине 30–60 секунд",
        ],
    ),
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
            "Поставьте стопы на пол и почувствуйте контакт",
            "Скажите тихо: «Я здесь. Я могу быть с собой мягко.»",
            "Повторите фразу 5 раз на выдохе",
            "Заметьте одно ощущение опоры в теле",
        ],
    ),
    _new_practice(
        id="evening-release",
        title="Вечерний отпуск",
        description="Ритуал отпускания дня перед сном",
        category="ritual",
        duration_minutes=6,
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
        title="Звук у постели",
        description="Музыкальная практика: слушать спокойный звук лёжа",
        category="meditation",
        duration_minutes=10,
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
        id="calm-ambient-backdrop",
        title="Спокойный ambient-фон",
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
        id="focus-return-4",
        title="Возврат фокуса за 4 минуты",
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

"""Day color catalog — knowledge source only (not user-facing SoT).

Phase B2: scenario props pick a color from this catalog *because* a scene needs
a quality; catalog copy is never shipped as the day's meaning without
origin_scene_id + conflict link.

Legacy `celestial_events_builder` presets remain a seed/index path until B3 wire
projection replaces them.
"""

from __future__ import annotations

from typing import Any

# Symbolic qualities used to match conflict/scene needs.
# Catalog is knowledge: names, tags, apply hints, avoid candidates.
COLOR_CATALOG_V1: list[dict[str, Any]] = [
    {
        "name": "Глубокий синий",
        "tags": ("hold_distance", "depth", "boundaries", "slow_reply", "clarity"),
        "symbolic_property": "дистанция и опора — сначала сформулировать позицию",
        "apply": {
            "clothing": "Тёмно-синий свитер, пиджак или джинсы глубокого синего.",
            "accessory": "Сумка, ремень или перстень в спокойном синем.",
            "workspace": "Один синий предмет в зоне разговора или на столе.",
            "makeup": "Холодный синий акцент у глаз — без «маски».",
            "ui_or_bg": "Спокойный тёмно-синий фон в заметках дня.",
        },
        "intensity_default": "один заметный элемент или два мелких",
        "avoid_candidates": (
            {"name": "Ярко-розовый", "amplifies": ("please", "harmony_at_any_cost", "soft_over_truth")},
            {"name": "Неоновый жёлтый", "amplifies": ("rush", "scatter", "noise")},
        ),
    },
    {
        "name": "Лазурь",
        "tags": ("calm_clarity", "decision", "focus", "cool_mind"),
        "symbolic_property": "ясность ума без суеты",
        "apply": {
            "clothing": "Светлая рубашка, шарф или носки лазурного оттенка.",
            "accessory": "Тонкий браслет или блокнот в мягком синем.",
            "workspace": "Лазурный стикер на одном приоритете.",
            "makeup": None,
            "ui_or_bg": "Мягкий голубой акцент в списке задач.",
        },
        "intensity_default": "10–15% образа — один акцент",
        "avoid_candidates": (
            {"name": "Кислотно-оранжевый", "amplifies": ("rush", "impulse", "scatter")},
        ),
    },
    {
        "name": "Индиго",
        "tags": ("inner_honesty", "pause_before_act", "intuition", "depth"),
        "symbolic_property": "услышать себя до действия",
        "apply": {
            "clothing": "Индиго в нижнем слое ближе к телу.",
            "accessory": "Платок или обложка телефона.",
            "workspace": None,
            "makeup": None,
            "ui_or_bg": None,
        },
        "intensity_default": "мягкий акцент ближе к телу",
        "avoid_candidates": (
            {"name": "Красный «сигнал тревоги»", "amplifies": ("react_first", "rush", "alarm")},
        ),
    },
    {
        "name": "Коралловый",
        "tags": ("soft_speech", "connection", "warm_contact", "communication"),
        "symbolic_property": "мягкий контакт без давления",
        "apply": {
            "clothing": "Коралловый топ под пиджак или шарф.",
            "accessory": "Небольшая брошь или чехол.",
            "workspace": None,
            "makeup": "Помада мягкого коралла.",
            "ui_or_bg": None,
        },
        "intensity_default": "небольшой тёплый штрих",
        "avoid_candidates": (
            {"name": "Чёрный «всё или ничего»", "amplifies": ("heavy", "all_or_nothing", "pressure")},
        ),
    },
    {
        "name": "Изумрудный",
        "tags": ("restore", "growth", "body", "relationships", "ground_soft"),
        "symbolic_property": "восстановление и мягкий рост",
        "apply": {
            "clothing": "Изумрудный шарф или кардиган.",
            "accessory": "Маленький зелёный якорь.",
            "workspace": "Растение или зелёный предмет на столе.",
            "makeup": None,
            "ui_or_bg": None,
        },
        "intensity_default": "один живой акцент",
        "avoid_candidates": (
            {"name": "Серый «офисный бетон»", "amplifies": ("numb", "flat", "overwork")},
        ),
    },
    {
        "name": "Оливковый",
        "tags": ("ground", "steady", "work", "no_jerk"),
        "symbolic_property": "заземление без рывков",
        "apply": {
            "clothing": "Оливковый слой outerwear или брюки.",
            "accessory": "Ремень или сумка спокойного оливкового.",
            "workspace": None,
            "makeup": None,
            "ui_or_bg": None,
        },
        "intensity_default": "один спокойный слой",
        "avoid_candidates": (
            {"name": "Неоновый жёлтый", "amplifies": ("rush", "scatter")},
        ),
    },
    {
        "name": "Бордовый",
        "tags": ("focus", "depth", "boundaries", "serious"),
        "symbolic_property": "собранность и глубина",
        "apply": {
            "clothing": "Бордовый шарф или один слой outerwear.",
            "accessory": "Кожаный аксессуар винного тона.",
            "workspace": None,
            "makeup": None,
            "ui_or_bg": None,
        },
        "intensity_default": "один насыщенный акцент",
        "avoid_candidates": (
            {"name": "Кислотно-розовый", "amplifies": ("scatter", "please", "noise")},
        ),
    },
    {
        "name": "Янтарный",
        "tags": ("warm_energy", "restore", "body", "tempo_gentle"),
        "symbolic_property": "тёплая энергия без суеты",
        "apply": {
            "clothing": "Янтарный шарф или тёплый свитер.",
            "accessory": "Украшение медового оттенка.",
            "workspace": None,
            "makeup": None,
            "ui_or_bg": None,
        },
        "intensity_default": "тёплый акцент у лица или на руках",
        "avoid_candidates": (
            {"name": "Холодный стальной", "amplifies": ("harsh", "over_control")},
        ),
    },
]


def list_color_knowledge() -> list[dict[str, Any]]:
    return list(COLOR_CATALOG_V1)


def get_color_entry(name: str) -> dict[str, Any] | None:
    needle = (name or "").strip().lower()
    for row in COLOR_CATALOG_V1:
        if str(row.get("name") or "").strip().lower() == needle:
            return row
    return None


def score_color_for_needs(entry: dict[str, Any], needed_tags: set[str]) -> int:
    tags = set(entry.get("tags") or ())
    return len(tags & needed_tags)

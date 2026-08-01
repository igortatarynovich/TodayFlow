"""Day color catalog — knowledge source only (not user-facing SoT).

Phase B2: scenario props pick a color from this catalog *because* a scene needs
a quality; catalog copy is never shipped as the day's meaning without
origin_scene_id + conflict link.

Color is NOT an independent daily draw (unlike card/number). Tag coverage for
`_needed_color_tags` / `_amplify_tags_for_trap` is intentionally closed at 8
entries — deepen meaning, do not expand the palette without Architecture impact.

Legacy `celestial_events_builder` presets remain a seed/index path until B3 wire
projection replaces them.
"""

from __future__ import annotations

from typing import Any

# Amplify tags that `_amplify_tags_for_trap` can actually emit (live scoring set).
LIVE_AVOID_AMPLIFY_TAGS: frozenset[str] = frozenset(
    {
        "please",
        "harmony_at_any_cost",
        "soft_over_truth",
        "rush",
        "react_first",
        "impulse",
        "alarm",
        "scatter",
        "noise",
        "pressure",
        "all_or_nothing",
        "over_control",
        "harsh",
    }
)

# Symbolic qualities used to match conflict/scene needs.
# Catalog is knowledge: names, tags, apply hints, avoid candidates.
COLOR_CATALOG_V1: list[dict[str, Any]] = [
    {
        "name": "Глубокий синий",
        "tags": ("hold_distance", "depth", "boundaries", "slow_reply", "clarity"),
        "symbolic_property": "дистанция, которая снижает реактивность, — сформулировать позицию раньше, чем ответить",
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
        "symbolic_property": "ясность без тяжести — ровный фон для решения, не для дистанцирования",
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
        "symbolic_property": "пауза внутрь, не наружу — услышать свою честную реакцию до того, как её озвучить",
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
        "symbolic_property": "тёплый контакт без напора — говорить прямо, но не колко",
        "apply": {
            "clothing": "Коралловый топ под пиджак или шарф.",
            "accessory": "Небольшая брошь или чехол.",
            "workspace": None,
            "makeup": "Помада мягкого коралла.",
            "ui_or_bg": None,
        },
        "intensity_default": "небольшой тёплый штрих",
        "avoid_candidates": (
            # was decorative heavy — remapped to live amplify set
            {"name": "Чёрный «всё или ничего»", "amplifies": ("all_or_nothing", "pressure", "over_control")},
        ),
    },
    {
        "name": "Изумрудный",
        "tags": ("restore", "growth", "body", "relationships", "ground_soft"),
        "symbolic_property": "мягкое восстановление через тело и связь, не через изоляцию",
        "apply": {
            "clothing": "Изумрудный шарф или кардиган.",
            "accessory": "Маленький зелёный якорь.",
            "workspace": "Растение или зелёный предмет на столе.",
            "makeup": None,
            "ui_or_bg": None,
        },
        "intensity_default": "один живой акцент",
        "avoid_candidates": (
            # was decorative numb/flat/overwork — remapped to live amplify set
            {"name": "Серый «офисный бетон»", "amplifies": ("pressure", "over_control", "harsh")},
        ),
    },
    {
        "name": "Оливковый",
        "tags": ("ground", "steady", "work", "no_jerk"),
        "symbolic_property": "заземление в рабочем темпе — устойчивость без рывков и без демонстрации усилия",
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
        "symbolic_property": "серьёзная собранность — граница, которая не кричит, а просто есть",
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
        "symbolic_property": "тёплая поддержка энергии тела без разгона и без суеты",
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


def color_hook_base(name: str) -> dict[str, Any] | None:
    """Project catalog row into hook_reveal.base shape (static archetype + apply)."""
    entry = get_color_entry(name)
    if not entry:
        return None
    return {
        "name": str(entry.get("name") or "").strip(),
        "base_archetype": str(entry.get("symbolic_property") or "").strip(),
        "meaning": str(entry.get("symbolic_property") or "").strip(),
        "apply": dict(entry.get("apply") or {}),
        "intensity_default": str(entry.get("intensity_default") or "").strip() or None,
        "avoid_candidates": list(entry.get("avoid_candidates") or ()),
    }


def score_color_for_needs(entry: dict[str, Any], needed_tags: set[str]) -> int:
    tags = set(entry.get("tags") or ())
    return len(tags & needed_tags)


def validate_color_catalog_v1() -> list[str]:
    """Structural + scoring-tag hygiene for the knowledge catalog."""
    errors: list[str] = []
    names: set[str] = set()
    for i, row in enumerate(COLOR_CATALOG_V1):
        name = str(row.get("name") or "").strip()
        if not name:
            errors.append(f"row[{i}]: empty name")
            continue
        if name in names:
            errors.append(f"duplicate name: {name}")
        names.add(name)
        prop = str(row.get("symbolic_property") or "").strip()
        if len(prop) < 12:
            errors.append(f"{name}: symbolic_property too short")
        tags = tuple(row.get("tags") or ())
        if len(tags) < 2:
            errors.append(f"{name}: need ≥2 tags")
        for cand in row.get("avoid_candidates") or ():
            amplifies = tuple((cand or {}).get("amplifies") or ())
            dead = [a for a in amplifies if a not in LIVE_AVOID_AMPLIFY_TAGS]
            if dead:
                errors.append(f"{name}: dead avoid amplifies {dead}")
    return errors

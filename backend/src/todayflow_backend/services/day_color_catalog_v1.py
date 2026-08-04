"""Day color catalog — knowledge source only (not user-facing SoT).

Phase B2: scenario props pick a color from this catalog *because* a scene needs
a quality; catalog copy is never shipped as the day's meaning without
origin_scene_id + conflict link.

Color is NOT an independent daily draw (unlike card/number).
Layer A reused existing `_needed_color_tags`. Layer B (creativity/home/money
abundance/passion/closure) shipped only with matching generator branches —
never catalog-only orphans. Champagne unlocks via ``day_favorable`` from
domain_verdicts computed on the same natal activations at scenario generation.

Legacy `celestial_events_builder` presets remain a seed/index path until B3 wire
projection replaces them.
"""

from __future__ import annotations

import re
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

# Tags `_needed_color_tags` may request. Catalog tags must ⊆ this set (anti-orphan).
# Keep in sync with day_scenario_v1._needed_color_tags (+ tests).
LIVE_NEEDED_COLOR_TAGS: frozenset[str] = frozenset(
    {
        "hold_distance",
        "boundaries",
        "slow_reply",
        "clarity",
        "calm_clarity",
        "pause_before_act",
        "depth",
        "soft_speech",
        "communication",
        "inner_honesty",
        "restore",
        "body",
        "tempo_gentle",
        "ground",
        "focus",
        "steady",
        "decision",
        # Layer B
        "creative_spark",
        "generous_warmth",
        "home_warmth",
        "belonging",
        "confident_abundance",
        "steady_growth",
        "passionate_assertion",
        "vital_courage",
        "gentle_closure",
        "honor_loss",
        "quiet_celebration",
        "light_gratitude",
        # Catalog-only flavor tags still used on core/layer-A rows (scoring bonus
        # when present in needed — some are never emitted; allowed as secondary).
        "cool_mind",
        "intuition",
        "connection",
        "warm_contact",
        "growth",
        "relationships",
        "ground_soft",
        "work",
        "no_jerk",
        "serious",
        "warm_energy",
    }
)

# Empty when all layer-B rows are live; kept for validator anti-premature-merge.
PENDING_LAYER_B_COLORS: frozenset[str] = frozenset()

# Primary Layer-B tags that must be reachable from generator / day_favorable.
LAYER_B_PRIMARY_TAGS: frozenset[str] = frozenset(
    {
        "creative_spark",
        "generous_warmth",
        "home_warmth",
        "belonging",
        "confident_abundance",
        "steady_growth",
        "passionate_assertion",
        "vital_courage",
        "gentle_closure",
        "honor_loss",
        "quiet_celebration",
        "light_gratitude",
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
            "clothing_warm": "Тёмно-синяя рубашка, льняной пиджак или джинсы глубокого синего.",
            "clothing_cold": "Тёмно-синий свитер, шерстяной пиджак или джинсы глубокого синего.",
            "accessory": "Сумка, ремень или перстень в спокойном синем.",
            "accessory_warm": "Лёгкая сумка или тонкий браслет в спокойном синем.",
            "accessory_cold": "Шерстяной шарф, ремень или перстень в спокойном синем.",
            "workspace": "Один синий предмет в зоне разговора или на столе.",
            "makeup": "Холодный синий акцент у глаз — без «маски».",
            "ui_or_bg": "Спокойный тёмно-синий фон в заметках дня.",
        },
        "intensity_default": "один заметный элемент или два мелких",
        "avoid_candidates": (
            {"name": "Ярко-розовый", "why": "розовый тон усиливает желание сгладить и угодить — сегодня это не союзник", "amplifies": ("please", "harmony_at_any_cost", "soft_over_truth")},
            {"name": "Неоновый жёлтый", "why": "кислотный тон усиливает суету и спешку — не твой сегодня союзник", "amplifies": ("rush", "scatter", "noise")},
        ),
    },
    {
        "name": "Лазурь",
        "tags": ("calm_clarity", "decision", "focus", "cool_mind"),
        "symbolic_property": "ясность без тяжести — ровный фон для решения, не для дистанцирования",
        "apply": {
            "clothing": "Светлая рубашка, шарф или носки лазурного оттенка.",
            "clothing_warm": "Светлая рубашка или тонкий шарф лазурного оттенка.",
            "clothing_cold": "Лазурный свитер, шарф или носки.",
            "accessory": "Тонкий браслет или блокнот в мягком синем.",
            "accessory_warm": "Тонкий браслет или блокнот в мягком синем.",
            "accessory_cold": "Тёплый шарф или чехол телефона в мягком синем.",
            "workspace": "Лазурный стикер на одном приоритете.",
            "makeup": None,
            "ui_or_bg": "Мягкий голубой акцент в списке задач.",
        },
        "intensity_default": "10–15% образа — один акцент",
        "avoid_candidates": (
            {"name": "Кислотно-оранжевый", "why": "кислотный тон усиливает суету и спешку — не твой сегодня союзник", "amplifies": ("rush", "impulse", "scatter")},
        ),
    },
    {
        "name": "Индиго",
        "tags": ("inner_honesty", "pause_before_act", "intuition", "depth"),
        "symbolic_property": "пауза внутрь, не наружу — услышать свою честную реакцию до того, как её озвучить",
        "apply": {
            "clothing": "Индиго в нижнем слое ближе к телу.",
            "clothing_warm": "Индиго в лёгком нижнем слое ближе к телу.",
            "clothing_cold": "Индиго в тёплом нижнем слое ближе к телу.",
            "accessory": "Платок или обложка телефона.",
            "accessory_warm": "Лёгкий платок или обложка телефона.",
            "accessory_cold": "Тёплый платок или обложка телефона.",
            "workspace": None,
            "makeup": None,
            "ui_or_bg": None,
        },
        "intensity_default": "мягкий акцент ближе к телу",
        "avoid_candidates": (
            {"name": "Красный", "why": "резкий акцент толкает отвечать раньше, чем подумать", "amplifies": ("react_first", "rush", "alarm")},
        ),
    },
    {
        "name": "Коралловый",
        "tags": ("soft_speech", "connection", "warm_contact", "communication"),
        "symbolic_property": "тёплый контакт без напора — говорить прямо, но не колко",
        "apply": {
            "clothing": "Коралловый топ под пиджак или шарф.",
            "clothing_warm": "Коралловый топ или лёгкий шарф.",
            "clothing_cold": "Коралловый свитер или тёплый шарф.",
            "accessory": "Небольшая брошь или чехол.",
            "accessory_warm": "Тонкий коралловый аксессуар — серьги или браслет.",
            "accessory_cold": "Коралловый шарф или перчатки.",
            "workspace": None,
            "makeup": "Помада мягкого коралла.",
            "ui_or_bg": None,
        },
        "intensity_default": "небольшой тёплый штрих",
        "avoid_candidates": (
            # was decorative heavy — remapped to live amplify set
            {"name": "Чёрный", "why": "контрастный тон толкает к крайностям вместо меры", "amplifies": ("all_or_nothing", "pressure", "over_control")},
        ),
    },
    {
        "name": "Изумрудный",
        "tags": ("restore", "growth", "body", "relationships", "ground_soft"),
        "symbolic_property": "мягкое восстановление через тело и связь, не через изоляцию",
        "apply": {
            "clothing": "Изумрудный шарф или кардиган.",
            "clothing_warm": "Изумрудный шарф или лёгкий кардиган.",
            "clothing_cold": "Изумрудный свитер или плотный кардиган.",
            "accessory": "Маленький зелёный якорь.",
            "accessory_warm": "Изумрудный браслет или тонкий ремень.",
            "accessory_cold": "Изумрудный шарф или сумка.",
            "workspace": "Растение или зелёный предмет на столе.",
            "makeup": None,
            "ui_or_bg": None,
        },
        "intensity_default": "один живой акцент",
        "avoid_candidates": (
            # was decorative numb/flat/overwork — remapped to live amplify set
            {"name": "Серый", "why": "тяжёлый акцент усиливает давление «надо уже»", "amplifies": ("pressure", "over_control", "harsh")},
        ),
    },
    {
        "name": "Оливковый",
        "tags": ("ground", "steady", "work", "no_jerk"),
        "symbolic_property": "заземление в рабочем темпе — устойчивость без рывков и без демонстрации усилия",
        "apply": {
            "clothing": "Оливковый слой outerwear или брюки.",
            "clothing_warm": "Оливковая рубашка, жилет или брюки.",
            "clothing_cold": "Оливковый слой outerwear или брюки.",
            "accessory": "Ремень или сумка спокойного оливкового.",
            "accessory_warm": "Оливковый ремень или лёгкая сумка.",
            "accessory_cold": "Оливковый шарф или плотная сумка.",
            "workspace": None,
            "makeup": None,
            "ui_or_bg": None,
        },
        "intensity_default": "один спокойный слой",
        "avoid_candidates": (
            {"name": "Неоновый жёлтый", "why": "кислотный тон усиливает суету и спешку — не твой сегодня союзник", "amplifies": ("rush", "scatter")},
        ),
    },
    {
        "name": "Бордовый",
        "tags": ("focus", "depth", "boundaries", "serious"),
        "symbolic_property": "серьёзная собранность — граница, которая не кричит, а просто есть",
        "apply": {
            "clothing": "Бордовый шарф или один слой outerwear.",
            "clothing_warm": "Бордовый шарф или лёгкий слой в образе.",
            "clothing_cold": "Бордовый шарф или один слой outerwear.",
            "accessory": "Кожаный аксессуар винного тона.",
            "accessory_warm": "Бордовый браслет или тонкий ремень.",
            "accessory_cold": "Бордовый шарф или перчатки.",
            "workspace": None,
            "makeup": None,
            "ui_or_bg": None,
        },
        "intensity_default": "один насыщенный акцент",
        "avoid_candidates": (
            {"name": "Кислотно-розовый", "why": "дробный яркий тон разбрасывает внимание по мелочам", "amplifies": ("scatter", "please", "noise")},
        ),
    },
    {
        "name": "Янтарный",
        "tags": ("warm_energy", "restore", "body", "tempo_gentle"),
        "symbolic_property": "тёплая поддержка энергии тела без разгона и без суеты",
        "apply": {
            "clothing": "Янтарный шарф или тёплый свитер.",
            "clothing_warm": "Янтарный шарф или лёгкий кардиган.",
            "clothing_cold": "Янтарный шарф или тёплый свитер.",
            "accessory": "Украшение медового оттенка.",
            "accessory_warm": "Янтарный браслет или тонкая цепочка.",
            "accessory_cold": "Янтарный шарф или варежки.",
            "workspace": None,
            "makeup": None,
            "ui_or_bg": None,
        },
        "intensity_default": "тёплый акцент у лица или на руках",
        "avoid_candidates": (
            {"name": "Холодный стальной", "why": "резкий тон делает общение суше и острее, чем нужно сегодня", "amplifies": ("harsh", "over_control")},
        ),
    },
    # --- Layer A expansion (existing tags only; 2026-08-02) ---
    {
        "name": "Малахитовый",
        "tags": ("restore", "ground", "depth"),
        "symbolic_property": "глубокое восстановление под защитой — не отдых на бегу, а настоящая пауза",
        "apply": {
            "clothing": "Малахитовый свитер или тёмно-зелёный слой outerwear.",
            "clothing_warm": "Малахитовая рубашка или лёгкий тёмно-зелёный слой.",
            "clothing_cold": "Малахитовый свитер или тёмно-зелёный слой outerwear.",
            "accessory": "Кольцо или подвеска с малахитовым отливом.",
            "accessory_warm": "Малахитовый браслет или тонкий ремень.",
            "accessory_cold": "Малахитовый шарф или плотная сумка.",
            "workspace": "Тёмно-зелёный предмет на столе, не растение — камень или ткань.",
            "makeup": None,
            "ui_or_bg": None,
        },
        "intensity_default": "один глубокий акцент, не россыпь мелочей",
        "avoid_candidates": (
            {"name": "Плоский белый", "why": "тяжёлый акцент усиливает давление «надо уже»", "amplifies": ("pressure", "harsh")},
        ),
    },
    {
        "name": "Пыльная роза",
        "tags": ("soft_speech", "tempo_gentle", "communication"),
        "symbolic_property": "контакт на самом тихом регистре — мягче, чем тепло, ближе к бережности",
        "apply": {
            "clothing": "Пыльно-розовый свитер, шарф или блуза.",
            "clothing_warm": "Пыльно-розовая блуза или лёгкий шарф.",
            "clothing_cold": "Пыльно-розовый свитер или шарф.",
            "accessory": "Лёгкий шёлковый платок того же тона.",
            "accessory_warm": "Пыльно-розовый браслет или тонкий платок.",
            "accessory_cold": "Пыльно-розовый шарф или перчатки.",
            "workspace": None,
            "makeup": "Приглушённая розовая помада без блеска.",
            "ui_or_bg": None,
        },
        "intensity_default": "мягкий, почти незаметный тон — не яркое пятно",
        "avoid_candidates": (
            {"name": "Кислотно-красный", "why": "тревожный акцент держит нервную готовность на взводе", "amplifies": ("alarm", "harsh")},
        ),
    },
    {
        "name": "Мускатный",
        "tags": ("ground", "steady", "body"),
        "symbolic_property": "тёплая устойчивость через тело — заземление, которое греет, а не просто держит",
        "apply": {
            "clothing": "Мускатный свитер или пальто тёплого коричневого.",
            "clothing_warm": "Мускатная рубашка или лёгкий жакет.",
            "clothing_cold": "Мускатный свитер или пальто тёплого коричневого.",
            "accessory": "Кожаный аксессуар цвета мускатного ореха.",
            "accessory_warm": "Мускатный ремень или лёгкая сумка.",
            "accessory_cold": "Мускатный шарф или плотные перчатки.",
            "workspace": None,
            "makeup": None,
            "ui_or_bg": None,
        },
        "intensity_default": "один тёплый слой",
        "avoid_candidates": (
            {"name": "Ледяной серебристый", "why": "резкий тон делает общение суше и острее, чем нужно сегодня", "amplifies": ("harsh", "over_control")},
        ),
    },
    {
        "name": "Аметистовый",
        "tags": ("inner_honesty", "pause_before_act", "clarity", "depth"),
        "symbolic_property": "ясность, добытая через паузу, — не просто «подожди», а «теперь видно»",
        "apply": {
            "clothing": "Аметистовый шарф или свитер глубокого фиолетового.",
            "clothing_warm": "Аметистовый шарф или лёгкий кардиган.",
            "clothing_cold": "Аметистовый шарф или свитер глубокого фиолетового.",
            "accessory": "Кольцо или серьги с фиолетовым камнем.",
            "accessory_warm": "Аметистовый браслет или тонкий платок.",
            "accessory_cold": "Аметистовый шарф или тёплые перчатки.",
            "workspace": None,
            "makeup": None,
            "ui_or_bg": None,
        },
        "intensity_default": "один насыщенный акцент",
        "avoid_candidates": (
            {"name": "Кричащий фуксия", "why": "дробный яркий тон разбрасывает внимание по мелочам", "amplifies": ("scatter", "noise")},
        ),
    },
    {
        "name": "Кобальтовый",
        "tags": ("calm_clarity", "decision", "focus"),
        "symbolic_property": "решительная ясность — не фон для решения, а сам толчок его принять",
        "apply": {
            "clothing": "Кобальтовая рубашка или свитер.",
            "clothing_warm": "Кобальтовая рубашка или лёгкий слой.",
            "clothing_cold": "Кобальтовый свитер или плотная рубашка.",
            "accessory": "Ручка, часы или чехол насыщенного синего.",
            "accessory_warm": "Кобальтовый браслет или тонкий ремень.",
            "accessory_cold": "Кобальтовый шарф или сумка.",
            "workspace": "Кобальтовый стикер на самом важном пункте дня.",
            "makeup": None,
            "ui_or_bg": "Кобальтовый акцент на главной задаче.",
        },
        "intensity_default": "один яркий, но не кричащий акцент",
        "avoid_candidates": (
            {"name": "Блёклый бежевый", "why": "дробный яркий тон разбрасывает внимание по мелочам", "amplifies": ("scatter", "noise")},
        ),
    },
    {
        "name": "Слоновая кость",
        "tags": ("hold_distance", "boundaries", "slow_reply", "clarity"),
        "symbolic_property": "лёгкая дистанция — граница, которая не давит и не тяжелеет",
        "apply": {
            "clothing": "Молочно-белый свитер или рубашка цвета слоновой кости.",
            "clothing_warm": "Молочно-белая рубашка или лёгкий слой цвета слоновой кости.",
            "clothing_cold": "Молочно-белый свитер или плотная рубашка цвета слоновой кости.",
            "accessory": "Светлый шарф или сумка нейтрального тона.",
            "accessory_warm": "Светлый браслет или тонкий платок.",
            "accessory_cold": "Светлый шарф или перчатки.",
            "workspace": "Один светлый нейтральный предмет на столе.",
            "makeup": None,
            "ui_or_bg": "Светлый нейтральный фон в заметках дня.",
        },
        "intensity_default": "фон, не акцент — можно взять базой образа",
        "avoid_candidates": (
            {"name": "Тяжёлый чёрный", "why": "тяжёлый акцент усиливает давление «надо уже»", "amplifies": ("pressure", "harsh")},
        ),
    },
    # --- Layer B (generator tags + catalog together; 2026-08-02) ---
    # Champagne held — no quiet_celebration signal in conflict model.
    {
        "name": "Шафрановый",
        "tags": ("creative_spark", "generous_warmth"),
        "symbolic_property": "искра без спешки — творческий импульс, которому не нужно оправдание",
        "apply": {
            "clothing": "Шафрановый шарф, свитер или яркий акцент в одежде.",
            "clothing_warm": "Шафрановый шарф или яркий акцент в лёгкой одежде.",
            "clothing_cold": "Шафрановый шарф, свитер или яркий акцент в одежде.",
            "accessory": "Украшение или чехол медово-оранжевого тона.",
            "accessory_warm": "Шафрановый браслет или тонкий платок.",
            "accessory_cold": "Шафрановый шарф или тёплые перчатки.",
            "workspace": "Шафрановый стикер на творческой задаче.",
            "makeup": None,
            "ui_or_bg": "Тёплый оранжевый акцент в заметках творческой сферы.",
        },
        "intensity_default": "один яркий акцент — шафран не любит разбавления",
        "avoid_candidates": (
            # editorial numb/flat → live amplify set
            {"name": "Блёклый серый", "why": "дробный яркий тон разбрасывает внимание по мелочам", "amplifies": ("scatter", "noise")},
        ),
    },
    {
        "name": "Терракотовый",
        "tags": ("home_warmth", "belonging"),
        "symbolic_property": "тепло дома как опора — принадлежность месту, не просто устойчивость",
        "apply": {
            "clothing": "Терракотовый свитер, платье или слой outerwear.",
            "clothing_warm": "Терракотовое платье, топ или лёгкий слой.",
            "clothing_cold": "Терракотовый свитер, платье или слой outerwear.",
            "accessory": "Керамическое украшение или сумка терракотового тона.",
            "accessory_warm": "Терракотовый браслет или лёгкая сумка.",
            "accessory_cold": "Терракотовый шарф или плотная сумка.",
            "workspace": "Терракотовый предмет или ткань дома, не на рабочем столе.",
            "makeup": None,
            "ui_or_bg": None,
        },
        "intensity_default": "один тёплый слой, лучше дома, чем на работе",
        "avoid_candidates": (
            {"name": "Холодный стальной", "why": "резкий тон делает общение суше и острее, чем нужно сегодня", "amplifies": ("harsh", "over_control")},
        ),
    },
    {
        "name": "Гранатовый",
        "tags": ("passionate_assertion", "vital_courage"),
        "symbolic_property": "честная страсть — показать желание, а не смягчать его до вежливости",
        "apply": {
            "clothing": "Гранатовый топ, платье или шарф.",
            "clothing_warm": "Гранатовый топ, платье или лёгкий шарф.",
            "clothing_cold": "Гранатовый свитер, платье или тёплый шарф.",
            "accessory": "Украшение глубокого красного тона.",
            "accessory_warm": "Гранатовый браслет или тонкий платок.",
            "accessory_cold": "Гранатовый шарф или перчатки.",
            "workspace": None,
            "makeup": "Помада или тени глубокого гранатового.",
            "ui_or_bg": None,
        },
        "intensity_default": "один насыщенный акцент — не костюм целиком",
        "avoid_candidates": (
            {"name": "Блёклый пастельный", "why": "розовый тон усиливает желание сгладить и угодить — сегодня это не союзник", "amplifies": ("please", "soft_over_truth")},
        ),
    },
    {
        "name": "Хризолитовый",
        "tags": ("confident_abundance", "steady_growth"),
        "symbolic_property": "уверенность в росте — не только решение, но и спокойное ощущение достатка",
        "apply": {
            "clothing": "Хризолитовый шарф или акцент в одежде.",
            "clothing_warm": "Хризолитовый шарф или лёгкий акцент в одежде.",
            "clothing_cold": "Хризолитовый шарф, свитер или акцент в одежде.",
            "accessory": "Украшение светло-зелёного камня.",
            "accessory_warm": "Хризолитовый браслет или тонкий платок.",
            "accessory_cold": "Хризолитовый шарф или тёплые перчатки.",
            "workspace": "Хризолитовый стикер на финансовой задаче.",
            "makeup": None,
            "ui_or_bg": "Светло-зелёный акцент в финансовой заметке.",
        },
        "intensity_default": "один спокойный акцент",
        "avoid_candidates": (
            # editorial numb → live amplify set
            {"name": "Тусклый коричневый", "why": "тяжёлый акцент усиливает давление «надо уже»", "amplifies": ("pressure", "harsh")},
        ),
    },
    {
        "name": "Дымчато-сиреневый",
        "tags": ("gentle_closure", "honor_loss"),
        "symbolic_property": "мягкое прощание — закрыть тему честно, не пряча и не драматизируя",
        "apply": {
            "clothing": "Дымчато-сиреневый свитер или шарф.",
            "clothing_warm": "Дымчато-сиреневая блуза или лёгкий шарф.",
            "clothing_cold": "Дымчато-сиреневый свитер или шарф.",
            "accessory": "Приглушённое украшение сиреневого тона.",
            "accessory_warm": "Сиреневый браслет или тонкий платок.",
            "accessory_cold": "Сиреневый шарф или перчатки.",
            "workspace": None,
            "makeup": None,
            "ui_or_bg": "Приглушённый лиловый фон в заметке дня.",
        },
        "intensity_default": "мягкий, приглушённый тон",
        "avoid_candidates": (
            {"name": "Ярко-красный", "why": "тревожный акцент держит нервную готовность на взводе", "amplifies": ("alarm", "rush")},
        ),
    },
    {
        "name": "Шампань",
        "tags": ("quiet_celebration", "light_gratitude"),
        "symbolic_property": "тихая благодарность — отметить, что получилось, без громкого жеста",
        "apply": {
            "clothing": "Шампань-оттенок в одном предмете — блуза, шарф.",
            "clothing_warm": "Шампань-оттенок в одном предмете — блуза или лёгкий шарф.",
            "clothing_cold": "Шампань-оттенок в одном предмете — свитер или шарф.",
            "accessory": "Лёгкое украшение с перламутровым отливом.",
            "accessory_warm": "Шампань-акцент в браслете или тонком платке.",
            "accessory_cold": "Шампань-акцент в шарфе или перчатках.",
            "workspace": None,
            "makeup": "Шампань-хайлайтер или тени.",
            "ui_or_bg": None,
        },
        "intensity_default": "лёгкий блеск — одна деталь",
        "avoid_candidates": (
            {"name": "Тяжёлый чёрный", "why": "тяжёлый акцент усиливает давление «надо уже»", "amplifies": ("pressure",)},
        ),
    },
]


def list_color_knowledge() -> list[dict[str, Any]]:
    return list(COLOR_CATALOG_V1)


def sanitize_color_display_name(name: str | None) -> str:
    """Strip trap-theme glue from color names (legacy «вежливость» mash).

    Color name and trap theme are separate fields — never embed theme in name.
    """
    t = str(name or "").strip()
    if not t:
        return ""
    t = re.sub(r"\s*«[^»]*»\s*", " ", t)
    t = re.sub(r"\s*[\"“”][^\"“”]*[\"“”]\s*", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def clothing_season_bucket(month: int | None) -> str:
    """NH meteorological warm (Apr–Sep) vs cold (Oct–Mar) for clothing copy."""
    m = int(month or 0)
    if m in (4, 5, 6, 7, 8, 9):
        return "warm"
    return "cold"


def resolve_seasonal_apply(apply: dict[str, Any] | None, *, month: int | None) -> dict[str, Any]:
    """Pick clothing/accessory for current season; keep other surfaces flat."""
    src = dict(apply or {})
    bucket = clothing_season_bucket(month)
    clothing = src.get(f"clothing_{bucket}") or src.get("clothing")
    accessory = src.get(f"accessory_{bucket}") or src.get("accessory")
    out = {
        "clothing": clothing,
        "accessory": accessory,
        "workspace": src.get("workspace"),
        "makeup": src.get("makeup"),
        "ui_or_bg": src.get("ui_or_bg"),
    }
    return out


def avoid_psychology_why(candidate: dict[str, Any] | None) -> str:
    """Color-psychology avoid justification — never paste scene trap prose."""
    cand = candidate or {}
    why = str(cand.get("why") or "").strip()
    if why:
        return why
    return "этот акцент усиливает визуальный шум — сегодня лучше держать его вне поля"


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
    """Score catalog row against needed tags.

    Layer-B primary tags are sparse sphere/keyword triggers. Without a specialty
    bonus, broad core rows that only share default calm/clarity would always
    win ties and leave Layer-B colors unreachable in practice.
    """
    tags = set(entry.get("tags") or ())
    overlap = tags & needed_tags
    if not overlap:
        return 0
    specialty = len(overlap & LAYER_B_PRIMARY_TAGS)
    return len(overlap) + 5 * specialty


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
        if name in PENDING_LAYER_B_COLORS:
            errors.append(f"{name}: pending color must not be in live catalog")
        prop = str(row.get("symbolic_property") or "").strip()
        if len(prop) < 12:
            errors.append(f"{name}: symbolic_property too short")
        tags = tuple(row.get("tags") or ())
        if len(tags) < 2:
            errors.append(f"{name}: need ≥2 tags")
        unknown = [t for t in tags if t not in LIVE_NEEDED_COLOR_TAGS]
        if unknown:
            errors.append(f"{name}: tags not in LIVE_NEEDED_COLOR_TAGS {unknown}")
        for cand in row.get("avoid_candidates") or ():
            amplifies = tuple((cand or {}).get("amplifies") or ())
            dead = [a for a in amplifies if a not in LIVE_AVOID_AMPLIFY_TAGS]
            if dead:
                errors.append(f"{name}: dead avoid amplifies {dead}")
            why = str((cand or {}).get("why") or "").strip()
            if len(why) < 12:
                errors.append(f"{name}: avoid candidate needs psychology why (≥12 chars)")
    return errors

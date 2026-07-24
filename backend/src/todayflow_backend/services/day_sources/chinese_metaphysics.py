"""Chinese metaphysics day factors — Gan-Zhi, elements, Jianchu, jieqi (canon §5.7).

v0: civil local date → sexagenary day pillar. Jianchu from solar-month branch.
BaZi / clashes stay Personal later.
"""

from __future__ import annotations

from datetime import date
from typing import Any

from todayflow_backend.services.day_sources.panchanga import tropical_sun_longitude

# 1984-02-02 is a Jia-Zi (甲子) day — common sexagenary day epoch.
_DAY_PILLAR_EPOCH = date(1984, 2, 2)

_STEMS: list[tuple[str, str, str, str, str]] = [
    # id, pinyin, zh, element, polarity
    ("jia", "Jia", "甲", "wood", "yang"),
    ("yi", "Yi", "乙", "wood", "yin"),
    ("bing", "Bing", "丙", "fire", "yang"),
    ("ding", "Ding", "丁", "fire", "yin"),
    ("wu", "Wu", "戊", "earth", "yang"),
    ("ji", "Ji", "己", "earth", "yin"),
    ("geng", "Geng", "庚", "metal", "yang"),
    ("xin", "Xin", "辛", "metal", "yin"),
    ("ren", "Ren", "壬", "water", "yang"),
    ("gui", "Gui", "癸", "water", "yin"),
]

_BRANCHES: list[tuple[str, str, str, str, str]] = [
    # id, pinyin, zh, animal, element
    ("zi", "Zi", "子", "rat", "water"),
    ("chou", "Chou", "丑", "ox", "earth"),
    ("yin", "Yin", "寅", "tiger", "wood"),
    ("mao", "Mao", "卯", "rabbit", "wood"),
    ("chen", "Chen", "辰", "dragon", "earth"),
    ("si", "Si", "巳", "snake", "fire"),
    ("wu", "Wu", "午", "horse", "fire"),
    ("wei", "Wei", "未", "goat", "earth"),
    ("shen", "Shen", "申", "monkey", "metal"),
    ("you", "You", "酉", "rooster", "metal"),
    ("xu", "Xu", "戌", "dog", "earth"),
    ("hai", "Hai", "亥", "pig", "water"),
]

_ELEMENT_RU = {
    "wood": "Дерево",
    "fire": "Огонь",
    "earth": "Земля",
    "metal": "Металл",
    "water": "Вода",
}

_POLARITY_RU = {"yang": "Ян", "yin": "Инь"}

_ANIMAL_RU = {
    "rat": "Крыса",
    "ox": "Бык",
    "tiger": "Тигр",
    "rabbit": "Кролик",
    "dragon": "Дракон",
    "snake": "Змея",
    "horse": "Лошадь",
    "goat": "Коза",
    "monkey": "Обезьяна",
    "rooster": "Петух",
    "dog": "Собака",
    "pig": "Свинья",
}

# Jianchu 12 officers (Establish…Close)
_JIANCHU: list[tuple[str, str, str]] = [
    ("establish", "Jian", "Установление"),
    ("remove", "Chu", "Удаление"),
    ("full", "Man", "Полнота"),
    ("balance", "Ping", "Баланс"),
    ("stable", "Ding", "Стабильность"),
    ("initiate", "Zhi", "Начало"),
    ("destruction", "Po", "Разрушение"),
    ("danger", "Wei", "Опасность"),
    ("success", "Cheng", "Успех"),
    ("receive", "Shou", "Принятие"),
    ("open", "Kai", "Открытие"),
    ("close", "Bi", "Закрытие"),
]

# Soft suitable / avoid hints by officer (almanac_actions lite).
_JIANCHU_ACTIONS: dict[str, dict[str, list[str]]] = {
    "establish": {
        "suitable_ru": ["начало дел", "регистрация", "закладка"],
        "avoid_ru": ["снос", "разрывы"],
    },
    "remove": {
        "suitable_ru": ["уборка", "лечение", "завершение лишнего"],
        "avoid_ru": ["свадьба", "открытие бизнеса"],
    },
    "full": {
        "suitable_ru": ["наполнение", "обучение", "подарки"],
        "avoid_ru": ["суды", "переезды"],
    },
    "balance": {
        "suitable_ru": ["переговоры", "ремонт", "планирование"],
        "avoid_ru": ["рискованные сделки"],
    },
    "stable": {
        "suitable_ru": ["строительство", "инвестиции", "рутина"],
        "avoid_ru": ["переезды", "резкие разрывы"],
    },
    "initiate": {
        "suitable_ru": ["запуски", "поездки", "обучение"],
        "avoid_ru": ["тяжёлые операции"],
    },
    "destruction": {
        "suitable_ru": ["снос", "разрыв старого"],
        "avoid_ru": ["свадьба", "открытие", "подписание"],
    },
    "danger": {
        "suitable_ru": ["осторожные дела", "проверка рисков"],
        "avoid_ru": ["путешествия", "операции", "споры"],
    },
    "success": {
        "suitable_ru": ["свадьба", "открытие", "подписание", "праздник"],
        "avoid_ru": ["судебные конфликты"],
    },
    "receive": {
        "suitable_ru": ["сбор урожая", "получение", "встречи"],
        "avoid_ru": ["агрессивные запуски"],
    },
    "open": {
        "suitable_ru": ["открытие", "публикация", "переговоры"],
        "avoid_ru": ["закрытие проектов"],
    },
    "close": {
        "suitable_ru": ["завершение", "отдых", "архив"],
        "avoid_ru": ["новые старты", "свадьба"],
    },
}

# 24 solar terms at tropical longitude 0, 15, 30, …
_SOLAR_TERMS: list[tuple[str, str, float]] = [
    ("lichun", "立春", 315.0),
    ("yushui", "雨水", 330.0),
    ("jingzhe", "惊蛰", 345.0),
    ("chunfen", "春分", 0.0),
    ("qingming", "清明", 15.0),
    ("guyu", "谷雨", 30.0),
    ("lixia", "立夏", 45.0),
    ("xiaoman", "小满", 60.0),
    ("mangzhong", "芒种", 75.0),
    ("xiazhi", "夏至", 90.0),
    ("xiaoshu", "小暑", 105.0),
    ("dashu", "大暑", 120.0),
    ("liqiu", "立秋", 135.0),
    ("chushu", "处暑", 150.0),
    ("bailu", "白露", 165.0),
    ("qiufen", "秋分", 180.0),
    ("hanlu", "寒露", 195.0),
    ("shuangjiang", "霜降", 210.0),
    ("lidong", "立冬", 225.0),
    ("xiaoxue", "小雪", 240.0),
    ("daxue", "大雪", 255.0),
    ("dongzhi", "冬至", 270.0),
    ("xiaohan", "小寒", 285.0),
    ("dahan", "大寒", 300.0),
]

_SOLAR_TERM_RU = {
    "lichun": "Начало весны",
    "yushui": "Дождевая вода",
    "jingzhe": "Пробуждение насекомых",
    "chunfen": "Весеннее равноденствие",
    "qingming": "Чистый свет",
    "guyu": "Хлебный дождь",
    "lixia": "Начало лета",
    "xiaoman": "Малое изобилие",
    "mangzhong": "Колосистые хлеба",
    "xiazhi": "Летнее солнцестояние",
    "xiaoshu": "Малая жара",
    "dashu": "Большая жара",
    "liqiu": "Начало осени",
    "chushu": "Конец жары",
    "bailu": "Белая роса",
    "qiufen": "Осеннее равноденствие",
    "hanlu": "Холодная роса",
    "shuangjiang": "Иней",
    "lidong": "Начало зимы",
    "xiaoxue": "Малый снег",
    "daxue": "Большой снег",
    "dongzhi": "Зимнее солнцестояние",
    "xiaohan": "Малый холод",
    "dahan": "Большой холод",
}


def day_pillar_index(d: date) -> int:
    return (d - _DAY_PILLAR_EPOCH).days % 60


def gan_zhi_from_index(idx: int) -> dict[str, Any]:
    idx = idx % 60
    stem = _STEMS[idx % 10]
    branch = _BRANCHES[idx % 12]
    return {
        "cycle_index": idx,
        "stem": {
            "id": stem[0],
            "pinyin": stem[1],
            "zh": stem[2],
            "element": stem[3],
            "element_ru": _ELEMENT_RU[stem[3]],
            "polarity": stem[4],
            "polarity_ru": _POLARITY_RU[stem[4]],
        },
        "branch": {
            "id": branch[0],
            "pinyin": branch[1],
            "zh": branch[2],
            "animal": branch[3],
            "animal_ru": _ANIMAL_RU[branch[3]],
            "element": branch[4],
            "element_ru": _ELEMENT_RU[branch[4]],
            "index": idx % 12,
        },
        "label_zh": f"{stem[2]}{branch[2]}",
        "label_pinyin": f"{stem[1]}-{branch[1]}",
    }


def solar_month_branch_index(sun_lon: float) -> int:
    """Branch index of Chinese solar month; Yin starts near Lichun (315°)."""
    adjusted = (float(sun_lon) - 315.0) % 360.0
    month_offset = int(adjusted // 30.0)  # 0 = Yin
    return (2 + month_offset) % 12  # Yin=2


def jianchu_from_branches(day_branch_index: int, month_branch_index: int) -> dict[str, Any]:
    officer_i = (day_branch_index - month_branch_index) % 12
    oid, pinyin, name_ru = _JIANCHU[officer_i]
    actions = _JIANCHU_ACTIONS[oid]
    return {
        "id": oid,
        "pinyin": pinyin,
        "name_ru": name_ru,
        "index": officer_i,
        "suitable_ru": list(actions["suitable_ru"]),
        "avoid_ru": list(actions["avoid_ru"]),
    }


def current_solar_term(sun_lon: float) -> dict[str, Any]:
    lon = float(sun_lon) % 360.0
    start_lon = (int(lon // 15.0) * 15) % 360.0
    term = next(t for t in _SOLAR_TERMS if abs(t[2] - start_lon) < 1e-9)
    tid, zh, _ = term
    next_lon = (start_lon + 15.0) % 360.0
    return {
        "id": tid,
        "zh": zh,
        "name_ru": _SOLAR_TERM_RU[tid],
        "start_longitude": start_lon,
        "sun_longitude": round(lon, 4),
        "degrees_into_term": round((lon - start_lon) % 360.0, 4),
        "next_term_longitude": next_lon,
    }


def build_chinese_day_payload(d: date) -> dict[str, Any]:
    idx = day_pillar_index(d)
    pillar = gan_zhi_from_index(idx)
    sun_lon = tropical_sun_longitude(d)
    month_bi = solar_month_branch_index(sun_lon)
    officer = jianchu_from_branches(pillar["branch"]["index"], month_bi)
    term = current_solar_term(sun_lon)
    month_branch = _BRANCHES[month_bi]

    stem_el = pillar["stem"]["element"]
    branch_el = pillar["branch"]["element"]

    summary = (
        f"Китайский день {pillar['label_zh']} ({pillar['label_pinyin']}): "
        f"{pillar['stem']['polarity_ru']} {_ELEMENT_RU[stem_el]}, "
        f"ветвь {pillar['branch']['animal_ru']}. "
        f"Управитель Jianchu — {officer['name_ru']}. "
        f"Солнечный термин — {term['name_ru']}."
    )

    return {
        "gan_zhi_day": pillar,
        "five_elements_day": {
            "stem_element": stem_el,
            "stem_element_ru": _ELEMENT_RU[stem_el],
            "stem_polarity": pillar["stem"]["polarity"],
            "stem_polarity_ru": pillar["stem"]["polarity_ru"],
            "branch_element": branch_el,
            "branch_element_ru": _ELEMENT_RU[branch_el],
        },
        "jianchu_officer": officer,
        "almanac_actions": {
            "suitable_ru": officer["suitable_ru"],
            "avoid_ru": officer["avoid_ru"],
            "source": "jianchu_v0",
        },
        "solar_term": term,
        "solar_month_branch": {
            "id": month_branch[0],
            "pinyin": month_branch[1],
            "zh": month_branch[2],
            "index": month_bi,
        },
        "capability_ids": [
            "gan_zhi_day",
            "five_elements_day",
            "jianchu_officer",
            "almanac_actions",
            "solar_terms",
        ],
        "summary_ru": summary,
        "target_date": d.isoformat(),
        "method": "sexagenary_day_v0",
    }

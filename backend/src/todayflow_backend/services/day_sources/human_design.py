"""Human Design v0 — tropical longitude → 64 gates / 6 lines (canon §5.9).

School: standard Rave Mandala (Gate 41 starts at 02° Aquarius).
Sun/Moon longitudes reuse closed-form helpers from panchanga (no Swiss in backend).
Design chart uses the common ~88-day solar-arc approximation until timed ephemeris walks land.
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from todayflow_backend.services.day_sources.panchanga import (
    tropical_moon_longitude,
    tropical_sun_longitude,
)

# Gate 41 opens at 02°00' Aquarius = absolute tropical longitude 302°.
GATE_41_START_LON = 302.0
GATE_SPAN = 360.0 / 64.0  # 5°37'30"
LINE_SPAN = GATE_SPAN / 6.0  # 0°56'15"
DESIGN_SOLAR_ARC_DAYS = 88

# Wheel order starting at Gate 41, increasing tropical longitude.
GATE_WHEEL: tuple[int, ...] = (
    41,
    19,
    13,
    49,
    30,
    55,
    37,
    63,
    22,
    36,
    25,
    17,
    21,
    51,
    42,
    3,
    27,
    24,
    2,
    23,
    8,
    20,
    16,
    35,
    45,
    12,
    15,
    52,
    39,
    53,
    62,
    56,
    31,
    33,
    7,
    4,
    29,
    59,
    40,
    64,
    47,
    6,
    46,
    18,
    48,
    57,
    32,
    50,
    28,
    44,
    1,
    43,
    14,
    34,
    9,
    5,
    26,
    11,
    10,
    58,
    38,
    54,
    61,
    60,
)

# Short RU themes for day copy (not full HD lexicon).
_GATE_THEME_RU: dict[int, str] = {
    1: "самовыражение",
    2: "направление",
    3: "порядок из хаоса",
    4: "формулировка ответа",
    5: "ритм",
    6: "трение и близость",
    7: "роль лидера",
    8: "вклад",
    9: "фокус",
    10: "поведение",
    11: "идеи",
    12: "осторожное слово",
    13: "слушание",
    14: "ресурсы в деле",
    15: "крайности ритма",
    16: "мастерство",
    17: "мнения",
    18: "коррекция",
    19: "потребность",
    20: "присутствие сейчас",
    21: "контроль",
    22: "открытость",
    23: "ясность",
    24: "рационализация",
    25: "невинность духа",
    26: "убеждение",
    27: "забота",
    28: "риск смысла",
    29: "обязательство",
    30: "желание",
    31: "влияние",
    32: "преемственность",
    33: "уединение и история",
    34: "сила",
    35: "опыт",
    36: "кризис роста",
    37: "дружба и договор",
    38: "бороться за смысл",
    39: "провокация",
    40: "одиночество / отдых",
    41: "старт желания",
    42: "завершение цикла",
    43: "инсайт",
    44: "бдительность",
    45: "собирать и делиться",
    46: "тело в процессе",
    47: "осознание паттерна",
    48: "глубина",
    49: "принципы",
    50: "ценности",
    51: "шоковое пробуждение",
    52: "тишина / концентрация",
    53: "начинания",
    54: "амбиция",
    55: "дух / настроение",
    56: "странник-рассказчик",
    57: "интуитивная ясность",
    58: "радость жизни",
    59: "интимность",
    60: "ограничение",
    61: "внутренняя тайна",
    62: "детали",
    63: "сомнение / вопрос",
    64: "путаница до ясности",
}


def longitude_to_gate_line(longitude: float) -> dict[str, Any]:
    """Map tropical ecliptic longitude → HD gate + line (1..6)."""
    lon = float(longitude) % 360.0
    offset = (lon - GATE_41_START_LON) % 360.0
    idx = int(offset // GATE_SPAN) % 64
    within = offset - (idx * GATE_SPAN)
    line = int(within // LINE_SPAN) + 1
    if line > 6:
        line = 6
    gate = GATE_WHEEL[idx]
    theme = _GATE_THEME_RU.get(gate, "")
    return {
        "gate": gate,
        "line": line,
        "label": f"{gate}.{line}",
        "theme_ru": theme,
        "longitude": round(lon, 4),
        "wheel_index": idx,
    }


def activation_for_date(d: date, *, body: str = "Sun") -> dict[str, Any]:
    if body == "Moon":
        lon = tropical_moon_longitude(d)
    else:
        lon = tropical_sun_longitude(d)
    act = longitude_to_gate_line(lon)
    act["body"] = body
    act["date"] = d.isoformat()
    return act


def earth_from_sun(sun_act: dict[str, Any]) -> dict[str, Any]:
    lon = (float(sun_act["longitude"]) + 180.0) % 360.0
    act = longitude_to_gate_line(lon)
    act["body"] = "Earth"
    act["date"] = sun_act.get("date")
    return act


def transit_gates_for_day(target_date: date) -> dict[str, Any]:
    sun = activation_for_date(target_date, body="Sun")
    earth = earth_from_sun(sun)
    moon = activation_for_date(target_date, body="Moon")
    summary = (
        f"Транзит HD: Солнце {sun['label']} ({sun['theme_ru']}), "
        f"Земля {earth['label']}, Луна {moon['label']}."
    )
    return {
        "capability_id": "transit_gates",
        "sun": sun,
        "earth": earth,
        "moon": moon,
        "summary_ru": summary,
        "school_canon": "rave_mandala_gate41_aquarius_2",
    }


def bodygraph_soft(
    birth_date: date,
    *,
    transit: dict[str, Any] | None = None,
    has_birth_time: bool = False,
    has_birth_place: bool = False,
) -> dict[str, Any]:
    """Soft bodygraph: Personality/Design Sun–Earth from birth date (±88d)."""
    personality_sun = activation_for_date(birth_date, body="Sun")
    personality_earth = earth_from_sun(personality_sun)
    design_date = birth_date - timedelta(days=DESIGN_SOLAR_ARC_DAYS)
    design_sun = activation_for_date(design_date, body="Sun")
    design_earth = earth_from_sun(design_sun)

    natal_gates = {
        int(personality_sun["gate"]),
        int(personality_earth["gate"]),
        int(design_sun["gate"]),
        int(design_earth["gate"]),
    }

    activations: list[dict[str, Any]] = []
    if isinstance(transit, dict):
        for key in ("sun", "earth", "moon"):
            row = transit.get(key)
            if not isinstance(row, dict):
                continue
            g = int(row.get("gate") or 0)
            if g and g in natal_gates:
                activations.append(
                    {
                        "id": f"hd-activate-{key}-{g}",
                        "kind": "transit_hits_natal_gate",
                        "transit_body": key,
                        "gate": g,
                        "line": row.get("line"),
                        "title": f"Транзит активирует ворота {g}",
                        "story_ru": (
                            f"Сегодняшний {key} в {row.get('label')} касается "
                            f"ваших ворот {g} ({_GATE_THEME_RU.get(g, '')})."
                        ),
                    }
                )

    depth = "date_only"
    if has_birth_time and has_birth_place:
        depth = "time_place_known"
    elif has_birth_time or has_birth_place:
        depth = "partial_birth_data"

    summary = (
        f"Бодиграф (soft): Personality Sun {personality_sun['label']}, "
        f"Design Sun {design_sun['label']}."
    )
    if activations:
        summary = f"{summary} Активаций транзитом сегодня: {len(activations)}."

    return {
        "capability_id": "bodygraph_interaction",
        "depth": depth,
        "approximation": "design_minus_88d_solar_arc",
        "personality": {"sun": personality_sun, "earth": personality_earth},
        "design": {
            "sun": design_sun,
            "earth": design_earth,
            "approx_date": design_date.isoformat(),
        },
        "natal_sun_earth_gates": sorted(natal_gates),
        "activations": activations,
        "summary_ru": summary,
        "school_canon": "rave_mandala_gate41_aquarius_2",
    }


def build_human_design_payload(
    target_date: date,
    *,
    birth_date: date | None = None,
    has_birth_time: bool = False,
    has_birth_place: bool = False,
) -> dict[str, Any]:
    transit = transit_gates_for_day(target_date)
    caps = ["transit_gates"]
    bodygraph = None
    if birth_date is not None:
        bodygraph = bodygraph_soft(
            birth_date,
            transit=transit,
            has_birth_time=has_birth_time,
            has_birth_place=has_birth_place,
        )
        caps.append("bodygraph_interaction")

    beats: list[dict[str, Any]] = [
        {
            "id": "hd.transit.sun",
            "kind": "transit_gate",
            "title": f"Солнце {transit['sun']['label']}",
            "story_ru": (
                f"Транзитное Солнце в воротах {transit['sun']['label']} — "
                f"{transit['sun']['theme_ru']}."
            ),
            "evidence_ref": "human_design.transit_gates",
        }
    ]
    if bodygraph and bodygraph.get("activations"):
        for act in bodygraph["activations"][:3]:
            beats.append(
                {
                    "id": act["id"],
                    "kind": act["kind"],
                    "title": act["title"],
                    "story_ru": act["story_ru"],
                    "evidence_ref": "human_design.bodygraph_interaction",
                }
            )

    summary = str(transit.get("summary_ru") or "")
    if bodygraph and bodygraph.get("activations"):
        summary = f"{summary} {bodygraph['summary_ru']}"
    elif bodygraph:
        summary = f"{summary} {bodygraph['summary_ru']}"

    return {
        "capability_ids": caps,
        "transit_gates": transit,
        "bodygraph": bodygraph,
        "beats": beats,
        "summary_ru": summary[:420],
        "school_canon": "rave_mandala_gate41_aquarius_2",
    }

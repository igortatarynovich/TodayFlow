"""Human Design v0 — tropical longitude → 64 gates / 6 lines (canon §5.9).

School: standard Rave Mandala (Gate 41 starts at 02° Aquarius).
Longitudes prefer Swiss snapshots via ephemeris_bridge; fallback mean lon.
Design chart prefers Swiss snapshot at birth−88d when ephemeris bridge provides it;
otherwise soft mean longitude on the shifted calendar day.
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from todayflow_backend.services.day_sources.classical_longitudes import classical_bodies
from todayflow_backend.services.day_sources.ephemeris_bridge import resolve_body_longitude

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

# Standard Rave channels: (gate_a, gate_b, id, name_ru, center_a, center_b).
_CHANNELS: tuple[tuple[int, int, str, str, str, str], ...] = (
    (1, 8, "1-8", "Вдохновение", "g", "throat"),
    (2, 14, "2-14", "Ритм биения", "g", "sacral"),
    (3, 60, "3-60", "Мутация", "sacral", "root"),
    (4, 63, "4-63", "Логика", "ajna", "head"),
    (5, 15, "5-15", "Ритмы", "sacral", "g"),
    (6, 59, "6-59", "Близость", "solar_plexus", "sacral"),
    (7, 31, "7-31", "Альфа", "g", "throat"),
    (9, 52, "9-52", "Концентрация", "sacral", "root"),
    (10, 20, "10-20", "Пробуждение", "g", "throat"),
    (10, 34, "10-34", "Исследование", "g", "sacral"),
    (10, 57, "10-57", "Совершенная форма", "g", "spleen"),
    (11, 56, "11-56", "Любопытство", "ajna", "throat"),
    (12, 22, "12-22", "Открытость", "throat", "solar_plexus"),
    (13, 33, "13-33", "Странник", "g", "throat"),
    (16, 48, "16-48", "Длина волны", "throat", "spleen"),
    (17, 62, "17-62", "Принятие", "ajna", "throat"),
    (18, 58, "18-58", "Суждение", "spleen", "root"),
    (19, 49, "19-49", "Синтез", "root", "solar_plexus"),
    (20, 34, "20-34", "Харизма", "throat", "sacral"),
    (20, 57, "20-57", "Мозговая волна", "throat", "spleen"),
    (21, 45, "21-45", "Денежная линия", "heart", "throat"),
    (23, 43, "23-43", "Структурирование", "throat", "ajna"),
    (24, 61, "24-61", "Осознание", "ajna", "head"),
    (25, 51, "25-51", "Инициация", "g", "heart"),
    (26, 44, "26-44", "Сдача", "heart", "spleen"),
    (27, 50, "27-50", "Сохранение", "sacral", "spleen"),
    (28, 38, "28-38", "Борьба", "spleen", "root"),
    (29, 46, "29-46", "Открытие", "sacral", "g"),
    (30, 41, "30-41", "Узнавание", "solar_plexus", "root"),
    (32, 54, "32-54", "Трансформация", "spleen", "root"),
    (35, 36, "35-36", "Преходящесть", "throat", "solar_plexus"),
    (37, 40, "37-40", "Сообщество", "solar_plexus", "heart"),
    (39, 55, "39-55", "Эмоция", "root", "solar_plexus"),
    (42, 53, "42-53", "Созревание", "sacral", "root"),
    (47, 64, "47-64", "Абстракция", "ajna", "head"),
)

_CENTER_RU: dict[str, str] = {
    "head": "Голова",
    "ajna": "Аджна",
    "throat": "Горло",
    "g": "G-центр",
    "heart": "Эго / Воля",
    "sacral": "Сакрал",
    "solar_plexus": "Солнечное сплетение",
    "spleen": "Селезёнка",
    "root": "Корень",
}


def resolve_channels(active_gates: set[int]) -> list[dict[str, Any]]:
    """Return channels whose both gates are present in active_gates."""
    out: list[dict[str, Any]] = []
    gates = {int(g) for g in active_gates if g}
    for a, b, cid, name_ru, c1, c2 in _CHANNELS:
        if a in gates and b in gates:
            out.append(
                {
                    "id": cid,
                    "gates": [a, b],
                    "name_ru": name_ru,
                    "centers": [c1, c2],
                    "centers_ru": [_CENTER_RU[c1], _CENTER_RU[c2]],
                }
            )
    return out


def defined_centers_from_channels(channels: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: dict[str, list[str]] = {}
    for ch in channels:
        for c in ch.get("centers") or []:
            seen.setdefault(str(c), []).append(str(ch.get("id")))
    return [
        {
            "id": cid,
            "name_ru": _CENTER_RU.get(cid, cid),
            "via_channels": ch_ids,
        }
        for cid, ch_ids in sorted(seen.items())
    ]


def build_channels_payload(
    *,
    transit_gates: dict[str, Any],
    bodygraph: dict[str, Any] | None = None,
) -> dict[str, Any]:
    transit_set: set[int] = set()
    # Prefer explicit planets list; fall back to sun/earth/moon keys.
    planet_rows = transit_gates.get("planets") if isinstance(transit_gates, dict) else None
    if isinstance(planet_rows, list):
        for row in planet_rows:
            if isinstance(row, dict) and row.get("gate"):
                transit_set.add(int(row["gate"]))
    else:
        for key in ("sun", "earth", "moon"):
            row = transit_gates.get(key) if isinstance(transit_gates, dict) else None
            if isinstance(row, dict) and row.get("gate"):
                transit_set.add(int(row["gate"]))

    natal_set: set[int] = set()
    if isinstance(bodygraph, dict):
        for g in bodygraph.get("natal_gates") or bodygraph.get("natal_sun_earth_gates") or []:
            natal_set.add(int(g))

    # Channels from transit-only and from natal∪transit (bodygraph interaction).
    transit_channels = resolve_channels(transit_set)
    combined = transit_set | natal_set
    combined_channels = resolve_channels(combined) if natal_set else list(transit_channels)
    # Prefer reporting channels that appear in the combined (personal) view when natal exists.
    channels = combined_channels
    centers = defined_centers_from_channels(channels)

    if channels:
        labels = ", ".join(f"{c['id']} ({c['name_ru']})" for c in channels[:3])
        summary = f"Каналы HD (soft): {labels}" + (
            f" и ещё {len(channels) - 3}." if len(channels) > 3 else "."
        )
        if centers:
            summary += " Центры: " + ", ".join(c["name_ru"] for c in centers[:4]) + "."
    else:
        summary = (
            "Каналы HD (soft): полной пары ворот сегодня нет "
            "(классические планеты ± natal gates)."
        )

    return {
        "capability_id": "channels",
        "active_gates": {
            "transit": sorted(transit_set),
            "natal": sorted(natal_set),
            "combined": sorted(combined),
        },
        "channels": channels,
        "transit_only_channels": transit_channels,
        "defined_centers": centers,
        "summary_ru": summary,
        "school_canon": "rave_channels_v1_full_planet_set",
        "limitation_ru": (
            "Ворота Sun…Pluto + Earth (mean longitude noon). "
            "Точный Swiss / Design-время — later."
        ),
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


def activation_for_date(
    d: date,
    *,
    body: str = "Sun",
    ephemeris: dict[str, Any] | None = None,
    role: str = "transit",
) -> dict[str, Any]:
    if body == "Earth":
        sun = activation_for_date(d, body="Sun", ephemeris=ephemeris, role=role)
        act = earth_from_sun(sun)
        act["ephemeris_source"] = sun.get("ephemeris_source")
        return act
    resolved = resolve_body_longitude(body, d, ephemeris=ephemeris, role=role)
    lon = float(resolved["longitude"])
    act = longitude_to_gate_line(lon)
    act["body"] = body
    act["date"] = d.isoformat()
    act["ephemeris_source"] = resolved.get("source")
    return act


def earth_from_sun(sun_act: dict[str, Any]) -> dict[str, Any]:
    lon = (float(sun_act["longitude"]) + 180.0) % 360.0
    act = longitude_to_gate_line(lon)
    act["body"] = "Earth"
    act["date"] = sun_act.get("date")
    return act


def transit_gates_for_day(
    target_date: date,
    *,
    ephemeris: dict[str, Any] | None = None,
) -> dict[str, Any]:
    planets: list[dict[str, Any]] = []
    by_body: dict[str, dict[str, Any]] = {}
    sources: set[str] = set()
    for body in classical_bodies():
        act = activation_for_date(
            target_date, body=body, ephemeris=ephemeris, role="transit"
        )
        planets.append(act)
        by_body[body.lower()] = act
        if act.get("ephemeris_source"):
            sources.add(str(act["ephemeris_source"]))
    earth = earth_from_sun(by_body["sun"])
    earth["ephemeris_source"] = by_body["sun"].get("ephemeris_source")
    planets.append(earth)
    by_body["earth"] = earth

    sun = by_body["sun"]
    moon = by_body["moon"]
    swiss = "astro_service_swiss" in sources
    depth = "full_planet_set_swiss_noon" if swiss else "full_planet_set_mean_lon"
    summary = (
        f"Транзит HD ({'Swiss noon' if swiss else 'soft mean'}): "
        f"Солнце {sun['label']} ({sun['theme_ru']}), "
        f"Земля {earth['label']}, Луна {moon['label']}; "
        f"ещё {len(planets) - 3} тел."
    )
    return {
        "capability_id": "transit_gates",
        "depth": depth,
        "ephemeris_source": "astro_service_swiss" if swiss else "mean_longitude_soft",
        "sun": sun,
        "earth": earth,
        "moon": moon,
        "planets": planets,
        "summary_ru": summary,
        "school_canon": "rave_mandala_gate41_aquarius_2",
        "limitation_ru": (
            "Sun…Pluto + Earth. Swiss transit noon when ephemeris bridge is present; "
            "else mean longitude. Design −88d uses separate Swiss walk when present."
        ),
    }


def bodygraph_soft(
    birth_date: date,
    *,
    transit: dict[str, Any] | None = None,
    has_birth_time: bool = False,
    has_birth_place: bool = False,
    ephemeris: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Soft bodygraph: Personality/Design classical planets (±88d Design)."""
    personality: dict[str, dict[str, Any]] = {}
    for body in classical_bodies():
        personality[body.lower()] = activation_for_date(
            birth_date, body=body, ephemeris=ephemeris, role="natal"
        )
    personality["earth"] = earth_from_sun(personality["sun"])

    design_date = birth_date - timedelta(days=DESIGN_SOLAR_ARC_DAYS)
    design_swiss = (
        isinstance(ephemeris, dict)
        and isinstance(ephemeris.get("design_minus_88d"), dict)
        and bool((ephemeris.get("design_minus_88d") or {}).get("bodies"))
    )
    design: dict[str, dict[str, Any]] = {}
    for body in classical_bodies():
        design[body.lower()] = activation_for_date(
            design_date,
            body=body,
            ephemeris=ephemeris,
            role="design" if design_swiss else "transit",
        )
    design["earth"] = earth_from_sun(design["sun"])

    natal_gates = {
        int(row["gate"])
        for block in (personality, design)
        for row in block.values()
        if isinstance(row, dict) and row.get("gate")
    }

    activations: list[dict[str, Any]] = []
    if isinstance(transit, dict):
        transit_rows = transit.get("planets") if isinstance(transit.get("planets"), list) else []
        if not transit_rows:
            transit_rows = [
                transit[k]
                for k in ("sun", "earth", "moon")
                if isinstance(transit.get(k), dict)
            ]
        for row in transit_rows:
            if not isinstance(row, dict):
                continue
            g = int(row.get("gate") or 0)
            body = str(row.get("body") or "")
            if g and g in natal_gates:
                activations.append(
                    {
                        "id": f"hd-activate-{body.lower()}-{g}",
                        "kind": "transit_hits_natal_gate",
                        "transit_body": body,
                        "gate": g,
                        "line": row.get("line"),
                        "title": f"Транзит активирует ворота {g}",
                        "story_ru": (
                            f"Сегодняшний {body} в {row.get('label')} касается "
                            f"ваших ворот {g} ({_GATE_THEME_RU.get(g, '')})."
                        ),
                    }
                )

    depth = "date_only"
    if has_birth_time and has_birth_place:
        depth = "time_place_known"
    elif has_birth_time or has_birth_place:
        depth = "partial_birth_data"
    if design_swiss:
        depth = f"{depth}_design_swiss"

    personality_swiss = any(
        str(row.get("ephemeris_source") or "").startswith("astro_service")
        for row in personality.values()
        if isinstance(row, dict)
    )
    if design_swiss:
        approx = "design_minus_88d_swiss_walk"
    elif personality_swiss:
        approx = "design_minus_88d_mean_lon_personality_swiss"
    else:
        approx = "design_minus_88d_classical_mean_lon"

    summary = (
        f"Бодиграф (classical): Personality Sun {personality['sun']['label']}, "
        f"Design Sun {design['sun']['label']}; natal gates {len(natal_gates)}."
    )
    if design_swiss:
        summary = f"{summary} Design −88d: Swiss."
    if activations:
        summary = f"{summary} Активаций транзитом сегодня: {len(activations)}."

    return {
        "capability_id": "bodygraph_interaction",
        "depth": depth,
        "approximation": approx,
        "ephemeris_source": {
            "personality": "astro_service_swiss" if personality_swiss else "mean_longitude_soft",
            "design": "astro_service_swiss" if design_swiss else "mean_longitude_soft",
        },
        "personality": {
            "sun": personality["sun"],
            "earth": personality["earth"],
            "planets": list(personality.values()),
        },
        "design": {
            "sun": design["sun"],
            "earth": design["earth"],
            "approx_date": design_date.isoformat(),
            "planets": list(design.values()),
        },
        "natal_sun_earth_gates": sorted(
            {
                int(personality["sun"]["gate"]),
                int(personality["earth"]["gate"]),
                int(design["sun"]["gate"]),
                int(design["earth"]["gate"]),
            }
        ),
        "natal_gates": sorted(natal_gates),
        "activations": activations,
        "summary_ru": summary,
        "school_canon": "rave_mandala_gate41_aquarius_2",
        "limitation_ru": (
            "Personality/Design Sun…Pluto + Earth. "
            "Design ≈ birth−88d (Swiss walk when bridge present; else mean lon). "
            "Not a full HD BodyGraph engine (centers/type/authority deferred)."
        ),
    }


def build_human_design_payload(
    target_date: date,
    *,
    birth_date: date | None = None,
    has_birth_time: bool = False,
    has_birth_place: bool = False,
    ephemeris: dict[str, Any] | None = None,
) -> dict[str, Any]:
    transit = transit_gates_for_day(target_date, ephemeris=ephemeris)
    caps = ["transit_gates"]
    bodygraph = None
    if birth_date is not None:
        bodygraph = bodygraph_soft(
            birth_date,
            transit=transit,
            has_birth_time=has_birth_time,
            has_birth_place=has_birth_place,
            ephemeris=ephemeris,
        )
        caps.append("bodygraph_interaction")

    channels = build_channels_payload(transit_gates=transit, bodygraph=bodygraph)
    caps.append("channels")

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
    for ch in (channels.get("channels") or [])[:2]:
        beats.append(
            {
                "id": f"hd.channel.{ch['id']}",
                "kind": "channel",
                "title": f"Канал {ch['id']} · {ch['name_ru']}",
                "story_ru": (
                    f"Активен канал {ch['id']} ({ch['name_ru']}) — "
                    f"{' / '.join(ch.get('centers_ru') or [])}."
                ),
                "evidence_ref": "human_design.channels",
            }
        )

    summary = str(transit.get("summary_ru") or "")
    if bodygraph and bodygraph.get("activations"):
        summary = f"{summary} {bodygraph['summary_ru']}"
    elif bodygraph:
        summary = f"{summary} {bodygraph['summary_ru']}"
    if channels.get("channels"):
        summary = f"{summary} {channels['summary_ru']}"

    return {
        "capability_ids": caps,
        "transit_gates": transit,
        "bodygraph": bodygraph,
        "channels": channels,
        "beats": beats,
        "summary_ru": summary[:480],
        "school_canon": "rave_mandala_gate41_aquarius_2",
    }

"""House rulers + soft dispositor chains (canon §5.3 `house_rulers_chains`).

School freeze v0:
- Whole-sign houses from tropical ASC (requires birth time+place).
- Traditional domicile rulers (no exaltation/triplicity almuten).
- Dispositor chains use soft mean-longitude natal signs (Sun…Pluto).
"""

from __future__ import annotations

from datetime import date, time
from typing import Any

from todayflow_backend.services.day_sources.vedic_personal import compute_sidereal_lagna

_SIGN_RU = [
    "Овен",
    "Телец",
    "Близнецы",
    "Рак",
    "Лев",
    "Дева",
    "Весы",
    "Скорпион",
    "Стрелец",
    "Козерог",
    "Водолей",
    "Рыбы",
]

# Traditional domicile rulers (tropical).
_SIGN_RULERS: list[tuple[str, str]] = [
    ("Mars", "Марс"),
    ("Venus", "Венера"),
    ("Mercury", "Меркурий"),
    ("Moon", "Луна"),
    ("Sun", "Солнце"),
    ("Mercury", "Меркурий"),
    ("Venus", "Венера"),
    ("Mars", "Марс"),
    ("Jupiter", "Юпитер"),
    ("Saturn", "Сатурн"),
    ("Saturn", "Сатурн"),
    ("Jupiter", "Юпитер"),
]

_HOUSE_THEME_RU: dict[int, str] = {
    1: "тело, самопрезентация",
    2: "ресурсы, речь",
    3: "связь, малые шаги",
    4: "дом, корни",
    5: "творчество, радость",
    6: "ритм дел, служебное",
    7: "другой, договор",
    8: "глубина, общее",
    9: "смысл, путь",
    10: "дело, видимость",
    11: "круг, цели",
    12: "пауза, невидимое",
}

_PLANET_RU = {
    "Sun": "Солнце",
    "Moon": "Луна",
    "Mercury": "Меркурий",
    "Venus": "Венера",
    "Mars": "Марс",
    "Jupiter": "Юпитер",
    "Saturn": "Сатурн",
}


def _sign_index(lon: float) -> int:
    return int(float(lon) % 360.0 // 30.0) % 12


def _whole_sign_house(asc_sign: int, body_sign: int) -> int:
    return ((body_sign - asc_sign) % 12) + 1


def _known_natal_signs(birth_date: date) -> dict[str, int]:
    """Natal signs from soft mean longitudes (Sun…Pluto)."""
    from todayflow_backend.services.day_sources.classical_longitudes import (
        classical_bodies,
        classical_longitude,
    )

    return {name: _sign_index(classical_longitude(name, birth_date)) for name in classical_bodies()}


def build_house_rulers(
    asc_sign: int,
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for house in range(1, 13):
        sign_i = (asc_sign + house - 1) % 12
        lord, lord_ru = _SIGN_RULERS[sign_i]
        out.append(
            {
                "house": house,
                "sign_index": sign_i,
                "sign_ru": _SIGN_RU[sign_i],
                "lord": lord,
                "lord_ru": lord_ru,
                "theme_ru": _HOUSE_THEME_RU.get(house, ""),
            }
        )
    return out


def dispositor_chain(
    start_planet: str,
    natal_signs: dict[str, int],
    *,
    max_steps: int = 6,
) -> dict[str, Any]:
    """Follow domicile dispositors while natal sign of the lord is known."""
    steps: list[dict[str, Any]] = []
    seen: set[str] = set()
    planet = start_planet
    truncated: str | None = None
    final = False

    for _ in range(max_steps):
        if planet in seen:
            truncated = "cycle"
            final = True
            break
        seen.add(planet)
        sign_i = natal_signs.get(planet)
        if sign_i is None:
            truncated = "missing_planet_longitude"
            steps.append(
                {
                    "planet": planet,
                    "planet_ru": _PLANET_RU.get(planet, planet),
                    "sign_ru": None,
                    "next_lord": None,
                }
            )
            break
        next_lord, next_ru = _SIGN_RULERS[sign_i]
        steps.append(
            {
                "planet": planet,
                "planet_ru": _PLANET_RU.get(planet, planet),
                "sign_index": sign_i,
                "sign_ru": _SIGN_RU[sign_i],
                "next_lord": next_lord,
                "next_lord_ru": next_ru,
            }
        )
        if next_lord == planet:
            # Domicile / final dispositor (planet in own sign).
            final = True
            truncated = None
            break
        planet = next_lord

    label = " → ".join(
        f"{s['planet_ru']}"
        + (f" ({s['sign_ru']})" if s.get("sign_ru") else "")
        for s in steps
    )
    return {
        "start": start_planet,
        "steps": steps,
        "label_ru": label,
        "final_dispositor": final and truncated is None,
        "truncated": truncated,
    }


def build_house_rulers_chains(
    birth_date: date,
    *,
    birth_time: time,
    birth_lat: float,
    birth_lon: float,
    timezone_name: str | None = None,
    focus_house: int | None = None,
) -> dict[str, Any]:
    asc = compute_sidereal_lagna(
        birth_date,
        birth_time,
        birth_lat=float(birth_lat),
        birth_lon=float(birth_lon),
        timezone_name=timezone_name,
    )
    asc_sign = _sign_index(float(asc["tropical_lon"]))
    rulers = build_house_rulers(asc_sign)
    natal_signs = _known_natal_signs(birth_date)

    luminaries = {
        name: {
            "sign_index": si,
            "sign_ru": _SIGN_RU[si],
            "whole_sign_house": _whole_sign_house(asc_sign, si),
        }
        for name, si in natal_signs.items()
    }

    # Chains: ASC lord, 10th lord, luminaries, optional focus house lord.
    chain_seeds: list[str] = []
    asc_lord = rulers[0]["lord"]
    tenth_lord = rulers[9]["lord"]
    for p in (asc_lord, tenth_lord, "Sun", "Moon"):
        if p not in chain_seeds:
            chain_seeds.append(p)
    if focus_house is not None and 1 <= int(focus_house) <= 12:
        fl = rulers[int(focus_house) - 1]["lord"]
        if fl not in chain_seeds:
            chain_seeds.append(fl)

    chains = [dispositor_chain(p, natal_signs) for p in chain_seeds]

    focus = None
    if focus_house is not None and 1 <= int(focus_house) <= 12:
        row = rulers[int(focus_house) - 1]
        focus = {
            **row,
            "chain": dispositor_chain(row["lord"], natal_signs),
        }

    summary = (
        f"Управители домов (whole-sign от ASC {_SIGN_RU[asc_sign]}): "
        f"1-й — {rulers[0]['lord_ru']} ({rulers[0]['sign_ru']}), "
        f"10-й — {rulers[9]['lord_ru']} ({rulers[9]['sign_ru']})."
    )
    if focus:
        summary += (
            f" Фокус {focus['house']}-го: {focus['lord_ru']} "
            f"({focus['chain']['label_ru']})."
        )

    beat = {
        "id": "house-rulers-asc-tenth",
        "kind": "house_rulers_chains",
        "title": f"Управители · ASC {rulers[0]['lord_ru']} / MC-дом {rulers[9]['lord_ru']}",
        "story_ru": summary,
        "evidence_ref": "personal_astrology.house_rulers_chains",
    }

    return {
        "capability_id": "house_rulers_chains",
        "school_canon": "whole_sign_domicile_rulers_v0",
        "depth": "asc_whole_sign_full_planet_soft",
        "ascendant": {
            "tropical_lon": asc["tropical_lon"],
            "sign_index": asc_sign,
            "sign_ru": _SIGN_RU[asc_sign],
        },
        "houses": rulers,
        "luminaries": luminaries,
        "natal_signs": {
            name: {"sign_index": si, "sign_ru": _SIGN_RU[si]}
            for name, si in natal_signs.items()
        },
        "chains": chains,
        "focus": focus,
        "limitation_ru": (
            "Цепочки диспозиторов через soft mean-longitude Sun…Pluto. "
            "Swiss-точные натальные позиции — later."
        ),
        "beats": [beat],
        "summary_ru": summary[:420],
    }

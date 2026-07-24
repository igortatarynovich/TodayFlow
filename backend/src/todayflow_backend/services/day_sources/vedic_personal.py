"""Vedic personal layer — Chandra gochara + Vimshottari dasha (canon §5.6).

Natal reference: sidereal Moon from birth_date (Lahiri). Lagna gochara stays later.
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from todayflow_backend.services.day_sources.panchanga import (
    compute_panchanga_core,
    lahiri_ayanamsha,
    to_sidereal,
    tropical_moon_longitude,
    tropical_sun_longitude,
)

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

_DASHA_ORDER: tuple[str, ...] = (
    "ketu",
    "venus",
    "sun",
    "moon",
    "mars",
    "rahu",
    "jupiter",
    "saturn",
    "mercury",
)
_DASHA_YEARS: dict[str, int] = {
    "ketu": 7,
    "venus": 20,
    "sun": 6,
    "moon": 10,
    "mars": 7,
    "rahu": 18,
    "jupiter": 16,
    "saturn": 19,
    "mercury": 17,
}
_DASHA_RU: dict[str, str] = {
    "ketu": "Кету",
    "venus": "Венера",
    "sun": "Солнце",
    "moon": "Луна",
    "mars": "Марс",
    "rahu": "Раху",
    "jupiter": "Юпитер",
    "saturn": "Сатурн",
    "mercury": "Меркурий",
}

# Ashwini→Ketu, Bharani→Venus, … cycles through 9 lords.
_NAK_LORD: tuple[str, ...] = tuple(_DASHA_ORDER[i % 9] for i in range(27))

_DAYS_PER_YEAR = 365.2425

# Soft house readings from Chandra Lagna (gochara lite).
_MOON_HOUSE_RU: dict[int, str] = {
    1: "Луна проходит по вашему знаку — тема самочувствия и настроения на первом плане.",
    2: "Луна во 2-м от натальной — речь, ресурсы и ближайший круг.",
    3: "Луна в 3-м — короткие шаги, связь с близкими, смелость маленьких действий.",
    4: "Луна в 4-м — дом, корни, потребность в опоре.",
    5: "Луна в 5-м — творчество, дети, радость выбора.",
    6: "Луна в 6-м — дела, здоровье-ритм, мелкие трения.",
    7: "Луна в 7-м — партнёрство и зеркало другого человека.",
    8: "Луна в 8-м — глубина, чуткость к переменам, меньше суеты.",
    9: "Луна в 9-м — смысл, учёба, расширение горизонта.",
    10: "Луна в 10-м — видимость, дело, ответственность.",
    11: "Луна в 11-м — круг, цели, поддержка извне.",
    12: "Луна в 12-м — пауза, уединение, отпускание лишнего.",
}

_SUN_HOUSE_SOFT: dict[int, str] = {
    1: "Солнце по Chandra Lagna в 1-м — акцент на самопрезентации.",
    5: "Солнце в 5-м от Луны — ярче творческий и игровой тон.",
    9: "Солнце в 9-м — тема направления и смысла.",
    10: "Солнце в 10-м — день сильнее про дело и видимость.",
}


def _lon_to_sign_index(lon: float) -> int:
    return int(float(lon) % 360.0 // 30.0) % 12


def _house_from(natal_sign: int, transit_sign: int) -> int:
    return ((int(transit_sign) - int(natal_sign)) % 12) + 1


def natal_moon_ref(birth_date: date) -> dict[str, Any]:
    core = compute_panchanga_core(birth_date)
    moon_s = float(core["moon_sidereal_lon"])
    sign_i = _lon_to_sign_index(moon_s)
    nak = core["nakshatra"]
    return {
        "date": birth_date.isoformat(),
        "sidereal_lon": moon_s,
        "sign_index": sign_i,
        "sign_ru": _SIGN_RU[sign_i],
        "nakshatra": nak,
        "lord": _NAK_LORD[int(nak["index"])],
        "lord_ru": _DASHA_RU[_NAK_LORD[int(nak["index"])]],
        "ayanamsha": core["ayanamsha"],
    }


def _sidereal_body(d: date, body: str) -> float:
    aya = lahiri_ayanamsha(d)
    if body == "moon":
        trop = tropical_moon_longitude(d)
    else:
        trop = tropical_sun_longitude(d)
    return to_sidereal(trop, aya)


def build_gochara(
    target_date: date,
    natal: dict[str, Any],
) -> dict[str, Any]:
    natal_sign = int(natal["sign_index"])
    moon_lon = _sidereal_body(target_date, "moon")
    sun_lon = _sidereal_body(target_date, "sun")
    moon_sign = _lon_to_sign_index(moon_lon)
    sun_sign = _lon_to_sign_index(sun_lon)
    moon_house = _house_from(natal_sign, moon_sign)
    sun_house = _house_from(natal_sign, sun_sign)
    day_nak = compute_panchanga_core(target_date)["nakshatra"]

    beats: list[dict[str, Any]] = [
        {
            "id": f"gochara-moon-h{moon_house}",
            "kind": "moon_gochara",
            "title": f"Луна в {moon_house}-м от натальной",
            "story_ru": _MOON_HOUSE_RU.get(
                moon_house, f"Луна в {moon_house}-м доме от натальной Луны."
            ),
            "house": moon_house,
            "evidence_ref": "vedic_personal.gochara",
        }
    ]
    sun_story = _SUN_HOUSE_SOFT.get(sun_house)
    if sun_story:
        beats.append(
            {
                "id": f"gochara-sun-h{sun_house}",
                "kind": "sun_gochara",
                "title": f"Солнце в {sun_house}-м от Луны",
                "story_ru": sun_story,
                "house": sun_house,
                "evidence_ref": "vedic_personal.gochara",
            }
        )

    summary = (
        f"Gochara (Chandra Lagna): транзитная Луна в {_SIGN_RU[moon_sign]} "
        f"({moon_house}-й дом), накшатра дня {day_nak['name_ru']}."
    )
    return {
        "reference": "chandra_lagna",
        "natal_moon_sign_ru": natal["sign_ru"],
        "transit_moon": {
            "sign_ru": _SIGN_RU[moon_sign],
            "house_from_natal_moon": moon_house,
            "sidereal_lon": round(moon_lon, 4),
            "nakshatra": day_nak,
        },
        "transit_sun": {
            "sign_ru": _SIGN_RU[sun_sign],
            "house_from_natal_moon": sun_house,
            "sidereal_lon": round(sun_lon, 4),
        },
        "beats": beats,
        "summary_ru": summary,
    }


def _add_years(d: date, years: float) -> date:
    return d + timedelta(days=years * _DAYS_PER_YEAR)


def vimshottari_at(
    birth_date: date,
    target_date: date,
    natal: dict[str, Any],
) -> dict[str, Any]:
    nak_index = int(natal["nakshatra"]["index"])
    lord0 = _NAK_LORD[nak_index]
    nak_span = 360.0 / 27.0
    pos_in = float(natal["sidereal_lon"]) % nak_span
    frac_left = max(0.0, min(1.0, 1.0 - (pos_in / nak_span)))
    balance_years = frac_left * float(_DASHA_YEARS[lord0])

    # Build mahadasha timeline from birth.
    cursor = birth_date
    order_start = _DASHA_ORDER.index(lord0)
    timeline: list[dict[str, Any]] = []
    # First (balance) MD
    end0 = _add_years(cursor, balance_years)
    timeline.append(
        {
            "lord": lord0,
            "lord_ru": _DASHA_RU[lord0],
            "years": round(balance_years, 4),
            "start": cursor.isoformat(),
            "end": end0.isoformat(),
            "is_balance": True,
        }
    )
    cursor = end0
    # Full cycles until past target (+ buffer)
    i = 1
    guard = 0
    while cursor <= target_date and guard < 40:
        lord = _DASHA_ORDER[(order_start + i) % 9]
        yrs = float(_DASHA_YEARS[lord])
        end = _add_years(cursor, yrs)
        timeline.append(
            {
                "lord": lord,
                "lord_ru": _DASHA_RU[lord],
                "years": yrs,
                "start": cursor.isoformat(),
                "end": end.isoformat(),
                "is_balance": False,
            }
        )
        cursor = end
        i += 1
        guard += 1

    current = timeline[-1]
    for row in timeline:
        start = date.fromisoformat(row["start"])
        end = date.fromisoformat(row["end"])
        if start <= target_date < end or (target_date == end and row is timeline[-1]):
            current = row
            break
        if start <= target_date <= end:
            current = row
            break

    # Antardasha within current MD: same 9-lord sequence starting from MD lord.
    md_lord = current["lord"]
    md_start = date.fromisoformat(current["start"])
    md_end = date.fromisoformat(current["end"])
    md_days = max((md_end - md_start).days, 1)
    md_years = float(current["years"])
    ad_start = md_start
    antardasha = None
    ad_order_i = _DASHA_ORDER.index(md_lord)
    for j in range(9):
        ad_lord = _DASHA_ORDER[(ad_order_i + j) % 9]
        ad_years = md_years * (_DASHA_YEARS[ad_lord] / 120.0)
        ad_end = _add_years(ad_start, ad_years)
        if ad_start <= target_date < ad_end or (j == 8 and target_date <= ad_end):
            antardasha = {
                "lord": ad_lord,
                "lord_ru": _DASHA_RU[ad_lord],
                "years": round(ad_years, 4),
                "start": ad_start.isoformat(),
                "end": ad_end.isoformat(),
            }
            break
        ad_start = ad_end

    progress = min(
        1.0,
        max(0.0, (target_date - md_start).days / float(md_days)),
    )

    summary = (
        f"Vimshottari: махадаша {_DASHA_RU[md_lord]}"
        + (
            f" / антардаша {_DASHA_RU[antardasha['lord']]}"
            if antardasha
            else ""
        )
        + f" (баланс при рождении {balance_years:.2f} лет {_DASHA_RU[lord0]})."
    )

    return {
        "system": "vimshottari",
        "birth_nakshatra": natal["nakshatra"],
        "birth_lord": lord0,
        "birth_lord_ru": _DASHA_RU[lord0],
        "balance_years": round(balance_years, 4),
        "mahadasha": {
            "lord": md_lord,
            "lord_ru": _DASHA_RU[md_lord],
            "start": current["start"],
            "end": current["end"],
            "years": current["years"],
            "progress": round(progress, 4),
        },
        "antardasha": antardasha,
        "summary_ru": summary,
        "beats": [
            {
                "id": f"dasha-md-{md_lord}",
                "kind": "mahadasha",
                "title": f"Махадаша {_DASHA_RU[md_lord]}",
                "story_ru": summary,
                "evidence_ref": "vedic_personal.dasha",
            }
        ],
    }


def build_vedic_personal_payload(
    target_date: date,
    birth_date: date,
    *,
    has_birth_time: bool = False,
    has_birth_place: bool = False,
) -> dict[str, Any]:
    natal = natal_moon_ref(birth_date)
    gochara = build_gochara(target_date, natal)
    dasha = vimshottari_at(birth_date, target_date, natal)

    caps = ["gochara", "dasha"]
    depth = "chandra_lagna"
    if has_birth_time and has_birth_place:
        depth = "chandra_lagna_time_known"  # Lagna gochara still deferred

    beats = list(gochara.get("beats") or [])[:2]
    beats.extend(list(dasha.get("beats") or [])[:1])

    summary = f"{gochara['summary_ru']} {dasha['summary_ru']}"

    return {
        "capability_ids": caps,
        "depth": depth,
        "natal_moon": natal,
        "gochara": gochara,
        "dasha": dasha,
        "beats": beats,
        "summary_ru": summary[:480],
        "school_canon": "lahiri_vimshottari_v0",
        "lagna_gochara": "planned",
        "birth_date": birth_date.isoformat(),
        "target_date": target_date.isoformat(),
    }

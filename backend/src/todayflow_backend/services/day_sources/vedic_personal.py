"""Vedic personal layer — Chandra/Lagna gochara + Vimshottari dasha (canon §5.6).

Natal Moon from birth_date (Lahiri). Sidereal Lagna when birth time+place present.
"""

from __future__ import annotations

import math
from datetime import date, datetime, time, timedelta, timezone as dt_timezone
from typing import Any

from todayflow_backend.services.day_sources.panchanga import (
    compute_panchanga_core,
    lahiri_ayanamsha,
    to_sidereal,
    tropical_moon_longitude,
    tropical_sun_longitude,
)

try:
    from zoneinfo import ZoneInfo
except ImportError:  # pragma: no cover
    ZoneInfo = None  # type: ignore[misc, assignment]

_OBLIQUITY = 23.4392911

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

_LAGNA_MOON_HOUSE_RU: dict[int, str] = {
    1: "Луна в Lagna — день сильнее про тело, настроение и «как меня видят».",
    4: "Луна в 4-м от Lagna — дом и внутренний покой важнее внешнего шума.",
    7: "Луна в 7-м от Lagna — зеркало отношений и переговоров.",
    10: "Луна в 10-м от Lagna — видимость и деловой тон дня.",
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


def _julian_day_utc(dt: datetime) -> float:
    """Julian Day for a timezone-aware UTC datetime."""
    y, m = dt.year, dt.month
    if m <= 2:
        y -= 1
        m += 12
    a = y // 100
    b = 2 - a + a // 4
    day = dt.day + (dt.hour + dt.minute / 60.0 + dt.second / 3600.0) / 24.0
    return int(365.25 * (y + 4716)) + int(30.6001 * (m + 1)) + day + b - 1524.5


def _gmst_degrees(jd: float) -> float:
    t = (jd - 2451545.0) / 36525.0
    gmst = (
        280.46061837
        + 360.98564736629 * (jd - 2451545.0)
        + 0.000387933 * t * t
        - t * t * t / 38710000.0
    )
    return gmst % 360.0


def _ascendant_tropical(lat: float, lst_deg: float) -> float:
    """Tropical ecliptic longitude of Ascendant (degrees)."""
    ramc = math.radians(lst_deg % 360.0)
    phi = math.radians(lat)
    eps = math.radians(_OBLIQUITY)
    y = -math.cos(ramc)
    x = math.sin(ramc) * math.cos(eps) + math.tan(phi) * math.sin(eps)
    return math.degrees(math.atan2(y, x)) % 360.0


def birth_instant_utc(
    birth_date: date,
    birth_time: time,
    *,
    birth_lon: float,
    timezone_name: str | None = None,
) -> datetime:
    if timezone_name and ZoneInfo is not None:
        try:
            local = datetime.combine(birth_date, birth_time, tzinfo=ZoneInfo(timezone_name))
            return local.astimezone(dt_timezone.utc)
        except Exception:
            pass
    # Local mean time ≈ UTC + lon/15h
    naive = datetime.combine(birth_date, birth_time)
    return naive.replace(tzinfo=dt_timezone.utc) - timedelta(hours=float(birth_lon) / 15.0)


def compute_sidereal_lagna(
    birth_date: date,
    birth_time: time,
    *,
    birth_lat: float,
    birth_lon: float,
    timezone_name: str | None = None,
) -> dict[str, Any]:
    utc = birth_instant_utc(
        birth_date, birth_time, birth_lon=birth_lon, timezone_name=timezone_name
    )
    jd = _julian_day_utc(utc)
    lst = (_gmst_degrees(jd) + float(birth_lon)) % 360.0
    tropical = _ascendant_tropical(float(birth_lat), lst)
    aya = lahiri_ayanamsha(birth_date)
    sidereal = to_sidereal(tropical, aya)
    sign_i = _lon_to_sign_index(sidereal)
    return {
        "tropical_lon": round(tropical, 4),
        "sidereal_lon": round(sidereal, 4),
        "sign_index": sign_i,
        "sign_ru": _SIGN_RU[sign_i],
        "ayanamsha": {"id": "lahiri_v0", "degrees": round(aya, 4)},
        "lst_deg": round(lst, 4),
        "method": "closed_form_asc_v0",
        "utc": utc.isoformat(),
    }


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
    *,
    reference: str = "chandra_lagna",
    evidence_ref: str = "vedic_personal.gochara",
    moon_house_copy: dict[int, str] | None = None,
) -> dict[str, Any]:
    natal_sign = int(natal["sign_index"])
    moon_lon = _sidereal_body(target_date, "moon")
    sun_lon = _sidereal_body(target_date, "sun")
    moon_sign = _lon_to_sign_index(moon_lon)
    sun_sign = _lon_to_sign_index(sun_lon)
    moon_house = _house_from(natal_sign, moon_sign)
    sun_house = _house_from(natal_sign, sun_sign)
    day_nak = compute_panchanga_core(target_date)["nakshatra"]
    copy = moon_house_copy or _MOON_HOUSE_RU

    ref_label = "натальной Луны" if reference == "chandra_lagna" else "Lagna"
    beats: list[dict[str, Any]] = [
        {
            "id": f"{reference}-moon-h{moon_house}",
            "kind": "moon_gochara",
            "title": f"Луна в {moon_house}-м от {ref_label}",
            "story_ru": copy.get(
                moon_house, f"Луна в {moon_house}-м доме от {ref_label}."
            ),
            "house": moon_house,
            "evidence_ref": evidence_ref,
        }
    ]
    if reference == "chandra_lagna":
        sun_story = _SUN_HOUSE_SOFT.get(sun_house)
        if sun_story:
            beats.append(
                {
                    "id": f"gochara-sun-h{sun_house}",
                    "kind": "sun_gochara",
                    "title": f"Солнце в {sun_house}-м от Луны",
                    "story_ru": sun_story,
                    "house": sun_house,
                    "evidence_ref": evidence_ref,
                }
            )

    summary = (
        f"Gochara ({reference}): транзитная Луна в {_SIGN_RU[moon_sign]} "
        f"({moon_house}-й дом от {ref_label}), накшатра дня {day_nak['name_ru']}."
    )
    return {
        "reference": reference,
        "natal_sign_ru": natal.get("sign_ru"),
        "natal_moon_sign_ru": natal.get("sign_ru") if reference == "chandra_lagna" else None,
        "transit_moon": {
            "sign_ru": _SIGN_RU[moon_sign],
            "house_from_natal": moon_house,
            "house_from_natal_moon": moon_house if reference == "chandra_lagna" else None,
            "sidereal_lon": round(moon_lon, 4),
            "nakshatra": day_nak,
        },
        "transit_sun": {
            "sign_ru": _SIGN_RU[sun_sign],
            "house_from_natal": sun_house,
            "house_from_natal_moon": sun_house if reference == "chandra_lagna" else None,
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

    cursor = birth_date
    order_start = _DASHA_ORDER.index(lord0)
    timeline: list[dict[str, Any]] = []
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
    birth_time: time | None = None,
    birth_lat: float | None = None,
    birth_lon: float | None = None,
    timezone_name: str | None = None,
) -> dict[str, Any]:
    natal = natal_moon_ref(birth_date)
    gochara = build_gochara(target_date, natal)
    dasha = vimshottari_at(birth_date, target_date, natal)

    caps = ["gochara", "dasha"]
    depth = "chandra_lagna"
    lagna = None
    lagna_gochara = None

    has_time = birth_time is not None
    has_place = birth_lat is not None and birth_lon is not None
    if has_time and has_place:
        assert birth_time is not None and birth_lat is not None and birth_lon is not None
        lagna = compute_sidereal_lagna(
            birth_date,
            birth_time,
            birth_lat=float(birth_lat),
            birth_lon=float(birth_lon),
            timezone_name=timezone_name,
        )
        lagna_gochara = build_gochara(
            target_date,
            {"sign_index": lagna["sign_index"], "sign_ru": lagna["sign_ru"]},
            reference="lagna",
            evidence_ref="vedic_personal.lagna_gochara",
            moon_house_copy=_LAGNA_MOON_HOUSE_RU,
        )
        caps.append("lagna_gochara")
        depth = "lagna_gochara"

    beats = list(gochara.get("beats") or [])[:2]
    if lagna_gochara:
        beats.extend(list(lagna_gochara.get("beats") or [])[:1])
    beats.extend(list(dasha.get("beats") or [])[:1])

    summary = f"{gochara['summary_ru']} {dasha['summary_ru']}"
    if lagna_gochara:
        summary = f"{summary} {lagna_gochara['summary_ru']}"

    return {
        "capability_ids": caps,
        "depth": depth,
        "natal_moon": natal,
        "lagna": lagna,
        "gochara": gochara,
        "lagna_gochara": lagna_gochara,
        "dasha": dasha,
        "beats": beats,
        "summary_ru": summary[:520],
        "school_canon": "lahiri_vimshottari_v0",
        "birth_date": birth_date.isoformat(),
        "target_date": target_date.isoformat(),
    }

"""Electional / horary soft checklist v0 (canon §5.4).

School freeze: traditional elective checklist lite — not a full Lilly horary judgment.
Runs only on explicit request + datetime + place.
"""

from __future__ import annotations

from datetime import date, datetime, time
from typing import Any
from zoneinfo import ZoneInfo

from todayflow_backend.services.day_sources.adapters.planetary_hours import (
    build_planetary_hours_table,
)
from todayflow_backend.services.day_sources.panchanga import tropical_moon_longitude
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

# Tropical Moon dignities (traditional).
_MOON_DOMICILE = 3  # Cancer
_MOON_EXALT = 1  # Taurus
_MOON_DETRIMENT = 9  # Capricorn
_MOON_FALL = 7  # Scorpio

_WEEKDAY_RULER_RU = [
    ("Moon", "Луна"),
    ("Mars", "Марс"),
    ("Mercury", "Меркурий"),
    ("Jupiter", "Юпитер"),
    ("Venus", "Венера"),
    ("Saturn", "Сатурн"),
    ("Sun", "Солнце"),
]

# Soft mean lunar speed (°/day) for sub-day Moon estimate.
_MOON_DEG_PER_DAY = 13.176358


def _sign_index(lon: float) -> int:
    return int(float(lon) % 360.0 // 30.0) % 12


def _deg_in_sign(lon: float) -> float:
    return float(lon) % 30.0


def _check(
    *,
    check_id: str,
    status: str,
    title: str,
    story_ru: str,
) -> dict[str, Any]:
    return {
        "id": check_id,
        "status": status,  # pass | caution | fail | info
        "title": title,
        "story_ru": story_ru,
    }


def moon_dignity(sign_i: int) -> dict[str, Any]:
    if sign_i == _MOON_DOMICILE:
        return {"id": "domicile", "name_ru": "обитель", "tone": "pass"}
    if sign_i == _MOON_EXALT:
        return {"id": "exaltation", "name_ru": "экзальтация", "tone": "pass"}
    if sign_i == _MOON_DETRIMENT:
        return {"id": "detriment", "name_ru": "изгнание", "tone": "caution"}
    if sign_i == _MOON_FALL:
        return {"id": "fall", "name_ru": "падение", "tone": "fail"}
    return {"id": "peregrine", "name_ru": "без акцента", "tone": "info"}


def tropical_moon_longitude_at(d: date, t: time) -> dict[str, Any]:
    """Noon mean Moon drifted by soft mean speed to elected clock."""
    noon = tropical_moon_longitude(d)
    hours_from_noon = (t.hour + t.minute / 60.0 + t.second / 3600.0) - 12.0
    lon = (noon + hours_from_noon * (_MOON_DEG_PER_DAY / 24.0)) % 360.0
    return {
        "tropical_lon": round(lon, 4),
        "method": "mean_noon_plus_soft_drift",
        "hours_from_noon": round(hours_from_noon, 4),
    }


def _parse_iso_dt(raw: str | None) -> datetime | None:
    if not raw or not isinstance(raw, str):
        return None
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return None


def _elected_local_dt(
    target_date: date,
    electional_time: time,
    *,
    timezone_name: str | None,
) -> datetime:
    tz = ZoneInfo(timezone_name) if timezone_name else ZoneInfo("UTC")
    return datetime(
        target_date.year,
        target_date.month,
        target_date.day,
        electional_time.hour,
        electional_time.minute,
        electional_time.second,
        tzinfo=tz,
    )


def planetary_hour_for_moment(
    target_date: date,
    electional_time: time,
    *,
    lat: float,
    lon: float,
    timezone_name: str | None,
) -> dict[str, Any] | None:
    try:
        table = build_planetary_hours_table(
            target_date=target_date,
            lat=lat,
            lon=lon,
            timezone_name=timezone_name,
        )
    except Exception:
        return None
    elected = _elected_local_dt(target_date, electional_time, timezone_name=timezone_name)
    for row in table.get("hours") or []:
        if not isinstance(row, dict):
            continue
        start = _parse_iso_dt(str(row.get("start_local") or ""))
        end = _parse_iso_dt(str(row.get("end_local") or ""))
        if start is None or end is None:
            continue
        if start.tzinfo is None:
            start = start.replace(tzinfo=elected.tzinfo)
        if end.tzinfo is None:
            end = end.replace(tzinfo=elected.tzinfo)
        if start <= elected < end:
            return {
                **row,
                "day_ruler_planet_ru": table.get("day_ruler_planet_ru"),
                "matched": True,
            }
    return {
        "matched": False,
        "day_ruler_planet_ru": table.get("day_ruler_planet_ru"),
        "hours_count": len(table.get("hours") or []),
    }


def nearest_timed_lunar_aspect(
    celestial_events: dict[str, Any] | None,
    *,
    elected: datetime,
) -> dict[str, Any] | None:
    ce = celestial_events if isinstance(celestial_events, dict) else {}
    rows = ce.get("timed_lunar_aspects")
    if not isinstance(rows, list) or not rows:
        return None
    best: dict[str, Any] | None = None
    best_delta: float | None = None
    for row in rows:
        if not isinstance(row, dict):
            continue
        exact = _parse_iso_dt(str(row.get("exact_time") or row.get("exact_time_utc") or ""))
        if exact is None:
            continue
        if exact.tzinfo is None:
            exact = exact.replace(tzinfo=elected.tzinfo)
        delta = abs((exact - elected).total_seconds())
        if best_delta is None or delta < best_delta:
            best_delta = delta
            best = {
                **row,
                "delta_minutes": round(delta / 60.0, 1),
                "within_3h": delta <= 3 * 3600,
            }
    return best


def build_electional_horary_payload(
    target_date: date,
    *,
    electional_time: time,
    lat: float,
    lon: float,
    timezone_name: str | None = None,
    question: str | None = None,
    celestial_events: dict[str, Any] | None = None,
) -> dict[str, Any]:
    mode = "horary" if (question or "").strip() else "electional"
    caps = ["elective_checklist"]
    if mode == "horary":
        caps.append("horary_radicality_soft")

    asc = compute_sidereal_lagna(
        target_date,
        electional_time,
        birth_lat=lat,
        birth_lon=lon,
        timezone_name=timezone_name,
    )
    asc_trop = float(asc["tropical_lon"])
    asc_sign = _sign_index(asc_trop)
    asc_deg = _deg_in_sign(asc_trop)

    moon_pack = tropical_moon_longitude_at(target_date, electional_time)
    moon_lon = float(moon_pack["tropical_lon"])
    moon_sign = _sign_index(moon_lon)
    moon_dig = moon_dignity(moon_sign)

    wd = target_date.weekday()
    day_planet, day_planet_ru = _WEEKDAY_RULER_RU[wd]

    checks: list[dict[str, Any]] = []

    if asc_deg < 3.0:
        checks.append(
            _check(
                check_id="asc_early",
                status="caution",
                title="ASC слишком ранний",
                story_ru="Асцендент в первых градусах знака — момент ещё «не собран» (soft).",
            )
        )
    elif asc_deg > 27.0:
        checks.append(
            _check(
                check_id="asc_late",
                status="caution",
                title="ASC слишком поздний",
                story_ru="Асцендент в последних градусах — вопрос/дело могут быть «уже решены» (soft).",
            )
        )
    else:
        checks.append(
            _check(
                check_id="asc_band",
                status="pass",
                title="ASC в рабочей зоне",
                story_ru=f"ASC {_SIGN_RU[asc_sign]} {asc_deg:.1f}° — рабочая середина знака.",
            )
        )

    dig_status = moon_dig["tone"] if moon_dig["tone"] != "info" else "pass"
    checks.append(
        _check(
            check_id="moon_dignity",
            status=dig_status if dig_status != "info" else "info",
            title=f"Луна — {moon_dig['name_ru']}",
            story_ru=(
                f"Луна ≈ {_SIGN_RU[moon_sign]} в выбранный час "
                f"({moon_dig['name_ru']}; soft drift от noon mean)."
            ),
        )
    )

    ce = celestial_events if isinstance(celestial_events, dict) else {}
    voc = ce.get("void_of_course") if isinstance(ce.get("void_of_course"), dict) else None
    if isinstance(voc, dict) and voc.get("status") == "ok":
        in_voc = bool(voc.get("in_void_of_course"))
        checks.append(
            _check(
                check_id="moon_voc",
                status="fail" if in_voc else "pass",
                title="Луна VOC" if in_voc else "Луна не VOC",
                story_ru=(
                    "Луна в void-of-course — традиционно осторожнее с новыми стартами."
                    if in_voc
                    else "Луна не в VOC по majors-only правилу дня."
                ),
            )
        )
    else:
        checks.append(
            _check(
                check_id="moon_voc",
                status="info",
                title="VOC недоступен",
                story_ru="Нет timed VOC для момента — чеклист не угадывает void-of-course.",
            )
        )

    checks.append(
        _check(
            check_id="weekday_ruler",
            status="info",
            title=f"Управитель дня — {day_planet_ru}",
            story_ru=f"День недели под {day_planet_ru}; учитывайте согласованность с целью.",
        )
    )

    ph = planetary_hour_for_moment(
        target_date,
        electional_time,
        lat=lat,
        lon=lon,
        timezone_name=timezone_name,
    )
    if isinstance(ph, dict) and ph.get("matched"):
        checks.append(
            _check(
                check_id="planetary_hour",
                status="info",
                title=f"Планетарный час — {ph.get('ruler_planet_ru')}",
                story_ru=(
                    f"Сейчас (soft) час {ph.get('ruler_planet_ru')} "
                    f"({str(ph.get('start_local') or '')[11:16]}–{str(ph.get('end_local') or '')[11:16]}), "
                    f"период {ph.get('period')}."
                ),
            )
        )
        caps.append("planetary_hour_at_moment")
    else:
        checks.append(
            _check(
                check_id="planetary_hour",
                status="info",
                title="Планетарный час недоступен",
                story_ru="Не удалось сопоставить unequal hour с выбранным временем (geo/sunrise).",
            )
        )

    elected_dt = _elected_local_dt(
        target_date, electional_time, timezone_name=timezone_name
    )
    near_asp = nearest_timed_lunar_aspect(ce, elected=elected_dt)
    if isinstance(near_asp, dict) and near_asp.get("within_3h"):
        title = str(near_asp.get("title") or near_asp.get("aspect") or "лунный аспект")
        checks.append(
            _check(
                check_id="lunar_aspect_near",
                status="caution",
                title=f"Рядом: {title}",
                story_ru=(
                    f"Ближайший timed-аспект Луны ≈ через/назад {near_asp.get('delta_minutes')} мин "
                    f"— учитывайте пик контакта (soft)."
                ),
            )
        )
        caps.append("timed_lunar_aspect_near")
    elif isinstance(near_asp, dict):
        checks.append(
            _check(
                check_id="lunar_aspect_near",
                status="info",
                title="Ближайший лунный аспект далеко",
                story_ru=(
                    f"Ближайший timed majors-аспект в ~{near_asp.get('delta_minutes')} мин от момента "
                    f"— вне 3-часового окна."
                ),
            )
        )

    if mode == "horary":
        q = (question or "").strip()
        checks.append(
            _check(
                check_id="horary_question",
                status="pass" if q else "fail",
                title="Вопрос хорара",
                story_ru=(
                    f"Вопрос зафиксирован: «{q[:160]}»."
                    if q
                    else "Для хорара нужен явный вопрос."
                ),
            )
        )
        caps_note = (
            "Хорар soft: ASC + Луна (час) + VOC + планетарный час; без полного суда."
        )
    else:
        caps_note = (
            "Электив soft: чеклист момента (ASC, Луна, VOC, час, аспект) — не полный эфемеридный суд."
        )

    fails = sum(1 for c in checks if c["status"] == "fail")
    cautions = sum(1 for c in checks if c["status"] == "caution")
    passes = sum(1 for c in checks if c["status"] == "pass")
    if fails:
        verdict = "avoid"
        verdict_ru = "Лучше не брать этот момент без сильной причины."
    elif cautions:
        verdict = "caution"
        verdict_ru = "Момент рабочий с оговорками — смотрите caution-пункты."
    else:
        verdict = "supportive"
        verdict_ru = "Мягкий сигнал: чеклист не видит жёстких стоп-факторов."

    summary = (
        f"{'Хорар' if mode == 'horary' else 'Электив'} {target_date.isoformat()} "
        f"{electional_time.isoformat(timespec='minutes')}: "
        f"ASC {_SIGN_RU[asc_sign]}, Луна {_SIGN_RU[moon_sign]} ({moon_dig['name_ru']}). "
        f"{verdict_ru}"
    )

    ordered = sorted(
        checks,
        key=lambda c: {"fail": 0, "caution": 1, "pass": 2, "info": 3}.get(str(c["status"]), 9),
    )
    beats = [
        {
            "id": f"electional.{c['id']}",
            "kind": "checklist",
            "title": c["title"],
            "story_ru": c["story_ru"],
            "status": c["status"],
            "evidence_ref": "electional_horary.checklist",
        }
        for c in ordered
        if c["status"] in {"fail", "caution", "pass"}
    ][:5]
    beats.insert(
        0,
        {
            "id": f"electional.verdict.{verdict}",
            "kind": "verdict",
            "title": f"Вердикт — {verdict_ru}",
            "story_ru": summary,
            "status": verdict,
            "evidence_ref": "electional_horary.verdict",
        },
    )

    return {
        "capability_ids": caps,
        "mode": mode,
        "school_canon": "traditional_elective_checklist_v0",
        "requested": True,
        "moment": {
            "date": target_date.isoformat(),
            "time": electional_time.isoformat(timespec="minutes"),
            "timezone": timezone_name,
            "lat": lat,
            "lon": lon,
        },
        "question": (question or "").strip() or None,
        "ascendant": {
            "tropical_lon": round(asc_trop, 4),
            "sign_ru": _SIGN_RU[asc_sign],
            "degree_in_sign": round(asc_deg, 4),
        },
        "moon": {
            "tropical_lon": round(moon_lon, 4),
            "sign_ru": _SIGN_RU[moon_sign],
            "dignity": moon_dig,
            "longitude_method": moon_pack.get("method"),
        },
        "weekday_ruler": {"planet": day_planet, "planet_ru": day_planet_ru},
        "planetary_hour": ph,
        "nearest_lunar_aspect": near_asp,
        "void_of_course": voc,
        "checklist": checks,
        "checklist_counts": {
            "pass": passes,
            "caution": cautions,
            "fail": fails,
            "info": sum(1 for c in checks if c["status"] == "info"),
        },
        "verdict": verdict,
        "verdict_ru": verdict_ru,
        "beats": beats,
        "summary_ru": summary[:420],
        "notes_ru": caps_note,
        "limitation_ru": (
            "Soft elective/horary checklist. Moon at hour uses mean noon + drift; "
            "ASC via lagna helper; planetary hours NOAA-approx. Not a full Lilly court."
        ),
    }

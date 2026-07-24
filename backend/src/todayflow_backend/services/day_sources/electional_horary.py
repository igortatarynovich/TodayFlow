"""Electional / horary soft checklist v0 (canon §5.4).

School freeze: traditional elective checklist lite — not a full Lilly horary judgment.
Runs only on explicit request + datetime + place.
"""

from __future__ import annotations

from datetime import date, time
from typing import Any

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

    moon_lon = tropical_moon_longitude(target_date)
    moon_sign = _sign_index(moon_lon)
    moon_dig = moon_dignity(moon_sign)

    wd = target_date.weekday()
    day_planet, day_planet_ru = _WEEKDAY_RULER_RU[wd]

    checks: list[dict[str, Any]] = []

    # ASC early/late in sign (horary radicality soft; also useful for elections).
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
                f"Луна в {_SIGN_RU[moon_sign]}: {moon_dig['name_ru']} "
                f"(традиционные достоинства)."
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
        caps_note = "Хорар soft: радикальность ASC + достоинства Луны + VOC; без полного суда."
    else:
        caps_note = "Электив soft: чеклист момента для выбора времени, не полный эфемеридный суд."

    fails = sum(1 for c in checks if c["status"] == "fail")
    cautions = sum(1 for c in checks if c["status"] == "caution")
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

    beats = [
        {
            "id": f"electional.{c['id']}",
            "kind": "checklist",
            "title": c["title"],
            "story_ru": c["story_ru"],
            "status": c["status"],
            "evidence_ref": "electional_horary.checklist",
        }
        for c in checks
        if c["status"] in {"fail", "caution", "pass"}
    ][:4]

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
        },
        "weekday_ruler": {"planet": day_planet, "planet_ru": day_planet_ru},
        "void_of_course": voc,
        "checklist": checks,
        "verdict": verdict,
        "verdict_ru": verdict_ru,
        "beats": beats,
        "summary_ru": summary[:420],
        "notes_ru": caps_note,
    }

"""Assemble day_events_pack_v1 from celestial payload + curated cycles + solar/calendar.

LLM and interpretation must choose 1–3 drivers from this pack — never invent sky facts.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from typing import Any

from todayflow_backend.data import astrology as astrology_ref
from todayflow_backend.services.day_events_ranker_v1 import rank_day_events

DAY_EVENTS_PACK_V1 = "day_events_pack_v1"

_PLANET_RU: dict[str, str] = {
    "Sun": "Солнце",
    "Moon": "Луна",
    "Mercury": "Меркурий",
    "Venus": "Венера",
    "Mars": "Марс",
    "Jupiter": "Юпитер",
    "Saturn": "Сатурн",
    "Uranus": "Уран",
    "Neptune": "Нептун",
    "Pluto": "Плутон",
}

_SIGN_RU: dict[str, str] = {
    "Aries": "Овен",
    "Taurus": "Телец",
    "Gemini": "Близнецы",
    "Cancer": "Рак",
    "Leo": "Лев",
    "Virgo": "Дева",
    "Libra": "Весы",
    "Scorpio": "Скорпион",
    "Sagittarius": "Стрелец",
    "Capricorn": "Козерог",
    "Aquarius": "Водолей",
    "Pisces": "Рыбы",
}

_ASPECT_RU: dict[str, str] = {
    "conjunction": "соединение",
    "square": "квадрат",
    "trine": "тригон",
    "opposition": "оппозиция",
    "sextile": "секстиль",
}

_LUNAR_ASPECT_STORY: dict[str, str] = {
    "conjunction": "Луна сливается с темой планеты — эмоции и событие звучат в одной тональности.",
    "opposition": "Луна напротив планеты — полярность: нужно удерживать два полюса, не выбирая «всё или ничего».",
    "square": "Луна в квадрате — трение и накал; легче сорваться на резкость, чем договорить.",
    "trine": "Луна в тригоне — поддержка без усилия; хороший день для мягкого движения вперёд.",
    "sextile": "Луна в секстиле — открывается окно для лёгкого шага, если не игнорировать сигнал.",
}

# Tropical season points (approx civil dates; ±2 days = in window).
_SEASONAL_POINTS: tuple[tuple[int, int, str, str], ...] = (
    (3, 20, "spring_equinox", "Весеннее равноденствие"),
    (6, 21, "summer_solstice", "Летнее солнцестояние"),
    (9, 22, "autumn_equinox", "Осеннее равноденствие"),
    (12, 21, "winter_solstice", "Зимнее солнцестояние"),
)


def _planet_ru(name: str) -> str:
    key = str(name or "").strip()
    return _PLANET_RU.get(key) or _PLANET_RU.get(key.title()) or key


def _sign_ru(name: str) -> str:
    key = str(name or "").strip()
    return _SIGN_RU.get(key) or _SIGN_RU.get(key.title()) or key


def _aspect_ru(name: str) -> str:
    key = str(name or "").strip().lower().replace(" ", "_")
    return _ASPECT_RU.get(key) or name


def _parse_iso_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        raw = str(value).strip().replace("Z", "+00:00")
        dt = datetime.fromisoformat(raw)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except ValueError:
        return None


def _within_days(event_day: date, target: date, window: int = 2) -> bool:
    return abs((event_day - target).days) <= window


def _event(
    *,
    eid: str,
    kind: str,
    title_ru: str,
    fact_ru: str = "",
    when: str | None = None,
    priority_hint: str | None = None,
    orb_delta: float | None = None,
    tension_level: str | None = None,
    strength_label: str | None = None,
    meta: dict[str, Any] | None = None,
    body: str | None = None,
    sign: str | None = None,
    aspect: str | None = None,
    target_body: str | None = None,
    fact_key: str | None = None,
    source: str = "celestial_events_builder",
) -> dict[str, Any]:
    """Structured evidence row. fact_ru is a projection — formatter may rebuild it."""
    row: dict[str, Any] = {
        "id": eid,
        "kind": kind,
        "title_ru": title_ru,
        "source": source,
    }
    if body:
        row["body"] = body
    if sign:
        row["sign"] = sign
    if aspect:
        row["aspect"] = aspect
    if target_body:
        row["target_body"] = target_body
    if fact_key:
        row["fact_key"] = fact_key
    args: dict[str, Any] = {}
    if body:
        args["body"] = body
    if sign:
        args["sign"] = sign
    if aspect:
        args["aspect"] = aspect
    if target_body:
        args["target_body"] = target_body
    if args:
        row["fact_args"] = args
    if when:
        row["when"] = when
        row["exact_at"] = when
    if priority_hint:
        row["priority_hint"] = priority_hint
    if orb_delta is not None:
        row["orb_delta"] = orb_delta
        row["orb"] = orb_delta
    if tension_level:
        row["tension_level"] = tension_level
    if strength_label:
        row["strength_label"] = strength_label
    if meta:
        row["meta"] = meta
    if fact_ru:
        row["fact_ru"] = fact_ru  # temporary projection; formatter overwrites
    return row


def _events_from_ingresses(ingresses: list[Any], target: date) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in ingresses:
        if not isinstance(row, dict):
            continue
        planet = str(row.get("planet") or "")
        sign = str(row.get("sign") or "")
        if not planet or not sign:
            continue
        try:
            ing_day = date.fromisoformat(str(row.get("ingress_date") or target)[:10])
        except ValueError:
            ing_day = target
        if not _within_days(ing_day, target, 2):
            continue
        is_moon = "moon" in planet.lower() or "лун" in str(row.get("planet_ru") or "").lower()
        when = str(row.get("exact_time") or row.get("ingress_date") or "") or None
        planet_ru = str(row.get("planet_ru") or _planet_ru(planet))
        sign_ru = str(row.get("sign_ru") or _sign_ru(sign))
        if is_moon:
            time_bit = ""
            if row.get("exact_time"):
                try:
                    time_bit = f" около {str(row['exact_time'])[11:16]}"
                except Exception:
                    time_bit = ""
            fact = f"Луна переходит в {sign_ru}{time_bit} — меняется эмоциональный тон дня."
            out.append(
                _event(
                    eid=f"ingress-moon-{sign.lower()}-{ing_day.isoformat()}",
                    kind="moon_ingress",
                    title_ru=f"Луна → {sign_ru}",
                    fact_ru=fact,
                    when=when,
                    priority_hint="primary",
                    body="Moon",
                    sign=sign,
                    fact_key="moon_ingress",
                    meta={"planet": planet, "sign": sign},
                )
            )
        else:
            fact = f"{planet_ru} входит в {sign_ru} ({ing_day.isoformat()}) — смещается акцент тем этой планеты."
            out.append(
                _event(
                    eid=f"ingress-{planet.lower()}-{sign.lower()}-{ing_day.isoformat()}",
                    kind="planet_ingress",
                    title_ru=f"{planet_ru} → {sign_ru}",
                    fact_ru=fact,
                    when=when or ing_day.isoformat(),
                    body=planet,
                    sign=sign,
                    fact_key="planet_ingress",
                    meta={"planet": planet, "sign": sign},
                )
            )
    return out


def _events_from_sky_aspects(aspects: list[Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for i, row in enumerate(aspects[:8]):
        if not isinstance(row, dict):
            continue
        title = str(row.get("title_ru") or row.get("title") or "").strip()
        story = str(row.get("story_ru") or "").strip()
        if not title and not story:
            continue
        eid = str(row.get("id") or f"sky-aspect-{i}")
        fact = story or title
        planet_a = str(row.get("planet_a") or "").strip() or None
        planet_b = str(row.get("planet_b") or "").strip() or None
        aspect = str(row.get("aspect") or "").strip() or None
        hint = str(row.get("priority_hint") or "").strip() or None
        meta = {
            "aspect": aspect,
            "planet_a": planet_a,
            "planet_b": planet_b,
            "thesis_hint": row.get("thesis_hint"),
            "domain_weights": row.get("domain_weights"),
            "daily_score": row.get("daily_score"),
        }
        out.append(
            _event(
                eid=eid,
                kind="sky_aspect",
                title_ru=title or "Аспект дня",
                fact_ru=fact[:240],
                orb_delta=row.get("orb_delta"),
                tension_level=str(row.get("tension_level") or "") or None,
                strength_label=str(row.get("strength") or "") or None,
                priority_hint=hint,
                body=planet_a,
                target_body=planet_b,
                aspect=aspect,
                fact_key="sky_aspect",
                when=str(row.get("exact_time") or "") or None,
                meta={k: v for k, v in meta.items() if v is not None},
            )
        )
    return out


def _events_from_timed_lunar(aspects: list[Any], target: date) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for i, row in enumerate(aspects[:8]):
        if not isinstance(row, dict):
            continue
        aspect = str(row.get("aspect") or "").strip().lower()
        body = str(row.get("planet") or row.get("body") or row.get("target") or "").strip()
        title = str(row.get("title") or "").strip()
        when = str(row.get("exact_time") or "") or None
        if when:
            try:
                when_day = date.fromisoformat(when[:10])
                if when_day != target:
                    continue
            except ValueError:
                pass
        body_ru = _planet_ru(body.title()) if body else ""
        asp_ru = _aspect_ru(aspect) if aspect else ""
        if not title:
            title = f"Луна — {asp_ru} — {body_ru}".strip(" —")
        story = str(row.get("story_ru") or "").strip()
        if not story:
            base = _LUNAR_ASPECT_STORY.get(aspect, "Лунный аспект задаёт ритм эмоций на часы.")
            time_bit = f" Exact ≈ {when[11:16]}." if when and len(when) >= 16 else ""
            # Keep RU for user-facing
            time_bit_ru = f" Точно около {when[11:16]}." if when and len(when) >= 16 else ""
            story = f"{title}: {base}{time_bit_ru}"
        out.append(
            _event(
                eid=str(row.get("id") or f"lunar-aspect-{aspect}-{body.lower()}-{i}"),
                kind="lunar_aspect",
                title_ru=title,
                fact_ru=story[:240],
                when=when,
                orb_delta=row.get("orb_delta"),
                tension_level="high" if aspect in {"square", "opposition"} else None,
                meta={"aspect": aspect, "planet": body},
            )
        )
    return out


def _events_from_retrogrades(retros: list[Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in retros[:4]:
        if not isinstance(row, dict):
            continue
        planet = str(row.get("planet") or "")
        if not planet:
            continue
        planet_ru = str(row.get("planet_ru") or _planet_ru(planet))
        story = str(row.get("story_ru") or f"{planet_ru} ретрограден.").strip()
        out.append(
            _event(
                eid=f"retro-{planet.lower()}",
                kind="retrograde",
                title_ru=f"{planet_ru} Rx",
                fact_ru=story[:240],
                priority_hint="ambient",
                meta={"planet": planet},
            )
        )
    return out


_SIGN_INDEX = {
    "Aries": 0,
    "Taurus": 1,
    "Gemini": 2,
    "Cancer": 3,
    "Leo": 4,
    "Virgo": 5,
    "Libra": 6,
    "Scorpio": 7,
    "Sagittarius": 8,
    "Capricorn": 9,
    "Aquarius": 10,
    "Pisces": 11,
}

# ~1 day of Moon motion. Catalog "new" farther than this is texture, not a plot turn.
_QUARTER_ELONGATION_DEG = 15.0


def _lon_from_sign_degree(row: dict[str, Any] | None) -> float | None:
    if not isinstance(row, dict):
        return None
    lon = row.get("longitude")
    if isinstance(lon, (int, float)):
        return float(lon) % 360.0
    sign = str(row.get("sign") or "").strip()
    deg = row.get("degree")
    idx = _SIGN_INDEX.get(sign)
    if idx is None or not isinstance(deg, (int, float)):
        return None
    return (idx * 30.0 + float(deg)) % 360.0


def _sun_moon_elongation_deg(
    *,
    moon_sign: dict[str, Any] | None,
    sun_sign: dict[str, Any] | None,
    sky_positions: list[Any] | None,
) -> float | None:
    """Swiss/noon elongation 0..180°. None if lights missing."""
    from todayflow_backend.services.sky_geometry_v1 import angular_separation

    sun_lon = moon_lon = None
    for row in sky_positions or []:
        if not isinstance(row, dict):
            continue
        body = str(row.get("body") or "").strip().lower()
        lon = row.get("longitude")
        if not isinstance(lon, (int, float)):
            continue
        if body == "sun":
            sun_lon = float(lon) % 360.0
        elif body == "moon":
            moon_lon = float(lon) % 360.0
    if sun_lon is None:
        sun_lon = _lon_from_sign_degree(sun_sign)
    if moon_lon is None:
        moon_lon = _lon_from_sign_degree(moon_sign)
    if sun_lon is None or moon_lon is None:
        return None
    return angular_separation(sun_lon, moon_lon)


def _near_lunar_quarter(elongation_deg: float | None) -> bool | None:
    """True = new/quarter/full geometry today. None = unknown."""
    if elongation_deg is None:
        return None
    sep = float(elongation_deg)
    dist = min(sep, abs(sep - 90.0), abs(sep - 180.0))
    return dist <= _QUARTER_ELONGATION_DEG


def _events_from_phase(
    lunar_phase: dict[str, Any] | None,
    moon_sign: dict[str, Any] | None,
    target: date,
    *,
    sun_sign: dict[str, Any] | None = None,
    sky_positions: list[Any] | None = None,
) -> list[dict[str, Any]]:
    if not isinstance(lunar_phase, dict) or not lunar_phase:
        return []
    name = str(lunar_phase.get("name") or "").strip()
    phase_id = str(lunar_phase.get("id") or "").strip()
    if not name and not phase_id:
        return []
    sign_ru = ""
    if isinstance(moon_sign, dict):
        sign_ru = str(moon_sign.get("sign_ru") or _sign_ru(str(moon_sign.get("sign") or ""))).strip()
    guidance = str(lunar_phase.get("guidance") or lunar_phase.get("themes") or "").strip()
    title = name or phase_id
    if sign_ru:
        fact = f"{title} Луны в знаке {sign_ru}"
        if guidance:
            fact = f"{fact}: {guidance}"
    else:
        fact = f"{title}" + (f": {guidance}" if guidance else "")
    # Catalog phase is texture. It competes for the plot only on a real quarter-turn
    # (Swiss Sun–Moon elongation), not because LunarService labelled the window "new".
    kind = "phase_change"
    next_phase = lunar_phase.get("next_phase") if isinstance(lunar_phase.get("next_phase"), dict) else {}
    in_days = next_phase.get("in_days")
    sep = _sun_moon_elongation_deg(
        moon_sign=moon_sign,
        sun_sign=sun_sign,
        sky_positions=sky_positions,
    )
    near_quarter = _near_lunar_quarter(sep)
    priority = "ambient"
    try:
        soon = in_days is not None and float(in_days) <= 1.0
    except (TypeError, ValueError):
        soon = False
    if near_quarter is True:
        priority = "primary"
    elif near_quarter is False:
        priority = "ambient"
    elif soon:
        priority = "primary"
    return [
        _event(
            eid=f"phase-{phase_id or name}-{target.isoformat()}",
            kind=kind,
            title_ru=title if not sign_ru else f"{title} · {sign_ru}",
            fact_ru=fact[:240],
            when=target.isoformat(),
            priority_hint=priority,
            meta={
                "phase_id": phase_id,
                "moon_sign": sign_ru or None,
                "sun_moon_sep_deg": round(sep, 2) if sep is not None else None,
            },
        )
    ]


def _events_from_personal(transits: list[Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in transits[:3]:
        if not isinstance(row, dict):
            continue
        eid = str(row.get("id") or "").strip()
        title = str(row.get("title") or "").strip()
        story = str(row.get("story_ru") or "").strip()
        if not eid or not (title or story):
            continue
        out.append(
            _event(
                eid=eid,
                kind="personal_transit",
                title_ru=title or "Личный транзит",
                fact_ru=(story or title)[:240],
                strength_label=str(row.get("strength") or "") or None,
            )
        )
    return out


def _events_from_planetary_cycles(target: date, *, window_days: int = 2) -> list[dict[str, Any]]:
    """Pull curated stations, aspects, ingresses, and Rx window edges near target_date."""
    out: list[dict[str, Any]] = []
    try:
        entries = astrology_ref.planetary_cycles()
    except Exception:
        return out

    for entry in entries:
        if not isinstance(entry, dict):
            continue
        eid = str(entry.get("id") or "").strip()
        planet = str(entry.get("planet") or "").strip()
        event_type = str(entry.get("event_type") or "").strip().lower()
        if not eid:
            continue

        # Point events
        ts = _parse_iso_dt(entry.get("timestamp"))
        if ts is not None and _within_days(ts.date(), target, window_days):
            planet_ru = _planet_ru(planet)
            sign = str(entry.get("sign") or "").strip()
            sign_ru = _sign_ru(sign) if sign else ""
            aspect = str(entry.get("aspect") or "").strip()
            desc = str(entry.get("description") or "").strip()
            if event_type == "station":
                # Heuristic: ids / keywords mentioning direct → station_direct
                low_id = eid.lower()
                is_direct = "direct" in low_id or "прям" in desc.lower()
                kind = "station_direct" if is_direct else "station"
                title = f"{planet_ru} {'выходит из ретрограда' if is_direct else 'становится в станцию'}"
                if sign_ru:
                    title = f"{title} ({sign_ru})"
                fact = desc[:200] if desc else title
                out.append(
                    _event(
                        eid=f"cycle-{eid}",
                        kind=kind,
                        title_ru=title,
                        fact_ru=fact,
                        when=ts.isoformat(),
                        priority_hint="primary",
                        meta={"planet": planet, "sign": sign or None, "cycle_id": eid},
                    )
                )
            elif event_type == "ingress":
                title = f"{planet_ru} → {sign_ru}" if sign_ru else f"{planet_ru}: ингресс"
                fact = desc[:200] if desc else f"{planet_ru} переходит в {sign_ru}."
                out.append(
                    _event(
                        eid=f"cycle-{eid}",
                        kind="planet_ingress",
                        title_ru=title,
                        fact_ru=fact,
                        when=ts.isoformat(),
                        meta={"planet": planet, "sign": sign or None, "cycle_id": eid},
                    )
                )
            elif event_type == "aspect":
                title = f"{planet_ru} — {aspect}" if aspect else f"{planet_ru}: аспект"
                fact = desc[:200] if desc else title
                out.append(
                    _event(
                        eid=f"cycle-{eid}",
                        kind="cycle_aspect",
                        title_ru=title,
                        fact_ru=fact,
                        when=ts.isoformat(),
                        tension_level="high" if "square" in aspect.lower() or "oppos" in aspect.lower() else None,
                        meta={"planet": planet, "aspect": aspect or None, "cycle_id": eid},
                    )
                )
            continue

        # Window edges (Rx start / end ≈ station)
        start = _parse_iso_dt(entry.get("start_timestamp"))
        end = _parse_iso_dt(entry.get("end_timestamp"))
        if not start or not end:
            continue
        label = str(entry.get("window_label") or eid)
        planet_ru = _planet_ru(planet)
        if _within_days(start.date(), target, window_days):
            out.append(
                _event(
                    eid=f"cycle-{eid}-start",
                    kind="retrograde_edge",
                    title_ru=f"{planet_ru}: начало {label}",
                    fact_ru=f"{planet_ru} входит в ретроградное окно — темп тем планеты просит пересмотра, не рывка.",
                    when=start.isoformat(),
                    priority_hint="primary",
                    meta={"planet": planet, "edge": "start", "cycle_id": eid},
                )
            )
        if _within_days(end.date(), target, window_days):
            out.append(
                _event(
                    eid=f"cycle-{eid}-end",
                    kind="station_direct",
                    title_ru=f"{planet_ru}: выход из ретрограда",
                    fact_ru=f"{planet_ru} завершает ретроградное окно — зелёный свет для тем, которые висели в черновиках.",
                    when=end.isoformat(),
                    priority_hint="primary",
                    meta={"planet": planet, "edge": "end", "cycle_id": eid},
                )
            )
    return out


def _events_seasonal_calendar(target: date) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    year = target.year
    for month, day, sid, title_ru in _SEASONAL_POINTS:
        try:
            point = date(year, month, day)
        except ValueError:
            continue
        delta = abs((point - target).days)
        if delta > 3:
            continue
        proximity = "сегодня" if delta == 0 else f"через {delta} дн." if point > target else f"{delta} дн. назад"
        out.append(
            _event(
                eid=f"seasonal-{sid}-{year}",
                kind="seasonal",
                title_ru=title_ru,
                fact_ru=f"{title_ru} ({point.isoformat()}, {proximity}) — сезонный поворот солнечного года.",
                when=point.isoformat(),
                priority_hint="secondary" if delta <= 1 else "ambient",
                meta={"season_point": sid, "delta_days": delta},
            )
        )

    doy = target.timetuple().tm_yday
    out.append(
        _event(
            eid=f"calendar-doy-{target.isoformat()}",
            kind="calendar",
            title_ru=f"День года {doy}",
            fact_ru=f"Календарный день {target.isoformat()} — {doy}-й день года.",
            when=target.isoformat(),
            priority_hint="ambient",
            meta={"day_of_year": doy},
        )
    )
    return out


def _events_solar_daylight(
    target: date,
    *,
    lat: float | None,
    lon: float | None,
    timezone_name: str | None,
) -> list[dict[str, Any]]:
    if lat is None or lon is None:
        return []
    try:
        from todayflow_backend.services.day_sources.sun_rise_set import sun_rise_set_local

        sun = sun_rise_set_local(target, lat=float(lat), lon=float(lon), timezone_name=timezone_name)
    except Exception:
        return []
    rise = str(sun.get("sunrise_local") or "")
    set_ = str(sun.get("sunset_local") or "")
    minutes = sun.get("day_length_minutes")
    rise_hm = rise[11:16] if len(rise) >= 16 else rise
    set_hm = set_[11:16] if len(set_) >= 16 else set_
    fact = f"Восход {rise_hm}, закат {set_hm}"
    if minutes is not None:
        fact = f"{fact} — длина дня ≈ {int(minutes)} мин."
    return [
        _event(
            eid=f"solar-daylight-{target.isoformat()}",
            kind="solar_daylight",
            title_ru="Свет дня",
            fact_ru=fact,
            when=rise or target.isoformat(),
            priority_hint="ambient",
            meta={"day_length_minutes": minutes, "sunrise_local": rise, "sunset_local": set_},
        )
    ]


def collect_raw_day_events(
    celestial_events: dict[str, Any] | None,
    *,
    target_date: date,
    lat: float | None = None,
    lon: float | None = None,
    timezone_name: str | None = None,
) -> list[dict[str, Any]]:
    """Flatten celestial + cycles + solar/calendar into raw event rows (pre-rank)."""
    ce = celestial_events if isinstance(celestial_events, dict) else {}
    events: list[dict[str, Any]] = []
    events.extend(_events_from_ingresses(list(ce.get("ingresses") or []), target_date))
    events.extend(_events_from_sky_aspects(list(ce.get("sky_aspects") or [])))
    events.extend(_events_from_timed_lunar(list(ce.get("timed_lunar_aspects") or []), target_date))
    events.extend(_events_from_retrogrades(list(ce.get("retrogrades") or [])))
    events.extend(
        _events_from_phase(
            ce.get("lunar_phase") if isinstance(ce.get("lunar_phase"), dict) else None,
            ce.get("moon_sign") if isinstance(ce.get("moon_sign"), dict) else None,
            target_date,
            sun_sign=ce.get("sun_sign") if isinstance(ce.get("sun_sign"), dict) else None,
            sky_positions=list(ce.get("sky_positions") or []),
        )
    )
    events.extend(_events_from_personal(list(ce.get("personal_transits") or [])))
    events.extend(_events_from_planetary_cycles(target_date))
    events.extend(_events_seasonal_calendar(target_date))
    events.extend(_events_solar_daylight(target_date, lat=lat, lon=lon, timezone_name=timezone_name))

    # Deduplicate by id (first wins — prefer live sky over cycle duplicates).
    seen: set[str] = set()
    unique: list[dict[str, Any]] = []
    for ev in events:
        eid = str(ev.get("id") or "")
        if not eid or eid in seen:
            continue
        seen.add(eid)
        unique.append(ev)
    return unique


def build_day_events_pack_v1(
    celestial_events: dict[str, Any] | None,
    *,
    target_date: date,
    lat: float | None = None,
    lon: float | None = None,
    timezone_name: str | None = None,
) -> dict[str, Any]:
    """Build ranked day_events_pack_v1 (evidence only — nest under DayContext)."""
    from todayflow_backend.services.day_event_fact_formatter_v1 import project_fact_ru

    raw = collect_raw_day_events(
        celestial_events,
        target_date=target_date,
        lat=lat,
        lon=lon,
        timezone_name=timezone_name,
    )
    raw = project_fact_ru(raw, locale="ru")
    pack = rank_day_events(raw)
    limitations: list[str] = []
    kinds = {str(e.get("kind") or "") for e in pack.get("events") or []}
    if "perigee" not in kinds and "apogee" not in kinds:
        limitations.append("perigee_apogee_not_computed_v1")
    pack["limitations"] = limitations
    pack["target_date"] = target_date.isoformat()
    pack["role"] = "evidence"
    return pack


def slim_day_events_for_llm(pack: dict[str, Any] | None, *, max_ambient: int = 3) -> dict[str, Any]:
    """Compact pack for LLM prompts: drivers fully, ambient titles only."""
    if not isinstance(pack, dict):
        return {"contract_version": DAY_EVENTS_PACK_V1, "ranked_drivers": [], "events": []}
    by_id = {
        str(e.get("id")): e
        for e in (pack.get("events") or [])
        if isinstance(e, dict) and e.get("id")
    }
    drivers = []
    for eid in pack.get("ranked_drivers") or []:
        row = by_id.get(str(eid))
        if not row:
            continue
        drivers.append(
            {
                "id": row["id"],
                "kind": row.get("kind"),
                "title_ru": row.get("title_ru"),
                "fact_ru": row.get("fact_ru"),
                "when": row.get("when"),
                "strength": row.get("strength"),
            }
        )
    ambient = []
    for eid in (pack.get("ambient") or [])[:max_ambient]:
        row = by_id.get(str(eid))
        if not row:
            continue
        ambient.append({"id": row["id"], "kind": row.get("kind"), "title_ru": row.get("title_ru")})
    return {
        "contract_version": pack.get("contract_version") or DAY_EVENTS_PACK_V1,
        "ranked_drivers": list(pack.get("ranked_drivers") or []),
        "drivers": drivers,
        "ambient": ambient,
        "limitations": list(pack.get("limitations") or []),
    }

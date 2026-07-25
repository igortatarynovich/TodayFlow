"""Format structured celestial evidence into localized fact strings.

Evidence stores body/sign/kind; fact_ru is a projection — not SoT.
"""

from __future__ import annotations

from typing import Any

_PLANET_RU = {
    "sun": "Солнце",
    "moon": "Луна",
    "mercury": "Меркурий",
    "venus": "Венера",
    "mars": "Марс",
    "jupiter": "Юпитер",
    "saturn": "Сатурн",
    "uranus": "Уран",
    "neptune": "Нептун",
    "pluto": "Плутон",
}

_SIGN_RU = {
    "aries": "Овен",
    "taurus": "Телец",
    "gemini": "Близнецы",
    "cancer": "Рак",
    "leo": "Лев",
    "virgo": "Дева",
    "libra": "Весы",
    "scorpio": "Скорпион",
    "sagittarius": "Стрелец",
    "capricorn": "Козерог",
    "aquarius": "Водолей",
    "pisces": "Рыбы",
}

_ASPECT_RU = {
    "conjunction": "соединение",
    "sextile": "секстиль",
    "square": "квадрат",
    "trine": "тригон",
    "opposition": "оппозиция",
}


def _ru_body(name: str | None) -> str:
    key = str(name or "").strip().lower().replace(" ", "_")
    return _PLANET_RU.get(key) or str(name or "").strip()


def _ru_sign(name: str | None) -> str:
    key = str(name or "").strip().lower()
    return _SIGN_RU.get(key) or str(name or "").strip()


def _ru_aspect(name: str | None) -> str:
    key = str(name or "").strip().lower().replace(" ", "_")
    return _ASPECT_RU.get(key) or str(name or "").strip()


def format_event_fact_ru(event: dict[str, Any], *, locale: str = "ru") -> str:
    """Build one factual RU sentence from structured fields (or fall back to fact_ru)."""
    if not (locale or "").lower().startswith("ru"):
        # EN later — keep RU projection for now
        pass

    existing = str(event.get("fact_ru") or "").strip()
    kind = str(event.get("kind") or "").lower()
    body = _ru_body(event.get("body") or (event.get("meta") or {}).get("planet"))
    sign = _ru_sign(event.get("sign") or (event.get("meta") or {}).get("sign"))
    aspect = _ru_aspect(event.get("aspect") or (event.get("meta") or {}).get("aspect"))
    target = _ru_body(event.get("target_body") or (event.get("meta") or {}).get("target"))
    when = str(event.get("exact_at") or event.get("when") or "")
    time_bit = ""
    if len(when) >= 16 and "T" in when:
        time_bit = f" около {when[11:16]}"

    if kind == "station_direct":
        base = f"{body} разворачивается в директное движение"
        if sign:
            base = f"{base} в знаке {sign}"
        return base + "."
    if kind == "station":
        base = f"{body} становится в станцию"
        if sign:
            base = f"{base} в знаке {sign}"
        return base + "."
    if kind == "moon_ingress":
        return f"Луна переходит в {sign or 'новый знак'}{time_bit}."
    if kind == "planet_ingress":
        return f"{body} входит в {sign or 'новый знак'}{time_bit}."
    if kind in {"lunar_aspect", "sky_aspect", "cycle_aspect"}:
        left = "Луна" if kind == "lunar_aspect" else body
        right = target or aspect
        if aspect and target:
            return f"{left} — {aspect} — {target}{time_bit}."
        if aspect:
            return f"{left}: {aspect}{time_bit}."
        return existing or f"{left} в аспекте дня{time_bit}."
    if kind == "phase_change":
        title = str(event.get("title_ru") or "Смена лунной фазы")
        if sign:
            return f"{title} в знаке {sign}."
        return f"{title}."
    if kind == "retrograde_edge":
        edge = str((event.get("meta") or {}).get("edge") or "")
        if edge == "end":
            return f"{body} завершает ретроградное окно."
        if edge == "start":
            return f"{body} входит в ретроградное окно."
        return existing or f"{body}: край ретроградного окна."
    if kind == "solar_daylight":
        return existing or "Локальный свет дня задаёт длину активного окна."
    if kind == "seasonal":
        return existing or str(event.get("title_ru") or "Сезонный поворот") + "."
    if kind == "calendar":
        return existing or str(event.get("title_ru") or "Календарный маркер") + "."

    return existing or str(event.get("title_ru") or "Сигнал неба") + "."


def project_fact_ru(events: list[dict[str, Any]], *, locale: str = "ru") -> list[dict[str, Any]]:
    """Ensure each event has fact_ru as projection from structure."""
    out: list[dict[str, Any]] = []
    for raw in events:
        if not isinstance(raw, dict):
            continue
        row = dict(raw)
        row["fact_ru"] = format_event_fact_ru(row, locale=locale)
        out.append(row)
    return out

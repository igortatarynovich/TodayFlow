"""Helpers to extract DaySourceInputs atoms from profile / request context."""

from __future__ import annotations

from datetime import date, datetime, time
from typing import Any


def parse_iso_date(value: Any) -> date | None:
    if value is None:
        return None
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    text = str(value).strip()
    if not text:
        return None
    try:
        return date.fromisoformat(text[:10])
    except ValueError:
        return None


def birth_date_from_core_profile(core_profile: dict[str, Any] | None) -> date | None:
    """Resolve birth_date from core_profile.astro (or nested person/astro shapes)."""
    if not isinstance(core_profile, dict):
        return None
    astro = core_profile.get("astro") if isinstance(core_profile.get("astro"), dict) else {}
    parsed = parse_iso_date(astro.get("birth_date"))
    if parsed:
        return parsed
    person = core_profile.get("person") if isinstance(core_profile.get("person"), dict) else {}
    return parse_iso_date(person.get("birth_date") or person.get("date_of_birth"))


def birth_time_from_core_profile(core_profile: dict[str, Any] | None) -> time | None:
    if not isinstance(core_profile, dict):
        return None
    astro = core_profile.get("astro") if isinstance(core_profile.get("astro"), dict) else {}
    raw = astro.get("birth_time")
    if raw is None:
        return None
    if isinstance(raw, time):
        return raw
    text = str(raw).strip()
    if not text:
        return None
    for fmt in ("%H:%M:%S", "%H:%M"):
        try:
            return datetime.strptime(text[:8], fmt).time()
        except ValueError:
            continue
    return None


def birth_place_from_core_profile(
    core_profile: dict[str, Any] | None,
) -> tuple[float | None, float | None]:
    """Birth coordinates (not current geo) when present on profile."""
    if not isinstance(core_profile, dict):
        return None, None
    astro = core_profile.get("astro") if isinstance(core_profile.get("astro"), dict) else {}
    lat = astro.get("latitude")
    lon = astro.get("longitude")
    # Prefer explicit birth_* if ever split from current geo.
    if astro.get("birth_latitude") is not None:
        lat = astro.get("birth_latitude")
    if astro.get("birth_longitude") is not None:
        lon = astro.get("birth_longitude")
    try:
        lat_f = float(lat) if lat is not None else None
    except (TypeError, ValueError):
        lat_f = None
    try:
        lon_f = float(lon) if lon is not None else None
    except (TypeError, ValueError):
        lon_f = None
    return lat_f, lon_f


def birth_name_from_core_profile(core_profile: dict[str, Any] | None) -> str | None:
    """Display / first name for soft name_numbers (optional)."""
    if not isinstance(core_profile, dict):
        return None
    person = core_profile.get("person") if isinstance(core_profile.get("person"), dict) else {}
    for key in ("display_name", "first_name", "full_name", "birth_name"):
        raw = person.get(key)
        text = str(raw).strip() if raw is not None else ""
        if text:
            return text[:120]
    settings = core_profile.get("settings") if isinstance(core_profile.get("settings"), dict) else {}
    first = str(settings.get("first_name") or "").strip()
    last = str(settings.get("last_name") or "").strip()
    joined = " ".join(x for x in (first, last) if x).strip()
    return joined[:120] or None


def geo_from_core_profile(
    core_profile: dict[str, Any] | None,
) -> tuple[float | None, float | None, str | None]:
    """Return (lat, lon, timezone_name) from profile astro block when present."""
    if not isinstance(core_profile, dict):
        return None, None, None
    astro = core_profile.get("astro") if isinstance(core_profile.get("astro"), dict) else {}
    lat = astro.get("latitude")
    lon = astro.get("longitude")
    try:
        lat_f = float(lat) if lat is not None else None
    except (TypeError, ValueError):
        lat_f = None
    try:
        lon_f = float(lon) if lon is not None else None
    except (TypeError, ValueError):
        lon_f = None
    tz = astro.get("timezone_name") or astro.get("timezone")
    tz_s = str(tz).strip() if tz else None
    return lat_f, lon_f, tz_s or None

"""Helpers to extract DaySourceInputs atoms from profile / request context."""

from __future__ import annotations

from datetime import date, datetime
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

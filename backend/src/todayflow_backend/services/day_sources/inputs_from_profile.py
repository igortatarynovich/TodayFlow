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

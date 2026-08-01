"""Typed failures from the astrology engine (no silent wrong geometry)."""

from __future__ import annotations


class TimezoneRequiredError(ValueError):
    """Precise birth time was given but no IANA TZ / offset — refuse civil-as-UT."""

    code = "timezone_required"

    def __init__(self, message: str | None = None) -> None:
        super().__init__(
            message
            or (
                "Precise birth time requires timezone_name (IANA) or "
                "timezone_offset_minutes; refusing civil-clock-as-UT fallback"
            )
        )


class EphemerisDegradedError(RuntimeError):
    """Swiss Ephemeris files missing/unusable — would silently fall back to Moshier."""

    code = "ephemeris_degraded"

    def __init__(self, message: str | None = None) -> None:
        super().__init__(
            message
            or (
                "Swiss Ephemeris (FLG_SWIEPH) unavailable; refusing silent Moshier "
                "fallback. Set SWISS_EPHEMERIS_PATH with sepl/semo ephe files."
            )
        )

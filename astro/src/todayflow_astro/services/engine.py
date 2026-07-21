"""Astrology calculation engine powered by Swiss Ephemeris."""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Tuple
from zoneinfo import ZoneInfo

import swisseph as swe

from todayflow_astro.core import models

ZODIAC = [
    "Aries",
    "Taurus",
    "Gemini",
    "Cancer",
    "Leo",
    "Virgo",
    "Libra",
    "Scorpio",
    "Sagittarius",
    "Capricorn",
    "Aquarius",
    "Pisces",
]

# Единый флаг эфемерид для планет и чувствительных точек.
_CALC_FLAG = getattr(swe, "FLG_SWIEPH", 0)


class AstroEngine:
    """Encapsulates chart calculations so endpoints stay thin."""

    PLANET_SERIES = [
        ("sun", swe.SUN),
        ("moon", swe.MOON),
        ("mercury", swe.MERCURY),
        ("venus", swe.VENUS),
        ("mars", swe.MARS),
        ("jupiter", swe.JUPITER),
        ("saturn", swe.SATURN),
        ("uranus", swe.URANUS),
        ("neptune", swe.NEPTUNE),
        ("pluto", swe.PLUTO),
    ]

    def __init__(self) -> None:
        ephe_path = os.getenv("SWISS_EPHEMERIS_PATH")
        if ephe_path:
            swe.set_ephe_path(ephe_path)

    def compute_chart(self, payload: models.ChartRequest) -> models.ChartResponse:
        birth_dt_utc, precise = self._parse_birth_datetime_utc(payload)
        julian_day = self._julian_day(birth_dt_utc)

        rising, houses, cusp_longitudes = self._resolve_rising_and_houses(julian_day, precise, payload)

        positions: list[models.PlanetPosition] = []
        for label, planet_id in self.PLANET_SERIES:
            planet_position = self._planet_position(julian_day, planet_id, label)
            if planet_position:
                positions.append(self._with_house(planet_position, cusp_longitudes))

        north = self._planet_position(
            julian_day,
            getattr(swe, "TRUE_NODE", getattr(swe, "MEAN_NODE", None)),
            "north_node",
        )
        if north is not None:
            positions.append(self._with_house(north, cusp_longitudes))
            south_lon = (north.longitude + 180.0) % 360.0
            s_sign, s_deg = self._sign_from_longitude(south_lon)
            south_base = models.PlanetPosition(
                body="south_node",
                sign=s_sign,
                degree=round(s_deg, 2),
                longitude=south_lon,
            )
            positions.append(self._with_house(south_base, cusp_longitudes))

        chiron_id = getattr(swe, "CHIRON", None)
        if chiron_id is not None:
            ch = self._planet_position(julian_day, chiron_id, "chiron")
            if ch:
                positions.append(self._with_house(ch, cusp_longitudes))

        lilith_id = getattr(swe, "MEAN_APOG", None)
        if lilith_id is not None:
            li = self._planet_position(julian_day, lilith_id, "lilith")
            if li:
                positions.append(self._with_house(li, cusp_longitudes))

        # Honest ASC: only when birth time is known and houses computed.
        if rising is not None and cusp_longitudes:
            positions.append(rising.model_copy(update={"house": 1}))

        meta: dict = {
            "location": payload.birth.location,
            "coordinates": payload.coordinates.model_dump() if payload.coordinates else None,
            "house_system": "Placidus" if cusp_longitudes else None,
            "bodies": [p.body for p in positions],
            "time_unknown": not precise,
            "ascendant_precision": "exact" if (precise and cusp_longitudes) else "unavailable",
            "timezone_name": self._resolve_timezone_name(payload),
        }
        meta = {k: v for k, v in meta.items() if v is not None}

        return models.ChartResponse(
            mode="precise" if precise and cusp_longitudes else "unknown_time",
            positions=positions,
            houses=houses,
            metadata=meta,
        )

    @staticmethod
    def _with_house(
        pos: models.PlanetPosition, cusp_longitudes: list[float] | None
    ) -> models.PlanetPosition:
        if not cusp_longitudes:
            return pos
        h = AstroEngine._house_for_longitude(pos.longitude, cusp_longitudes)
        return pos.model_copy(update={"house": h})

    @staticmethod
    def _house_for_longitude(longitude: float, cusps: list[float]) -> int:
        """Номер дома 1–12; cusps[i] — куспид начала дома i+1 (Placidus)."""
        p = longitude % 360.0
        for h in range(12):
            start = cusps[h] % 360.0
            end = cusps[(h + 1) % 12] % 360.0
            if start <= end:
                if start <= p < end:
                    return h + 1
            else:
                if p >= start or p < end:
                    return h + 1
        return 12

    def _planet_position(self, julian_day: float, body: int | None, label: str) -> models.PlanetPosition | None:
        if body is None:
            return None
        try:
            result = swe.calc_ut(julian_day, body, _CALC_FLAG)
        except swe.Error:
            return None
        if isinstance(result, tuple) and len(result) == 2 and isinstance(result[0], (list, tuple)):
            values = result[0]
        else:
            values = result
        longitude = float(values[0]) % 360.0
        sign, degree = self._sign_from_longitude(longitude)
        return models.PlanetPosition(body=label, sign=sign, degree=round(degree, 2), longitude=longitude)

    def _resolve_rising_and_houses(
        self,
        julian_day: float,
        precise: bool,
        payload: models.ChartRequest,
    ) -> Tuple[models.PlanetPosition | None, dict, list[float] | None]:
        coordinates = payload.coordinates
        if precise and coordinates:
            asc, houses, cusps = self._compute_houses(julian_day, coordinates.latitude, coordinates.longitude)
            if asc and cusps:
                return asc, houses, cusps
        # No fabricated ASC when birth time is unknown or houses cannot be computed.
        return None, {}, None

    def _compute_houses(
        self, julian_day: float, latitude: float, longitude: float
    ) -> Tuple[models.PlanetPosition | None, dict, list[float] | None]:
        try:
            cusps, ascmc = swe.houses_ex(julian_day, swe.FLG_SWIEPH, latitude, longitude, b"P")
        except TypeError:
            cusps, ascmc = swe.houses_ex(julian_day, latitude, longitude, b"P")
        except swe.Error:
            return None, {}, None

        cusp_list = self._normalize_twelve_cusps(cusps)
        if not cusp_list or len(cusp_list) != 12:
            return None, {}, None

        asc_lon = float(ascmc[0]) % 360.0
        sign, degree = self._sign_from_longitude(asc_lon)
        houses: dict = {}
        for i, cusp in enumerate(cusp_list, start=1):
            house_sign, house_degree = self._sign_from_longitude(cusp)
            houses[f"house_{i}"] = {
                "sign": house_sign,
                "degree": round(house_degree, 2),
                "longitude": round(cusp % 360.0, 4),
            }
        return (
            models.PlanetPosition(body="rising", sign=sign, degree=round(degree, 2), longitude=asc_lon),
            houses,
            cusp_list,
        )

    @staticmethod
    def _normalize_twelve_cusps(cusps) -> list[float] | None:
        raw = [float(c) % 360.0 for c in cusps]
        if len(raw) >= 13:
            return raw[1:13]
        if len(raw) == 12:
            return raw
        return None

    def _sign_from_longitude(self, longitude: float) -> Tuple[str, float]:
        normalized = longitude % 360
        index = int(normalized // 30) % 12
        degree = normalized % 30
        return ZODIAC[index], degree

    def _resolve_timezone_name(self, payload: models.ChartRequest) -> str | None:
        for candidate in (
            payload.timezone_name,
            payload.birth.timezone_name,
        ):
            name = (candidate or "").strip()
            if name:
                return name
        return None

    def _parse_birth_datetime_utc(self, payload: models.ChartRequest) -> Tuple[datetime, bool]:
        """Return (UTC naive datetime for Swiss Ephemeris, precise_time_flag)."""
        date_str = payload.birth.date
        time_str = payload.birth.time
        precise = bool(time_str and str(time_str).strip())
        if precise:
            raw = str(time_str).strip()
            parts = raw.split(":")
            try:
                h = int(parts[0])
                m = int(parts[1]) if len(parts) > 1 else 0
                s = int(float(parts[2])) if len(parts) > 2 else 0
            except (ValueError, IndexError):
                h, m, s = 12, 0, 0
                precise = False
        else:
            h, m, s = 12, 0, 0

        try:
            local_naive = datetime(int(date_str[0:4]), int(date_str[5:7]), int(date_str[8:10]), h, m, s)
        except (ValueError, TypeError, IndexError):
            return datetime.now(timezone.utc).replace(tzinfo=None), False

        if not precise:
            # Midday UT for planetary positions when time is unknown — no houses/ASC.
            return local_naive.replace(tzinfo=None), False

        tz_name = self._resolve_timezone_name(payload)
        if tz_name:
            try:
                tz = ZoneInfo(tz_name)
                local_aware = local_naive.replace(tzinfo=tz)
                return local_aware.astimezone(timezone.utc).replace(tzinfo=None), True
            except Exception:
                pass

        offset = payload.timezone_offset_minutes
        if offset is None:
            offset = payload.birth.timezone_offset_minutes
        if offset is not None:
            try:
                delta = timedelta(minutes=int(offset))
                return (local_naive - delta).replace(tzinfo=None), True
            except (TypeError, ValueError):
                pass

        # Last resort: treat civil clock as UT (legacy behavior) but still mark precise
        # only when time was provided — houses still need coordinates.
        return local_naive.replace(tzinfo=None), True

    def _julian_day(self, dt: datetime) -> float:
        decimal_hours = dt.hour + dt.minute / 60.0 + dt.second / 3600.0
        return swe.julday(dt.year, dt.month, dt.day, decimal_hours)

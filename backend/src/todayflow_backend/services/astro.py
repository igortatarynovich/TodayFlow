"""HTTP client for the dedicated astrology microservice."""

from __future__ import annotations

from typing import Any

import httpx
from pydantic import BaseModel, field_validator

from todayflow_backend.core.config import settings


def coerce_chart_positions(positions: Any) -> list[dict]:
    """Accept list rows or legacy dict keyed by body name (old natal cache rows)."""
    if isinstance(positions, list):
        return [p for p in positions if isinstance(p, dict)]
    if isinstance(positions, dict):
        out: list[dict] = []
        for key, value in positions.items():
            if not isinstance(value, dict):
                continue
            row = dict(value)
            if not (row.get("body") or row.get("name") or row.get("id") or row.get("planet")):
                row["body"] = key
            out.append(row)
        return out
    return []


def coerce_chart_houses(houses: Any) -> dict:
    """ChartResponse stores houses as a dict; drop unusable legacy list shapes."""
    if isinstance(houses, dict):
        return houses
    return {}


class ChartResponse(BaseModel):
    mode: str
    positions: list[dict]
    houses: dict
    metadata: dict

    @field_validator("positions", mode="before")
    @classmethod
    def _coerce_positions(cls, value: Any) -> list[dict]:
        return coerce_chart_positions(value)

    @field_validator("houses", mode="before")
    @classmethod
    def _coerce_houses(cls, value: Any) -> dict:
        return coerce_chart_houses(value)

    @field_validator("metadata", mode="before")
    @classmethod
    def _coerce_metadata(cls, value: Any) -> dict:
        return value if isinstance(value, dict) else {}


class AstroService:
    def __init__(self, base_url: str | None = None):
        self.base_url = base_url or settings.astro_service_url
        self._client = httpx.AsyncClient(base_url=self.base_url, timeout=10.0)

    async def compute_chart(self, birth_payload: dict, coordinates: dict | None = None) -> ChartResponse:
        payload = _build_chart_payload(birth_payload, coordinates)
        response = await self._client.post("/chart", json=payload)
        handled = _handle_chart_error_response(response)
        if handled is not None:
            return handled
        response.raise_for_status()
        return ChartResponse.model_validate(response.json())

    async def close(self) -> None:
        await self._client.aclose()


def _build_chart_payload(
    birth_payload: dict[str, Any],
    coordinates: dict[str, Any] | None = None,
) -> dict[str, Any]:
    birth = dict(birth_payload)
    loc = (birth.get("location") or "").strip()
    if not loc and coordinates:
        lat, lon = coordinates.get("latitude"), coordinates.get("longitude")
        if lat is not None and lon is not None:
            loc = f"{lat},{lon}"
    birth["location"] = loc
    payload: dict[str, Any] = {"birth": birth}
    if coordinates:
        payload["coordinates"] = coordinates
    if birth.get("timezone_name"):
        payload["timezone_name"] = birth.get("timezone_name")
    if birth.get("timezone_offset_minutes") is not None:
        payload["timezone_offset_minutes"] = birth.get("timezone_offset_minutes")
    return payload


def _handle_chart_error_response(response: httpx.Response) -> ChartResponse | None:
    detail = None
    if response.headers.get("content-type", "").startswith("application/json"):
        try:
            detail = response.json().get("detail")
        except Exception:
            detail = None
    code = None
    if isinstance(detail, dict):
        code = detail.get("code")
    elif isinstance(detail, list) and detail and isinstance(detail[0], dict):
        code = detail[0].get("code")
    if response.status_code == 422 and code == "timezone_required":
        return ChartResponse(
            mode="timezone_required",
            positions=[],
            houses={},
            metadata={
                "timezone_required": True,
                "ascendant_precision": "unavailable",
                "time_unknown": False,
            },
        )
    if response.status_code == 503 and code == "ephemeris_degraded":
        return ChartResponse(
            mode="ephemeris_degraded",
            positions=[],
            houses={},
            metadata={
                "ephemeris_degraded": True,
                "ephemeris_source": "moshier_refused",
                "ascendant_precision": "unavailable",
                "time_unknown": False,
            },
        )
    return None


def compute_chart_sync(
    birth_payload: dict[str, Any],
    coordinates: dict[str, Any] | None = None,
    *,
    base_url: str | None = None,
) -> ChartResponse:
    """Synchronous chart computation for non-async callers (e.g. natal_facts).

    Raises httpx.HTTPError on unexpected service failures; caller must degrade.
    """
    url = base_url or settings.astro_service_url
    payload = _build_chart_payload(birth_payload, coordinates)
    with httpx.Client(base_url=url, timeout=10.0) as client:
        response = client.post("/chart", json=payload)
    handled = _handle_chart_error_response(response)
    if handled is not None:
        return handled
    response.raise_for_status()
    return ChartResponse.model_validate(response.json())


def get_astro_service() -> AstroService:
    """Зависимость FastAPI для эндпоинтов с наталом; в тестах подменяется фейком."""
    return AstroService()

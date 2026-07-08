"""HTTP client for the dedicated astrology microservice."""

from __future__ import annotations

import httpx
from pydantic import BaseModel

from todayflow_backend.core.config import settings


class ChartResponse(BaseModel):
    mode: str
    positions: list[dict]
    houses: dict
    metadata: dict


class AstroService:
    def __init__(self, base_url: str | None = None):
        self.base_url = base_url or settings.astro_service_url
        self._client = httpx.AsyncClient(base_url=self.base_url, timeout=10.0)

    async def compute_chart(self, birth_payload: dict, coordinates: dict | None = None) -> ChartResponse:
        birth = dict(birth_payload)
        loc = (birth.get("location") or "").strip()
        if not loc and coordinates:
            lat, lon = coordinates.get("latitude"), coordinates.get("longitude")
            if lat is not None and lon is not None:
                loc = f"{lat},{lon}"
        birth["location"] = loc
        payload: dict = {"birth": birth}
        if coordinates:
            payload["coordinates"] = coordinates
        response = await self._client.post("/chart", json=payload)
        response.raise_for_status()
        return ChartResponse.model_validate(response.json())

    async def close(self) -> None:
        await self._client.aclose()


def get_astro_service() -> AstroService:
    """Зависимость FastAPI для эндпоинтов с наталом; в тестах подменяется фейком."""
    return AstroService()

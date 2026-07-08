"""Детерминированные натальные карты для pytest без astro-микросервиса."""

from __future__ import annotations

from todayflow_backend.services.astro import ChartResponse


def chart_response_for_birth_payload(birth_payload: dict) -> ChartResponse:
    """Стабильная карта по дате/времени рождения: разные профили → разные долготы → синастрия считается."""
    raw = f"{birth_payload.get('date', '')}|{birth_payload.get('time', '')}"
    seed = sum(ord(c) for c in raw) % 360
    key_planets = [
        "Sun",
        "Moon",
        "Mercury",
        "Venus",
        "Mars",
        "Jupiter",
        "Saturn",
        "Uranus",
        "Neptune",
        "Pluto",
        "Chiron",
        "North Node",
        "South Node",
    ]
    sign_names = [
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
    positions: list[dict] = []
    for i, body in enumerate(key_planets):
        lon = float((seed + i * 29) % 360)
        positions.append(
            {
                "body": body,
                "longitude": lon,
                "sign": sign_names[int(lon // 30) % 12],
            }
        )
    positions.append(
        {
            "body": "rising",
            "longitude": float(seed % 360),
            "sign": sign_names[int(seed // 30) % 12],
        }
    )
    houses: dict[str, dict[str, float]] = {}
    for h in range(1, 13):
        houses[str(h)] = {"cusp": float(((seed + (h - 1) * 30) % 360))}
    return ChartResponse(mode="natal", positions=positions, houses=houses, metadata={"source": "pytest_fake_astro"})


class FakeAstroServiceForTests:
    """Тот же контракт, что `AstroService`, без HTTP."""

    async def compute_chart(self, birth_payload: dict, coordinates: dict | None = None) -> ChartResponse:
        _ = coordinates
        return chart_response_for_birth_payload(birth_payload)

    async def close(self) -> None:
        return None

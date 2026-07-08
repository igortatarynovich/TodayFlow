"""Shared request/response models for the astro microservice."""

from __future__ import annotations

from pydantic import BaseModel, Field
from typing import List, Literal, Optional


class BirthData(BaseModel):
    date: str  # ISO YYYY-MM-DD
    time: Optional[str] = None  # HH:MM, optional
    # Optional at wire level: backend/iOS often send date+time+coordinates only; engine uses coordinates for houses.
    location: str = ""


class Coordinates(BaseModel):
    latitude: float
    longitude: float


class ChartRequest(BaseModel):
    birth: BirthData
    coordinates: Coordinates | None = None


PlanetBody = Literal[
    "sun",
    "moon",
    "mercury",
    "venus",
    "mars",
    "jupiter",
    "saturn",
    "uranus",
    "neptune",
    "pluto",
    "north_node",
    "south_node",
    "chiron",
    "lilith",
    "rising",
]


class PlanetPosition(BaseModel):
    body: PlanetBody
    sign: str
    degree: float
    longitude: float  # эклиптика 0..360° для аспектов и колеса
    house: int | None = None  # 1–12 при точном времени и известных координатах


class ChartResponse(BaseModel):
    mode: Literal["precise", "unknown_time"]
    positions: List[PlanetPosition] = Field(default_factory=list)
    houses: dict = Field(default_factory=dict)
    metadata: dict = Field(default_factory=dict)

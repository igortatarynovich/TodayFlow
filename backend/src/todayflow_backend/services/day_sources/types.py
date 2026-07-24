"""Types for Day Source Registry (docs/DAY_SOURCES_CANON.md)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, time
from typing import Any, Callable, Literal

DAY_SOURCES_CONTRACT = "day_sources_v0"

SourceLayer = Literal["foundation", "personal", "life", "interactive"]
SourceStatus = Literal["ok", "unavailable", "skipped"]


@dataclass(frozen=True)
class DaySourceInputs:
    """Minimal shared inputs for resolving/running Source Families."""

    target_date: date
    timezone: str | None = None
    lat: float | None = None
    lon: float | None = None
    birth_date: date | None = None
    birth_time: time | None = None
    birth_lat: float | None = None
    birth_lon: float | None = None
    # Bridge to current celestial pipeline until ephemeris adapters are first-class.
    celestial_events: dict[str, Any] | None = None
    # Optional Swiss/AstroService snapshots (from celestial_events.ephemeris or pre-fetch).
    ephemeris: dict[str, Any] | None = None
    locale: str = "ru"
    # Explicit electional/horary request (canon §5.4 — not auto-run on Today).
    electional_requested: bool = False
    electional_time: time | None = None
    electional_question: str | None = None


@dataclass
class SourceResult:
    family_id: str
    capability_ids: list[str]
    layer: SourceLayer
    status: SourceStatus
    payload: dict[str, Any] = field(default_factory=dict)
    evidence_refs: list[str] = field(default_factory=list)
    calculation_version: str = "source-v0"
    unavailable_reason: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "family_id": self.family_id,
            "capability_ids": list(self.capability_ids),
            "layer": self.layer,
            "status": self.status,
            "unavailable_reason": self.unavailable_reason,
            "payload": self.payload,
            "evidence_refs": list(self.evidence_refs),
            "calculation_version": self.calculation_version,
        }


@dataclass(frozen=True)
class SourceFamilySpec:
    family_id: str
    layer: SourceLayer
    in_foundation: bool
    in_personal: bool
    in_today: bool
    # Input keys from DaySourceInputs that must be present for status=ok
    # Special: "celestial_events" means non-empty celestial_events dict.
    required_input_keys: tuple[str, ...] = ()
    run: Callable[[DaySourceInputs], SourceResult] | None = None

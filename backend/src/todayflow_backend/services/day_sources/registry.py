"""Day Source Registry — register / resolve / collect Source Families."""

from __future__ import annotations

from typing import Any, Iterable

from todayflow_backend.services.day_sources.adapters.moon import run_moon
from todayflow_backend.services.day_sources.adapters.numerology import run_numerology
from todayflow_backend.services.day_sources.adapters.weekday_ruler import run_weekday_ruler
from todayflow_backend.services.day_sources.adapters.western_astrology import (
    run_western_astrology,
)
from todayflow_backend.services.day_sources.types import (
    DaySourceInputs,
    SourceFamilySpec,
    SourceResult,
)


def _has_input(inputs: DaySourceInputs, key: str) -> bool:
    if key == "target_date":
        return inputs.target_date is not None
    if key == "celestial_events":
        return isinstance(inputs.celestial_events, dict) and bool(inputs.celestial_events)
    if key == "birth_date":
        return inputs.birth_date is not None
    if key == "birth_time":
        return inputs.birth_time is not None
    if key == "geo":
        return inputs.lat is not None and inputs.lon is not None
    if key == "timezone":
        return bool(inputs.timezone)
    return getattr(inputs, key, None) is not None


class DaySourceRegistry:
    def __init__(self) -> None:
        self._families: dict[str, SourceFamilySpec] = {}

    def register(self, spec: SourceFamilySpec) -> None:
        if not spec.run:
            raise ValueError(f"SourceFamilySpec {spec.family_id} missing run()")
        self._families[spec.family_id] = spec

    def list_families(self) -> list[str]:
        return sorted(self._families)

    def get(self, family_id: str) -> SourceFamilySpec | None:
        return self._families.get(family_id)

    def resolve(
        self,
        inputs: DaySourceInputs,
        *,
        foundation_only: bool = True,
    ) -> list[SourceFamilySpec]:
        out: list[SourceFamilySpec] = []
        for spec in self._families.values():
            if foundation_only and not spec.in_foundation:
                continue
            out.append(spec)
        return sorted(out, key=lambda s: s.family_id)

    def collect(
        self,
        inputs: DaySourceInputs,
        *,
        foundation_only: bool = True,
        family_ids: Iterable[str] | None = None,
    ) -> dict[str, SourceResult]:
        wanted = set(family_ids) if family_ids is not None else None
        results: dict[str, SourceResult] = {}
        for spec in self.resolve(inputs, foundation_only=foundation_only):
            if wanted is not None and spec.family_id not in wanted:
                continue
            missing = [k for k in spec.required_input_keys if not _has_input(inputs, k)]
            if missing:
                results[spec.family_id] = SourceResult(
                    family_id=spec.family_id,
                    capability_ids=[],
                    layer=spec.layer,
                    status="unavailable",
                    unavailable_reason="missing_" + ",".join(missing),
                    calculation_version="registry-gate-v0",
                )
                continue
            assert spec.run is not None
            results[spec.family_id] = spec.run(inputs)
        return results


def default_registry() -> DaySourceRegistry:
    reg = DaySourceRegistry()
    reg.register(
        SourceFamilySpec(
            family_id="western_astrology",
            layer="foundation",
            in_foundation=True,
            in_personal=True,
            in_today=True,
            required_input_keys=("celestial_events",),
            run=run_western_astrology,
        )
    )
    reg.register(
        SourceFamilySpec(
            family_id="moon",
            layer="foundation",
            in_foundation=True,
            in_personal=False,
            in_today=True,
            required_input_keys=("celestial_events",),
            run=run_moon,
        )
    )
    reg.register(
        SourceFamilySpec(
            family_id="numerology",
            layer="foundation",
            in_foundation=True,
            in_personal=True,
            in_today=True,
            required_input_keys=("target_date",),
            run=run_numerology,
        )
    )
    reg.register(
        SourceFamilySpec(
            family_id="weekday_ruler",
            layer="foundation",
            in_foundation=True,
            in_personal=False,
            in_today=True,
            required_input_keys=("target_date",),
            run=run_weekday_ruler,
        )
    )
    return reg


_DEFAULT: DaySourceRegistry | None = None


def get_default_registry() -> DaySourceRegistry:
    global _DEFAULT
    if _DEFAULT is None:
        _DEFAULT = default_registry()
    return _DEFAULT


def collect_foundation_sources(
    inputs: DaySourceInputs,
    *,
    registry: DaySourceRegistry | None = None,
) -> dict[str, Any]:
    """Run foundation families; return serializable bundle for Day Foundation."""
    reg = registry or get_default_registry()
    results = reg.collect(inputs, foundation_only=True)
    return {
        "contract_version": "day_source_bundle_v0",
        "target_date": inputs.target_date.isoformat(),
        "sources": {fid: res.to_dict() for fid, res in results.items()},
        "ok_family_ids": sorted(
            fid for fid, res in results.items() if res.status == "ok"
        ),
    }

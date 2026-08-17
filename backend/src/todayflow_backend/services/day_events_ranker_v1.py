"""Deterministic ranking of day celestial events into 1–3 drivers + compositions.

Canon: day_thesis rests on ranked_drivers + compositions; ambient never competes for the plot.
Evidence pack is nested under DayContext — not a second day SoT.
"""

from __future__ import annotations

from typing import Any

DAY_EVENTS_RANKER_V1 = "day_events_ranker_v1"

_KIND_BASE: dict[str, float] = {
    "station_direct": 0.95,
    "station": 0.93,
    "phase_change": 0.88,
    "moon_ingress": 0.82,
    "planet_ingress": 0.78,
    "lunar_aspect": 0.74,
    "sky_aspect": 0.70,
    "cycle_aspect": 0.72,
    "retrograde_edge": 0.86,
    "perigee": 0.65,
    "apogee": 0.60,
    "seasonal": 0.55,
    "solar_daylight": 0.35,
    "calendar": 0.30,
    "retrograde": 0.45,
    "personal_transit": 0.68,
}

_AMBIENT_KINDS = frozenset({"solar_daylight", "calendar", "retrograde"})

_MAX_DRIVERS = 3
_MIN_DRIVER_STRENGTH = 0.42

# Pair rules: (kind_a, kind_b) → composition relationship + thesis hint family/variant
_COMPOSITION_RULES: tuple[tuple[frozenset[str], str, str, float], ...] = (
    (
        frozenset({"station_direct", "moon_ingress"}),
        "reinforcing",
        "communication/clarity_returns_after_delay",
        0.12,
    ),
    (
        frozenset({"station_direct", "lunar_aspect"}),
        "escalating",
        "communication/truth_without_filter",
        0.10,
    ),
    (
        frozenset({"moon_ingress", "phase_change"}),
        "transition",
        "change/soft_expansion",
        0.08,
    ),
    (
        frozenset({"lunar_aspect", "sky_aspect"}),
        "escalating",
        "change/sudden_turns",
        0.08,
    ),
    (
        frozenset({"station_direct", "cycle_aspect"}),
        "reinforcing",
        "communication/restart_messages",
        0.08,
    ),
    (
        frozenset({"retrograde_edge", "lunar_aspect"}),
        "counterbalancing",
        "pressure/patience_test",
        0.09,
    ),
)


def _clip01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def event_strength(event: dict[str, Any]) -> float:
    """Compute strength 0..1 from kind + optional orb/tension/priority_hint."""
    kind = str(event.get("kind") or "").strip().lower()
    base = _KIND_BASE.get(kind, 0.40)
    hint = str(event.get("priority_hint") or "").strip().lower()
    if hint == "primary":
        base = max(base, 0.85)
    elif hint == "secondary":
        base = max(base, 0.55)
    elif hint == "ambient":
        base = min(base, 0.38)

    orb = event.get("orb_delta") if event.get("orb_delta") is not None else event.get("orb")
    if orb is not None:
        try:
            orb_f = abs(float(orb))
            if orb_f <= 1.0:
                base += 0.12
            elif orb_f <= 3.0:
                base += 0.05
            else:
                base -= 0.05
        except (TypeError, ValueError):
            pass

    tension = str(event.get("tension_level") or "").strip().lower()
    if tension in {"high", "tense", "challenging"}:
        base += 0.06
    elif tension in {"harmonious", "easy", "low"}:
        base += 0.02

    strength_label = str(event.get("strength_label") or "").strip().lower()
    if strength_label in {"exact", "strong"}:
        base += 0.08
    elif strength_label in {"tight", "medium"}:
        base += 0.04
    elif strength_label in {"loose", "weak"}:
        base -= 0.04

    daily = event.get("daily_score")
    if daily is None:
        daily = (event.get("meta") or {}).get("daily_score") if isinstance(event.get("meta"), dict) else None
    if daily is not None:
        try:
            # Blend kind floor with shared-sky daily influence (exact Mercury×Jupiter beats a distant phase).
            base = (base * 0.45) + (_clip01(float(daily)) * 0.55)
        except (TypeError, ValueError):
            pass

    return _clip01(base)


def build_event_compositions(drivers: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Derive causal compositions from top drivers (not just isolated events)."""
    if len(drivers) < 2:
        return []
    out: list[dict[str, Any]] = []
    for i, a in enumerate(drivers):
        for b in drivers[i + 1 :]:
            kinds = frozenset(
                {
                    str(a.get("kind") or "").lower(),
                    str(b.get("kind") or "").lower(),
                }
            )
            for rule_kinds, relationship, thesis_hint, boost in _COMPOSITION_RULES:
                if not rule_kinds.issubset(kinds):
                    continue
                strength = _clip01(
                    (float(a.get("strength") or 0) + float(b.get("strength") or 0)) / 2.0 + boost
                )
                ids = [str(a.get("id")), str(b.get("id"))]
                cid = f"comp-{'-'.join(sorted(ids))}"
                out.append(
                    {
                        "composition_id": cid,
                        "event_ids": ids,
                        "relationship": relationship,
                        "strength": strength,
                        "thesis_hint": thesis_hint,
                    }
                )
                break
    out.sort(key=lambda c: (-float(c.get("strength") or 0), str(c.get("composition_id") or "")))
    return out[:3]


def rank_day_events(events: list[dict[str, Any]]) -> dict[str, Any]:
    """Attach strength, pick 1–3 ranked_drivers, compositions, ambient."""
    enriched: list[dict[str, Any]] = []
    for raw in events:
        if not isinstance(raw, dict):
            continue
        eid = str(raw.get("id") or "").strip()
        if not eid:
            continue
        row = dict(raw)
        row["strength"] = event_strength(row)
        kind = str(row.get("kind") or "").lower()
        if not row.get("priority_hint"):
            if kind in _AMBIENT_KINDS or row["strength"] < _MIN_DRIVER_STRENGTH:
                row["priority_hint"] = "ambient"
            elif row["strength"] >= 0.75:
                row["priority_hint"] = "primary"
            else:
                row["priority_hint"] = "secondary"
        enriched.append(row)

    candidates = [
        e
        for e in enriched
        if str(e.get("priority_hint") or "") != "ambient"
        and float(e.get("strength") or 0) >= _MIN_DRIVER_STRENGTH
    ]
    candidates.sort(key=lambda e: (-float(e.get("strength") or 0), str(e.get("id") or "")))

    drivers: list[dict[str, Any]] = []
    seen_kinds: set[str] = set()
    for ev in candidates:
        kind = str(ev.get("kind") or "")
        if kind in seen_kinds and len(drivers) >= 1:
            if float(ev.get("strength") or 0) < 0.90 or len(drivers) >= _MAX_DRIVERS:
                continue
        drivers.append(ev)
        seen_kinds.add(kind)
        if len(drivers) >= _MAX_DRIVERS:
            break

    if not drivers and enriched:
        enriched_sorted = sorted(
            enriched, key=lambda e: (-float(e.get("strength") or 0), str(e.get("id") or ""))
        )
        top = enriched_sorted[0]
        top["priority_hint"] = "primary"
        drivers = [top]

    driver_ids = [str(d["id"]) for d in drivers]
    driver_set = set(driver_ids)
    ambient_ids = [str(ev["id"]) for ev in enriched if str(ev["id"]) not in driver_set]
    compositions = build_event_compositions(drivers)

    return {
        "contract_version": "day_events_pack_v1",
        "ranker_version": DAY_EVENTS_RANKER_V1,
        "role": "evidence",  # nested under DayContext — not day SoT
        "events": enriched,
        "ranked_drivers": driver_ids,
        "compositions": compositions,
        "ambient": ambient_ids,
    }

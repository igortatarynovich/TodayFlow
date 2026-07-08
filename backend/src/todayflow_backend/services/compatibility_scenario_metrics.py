"""Scenario-scoped metrics: same pair gets different % and hero score per theme.

Metric blends load from DATA/reference/compatibility/ (Compat-ref-1).
"""

from __future__ import annotations

from todayflow_backend.data.compatibility_scenario_metrics_registry_loader import (
    get_default_scenario_id,
    get_scenario_blends,
    get_scenario_funnel_domains,
    get_scenario_hero_weights,
)
from todayflow_backend.services.sign_compatibility_product import SignCompatSubscores

Blend = dict[str, float]


def _clamp(x: float) -> int:
    return max(0, min(100, int(round(x))))


def _pair_jitter(from_sign: str, to_sign: str, scenario_id: str, slot: str) -> int:
    a, b = sorted([(from_sign or "").lower(), (to_sign or "").lower()])
    h = sum(ord(c) for c in f"{a}:{b}:{scenario_id}:{slot}")
    return (h % 5) - 2


def _element_nudge(scenario_id: str, slot: str, fe: str, te: str, fm: str, tm: str) -> int:
    fe, te = fe.lower(), te.lower()
    fm, tm = fm.lower(), tm.lower()
    if scenario_id == "office" and fm == tm and slot == "stability":
        return 5
    if scenario_id == "money_together" and fe in {"earth", "water"} and te in {"earth", "water"} and slot == "stability":
        return 6
    if scenario_id == "vacation" and fe in {"fire", "air"} and te in {"fire", "air"} and slot == "attraction":
        return 4
    if scenario_id == "living_together" and "water" in {fe, te} and slot == "stability":
        return 3
    if scenario_id == "conflict_style" and fe != te and slot == "conflicts":
        return 4
    if scenario_id == "apocalypse" and slot == "stability":
        return 2
    if scenario_id == "sex" and slot == "sexuality":
        return 3
    return 0


def _blend(base: dict[str, int], weights: Blend) -> int:
    total = 0.0
    wsum = 0.0
    for key, w in weights.items():
        if w <= 0:
            continue
        total += float(base.get(key, 0)) * w
        wsum += w
    if wsum <= 0:
        return _clamp(sum(base.values()) / max(len(base), 1))
    return _clamp(total / wsum)


def apply_scenario_metrics(
    scenario_id: str,
    subscores: dict[str, int],
    overall: int,
    *,
    from_sign: str = "",
    to_sign: str = "",
    from_element: str = "",
    to_element: str = "",
    from_modality: str = "",
    to_modality: str = "",
) -> tuple[SignCompatSubscores, int]:
    """Return theme-scoped subscores + hero % — different atmosphere per scenario."""
    blends_map = get_scenario_blends()
    hero_map = get_scenario_hero_weights()
    default_id = get_default_scenario_id()
    sid = scenario_id if scenario_id in blends_map else default_id
    blends = blends_map[sid]
    base = {
        "attraction": int(subscores.get("attraction", overall)),
        "stability": int(subscores.get("stability", overall)),
        "conflicts": int(subscores.get("conflicts", overall)),
        "sexuality": int(subscores.get("sexuality", overall)),
    }

    adjusted: dict[str, int] = {}
    for slot in ("attraction", "stability", "conflicts", "sexuality"):
        w = blends.get(slot) or blends.get("attraction")
        score = _blend(base, w)
        score += _element_nudge(sid, slot, from_element, to_element, from_modality, to_modality)
        score += _pair_jitter(from_sign, to_sign, sid, slot)
        adjusted[slot] = _clamp(score)

    hero_w = hero_map.get(sid) or hero_map.get(default_id)
    if hero_w is None and hero_map:
        hero_w = next(iter(hero_map.values()))
    hero = _blend(adjusted, hero_w)
    hero += _pair_jitter(from_sign, to_sign, sid, "hero")
    hero = _clamp(hero)

    return (
        SignCompatSubscores(
            attraction=adjusted["attraction"],
            stability=adjusted["stability"],
            conflicts=adjusted["conflicts"],
            sexuality=adjusted["sexuality"],
        ),
        hero,
    )


def funnel_domains_for_scenario(scenario_id: str | None) -> list[str] | None:
    if not scenario_id:
        return None
    domains = get_scenario_funnel_domains().get(scenario_id)
    return list(domains) if domains else None

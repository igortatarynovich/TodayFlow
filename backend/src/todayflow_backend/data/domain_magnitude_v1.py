"""Domain magnitude v1 — calibrated product weights for top_driver valence.

Canon: docs/foundation/DOMAIN_MAGNITUDE_V1.md
Source (pre-extract): today_domain_verdicts_v1.valence_domain if/elif draft.

These are NOT atomic foundation facts (sign/house/aspect character).
Numbers are preserved exactly from the draft — do not silently recalibrate.
Aspect *character* (harmonious/challenging) remains foundation_constants_v1.
"""

from __future__ import annotations

from typing import Any

from todayflow_backend.data.foundation_constants_v1 import (
    aspect_is_challenging,
    aspect_is_harmonious,
)

CONTRACT_VERSION = "domain_magnitude_v1"

# Any harmonious aspect → this magnitude, before domain tables.
ANY_HARMONIOUS_MAGNITUDE = 1.0

# Observed rule (was implicit in if/elif branches) — documentation only:
# conjunction+mars charges work/energy; friction in relationships; money treats
# mars with saturn/pluto as negative conjunction (no separate mars+ drive).
MARS_CONJUNCTION_RULE_RU = (
    "Соединение с Марсом: work/energy — заряд (драйв/активация); "
    "relationships — трение/напор; money — в общем негативном пуле с Сатурном/Плутоном."
)

# special_cases: checked in order. aspect may be exact id or "challenging"
# (any aspect_is_challenging). natal_points = frozenset of natal ids.
DOMAIN_MAGNITUDE_V1: dict[str, dict[str, Any]] = {
    "work": {
        "special_cases": (
            {
                "aspect": "square",
                "natal_points": frozenset({"mars"}),
                "magnitude": 0.85,
                "note": "pressure → act → charged, not friction",
            },
            {
                "aspect": "opposition",
                "natal_points": frozenset({"sun", "mc", "midheaven"}),
                "magnitude": -0.55,
                "note": "career axis stretch → friction, not ban",
            },
            {
                "aspect": "challenging",
                "natal_points": frozenset({"saturn"}),
                "magnitude": -0.7,
            },
        ),
        "conjunction_by_transit": {
            "venus": 0.8,
            "jupiter": 0.8,
            "mars": 0.75,
            "pluto": 0.75,
            "saturn": -0.55,
        },
        "conjunction_other": 0.0,
        "challenging_fallback": -0.65,
        "default": 0.0,
    },
    "money": {
        # OPEN: no square+planet specials (unlike work/relationships/energy).
        # Preserved empty — calibration gap vs intentional simplicity; see canon.
        "special_cases": (),
        "conjunction_by_transit": {
            "venus": 1.0,
            "jupiter": 1.0,
            "saturn": -0.7,
            "pluto": -0.7,
            "mars": -0.7,
        },
        "conjunction_other": 0.0,
        "challenging_fallback": -0.75,
        "default": 0.0,
    },
    "relationships": {
        "special_cases": (
            {
                "aspect": "square",
                "natal_points": frozenset({"venus"}),
                "magnitude": -0.8,
            },
            {
                "aspect": "square",
                "natal_points": frozenset({"moon"}),
                "magnitude": -0.7,
            },
        ),
        "conjunction_by_transit": {
            "venus": 1.0,
            "jupiter": 1.0,
            "saturn": -0.75,
            "mars": -0.75,
            "pluto": -0.75,
        },
        "conjunction_other": 0.0,
        "challenging_fallback": -0.7,
        "default": 0.0,
    },
    "energy": {
        "special_cases": (
            {
                "aspect": "square",
                "natal_points": frozenset({"mars"}),
                "magnitude": 0.9,
                "note": "activation, not friction",
            },
        ),
        "conjunction_by_transit": {
            "venus": 0.8,
            "jupiter": 0.8,
            "mars": 0.85,
            "saturn": -0.65,
            "pluto": -0.65,
        },
        "conjunction_other": 0.0,
        "challenging_fallback": -0.6,
        "default": 0.0,
    },
}

# Unknown domain historically fell through to the energy branch in valence_domain.
_DEFAULT_DOMAIN = "energy"

OPEN_CALIBRATION_QUESTIONS: tuple[dict[str, str], ...] = (
    {
        "id": "money_no_square_specials",
        "issue": "money — no square+planet special cases",
        "status": "open",
        "decision_now": "preserve empty special_cases; do not invent weights",
    },
    {
        "id": "mars_conjunction_by_domain",
        "issue": "conjunction+mars sign depends on domain",
        "status": "documented_rule",
        "decision_now": "formalize MARS_CONJUNCTION_RULE_RU; numbers unchanged",
    },
    {
        "id": "challenging_fallback_scale",
        "issue": "challenging_fallback by domain",
        "status": "documented_principle",
        "decision_now": (
            "domain irreversibility scale step 0.05: "
            "money−0.75 > relationships−0.70 > work−0.65 > energy−0.60"
        ),
    },
)

# Canonical order for the irreversibility scale (harshest → softest fallback).
CHALLENGING_FALLBACK_IRREVERSIBILITY_ORDER: tuple[str, ...] = (
    "money",
    "relationships",
    "work",
    "energy",
)
CHALLENGING_FALLBACK_STEP = 0.05


def _norm(name: str | None) -> str:
    return (name or "").strip().lower().replace(" ", "_")


def _match_special(
    case: dict[str, Any],
    *,
    asp: str,
    natal: str,
    challenging: bool,
) -> bool:
    rule = str(case.get("aspect") or "")
    points = case.get("natal_points") or frozenset()
    if natal not in points:
        return False
    if rule == "challenging":
        return challenging
    return asp == rule


def resolve_valence(
    domain: str,
    aspect: str,
    transiting_planet: str,
    natal_point: str,
) -> float:
    """Thin resolver: harmonious → specials → conjunction → challenging_fallback → default."""
    asp = _norm(aspect)
    transit = _norm(transiting_planet)
    natal = _norm(natal_point)
    dom = _norm(domain) or _DEFAULT_DOMAIN

    if aspect_is_harmonious(asp):
        return float(ANY_HARMONIOUS_MAGNITUDE)

    table = DOMAIN_MAGNITUDE_V1.get(dom) or DOMAIN_MAGNITUDE_V1[_DEFAULT_DOMAIN]
    challenging = aspect_is_challenging(asp)

    for case in table.get("special_cases") or ():
        if _match_special(case, asp=asp, natal=natal, challenging=challenging):
            return float(case["magnitude"])

    if asp == "conjunction":
        by_transit = table.get("conjunction_by_transit") or {}
        if transit in by_transit:
            return float(by_transit[transit])
        return float(table.get("conjunction_other", 0.0))

    if challenging:
        return float(table.get("challenging_fallback", 0.0))

    return float(table.get("default", 0.0))

"""Soft name_numbers pair flavor for Compatibility (not a score gate).

Reuses Day Source school: pythagorean_latin_v0_via_ru_translit via
`build_name_numbers_payload`. Names are optional; omit pack when neither side
resolves to an ok Expression.
"""

from __future__ import annotations

from typing import Any

from todayflow_backend.services.day_sources.name_numbers import build_name_numbers_payload


def _slim_side(pack: dict[str, Any] | None) -> dict[str, Any] | None:
    if not isinstance(pack, dict) or pack.get("status") != "ok":
        return None
    expr = pack.get("expression") if isinstance(pack.get("expression"), dict) else None
    if not expr or expr.get("value") is None:
        return None
    soul = pack.get("soul_urge") if isinstance(pack.get("soul_urge"), dict) else None
    pers = pack.get("personality") if isinstance(pack.get("personality"), dict) else None
    return {
        "birth_name": pack.get("birth_name"),
        "normalized_name": pack.get("normalized_name"),
        "expression": {"value": expr.get("value"), "theme_ru": expr.get("theme_ru")},
        "soul_urge": (
            {"value": soul.get("value"), "theme_ru": soul.get("theme_ru")}
            if soul and soul.get("value") is not None
            else None
        ),
        "personality": (
            {"value": pers.get("value"), "theme_ru": pers.get("theme_ru")}
            if pers and pers.get("value") is not None
            else None
        ),
        "summary_ru": pack.get("summary_ru"),
    }


def _pair_claim_line(a: dict[str, Any] | None, b: dict[str, Any] | None) -> str | None:
    if a and b:
        ea = a["expression"]["value"]
        eb = b["expression"]["value"]
        return (
            f"Числа имён (soft): Expression {ea} и {eb} — "
            f"как каждый звучит вовне; не заменяет карту пары."
        )
    side = a or b
    if not side:
        return None
    return (
        f"Числа имени (soft): Expression {side['expression']['value']} — "
        f"слой самопрезентации; второй стороне не хватает имени."
    )


def build_name_numbers_pair(
    *,
    name_a: str | None = None,
    name_b: str | None = None,
    label_a: str = "A",
    label_b: str = "B",
) -> dict[str, Any] | None:
    """Build optional soft pair pack. Returns None when nothing usable."""
    raw_a = build_name_numbers_payload(name_a)
    raw_b = build_name_numbers_payload(name_b)
    a = _slim_side(raw_a)
    b = _slim_side(raw_b)
    if not a and not b:
        return None

    claim = _pair_claim_line(a, b)
    return {
        "school_canon": "pythagorean_latin_v0_via_ru_translit",
        "status": "ok" if (a and b) else "partial",
        "a": a,
        "b": b,
        "labels": {"a": label_a, "b": label_b},
        "claim_lines": [claim] if claim else [],
        "limitation_ru": (
            "Soft name numbers for pair flavor only. Same school as Today Day Personal. "
            "Not a synastry score; not destiny from a label."
        ),
    }

"""hook_reveal_v1 — assemble base + chorus/props bridge for day hooks.

Canon: docs/audits/DAY_SYMBOL_REVEAL_CANON_V1.md

- base: static lookup (card_base / number_base / COLOR_CATALOG)
- bridge_to_day: sole SoT = interpretive_chorus / props.color (never explainer)
- instruction / personal: optional overlays; never invent bridge on fail
"""

from __future__ import annotations

from typing import Any, Literal

from todayflow_backend.data import card_base_v1, number_base_v1
from todayflow_backend.services import day_color_catalog_v1 as color_catalog

HookKind = Literal["card", "number", "color"]

BRIDGE_FAIL_COPY = {
    "card": "Не удалось раскрыть день для этой карты.",
    "number": "Не удалось раскрыть день для этого числа.",
    "color": "Не удалось раскрыть день для этого цвета.",
}


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _clean(text: Any) -> str:
    return str(text or "").strip()


def _bridge_from_voice(voice: dict[str, Any]) -> str:
    link = _clean(voice.get("link_to_conflict"))
    if link:
        return link
    # Accept projected chorus shapes (role / for_conflict / tempo as weak bridge)
    for key in ("role", "for_conflict", "archetype_role", "human_meaning"):
        alt = _clean(voice.get(key))
        if alt:
            return alt
    return ""


def build_card_hook_reveal(
    *,
    card_id: int,
    orientation: str,
    chorus: dict[str, Any] | None = None,
    instruction: str | None = None,
    personal_angle: str | None = None,
    profile_depth: str = "light",
) -> dict[str, Any]:
    base_row = card_base_v1.get_base_meaning(card_id, orientation)
    if not base_row:
        return {
            "kind": "card",
            "identity": {"id": card_id, "orientation": card_base_v1.normalize_orientation(orientation)},
            "base": None,
            "bridge_to_day": None,
            "bridge_status": "unavailable",
            "bridge_fail_copy": BRIDGE_FAIL_COPY["card"],
            "personal_angle": "omit",
            "instruction": None,
            "instruction_status": "unavailable",
            "result_loop": "tap",
        }

    chorus_d = _as_dict(chorus)
    voice = _as_dict(chorus_d.get("day_card"))
    bridge = _bridge_from_voice(voice)
    bridge_ok = bool(bridge)
    personal = "omit"
    if profile_depth == "deep" and bridge_ok:
        pa = _clean(personal_angle)
        personal = pa if pa else "omit"

    instr = _clean(instruction) if bridge_ok else ""
    return {
        "kind": "card",
        "identity": {
            "id": base_row["id"],
            "orientation": base_row["orientation"],
            "name_ru": base_row["name_ru"],
        },
        "base": {"meaning": base_row["meaning"], "keywords": base_row["keywords"]},
        "bridge_to_day": bridge if bridge_ok else None,
        "bridge_status": "ok" if bridge_ok else "unavailable",
        "bridge_fail_copy": None if bridge_ok else BRIDGE_FAIL_COPY["card"],
        "personal_angle": personal,
        "instruction": instr or None,
        "instruction_status": "ok" if instr else ("unavailable" if not bridge_ok else "unavailable"),
        "result_loop": "tap",
    }


def build_number_hook_reveal(
    *,
    value: int,
    chorus: dict[str, Any] | None = None,
    instruction: str | None = None,
    personal_angle: str | None = None,
    profile_depth: str = "light",
) -> dict[str, Any]:
    base_row = number_base_v1.get_number_base(int(value))
    if not base_row:
        return {
            "kind": "number",
            "identity": {"value": int(value)},
            "base": None,
            "bridge_to_day": None,
            "bridge_status": "unavailable",
            "bridge_fail_copy": BRIDGE_FAIL_COPY["number"],
            "personal_angle": "omit",
            "instruction": None,
            "instruction_status": "unavailable",
            "result_loop": "none",
        }

    chorus_d = _as_dict(chorus)
    voice = _as_dict(chorus_d.get("day_number"))
    bridge = _bridge_from_voice(voice)
    if not bridge:
        # tempo alone is not a full bridge, but tempo+style can serve when link missing
        tempo = _clean(voice.get("tempo"))
        style = _clean(voice.get("style"))
        if tempo and style:
            bridge = f"{tempo}; {style}"
        elif tempo:
            bridge = tempo
    bridge_ok = bool(bridge)
    personal = "omit"
    if profile_depth == "deep" and bridge_ok:
        pa = _clean(personal_angle)
        personal = pa if pa else "omit"
    instr = _clean(instruction) if bridge_ok else ""
    return {
        "kind": "number",
        "identity": {
            "value": base_row["value"],
            "title": base_row["title"],
        },
        "base": {"meaning": base_row["base_meaning"], "keywords": base_row["keywords"]},
        "bridge_to_day": bridge if bridge_ok else None,
        "bridge_status": "ok" if bridge_ok else "unavailable",
        "bridge_fail_copy": None if bridge_ok else BRIDGE_FAIL_COPY["number"],
        "personal_angle": personal,
        "instruction": instr or None,
        "instruction_status": "ok" if instr else "unavailable",
        "result_loop": "none",
    }


def build_color_hook_reveal(
    *,
    color_name: str,
    props_color: dict[str, Any] | None = None,
    instruction: str | None = None,
) -> dict[str, Any]:
    props = _as_dict(props_color)
    name = _clean(props.get("name") or color_name)
    entry = color_catalog.get_color_entry(name) if name else None
    base_archetype = ""
    apply = {}
    if entry:
        base_archetype = _clean(entry.get("symbolic_property"))
        apply = dict(entry.get("apply") or {})
        intensity = _clean(entry.get("intensity_default"))
    else:
        intensity = ""

    bridge = _clean(props.get("link_to_conflict"))
    bridge_ok = bool(bridge)
    # Apply hints as instruction fallback when bridge ok and no explicit instruction
    instr = _clean(instruction)
    if not instr and bridge_ok:
        where = _clean(props.get("where_to_use"))
        if where:
            instr = where
        elif intensity:
            instr = intensity

    base_payload = None
    if base_archetype or name:
        base_payload = {
            "meaning": base_archetype or name,
            "name": name,
            "apply": {k: v for k, v in apply.items() if v},
            "intensity_default": intensity or None,
        }

    return {
        "kind": "color",
        "identity": {"name": name},
        "base": base_payload,
        "bridge_to_day": bridge if bridge_ok else None,
        "bridge_status": "ok" if bridge_ok else "unavailable",
        "bridge_fail_copy": None if bridge_ok else BRIDGE_FAIL_COPY["color"],
        "personal_angle": "omit",
        "instruction": instr or None,
        "instruction_status": "ok" if instr else "unavailable",
        "result_loop": "none",
    }


def attach_hooks_to_symbol_view(
    view: dict[str, Any],
    *,
    chorus: dict[str, Any] | None = None,
    props: dict[str, Any] | None = None,
    profile_depth: str = "light",
) -> dict[str, Any]:
    """Mutate a copy of public symbol view with hook_reveal nests when revealed."""
    out = dict(view)
    card = _as_dict(out.get("card"))
    number = _as_dict(out.get("number"))
    props_d = _as_dict(props)
    color_props = _as_dict(props_d.get("color"))

    if card.get("revealed") and card.get("id") is not None:
        hook = build_card_hook_reveal(
            card_id=int(card["id"]),
            orientation=str(card.get("orientation") or "upright"),
            chorus=chorus,
            profile_depth=profile_depth,
        )
        # Prefer card_base meaning over EN deck string in public view
        if hook.get("base"):
            card = {
                **card,
                "name": hook["identity"].get("name_ru") or card.get("name"),
                "meaning": hook["base"]["meaning"],
                "keywords": hook["base"].get("keywords") or card.get("keywords") or [],
                "hook_reveal": hook,
            }
            out["card"] = card

    if number.get("revealed") and number.get("reduced_value") is not None:
        hook = build_number_hook_reveal(
            value=int(number.get("reduced_value") or number.get("value") or 0),
            chorus=chorus,
            profile_depth=profile_depth,
        )
        if hook.get("base"):
            number = {
                **number,
                "title": hook["identity"].get("title") or number.get("title"),
                "summary": hook["base"]["meaning"],
                "hook_reveal": hook,
            }
            out["number"] = number

    if color_props.get("name") or props_d.get("color"):
        color_hook = build_color_hook_reveal(
            color_name=str(color_props.get("name") or ""),
            props_color=color_props,
        )
        out["color_hook_reveal"] = color_hook

    return out

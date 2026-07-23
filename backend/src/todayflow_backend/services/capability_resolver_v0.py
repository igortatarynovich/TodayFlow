"""Capability Resolver v0 — Availability Matrix → capability state.

SoT: docs/PRODUCT_AVAILABILITY_MATRIX.md (APPROVED Profile)
     docs/PRODUCT_CAPABILITY_CONTRACTS.md

Resolves available_input → natal mode · unavailable_facts · allowed Profile 3.1 slots.
Does not call LLM. Does not invent ASC/houses.
"""

from __future__ import annotations

from datetime import date, time
from typing import Any, Literal

NatalMode = Literal["none", "date_only", "full"]
AccessTier = Literal["guest", "free", "trial", "paid"]

# Profile matrix 3.1 slot ids (stable keys for gates / adapter / UI later).
SLOT_IDENTITY = "identity_summary"
SLOT_SUN_ELEMENT_NUM = "sun_element_numerology"
SLOT_CATALOG = "cultural_catalog"
SLOT_NAME_NUMEROLOGY = "name_numerology"
SLOT_NATAL_STRUCTURE = "natal_structure"
SLOT_EMOTIONAL = "emotional_style"
SLOT_DECISION = "decision_style"
SLOT_RELATIONSHIP = "relationship_style"
SLOT_WORK = "work_and_realization"
SLOT_MONEY = "money_patterns"
SLOT_HOME = "home_and_security"
SLOT_STRENGTHS = "strengths"
SLOT_TENSIONS = "tensions_growth"
SLOT_HELPS = "helps"
SLOT_LIMITATIONS = "limitations"
SLOT_CTA_TODAY = "cta_today"
SLOT_CTA_DEPTH = "cta_depth"

L1_SLOTS = frozenset(
    {
        SLOT_IDENTITY,
        SLOT_SUN_ELEMENT_NUM,
        SLOT_CATALOG,
        SLOT_EMOTIONAL,
        SLOT_DECISION,
        SLOT_RELATIONSHIP,
        SLOT_STRENGTHS,
        SLOT_TENSIONS,
        SLOT_LIMITATIONS,
        SLOT_CTA_TODAY,
        SLOT_CTA_DEPTH,
    }
)
L2_STRUCTURE_SLOTS = frozenset(
    {
        SLOT_NATAL_STRUCTURE,
        SLOT_WORK,
        SLOT_MONEY,
        SLOT_HOME,
    }
)
L3_SLOTS = frozenset({SLOT_HELPS})
NAME_SLOTS = frozenset({SLOT_NAME_NUMEROLOGY})

RESOLVER_VERSION = "capability_resolver_v0.2"


def _truthy_name(display_name: str | None) -> bool:
    return bool((display_name or "").strip())


def _has_time(birth_time: time | str | None, time_unknown: bool) -> bool:
    if time_unknown:
        return False
    if birth_time is None:
        return False
    if isinstance(birth_time, str) and not birth_time.strip():
        return False
    return True


def _has_coords(latitude: float | None, longitude: float | None) -> bool:
    return latitude is not None and longitude is not None


def resolve_natal_mode(
    *,
    birth_date: date | str | None,
    birth_time: time | str | None = None,
    time_unknown: bool = True,
    latitude: float | None = None,
    longitude: float | None = None,
) -> NatalMode:
    if birth_date is None or (isinstance(birth_date, str) and not birth_date.strip()):
        return "none"
    if not _has_time(birth_time, time_unknown):
        return "date_only"
    if not _has_coords(latitude, longitude):
        # Time without place must not unlock full angles/houses.
        return "date_only"
    return "full"


def build_unavailable_facts(
    *,
    mode: NatalMode,
    has_name: bool,
    has_time: bool,
    has_place: bool,
) -> list[dict[str, str]]:
    """Explicit unavailable keys with matrix reasons (not inventable)."""
    out: list[dict[str, str]] = []

    def add(key: str, reason: str) -> None:
        if not any(u["key"] == key for u in out):
            out.append({"key": key, "reason": reason})

    if mode == "none":
        add("sun_sign", "birth_date_missing")
        add("planets", "birth_date_missing")
        add("life_path", "birth_date_missing")
        add("ascendant", "birth_date_missing")
        add("houses", "birth_date_missing")
        add("mc", "birth_date_missing")
        add("ic", "birth_date_missing")
        add("descendant", "birth_date_missing")
        add("name_numerology", "birth_date_missing")
        return out

    if mode != "full":
        if not has_time:
            reason = "birth_time_missing"
        elif not has_place:
            reason = "birth_place_missing"
        else:
            reason = "birth_time_or_place_missing"
        for key in ("ascendant", "mc", "ic", "descendant", "houses", "planets_in_houses", "house_rulers"):
            add(key, reason)

    if not has_name:
        add("name_numerology", "name_missing")
        add("expression_number", "name_missing")
        add("soul_urge_number", "name_missing")
        add("personality_number", "name_missing")

    return out


def access_allows_l3(access: AccessTier) -> bool:
    return access in ("trial", "paid")


def allowed_profile_slots(
    *,
    mode: NatalMode,
    has_name: bool,
    access: AccessTier,
) -> dict[str, Any]:
    """Matrix 3.1 slot gates.

    - ``data_eligible`` — slots the interpretation may include (same for Free/Trial).
    - ``revealed`` / ``allowed`` — slots UI may show for this access tier.
    - ``access_gated`` — in the saved result, hidden in presentation (not a second interpretation).
    - ``omitted`` — missing input data (not a tariff cut).
    """
    all_slots = L1_SLOTS | L2_STRUCTURE_SLOTS | L3_SLOTS | NAME_SLOTS
    if access == "guest" or mode == "none":
        return {
            "data_eligible": [],
            "revealed": [],
            "allowed": [],
            "access_gated": sorted(L3_SLOTS) if access != "guest" and mode == "none" else [],
            "omitted": sorted(all_slots),
            "gated_l3": sorted(L3_SLOTS),
        }

    data_eligible: set[str] = set(L1_SLOTS) | set(L3_SLOTS)
    omitted: set[str] = set()

    if has_name:
        data_eligible |= NAME_SLOTS
    else:
        omitted |= NAME_SLOTS

    if mode == "full":
        data_eligible |= L2_STRUCTURE_SLOTS
    else:
        omitted |= L2_STRUCTURE_SLOTS

    access_gated: set[str] = set()
    if not access_allows_l3(access):
        access_gated |= L3_SLOTS & data_eligible

    revealed = data_eligible - access_gated
    return {
        "data_eligible": sorted(data_eligible),
        "revealed": sorted(revealed),
        "allowed": sorted(revealed),  # presentation alias for UI wiring
        "access_gated": sorted(access_gated),
        "omitted": sorted(omitted),
        "gated_l3": sorted(access_gated & L3_SLOTS),
    }


def resolve_capability(
    *,
    birth_date: date | str | None = None,
    birth_time: time | str | None = None,
    time_unknown: bool = True,
    location_name: str | None = None,
    latitude: float | None = None,
    longitude: float | None = None,
    timezone_name: str | None = None,
    display_name: str | None = None,
    access: AccessTier = "free",
) -> dict[str, Any]:
    """Full capability pack for natal_facts + Profile slot gates."""
    has_name = _truthy_name(display_name)
    has_time = _has_time(birth_time, time_unknown)
    # Place for angles requires coordinates (matrix: lat/lon). Location name alone is not enough.
    has_place = _has_coords(latitude, longitude)
    mode = resolve_natal_mode(
        birth_date=birth_date,
        birth_time=birth_time,
        time_unknown=time_unknown,
        latitude=latitude,
        longitude=longitude,
    )
    unavailable = build_unavailable_facts(
        mode=mode,
        has_name=has_name,
        has_time=has_time,
        has_place=has_place,
    )
    slots = allowed_profile_slots(mode=mode, has_name=has_name, access=access)

    # Preserve entered time even when mode stays date_only (time without place).
    time_str: str | None = None
    if has_time and birth_time is not None:
        if isinstance(birth_time, time):
            time_str = birth_time.strftime("%H:%M:%S")
        else:
            time_str = str(birth_time).strip() or None

    birth_iso: str | None
    if isinstance(birth_date, date):
        birth_iso = birth_date.isoformat()
    elif birth_date:
        birth_iso = str(birth_date).strip() or None
    else:
        birth_iso = None

    location = (location_name or "").strip() or None
    angles_eligible = mode == "full"
    time_recorded = bool(has_time and time_str)
    birth_time_unsuitable_for_angles = bool(time_recorded and not angles_eligible)

    available_input = {
        "display_name": (display_name or "").strip() or None,
        "birth_date": birth_iso,
        "birth_time": time_str,
        "time_unknown": not has_time,
        "location_name": location,
        "latitude": latitude,
        "longitude": longitude,
        "timezone_name": timezone_name,
        "mode": mode if mode != "none" else "date_only",
        # Honesty markers — time may be saved while ASC/houses stay locked.
        "angles_eligible": angles_eligible,
        "time_recorded": time_recorded,
        "birth_time_unsuitable_for_angles": birth_time_unsuitable_for_angles,
    }

    l3_in_result = mode != "none"
    l3_revealed = access_allows_l3(access) and l3_in_result

    return {
        "resolver_version": RESOLVER_VERSION,
        "access": access,
        "mode": mode,
        "has_name": has_name,
        "has_time": has_time,
        "has_place": has_place,
        "angles_eligible": angles_eligible,
        "time_recorded": time_recorded,
        "birth_time_unsuitable_for_angles": birth_time_unsuitable_for_angles,
        "available_input": available_input,
        "unavailable_facts": unavailable,
        "profile_slots": slots,
        "layers": {
            "l1": mode != "none",
            "l2_structure": mode == "full",
            # Saved interpretation may include L3; tariff only controls reveal.
            "l3_in_result": l3_in_result,
            "l3_revealed": l3_revealed,
            "l3_depth": l3_revealed,  # alias: presentation depth, not a second generation
            "name_numerology": has_name and mode != "none",
        },
        "user_messages": _user_messages(
            mode=mode,
            has_name=has_name,
            has_time=has_time,
            has_place=has_place,
            access=access,
        ),
    }


def _user_messages(
    *,
    mode: NatalMode,
    has_name: bool,
    has_time: bool,
    has_place: bool,
    access: AccessTier,
) -> list[dict[str, str]]:
    """Voice-safe CTA copy from Availability Matrix слой 1."""
    msgs: list[dict[str, str]] = []
    if mode == "none":
        msgs.append(
            {
                "code": "need_birth_date",
                "text": "Добавьте дату рождения, чтобы построить основу профиля.",
            }
        )
        return msgs
    if not has_time:
        msgs.append(
            {
                "code": "need_birth_time",
                "text": "Дата создаёт астрологическую и нумерологическую основу. "
                "Время рождения откроет Асцендент, дома и жизненные сферы.",
            }
        )
    elif not has_place:
        msgs.append(
            {
                "code": "need_birth_place",
                "text": "Чтобы рассчитать Асцендент и дома, укажите место рождения — "
                "нужны координаты и часовой пояс.",
            }
        )
    if not has_name:
        msgs.append(
            {
                "code": "need_name",
                "text": "Добавьте имя для отдельного разбора имени — на натальную карту оно не влияет.",
            }
        )
    if mode != "none" and not access_allows_l3(access):
        msgs.append(
            {
                "code": "l3_gated",
                "text": "В trial откроются конкретные опоры и практические выводы.",
            }
        )
    return msgs


def insight_tier_to_access(insight_depth_tier: str | None) -> AccessTier:
    """Map billing insight tier → matrix access column."""
    t = (insight_depth_tier or "free").strip().lower()
    if t in ("pro", "premium"):
        return "paid"
    return "free"


def merge_unavailable_into_facts(
    facts: dict[str, Any],
    capability: dict[str, Any],
) -> dict[str, Any]:
    """Ensure natal_facts.unavailable_facts includes resolver keys (precise reasons)."""
    out = dict(facts)
    existing = [
        {"key": str(u["key"]), "reason": str(u.get("reason") or "unavailable")}
        for u in (out.get("unavailable_facts") or [])
        if isinstance(u, dict) and u.get("key")
    ]
    by_key = {u["key"]: u for u in existing}
    for u in capability.get("unavailable_facts") or []:
        if not isinstance(u, dict) or not u.get("key"):
            continue
        key = str(u["key"])
        # Prefer resolver reason for structure keys (clearer than generic).
        if key in by_key and key in (
            "ascendant",
            "mc",
            "ic",
            "descendant",
            "houses",
            "planets_in_houses",
            "house_rulers",
            "name_numerology",
            "expression_number",
            "soul_urge_number",
            "personality_number",
        ):
            by_key[key] = {"key": key, "reason": str(u.get("reason") or by_key[key]["reason"])}
        elif key not in by_key:
            by_key[key] = {"key": key, "reason": str(u.get("reason") or "unavailable")}
    out["unavailable_facts"] = list(by_key.values())
    out["capability"] = {
        "resolver_version": capability.get("resolver_version"),
        "mode": capability.get("mode"),
        "layers": capability.get("layers"),
        "profile_slots": capability.get("profile_slots"),
        "access": capability.get("access"),
        "user_messages": capability.get("user_messages"),
    }
    return out

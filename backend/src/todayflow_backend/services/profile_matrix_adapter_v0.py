"""Profile matrix adapter v0 — legacy Snapshot/contract → Availability 3.1 slots.

Does not expand the legacy funnel. Maps existing fields into matrix slot bags and
applies capability + access gates. UI may consume this later; no layout changes here.

SoT: docs/PRODUCT_AVAILABILITY_MATRIX.md §3.1
"""

from __future__ import annotations

from typing import Any

from todayflow_backend.services.capability_resolver_v0 import (
    SLOT_CATALOG,
    SLOT_CTA_DEPTH,
    SLOT_CTA_TODAY,
    SLOT_DECISION,
    SLOT_EMOTIONAL,
    SLOT_HELPS,
    SLOT_HOME,
    SLOT_IDENTITY,
    SLOT_LIMITATIONS,
    SLOT_MONEY,
    SLOT_NAME_NUMEROLOGY,
    SLOT_NATAL_STRUCTURE,
    SLOT_RELATIONSHIP,
    SLOT_STRENGTHS,
    SLOT_SUN_ELEMENT_NUM,
    SLOT_TENSIONS,
    SLOT_WORK,
    AccessTier,
    resolve_capability,
)

ADAPTER_VERSION = "profile_matrix_adapter_v0.1"


def resolve_access_tier(
    *,
    insight_depth_tier: str | None = None,
    subscription_status: str | None = None,
    billing_level: str | None = None,
    is_guest: bool = False,
) -> AccessTier:
    """Map billing / trial status → matrix access column."""
    if is_guest:
        return "guest"
    status = (subscription_status or "").strip().lower()
    if status == "trialing":
        return "trial"
    tier = (insight_depth_tier or "").strip().lower()
    if tier in ("pro", "premium"):
        return "paid"
    billing = (billing_level or "").strip().lower()
    if billing in ("lite", "pro"):
        return "paid"
    return "free"


def _sun_sign(facts: dict[str, Any] | None) -> str | None:
    if not facts:
        return None
    for p in facts.get("planets") or []:
        if isinstance(p, dict) and str(p.get("id") or "").lower() == "sun":
            sign = p.get("sign")
            return str(sign) if sign else None
    return None


def _angles_pack(facts: dict[str, Any] | None) -> dict[str, Any] | None:
    if not facts or facts.get("mode") != "full":
        return None
    angles = facts.get("angles") if isinstance(facts.get("angles"), dict) else {}
    houses = facts.get("houses") if isinstance(facts.get("houses"), list) else []
    if not angles and not houses:
        return None
    return {"angles": angles, "houses": houses, "mode": "full"}


def project_profile_slots_v0(
    *,
    contract: dict[str, Any] | None = None,
    natal_facts: dict[str, Any] | None = None,
    capability: dict[str, Any] | None = None,
    birth_date: str | None = None,
    birth_time: str | None = None,
    time_unknown: bool = True,
    latitude: float | None = None,
    longitude: float | None = None,
    location_name: str | None = None,
    timezone_name: str | None = None,
    display_name: str | None = None,
    access: AccessTier = "free",
    catalog: dict[str, Any] | None = None,
    name_numerology: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Project current Profile payload into matrix 3.1 slots (gated).

    Legacy field map (temporary Δ — not a new funnel):
      recognition_line / identity_core → identity_summary
      styles → emotional / decision / relationship / work / money / home
      strengths / growth_zones / recurring_patterns → strengths / tensions
      helps / effort_vector → helps (L3)
    """
    cap = capability or resolve_capability(
        birth_date=birth_date,
        birth_time=birth_time,
        time_unknown=time_unknown,
        latitude=latitude,
        longitude=longitude,
        location_name=location_name,
        timezone_name=timezone_name,
        display_name=display_name,
        access=access,
    )
    slots_meta = cap.get("profile_slots") or {}
    data_eligible = set(slots_meta.get("data_eligible") or slots_meta.get("allowed") or [])
    revealed = set(slots_meta.get("revealed") or slots_meta.get("allowed") or [])
    access_gated = set(slots_meta.get("access_gated") or slots_meta.get("gated_l3") or [])
    c = contract if isinstance(contract, dict) else {}
    facts = natal_facts if isinstance(natal_facts, dict) else {}

    sun_from_facts = _sun_sign(facts)
    sun_from_catalog = None
    element_from_catalog = None
    if isinstance(catalog, dict):
        trop = catalog.get("tropical_sign") if isinstance(catalog.get("tropical_sign"), dict) else {}
        sun_from_catalog = trop.get("id") or trop.get("label")
        element_from_catalog = trop.get("element")
        num_core = catalog.get("numerology_core") if isinstance(catalog.get("numerology_core"), dict) else {}
    else:
        num_core = {}

    sun_element_bag = {
        "sun_sign": sun_from_facts or sun_from_catalog,
        "element": c.get("element") or element_from_catalog,
        "life_path": c.get("life_path") if c.get("life_path") is not None else num_core.get("life_path"),
        "birthday_number": c.get("birthday_number")
        if c.get("birthday_number") is not None
        else num_core.get("birthday_number"),
    }

    raw_slots: dict[str, Any] = {
        SLOT_IDENTITY: _clip_text(
            c.get("identity_summary") or c.get("recognition_line") or c.get("identity_core")
        ),
        SLOT_SUN_ELEMENT_NUM: sun_element_bag,
        SLOT_CATALOG: catalog,
        SLOT_NAME_NUMEROLOGY: name_numerology,
        SLOT_NATAL_STRUCTURE: _angles_pack(facts),
        SLOT_EMOTIONAL: _style_field(c, "emotional_style", "emotional"),
        SLOT_DECISION: _style_field(c, "decision_style", "decision"),
        SLOT_RELATIONSHIP: _style_field(c, "relationship_style", "relationship"),
        SLOT_WORK: _style_field(c, "work_and_realization", "work_style", "work", "career_style"),
        SLOT_MONEY: _style_field(c, "money_patterns", "money_style", "money"),
        SLOT_HOME: _style_field(c, "home_and_security", "home_style", "security_style", "home"),
        SLOT_STRENGTHS: _listish(c.get("strengths") or c.get("core_strengths")),
        SLOT_TENSIONS: {
            "growth_zones": _listish(c.get("growth_zones")),
            "internal_tensions": _listish(c.get("internal_tensions") or c.get("recurring_patterns")),
            "blind_spots": _listish(c.get("blind_spots")),
        },
        SLOT_HELPS: _listish(c.get("helps"))
        or _clip_text((c.get("effort_vector_v0") or {}).get("effort_vector") if isinstance(c.get("effort_vector_v0"), dict) else c.get("effort_vector")),
        SLOT_LIMITATIONS: {
            "unavailable_facts": facts.get("unavailable_facts") or cap.get("unavailable_facts") or [],
            "user_messages": cap.get("user_messages") or [],
        },
        SLOT_CTA_TODAY: {"ready": bool(birth_date or facts.get("mode"))},
        SLOT_CTA_DEPTH: {
            "gated_l3": slots_meta.get("gated_l3") or [],
            "access_gated": sorted(access_gated),
            "omitted": slots_meta.get("omitted") or [],
        },
    }

    # Empty bag → null (omit)
    for key, val in list(raw_slots.items()):
        if _is_empty_slot(val):
            raw_slots[key] = None

    # Full interpretation bag (same for Free/Trial) — data eligibility only.
    slots: dict[str, Any] = {}
    omitted: dict[str, str] = {}
    for slot_id, value in raw_slots.items():
        if slot_id not in data_eligible:
            omitted[slot_id] = "data_gate"
            continue
        if value is None:
            omitted[slot_id] = "empty"
            continue
        slots[slot_id] = value

    revealed_slots = {k: v for k, v in slots.items() if k in revealed}
    gated_present = sorted(k for k in slots if k in access_gated)

    return {
        "adapter_version": ADAPTER_VERSION,
        "capability": {
            "resolver_version": cap.get("resolver_version"),
            "mode": cap.get("mode"),
            "access": cap.get("access"),
            "layers": cap.get("layers"),
            "profile_slots": cap.get("profile_slots"),
            "user_messages": cap.get("user_messages"),
            "angles_eligible": cap.get("angles_eligible"),
            "birth_time_unsuitable_for_angles": cap.get("birth_time_unsuitable_for_angles"),
            "has_name": cap.get("has_name"),
            "has_time": cap.get("has_time"),
            "has_place": cap.get("has_place"),
            "time_recorded": cap.get("time_recorded"),
        },
        # Full result projection (persist/read). UI must filter via revealed_slots.
        "slots": slots,
        "revealed_slots": revealed_slots,
        "access_gated_slot_ids": gated_present,
        "omitted_slots": omitted,
        "provenance": {
            "facts_mode": facts.get("mode"),
            "facts_provider": facts.get("provider"),
            "facts_calculation_id": facts.get("calculation_id"),
            "contract_keys": sorted(k for k in c.keys() if c.get(k) not in (None, "", [], {})),
        },
    }


def slot_revealed(capability: dict[str, Any], slot_id: str) -> bool:
    """True when UI may show the slot for this access tier."""
    meta = capability.get("profile_slots") or {}
    revealed = meta.get("revealed") or meta.get("allowed") or []
    return slot_id in revealed


def slot_allowed(capability: dict[str, Any], slot_id: str) -> bool:
    """Alias of slot_revealed (presentation). Data eligibility is separate."""
    return slot_revealed(capability, slot_id)


def _style_field(contract: dict[str, Any], *keys: str) -> Any:
    styles = contract.get("styles") if isinstance(contract.get("styles"), dict) else {}
    for key in keys:
        if contract.get(key) not in (None, "", [], {}):
            return contract.get(key)
        if styles.get(key) not in (None, "", [], {}):
            return styles.get(key)
    return None


def _listish(value: Any) -> list[Any] | None:
    if isinstance(value, list):
        cleaned = [x for x in value if x not in (None, "")]
        return cleaned or None
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return None


def _clip_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _is_empty_slot(value: Any) -> bool:
    if value is None:
        return True
    if value == "" or value == [] or value == {}:
        return True
    if isinstance(value, dict):
        meaningful = [v for v in value.values() if v not in (None, "", [], {})]
        return not meaningful
    return False

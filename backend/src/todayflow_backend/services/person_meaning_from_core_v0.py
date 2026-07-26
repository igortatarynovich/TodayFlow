"""Shared person-meaning excerpts from core_profile after CE PUBLISH_READY.

Prefer profile_contract_v1 / character_engine_v1 over interpretation.life_areas.
"""

from __future__ import annotations

from typing import Any

_AREA_TO_CONTRACT_STYLE = {
    "love": "relationship_style",
    "money": "money_style",
    "decisions": "decision_style",
    "career": "money_style",  # closest stable proxy when no career root
}


def _clip(text: Any, n: int = 280) -> str | None:
    s = " ".join(str(text or "").split()).strip()
    if not s:
        return None
    return s if len(s) <= n else s[: n - 1].rstrip() + "…"


def person_sot_label(core_profile: dict[str, Any] | None) -> str:
    if not isinstance(core_profile, dict):
        return "none"
    ce = core_profile.get("character_engine_v1")
    if isinstance(ce, dict) and str(ce.get("status") or "") == "ready":
        return "character_engine_v1"
    pc = core_profile.get("profile_contract_v1")
    if isinstance(pc, dict):
        gm = pc.get("generation_meta") if isinstance(pc.get("generation_meta"), dict) else {}
        if gm.get("sot") == "character_engine_v1":
            return "character_engine_v1"
        if str(pc.get("identity_core") or "").strip():
            return "profile_contract_v1"
    return "interpretation"


def identity_excerpt_from_core(core_profile: dict[str, Any] | None, *, max_len: int = 280) -> str | None:
    if not isinstance(core_profile, dict):
        return None
    pc = core_profile.get("profile_contract_v1")
    if isinstance(pc, dict):
        for key in ("identity_core", "recognition_line"):
            hit = _clip(pc.get(key), max_len)
            if hit:
                return hit
    ce = core_profile.get("character_engine_v1")
    if isinstance(ce, dict):
        legacy = ce.get("legacy_projections") if isinstance(ce.get("legacy_projections"), dict) else {}
        fields = legacy.get("fields") if isinstance(legacy.get("fields"), dict) else {}
        row = fields.get("identity_core") if isinstance(fields.get("identity_core"), dict) else {}
        hit = _clip(row.get("value"), max_len)
        if hit:
            return hit
        cascade = ce.get("cascade") if isinstance(ce.get("cascade"), dict) else {}
        ic = cascade.get("identity_core") if isinstance(cascade.get("identity_core"), dict) else {}
        hit = _clip(ic.get("surface_text"), max_len)
        if hit:
            return hit
    interp = core_profile.get("interpretation")
    if isinstance(interp, dict):
        return _clip(interp.get("identity"), max_len)
    return None


def sphere_excerpt_from_core(
    core_profile: dict[str, Any] | None,
    area_key: str,
    *,
    max_len: int = 240,
) -> str | None:
    """Resolve a life-area/sphere line without treating life_areas as SoT."""
    if not isinstance(core_profile, dict) or not area_key:
        return None
    pc = core_profile.get("profile_contract_v1")
    if isinstance(pc, dict):
        spheres = pc.get("life_spheres") if isinstance(pc.get("life_spheres"), dict) else {}
        sphere = spheres.get(area_key) if isinstance(spheres.get(area_key), dict) else None
        if sphere:
            for key in ("how", "text", "need"):
                hit = _clip(sphere.get(key), max_len)
                if hit:
                    return hit
        # Alias work ↔ career
        if area_key == "career":
            work = spheres.get("work") if isinstance(spheres.get("work"), dict) else None
            if work:
                for key in ("how", "text", "need"):
                    hit = _clip(work.get(key), max_len)
                    if hit:
                        return hit
        style_key = _AREA_TO_CONTRACT_STYLE.get(area_key)
        if style_key:
            hit = _clip(pc.get(style_key), max_len)
            if hit:
                return hit
    # Legacy fallback only.
    interp = core_profile.get("interpretation")
    if isinstance(interp, dict):
        life_areas = interp.get("life_areas") if isinstance(interp.get("life_areas"), dict) else {}
        return _clip(life_areas.get(area_key), max_len)
    return None


def strengths_from_core(core_profile: dict[str, Any] | None) -> list[str]:
    if not isinstance(core_profile, dict):
        return []
    pc = core_profile.get("profile_contract_v1")
    if isinstance(pc, dict) and isinstance(pc.get("strengths"), list):
        return [str(x).strip() for x in pc["strengths"] if str(x).strip()][:6]
    interp = core_profile.get("interpretation")
    if isinstance(interp, dict) and isinstance(interp.get("strengths"), list):
        return [str(x).strip() for x in interp["strengths"] if str(x).strip()][:6]
    return []


def watchouts_from_core(core_profile: dict[str, Any] | None) -> list[str]:
    if not isinstance(core_profile, dict):
        return []
    pc = core_profile.get("profile_contract_v1")
    if isinstance(pc, dict) and isinstance(pc.get("growth_zones"), list):
        return [str(x).strip() for x in pc["growth_zones"] if str(x).strip()][:4]
    if isinstance(pc, dict) and isinstance(pc.get("recurring_patterns"), list):
        return [str(x).strip() for x in pc["recurring_patterns"] if str(x).strip()][:4]
    interp = core_profile.get("interpretation")
    if isinstance(interp, dict) and isinstance(interp.get("watchouts"), list):
        return [str(x).strip() for x in interp["watchouts"] if str(x).strip()][:4]
    return []

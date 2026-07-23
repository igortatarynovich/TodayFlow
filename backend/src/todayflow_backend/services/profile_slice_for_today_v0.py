"""Profile continuity slice for Today day-story — saved personality, not a new Profile run.

SoT: PRODUCT_GENERATION_CONTRACTS — today requires profile packages; never recompute natal_facts.
"""

from __future__ import annotations

from typing import Any, Mapping


def _clip(value: Any, max_len: int) -> str | None:
    text = str(value or "").strip()
    if not text:
        return None
    if len(text) <= max_len:
        return text
    return text[: max_len - 1].rstrip() + "…"


def build_profile_slice_for_today(core_profile: Mapping[str, Any] | None) -> dict[str, Any]:
    """Thin continuity pack: who the person is + natal mode. Empty when no portrait yet."""
    if not isinstance(core_profile, dict):
        return {}
    contract = core_profile.get("profile_contract_v1")
    contract = contract if isinstance(contract, dict) else {}
    personality = contract.get("personality_v1")
    personality = personality if isinstance(personality, dict) else {}
    astro = core_profile.get("astro") if isinstance(core_profile.get("astro"), dict) else {}
    numerology = core_profile.get("numerology") if isinstance(core_profile.get("numerology"), dict) else {}
    capability = core_profile.get("capability") if isinstance(core_profile.get("capability"), dict) else {}
    matrix = core_profile.get("profile_matrix_v0") if isinstance(core_profile.get("profile_matrix_v0"), dict) else {}
    revealed = matrix.get("revealed_slots") if isinstance(matrix.get("revealed_slots"), dict) else {}

    def pick(*keys: str, limit: int = 520) -> str | None:
        for src in (personality, contract, revealed):
            if not isinstance(src, dict):
                continue
            for key in keys:
                hit = _clip(src.get(key), limit)
                if hit:
                    return hit
        return None

    natal_mode = capability.get("mode") or (matrix.get("provenance") or {}).get("facts_mode")
    sun_bag = revealed.get("sun_element_numerology") if isinstance(revealed.get("sun_element_numerology"), dict) else {}

    slice_out: dict[str, Any] = {
        "source": "profile_slice_for_today_v0",
        "identity_summary": pick("identity_summary", "recognition_line", "identity_core", limit=160),
        "emotional_style": pick("emotional_style"),
        "decision_style": pick("decision_style"),
        "relationship_style": pick("relationship_style"),
        "work_and_realization": pick("work_and_realization", "work_style"),
        "strengths": [],
        "sun_sign": _clip(sun_bag.get("sun_sign") or astro.get("sun_sign"), 40),
        "element": _clip(sun_bag.get("element") or astro.get("sun_element") or contract.get("element"), 40),
        "life_path": sun_bag.get("life_path")
        if sun_bag.get("life_path") is not None
        else numerology.get("life_path") or contract.get("life_path"),
        "natal_mode": natal_mode,
    }
    strengths = personality.get("strengths") or contract.get("strengths") or revealed.get("strengths")
    if isinstance(strengths, list):
        slice_out["strengths"] = [s for s in (_clip(x, 120) for x in strengths) if s][:4]

    # Drop empties
    return {k: v for k, v in slice_out.items() if v not in (None, "", [], {})}

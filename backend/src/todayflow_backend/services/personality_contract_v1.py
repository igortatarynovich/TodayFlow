"""personality Generation Contract — interpret natal_facts into Profile matrix fields.

SoT: docs/PRODUCT_GENERATION_CONTRACTS.md
Does not recompute ASC/houses. Requires validated natal_facts with sun.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any

from todayflow_backend.core.llm_openai_compatible import (
    chat_completion_text,
    get_openai_compatible_client,
    is_llm_chat_configured,
    resolve_default_chat_model,
)
from todayflow_backend.prompts.registry_v1 import get_prompt

logger = logging.getLogger(__name__)

PERSONALITY_CONTRACT = "personality_v1"
PROMPT_ID = "profile.personality.v1"
IDENTITY_SUMMARY_MAX = 120

_STRING_FIELDS = (
    "identity_summary",
    "sun_sign_meaning",
    "element_expression",
    "numerology_core",
    "emotional_style",
    "decision_style",
    "relationship_style",
    "work_and_realization",
    "money_patterns",
    "home_and_security",
    "limitations",
)
_LIST_FIELDS = (
    "strengths",
    "core_strengths",
    "internal_tensions",
    "growth_zones",
    "blind_spots",
    "chart_dominants",
    "important_aspects",
)
_HOUSE_FIELDS = frozenset({"work_and_realization", "money_patterns", "home_and_security"})


def _clip(value: Any, max_len: int) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    if len(text) > max_len:
        text = text[: max_len - 1].rstrip() + "…"
    return text


def _list_str(value: Any, *, limit: int = 6) -> list[str]:
    if not isinstance(value, list):
        return []
    out: list[str] = []
    for item in value:
        s = _clip(item, 220)
        if s:
            out.append(s)
        if len(out) >= limit:
            break
    return out


def _sun_sign(facts: dict[str, Any]) -> str | None:
    for p in facts.get("planets") or []:
        if isinstance(p, dict) and str(p.get("id") or "").lower() == "sun":
            sign = p.get("sign")
            return str(sign).lower() if sign else None
    return None


def calculated_facts_from_natal(facts: dict[str, Any]) -> dict[str, Any]:
    """Thin projection for the personality prompt — never invents structure."""
    planets = [p for p in (facts.get("planets") or []) if isinstance(p, dict)]
    pack: dict[str, Any] = {
        "mode": facts.get("mode"),
        "sun_sign": _sun_sign(facts),
        "planets": planets,
        "aspects": facts.get("aspects") or [],
        "confidence": facts.get("confidence"),
        "calculation_id": facts.get("calculation_id"),
        "provider": facts.get("provider"),
    }
    if facts.get("mode") == "full":
        angles = facts.get("angles") if isinstance(facts.get("angles"), dict) else {}
        if angles.get("ascendant"):
            pack["ascendant"] = angles.get("ascendant")
        if angles.get("mc"):
            pack["mc"] = angles.get("mc")
        houses = facts.get("houses") if isinstance(facts.get("houses"), list) else []
        if houses:
            pack["houses"] = houses
    return pack


def validate_personality(
    raw: dict[str, Any],
    *,
    natal_facts: dict[str, Any],
) -> dict[str, Any]:
    """Normalize + gate house fields when natal mode is not full."""
    mode = str(natal_facts.get("mode") or "date_only")
    out: dict[str, Any] = {
        "contract_version": PERSONALITY_CONTRACT,
        "contract_id": "personality",
    }
    for key in _STRING_FIELDS:
        out[key] = _clip(raw.get(key), IDENTITY_SUMMARY_MAX if key == "identity_summary" else 600)
    for key in _LIST_FIELDS:
        out[key] = _list_str(raw.get(key))

    if mode != "full":
        for key in _HOUSE_FIELDS:
            out[key] = None

    claims_in = raw.get("claims") if isinstance(raw.get("claims"), list) else []
    claims: list[dict[str, Any]] = []
    for item in claims_in[:24]:
        if not isinstance(item, dict):
            continue
        field = _clip(item.get("field"), 64)
        claim = _clip(item.get("claim"), 400)
        if not field or not claim:
            continue
        src = item.get("source_fact_ids")
        src_ids = [str(x) for x in src if x] if isinstance(src, list) else []
        conf = str(item.get("confidence") or "medium").lower()
        if conf not in ("high", "medium", "low"):
            conf = "medium"
        avail = str(item.get("availability") or "available").lower()
        if avail not in ("available", "partial", "unavailable"):
            avail = "available"
        claims.append(
            {
                "field": field,
                "claim": claim,
                "source_fact_ids": src_ids[:8],
                "confidence": conf,
                "availability": avail,
            }
        )
    out["claims"] = claims
    out["natal_mode"] = mode
    out["natal_calculation_id"] = natal_facts.get("calculation_id")
    return out


def personality_has_minimum(personality: dict[str, Any]) -> bool:
    """Ready interpretation needs recognition + at least one style or strength."""
    if not _clip(personality.get("identity_summary"), IDENTITY_SUMMARY_MAX):
        return False
    if any(_clip(personality.get(k), 40) for k in ("emotional_style", "decision_style", "relationship_style")):
        return True
    if _list_str(personality.get("strengths")) or _list_str(personality.get("core_strengths")):
        return True
    return False


def personality_to_profile_contract(personality: dict[str, Any], *, generation_meta: dict[str, Any] | None = None) -> dict[str, Any]:
    """Map personality fields onto profile_contract_v1 keys the matrix adapter already reads."""
    identity = personality.get("identity_summary")
    return {
        "contract_version": "profile_contract_v1",
        "status": "ready",
        "recognition_line": identity,
        "identity_core": identity,
        "identity_summary": identity,
        "sun_sign_meaning": personality.get("sun_sign_meaning"),
        "element_expression": personality.get("element_expression"),
        "numerology_core_text": personality.get("numerology_core"),
        "emotional_style": personality.get("emotional_style"),
        "decision_style": personality.get("decision_style"),
        "relationship_style": personality.get("relationship_style"),
        "work_style": personality.get("work_and_realization"),
        "work_and_realization": personality.get("work_and_realization"),
        "money_style": personality.get("money_patterns"),
        "money_patterns": personality.get("money_patterns"),
        "home_style": personality.get("home_and_security"),
        "home_and_security": personality.get("home_and_security"),
        "strengths": personality.get("strengths") or [],
        "core_strengths": personality.get("core_strengths") or [],
        "growth_zones": personality.get("growth_zones") or [],
        "internal_tensions": personality.get("internal_tensions") or [],
        "blind_spots": personality.get("blind_spots") or [],
        "chart_dominants": personality.get("chart_dominants") or [],
        "important_aspects": personality.get("important_aspects") or [],
        "limitations_text": personality.get("limitations"),
        "personality_v1": personality,
        "generation_meta": {
            **(generation_meta or {}),
            "path": "personality_v1",
            "prompt_id": PROMPT_ID,
            "contract_id": "personality",
        },
    }


def _parse_json_object(raw: str) -> dict[str, Any] | None:
    text = (raw or "").strip()
    if not text:
        return None
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if fence:
        text = fence.group(1).strip()
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start < 0 or end <= start:
            return None
        try:
            parsed = json.loads(text[start : end + 1])
        except json.JSONDecodeError:
            return None
    return parsed if isinstance(parsed, dict) else None


def generate_personality(
    *,
    natal_facts: dict[str, Any],
    available_input: dict[str, Any] | None = None,
    numerology: dict[str, Any] | None = None,
    catalog: dict[str, Any] | None = None,
    locale: str = "ru",
) -> dict[str, Any] | None:
    """Run personality LLM. None when LLM missing / invalid / below minimum."""
    if not isinstance(natal_facts, dict) or not _sun_sign(natal_facts):
        logger.info("personality: skip — natal_facts without sun")
        return None
    if not is_llm_chat_configured():
        logger.info("personality: LLM not configured — skip (caller may use funnel/fallback)")
        return None

    calculated = calculated_facts_from_natal(natal_facts)
    system, version = get_prompt(PROMPT_ID, locale=locale)
    user_payload = {
        "contract_id": "personality",
        "prompt_version": version,
        "available_input": available_input or {},
        "calculated_facts": calculated,
        "unavailable_facts": natal_facts.get("unavailable_facts") or [],
        "numerology_core": {
            "life_path": (numerology or {}).get("life_path"),
            "birthday_number": (numerology or {}).get("birthday_number"),
        }
        if numerology
        else None,
        "catalog": catalog,
    }
    client = get_openai_compatible_client(operation="background")
    model = resolve_default_chat_model()
    raw = chat_completion_text(
        client,
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": json.dumps(user_payload, ensure_ascii=False)},
        ],
        temperature=0.55,
        max_tokens=2800,
        json_object=True,
    )
    parsed = _parse_json_object(raw or "")
    if not parsed:
        logger.warning("personality: empty/invalid LLM JSON")
        return None
    personality = validate_personality(parsed, natal_facts=natal_facts)
    personality["prompt_id"] = PROMPT_ID
    personality["prompt_version"] = version
    if not personality_has_minimum(personality):
        logger.warning("personality: below minimum fields")
        return None
    return personality

"""Natal Decode Depth v0 — opt-in chart decode over fixed Character Engine Identity Core.

Canon: docs/profile/PROFILE_NATAL_DECODE_DEPTH_V1.md

Rules:
- Explicit request only (API POST). Never on core-profile GET / publish.
- Does NOT write character_engine_v1 or overwrite portrait Snapshot.
- Not a personality SoT for Today / Compat / Tarot.
"""

from __future__ import annotations

import hashlib
import json
import logging
import re
from typing import Any

from sqlalchemy.orm import Session

from todayflow_backend.core.llm_openai_compatible import (
    chat_completion_text,
    get_openai_compatible_client,
    is_llm_chat_configured,
    resolve_default_chat_model,
)
from todayflow_backend.prompts.registry_v1 import get_prompt

logger = logging.getLogger(__name__)

DECODE_VERSION = "natal_decode_depth_v0"
PROMPT_ID = "profile.natal_decode_depth.v1"
LAYER_KIND = "natal_decode_depth"
_ALLOWED_SECTION_IDS = frozenset({"mind", "feelings", "will", "growth", "presence", "structure"})
_MAX_SECTIONS = 5
_MAX_HOOKS = 4
_MAX_TEXT = 480


def _clip(value: Any, limit: int = _MAX_TEXT) -> str:
    text = " ".join(str(value or "").split()).strip()
    if not text:
        return ""
    if len(text) > limit:
        return text[: limit - 1].rstrip() + "…"
    return text


def _stage2_from_payload(payload: dict[str, Any] | None) -> dict[str, Any] | None:
    if not isinstance(payload, dict):
        return None
    diagnostics = payload.get("diagnostics") if isinstance(payload.get("diagnostics"), dict) else {}
    art = diagnostics.get("character_engine_stage2")
    if isinstance(art, dict):
        stage2 = art.get("stage2") if isinstance(art.get("stage2"), dict) else None
        if isinstance(stage2, dict):
            return stage2
        if art.get("identity_core"):
            return art
    ce = payload.get("character_engine_v1") if isinstance(payload.get("character_engine_v1"), dict) else {}
    identity = ce.get("identity_core") if isinstance(ce.get("identity_core"), dict) else None
    if isinstance(identity, dict) and identity.get("surface_text"):
        return {"status": "grounded", "identity_core": identity}
    return None


def extract_identity_core_for_decode(payload: dict[str, Any] | None) -> dict[str, Any] | None:
    """Return {thesis_key, surface_text} when CE Identity Core is grounded."""
    stage2 = _stage2_from_payload(payload)
    if not isinstance(stage2, dict):
        return None
    status = str(stage2.get("status") or "").strip()
    core = stage2.get("identity_core") if isinstance(stage2.get("identity_core"), dict) else None
    if not isinstance(core, dict):
        return None
    # CE nest path may omit stage2.status — treat present surface+thesis as grounded.
    if status and status != "grounded":
        return None
    surface = _clip(core.get("surface_text"), 280)
    thesis = str(core.get("thesis_key") or "").strip()
    if not surface or not thesis:
        return None
    return {
        "thesis_key": thesis,
        "surface_text": surface,
        "primary_claim_id": core.get("primary_claim_id"),
    }


def extract_primary_tension_surface(payload: dict[str, Any] | None) -> str | None:
    if not isinstance(payload, dict):
        return None
    diagnostics = payload.get("diagnostics") if isinstance(payload.get("diagnostics"), dict) else {}
    stage3 = diagnostics.get("character_engine_stage3")
    if not isinstance(stage3, dict):
        return None
    eng = stage3.get("internal_engine") if isinstance(stage3.get("internal_engine"), dict) else stage3
    pt = eng.get("primary_tension") if isinstance(eng, dict) else None
    if isinstance(pt, dict):
        text = _clip(pt.get("surface_text"), 280)
        return text or None
    return None


def build_offer_payload(
    *,
    identity_core: dict[str, Any] | None,
    natal_available: bool,
) -> dict[str, Any]:
    """GET-safe offer — no LLM."""
    if not identity_core:
        return {
            "layer": LAYER_KIND,
            "version": DECODE_VERSION,
            "access": "blocked",
            "reason": "identity_core_required",
            "cta": "Сначала нужен устойчивый портрет характера — расшифровка карты опирается на него.",
            "can_generate": False,
        }
    if not natal_available:
        return {
            "layer": LAYER_KIND,
            "version": DECODE_VERSION,
            "access": "blocked",
            "reason": "natal_facts_required",
            "cta": "Время и место рождения открывают структуру карты для расшифровки.",
            "can_generate": False,
            "identity_thesis": identity_core.get("thesis_key"),
        }
    return {
        "layer": LAYER_KIND,
        "version": DECODE_VERSION,
        "access": "offer",
        "reason": None,
        "cta": "Открыть расшифровку натальной карты — как структура карты объясняет твоё ядро.",
        "can_generate": True,
        "identity_thesis": identity_core.get("thesis_key"),
        "note": "Генерируется только по явному запросу. Не второй портрет.",
    }


def _compact_natal_pack(natal_summary: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(natal_summary, dict):
        return {}
    pack: dict[str, Any] = {"available": bool(natal_summary.get("available", True))}
    angles = natal_summary.get("angles") if isinstance(natal_summary.get("angles"), dict) else {}
    if angles:
        pack["angles"] = {
            k: angles.get(k)
            for k in ("ascendant_sign", "midheaven_sign", "ascendant", "midheaven")
            if angles.get(k) is not None
        }
    planets: list[dict[str, Any]] = []
    for bucket in ("luminaries", "personal_planets", "social_planets", "outer_planets"):
        rows = natal_summary.get(bucket) if isinstance(natal_summary.get(bucket), list) else []
        for row in rows:
            if not isinstance(row, dict):
                continue
            planets.append(
                {
                    "name": row.get("name") or row.get("body"),
                    "sign": row.get("sign"),
                    "house": row.get("house"),
                    "degree": row.get("degree"),
                    "retrograde": row.get("retrograde"),
                }
            )
    if planets:
        pack["planets"] = planets[:14]
    houses = natal_summary.get("houses")
    if isinstance(houses, list):
        pack["houses"] = [
            {"house": h.get("house") if isinstance(h, dict) else None, "sign": h.get("sign") if isinstance(h, dict) else h}
            for h in houses[:12]
            if h is not None
        ]
    return pack


def _fingerprint(identity_core: dict[str, Any], natal_pack: dict[str, Any]) -> str:
    raw = json.dumps(
        {
            "thesis": identity_core.get("thesis_key"),
            "surface": identity_core.get("surface_text"),
            "natal": natal_pack,
        },
        ensure_ascii=False,
        sort_keys=True,
        default=str,
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]


def _parse_decode_json(raw: str) -> dict[str, Any] | None:
    text = (raw or "").strip()
    if not text:
        return None
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return None
    return parsed if isinstance(parsed, dict) else None


def _normalize_decode(
    parsed: dict[str, Any],
    *,
    identity_core: dict[str, Any],
    fingerprint: str,
) -> dict[str, Any]:
    status = str(parsed.get("status") or "grounded").strip()
    if status not in {"grounded", "insufficient_input"}:
        status = "grounded"
    sections_in = parsed.get("sections") if isinstance(parsed.get("sections"), list) else []
    sections: list[dict[str, str]] = []
    for item in sections_in:
        if not isinstance(item, dict):
            continue
        sid = str(item.get("id") or "").strip()
        if sid not in _ALLOWED_SECTION_IDS:
            sid = "structure"
        thesis = _clip(item.get("thesis"))
        because = _clip(item.get("because_core"))
        title = _clip(item.get("title"), 80)
        if not thesis or not because:
            continue
        sections.append(
            {
                "id": sid,
                "title": title or sid,
                "thesis": thesis,
                "because_core": because,
            }
        )
        if len(sections) >= _MAX_SECTIONS:
            break
    hooks_in = parsed.get("day_hooks") if isinstance(parsed.get("day_hooks"), list) else []
    hooks = [_clip(h, 180) for h in hooks_in if _clip(h, 180)]
    hooks = hooks[:_MAX_HOOKS]
    if status == "insufficient_input" or not sections:
        return {
            "layer": LAYER_KIND,
            "version": DECODE_VERSION,
            "status": "insufficient_input",
            "identity_core": {
                "thesis_key": identity_core["thesis_key"],
                "surface_text": identity_core["surface_text"],
            },
            "fingerprint": fingerprint,
            "pattern_thesis": None,
            "sections": [],
            "day_hooks": [],
            "limits": _clip(parsed.get("limits"), 240) or None,
            "sot_role": "depth_projection",
            "writes_character_engine": False,
        }
    return {
        "layer": LAYER_KIND,
        "version": DECODE_VERSION,
        "status": "grounded",
        "identity_core": {
            "thesis_key": identity_core["thesis_key"],
            "surface_text": identity_core["surface_text"],
        },
        "fingerprint": fingerprint,
        "pattern_thesis": _clip(parsed.get("pattern_thesis"), 220) or None,
        "sections": sections,
        "day_hooks": hooks,
        "limits": _clip(parsed.get("limits"), 240) or None,
        "sot_role": "depth_projection",
        "writes_character_engine": False,
    }


def generate_natal_decode_depth_v0(
    db: Session,
    *,
    user_id: int,
    core_profile_payload: dict[str, Any] | None,
    natal_summary: dict[str, Any] | None = None,
    locale: str = "ru",
    force_refresh: bool = False,
) -> dict[str, Any]:
    """Generate decode on explicit request. Never mutates CE Snapshot."""
    del force_refresh  # reserved: reuse cache later via generation_logs
    identity = extract_identity_core_for_decode(core_profile_payload)
    natal_pack = _compact_natal_pack(
        natal_summary
        if isinstance(natal_summary, dict)
        else (
            (core_profile_payload or {}).get("natal_summary")
            if isinstance(core_profile_payload, dict)
            else None
        )
    )
    natal_available = bool(natal_pack.get("planets") or natal_pack.get("angles"))

    if not identity:
        return {
            "layer": LAYER_KIND,
            "version": DECODE_VERSION,
            "status": "blocked",
            "reason": "identity_core_required",
            "cta": "Сначала нужен устойчивый портрет характера — расшифровка карты опирается на него.",
            "sot_role": "depth_projection",
            "writes_character_engine": False,
        }
    if not natal_available:
        return {
            "layer": LAYER_KIND,
            "version": DECODE_VERSION,
            "status": "blocked",
            "reason": "natal_facts_required",
            "cta": "Время и место рождения открывают структуру карты для расшифровки.",
            "identity_core": {
                "thesis_key": identity["thesis_key"],
                "surface_text": identity["surface_text"],
            },
            "sot_role": "depth_projection",
            "writes_character_engine": False,
        }

    fingerprint = _fingerprint(identity, natal_pack)
    tension = extract_primary_tension_surface(core_profile_payload)

    if not is_llm_chat_configured():
        return {
            "layer": LAYER_KIND,
            "version": DECODE_VERSION,
            "status": "unavailable",
            "reason": "llm_unconfigured",
            "identity_core": {
                "thesis_key": identity["thesis_key"],
                "surface_text": identity["surface_text"],
            },
            "fingerprint": fingerprint,
            "sot_role": "depth_projection",
            "writes_character_engine": False,
        }

    system, prompt_version = get_prompt(PROMPT_ID, locale=locale)
    from todayflow_backend.services.llm_practitioner_persona_v1 import with_practitioner_persona

    system = with_practitioner_persona(system, locale=locale)
    user_msg = (
        "Собери Natal Decode Depth. Identity Core фиксирован — не переписывай.\n"
        f"Данные:\n{json.dumps({'identity_core': identity, 'primary_tension_surface': tension, 'natal_pack': natal_pack}, ensure_ascii=False)}"
    )

    try:
        client = get_openai_compatible_client()
        raw = chat_completion_text(
            client,
            model=resolve_default_chat_model(),
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user_msg},
            ],
            temperature=0.4,
            max_tokens=1400,
            json_object=True,
        )
    except Exception:
        logger.exception("natal_decode_depth LLM failed user_id=%s", user_id)
        return {
            "layer": LAYER_KIND,
            "version": DECODE_VERSION,
            "status": "unavailable",
            "reason": "llm_failed",
            "identity_core": {
                "thesis_key": identity["thesis_key"],
                "surface_text": identity["surface_text"],
            },
            "fingerprint": fingerprint,
            "sot_role": "depth_projection",
            "writes_character_engine": False,
        }

    parsed = _parse_decode_json(raw or "")
    if not parsed:
        return {
            "layer": LAYER_KIND,
            "version": DECODE_VERSION,
            "status": "unavailable",
            "reason": "parse_failed",
            "identity_core": {
                "thesis_key": identity["thesis_key"],
                "surface_text": identity["surface_text"],
            },
            "fingerprint": fingerprint,
            "sot_role": "depth_projection",
            "writes_character_engine": False,
        }

    result = _normalize_decode(parsed, identity_core=identity, fingerprint=fingerprint)
    result["prompt_id"] = PROMPT_ID
    result["prompt_version"] = prompt_version

    try:
        from todayflow_backend.services.learning import get_learning_service

        learning = get_learning_service()
        learning.log_generation(
            db,
            module="profile",
            surface=LAYER_KIND,
            user_id=user_id,
            model=resolve_default_chat_model(),
            locale=locale,
            input_payload={
                "fingerprint": fingerprint,
                "thesis_key": identity["thesis_key"],
                "prompt_id": PROMPT_ID,
                "prompt_version": prompt_version,
                "writes_character_engine": False,
            },
            normalized_response={
                "status": result.get("status"),
                "pattern_thesis": result.get("pattern_thesis"),
                "section_count": len(result.get("sections") or []),
            },
            status="success" if result.get("status") == "grounded" else "partial",
        )
    except Exception:
        logger.debug("natal_decode_depth log_generation failed", exc_info=True)

    # Explicit invariant for callers / tests.
    result["writes_character_engine"] = False
    result["sot_role"] = "depth_projection"
    return result

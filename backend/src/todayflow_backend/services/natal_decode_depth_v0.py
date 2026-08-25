"""Natal Decode Depth v0 — one-shot chart story over fixed Character Engine Identity Core.

Canon: docs/profile/PROFILE_NATAL_DECODE_DEPTH_V1.md

Rules:
- First explicit POST generates; thereafter GET/POST serve persisted artifact for fingerprint.
- Never on core-profile GET / publish auto-path.
- Does NOT write character_engine_v1 as personality SoT.
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
    llm_call_context,
    resolve_complex_chat_model,
)
from todayflow_backend.db import models
from todayflow_backend.prompts.registry_v1 import get_prompt
from todayflow_backend.services.prose_clip_v1 import clip_prose

logger = logging.getLogger(__name__)

DECODE_VERSION = "natal_decode_depth_v0.3"
PROMPT_ID = "profile.natal_decode_depth.v1"
LAYER_KIND = "natal_decode_depth"
_ALLOWED_SECTION_IDS = frozenset({"mind", "feelings", "will", "growth", "presence", "structure"})
_MAX_SECTIONS = 5
_MAX_HOOKS = 4
_MAX_TEXT = 900


def _clip(value: Any, limit: int = _MAX_TEXT) -> str:
    return clip_prose(" ".join(str(value or "").split()).strip(), limit)


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
    cascade = ce.get("cascade") if isinstance(ce.get("cascade"), dict) else {}
    identity = cascade.get("identity_core") if isinstance(cascade.get("identity_core"), dict) else None
    if isinstance(identity, dict) and identity.get("surface_text"):
        return {"status": "grounded", "identity_core": identity}
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
    if status and status != "grounded":
        return None
    surface = _clip(core.get("surface_text"), 900)
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
    if isinstance(stage3, dict):
        nested = stage3.get("stage3") if isinstance(stage3.get("stage3"), dict) else stage3
        pt = nested.get("primary_tension") if isinstance(nested, dict) else None
        if isinstance(pt, dict):
            text = _clip(pt.get("surface_text"), 400)
            if text:
                return text
    ce = payload.get("character_engine_v1") if isinstance(payload.get("character_engine_v1"), dict) else {}
    cascade = ce.get("cascade") if isinstance(ce.get("cascade"), dict) else {}
    pt = cascade.get("primary_tension") if isinstance(cascade.get("primary_tension"), dict) else None
    if isinstance(pt, dict):
        text = _clip(pt.get("surface_text"), 400)
        return text or None
    return None


def _compact_numerology_pack(payload: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(payload, dict):
        return {}
    num = payload.get("numerology") if isinstance(payload.get("numerology"), dict) else {}
    pack: dict[str, Any] = {}
    for key in (
        "life_path",
        "expression",
        "soul_urge",
        "personality",
        "birthday",
        "maturity",
        "life_path_number",
        "expression_number",
    ):
        if num.get(key) is not None:
            pack[key] = num.get(key)
    # Flatten common nested shapes
    for bucket in ("numbers", "core", "summary"):
        nested = num.get(bucket) if isinstance(num.get(bucket), dict) else None
        if not nested:
            continue
        for k, v in nested.items():
            if v is not None and k not in pack:
                pack[k] = v
    return pack


def build_offer_payload(
    *,
    identity_core: dict[str, Any] | None,
    natal_available: bool,
    cached: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """GET-safe: ready artifact when cached, else one-shot offer — no LLM."""
    if isinstance(cached, dict) and str(cached.get("status") or "") == "grounded":
        out = dict(cached)
        persisted = str(out.get("version") or "").strip()
        out.update(
            {
                "layer": LAYER_KIND,
                "version": persisted or DECODE_VERSION,
                "access": "ready",
                "can_generate": False,
                "reason": None,
                "cta": None,
                "note": "Карта уже расшифрована — это готовая история, не кнопка «ещё раз».",
            }
        )
        return out
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
        "cta": "Открыть расшифровку натальной карты — целостная история из планет, углов и чисел.",
        "can_generate": True,
        "identity_thesis": identity_core.get("thesis_key"),
        "note": "Собирается один раз. Повторно не генерируется, пока не изменятся данные карты.",
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
            {
                "house": h.get("house") if isinstance(h, dict) else None,
                "sign": h.get("sign") if isinstance(h, dict) else h,
            }
            for h in houses[:12]
            if h is not None
        ]
    return pack


def _fingerprint(
    identity_core: dict[str, Any],
    natal_pack: dict[str, Any],
    numerology_pack: dict[str, Any] | None = None,
) -> str:
    raw = json.dumps(
        {
            "thesis": identity_core.get("thesis_key"),
            "surface": identity_core.get("surface_text"),
            "natal": natal_pack,
            "numerology": numerology_pack or {},
            "decode_version": DECODE_VERSION,
        },
        ensure_ascii=False,
        sort_keys=True,
        default=str,
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]


def load_cached_natal_decode(
    db: Session,
    *,
    user_id: int,
    fingerprint: str,
) -> dict[str, Any] | None:
    """Return grounded decode for fingerprint from generation_logs, if any."""
    rows = (
        db.query(models.GenerationLog)
        .filter(
            models.GenerationLog.user_id == int(user_id),
            models.GenerationLog.module == "profile",
            models.GenerationLog.surface == LAYER_KIND,
            models.GenerationLog.status == "success",
        )
        .order_by(models.GenerationLog.id.desc())
        .limit(20)
        .all()
    )
    for row in rows:
        inp = row.input_payload if isinstance(row.input_payload, dict) else {}
        if str(inp.get("fingerprint") or "") != fingerprint:
            continue
        body = row.normalized_response if isinstance(row.normalized_response, dict) else None
        if not body:
            continue
        if str(body.get("status") or "") != "grounded":
            continue
        sections = body.get("sections")
        if not isinstance(sections, list) or not sections:
            continue
        return dict(body)
    return None


def persisted_decode_version(
    body: dict[str, Any] | None,
    input_payload: dict[str, Any] | None = None,
) -> str:
    """Stored artifact version. Does not stamp the live DECODE_VERSION."""
    if isinstance(body, dict):
        stored = str(body.get("version") or "").strip()
        if stored:
            return stored
    if isinstance(input_payload, dict):
        return str(input_payload.get("decode_version") or "").strip()
    return ""


def decode_cache_state(
    body: dict[str, Any] | None,
    input_payload: dict[str, Any] | None = None,
) -> str:
    """current · stale · invalid — ops inventory only. Not a GET rebuild signal."""
    if not isinstance(body, dict):
        return "invalid"
    if str(body.get("status") or "") != "grounded":
        return "invalid"
    sections = body.get("sections")
    if not isinstance(sections, list) or not sections:
        return "invalid"
    if persisted_decode_version(body, input_payload) == DECODE_VERSION:
        return "current"
    return "stale"


def list_latest_natal_decode_by_user(db: Session) -> list[dict[str, Any]]:
    """Latest successful natal-decode log per user (inventory). GET still fingerprints."""
    rows = (
        db.query(models.GenerationLog)
        .filter(
            models.GenerationLog.module == "profile",
            models.GenerationLog.surface == LAYER_KIND,
            models.GenerationLog.status == "success",
        )
        .order_by(models.GenerationLog.id.desc())
        .all()
    )
    latest: dict[int, models.GenerationLog] = {}
    for row in rows:
        uid = int(row.user_id or 0)
        if uid and uid not in latest:
            latest[uid] = row
    out: list[dict[str, Any]] = []
    for uid, row in sorted(latest.items()):
        inp = row.input_payload if isinstance(row.input_payload, dict) else {}
        body = row.normalized_response if isinstance(row.normalized_response, dict) else {}
        identity = body.get("identity_core") if isinstance(body.get("identity_core"), dict) else {}
        out.append(
            {
                "user_id": uid,
                "gen_id": int(row.id),
                "state": decode_cache_state(body, inp),
                "body_version": persisted_decode_version(body, inp),
                "prompt_version": str(inp.get("prompt_version") or ""),
                "status": str(body.get("status") or ""),
                "thesis_key": str(identity.get("thesis_key") or ""),
                "writes_character_engine": bool(body.get("writes_character_engine")),
                "sections": len(body.get("sections") or []) if isinstance(body.get("sections"), list) else 0,
            }
        )
    return out


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
            "limits": _clip(parsed.get("limits"), 360) or None,
            "sot_role": "depth_projection",
            "writes_character_engine": False,
            "access": "insufficient",
            "can_generate": False,
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
        "pattern_thesis": _clip(parsed.get("pattern_thesis"), 360) or None,
        "sections": sections,
        "day_hooks": hooks,
        "limits": _clip(parsed.get("limits"), 360) or None,
        "sot_role": "depth_projection",
        "writes_character_engine": False,
        "access": "ready",
        "can_generate": False,
    }


def _inputs_for_payload(
    core_profile_payload: dict[str, Any] | None,
    natal_summary: dict[str, Any] | None,
) -> tuple[dict[str, Any] | None, dict[str, Any], dict[str, Any], bool, str | None]:
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
    numerology_pack = _compact_numerology_pack(core_profile_payload)
    natal_available = bool(natal_pack.get("planets") or natal_pack.get("angles"))
    fingerprint = None
    if identity:
        fingerprint = _fingerprint(identity, natal_pack, numerology_pack)
    return identity, natal_pack, numerology_pack, natal_available, fingerprint


def resolve_natal_decode_get(
    db: Session,
    *,
    user_id: int,
    core_profile_payload: dict[str, Any] | None,
    natal_summary: dict[str, Any] | None = None,
) -> dict[str, Any]:
    identity, natal_pack, numerology_pack, natal_available, fingerprint = _inputs_for_payload(
        core_profile_payload, natal_summary
    )
    cached = None
    if identity and fingerprint:
        cached = load_cached_natal_decode(db, user_id=user_id, fingerprint=fingerprint)
    return build_offer_payload(
        identity_core=identity,
        natal_available=natal_available,
        cached=cached,
    )


def _astro_profile_id_from_payload(payload: dict[str, Any] | None) -> int | None:
    if not isinstance(payload, dict):
        return None
    profiles = payload.get("profiles") if isinstance(payload.get("profiles"), dict) else {}
    raw = profiles.get("selected_profile_id") or profiles.get("primary_profile_id")
    if raw is None:
        return None
    try:
        return int(raw)
    except (TypeError, ValueError):
        return None


def _attach_profile_il4_pack(
    db: Session,
    *,
    core_profile_payload: dict[str, Any] | None,
    natal_chart: Any | None = None,
) -> dict[str, Any] | None:
    """Attach IL-4 via gateway only. Missing geometry → None (previous decode path)."""
    from todayflow_backend.services.il4_surface_attach_v1 import (
        attach_from_profile_input,
        attach_il4_expression_pack,
    )

    if natal_chart is not None:
        pack = attach_il4_expression_pack(surface="profile", natal=natal_chart)
        if pack is not None:
            return pack
        if isinstance(natal_chart, dict):
            pack = attach_from_profile_input(natal_chart, surface="profile")
            if pack is not None:
                return pack
    aid = _astro_profile_id_from_payload(core_profile_payload)
    if aid is None:
        return None
    from todayflow_backend.services.natal_chart_cache import get_natal_chart_cache_service

    cached = get_natal_chart_cache_service(db).get_cached_natal_chart(aid)
    if cached is None:
        return None
    return attach_il4_expression_pack(surface="profile", natal=cached)


def generate_natal_decode_depth_v0(
    db: Session,
    *,
    user_id: int,
    core_profile_payload: dict[str, Any] | None,
    natal_summary: dict[str, Any] | None = None,
    locale: str = "ru",
    force_refresh: bool = False,
    natal_chart: Any | None = None,
    ops_force: bool = False,
) -> dict[str, Any]:
    """Generate once per fingerprint. Client force_refresh is ignored. ops_force is ops one-shot only."""
    # Product rule: not a spam button. Client cannot force re-LLM.
    del force_refresh

    identity, natal_pack, numerology_pack, natal_available, fingerprint = _inputs_for_payload(
        core_profile_payload, natal_summary
    )
    tension = extract_primary_tension_surface(core_profile_payload)

    if not identity:
        return {
            "layer": LAYER_KIND,
            "version": DECODE_VERSION,
            "status": "blocked",
            "reason": "identity_core_required",
            "cta": "Сначала нужен устойчивый портрет характера — расшифровка карты опирается на него.",
            "sot_role": "depth_projection",
            "writes_character_engine": False,
            "can_generate": False,
        }
    if not natal_available or not fingerprint:
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
            "can_generate": False,
        }

    cached = load_cached_natal_decode(db, user_id=user_id, fingerprint=fingerprint)
    if cached and not ops_force:
        out = dict(cached)
        out["access"] = "ready"
        out["can_generate"] = False
        out["writes_character_engine"] = False
        out["sot_role"] = "depth_projection"
        return out

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
            "can_generate": True,
        }

    system, prompt_version = get_prompt(PROMPT_ID, locale=locale)
    from todayflow_backend.services.llm_practitioner_persona_v1 import with_practitioner_persona
    from todayflow_backend.services.il4_editorial_consume_v1 import (
        augment_system_prompt,
        pack_present,
        protected_block,
        reject_invalid_output,
    )
    from todayflow_backend.services.profile_meaning_polish_v1 import (
        augment_decode_system,
        fill_empty_decode_theses,
        reject_invalid_decode,
    )

    il4_pack = _attach_profile_il4_pack(
        db, core_profile_payload=core_profile_payload, natal_chart=natal_chart
    )
    system = with_practitioner_persona(system, locale=locale)
    system = augment_system_prompt(system, il4_pack, locale=locale)
    system = augment_decode_system(system, il4_pack, locale=locale)
    meaning_prefix = protected_block(il4_pack, locale=locale) if pack_present(il4_pack) else ""
    user_payload = {
        "identity_core": identity,
        "primary_tension_surface": tension,
        "natal_pack": natal_pack,
        "numerology_pack": numerology_pack,
    }
    user_msg = (
        f"{meaning_prefix}"
        "Собери Natal Decode Depth — целостную историю человека. "
        "Identity Core фиксирован — не переписывай.\n"
        f"Данные:\n{json.dumps(user_payload, ensure_ascii=False)}"
    )

    try:
        model = resolve_complex_chat_model()
        client = get_openai_compatible_client(model=model)
        with llm_call_context(
            feature="natal.decode",
            user_id=user_id,
            ensure_operation=True,
            operation="natal.decode",
        ):
            raw = chat_completion_text(
                client,
                model=model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user_msg},
                ],
                temperature=0.45,
                max_tokens=2800,
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
            "can_generate": True,
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
            "can_generate": True,
        }

    consume_reject = reject_invalid_output(parsed, il4_pack)
    if consume_reject:
        return {
            "layer": LAYER_KIND,
            "version": DECODE_VERSION,
            "status": "unavailable",
            "reason": f"il4_consume:{consume_reject}",
            "identity_core": {
                "thesis_key": identity["thesis_key"],
                "surface_text": identity["surface_text"],
            },
            "fingerprint": fingerprint,
            "sot_role": "depth_projection",
            "writes_character_engine": False,
            "can_generate": True,
        }
    parsed = fill_empty_decode_theses(parsed, il4_pack)
    polish_reject = reject_invalid_decode(parsed, il4_pack)
    if polish_reject:
        return {
            "layer": LAYER_KIND,
            "version": DECODE_VERSION,
            "status": "unavailable",
            "reason": f"profile_polish:{polish_reject}",
            "identity_core": {
                "thesis_key": identity["thesis_key"],
                "surface_text": identity["surface_text"],
            },
            "fingerprint": fingerprint,
            "sot_role": "depth_projection",
            "writes_character_engine": False,
            "can_generate": True,
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
            model=resolve_complex_chat_model(),
            locale=locale,
            input_payload={
                "fingerprint": fingerprint,
                "thesis_key": identity["thesis_key"],
                "prompt_id": PROMPT_ID,
                "prompt_version": prompt_version,
                "writes_character_engine": False,
                "decode_version": DECODE_VERSION,
                "ops_force": bool(ops_force),
            },
            normalized_response=result,
            status="success" if result.get("status") == "grounded" else "partial",
        )
    except Exception:
        logger.debug("natal_decode_depth log_generation failed", exc_info=True)

    result["writes_character_engine"] = False
    result["sot_role"] = "depth_projection"
    return result

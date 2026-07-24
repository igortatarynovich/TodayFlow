"""Profile portrait funnel (identity → styles → patterns? → spheres synthesis).

Shared normalized input for LLM steps. Patterns gated by longitudinal eligibility.
Spheres: profile.spheres.synthesis.v1 on prepared cues (natal-presence gate),
independent of patterns outcome. Fail/omit — never projector phrase tables as copy.
Legacy profile.spheres.v1 is not called. Global ready still requires full contract elsewhere.
"""

from __future__ import annotations

import json
import logging
import re
from time import perf_counter
from typing import Any

from todayflow_backend.core.config import settings
from todayflow_backend.core.llm_openai_compatible import (
    chat_completion_plain,
    get_openai_compatible_client,
    is_llm_chat_configured,
    resolve_default_chat_model,
)
from todayflow_backend.prompts.registry_v1 import get_prompt
from todayflow_backend.services.llm_quality_policy_v1 import (
    funnel_step_max_tokens,
    prefer_multi_step_funnels,
    user_json_char_budget,
)
from todayflow_backend.services.life_path_visibility_v0 import (
    IDENTITY_FIELDS,
    detect_life_path_visibility,
    life_path_co_voice_hint,
)
from todayflow_backend.services.life_spheres_projector_v0 import (
    build_sphere_foundations_v0,
    spheres_projection_allowed,
)
from todayflow_backend.services.life_spheres_synthesis_run_v0 import (
    SPHERES_SOURCE,
    SYNTHESIS_VERSION,
    synthesize_life_spheres_v0,
)
from todayflow_backend.services.profile_content_v1.source_depth import (
    depth_from_profile_pack,
    identity_generation_allowed,
    patterns_generation_allowed,
)
from todayflow_backend.services.profile_capture_session_v0 import (
    get_profile_capture_session,
    profile_capture_enabled,
)

logger = logging.getLogger(__name__)

PROFILE_DISCLOSURE_FUNNEL_V0 = "profile_disclosure_funnel_v0"
IDENTITY_CONTRACT = "profile_funnel_identity_v0"
STYLES_CONTRACT = "profile_funnel_styles_v0"
PATTERNS_CONTRACT = "profile_funnel_patterns_v0"
SPHERES_CONTRACT = "profile_funnel_spheres_v0"
CHART_READING_CONTRACT = "profile_funnel_chart_reading_v0"

SPHERE_IDS = (
    "love",
    "sex",
    "money",
    "work",
    "family",
    "kids",
    "body",
    "friends",
    "decisions",
)
SPHERE_FIELDS = ("how", "need", "risk", "turns_on", "turns_off", "helps")

PROMPT_IDS = (
    "profile.identity.v1",
    "profile.styles.v1",
    "profile.patterns.v1",
    "profile.spheres.synthesis.v1",
    "profile.chart_reading.v1",
)


def profile_prompt_versions() -> dict[str, str]:
    out: dict[str, str] = {}
    for pid in PROMPT_IDS:
        _, ver = get_prompt(pid, locale="ru")
        out[pid] = ver
    return out


def _parse_json_content(raw: str) -> dict[str, Any] | None:
    text = (raw or "").strip()
    if not text:
        return None
    m = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if m:
        text = m.group(1).strip()
    try:
        obj = json.loads(text)
        return obj if isinstance(obj, dict) else None
    except json.JSONDecodeError:
        return None


def _call(
    system: str,
    user: str,
    *,
    depth_level: str = "normal",
    temperature: float = 0.48,
) -> tuple[dict[str, Any] | None, str | None]:
    """Returns (parsed_dict_or_none, raw_content_or_none). Behavior unchanged when capture off."""
    if not is_llm_chat_configured():
        return None, None
    client = get_openai_compatible_client()
    if client is None:
        return None, None
    content = chat_completion_plain(
        client,
        model=resolve_default_chat_model(),
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=temperature,
        max_tokens=funnel_step_max_tokens(depth_level),
    )
    if not content:
        return None, None
    return _parse_json_content(content), content


def _step_name_from_prompt_id(prompt_id: str) -> str:
    if "identity" in prompt_id:
        return "identity"
    if "styles" in prompt_id:
        return "styles"
    if "patterns" in prompt_id:
        return "patterns"
    if "chart_reading" in prompt_id:
        return "chart_reading"
    if "spheres" in prompt_id:
        return "spheres"
    return prompt_id


def _call_with_retry(
    *,
    prompt_id: str,
    locale: str,
    user_payload: dict[str, Any],
    depth_level: str,
    ok_fn: Any,
    temperature: float = 0.48,
) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    system, ver = get_prompt(prompt_id, locale=locale)
    user = json.dumps(user_payload, ensure_ascii=False)[: user_json_char_budget()]
    max_tokens = funnel_step_max_tokens(depth_level)
    model = resolve_default_chat_model()
    step_meta: dict[str, Any] = {
        "prompt_id": prompt_id,
        "prompt_version": ver,
        "model": model,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "attempts": 0,
        "ms": 0,
        "ok": False,
    }
    t0 = perf_counter()
    result: dict[str, Any] | None = None
    capture = get_profile_capture_session() if profile_capture_enabled() else None
    step_name = _step_name_from_prompt_id(prompt_id)
    for attempt in range(2):
        step_meta["attempts"] = attempt + 1
        attempt_t0 = perf_counter()
        parsed, raw = _call(system, user, depth_level=depth_level, temperature=temperature)
        ok = bool(ok_fn(parsed))
        validation = {
            "ok": ok,
            "validator": getattr(ok_fn, "__name__", "ok_fn"),
            "reject_reason": None if ok else "step_schema_failed",
        }
        if capture is not None:
            capture.record_step_attempt(
                step_name,
                prompt_id=prompt_id,
                prompt_version=ver,
                system_prompt=system,
                user_prompt=user,
                model_request={
                    "model": model,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "depth_level": depth_level,
                    "messages": [
                        {"role": "system", "chars": len(system)},
                        {"role": "user", "chars": len(user)},
                    ],
                },
                raw_response=raw,
                parsed_response=parsed,
                validation_result=validation,
                attempt_index=attempt + 1,
                ms=int((perf_counter() - attempt_t0) * 1000),
            )
        if ok:
            result = parsed
            step_meta["ok"] = True
            break
        result = None
    step_meta["ms"] = int((perf_counter() - t0) * 1000)
    return result, step_meta


def _repair_identity_life_path_co_voice(
    *,
    shared: dict[str, Any],
    locale: str,
    draft: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    """One repair LLM call if claimed life_path is not visible in the draft."""
    numerology = shared.get("numerology") if isinstance(shared.get("numerology"), dict) else {}
    try:
        lp = int(numerology.get("life_path"))
    except (TypeError, ValueError):
        return draft, None
    det = detect_life_path_visibility(draft, lp, fields=IDENTITY_FIELDS)
    if det.get("visible"):
        return draft, None
    hint = life_path_co_voice_hint(lp) or {}
    themes = hint.get("themes_ru") or []
    repaired, meta = _call_with_retry(
        prompt_id="profile.identity.v1",
        locale=locale,
        user_payload={
            "shared": shared,
            "step": "identity",
            "draft": draft,
            "repair": {
                "reason": "life_path_co_voice_missing",
                "life_path": lp,
                "themes_ru": themes,
                "instruction_ru": (
                    f"Черновик не проявил life path {lp} детектируемо. Перепиши "
                    f"strengths[2] ИЛИ growth_zones[0] так, чтобы тема из {themes} "
                    "была явной (закрытие циклов / сострадание→действие / отпускание "
                    "для 9; инициация/независимость для 1; и т.д.). Astro не должен "
                    "поглотить число. Остальные поля можно слегка подправить."
                ),
            },
        },
        depth_level="normal",
        ok_fn=_identity_ok,
        temperature=0.32,
    )
    if meta:
        meta["repair"] = True
        meta["repair_reason"] = "life_path_co_voice_missing"
    if not repaired:
        return draft, meta
    det2 = detect_life_path_visibility(repaired, lp, fields=IDENTITY_FIELDS)
    if meta:
        meta["repair_visible"] = bool(det2.get("visible"))
    return (repaired if det2.get("visible") else draft), meta


def _identity_ok(d: dict[str, Any] | None) -> bool:
    if not isinstance(d, dict):
        return False
    if str(d.get("contract_version") or "").strip() != IDENTITY_CONTRACT:
        return False
    if len(str(d.get("identity_core") or "").strip()) < 20:
        return False
    from todayflow_backend.services.profile_contract_v1 import validate_recognition_line

    if validate_recognition_line(str(d.get("recognition_line") or ""), require=True):
        return False
    for key in ("strengths", "growth_zones"):
        items = d.get(key)
        if not isinstance(items, list) or len(items) < 3:
            return False
    return True


def _styles_ok(d: dict[str, Any] | None) -> bool:
    if not isinstance(d, dict):
        return False
    if str(d.get("contract_version") or "").strip() != STYLES_CONTRACT:
        return False
    return all(len(str(d.get(k) or "").strip()) >= 12 for k in ("relationship_style", "money_style", "decision_style"))


def _patterns_ok(d: dict[str, Any] | None) -> bool:
    if not isinstance(d, dict):
        return False
    if str(d.get("contract_version") or "").strip() != PATTERNS_CONTRACT:
        return False
    patterns = d.get("recurring_patterns")
    if not isinstance(patterns, list) or len(patterns) < 1 or len(str(patterns[0] or "").strip()) < 8:
        return False
    if len(str(d.get("living_changes") or "").strip()) < 12:
        return False
    if len(str(d.get("life_mission") or "").strip()) < 12:
        return False
    helps = d.get("helps")
    if not isinstance(helps, list) or len(helps) < 2:
        return False
    return True


def _chart_reading_ok(d: dict[str, Any] | None) -> bool:
    if not isinstance(d, dict):
        return False
    if str(d.get("contract_version") or "").strip() != CHART_READING_CONTRACT:
        return False
    if len(str(d.get("chart_reading") or "").strip()) < 40:
        return False
    if len(str(d.get("methodology_note") or "").strip()) < 20:
        return False
    return True


def _slim_natal_for_chart_reading(shared: dict[str, Any]) -> dict[str, Any]:
    natal = shared.get("natal") if isinstance(shared.get("natal"), dict) else {}
    astro = shared.get("astro") if isinstance(shared.get("astro"), dict) else {}
    positions = natal.get("positions") if isinstance(natal.get("positions"), dict) else {}
    asc = natal.get("ascendant") if isinstance(natal.get("ascendant"), dict) else {}
    out_pos: dict[str, Any] = {}
    for key in ("sun", "moon", "mc"):
        row = positions.get(key) if isinstance(positions.get(key), dict) else None
        if row:
            out_pos[key] = {
                "sign": row.get("sign"),
                "house": row.get("house"),
                "degree": row.get("degree") or row.get("longitude"),
            }
    if asc:
        houses = natal.get("houses") if isinstance(natal.get("houses"), list) else []
        house0 = houses[0] if houses and isinstance(houses[0], dict) else {}
        out_pos["ascendant"] = {
            "sign": asc.get("sign") or house0.get("sign"),
            "degree": asc.get("longitude") or asc.get("degree"),
        }
    aspects = natal.get("aspects") if isinstance(natal.get("aspects"), list) else []
    major = []
    for a in aspects[:8]:
        if isinstance(a, dict):
            major.append(
                {
                    "a": a.get("planet_a") or a.get("a"),
                    "b": a.get("planet_b") or a.get("b"),
                    "aspect": a.get("aspect") or a.get("type"),
                }
            )
    person = shared.get("person") if isinstance(shared.get("person"), dict) else {}
    return {
        "natal_positions": out_pos
        or {
            "sun": {"sign": astro.get("sun_sign")},
            "moon": {"sign": astro.get("moon_sign")},
        },
        "major_aspects": major,
        "time_unknown": not bool(person.get("birth_time") or person.get("birth_time_local")),
        "place_unknown": not bool(
            person.get("birth_place") or person.get("birth_city") or person.get("lat")
        ),
    }


def _spheres_ok(d: dict[str, Any] | None) -> bool:
    if not isinstance(d, dict):
        return False
    if str(d.get("contract_version") or "").strip() != SPHERES_CONTRACT:
        return False
    spheres = d.get("life_spheres")
    if not isinstance(spheres, dict):
        return False
    for sid in SPHERE_IDS:
        row = spheres.get(sid)
        if not isinstance(row, dict):
            return False
        for field in SPHERE_FIELDS:
            if len(str(row.get(field) or "").strip()) < 8:
                return False
    return True


def build_shared_profile_input(user_json: dict[str, Any]) -> dict[str, Any]:
    """One normalized pack for all funnel steps (no drift between requests)."""
    natal = user_json.get("natal") if isinstance(user_json.get("natal"), dict) else {}
    # Prefer explicit natal; optionally lift planet signs from natal_summary.personal_planets.
    summary = user_json.get("natal_summary") if isinstance(user_json.get("natal_summary"), dict) else {}
    if not natal.get("venus_sign") and isinstance(summary.get("personal_planets"), list):
        lifted: dict[str, Any] = dict(natal)
        for row in summary["personal_planets"]:
            if not isinstance(row, dict):
                continue
            body = str(row.get("body") or row.get("planet") or "").strip().lower()
            sign = row.get("sign")
            if body and sign and not lifted.get(f"{body}_sign"):
                lifted[f"{body}_sign"] = sign
        if summary.get("houses_available") is not None:
            lifted.setdefault("houses_available", bool(summary.get("houses_available")))
        if isinstance(summary.get("houses"), dict):
            lifted.setdefault("houses", summary["houses"])
        natal = lifted
    numerology = user_json.get("numerology")
    if isinstance(numerology, dict):
        numerology = dict(numerology)
        hint = life_path_co_voice_hint(numerology.get("life_path"))
        if hint:
            numerology["co_voice"] = hint
    elif numerology is None:
        numerology = None
    return {
        "contract_version": "profile_funnel_shared_input_v0",
        "person": user_json.get("person"),
        "astro": user_json.get("astro"),
        "natal": natal,
        "numerology": numerology,
        "baseline": user_json.get("baseline"),
        "living": user_json.get("living"),
        "locale": user_json.get("locale") or "ru",
        "profile_hash": user_json.get("profile_hash"),
    }


def run_profile_disclosure_funnel_v0(
    user_json: dict[str, Any],
    *,
    locale: str = "ru",
) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    """Returns (merged_raw_fields | None, meta).

    On partial failure returns whatever steps succeeded (never drops prior steps).
    """
    versions = profile_prompt_versions()
    meta: dict[str, Any] = {
        "failed": True,
        "partial": False,
        "funnel_contract": PROFILE_DISCLOSURE_FUNNEL_V0,
        "prompt_versions": versions,
        "model": resolve_default_chat_model() if is_llm_chat_configured() else None,
        "provider": (settings.llm_provider or "").strip().lower(),
        "locale": locale,
        "steps": [],
        "completed_steps": [],
    }
    if not prefer_multi_step_funnels():
        meta["reason"] = "quality_mode_economize"
        return None, meta
    if not is_llm_chat_configured():
        meta["reason"] = "llm_not_configured"
        return None, meta

    shared = build_shared_profile_input(user_json)
    meta["input_snapshot"] = {
        "profile_hash": shared.get("profile_hash"),
        "has_living": isinstance(shared.get("living"), dict),
        "sun_sign": (shared.get("astro") or {}).get("sun_sign") if isinstance(shared.get("astro"), dict) else None,
        "life_path": (shared.get("numerology") or {}).get("life_path") if isinstance(shared.get("numerology"), dict) else None,
    }
    if profile_capture_enabled():
        capture = get_profile_capture_session()
        if capture is not None and capture.pack.get("inputs") is None:
            # CLI usually pre-fills inputs; do not overwrite source_depth / missing_fields.
            capture.set_inputs(
                inputs=dict(shared),
                calculated_facts={
                    "astro": shared.get("astro"),
                    "numerology": shared.get("numerology"),
                    "baseline": shared.get("baseline"),
                },
            )

    # Production invariant: do not call identity LLM without birth + usable foundations.
    if not identity_generation_allowed(user_json):
        skip_id: dict[str, Any] = {
            "prompt_id": "profile.identity.v1",
            "skipped": True,
            "skip_reason": "generation_gate_ineligible",
            "attempts": 0,
            "ms": 0,
            "ok": False,
        }
        meta["steps"].append(skip_id)
        meta["reason"] = "identity_skipped_ineligible"
        meta["partial"] = True
        if profile_capture_enabled():
            capture = get_profile_capture_session()
            if capture is not None:
                bel = capture.pack.get("block_eligibility")
                if isinstance(bel, dict) and isinstance(bel.get("identity"), dict):
                    bel["identity"]["may_generate"] = False
                    bel["identity"]["reason"] = (
                        "birth_date + sun_sign/baseline/life_path required for identity"
                    )
                capture.mark_step_ran("identity", ran=False)
        return None, meta

    if profile_capture_enabled():
        capture = get_profile_capture_session()
        if capture is not None:
            bel = capture.pack.get("block_eligibility")
            if isinstance(bel, dict) and isinstance(bel.get("identity"), dict):
                bel["identity"]["may_generate"] = True
                bel["identity"]["reason"] = "birth_date + usable astro/baseline/numerology"

    r1, m1 = _call_with_retry(
        prompt_id="profile.identity.v1",
        locale=locale,
        user_payload={"shared": shared, "step": "identity"},
        depth_level="normal",
        ok_fn=_identity_ok,
    )
    meta["steps"].append(m1)
    if r1:
        r1, repair_meta = _repair_identity_life_path_co_voice(
            shared=shared,
            locale=locale,
            draft=r1,
        )
        if repair_meta:
            meta["steps"].append(repair_meta)
    if profile_capture_enabled():
        capture = get_profile_capture_session()
        if capture is not None:
            capture.mark_step_ran("identity", ran=bool(r1))
    if not r1:
        meta["reason"] = "identity_failed"
        return None, meta
    meta["completed_steps"].append("identity")

    r2, m2 = _call_with_retry(
        prompt_id="profile.styles.v1",
        locale=locale,
        user_payload={"shared": shared, "identity": r1, "step": "styles"},
        depth_level="normal",
        ok_fn=_styles_ok,
    )
    meta["steps"].append(m2)
    if not r2:
        meta["reason"] = "styles_failed"
        meta["partial"] = True
        merged = {
            "recognition_line": r1.get("recognition_line"),
            "identity_core": r1.get("identity_core"),
            "strengths": r1.get("strengths"),
            "growth_zones": r1.get("growth_zones"),
        }
        return merged, meta
    meta["completed_steps"].append("styles")

    # Production invariant: do not call patterns LLM without longitudinal eligibility.
    # Skipped/failed patterns must NOT stop spheres (natal-presence synthesis).
    r3: dict[str, Any] | None = None
    if not patterns_generation_allowed(user_json):
        depth = depth_from_profile_pack(user_json)
        skip_meta: dict[str, Any] = {
            "prompt_id": "profile.patterns.v1",
            "skipped": True,
            "skip_reason": "generation_gate_ineligible",
            "source_depth": depth,
            "attempts": 0,
            "ms": 0,
            "ok": False,
        }
        meta["steps"].append(skip_meta)
        meta["reason"] = "patterns_skipped_ineligible"
        meta["partial"] = True
        meta["patterns_omitted"] = True
        if profile_capture_enabled():
            capture = get_profile_capture_session()
            if capture is not None:
                from todayflow_backend.services.profile_content_v1.architecture import (
                    classify_allowed_claims,
                )

                if capture.pack.get("source_depth") is None:
                    capture.set_inputs(
                        inputs=dict(shared),
                        calculated_facts={
                            "astro": shared.get("astro"),
                            "numerology": shared.get("numerology"),
                            "baseline": shared.get("baseline"),
                        },
                        source_depth=depth,
                        allowed_claims=classify_allowed_claims(depth),
                    )
                capture.mark_step_ran("patterns", ran=False)
    else:
        r3, m3 = _call_with_retry(
            prompt_id="profile.patterns.v1",
            locale=locale,
            user_payload={"shared": shared, "identity": r1, "styles": r2, "step": "patterns"},
            depth_level="deep",
            ok_fn=_patterns_ok,
        )
        meta["steps"].append(m3)
        if profile_capture_enabled():
            capture = get_profile_capture_session()
            if capture is not None:
                bel = capture.pack.get("block_eligibility")
                if isinstance(bel, dict) and isinstance(bel.get("patterns"), dict):
                    bel["patterns"]["may_generate"] = True
                capture.mark_step_ran("patterns", ran=bool(r3))
        if r3:
            meta["completed_steps"].append("patterns")
        else:
            meta["reason"] = "patterns_failed"
            meta["partial"] = True
            meta["patterns_omitted"] = True

    # Spheres synthesis (love/money/decisions) — independent of patterns outcome.
    # Legacy profile.spheres.v1 and projector phrase tables are NOT content authority.
    foundations = build_sphere_foundations_v0(shared=shared, identity=r1, styles=r2)
    spheres_ok_gate = spheres_projection_allowed(foundations)
    if profile_capture_enabled():
        capture = get_profile_capture_session()
        if capture is not None:
            bel = capture.pack.get("block_eligibility")
            if isinstance(bel, dict) and isinstance(bel.get("spheres"), dict):
                bel["spheres"]["may_generate"] = spheres_ok_gate
                bel["spheres"]["reason"] = (
                    "natal-presence foundations allow sphere synthesis on prepared cues"
                    if spheres_ok_gate
                    else "insufficient natal/identity/styles foundations for spheres"
                )
                bel["spheres"]["min_source_depth"] = "birth_data_only"

    life_spheres: dict[str, Any] = {}
    spheres_meta: dict[str, Any] = {}
    if spheres_ok_gate:
        life_spheres, spheres_meta = synthesize_life_spheres_v0(foundations)
        step_spheres: dict[str, Any] = {
            "prompt_id": "profile.spheres.synthesis.v1",
            "synthesis_version": SYNTHESIS_VERSION,
            "spheres_source": SPHERES_SOURCE,
            "attempts": sum(
                int((spheres_meta.get("per_sphere") or {}).get(sid, {}).get("attempts") or 0)
                for sid in ("love", "money", "decisions")
            ),
            "ms": spheres_meta.get("ms"),
            "ok": bool(life_spheres),
            "synthesis": {
                "spheres_projected": spheres_meta.get("spheres_projected"),
                "spheres_omitted": spheres_meta.get("spheres_omitted"),
                "per_sphere": {
                    sid: {
                        "ok": info.get("ok"),
                        "cues_ok": info.get("cues_ok"),
                        "cue_ids": info.get("cue_ids"),
                        "omit_reason": info.get("omit_reason"),
                        "attempts": info.get("attempts"),
                    }
                    for sid, info in (spheres_meta.get("per_sphere") or {}).items()
                },
            },
        }
        meta["steps"].append(step_spheres)
        meta["spheres_source"] = SPHERES_SOURCE
        meta["life_spheres_meta"] = spheres_meta
        if life_spheres:
            meta["completed_steps"].append("spheres")
            if profile_capture_enabled():
                capture = get_profile_capture_session()
                if capture is not None:
                    capture.mark_step_ran("spheres", ran=True)
        else:
            meta["spheres_omitted"] = True
            if not meta.get("reason"):
                meta["reason"] = "spheres_synthesis_empty"
            meta["partial"] = True
            if profile_capture_enabled():
                capture = get_profile_capture_session()
                if capture is not None:
                    capture.mark_step_ran("spheres", ran=False)
    else:
        meta["steps"].append(
            {
                "prompt_id": "profile.spheres.synthesis.v1",
                "synthesis_version": SYNTHESIS_VERSION,
                "skipped": True,
                "skip_reason": "spheres_projection_gate_ineligible",
                "attempts": 0,
                "ms": 0,
                "ok": False,
            }
        )
        meta["spheres_omitted"] = True
        meta["partial"] = True
        if not meta.get("reason"):
            meta["reason"] = "spheres_projection_gate_ineligible"
        if profile_capture_enabled():
            capture = get_profile_capture_session()
            if capture is not None:
                capture.mark_step_ran("spheres", ran=False)

    # Step 5: connected natal chart reading (optional — does not fail the funnel).
    chart_reading_payload: dict[str, Any] | None = None
    if r1:
        natal_pack = _slim_natal_for_chart_reading(shared)
        r5, m5 = _call_with_retry(
            prompt_id="profile.chart_reading.v1",
            locale=locale,
            user_payload={
                "shared": shared,
                "identity_core": r1.get("identity_core"),
                **natal_pack,
                "step": "chart_reading",
            },
            depth_level="normal",
            ok_fn=_chart_reading_ok,
        )
        meta["steps"].append(m5)
        if r5:
            chart_reading_payload = r5
            meta["completed_steps"].append("chart_reading")
            if profile_capture_enabled():
                capture = get_profile_capture_session()
                if capture is not None:
                    capture.mark_step_ran("chart_reading", ran=True)
        elif profile_capture_enabled():
            capture = get_profile_capture_session()
            if capture is not None:
                capture.mark_step_ran("chart_reading", ran=False)

    # Birth-safe slice: identity + styles (+ optional patterns) + up to 3 natal spheres.
    # Still "partial" vs full 9-sphere/patterns contract, but not a failed publish —
    # FE must show the usable identity/styles/spheres instead of an empty shell.
    has_core = bool(r1 and r2)
    meta["failed"] = not has_core
    meta["partial"] = True
    if has_core and not meta.get("reason"):
        meta["reason"] = "spheres_slice_partial_synthesis_v1"

    merged: dict[str, Any] = {
        "recognition_line": r1.get("recognition_line"),
        "identity_core": r1.get("identity_core"),
        "strengths": r1.get("strengths"),
        "growth_zones": r1.get("growth_zones"),
        "relationship_style": r2.get("relationship_style"),
        "money_style": r2.get("money_style"),
        "decision_style": r2.get("decision_style"),
        "recurring_patterns": (r3.get("recurring_patterns") if r3 else []) or [],
        "living_changes": r3.get("living_changes") if r3 else None,
    }
    if r3:
        merged["life_mission"] = r3.get("life_mission")
        merged["helps"] = r3.get("helps")
    if life_spheres:
        merged["life_spheres"] = life_spheres
        if spheres_meta:
            merged["life_spheres_meta"] = spheres_meta
    if chart_reading_payload:
        merged["chart_reading"] = chart_reading_payload.get("chart_reading")
        merged["methodology_note"] = chart_reading_payload.get("methodology_note")
        merged["unavailable_note"] = chart_reading_payload.get("unavailable_note")
    return merged, meta

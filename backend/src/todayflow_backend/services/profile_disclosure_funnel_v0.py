"""Profile portrait funnel (identity → styles → patterns? → deterministic spheres).

Shared normalized input for LLM steps. Patterns gated by longitudinal eligibility.
Spheres: life_spheres_projector_v0 (natal-presence), independent of patterns outcome.
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
from todayflow_backend.services.life_spheres_projector_v0 import (
    PROJECTION_VERSION,
    SPHERES_SOURCE,
    build_sphere_foundations_v0,
    project_life_spheres_v0,
    spheres_projection_allowed,
)
from todayflow_backend.services.profile_content_v1.source_depth import (
    depth_from_profile_pack,
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
    "profile.spheres.v1",
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


def _identity_ok(d: dict[str, Any] | None) -> bool:
    if not isinstance(d, dict):
        return False
    if str(d.get("contract_version") or "").strip() != IDENTITY_CONTRACT:
        return False
    if len(str(d.get("identity_core") or "").strip()) < 20:
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
    return {
        "contract_version": "profile_funnel_shared_input_v0",
        "person": user_json.get("person"),
        "astro": user_json.get("astro"),
        "numerology": user_json.get("numerology"),
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

    r1, m1 = _call_with_retry(
        prompt_id="profile.identity.v1",
        locale=locale,
        user_payload={"shared": shared, "step": "identity"},
        depth_level="normal",
        ok_fn=_identity_ok,
    )
    meta["steps"].append(m1)
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
            "identity_core": r1.get("identity_core"),
            "strengths": r1.get("strengths"),
            "growth_zones": r1.get("growth_zones"),
        }
        return merged, meta
    meta["completed_steps"].append("styles")

    # Production invariant: do not call patterns LLM without longitudinal eligibility.
    # Skipped/failed patterns must NOT stop spheres (natal-presence projector).
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
        if r3:
            meta["completed_steps"].append("patterns")
        else:
            meta["reason"] = "patterns_failed"
            meta["partial"] = True

    # Deterministic spheres (PR-2 slice) — independent of patterns outcome.
    # Legacy profile.spheres.v1 is not content authority (not called).
    foundations = build_sphere_foundations_v0(shared=shared, identity=r1, styles=r2)
    spheres_ok_gate = spheres_projection_allowed(foundations)
    if profile_capture_enabled():
        capture = get_profile_capture_session()
        if capture is not None:
            bel = capture.pack.get("block_eligibility")
            if isinstance(bel, dict) and isinstance(bel.get("spheres"), dict):
                bel["spheres"]["may_generate"] = spheres_ok_gate
                bel["spheres"]["reason"] = (
                    "natal-presence foundations allow deterministic sphere projection"
                    if spheres_ok_gate
                    else "insufficient natal/identity/styles foundations for spheres"
                )
                bel["spheres"]["min_source_depth"] = "birth_data_only"

    life_spheres: dict[str, Any] = {}
    spheres_proj_meta: dict[str, Any] = {}
    t_sph0 = perf_counter()
    if spheres_ok_gate:
        life_spheres, spheres_proj_meta = project_life_spheres_v0(foundations)
        step_spheres: dict[str, Any] = {
            "prompt_id": None,
            "projector": PROJECTION_VERSION,
            "spheres_source": SPHERES_SOURCE,
            "attempts": 0,
            "ms": int((perf_counter() - t_sph0) * 1000),
            "ok": bool(life_spheres),
            "projection": {
                "spheres_projected": spheres_proj_meta.get("spheres_projected"),
                "spheres_omitted": spheres_proj_meta.get("spheres_omitted"),
                "fingerprint": spheres_proj_meta.get("fingerprint"),
            },
        }
        meta["steps"].append(step_spheres)
        meta["spheres_source"] = SPHERES_SOURCE
        meta["life_spheres_meta"] = spheres_proj_meta
        if life_spheres:
            meta["completed_steps"].append("spheres")
            if profile_capture_enabled():
                capture = get_profile_capture_session()
                if capture is not None:
                    capture.mark_step_ran("spheres", ran=True)
        else:
            meta["spheres_omitted"] = True
            if not meta.get("reason"):
                meta["reason"] = "spheres_projection_empty"
            meta["partial"] = True
            if profile_capture_enabled():
                capture = get_profile_capture_session()
                if capture is not None:
                    capture.mark_step_ran("spheres", ran=False)
    else:
        meta["steps"].append(
            {
                "prompt_id": None,
                "projector": PROJECTION_VERSION,
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

    # Global ready still requires full 9 spheres + patterns bundle — not redesigned in PR-2.
    # v0.1 always returns partial once identity/styles ran (slice spheres ≠ ready contract).
    meta["partial"] = True
    meta["failed"] = True
    if not meta.get("reason"):
        meta["reason"] = "spheres_slice_partial_v0_1"

    merged: dict[str, Any] = {
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
        if spheres_proj_meta:
            merged["life_spheres_meta"] = spheres_proj_meta
    return merged, meta

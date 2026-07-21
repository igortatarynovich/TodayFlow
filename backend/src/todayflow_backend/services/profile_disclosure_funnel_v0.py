"""Profile portrait multi-request funnel (identity → styles → patterns → spheres).

Shared normalized input for all steps. Per-step retry once. Partial merge on failure.
Generation meta carries prompt versions / model / tokens / timings.
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
from todayflow_backend.services.profile_capture_session_v0 import (
    get_profile_capture_session,
    profile_capture_enabled,
)
from todayflow_backend.services.llm_quality_policy_v1 import (
    funnel_step_max_tokens,
    prefer_multi_step_funnels,
    user_json_char_budget,
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

    r3, m3 = _call_with_retry(
        prompt_id="profile.patterns.v1",
        locale=locale,
        user_payload={"shared": shared, "identity": r1, "styles": r2, "step": "patterns"},
        depth_level="deep",
        ok_fn=_patterns_ok,
    )
    meta["steps"].append(m3)
    if not r3:
        meta["reason"] = "patterns_failed"
        meta["partial"] = True
        merged = {
            "identity_core": r1.get("identity_core"),
            "strengths": r1.get("strengths"),
            "growth_zones": r1.get("growth_zones"),
            "relationship_style": r2.get("relationship_style"),
            "money_style": r2.get("money_style"),
            "decision_style": r2.get("decision_style"),
        }
        return merged, meta
    meta["completed_steps"].append("patterns")

    r4, m4 = _call_with_retry(
        prompt_id="profile.spheres.v1",
        locale=locale,
        user_payload={
            "shared": shared,
            "identity": r1,
            "styles": r2,
            "patterns": r3,
            "step": "spheres",
        },
        depth_level="deep",
        ok_fn=_spheres_ok,
    )
    meta["steps"].append(m4)
    if not r4:
        meta["reason"] = "spheres_failed"
        meta["partial"] = True
        merged = {
            "identity_core": r1.get("identity_core"),
            "strengths": r1.get("strengths"),
            "growth_zones": r1.get("growth_zones"),
            "relationship_style": r2.get("relationship_style"),
            "money_style": r2.get("money_style"),
            "decision_style": r2.get("decision_style"),
            "recurring_patterns": r3.get("recurring_patterns"),
            "living_changes": r3.get("living_changes"),
            "life_mission": r3.get("life_mission"),
            "helps": r3.get("helps"),
        }
        return merged, meta
    meta["completed_steps"].append("spheres")

    meta["failed"] = False
    merged = {
        "identity_core": r1.get("identity_core"),
        "strengths": r1.get("strengths"),
        "growth_zones": r1.get("growth_zones"),
        "relationship_style": r2.get("relationship_style"),
        "money_style": r2.get("money_style"),
        "decision_style": r2.get("decision_style"),
        "recurring_patterns": r3.get("recurring_patterns"),
        "living_changes": r3.get("living_changes"),
        "life_mission": r3.get("life_mission"),
        "helps": r3.get("helps"),
        "life_spheres": r4.get("life_spheres"),
    }
    return merged, meta

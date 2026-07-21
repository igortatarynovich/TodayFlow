"""Production runner: sphere_cues → profile.spheres.synthesis.v1 → validate → partial map.

Fail/omit per sphere. Never falls back to projector phrase tables as user copy.
"""

from __future__ import annotations

import json
import logging
import re
from time import perf_counter
from typing import Any

from todayflow_backend.core.llm_openai_compatible import (
    chat_completion_text,
    get_openai_compatible_client,
    is_llm_chat_configured,
    resolve_default_chat_model,
)
from todayflow_backend.prompts.profile_spheres_synthesis_v1 import (
    format_synthesis_user_message,
)
from todayflow_backend.prompts.registry_v1 import get_prompt
from todayflow_backend.services.life_spheres_cues_v0 import build_sphere_cues
from todayflow_backend.services.life_spheres_projector_v0 import (
    SLICE_SPHERE_IDS,
    spheres_projection_allowed,
)
from todayflow_backend.services.life_spheres_synthesis_validate_v0 import (
    SPHERE_FIELDS,
    validate_sphere_synthesis_v0,
)
from todayflow_backend.services.llm_quality_policy_v1 import funnel_step_max_tokens
from todayflow_backend.services.profile_capture_session_v0 import (
    get_profile_capture_session,
    profile_capture_enabled,
)

logger = logging.getLogger(__name__)

SYNTHESIS_VERSION = "life_spheres_synthesis_v1.0.0"
SPHERES_SOURCE = "spheres_synthesis_v1"
PROMPT_ID = "profile.spheres.synthesis.v1"


def _parse_json(raw: str | None) -> dict[str, Any] | None:
    if not raw:
        return None
    text = raw.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:].strip()
    try:
        obj = json.loads(text)
        return obj if isinstance(obj, dict) else None
    except json.JSONDecodeError:
        m = re.search(r"\{[\s\S]*\}", text)
        if not m:
            return None
        try:
            obj = json.loads(m.group(0))
            return obj if isinstance(obj, dict) else None
        except json.JSONDecodeError:
            return None


def _call_sphere_llm(
    *,
    system: str,
    user: str,
    temperature: float,
    max_tokens: int,
) -> tuple[dict[str, Any] | None, str | None]:
    if not is_llm_chat_configured():
        return None, None
    client = get_openai_compatible_client(operation="background")
    if client is None:
        return None, None
    model = resolve_default_chat_model()
    raw = chat_completion_text(
        client,
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=temperature,
        max_tokens=max_tokens,
        json_object=True,
    )
    return _parse_json(raw), raw


def synthesize_life_spheres_v0(
    foundations: dict[str, Any],
    *,
    temperature: float = 0.4,
    max_retries: int = 1,
) -> tuple[dict[str, dict[str, str]], dict[str, Any]]:
    """Return validated partial life_spheres + kitchen meta. No projector fallback."""
    t0 = perf_counter()
    meta: dict[str, Any] = {
        "synthesis_version": SYNTHESIS_VERSION,
        "spheres_source": SPHERES_SOURCE,
        "prompt_id": PROMPT_ID,
        "spheres_projected": [],
        "spheres_omitted": [],
        "per_sphere": {},
    }
    if not spheres_projection_allowed(foundations):
        meta["gate"] = False
        meta["reason"] = "spheres_projection_gate_ineligible"
        for sid in SLICE_SPHERE_IDS:
            meta["spheres_omitted"].append({"id": sid, "reason": "gate_ineligible"})
        return {}, meta

    meta["gate"] = True
    locale = str(foundations.get("locale") or "ru")
    system, prompt_version = get_prompt(PROMPT_ID, locale=locale)
    meta["prompt_version"] = prompt_version
    natal = foundations.get("natal") if isinstance(foundations.get("natal"), dict) else {}
    houses_available = bool(natal.get("houses_available"))
    max_tokens = funnel_step_max_tokens("normal")
    capture = get_profile_capture_session() if profile_capture_enabled() else None

    life_spheres: dict[str, dict[str, str]] = {}

    for sid in SLICE_SPHERE_IDS:
        pack = build_sphere_cues(sid, foundations)
        per: dict[str, Any] = {
            "sphere_id": sid,
            "cues_ok": bool(pack.get("ok")),
            "cue_ids": [c.get("id") for c in (pack.get("sphere_cues") or [])],
            "kitchen": pack.get("kitchen"),
            "attempts": 0,
            "ok": False,
        }
        if not pack.get("ok"):
            reason = str(pack.get("reason") or "cues_empty")
            per["omit_reason"] = reason
            meta["spheres_omitted"].append({"id": sid, "reason": reason})
            meta["per_sphere"][sid] = per
            continue

        cue_texts = [str(c.get("text") or "") for c in (pack.get("sphere_cues") or [])]
        user = format_synthesis_user_message(pack, locale=locale)
        identity_core = str(pack.get("identity_core") or "")
        relevant_style = str(pack.get("relevant_style") or "")
        accepted: dict[str, str] | None = None
        last_defects: list[dict[str, str]] = []

        for attempt in range(1 + max(0, max_retries)):
            per["attempts"] = attempt + 1
            attempt_t0 = perf_counter()
            parsed, raw = _call_sphere_llm(
                system=system,
                user=user,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            validation = validate_sphere_synthesis_v0(
                parsed,
                identity_core=identity_core,
                relevant_style=relevant_style,
                sphere_cues=cue_texts,
                houses_available=houses_available,
            )
            last_defects = list(validation.get("defects") or [])
            if capture is not None:
                capture.record_step_attempt(
                    "spheres",
                    prompt_id=PROMPT_ID,
                    prompt_version=prompt_version,
                    system_prompt=system,
                    user_prompt=user[:8000],
                    model_request={
                        "model": resolve_default_chat_model(),
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                        "sphere_id": sid,
                        "cue_ids": per["cue_ids"],
                    },
                    raw_response=raw,
                    parsed_response=parsed,
                    validation_result={
                        "ok": bool(validation.get("ok")),
                        "validator": "validate_sphere_synthesis_v0",
                        "sphere_id": sid,
                        "checks": validation.get("checks"),
                        "reject_reason": None if validation.get("ok") else "synthesis_validation_failed",
                        "defects": last_defects[:12],
                    },
                    attempt_index=attempt + 1,
                    ms=int((perf_counter() - attempt_t0) * 1000),
                )
            if validation.get("ok") and validation.get("fields"):
                accepted = {f: str(validation["fields"][f]) for f in SPHERE_FIELDS}
                per["ok"] = True
                per["validation_checks"] = validation.get("checks")
                break
            per["last_defects"] = last_defects[:12]

        if accepted:
            life_spheres[sid] = accepted
            meta["spheres_projected"].append(sid)
            meta["per_sphere"][sid] = per
        else:
            per["omit_reason"] = "synthesis_validation_failed"
            meta["spheres_omitted"].append({"id": sid, "reason": "synthesis_validation_failed"})
            meta["per_sphere"][sid] = per
            # Explicit: do NOT call project_life_spheres_v0 for user-facing fill.

    meta["ms"] = int((perf_counter() - t0) * 1000)
    meta["ok"] = bool(life_spheres)
    return life_spheres, meta

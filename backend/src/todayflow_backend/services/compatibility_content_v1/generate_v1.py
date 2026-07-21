"""Offline / flagged LLM generation for content v1 contracts.

Production enrichment stays on legacy pipeline until COMPATIBILITY_CONTENT_V1
is enabled AND eval baseline beats current.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any, Literal

from todayflow_backend.services.compatibility_content_v1.prompts_v1 import (
    PROMPT_VERSION,
    build_user_prompt_v1,
    system_prompt_guest_v1,
    system_prompt_premium_v1,
    system_prompt_registered_v1,
)
from todayflow_backend.services.compatibility_content_v1.quality_checks import run_quality_suite
from todayflow_backend.services.compatibility_content_v1.source_depth import resolve_source_depth

logger = logging.getLogger("todayflow.compatibility.content_v1")

Tier = Literal["guest", "registered", "premium"]

_JSON_RE = re.compile(r"\{[\s\S]*\}")


def _extract_json(raw: str) -> dict[str, Any] | None:
    text = (raw or "").strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        data = json.loads(text)
        return data if isinstance(data, dict) else None
    except json.JSONDecodeError:
        m = _JSON_RE.search(text)
        if not m:
            return None
        try:
            data = json.loads(m.group(0))
            return data if isinstance(data, dict) else None
        except json.JSONDecodeError:
            return None


def _system_for_tier(tier: Tier, *, source_depth: str, locale: str) -> str:
    if tier == "guest":
        return system_prompt_guest_v1(source_depth=source_depth, locale=locale)
    if tier == "registered":
        return system_prompt_registered_v1(source_depth=source_depth, locale=locale)
    return system_prompt_premium_v1(source_depth=source_depth, locale=locale)


def build_generation_input(
    *,
    from_sign: str,
    to_sign: str,
    locale: str = "ru",
    relationship_context: str | None = None,
    birth_date_1: str | None = None,
    birth_date_2: str | None = None,
    profile_a: dict[str, Any] | None = None,
    profile_b: dict[str, Any] | None = None,
    user_question: str | None = None,
    score_hint: int | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    depth = resolve_source_depth(
        has_birth_dates=bool(birth_date_1 and birth_date_2),
        profile_a_ready=bool(profile_a),
        profile_b_ready=bool(profile_b),
        has_signs=bool(from_sign and to_sign),
    )
    payload: dict[str, Any] = {
        "from_sign": from_sign,
        "to_sign": to_sign,
        "locale": locale,
        "relationship_context": relationship_context or "unspecified",
        "source_depth": depth,
        "birth_date_1": birth_date_1,
        "birth_date_2": birth_date_2,
        "profile_a_ready": bool(profile_a),
        "profile_b_ready": bool(profile_b),
        "profile_a": profile_a,
        "profile_b": profile_b,
        "user_question": user_question,
        "score_hint": score_hint,
    }
    if extra:
        payload.update(extra)
    return payload


def generate_content_v1(
    *,
    tier: Tier,
    input_payload: dict[str, Any],
    chat_fn: Any | None = None,
) -> dict[str, Any]:
    """Generate + validate one content layer.

    chat_fn(system: str, user: str) -> str  — injectable for tests / eval runner.
    If chat_fn is None, uses core LLM client.
    """
    locale = str(input_payload.get("locale") or "ru")
    depth = str(
        input_payload.get("source_depth")
        or resolve_source_depth(
            has_birth_dates=bool(input_payload.get("birth_date_1") and input_payload.get("birth_date_2")),
            profile_a_ready=bool(input_payload.get("profile_a_ready") or input_payload.get("profile_a")),
            profile_b_ready=bool(input_payload.get("profile_b_ready") or input_payload.get("profile_b")),
            has_signs=bool(input_payload.get("from_sign") and input_payload.get("to_sign")),
        )
    )
    system = _system_for_tier(tier, source_depth=depth, locale=locale)
    user = build_user_prompt_v1(input_payload)

    if chat_fn is None:
        from todayflow_backend.core.llm_openai_compatible import (
            chat_completion_text,
            get_openai_compatible_client,
            resolve_default_chat_model,
            resolve_max_tokens,
        )

        client = get_openai_compatible_client()
        if client is None:
            return {
                "ok": False,
                "errors": ["llm:client_unavailable"],
                "prompt_version": PROMPT_VERSION,
                "tier": tier,
            }
        raw = chat_completion_text(
            client,
            model=resolve_default_chat_model(),
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.55,
            max_tokens=resolve_max_tokens(2200 if tier != "guest" else 900),
            json_object=True,
        )
    else:
        raw = chat_fn(system, user)

    parsed = _extract_json(raw or "")
    if not parsed:
        return {
            "ok": False,
            "errors": ["parse:invalid_json"],
            "raw": (raw or "")[:2000],
            "prompt_version": PROMPT_VERSION,
            "tier": tier,
        }

    parsed.setdefault("contract_version", "compatibility_content_v1")
    parsed.setdefault("tier", tier)
    parsed.setdefault("source_depth", depth)
    parsed.setdefault("locale", locale)
    if tier == "premium":
        # Premium UI does not show score; drop 0 / stray scores before validate.
        if parsed.get("score") in (0, "0", None):
            parsed.pop("score", None)

    known: set[str] = set()
    if parsed.get("source_depth") in ("profile_enriched", "two_profiles") or input_payload.get("profile_a"):
        known.add("profile_a")
    if parsed.get("source_depth") == "two_profiles" or input_payload.get("profile_b"):
        known.add("profile_b")

    from todayflow_backend.services.compatibility_content_v1.publish_gate import evaluate_publish

    quality = run_quality_suite(tier=tier, content=parsed, known_facts=known)
    gate = evaluate_publish(tier=tier, content=parsed, known_facts=known)
    return {
        **quality,
        "content": parsed if gate["publish_allowed"] else parsed,
        "publish_allowed": gate["publish_allowed"],
        "publish_decision": gate["decision"],
        "user_facing": gate.get("user_facing"),
        "prompt_version": PROMPT_VERSION,
        "raw": (raw or "")[:4000] if not quality.get("ok") else None,
    }

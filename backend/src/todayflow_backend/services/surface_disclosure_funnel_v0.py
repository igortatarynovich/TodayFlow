"""Multi-step disclosure funnels for day_layer / spheres / evening / deepen.

Quality-first: each surface runs interpretation/personalize → render as separate
API calls. Falls back to None so ``today_narrative`` can use the monolith prompt.
"""

from __future__ import annotations

import json
import logging
import re
from time import perf_counter
from typing import Any, Callable

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

logger = logging.getLogger(__name__)

SURFACE_DISCLOSURE_FUNNEL_V0 = "surface_disclosure_funnel_v0"

DAY_LAYER_PERSONALIZE_CONTRACT = "day_layer_funnel_personalize_v0"
SPHERES_MAP_CONTRACT = "spheres_funnel_map_v0"
EVENING_REFLECT_CONTRACT = "evening_funnel_reflect_v0"
DEEPEN_EXPAND_CONTRACT = "deepen_funnel_expand_v0"

OpenaiJsonFn = Callable[..., dict[str, Any] | None]


def _parse_json_content(content: str) -> dict[str, Any] | None:
    raw = (content or "").strip()
    if not raw:
        return None
    m = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", raw)
    if m:
        raw = m.group(1).strip()
    try:
        obj = json.loads(raw)
        return obj if isinstance(obj, dict) else None
    except json.JSONDecodeError:
        return None


def _openai_json_step(system: str, user: str, *, depth_level: str) -> dict[str, Any] | None:
    if not is_llm_chat_configured():
        return None
    client = get_openai_compatible_client()
    if client is None:
        return None
    content = chat_completion_plain(
        client,
        model=resolve_default_chat_model(),
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=0.5,
        max_tokens=funnel_step_max_tokens(depth_level),
    )
    if not content:
        return None
    return _parse_json_content(content)


def surface_funnel_openai_json_adapter(
    system: str,
    user: str,
    *,
    depth_level: str = "normal",
) -> dict[str, Any] | None:
    return _openai_json_step(system, user, depth_level=depth_level)


def _pack_json(pack: dict[str, Any]) -> str:
    return json.dumps(pack, ensure_ascii=False)[: user_json_char_budget()]


def _min_len_ok(d: dict[str, Any] | None, keys: tuple[str, ...], *, n: int = 8) -> bool:
    if not isinstance(d, dict):
        return False
    return all(len(str(d.get(k) or "").strip()) >= n for k in keys)


def _day_layer_personalize_ok(d: dict[str, Any] | None) -> bool:
    if not isinstance(d, dict):
        return False
    if str(d.get("contract_version") or "").strip() != DAY_LAYER_PERSONALIZE_CONTRACT:
        return False
    return _min_len_ok(d, ("what_lands", "soft_edge", "micro_move", "life_now_angle", "question_tone"))


def _day_layer_render_ok(d: dict[str, Any] | None) -> bool:
    if not isinstance(d, dict):
        return False
    return _min_len_ok(d, ("nudge_message", "personal_insight_title", "personal_insight_body"), n=6)


def _spheres_map_ok(d: dict[str, Any] | None) -> bool:
    if not isinstance(d, dict):
        return False
    if str(d.get("contract_version") or "").strip() != SPHERES_MAP_CONTRACT:
        return False
    spheres = d.get("spheres")
    if not isinstance(spheres, dict):
        return False
    for key in ("love", "family", "career", "money"):
        row = spheres.get(key)
        if not isinstance(row, dict):
            return False
        if str(row.get("stance") or "").strip().lower() not in ("up", "down", "neutral"):
            return False
        if len(str(row.get("angle") or "").strip()) < 6:
            return False
    return len(str(d.get("day_thread") or "").strip()) >= 8


def _spheres_render_ok(d: dict[str, Any] | None) -> bool:
    if not isinstance(d, dict):
        return False
    if len(str(d.get("page_intro") or "").strip()) < 8:
        return False
    sti = d.get("scenario_tie_ins")
    if not isinstance(sti, dict):
        return False
    return all(len(str(sti.get(k) or "").strip()) >= 6 for k in ("love", "family", "career", "money"))


def _evening_reflect_ok(d: dict[str, Any] | None) -> bool:
    if not isinstance(d, dict):
        return False
    if str(d.get("contract_version") or "").strip() != EVENING_REFLECT_CONTRACT:
        return False
    return _min_len_ok(d, ("morning_thread", "day_residue", "gentle_close"))


def _evening_render_ok(d: dict[str, Any] | None) -> bool:
    return _min_len_ok(
        d if isinstance(d, dict) else None,
        ("panel_intro", "outlook_preamble", "closure_invitation"),
        n=6,
    )


def _deepen_expand_ok(d: dict[str, Any] | None) -> bool:
    if not isinstance(d, dict):
        return False
    if str(d.get("contract_version") or "").strip() != DEEPEN_EXPAND_CONTRACT:
        return False
    spine = d.get("practical_spine")
    if not isinstance(spine, list) or len(spine) < 2:
        return False
    return _min_len_ok(d, ("topic_frame", "why_this_topic_today", "personal_hook"))


def _deepen_render_ok(d: dict[str, Any] | None) -> bool:
    if not isinstance(d, dict):
        return False
    bullets = d.get("bullets")
    if not isinstance(bullets, list) or len(bullets) < 2:
        return False
    return _min_len_ok(d, ("title", "body", "closing_line"), n=6)


def _run_two_step(
    *,
    surface: str,
    locale_value: str,
    depth_norm: str,
    user_pack: dict[str, Any],
    step1_prompt_id: str,
    step2_prompt_id: str,
    step1_ok: Callable[[dict[str, Any] | None], bool],
    step2_ok: Callable[[dict[str, Any] | None], bool],
    step1_key: str,
    openai_json: OpenaiJsonFn,
) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    sys1, ver1 = get_prompt(step1_prompt_id, locale=locale_value)
    u1 = _pack_json({"contract_version": f"{surface}_funnel_step1_input_v0", **user_pack})
    t0 = perf_counter()
    r1 = openai_json(sys1, u1, depth_level="quick" if depth_norm == "quick" else "normal")
    step1_ms = int((perf_counter() - t0) * 1000)
    meta: dict[str, Any] = {
        "failed": True,
        "surface": surface,
        "funnel_contract": SURFACE_DISCLOSURE_FUNNEL_V0,
        "step1_prompt_id": step1_prompt_id,
        "step1_prompt_version": ver1,
        "step2_prompt_id": step2_prompt_id,
        "step1_ms": step1_ms,
        "step2_ms": 0,
    }
    if not step1_ok(r1):
        logger.info("surface_disclosure_funnel_v0: %s step1 failed", surface)
        return None, meta

    sys2, ver2 = get_prompt(step2_prompt_id, locale=locale_value)
    meta["step2_prompt_version"] = ver2
    u2 = _pack_json(
        {
            "contract_version": f"{surface}_funnel_step2_input_v0",
            step1_key: r1,
            "avoid_echo_of_guide": (r1 or {}).get("avoid_echo_of_guide") if isinstance(r1, dict) else None,
            "already_said_in_guide": user_pack.get("already_said_in_guide"),
            "fixed_day_color": user_pack.get("fixed_day_color"),
            **{
                k: user_pack.get(k)
                for k in (
                    "funnel_interpretation",
                    "prior_thesis",
                    "day_model",
                    "ritual_context",
                    "intent",
                    "topic",
                    "day_engine_brief",
                )
                if k in user_pack
            },
        }
    )
    t1 = perf_counter()
    r2 = openai_json(sys2, u2, depth_level=depth_norm)
    meta["step2_ms"] = int((perf_counter() - t1) * 1000)
    if not step2_ok(r2):
        logger.info("surface_disclosure_funnel_v0: %s step2 failed", surface)
        return None, meta
    meta["failed"] = False
    meta["step1_artifact"] = r1
    out = {k: v for k, v in (r2 or {}).items() if k != "contract_version"}
    return out, meta


def run_day_layer_disclosure_funnel_v0(
    openai_json: OpenaiJsonFn,
    *,
    locale_value: str,
    depth_norm: str,
    user_pack: dict[str, Any],
) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    return _run_two_step(
        surface="day_layer",
        locale_value=locale_value,
        depth_norm=depth_norm,
        user_pack=user_pack,
        step1_prompt_id="day.day_layer.funnel.personalize.v1",
        step2_prompt_id="day.day_layer.funnel.render.v1",
        step1_ok=_day_layer_personalize_ok,
        step2_ok=_day_layer_render_ok,
        step1_key="day_layer_personalize",
        openai_json=openai_json,
    )


def run_spheres_disclosure_funnel_v0(
    openai_json: OpenaiJsonFn,
    *,
    locale_value: str,
    depth_norm: str,
    user_pack: dict[str, Any],
) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    return _run_two_step(
        surface="spheres",
        locale_value=locale_value,
        depth_norm=depth_norm,
        user_pack=user_pack,
        step1_prompt_id="day.spheres.funnel.map.v1",
        step2_prompt_id="day.spheres.funnel.render.v1",
        step1_ok=_spheres_map_ok,
        step2_ok=_spheres_render_ok,
        step1_key="spheres_map",
        openai_json=openai_json,
    )


def run_evening_disclosure_funnel_v0(
    openai_json: OpenaiJsonFn,
    *,
    locale_value: str,
    depth_norm: str,
    user_pack: dict[str, Any],
) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    return _run_two_step(
        surface="evening",
        locale_value=locale_value,
        depth_norm=depth_norm,
        user_pack=user_pack,
        step1_prompt_id="day.evening.funnel.reflect.v1",
        step2_prompt_id="day.evening.funnel.render.v1",
        step1_ok=_evening_reflect_ok,
        step2_ok=_evening_render_ok,
        step1_key="evening_reflect",
        openai_json=openai_json,
    )


def run_deepen_disclosure_funnel_v0(
    openai_json: OpenaiJsonFn,
    *,
    locale_value: str,
    depth_norm: str,
    user_pack: dict[str, Any],
) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    return _run_two_step(
        surface="deepen",
        locale_value=locale_value,
        depth_norm=depth_norm,
        user_pack=user_pack,
        step1_prompt_id="day.deepen.funnel.expand.v1",
        step2_prompt_id="day.deepen.funnel.render.v1",
        step1_ok=_deepen_expand_ok,
        step2_ok=_deepen_render_ok,
        step1_key="deepen_expand",
        openai_json=openai_json,
    )


def run_surface_disclosure_funnel_v0(
    surface: str,
    openai_json: OpenaiJsonFn,
    *,
    locale_value: str,
    depth_norm: str,
    user_pack: dict[str, Any],
) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    if not prefer_multi_step_funnels():
        return None, {"failed": True, "reason": "quality_mode_economize", "surface": surface}
    runners = {
        "day_layer": run_day_layer_disclosure_funnel_v0,
        "spheres": run_spheres_disclosure_funnel_v0,
        "evening": run_evening_disclosure_funnel_v0,
        "deepen": run_deepen_disclosure_funnel_v0,
    }
    runner = runners.get(surface)
    if runner is None:
        return None, {"failed": True, "reason": "unsupported_surface", "surface": surface}
    return runner(
        openai_json,
        locale_value=locale_value,
        depth_norm=depth_norm,
        user_pack=user_pack,
    )

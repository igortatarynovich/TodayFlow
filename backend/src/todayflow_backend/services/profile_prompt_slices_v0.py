"""Day-state prompt layers for Today (ritual / intent / behavior / scores).

Personal identity fields come only from ExperienceSlice (experience_contract_assembler_v0).
This module must not assemble personality from a raw Snapshot / CoreProfile.
"""

from __future__ import annotations

from typing import Any

from todayflow_backend.services.llm_quality_policy_v1 import profile_slice_clips

_VISIBLE_VER = "visible_profile_slice_v0"
_INTERNAL_VER = "internal_profile_slice_v0"


def _clip(s: str, n: int) -> str:
    t = (s or "").strip()
    if len(t) <= n:
        return t
    return t[: n - 1].rstrip() + "…"


def _clips() -> dict[str, int]:
    return profile_slice_clips()


def _goal_titles_from_fusion(fusion: dict[str, Any] | None, max_n: int = 3) -> list[str]:
    if not isinstance(fusion, dict):
        return []
    rc = fusion.get("rhythm_context")
    if not isinstance(rc, dict):
        return []
    goals = rc.get("goals")
    if not isinstance(goals, list):
        return []
    titles: list[str] = []
    for g in goals[:8]:
        if not isinstance(g, dict):
            continue
        t = str(g.get("title") or "").strip()
        if t and t not in titles:
            titles.append(_clip(t, _clips()["goal_title"]))
        if len(titles) >= max_n:
            break
    return titles


def build_visible_profile_slice_v0(
    *,
    experience_slice: dict[str, Any] | None,
    intent_slice: dict[str, Any] | None,
    ritual: dict[str, Any] | None,
    fusion_layer: dict[str, Any] | None,
    locale: str,
) -> dict[str, Any] | None:
    """Day surface + allowlisted identity from ExperienceSlice (not raw Snapshot)."""
    exp = experience_slice if isinstance(experience_slice, dict) else {}
    display_name = str(exp.get("display_name") or "").strip() or None
    sun_sign = str(exp.get("sun_sign") or "").strip() or None

    intent = intent_slice if isinstance(intent_slice, dict) else {}
    morning_intention = str(intent.get("morning_intention") or "").strip() or None
    morning_focus = str(intent.get("morning_focus") or "").strip() or None

    r = ritual if isinstance(ritual, dict) else {}
    mood = str(r.get("mood") or "").strip() or None
    head_topic = str(r.get("head_topic") or "").strip() or None

    en = (locale or "").strip().lower().startswith("en")
    rhythm_goals = _goal_titles_from_fusion(fusion_layer if isinstance(fusion_layer, dict) else None)

    if not any(
        [
            display_name,
            sun_sign,
            morning_intention,
            morning_focus,
            head_topic,
            mood,
            rhythm_goals,
        ]
    ):
        return None

    c = _clips()
    out: dict[str, Any] = {
        "contract_version": _VISIBLE_VER,
        "locale_hint": "en" if en else "ru",
    }
    if display_name:
        out["display_name"] = _clip(display_name, c["display_name"])
    if sun_sign:
        out["sun_sign"] = _clip(sun_sign, c["sun_sign"])
    if morning_intention:
        out["current_intention_or_goal_text"] = _clip(morning_intention, c["intention"])
    if morning_focus:
        out["morning_focus_label"] = _clip(morning_focus, c["morning_focus"])
    if head_topic:
        out["head_topic_after_ritual"] = _clip(head_topic, c["head_topic"])
    if mood:
        out["recent_self_reported_mood"] = _clip(mood, c["mood"])
    if rhythm_goals:
        out["active_rhythm_goal_titles"] = rhythm_goals
    return out


def build_internal_profile_slice_v0(
    *,
    behavior_patterns: dict[str, Any] | None,
    fusion_layer: dict[str, Any] | None,
    source_profile_version: Any | None = None,
) -> dict[str, Any] | None:
    """App day-state aggregates only — never learning / interpretation from Snapshot."""
    surface_block: dict[str, Any] = {}
    if isinstance(behavior_patterns, dict) and behavior_patterns.get("total_events"):
        surface_block = {
            "contract_version": behavior_patterns.get("contract_version"),
            "window_days": behavior_patterns.get("window_days"),
            "window_start": behavior_patterns.get("window_start"),
            "window_end": behavior_patterns.get("window_end"),
            "total_events": behavior_patterns.get("total_events"),
            "pattern_hints": (behavior_patterns.get("pattern_hints") or [])[:5],
            "by_event_type": (behavior_patterns.get("by_event_type") or [])[:8],
        }
        tags = behavior_patterns.get("tags")
        if isinstance(tags, dict):
            tcopy: dict[str, Any] = {}
            for key in (
                "top_mood_ids",
                "top_sphere_ids",
                "top_honest_step_ids",
                "top_guidance_lanes",
                "top_guidance_themes",
            ):
                v = tags.get(key)
                if isinstance(v, list):
                    tcopy[key] = v[:5]
            if tags.get("ritual_proximity") is not None:
                tcopy["ritual_proximity"] = tags.get("ritual_proximity")
            if tags.get("day_promise_sets") is not None:
                tcopy["day_promise_sets"] = tags.get("day_promise_sets")
            if tcopy:
                surface_block["tags"] = tcopy

    scores: dict[str, Any] = {}
    if isinstance(fusion_layer, dict):
        sc = fusion_layer.get("scores")
        if isinstance(sc, dict):
            for k in ("energy", "focus", "emotional_balance"):
                if k in sc and sc[k] is not None:
                    try:
                        scores[k] = int(sc[k])
                    except (TypeError, ValueError):
                        pass

    if not surface_block and not scores:
        return None

    out: dict[str, Any] = {
        "contract_version": _INTERNAL_VER,
        "usage": (
            "Системный слой дня: не цитировать дословно как «факты о личности»; "
            "использовать для реалистичности шагов."
        ),
    }
    if source_profile_version is not None:
        out["source_profile_version"] = source_profile_version
    if surface_block:
        out["surface_behavior_aggregates"] = surface_block
    if scores:
        out["app_rhythm_scores"] = scores
    return out

"""Сжатый селектор фрагментов core profile для Guidance (меньше токенов, релевантность теме)."""

from __future__ import annotations

from typing import Any


def _s(v: Any, limit: int = 420) -> str | None:
    if not isinstance(v, str):
        return None
    t = " ".join(v.split()).strip()
    if not t:
        return None
    return t[:limit]


def select_guidance_profile_modules(
    core_profile: dict[str, Any] | None,
    *,
    topic: str | None,
    lane: str,
    user_intent: str | None = None,
) -> dict[str, Any]:
    """Возвращает только релевантные поддеревья для промпта Guidance."""
    if not core_profile:
        return {"profile_ready": False}

    out: dict[str, Any] = {
        "profile_ready": bool(core_profile.get("is_ready")),
        "lane": lane,
        "topic": topic,
        "user_intent": user_intent,
    }

    baseline = core_profile.get("baseline") if isinstance(core_profile.get("baseline"), dict) else {}
    if isinstance(baseline, dict):
        arch = _s(baseline.get("archetype_seed"), 120)
        if arch:
            out["baseline_archetype"] = arch

    interpretation = core_profile.get("interpretation") if isinstance(core_profile.get("interpretation"), dict) else {}
    daily_i = (
        core_profile.get("daily_interpretation") if isinstance(core_profile.get("daily_interpretation"), dict) else {}
    )

    if isinstance(interpretation, dict):
        ident = _s(interpretation.get("identity"), 500)
        if ident:
            out["identity"] = ident
        rel = interpretation.get("relationships") if isinstance(interpretation.get("relationships"), str) else None
        if rel and (topic in {"relationships", "family", "intimacy"} or lane == "love"):
            out["relationships_note"] = _s(rel, 400)
        work_note = interpretation.get("work_money") if isinstance(interpretation.get("work_money"), str) else None
        if work_note and (topic in {"work", "money"} or lane == "money_career"):
            out["work_money_note"] = _s(work_note, 400)

    if isinstance(daily_i, dict) and lane in {"daily", "state", "future"}:
        lenses = daily_i.get("daily_lenses")
        if isinstance(lenses, dict) and lenses:
            slim: dict[str, str] = {}
            for k, v in list(lenses.items())[:6]:
                if isinstance(v, str) and v.strip():
                    slim[str(k)[:48]] = _s(v, 200) or ""
            if slim:
                out["daily_lenses"] = slim

    if lane in {"pattern", "self"} and isinstance(interpretation, dict):
        growth = interpretation.get("growth_edges")
        if isinstance(growth, str) and growth.strip():
            out["growth_edges"] = _s(growth, 400)

    living = core_profile.get("living") if isinstance(core_profile.get("living"), dict) else {}
    if isinstance(living, dict):
        lc = living.get("learning_context")
        if isinstance(lc, dict):
            summary = _s(lc.get("summary"), 280)
            if summary:
                out["learning_summary"] = summary

    return out

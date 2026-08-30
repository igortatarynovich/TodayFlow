"""Bridge morning ritual inputs to existing practice selector/library.

Does not create a new recommendation engine. Uses rank_practice_selection_v1
with a context snapshot derived from ritual state (mood, head_topic, tarot,
numerology) plus optional day_model / decision_engine signals.
"""

from __future__ import annotations

from typing import Any


def _norm(value: Any) -> str:
    return str(value or "").strip().lower()


def _mood_to_energy_state(mood: str) -> str:
    low = _norm(mood)
    if low in ("tired", "heavy", "exhausted", "drained"):
        return "low"
    if low in ("driven", "motivated", "energetic"):
        return "high"
    return "moderate"


def _mood_to_emotional_load(mood: str) -> str:
    low = _norm(mood)
    if low in ("anxious", "irritated", "confused", "heavy"):
        return "high"
    if low in ("calm", "hopeful", "quiet_wish"):
        return "low"
    return "moderate"


def _head_topic_to_path_themes(head_topic: str) -> list[str]:
    topic = str(head_topic or "").strip().lower()
    if not topic:
        return []
    mapping = {
        "general": ["clarity"],
        "body": ["body"],
        "money": ["money"],
        "dialogue": ["communication"],
        "family": ["home", "relationships"],
        "career": ["work"],
        "love": ["relationships"],
    }
    return mapping.get(topic, [topic])


def build_ritual_practice_selection_context(
    *,
    ritual_context: dict[str, Any] | None,
    decision_engine: dict[str, Any] | None = None,
    core_profile: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a valid practice_selection_context_snapshot_v1 from ritual inputs."""
    ritual = ritual_context if isinstance(ritual_context, dict) else {}
    de = decision_engine if isinstance(decision_engine, dict) else {}
    hero = de.get("hero") if isinstance(de.get("hero"), dict) else {}

    mood = str(ritual.get("mood") or "").strip()
    head_topic = str(ritual.get("head_topic") or "").strip()
    tarot = str(ritual.get("tarot_name_ru") or ritual.get("tarot_name") or "").strip()
    numerology = str(ritual.get("numerology_value") or "").strip()

    path_themes = _head_topic_to_path_themes(head_topic)
    if tarot:
        path_themes.append(f"tarot:{tarot}")
    if numerology:
        path_themes.append(f"numerology:{numerology}")
    path_themes = list(dict.fromkeys(path_themes))[:6]

    energy_state = _mood_to_energy_state(mood)
    emotional_load = _mood_to_emotional_load(mood)

    cp = core_profile if isinstance(core_profile, dict) else {}
    evolution = cp.get("evolution") if isinstance(cp.get("evolution"), dict) else {}
    evolution_stage = str(evolution.get("stage") or "seeker").strip() or "seeker"

    goals = []
    baseline = cp.get("baseline") if isinstance(cp.get("baseline"), dict) else {}
    for g in baseline.get("goals") or []:
        if isinstance(g, dict) and g.get("category"):
            goals.append(str(g["category"]).strip().lower())
    goals = list(dict.fromkeys(goals))[:4]

    return {
        "contract_version": "practice_selection_context_snapshot_v1",
        "strategy": str(hero.get("focus") or "stabilize").strip()[:32] or "stabilize",
        "tempo": str(hero.get("energy_label") or "steady").strip()[:32] or "steady",
        "risk": str(hero.get("risk") or "low").strip()[:32] or "low",
        "emotional_load": emotional_load,
        "evolution_stage": evolution_stage,
        "active_path_themes": path_themes,
        "rhythm_pattern_types": [],
        "energy_state": energy_state,
        "mood_state": mood[:32] or "neutral",
        "goal_categories": goals,
        "knowledge_claim_prefixes": [],
    }


def select_practice_for_ritual(
    *,
    ritual_context: dict[str, Any] | None,
    decision_engine: dict[str, Any] | None = None,
    core_profile: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    """Run existing practice selector on ritual context and return top candidate.

    Returns None gracefully if the selector cannot run (missing registry, empty
    candidates) so the ritual surface never breaks on selector failure.
    """
    try:
        from todayflow_backend.data.practice_definition_registry_loader import (
            get_practice_definition,
            load_practice_definition_registry_v1,
        )
        from todayflow_backend.services.practice_selection_ranker_v1 import (
            rank_practice_selection_v1,
        )

        context = build_ritual_practice_selection_context(
            ritual_context=ritual_context,
            decision_engine=decision_engine,
            core_profile=core_profile,
        )
        rank_output = rank_practice_selection_v1(context)
        ranked = (
            rank_output.get("rank_result", {}).get("ranked_candidates") or []
            if isinstance(rank_output, dict)
            else []
        )
        if not ranked:
            return None
        top = ranked[0]
        code = str(top.get("practice_definition_code") or "").strip()
        if not code:
            return None
        registry = load_practice_definition_registry_v1()
        definition = get_practice_definition(code, registry=registry)
        return {
            "contract_version": "ritual_practice_recommendation_v1",
            "practice_code": code,
            "title": definition.get("title") or code,
            "description": definition.get("description") or "",
            "category": definition.get("category") or code,
            "effort_level": definition.get("effort_level") or "low",
            "duration_range": definition.get("duration_range") or {},
            "rank_score": top.get("rank_score"),
            "selected_before_llm": True,
        }
    except Exception:
        return None

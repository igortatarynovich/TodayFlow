"""Profile Selector v0 — детерминированный выбор контекста для генерации (без LLM).

Шесть шагов: задача → тема → режим → релевантный срез → (веса задокументированы) → ProfileSelectorOutput.

См. docs/PROFILE_ENGINE_AND_SELECTOR.md.
"""

from __future__ import annotations

from typing import Any

from todayflow_backend.profile_engine.models import (
    ConfidenceScalar,
    GenerationRules,
    GoalsAndConstraints,
    ProfileContextSelectorInput,
    ProfilePromptSurface,
    ProfileSelectorOutput,
    ProfileTaskType,
    ProfileTopicDomain,
    SIGNAL_WEIGHT_ORDER,
    UserOperatingMode,
)


def narrative_surface_to_selector_params(
    surface: str,
    *,
    deepen_topic: str = "",
) -> tuple[ProfilePromptSurface, ProfileTaskType | None, ProfileTopicDomain | None]:
    """Маппинг surface Today narrative → вход Profile Selector (задача + домен)."""

    st = (surface or "").strip().lower()
    if st == "guide":
        return ProfilePromptSurface.GUIDANCE, ProfileTaskType.GUIDANCE_QUESTION, None
    if st == "day_layer":
        return ProfilePromptSurface.TODAY, ProfileTaskType.TODAY_SUMMARY, None
    if st == "spheres":
        return ProfilePromptSurface.TODAY, ProfileTaskType.TODAY_SPHERES, None
    if st == "evening":
        return ProfilePromptSurface.EVENING, ProfileTaskType.EVENING_REFLECTION, None
    if st == "deepen":
        dt = (deepen_topic or "").strip().lower()
        topic_domain = {
            "love": ProfileTopicDomain.INTIMACY,
            "money": ProfileTopicDomain.MONEY,
            "career": ProfileTopicDomain.WORK,
            "family": ProfileTopicDomain.FAMILY,
            "full_day": ProfileTopicDomain.GENERAL,
        }.get(dt, ProfileTopicDomain.GENERAL)
        return ProfilePromptSurface.TODAY, ProfileTaskType.TODAY_SPHERES, topic_domain
    return ProfilePromptSurface.TODAY, ProfileTaskType.TODAY_SUMMARY, None

SELECTOR_RULES_VERSION = "profile-selector-v1"

_TOPIC_TO_LIFE_AREA: dict[ProfileTopicDomain, str] = {
    ProfileTopicDomain.INTIMACY: "love",
    ProfileTopicDomain.RELATIONSHIPS: "love",
    ProfileTopicDomain.MONEY: "money",
    ProfileTopicDomain.WORK: "career",
    ProfileTopicDomain.FAMILY: "family",
    ProfileTopicDomain.BODY_ENERGY: "body",
    ProfileTopicDomain.DECISION: "decisions",
    ProfileTopicDomain.HABITS_DISCIPLINE: "decisions",
}


def default_task_for_surface(surface: ProfilePromptSurface) -> ProfileTaskType:
    return {
        ProfilePromptSurface.TODAY: ProfileTaskType.TODAY_SUMMARY,
        ProfilePromptSurface.GUIDANCE: ProfileTaskType.GUIDANCE_QUESTION,
        ProfilePromptSurface.COMPATIBILITY: ProfileTaskType.COMPATIBILITY,
        ProfilePromptSurface.FLOW: ProfileTaskType.FLOW_ACTION,
        ProfilePromptSurface.PRACTICE: ProfileTaskType.FLOW_ACTION,
        ProfilePromptSurface.GOAL: ProfileTaskType.FLOW_ACTION,
        ProfilePromptSurface.EVENING: ProfileTaskType.EVENING_REFLECTION,
    }.get(surface, ProfileTaskType.TODAY_SUMMARY)


def resolve_task(inp: ProfileContextSelectorInput) -> ProfileTaskType:
    if inp.task is not None:
        return inp.task
    return default_task_for_surface(inp.surface)


_HEAD_TOPIC_TO_DOMAIN: dict[str, ProfileTopicDomain] = {
    "general": ProfileTopicDomain.GENERAL,
    "body": ProfileTopicDomain.BODY_ENERGY,
    "money": ProfileTopicDomain.MONEY,
    "dialogue": ProfileTopicDomain.RELATIONSHIPS,
    "family": ProfileTopicDomain.FAMILY,
    "career": ProfileTopicDomain.WORK,
    "love": ProfileTopicDomain.INTIMACY,
}


def _topic_from_freeform(text: str | None) -> ProfileTopicDomain | None:
    if not text or not str(text).strip():
        return None
    t = str(text).lower()
    pairs = [
        (("отнош", "партн", "близост", "любов"), ProfileTopicDomain.RELATIONSHIPS),
        (("секс", "интим", "желан"), ProfileTopicDomain.INTIMACY),
        (("деньг", "ресурс", "финанс"), ProfileTopicDomain.MONEY),
        (("работ", "карьер", "проект"), ProfileTopicDomain.WORK),
        (("семь", "дет", "дом"), ProfileTopicDomain.FAMILY),
        (("тел", "энерг", "сон", "устал"), ProfileTopicDomain.BODY_ENERGY),
        (("реш", "выбор"), ProfileTopicDomain.DECISION),
        (("привыч", "дисциплин", "ритм"), ProfileTopicDomain.HABITS_DISCIPLINE),
        (("тревог", "стресс", "состоян"), ProfileTopicDomain.INNER_STATE),
    ]
    for keys, domain in pairs:
        if any(k in t for k in keys):
            return domain
    return None


def resolve_topic(
    inp: ProfileContextSelectorInput,
    ritual: dict[str, Any] | None,
) -> ProfileTopicDomain:
    if inp.topic is not None:
        return inp.topic
    tf = _topic_from_freeform(inp.topic_freeform)
    if tf is not None:
        return tf
    ht = ""
    if isinstance(ritual, dict):
        ht = str(ritual.get("head_topic") or "").strip().lower()
    if ht:
        slug = ht.split("/")[-1].strip()
        if slug in _HEAD_TOPIC_TO_DOMAIN:
            return _HEAD_TOPIC_TO_DOMAIN[slug]
    return ProfileTopicDomain.GENERAL


_MOOD_TO_MODE: dict[str, UserOperatingMode] = {
    "anxious": UserOperatingMode.ANXIETY,
    "tired": UserOperatingMode.FATIGUE,
    "heavy": UserOperatingMode.OVERLOAD,
    "irritated": UserOperatingMode.RESISTANCE,
    "confused": UserOperatingMode.UNCERTAINTY,
    "distant": UserOperatingMode.AVOIDANCE,
    "quiet_wish": UserOperatingMode.FATIGUE,
    "calm": UserOperatingMode.RESOURCE,
    "hopeful": UserOperatingMode.RESOURCE,
    "driven": UserOperatingMode.HIGH_IMPULSE,
    "motivated": UserOperatingMode.HIGH_IMPULSE,
    "move_wish": UserOperatingMode.HIGH_IMPULSE,
    "other": UserOperatingMode.NEUTRAL,
}


def _fusion_suggests_overload(fusion: dict[str, Any] | None) -> bool:
    if not isinstance(fusion, dict):
        return False
    scores = fusion.get("scores")
    if not isinstance(scores, dict):
        return False
    try:
        e = int(scores.get("energy", 3))
        f = int(scores.get("focus", 3))
    except (TypeError, ValueError):
        return False
    return e <= 1 and f <= 1


def infer_mode(
    inp: ProfileContextSelectorInput,
    ritual: dict[str, Any] | None,
    fusion: dict[str, Any] | None,
) -> UserOperatingMode:
    if inp.current_mode is not None:
        return inp.current_mode
    mood = ""
    if isinstance(ritual, dict):
        mood = str(ritual.get("mood") or "").strip().lower()
    if mood:
        if mood in _MOOD_TO_MODE:
            return _MOOD_TO_MODE[mood]
        if "тревог" in mood or "anx" in mood:
            return UserOperatingMode.ANXIETY
        if "устал" in mood or "тяжел" in mood:
            return UserOperatingMode.FATIGUE
    if _fusion_suggests_overload(fusion):
        return UserOperatingMode.OVERLOAD
    return UserOperatingMode.NEUTRAL


def _clip(s: str, n: int) -> str:
    t = (s or "").strip()
    if len(t) <= n:
        return t
    return t[: n - 1].rstrip() + "…"


def _living_signal_excerpt(core_profile: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(core_profile, dict):
        return {}
    living = core_profile.get("living")
    if not isinstance(living, dict):
        return {}
    sp = living.get("signal_profile")
    return sp if isinstance(sp, dict) else {}


def _topic_sphere_excerpt(
    core_profile: dict[str, Any] | None,
    topic: ProfileTopicDomain,
) -> str | None:
    if not isinstance(core_profile, dict):
        return None
    interp = core_profile.get("interpretation")
    if not isinstance(interp, dict):
        return None
    life_areas = interp.get("life_areas")
    if not isinstance(life_areas, dict):
        return None
    area_key = _TOPIC_TO_LIFE_AREA.get(topic)
    if not area_key:
        return None
    raw = life_areas.get(area_key)
    if not isinstance(raw, str) or not raw.strip():
        return None
    return _clip(raw.strip(), 240)


def build_relevant_profile(
    core_profile: dict[str, Any] | None,
    mode: UserOperatingMode,
    topic: ProfileTopicDomain,
) -> dict[str, Any]:
    rp: dict[str, Any] = {"topic": topic.value}
    baseline: dict[str, Any] = {}
    if isinstance(core_profile, dict):
        b = core_profile.get("baseline")
        if isinstance(b, dict):
            baseline = b
    if baseline.get("rhythm_style"):
        rp["rhythm_style"] = _clip(str(baseline["rhythm_style"]), 200)
    if baseline.get("archetype_seed"):
        rp["archetype_seed"] = _clip(str(baseline["archetype_seed"]), 120)

    interp = core_profile.get("interpretation") if isinstance(core_profile, dict) else None
    if isinstance(interp, dict):
        if interp.get("identity"):
            rp["identity_excerpt"] = _clip(str(interp["identity"]), 280)
        wo = interp.get("watchouts")
        if isinstance(wo, list) and wo:
            rp["primary_watchout_excerpt"] = _clip(str(wo[0]), 220)
        st_list = interp.get("strengths")
        if isinstance(st_list, list) and st_list:
            rp["primary_strength_excerpt"] = _clip(str(st_list[0]), 220)

    living = core_profile.get("living") if isinstance(core_profile, dict) else None
    if isinstance(living, dict):
        lc = living.get("learning_context")
        if isinstance(lc, dict):
            rs = lc.get("response_style")
            ss = lc.get("support_style")
            if rs:
                rp["learning_response_style"] = _clip(str(rs), 120)
            if ss:
                rp["learning_support_style"] = _clip(str(ss), 120)
            qm = lc.get("quality_memory")
            if isinstance(qm, dict):
                weak = qm.get("weak_patterns")
                if isinstance(weak, list) and weak:
                    rp["weak_pattern_hint"] = _clip(str(weak[0]), 160)

    sp = _living_signal_excerpt(core_profile)
    if sp.get("closure_state"):
        rp["closure_state"] = _clip(str(sp["closure_state"]), 80)
    if sp.get("clarity_state"):
        rp["clarity_state"] = _clip(str(sp["clarity_state"]), 80)
    if sp.get("dominant_focus"):
        rp["dominant_focus"] = _clip(str(sp["dominant_focus"]), 200)

    avoid: list[str] = []
    if mode == UserOperatingMode.ANXIETY:
        rp["stress_response"] = "prefer_stabilization_and_small_steps"
        rp["action_fit"] = "one_small_concrete_step"
        avoid.extend(["long abstract advice", "too many options", "pressure to confront before clarity"])
    elif mode == UserOperatingMode.OVERLOAD:
        rp["stress_response"] = "reduce_load_and_narrow_focus"
        rp["action_fit"] = "short_block_or_single_task"
        avoid.extend(["long plans", "multi-step agendas without prioritization"])
    elif mode == UserOperatingMode.FATIGUE:
        rp["action_fit"] = "micro_step_or_rest_first"
        avoid.extend(["high intensity pushes", "shame framing"])
    elif mode == UserOperatingMode.RESOURCE:
        rp["action_fit"] = "can_offer_bolder_step"
    elif mode == UserOperatingMode.UNCERTAINTY:
        rp["decision_style"] = "needs_clarity_before_commitment"
        avoid.extend(["false certainty", "binary ultimatums"])
    if avoid:
        rp["avoid"] = avoid[:8]

    sphere = _topic_sphere_excerpt(core_profile, topic)
    if sphere:
        rp["topic_sphere_excerpt"] = sphere

    return rp


def build_generation_rules(mode: UserOperatingMode, task: ProfileTaskType) -> GenerationRules:
    if mode in (UserOperatingMode.ANXIETY, UserOperatingMode.OVERLOAD, UserOperatingMode.FATIGUE):
        return GenerationRules(
            tone="direct_supportive",
            depth="short",
            max_actions=2,
            must_include=["one concrete action", "one avoid"],
            must_avoid=["abstract wording", "multiple competing priorities"],
        )
    if task == ProfileTaskType.TODAY_ACTION:
        return GenerationRules(
            tone="direct_supportive",
            depth="short",
            max_actions=2,
            must_include=["one concrete action"],
            must_avoid=["vague encouragement"],
        )
    if task == ProfileTaskType.GUIDANCE_QUESTION:
        return GenerationRules(
            tone="direct_supportive",
            depth="medium",
            max_actions=3,
            must_include=["one next step", "what would make advice wrong"],
            must_avoid=["medical or diagnostic claims"],
        )
    return GenerationRules(
        tone="supportive",
        depth="medium",
        max_actions=2,
        must_include=[],
        must_avoid=["overconfident claims without caveats"],
    )


def recent_signals_from_inputs(
    fusion: dict[str, Any] | None,
    behavior_patterns: dict[str, Any] | None,
    ritual: dict[str, Any] | None,
    history_slice: dict[str, Any] | None = None,
) -> list[str]:
    out: list[str] = []
    if isinstance(ritual, dict):
        m = str(ritual.get("mood") or "").strip()
        if m:
            out.append(f"ritual_mood:{m[:48]}")
    if isinstance(fusion, dict):
        scores = fusion.get("scores")
        if isinstance(scores, dict):
            parts = []
            for k in ("energy", "focus", "emotional_balance"):
                if k in scores and scores[k] is not None:
                    parts.append(f"{k}={scores[k]}")
            if parts:
                out.append("fusion_scores:" + ",".join(parts))
    if isinstance(history_slice, dict) and history_slice.get("contract_version") == "day_history_v0":
        delta = history_slice.get("fusion_score_delta_vs_yesterday")
        if isinstance(delta, dict) and history_slice.get("fusion_score_delta_trustworthy"):
            parts = []
            for k in ("energy", "focus", "emotional_balance"):
                if k in delta and delta[k] is not None:
                    parts.append(f"{k}={delta[k]:+d}" if isinstance(delta[k], int) else f"{k}={delta[k]}")
            if parts:
                out.append("day_history_delta:" + ",".join(parts))
        trailing = history_slice.get("trailing_7d_summary")
        if isinstance(trailing, dict) and history_slice.get("trailing_7d_summary_trustworthy"):
            energy = trailing.get("energy")
            if isinstance(energy, dict) and energy.get("avg") is not None:
                out.append(f"day_history_week_energy_avg:{energy['avg']}")
    if isinstance(behavior_patterns, dict):
        te = behavior_patterns.get("total_events")
        if te is not None:
            out.append(f"behavior_window_events:{te}")
        hints = behavior_patterns.get("pattern_hints")
        if isinstance(hints, list) and hints:
            out.append(f"pattern_hint:{_clip(str(hints[0]), 160)}")
        tags = behavior_patterns.get("tags")
        if isinstance(tags, dict):
            moods = tags.get("top_mood_ids")
            if isinstance(moods, list) and moods:
                out.append("top_moods:" + ",".join(str(x) for x in moods[:3]))
    return out[:12]


def module_keys_for(task: ProfileTaskType, topic: ProfileTopicDomain) -> list[str]:
    """Ключи срезов (документация / debug); фактическая сборка пока в day_context layers."""
    base = ["user_core", "fusion", "visible_profile", "internal_profile"]
    if task in (
        ProfileTaskType.TODAY_SUMMARY,
        ProfileTaskType.TODAY_SPHERES,
        ProfileTaskType.TODAY_ACTION,
    ):
        base += ["daily_foundation", "ritual", "behavior_patterns"]
    if task == ProfileTaskType.GUIDANCE_QUESTION:
        base += ["user_core.interpretation", "living.learning_context"]
    if task == ProfileTaskType.COMPATIBILITY:
        base += ["relationships", "communication_style"]
    if task == ProfileTaskType.FLOW_ACTION:
        base += ["action_fit", "rhythm_context.goals", "habits"]
    if topic == ProfileTopicDomain.INTIMACY:
        base.append("topic:intimacy")
    elif topic == ProfileTopicDomain.MONEY:
        base.append("topic:money")
    elif topic == ProfileTopicDomain.WORK:
        base.append("topic:work")
    return list(dict.fromkeys(base))


def select_profile_context(
    inp: ProfileContextSelectorInput,
    *,
    core_profile: dict[str, Any] | None = None,
    fusion_dump: dict[str, Any] | None = None,
    ritual_context: dict[str, Any] | None = None,
    behavior_patterns: dict[str, Any] | None = None,
    history_slice: dict[str, Any] | None = None,
) -> ProfileSelectorOutput:
    task = resolve_task(inp)
    topic = resolve_topic(inp, ritual_context)
    mode = infer_mode(inp, ritual_context, fusion_dump)
    rp = build_relevant_profile(core_profile, mode, topic)
    if inp.goals_and_constraints is not None:
        gc: GoalsAndConstraints = inp.goals_and_constraints
        if gc.active_goals:
            rp["active_goals"] = [_clip(x, 200) for x in gc.active_goals[:3]]
        if gc.constraints:
            rp["constraints"] = [_clip(x, 200) for x in gc.constraints[:5]]
        if gc.resources:
            rp["resources"] = [_clip(x, 200) for x in gc.resources[:5]]

    signals = recent_signals_from_inputs(
        fusion_dump,
        behavior_patterns,
        ritual_context,
        history_slice,
    )
    rules = build_generation_rules(mode, task)
    overall = ConfidenceScalar.MEDIUM
    if mode in (UserOperatingMode.ANXIETY, UserOperatingMode.UNCERTAINTY):
        overall = ConfidenceScalar.LOW

    debug: dict[str, Any] = {
        "selector_rules_version": SELECTOR_RULES_VERSION,
        "signal_weight_order": list(SIGNAL_WEIGHT_ORDER),
        "module_keys": module_keys_for(task, topic),
        "resolved_task": task.value,
        "resolved_topic": topic.value,
        "resolved_mode": mode.value,
    }

    return ProfileSelectorOutput(
        task=task,
        topic=topic,
        current_mode=mode,
        relevant_profile=rp,
        recent_signals=signals,
        generation_rules=rules,
        module_refs_used=[],
        overall_confidence=overall,
        debug_trace=debug,
    )

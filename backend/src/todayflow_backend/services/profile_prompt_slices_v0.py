"""DE-12: явное разделение «видимый профиль» vs «внутренний» для промптов (без новых таблиц).

Видимый слой — только то, что пользователь осознанно ввёл / видит в продукте.
Внутренний — агрегаты поведения и learning; не показывать дословно в UI, допустимо
мягко отражать в «Почему так». Не выдумывать полей сверх фактов из входных dict.
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


def _focus_areas_from_core(core_profile: dict[str, Any] | None, max_n: int = 5) -> list[str]:
    if not isinstance(core_profile, dict):
        return []
    out: list[str] = []
    living = core_profile.get("living") if isinstance(core_profile.get("living"), dict) else {}
    learning = living.get("learning_context") if isinstance(living.get("learning_context"), dict) else {}
    lanes = learning.get("dominant_lanes")
    if isinstance(lanes, list):
        for x in lanes[:max_n]:
            s = str(x).strip()
            if s and s not in out:
                out.append(_clip(s, 48))
    if len(out) >= max_n:
        return out
    interp = core_profile.get("interpretation") if isinstance(core_profile.get("interpretation"), dict) else {}
    la = interp.get("life_areas")
    if isinstance(la, dict):
        for k in list(la.keys())[: max_n * 2]:
            key = str(k).strip()
            if not key:
                continue
            label = _clip(key.replace("_", " "), 40)
            if label.lower() not in {x.lower() for x in out}:
                out.append(label)
            if len(out) >= max_n:
                break
    return out[:max_n]


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
    core_profile: dict[str, Any] | None,
    intent_slice: dict[str, Any] | None,
    ritual: dict[str, Any] | None,
    fusion_layer: dict[str, Any] | None,
    locale: str,
) -> dict[str, Any] | None:
    """Срез для промпта: имя, дата рождения/знак, фокусы, намерение, настроение из ритуала."""
    person: dict[str, Any] = {}
    astro: dict[str, Any] = {}
    if isinstance(core_profile, dict):
        p = core_profile.get("person")
        if isinstance(p, dict):
            person = p
        a = core_profile.get("astro")
        if isinstance(a, dict):
            astro = a

    display_name = str(person.get("display_name") or person.get("first_name") or "").strip() or None
    birth_date = str(astro.get("birth_date") or "").strip() or None
    sun_sign = str(astro.get("sun_sign") or "").strip() or None

    intent = intent_slice if isinstance(intent_slice, dict) else {}
    morning_intention = str(intent.get("morning_intention") or "").strip() or None
    morning_focus = str(intent.get("morning_focus") or "").strip() or None

    r = ritual if isinstance(ritual, dict) else {}
    mood = str(r.get("mood") or "").strip() or None
    head_topic = str(r.get("head_topic") or "").strip() or None

    focus_areas = _focus_areas_from_core(core_profile if isinstance(core_profile, dict) else None)
    en = (locale or "").strip().lower().startswith("en")

    rhythm_goals = _goal_titles_from_fusion(fusion_layer if isinstance(fusion_layer, dict) else None)

    if not any(
        [
            display_name,
            birth_date,
            sun_sign,
            focus_areas,
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
    if birth_date:
        out["birth_date"] = birth_date[:32]
    if sun_sign:
        out["sun_sign"] = _clip(sun_sign, c["sun_sign"])
    if focus_areas:
        out["focus_areas"] = focus_areas
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
    core_profile: dict[str, Any] | None,
    behavior_patterns: dict[str, Any] | None,
    fusion_layer: dict[str, Any] | None,
) -> dict[str, Any] | None:
    """Поведение и learning; только факты из JSON, без диагнозов и без выдуманных enum."""
    learning_slim: dict[str, Any] = {}
    pv = None
    if isinstance(core_profile, dict):
        pv = core_profile.get("profile_version")
        living = core_profile.get("living") if isinstance(core_profile.get("living"), dict) else {}
        lc = living.get("learning_context") if isinstance(living.get("learning_context"), dict) else {}
        learning = lc
        if learning:
            c = _clips()
            summary = _clip(str(learning.get("summary") or ""), c["learning_summary"])
            qm = learning.get("quality_memory") if isinstance(learning.get("quality_memory"), dict) else {}
            weak = qm.get("weak_patterns") if isinstance(qm.get("weak_patterns"), list) else []
            best = qm.get("best_patterns") if isinstance(qm.get("best_patterns"), list) else []
            learning_slim = {
                "summary_excerpt": summary or None,
                "quality_memory": {
                    "weak_patterns": [_clip(str(x), c["weak_or_best"]) for x in weak[:3] if str(x).strip()],
                    "best_patterns": [_clip(str(x), c["weak_or_best"]) for x in best[:3] if str(x).strip()],
                },
            }
            if not learning_slim["quality_memory"]["weak_patterns"]:
                del learning_slim["quality_memory"]["weak_patterns"]
            if not learning_slim["quality_memory"]["best_patterns"]:
                del learning_slim["quality_memory"]["best_patterns"]
            if not learning_slim["quality_memory"]:
                del learning_slim["quality_memory"]
            if not learning_slim.get("summary_excerpt") and not learning_slim.get("quality_memory"):
                learning_slim = {}

    surface_block: dict[str, Any] = {}
    if isinstance(behavior_patterns, dict) and behavior_patterns.get("total_events"):
        hints = behavior_patterns.get("pattern_hints")
        surface_block = {
            "window_days": behavior_patterns.get("window_days"),
            "window_start": behavior_patterns.get("window_start"),
            "window_end": behavior_patterns.get("window_end"),
            "total_events": behavior_patterns.get("total_events"),
            "pattern_hints": [
                _clip(str(h), _clips()["pattern_hint"]) for h in (hints if isinstance(hints, list) else [])[:5]
            ],
        }
        tags = behavior_patterns.get("tags")
        if isinstance(tags, dict):
            tcopy: dict[str, Any] = {}
            for key in ("top_mood_ids", "top_sphere_ids", "top_head_topics"):
                v = tags.get(key)
                if isinstance(v, list) and v:
                    tcopy[key] = v[:5]
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

    if not learning_slim and not surface_block and not scores:
        return None

    out: dict[str, Any] = {
        "contract_version": _INTERNAL_VER,
        "usage": "Системный слой: не цитировать дословно как «факты о личности»; использовать для реалистичности шагов и нейтральных отсылок в «почему так».",
    }
    if pv is not None:
        out["source_profile_version"] = pv
    if learning_slim:
        out["learning"] = learning_slim
    if surface_block:
        out["surface_behavior_aggregates"] = surface_block
    if scores:
        out["app_rhythm_scores"] = scores
    return out

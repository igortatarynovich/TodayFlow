"""UMTS-2 v0 — Compact User Model read path for all surfaces.

Assembles a top-K slice from existing stores (no full UKM yet):
  MeaningEvent (explicit L1) · meaning_surface_patterns · UserActiveKnowledge · CoreProfile identity.

Canon: USER_MODEL_TARGET_STATE.md §3 · PERSONAL_INTELLIGENCE_LAYER.md §3.1
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any

from sqlalchemy.orm import Session

from todayflow_backend.db.models import MeaningEvent, utc_naive_now
from todayflow_backend.services.cum_confidence_history_v0 import apply_confidence_delta_30d
from todayflow_backend.services.cum_day_model_alternates_v0 import (
    build_day_model_recommendation_alternates_v0,
)
from todayflow_backend.services.day_model_v1_active_knowledge_loader import (
    load_user_active_knowledge_list_v1,
)
from todayflow_backend.services.explicit_l1_knowledge_v0 import (
    EXPLICIT_L1_KNOWLEDGE_V0_CONTRACT,
    load_user_explicit_l1_knowledge_v0,
)
from todayflow_backend.services.interpretation_engine_v0 import (
    load_user_interpretation_instances_v0,
    sync_interpretation_engine_v0,
)
from todayflow_backend.services.meaning_derived_knowledge_v0 import (
    INFERRED_KNOWLEDGE_V0_CONTRACT,
    INFERRED_STATUS_ACTIVE,
    load_user_inferred_knowledge_v0,
    sync_meaning_derived_knowledge_v0,
)
from todayflow_backend.services.meaning_surface_patterns import (
    build_meaning_surface_patterns_v0,
)

COMPACT_USER_MODEL_V0_CONTRACT = "compact_user_model_v0"
PROFILE_IDENTITY_ATOM_CONTRACT = "profile_identity_v0"

_EXPLICIT_STATE_EVENT_TYPES = frozenset(
    {
        "mood_selected",
        "head_topic_selected",
        "action_option_selected",
        "day_focus_outcome",
        "sphere_feedback",
    }
)


def _payload_dict(raw: Any) -> dict[str, Any]:
    return raw if isinstance(raw, dict) else {}


def _iso_dt(value: datetime | None) -> str | None:
    if value is None:
        return None
    if value.tzinfo is not None:
        return value.astimezone(datetime.now().astimezone().tzinfo).replace(tzinfo=None).isoformat()
    return value.isoformat()


def _latest_explicit_state(
    db: Session,
    *,
    user_id: int,
    reference_date: date,
    lookback_days: int = 14,
) -> dict[str, Any]:
    """Most recent explicit L1 signals — mood, focus, promise, outcome."""
    start = reference_date - timedelta(days=max(1, lookback_days) - 1)
    rows = (
        db.query(MeaningEvent)
        .filter(
            MeaningEvent.user_id == user_id,
            MeaningEvent.local_date >= start,
            MeaningEvent.local_date <= reference_date,
            MeaningEvent.event_type.in_(tuple(_EXPLICIT_STATE_EVENT_TYPES)),
        )
        .order_by(MeaningEvent.event_time.desc(), MeaningEvent.id.desc())
        .limit(200)
        .all()
    )

    state: dict[str, Any] = {
        "local_date": reference_date.isoformat(),
        "mood_id": None,
        "mood_captured_at": None,
        "focus_topic_id": None,
        "focus_captured_at": None,
        "day_promise_text": None,
        "day_promise_captured_at": None,
        "day_focus_outcome": None,
        "day_focus_outcome_captured_at": None,
        "ritual_proximity_choice": None,
        "ritual_proximity_target": None,
        "ritual_proximity_captured_at": None,
        "honest_step_id": None,
        "honest_step_captured_at": None,
    }

    for row in rows:
        pl = _payload_dict(row.payload)
        captured = _iso_dt(row.event_time)
        if row.event_type == "mood_selected" and state["mood_id"] is None:
            mood_id = str(pl.get("mood_id") or pl.get("mood") or "").strip()
            if mood_id:
                state["mood_id"] = mood_id[:64]
                state["mood_captured_at"] = captured
        elif row.event_type == "head_topic_selected" and state["focus_topic_id"] is None:
            topic_id = str(pl.get("topic_id") or pl.get("head_topic") or "").strip()
            if topic_id:
                state["focus_topic_id"] = topic_id[:64]
                state["focus_captured_at"] = captured
        elif row.event_type == "action_option_selected" and state["day_promise_text"] is None:
            text = str(pl.get("action_text") or pl.get("promise_text") or pl.get("text") or "").strip()
            if not text and pl.get("action_option_index") is not None:
                text = f"action_option:{pl.get('action_option_index')}"
            if text:
                state["day_promise_text"] = text[:240]
                state["day_promise_captured_at"] = captured
        elif row.event_type == "day_focus_outcome" and state["day_focus_outcome"] is None:
            outcome = str(pl.get("outcome") or pl.get("day_focus_outcome") or "").strip()
            if outcome:
                state["day_focus_outcome"] = outcome[:32]
                state["day_focus_outcome_captured_at"] = captured
        elif row.event_type == "sphere_feedback":
            if state["ritual_proximity_choice"] is None:
                choice = str(pl.get("proximity_choice") or "").strip()
                target = str(pl.get("target") or "").strip()
                if choice:
                    state["ritual_proximity_choice"] = choice[:64]
                    state["ritual_proximity_target"] = target[:64] if target else None
                    state["ritual_proximity_captured_at"] = captured
            if state["honest_step_id"] is None:
                honest = str(pl.get("tarot_honest_step") or pl.get("honest_step") or "").strip()
                if honest and honest.lower() not in {"unset", "null", "unknown"}:
                    state["honest_step_id"] = honest[:64]
                    state["honest_step_captured_at"] = captured

    return state


def _themes_from_patterns(patterns: dict[str, Any] | None, *, limit: int = 8) -> list[dict[str, Any]]:
    if not patterns:
        return []
    tags = patterns.get("tags") if isinstance(patterns.get("tags"), dict) else {}

    ranked: list[tuple[str, int, str]] = []

    for item in tags.get("top_head_topics") if isinstance(tags.get("top_head_topics"), list) else []:
        if not isinstance(item, dict):
            continue
        topic_id = str(item.get("id") or "").strip()
        if topic_id:
            ranked.append((topic_id, int(item.get("count") or 0), "meaning_surface_patterns_v0"))

    for item in tags.get("top_guidance_themes") if isinstance(tags.get("top_guidance_themes"), list) else []:
        if not isinstance(item, dict):
            continue
        theme_id = str(item.get("id") or "").strip()
        if theme_id:
            ranked.append((theme_id, int(item.get("count") or 0), "guidance_semantic_v0"))

    if not ranked:
        return []

    total = sum(count for _, count, _ in ranked) or 1
    merged: dict[str, dict[str, Any]] = {}
    for theme_id, count, source in ranked:
        bucket = merged.setdefault(
            theme_id,
            {"id": theme_id, "count": 0, "sources": set()},
        )
        bucket["count"] += count
        bucket["sources"].add(source)

    themes: list[dict[str, Any]] = []
    for theme_id, bucket in sorted(merged.items(), key=lambda x: x[1]["count"], reverse=True)[:limit]:
        count = int(bucket["count"])
        themes.append(
            {
                "id": theme_id,
                "weight": round(min(1.0, count / total), 3),
                "stability": "emerging" if count < 3 else "stable",
                "source": "guidance_semantic_v0"
                if "guidance_semantic_v0" in bucket["sources"]
                else "meaning_surface_patterns_v0",
            }
        )
    return themes


def _behavioral_from_patterns(patterns: dict[str, Any] | None) -> dict[str, Any]:
    if not patterns:
        return {"works": [], "does_not_work": [], "hints": []}
    hints = patterns.get("pattern_hints") if isinstance(patterns.get("pattern_hints"), list) else []
    tags = patterns.get("tags") if isinstance(patterns.get("tags"), dict) else {}
    works: list[str] = []
    if int((tags.get("focus_sessions_started") if tags else 0) or 0) >= 3:
        works.append("short_focus_sessions")
    if int((tags.get("evening_reflections_submitted") if tags else 0) or 0) >= 2:
        works.append("evening_reflection")
    top_moods = tags.get("top_mood_ids") if isinstance(tags.get("top_mood_ids"), list) else []
    if top_moods and isinstance(top_moods[0], dict):
        mid = str(top_moods[0].get("id") or "").strip()
        if mid:
            works.append(f"ritual_mood:{mid}")
    if int(tags.get("guidance_questions_asked") or 0) >= 2:
        works.append("asks_guidance_questions")
    if int(tags.get("practices_completed") or 0) >= 2:
        works.append("completes_today_practices")
    if int(tags.get("tarot_deepen_sessions") or 0) >= 2:
        works.append("tarot_deepen_from_today")
    ritual_prox = tags.get("ritual_proximity") if isinstance(tags.get("ritual_proximity"), dict) else {}
    prox_top = ritual_prox.get("top_choices") if isinstance(ritual_prox.get("top_choices"), list) else []
    if prox_top and isinstance(prox_top[0], dict):
        choice = str(prox_top[0].get("id") or "").strip()
        if choice and int(prox_top[0].get("count") or 0) >= 3:
            works.append(f"ritual_proximity:{choice}")
    if int(tags.get("day_promise_sets") or 0) >= 2:
        works.append("day_promise_habit")
    honest_top = tags.get("top_honest_step_ids") if isinstance(tags.get("top_honest_step_ids"), list) else []
    if honest_top and isinstance(honest_top[0], dict):
        step_id = str(honest_top[0].get("id") or "").strip()
        if step_id and int(honest_top[0].get("count") or 0) >= 2:
            works.append(f"honest_step:{step_id}")
    return {
        "works": works[:8],
        "does_not_work": [],
        "hints": [str(h) for h in hints[:6] if str(h).strip()],
        "window_days": patterns.get("window_days"),
        "total_events": patterns.get("total_events"),
    }


_WORKS_LABEL_RU: dict[str, str] = {
    "short_focus_sessions": "короткие сессии фокуса",
    "evening_reflection": "вечерняя фиксация дня",
    "asks_guidance_questions": "вопросы в подсказках",
    "completes_today_practices": "завершённые практики дня",
    "tarot_deepen_from_today": "углубление через таро",
    "day_promise_habit": "обещание дня",
}


def format_behavioral_work_label(work_id: str) -> str:
    """Human RU label for CUM behavioral works — never expose raw machine ids in UI copy."""
    raw = (work_id or "").strip()
    if not raw:
        return ""
    mapped = _WORKS_LABEL_RU.get(raw)
    if mapped:
        return mapped
    if raw.startswith("ritual_mood:"):
        mood = raw.split(":", 1)[1].replace("_", " ").strip()
        return f"ритуал настроения «{mood}»" if mood else "ритуал настроения"
    if raw.startswith("ritual_proximity:"):
        choice = raw.split(":", 1)[1].replace("_", " ").strip()
        return f"близость в ритуале «{choice}»" if choice else "близость в ритуале"
    if raw.startswith("honest_step:"):
        step = raw.split(":", 1)[1].replace("_", " ").strip()
        return f"честный шаг «{step}»" if step else "честный шаг"
    if ":" in raw:
        return raw.split(":", 1)[1].replace("_", " ").strip() or raw
    return raw.replace("_", " ")


def _sign_from_natal_summary_rows(natal_summary: dict[str, Any], body: str) -> str | None:
    for key in ("luminaries", "personal_planets"):
        rows = natal_summary.get(key)
        if not isinstance(rows, list):
            continue
        for row in rows:
            if not isinstance(row, dict):
                continue
            name = str(row.get("name") or "").strip().lower()
            if name != body.lower():
                continue
            sign = row.get("sign")
            if isinstance(sign, str) and sign.strip():
                return sign.strip()
    return None


def _moon_sign_from_natal_summary(natal_summary: dict[str, Any]) -> str | None:
    direct = natal_summary.get("moon_sign")
    if isinstance(direct, str) and direct.strip():
        return direct.strip()
    return _sign_from_natal_summary_rows(natal_summary, "moon")


def _rising_sign_from_natal_summary(natal_summary: dict[str, Any]) -> str | None:
    angles = natal_summary.get("angles") if isinstance(natal_summary.get("angles"), dict) else {}
    for key in ("ascendant_sign", "rising_sign"):
        sign = angles.get(key)
        if isinstance(sign, str) and sign.strip():
            return sign.strip()
    direct = natal_summary.get("rising_sign")
    if isinstance(direct, str) and direct.strip():
        return direct.strip()
    return None


def _identity_facts_from_core_profile(core_profile: dict[str, Any] | None) -> dict[str, Any]:
    """UMTS §3.1 facts — birth, timezone from CoreProfile person slice."""
    if not isinstance(core_profile, dict):
        return {}

    person = core_profile.get("person") if isinstance(core_profile.get("person"), dict) else {}
    facts: dict[str, Any] = {}

    birth_date = person.get("birth_date")
    if isinstance(birth_date, str) and birth_date.strip():
        facts["birth_date"] = birth_date.strip()[:10]

    if "time_unknown" in person:
        facts["birth_time_known"] = not bool(person.get("time_unknown"))

    timezone_name = person.get("timezone_name")
    if isinstance(timezone_name, str) and timezone_name.strip():
        facts["timezone_name"] = timezone_name.strip()[:64]

    return facts


def _enrich_current_state_v1(state: dict[str, Any]) -> dict[str, Any]:
    """Add UMTS §3.2 mood_energy wrapper when explicit mood exists."""
    enriched = dict(state)
    mood_id = enriched.get("mood_id")
    if isinstance(mood_id, str) and mood_id.strip():
        enriched["mood_energy"] = {
            "mood_id": mood_id.strip()[:64],
            "energy_level": None,
            "captured_at": enriched.get("mood_captured_at"),
        }
    return enriched


def _recommendations_v1_slice(
    *,
    current_state: dict[str, Any],
    behavioral: dict[str, Any],
    active_themes: list[dict[str, Any]],
) -> dict[str, Any]:
    """UMTS §3.5 — 1 primary (+ optional alternates) from explicit state and patterns."""
    promise = current_state.get("day_promise_text")
    if isinstance(promise, str) and promise.strip():
        return {
            "primary": {
                "id": "rec-day-promise",
                "text": promise.strip()[:280],
                "timing_hint": "сегодня",
                "measurable": "отметить исход вечером",
                "source": "day_context",
                "evidence_atom_ids": [],
                "knowledge_type_gate": "pattern",
            },
            "alternates": [],
        }

    works = behavioral.get("works") if isinstance(behavioral.get("works"), list) else []
    if works and isinstance(works[0], str) and works[0].strip():
        slug = works[0].strip().replace(" ", "_")[:48]
        label = format_behavioral_work_label(works[0].strip())
        return {
            "primary": {
                "id": f"rec-pattern-{slug}",
                "text": f"Продолжи то, что уже работает: {label}.",
                "timing_hint": None,
                "measurable": "одно подтверждённое действие",
                "source": "behavioral_pattern",
                "evidence_atom_ids": [],
                "knowledge_type_gate": "pattern",
            },
            "alternates": [],
        }

    theme_id = None
    if active_themes and isinstance(active_themes[0], dict):
        theme_id = str(active_themes[0].get("id") or "").strip() or None
    if theme_id:
        theme_label = theme_id.replace("_", " ")
        return {
            "primary": {
                "id": f"rec-theme-{theme_id[:48]}",
                "text": f"Сфокусируй день на теме «{theme_label}» — один конкретный шаг.",
                "timing_hint": "сегодня",
                "measurable": "один завершённый шаг",
                "source": "day_context",
                "evidence_atom_ids": [],
                "knowledge_type_gate": "pattern",
            },
            "alternates": [],
        }

    return {
        "primary": {
            "id": "rec-today-checkin",
            "text": "Отметь настроение и фокус в Today — так система точнее подскажет следующий шаг.",
            "timing_hint": "утром или днём",
            "measurable": "check-in выполнен",
            "source": "template",
            "evidence_atom_ids": [],
            "knowledge_type_gate": "fact",
        },
        "alternates": [],
    }


def _attach_recommendation_alternates(
    recommendations: dict[str, Any],
    *,
    day_model_alternates: list[dict[str, Any]] | None,
) -> dict[str, Any]:
    if not day_model_alternates:
        return recommendations
    merged = dict(recommendations)
    existing = merged.get("alternates") if isinstance(merged.get("alternates"), list) else []
    if existing:
        return merged
    merged["alternates"] = day_model_alternates[:2]
    return merged


def _confidence_by_domain_v1(
    *,
    identity: dict[str, Any],
    themes: list[dict[str, Any]],
    behavioral: dict[str, Any],
    atom_count: int,
    has_explicit_today: bool,
) -> dict[str, float]:
    identity_score = 0.35
    if identity.get("summary") or identity.get("archetype"):
        identity_score = 0.65
    if identity.get("strengths") or identity.get("facts"):
        identity_score = min(0.85, identity_score + 0.1)

    theme_score = 0.25
    if themes:
        theme_score = min(0.9, 0.4 + len(themes) * 0.08)

    timing_score = 0.3
    works = behavioral.get("works") if isinstance(behavioral.get("works"), list) else []
    if len(works) >= 2:
        timing_score = 0.75
    elif works:
        timing_score = 0.55

    rec_score = 0.35
    if has_explicit_today:
        rec_score = 0.6
    if atom_count >= 2:
        rec_score = min(0.85, rec_score + 0.15)

    return {
        "identity": round(identity_score, 3),
        "themes": round(theme_score, 3),
        "timing": round(timing_score, 3),
        "recommendations": round(rec_score, 3),
    }


def _identity_from_core_profile(core_profile: dict[str, Any] | None) -> dict[str, Any]:
    """Stable identity slice for CUM §3.1 — from CoreProfile, not raw events."""
    if not isinstance(core_profile, dict):
        return {}

    person = core_profile.get("person") if isinstance(core_profile.get("person"), dict) else {}
    astro = core_profile.get("astro") if isinstance(core_profile.get("astro"), dict) else {}
    numerology = core_profile.get("numerology") if isinstance(core_profile.get("numerology"), dict) else {}
    baseline = core_profile.get("baseline") if isinstance(core_profile.get("baseline"), dict) else {}
    interpretation = (
        core_profile.get("interpretation") if isinstance(core_profile.get("interpretation"), dict) else {}
    )
    natal_summary = (
        core_profile.get("natal_summary") if isinstance(core_profile.get("natal_summary"), dict) else {}
    )

    strengths_raw = interpretation.get("strengths") if isinstance(interpretation.get("strengths"), list) else []
    constraints_raw = interpretation.get("watchouts") if isinstance(interpretation.get("watchouts"), list) else []
    identity_text = interpretation.get("identity") if isinstance(interpretation.get("identity"), str) else None

    moon_sign = (
        astro.get("moon_sign")
        or _moon_sign_from_natal_summary(natal_summary)
    )
    rising_sign = (
        astro.get("rising_sign")
        or astro.get("ascendant_sign")
        or _rising_sign_from_natal_summary(natal_summary)
    )

    return {
        "facts": _identity_facts_from_core_profile(core_profile) or None,
        "display_name": person.get("display_name") if isinstance(person, dict) else None,
        "sun_sign": astro.get("sun_sign") if isinstance(astro, dict) else None,
        "moon_sign": moon_sign,
        "rising_sign": rising_sign,
        "life_path": numerology.get("life_path") if isinstance(numerology, dict) else None,
        "archetype": baseline.get("archetype_seed") if isinstance(baseline, dict) else None,
        "summary": identity_text.strip()[:240] if isinstance(identity_text, str) and identity_text.strip() else None,
        "strengths": [str(item).strip()[:120] for item in strengths_raw if str(item).strip()][:4],
        "constraints": [str(item).strip()[:120] for item in constraints_raw if str(item).strip()][:4],
    }


def _identity_atoms_from_core_profile(core_profile: dict[str, Any] | None, *, limit: int = 6) -> list[dict[str, Any]]:
    """Profile identity facts as knowledge atoms for Quick Map / confirm surfaces."""
    identity = _identity_from_core_profile(core_profile)
    if not identity:
        return []

    atoms: list[dict[str, Any]] = []

    summary = identity.get("summary")
    if isinstance(summary, str) and summary.strip():
        atoms.append(
            {
                "knowledge_id": "profile-identity-summary",
                "contract_version": PROFILE_IDENTITY_ATOM_CONTRACT,
                "knowledge_type": "fact",
                "data_class": "identity",
                "claim": "profile_identity:summary",
                "claim_summary": summary.strip()[:200],
                "confidence": 0.72,
                "evidence_count": 1,
                "confirmation_required": False,
            }
        )

    archetype = identity.get("archetype")
    if isinstance(archetype, str) and archetype.strip():
        slug = archetype.strip().lower().replace(" ", "_")
        atoms.append(
            {
                "knowledge_id": "profile-archetype",
                "contract_version": PROFILE_IDENTITY_ATOM_CONTRACT,
                "knowledge_type": "fact",
                "data_class": "identity",
                "claim": f"profile_archetype:{slug}",
                "claim_summary": f"Архетип {archetype.strip()}",
                "confidence": 0.7,
                "evidence_count": 1,
                "confirmation_required": False,
            }
        )

    moon_sign = identity.get("moon_sign")
    if isinstance(moon_sign, str) and moon_sign.strip() and len(atoms) < limit:
        atoms.append(
            {
                "knowledge_id": "profile-moon-sign",
                "contract_version": PROFILE_IDENTITY_ATOM_CONTRACT,
                "knowledge_type": "fact",
                "data_class": "identity",
                "claim": f"profile_moon:{moon_sign.strip().lower().replace(' ', '_')}",
                "claim_summary": f"Луна в {moon_sign.strip()}",
                "confidence": 0.68,
                "evidence_count": 1,
                "confirmation_required": False,
            }
        )

    rising_sign = identity.get("rising_sign")
    if isinstance(rising_sign, str) and rising_sign.strip() and len(atoms) < limit:
        atoms.append(
            {
                "knowledge_id": "profile-rising-sign",
                "contract_version": PROFILE_IDENTITY_ATOM_CONTRACT,
                "knowledge_type": "fact",
                "data_class": "identity",
                "claim": f"profile_rising:{rising_sign.strip().lower().replace(' ', '_')}",
                "claim_summary": f"Асцендент в {rising_sign.strip()}",
                "confidence": 0.68,
                "evidence_count": 1,
                "confirmation_required": False,
            }
        )

    for index, strength in enumerate(identity.get("strengths") or []):
        if len(atoms) >= limit:
            break
        atoms.append(
            {
                "knowledge_id": f"profile-strength-{index}",
                "contract_version": PROFILE_IDENTITY_ATOM_CONTRACT,
                "knowledge_type": "pattern",
                "data_class": "identity",
                "claim": f"profile_strength:{index}",
                "claim_summary": str(strength)[:200],
                "confidence": 0.65,
                "evidence_count": 1,
                "confirmation_required": False,
            }
        )

    for index, constraint in enumerate(identity.get("constraints") or []):
        if len(atoms) >= limit:
            break
        atoms.append(
            {
                "knowledge_id": f"profile-constraint-{index}",
                "contract_version": PROFILE_IDENTITY_ATOM_CONTRACT,
                "knowledge_type": "pattern",
                "data_class": "identity",
                "claim": f"profile_constraint:{index}",
                "claim_summary": str(constraint)[:200],
                "confidence": 0.62,
                "evidence_count": 1,
                "confirmation_required": False,
            }
        )

    return atoms[:limit]


def _merge_identity_atoms(
    runtime_atoms: list[dict[str, Any]],
    identity_atoms: list[dict[str, Any]],
    *,
    limit: int = 20,
) -> list[dict[str, Any]]:
    if not identity_atoms:
        return runtime_atoms[:limit]

    seen = {str(row.get("knowledge_id") or "") for row in identity_atoms if row.get("knowledge_id")}
    merged = list(identity_atoms)
    for row in runtime_atoms:
        kid = str(row.get("knowledge_id") or "")
        if kid and kid in seen:
            continue
        merged.append(row)
        if len(merged) >= limit:
            break
    return merged[:limit]


def _atoms_top_k(db: Session, user_id: int, *, limit: int = 20) -> list[dict[str, Any]]:
    explicit = load_user_explicit_l1_knowledge_v0(db, user_id, limit=limit)
    inferred = load_user_inferred_knowledge_v0(db, user_id, limit=limit)
    pattern_rows = load_user_active_knowledge_list_v1(db, user_id, limit=limit)
    atoms: list[dict[str, Any]] = []

    for row in explicit:
        atoms.append(
            {
                "knowledge_id": row.get("knowledge_id"),
                "contract_version": EXPLICIT_L1_KNOWLEDGE_V0_CONTRACT,
                "knowledge_type": row.get("knowledge_type"),
                "data_class": row.get("data_class"),
                "claim": row.get("claim"),
                "claim_summary": str(row.get("summary") or row.get("value") or "")[:200],
                "confidence": row.get("confidence"),
                "evidence_count": row.get("evidence_count"),
                "last_confirmed_at": row.get("last_confirmed_at"),
                "confirmation_required": False,
            }
        )

    for row in pattern_rows:
        if len(atoms) >= limit:
            break
        claim_summary = str(row.get("claim") or "")[:200]
        atoms.append(
            {
                "knowledge_id": row.get("knowledge_id"),
                "contract_version": row.get("contract_version"),
                "knowledge_type": row.get("knowledge_type"),
                "data_class": "behavioral",
                "claim_summary": claim_summary,
                "confidence": row.get("confidence"),
                "evidence_count": row.get("evidence_count"),
                "last_confirmed_at": row.get("last_confirmed_at"),
                "confirmation_required": False,
            }
        )

    for row in inferred:
        if len(atoms) >= limit:
            break
        atoms.append(
            {
                "knowledge_id": row.get("knowledge_id"),
                "contract_version": INFERRED_KNOWLEDGE_V0_CONTRACT,
                "knowledge_type": row.get("knowledge_type"),
                "data_class": row.get("data_class"),
                "claim": row.get("claim"),
                "claim_summary": str(row.get("summary") or "")[:200],
                "confidence": row.get("confidence"),
                "evidence_count": row.get("evidence_count"),
                "last_confirmed_at": row.get("last_confirmed_at"),
                "confirmation_required": bool(row.get("confirmation_required")),
            }
        )

    return atoms[:limit]


def _relationship_insights_top_k(db: Session, user_id: int, *, limit: int = 3) -> list[dict[str, Any]]:
    """Confirmed relationship hypotheses for Profile quick map (attachment lens v0)."""
    from todayflow_backend.db import models as db_models

    rows = (
        db.query(db_models.UserActiveKnowledge)
        .filter(
            db_models.UserActiveKnowledge.user_id == user_id,
            db_models.UserActiveKnowledge.status == INFERRED_STATUS_ACTIVE,
        )
        .order_by(db_models.UserActiveKnowledge.updated_at.desc())
        .limit(max(1, min(limit * 4, 40)))
        .all()
    )
    insights: list[dict[str, Any]] = []
    for row in rows:
        payload = row.payload if isinstance(row.payload, dict) else {}
        if payload.get("contract_version") != INFERRED_KNOWLEDGE_V0_CONTRACT:
            continue
        if payload.get("user_verdict") != "confirm":
            continue
        claim = str(payload.get("claim") or "")
        if not claim.startswith("behavior_hypothesis:attachment_lens_"):
            continue
        label = str(payload.get("display_label") or payload.get("summary") or claim)[:200]
        insights.append(
            {
                "knowledge_id": row.knowledge_id,
                "kind": "attachment_lens",
                "label": label,
                "summary": str(payload.get("summary") or "")[:240],
                "domain": payload.get("domain") or "compatibility",
                "confirmed_at": payload.get("verdict_at") or payload.get("last_confirmed_at"),
            }
        )
        if len(insights) >= limit:
            break
    return insights


def _confidence_v0(
    *,
    patterns: dict[str, Any] | None,
    atom_count: int,
    has_explicit_today: bool,
    identity: dict[str, Any] | None = None,
    themes: list[dict[str, Any]] | None = None,
    behavioral: dict[str, Any] | None = None,
) -> dict[str, Any]:
    total_events = int((patterns or {}).get("total_events") or 0)
    overall = 0.25
    if total_events >= 5:
        overall = 0.45
    if total_events >= 20:
        overall = 0.6
    if atom_count >= 1:
        overall = min(0.85, overall + 0.15)
    if has_explicit_today:
        overall = min(0.9, overall + 0.1)

    flags: list[str] = []
    if total_events < 3:
        flags.append("low_meaning_events")
    if atom_count == 0:
        flags.append("no_active_knowledge_atoms")
    if not has_explicit_today:
        flags.append("no_explicit_state_today")

    return {
        "overall": round(overall, 3),
        "by_domain": _confidence_by_domain_v1(
            identity=identity or {},
            themes=themes or [],
            behavioral=behavioral or {},
            atom_count=atom_count,
            has_explicit_today=has_explicit_today,
        ),
        "uncertainty_flags": flags,
        "delta_30d": None,
        "meaning_events_28d": total_events,
    }


def build_compact_user_model_v0(
    db: Session,
    *,
    user_id: int,
    core_profile: dict[str, Any] | None = None,
    reference_date: date | None = None,
    window_days: int = 28,
) -> dict[str, Any]:
    """Build read-model slice for Profile → surface give loop."""
    ref = reference_date or date.today()
    sync_meaning_derived_knowledge_v0(
        db,
        user_id=user_id,
        reference_date=ref,
        window_days=window_days,
        commit=True,
    )
    sync_interpretation_engine_v0(
        db,
        user_id=user_id,
        reference_date=ref,
        window_days=window_days,
        commit=True,
    )
    patterns = build_meaning_surface_patterns_v0(
        db, user_id=user_id, reference_date=ref, window_days=window_days
    )
    current_state = _enrich_current_state_v1(_latest_explicit_state(db, user_id=user_id, reference_date=ref))
    identity = _identity_from_core_profile(core_profile)
    if identity.get("facts") is None:
        identity.pop("facts", None)
    identity_atoms = _identity_atoms_from_core_profile(core_profile)
    atoms = _merge_identity_atoms(_atoms_top_k(db, user_id, limit=20), identity_atoms, limit=20)
    interpretation_instances = load_user_interpretation_instances_v0(db, user_id, limit=5)
    themes = _themes_from_patterns(patterns)
    behavioral = _behavioral_from_patterns(patterns)

    has_explicit_today = bool(
        current_state.get("mood_id")
        or current_state.get("focus_topic_id")
        or current_state.get("day_promise_text")
    )

    return {
        "contract_version": COMPACT_USER_MODEL_V0_CONTRACT,
        "as_of": ref.isoformat(),
        "generated_at": utc_naive_now().isoformat(),
        "identity": identity,
        "current_state": current_state,
        "active_themes": themes,
        "behavioral_patterns": behavioral,
        "recommendations": _attach_recommendation_alternates(
            _recommendations_v1_slice(
                current_state=current_state,
                behavioral=behavioral,
                active_themes=themes,
            ),
            day_model_alternates=build_day_model_recommendation_alternates_v0(
                user_id=user_id,
                reference_date=ref,
                core_profile=core_profile,
                db=db,
            ),
        ),
        "knowledge_atoms_top_k": atoms,
        "interpretation_instances_top_k": [
            {
                "instance_id": row.get("instance_id"),
                "interpretation_ref_id": row.get("interpretation_ref_id"),
                "level": row.get("level"),
                "summary": str(row.get("summary") or "")[:200],
                "dominant_meaning": row.get("dominant_meaning"),
                "confirmation_required": bool(row.get("confirmation_required")),
                "evidence_count": row.get("evidence_count"),
                "user_verdict": row.get("user_verdict"),
            }
            for row in interpretation_instances
        ],
        "relationship_insights_top_k": _relationship_insights_top_k(db, user_id, limit=3),
        "confidence": apply_confidence_delta_30d(
            db,
            user_id=user_id,
            reference_date=ref,
            confidence=_confidence_v0(
                patterns=patterns,
                atom_count=len(atoms),
                has_explicit_today=has_explicit_today,
                identity=identity,
                themes=themes,
                behavioral=behavioral,
            ),
            commit_snapshot=True,
        ),
    }

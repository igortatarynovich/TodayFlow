"""Meaning patterns → inferred hypotheses (L3) and active knowledge (pattern gate v0).

Bridge: meaning_surface_patterns_v0 →
  · 3–6 signals → inferred_knowledge_v0 (hypothesis, needs confirm)
  · 7+ signals  → day_active_knowledge_v1 via knowledge candidate gate

Canon: USER_KNOWLEDGE_MODEL.md §4.2 · day_model P1.19–P1.20
"""

from __future__ import annotations

import logging
import re
from datetime import UTC, date, datetime
from typing import Any

from sqlalchemy.orm import Session

from todayflow_backend.services.day_model_v1_active_knowledge import (
    try_activate_knowledge_from_candidate_v1,
)
from todayflow_backend.services.day_model_v1_active_knowledge_loader import (
    upsert_user_active_knowledge_v1,
)
from todayflow_backend.services.day_model_v1_confirmed_pattern import (
    DAY_CONFIRMED_PATTERN_V1_CONTRACT,
    PATTERN_STATUS_CONFIRMED,
)
from todayflow_backend.services.day_model_v1_knowledge_candidate import (
    try_build_knowledge_candidate_from_pattern_v1,
)
from todayflow_backend.services.day_model_v1_pattern_candidate import (
    CANDIDATE_TYPE_ACTION_PREFERENCE,
    CANDIDATE_TYPE_SURFACE_PREFERENCE,
    CANDIDATE_TYPE_TEMPO_PREFERENCE,
)
from todayflow_backend.services.day_model_v1_surface_learning_signal import (
    SIGNAL_DIRECTION_POSITIVE,
)
from todayflow_backend.services.meaning_surface_patterns import (
    build_meaning_surface_patterns_v0,
)

logger = logging.getLogger(__name__)

INFERRED_KNOWLEDGE_V0_CONTRACT = "inferred_knowledge_v0"
INFERRED_STATUS_ACTIVE = "active"

HYPOTHESIS_MIN_COUNT = 3
PATTERN_MIN_COUNT = 7

MACHINE_CLAIM_PATTERN = re.compile(r"^[a-z_]+:[a-z0-9_.-]+$")

ALLOWED_INFERRED_CLAIM_PREFIXES = frozenset(
    {"behavior_hypothesis", "behavior_pattern", "interpretation_hypothesis"}
)


def _utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _sanitize(value: str) -> str:
    cleaned = value.strip().lower().replace(" ", "_")
    return re.sub(r"[^a-z0-9_.-]", "", cleaned)[:64]


def _confidence_for_count(count: int) -> float:
    return round(min(0.92, 0.62 + count * 0.04), 3)


def _evidence_ids(key: str, count: int) -> list[str]:
    return [f"msp:{key}:{i}" for i in range(max(1, count))]


def _rank_items(tags: dict[str, Any], field: str) -> list[dict[str, Any]]:
    raw = tags.get(field)
    return raw if isinstance(raw, list) else []


def _type_count(patterns: dict[str, Any], event_type: str) -> int:
    rows = patterns.get("by_event_type")
    if not isinstance(rows, list):
        return 0
    for row in rows:
        if isinstance(row, dict) and str(row.get("event_type")) == event_type:
            return int(row.get("count") or 0)
    return 0


def _derive_pattern_specs(patterns: dict[str, Any]) -> list[dict[str, Any]]:
    tags = patterns.get("tags") if isinstance(patterns.get("tags"), dict) else {}
    specs: list[dict[str, Any]] = []

    for item in _rank_items(tags, "top_mood_ids"):
        mood_id = _sanitize(str(item.get("id") or ""))
        count = int(item.get("count") or 0)
        if not mood_id or count < HYPOTHESIS_MIN_COUNT:
            continue
        specs.append(
            {
                "slug": f"ritual_mood_{mood_id}",
                "pattern_type": CANDIDATE_TYPE_TEMPO_PREFERENCE,
                "aggregation_key": f"ritual_mood_{mood_id}",
                "count": count,
                "summary": f"В ритуале часто отмечаешь состояние «{mood_id}» ({count} раз).",
            }
        )

    for item in _rank_items(tags, "top_head_topics"):
        topic_id = _sanitize(str(item.get("id") or ""))
        count = int(item.get("count") or 0)
        if not topic_id or count < HYPOTHESIS_MIN_COUNT:
            continue
        specs.append(
            {
                "slug": f"today_focus_{topic_id}",
                "pattern_type": CANDIDATE_TYPE_SURFACE_PREFERENCE,
                "aggregation_key": f"today_focus_{topic_id}",
                "count": count,
                "summary": f"Чаще смотришь на день через тему «{topic_id}» ({count} раз).",
            }
        )

    focus_count = int(tags.get("focus_sessions_started") or 0) or _type_count(patterns, "focus_started")
    if focus_count >= HYPOTHESIS_MIN_COUNT:
        specs.append(
            {
                "slug": "focus_session",
                "pattern_type": CANDIDATE_TYPE_ACTION_PREFERENCE,
                "aggregation_key": "focus_session",
                "count": focus_count,
                "summary": f"Регулярно отмечаешь старт фокуса на шаге дня ({focus_count} раз).",
            }
        )

    evening_count = int(tags.get("evening_reflections_submitted") or 0) or _type_count(
        patterns, "evening_reflection_submitted"
    )
    if evening_count >= HYPOTHESIS_MIN_COUNT:
        specs.append(
            {
                "slug": "evening_reflection",
                "pattern_type": CANDIDATE_TYPE_TEMPO_PREFERENCE,
                "aggregation_key": "evening_reflection",
                "count": evening_count,
                "summary": f"Закрываешь день рефлексией ({evening_count} раз за окно).",
            }
        )

    tarot_count = _type_count(patterns, "tarot_selected")
    if tarot_count >= HYPOTHESIS_MIN_COUNT:
        specs.append(
            {
                "slug": "today_tarot_ritual",
                "pattern_type": CANDIDATE_TYPE_SURFACE_PREFERENCE,
                "aggregation_key": "today_tarot_ritual",
                "count": tarot_count,
                "summary": f"Активно проходишь ритуал карты дня ({tarot_count} раз).",
            }
        )

    guidance_count = int(tags.get("guidance_questions_asked") or 0) or _type_count(patterns, "guidance_ask")
    if guidance_count >= HYPOTHESIS_MIN_COUNT:
        specs.append(
            {
                "slug": "guidance_questions",
                "pattern_type": CANDIDATE_TYPE_SURFACE_PREFERENCE,
                "aggregation_key": "guidance_questions",
                "count": guidance_count,
                "summary": f"Регулярно задаёшь вопросы в разделе «Вопросы» ({guidance_count} раз).",
            }
        )

    practice_count = int(tags.get("practices_completed") or 0) or _type_count(patterns, "practice_completed")
    if practice_count >= HYPOTHESIS_MIN_COUNT:
        specs.append(
            {
                "slug": "today_practice_completion",
                "pattern_type": CANDIDATE_TYPE_ACTION_PREFERENCE,
                "aggregation_key": "today_practice_completion",
                "count": practice_count,
                "summary": f"Завершаешь практики из Today ({practice_count} раз за окно).",
            }
        )

    ritual_prox = tags.get("ritual_proximity") if isinstance(tags.get("ritual_proximity"), dict) else {}
    for item in _rank_items(ritual_prox, "top_choices"):
        choice_id = _sanitize(str(item.get("id") or ""))
        count = int(item.get("count") or 0)
        if not choice_id or count < HYPOTHESIS_MIN_COUNT:
            continue
        specs.append(
            {
                "slug": f"ritual_proximity_{choice_id}",
                "pattern_type": CANDIDATE_TYPE_TEMPO_PREFERENCE,
                "aggregation_key": f"ritual_proximity_{choice_id}",
                "count": count,
                "summary": (
                    f"После символов дня чаще выбираешь шаг «{choice_id.replace('_', ' ')}» "
                    f"({count} раз)."
                ),
            }
        )

    day_promise_sets = int(tags.get("day_promise_sets") or 0)
    if day_promise_sets >= HYPOTHESIS_MIN_COUNT:
        specs.append(
            {
                "slug": "day_promise_habit",
                "pattern_type": CANDIDATE_TYPE_ACTION_PREFERENCE,
                "aggregation_key": "day_promise_habit",
                "count": day_promise_sets,
                "summary": f"Регулярно формулируешь обещание дня ({day_promise_sets} раз).",
            }
        )

    for item in _rank_items(tags, "top_honest_step_ids"):
        step_id = _sanitize(str(item.get("id") or ""))
        count = int(item.get("count") or 0)
        if not step_id or count < HYPOTHESIS_MIN_COUNT:
            continue
        specs.append(
            {
                "slug": f"honest_step_{step_id}",
                "pattern_type": CANDIDATE_TYPE_ACTION_PREFERENCE,
                "aggregation_key": f"honest_step_{step_id}",
                "count": count,
                "summary": (
                    f"Честный шаг дня чаще про «{step_id.replace('_', ' ')}» ({count} раз)."
                ),
            }
        )

    for item in _rank_items(tags, "top_guidance_themes"):
        theme_id = _sanitize(str(item.get("id") or ""))
        count = int(item.get("count") or 0)
        if not theme_id or count < HYPOTHESIS_MIN_COUNT:
            continue
        specs.append(
            {
                "slug": f"guidance_theme_{theme_id.replace(':', '_')}",
                "pattern_type": CANDIDATE_TYPE_SURFACE_PREFERENCE,
                "aggregation_key": f"guidance_theme_{theme_id}",
                "count": count,
                "summary": (
                    f"В вопросах повторяется тема «{theme_id.replace(':', ' / ')}» ({count} раз)."
                ),
            }
        )

    compat = tags.get("compatibility_engagement")
    if isinstance(compat, dict):
        echo_yes = int(compat.get("echo_yes") or 0)
        if echo_yes >= HYPOTHESIS_MIN_COUNT:
            specs.append(
                {
                    "slug": "compat_reading_resonates",
                    "pattern_type": CANDIDATE_TYPE_SURFACE_PREFERENCE,
                    "aggregation_key": "compat_reading_resonates",
                    "count": echo_yes,
                    "summary": (
                        f"Разборы совместимости часто попадают "
                        f"({echo_yes} отметок «точно»)."
                    ),
                }
            )
        echo_no = int(compat.get("echo_no") or 0)
        if echo_no >= HYPOTHESIS_MIN_COUNT:
            specs.append(
                {
                    "slug": "compat_reading_miss",
                    "pattern_type": CANDIDATE_TYPE_SURFACE_PREFERENCE,
                    "aggregation_key": "compat_reading_miss",
                    "count": echo_no,
                    "summary": (
                        f"Часто отмечает «мимо» в блоках совместимости ({echo_no} раз)."
                    ),
                }
            )
        for item in _rank_items(compat, "top_format_ids"):
            fmt = _sanitize(str(item.get("id") or ""))
            count = int(item.get("count") or 0)
            if fmt and count >= HYPOTHESIS_MIN_COUNT:
                specs.append(
                    {
                        "slug": f"compat_scenario_{fmt}",
                        "pattern_type": CANDIDATE_TYPE_SURFACE_PREFERENCE,
                        "aggregation_key": f"compat_scenario_{fmt}",
                        "count": count,
                        "summary": (
                            f"Чаще исследует совместимость через сценарий "
                            f"«{fmt}» ({count} раз)."
                        ),
                    }
                )
        deep_opens = int(compat.get("deep_opens") or 0)
        if deep_opens >= HYPOTHESIS_MIN_COUNT:
            specs.append(
                {
                    "slug": "compat_deep_reader",
                    "pattern_type": CANDIDATE_TYPE_SURFACE_PREFERENCE,
                    "aggregation_key": "compat_deep_reader",
                    "count": deep_opens,
                    "summary": f"Регулярно открывает глубокий разбор совместимости ({deep_opens} раз).",
                }
            )

    return specs


def _build_synthetic_confirmed_pattern(spec: dict[str, Any], *, window_days: int) -> dict[str, Any]:
    count = int(spec["count"])
    slug = str(spec["slug"])
    return {
        "contract_version": DAY_CONFIRMED_PATTERN_V1_CONTRACT,
        "pattern_id": f"pat-msp-{slug}",
        "source_pattern_candidate_id": f"pcand-msp-{slug}",
        "pattern_type": spec["pattern_type"],
        "aggregation_key": spec["aggregation_key"],
        "evidence_signal_ids": _evidence_ids(slug, count),
        "evidence_count": count,
        "evidence_window_days": max(PATTERN_MIN_COUNT, window_days),
        "confidence": _confidence_for_count(count),
        "direction": SIGNAL_DIRECTION_POSITIVE,
        "status": PATTERN_STATUS_CONFIRMED,
        "created_at": _utc_now_iso(),
        "expires_at": None,
        "memory_update_allowed": False,
        "profile_update_allowed": False,
        "ranking_update_allowed": False,
    }


def _build_inferred_payload(spec: dict[str, Any], *, window_days: int) -> dict[str, Any]:
    count = int(spec["count"])
    slug = _sanitize(str(spec["slug"]))
    prefix = "behavior_pattern" if count >= PATTERN_MIN_COUNT else "behavior_hypothesis"
    captured = _utc_now_iso()
    return {
        "contract_version": INFERRED_KNOWLEDGE_V0_CONTRACT,
        "knowledge_id": f"inf-{slug}",
        "knowledge_type": "pattern" if count >= PATTERN_MIN_COUNT else "hypothesis",
        "data_class": "inferred",
        "claim": f"{prefix}:{slug}",
        "value": slug,
        "summary": str(spec["summary"]),
        "confidence": _confidence_for_count(count),
        "evidence_count": count,
        "evidence_window_days": window_days,
        "evidence_signal_ids": _evidence_ids(slug, count),
        "confirmation_required": True,
        "confirmation_stage": "hypothesis",
        "status": INFERRED_STATUS_ACTIVE,
        "created_at": captured,
        "last_confirmed_at": captured,
        "captured_at": captured,
        "source": "meaning_surface_patterns_v0",
    }


def validate_inferred_knowledge_v0(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("contract_version") != INFERRED_KNOWLEDGE_V0_CONTRACT:
        errors.append("invalid contract_version")
    claim = payload.get("claim")
    if isinstance(claim, str):
        if " " in claim:
            errors.append("prose claim not allowed")
        if not MACHINE_CLAIM_PATTERN.match(claim):
            errors.append("claim must be machine-readable")
        prefix = claim.split(":", 1)[0]
        if prefix not in ALLOWED_INFERRED_CLAIM_PREFIXES:
            errors.append("claim prefix not allowed")
    if payload.get("confirmation_required") is not True:
        errors.append("confirmation_required must be true for inferred L3")
    return errors


def upsert_inferred_knowledge_v0(
    db: Session,
    *,
    user_id: int,
    payload: dict[str, Any],
    commit: bool = False,
) -> None:
    errors = validate_inferred_knowledge_v0(payload)
    if errors:
        raise ValueError("; ".join(errors))

    from todayflow_backend.db import models as db_models

    knowledge_id = str(payload["knowledge_id"])
    row = (
        db.query(db_models.UserActiveKnowledge)
        .filter(
            db_models.UserActiveKnowledge.user_id == user_id,
            db_models.UserActiveKnowledge.knowledge_id == knowledge_id,
        )
        .first()
    )
    if row is None:
        row = db_models.UserActiveKnowledge(
            user_id=user_id,
            knowledge_id=knowledge_id,
            status=INFERRED_STATUS_ACTIVE,
            payload=payload,
        )
        db.add(row)
    else:
        existing = row.payload if isinstance(row.payload, dict) else {}
        if existing.get("user_verdict") in {"confirm", "reject", "partial"}:
            return
        row.payload = payload
        row.status = INFERRED_STATUS_ACTIVE

    if commit:
        db.commit()
    else:
        db.flush()


def _existing_active_claims(db: Session, user_id: int) -> set[str]:
    from todayflow_backend.services.day_model_v1_active_knowledge_loader import (
        load_user_active_knowledge_list_v1,
    )
    from todayflow_backend.services.explicit_l1_knowledge_v0 import (
        load_user_explicit_l1_knowledge_v0,
    )

    claims: set[str] = set()
    for row in load_user_active_knowledge_list_v1(db, user_id, limit=100):
        claim = row.get("claim")
        if isinstance(claim, str):
            claims.add(claim)
    for row in load_user_explicit_l1_knowledge_v0(db, user_id, limit=100):
        claim = row.get("claim")
        if isinstance(claim, str):
            claims.add(claim)
    return claims


def _promote_stable_pattern(
    db: Session,
    *,
    user_id: int,
    spec: dict[str, Any],
    window_days: int,
    existing_claims: set[str],
) -> bool:
    confirmed = _build_synthetic_confirmed_pattern(spec, window_days=window_days)
    candidate_out = try_build_knowledge_candidate_from_pattern_v1(
        confirmed,
        knowledge_candidate_id=f"kcand-msp-{spec['slug']}",
        requires_review=True,
    )
    if candidate_out.get("result") != "created":
        return False

    candidate = candidate_out["knowledge_candidate"]
    claim = str(candidate.get("claim") or "")
    if claim in existing_claims:
        return False

    active_out = try_activate_knowledge_from_candidate_v1(
        candidate,
        review_approved=True,
        knowledge_id=f"know-msp-{spec['slug']}",
    )
    if active_out.get("result") != "activated":
        logger.info(
            "pattern promotion not activated user=%s slug=%s reasons=%s",
            user_id,
            spec.get("slug"),
            active_out.get("reasons"),
        )
        return False

    upsert_user_active_knowledge_v1(db, user_id=user_id, active_knowledge=active_out["active_knowledge"])
    existing_claims.add(claim)
    return True


def sync_meaning_derived_knowledge_v0(
    db: Session,
    *,
    user_id: int,
    reference_date: date | None = None,
    window_days: int = 28,
    commit: bool = True,
) -> dict[str, int]:
    """Promote behavioral patterns from meaning events. Returns counters."""
    ref = reference_date or date.today()
    patterns = build_meaning_surface_patterns_v0(
        db, user_id=user_id, reference_date=ref, window_days=window_days
    )
    if not patterns:
        return {"hypotheses": 0, "patterns": 0}

    specs = _derive_pattern_specs(patterns)
    existing_claims = _existing_active_claims(db, user_id)
    hypotheses = 0
    patterns_promoted = 0
    wd = int(patterns.get("window_days") or window_days)

    for spec in specs:
        count = int(spec["count"])
        if count >= PATTERN_MIN_COUNT:
            if _promote_stable_pattern(
                db,
                user_id=user_id,
                spec=spec,
                window_days=wd,
                existing_claims=existing_claims,
            ):
                patterns_promoted += 1
            continue

        try:
            upsert_inferred_knowledge_v0(
                db,
                user_id=user_id,
                payload=_build_inferred_payload(spec, window_days=wd),
                commit=False,
            )
            hypotheses += 1
        except ValueError as exc:
            logger.warning("skip inferred knowledge user=%s: %s", user_id, exc)

    if commit:
        db.commit()

    return {"hypotheses": hypotheses, "patterns": patterns_promoted}


def load_user_inferred_knowledge_v0(
    db: Session,
    user_id: int,
    *,
    limit: int = 20,
) -> list[dict[str, Any]]:
    from todayflow_backend.db import models as db_models

    rows = (
        db.query(db_models.UserActiveKnowledge)
        .filter(
            db_models.UserActiveKnowledge.user_id == user_id,
            db_models.UserActiveKnowledge.status == INFERRED_STATUS_ACTIVE,
        )
        .order_by(db_models.UserActiveKnowledge.updated_at.desc())
        .limit(max(1, min(limit, 100)))
        .all()
    )
    result: list[dict[str, Any]] = []
    for row in rows:
        payload = row.payload
        if not isinstance(payload, dict):
            continue
        if payload.get("contract_version") != INFERRED_KNOWLEDGE_V0_CONTRACT:
            continue
        if payload.get("user_verdict") in {"confirm", "reject", "partial"}:
            continue
        errors = validate_inferred_knowledge_v0(payload)
        if errors:
            continue
        result.append(payload)
    return result

"""Wire day_story_v1 → today_contract_v1 (single LLM path for GET /today/contract)."""

from __future__ import annotations

import logging
from datetime import date
from time import perf_counter
from typing import Any

from sqlalchemy.orm import Session

from todayflow_backend.api.morning_ritual import MorningRitualResponse
from todayflow_backend.core.llm_openai_compatible import (
    is_llm_chat_configured,
    resolve_default_chat_model,
)
from todayflow_backend.db import models as db_models
from todayflow_backend.db.models import User
from todayflow_backend.services.day_narrative_brief_v0 import build_day_narrative_brief_v0
from todayflow_backend.services.day_story_v1 import (
    DAY_STORY_PROMPT_VER,
    DAY_STORY_V1_CONTRACT,
    _DAY_STORY_SYS_RU,
    build_day_story_fallback_v1,
    build_day_story_llm_input,
    call_day_story_llm_v1,
    day_story_to_legacy_narrative,
    day_story_to_today_contract_v1,
    validate_day_story_v1,
)
from todayflow_backend.services.history_layer_v0 import build_history_layer_v0
from todayflow_backend.services.insight_depth import get_insight_depth_tier
from todayflow_backend.services.intent_slice_v0 import build_intent_layer_v0
from todayflow_backend.services.learning import get_learning_service
from todayflow_backend.services.meaning_surface_patterns import build_meaning_surface_patterns_v0
from todayflow_backend.services.today_contract_assembler_v1 import validate_today_contract_v1
from todayflow_backend.services.today_narrative import (
    _core_context_for_narrative,
    _intent_context_fingerprint,
    _latest_snapshot_id,
    _load_foundation_from_logs,
    _normalize_ritual_context,
    _ritual_context_fingerprint,
)

logger = logging.getLogger(__name__)

MODULE = "day_story_v1"
SURFACE = "day_story"


def _ritual_from_morning_and_connection(
    morning: MorningRitualResponse,
    dc_row: db_models.DayConnection | None,
) -> dict[str, Any]:
    ritual: dict[str, Any] = {}
    tarot = morning.tarot_card if isinstance(morning.tarot_card, dict) else {}
    if tarot.get("id") is not None:
        ritual["tarot_main_id"] = tarot.get("id")
    if tarot.get("name"):
        ritual["tarot_name_ru"] = tarot.get("name")
    num = morning.numerology_number if isinstance(morning.numerology_number, dict) else {}
    if num.get("value") is not None:
        ritual["numerology_value"] = num.get("value")
    if dc_row is not None and dc_row.morning_focus:
        ritual["head_topic"] = dc_row.morning_focus
    return _normalize_ritual_context(ritual)


def _load_cached_day_story(
    db: Session,
    *,
    user_id: int,
    target_date: date,
    ritual_fp: str,
    snapshot_id: int | None,
) -> tuple[dict[str, Any], int] | None:
    q = (
        db.query(db_models.GenerationLog)
        .filter(
            db_models.GenerationLog.user_id == user_id,
            db_models.GenerationLog.module == MODULE,
            db_models.GenerationLog.surface == SURFACE,
            db_models.GenerationLog.status.in_(("success", "fallback")),
        )
        .order_by(db_models.GenerationLog.created_at.desc())
    )
    if snapshot_id is not None:
        q = q.filter(db_models.GenerationLog.core_profile_snapshot_id == snapshot_id)
    for row in q.limit(12):
        ip = row.input_payload if isinstance(row.input_payload, dict) else {}
        if str(ip.get("target_date") or "") != target_date.isoformat():
            continue
        if ritual_fp and str(ip.get("ritual_context_fingerprint") or "") != ritual_fp:
            continue
        nr = row.normalized_response if isinstance(row.normalized_response, dict) else None
        if nr and nr.get("contract_version") == DAY_STORY_V1_CONTRACT:
            return nr, int(row.id)
    return None


def _build_day_story_record(
    db: Session,
    *,
    user: User,
    target_date: date,
    locale: str,
    fusion_dump: dict[str, Any],
    core_profile: dict[str, Any],
    ritual_norm: dict[str, Any],
    color: str = "",
    stone: str = "",
) -> tuple[dict[str, Any], int, bool]:
    """Load cached day_story or build via LLM/fallback. Returns (story, generation_log_id, used_fallback)."""
    learning = get_learning_service()
    locale_value = (locale or "ru").strip()[:32] or "ru"
    insight_tier = get_insight_depth_tier(user, db)
    snapshot_id = _latest_snapshot_id(db, user.id)
    ritual_fp = _ritual_context_fingerprint(ritual_norm)

    dc_row = (
        db.query(db_models.DayConnection)
        .filter(
            db_models.DayConnection.user_id == user.id,
            db_models.DayConnection.date == target_date,
        )
        .first()
    )

    head_from_ritual = str(ritual_norm.get("head_topic") or "").strip() or None
    intent_slice = build_intent_layer_v0(
        morning_intention=dc_row.morning_intention if dc_row else None,
        morning_focus=dc_row.morning_focus if dc_row else None,
        head_topic=head_from_ritual,
        question_of_day_answer=dc_row.question_of_day_answer if dc_row else None,
        quick_decision_answer=dc_row.quick_decision_answer if dc_row else None,
    )
    intent_fp = _intent_context_fingerprint(intent_slice)

    foundation = _load_foundation_from_logs(db, user.id, target_date, snapshot_id)
    scores_raw = fusion_dump.get("scores") if isinstance(fusion_dump, dict) else {}
    day_engine_brief = build_day_narrative_brief_v0(
        foundation=foundation,
        ritual=ritual_norm if ritual_norm else None,
        fusion_scores=scores_raw if isinstance(scores_raw, dict) else {},
        intent_slice=intent_slice,
        locale=locale_value,
    )

    behavior_patterns = build_meaning_surface_patterns_v0(
        db, user_id=user.id, reference_date=target_date, window_days=28
    )
    user_core = _core_context_for_narrative(core_profile, locale=locale_value)
    rhythm_context = (
        fusion_dump.get("rhythm_context")
        if isinstance(fusion_dump.get("rhythm_context"), dict)
        else {}
    )

    cached = _load_cached_day_story(
        db,
        user_id=user.id,
        target_date=target_date,
        ritual_fp=ritual_fp,
        snapshot_id=snapshot_id,
    )
    used_fallback = False
    gen_id: int
    started = perf_counter()

    if cached is not None:
        story, gen_id = cached
        used_fallback = False
    else:
        llm_input = build_day_story_llm_input(
            day_engine_brief=day_engine_brief,
            ritual_context=ritual_norm,
            user_core_slim=user_core,
            intent_slice=intent_slice,
            behavior_patterns=behavior_patterns,
            rhythm_context=rhythm_context,
            color=color,
            stone=stone,
            locale=locale_value,
        )
        llm_input["insight_depth_tier"] = insight_tier
        llm_input["daily_foundation"] = foundation
        today_scores = scores_raw if isinstance(scores_raw, dict) else {}
        history_slice = build_history_layer_v0(
            db,
            user_id=user.id,
            target_date=target_date,
            today_fusion_scores=today_scores,
        )
        if history_slice:
            llm_input["day_history"] = history_slice

        story = call_day_story_llm_v1(llm_input, locale=locale_value)
        used_fallback = story is None
        if story is None:
            story = build_day_story_fallback_v1(
                day_engine_brief=day_engine_brief,
                color=color,
                stone=stone,
                locale=locale_value,
            )

        story_errors = validate_day_story_v1(story)
        if story_errors:
            logger.warning("day_story_v1 validation failed, using fallback: %s", story_errors)
            story = build_day_story_fallback_v1(
                day_engine_brief=day_engine_brief,
                color=color,
                stone=stone,
                locale=locale_value,
            )
            used_fallback = True

        pv = learning.get_or_create_prompt_version(
            db,
            module=MODULE,
            version=DAY_STORY_PROMPT_VER,
            prompt_kind="system",
            prompt_text=_DAY_STORY_SYS_RU,
            label="day_story_v1",
            metadata={"contract": DAY_STORY_V1_CONTRACT},
        )
        input_payload: dict[str, Any] = {
            "target_date": target_date.isoformat(),
            "locale": locale_value,
            "insight_depth_tier": insight_tier,
            "ritual_context_fingerprint": ritual_fp,
            "intent_context_fingerprint": intent_fp,
            "day_engine_brief_contract": day_engine_brief.get("contract_version"),
            "contract": DAY_STORY_V1_CONTRACT,
            "prompt_version": DAY_STORY_PROMPT_VER,
            "llm_input_keys": sorted(llm_input.keys()),
        }
        gen = learning.log_generation(
            db,
            module=MODULE,
            surface=SURFACE,
            user_id=user.id,
            core_profile_snapshot_id=snapshot_id,
            prompt_version_id=pv.id,
            model=resolve_default_chat_model()
            if is_llm_chat_configured() and not used_fallback
            else None,
            locale=locale_value,
            input_payload=input_payload,
            system_prompt=_DAY_STORY_SYS_RU[:2000],
            normalized_response=story,
            status="success" if not used_fallback else "fallback",
            used_fallback=used_fallback,
            duration_ms=int((perf_counter() - started) * 1000),
        )
        gen_id = gen.id

    return story, gen_id, used_fallback


def build_day_story_v1_wire(
    db: Session,
    *,
    user: User,
    target_date: date,
    locale: str,
    morning: MorningRitualResponse,
    fusion_dump: dict[str, Any],
    core_profile: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any], int]:
    """
    Build day_story_v1 and today_contract_v1 from one narrative source.

    Returns (contract, legacy_narrative_surfaces, generation_log_id).
    """
    dc_row = (
        db.query(db_models.DayConnection)
        .filter(
            db_models.DayConnection.user_id == user.id,
            db_models.DayConnection.date == target_date,
        )
        .first()
    )
    ritual_norm = _ritual_from_morning_and_connection(morning, dc_row)
    recs = morning.daily_recommendations if isinstance(morning.daily_recommendations, dict) else {}
    color = str(recs.get("lucky_color") or "") if recs else ""
    stone = str(recs.get("lucky_stone") or "") if recs else ""

    story, gen_id, _ = _build_day_story_record(
        db,
        user=user,
        target_date=target_date,
        locale=locale,
        fusion_dump=fusion_dump,
        core_profile=core_profile,
        ritual_norm=ritual_norm,
        color=color,
        stone=stone,
    )

    contract = day_story_to_today_contract_v1(
        story,
        generation_id=str(gen_id),
        progress={},
    )
    contract_errors = validate_today_contract_v1(contract)
    if contract_errors:
        logger.error("today_contract_v1 from day_story failed validation: %s", contract_errors)
        raise ValueError(f"today_contract_v1 invalid: {contract_errors}")

    narrative = day_story_to_legacy_narrative(story, generation_id=str(gen_id))
    return contract, narrative, gen_id


def resolve_narrative_surface_via_day_story_v1(
    db: Session,
    *,
    user_id: int,
    surface: str,
    target_date: date,
    locale: str,
    core_profile: dict[str, Any] | None,
    fusion_dump: dict[str, Any],
    ritual_norm: dict[str, Any],
    parent_generation_id: int | None = None,
    build_if_missing: bool = False,
) -> tuple[dict[str, Any], int, bool] | None:
    """
    Derive legacy narrative surface payload from day_story_v1 (no extra LLM).

    guide: builds day_story when build_if_missing; child surfaces derive from cached/parent day_story.
    """
    surface_norm = (surface or "").strip().lower()
    if surface_norm not in ("guide", "spheres", "day_layer", "evening"):
        return None

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        return None

    story: dict[str, Any] | None = None
    gen_id: int | None = None
    used_fallback = False

    if parent_generation_id is not None:
        parent = (
            db.query(db_models.GenerationLog)
            .filter(
                db_models.GenerationLog.id == parent_generation_id,
                db_models.GenerationLog.user_id == user_id,
            )
            .first()
        )
        if parent and parent.module == MODULE:
            nr = parent.normalized_response if isinstance(parent.normalized_response, dict) else None
            if nr and nr.get("contract_version") == DAY_STORY_V1_CONTRACT:
                story = nr
                gen_id = int(parent.id)
                used_fallback = bool(parent.used_fallback)

    if story is None:
        ritual_fp = _ritual_context_fingerprint(ritual_norm)
        snapshot_id = _latest_snapshot_id(db, user_id)
        cached = _load_cached_day_story(
            db,
            user_id=user_id,
            target_date=target_date,
            ritual_fp=ritual_fp,
            snapshot_id=snapshot_id,
        )
        if cached is not None:
            story, gen_id = cached
        elif build_if_missing and surface_norm == "guide":
            story, gen_id, used_fallback = _build_day_story_record(
                db,
                user=user,
                target_date=target_date,
                locale=locale,
                fusion_dump=fusion_dump,
                core_profile=core_profile if isinstance(core_profile, dict) else {},
                ritual_norm=ritual_norm,
            )
        else:
            return None

    narrative = day_story_to_legacy_narrative(story, generation_id=str(gen_id))
    surf = narrative.get(surface_norm)
    if not isinstance(surf, dict):
        return None
    payload = surf.get("payload") if isinstance(surf.get("payload"), dict) else surf
    if not isinstance(payload, dict):
        return None
    return payload, int(gen_id), used_fallback

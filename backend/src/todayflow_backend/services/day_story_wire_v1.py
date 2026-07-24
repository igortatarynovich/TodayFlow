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
from todayflow_backend.services.day_narrative_brief_v0 import (
    build_day_narrative_brief_v0,
    slim_day_engine_brief_for_story_llm,
)
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
from todayflow_backend.services.day_story_interpretation_v1 import (
    build_day_story_interpretation_v1,
)
from todayflow_backend.services.history_layer_v0 import build_history_layer_v0
from todayflow_backend.services.insight_depth import get_insight_depth_tier
from todayflow_backend.services.intent_slice_v0 import build_intent_layer_v0
from todayflow_backend.services.learning import get_learning_service
from todayflow_backend.services.meaning_surface_patterns import build_meaning_surface_patterns_v0
from todayflow_backend.services.today_contract_assembler_v1 import validate_today_contract_v1
from todayflow_backend.services.experience_contract_assembler_v0 import (
    assemble_experience_slice,
    slice_log_fields,
)
from todayflow_backend.services.today_narrative import (
    _intent_context_fingerprint,
    _latest_snapshot_id,
    _load_foundation_from_logs,
    _normalize_ritual_context,
    _ritual_context_fingerprint,
)

logger = logging.getLogger(__name__)

MODULE = "day_story_v1"
SURFACE = "day_story"


def _daily_symbols_from_morning(
    morning: MorningRitualResponse | None,
) -> tuple[str, str, dict[str, Any], dict[str, Any], dict[str, Any]]:
    """Prefer celestial daily_symbols over legacy lucky_* recommendation keys."""
    ce: dict[str, Any] = {}
    if morning is not None and isinstance(getattr(morning, "celestial_events", None), dict):
        ce = morning.celestial_events or {}
    symbols = ce.get("daily_symbols") if isinstance(ce.get("daily_symbols"), dict) else {}
    color_sym = symbols.get("color") if isinstance(symbols.get("color"), dict) else {}
    stone_sym = symbols.get("stone") if isinstance(symbols.get("stone"), dict) else {}
    recs = (
        morning.daily_recommendations
        if morning is not None and isinstance(morning.daily_recommendations, dict)
        else {}
    )
    color = str(color_sym.get("name") or (recs.get("lucky_color") if recs else "") or "").strip()
    stone = str(stone_sym.get("name") or (recs.get("lucky_stone") if recs else "") or "").strip()
    return color, stone, color_sym, stone_sym, ce


def _ritual_from_morning_and_connection(
    morning: MorningRitualResponse,
    dc_row: db_models.DayConnection | None,
) -> dict[str, Any]:
    """Only revealed card/number from morning payloads (already redacted by SoT)."""
    from todayflow_backend.services.day_symbol_state_v1 import ritual_context_from_symbol_view

    # Morning payloads are redacted views; rebuild a mini view for ritual_context.
    tarot = morning.tarot_card if isinstance(morning.tarot_card, dict) else {}
    num = morning.numerology_number if isinstance(morning.numerology_number, dict) else {}
    mini_view = {
        "card": {
            "revealed": tarot.get("selection_status") == "selected" or tarot.get("status") in ("revealed", "ready"),
            "id": tarot.get("id"),
            "name": tarot.get("name"),
        },
        "number": {
            "revealed": num.get("selection_status") == "selected" or num.get("status") in ("revealed", "ready"),
            "reduced_value": num.get("reduced_value") if num.get("value") is None else num.get("value"),
        },
    }
    ritual = ritual_context_from_symbol_view(mini_view)
    if dc_row is not None and dc_row.morning_focus:
        ritual["head_topic"] = dc_row.morning_focus
    return _normalize_ritual_context(ritual)


def _load_cached_day_story(
    db: Session,
    *,
    user_id: int,
    target_date: date,
    day_story_fingerprint: str | None = None,
    ritual_fp: str | None = None,
    snapshot_id: int | None = None,
    any_for_date: bool = False,
) -> tuple[dict[str, Any], int, str | None] | None:
    """Returns (story, generation_log_id, fingerprint) or None."""
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
    if snapshot_id is not None and not any_for_date:
        q = q.filter(db_models.GenerationLog.core_profile_snapshot_id == snapshot_id)
    for row in q.limit(20):
        ip = row.input_payload if isinstance(row.input_payload, dict) else {}
        if str(ip.get("target_date") or "") != target_date.isoformat():
            continue
        stored_fp = str(ip.get("day_story_fingerprint") or "") or None
        if not any_for_date:
            if day_story_fingerprint:
                if stored_fp != day_story_fingerprint:
                    continue
            elif ritual_fp and str(ip.get("ritual_context_fingerprint") or "") != ritual_fp:
                continue
        # Literary editor bump must not keep serving checklist-era prose.
        if str(ip.get("prompt_version") or "") != DAY_STORY_PROMPT_VER:
            continue
        nr = row.normalized_response if isinstance(row.normalized_response, dict) else None
        if nr and nr.get("contract_version") == DAY_STORY_V1_CONTRACT:
            from todayflow_backend.services.day_story_phrase_gate_v1 import day_story_passes_phrase_gate

            ok_phrase, _hits = day_story_passes_phrase_gate(nr)
            if not ok_phrase:
                continue
            return nr, int(row.id), stored_fp
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
    celestial_events: dict[str, Any] | None = None,
    color_symbol: dict[str, Any] | None = None,
    stone_symbol: dict[str, Any] | None = None,
    force_rebuild: bool = False,
    expected_fingerprint: str | None = None,
    fingerprint_payload: dict[str, Any] | None = None,
    timezone_name: str = "UTC",
    commit_story_state: bool = True,
) -> tuple[dict[str, Any], int, bool]:
    """Load cached day_story or build via LLM/fallback. Returns (story, generation_log_id, used_fallback)."""
    from todayflow_backend.services.day_story_fingerprint_v1 import (
        compute_expected_day_story_fingerprint,
    )
    from todayflow_backend.services.day_story_refresh_v1 import ensure_story_state
    from todayflow_backend.services.day_sources.inputs_from_profile import (
        birth_date_from_core_profile,
        birth_name_from_core_profile,
        birth_place_from_core_profile,
        birth_time_from_core_profile,
        geo_from_core_profile,
    )
    from todayflow_backend.services.day_symbol_state_v1 import owner_key_for_user

    learning = get_learning_service()
    locale_value = (locale or "ru").strip()[:32] or "ru"
    insight_tier = get_insight_depth_tier(user, db)
    snapshot_id = _latest_snapshot_id(db, user.id)
    ritual_fp = _ritual_context_fingerprint(ritual_norm)
    owner_key = owner_key_for_user(user.id)
    color_sym = color_symbol if isinstance(color_symbol, dict) else {}
    stone_sym = stone_symbol if isinstance(stone_symbol, dict) else {}
    ce = celestial_events if isinstance(celestial_events, dict) else {}
    profile = core_profile if isinstance(core_profile, dict) else None
    birth_date = birth_date_from_core_profile(profile)
    birth_time = birth_time_from_core_profile(profile)
    birth_lat, birth_lon = birth_place_from_core_profile(profile)
    lat, lon, profile_tz = geo_from_core_profile(profile)
    geo_timezone = profile_tz or timezone_name or None
    birth_name = birth_name_from_core_profile(profile)

    if expected_fingerprint is None or fingerprint_payload is None:
        expected_fingerprint, fingerprint_payload = compute_expected_day_story_fingerprint(
            db,
            user_id=int(user.id),
            owner_key=owner_key,
            local_date=target_date,
            timezone_name=timezone_name,
            locale=locale_value,
            celestial_events=ce or None,
            color_name=color or None,
            stone_name=stone or None,
        )

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
    user_core = assemble_experience_slice(
        core_profile if isinstance(core_profile, dict) else None,
        experience_id="today",
    )
    rhythm_context = (
        fusion_dump.get("rhythm_context")
        if isinstance(fusion_dump.get("rhythm_context"), dict)
        else {}
    )

    cached = None
    if not force_rebuild:
        cached = _load_cached_day_story(
            db,
            user_id=user.id,
            target_date=target_date,
            day_story_fingerprint=expected_fingerprint,
            ritual_fp=ritual_fp,
            snapshot_id=snapshot_id,
            any_for_date=False,
        )
    used_fallback = False
    gen_id: int
    started = perf_counter()

    if cached is not None:
        story, gen_id, _ = cached
        used_fallback = False
        if commit_story_state:
            state = ensure_story_state(
                db,
                owner_key=owner_key,
                local_date=target_date,
                timezone_name=timezone_name,
                locale=locale_value,
                user_id=int(user.id),
            )
            if state.fingerprint == expected_fingerprint:
                state.expected_fingerprint = expected_fingerprint
                state.stale = False
                state.last_generation_log_id = gen_id
                db.add(state)
                db.commit()
    else:
        # Guard: unrevealed symbols must not appear in LLM input.
        safe_ritual = {
            k: v
            for k, v in (ritual_norm or {}).items()
            if k
            in (
                "tarot_main_id",
                "tarot_name_ru",
                "numerology_value",
                "head_topic",
                "mood",
                "electional_requested",
                "electional_time",
                "electional_question",
            )
            and v not in (None, "", [])
        }
        story_brief = slim_day_engine_brief_for_story_llm(
            day_engine_brief,
            ritual_has_card=bool(safe_ritual.get("tarot_main_id") or safe_ritual.get("tarot_name_ru")),
            ritual_has_number=safe_ritual.get("numerology_value") is not None,
        )
        interpretation = build_day_story_interpretation_v1(
            day_engine_brief=day_engine_brief,
            ritual_context=safe_ritual,
            intent_slice=intent_slice,
            rhythm_context=rhythm_context,
            color=color,
            stone=stone,
            celestial_events=ce or None,
            color_symbol=color_sym or None,
            stone_symbol=stone_sym or None,
            fingerprint=expected_fingerprint,
            locale=locale_value,
            target_date=target_date,
            birth_date=birth_date,
            birth_time=birth_time,
            birth_lat=birth_lat,
            birth_lon=birth_lon,
            lat=lat,
            lon=lon,
            timezone=geo_timezone,
            birth_name=birth_name,
        )
        llm_input = build_day_story_llm_input(
            day_engine_brief=story_brief,
            ritual_context=safe_ritual,
            user_core_slim=user_core,
            intent_slice=intent_slice,
            behavior_patterns=behavior_patterns,
            rhythm_context=rhythm_context,
            color=color,
            stone=stone,
            locale=locale_value,
            interpretation=interpretation,
            celestial_events=ce or None,
            color_symbol=color_sym or None,
            stone_symbol=stone_sym or None,
            target_date=target_date,
            birth_date=birth_date,
        )
        llm_input["insight_depth_tier"] = insight_tier
        llm_input["daily_foundation"] = foundation
        llm_input["day_story_fingerprint"] = expected_fingerprint
        today_scores = scores_raw if isinstance(scores_raw, dict) else {}
        history_slice = build_history_layer_v0(
            db,
            user_id=user.id,
            target_date=target_date,
            today_fusion_scores=today_scores,
        )
        if history_slice:
            llm_input["day_history"] = history_slice

        # P0: GET /today/contract must not block on Nebius. Prefer deterministic story;
        # LLM remaining available via force_rebuild / refresh paths later.
        if force_rebuild and is_llm_chat_configured():
            story = call_day_story_llm_v1(
                llm_input, locale=locale_value, interpretation=interpretation
            )
            used_fallback = story is None
        else:
            story = None
            used_fallback = True
        if story is None:
            story = build_day_story_fallback_v1(
                day_engine_brief=day_engine_brief,
                color=color,
                stone=stone,
                locale=locale_value,
                interpretation=interpretation,
                fingerprint=expected_fingerprint,
                ritual_context=safe_ritual,
                intent_slice=intent_slice,
                celestial_events=ce or None,
                color_symbol=color_sym or None,
                stone_symbol=stone_sym or None,
                target_date=target_date,
                birth_date=birth_date,
            )

        story_errors = validate_day_story_v1(story)
        if story_errors:
            logger.warning("day_story_v1 validation failed, using fallback: %s", story_errors)
            story = build_day_story_fallback_v1(
                day_engine_brief=day_engine_brief,
                color=color,
                stone=stone,
                locale=locale_value,
                interpretation=interpretation,
                fingerprint=expected_fingerprint,
                ritual_context=safe_ritual,
                intent_slice=intent_slice,
                celestial_events=ce or None,
                color_symbol=color_sym or None,
                stone_symbol=stone_sym or None,
                target_date=target_date,
                birth_date=birth_date,
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
            "day_story_fingerprint": expected_fingerprint,
            "day_story_fingerprint_payload": fingerprint_payload,
            "day_engine_brief_contract": day_engine_brief.get("contract_version"),
            "contract": DAY_STORY_V1_CONTRACT,
            "prompt_version": DAY_STORY_PROMPT_VER,
            "llm_input_keys": sorted(llm_input.keys()),
            **slice_log_fields(user_core),
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
        if commit_story_state:
            state = ensure_story_state(
                db,
                owner_key=owner_key,
                local_date=target_date,
                timezone_name=timezone_name,
                locale=locale_value,
                user_id=int(user.id),
            )
            state.fingerprint = expected_fingerprint
            state.expected_fingerprint = expected_fingerprint
            state.stale = False
            state.last_generation_log_id = gen_id
            db.add(state)
            db.commit()

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
    timezone_name: str = "UTC",
    allow_rebuild_on_miss: bool = True,
) -> tuple[dict[str, Any], dict[str, Any], int]:
    """
    Build day_story_v1 and today_contract_v1 from one narrative source.

    GET path: serve matching fingerprint cache, or last story if stale (no silent rebuild),
    or first-time build when missing and allow_rebuild_on_miss.

    Returns (contract, legacy_narrative_surfaces, generation_log_id).
    """
    from todayflow_backend.services.day_story_fingerprint_v1 import (
        compute_expected_day_story_fingerprint,
    )
    from todayflow_backend.services.day_story_refresh_v1 import (
        ensure_story_state,
        load_story_by_log_id,
        story_progress_meta,
    )
    from todayflow_backend.services.day_symbol_state_v1 import owner_key_for_user

    dc_row = (
        db.query(db_models.DayConnection)
        .filter(
            db_models.DayConnection.user_id == user.id,
            db_models.DayConnection.date == target_date,
        )
        .first()
    )
    ritual_norm = _ritual_from_morning_and_connection(morning, dc_row)
    color, stone, color_sym, stone_sym, ce = _daily_symbols_from_morning(morning)
    locale_value = (locale or "ru").strip()[:32] or "ru"
    owner_key = owner_key_for_user(user.id)
    expected_fp, fp_payload = compute_expected_day_story_fingerprint(
        db,
        user_id=int(user.id),
        owner_key=owner_key,
        local_date=target_date,
        timezone_name=timezone_name,
        locale=locale_value,
        celestial_events=ce or None,
        color_name=color or None,
        stone_name=stone or None,
    )
    ritual_fp = _ritual_context_fingerprint(ritual_norm)
    snapshot_id = _latest_snapshot_id(db, user.id)

    matched = _load_cached_day_story(
        db,
        user_id=user.id,
        target_date=target_date,
        day_story_fingerprint=expected_fp,
        ritual_fp=ritual_fp,
        snapshot_id=snapshot_id,
        any_for_date=False,
    )
    story: dict[str, Any] | None = None
    gen_id = 0
    if matched is not None:
        story, gen_id, _ = matched
        state = ensure_story_state(
            db,
            owner_key=owner_key,
            local_date=target_date,
            timezone_name=timezone_name,
            locale=locale_value,
            user_id=int(user.id),
        )
        state.fingerprint = expected_fp
        state.expected_fingerprint = expected_fp
        state.stale = False
        state.last_generation_log_id = gen_id
        db.add(state)
        db.commit()
    else:
        # Stale path: return last valid story without rebuilding on GET.
        state = ensure_story_state(
            db,
            owner_key=owner_key,
            local_date=target_date,
            timezone_name=timezone_name,
            locale=locale_value,
            user_id=int(user.id),
        )
        state.expected_fingerprint = expected_fp
        if state.fingerprint and state.fingerprint != expected_fp:
            state.stale = True
        db.add(state)
        db.commit()
        last = load_story_by_log_id(db, state.last_generation_log_id)
        if last is None:
            any_row = _load_cached_day_story(
                db,
                user_id=user.id,
                target_date=target_date,
                any_for_date=True,
            )
            if any_row is not None:
                last, gen_id, _ = any_row
                state.last_generation_log_id = gen_id
                state.stale = True
                db.add(state)
                db.commit()
        else:
            gen_id = int(state.last_generation_log_id or 0)
        if last is not None:
            story = last
        elif allow_rebuild_on_miss:
            story, gen_id, _ = _build_day_story_record(
                db,
                user=user,
                target_date=target_date,
                locale=locale_value,
                fusion_dump=fusion_dump,
                core_profile=core_profile,
                ritual_norm=ritual_norm,
                color=color,
                stone=stone,
                celestial_events=ce or None,
                color_symbol=color_sym or None,
                stone_symbol=stone_sym or None,
                force_rebuild=False,
                expected_fingerprint=expected_fp,
                fingerprint_payload=fp_payload,
                timezone_name=timezone_name,
            )
        else:
            raise ValueError("day_story_missing")

    assert story is not None
    progress = story_progress_meta(db, owner_key=owner_key, local_date=target_date)
    contract = day_story_to_today_contract_v1(
        story,
        generation_id=str(gen_id),
        progress=progress,
    )
    contract_errors = validate_today_contract_v1(contract)
    if contract_errors:
        logger.error("today_contract_v1 from day_story failed validation: %s", contract_errors)
        raise ValueError(f"today_contract_v1 invalid: {contract_errors}")

    narrative = day_story_to_legacy_narrative(story, generation_id=str(gen_id))
    return contract, narrative, gen_id


def build_day_story_record_for_refresh(
    db: Session,
    *,
    user: User,
    target_date: date,
    locale: str,
    morning: MorningRitualResponse,
    fusion_dump: dict[str, Any],
    core_profile: dict[str, Any],
    force_rebuild: bool = True,
    expected_fingerprint: str | None = None,
    fingerprint_payload: dict[str, Any] | None = None,
    timezone_name: str = "UTC",
) -> tuple[dict[str, Any], int, bool]:
    """Explicit rebuild entry used by POST /today/story/refresh."""
    dc_row = (
        db.query(db_models.DayConnection)
        .filter(
            db_models.DayConnection.user_id == user.id,
            db_models.DayConnection.date == target_date,
        )
        .first()
    )
    ritual_norm = _ritual_from_morning_and_connection(morning, dc_row)
    color, stone, color_sym, stone_sym, ce = _daily_symbols_from_morning(morning)
    return _build_day_story_record(
        db,
        user=user,
        target_date=target_date,
        locale=locale,
        fusion_dump=fusion_dump,
        core_profile=core_profile,
        ritual_norm=ritual_norm,
        color=color,
        stone=stone,
        celestial_events=ce or None,
        color_symbol=color_sym or None,
        stone_symbol=stone_sym or None,
        force_rebuild=force_rebuild,
        expected_fingerprint=expected_fingerprint,
        fingerprint_payload=fingerprint_payload,
        timezone_name=timezone_name,
        commit_story_state=False,
    )


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
            any_for_date=True,
        )
        if cached is not None:
            story, gen_id, _ = cached
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

"""Связанные тексты экрана «Сегодня»: генерация через LLM с кэшем и parent_generation_id."""

from __future__ import annotations

import hashlib
import json
import logging
import re
from datetime import date
from time import perf_counter
from typing import Any, Literal

from sqlalchemy.orm import Session

from todayflow_backend.core.config import settings
from todayflow_backend.core.llm_openai_compatible import (
    chat_completion_plain,
    get_openai_compatible_client,
    is_llm_chat_configured,
    resolve_default_chat_model,
    resolve_max_tokens,
)
from todayflow_backend.db import models as db_models
from todayflow_backend.services.day_context import build_day_context_v0
from todayflow_backend.services.generation_orchestrator import (
    MERGE_PASS_CONTRACT,
    NARRATIVE_OUTCOME_CONTRACT,
    ORCHESTRATOR_VERSION,
    PIPELINE_TODAY_NARRATIVE,
    attach_narrative_outcome_to_orchestration,
    attach_semantic_quality_to_orchestration,
    attach_amll_gate_to_orchestration,
    build_today_narrative_orchestration_meta,
    narrative_merge_pass_plan,
    record_guide_funnel_step_handoffs,
)
from todayflow_backend.profile_engine.selector import narrative_surface_to_selector_params
from todayflow_backend.services.day_model_v0 import build_day_model_v0
from todayflow_backend.services.day_narrative_brief_v0 import build_day_narrative_brief_v0
from todayflow_backend.services.profile_prompt_slices_v0 import build_internal_profile_slice_v0
from todayflow_backend.services.learning import get_learning_service
from todayflow_backend.services.ritual_cue_sanitize import (
    is_ru_abstract_topic_headline,
    strip_llm_meta_commentary,
    strip_meta_from_guide_payload,
)
from todayflow_backend.services.intent_slice_v0 import build_intent_layer_v0
from todayflow_backend.services.meaning_surface_patterns import build_meaning_surface_patterns_v0
from todayflow_backend.services.guide_flow_signals import GUIDE_MEANING_COMPLETION_EVENT_TYPES
from todayflow_backend.services.history_layer_v0 import build_history_layer_v0
from todayflow_backend.services.guide_narrative_funnel_v0 import (
    CORE_CONTRACT,
    FUNNEL_CONTRACT,
    FUNNEL_CHILD_CHAIN_CONTRACT,
    FUNNEL_PROMPT_VER_STEP1,
    FUNNEL_PROMPT_VER_STEP2,
    FUNNEL_PROMPT_VER_STEP3,
    SATELLITES_CONTRACT,
    funnel_openai_json_adapter,
    funnel_system_prompts_for_locale,
    is_funnel_core_text_valid,
    is_funnel_interpretation_valid,
    is_funnel_satellites_valid,
    run_guide_narrative_funnel_v0,
    slim_funnel_interpretation_for_child,
)
from todayflow_backend.services.llm_quality_policy_v1 import (
    funnel_step_max_tokens,
    quality_policy_snapshot,
    user_json_char_budget,
)
from todayflow_backend.services.surface_disclosure_funnel_v0 import (
    run_surface_disclosure_funnel_v0,
    surface_funnel_openai_json_adapter,
)
from todayflow_backend.services.guide_contract_v2 import (
    attach_guide_contract_v2,
    guide_funnel_core_is_llm_locked,
)

logger = logging.getLogger(__name__)

# Порядок отдачи life_areas в компактный контекст для LLM (PM-1: девять сфер + запас под расширения).
_LIFE_AREA_CONTEXT_ORDER = (
    "love",
    "career",
    "money",
    "family",
    "sex",
    "kids",
    "body",
    "friends",
    "decisions",
)


def _ordered_life_area_entries(la: dict[str, Any]) -> list[tuple[str, Any]]:
    seen: set[str] = set()
    out: list[tuple[str, Any]] = []
    for k in _LIFE_AREA_CONTEXT_ORDER:
        if k in la:
            out.append((k, la[k]))
            seen.add(k)
    for k, v in la.items():
        if k not in seen:
            out.append((k, v))
    return out


MODULE = "today_narrative"
PROMPT_VER = "today-narrative-v18"
# Записи кэша без `prompt_label` в input_payload — до добавления версии в ключ (старее v13).
_LEGACY_NARRATIVE_CACHE_PROMPT_LABEL = "today-narrative-v12"
# O2: явный primary в HTTP-ответе guide (см. `primary_narrative_anchor` в orchestration-логе).
NARRATIVE_HIERARCHY_CONTRACT_V0 = "narrative_hierarchy_v0"

TodaySurface = Literal["guide", "day_layer", "spheres", "evening", "deepen"]


def _narrative_hierarchy_meta_for_guide() -> dict[str, Any]:
    """Один канонический якорь «ядра дня» для клиентов; headline/subline — выравнивание поверх него."""
    return {
        "contract_version": NARRATIVE_HIERARCHY_CONTRACT_V0,
        "primary_anchor": "day_engine_brief",
    }


def _attach_narrative_hierarchy_to_guide_payload(payload: dict[str, Any]) -> None:
    payload["narrative_hierarchy"] = _narrative_hierarchy_meta_for_guide()


def _meaning_patterns_from_core(core_profile: dict[str, Any] | None) -> dict[str, Any] | None:
    """Срез агрегатов из `core_profile.living.learning_context`, если профиль уже собран с DE-5."""
    if not isinstance(core_profile, dict):
        return None
    living = core_profile.get("living")
    if not isinstance(living, dict):
        return None
    lc = living.get("learning_context")
    if not isinstance(lc, dict):
        return None
    msp = lc.get("meaning_surface_patterns")
    if not isinstance(msp, dict) or not msp.get("total_events"):
        return None
    return msp


def _normalize_ritual_context(rc: dict[str, Any] | None) -> dict[str, Any]:
    """Сжатый словарь для промпта и ключа кэша (любой surface, если клиент передал ritual_context)."""
    if not rc or not isinstance(rc, dict):
        return {}
    out: dict[str, Any] = {}
    tid = rc.get("tarot_main_id")
    if isinstance(tid, int) and tid > 0:
        out["tarot_main_id"] = tid
    tname = str(rc.get("tarot_name_ru") or "").strip()
    if tname:
        out["tarot_name_ru"] = tname[:160]
    nv = str(rc.get("numerology_value") or "").strip()
    if nv:
        out["numerology_value"] = nv[:24]
    mood = str(rc.get("mood") or "").strip()
    if mood:
        out["mood"] = mood[:80]
    ht = str(rc.get("head_topic") or "").strip()
    if ht:
        out["head_topic"] = ht[:120]
    de = rc.get("day_events")
    if isinstance(de, list):
        ev = [str(x).strip()[:240] for x in de if str(x).strip()]
        if ev:
            out["day_events"] = ev[:30]
    return out


def _ritual_context_fingerprint(rc: dict[str, Any]) -> str:
    if not rc:
        return ""
    try:
        blob = json.dumps(rc, sort_keys=True, ensure_ascii=False).encode("utf-8")
        return hashlib.sha256(blob).hexdigest()[:24]
    except Exception:
        return "invalid"


def _intent_context_fingerprint(intent: dict[str, Any] | None) -> str:
    """Ключ кэша narrative по слою намерения (DayConnection + head_topic из ритуала)."""
    if not intent or not isinstance(intent, dict) or not intent.get("contract_version"):
        return ""
    try:
        keys = (
            "morning_intention",
            "morning_focus",
            "head_topic",
            "question_of_day_answer",
            "quick_decision_answer",
            "what_matters_line",
        )
        slim = {k: intent.get(k) for k in keys}
        blob = json.dumps(slim, sort_keys=True, ensure_ascii=False).encode("utf-8")
        return hashlib.sha256(blob).hexdigest()[:24]
    except Exception:
        return "invalid"


def _append_ritual_why_layers(payload: dict[str, Any], ritual: dict[str, Any], locale: str) -> dict[str, Any]:
    """Добавляет слои «ритуал» в why_astrological_layers (карта, число, настроение, события дня)."""
    if not ritual:
        return payload
    out = dict(payload)
    layers = list(_sanitize_why_astrological_layers(out.get("why_astrological_layers")))
    en = _is_en_locale(locale)
    extras: list[dict[str, str]] = []
    tname = str(ritual.get("tarot_name_ru") or "").strip()
    tid = ritual.get("tarot_main_id")
    if tname or (isinstance(tid, int) and tid > 0):
        anchor = tname or (f"Карта #{tid}" if not en else f"Card #{tid}")
        detail = (
            f"В ритуале «Твой день» выбран символ — «{anchor}». В слоях «почему так» свяжи это мягко с луной, домами и транзитами выше, без противоречия выбору пользователя."
            if not en
            else f"In the ritual the day's symbol is «{anchor}». Tie it gently to lunar, house, and transit layers above."
        )
        extras.append({"kind": "ritual_tarot", "anchor": anchor[:120], "detail": detail[:520]})
    nv = str(ritual.get("numerology_value") or "").strip()
    if nv:
        detail = (
            f"Число дня в ритуале: {nv}. Покажи, как оно может отзываться в ритме и фокусе вместе с небом и картой — без жёстких предсказаний."
            if not en
            else f"Day number in the ritual: {nv}. Relate it to rhythm and sky together with the card — no rigid predictions."
        )
        extras.append({"kind": "ritual_number", "anchor": nv[:40], "detail": detail[:520]})
    mood = str(ritual.get("mood") or "").strip()
    if mood:
        label = mood if en else f"настроение: {mood}"
        detail = (
            "Отметка «как ты сейчас» в ритуале — учти её в тоне дня и в связке с картой и числом."
            if not en
            else "Mood from the ritual check-in — reflect it in tone and together with card and number."
        )
        extras.append({"kind": "ritual_mood", "anchor": label[:120], "detail": detail[:520]})
    head_topic = str(ritual.get("head_topic") or "").strip()
    if head_topic:
        anchor = head_topic if en else f"тема: {head_topic}"
        detail = (
            "Пользователь отметил тему «в голове» после чек-ина — мягко учти приоритет формулировок и шагов дня."
            if not en
            else "Head topic from the ritual — reflect it softly in priorities and suggested steps."
        )
        extras.append({"kind": "ritual_head_topic", "anchor": anchor[:120], "detail": detail[:520]})
    events = ritual.get("day_events")
    if isinstance(events, list) and events:
        ev_text = "; ".join(str(e) for e in events[:10])
        anchor = "События и контекст сегодня" if not en else "Today's context"
        extras.append({"kind": "ritual_day_events", "anchor": anchor, "detail": ev_text[:520]})
    for e in extras:
        if len(layers) >= 8:
            break
        layers.append(e)
    out["why_astrological_layers"] = layers[:8]
    return out


def _is_en_locale(locale: str | None) -> bool:
    v = (locale or "").strip().lower()
    return v.startswith("en")


def _locale_norm(locale: str | None) -> str:
    return "en" if _is_en_locale(locale) else "ru"


def _latest_snapshot_id(db: Session, user_id: int) -> int | None:
    row = (
        db.query(db_models.CoreProfileSnapshot)
        .filter(db_models.CoreProfileSnapshot.user_id == user_id)
        .order_by(db_models.CoreProfileSnapshot.updated_at.desc())
        .first()
    )
    return row.id if row else None


def _load_foundation_from_logs(
    db: Session, user_id: int, target_date: date, snapshot_id: int | None
) -> dict[str, Any] | None:
    iso = target_date.isoformat()
    q = (
        db.query(db_models.GenerationLog)
        .filter(
            db_models.GenerationLog.user_id == user_id,
            db_models.GenerationLog.module == "daily_foundation",
            db_models.GenerationLog.status.in_(("success", "fallback")),
        )
        .order_by(db_models.GenerationLog.created_at.desc())
    )
    if snapshot_id is not None:
        q = q.filter(db_models.GenerationLog.core_profile_snapshot_id == snapshot_id)
    for gen in q.limit(25).all():
        payload = gen.input_payload or {}
        if payload.get("target_date") != iso:
            continue
        if isinstance(gen.normalized_response, dict):
            return gen.normalized_response
    return None


def _load_generation_by_id(db: Session, user_id: int, gen_id: int) -> db_models.GenerationLog | None:
    row = (
        db.query(db_models.GenerationLog)
        .filter(db_models.GenerationLog.id == gen_id, db_models.GenerationLog.user_id == user_id)
        .first()
    )
    return row


def _normalize_depth_level(raw: str | None) -> str:
    s = (raw or "normal").strip().lower()
    return s if s in ("quick", "normal", "deep") else "normal"


def _clamp_narrative_depth_for_insight_tier(depth: str, insight_tier: str) -> str:
    """DE-8: режим ``deep`` (максимальный объём за один вызов) только при платной глубине инсайта."""
    d = _normalize_depth_level(depth)
    t = (insight_tier or "free").strip().lower()
    if t not in ("free", "pro", "premium"):
        t = "free"
    if t == "free" and d == "deep":
        return "normal"
    return d


def _load_narrative_cache(
    db: Session,
    user_id: int,
    target_date: date,
    surface: TodaySurface,
    parent_generation_id: int | None,
    deepen_topic: str | None,
    snapshot_id: int | None,
    insight_depth_tier: str,
    locale: str,
    ritual_context_fp: str = "",
    intent_context_fp: str = "",
    day_context_sha256: str = "",
    depth_level: str = "normal",
    *,
    prompt_label: str = "",
) -> db_models.GenerationLog | None:
    iso = target_date.isoformat()
    parent = parent_generation_id if parent_generation_id is not None else -1
    topic = (deepen_topic or "").strip().lower() or ""
    q = (
        db.query(db_models.GenerationLog)
        .filter(
            db_models.GenerationLog.user_id == user_id,
            db_models.GenerationLog.module == MODULE,
            db_models.GenerationLog.status.in_(("success", "fallback")),
        )
        .order_by(db_models.GenerationLog.created_at.desc())
    )
    if snapshot_id is not None:
        q = q.filter(db_models.GenerationLog.core_profile_snapshot_id == snapshot_id)
    # Same-day reuse: an exact ``day_context_sha256`` match is preferred (freshest
    # context), but it is NOT a hard gate. Within a day the hash drifts because
    # `get_daily_fusion_index` recomputes today's scores/recommendations from the
    # user's own tracked activity — so hard-gating on it made every visit a cache
    # miss and re-ran the LLM funnel ("собирается бесконечно"). We therefore reuse
    # the most recent row that matches the stable key (date, surface, parent, tier,
    # locale, ritual_fp, intent_fp, depth, prompt_label), mirroring the day_story_v1
    # stable-key policy. Meaningful changes (ritual / intent / tier / profile) are
    # already captured by that stable key.
    soft_hit: db_models.GenerationLog | None = None
    for gen in q.limit(40).all():
        ip = gen.input_payload or {}
        if ip.get("target_date") != iso:
            continue
        if ip.get("surface") != surface:
            continue
        if int(ip.get("parent_generation_id") or -1) != int(parent):
            continue
        if str(ip.get("deepen_topic") or "") != topic:
            continue
        if str(ip.get("insight_depth_tier") or "free").lower() != str(insight_depth_tier or "free").lower():
            continue
        if str(ip.get("locale") or "ru").lower() != str(locale or "ru").lower():
            continue
        if str(ip.get("ritual_context_fp") or "") != str(ritual_context_fp or ""):
            continue
        if str(ip.get("intent_context_fp") or "") != str(intent_context_fp or ""):
            continue
        if str(ip.get("depth_level") or "normal") != str(depth_level or "normal"):
            continue
        if prompt_label:
            pl_stored = str(ip.get("prompt_label") or _LEGACY_NARRATIVE_CACHE_PROMPT_LABEL).strip()
            if pl_stored != str(prompt_label).strip():
                continue
        if not isinstance(gen.normalized_response, dict):
            continue
        if day_context_sha256 and str(ip.get("day_context_sha256") or "") == str(day_context_sha256):
            return gen
        if soft_hit is None:
            soft_hit = gen
    return soft_hit


def _load_funnel_step_cache(
    db: Session,
    user_id: int,
    target_date: date,
    *,
    funnel_step: str,
    funnel_prompt_ver: str,
    snapshot_id: int | None,
    tier_norm: str,
    depth_norm: str,
    locale: str,
    ritual_fp: str,
    intent_fp: str,
    day_context_sha256: str,
    parent_generation_log_id: int | None = None,
) -> db_models.GenerationLog | None:
    """DE-13 v2: reuse `guide_funnel_v0` step logs when DayContext fingerprints match."""
    iso = target_date.isoformat()
    parent = int(parent_generation_log_id) if parent_generation_log_id is not None else None
    q = (
        db.query(db_models.GenerationLog)
        .filter(
            db_models.GenerationLog.user_id == user_id,
            db_models.GenerationLog.module == MODULE,
            db_models.GenerationLog.surface == "guide_funnel_v0",
            db_models.GenerationLog.status.in_(("success", "fallback")),
        )
        .order_by(db_models.GenerationLog.created_at.desc())
    )
    if snapshot_id is not None:
        q = q.filter(db_models.GenerationLog.core_profile_snapshot_id == snapshot_id)
    # Same-day reuse (see `_load_narrative_cache`): `day_context_sha256` is a
    # freshness preference, not a hard gate, so per-step funnel LLM outputs are
    # reused across intra-day visits instead of being regenerated on hash drift.
    soft_hit: db_models.GenerationLog | None = None
    for gen in q.limit(40).all():
        ip = gen.input_payload or {}
        if ip.get("target_date") != iso:
            continue
        if str(ip.get("narrative_funnel_step") or "") != funnel_step:
            continue
        if str(ip.get("funnel_prompt_ver") or "") != funnel_prompt_ver:
            continue
        if str(ip.get("locale") or "ru").lower() != str(locale or "ru").lower():
            continue
        if str(ip.get("ritual_context_fp") or "") != str(ritual_fp or ""):
            continue
        if str(ip.get("intent_context_fp") or "") != str(intent_fp or ""):
            continue
        if str(ip.get("insight_depth_tier") or "free").lower() != str(tier_norm or "free").lower():
            continue
        if str(ip.get("depth_level") or "normal") != str(depth_norm or "normal"):
            continue
        if funnel_step in ("satellites_v0", "core_text_v0"):
            if parent is None:
                continue
            if int(ip.get("parent_generation_log_id") or 0) != parent:
                continue
        if not isinstance(gen.normalized_response, dict):
            continue
        if funnel_step == "interpretation_v0" and not is_funnel_interpretation_valid(gen.normalized_response):
            continue
        if funnel_step == "satellites_v0" and not is_funnel_satellites_valid(gen.normalized_response):
            continue
        if funnel_step == "core_text_v0" and not is_funnel_core_text_valid(gen.normalized_response):
            continue
        if day_context_sha256 and str(ip.get("day_context_sha256") or "") == str(day_context_sha256):
            return gen
        if soft_hit is None:
            soft_hit = gen
    return soft_hit


def _resolve_funnel_chain_from_guide_parent(
    db: Session,
    user_id: int,
    parent_row: db_models.GenerationLog | None,
    parent_payload: dict[str, Any],
) -> dict[str, Any] | None:
    """DE-13 v3: funnel step1 interpretation + context_for_next_surfaces из parent guide."""
    if parent_row is None:
        return None
    if str(parent_row.surface or "").strip().lower() != "guide":
        return None
    ip = parent_row.input_payload if isinstance(parent_row.input_payload, dict) else {}
    if not ip.get("guide_funnel_used"):
        return None
    step1_id = ip.get("guide_funnel_parent_log_id")
    if step1_id is None:
        return None
    step1_row = _load_generation_by_id(db, user_id, int(step1_id))
    if step1_row is None or not isinstance(step1_row.normalized_response, dict):
        return None
    slim = slim_funnel_interpretation_for_child(step1_row.normalized_response)
    if slim is None:
        return None
    cfs = str(parent_payload.get("context_for_next_surfaces") or "").strip()
    if len(cfs) < 16:
        return None
    chain: dict[str, Any] = {
        "contract_version": FUNNEL_CHILD_CHAIN_CONTRACT,
        "funnel_interpretation": slim,
        "context_for_next_surfaces": cfs[:1200],
        "guide_funnel_step1_log_id": int(step1_id),
    }
    step2_id = ip.get("guide_funnel_step2_log_id")
    if step2_id is not None:
        chain["guide_funnel_step2_log_id"] = int(step2_id)
    return chain


def _attach_funnel_chain_to_child_pack(pack: dict[str, Any], funnel_chain: dict[str, Any] | None) -> None:
    """DE-13 v3: явная цепочка funnel → child surface user JSON."""
    if not isinstance(funnel_chain, dict):
        return
    interp = funnel_chain.get("funnel_interpretation")
    if isinstance(interp, dict):
        pack["funnel_interpretation"] = interp
    cfs = funnel_chain.get("context_for_next_surfaces")
    if isinstance(cfs, str) and cfs.strip():
        pack["context_for_next_surfaces"] = cfs.strip()[:1200]


def _guide_payload_from_funnel_satellites(
    sat_part: dict[str, Any],
    *,
    layers_dc: dict[str, Any],
    foundation: dict[str, Any] | None,
    fusion_for_prompt: dict[str, Any],
    core_profile: dict[str, Any] | None,
    locale_value: str,
    ritual_norm: dict[str, Any],
    funnel_core: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    """Собирает guide payload из funnel satellites + core (step3 или guide_decision)."""
    payload_try = dict(sat_part)
    if isinstance(funnel_core, dict) and is_funnel_core_text_valid(funnel_core):
        payload_try = _apply_funnel_core_to_guide_payload(payload_try, funnel_core)
    else:
        _gd_f = layers_dc.get("guide_decision")
        payload_try = _apply_guide_decision_to_guide_payload(
            payload_try, _gd_f if isinstance(_gd_f, dict) else None, locale_value
        )
    payload_try = _ensure_guide_actionable_fields(payload_try, foundation, fusion_for_prompt, locale_value)
    if not _narrative_payload_acceptable("guide", payload_try, locale_value, ritual_norm=ritual_norm):
        return None
    merged = _merge_guide_why_astrological_layers(
        payload_try, foundation, fusion_for_prompt, core_profile, locale_value
    )
    if not _narrative_payload_acceptable("guide", merged, locale_value, ritual_norm=ritual_norm):
        return None
    return merged


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


def _truncate_narrative_text(value: str, max_len: int) -> str:
    s = (value or "").strip()
    if len(s) <= max_len:
        return s
    return s[: max_len - 1].rstrip() + "…"


_ZODIAC_EN_RU: dict[str, str] = {
    "aries": "Овен",
    "taurus": "Телец",
    "gemini": "Близнецы",
    "cancer": "Рак",
    "leo": "Лев",
    "virgo": "Дева",
    "libra": "Весы",
    "scorpio": "Скорпион",
    "sagittarius": "Стрелец",
    "capricorn": "Козерог",
    "aquarius": "Водолей",
    "pisces": "Рыбы",
}


def _localize_zodiac_label(value: str | None, *, locale: str) -> str | None:
    if not value or not isinstance(value, str):
        return None
    t = value.strip()
    if not t:
        return None
    if _is_en_locale(locale):
        return t
    return _ZODIAC_EN_RU.get(t.lower(), t)


def _slim_signal_profile_for_llm(sp: dict[str, Any] | None) -> dict[str, Any]:
    """Без длинных ответов пользователя в dominant_focus — они раздувают промпт и ломают тон."""
    if not isinstance(sp, dict):
        return {}
    out: dict[str, Any] = {}
    for k in (
        "signals_days",
        "closure_state",
        "clarity_state",
        "ritual_feedback_yes_days",
        "ritual_feedback_no_days",
        "unclear_decision_days",
    ):
        if k in sp and sp[k] is not None:
            out[k] = sp[k]
    df = sp.get("dominant_focus")
    if isinstance(df, str) and df.strip():
        out["dominant_focus_excerpt"] = _truncate_narrative_text(df, 160)
    return out


def _core_context_for_narrative(core_profile: dict[str, Any] | None, *, locale: str = "ru") -> dict[str, Any]:
    """Компактное «ядро» для LLM: интерпретации, нумерология, астрология, живой слой и learning.

    Полный натальный расчёт (дома, аспекты) в CoreProfileService пока не сериализуется в этот объект;
    сюда попадает то, что уже собрано в core_profile (interpretation, daily_interpretation, living).
    """
    if not core_profile or not isinstance(core_profile, dict):
        return {"_note": "core_profile_unavailable"}

    interpretation = core_profile.get("interpretation") if isinstance(core_profile.get("interpretation"), dict) else {}
    daily_interpretation = (
        core_profile.get("daily_interpretation") if isinstance(core_profile.get("daily_interpretation"), dict) else {}
    )
    living = core_profile.get("living") if isinstance(core_profile.get("living"), dict) else {}
    learning = living.get("learning_context") if isinstance(living.get("learning_context"), dict) else {}

    def prune_interpretation(interp: dict[str, Any]) -> dict[str, Any]:
        out: dict[str, Any] = {}
        if isinstance(interp.get("identity"), str):
            out["identity"] = _truncate_narrative_text(interp["identity"], 520)
        for key in ("strengths", "watchouts"):
            arr = interp.get(key)
            if isinstance(arr, list):
                out[key] = [_truncate_narrative_text(str(x), 220) for x in arr[:6]]
        la = interp.get("life_areas")
        if isinstance(la, dict):
            out["life_areas"] = {
                str(k): _truncate_narrative_text(str(v), 360)
                for k, v in _ordered_life_area_entries(la)[:12]
            }
        return out

    def prune_daily(d: dict[str, Any]) -> dict[str, Any]:
        lenses = d.get("daily_lenses")
        if not isinstance(lenses, dict):
            return {}
        return {
            "daily_lenses": {
                str(k): _truncate_narrative_text(str(v), 300) for k, v in list(lenses.items())[:8]
            }
        }

    astro = core_profile.get("astro") if isinstance(core_profile.get("astro"), dict) else {}
    astro_slim = {
        k: astro.get(k)
        for k in (
            "sun_sign",
            "sun_element",
            "sun_modality",
            "birth_date",
            "location_name",
            "time_unknown",
            "label",
            "relation",
        )
    }
    ss = astro_slim.get("sun_sign")
    if isinstance(ss, str) and ss.strip():
        astro_slim["sun_sign"] = _localize_zodiac_label(ss, locale=locale) or ss

    num = core_profile.get("numerology") if isinstance(core_profile.get("numerology"), dict) else {}
    num_slim: dict[str, Any] = {
        k: num.get(k)
        for k in (
            "life_path",
            "expression",
            "soul_urge",
            "personality",
            "is_master_life_path",
            "birth_date",
        )
    }
    if num.get("full_name"):
        num_slim["name_on_chart"] = _truncate_narrative_text(str(num["full_name"]), 96)

    insights_out: list[dict[str, Any]] = []
    for ins in (living.get("recent_insights") or [])[:4]:
        if isinstance(ins, dict):
            insights_out.append(
                {
                    "date": ins.get("date"),
                    "type": ins.get("type"),
                    "text": _truncate_narrative_text(str(ins.get("text") or ""), 240),
                }
            )

    learning_slim: dict[str, Any] = {}
    if learning:
        qm = learning.get("quality_memory")
        if isinstance(qm, dict):
            qm = {
                "best_patterns": (qm.get("best_patterns") or [])[:2],
                "weak_patterns": (qm.get("weak_patterns") or [])[:2],
            }
        learning_slim = {
            "summary": _truncate_narrative_text(str(learning.get("summary") or ""), 640),
            "response_style": learning.get("response_style"),
            "support_style": learning.get("support_style"),
            "dominant_lanes": (learning.get("dominant_lanes") or [])[:5],
            "dominant_diary_topics": (learning.get("dominant_diary_topics") or [])[:5],
            "signal_bias": learning.get("signal_bias"),
            "stats": learning.get("stats"),
            "quality_memory": qm,
        }
        msp = learning.get("meaning_surface_patterns")
        if isinstance(msp, dict) and msp.get("total_events"):
            tags = msp.get("tags") if isinstance(msp.get("tags"), dict) else {}
            learning_slim["today_surface_patterns"] = {
                "window_days": msp.get("window_days"),
                "total_events": msp.get("total_events"),
                "pattern_hints": (msp.get("pattern_hints") or [])[:5],
                "by_event_type": (msp.get("by_event_type") or [])[:8],
                "top_mood_ids": (tags.get("top_mood_ids") or [])[:3] if isinstance(tags, dict) else [],
                "top_sphere_ids": (tags.get("top_sphere_ids") or [])[:3] if isinstance(tags, dict) else [],
                "ritual_proximity": tags.get("ritual_proximity") if isinstance(tags, dict) else None,
                "top_honest_step_ids": (tags.get("top_honest_step_ids") or [])[:3]
                if isinstance(tags, dict)
                else [],
                "day_promise_sets": tags.get("day_promise_sets") if isinstance(tags, dict) else 0,
                "top_guidance_lanes": (tags.get("top_guidance_lanes") or [])[:3]
                if isinstance(tags, dict)
                else [],
                "top_guidance_themes": (tags.get("top_guidance_themes") or [])[:5]
                if isinstance(tags, dict)
                else [],
            }

    weekly = living.get("weekly_state")
    weekly_slim = None
    if isinstance(weekly, dict):
        weekly_slim = {
            "week_start": weekly.get("week_start"),
            "integration_text": _truncate_narrative_text(str(weekly.get("integration_text") or ""), 420),
            "dominant_question_focus": weekly.get("dominant_question_focus"),
        }

    person = core_profile.get("person") if isinstance(core_profile.get("person"), dict) else {}
    person_slim = {
        k: person.get(k) for k in ("first_name", "display_name", "locale") if person.get(k) is not None
    }

    natal_raw = core_profile.get("natal_summary")
    natal_chart: dict[str, Any] = (
        natal_raw if isinstance(natal_raw, dict) else {"available": False, "reason": "not_in_profile"}
    )

    return {
        "profile_version": core_profile.get("profile_version"),
        "is_ready": core_profile.get("is_ready"),
        "missing_fields": (core_profile.get("missing_fields") or [])[:12]
        if isinstance(core_profile.get("missing_fields"), list)
        else [],
        "person": person_slim,
        "baseline": core_profile.get("baseline") if isinstance(core_profile.get("baseline"), dict) else {},
        "astro": astro_slim,
        "numerology": num_slim,
        "natal_chart": natal_chart,
        "interpretation": prune_interpretation(interpretation) if interpretation else {},
        "daily_interpretation": prune_daily(daily_interpretation) if daily_interpretation else {},
        "living_summary": _truncate_narrative_text(str(living.get("summary") or ""), 720),
        "signal_profile": _slim_signal_profile_for_llm(
            living.get("signal_profile") if isinstance(living.get("signal_profile"), dict) else None
        ),
        "recent_insights": insights_out,
        "weekly_snapshot": weekly_slim,
        "learning": learning_slim,
    }


_PLANET_RU: dict[str, str] = {
    "Sun": "Солнце",
    "Moon": "Луна",
    "Mercury": "Меркурий",
    "Venus": "Венера",
    "Mars": "Марс",
    "Jupiter": "Юпитер",
    "Saturn": "Сатурн",
    "Uranus": "Уран",
    "Neptune": "Нептун",
    "Pluto": "Плутон",
}


def _planet_label(name: str | None, en_locale: bool) -> str:
    raw = (name or "").strip()
    if not raw:
        return "planet"
    if en_locale:
        return raw
    return _PLANET_RU.get(raw, raw)


def _house_phrase(house: Any, en_locale: bool) -> str:
    try:
        h = int(house)
    except (TypeError, ValueError):
        return ""
    if h < 1 or h > 12:
        return ""
    if en_locale:
        return f", house {h}"
    return f", {h}-й дом"


def _natal_layer_anchor_detail(row: dict[str, Any], *, role: str, en_locale: bool) -> tuple[str, str] | None:
    name = row.get("name")
    sign = str(row.get("sign") or "").strip()
    gist = str(row.get("gist") or "").strip()
    house = row.get("house")
    label = _planet_label(str(name) if name else None, en_locale)
    anchor = label
    if sign:
        anchor += f" — {sign}" if en_locale else f" — {sign}"
    anchor += _house_phrase(house, en_locale)
    detail = gist[:420] if gist else ""
    if not detail:
        if en_locale:
            detail = (
                f"This placement is part of your natal chart snapshot — today’s tone connects to how you "
                f"usually move through «{role}» themes."
            )
        else:
            detail = (
                f"Это положение из твоей натальной карты — сегодняшний фон лучше читать через то, как у тебя "
                f"обычно звучит тема «{role}», а не через абстрактный «гороскоп для всех»."
            )
    return anchor[:180], detail[:520]


def _aspect_layer(aspect: dict[str, Any], en_locale: bool) -> tuple[str, str] | None:
    gist = str(aspect.get("gist") or "").strip()
    bodies = aspect.get("bodies")
    parts: list[str] = []
    if isinstance(bodies, list):
        parts = [str(x).strip() for x in bodies if str(x).strip()]
    elif bodies:
        parts = [str(bodies).strip()]
    if not gist and not parts:
        return None
    anchor = " · ".join(parts) if parts else ("Key aspect" if en_locale else "Ключевой аспект")
    ax = str(aspect.get("aspect") or "").strip()
    if ax:
        anchor = f"{anchor} ({ax})" if en_locale else f"{anchor} ({ax})"
    detail = gist or (
        "A recurring aspect pattern in your natal chart shapes how tensions and talents show up day to day."
        if en_locale
        else "Этот аспект в натале задаёт привычный способ, как у тебя проявляются напряжение и ресурс — "
        "именно поэтому день может «цепляться» за знакомые мотивы."
    )
    return anchor[:200], detail[:520]


def _build_why_astrological_layers_fallback(
    foundation: dict[str, Any] | None,
    fusion: dict[str, Any],
    core_profile: dict[str, Any] | None,
    locale: str,
) -> list[dict[str, Any]]:
    """Детерминированные «астро-слои» для шита «почему так»: натал + стержень дня (+ знак Солнца если карты нет)."""
    en_locale = _is_en_locale(locale)
    layers: list[dict[str, Any]] = []
    natal = (core_profile or {}).get("natal_summary")
    if not isinstance(natal, dict):
        natal = {}

    angles = natal.get("angles") if isinstance(natal.get("angles"), dict) else {}
    asc_sign = str(angles.get("ascendant_sign") or "").strip()
    asc_txt = str(angles.get("ascendant") or "").strip()
    if asc_sign or asc_txt:
        anchor = (
            f"ASC — {asc_sign}" if asc_sign else ("Ascendant" if en_locale else "ASC (восходящий знак)")
        )
        detail = asc_txt[:520] if asc_txt else (
            "Your rising sign colors first reactions and how you enter situations — it matters for today's «texture»."
            if en_locale
            else "Восходящий знак задаёт первую реакцию и способ «входить» в ситуации — это часть персонального фона дня."
        )
        layers.append({"kind": "natal_angle", "anchor": anchor[:180], "detail": detail})

    luminaries = natal.get("luminaries") if isinstance(natal.get("luminaries"), list) else []
    for row in luminaries[:2]:
        if not isinstance(row, dict):
            continue
        pair = _natal_layer_anchor_detail(row, role="ядро темперамента", en_locale=en_locale)
        if pair:
            layers.append({"kind": "natal_luminary", "anchor": pair[0], "detail": pair[1]})

    aspects = natal.get("notable_aspects") if isinstance(natal.get("notable_aspects"), list) else []
    for asp in aspects[:2]:
        if not isinstance(asp, dict):
            continue
        pair = _aspect_layer(asp, en_locale=en_locale)
        if pair:
            layers.append({"kind": "natal_aspect", "anchor": pair[0], "detail": pair[1]})

    personal = natal.get("personal_planets") if isinstance(natal.get("personal_planets"), list) else []
    if len(layers) < 4:
        for row in personal[:2]:
            if not isinstance(row, dict):
                continue
            pair = _natal_layer_anchor_detail(row, role="повседневные решения", en_locale=en_locale)
            if pair:
                layers.append({"kind": "natal_personal", "anchor": pair[0], "detail": pair[1]})

    spine = (foundation or {}).get("spine") if isinstance(foundation, dict) else None
    spine = spine if isinstance(spine, dict) else {}
    axis = str(spine.get("day_axis") or spine.get("best_mode") or "").strip()
    first_move = str(spine.get("first_move") or "").strip()
    main_risk = str(spine.get("main_risk") or "").strip()
    if axis or first_move or main_risk:
        anchor = axis[:120] if axis else ("Today's spine" if en_locale else "Стержень дня")
        chunks = []
        if first_move:
            chunks.append(first_move[:280])
        if main_risk:
            chunks.append(main_risk[:280])
        detail = " ".join(chunks)[:520]
        if not detail:
            detail = (
                "Computed daily spine links your profile context with today's priorities."
                if en_locale
                else "Стержень дня собирается из расчёта персонального гороскопа на дату и контекста профиля."
            )
        layers.append({"kind": "daily_spine", "anchor": anchor[:180], "detail": detail})

    prism = str((foundation or {}).get("profile_prism") or "").strip()
    if prism and len(layers) < 6:
        layers.append(
            {
                "kind": "profile_prism",
                "anchor": "Профиль и фокус" if not en_locale else "Profile focus",
                "detail": prism[:520],
            }
        )

    if natal.get("available") is not True:
        astro = (core_profile or {}).get("astro") if isinstance((core_profile or {}).get("astro"), dict) else {}
        sun_sign = str(astro.get("sun_sign") or "").strip()
        if sun_sign:
            layers.insert(
                0,
                {
                    "kind": "natal_sun_sign",
                    "anchor": (f"Sun sign — {sun_sign}" if en_locale else f"Солнце в знаке {sun_sign}"),
                    "detail": (
                        "Your solar sign is the baseline filter for how today's sky speaks to you — "
                        "even before transits are spelled out."
                        if en_locale
                        else "Солнечный знак — базовый фильтр, через который «читается» день: это уже персональная опора, "
                        "даже до детализации транзитов."
                    ),
                },
            )

    # Обрезаем и гарантируем хотя бы один «небесный» слой
    out = layers[:6]
    if not out:
        scores = (fusion or {}).get("scores") or {}
        ene = int(scores.get("energy") or 50)
        detail = (
            f"Today’s blend of energy/focus in your rhythm index sits around {ene}/100 — "
            "use it as a pacing cue while we collect more chart detail."
            if en_locale
            else f"Сводка ритма по профилю сегодня около {ene}/100 — это временная опора, пока карта не заполнена детальнее."
        )
        out.append({"kind": "rhythm_placeholder", "anchor": "Ритм дня" if not en_locale else "Day rhythm", "detail": detail})
    return out


def _sanitize_why_astrological_layers(raw: Any) -> list[dict[str, Any]]:
    if not isinstance(raw, list):
        return []
    out: list[dict[str, Any]] = []
    for item in raw[:8]:
        if not isinstance(item, dict):
            continue
        kind = str(item.get("kind") or "layer").strip()[:48]
        anchor = str(item.get("anchor") or "").strip()[:220]
        detail = str(item.get("detail") or "").strip()[:720]
        if len(anchor) < 2 or len(detail) < 10:
            continue
        out.append({"kind": kind, "anchor": anchor, "detail": detail})
    return out


def _why_astrological_layers_usable(layers: Any) -> bool:
    sanitized = _sanitize_why_astrological_layers(layers)
    return len(sanitized) >= 2


def _sphere_triad_valid(st: Any) -> bool:
    if not isinstance(st, list) or len(st) != 3:
        return False
    need = {"work", "love", "money"}
    seen: set[str] = set()
    for item in st:
        if not isinstance(item, dict):
            return False
        a = str(item.get("area") or "").strip().lower()
        stance = str(item.get("stance") or "").strip().lower()
        line = str(item.get("line") or "").strip()
        if a not in need or stance not in ("up", "down", "neutral") or len(line) < 8:
            return False
        seen.add(a)
    return seen == need


def _default_sphere_triad(foundation: dict[str, Any] | None, locale: str) -> list[dict[str, Any]]:
    spine = (foundation or {}).get("spine") if isinstance(foundation, dict) else None
    spine = spine if isinstance(spine, dict) else {}
    fm = str(spine.get("first_move") or "").strip()
    mr = str(spine.get("main_risk") or "").strip()
    en_locale = _is_en_locale(locale)
    if en_locale:
        return [
            {
                "area": "work",
                "stance": "up",
                "line": (
                    f"Work — best place to move today: {fm or 'finish one clear block instead of ten starts.'}"
                )[:280],
            },
            {
                "area": "love",
                "stance": "down",
                "line": (
                    f"Relationships — go gently, do not push: {mr or 'say it plainly instead of reading minds.'}"
                )[:280],
            },
            {
                "area": "money",
                "stance": "neutral",
                "line": "Money — neutral: check numbers and boundaries, skip impulse and vague 'later'.",
            },
        ]
    return [
        {
            "area": "work",
            "stance": "up",
            "line": (
                f"Работа — сейчас лучшее место для движения: {fm or 'один законченный кусок важнее десяти начатых.'}"
            )[:280],
        },
        {
            "area": "love",
            "stance": "down",
            "line": (
                f"Отношения — аккуратно, не дави: {mr or 'лучше сказать прямо, чем угадывать другого человека.'}"
            )[:280],
        },
        {
            "area": "money",
            "stance": "neutral",
            "line": "Деньги — нейтрально: цифры и границы, без импульса и без «потом» без даты.",
        },
    ]


def _default_action_options(locale: str) -> list[str]:
    if _is_en_locale(locale):
        return [
            "Close one task that actually blocks the day.",
            "Unpack one decision: what to decide and by when.",
            "Cap the day: three items max, move the rest.",
        ]
    return [
        "Закрой одну задачу, которая реально блокирует день.",
        "Разберись с одним вопросом: что решить и до когда.",
        "Не перегружай день: максимум три пункта, остальное — перенос.",
    ]


def _default_support_hooks(locale: str) -> list[str]:
    if _is_en_locale(locale):
        return [
            "Set one goal for today in Flow.",
            "Or take a 3–5 minute practice so the day does not slide into noise.",
        ]
    return [
        "Поставь одну цель на сегодня в Flow.",
        "Или короткая практика 3–5 минут — чтобы день не уехал в шум.",
    ]


def _core_message_body_text(cm: Any) -> str:
    if isinstance(cm, str):
        return cm.strip()
    if isinstance(cm, dict):
        for k in ("body", "main_text", "message"):
            v = cm.get(k)
            if isinstance(v, str) and v.strip():
                return v.strip()
    return ""


_RITUAL_WORD_TOKEN_RE = re.compile(r"[0-9\u0400-\u04FFa-z]+", re.IGNORECASE)

_MOOD_SLUG_RU_HINTS: dict[str, tuple[str, ...]] = {
    "tired": ("устал", "усталост", "низк", "мягк"),
    "heavy": ("тяжел", "тяжёлы", "плотн"),
    "quiet_wish": ("тиш", "тих", "наедине"),
    "motivated": ("мотив", "заряд", "подъём", "подъем"),
    "driven": ("драйв", "ритм", "темп"),
}


def _guide_visible_text_blob_for_ritual_link(payload: dict[str, Any]) -> str:
    """Видимые строки guide для O4 (герой + сигналы, без длинного «дополнительно»)."""
    parts = [
        str(payload.get("headline") or ""),
        str(payload.get("subline") or ""),
        str(payload.get("energy_line") or ""),
        str(payload.get("focus_line") or ""),
        _core_message_body_text(payload.get("core_message")),
    ]
    return _squeeze_ws(" ".join(parts)).lower()


def _guide_ritual_linkage_needles(ritual_norm: dict[str, Any]) -> list[str]:
    """Лексические якоря из ritual_context; хотя бы один должен встретиться в видимом тексте (RU O4)."""
    if not ritual_norm:
        return []
    seen: set[str] = set()
    out: list[str] = []

    def push(raw: str) -> None:
        t = _squeeze_ws(raw).lower()
        if not t:
            return
        if len(t) == 1 and not t.isdigit():
            return
        if t not in seen:
            seen.add(t)
            out.append(t)

    tname = str(ritual_norm.get("tarot_name_ru") or "").strip()
    if tname:
        push(tname)
        for w in _RITUAL_WORD_TOKEN_RE.findall(tname.lower()):
            if len(w) >= 4:
                push(w)
    nv = str(ritual_norm.get("numerology_value") or "").strip()
    if nv:
        push(nv.lower())
    mood = str(ritual_norm.get("mood") or "").strip()
    if mood:
        ml = mood.lower()
        push(ml)
        if re.fullmatch(r"[a-z][a-z0-9_]{0,31}", ml):
            for h in _MOOD_SLUG_RU_HINTS.get(ml, ()):
                push(h)
    ht = str(ritual_norm.get("head_topic") or "").strip()
    if ht:
        hl = ht.lower()
        if len(hl) >= 5:
            push(hl[:120])
        for w in _RITUAL_WORD_TOKEN_RE.findall(hl):
            if len(w) >= 4:
                push(w)
    de = ritual_norm.get("day_events")
    if isinstance(de, list):
        for ev in de[:5]:
            s = str(ev).strip()
            if not s:
                continue
            sl = s.lower()
            if len(sl) >= 6:
                push(sl[:120])
            for w in _RITUAL_WORD_TOKEN_RE.findall(sl):
                if len(w) >= 4:
                    push(w)
    return out


def _ritual_needle_in_text_blob(needle: str, blob: str) -> bool:
    if not needle or not blob:
        return False
    n = needle.strip().lower()
    if not n:
        return False
    if n.isdigit():
        return bool(re.search(rf"(?<!\d){re.escape(n)}(?!\d)", blob))
    return n in blob


def _guide_payload_links_ritual_context(payload: dict[str, Any], ritual_norm: dict[str, Any] | None) -> bool:
    """O4: при переданном ritual_context видимый текст не «отрывается» от выбора в ритуале."""
    if not ritual_norm:
        return True
    needles = _guide_ritual_linkage_needles(ritual_norm)
    if not needles:
        return True
    blob = _guide_visible_text_blob_for_ritual_link(payload)
    if len(blob) < 16:
        return False
    return any(_ritual_needle_in_text_blob(n, blob) for n in needles)


def _core_message_valid(cm: Any) -> bool:
    return len(_core_message_body_text(cm)) >= 8


def _action_option_title_text(x: Any) -> str:
    if isinstance(x, str):
        return x.strip()
    if isinstance(x, dict):
        for k in ("title", "label", "text"):
            v = x.get(k)
            if isinstance(v, str) and v.strip():
                return v.strip()
    return ""


def _normalize_one_action_option(x: Any) -> str | dict[str, Any] | None:
    if isinstance(x, dict):
        title = _action_option_title_text(x)
        if not title:
            return None
        out: dict[str, Any] = {"title": title[:320]}
        r = x.get("reason") or x.get("why")
        if isinstance(r, str) and r.strip():
            out["reason"] = r.strip()[:280]
        em = x.get("estimated_minutes")
        if isinstance(em, (int, float)) and 0 < em <= 240:
            out["estimated_minutes"] = int(em)
        ek = x.get("entity_kind") or x.get("creates")
        if isinstance(ek, str) and ek.strip():
            out["entity_kind"] = ek.strip()[:48]
        return out
    s = str(x).strip() if x is not None else ""
    return s[:320] if s else None


def _action_option_dedupe_key(item: str | dict[str, Any]) -> str:
    if isinstance(item, str):
        return item.strip().lower()
    return str(item.get("title", "")).strip().lower()


def _action_options_list_valid(ao: Any) -> bool:
    if not isinstance(ao, list) or len(ao) != 3:
        return False
    return all(bool(_action_option_title_text(x)) for x in ao)


def _ensure_guide_actionable_fields(
    payload: dict[str, Any],
    foundation: dict[str, Any] | None,
    fusion: dict[str, Any],
    locale: str,
) -> dict[str, Any]:
    """Поля v5: core_message, action_options, sphere_triad, support_hooks — для кэша и частичных ответов.

    core_message: строка (legacy) или объект {body, headline?, risk?, best_move?} — один Day Engine слой для веб/iOS.
    action_options: 3 элемента — строка или {title, reason?, estimated_minutes?, entity_kind?}.
    """
    p = dict(payload)
    headline = str(p.get("headline") or "").strip()
    subline = str(p.get("subline") or "").strip()
    cm_raw = p.get("core_message")
    if not _core_message_valid(cm_raw):
        parts = [x for x in [headline, subline] if x]
        filler = ("\n\n".join(parts)[:900] if parts else (headline or subline))[:900]
        if isinstance(cm_raw, dict):
            d = dict(cm_raw)
            d["body"] = (filler or _core_message_body_text(d) or headline or subline or "")[:900]
            p["core_message"] = d
        else:
            p["core_message"] = filler or str(cm_raw or "").strip()[:900]
    else:
        if isinstance(cm_raw, str):
            p["core_message"] = str(cm_raw).strip()[:900]
        elif isinstance(cm_raw, dict):
            d = dict(cm_raw)
            bt = _core_message_body_text(d)
            if len(bt) > 900:
                d["body"] = bt[:900]
            p["core_message"] = d
        else:
            p["core_message"] = str(cm_raw).strip()[:900]

    ao = p.get("action_options")
    opts: list[str | dict[str, Any]] = []
    if isinstance(ao, list):
        for x in ao:
            n = _normalize_one_action_option(x)
            if n:
                opts.append(n)
    if len(opts) < 3:
        di = p.get("do_items")
        if isinstance(di, list):
            for x in di:
                n = _normalize_one_action_option(x)
                if not n:
                    continue
                k = _action_option_dedupe_key(n)
                if k and k not in {_action_option_dedupe_key(y) for y in opts}:
                    opts.append(n)
                if len(opts) >= 3:
                    break
    merged_opts: list[str | dict[str, Any]] = []
    seen: set[str] = set()
    for x in opts + [s for s in _default_action_options(locale)]:
        n = _normalize_one_action_option(x)
        if not n:
            continue
        k = _action_option_dedupe_key(n)
        if not k or k in seen:
            continue
        seen.add(k)
        merged_opts.append(n)
        if len(merged_opts) >= 3:
            break
    p["action_options"] = merged_opts[:3]

    if not _sphere_triad_valid(p.get("sphere_triad")):
        p["sphere_triad"] = _default_sphere_triad(foundation, locale)

    sh = p.get("support_hooks")
    hooks: list[str] = []
    if isinstance(sh, list):
        hooks = [str(x).strip() for x in sh if str(x).strip()]
    if len(hooks) < 1:
        hooks = _default_support_hooks(locale)
    p["support_hooks"] = [str(x)[:360] for x in hooks[:3]]
    return p


def _apply_guide_decision_to_guide_payload(
    payload: dict[str, Any],
    guide_decision: dict[str, Any] | None,
    locale: str,
) -> dict[str, Any]:
    """Подменяет ядро guide детерминированным решением (guide_decision_v0)."""
    if not isinstance(payload, dict) or not isinstance(guide_decision, dict):
        return payload
    if guide_decision.get("contract_version") != "guide_decision_v0":
        return payload
    p = dict(payload)
    for key in ("headline", "subline", "energy_line", "focus_line", "risk_line", "risk_detail"):
        v = guide_decision.get(key)
        if isinstance(v, str) and v.strip():
            lim = 400 if key == "headline" else 500
            p[key] = v.strip()[:lim]
    cm = guide_decision.get("core_message")
    if isinstance(cm, dict):
        body = str(cm.get("body") or "").strip()
        if body:
            nd: dict[str, Any] = {"body": body[:900]}
            r = str(cm.get("risk") or "").strip()
            bm = str(cm.get("best_move") or "").strip()
            if r:
                nd["risk"] = r[:320]
            if bm:
                nd["best_move"] = bm[:320]
            p["core_message"] = nd
    di = guide_decision.get("do_items")
    if isinstance(di, list):
        rows = [str(x).strip()[:320] for x in di if str(x).strip()]
        if len(rows) >= 3:
            p["do_items"] = rows[:3]
    ai = guide_decision.get("avoid_items")
    if isinstance(ai, list):
        av = [str(x).strip()[:320] for x in ai if str(x).strip()]
        if len(av) >= 3:
            p["avoid_items"] = av[:3]
    return p


def _apply_funnel_core_to_guide_payload(
    payload: dict[str, Any],
    funnel_core: dict[str, Any] | None,
) -> dict[str, Any]:
    """DE-13 v4: ядро guide из funnel step3 (те же поля, что guide_decision_v0)."""
    if not isinstance(payload, dict) or not isinstance(funnel_core, dict):
        return payload
    if funnel_core.get("contract_version") != CORE_CONTRACT:
        return payload
    p = dict(payload)
    for key in ("headline", "subline", "energy_line", "focus_line", "risk_line", "risk_detail"):
        v = funnel_core.get(key)
        if isinstance(v, str) and v.strip():
            lim = 400 if key == "headline" else 500
            p[key] = v.strip()[:lim]
    cm = funnel_core.get("core_message")
    if isinstance(cm, dict):
        body = str(cm.get("body") or "").strip()
        if body:
            nd: dict[str, Any] = {"body": body[:900]}
            r = str(cm.get("risk") or "").strip()
            bm = str(cm.get("best_move") or "").strip()
            if r:
                nd["risk"] = r[:320]
            if bm:
                nd["best_move"] = bm[:320]
            p["core_message"] = nd
    di = funnel_core.get("do_items")
    if isinstance(di, list):
        rows = [str(x).strip()[:320] for x in di if str(x).strip()]
        if len(rows) >= 3:
            p["do_items"] = rows[:3]
    ai = funnel_core.get("avoid_items")
    if isinstance(ai, list):
        av = [str(x).strip()[:320] for x in ai if str(x).strip()]
        if len(av) >= 3:
            p["avoid_items"] = av[:3]
    return p


def _merge_guide_why_astrological_layers(
    payload: dict[str, Any],
    foundation: dict[str, Any] | None,
    fusion: dict[str, Any],
    core_profile: dict[str, Any] | None,
    locale: str,
) -> dict[str, Any]:
    out = dict(payload)
    raw_layers = out.get("why_astrological_layers")
    if _why_astrological_layers_usable(raw_layers):
        out["why_astrological_layers"] = _sanitize_why_astrological_layers(raw_layers)
    else:
        out["why_astrological_layers"] = _build_why_astrological_layers_fallback(foundation, fusion, core_profile, locale)
    return out


# --- Fallbacks (без LLM) -----------------------------------------------------

def _fallback_guide(
    foundation: dict[str, Any] | None,
    fusion: dict[str, Any],
    core_profile: dict[str, Any] | None,
    insight_depth_tier: str = "free",
    locale: str = "ru",
) -> dict[str, Any]:
    spine = (foundation or {}).get("spine") if isinstance(foundation, dict) else None
    spine = spine if isinstance(spine, dict) else {}
    scores = (fusion or {}).get("scores") or {}
    en = int(scores.get("energy") or 50)
    fo = int(scores.get("focus") or 50)
    en_locale = _is_en_locale(locale)
    headline = str(
        spine.get("day_axis")
        or (
            "Keep one clear priority today and avoid scattering your attention."
            if en_locale
            else "Сегодня держи один ясный приоритет и не распыляйся на лишние входы."
        )
    )
    subline = str(
        spine.get("first_move")
        or (
            "Take one short first step on the main line and log the result."
            if en_locale
            else "Сделай первый короткий шаг по главной линии и зафиксируй результат."
        )
    )
    out: dict[str, Any] = {
        "headline": headline[:400],
        "subline": subline[:500],
        "energy_line": (
            f"Daily energy is around {en}/100: lower pressure and remove non-critical commitments when needed."
            if en_locale
            else f"Ресурс дня около {en}/100: при необходимости снижай темп и убирай лишние обязательства."
        ),
        "focus_line": (
            f"Focus and clarity are around {fo}/100: one finished block beats many started ones."
            if en_locale
            else f"Внимание и ясность — около {fo}/100: лучше один завершённый блок, чем много начатых."
        ),
        "risk_line": str(spine.get("main_risk") or ("Overload and rushed decisions" if en_locale else "Перегруз и резкие решения"))[:120],
        "risk_detail": str(
            spine.get("main_risk")
            or spine.get("do_not_enter")
            or ("Watch that urgent tasks do not swallow the main line." if en_locale else "Следи, чтобы срочное не съело главное.")
        )[:500],
        "do_items": [
            str(spine.get("first_move") or ("One step on the top priority" if en_locale else "Один шаг по приоритету")),
            str((foundation or {}).get("profile_prism") or "")[:200]
            or ("Quick check-in: what was done in the morning." if en_locale else "Короткая фиксация: что сделано за утро."),
            "Check your state and take a pause if needed." if en_locale else "Проверить состояние и при необходимости сделать паузу.",
        ],
        "avoid_items": [
            str(spine.get("do_not_enter") or ("Extra promises and new topics without resources." if en_locale else "Лишние обещания и новые темы без ресурса."))[:240],
            "Reactivity to urgent noise instead of important work." if en_locale else "Реакции на срочное вместо важного.",
            "Trying to finish the whole list in one run." if en_locale else "Попытки закрыть весь список за один заход.",
        ],
        "header_disclaimer": (
            "This screen is only about your personal day based on profile and context. Compatibility with other people is a separate service."
            if en_locale
            else "Здесь только ваш день по профилю и небесному контексту. Совместимости с другими людьми — отдельный сервис."
        ),
        "context_for_next_surfaces": " ".join(
            filter(
                None,
                [
                    headline[:200],
                    subline[:200],
                    str(spine.get("best_mode") or "")[:200],
                ],
            )
        )[:1200],
    }
    tier = (insight_depth_tier or "free").strip().lower()
    if tier not in ("free", "pro", "premium"):
        tier = "free"
    out["pattern_insight"] = ""
    out["life_context_insight"] = ""
    if tier in ("pro", "premium"):
        out["pattern_insight"] = (
            "You tend to overload when results are not visible; today it is important to close at least one clear, finished step."
            if en_locale
            else "Ты сильнее перегружаешь себя, когда не видишь ощутимого результата — "
            "сегодня важно закрыть хотя бы один понятный, завершённый шаг."
        )
    if tier == "premium":
        out["life_context_insight"] = (
            "Long processes without visible payoff usually drain you: a format with movement and meaning fits you better than endless routine without progress marks."
            if en_locale
            else "Долгие процессы без видимой отдачи обычно тебя выжимают: тебе ближе формат, "
            "где есть движение и смысл, чем бесконечная рутина без метки прогресса."
        )
    out["why_astrological_layers"] = _build_why_astrological_layers_fallback(foundation, fusion, core_profile, locale)
    out["core_message"] = "\n\n".join([x for x in [headline, subline] if x])[:900]
    out["action_options"] = _default_action_options(locale)
    out["sphere_triad"] = _default_sphere_triad(foundation, locale)
    out["support_hooks"] = _default_support_hooks(locale)
    return out


def _fallback_day_layer(encouragement: str, recommendations: list[str], locale: str = "ru") -> dict[str, Any]:
    en_locale = _is_en_locale(locale)
    rec = recommendations[:3] if recommendations else (["Take one measurable step and mark it."] if en_locale else ["Сделай один измеримый шаг и отметь его."])
    return {
        "nudge_message": encouragement[:500],
        "nudge_cta_label": "Go to action" if en_locale else "Перейти к действию",
        "personal_insight_title": "Anchor point" if en_locale else "Точка сборки",
        "personal_insight_body": (
            "Use the morning spine as your anchor: avoid unnecessary acceleration and complete one line."
            if en_locale
            else "Опирайся на утренний стержень дня: не ускоряйся без нужды и доводи одну линию."
        ),
        "personal_insight_chips": ["One step", "Check-in"] if en_locale else ["Один шаг", "Фиксация"],
        "mini_decision_caption": (
            "Short cue: what kind of 'extra' step is worth noticing today (context only for yes/no/unclear)."
            if en_locale
            else "Короткий акцент: о каком типе «лишнего» шага сегодня стоит помнить (без нового вопроса — только контекст к да/нет/неясно)."
        ),
        "question_of_day_prompt": (
            "Softly: what is closer to how you restore energy now — routine/home, people, quiet, or change of setting?"
            if en_locale
            else "Ненавязчиво: что сейчас ближе к тому, как ты набираешь силы в обычной жизни — рутина и дом, люди, тишина или смена обстановки?"
        ),
        "life_now_weekly": (
            "If you have a weekly focus, mark one step so urgent tasks do not steal the week."
            if en_locale
            else "Если есть недельный фокус — отметь по нему один шаг, чтобы срочное не забрало неделю."
        ),
        "life_now_discipline": (
            "Today's discipline is in finishing, not in starting many tasks."
            if en_locale
            else "Дисциплина сегодня — в завершении, а не в количестве начатых задач."
        ),
        "recommendations": rec,
    }


def _fallback_spheres(ctx: str, locale: str = "ru") -> dict[str, Any]:
    en_locale = _is_en_locale(locale)
    return {
        "page_intro": (
            "Below is how love, money, work, and family themes align today around your core line."
            if en_locale
            else "Ниже — как темы любви, денег, работы и семьи складываются сегодня вокруг вашего стержня."
        ),
        "thesis_reminder": (
            (ctx or "Stay with your main line today and do not mix it with other people's scripts.")
            if en_locale
            else (ctx or "Держись главной линии дня и не смешивай её с чужими сценариями.")
        )[:500],
        "scenario_tie_ins": {
            "love": "In love, clarity of intention matters more than speed of response." if en_locale else "В любви сегодня важнее ясность намерения, чем скорость ответа.",
            "family": "In family/home, keep a calm tone and one agreed next step." if en_locale else "В семье и доме — спокойный тон и один договорённый шаг.",
            "career": "At work, complete or align first; avoid a new push without resources." if en_locale else "В работе — завершение или согласование, а не новый заход без ресурса.",
            "money": "With money, verify numbers and boundaries; avoid impulsive spending." if en_locale else "В деньгах — проверка цифр и границ, без импульсивных трат.",
        },
    }


def _fallback_evening(locale: str = "ru") -> dict[str, Any]:
    en_locale = _is_en_locale(locale)
    return {
        "panel_intro": "Evening is a good moment to note what mattered, honestly and without pressure." if en_locale else "Вечер — время честно зафиксировать, что было важным, без самообмана.",
        "outlook_preamble": "A short summary helps tomorrow start with clarity, not from scratch." if en_locale else "Краткий итог помогает завтра начать не с нуля.",
        "closure_invitation": "Close the day briefly: what worked, what drained you, and what to carry into tomorrow." if en_locale else "Закрой день коротко: что получилось, что утомило, что оставить на завтра.",
    }


def _fallback_deepen(topic: str, ctx: str, locale: str = "ru") -> dict[str, Any]:
    en_locale = _is_en_locale(locale)
    title = {
        "love": "Love and closeness today" if en_locale else "Любовь и близость сегодня",
        "money": "Money and value" if en_locale else "Деньги и ценность",
        "career": "Work and responsibility" if en_locale else "Работа и ответственность",
        "family": "Family and home" if en_locale else "Семья и дом",
        "full_day": "Whole day" if en_locale else "День целиком",
    }.get(topic, "Day topic" if en_locale else "Тема дня")
    body = (
        (
            f"Use the day's core thesis as anchor: {ctx[:600]}\n\n"
            f"Expand the '{title}' topic concretely: one action today, one boundary, and one signal worth tracking."
            if en_locale
            else f"Опирайся на общий тезис дня: {ctx[:600]}\n\n"
            f"Разверни тему «{title}» конкретно: одно действие сегодня, одна граница, один сигнал, на который стоит смотреть."
        )
    )
    return {
        "title": title,
        "body": body[:2500],
        "bullets": [
            "Define one step for today in this topic." if en_locale else "Сформулируй один шаг на сегодня в этой теме.",
            "Name what is better not to do in this topic today." if en_locale else "Назови, чего сегодня лучше не делать в этой теме.",
        ],
        "closing_line": "If needed, write one line in your journal so you do not lose the thread." if en_locale else "Если нужно — запиши мысль в дневник, чтобы не потерять нить.",
    }


# --- LLM --------------------------------------------------------------------

_GUIDE_SYS = """Ты пишешь тексты для экрана «Главное» TodayFlow (русский язык).
В пакете user_core — единственное фактологическое ядро профиля для этого запроса: natal_chart (резюме натала; если available=false — не придумывай карту), интерпретации, числа, знак, baseline, living_summary, урезанный signal_profile, learning. Отдельного полного profile в JSON нет — не ищи его. Плюс visible_profile и internal_profile (если есть), daily_foundation, fusion и insight_depth_tier.
Если во входном JSON есть behavior_patterns (агрегаты событий за скользящее окно): это фактические сигналы поведения — mood, actions, proximity choices (ritual_proximity), вопросы (guidance_questions_asked), практики, навигация по совместимости. Не выдумывай действий сверх этих данных; учитывай pattern_hints мягко в тоне и в формулировке шагов, без ярлыков и без «диагноза личности».
Если есть intent (morning_intention, morning_focus, head_topic, ответы мини-вопросов): это явное «что важно сегодня» от пользователя. Приоритезируй смысл и action_options под эти формулировки, не противоречь им и не подменяй своим выдуманным приоритетом; если данных мало — не раздувай.
Если во входном JSON есть day_engine_brief — серверная детерминированная «опора дня» (anchor_summary, do_hint, avoid_hint, tempo_hint). Строй headline, subline, core_message и action_options в согласии с ней: не противоречь явным нитям (ось, риск, «что важно»), расширяй и оживляй формулировками, не заменяя смысл общими фразами.
Если во входном JSON есть day_model (contract_version day_model_v0) — логический каркас дня: vector, tension, opportunity, risk, tempo, strategy, gate и при наличии temporal (DE-9: динамика вчера/недели). headline, subline, core_message, do_items, avoid_items и action_options должны быть согласованы с vector.direction, tension.summary, risk.summary, strategy.one_focus и tempo.label; при temporal.summary — не более одной мягкой отсылки к динамике, без перечисления сырых чисел и без стыда за «пустой» вчера.
Если во входном JSON есть day_history (contract_version day_history_v0): вчерашние fusion_scores, fusion_score_delta_vs_yesterday, trailing_7d_summary и meaning_day_signals — фактические шаги/сферы вчера. Используй только если fusion_score_delta_trustworthy или trailing_7d_summary_trustworthy или yesterday.meaning_active; не выводи баллы в headline; одна нейтральная отсылка к тренду или вчерашнему шагу — достаточно.
Если есть guide_decision (contract_version guide_decision_v0) — это **серверное решение дня** (сводка ритуала, day_model и короткого контура профиля): причинность «что происходит → конфликт → где сломаешься → что сработает → один ход». Поля headline, subline, core_message, do_items, avoid_items, energy_line, focus_line, risk_line, risk_detail сервер выровняет с ним после ответа; твоя задача — не выдумывать другой тезис: согласуй action_options, sphere_triad, support_hooks, context_for_next_surfaces и why_astrological_layers, **опираясь на те же якоря** (карта, число, луна, настроение, tension/risk). Запрещено сводить день к пустым парам существительных или к линии «general».
В объекте fusion есть rhythm_context: активные цели (неделя/месяц), привычки с частотой и флагом «отмечено сегодня», активные аскезы со streak и отметкой дня, сводка дневника (есть ли запись сегодня, сколько записей за последние 7 дней). Используй только как фактический контур ритма — не выдумывай действий, которых нет в данных.
Если во входном JSON есть ritual_context (карта дня, число, настроение, тема «в голове», day_events): это осознанный выбор пользователя в ритуале «Твой день». headline и subline должны согласоваться с ним как с личным акцентом, не отменяя астро-логику. В why_astrological_layers добавь 1–2 слоя, которые явно связывают луну/дома/транзиты с картой и числом — мягко, без жёстких предсказаний и без выдуманных фактов.
Во входном JSON есть insight_depth_tier: "free" | "pro" | "premium" — это не «функции», а глубина понимания, которую мы показываем за один день.
- free: только поверхностные сигналы (headline, subline, energy_line, focus_line, risk_*, do_items, avoid_items). pattern_insight и life_context_insight — пустые строки "".
- pro: как free плюс pattern_insight: 1–2 предложения — объяснение «почему так», причинность, узнаваемый паттерн по данным профиля. life_context_insight — "".
- premium: как pro, плюс life_context_insight: 1–2 предложения — как это стыкуется с форматом жизни и устойчивыми сценариями этого человека (не общий гороскоп).
Поле why_astrological_layers обязательно: массив из 3–6 объектов для экрана «почему так». Каждый объект:
  {"kind": "natal_angle|natal_luminary|natal_personal|natal_aspect|daily_spine|lunar_context|profile_prism", "anchor": "string — короткая метка с конкретикой (планета+знак+дом / аспект между телами / ASC или MC / фаза Луны / стержень дня)", "detail": "string — 1–2 предложения: как этот слой участвует в ощущении дня"}.
Требования к why_astrological_layers:
- Опирайся только на user_core.natal_chart и daily_foundation (+ знаки/дома из JSON). Если natal_chart.available=false — делай 2–3 слоя из solar знака (astro.sun_sign), интерпретаций и daily_foundation.spine; не выдумывай карту.
- Минимум один слой должен явно ссылаться на натал (планета в доме/знаке ИЛИ аспект ИЛИ ASC/MC), если в natal_chart есть данные.
- Минимум один слой — на сегодняшний расчёт дня: daily_foundation.spine (ось дня, режим, риск) или лунный/событийный контекст из foundation, если он есть в JSON.
- Не дублируй дословно headline/subline; дополняй причинность («почему так») астро-логикой простыми словами.
Все формулировки должны опираться на данные: не противоречь им и не выдумывай факты, которых нет в JSON. Пиши так, будто ты знаком с этим человеком через его профиль.
Нужно связное целое без штампов и пустых фраз.
Тон: живой, тёплый, человеческий; фразы конкретные, без канцелярита и без «клинической сухости».
Всегда сохраняй субъектность пользователя: это ориентиры, решение остаётся за человеком.
Запрещено давить страхом, обещать гарантированный исход или звучать как приговор.
Запрещено: «вселенная», «поток», «слушай интуицию» без конкретики, англицизмы вроде Energy/Focus в тексте для пользователя.
Жёстко про конкретику (иначе ответ бракуется на сервере):
- Заголовки из двух абстрактных существительных без ситуации — недопустимы (плохие примеры: «смысл и коммуникация», «формат и устойчивость», «пространство и контакт»).
- do_items и заголовки action_options — это действие: глагол + что именно (ситуация); не копируй дословно headline/subline и не повторяй одну и ту же фразу в разных полях. Сервер дополнительно срежет семантические дубли между полями — сразу давай разные ракурсы (сигнал дня vs шаг vs «почему так»).
- avoid_items — только понятные человеку формулировки; никаких внутренних кодов и slug'ов (general, neutral, work как метки API).
- sphere_triad.line — одна приземлённая подсказка по сфере (что сделать или чего не ждать); запрещены пустые метафоры вроде «тон близости», «ресурс отношений» без глагола и контекста дня.
- energy_line и focus_line свяжи с ritual_context и daily_foundation в одной цепочке причинности, а не общими словами «энергия/ресурс» сами по себе.
Обязательный блок «действие, не вода» (экран после ритуала; цепочка причина → смысл → шаг, см. Day Engine):
- core_message: либо одна строка (2–4 короткие фразы, абзацы через \\n в JSON, до ~500 символов), либо объект:
  {"headline": "опционально — одна строка", "body": "обязательно — главный смысл дня простыми словами", "risk": "опционально — где можно ошибиться", "best_move": "опционально — один конкретный ход"}.
  Поле body обязательно если объект; свяжи карту/число/настроение из ritual_context с daily_foundation и fusion; без «энергий» и пустых лозунгов.
- action_options: ровно 3 элемента. Каждый — либо строка (один шаг), либо объект {"title": "…", "reason": "зачем это даст пользу (1 короткое предложение)", "estimated_minutes": 20, "entity_kind": "goal|habit|ascetic"} — поля кроме title опциональны.
- sphere_triad: ровно 3 объекта, области ровно work, love, money — каждая по разу; stance: up | down | neutral; line — одна короткая строка-подсказка (как на сайте: «не угадывай человека — скажи прямо», а не «тон близости»).
- support_hooks: 1–2 строки: если в rhythm_context нет привычек/целей — предложи одну цель на сегодня или практику 3–5 минут; если ритм уже есть — «продолжи: …» с отсылкой к данным.
Верни только JSON:
{
  "headline": "string — 1 строка, суть дня",
  "subline": "string — 1–2 предложения",
  "energy_line": "string — про ресурс дня простыми словами",
  "focus_line": "string — куда направить внимание",
  "risk_line": "string — короткая метка риска",
  "risk_detail": "string — 1–2 предложения",
  "do_items": ["строка","строка","строка"],
  "avoid_items": ["строка","строка","строка"],
  "header_disclaimer": "string — что экран про личный день, не про совместимость с другими",
  "context_for_next_surfaces": "string — 4–8 предложений: единый тезис дня для следующих экранов (сферы, углубление)",
  "pattern_insight": "string — пусто на free; на pro/premium — почему так, паттерн",
  "life_context_insight": "string — пусто на free и pro; на premium — контекст жизни",
  "why_astrological_layers": [{"kind": "natal_aspect", "anchor": "…", "detail": "…"}],
  "core_message": "string ИЛИ объект {headline?, body, risk?, best_move?}",
  "action_options": ["строка или {title, reason?, estimated_minutes?, entity_kind?}","…","…"],
  "sphere_triad": [
    {"area": "work", "stance": "up", "line": "…"},
    {"area": "love", "stance": "down", "line": "…"},
    {"area": "money", "stance": "neutral", "line": "…"}
  ],
  "support_hooks": ["строка", "строка"]
}
"""

_DAY_SYS = """Ты пишешь тексты для вкладки «День» TodayFlow: мягкий nudge, инсайт, подпись к мини-решению и короткий сигнал для профиля (не «вопрос дня», а ненавязчивое уточнение контекста жизни).
В контексте: user_core (в т.ч. natal_chart — резюме натала, если available), prior_thesis с «Главного», fusion (в т.ч. rhythm_context — цели, привычки, аскезы, дневник за окно; только факты из JSON). Если есть behavior_patterns — слегка учитывай pattern_hints как нейтральные сигналы привычки на Today, без перегруза текста. Если есть intent — не обходи morning_intention и head_topic стороной: пусть нudge и вопрос дня созвучны сказанному пользователем.
Если во входном JSON есть day_engine_brief — та же детерминированная опора дня, что на экране «Главное» (anchor_summary, do_hint, avoid_hint, tempo_hint): nudge и инсайт должны с ней согласовываться, не перебивать другим тезисом и не противоречить do_hint/avoid_hint. При наличии day_model (day_model_v0) не расходись с vector/tension/risk/strategy/temporal по смыслу. При day_history (day_history_v0) — не более одной мягкой отсылки к вчера/неделе, без сырых баллов.
Не вставляй anchor_summary дословно в nudge_message или personal_insight_body: тот же смысл, но новая формулировка и хотя бы один новый ракурс (микро-действие, граница или сигнал); иначе сервер срежет дубль.
Бюджет длины (O8, сервер подрежет при перелице): nudge_message до ~300 символов; personal_insight_body до ~520; mini_decision_caption, question_of_day_prompt, life_now_* — компактно, без «простыни».
Заголовок инсайта (personal_insight_title) и nudge — не пара абстрактных существительных; в теле инсайта обязательна связка «почему так → что с этим сделать» в бытовых словах.
Всё должно согласовываться с тезисом и с user_core, без противоречий. Пиши для этого конкретного человека, а не «для всех».
Тон: живой и поддерживающий, без назидательности. Один образ допустим, но обязательно приземляй его в действие.
Не используй давление страхом, не обещай «точное» или «неизбежное», не отбирай агентность у пользователя.
Верни только JSON:
{
  "nudge_message": "string",
  "nudge_cta_label": "string — коротко",
  "personal_insight_title": "string",
  "personal_insight_body": "string — 2–4 предложения",
  "personal_insight_chips": ["строка","строка"],
  "mini_decision_caption": "string — 1 короткое предложение: типичный для этого человека «лишний» шаг сегодня (задача, просьба, импульс). Не задавай другой вопрос и не дублируй да/нет — только контекст к блоку «взять ли ещё одно в день».",
  "question_of_day_prompt": "string — один мягкий вопрос про формат жизни/ресурс (не «что делать сегодня»); варианты ответов на экране уже заданы, текст только задаёт тон",
  "life_now_weekly": "string",
  "life_now_discipline": "string"
}
"""

_SPHERES_SYS = """Ты связываешь экран «Сферы» с тезисом дня и с user_core (natal_chart при available, сферы в interpretation, линзы, living/learning).
Во входе есть компактный fusion (scores, encouragement, rhythm_context): при необходимости мягко стыкни сферы с фактическим ритмом (цели, привычки), не выдумывая отметок. Если передан behavior_patterns — можно слегка отразить устойчивый интерес к зонам (top_sphere_ids), без навязчивости. Если есть intent — там, где уместно, отзовись на morning_intention и head_topic без давления.
O11: если в rhythm_context есть сразу несколько типов опоры (например цели и привычки, или дневник с записями) — в page_intro или thesis_reminder должна прозвучать хотя бы одна узнаваемая связка с этими данными: слово из названия цели/привычки/аскезы или явное упоминание цели, привычки, дневника или записи. Если rhythm_context почти пуст — честно обозначь, что опора пока общая (тезис дня и astro), без выдуманных отметок в Flow.
Если во входном JSON есть day_engine_brief — опора дня совпадает с «Главным»: page_intro и thesis_reminder должны читаться как продолжение anchor_summary, а мостики scenario_tie_ins — как разложение тех же нитей по сферам, без нового «второго дня». При наличии day_model не противоречь risk/strategy/temporal; при day_history — не более одной мягкой отсылки к динамике, без сырых чисел.
Даны сценарии из стержня (love/money/career/family). Напиши короткие мостики: по одному предложению на сферу, согласованные и с тезисом, и с ядром личности. Каждое предложение — глагол, граница или один ясный шаг; без абстрактных ярлыков («тон близости», «смысл и коммуникация», «пространство»). Без внутренних кодов (general и т.п.).
Стиль: живой и лаконичный, без мистификации и без императивного давления.
Верни только JSON:
{
  "page_intro": "string — 2 предложения",
  "thesis_reminder": "string — напоминание общей линии",
  "scenario_tie_ins": {
    "love": "string",
    "family": "string",
    "career": "string",
    "money": "string"
  }
}
"""

_EVENING_SYS = """Ты пишешь короткие тексты для вечернего закрытия дня TodayFlow.
Учитывай prior_thesis и user_core (natal_chart, интерпретация, живые сигналы, learning). В fusion — scores, encouragement, recommendations и rhythm_context (цели, привычки, аскезы, дневник): используй как фактический контур дня, без выдуманных действий. Если есть behavior_patterns (например частые evening_reflection) — можно на слово поддержать привычку закрытия дня, без морали. intent с утренним намерением — мягкая нить «что человек хотел утром»; не читай мысли, не подводи итог за пользователя.
Если во входном JSON есть day_engine_brief — закрытие дня созвучно той же опоре (anchor_summary, do_hint, avoid_hint, tempo_hint): не вводи противоречащий дню тезис. При наличии day_model — мягко стыкуйся с риском, стратегией и temporal; при day_history — одна нейтральная отсылка к вчера/неделе максимум.
Стиль: тёплый, мягкий, с уважением к выбору пользователя; без вины и без давления.
Верни только JSON:
{
  "panel_intro": "string",
  "outlook_preamble": "string — для блока итога дня",
  "closure_invitation": "string — приглашение подвести итог"
}
"""

_DEEPEN_SYS = """Ты углубляешь одну тему дня для пользователя TodayFlow. Есть topic, prior_thesis, стержень/сценарии и user_core (natal_chart при available, интерпретация, числа, знак, learning).
В fusion передаётся компактный слой (scores, encouragement, rhythm_context с целями/привычками/аскезами/дневником): опирайся только на факты из JSON, не придумывай отметки или контракты. behavior_patterns при наличии — дополнительный фон повторяемых действий на Today, без выхода за пределы pattern_hints и счётчиков. intent при наличии — дополнительная нить «что важно человеку сегодня»; вплетай её мягко, не подменяя выбранный topic.
Если во входном JSON есть day_engine_brief — углубление не отменяет опору дня: title/body должны развивать выбранный topic в рамках тех же нитей (anchor_summary, do_hint, avoid_hint), без конфликта с day_model/temporal; day_history — не более одной мягкой отсылки к динамике.
Развивай тему так, чтобы это было приземлено на этого человека, без общих гороскопов. Не мистифицируй.
Тон: живой и конкретный. Удерживай баланс «смысл + практический шаг», без категоричных предсказаний.
Верни только JSON:
{
  "title": "string",
  "body": "string — 2–5 абзацев по смыслу",
  "bullets": ["строка","строка","строка"],
  "closing_line": "string"
}
"""

_NARRATIVE_PROFILE_SLICES_RU = """
Слои входа (разделяй роли, не подменяй одно другим):
1) День наружу: daily_foundation, ritual_context, fusion (scores и rhythm_context), при наличии — day_engine_brief, day_model (contract_version day_model_v0: vector, tension, risk, strategy, tempo, gate, temporal) и day_history (day_history_v0: вчера, 7 дней, meaning_day_signals).
2) Видимый профиль: объект visible_profile (если есть) — то, что человек явно задал или видит (имя, знак/даты, намерение, тема «в голове», настроение из ритуала, активные цели в Flow из подписей).
3) Внутренний профиль: объект internal_profile (если есть) — агрегаты приложения (surface_behavior_aggregates, learning, app_rhythm_scores). Не зачитывать дословно как «диагноз» в пользовательский текст; использовать для реалистичности шага и нейтральных отсылок в «почему так».

Конфликт «идеальный совет дня» и слабые сигналы follow-through во internal_profile → выбирай реалистичный шаг без стыда, без отмены астро/ритуала.

4) profile_selector (если есть): task, topic, current_mode, relevant_profile, generation_rules. Соблюдай generation_rules (tone, depth, max_actions, must_include, must_avoid); не повышай уверенность выше overall_confidence; учитывай avoid из relevant_profile как мягкие запреты формата, не как юридический договор.

Опирайся на user_core как на фактологическое ядро (натал, интерпретации) и на visible_profile — не противоречь им; не подмешивай поля, которых нет во входном JSON.
"""

_NARRATIVE_PROFILE_SLICES_EN = """
Input roles (keep them separate):
(1) Day externally: daily_foundation, ritual_context, fusion, day_engine_brief when present, day_model (day_model_v0: vector, tension, risk, strategy, tempo, gate, temporal) when present, and day_history (day_history_v0: yesterday, 7d trend, meaning_day_signals) when present.
(2) Visible profile: visible_profile — what the user explicitly set or sees (name, sign/dates, intention, ritual mood, Flow goal titles).
(3) Internal profile: internal_profile — app aggregates only; never as a verdict label in user-facing copy; use for realistic pacing and “why” hints.

If ideal day advice conflicts with sparse follow-through in aggregates, choose an achievable step; do not shame the user.

(4) profile_selector when present: task, topic, current_mode, relevant_profile, generation_rules. Honor generation_rules (tone, depth, max_actions, must_include, must_avoid); do not sound more certain than overall_confidence suggests; treat relevant_profile.avoid as soft format constraints.

user_core is the factual profile backbone for this request—stay consistent; there is no separate full `profile` object in the JSON.
"""

_FUNNEL_CHILD_SYS_RU = """
Если во входе есть funnel_interpretation (результат шага 1 narrative funnel с экрана «Главное») и context_for_next_surfaces — это каноническая цепочка смысла дня. Не противоречь what_happens, what_works и one_concrete_move; prior_thesis дублирует context_for_next_surfaces — не вводи второй независимый тезис. Развивай детали своего surface, не пересказывай interpretation целиком.
"""

_FUNNEL_CHILD_SYS_EN = """
When funnel_interpretation (narrative funnel step 1 from the Guide screen) and context_for_next_surfaces are present, they are the canonical day-meaning chain. Do not contradict what_happens, what_works, or one_concrete_move; prior_thesis mirrors context_for_next_surfaces — do not introduce a second independent thesis. Expand this surface’s details; do not repeat the full interpretation.
"""


def _attach_day_history_to_llm_pack(pack: dict[str, Any], layers_dc: dict[str, Any]) -> None:
    h = layers_dc.get("history")
    if isinstance(h, dict) and h.get("contract_version") == "day_history_v0":
        pack["day_history"] = h


def _attach_profile_slices(pack: dict[str, Any], layers_dc: dict[str, Any]) -> None:
    vp = layers_dc.get("visible_profile")
    ip = layers_dc.get("internal_profile")
    if isinstance(vp, dict):
        pack["visible_profile"] = vp
    if isinstance(ip, dict):
        pack["internal_profile"] = ip


def _slim_profile_selector(sel: dict[str, Any] | None) -> dict[str, Any] | None:
    """Урезанный селектор для LLM и логов (без полного debug_trace)."""

    if not isinstance(sel, dict):
        return None
    keys = (
        "task",
        "topic",
        "current_mode",
        "relevant_profile",
        "generation_rules",
        "overall_confidence",
        "recent_signals",
        "safe_personalization_summary",
    )
    out: dict[str, Any] = {k: sel[k] for k in keys if k in sel}
    dt = sel.get("debug_trace")
    if isinstance(dt, dict) and dt.get("selector_rules_version"):
        out["selector_rules_version"] = dt["selector_rules_version"]
    return out if out else None


def _attach_profile_selector(pack: dict[str, Any], layers_dc: dict[str, Any]) -> None:
    slim = _slim_profile_selector(layers_dc.get("profile_selector"))
    if slim:
        pack["profile_selector"] = slim


def _attach_day_logic_slices(pack: dict[str, Any], *, layers_dc: dict[str, Any], day_engine_brief: dict[str, Any]) -> None:
    """Детерминированная опора и DayModel — паритет с guide, чтобы дочерние surface не расходились по смыслу."""
    dm = layers_dc.get("day_model")
    if isinstance(dm, dict):
        pack["day_model"] = dm
    if isinstance(day_engine_brief, dict) and day_engine_brief.get("contract_version"):
        pack["day_engine_brief"] = day_engine_brief


_LOW_ENERGY_RITUAL_MOODS = frozenset({"tired", "heavy", "quiet_wish"})


def _ritual_mood_is_low_energy(ritual_norm: dict[str, Any] | None) -> bool:
    """O6: настроения ритуала с низким ресурсом — короче текст и меньше давления в промпте."""
    if not ritual_norm:
        return False
    m = str(ritual_norm.get("mood") or "").strip().lower()
    return m in _LOW_ENERGY_RITUAL_MOODS


def _low_energy_ritual_branch_system_addon(locale: str) -> str:
    if _is_en_locale(locale):
        return (
            "\nLOW_RESOURCE_MOOD (ritual_context.mood signals fatigue/low bandwidth): write shorter, gentler copy; "
            "one primary practical move — not a stack of must-dos; fewer stacked CTAs in wording; "
            "do not push peak-productivity framing."
        )
    return (
        "\nРЕЖИМ_НИЗКИЙ_РЕСУРС (ritual_context.mood: tired / heavy / quiet_wish — пользователь на низком заряде): "
        "формулировки короче и мягче; один главный практический шаг, не «список из десяти обязательств»; "
        "меньше навязчивых призывов и второстепенных CTA в тексте; без тона «выдавай максимум»."
    )


def _depth_level_prompt_addon(depth_level: str, locale: str) -> str:
    dl = _normalize_depth_level(depth_level)
    if _is_en_locale(locale):
        if dl == "quick":
            return (
                "\nDEPTH_LEVEL=quick: keep copy compact; fewer secondary nuances; one clear takeaway per block; "
                "do not inflate core_message or risk_detail length."
            )
        if dl == "deep":
            return (
                "\nDEPTH_LEVEL=deep: you may add a bit more nuance and linkage while staying grounded in the "
                "provided facts only; do not invent events; respect the same JSON field budget."
            )
        return "\nDEPTH_LEVEL=normal: balance detail and readability."
    if dl == "quick":
        return (
            "\nРЕЖИМ_ГЛУБИНЫ=quick: тексты компактнее, меньше второстепенных нюансов; по одному ясному выводу на блок; "
            "не раздувай длину core_message и risk_detail."
        )
    if dl == "deep":
        return (
            "\nРЕЖИМ_ГЛУБИНЫ=deep: допустимо чуть больше нюанса и связок, только из фактов входа; не выдумывай событий; "
            "тот же бюджет полей JSON."
        )
    return "\nРЕЖИМ_ГЛУБИНЫ=normal: баланс детали и читаемости."


def _system_prompt_for_surface(
    surface: TodaySurface,
    locale: str,
    *,
    depth_level: str = "normal",
    ritual_norm: dict[str, Any] | None = None,
    funnel_chain: dict[str, Any] | None = None,
) -> str:
    base = {
        "guide": _GUIDE_SYS,
        "day_layer": _DAY_SYS,
        "spheres": _SPHERES_SYS,
        "evening": _EVENING_SYS,
        "deepen": _DEEPEN_SYS,
    }.get(surface, _GUIDE_SYS)
    if surface in ("guide", "day_layer", "spheres", "evening", "deepen"):
        base = base + (_NARRATIVE_PROFILE_SLICES_EN if _is_en_locale(locale) else _NARRATIVE_PROFILE_SLICES_RU)
    if funnel_chain and surface in ("day_layer", "spheres", "evening", "deepen"):
        base = base + (_FUNNEL_CHILD_SYS_EN if _is_en_locale(locale) else _FUNNEL_CHILD_SYS_RU)
    base = base + _depth_level_prompt_addon(depth_level, locale)
    if _ritual_mood_is_low_energy(ritual_norm):
        base = base + _low_energy_ritual_branch_system_addon(locale)
    if _is_en_locale(locale):
        return (
            base
            + "\nIMPORTANT: Return all end-user text values in English. "
            "Keep output natural and concise. Do not switch to Russian."
        )
    return (
        base
        + "\nВАЖНО: Возвращай все пользовательские текстовые значения на русском языке. "
        "Не переключайся на английский в финальном JSON."
    )


def _validate_payload_shape(surface: TodaySurface, payload: dict[str, Any]) -> bool:
    if not isinstance(payload, dict):
        return False
    required: dict[str, list[str]] = {
        "guide": [
            "headline",
            "subline",
            "energy_line",
            "focus_line",
            "risk_line",
            "risk_detail",
            "do_items",
            "avoid_items",
            "header_disclaimer",
            "context_for_next_surfaces",
            "pattern_insight",
            "life_context_insight",
            "core_message",
            "action_options",
            "sphere_triad",
            "support_hooks",
        ],
        "day_layer": ["nudge_message", "nudge_cta_label", "personal_insight_title", "personal_insight_body", "personal_insight_chips", "mini_decision_caption", "question_of_day_prompt", "life_now_weekly", "life_now_discipline"],
        "spheres": ["page_intro", "thesis_reminder", "scenario_tie_ins"],
        "evening": ["panel_intro", "outlook_preamble", "closure_invitation"],
        "deepen": ["title", "body", "bullets", "closing_line"],
    }
    for key in required.get(surface, []):
        if key not in payload:
            return False
    if surface == "guide":
        ao = payload.get("action_options")
        if not _action_options_list_valid(ao):
            return False
        sh = payload.get("support_hooks")
        if not isinstance(sh, list) or not any(str(x).strip() for x in sh):
            return False
        if not _core_message_valid(payload.get("core_message")):
            return False
        if not _sphere_triad_valid(payload.get("sphere_triad")):
            return False
    return True


def _payload_text_values(surface: TodaySurface, payload: dict[str, Any]) -> list[str]:
    texts: list[str] = []

    def add(v: Any) -> None:
        if isinstance(v, str):
            t = v.strip()
            if t:
                texts.append(t)
        elif isinstance(v, list):
            for item in v:
                if isinstance(item, str):
                    t = item.strip()
                    if t:
                        texts.append(t)
        elif isinstance(v, dict):
            for item in v.values():
                if isinstance(item, str):
                    t = item.strip()
                    if t:
                        texts.append(t)

    if surface == "guide":
        for key in (
            "headline",
            "subline",
            "energy_line",
            "focus_line",
            "risk_line",
            "risk_detail",
            "header_disclaimer",
            "context_for_next_surfaces",
            "pattern_insight",
            "life_context_insight",
        ):
            add(payload.get(key))
        cmv = payload.get("core_message")
        if isinstance(cmv, dict):
            for k in ("headline", "title", "body", "main_text", "message", "risk", "main_risk", "best_move", "first_move", "action_hint"):
                add(cmv.get(k))
        else:
            add(cmv)
        add(payload.get("do_items"))
        add(payload.get("avoid_items"))
        aov = payload.get("action_options")
        if isinstance(aov, list):
            for item in aov:
                if isinstance(item, dict):
                    add(item.get("title"))
                    add(item.get("label"))
                    add(item.get("text"))
                    add(item.get("reason"))
                    add(item.get("why"))
                else:
                    add(item)
        add(payload.get("support_hooks"))
        st = payload.get("sphere_triad")
        if isinstance(st, list):
            for item in st:
                if isinstance(item, dict):
                    add(item.get("line"))
        wl = payload.get("why_astrological_layers")
        if isinstance(wl, list):
            for item in wl:
                if isinstance(item, dict):
                    add(item.get("anchor"))
                    add(item.get("detail"))
    elif surface == "day_layer":
        for key in ("nudge_message", "nudge_cta_label", "personal_insight_title", "personal_insight_body", "mini_decision_caption", "question_of_day_prompt", "life_now_weekly", "life_now_discipline"):
            add(payload.get(key))
        add(payload.get("personal_insight_chips"))
        add(payload.get("recommendations"))
    elif surface == "spheres":
        add(payload.get("page_intro"))
        add(payload.get("thesis_reminder"))
        add(payload.get("scenario_tie_ins"))
    elif surface == "evening":
        add(payload.get("panel_intro"))
        add(payload.get("outlook_preamble"))
        add(payload.get("closure_invitation"))
    elif surface == "deepen":
        add(payload.get("title"))
        add(payload.get("body"))
        add(payload.get("bullets"))
        add(payload.get("closing_line"))
    return texts


_CYRILLIC_RE = re.compile(r"[А-Яа-яЁё]")
_LATIN_RE = re.compile(r"[A-Za-z]")


def _validate_payload_language(surface: TodaySurface, payload: dict[str, Any], locale: str) -> bool:
    texts = _payload_text_values(surface, payload)
    if not texts:
        return False
    sample = " ".join(texts)
    has_cyr = bool(_CYRILLIC_RE.search(sample))
    has_lat = bool(_LATIN_RE.search(sample))
    if _is_en_locale(locale):
        return has_lat
    return has_cyr


_RU_NARRATIVE_BANNED_SUBSTRINGS: tuple[str, ...] = (
    "смысл и коммуникац",
    "проживать через устойчив",
    "цена времени и устойчив",
    "тон близости",
    "ресурс отношений",
    "пространство и контакт",
    "энергия и смысл",
    "формат и устойчив",
)


def _squeeze_ws(value: str) -> str:
    return re.sub(r"\s+", " ", (value or "").strip())


def _narrative_quality_mode() -> str:
    mode = (settings.today_narrative_quality_mode or "trust_llm").strip().lower()
    return mode if mode in ("strict", "trust_llm") else "trust_llm"


def _narrative_quality_strict() -> bool:
    return _narrative_quality_mode() == "strict"


def _narrative_payload_acceptable(
    surface: TodaySurface,
    payload: dict[str, Any],
    locale: str,
    *,
    ritual_norm: dict[str, Any] | None = None,
    spheres_rhythm_ctx: dict[str, Any] | None = None,
) -> bool:
    """Минимальный приём ответа LLM: shape + locale; strict добавляет copy-quality gates."""
    if not _validate_payload_shape(surface, payload):
        return False
    if not _validate_payload_language(surface, payload, locale):
        return False
    if not _narrative_quality_strict():
        return True
    if surface == "guide":
        return _guide_payload_concrete(locale, payload, ritual_norm=ritual_norm)
    if surface == "day_layer":
        return _day_layer_payload_concrete(locale, payload)
    if surface == "spheres":
        return _spheres_payload_concrete(locale, payload, spheres_rhythm_ctx or {})
    if surface == "evening":
        return _evening_payload_concrete(locale, payload)
    if surface == "deepen":
        return _deepen_payload_concrete(locale, payload)
    return True


def _narrative_guide_brief_aligned(
    locale: str,
    payload: dict[str, Any],
    day_engine_brief: dict[str, Any] | None,
) -> bool:
    if not _narrative_quality_strict():
        return True
    return _guide_payload_aligned_with_day_engine_brief(locale, payload, day_engine_brief)


def _ru_narrative_quality_reject(texts: list[str]) -> bool:
    """True — в текстах шаблонный мусор или служебные slug'i; ответ не показываем."""
    if not texts:
        return True
    blob = " ".join(t.lower() for t in texts)
    for phrase in _RU_NARRATIVE_BANNED_SUBSTRINGS:
        if phrase in blob:
            return True
    if re.search(r"\bgeneral\b", blob):
        return True
    return False


def _guide_payload_concrete(
    locale: str,
    payload: dict[str, Any],
    *,
    ritual_norm: dict[str, Any] | None = None,
) -> bool:
    """Доп. гейт для ru: не пускаем абстрактные дубликаты и пустые заголовки (см. DE-6 / качество копирайта)."""
    if _is_en_locale(locale):
        return True
    texts = _payload_text_values("guide", payload)
    if _ru_narrative_quality_reject(texts):
        return False
    hl = _squeeze_ws(str(payload.get("headline") or "")).lower()
    if len(hl) < 12:
        return False
    dos = payload.get("do_items")
    if isinstance(dos, list):
        for raw in dos[:3]:
            d = _squeeze_ws(str(raw)).lower()
            if len(d) < 10:
                return False
            if hl and d == hl:
                return False
    avs = payload.get("avoid_items")
    if isinstance(avs, list) and avs and hl:
        if _squeeze_ws(str(avs[0])).lower() == hl:
            return False
    ao = payload.get("action_options")
    if isinstance(ao, list):
        for item in ao[:3]:
            tit = ""
            if isinstance(item, dict):
                tit = str(item.get("title") or item.get("label") or item.get("text") or "").strip()
            else:
                tit = str(item).strip()
            t = _squeeze_ws(tit).lower()
            if t and hl and t == hl:
                return False
    if ritual_norm and not _guide_payload_links_ritual_context(payload, ritual_norm):
        return False
    return True


_GUIDE_BRIEF_ALIGNMENT_RETRY_ADDON_RU = (
    "\n\nСТРОГОЕ ДОПОЛНЕНИЕ (повтор генерации): headline и subline ОБЯЗАНЫ явно продолжать смысл "
    "anchor_summary из входного day_engine_brief — повтори 2–4 опорных образа дословно или почти дословно "
    "(карта дня, число дня, настроение из чек-ина, тема «в голове», ось дня из foundation). "
    "Не вводи новый тезис, который не вытекает из anchor_summary."
)

_GUIDE_BRIEF_ALIGNMENT_RETRY_ADDON_EN = (
    "\n\nSTRICT REGENERATION: headline and subline MUST explicitly extend day_engine_brief.anchor_summary — "
    "reuse 2–4 concrete anchors verbatim or near-verbatim (day card, day number, check-in mood, head topic, day axis). "
    "Do not introduce a new thesis unrelated to anchor_summary."
)

_BRIEF_ALIGN_STOP_RU: frozenset[str] = frozenset(
    {
        "этот",
        "этого",
        "этой",
        "этом",
        "этим",
        "этих",
        "когда",
        "который",
        "которая",
        "которое",
        "которые",
        "которой",
        "которых",
        "сегодня",
        "сейчас",
        "очень",
        "чтобы",
        "если",
        "либо",
        "будто",
        "после",
        "перед",
        "очень",
        "просто",
        "только",
        "лишь",
        "тоже",
        "также",
        "уже",
        "ещё",
        "еще",
        "все",
        "всё",
        "ваш",
        "ваша",
        "ваши",
        "надо",
        "есть",
        "быть",
        "будет",
        "будут",
        "этого",
        "твой",
        "твоя",
        "твои",
        "тебе",
        "тебя",
        "свой",
        "своя",
        "свои",
        "себя",
        "собой",
        "любой",
        "любая",
        "любые",
        "другой",
        "другая",
        "другие",
        "такой",
        "такая",
        "такие",
        "этот",
        "этим",
        "через",
        "про",
        "при",
        "без",
        "над",
        "под",
        "для",
        "или",
        "как",
        "что",
        "чем",
        "кто",
        "где",
        "куда",
        "откуда",
        "пока",
        "вот",
        "там",
        "тут",
        "тогда",
        "потом",
        "пока",
        "даже",
        "ведь",
        "лишь",
        "уж",
        "уже",
    }
)

_BRIEF_ALIGN_STOP_EN: frozenset[str] = frozenset(
    {
        "about",
        "after",
        "again",
        "also",
        "before",
        "being",
        "could",
        "every",
        "first",
        "going",
        "great",
        "might",
        "never",
        "other",
        "really",
        "right",
        "should",
        "still",
        "their",
        "there",
        "these",
        "those",
        "through",
        "today",
        "under",
        "until",
        "where",
        "which",
        "while",
        "would",
        "your",
        "yours",
        "without",
    }
)

_RE_ANCHOR_WORDS_RU = re.compile(r"[а-яё]+", re.IGNORECASE)
_RE_ANCHOR_WORDS_EN = re.compile(r"[a-z]+", re.IGNORECASE)


def _guide_brief_alignment_retry_addon(locale: str) -> str:
    return _GUIDE_BRIEF_ALIGNMENT_RETRY_ADDON_EN if _is_en_locale(locale) else _GUIDE_BRIEF_ALIGNMENT_RETRY_ADDON_RU


def _brief_anchor_keywords(anchor: str, *, locale_value: str) -> list[str]:
    if _is_en_locale(locale_value):
        words = [m.group(0).lower() for m in _RE_ANCHOR_WORDS_EN.finditer(anchor)]
        stop = _BRIEF_ALIGN_STOP_EN
        min_len = 4
    else:
        words = [m.group(0).lower() for m in _RE_ANCHOR_WORDS_RU.finditer(anchor)]
        stop = _BRIEF_ALIGN_STOP_RU
        min_len = 5
    scored = [w for w in words if len(w) >= min_len and w not in stop]
    seen: set[str] = set()
    uniq: list[str] = []
    for w in scored:
        if w not in seen:
            seen.add(w)
            uniq.append(w)
    uniq.sort(key=len, reverse=True)
    return uniq[:14]


def _guide_payload_aligned_with_day_engine_brief(
    locale: str,
    payload: dict[str, Any],
    brief: dict[str, Any],
) -> bool:
    """Пост-проверка P0: headline+subline должны делить лексику с anchor_summary (мягкий якорь, без LLM)."""
    if not isinstance(brief, dict) or brief.get("contract_version") != "day_narrative_brief_v0":
        return True
    anchor = str(brief.get("anchor_summary") or "").strip()
    if len(anchor) < 72:
        return True
    keys = _brief_anchor_keywords(anchor, locale_value=locale)
    if len(keys) < 5:
        return True
    hl = _squeeze_ws(str(payload.get("headline") or "")).lower()
    sl = _squeeze_ws(str(payload.get("subline") or "")).lower()
    blob = f"{hl} {sl}"
    hits = [w for w in keys if w in blob]
    if len(hits) >= 2:
        return True
    if len(hits) == 1 and len(hits[0]) >= 9:
        return True
    return False


def _guide_apply_final_processing_pass(
    payload: dict[str, Any],
    *,
    day_ctx: dict[str, Any],
    foundation: dict[str, Any] | None,
    fusion_post: dict[str, Any],
    core_profile: dict[str, Any] | None,
    ritual_norm: dict[str, Any],
    locale_value: str,
    tier_norm: str,
    day_engine_brief: dict[str, Any] | None = None,
    preserve_funnel_core: bool = False,
) -> dict[str, Any]:
    """Тот же финальный проход, что у HTTP-ответа guide (перед вложением day_engine_brief)."""
    p = dict(payload)
    p = _ensure_guide_actionable_fields(p, foundation, fusion_post, locale_value)
    p = _merge_guide_why_astrological_layers(p, foundation, fusion_post, core_profile, locale_value)
    if ritual_norm:
        p = _append_ritual_why_layers(p, ritual_norm, locale_value)
    if not preserve_funnel_core:
        _gd_p = (day_ctx.get("layers") or {}).get("guide_decision")
        p = _apply_guide_decision_to_guide_payload(p, _gd_p if isinstance(_gd_p, dict) else None, locale_value)
    p = _ensure_guide_actionable_fields(p, foundation, fusion_post, locale_value)
    p = _dedupe_guide_payload_cross_fields(
        p, foundation, fusion_post, locale_value, day_engine_brief=day_engine_brief
    )
    p = strip_meta_from_guide_payload(p)
    p = _normalize_guide_payload_for_tier(p, tier_norm)
    p.pop("funnel_contract", None)
    return p


def _rhythm_context_signal_categories(rc: dict[str, Any] | None) -> int:
    """Сколько разных контуров ритма непусто (цели / привычки / аскезы / дневник)."""
    if not isinstance(rc, dict):
        return 0
    n = 0
    g = rc.get("goals")
    if isinstance(g, list) and len(g) > 0:
        n += 1
    h = rc.get("habits")
    if isinstance(h, list) and len(h) > 0:
        n += 1
    a = rc.get("ascetics")
    if isinstance(a, list) and len(a) > 0:
        n += 1
    d = rc.get("diary")
    if isinstance(d, dict) and (
        bool(d.get("has_entry_today")) or int(d.get("entries_last_7_days") or 0) > 0
    ):
        n += 1
    return n


def _rhythm_context_grounding_needles(rc: dict[str, Any] | None) -> list[str]:
    """Фрагменты из rhythm_context для проверки, что текст сфер не «плавает» (O11)."""
    if not isinstance(rc, dict):
        return []
    seen: set[str] = set()
    out: list[str] = []

    def add_raw(s: str) -> None:
        t = _squeeze_ws(str(s)).lower()
        if len(t) < 4:
            return
        if t in seen:
            return
        seen.add(t)
        out.append(t)

    def add_words(s: str) -> None:
        for w in re.split(r"[^\wа-яёА-ЯЁa-zA-Z0-9]+", str(s)):
            wl = w.lower()
            if len(wl) >= 5:
                add_raw(wl)

    for g in rc.get("goals") or []:
        if isinstance(g, dict):
            title = str(g.get("title") or "")
            add_raw(title)
            add_words(title)
    for h in rc.get("habits") or []:
        if isinstance(h, dict):
            name = str(h.get("name") or "")
            add_raw(name)
            add_words(name)
    for a in rc.get("ascetics") or []:
        if isinstance(a, dict):
            title = str(a.get("title") or "")
            add_raw(title)
            add_words(title)
    d = rc.get("diary")
    if isinstance(d, dict) and (
        bool(d.get("has_entry_today")) or int(d.get("entries_last_7_days") or 0) > 0
    ):
        add_raw("дневник")
        add_raw("запись")
    return out[:48]


def _spheres_blob_for_grounding(payload: dict[str, Any]) -> str:
    parts: list[str] = []
    for key in ("page_intro", "thesis_reminder"):
        v = payload.get(key)
        if isinstance(v, str) and v.strip():
            parts.append(v)
    sti = payload.get("scenario_tie_ins")
    if isinstance(sti, dict):
        for v in sti.values():
            if isinstance(v, str) and v.strip():
                parts.append(v)
    return _squeeze_ws(" ".join(parts)).lower()


_RHYTHM_GROUNDING_SOFT_RU = ("цел", "привыч", "аскез", "дневник", "запис", "ритм")


def _spheres_payload_grounded_in_rhythm(
    payload: dict[str, Any],
    rhythm_context: dict[str, Any] | None,
) -> bool:
    """O11: при богатом rhythm_context текст сфер должен отсылать к фактам или типам опоры."""
    if _rhythm_context_signal_categories(rhythm_context) < 2:
        return True
    blob = _spheres_blob_for_grounding(payload)
    if not blob:
        return False
    needles = _rhythm_context_grounding_needles(rhythm_context)
    for n in needles:
        if len(n) >= 4 and n in blob:
            return True
    if any(s in blob for s in _RHYTHM_GROUNDING_SOFT_RU):
        return True
    return False


def _spheres_payload_concrete(
    locale: str,
    payload: dict[str, Any],
    rhythm_context: dict[str, Any] | None = None,
) -> bool:
    if _is_en_locale(locale):
        return True
    texts: list[str] = []
    for key in ("page_intro", "thesis_reminder"):
        v = payload.get(key)
        if isinstance(v, str) and v.strip():
            texts.append(v)
    sti = payload.get("scenario_tie_ins")
    if isinstance(sti, dict):
        for v in sti.values():
            if isinstance(v, str) and v.strip():
                texts.append(v)
    if _ru_narrative_quality_reject(texts):
        return False
    if not _spheres_payload_grounded_in_rhythm(payload, rhythm_context):
        return False
    return True


def _day_layer_payload_concrete(locale: str, payload: dict[str, Any]) -> bool:
    """RU: тот же бан шаблонов, что для guide/spheres (DE-6)."""
    if _is_en_locale(locale):
        return True
    pit = _squeeze_ws(str(payload.get("personal_insight_title") or ""))
    if len(pit) < 12:
        return False
    if is_ru_abstract_topic_headline(pit):
        return False
    texts: list[str] = []
    for key in ("nudge_message", "personal_insight_title", "personal_insight_body", "question_of_day_prompt", "mini_decision_caption"):
        v = payload.get(key)
        if isinstance(v, str) and v.strip():
            texts.append(v)
    chips = payload.get("personal_insight_chips")
    if isinstance(chips, list):
        for c in chips:
            if isinstance(c, str) and c.strip():
                texts.append(c)
    return not _ru_narrative_quality_reject(texts)


def _evening_payload_concrete(locale: str, payload: dict[str, Any]) -> bool:
    if _is_en_locale(locale):
        return True
    texts: list[str] = []
    for key in ("panel_intro", "outlook_preamble", "closure_invitation"):
        v = payload.get(key)
        if isinstance(v, str) and v.strip():
            texts.append(v)
    return not _ru_narrative_quality_reject(texts)


def _deepen_payload_concrete(locale: str, payload: dict[str, Any]) -> bool:
    if _is_en_locale(locale):
        return True
    texts: list[str] = []
    for key in ("title", "body", "closing_line"):
        v = payload.get(key)
        if isinstance(v, str) and v.strip():
            texts.append(v)
    bl = payload.get("bullets")
    if isinstance(bl, list):
        for b in bl:
            if isinstance(b, str) and b.strip():
                texts.append(b)
    return not _ru_narrative_quality_reject(texts)


def _normalize_guide_payload_for_tier(payload: dict[str, Any], tier: str) -> dict[str, Any]:
    """Не отдаём глубже тарифа, даже если модель вернула лишнее."""
    p = dict(payload)
    t = (tier or "free").lower()
    if t not in ("free", "pro", "premium"):
        t = "free"
    pat = str(p.get("pattern_insight") or "").strip()
    life = str(p.get("life_context_insight") or "").strip()
    if t == "free":
        pat, life = "", ""
    elif t == "pro":
        life = ""
    p["pattern_insight"] = pat
    p["life_context_insight"] = life
    return p


_WHY_LINE_PREFIXES_RE: tuple[re.Pattern[str], ...] = (
    re.compile(r"^напряжение дня сейчас в одном месте:\s*", re.I),
    re.compile(r"^лучше всего день раскрывается через такой режим:\s*", re.I),
    re.compile(r"^утренний фокус для дня:\s*", re.I),
)


def _normalize_loose_guide_text(s: str) -> str:
    t = (s or "").lower()
    t = re.sub(r"[·,.:;!?—–\-]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def _texts_semantically_redundant(a: str, b: str, *, min_token_overlap: float = 0.56) -> bool:
    """Похожесть по смыслу (как todayRitualCopy.textsSemanticallyRedundant на вебе)."""
    na = _normalize_loose_guide_text(a)
    nb = _normalize_loose_guide_text(b)
    if not na or not nb:
        return False
    if na == nb:
        return True
    min_l = min(len(na), len(nb))
    if min_l >= 22 and (na in nb or nb in na):
        return True
    ta = [w for w in na.split() if len(w) > 2]
    tb = [w for w in nb.split() if len(w) > 2]
    if len(ta) < 3 or len(tb) < 3:
        return min_l >= 10 and (na in nb or nb in na)
    set_a, set_b = set(ta), set(tb)
    inter = len(set_a & set_b)
    denom = min(len(set_a), len(set_b))
    return denom > 0 and inter / denom >= min_token_overlap


# --- O8: day_layer — «короткая сводка»: лимиты и отрыв от дословного anchor_summary ---

_DAY_LAYER_NUDGE_MAX = 300
_DAY_LAYER_NUDGE_CTA_MAX = 56
_DAY_LAYER_INSIGHT_TITLE_MAX = 120
_DAY_LAYER_INSIGHT_BODY_MAX = 520
_DAY_LAYER_CHIP_MAX = 72
_DAY_LAYER_MINI_DECISION_MAX = 220
_DAY_LAYER_QOD_MAX = 260
_DAY_LAYER_LIFE_NOW_MAX = 220


def _smart_truncate_day_layer_line(value: str, max_len: int) -> str:
    s = (value or "").strip()
    if len(s) <= max_len:
        return s
    cut = s[: max_len - 1].rstrip()
    for sep in ("\n\n", ". ", "! ", "? ", "; "):
        i = cut.rfind(sep)
        if i >= max(24, max_len // 3):
            frag = cut[: i + len(sep)].strip()
            if len(frag) >= 20:
                return frag + ("…" if len(frag) < len(s) - 1 else "")
    return _truncate_narrative_text(s, max_len)


def _day_layer_strip_anchor_echo(anchor: str, text: str) -> str:
    """Если модель вставила anchor_summary в начало — убрать дубль, оставить добавленный смысл (O8)."""
    a = (anchor or "").strip()
    b = (text or "").strip()
    if len(a) < 18 or not b:
        return b
    al, bl = a.lower(), b.lower()
    if bl.startswith(al):
        rest = b[len(a) :].lstrip(" \n\r\t—–-.,;:")
        return rest if len(rest) >= 20 else b
    first_para = b.split("\n\n", 1)[0].strip()
    if len(first_para) >= len(a) * 0.85 and _texts_semantically_redundant(a, first_para):
        tail = b[len(first_para) :].lstrip("\n ")
        return tail if len(tail) >= 20 else b
    return b


def _finalize_day_layer_payload_o8(
    payload: dict[str, Any],
    *,
    day_engine_brief: dict[str, Any] | None,
) -> dict[str, Any]:
    """Пост-обработка ответа day_layer: бюджет длины и отрыв от дословного anchor_summary."""
    p = dict(payload)
    anchor = ""
    if isinstance(day_engine_brief, dict):
        anchor = str(day_engine_brief.get("anchor_summary") or "").strip()

    def clip_str(key: str, max_len: int, *, strip_anchor: bool) -> None:
        raw = p.get(key)
        if not isinstance(raw, str):
            return
        t = strip_llm_meta_commentary(raw).strip()
        if not t:
            return
        if strip_anchor and anchor:
            t = _day_layer_strip_anchor_echo(anchor, t)
        if key in ("nudge_message", "personal_insight_body"):
            p[key] = _smart_truncate_day_layer_line(t, max_len)
        else:
            p[key] = _truncate_narrative_text(t, max_len)

    clip_str("nudge_message", _DAY_LAYER_NUDGE_MAX, strip_anchor=True)
    clip_str("nudge_cta_label", _DAY_LAYER_NUDGE_CTA_MAX, strip_anchor=False)
    clip_str("personal_insight_title", _DAY_LAYER_INSIGHT_TITLE_MAX, strip_anchor=False)
    clip_str("personal_insight_body", _DAY_LAYER_INSIGHT_BODY_MAX, strip_anchor=True)
    clip_str("mini_decision_caption", _DAY_LAYER_MINI_DECISION_MAX, strip_anchor=False)
    clip_str("question_of_day_prompt", _DAY_LAYER_QOD_MAX, strip_anchor=False)
    clip_str("life_now_weekly", _DAY_LAYER_LIFE_NOW_MAX, strip_anchor=False)
    clip_str("life_now_discipline", _DAY_LAYER_LIFE_NOW_MAX, strip_anchor=False)

    chips = p.get("personal_insight_chips")
    if isinstance(chips, list):
        out_chips: list[str] = []
        for c in chips:
            if isinstance(c, str):
                cs = strip_llm_meta_commentary(c).strip()
                if cs:
                    out_chips.append(_truncate_narrative_text(cs, _DAY_LAYER_CHIP_MAX))
        p["personal_insight_chips"] = out_chips
    return p


def _expansion_variants_for_why_dedup(line: str) -> list[str]:
    t = (line or "").strip()
    if not t:
        return []
    out: list[str] = [t]
    seen: set[str] = {t.lower()}
    for rx in _WHY_LINE_PREFIXES_RE:
        rest = rx.sub("", t).strip()
        if len(rest) >= 4 and rest.lower() not in seen:
            seen.add(rest.lower())
            out.append(rest)
    return out


def _line_redundant_with_any(line: str, pool: list[str]) -> bool:
    variants = _expansion_variants_for_why_dedup(line)
    for p in pool:
        pt = p.strip()
        if not pt:
            continue
        pvars = _expansion_variants_for_why_dedup(pt)
        for v in variants:
            for x in pvars:
                if _texts_semantically_redundant(v, x):
                    return True
    return False


def _foundation_spine_fallback_lines(foundation: dict[str, Any] | None) -> list[str]:
    spine = (foundation or {}).get("spine") if isinstance(foundation, dict) else None
    spine = spine if isinstance(spine, dict) else {}
    keys = ("first_move", "best_mode", "main_risk", "day_axis", "do_not_enter", "next_action")
    out: list[str] = []
    seen: set[str] = set()
    for k in keys:
        v = str(spine.get(k) or "").strip()
        if not v:
            continue
        low = v.lower()
        if low in seen:
            continue
        seen.add(low)
        out.append(v)
    return out


def _fusion_scored_energy_focus_lines(fusion: dict[str, Any] | None, locale: str) -> tuple[str, str]:
    scores = (fusion or {}).get("scores") or {}
    try:
        en = int(scores.get("energy") or 50)
    except (TypeError, ValueError):
        en = 50
    try:
        fo = int(scores.get("focus") or 50)
    except (TypeError, ValueError):
        fo = 50
    en = max(0, min(100, en))
    fo = max(0, min(100, fo))
    if _is_en_locale(locale):
        return (
            f"Daily energy is around {en}/100: lower pressure and remove non-critical commitments when needed.",
            f"Focus and clarity are around {fo}/100: one finished block beats many started ones.",
        )
    return (
        f"Ресурс дня около {en}/100: при необходимости снижай темп и убирай лишние обязательства.",
        f"Внимание и ясность — около {fo}/100: лучше один завершённый блок, чем много начатых.",
    )


def _neutral_why_detail_replacement(anchor: str, locale: str) -> str:
    a = anchor.strip()
    if _is_en_locale(locale):
        if len(a) >= 8:
            return (
                f"This layer — «{a[:200]}» — shapes the day alongside the main focus, without repeating it verbatim."
            )[:720]
        return "Chart and sky context nudges how the day feels — without copying the headline wording."[:720]
    if len(a) >= 8:
        return (
            f"Этот слой — «{a[:200]}» — добавляет астро-контекст к дню рядом с главным акцентом, без дословного повтора."
        )[:720]
    return "Контекст карты и неба задаёт оттенок дня — без копирования формулировки заголовка."[:720]


def _dedupe_do_or_avoid_list(
    raw: Any,
    pool: list[str],
    spine_lines: list[str],
    preset_defaults: list[str],
    locale: str,
) -> list[str]:
    src = [str(x).strip() for x in raw] if isinstance(raw, list) else []
    while len(src) < 3:
        src.append("")
    out: list[str] = []
    extended = list(pool)
    fallbacks = [x for x in spine_lines if x.strip()] + list(preset_defaults)
    ultimate = (
        [
            "Bound today: finish one thing you already started.",
            "Write down one decision and its deadline.",
            "After three tasks, stop adding new inputs.",
        ]
        if _is_en_locale(locale)
        else [
            "Ограничь день: доведи одно уже начатое.",
            "Запиши одно решение и срок.",
            "После трёх задач — не добавляй новых входов.",
        ]
    )
    fi = 0
    for i in range(3):
        cand = src[i] if i < len(src) else ""
        chosen = ""
        if cand and not _line_redundant_with_any(cand, extended):
            chosen = cand
        else:
            while fi < len(fallbacks):
                c = fallbacks[fi].strip()
                fi += 1
                if c and not _line_redundant_with_any(c, extended):
                    chosen = c
                    break
        if not chosen:
            for u in ultimate:
                if u and not _line_redundant_with_any(u, extended):
                    chosen = u
                    break
        if not chosen:
            chosen = ultimate[i % len(ultimate)]
        chosen = chosen[:320]
        out.append(chosen)
        extended.append(chosen)
    return out


def _day_engine_brief_dedupe_seed_strings(brief: dict[str, Any] | None) -> list[str]:
    """Строки опоры дня в пул дедупликации (O1): вторичные поля не повторяют anchor/hints дословно."""
    if not isinstance(brief, dict) or brief.get("contract_version") != "day_narrative_brief_v0":
        return []
    out: list[str] = []
    for key in ("anchor_summary", "do_hint", "avoid_hint", "tempo_hint"):
        t = str(brief.get(key) or "").strip()
        if t:
            out.append(t)
    return out


def _dedupe_guide_payload_cross_fields(
    payload: dict[str, Any],
    foundation: dict[str, Any] | None,
    fusion: dict[str, Any] | None,
    locale: str,
    *,
    day_engine_brief: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Срезает семантические повторы между полями guide (паритет с вебом / iOS)."""
    p = dict(payload)
    headline = str(p.get("headline") or "").strip()
    subline = str(p.get("subline") or "").strip()
    cm = p.get("core_message")

    if isinstance(cm, dict):
        d = dict(cm)
        body = _core_message_body_text(d)
        hl = str(d.get("headline") or "").strip()
        risk = str(d.get("risk") or d.get("main_risk") or "").strip()
        bm = str(d.get("best_move") or d.get("first_move") or "").strip()
        if hl and body and _texts_semantically_redundant(hl, body):
            d.pop("headline", None)
            hl = ""
        if risk and body and _texts_semantically_redundant(risk, body):
            d.pop("risk", None)
            d.pop("main_risk", None)
            risk = ""
        if bm and body and _texts_semantically_redundant(bm, body):
            d.pop("best_move", None)
            d.pop("first_move", None)
            bm = ""
        if risk and bm and _texts_semantically_redundant(risk, bm):
            d.pop("risk", None)
            d.pop("main_risk", None)
        if bm and hl and _texts_semantically_redundant(bm, hl):
            d.pop("best_move", None)
            d.pop("first_move", None)
        p["core_message"] = d
        cm = d

    body_full = _core_message_body_text(cm)
    anchor_summary_only = ""
    if isinstance(day_engine_brief, dict):
        anchor_summary_only = str(day_engine_brief.get("anchor_summary") or "").strip()

    # O1: верхний hero (headline/subline) не повторяет тезис core_message.body и не дублирует anchor_summary.
    if body_full.strip():
        if headline and _texts_semantically_redundant(headline, body_full):
            hl_st = (headline or "").strip()
            # Hero дословно открывает core_message — не считаем это дублем (fallback-строка и часть dict-body).
            pref = hl_st[: min(len(hl_st), 160)] if hl_st else ""
            skip_hl_strip = bool(pref and body_full.strip().startswith(pref))
            # EN: мягкий семантический overlap guide_decision (hero vs body) часто не совпадает с префиксом;
            # обнуление заголовка даёт пустой hero (контракт guide / fallback-тесты).
            if not skip_hl_strip and not _is_en_locale(locale):
                p["headline"] = ""
                headline = ""
        if subline and _texts_semantically_redundant(subline, body_full):
            p["subline"] = ""
            subline = ""
    if headline and subline and _texts_semantically_redundant(subline, headline):
        p["subline"] = ""
        subline = ""
    if anchor_summary_only:
        # Не обнуляем headline только из‑за пересечения с anchor_summary: guide_decision часто
        # формулирует тот же тезис, что и детерминированный brief; пустой headline ломает
        # _guide_payload_concrete (RU ≥12) и повторную валидацию кэша при том же DayContext.
        if subline and _texts_semantically_redundant(subline, anchor_summary_only):
            p["subline"] = ""
            subline = ""

    seed = _day_engine_brief_dedupe_seed_strings(day_engine_brief)
    pool: list[str] = [t for t in (*seed, headline, subline, body_full) if t]

    spine_lines = _foundation_spine_fallback_lines(foundation)
    cfs0 = str(p.get("context_for_next_surfaces") or "").strip()
    if cfs0 and _line_redundant_with_any(cfs0, pool):
        spine_d = (foundation or {}).get("spine") if isinstance(foundation, dict) else None
        spine_d = spine_d if isinstance(spine_d, dict) else {}
        best_mode = str(spine_d.get("best_mode") or "").strip()
        bridge = " ".join(x for x in (headline[:220], subline[:220], best_mode[:220]) if x).strip()
        replacement = ""
        if bridge and not _line_redundant_with_any(bridge, pool):
            replacement = bridge
        else:
            replacement = next(
                (s for s in spine_lines if len(s) >= 28 and not _line_redundant_with_any(s, pool)),
                "",
            )
        if not replacement:
            replacement = (
                "Carry today's thesis into Spheres and Deepen without copying the morning headline word for word."
                if _is_en_locale(locale)
                else "На экранах «Сферы» и «Углубление» продолжай тезис дня, не копируя утренний заголовок дословно."
            )
        p["context_for_next_surfaces"] = replacement[:1200]
    cfs1 = str(p.get("context_for_next_surfaces") or "").strip()
    if cfs1:
        pool.append(cfs1)

    neu, nfo = _fusion_scored_energy_focus_lines(fusion, locale)

    el = str(p.get("energy_line") or "").strip()
    if el and _line_redundant_with_any(el, pool):
        if not _line_redundant_with_any(neu, pool):
            p["energy_line"] = neu[:500]
        else:
            pick = next((s for s in spine_lines if not _line_redundant_with_any(s, pool)), None)
            if pick:
                p["energy_line"] = pick[:500]

    el2 = str(p.get("energy_line") or "").strip()
    if el2:
        pool.append(el2)

    fln = str(p.get("focus_line") or "").strip()
    if fln and _line_redundant_with_any(fln, pool):
        if not _line_redundant_with_any(nfo, pool):
            p["focus_line"] = nfo[:500]
        else:
            pick = next((s for s in spine_lines if not _line_redundant_with_any(s, pool)), None)
            if pick:
                p["focus_line"] = pick[:500]

    fl2 = str(p.get("focus_line") or "").strip()
    if fl2:
        pool.append(fl2)

    rd = str(p.get("risk_detail") or "").strip()
    if rd and _line_redundant_with_any(rd, pool):
        spine = (foundation or {}).get("spine") if isinstance(foundation, dict) else None
        spine = spine if isinstance(spine, dict) else {}
        replaced = False
        for key in ("do_not_enter", "main_risk"):
            cand = str(spine.get(key) or "").strip()
            if cand and not _line_redundant_with_any(cand, pool):
                p["risk_detail"] = cand[:500]
                replaced = True
                break
        if not replaced:
            p["risk_detail"] = (
                "Watch that urgent tasks do not swallow the main line."
                if _is_en_locale(locale)
                else "Следи, чтобы срочное не съело главное."
            )[:500]

    en_loc = _is_en_locale(locale)
    do_presets = (
        [
            "Quick check-in: what was done in the morning.",
            "Check your state and take a pause if needed.",
            "One step on the top priority without scattering.",
        ]
        if en_loc
        else [
            "Короткая фиксация: что сделано за утро.",
            "Проверить состояние и при необходимости сделать паузу.",
            "Один шаг по приоритету без распыления на второстепенное.",
        ]
    )
    avoid_presets = (
        [
            "Reactivity to urgent noise instead of important work.",
            "Extra promises without resources.",
            "Trying to finish the whole list in one run.",
        ]
        if en_loc
        else [
            "Реакции на срочное вместо важного.",
            "Лишние обещания без ресурса.",
            "Попытки закрыть весь список за один заход.",
        ]
    )
    p["do_items"] = _dedupe_do_or_avoid_list(p.get("do_items"), pool, spine_lines, do_presets, locale)
    for d in p["do_items"]:
        if d:
            pool.append(d)
    p["avoid_items"] = _dedupe_do_or_avoid_list(p.get("avoid_items"), pool, spine_lines, avoid_presets, locale)

    ao = p.get("action_options")
    if isinstance(ao, list) and len(ao) == 3:
        default_ao = _default_action_options(locale)
        tit_pool: list[str] = list(pool)
        new_ao: list[str | dict[str, Any]] = []
        fi = 0
        for idx, item in enumerate(ao[:3]):
            title = _action_option_title_text(item)
            if title and not _line_redundant_with_any(title, tit_pool):
                new_ao.append(item)
                tit_pool.append(title)
                continue
            repl = ""
            while fi < len(default_ao):
                c = default_ao[fi].strip()
                fi += 1
                if c and not _line_redundant_with_any(c, tit_pool):
                    repl = c
                    break
            if not repl:
                repl = default_ao[idx % len(default_ao)]
            if isinstance(item, dict):
                nd = dict(item)
                nd["title"] = repl[:320]
                r = nd.get("reason")
                if isinstance(r, str) and r.strip() and _texts_semantically_redundant(r.strip(), repl):
                    nd.pop("reason", None)
                new_ao.append(nd)
            else:
                new_ao.append(repl)
            tit_pool.append(repl)
        p["action_options"] = new_ao

    sh = p.get("support_hooks")
    if isinstance(sh, list):
        defaults = _default_support_hooks(locale)
        new_sh: list[str] = []
        ext = list(pool)
        di = 0
        for x in sh:
            s = str(x).strip()
            if not s:
                continue
            if not _line_redundant_with_any(s, ext):
                new_sh.append(s[:360])
                ext.append(s)
            else:
                while di < len(defaults):
                    c = defaults[di].strip()
                    di += 1
                    if c and not _line_redundant_with_any(c, ext):
                        new_sh.append(c[:360])
                        ext.append(c)
                        break
        if not new_sh:
            new_sh = [str(x)[:360] for x in defaults if str(x).strip()]
        p["support_hooks"] = new_sh[:3]

    st = p.get("sphere_triad")
    defaults_triad = _default_sphere_triad(foundation, locale)
    if isinstance(st, list) and len(st) == 3:
        default_by_area = {str(d.get("area") or "").lower(): d for d in defaults_triad}
        ext = list(pool)
        new_st: list[dict[str, Any]] = []
        for item in st:
            if not isinstance(item, dict):
                continue
            area = str(item.get("area") or "").strip().lower()
            line = str(item.get("line") or "").strip()
            nd = dict(item)
            if line and not _line_redundant_with_any(line, ext):
                new_st.append(nd)
                ext.append(line)
                continue
            fb = str((default_by_area.get(area) or {}).get("line") or "").strip()
            nd["line"] = (fb or line)[:280]
            new_st.append(nd)
            ext.append(str(nd["line"]))
        if len(new_st) == 3:
            p["sphere_triad"] = new_st

    wide_pool: list[str] = list(pool)
    sh_for_wide = p.get("support_hooks")
    if isinstance(sh_for_wide, list):
        for x in sh_for_wide:
            sx = str(x).strip()
            if sx:
                wide_pool.append(sx)

    pat_fb_ru = (
        "Сегодня выигрывает формат «один завершённый шаг» вместо распыления по длинному списку.",
        "Ресурс растёт, когда ты фиксируешь результат короткой записью и честной границей «достаточно».",
    )
    pat_fb_en = (
        "Today favors one finished step over a long scattered list.",
        "Energy rises when you name one closure and keep the list honest.",
    )
    pi0 = str(p.get("pattern_insight") or "").strip()
    if pi0 and _line_redundant_with_any(pi0, wide_pool):
        pats = pat_fb_en if en_loc else pat_fb_ru
        rep_p = next((d for d in pats if not _line_redundant_with_any(d, wide_pool)), pats[0])
        p["pattern_insight"] = rep_p[:500]
        wide_pool.append(rep_p)

    life_fb_ru = (
        "Долгие процессы без видимой отдачи обычно выжимают: формат с движением и смыслом ближе, чем рутина без метки прогресса.",
        "Когда день расползается в задачи без завершения, помогает один явный «закрыл — дышу» вместо десяти открытых петель.",
    )
    life_fb_en = (
        "Long stretches without visible payoff drain you: motion with meaning beats endless routine without a progress mark.",
        "When the day spreads into unfinished loops, one clear \"closed — breathe\" beats ten open threads.",
    )
    li0 = str(p.get("life_context_insight") or "").strip()
    if li0 and _line_redundant_with_any(li0, wide_pool):
        lifes = life_fb_en if en_loc else life_fb_ru
        rep_l = next((d for d in lifes if not _line_redundant_with_any(d, wide_pool)), lifes[0])
        p["life_context_insight"] = rep_l[:500]

    wl = p.get("why_astrological_layers")
    if isinstance(wl, list):
        why_pool: list[str] = list(pool)
        for di in p.get("do_items") or []:
            t = str(di).strip()
            if t:
                why_pool.append(t)
        new_layers: list[dict[str, Any]] = []
        for item in wl:
            if not isinstance(item, dict):
                continue
            layer = dict(item)
            kind = str(layer.get("kind") or "")
            detail = str(layer.get("detail") or "").strip()
            anchor = str(layer.get("anchor") or "").strip()
            if kind.startswith("ritual_"):
                new_layers.append(layer)
                continue
            if detail and _line_redundant_with_any(detail, why_pool):
                layer["detail"] = _neutral_why_detail_replacement(anchor, locale)
            new_layers.append(layer)
            d2 = str(layer.get("detail") or "").strip()
            if d2:
                why_pool.append(d2)
        p["why_astrological_layers"] = new_layers[:8]

    return p


def _openai_json(
    system: str,
    user: str,
    *,
    depth_level: str = "normal",
    max_tokens_override: int | None = None,
) -> dict[str, Any] | None:
    if not is_llm_chat_configured():
        return None
    client = get_openai_compatible_client()
    if client is None:
        return None

    dl = _normalize_depth_level(depth_level)
    # Defaults follow LLM_QUALITY_MODE (rich = generous; economize = legacy tight caps).
    temperature = 0.48 if dl == "quick" else (0.54 if dl == "deep" else 0.52)
    max_tokens = funnel_step_max_tokens(dl)
    if isinstance(max_tokens_override, int) and max_tokens_override > 0:
        max_tokens = max_tokens_override

    content = chat_completion_plain(
        client,
        model=resolve_default_chat_model(),
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=temperature,
        max_tokens=resolve_max_tokens(max_tokens),
    )
    if not content:
        return None
    return _parse_json_content(content)


def _fusion_slim_for_prompt(fusion_dump: dict[str, Any]) -> dict[str, Any]:
    """Компактный fusion для промптов без тяжёлых cycle/activity блоков; сохраняет rhythm_context."""
    if not isinstance(fusion_dump, dict):
        return {}
    rc = fusion_dump.get("rhythm_context")
    ac = fusion_dump.get("activity_context")
    flow_flags: dict[str, Any] = {}
    if isinstance(ac, dict):
        for k in ("morning_completed", "day_completed", "evening_completed"):
            if k in ac:
                flow_flags[k] = bool(ac[k])
        if "guide_action_options_selected_today" in ac:
            try:
                flow_flags["guide_action_options_selected_today"] = max(
                    0, min(50, int(ac["guide_action_options_selected_today"]))
                )
            except (TypeError, ValueError):
                flow_flags["guide_action_options_selected_today"] = 0
        raw_gmc = ac.get("guide_meaning_completions_today")
        if isinstance(raw_gmc, dict):
            clamped_gmc: dict[str, int] = {}
            for k in GUIDE_MEANING_COMPLETION_EVENT_TYPES:
                try:
                    v = int(raw_gmc.get(k) or 0)
                except (TypeError, ValueError):
                    v = 0
                clamped_gmc[k] = max(0, min(50, v))
            flow_flags["guide_meaning_completions_today"] = clamped_gmc
    out: dict[str, Any] = {
        "scores": fusion_dump.get("scores"),
        "encouragement": fusion_dump.get("encouragement"),
        "recommendations": fusion_dump.get("recommendations")
        if isinstance(fusion_dump.get("recommendations"), list)
        else [],
        "rhythm_context": rc if isinstance(rc, dict) else {},
    }
    if flow_flags:
        out["activity_context"] = flow_flags
    return out


def _day_model_snapshot_for_guide(
    db: Session,
    *,
    user_id: int,
    target_date: date,
    foundation: dict[str, Any] | None,
    ritual_norm: dict[str, Any],
    fusion_dump: dict[str, Any],
    intent_slice: dict[str, Any] | None,
    core_profile: dict[str, Any] | None,
    locale_value: str,
) -> dict[str, Any]:
    """Детерминированный DayModel для guide (кэш-хит без полного DayContext)."""
    scores = (fusion_dump or {}).get("scores") if isinstance(fusion_dump, dict) else {}
    bp = _meaning_patterns_from_core(core_profile)
    if bp is None:
        bp = build_meaning_surface_patterns_v0(
            db, user_id=user_id, reference_date=target_date, window_days=28
        )
    fu = fusion_dump if isinstance(fusion_dump, dict) else {}
    ip = build_internal_profile_slice_v0(
        core_profile=core_profile if isinstance(core_profile, dict) else None,
        behavior_patterns=bp,
        fusion_layer=fu,
    )
    hist = build_history_layer_v0(
        db,
        user_id=user_id,
        target_date=target_date,
        today_fusion_scores=scores if isinstance(scores, dict) else {},
    )
    return build_day_model_v0(
        foundation=foundation,
        ritual=ritual_norm if ritual_norm else None,
        fusion_scores=scores if isinstance(scores, dict) else {},
        intent_slice=intent_slice,
        internal_profile=ip if isinstance(ip, dict) else None,
        locale=locale_value,
        history_slice=hist,
    )


def build_today_narrative(
    db: Session,
    *,
    user_id: int,
    insight_depth_tier: str,
    target_date: date,
    locale: str,
    surface: TodaySurface,
    core_profile: dict[str, Any] | None,
    fusion_dump: dict[str, Any],
    parent_generation_id: int | None,
    deepen_topic: str | None,
    policy_version: str | None = "clean-info-v1",
    voice_profile: str | None = "live-clean-supportive-v1",
    ritual_context: dict[str, Any] | None = None,
    depth_level: str | None = None,
) -> tuple[dict[str, Any], int, bool, dict[str, Any] | None]:
    """Возвращает (payload, generation_log_id, used_fallback, profile_selector_slim)."""
    learning = get_learning_service()
    locale_value = _locale_norm(locale)
    ritual_norm = _normalize_ritual_context(ritual_context) if ritual_context else {}
    ritual_fp = _ritual_context_fingerprint(ritual_norm)

    dc_row = (
        db.query(db_models.DayConnection)
        .filter(
            db_models.DayConnection.user_id == user_id,
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

    snapshot_id = _latest_snapshot_id(db, user_id)
    topic_norm = (deepen_topic or "").strip().lower() or ""
    parent_for_cache = parent_generation_id if parent_generation_id is not None else -1
    tier_norm = (insight_depth_tier or "free").strip().lower()
    if tier_norm not in ("free", "pro", "premium"):
        tier_norm = "free"
    depth_norm = _clamp_narrative_depth_for_insight_tier(_normalize_depth_level(depth_level), tier_norm)

    foundation = _load_foundation_from_logs(db, user_id, target_date, snapshot_id)

    scores_for_brief = (fusion_dump or {}).get("scores") if isinstance(fusion_dump, dict) else {}
    day_engine_brief = build_day_narrative_brief_v0(
        foundation=foundation,
        ritual=ritual_norm if ritual_norm else None,
        fusion_scores=scores_for_brief if isinstance(scores_for_brief, dict) else {},
        intent_slice=intent_slice,
        locale=locale_value,
    )

    behavior_patterns = _meaning_patterns_from_core(core_profile)
    if behavior_patterns is None:
        behavior_patterns = build_meaning_surface_patterns_v0(
            db, user_id=user_id, reference_date=target_date, window_days=28
        )

    pol_ver = (policy_version or "clean-info-v1").strip().lower()
    voice_ver = (voice_profile or "live-clean-supportive-v1").strip().lower()
    today_scores_raw = (fusion_dump or {}).get("scores") if isinstance(fusion_dump, dict) else {}
    today_scores_for_history = today_scores_raw if isinstance(today_scores_raw, dict) else {}
    history_slice = build_history_layer_v0(
        db,
        user_id=user_id,
        target_date=target_date,
        today_fusion_scores=today_scores_for_history,
    )
    sel_surface, sel_task, sel_topic = narrative_surface_to_selector_params(surface, deepen_topic=topic_norm)
    active_knowledge_list: list[dict[str, Any]] | None = None
    knowledge_target_surface = "day_guidance_card"
    try:
        from todayflow_backend.services.day_model_v1_narrative_knowledge_hot_path import (
            resolve_active_knowledge_for_narrative,
        )

        active_knowledge_list, knowledge_target_surface = resolve_active_knowledge_for_narrative(
            db,
            user_id,
            surface=str(surface),
        )
    except Exception:
        logger.warning(
            "Active Knowledge load failed for user_id=%s surface=%s",
            user_id,
            surface,
            exc_info=True,
        )

    day_ctx = build_day_context_v0(
        target_date=target_date,
        locale=locale_value,
        insight_depth_tier=tier_norm,
        core_profile=core_profile,
        fusion_dump=fusion_dump,
        daily_foundation=foundation,
        ritual_context=ritual_norm if ritual_norm else None,
        behavior_patterns=behavior_patterns,
        intent_slice=intent_slice,
        history_slice=history_slice,
        policy_version=pol_ver,
        voice_profile=voice_ver,
        profile_snapshot_id=snapshot_id,
        ritual_context_fingerprint=ritual_fp,
        depth_level=depth_norm,
        selector_surface=sel_surface,
        selector_task=sel_task,
        selector_topic=sel_topic,
        active_knowledge_list=active_knowledge_list,
        knowledge_target_surface=knowledge_target_surface,
    )
    day_ctx_canon_pre = json.dumps(day_ctx, ensure_ascii=False, sort_keys=True, default=str)
    day_context_sha256_pre = hashlib.sha256(day_ctx_canon_pre.encode("utf-8")).hexdigest()

    layers_for_contract = day_ctx.get("layers") if isinstance(day_ctx.get("layers"), dict) else {}
    profile_selector_slim = _slim_profile_selector(layers_for_contract.get("profile_selector"))
    orchestration_meta = build_today_narrative_orchestration_meta(
        surface=str(surface),
        day_ctx=day_ctx,
        profile_selector_slim=profile_selector_slim,
        profile_selector_full=layers_for_contract.get("profile_selector")
        if isinstance(layers_for_contract.get("profile_selector"), dict)
        else None,
        day_context_sha256=day_context_sha256_pre,
    )
    from todayflow_backend.services.generation_orchestrator import attach_pim_read_audit_to_orchestration

    orchestration_meta = attach_pim_read_audit_to_orchestration(
        orchestration_meta,
        day_ctx=day_ctx,
        ritual_context=ritual_norm if ritual_norm else None,
        fusion_dump=fusion_dump if isinstance(fusion_dump, dict) else None,
    )

    cached = _load_narrative_cache(
        db,
        user_id,
        target_date,
        surface,
        parent_generation_id,
        deepen_topic,
        snapshot_id,
        tier_norm,
        locale_value,
        ritual_fp,
        intent_fp,
        day_context_sha256_pre,
        depth_norm,
        prompt_label=PROMPT_VER,
    )
    if cached and isinstance(cached.normalized_response, dict):
        cached_payload = dict(cached.normalized_response)
        if surface == "guide":
            cached_payload = _ensure_guide_actionable_fields(
                cached_payload, foundation, fusion_dump, locale_value
            )
            cached_payload = _merge_guide_why_astrological_layers(
                cached_payload, foundation, fusion_dump, core_profile, locale_value
            )
            cached_ip = cached.input_payload if isinstance(cached.input_payload, dict) else {}
            if not guide_funnel_core_is_llm_locked(cached_ip):
                _gd_c = (day_ctx.get("layers") or {}).get("guide_decision")
                cached_payload = _apply_guide_decision_to_guide_payload(
                    cached_payload, _gd_c if isinstance(_gd_c, dict) else None, locale_value
                )
            cached_payload = _ensure_guide_actionable_fields(
                cached_payload, foundation, fusion_dump, locale_value
            )
            cached_payload = _dedupe_guide_payload_cross_fields(
                cached_payload, foundation, fusion_dump, locale_value, day_engine_brief=day_engine_brief
            )
            cached_payload = strip_meta_from_guide_payload(cached_payload)
            cached_payload = _normalize_guide_payload_for_tier(cached_payload, tier_norm)
            if not (
                _narrative_payload_acceptable("guide", cached_payload, locale_value, ritual_norm=ritual_norm)
                and _narrative_guide_brief_aligned(locale_value, cached_payload, day_engine_brief)
            ):
                cached = None
        elif surface == "day_layer":
            cached_payload = _finalize_day_layer_payload_o8(cached_payload, day_engine_brief=day_engine_brief)
            if not _narrative_payload_acceptable("day_layer", cached_payload, locale_value):
                cached = None
        if cached is not None:
            if surface == "guide" and isinstance(cached_payload, dict):
                cached_payload = dict(cached_payload)
                cached_payload["day_engine_brief"] = day_engine_brief
                cached_payload["day_model"] = _day_model_snapshot_for_guide(
                    db,
                    user_id=user_id,
                    target_date=target_date,
                    foundation=foundation,
                    ritual_norm=ritual_norm,
                    fusion_dump=fusion_dump,
                    intent_slice=intent_slice,
                    core_profile=core_profile,
                    locale_value=locale_value,
                )
                _ly_ret = day_ctx.get("layers") if isinstance(day_ctx.get("layers"), dict) else {}
                _gdo = _ly_ret.get("guide_decision")
                if isinstance(_gdo, dict):
                    cached_payload["guide_decision"] = _gdo
                _attach_narrative_hierarchy_to_guide_payload(cached_payload)
                attach_guide_contract_v2(cached_payload, input_payload=cached_ip)
            from todayflow_backend.services.today_narrative_llm_gate_v1 import build_cache_hit_gate_v1

            _cached_ip_hash = str((cached.input_payload or {}).get("day_context_sha256") or "")
            _cache_match_mode = (
                "exact"
                if _cached_ip_hash and _cached_ip_hash == day_context_sha256_pre
                else "same_day_reuse"
            )
            cache_gate = build_cache_hit_gate_v1(
                surface=str(surface),
                source_generation_log_id=int(cached.id),
                context_slice_id=day_context_sha256_pre,
                match_mode=_cache_match_mode,
            )
            ps_out = dict(profile_selector_slim) if isinstance(profile_selector_slim, dict) else {}
            ps_out["amll_gate"] = cache_gate
            return cached_payload, cached.id, bool(cached.used_fallback), ps_out

    if surface in ("guide", "spheres", "day_layer", "evening"):
        from todayflow_backend.services.day_story_wire_v1 import (
            resolve_narrative_surface_via_day_story_v1,
        )

        ds_hit = resolve_narrative_surface_via_day_story_v1(
            db,
            user_id=user_id,
            surface=str(surface),
            target_date=target_date,
            locale=locale_value,
            core_profile=core_profile,
            fusion_dump=fusion_dump if isinstance(fusion_dump, dict) else {},
            ritual_norm=ritual_norm,
            parent_generation_id=parent_generation_id,
            build_if_missing=(surface == "guide"),
        )
        if ds_hit is not None:
            ds_payload, ds_gen_id, ds_used_fb = ds_hit
            if surface == "guide" and isinstance(ds_payload, dict):
                ds_payload = dict(ds_payload)
                ds_payload["day_engine_brief"] = day_engine_brief
                ds_payload["day_model"] = _day_model_snapshot_for_guide(
                    db,
                    user_id=user_id,
                    target_date=target_date,
                    foundation=foundation,
                    ritual_norm=ritual_norm,
                    fusion_dump=fusion_dump,
                    intent_slice=intent_slice,
                    core_profile=core_profile,
                    locale_value=locale_value,
                )
                _ly_ds = day_ctx.get("layers") if isinstance(day_ctx.get("layers"), dict) else {}
                _gdo_ds = _ly_ds.get("guide_decision")
                if isinstance(_gdo_ds, dict):
                    ds_payload["guide_decision"] = _gdo_ds
                _attach_narrative_hierarchy_to_guide_payload(ds_payload)
            ps_out = dict(profile_selector_slim) if isinstance(profile_selector_slim, dict) else {}
            ps_out["day_story_source"] = "day_story_v1"
            return ds_payload, ds_gen_id, ds_used_fb, ps_out

    from todayflow_backend.services.today_narrative_llm_gate_v1 import (
        GATE_DECISION_CALL_LLM,
        decide_today_narrative_llm_call_v1,
        should_skip_llm_for_gate,
    )

    llm_configured = is_llm_chat_configured()
    bp_total = (
        int(behavior_patterns.get("total_events") or 0)
        if isinstance(behavior_patterns, dict)
        else 0
    )
    amll_gate = decide_today_narrative_llm_call_v1(
        surface=str(surface),
        llm_configured=llm_configured,
        cache_status={"exact_hit": False, "similarity_available": False},
        user_context={
            "has_day_context": bool(day_ctx),
            "has_foundation": foundation is not None,
            "behavior_event_count": bp_total,
            "quality_mode": _narrative_quality_mode(),
            "context_slice_id": day_context_sha256_pre,
        },
        depth_level=depth_norm,
    )
    skip_llm = should_skip_llm_for_gate(amll_gate)
    llm_max_tokens = (
        int(amll_gate["max_tokens"])
        if amll_gate.get("gate_decision") == GATE_DECISION_CALL_LLM
        else None
    )
    orchestration_meta = attach_amll_gate_to_orchestration(orchestration_meta, amll_gate)

    parent_row = _load_generation_by_id(db, user_id, parent_generation_id) if parent_generation_id else None
    parent_payload = (
        parent_row.normalized_response if parent_row and isinstance(parent_row.normalized_response, dict) else {}
    )
    prior_thesis = str(parent_payload.get("context_for_next_surfaces") or parent_payload.get("headline") or "")
    funnel_chain: dict[str, Any] | None = None
    if surface in ("day_layer", "spheres", "evening", "deepen"):
        funnel_chain = _resolve_funnel_chain_from_guide_parent(db, user_id, parent_row, parent_payload)

    system_prompt = _system_prompt_for_surface(
        surface, locale_value, depth_level=depth_norm, ritual_norm=ritual_norm, funnel_chain=funnel_chain
    )
    _pv_meta: dict[str, Any] = {"surface": surface, "locale": locale_value, "depth_level": depth_norm}
    if _ritual_mood_is_low_energy(ritual_norm):
        _pv_meta["low_energy_ritual_mood"] = str((ritual_norm or {}).get("mood") or "").strip().lower()
    pv = learning.get_or_create_prompt_version(
        db,
        module=MODULE,
        version=PROMPT_VER,
        prompt_kind="system",
        prompt_text=system_prompt,
        label=f"narrative_{surface}",
        metadata=_pv_meta,
    )

    started = perf_counter()
    input_payload: dict[str, Any] = {
        "target_date": target_date.isoformat(),
        "surface": surface,
        "parent_generation_id": parent_for_cache,
        "deepen_topic": topic_norm,
        "insight_depth_tier": tier_norm,
        "depth_level": depth_norm,
        "locale": locale_value,
        "policy_version": pol_ver,
        "voice_profile": voice_ver,
        "ritual_context_fp": ritual_fp,
        "intent_context_fp": intent_fp,
        "prompt_label": PROMPT_VER,
        "narrative_quality_mode": _narrative_quality_mode(),
    }
    if ritual_norm:
        input_payload["ritual_context"] = ritual_norm
    if funnel_chain:
        input_payload["guide_funnel_chain_used"] = True
        input_payload["guide_funnel_child_chain_contract"] = FUNNEL_CHILD_CHAIN_CONTRACT
        input_payload["guide_funnel_step1_log_id"] = funnel_chain.get("guide_funnel_step1_log_id")
        if funnel_chain.get("guide_funnel_step2_log_id") is not None:
            input_payload["guide_funnel_step2_log_id"] = funnel_chain.get("guide_funnel_step2_log_id")
    if surface == "guide":
        input_payload["day_engine_brief_contract"] = day_engine_brief.get("contract_version")

    input_payload["day_context_sha256"] = day_context_sha256_pre
    input_payload["day_context_contract_version"] = day_ctx.get("contract_version")
    if isinstance(layers_for_contract.get("day_model"), dict):
        input_payload["day_model_contract"] = "day_model_v0"
    if isinstance(layers_for_contract.get("guide_decision"), dict):
        input_payload["guide_decision_contract"] = "guide_decision_v0"
    _kumt = layers_for_contract.get("knowledge_usage_metrics_trace")
    if isinstance(_kumt, dict):
        from todayflow_backend.services.day_model_v1_narrative_knowledge_hot_path import (
            slim_knowledge_usage_metrics_for_log,
        )

        input_payload["knowledge_hot_path_active"] = True
        input_payload["knowledge_target_surface"] = _kumt.get("target_surface")
        input_payload["knowledge_usage_metrics_trace"] = slim_knowledge_usage_metrics_for_log(
            _kumt
        )
    _ps_log = profile_selector_slim
    if _ps_log:
        input_payload["profile_selector"] = _ps_log
    input_payload["orchestration"] = orchestration_meta
    input_payload["amll_gate"] = amll_gate
    input_payload["gate_decision"] = amll_gate.get("gate_decision")
    input_payload["amll_skip_llm"] = skip_llm
    input_payload["llm_quality_policy"] = quality_policy_snapshot()

    def _call_narrative_llm(system: str, user: str) -> dict[str, Any] | None:
        if skip_llm:
            return None
        return _openai_json(
            system,
            user,
            depth_level=depth_norm,
            max_tokens_override=llm_max_tokens,
        )

    payload: dict[str, Any] | None = None
    used_fb = True
    guide_user_prompt_for_retry: str | None = None

    try:
        layers_dc = day_ctx["layers"] if isinstance(day_ctx.get("layers"), dict) else {}
        uc_layer = layers_dc.get("user_core")
        user_core = (
            uc_layer
            if isinstance(uc_layer, dict)
            else _core_context_for_narrative(core_profile, locale=locale_value)
        )
        fu_layer = layers_dc.get("fusion")
        fusion_for_prompt = fu_layer if isinstance(fu_layer, dict) else fusion_dump
        policy_block = {
            "policy_version": input_payload["policy_version"],
            "voice_profile": input_payload["voice_profile"],
            "depth_level": depth_norm,
            "constraints": {
                "clean_information": True,
                "no_fear_pressure": True,
                "no_absolute_certainty": True,
                "preserve_user_agency": True,
                "live_human_tone": True,
                "always_include_action_step_when_relevant": True,
            },
        }
        if surface == "guide":
            guide_user: dict[str, Any] = {
                "insight_depth_tier": tier_norm,
                "depth_level": depth_norm,
                "policy": policy_block,
                "user_core": user_core,
                "fusion": fusion_for_prompt,
                "daily_foundation": layers_dc.get("daily_foundation", foundation),
            }
            ritual_layer = layers_dc.get("ritual")
            if isinstance(ritual_layer, dict) and ritual_layer:
                guide_user["ritual_context"] = ritual_layer
            elif ritual_norm:
                guide_user["ritual_context"] = ritual_norm
            bp_layer = layers_dc.get("behavior_patterns")
            if isinstance(bp_layer, dict) and bp_layer.get("total_events"):
                guide_user["behavior_patterns"] = bp_layer
            intent_layer = layers_dc.get("intent")
            if isinstance(intent_layer, dict) and intent_layer.get("contract_version"):
                guide_user["intent"] = intent_layer
            guide_user["day_engine_brief"] = day_engine_brief
            dm = layers_dc.get("day_model")
            if isinstance(dm, dict):
                guide_user["day_model"] = dm
            gd = layers_dc.get("guide_decision")
            if isinstance(gd, dict):
                guide_user["guide_decision"] = gd
            _attach_profile_slices(guide_user, layers_dc)
            _attach_profile_selector(guide_user, layers_dc)
            _attach_day_history_to_llm_pack(guide_user, layers_dc)
            user_prompt = json.dumps(guide_user, ensure_ascii=False)[: user_json_char_budget()]
            guide_user_prompt_for_retry = user_prompt
            funnel_ok = False
            if llm_configured and not skip_llm:
                s1_txt, s3_txt, s2_txt = funnel_system_prompts_for_locale(locale_value)
                pv_f1 = learning.get_or_create_prompt_version(
                    db,
                    module=MODULE,
                    version=FUNNEL_PROMPT_VER_STEP1,
                    prompt_kind="system",
                    prompt_text=s1_txt,
                    label="guide_funnel_step1",
                    metadata={"funnel": FUNNEL_CONTRACT, "step": "interpretation"},
                )
                pv_f3 = learning.get_or_create_prompt_version(
                    db,
                    module=MODULE,
                    version=FUNNEL_PROMPT_VER_STEP3,
                    prompt_kind="system",
                    prompt_text=s3_txt,
                    label="guide_funnel_step3",
                    metadata={"funnel": FUNNEL_CONTRACT, "step": "core_text"},
                )
                pv_f2 = learning.get_or_create_prompt_version(
                    db,
                    module=MODULE,
                    version=FUNNEL_PROMPT_VER_STEP2,
                    prompt_kind="system",
                    prompt_text=s2_txt,
                    label="guide_funnel_step2",
                    metadata={"funnel": FUNNEL_CONTRACT, "step": "satellites"},
                )
                funnel_base_payload = {
                    **input_payload,
                    "guide_funnel_contract": FUNNEL_CONTRACT,
                }
                cached_step1 = _load_funnel_step_cache(
                    db,
                    user_id,
                    target_date,
                    funnel_step="interpretation_v0",
                    funnel_prompt_ver=FUNNEL_PROMPT_VER_STEP1,
                    snapshot_id=snapshot_id,
                    tier_norm=tier_norm,
                    depth_norm=depth_norm,
                    locale=locale_value,
                    ritual_fp=ritual_fp,
                    intent_fp=intent_fp,
                    day_context_sha256=day_context_sha256_pre,
                )
                interp_part: dict[str, Any] | None = None
                core_part: dict[str, Any] | None = None
                funnel_parent_log_id: int | None = None
                funnel_step3_log_id: int | None = None
                step1_cache_hit = False
                step3_cache_hit = False
                if cached_step1 and isinstance(cached_step1.normalized_response, dict):
                    interp_part = dict(cached_step1.normalized_response)
                    funnel_parent_log_id = cached_step1.id
                    step1_cache_hit = True

                cached_step3 = None
                if funnel_parent_log_id is not None:
                    cached_step3 = _load_funnel_step_cache(
                        db,
                        user_id,
                        target_date,
                        funnel_step="core_text_v0",
                        funnel_prompt_ver=FUNNEL_PROMPT_VER_STEP3,
                        snapshot_id=snapshot_id,
                        tier_norm=tier_norm,
                        depth_norm=depth_norm,
                        locale=locale_value,
                        ritual_fp=ritual_fp,
                        intent_fp=intent_fp,
                        day_context_sha256=day_context_sha256_pre,
                        parent_generation_log_id=funnel_parent_log_id,
                    )
                    if (
                        cached_step3
                        and isinstance(cached_step3.normalized_response, dict)
                        and is_funnel_core_text_valid(cached_step3.normalized_response)
                    ):
                        core_part = dict(cached_step3.normalized_response)
                        funnel_step3_log_id = cached_step3.id
                        step3_cache_hit = True

                cached_step2 = None
                if funnel_parent_log_id is not None:
                    cached_step2 = _load_funnel_step_cache(
                        db,
                        user_id,
                        target_date,
                        funnel_step="satellites_v0",
                        funnel_prompt_ver=FUNNEL_PROMPT_VER_STEP2,
                        snapshot_id=snapshot_id,
                        tier_norm=tier_norm,
                        depth_norm=depth_norm,
                        locale=locale_value,
                        ritual_fp=ritual_fp,
                        intent_fp=intent_fp,
                        day_context_sha256=day_context_sha256_pre,
                        parent_generation_log_id=funnel_parent_log_id,
                    )

                if (
                    cached_step2
                    and isinstance(cached_step2.normalized_response, dict)
                    and is_funnel_satellites_valid(cached_step2.normalized_response)
                ):
                    sat_cached = {
                        k: v
                        for k, v in cached_step2.normalized_response.items()
                        if k != "contract_version"
                    }
                    sat_cached["funnel_contract"] = FUNNEL_CONTRACT
                    merged_cached = _guide_payload_from_funnel_satellites(
                        sat_cached,
                        layers_dc=layers_dc,
                        foundation=foundation,
                        fusion_for_prompt=fusion_for_prompt,
                        core_profile=core_profile,
                        locale_value=locale_value,
                        ritual_norm=ritual_norm,
                        funnel_core=core_part,
                    )
                    if merged_cached is not None:
                        payload = merged_cached
                        funnel_ok = True
                        used_fb = False
                        input_payload["guide_funnel_used"] = True
                        input_payload["guide_funnel_contract"] = FUNNEL_CONTRACT
                        input_payload["guide_funnel_parent_log_id"] = funnel_parent_log_id
                        input_payload["guide_funnel_step1_cache_hit"] = step1_cache_hit
                        input_payload["guide_funnel_step3_cache_hit"] = step3_cache_hit
                        input_payload["guide_funnel_step2_cache_hit"] = True
                        if funnel_step3_log_id is not None:
                            input_payload["guide_funnel_step3_log_id"] = funnel_step3_log_id
                        input_payload["guide_funnel_step2_log_id"] = cached_step2.id
                        input_payload["guide_funnel_core_source"] = (
                            "funnel_core_text_v0"
                            if isinstance(core_part, dict) and is_funnel_core_text_valid(core_part)
                            else "guide_decision_v0"
                        )
                        record_guide_funnel_step_handoffs(
                            input_payload,
                            interp=interp_part,
                            core=core_part,
                            satellites=sat_cached,
                        )

                if not funnel_ok:
                    sat_part, interp_new, core_new, funnel_meta = run_guide_narrative_funnel_v0(
                        funnel_openai_json_adapter,
                        locale_value=locale_value,
                        tier_norm=tier_norm,
                        depth_norm=depth_norm,
                        guide_user=guide_user,
                        foundation=foundation,
                        fusion_for_prompt=fusion_for_prompt,
                        cached_interpretation=interp_part if step1_cache_hit else None,
                        cached_core_text=core_part if step3_cache_hit else None,
                    )
                    if isinstance(interp_new, dict) and not step1_cache_hit:
                        interp_part = interp_new
                        gen_f1 = learning.log_generation(
                            db,
                            module=MODULE,
                            surface="guide_funnel_v0",
                            user_id=user_id,
                            core_profile_snapshot_id=snapshot_id,
                            prompt_version_id=pv_f1.id,
                            model=resolve_default_chat_model(),
                            locale=locale_value,
                            input_payload={
                                **funnel_base_payload,
                                "narrative_funnel_step": "interpretation_v0",
                                "funnel_prompt_ver": FUNNEL_PROMPT_VER_STEP1,
                                "parent_generation_log_id": None,
                            },
                            system_prompt=s1_txt[:2000],
                            user_prompt=str(funnel_meta.get("user_json_step1") or "")[:8000],
                            normalized_response=interp_part,
                            status="success",
                            used_fallback=False,
                            duration_ms=int(funnel_meta.get("step1_ms") or 0),
                        )
                        funnel_parent_log_id = gen_f1.id
                    elif isinstance(interp_new, dict):
                        interp_part = interp_new

                    if (
                        isinstance(core_new, dict)
                        and is_funnel_core_text_valid(core_new)
                        and not step3_cache_hit
                    ):
                        core_part = core_new
                        gen_f3 = learning.log_generation(
                            db,
                            module=MODULE,
                            surface="guide_funnel_v0",
                            user_id=user_id,
                            core_profile_snapshot_id=snapshot_id,
                            prompt_version_id=pv_f3.id,
                            model=resolve_default_chat_model(),
                            locale=locale_value,
                            input_payload={
                                **funnel_base_payload,
                                "narrative_funnel_step": "core_text_v0",
                                "funnel_prompt_ver": FUNNEL_PROMPT_VER_STEP3,
                                "parent_generation_log_id": funnel_parent_log_id,
                            },
                            system_prompt=s3_txt[:2000],
                            user_prompt=str(funnel_meta.get("user_json_step3") or "")[:8000],
                            normalized_response=core_part,
                            status="success",
                            used_fallback=False,
                            duration_ms=int(funnel_meta.get("step3_ms") or 0),
                        )
                        funnel_step3_log_id = gen_f3.id
                    elif isinstance(core_new, dict) and is_funnel_core_text_valid(core_new):
                        core_part = core_new

                    if isinstance(sat_part, dict) and not funnel_meta.get("failed"):
                        merged_try = _guide_payload_from_funnel_satellites(
                            sat_part,
                            layers_dc=layers_dc,
                            foundation=foundation,
                            fusion_for_prompt=fusion_for_prompt,
                            core_profile=core_profile,
                            locale_value=locale_value,
                            ritual_norm=ritual_norm,
                            funnel_core=core_part,
                        )
                        if merged_try is not None:
                            gen_f2 = learning.log_generation(
                                db,
                                module=MODULE,
                                surface="guide_funnel_v0",
                                user_id=user_id,
                                core_profile_snapshot_id=snapshot_id,
                                prompt_version_id=pv_f2.id,
                                model=resolve_default_chat_model(),
                                locale=locale_value,
                                input_payload={
                                    **funnel_base_payload,
                                    "narrative_funnel_step": "satellites_v0",
                                    "funnel_prompt_ver": FUNNEL_PROMPT_VER_STEP2,
                                    "parent_generation_log_id": funnel_parent_log_id,
                                },
                                system_prompt=s2_txt[:2000],
                                user_prompt=str(funnel_meta.get("user_json_step2") or "")[:8000],
                                normalized_response={
                                    **{
                                        k: v
                                        for k, v in sat_part.items()
                                        if k not in ("funnel_contract", "contract_version")
                                    },
                                    "contract_version": SATELLITES_CONTRACT,
                                },
                                status="success",
                                used_fallback=False,
                                duration_ms=int(funnel_meta.get("step2_ms") or 0),
                            )
                            payload = merged_try
                            funnel_ok = True
                            used_fb = False
                            input_payload["guide_funnel_contract"] = FUNNEL_CONTRACT
                            input_payload["guide_funnel_used"] = True
                            input_payload["guide_funnel_parent_log_id"] = funnel_parent_log_id
                            input_payload["guide_funnel_step1_cache_hit"] = bool(
                                funnel_meta.get("step1_cache_hit") or step1_cache_hit
                            )
                            input_payload["guide_funnel_step3_cache_hit"] = bool(
                                funnel_meta.get("step3_cache_hit") or step3_cache_hit
                            )
                            input_payload["guide_funnel_step2_cache_hit"] = False
                            if funnel_step3_log_id is not None:
                                input_payload["guide_funnel_step3_log_id"] = funnel_step3_log_id
                            input_payload["guide_funnel_step2_log_id"] = gen_f2.id
                            input_payload["guide_funnel_core_source"] = (
                                "funnel_core_text_v0"
                                if isinstance(core_part, dict) and is_funnel_core_text_valid(core_part)
                                else "guide_decision_v0"
                            )
                            record_guide_funnel_step_handoffs(
                                input_payload,
                                interp=interp_part,
                                core=core_part,
                                satellites=sat_part,
                            )
            if not funnel_ok:
                payload = _call_narrative_llm(system_prompt, user_prompt)
                used_fb = True
                if payload and payload.get("headline"):
                    payload = _ensure_guide_actionable_fields(payload, foundation, fusion_for_prompt, locale_value)
                    if _narrative_payload_acceptable("guide", payload, locale_value, ritual_norm=ritual_norm):
                        merged_guide = _merge_guide_why_astrological_layers(
                            payload, foundation, fusion_for_prompt, core_profile, locale_value
                        )
                        if _narrative_payload_acceptable(
                            "guide", merged_guide, locale_value, ritual_norm=ritual_norm
                        ):
                            payload = merged_guide
                            used_fb = False
                if used_fb:
                    payload = _fallback_guide(foundation, fusion_for_prompt, core_profile, tier_norm, locale_value)

        elif surface == "day_layer":
            if not prior_thesis and foundation:
                spine = foundation.get("spine")
                if isinstance(spine, dict):
                    prior_thesis = json.dumps(spine, ensure_ascii=False)[:2000]
            day_layer_pack: dict[str, Any] = {
                "policy": policy_block,
                "user_core": user_core,
                "prior_thesis": prior_thesis,
                "fusion": fusion_for_prompt,
                "encouragement": fusion_for_prompt.get("encouragement"),
            }
            bp_dl = layers_dc.get("behavior_patterns")
            if isinstance(bp_dl, dict) and bp_dl.get("total_events"):
                day_layer_pack["behavior_patterns"] = bp_dl
            intent_dl = layers_dc.get("intent")
            if isinstance(intent_dl, dict) and intent_dl.get("contract_version"):
                day_layer_pack["intent"] = intent_dl
            _attach_profile_slices(day_layer_pack, layers_dc)
            _attach_profile_selector(day_layer_pack, layers_dc)
            _attach_day_history_to_llm_pack(day_layer_pack, layers_dc)
            _attach_day_logic_slices(day_layer_pack, layers_dc=layers_dc, day_engine_brief=day_engine_brief)
            _attach_funnel_chain_to_child_pack(day_layer_pack, funnel_chain)
            user_prompt = json.dumps(day_layer_pack, ensure_ascii=False)[: user_json_char_budget()]
            payload = None
            if llm_configured and not skip_llm:
                funnel_payload, funnel_meta = run_surface_disclosure_funnel_v0(
                    "day_layer",
                    surface_funnel_openai_json_adapter,
                    locale_value=locale_value,
                    depth_norm=depth_norm,
                    user_pack=day_layer_pack,
                )
                input_payload["disclosure_funnel"] = funnel_meta
                if isinstance(funnel_payload, dict) and funnel_payload.get("nudge_message"):
                    payload = funnel_payload
            if payload is None:
                payload = _call_narrative_llm(system_prompt, user_prompt)
            if isinstance(payload, dict):
                payload = _finalize_day_layer_payload_o8(payload, day_engine_brief=day_engine_brief)
            if (
                not skip_llm
                and payload
                and payload.get("nudge_message")
                and _narrative_payload_acceptable("day_layer", payload, locale_value)
            ):
                used_fb = False
            else:
                enc = str(fusion_for_prompt.get("encouragement") or ("Steady pace today: one step and one check-in." if _is_en_locale(locale_value) else "Ровный день — один шаг и фиксация."))
                recs = fusion_for_prompt.get("recommendations") if isinstance(fusion_for_prompt.get("recommendations"), list) else []
                payload = _finalize_day_layer_payload_o8(
                    _fallback_day_layer(enc, [str(x) for x in recs], locale_value),
                    day_engine_brief=day_engine_brief,
                )

        elif surface == "spheres":
            if not prior_thesis and foundation:
                spine = foundation.get("spine")
                if isinstance(spine, dict):
                    prior_thesis = str(spine.get("day_axis") or spine.get("first_move") or "")[:1200]
            scenarios = (foundation or {}).get("scenarios") if foundation else []
            spheres_pack: dict[str, Any] = {
                "policy": policy_block,
                "user_core": user_core,
                "prior_thesis": prior_thesis,
                "scenarios": scenarios,
                "spine": (foundation or {}).get("spine"),
                "fusion": _fusion_slim_for_prompt(fusion_for_prompt),
            }
            bp_sp = layers_dc.get("behavior_patterns")
            if isinstance(bp_sp, dict) and bp_sp.get("total_events"):
                spheres_pack["behavior_patterns"] = bp_sp
            intent_sp = layers_dc.get("intent")
            if isinstance(intent_sp, dict) and intent_sp.get("contract_version"):
                spheres_pack["intent"] = intent_sp
            _attach_profile_slices(spheres_pack, layers_dc)
            _attach_profile_selector(spheres_pack, layers_dc)
            _attach_day_history_to_llm_pack(spheres_pack, layers_dc)
            _attach_day_logic_slices(spheres_pack, layers_dc=layers_dc, day_engine_brief=day_engine_brief)
            _attach_funnel_chain_to_child_pack(spheres_pack, funnel_chain)
            user_prompt = json.dumps(spheres_pack, ensure_ascii=False)[: user_json_char_budget()]
            payload = None
            if llm_configured and not skip_llm:
                funnel_payload, funnel_meta = run_surface_disclosure_funnel_v0(
                    "spheres",
                    surface_funnel_openai_json_adapter,
                    locale_value=locale_value,
                    depth_norm=depth_norm,
                    user_pack=spheres_pack,
                )
                input_payload["disclosure_funnel"] = funnel_meta
                if isinstance(funnel_payload, dict) and funnel_payload.get("page_intro"):
                    payload = funnel_payload
            if payload is None:
                payload = _call_narrative_llm(system_prompt, user_prompt)
            spheres_rhythm_ctx: dict[str, Any] = {}
            if isinstance(fusion_for_prompt, dict):
                _rc_sp = fusion_for_prompt.get("rhythm_context")
                if isinstance(_rc_sp, dict):
                    spheres_rhythm_ctx = _rc_sp
            if (
                not skip_llm
                and payload
                and payload.get("page_intro")
                and _narrative_payload_acceptable(
                    "spheres", payload, locale_value, spheres_rhythm_ctx=spheres_rhythm_ctx
                )
            ):
                used_fb = False
            else:
                payload = _fallback_spheres(prior_thesis, locale_value)

        elif surface == "evening":
            evening_pack: dict[str, Any] = {
                "policy": policy_block,
                "user_core": user_core,
                "prior_thesis": prior_thesis,
                "fusion": _fusion_slim_for_prompt(fusion_for_prompt),
            }
            bp_ev = layers_dc.get("behavior_patterns")
            if isinstance(bp_ev, dict) and bp_ev.get("total_events"):
                evening_pack["behavior_patterns"] = bp_ev
            intent_ev = layers_dc.get("intent")
            if isinstance(intent_ev, dict) and intent_ev.get("contract_version"):
                evening_pack["intent"] = intent_ev
            _attach_profile_slices(evening_pack, layers_dc)
            _attach_profile_selector(evening_pack, layers_dc)
            _attach_day_history_to_llm_pack(evening_pack, layers_dc)
            _attach_day_logic_slices(evening_pack, layers_dc=layers_dc, day_engine_brief=day_engine_brief)
            _attach_funnel_chain_to_child_pack(evening_pack, funnel_chain)
            user_prompt = json.dumps(evening_pack, ensure_ascii=False)[: user_json_char_budget()]
            payload = None
            if llm_configured and not skip_llm:
                funnel_payload, funnel_meta = run_surface_disclosure_funnel_v0(
                    "evening",
                    surface_funnel_openai_json_adapter,
                    locale_value=locale_value,
                    depth_norm=depth_norm,
                    user_pack=evening_pack,
                )
                input_payload["disclosure_funnel"] = funnel_meta
                if isinstance(funnel_payload, dict) and funnel_payload.get("panel_intro"):
                    payload = funnel_payload
            if payload is None:
                payload = _call_narrative_llm(system_prompt, user_prompt)
            if (
                not skip_llm
                and payload
                and payload.get("panel_intro")
                and _narrative_payload_acceptable("evening", payload, locale_value)
            ):
                used_fb = False
            else:
                payload = _fallback_evening(locale_value)

        elif surface == "deepen":
            if topic_norm not in ("love", "money", "career", "family", "full_day"):
                topic_norm = "full_day"
            deepen_pack: dict[str, Any] = {
                "policy": policy_block,
                "user_core": user_core,
                "topic": topic_norm,
                "prior_thesis": prior_thesis,
                "foundation_spine": (foundation or {}).get("spine"),
                "scenarios": (foundation or {}).get("scenarios"),
                "fusion": _fusion_slim_for_prompt(fusion_for_prompt),
            }
            bp_dp = layers_dc.get("behavior_patterns")
            if isinstance(bp_dp, dict) and bp_dp.get("total_events"):
                deepen_pack["behavior_patterns"] = bp_dp
            intent_dp = layers_dc.get("intent")
            if isinstance(intent_dp, dict) and intent_dp.get("contract_version"):
                deepen_pack["intent"] = intent_dp
            _attach_profile_slices(deepen_pack, layers_dc)
            _attach_profile_selector(deepen_pack, layers_dc)
            _attach_day_history_to_llm_pack(deepen_pack, layers_dc)
            _attach_day_logic_slices(deepen_pack, layers_dc=layers_dc, day_engine_brief=day_engine_brief)
            _attach_funnel_chain_to_child_pack(deepen_pack, funnel_chain)
            user_prompt = json.dumps(deepen_pack, ensure_ascii=False)[: user_json_char_budget()]
            payload = None
            if llm_configured and not skip_llm:
                funnel_payload, funnel_meta = run_surface_disclosure_funnel_v0(
                    "deepen",
                    surface_funnel_openai_json_adapter,
                    locale_value=locale_value,
                    depth_norm=depth_norm,
                    user_pack=deepen_pack,
                )
                input_payload["disclosure_funnel"] = funnel_meta
                if isinstance(funnel_payload, dict) and funnel_payload.get("body"):
                    payload = funnel_payload
            if payload is None:
                payload = _call_narrative_llm(system_prompt, user_prompt)
            if (
                not skip_llm
                and payload
                and payload.get("body")
                and _narrative_payload_acceptable("deepen", payload, locale_value)
            ):
                used_fb = False
            else:
                payload = _fallback_deepen(topic_norm, prior_thesis or json.dumps(foundation or {}, ensure_ascii=False)[:800], locale_value)
        else:
            payload = _fallback_guide(foundation, fusion_for_prompt, core_profile, tier_norm, locale_value)

    except Exception as e:
        logger.warning("today_narrative LLM failed: %s", e, exc_info=True)
        if surface == "guide":
            fu_layer = (day_ctx.get("layers") or {}).get("fusion")
            fusion_fb = fu_layer if isinstance(fu_layer, dict) else fusion_dump
            payload = _fallback_guide(foundation, fusion_fb, core_profile, tier_norm, locale_value)
        elif surface == "day_layer":
            payload = _finalize_day_layer_payload_o8(
                _fallback_day_layer(
                    "Steady pace matters today." if _is_en_locale(locale_value) else "Сегодня важен ровный темп.",
                    [],
                    locale_value,
                ),
                day_engine_brief=day_engine_brief,
            )
        elif surface == "spheres":
            payload = _fallback_spheres(prior_thesis, locale_value)
        elif surface == "evening":
            payload = _fallback_evening(locale_value)
        elif surface == "deepen":
            payload = _fallback_deepen(topic_norm or "full_day", prior_thesis, locale_value)
        else:
            fu_layer = (day_ctx.get("layers") or {}).get("fusion")
            fusion_fb = fu_layer if isinstance(fu_layer, dict) else fusion_dump
            payload = _fallback_guide(foundation, fusion_fb, core_profile, tier_norm, locale_value)

    if surface == "guide" and isinstance(payload, dict):
        fu_layer = (day_ctx.get("layers") or {}).get("fusion")
        fusion_post = fu_layer if isinstance(fu_layer, dict) else fusion_dump
        preserve_funnel_core = guide_funnel_core_is_llm_locked(input_payload)
        # Alignment retry uses monolithic _openai_json (same as guide when funnel/chat is off).
        # Do not gate on is_llm_chat_configured(): otherwise first save skips alignment, but cache
        # read re-applies guide_decision and still enforces alignment — cache never hits (see tests).
        if _narrative_quality_strict() and not used_fb and guide_user_prompt_for_retry:
            probe = _guide_apply_final_processing_pass(
                dict(payload),
                day_ctx=day_ctx,
                foundation=foundation,
                fusion_post=fusion_post,
                core_profile=core_profile,
                ritual_norm=ritual_norm,
                locale_value=locale_value,
                tier_norm=tier_norm,
                day_engine_brief=day_engine_brief,
                preserve_funnel_core=preserve_funnel_core,
            )
            if (
                _validate_payload_shape("guide", probe)
                and _validate_payload_language("guide", probe, locale_value)
                and _guide_payload_concrete(locale_value, probe, ritual_norm=ritual_norm)
                and not _guide_payload_aligned_with_day_engine_brief(locale_value, probe, day_engine_brief)
            ):
                strict_sp = (system_prompt or "") + _guide_brief_alignment_retry_addon(locale_value)
                raw2 = _call_narrative_llm(strict_sp, guide_user_prompt_for_retry)
                if isinstance(raw2, dict) and raw2.get("headline"):
                    p2 = _ensure_guide_actionable_fields(dict(raw2), foundation, fusion_post, locale_value)
                    if (
                        _validate_payload_shape("guide", p2)
                        and _validate_payload_language("guide", p2, locale_value)
                        and _guide_payload_concrete(locale_value, p2, ritual_norm=ritual_norm)
                    ):
                        mg2 = _merge_guide_why_astrological_layers(
                            p2, foundation, fusion_post, core_profile, locale_value
                        )
                        if _validate_payload_language("guide", mg2, locale_value) and _guide_payload_concrete(
                            locale_value, mg2, ritual_norm=ritual_norm
                        ):
                            fin2 = _guide_apply_final_processing_pass(
                                dict(mg2),
                                day_ctx=day_ctx,
                                foundation=foundation,
                                fusion_post=fusion_post,
                                core_profile=core_profile,
                                ritual_norm=ritual_norm,
                                locale_value=locale_value,
                                tier_norm=tier_norm,
                                day_engine_brief=day_engine_brief,
                                preserve_funnel_core=False,
                            )
                            if (
                                _validate_payload_shape("guide", fin2)
                                and _validate_payload_language("guide", fin2, locale_value)
                                and _guide_payload_concrete(locale_value, fin2, ritual_norm=ritual_norm)
                                and _guide_payload_aligned_with_day_engine_brief(
                                    locale_value, fin2, day_engine_brief
                                )
                            ):
                                payload = mg2
                                input_payload["guide_brief_alignment_retry_used"] = True
        payload = _guide_apply_final_processing_pass(
            dict(payload),
            day_ctx=day_ctx,
            foundation=foundation,
            fusion_post=fusion_post,
            core_profile=core_profile,
            ritual_norm=ritual_norm,
            locale_value=locale_value,
            tier_norm=tier_norm,
            day_engine_brief=day_engine_brief,
            preserve_funnel_core=preserve_funnel_core,
        )
        payload["day_engine_brief"] = day_engine_brief
        dm_out = day_ctx.get("layers", {}).get("day_model") if isinstance(day_ctx.get("layers"), dict) else None
        if isinstance(dm_out, dict):
            payload["day_model"] = dm_out
        gd_out = day_ctx.get("layers", {}).get("guide_decision") if isinstance(day_ctx.get("layers"), dict) else None
        if isinstance(gd_out, dict):
            payload["guide_decision"] = gd_out
        _attach_narrative_hierarchy_to_guide_payload(payload)
        attach_guide_contract_v2(payload, input_payload=input_payload)

    input_payload["orchestration"] = attach_narrative_outcome_to_orchestration(
        input_payload.get("orchestration") or orchestration_meta,
        input_payload=input_payload,
        surface=surface,
        payload=payload if surface == "guide" and isinstance(payload, dict) else None,
        used_fallback=used_fb,
    )
    input_payload["orchestration"] = attach_semantic_quality_to_orchestration(
        input_payload["orchestration"],
        surface=surface,
        locale=locale_value,
        payload=payload if isinstance(payload, dict) else None,
        ritual_norm=ritual_norm if surface == "guide" else None,
    )

    gen = learning.log_generation(
        db,
        module=MODULE,
        surface=surface,
        user_id=user_id,
        core_profile_snapshot_id=snapshot_id,
        prompt_version_id=pv.id,
        model=resolve_default_chat_model()
        if llm_configured and not skip_llm and amll_gate.get("gate_decision") == GATE_DECISION_CALL_LLM
        else None,
        locale=locale_value,
        input_payload=input_payload,
        system_prompt=system_prompt[:2000],
        user_prompt=None,
        normalized_response=payload,
        status="success" if not used_fb else "fallback",
        used_fallback=used_fb,
        duration_ms=int((perf_counter() - started) * 1000),
    )
    return payload, gen.id, used_fb, profile_selector_slim

"""Compatibility endpoints for comparing astrological profiles."""

import copy
import logging
from hashlib import sha1
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Any, List, Literal, Optional
from datetime import date, time

from todayflow_backend.api.auth import get_optional_user, require_user
from todayflow_backend.api.learning_contracts import CompatibilityAttachmentReferenceV0
from todayflow_backend.db.session import get_session
from todayflow_backend.db import models as db_models
from todayflow_backend.db.models import AstroProfile, CachedCompatibility, Subscription, User, utc_naive_now
from todayflow_backend.data.astrology import lookup_sign_metadata
from todayflow_backend.services.chinese_horoscope import get_chinese_horoscope_service
from todayflow_backend.services.zoroastrian_horoscope import get_zoroastrian_horoscope_service
from todayflow_backend.services.tibetan_horoscope import get_tibetan_horoscope_service
from todayflow_backend.services import astro
from todayflow_backend.services.astro import AstroService, get_astro_service
from todayflow_backend.services.synastry import SynastryService, get_synastry_service
from todayflow_backend.services.composite import CompositeChartService, get_composite_chart_service
from todayflow_backend.services.psych_compatibility import PsychCompatibilityService, get_psych_compatibility_service
from todayflow_backend.services.compatibility_engine import (
    CompatibilityEngineService,
    get_compatibility_engine_service,
)
from todayflow_backend.services.business_partnership import BusinessPartnershipService
from todayflow_backend.services.children_charts import ChildrenChartsService
from todayflow_backend.services.group_compatibility import GroupCompatibilityService, get_group_compatibility_service
from todayflow_backend.services.lite_reports import LiteReportService, get_lite_report_service
from todayflow_backend.services.core_profile import CoreProfileService, get_core_profile_service
from todayflow_backend.services.experience_contract_assembler_v0 import (
    assemble_experience_slice,
    slice_log_fields,
)
from todayflow_backend.services.mapping import InternalModelMapper
from todayflow_backend.services.interpretation_orchestrator import (
    InterpretationOrchestrator,
    get_interpretation_orchestrator,
)
from todayflow_backend.services.compatibility_editorial import generate_compatibility_editorial
from todayflow_backend.services.compatibility_name_numbers_v0 import build_name_numbers_pair
from todayflow_backend.services.day_sources.inputs_from_profile import birth_name_from_core_profile
from todayflow_backend.services.sign_compatibility_product import (
    SignCompatibilityProductSurface,
    build_sign_product_surface,
    normalize_relationship_context,
)
from todayflow_backend.services.generation_orchestrator import run_compatibility_dynamics_pipeline
from todayflow_backend.services.compatibility_llm import (
    build_pair_dynamics,
    build_signals,
    generate_llm_base_model,
    resolve_sign_meta_for_date,
)
from todayflow_backend.services.compatibility_funnel_artifact import (
    CompatibilityFunnelArtifact,
    FunnelTodayAlignment,
    build_compatibility_funnel_artifact,
)
from todayflow_backend.services.compatibility_scenario_metrics import apply_scenario_metrics
from todayflow_backend.services.compatibility_encyclopedia import (
    CompatibilityEncyclopediaResponse,
    apply_encyclopedia_to_product_surface,
    build_compatibility_encyclopedia,
    resolve_encyclopedia_selection,
)
from todayflow_backend.services.compatibility_scenario_tone import (
    apply_scenario_tone_to_template_tagline,
    resolve_scenario_format,
)
from todayflow_backend.services.compatibility_learning_context import build_compatibility_learning_context
from todayflow_backend.services.compatibility_access_v0 import (
    apply_paragraph_gate,
    resolve_compat_access_tier,
    shape_product_surface_for_tier,
)
from todayflow_backend.services.compatibility_observability_v0 import log_compat, new_compat_request_id
from todayflow_backend.services.compatibility_attachment_knowledge_v0 import (
    ensure_attachment_lens_hypotheses_v0,
)
from todayflow_backend.services.compatibility_attachment_reference_v0 import (
    apply_attachment_reference_to_surface,
    build_attachment_reference_context,
)
from todayflow_backend.core import models
from todayflow_backend.i18n import localized_sign_name, request_locale, translate

router = APIRouter(prefix="/compatibility", tags=["compatibility"])
logger = logging.getLogger(__name__)
logger = logging.getLogger(__name__)
COMPATIBILITY_CACHE_TTL_HOURS = 24 * 7
DEFAULT_RELATION_MODE = "romantic"
_INTERNAL_MODEL_MAPPER = InternalModelMapper()
# todayflow_astro кладёт асцендент в positions с body="rising"; часть кода ожидала "Ascendant".
_RISING_POSITION_BODIES = frozenset({"Ascendant", "ASC", "rising", "Rising"})

_MODE_DIMENSION_META: dict[str, dict[str, tuple[str, int, str]]] = {
    "business": {
        "attraction": ("Рабочая химия", -6, "Здесь важно, насколько легко вам входить в общий процесс и не мешать друг другу в старте задач."),
        "emotional": ("Эмоциональная зрелость", 2, "Этот слой показывает, насколько вы выдерживаете напряжение без лишней драматизации и личных обид."),
        "communication": ("Коммуникация", 8, "Здесь видно, как вы обсуждаете решения, роли и разногласия в рабочем режиме."),
        "stability": ("Структура и устойчивость", 8, "Этот слой показывает, насколько связка выдерживает рутину, ответственность и повторяющиеся рабочие циклы."),
        "long_term": ("Потенциал партнёрства", 4, "Здесь читается, может ли эта связка расти дольше одного проекта или короткого импульса."),
    },
    "family": {
        "attraction": ("Тепло и привязанность", -8, "Этот слой показывает, насколько в семье сохраняются тепло, принятие и желание оставаться в контакте."),
        "emotional": ("Эмоциональная близость", 8, "Здесь видно, насколько легко быть рядом в чувствах, не уходя в молчание или защиту."),
        "communication": ("Семейный диалог", 5, "Этот слой показывает, как вы слышите друг друга в бытовых и эмоциональных разговорах."),
        "stability": ("Опора и границы", 8, "Здесь читается, насколько связь выдерживает рутину, обязанности и старые семейные роли."),
        "long_term": ("Долгий семейный сценарий", 4, "Этот слой показывает, помогает ли связь расти через время или уходит в повторяющийся круг."),
    },
    "parent_child": {
        "attraction": ("Контакт и отклик", -10, "Здесь видно, насколько легко в этой связи возникает тёплый отклик и желание идти навстречу друг другу."),
        "emotional": ("Чувствительность", 10, "Этот слой показывает, насколько бережно связь выдерживает чувства, перегруз и уязвимость."),
        "communication": ("Как вы слышите друг друга", 5, "Здесь читается, насколько легко объяснять, просить и быть услышанными без давления."),
        "stability": ("Безопасность и ритм", 10, "Этот слой показывает, насколько в связи есть понятный ритм, опора и ощущение безопасности."),
        "long_term": ("Рост через время", 4, "Здесь видно, помогает ли связь развиваться через возраст и этапы, а не только удерживать порядок."),
    },
}


def _life_path_from_personal_model(
    db: Session,
    *,
    user_id: int,
    astro_profile: AstroProfile,
    core_profile: dict[str, Any] | None = None,
) -> int | None:
    """Read life_path via Experience Contract (primary) or numerology store — not a private formula."""
    if (
        core_profile
        and isinstance(core_profile, dict)
        and astro_profile.is_primary
    ):
        slice_lp = assemble_experience_slice(
            core_profile, experience_id="compatibility"
        ).get("life_path")
        if isinstance(slice_lp, int):
            return slice_lp
        if isinstance(slice_lp, dict):
            for key in ("reduced_value", "value", "number"):
                if isinstance(slice_lp.get(key), int):
                    return int(slice_lp[key])
        try:
            if slice_lp is not None and str(slice_lp).strip().isdigit():
                return int(str(slice_lp).strip())
        except (TypeError, ValueError):
            pass

    row = (
        db.query(db_models.NumerologyProfileRecord)
        .filter(
            db_models.NumerologyProfileRecord.user_id == user_id,
            db_models.NumerologyProfileRecord.birth_date == astro_profile.birth_date,
        )
        .order_by(db_models.NumerologyProfileRecord.created_at.desc())
        .first()
    )
    if row is not None and isinstance(row.data, dict):
        life = row.data.get("life_path")
        if isinstance(life, int):
            return life
        if isinstance(life, dict):
            for key in ("reduced_value", "value", "number"):
                if isinstance(life.get(key), int):
                    return int(life[key])
    return None


def _compat_personalized_from_experience_slice(
    core_profile: dict[str, Any],
    *,
    consistency: dict[str, Any],
    to_display: str,
    static_payload: dict[str, Any],
    el_rel: Any,
    rh_rel: Any,
    locale: str,
) -> dict[str, Any]:
    """Compatibility personalization reads personality only via ExperienceSlice."""
    experience_slice = assemble_experience_slice(core_profile, experience_id="compatibility")
    user_sun = experience_slice.get("sun_sign")
    personal_focus = _compatibility_personal_focus_phrase(
        consistency.get("focus"), locale=locale
    )
    decision = experience_slice.get("decision_style")
    if isinstance(decision, str) and decision.strip() and not personal_focus:
        personal_focus = decision.strip()[:160]
    out: dict[str, Any] = {
        # Snapshot-gated readiness — shell without snapshot is not "profile ready".
        "profile_ready": bool(experience_slice.get("generated_from_snapshot")),
        "profile_hash": experience_slice.get("profile_hash"),
        "headline": translate("compat.personalized.headline", locale=locale).format(
            focus=personal_focus
        ),
        "hint": _compatibility_personal_hint(user_sun, to_display, locale=locale),
        "focus": personal_focus,
        "do_focus": _compatibility_clean_personal_line(
            consistency.get("do_focus"),
            fallback=_quick_sign_strongest_text(
                static_payload["score"], el_rel, locale=locale
            ),
            locale=locale,
        ),
        "avoid_focus": _compatibility_clean_personal_line(
            consistency.get("avoid_focus"),
            fallback=_quick_sign_friction_text(
                static_payload["score"], rh_rel, locale=locale
            ),
            locale=locale,
        ),
        "decision_style": experience_slice.get("decision_style"),
        "conflict_style": experience_slice.get("conflict_style"),
        "communication_style": experience_slice.get("communication_style"),
        "motivation": experience_slice.get("motivation"),
        "energy_source": experience_slice.get("energy_source"),
        "life_path": experience_slice.get("life_path"),
        **slice_log_fields(experience_slice),
    }
    return out


class CompatibilityRequest(BaseModel):
    profile_id_1: int
    profile_id_2: int
    relation_mode: str | None = None
    format_id: str | None = Field(
        None,
        description="Scenario format id (series/topic), e.g. office, after_wine",
    )


class ScenarioMetricsContext(BaseModel):
    format_id: str
    display_score: int
    subscores: dict[str, int]
    tone_mode: str | None = None
    deep_block_order: list[str] | None = None
    attachment_reference: CompatibilityAttachmentReferenceV0 | None = None


class GroupCompatibilityRequest(BaseModel):
    profile_ids: List[int]  # 3+ profile IDs


class CompatibilityResponse(BaseModel):
    profile_1: dict
    profile_2: dict
    compatibility: dict  # Результаты совместимости
    funnel_artifact: Optional[CompatibilityFunnelArtifact] = None
    scenario_context: ScenarioMetricsContext | None = None


class SignCompatibilityResponse(BaseModel):
    from_sign: str
    to_sign: str
    from_sign_name: str
    to_sign_name: str
    from_gender: Optional[str] = None
    to_gender: Optional[str] = None
    score: int
    summary: str
    quick_reading: dict
    free_paragraphs: list[str]
    full_paragraphs: list[str]
    is_paid: bool
    content_id: str
    personalized: Optional[dict] = None
    relationship_context: Optional[str] = None
    product_surface: SignCompatibilityProductSurface
    generation_source: Optional[str] = None
    pair_dynamics: Optional[dict] = None
    content_locale: str = "ru"
    funnel_artifact: Optional[CompatibilityFunnelArtifact] = None
    attachment_reference: CompatibilityAttachmentReferenceV0 | None = None
    access_disclosure: Optional[dict] = None
    generation_lifecycle: Optional[dict] = None
    # Soft Day Source echo — Expression/Soul/Personality; not a score gate.
    name_numbers_pair: Optional[dict] = None


class CompatibilityDynamicsRequest(BaseModel):
    mode: Literal["quick", "precise"] = "quick"
    from_sign: Optional[str] = None
    to_sign: Optional[str] = None
    relationship_context: Optional[str] = None
    # template = baseline only; llm = baseline + async enrichment (never blocks read path)
    generation: Literal["template", "llm"] = "llm"
    name_1: Optional[str] = None
    name_2: Optional[str] = None
    birth_date_1: Optional[date] = None
    birth_date_2: Optional[date] = None
    block_feedback: Optional[dict[str, str]] = None
    include_personalized: bool = True
    locale: Optional[str] = Field(
        None,
        description="Preferred UI locale: en | ru (overrides Accept-Language when set)",
    )
    topic_id: Optional[str] = Field(None, description="Encyclopedia category id, e.g. love, conflicts")
    reading_id: Optional[str] = Field(None, description="Popular reading id, e.g. opposites")
    series_id: Optional[str] = Field(None, description="Series id, e.g. living_together")
    format_id: Optional[str] = Field(
        None,
        description="Explicit scenario format id (overrides topic/reading/series resolution), e.g. after_wine",
    )


@router.get("/encyclopedia", response_model=CompatibilityEncyclopediaResponse)
def compatibility_encyclopedia(
    http_request: Request,
    locale: Optional[str] = Query(None, description="Preferred UI locale: en | ru"),
) -> CompatibilityEncyclopediaResponse:
    """Browse catalog: categories, popular readings, series with narrative intros."""
    effective_locale = request_locale(http_request, preferred=locale)
    return build_compatibility_encyclopedia(effective_locale)


@router.get("/signs", response_model=SignCompatibilityResponse)
def signs_compatibility(
    http_request: Request,
    from_sign: str = Query(..., alias="from"),
    to_sign: str = Query(..., alias="to"),
    from_gender: Optional[str] = Query(None),
    to_gender: Optional[str] = Query(None),
    relationship_context: Optional[str] = Query(
        None,
        description=(
            "Контекст связи: just_met | mutual_attraction | in_relationship | unclear | "
            "conflict_distance | split_but_pull"
        ),
    ),
    locale: Optional[str] = Query(
        None,
        description="Preferred UI locale: en | ru (overrides Accept-Language when set)",
    ),
    include_personalized: bool = Query(True),
    user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_session),
    core_profile_service: CoreProfileService = Depends(get_core_profile_service),
    orchestrator: InterpretationOrchestrator = Depends(get_interpretation_orchestrator),
) -> SignCompatibilityResponse:
    effective_locale = request_locale(http_request, preferred=locale)
    from_meta = lookup_sign_metadata(from_sign)
    to_meta = lookup_sign_metadata(to_sign)
    if not from_meta or not to_meta:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "invalid_sign_pair",
                "message": "Не удалось распознать пару знаков. Выберите оба знака из списка.",
            },
        )

    from_display = localized_sign_name(from_meta["id"], locale=effective_locale)
    to_display = localized_sign_name(to_meta["id"], locale=effective_locale)

    static_payload = _build_static_sign_report(
        from_sign=from_meta["id"],
        to_sign=to_meta["id"],
        from_name=from_display,
        to_name=to_display,
        from_element=from_meta.get("element", ""),
        to_element=to_meta.get("element", ""),
        from_modality=from_meta.get("modality", ""),
        to_modality=to_meta.get("modality", ""),
        locale=effective_locale,
    )
    ctx_norm = normalize_relationship_context(relationship_context)
    qr = static_payload["quick_reading"]
    el_rel = _localized_element_relation(from_meta.get("element", ""), to_meta.get("element", ""), locale=effective_locale)
    rh_rel = _localized_rhythm_relation(from_meta.get("modality", ""), to_meta.get("modality", ""), locale=effective_locale)
    product_surface = build_sign_product_surface(
        from_sign=from_meta["id"],
        to_sign=to_meta["id"],
        from_name=from_display,
        to_name=to_display,
        from_element=from_meta.get("element", ""),
        to_element=to_meta.get("element", ""),
        from_modality=from_meta.get("modality", ""),
        to_modality=to_meta.get("modality", ""),
        score=static_payload["score"],
        relationship_context=ctx_norm,
        element_relation=el_rel,
        rhythm_relation=rh_rel,
        strongest=str(qr.get("strongest") or ""),
        friction=str(qr.get("friction") or ""),
        locale=effective_locale,
    )
    paid = _is_paid_user(user, db)
    personalized = None
    access_tier_signs = resolve_compat_access_tier(user, db)
    name_numbers_pair = None
    profile_name_a: str | None = None

    if include_personalized and user is not None and access_tier_signs != "guest":
        try:
            core_profile = core_profile_service.build_cached_or_baseline(db, user)
            profile_name_a = birth_name_from_core_profile(
                core_profile if isinstance(core_profile, dict) else None
            )
            consistency = orchestrator.build_daily_guidance(
                core_profile=core_profile,
                numerology=None,
                needs="love",
            )
            personalized = _compat_personalized_from_experience_slice(
                core_profile if isinstance(core_profile, dict) else {},
                consistency=consistency.model_dump()
                if hasattr(consistency, "model_dump")
                else (consistency if isinstance(consistency, dict) else {}),
                to_display=to_display,
                static_payload=static_payload,
                el_rel=el_rel,
                rh_rel=rh_rel,
                locale=effective_locale,
            )
        except Exception:
            personalized = None

    name_numbers_pair = build_name_numbers_pair(
        name_a=profile_name_a,
        name_b=None,
        label_a=translate("compat.label.you", locale=effective_locale),
        label_b=translate("compat.label.partner", locale=effective_locale),
    )

    pair_dyn_for_funnel = build_pair_dynamics(
        user1_label=translate("compat.label.you", locale=effective_locale),
        user2_label=translate("compat.label.partner", locale=effective_locale),
        from_modality=from_meta.get("modality", ""),
        to_modality=to_meta.get("modality", ""),
        from_element=from_meta.get("element", ""),
        to_element=to_meta.get("element", ""),
        locale=effective_locale,
    )
    today_al = _funnel_today_alignment_from_personalized(personalized, locale=effective_locale)
    funnel_artifact = build_compatibility_funnel_artifact(
        mode="quick",
        relationship_context=ctx_norm,
        overall_score=static_payload["score"],
        subscores=product_surface.subscores.model_dump(),
        pair_dynamics=pair_dyn_for_funnel,
        user1_label=translate("compat.label.you", locale=effective_locale),
        user2_label=translate("compat.label.partner", locale=effective_locale),
        from_element=str(from_meta.get("element", "") or ""),
        to_element=str(to_meta.get("element", "") or ""),
        from_modality=str(from_meta.get("modality", "") or ""),
        to_modality=str(to_meta.get("modality", "") or ""),
        locale=effective_locale,
        today_alignment=today_al,
        llm_base_model=None,
    )

    product_surface, access_disclosure = shape_product_surface_for_tier(
        product_surface,
        tier=access_tier_signs,
        overall_score=static_payload["score"],
        locale=effective_locale,
    )
    from todayflow_backend.services.compatibility_content_v1.apply_guest_v1 import (
        maybe_replace_guest_surface,
    )

    product_surface, _content_v1, access_disclosure = maybe_replace_guest_surface(
        product_surface,
        tier=access_tier_signs,
        from_sign=from_meta["id"],
        to_sign=to_meta["id"],
        relationship_context=ctx_norm,
        locale=effective_locale,
        score=int(static_payload["score"]),
        has_birth_dates=False,
        access_disclosure=access_disclosure,
    )
    free_paragraphs, full_paragraphs = apply_paragraph_gate(
        list(static_payload["paragraphs"] or []),
        tier=access_tier_signs,
    )
    if access_tier_signs == "guest":
        personalized = None
        funnel_artifact = None

    return SignCompatibilityResponse(
        from_sign=from_meta["id"],
        to_sign=to_meta["id"],
        from_sign_name=from_display,
        to_sign_name=to_display,
        from_gender=from_gender,
        to_gender=to_gender,
        score=static_payload["score"],
        summary=static_payload["summary"],
        quick_reading=static_payload["quick_reading"],
        free_paragraphs=free_paragraphs,
        full_paragraphs=full_paragraphs,
        is_paid=paid or access_tier_signs == "paid",
        content_id=static_payload["content_id"],
        personalized=personalized,
        relationship_context=ctx_norm if relationship_context else None,
        product_surface=product_surface,
        generation_source="template",
        access_disclosure=access_disclosure,
        pair_dynamics=pair_dyn_for_funnel,
        content_locale=effective_locale,
        funnel_artifact=funnel_artifact,
        name_numbers_pair=name_numbers_pair,
    )


@router.post("/dynamics", response_model=SignCompatibilityResponse)
def compatibility_dynamics(
    http_request: Request,
    body: CompatibilityDynamicsRequest,
    user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_session),
    core_profile_service: CoreProfileService = Depends(get_core_profile_service),
    orchestrator: InterpretationOrchestrator = Depends(get_interpretation_orchestrator),
) -> SignCompatibilityResponse:
    """Разбор динамики пары: быстрый (знаки) или точный (даты рождения), опционально LLM-текст."""
    request_id = new_compat_request_id()
    access_tier = resolve_compat_access_tier(user, db)
    log_compat(
        "request",
        request_id=request_id,
        mode=body.mode,
        generation=body.generation,
        tier=access_tier,
        user_id=user.id if user is not None else None,
        from_sign=body.from_sign,
        to_sign=body.to_sign,
        has_dates=bool(body.birth_date_1 and body.birth_date_2),
    )

    if body.mode == "precise":
        if body.birth_date_1 is None or body.birth_date_2 is None:
            raise HTTPException(
                status_code=422,
                detail={
                    "code": "birth_dates_required",
                    "message": "Добавьте обе даты рождения, чтобы построить совместимость.",
                },
            )
        r1 = resolve_sign_meta_for_date(body.birth_date_1)
        r2 = resolve_sign_meta_for_date(body.birth_date_2)
        if not r1 or not r2:
            raise HTTPException(
                status_code=422,
                detail={
                    "code": "invalid_birth_dates",
                    "message": "Проверьте даты рождения — по ним не удалось определить знаки.",
                },
            )
        from_meta = lookup_sign_metadata(str(r1.get("id", "")))
        to_meta = lookup_sign_metadata(str(r2.get("id", "")))
    else:
        if not body.from_sign or not body.to_sign:
            raise HTTPException(
                status_code=422,
                detail={
                    "code": "signs_required",
                    "message": "Добавьте второй знак, чтобы построить совместимость.",
                },
            )
        from_meta = lookup_sign_metadata(body.from_sign)
        to_meta = lookup_sign_metadata(body.to_sign)

    if not from_meta or not to_meta:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "invalid_sign_pair",
                "message": "Не удалось распознать пару знаков. Выберите оба знака из списка.",
            },
        )

    effective_locale = request_locale(http_request, preferred=body.locale)
    loc = effective_locale
    from_display = localized_sign_name(from_meta["id"], locale=effective_locale)
    to_display = localized_sign_name(to_meta["id"], locale=effective_locale)

    user1_label = (body.name_1 or "").strip() or translate("compat.label.you", locale=loc)
    user2_label = (body.name_2 or "").strip() or translate("compat.label.partner", locale=loc)

    static_payload = _build_static_sign_report(
        from_sign=from_meta["id"],
        to_sign=to_meta["id"],
        from_name=from_display,
        to_name=to_display,
        from_element=from_meta.get("element", ""),
        to_element=to_meta.get("element", ""),
        from_modality=from_meta.get("modality", ""),
        to_modality=to_meta.get("modality", ""),
        locale=effective_locale,
    )
    ctx_norm = normalize_relationship_context(body.relationship_context)
    encyclopedia_selection = resolve_encyclopedia_selection(
        topic_id=body.topic_id,
        reading_id=body.reading_id,
        series_id=body.series_id,
        locale=effective_locale,
    )
    scenario_tone = resolve_scenario_format(
        topic_id=body.topic_id,
        reading_id=body.reading_id,
        series_id=body.series_id,
        format_id=body.format_id or (encyclopedia_selection or {}).get("format_id"),
    )
    scenario_context = (encyclopedia_selection or {}).get("scenario_context")
    if encyclopedia_selection and not body.relationship_context and encyclopedia_selection.get("relationship_context"):
        ctx_norm = normalize_relationship_context(str(encyclopedia_selection["relationship_context"]))
    qr = static_payload["quick_reading"]
    el_rel = _localized_element_relation(from_meta.get("element", ""), to_meta.get("element", ""), locale=effective_locale)
    rh_rel = _localized_rhythm_relation(from_meta.get("modality", ""), to_meta.get("modality", ""), locale=effective_locale)
    template_surface = build_sign_product_surface(
        from_sign=from_meta["id"],
        to_sign=to_meta["id"],
        from_name=from_display,
        to_name=to_display,
        from_element=from_meta.get("element", ""),
        to_element=to_meta.get("element", ""),
        from_modality=from_meta.get("modality", ""),
        to_modality=to_meta.get("modality", ""),
        score=static_payload["score"],
        relationship_context=ctx_norm,
        element_relation=el_rel,
        rhythm_relation=rh_rel,
        strongest=str(qr.get("strongest") or ""),
        friction=str(qr.get("friction") or ""),
        locale=effective_locale,
    )
    pair_dyn = build_pair_dynamics(
        user1_label=user1_label,
        user2_label=user2_label,
        from_modality=from_meta.get("modality", ""),
        to_modality=to_meta.get("modality", ""),
        from_element=from_meta.get("element", ""),
        to_element=to_meta.get("element", ""),
        locale=effective_locale,
    )
    signals = build_signals(
        subscores=template_surface.subscores.model_dump(),
        score=static_payload["score"],
    )
    fb_clean: dict[str, str] = {}
    allow_fb = {"emotions", "communication", "conflicts", "sexuality", "long_term"}
    if body.block_feedback:
        for key, val in body.block_feedback.items():
            if key in allow_fb and val in {"yes", "partial", "no"}:
                fb_clean[key] = val

    compat_learning = None
    if user is not None:
        compat_learning = build_compatibility_learning_context(db, user_id=user.id)
        if compat_learning and not fb_clean:
            recent = compat_learning.get("recent_block_feedback") or {}
            if isinstance(recent, dict):
                for key, val in recent.items():
                    if key in allow_fb and val in {"yes", "partial", "no"}:
                        fb_clean[key] = str(val)

    paid = _is_paid_user(user, db)
    personalized = None
    profile_name_a: str | None = None
    # build_daily_guidance is deterministic. Never call core_profile.build() here — it can
    # trigger portrait LLM (~12–25s) and make Compatibility look crashed.
    if body.include_personalized and user is not None and access_tier != "guest":
        try:
            core_profile = core_profile_service.build_cached_or_baseline(db, user)
            profile_name_a = birth_name_from_core_profile(
                core_profile if isinstance(core_profile, dict) else None
            )
            consistency = orchestrator.build_daily_guidance(
                core_profile=core_profile,
                numerology=None,
                needs="love",
            )
            personalized = _compat_personalized_from_experience_slice(
                core_profile if isinstance(core_profile, dict) else {},
                consistency=consistency.model_dump()
                if hasattr(consistency, "model_dump")
                else (consistency if isinstance(consistency, dict) else {}),
                to_display=to_display,
                static_payload=static_payload,
                el_rel=el_rel,
                rh_rel=rh_rel,
                locale=effective_locale,
            )
        except Exception as exc:
            log_compat(
                "generation",
                request_id=request_id,
                layer="personalized",
                error=str(exc)[:300],
                tier=access_tier,
            )
            personalized = None

    name_a = (body.name_1 or "").strip() or profile_name_a
    name_b = (body.name_2 or "").strip() or None
    name_numbers_pair = build_name_numbers_pair(
        name_a=name_a,
        name_b=name_b,
        label_a=(body.name_1 or "").strip()
        or translate("compat.label.you", locale=effective_locale),
        label_b=(body.name_2 or "").strip()
        or translate("compat.label.partner", locale=effective_locale),
    )

    td = (str(personalized.get("do_focus", "")).strip() if personalized else "") or None
    ta = (str(personalized.get("avoid_focus", "")).strip() if personalized else "") or None
    tf = (str(personalized.get("focus", "")).strip() if personalized else "") or None

    # C1: read path is always deterministic baseline. LLM runs only as a background job.
    from todayflow_backend.services.generation_jobs_v0 import (
        enqueue_or_reuse,
        job_to_public,
        lifecycle_payload,
        make_fingerprint,
        schedule_job_runner,
    )

    base_llm = None
    product_surface = template_surface
    product_surface.score_tagline = apply_scenario_tone_to_template_tagline(
        product_surface.score_tagline, scenario_tone, locale=effective_locale
    )
    gen_src = "template"
    generation_lifecycle = lifecycle_payload(
        status="baseline_ready",
        source="template",
        is_fully_personal=False,
    )

    want_enrich = (
        body.generation == "llm"
        and access_tier in ("registered", "paid")
        and scenario_tone.tone_mode != "playful"
    )
    if body.generation == "llm" and access_tier == "guest":
        log_compat("generation", request_id=request_id, skipped="guest_teaser_no_llm", tier=access_tier)

    if want_enrich:
        fingerprint = make_fingerprint(
            "compat_dyn",
            body.mode,
            from_meta["id"],
            to_meta["id"],
            ctx_norm,
            effective_locale,
            scenario_tone.format_id,
            body.topic_id,
            body.reading_id,
            body.series_id,
            access_tier,
        )
        idem = f"compatibility:{from_meta['id']}:{to_meta['id']}:{access_tier}:{fingerprint}"
        job_req = {
            "mode": body.mode,
            "from_sign": from_meta["id"],
            "to_sign": to_meta["id"],
            "relationship_context": ctx_norm,
            "locale": effective_locale,
            "name_1": body.name_1,
            "name_2": body.name_2,
            "block_feedback": fb_clean or None,
            "topic_id": body.topic_id,
            "reading_id": body.reading_id,
            "series_id": body.series_id,
            "format_id": body.format_id,
            "today_do": td,
            "today_avoid": ta,
            "today_focus": tf,
            # For content_v1 source_depth / honesty (enrichment worker).
            "birth_date_1": body.birth_date_1.isoformat() if body.birth_date_1 else None,
            "birth_date_2": body.birth_date_2.isoformat() if body.birth_date_2 else None,
        }
        job, _created = enqueue_or_reuse(
            db,
            idempotency_key=idem,
            fingerprint=fingerprint,
            module="compatibility",
            surface="dynamics_registered",
            user_id=user.id if user is not None else None,
            request_payload=job_req,
            baseline_payload={
                "score": static_payload["score"],
                "from_sign": from_meta["id"],
                "to_sign": to_meta["id"],
            },
        )
        if job.status == "enriched" and isinstance(job.result_payload, dict):
            generation_lifecycle = job_to_public(job)
            gen_src = "llm"
            # Prefer cached enriched surface; still apply encyclopedia below on a copy.
            try:
                cached_ps = job.result_payload.get("product_surface")
                if isinstance(cached_ps, dict):
                    product_surface = SignCompatibilityProductSurface.model_validate(cached_ps)
            except Exception:
                gen_src = "template"
                generation_lifecycle = lifecycle_payload(
                    status="baseline_ready",
                    job_id=job.id,
                    fingerprint=fingerprint,
                    source="template",
                    is_fully_personal=False,
                )
        else:
            generation_lifecycle = {
                **job_to_public(job),
                "status": "enrichment_pending"
                if job.status != "enrichment_failed"
                else "enrichment_failed",
            }
            if job.status != "enrichment_failed":
                from todayflow_backend.services.compatibility_enrichment_v0 import (
                    run_compatibility_enrichment_job,
                )

                schedule_job_runner(job.id, run_compatibility_enrichment_job)
            log_compat(
                "generation",
                request_id=request_id,
                queued_job_id=job.id,
                status=generation_lifecycle.get("status"),
                tier=access_tier,
            )

    apply_encyclopedia_to_product_surface(product_surface, encyclopedia_selection)

    scenario_subscores, scenario_score = apply_scenario_metrics(
        scenario_tone.format_id,
        product_surface.subscores.model_dump(),
        static_payload["score"],
        from_sign=from_meta["id"],
        to_sign=to_meta["id"],
        from_element=str(from_meta.get("element", "") or ""),
        to_element=str(to_meta.get("element", "") or ""),
        from_modality=str(from_meta.get("modality", "") or ""),
        to_modality=str(to_meta.get("modality", "") or ""),
    )
    product_surface.subscores = scenario_subscores
    display_score = scenario_score

    attachment_reference = None
    if scenario_tone.tone_mode == "playful":
        from todayflow_backend.services.compatibility_playful_surface import apply_playful_surface_contract

        apply_playful_surface_contract(product_surface, scenario_tone, locale=effective_locale)
    else:
        attachment_reference = apply_attachment_reference_to_surface(
            product_surface,
            fb_clean or None,
            locale=effective_locale,
        )
        if attachment_reference and compat_learning is not None:
            compat_learning = dict(compat_learning)
            compat_learning["attachment_reference"] = attachment_reference
    if encyclopedia_selection:
        pair_dyn = dict(pair_dyn or {})
        pair_dyn["encyclopedia_selection"] = {
            k: encyclopedia_selection.get(k)
            for k in (
                "selection_id",
                "selection_kind",
                "selection_label",
                "format_id",
                "tone_family",
                "tone_mode",
            )
            if encyclopedia_selection.get(k)
        }

    today_al = _funnel_today_alignment_from_personalized(personalized, locale=effective_locale)
    funnel_artifact = None
    if scenario_tone.tone_mode != "playful":
        funnel_artifact = build_compatibility_funnel_artifact(
            mode=body.mode,
            relationship_context=ctx_norm,
            overall_score=display_score,
            subscores=product_surface.subscores.model_dump(),
            pair_dynamics=pair_dyn,
            user1_label=user1_label,
            user2_label=user2_label,
            from_element=str(from_meta.get("element", "") or ""),
            to_element=str(to_meta.get("element", "") or ""),
            from_modality=str(from_meta.get("modality", "") or ""),
            to_modality=str(to_meta.get("modality", "") or ""),
            locale=effective_locale,
            today_alignment=today_al,
            llm_base_model=base_llm,
            format_id=scenario_tone.format_id,
        )

    _ensure_attachment_lens_for_user(db, user, attachment_reference)

    product_surface, access_disclosure = shape_product_surface_for_tier(
        product_surface,
        tier=access_tier,
        overall_score=display_score,
        locale=effective_locale,
    )
    from todayflow_backend.services.compatibility_content_v1.apply_guest_v1 import (
        maybe_replace_guest_surface,
    )

    product_surface, _content_v1, access_disclosure = maybe_replace_guest_surface(
        product_surface,
        tier=access_tier,
        from_sign=from_meta["id"],
        to_sign=to_meta["id"],
        relationship_context=ctx_norm,
        locale=effective_locale,
        score=int(display_score),
        has_birth_dates=(body.mode or "").strip().lower() == "precise",
        access_disclosure=access_disclosure,
    )
    free_paragraphs, full_paragraphs = apply_paragraph_gate(
        list(static_payload["paragraphs"] or []),
        tier=access_tier,
    )
    # Guests never get personalized Today-alignment copy.
    if access_tier == "guest":
        personalized = None
        funnel_artifact = None

    log_compat(
        "response",
        request_id=request_id,
        tier=access_tier,
        source=gen_src,
        score=display_score,
        blocks=len(product_surface.blocks),
        locale=effective_locale,
        lifecycle=generation_lifecycle.get("status"),
        job_id=generation_lifecycle.get("job_id"),
    )

    return SignCompatibilityResponse(
        from_sign=from_meta["id"],
        to_sign=to_meta["id"],
        from_sign_name=from_display,
        to_sign_name=to_display,
        from_gender=None,
        to_gender=None,
        score=display_score,
        summary=static_payload["summary"],
        quick_reading=static_payload["quick_reading"],
        free_paragraphs=free_paragraphs,
        full_paragraphs=full_paragraphs,
        is_paid=paid or access_tier == "paid",
        content_id=static_payload["content_id"],
        personalized=personalized,
        relationship_context=ctx_norm if body.relationship_context else None,
        product_surface=product_surface,
        generation_source=gen_src,
        pair_dynamics=pair_dyn,
        content_locale=effective_locale,
        funnel_artifact=funnel_artifact,
        attachment_reference=attachment_reference,
        access_disclosure=access_disclosure,
        generation_lifecycle=generation_lifecycle,
        name_numbers_pair=name_numbers_pair,
    )


class CompatibilityJobResponse(BaseModel):
    job: dict
    product_surface: Optional[SignCompatibilityProductSurface] = None
    generation_source: Optional[str] = None
    score: Optional[int] = None
    summary: Optional[str] = None
    access_disclosure: Optional[dict] = None


@router.get("/dynamics/jobs/{job_id}", response_model=CompatibilityJobResponse)
def get_compatibility_dynamics_job(
    job_id: int,
    user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_session),
) -> CompatibilityJobResponse:
    from todayflow_backend.db.models import GenerationJob
    from todayflow_backend.services.generation_jobs_v0 import job_to_public

    job = db.query(GenerationJob).filter(GenerationJob.id == job_id).first()
    if job is None or job.module != "compatibility":
        raise HTTPException(status_code=404, detail="job_not_found")
    if job.user_id is not None and (user is None or user.id != job.user_id):
        raise HTTPException(status_code=403, detail="job_forbidden")
    public = job_to_public(job)
    surface = None
    score = None
    summary = None
    disclosure = None
    gen_src = None
    if job.status == "enriched" and isinstance(job.result_payload, dict):
        try:
            ps = job.result_payload.get("product_surface")
            if isinstance(ps, dict):
                surface = SignCompatibilityProductSurface.model_validate(ps)
            score = job.result_payload.get("score")
            summary = job.result_payload.get("summary")
            disclosure = job.result_payload.get("access_disclosure")
            gen_src = job.result_payload.get("generation_source") or "llm"
        except Exception:
            surface = None
    return CompatibilityJobResponse(
        job=public,
        product_surface=surface,
        generation_source=gen_src,
        score=score,
        summary=summary,
        access_disclosure=disclosure,
    )


@router.post("/dynamics/jobs/{job_id}/retry", response_model=CompatibilityJobResponse)
def retry_compatibility_dynamics_job(
    job_id: int,
    user: User = Depends(require_user),
    db: Session = Depends(get_session),
) -> CompatibilityJobResponse:
    from todayflow_backend.db.models import GenerationJob
    from todayflow_backend.services.compatibility_enrichment_v0 import run_compatibility_enrichment_job
    from todayflow_backend.services.generation_jobs_v0 import job_to_public, schedule_job_runner

    job = db.query(GenerationJob).filter(GenerationJob.id == job_id).first()
    if job is None or job.module != "compatibility":
        raise HTTPException(status_code=404, detail="job_not_found")
    if job.user_id != user.id:
        raise HTTPException(status_code=403, detail="job_forbidden")
    if job.status not in ("enrichment_failed", "stale", "enrichment_pending"):
        raise HTTPException(status_code=409, detail="job_not_retryable")
    job.status = "enrichment_pending"
    job.error_message = None
    job.locked_at = None
    job.attempt_count = 0
    job.updated_at = utc_naive_now()
    db.add(job)
    db.commit()
    db.refresh(job)
    schedule_job_runner(job.id, run_compatibility_enrichment_job)
    return CompatibilityJobResponse(job=job_to_public(job))


class CompatibilityPremiumRequest(BaseModel):
    from_sign: str
    to_sign: str
    relationship_context: Optional[str] = None
    locale: Optional[str] = None
    question: Optional[str] = None


@router.post("/dynamics/premium", response_model=CompatibilityJobResponse)
def enqueue_compatibility_premium(
    http_request: Request,
    body: CompatibilityPremiumRequest,
    user: User = Depends(require_user),
    db: Session = Depends(get_session),
) -> CompatibilityJobResponse:
    """Paid-only: enqueue premium guidance pack on explicit user request (never pre-generated)."""
    from todayflow_backend.services.generation_jobs_v0 import (
        enqueue_or_reuse,
        job_to_public,
        make_fingerprint,
        schedule_job_runner,
    )

    tier = resolve_compat_access_tier(user, db)
    if tier != "paid":
        raise HTTPException(
            status_code=402,
            detail={
                "code": "premium_required",
                "message": "Премиум-разбор доступен по подписке и только по запросу.",
            },
        )
    from_meta = lookup_sign_metadata(body.from_sign)
    to_meta = lookup_sign_metadata(body.to_sign)
    if not from_meta or not to_meta:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "invalid_sign_pair",
                "message": "Не удалось распознать пару знаков.",
            },
        )
    locale = request_locale(http_request, preferred=body.locale)
    ctx = normalize_relationship_context(body.relationship_context)
    fingerprint = make_fingerprint(
        "compat_premium",
        from_meta["id"],
        to_meta["id"],
        ctx,
        locale,
        (body.question or "").strip()[:200],
    )
    idem = f"compatibility_premium:{user.id}:{from_meta['id']}:{to_meta['id']}:{fingerprint}"
    job, _ = enqueue_or_reuse(
        db,
        idempotency_key=idem,
        fingerprint=fingerprint,
        module="compatibility",
        surface="premium_guidance",
        user_id=user.id,
        request_payload={
            "from_sign": from_meta["id"],
            "to_sign": to_meta["id"],
            "relationship_context": ctx,
            "locale": locale,
            "question": (body.question or "").strip() or None,
            "kind": "premium_guidance",
        },
    )
    if job.status != "enriched":
        from todayflow_backend.services.compatibility_premium_enrichment_v0 import (
            run_compatibility_premium_job,
        )

        schedule_job_runner(job.id, run_compatibility_premium_job)
    return CompatibilityJobResponse(job=job_to_public(job))


def _funnel_today_alignment_from_personalized(
    personalized: dict | None,
    *,
    locale: str,
) -> FunnelTodayAlignment | None:
    if not personalized:
        return None
    do = str(personalized.get("do_focus") or "").strip()
    avoid = str(personalized.get("avoid_focus") or "").strip()
    focus = str(personalized.get("focus") or "").strip()
    if not do and not avoid and not focus:
        return None
    loc = (locale or "ru").strip().split("-")[0].lower()
    if loc not in ("en", "ru"):
        loc = "en"
    return FunnelTodayAlignment(
        focus_label=focus,
        do_echo=do,
        avoid_echo=avoid,
        sync_note=translate("compat.funnel.today_layer.sync_note", locale=loc),
    )


def _ensure_attachment_lens_for_user(
    db: Session,
    user: User | None,
    attachment_reference: dict | None,
) -> None:
    if user is None or not attachment_reference:
        return
    try:
        ensure_attachment_lens_hypotheses_v0(
            db,
            user_id=user.id,
            attachment_reference=attachment_reference,
            commit=True,
        )
    except Exception:
        logger.exception("attachment lens ensure failed user=%s", user.id)


def _relation_mode_to_funnel_context(relation_mode: str | None) -> str | None:
    m = (relation_mode or "").strip().lower()
    if m == "romantic":
        return "in_relationship"
    return None


_RELATION_MODE_DEFAULT_FORMAT: dict[str, str] = {
    "business": "office",
    "parent_child": "parenting",
    "family": "living_together",
}


def _resolve_pair_format_id(relation_mode: str | None, format_id: str | None) -> str:
    if format_id:
        spec = resolve_scenario_format(format_id=format_id, series_id=format_id, topic_id=format_id)
        return spec.format_id
    mode = (relation_mode or "").strip().lower()
    return _RELATION_MODE_DEFAULT_FORMAT.get(mode, "love")


def _sun_sign_from_horoscope_astro(astro: dict) -> str:
    return str(astro.get("sun") or "")


def _build_pair_scenario_context(
    *,
    format_id: str | None,
    relation_mode: str | None,
    deep_dive: dict | None,
    overall_score: int,
    from_sign: str,
    to_sign: str,
    from_element: str,
    to_element: str,
    from_modality: str,
    to_modality: str,
    block_feedback: dict[str, str] | None = None,
    locale: str = "ru",
) -> ScenarioMetricsContext:
    resolved_format = _resolve_pair_format_id(relation_mode, format_id)
    spec = resolve_scenario_format(format_id=resolved_format)
    attachment_ctx = build_attachment_reference_context(block_feedback, locale=locale)
    sub_raw = _funnel_subscores_from_deep_dive_dimensions(deep_dive)
    scenario_subscores, display_score = apply_scenario_metrics(
        resolved_format,
        sub_raw,
        overall_score,
        from_sign=from_sign,
        to_sign=to_sign,
        from_element=from_element,
        to_element=to_element,
        from_modality=from_modality,
        to_modality=to_modality,
    )
    return ScenarioMetricsContext(
        format_id=resolved_format,
        display_score=display_score,
        subscores=scenario_subscores.model_dump(),
        tone_mode=spec.tone_mode,
        deep_block_order=(attachment_ctx or {}).get("deep_block_order"),
        attachment_reference=attachment_ctx,
    )


def _funnel_subscores_from_deep_dive_dimensions(deep_dive: dict | None) -> dict[str, int]:
    if not deep_dive or not isinstance(deep_dive.get("dimensions"), list):
        return {"attraction": 55, "stability": 55, "conflicts": 55, "sexuality": 55}
    by_key: dict[str, int] = {}
    for d in deep_dive["dimensions"]:
        if not isinstance(d, dict):
            continue
        k = d.get("key")
        if k:
            by_key[str(k)] = int(d.get("score") or 50)
    attr = by_key.get("attraction", 50)
    emo = by_key.get("emotional", 50)
    comm = by_key.get("communication", 50)
    stab = by_key.get("stability", 50)
    long_t = by_key.get("long_term", 50)
    conflicts = max(0, min(100, 102 - comm))
    stability_mix = max(0, min(100, int(round((emo + stab) / 2))))
    sexuality = max(0, min(100, int(round(0.55 * attr + 0.45 * long_t))))
    return {
        "attraction": max(0, min(100, attr)),
        "stability": stability_mix,
        "conflicts": conflicts,
        "sexuality": sexuality,
    }


def _element_modality_from_horoscope_astro(astro: dict) -> tuple[str, str]:
    sun = astro.get("sun") or ""
    meta = lookup_sign_metadata(str(sun)) or {}
    return (str(meta.get("element") or ""), str(meta.get("modality") or ""))


def _sun_element_modality_from_chart(chart: Any) -> tuple[str, str]:
    positions = {
        item.get("body"): item
        for item in (getattr(chart, "positions", None) or [])
        if isinstance(item, dict) and item.get("body")
    }
    sun = (positions.get("Sun") or {}).get("sign") or ""
    meta = lookup_sign_metadata(str(sun)) or {}
    return (str(meta.get("element") or ""), str(meta.get("modality") or ""))


def _block_feedback_for_user(db: Session, user_id: int | None) -> dict[str, str] | None:
    if user_id is None:
        return None
    ctx = build_compatibility_learning_context(db, user_id=user_id)
    if not ctx:
        return None
    recent = ctx.get("recent_block_feedback") or {}
    if not isinstance(recent, dict) or not recent:
        return None
    allow = {"emotions", "communication", "conflicts", "sexuality", "long_term"}
    out = {k: str(v) for k, v in recent.items() if k in allow and str(v) in {"yes", "partial", "no"}}
    return out or None


def _build_profile_compare_funnel(
    *,
    profile_1: AstroProfile,
    profile_2: AstroProfile,
    horoscopes_1: dict,
    horoscopes_2: dict,
    relation_mode: str | None,
    format_id: str | None,
    overall_score: int,
    deep_dive: dict | None,
    locale: str,
    block_feedback: dict[str, str] | None = None,
) -> tuple[CompatibilityFunnelArtifact | None, ScenarioMetricsContext]:
    """Воронка для POST /compare (профили + быстрый движок): уровень birth_dates."""
    astro_1 = (horoscopes_1 or {}).get("astrology") or {}
    astro_2 = (horoscopes_2 or {}).get("astrology") or {}
    fe, fm = _element_modality_from_horoscope_astro(astro_1)
    te, tm = _element_modality_from_horoscope_astro(astro_2)
    fs = _sun_sign_from_horoscope_astro(astro_1)
    ts = _sun_sign_from_horoscope_astro(astro_2)
    scenario_ctx = _build_pair_scenario_context(
        format_id=format_id,
        relation_mode=relation_mode,
        deep_dive=deep_dive,
        overall_score=overall_score,
        from_sign=fs,
        to_sign=ts,
        from_element=fe,
        to_element=te,
        from_modality=fm,
        to_modality=tm,
        block_feedback=block_feedback,
        locale=locale,
    )
    ctx = _relation_mode_to_funnel_context(relation_mode)
    u1 = (profile_1.label or "").strip() or "1"
    u2 = (profile_2.label or "").strip() or "2"
    pd = build_pair_dynamics(
        user1_label=u1,
        user2_label=u2,
        from_modality=fm,
        to_modality=tm,
        from_element=fe,
        to_element=te,
        locale=locale,
    )
    if scenario_ctx.tone_mode == "playful":
        return None, scenario_ctx
    funnel = build_compatibility_funnel_artifact(
        mode="precise",
        relationship_context=ctx,
        overall_score=scenario_ctx.display_score,
        subscores=scenario_ctx.subscores,
        pair_dynamics=pd,
        user1_label=u1,
        user2_label=u2,
        from_element=fe,
        to_element=te,
        from_modality=fm,
        to_modality=tm,
        locale=locale,
        today_alignment=None,
        llm_base_model=None,
        format_id=scenario_ctx.format_id,
    )
    return funnel, scenario_ctx


def _build_synastry_funnel(
    *,
    profile_1: AstroProfile,
    profile_2: AstroProfile,
    chart1: Any,
    chart2: Any,
    relation_mode: str | None,
    format_id: str | None,
    payload: models.EnrichedCompatibilityResponse,
    locale: str,
    block_feedback: dict[str, str] | None = None,
) -> tuple[CompatibilityFunnelArtifact | None, ScenarioMetricsContext]:
    """Воронка для POST /synastry: уровень full_profile."""
    fe, fm = _sun_element_modality_from_chart(chart1)
    te, tm = _sun_element_modality_from_chart(chart2)
    positions1 = {
        item.get("body"): item
        for item in (getattr(chart1, "positions", None) or [])
        if isinstance(item, dict) and item.get("body")
    }
    positions2 = {
        item.get("body"): item
        for item in (getattr(chart2, "positions", None) or [])
        if isinstance(item, dict) and item.get("body")
    }
    fs = str((positions1.get("Sun") or {}).get("sign") or "")
    ts = str((positions2.get("Sun") or {}).get("sign") or "")
    deep = payload.deep_dive.model_dump() if payload.deep_dive else None
    scenario_ctx = _build_pair_scenario_context(
        format_id=format_id,
        relation_mode=relation_mode,
        deep_dive=deep,
        overall_score=int(payload.overall_score),
        from_sign=fs,
        to_sign=ts,
        from_element=fe,
        to_element=te,
        from_modality=fm,
        to_modality=tm,
        block_feedback=block_feedback,
        locale=locale,
    )
    ctx = _relation_mode_to_funnel_context(relation_mode)
    u1 = (profile_1.label or "").strip() or "1"
    u2 = (profile_2.label or "").strip() or "2"
    pd = build_pair_dynamics(
        user1_label=u1,
        user2_label=u2,
        from_modality=fm,
        to_modality=tm,
        from_element=fe,
        to_element=te,
        locale=locale,
    )
    if scenario_ctx.tone_mode == "playful":
        return None, scenario_ctx
    funnel = build_compatibility_funnel_artifact(
        mode="full",
        relationship_context=ctx,
        overall_score=scenario_ctx.display_score,
        subscores=scenario_ctx.subscores,
        pair_dynamics=pd,
        user1_label=u1,
        user2_label=u2,
        from_element=fe,
        to_element=te,
        from_modality=fm,
        to_modality=tm,
        locale=locale,
        today_alignment=None,
        llm_base_model=None,
        format_id=scenario_ctx.format_id,
    )
    return funnel, scenario_ctx


def _is_paid_user(user: Optional[User], db: Session) -> bool:
    if user is None:
        return False
    if user.is_paid:
        return True
    active_sub = (
        db.query(Subscription.id)
        .filter(
            Subscription.user_id == user.id,
            Subscription.status == "active",
        )
        .first()
    )
    return active_sub is not None


def _localized_element_relation(from_element: str, to_element: str, *, locale: str) -> str:
    fe = (from_element or "").lower()
    te = (to_element or "").lower()
    if fe == te:
        key = "compat.element.same"
    elif {fe, te} == {"fire", "air"}:
        key = "compat.element.fire_air"
    elif {fe, te} == {"earth", "water"}:
        key = "compat.element.earth_water"
    elif {fe, te} == {"fire", "water"}:
        key = "compat.element.fire_water"
    elif {fe, te} == {"earth", "air"}:
        key = "compat.element.earth_air"
    else:
        key = "compat.element.mixed"
    return translate(key, locale=locale)


def _localized_rhythm_relation(from_modality: str, to_modality: str, *, locale: str) -> str:
    fm = (from_modality or "").lower()
    tm = (to_modality or "").lower()
    if fm == tm:
        key = "compat.modality.same"
    elif {fm, tm} == {"cardinal", "fixed"}:
        key = "compat.modality.cardinal_fixed"
    elif {fm, tm} == {"cardinal", "mutable"}:
        key = "compat.modality.cardinal_mutable"
    elif {fm, tm} == {"fixed", "mutable"}:
        key = "compat.modality.fixed_mutable"
    else:
        key = "compat.modality.mixed"
    return translate(key, locale=locale)


def _build_static_sign_report(
    *,
    from_sign: str,
    to_sign: str,
    from_name: str,
    to_name: str,
    from_element: str,
    to_element: str,
    from_modality: str,
    to_modality: str,
    locale: str,
) -> dict:
    pair_key = f"{from_sign}:{to_sign}"
    content_id = f"sign-compatibility-{pair_key}"

    element_score = {
        ("fire", "fire"): 84,
        ("earth", "earth"): 80,
        ("air", "air"): 82,
        ("water", "water"): 81,
        ("fire", "air"): 86,
        ("air", "fire"): 86,
        ("earth", "water"): 83,
        ("water", "earth"): 83,
        ("fire", "water"): 61,
        ("water", "fire"): 61,
        ("earth", "air"): 63,
        ("air", "earth"): 63,
        ("fire", "earth"): 68,
        ("earth", "fire"): 68,
        ("air", "water"): 66,
        ("water", "air"): 66,
    }
    modality_bonus = 0
    if from_modality == to_modality:
        modality_bonus = 3
    elif {from_modality, to_modality} == {"cardinal", "mutable"}:
        modality_bonus = 1
    elif {from_modality, to_modality} == {"fixed", "mutable"}:
        modality_bonus = -1
    score = max(45, min(95, element_score.get((from_element, to_element), 70) + modality_bonus))

    element_relation = _localized_element_relation(from_element, to_element, locale=locale)
    rhythm_relation = _localized_rhythm_relation(from_modality, to_modality, locale=locale)
    summary = translate("compat.static.summary", locale=locale).format(
        from_name=from_name,
        to_name=to_name,
        element_relation=element_relation,
        rhythm_relation=rhythm_relation,
    )
    strongest = _quick_sign_strongest_text(score, element_relation, locale=locale)
    friction = _quick_sign_friction_text(score, rhythm_relation, locale=locale)
    next_step = _quick_sign_next_step(score, locale=locale)

    paragraphs = [
        translate("compat.static.para1", locale=locale).format(from_name=from_name, to_name=to_name),
        translate("compat.static.para2", locale=locale).format(element_relation=element_relation),
        translate("compat.static.para3", locale=locale).format(rhythm_relation=rhythm_relation),
        translate("compat.static.para4", locale=locale),
        translate("compat.static.para5", locale=locale),
    ]

    return {
        "content_id": content_id,
        "score": score,
        "summary": summary,
        "quick_reading": {
            "headline": _quick_sign_headline(score, locale=locale),
            "strongest": strongest,
            "friction": friction,
            "next_step": next_step,
            "strengths": [
                strongest,
                translate("compat.quick.strength_extra", locale=locale),
            ],
            "cautions": [
                friction,
                translate("compat.quick.caution_extra", locale=locale),
            ],
        },
        "paragraphs": paragraphs,
    }


def _quick_sign_headline(score: int, *, locale: str) -> str:
    if score >= 82:
        return translate("compat.quick.headline.hi", locale=locale)
    if score >= 68:
        return translate("compat.quick.headline.mid", locale=locale)
    if score >= 55:
        return translate("compat.quick.headline.low", locale=locale)
    return translate("compat.quick.headline.min", locale=locale)


def _quick_sign_strongest_text(score: int, element_relation: str, *, locale: str) -> str:
    if score >= 82:
        return translate("compat.quick.strongest.hi", locale=locale).format(element_relation=element_relation)
    if score >= 68:
        return translate("compat.quick.strongest.mid", locale=locale).format(element_relation=element_relation)
    if score >= 55:
        return translate("compat.quick.strongest.low", locale=locale).format(element_relation=element_relation)
    return translate("compat.quick.strongest.min", locale=locale).format(element_relation=element_relation)


def _quick_sign_friction_text(score: int, rhythm_relation: str, *, locale: str) -> str:
    if score >= 82:
        return translate("compat.quick.friction.hi", locale=locale).format(rhythm_relation=rhythm_relation)
    if score >= 68:
        return translate("compat.quick.friction.mid", locale=locale).format(rhythm_relation=rhythm_relation)
    if score >= 55:
        return translate("compat.quick.friction.low", locale=locale).format(rhythm_relation=rhythm_relation)
    return translate("compat.quick.friction.min", locale=locale).format(rhythm_relation=rhythm_relation)


def _quick_sign_next_step(score: int, *, locale: str) -> str:
    if score >= 82:
        return translate("compat.quick.next.hi", locale=locale)
    if score >= 68:
        return translate("compat.quick.next.mid", locale=locale)
    if score >= 55:
        return translate("compat.quick.next.low", locale=locale)
    return translate("compat.quick.next.min", locale=locale)


_FOCUS_TO_SEMANTIC: dict[str, str] = {
    "ясный старт и первый шаг": "clear_start",
    "устойчивость через понятный ритм": "steady_rhythm",
    "гибкость и мягкая перенастройка": "flexible_tune",
    "ритм через базовые микро-шаги": "micro_steps",
}


def _compatibility_personal_focus_phrase(raw_focus: object, *, locale: str) -> str:
    value = str(raw_focus or "").strip().lower()
    semantic = _FOCUS_TO_SEMANTIC.get(value)
    default_phrase = translate("compat.personalized.focus.default", locale=locale)
    if semantic:
        return translate(f"compat.personalized.focus.{semantic}", locale=locale)
    raw_strip = str(raw_focus or "").strip()
    return raw_strip or default_phrase


def _compatibility_personal_hint(user_sun: object, target_name: str, *, locale: str) -> str:
    sun = str(user_sun or "").strip()
    if sun:
        return translate("compat.personalized.hint.with_sun", locale=locale).format(target_name=target_name)
    return translate("compat.personalized.hint.no_sun", locale=locale).format(target_name=target_name)


def _compatibility_clean_personal_line(raw_line: object, fallback: str, *, locale: str) -> str:
    text = str(raw_line or "").strip()
    if not text:
        return fallback
    cleaned = text.replace("; ", ". ").replace("  ", " ").strip()
    loc = locale.strip().split("-")[0].lower()
    if loc == "ru":
        replacements = {
            "Смысл и коммуникация": "Открытый разговор и ясность",
            "Структура и устойчивость": "Понятный ритм и устойчивость",
            "Эмпатия и внутренняя глубина": "Бережность к чувствам",
            "Инициатива и действие": "Инициатива без давления",
            "Баланс и адаптация": "Спокойная настройка друг на друга",
        }
        for source, target in replacements.items():
            cleaned = cleaned.replace(source, target)
    return cleaned


async def _get_all_horoscopes_for_profile(profile: AstroProfile, db: Session) -> dict:
    """Получить все гороскопы для профиля (использует кеш натальных карт)."""
    birth_date = profile.birth_date if isinstance(profile.birth_date, date) else date.fromisoformat(str(profile.birth_date))
    
    chinese_service = get_chinese_horoscope_service()
    zoroastrian_service = get_zoroastrian_horoscope_service()
    tibetan_service = get_tibetan_horoscope_service()
    
    results = {
        "chinese": chinese_service.calculate(birth_date),
        "zoroastrian": zoroastrian_service.calculate(birth_date),
        "tibetan": tibetan_service.calculate(birth_date),
    }
    
    # Add Western astrology if time and coordinates are provided
    # Используем кеш натальных карт для ускорения
    if profile.birth_time and not profile.time_unknown and profile.latitude is not None and profile.longitude is not None:
        try:
            from todayflow_backend.services.natal_chart_cache import get_natal_chart_cache_service
            cache_service = get_natal_chart_cache_service(db)
            cached = cache_service.get_cached_natal_chart(profile.id)
            
            if cached and cached.positions:
                # Используем кешированные данные
                positions = cached.positions if isinstance(cached.positions, list) else cached.positions
                sun_sign = next((p.get("sign") for p in positions if p.get("body") == "Sun"), None)
                moon_sign = next((p.get("sign") for p in positions if p.get("body") == "Moon"), None)
                rising_sign = next((p.get("sign") for p in positions if p.get("body") in _RISING_POSITION_BODIES), None)
            else:
                # Если нет в кеше, вычисляем (но это медленно)
                astro_service = AstroService()
                
                if isinstance(profile.birth_time, time):
                    birth_time_str = profile.birth_time.strftime("%H:%M:%S")
                else:
                    birth_time_str = str(profile.birth_time)
                    if ":" not in birth_time_str:
                        birth_time_str = f"{birth_time_str}:00:00"
                
                birth_payload = {
                    "date": birth_date.isoformat(),
                    "time": birth_time_str,
                }
                coordinates = {
                    "latitude": profile.latitude,
                    "longitude": profile.longitude,
                }
                
                chart_response = await astro_service.compute_chart(birth_payload=birth_payload, coordinates=coordinates)
                await astro_service.close()
                
                if chart_response and chart_response.positions:
                    sun_sign = next((p.get("sign") for p in chart_response.positions if p.get("body") == "Sun"), None)
                    moon_sign = next((p.get("sign") for p in chart_response.positions if p.get("body") == "Moon"), None)
                    rising_sign = next((p.get("sign") for p in chart_response.positions if p.get("body") in _RISING_POSITION_BODIES), None)
                else:
                    sun_sign = moon_sign = rising_sign = None
            
            if sun_sign or moon_sign or rising_sign:
                results["astrology"] = {
                    "sun": sun_sign,
                    "moon": moon_sign,
                    "rising": rising_sign,
                    "description": f"Знак Солнца: {sun_sign}" + (f", Луны: {moon_sign}" if moon_sign else "") + (f", Восходящий: {rising_sign}" if rising_sign else ""),
                }
        except Exception:
            import logging
            logging.getLogger(__name__).warning(f"Failed to calculate astrology for profile {profile.id}")
            pass
    
    return results


@router.post("/compare", response_model=CompatibilityResponse)
async def compare_profiles(
    http_request: Request,
    request: CompatibilityRequest,
    user: User = Depends(require_user),
    db: Session = Depends(get_session),
    compatibility_engine: CompatibilityEngineService = Depends(get_compatibility_engine_service),
):
    """
    Сравнить два астрологических профиля и получить результаты совместимости.
    """
    locale = request_locale(http_request)

    # Получаем профили
    profile_1 = db.query(AstroProfile).filter(
        AstroProfile.id == request.profile_id_1,
        AstroProfile.user_id == user.id
    ).first()
    
    profile_2 = db.query(AstroProfile).filter(
        AstroProfile.id == request.profile_id_2,
        AstroProfile.user_id == user.id
    ).first()
    
    if not profile_1:
        raise HTTPException(status_code=404, detail=f"Profile {request.profile_id_1} not found")
    if not profile_2:
        raise HTTPException(status_code=404, detail=f"Profile {request.profile_id_2} not found")

    cache_key = _build_compatibility_cache_key(
        compatibility_type="quick",
        locale=locale,
        profile_1=profile_1,
        profile_2=profile_2,
        relation_mode=request.relation_mode,
        format_id=request.format_id,
    )
    pair_signature = _build_pair_signature(
        compatibility_type="quick",
        profile_1=profile_1,
        profile_2=profile_2,
        relation_mode=request.relation_mode,
    )
    cached = _get_cached_compatibility(db, user.id, cache_key, "quick", locale)
    if cached is not None:
        compatibility_payload = cached.get("compatibility") if isinstance(cached.get("compatibility"), dict) else None
        if compatibility_payload is not None and not isinstance(compatibility_payload.get("editorial"), dict):
            prior_memory = _find_prior_compatibility_memory(
                db,
                user_id=user.id,
                pair_signature=pair_signature,
                compatibility_type="quick",
                locale=locale,
            )
            compatibility_payload["editorial"] = generate_compatibility_editorial(
                db,
                user=user,
                relation_mode=_resolve_relation_mode_for_editorial(compatibility_payload, request.relation_mode),
                payload=compatibility_payload,
                prior_memory=prior_memory,
                locale=locale,
            ).model_dump()
            _store_cached_compatibility(
                db=db,
                user_id=user.id,
                cache_key=cache_key,
                compatibility_type="quick",
                locale=locale,
                result_data=cached,
                pair_signature=pair_signature,
                prior_memory=prior_memory,
            )
        cached_out = dict(cached)
        h1 = (cached_out.get("profile_1") or {}).get("horoscopes") or {}
        h2 = (cached_out.get("profile_2") or {}).get("horoscopes") or {}
        comp = cached_out.get("compatibility") or {}
        dd = comp.get("deep_dive")
        try:
            fa, scenario_ctx = _build_profile_compare_funnel(
                profile_1=profile_1,
                profile_2=profile_2,
                horoscopes_1=h1,
                horoscopes_2=h2,
                relation_mode=request.relation_mode,
                format_id=request.format_id,
                overall_score=int(comp.get("overall_score") or 0),
                deep_dive=dd if isinstance(dd, dict) else None,
                locale=locale,
                block_feedback=_block_feedback_for_user(db, user.id),
            )
            if cached_out.get("funnel_artifact") is None and fa is not None:
                cached_out["funnel_artifact"] = fa.model_dump(mode="json")
            cached_out["scenario_context"] = scenario_ctx.model_dump(mode="json")
        except Exception:
            cached_out["funnel_artifact"] = cached_out.get("funnel_artifact")
            cached_out["scenario_context"] = cached_out.get("scenario_context")
        sc = cached_out.get("scenario_context")
        att = sc.get("attachment_reference") if isinstance(sc, dict) else None
        _ensure_attachment_lens_for_user(db, user, att if isinstance(att, dict) else None)
        return CompatibilityResponse(**cached_out)
    prior_memory = _find_prior_compatibility_memory(
        db,
        user_id=user.id,
        pair_signature=pair_signature,
        compatibility_type="quick",
        locale=locale,
    )
    
    # Получаем гороскопы для обоих профилей (с использованием кеша)
    horoscopes_1 = await _get_all_horoscopes_for_profile(profile_1, db)
    horoscopes_2 = await _get_all_horoscopes_for_profile(profile_2, db)
    
    # Вычисляем быстрый, но уже структурированный слой совместимости
    core_for_lp = None
    try:
        core_for_lp = get_core_profile_service().build_cached_or_baseline(db, user)
    except Exception:
        core_for_lp = None
    compatibility_results = compatibility_engine.build_quick_payload(
        profile_1=profile_1,
        profile_2=profile_2,
        horoscopes_1=horoscopes_1,
        horoscopes_2=horoscopes_2,
        relation_mode=request.relation_mode,
        life_path_1=_life_path_from_personal_model(
            db, user_id=user.id, astro_profile=profile_1, core_profile=core_for_lp
        ),
        life_path_2=_life_path_from_personal_model(
            db, user_id=user.id, astro_profile=profile_2, core_profile=core_for_lp
        ),
    ).model_dump()
    compatibility_results = _apply_relation_mode_surface(
        compatibility_results,
        _resolve_relation_mode_for_editorial(compatibility_results, request.relation_mode),
    )
    
    # Нормализуем overall_score в проценты (0-100)
    if compatibility_results["overall_score"] > 100:
        compatibility_results["overall_score"] = min(100, compatibility_results["overall_score"])
    elif compatibility_results["overall_score"] < 0:
        compatibility_results["overall_score"] = max(0, compatibility_results["overall_score"])
    compatibility_results["editorial"] = generate_compatibility_editorial(
        db,
        user=user,
        relation_mode=_resolve_relation_mode_for_editorial(compatibility_results, request.relation_mode),
        payload=compatibility_results,
        prior_memory=prior_memory,
        locale=locale,
    ).model_dump()

    dd = compatibility_results.get("deep_dive")
    funnel_art, scenario_ctx = _build_profile_compare_funnel(
        profile_1=profile_1,
        profile_2=profile_2,
        horoscopes_1=horoscopes_1,
        horoscopes_2=horoscopes_2,
        relation_mode=request.relation_mode,
        format_id=request.format_id,
        overall_score=int(compatibility_results["overall_score"]),
        deep_dive=dd if isinstance(dd, dict) else None,
        locale=locale,
        block_feedback=_block_feedback_for_user(db, user.id),
    )

    response_payload = CompatibilityResponse(
        profile_1={
            "id": profile_1.id,
            "label": profile_1.label,
            "horoscopes": horoscopes_1,
        },
        profile_2={
            "id": profile_2.id,
            "label": profile_2.label,
            "horoscopes": horoscopes_2,
        },
        compatibility=compatibility_results,
        funnel_artifact=funnel_art,
        scenario_context=scenario_ctx,
    )
    _store_cached_compatibility(
        db=db,
        user_id=user.id,
        cache_key=cache_key,
        compatibility_type="quick",
        locale=locale,
        result_data=response_payload.model_dump(),
        pair_signature=pair_signature,
        prior_memory=prior_memory,
    )
    att = scenario_ctx.attachment_reference if scenario_ctx else None
    _ensure_attachment_lens_for_user(db, user, att if isinstance(att, dict) else None)
    return response_payload


def _calculate_compatibility(horoscopes_1: dict, horoscopes_2: dict) -> dict:
    """
    Вычислить совместимость между двумя профилями на основе гороскопов.
    """
    compatibility = {
        "overall_score": 0,
        "aspects": [],
        "synastry": {},
    }
    
    # Совместимость по китайскому гороскопу
    if "chinese" in horoscopes_1 and "chinese" in horoscopes_2:
        chinese_1 = horoscopes_1["chinese"]
        chinese_2 = horoscopes_2["chinese"]
        if "animal" in chinese_1 and "animal" in chinese_2:
            if chinese_2.get("animal") in chinese_1.get("compatibility", []):
                compatibility["aspects"].append({
                    "type": "chinese_zodiac",
                    "description": f"{chinese_1['animal']} и {chinese_2['animal']} - гармоничное сочетание",
                    "score": 8,
                })
                compatibility["overall_score"] += 8
    
    # Совместимость по знакам зодиака (Western astrology)
    if "astrology" in horoscopes_1 and "astrology" in horoscopes_2:
        astro_1 = horoscopes_1["astrology"]
        astro_2 = horoscopes_2["astrology"]
        
        sun_compatibility = _sign_compatibility(astro_1.get("sun"), astro_2.get("sun"))
        moon_compatibility = _sign_compatibility(astro_1.get("moon"), astro_2.get("moon"))
        
        if sun_compatibility:
            compatibility["aspects"].append({
                "type": "sun_signs",
                "description": f"Солнце {astro_1.get('sun')} и {astro_2.get('sun')} - {sun_compatibility['description']}",
                "score": sun_compatibility["score"],
            })
            compatibility["overall_score"] += sun_compatibility["score"]
        
        if moon_compatibility:
            compatibility["aspects"].append({
                "type": "moon_signs",
                "description": f"Луна {astro_1.get('moon')} и {astro_2.get('moon')} - {moon_compatibility['description']}",
                "score": moon_compatibility["score"],
            })
            compatibility["overall_score"] += moon_compatibility["score"]
        
        compatibility["synastry"] = {
            "sun": {
                "profile_1": astro_1.get("sun"),
                "profile_2": astro_2.get("sun"),
            },
            "moon": {
                "profile_1": astro_1.get("moon"),
                "profile_2": astro_2.get("moon"),
            },
            "rising": {
                "profile_1": astro_1.get("rising"),
                "profile_2": astro_2.get("rising"),
            },
        }
    
    # Нормализуем общий score (максимум 100)
    if compatibility["overall_score"] > 0:
        max_possible = len(compatibility["aspects"]) * 10 if compatibility["aspects"] else 20
        if max_possible > 0:
            compatibility["overall_score"] = min(100, int((compatibility["overall_score"] / max_possible) * 100))
        compatibility["overall_score"] = min(100, int((compatibility["overall_score"] / max_possible) * 100))
    
    return compatibility


def _sign_compatibility(sign1: Optional[str], sign2: Optional[str]) -> Optional[dict]:
    """Вычислить совместимость между двумя знаками зодиака."""
    if not sign1 or not sign2:
        return None
    
    # Простая логика совместимости (можно улучшить)
    fire_signs = ["Овен", "Лев", "Стрелец"]
    earth_signs = ["Телец", "Дева", "Козерог"]
    air_signs = ["Близнецы", "Весы", "Водолей"]
    water_signs = ["Рак", "Скорпион", "Рыбы"]
    
    signs_1_family = None
    signs_2_family = None
    
    if sign1 in fire_signs:
        signs_1_family = "fire"
    elif sign1 in earth_signs:
        signs_1_family = "earth"
    elif sign1 in air_signs:
        signs_1_family = "air"
    elif sign1 in water_signs:
        signs_1_family = "water"
    
    if sign2 in fire_signs:
        signs_2_family = "fire"
    elif sign2 in earth_signs:
        signs_2_family = "earth"
    elif sign2 in air_signs:
        signs_2_family = "air"
    elif sign2 in water_signs:
        signs_2_family = "water"
    
    if signs_1_family == signs_2_family:
        return {"description": "одна стихия - гармоничное сочетание", "score": 9}
    elif (signs_1_family == "fire" and signs_2_family == "air") or (signs_1_family == "air" and signs_2_family == "fire"):
        return {"description": "дополняющие стихии - активное взаимодействие", "score": 8}
    elif (signs_1_family == "earth" and signs_2_family == "water") or (signs_1_family == "water" and signs_2_family == "earth"):
        return {"description": "дополняющие стихии - стабильное взаимодействие", "score": 7}
    else:
        return {"description": "разные стихии - требуется больше понимания", "score": 5}


@router.post("/synastry", response_model=models.EnrichedCompatibilityResponse)
async def calculate_synastry(
    request: Request,
    request_data: CompatibilityRequest,
    user: User = Depends(require_user),
    db: Session = Depends(get_session),
    synastry_service: SynastryService = Depends(get_synastry_service),
    compatibility_engine: CompatibilityEngineService = Depends(get_compatibility_engine_service),
    astro_service: AstroService = Depends(get_astro_service),
) -> models.EnrichedCompatibilityResponse:
    """
    Calculate full synastry (astrological compatibility) between two natal charts.
    
    Returns:
    - Planet-to-planet aspects
    - Planet-to-angle aspects (ASC/MC)
    - House overlays
    - Strong aspects (Venus/Mars/Moon/Saturn/Pluto)
    - Compatibility summary
    """
    locale = request_locale(request)
    
    # Get both profiles
    profile_1 = db.query(AstroProfile).filter(
        AstroProfile.id == request_data.profile_id_1,
        AstroProfile.user_id == user.id
    ).first()
    
    profile_2 = db.query(AstroProfile).filter(
        AstroProfile.id == request_data.profile_id_2,
        AstroProfile.user_id == user.id
    ).first()
    
    if not profile_1:
        raise HTTPException(
            status_code=404,
            detail=translate("account.errors.profileNotFound", locale=locale, default=f"Profile {request_data.profile_id_1} not found")
        )
    if not profile_2:
        raise HTTPException(
            status_code=404,
            detail=translate("account.errors.profileNotFound", locale=locale, default=f"Profile {request_data.profile_id_2} not found")
        )

    cache_key = _build_compatibility_cache_key(
        compatibility_type="synastry",
        locale=locale,
        profile_1=profile_1,
        profile_2=profile_2,
        relation_mode=request_data.relation_mode,
        format_id=request_data.format_id,
    )
    pair_signature = _build_pair_signature(
        compatibility_type="synastry",
        profile_1=profile_1,
        profile_2=profile_2,
        relation_mode=request_data.relation_mode,
    )
    cached = _get_cached_compatibility(db, user.id, cache_key, "synastry", locale)
    if cached is not None:
        if not isinstance(cached.get("editorial"), dict):
            prior_memory = _find_prior_compatibility_memory(
                db,
                user_id=user.id,
                pair_signature=pair_signature,
                compatibility_type="synastry",
                locale=locale,
            )
            cached["editorial"] = generate_compatibility_editorial(
                db,
                user=user,
                relation_mode=_resolve_relation_mode_for_editorial(cached, request_data.relation_mode),
                payload=cached,
                prior_memory=prior_memory,
                locale=locale,
            ).model_dump()
            _store_cached_compatibility(
                db=db,
                user_id=user.id,
                cache_key=cache_key,
                compatibility_type="synastry",
                locale=locale,
                result_data=cached,
                pair_signature=pair_signature,
                prior_memory=prior_memory,
            )
        if not cached.get("funnel_artifact") or not cached.get("scenario_context"):
            try:
                chart1_fb = await _compute_chart_for_profile(profile_1, astro_service, locale, db)
                chart2_fb = await _compute_chart_for_profile(profile_2, astro_service, locale, db)
                payload_fb = models.EnrichedCompatibilityResponse.model_validate(cached)
                syn_funnel_fb, scenario_ctx_fb = _build_synastry_funnel(
                    profile_1=profile_1,
                    profile_2=profile_2,
                    chart1=chart1_fb,
                    chart2=chart2_fb,
                    relation_mode=request_data.relation_mode,
                    format_id=request_data.format_id,
                    payload=payload_fb,
                    locale=locale,
                    block_feedback=_block_feedback_for_user(db, user.id),
                )
                if not cached.get("funnel_artifact") and syn_funnel_fb is not None:
                    cached["funnel_artifact"] = syn_funnel_fb.model_dump(mode="json")
                cached["scenario_context"] = scenario_ctx_fb.model_dump(mode="json")
                prior_fb = _find_prior_compatibility_memory(
                    db,
                    user_id=user.id,
                    pair_signature=pair_signature,
                    compatibility_type="synastry",
                    locale=locale,
                )
                _store_cached_compatibility(
                    db=db,
                    user_id=user.id,
                    cache_key=cache_key,
                    compatibility_type="synastry",
                    locale=locale,
                    result_data=cached,
                    pair_signature=pair_signature,
                    prior_memory=prior_fb,
                )
            except Exception:
                import logging

                logging.getLogger(__name__).warning(
                    "synastry funnel_artifact cache backfill failed", exc_info=True
                )
        sc = cached.get("scenario_context")
        att = sc.get("attachment_reference") if isinstance(sc, dict) else None
        _ensure_attachment_lens_for_user(db, user, att if isinstance(att, dict) else None)
        return models.EnrichedCompatibilityResponse(**cached)
    prior_memory = _find_prior_compatibility_memory(
        db,
        user_id=user.id,
        pair_signature=pair_signature,
        compatibility_type="synastry",
        locale=locale,
    )
    
    # Compute natal charts for both profiles (использует кеш)
    chart1 = await _compute_chart_for_profile(profile_1, astro_service, locale, db)
    chart2 = await _compute_chart_for_profile(profile_2, astro_service, locale, db)
    
    # Calculate synastry
    synastry_report = await synastry_service.calculate_synastry(chart1, chart2, locale=locale)

    core_for_lp = None
    try:
        core_for_lp = get_core_profile_service().build_cached_or_baseline(db, user)
    except Exception:
        core_for_lp = None
    response_payload = compatibility_engine.build_deep_payload(
        profile_1=profile_1,
        profile_2=profile_2,
        chart1=chart1,
        chart2=chart2,
        synastry_report=synastry_report,
        relation_mode=request_data.relation_mode,
        life_path_1=_life_path_from_personal_model(
            db, user_id=user.id, astro_profile=profile_1, core_profile=core_for_lp
        ),
        life_path_2=_life_path_from_personal_model(
            db, user_id=user.id, astro_profile=profile_2, core_profile=core_for_lp
        ),
    )
    response_payload = await _enrich_deep_relation_mode(
        response_payload=response_payload,
        relation_mode=_resolve_relation_mode_for_editorial(response_payload.model_dump(), request_data.relation_mode),
        chart1=chart1,
        chart2=chart2,
        profile_1=profile_1,
        profile_2=profile_2,
        locale=locale,
    )
    response_payload.editorial = generate_compatibility_editorial(
        db,
        user=user,
        relation_mode=_resolve_relation_mode_for_editorial(response_payload.model_dump(), request_data.relation_mode),
        payload=response_payload.model_dump(),
        prior_memory=prior_memory,
        locale=locale,
    )
    syn_funnel, scenario_ctx = _build_synastry_funnel(
        profile_1=profile_1,
        profile_2=profile_2,
        chart1=chart1,
        chart2=chart2,
        relation_mode=request_data.relation_mode,
        format_id=request_data.format_id,
        payload=response_payload,
        locale=locale,
        block_feedback=_block_feedback_for_user(db, user.id),
    )
    response_payload = response_payload.model_copy(
        update={
            "funnel_artifact": syn_funnel.model_dump(mode="json") if syn_funnel else None,
            "scenario_context": scenario_ctx.model_dump(mode="json"),
        }
    )
    _store_cached_compatibility(
        db=db,
        user_id=user.id,
        cache_key=cache_key,
        compatibility_type="synastry",
        locale=locale,
        result_data=response_payload.model_dump(),
        pair_signature=pair_signature,
        prior_memory=prior_memory,
    )
    att = scenario_ctx.attachment_reference if scenario_ctx else None
    _ensure_attachment_lens_for_user(db, user, att if isinstance(att, dict) else None)
    return response_payload


def _build_internal_model_and_snapshot(chart: astro.ChartResponse) -> tuple[models.InternalModelSnapshot, models.ChartSnapshot]:
    internal_model = _INTERNAL_MODEL_MAPPER.map(chart.model_dump())
    snapshot = models.ChartSnapshot(
        sun=next((p.get("sign") for p in chart.positions if p.get("body") == "Sun"), "Unknown"),
        moon=next((p.get("sign") for p in chart.positions if p.get("body") == "Moon"), "Unknown"),
        rising=next((p.get("sign") for p in chart.positions if p.get("body") in _RISING_POSITION_BODIES), "Unknown"),
        houses=chart.houses,
    )
    return internal_model, snapshot


def _apply_relation_mode_surface(payload: dict, relation_mode: str | None) -> dict:
    mode = str(relation_mode or DEFAULT_RELATION_MODE).strip().lower()
    if mode == "romantic":
        return payload

    deep_dive = payload.get("deep_dive") if isinstance(payload.get("deep_dive"), dict) else None
    if not deep_dive:
        return payload

    dimensions = deep_dive.get("dimensions")
    if not isinstance(dimensions, list):
        return payload

    meta = _MODE_DIMENSION_META.get(mode)
    if not meta:
        return payload

    normalized_dimensions: list[dict] = []
    for item in dimensions:
        if not isinstance(item, dict):
            continue
        key = str(item.get("key") or "").strip()
        score = int(item.get("score") or 0)
        label = str(item.get("label") or key)
        summary = str(item.get("summary") or "").strip()
        mode_meta = meta.get(key)
        if mode_meta:
            label = mode_meta[0]
            score = max(25, min(96, score + mode_meta[1]))
            summary = mode_meta[2] if not summary else f"{mode_meta[2]} {summary}"
        normalized_dimensions.append(
            {
                **item,
                "label": label,
                "score": score,
                "summary": summary,
            }
        )

    if not normalized_dimensions:
        return payload

    deep_dive["dimensions"] = normalized_dimensions
    deep_dive["strongest_axis"] = max(normalized_dimensions, key=lambda item: int(item.get("score") or 0)).get("label")
    deep_dive["tension_axis"] = min(normalized_dimensions, key=lambda item: int(item.get("score") or 0)).get("label")
    payload["deep_dive"] = deep_dive
    return payload


def _merge_unique_lines(*groups: list[str]) -> list[str]:
    merged: list[str] = []
    seen: set[str] = set()
    for group in groups:
        for item in group:
            text = str(item or "").strip()
            if not text or text in seen:
                continue
            seen.add(text)
            merged.append(text)
    return merged


def _dimension_map(response_payload: models.EnrichedCompatibilityResponse) -> dict[str, models.CompatibilityDimension]:
    if not response_payload.deep_dive or not response_payload.deep_dive.dimensions:
        return {}
    return {item.key: item for item in response_payload.deep_dive.dimensions}


def _apply_mode_summary_overrides(response_payload: models.EnrichedCompatibilityResponse, relation_mode: str) -> None:
    meta = _MODE_DIMENSION_META.get(relation_mode)
    if not meta or not response_payload.deep_dive:
        return

    for item in response_payload.deep_dive.dimensions:
        mode_meta = meta.get(item.key)
        if not mode_meta:
            continue
        item.label = mode_meta[0]
        item.score = max(25, min(96, item.score + mode_meta[1]))
        item.summary = mode_meta[2] if not item.summary else f"{mode_meta[2]} {item.summary}"

    response_payload.deep_dive.strongest_axis = max(response_payload.deep_dive.dimensions, key=lambda item: item.score).label
    response_payload.deep_dive.tension_axis = min(response_payload.deep_dive.dimensions, key=lambda item: item.score).label


async def _build_psych_compatibility(
    chart1: astro.ChartResponse,
    chart2: astro.ChartResponse,
    locale: str | None,
) -> models.PsychCompatibilityReport:
    psych_service = await get_psych_compatibility_service()
    internal_model1, snapshot1 = _build_internal_model_and_snapshot(chart1)
    internal_model2, snapshot2 = _build_internal_model_and_snapshot(chart2)
    return await psych_service.analyze_compatibility(
        chart1,
        chart2,
        internal_model1,
        internal_model2,
        snapshot1,
        snapshot2,
        locale=locale,
    )


def _age_from_birth_date(birth_date: date | None) -> int | None:
    if not birth_date:
        return None
    today = date.today()
    years = today.year - birth_date.year
    if (today.month, today.day) < (birth_date.month, birth_date.day):
        years -= 1
    return max(0, years)


async def _enrich_deep_relation_mode(
    *,
    response_payload: models.EnrichedCompatibilityResponse,
    relation_mode: str,
    chart1: astro.ChartResponse,
    chart2: astro.ChartResponse,
    profile_1: AstroProfile,
    profile_2: AstroProfile,
    locale: str | None,
) -> models.EnrichedCompatibilityResponse:
    if not response_payload.deep_dive:
        return response_payload

    _apply_mode_summary_overrides(response_payload, relation_mode)
    dimensions = _dimension_map(response_payload)

    if relation_mode == "business":
        service = BusinessPartnershipService()
        roles_1 = service._extract_roles_from_chart(chart1)
        roles_2 = service._extract_roles_from_chart(chart2)
        role_pairs = service._analyze_role_compatibility_simple(roles_1, roles_2, locale)
        best_pair = role_pairs[0] if role_pairs else None

        business_strengths: list[str] = []
        business_challenges: list[str] = []
        business_guidance: list[str] = []
        if best_pair:
            business_strengths.extend(best_pair.strengths[:2])
            business_challenges.extend(best_pair.challenges[:2])
            business_guidance.extend(best_pair.recommendations[:2])
            if dimensions.get("communication"):
                dimensions["communication"].summary = f"В работе особенно важно, как распределяются роли и как вы обсуждаете решения. {dimensions['communication'].summary}"
            if dimensions.get("stability"):
                dimensions["stability"].summary = f"Для рабочей связки критично, выдерживает ли она ответственность, дедлайны и повторяющиеся процессы. {dimensions['stability'].summary}"

        response_payload.deep_dive.strengths = _merge_unique_lines(business_strengths, response_payload.deep_dive.strengths)[:6]
        response_payload.deep_dive.challenges = _merge_unique_lines(business_challenges, response_payload.deep_dive.challenges)[:6]
        response_payload.deep_dive.guidance = _merge_unique_lines(business_guidance, response_payload.deep_dive.guidance)[:6]
        return response_payload

    psych_report = await _build_psych_compatibility(chart1, chart2, locale)

    if relation_mode == "family":
        if dimensions.get("emotional"):
            dimensions["emotional"].summary = f"В семье особенно важно, как вы проходите чувства, не уходя в старые роли и защиту. {dimensions['emotional'].summary}"
        if dimensions.get("stability"):
            dimensions["stability"].summary = f"Этот слой показывает, есть ли у связи опора, границы и уважение к разному семейному темпу. {dimensions['stability'].summary}"
        response_payload.deep_dive.strengths = _merge_unique_lines(
            psych_report.what_you_do_perfectly[:2],
            psych_report.what_saves_you[:2],
            response_payload.deep_dive.strengths,
        )[:6]
        response_payload.deep_dive.challenges = _merge_unique_lines(
            psych_report.where_youll_argue[:2],
            response_payload.deep_dive.challenges,
        )[:6]
        response_payload.deep_dive.guidance = _merge_unique_lines(
            psych_report.relationship_rules[:3],
            response_payload.deep_dive.guidance,
        )[:6]
        return response_payload

    if relation_mode == "parent_child":
        child_service = ChildrenChartsService()
        internal_model2, snapshot2 = _build_internal_model_and_snapshot(chart2)
        child_report = await child_service.generate_children_report(
            chart=chart2,
            internal_model=internal_model2,
            snapshot=snapshot2,
            child_age=_age_from_birth_date(profile_2.birth_date),
            locale=locale,
        )
        if dimensions.get("emotional"):
            dimensions["emotional"].summary = f"В этой связи особенно важны чувствительность ребенка и способность взрослого не усиливать перегруз. {dimensions['emotional'].summary}"
        if dimensions.get("stability"):
            dimensions["stability"].summary = f"Здесь решающими становятся безопасность, понятный ритм и предсказуемость отклика. {dimensions['stability'].summary}"
        if dimensions.get("communication"):
            dimensions["communication"].summary = f"Важно не только что говорится, но и как именно ребенок слышит тон, паузу и давление. {dimensions['communication'].summary}"

        parent_child_strengths = [
            child_report.temperament.description,
            *child_report.parental_strategies[:2],
            *psych_report.what_saves_you[:1],
        ]
        parent_child_challenges = [
            *child_report.sensitivity.stress_triggers[:2],
            *psych_report.where_youll_argue[:1],
        ]
        parent_child_guidance = [
            *child_report.sensitivity.support_strategies[:2],
            *child_report.boundaries_discipline.recommendations[:2],
            *child_report.learning_interests.recommendations[:1],
        ]
        response_payload.deep_dive.strengths = _merge_unique_lines(parent_child_strengths, response_payload.deep_dive.strengths)[:6]
        response_payload.deep_dive.challenges = _merge_unique_lines(parent_child_challenges, response_payload.deep_dive.challenges)[:6]
        response_payload.deep_dive.guidance = _merge_unique_lines(parent_child_guidance, response_payload.deep_dive.guidance)[:6]
        return response_payload

    return response_payload


async def _compute_chart_for_profile(
    profile: AstroProfile,
    astro_service: AstroService,
    locale: str,
    db: Session,
) -> astro.ChartResponse:
    """Compute natal chart for an AstroProfile (использует кеш)."""
    if not profile.birth_time or profile.time_unknown or profile.latitude is None or profile.longitude is None:
        raise HTTPException(
            status_code=400,
            detail=translate(
                "compatibility.errors.incompleteProfile",
                locale=locale,
                default="Profile must have birth time and coordinates for synastry calculation"
            )
        )
    
    from todayflow_backend.services.natal_chart_cache import get_natal_chart_cache_service

    cache_service = get_natal_chart_cache_service(db)

    birth_date = profile.birth_date if isinstance(profile.birth_date, date) else date.fromisoformat(str(profile.birth_date))

    if isinstance(profile.birth_time, time):
        birth_time_str = profile.birth_time.strftime("%H:%M:%S")
    else:
        birth_time_str = str(profile.birth_time)
        if ":" not in birth_time_str:
            birth_time_str = f"{birth_time_str}:00:00"

    birth_payload = {
        "date": birth_date.isoformat(),
        "time": birth_time_str,
        "location": profile.location_name or f"{profile.latitude},{profile.longitude}",
    }
    coordinates = {
        "latitude": profile.latitude,
        "longitude": profile.longitude,
    }

    try:
        return await cache_service.get_or_compute_natal_chart(
            astro_profile=profile,
            astro_service=astro_service,
            birth_data=birth_payload,
            coordinates=coordinates,
        )
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to compute chart for profile {profile.id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=translate(
                "compatibility.errors.chartCalculationFailed",
                locale=locale,
                default="Failed to calculate natal chart"
            )
        )


def _build_compatibility_cache_key(
    *,
    compatibility_type: str,
    locale: str,
    profile_1: AstroProfile,
    profile_2: AstroProfile,
    relation_mode: str | None,
    format_id: str | None = None,
) -> str:
    resolved_format = _resolve_pair_format_id(relation_mode, format_id)
    raw = "|".join(
        [
            compatibility_type,
            locale,
            str(profile_1.id),
            str(profile_1.updated_at.isoformat() if profile_1.updated_at else ""),
            str(profile_1.birth_date.isoformat() if profile_1.birth_date else ""),
            str(profile_2.id),
            str(profile_2.updated_at.isoformat() if profile_2.updated_at else ""),
            str(profile_2.birth_date.isoformat() if profile_2.birth_date else ""),
            str(relation_mode or "default"),
            resolved_format,
        ]
    )
    return sha1(raw.encode("utf-8")).hexdigest()


def _build_pair_signature(
    *,
    compatibility_type: str,
    profile_1: AstroProfile,
    profile_2: AstroProfile,
    relation_mode: str | None,
) -> str:
    left, right = sorted([int(profile_1.id), int(profile_2.id)])
    return f"{compatibility_type}:{left}:{right}:{str(relation_mode or 'default').strip().lower()}"


def _resolve_relation_mode_for_editorial(payload: dict, requested_relation_mode: str | None) -> str:
    if isinstance(requested_relation_mode, str) and requested_relation_mode.strip():
        return requested_relation_mode.strip().lower()
    deep_dive = payload.get("deep_dive") if isinstance(payload.get("deep_dive"), dict) else {}
    knowledge = deep_dive.get("knowledge") if isinstance(deep_dive.get("knowledge"), dict) else {}
    relation_mode = knowledge.get("relationship_mode")
    if isinstance(relation_mode, str) and relation_mode.strip():
        return relation_mode.strip().lower()
    return DEFAULT_RELATION_MODE


def _compact_dimension_memory(raw_dimensions: object) -> list[dict]:
    if not isinstance(raw_dimensions, list):
        return []
    compact: list[dict] = []
    for item in raw_dimensions[:5]:
        if not isinstance(item, dict):
            continue
        compact.append(
            {
                "key": item.get("key"),
                "label": item.get("label"),
                "score": item.get("score"),
            }
        )
    return compact


def _compatibility_memory_from_payload(payload: dict) -> dict:
    deep_dive = payload.get("deep_dive") if isinstance(payload.get("deep_dive"), dict) else {}
    knowledge = deep_dive.get("knowledge") if isinstance(deep_dive.get("knowledge"), dict) else {}
    return {
        "version": 1,
        "summary": payload.get("summary"),
        "relationship_type": payload.get("relationship_type"),
        "relationship_archetype": deep_dive.get("relationship_archetype"),
        "relationship_mode": knowledge.get("relationship_mode"),
        "mode_title": knowledge.get("mode_title"),
        "strongest_axis": deep_dive.get("strongest_axis"),
        "tension_axis": deep_dive.get("tension_axis"),
        "top_strengths": [item for item in (deep_dive.get("strengths") or []) if isinstance(item, str)][:3],
        "top_challenges": [item for item in (deep_dive.get("challenges") or []) if isinstance(item, str)][:3],
        "top_guidance": [item for item in (deep_dive.get("guidance") or []) if isinstance(item, str)][:3],
        "dimensions": _compact_dimension_memory(deep_dive.get("dimensions")),
    }


def _merge_compatibility_memory(previous: dict | None, current: dict) -> dict:
    previous_history = previous.get("history") if isinstance(previous, dict) and isinstance(previous.get("history"), list) else []
    current_snapshot = {
        "summary": current.get("summary"),
        "relationship_type": current.get("relationship_type"),
        "relationship_archetype": current.get("relationship_archetype"),
        "strongest_axis": current.get("strongest_axis"),
        "tension_axis": current.get("tension_axis"),
        "top_strengths": current.get("top_strengths") or [],
        "top_challenges": current.get("top_challenges") or [],
        "top_guidance": current.get("top_guidance") or [],
    }
    history: list[dict] = [current_snapshot]
    for item in previous_history:
        if isinstance(item, dict) and item != current_snapshot:
            history.append(item)
        if len(history) >= 5:
            break

    merged = dict(current)
    merged["history"] = history
    return merged


def _wrap_cached_compatibility_payload(
    *,
    payload: dict,
    pair_signature: str,
    memory: dict,
) -> dict:
    return {
        "_cache_meta": {
            "pair_signature": pair_signature,
            "memory": memory,
        },
        "payload": payload,
    }


def _unwrap_cached_compatibility_payload(result_data: dict) -> dict:
    payload = result_data.get("payload") if isinstance(result_data.get("payload"), dict) else None
    if payload is not None:
        return payload
    return result_data


def _extract_cached_compatibility_memory(result_data: dict) -> dict | None:
    cache_meta = result_data.get("_cache_meta") if isinstance(result_data.get("_cache_meta"), dict) else {}
    memory = cache_meta.get("memory")
    if isinstance(memory, dict):
        return memory
    payload = result_data.get("payload") if isinstance(result_data.get("payload"), dict) else result_data
    if isinstance(payload, dict):
        return _compatibility_memory_from_payload(payload)
    return None


def _find_prior_compatibility_memory(
    db: Session,
    *,
    user_id: int,
    pair_signature: str,
    compatibility_type: str,
    locale: str,
) -> dict | None:
    records = (
        db.query(CachedCompatibility)
        .filter(
            CachedCompatibility.user_id == user_id,
            CachedCompatibility.compatibility_type == compatibility_type,
            CachedCompatibility.locale == locale,
        )
        .order_by(CachedCompatibility.updated_at.desc())
        .limit(20)
        .all()
    )
    for record in records:
        result_data = record.result_data if isinstance(record.result_data, dict) else {}
        cache_meta = result_data.get("_cache_meta") if isinstance(result_data.get("_cache_meta"), dict) else {}
        if cache_meta.get("pair_signature") == pair_signature:
            return _extract_cached_compatibility_memory(result_data)
    return None


def _get_cached_compatibility(
    db: Session,
    user_id: int,
    cache_key: str,
    compatibility_type: str,
    locale: str,
) -> dict | None:
    record = (
        db.query(CachedCompatibility)
        .filter(
            CachedCompatibility.user_id == user_id,
            CachedCompatibility.cache_key == cache_key,
            CachedCompatibility.compatibility_type == compatibility_type,
            CachedCompatibility.locale == locale,
        )
        .first()
    )
    if record is None:
        return None
    if record.expires_at <= utc_naive_now():
        db.delete(record)
        db.commit()
        return None
    if not isinstance(record.result_data, dict):
        return None
    return _unwrap_cached_compatibility_payload(record.result_data)


def _store_cached_compatibility(
    *,
    db: Session,
    user_id: int,
    cache_key: str,
    compatibility_type: str,
    locale: str,
    result_data: dict,
    pair_signature: str,
    prior_memory: dict | None = None,
) -> None:
    expires_at = utc_naive_now() + timedelta(hours=COMPATIBILITY_CACHE_TTL_HOURS)
    current_memory = _compatibility_memory_from_payload(result_data)
    merged_memory = _merge_compatibility_memory(prior_memory, current_memory)
    stored_payload = _wrap_cached_compatibility_payload(
        payload=copy.deepcopy(result_data),
        pair_signature=pair_signature,
        memory=merged_memory,
    )
    existing = (
        db.query(CachedCompatibility)
        .filter(
            CachedCompatibility.user_id == user_id,
            CachedCompatibility.cache_key == cache_key,
        )
        .first()
    )
    if existing is not None:
        existing.compatibility_type = compatibility_type
        existing.locale = locale
        existing.result_data = stored_payload
        existing.expires_at = expires_at
        db.add(existing)
        db.commit()
        return

    cache_record = CachedCompatibility(
        user_id=user_id,
        cache_key=cache_key,
        compatibility_type=compatibility_type,
        locale=locale,
        result_data=stored_payload,
        expires_at=expires_at,
    )
    db.add(cache_record)
    db.commit()


@router.post("/composite", response_model=models.CompositeChart)
async def calculate_composite_chart(
    request: Request,
    request_data: CompatibilityRequest,
    user: User = Depends(require_user),
    db: Session = Depends(get_session),
    composite_service: CompositeChartService = Depends(get_composite_chart_service),
    astro_service: AstroService = Depends(get_astro_service),
) -> models.CompositeChart:
    """
    Calculate Composite chart (midpoint method) for relationship analysis.
    
    Composite chart shows how the relationship functions as a system,
    using midpoints between two people's planetary positions.
    """
    locale = request_locale(request)
    
    # Get both profiles
    profile_1 = db.query(AstroProfile).filter(
        AstroProfile.id == request_data.profile_id_1,
        AstroProfile.user_id == user.id
    ).first()
    
    profile_2 = db.query(AstroProfile).filter(
        AstroProfile.id == request_data.profile_id_2,
        AstroProfile.user_id == user.id
    ).first()
    
    if not profile_1:
        raise HTTPException(
            status_code=404,
            detail=translate("account.errors.profileNotFound", locale=locale, default=f"Profile {request_data.profile_id_1} not found")
        )
    if not profile_2:
        raise HTTPException(
            status_code=404,
            detail=translate("account.errors.profileNotFound", locale=locale, default=f"Profile {request_data.profile_id_2} not found")
        )
    
    # Compute natal charts for both profiles (использует кеш)
    chart1 = await _compute_chart_for_profile(profile_1, astro_service, locale, db)
    chart2 = await _compute_chart_for_profile(profile_2, astro_service, locale, db)
    
    # Calculate composite chart
    composite_chart = await composite_service.calculate_composite_chart(chart1, chart2, locale=locale)
    
    return composite_chart


@router.post("/davison", response_model=models.DavisonChart)
async def calculate_davison_chart(
    request: Request,
    request_data: CompatibilityRequest,
    user: User = Depends(require_user),
    db: Session = Depends(get_session),
    composite_service: CompositeChartService = Depends(get_composite_chart_service),
    astro_service: AstroService = Depends(get_astro_service),
) -> models.DavisonChart:
    """
    Calculate Davison chart (time-space midpoint method) for relationship analysis.
    
    Davison chart uses the midpoint of birth dates/times and locations
    to create a chart for the "relationship moment".
    """
    locale = request_locale(request)
    
    # Get both profiles
    profile_1 = db.query(AstroProfile).filter(
        AstroProfile.id == request_data.profile_id_1,
        AstroProfile.user_id == user.id
    ).first()
    
    profile_2 = db.query(AstroProfile).filter(
        AstroProfile.id == request_data.profile_id_2,
        AstroProfile.user_id == user.id
    ).first()
    
    if not profile_1:
        raise HTTPException(
            status_code=404,
            detail=translate("account.errors.profileNotFound", locale=locale, default=f"Profile {request_data.profile_id_1} not found")
        )
    if not profile_2:
        raise HTTPException(
            status_code=404,
            detail=translate("account.errors.profileNotFound", locale=locale, default=f"Profile {request_data.profile_id_2} not found")
        )
    
    # Get birth dates and times
    birth_date1 = profile_1.birth_date if isinstance(profile_1.birth_date, date) else date.fromisoformat(str(profile_1.birth_date))
    birth_time1 = profile_1.birth_time if isinstance(profile_1.birth_time, time) else None
    birth_date2 = profile_2.birth_date if isinstance(profile_2.birth_date, date) else date.fromisoformat(str(profile_2.birth_date))
    birth_time2 = profile_2.birth_time if isinstance(profile_2.birth_time, time) else None
    
    # Compute natal charts (needed for Davison calculation)
    chart1 = await _compute_chart_for_profile(profile_1, astro_service, locale, db)
    chart2 = await _compute_chart_for_profile(profile_2, astro_service, locale, db)
    
    # Calculate Davison chart
    davison_chart = await composite_service.calculate_davison_chart(
        chart1, chart2,
        birth_date1, birth_time1,
        birth_date2, birth_time2,
        locale=locale
    )
    
    return davison_chart


@router.post("/psych", response_model=models.PsychCompatibilityReport)
async def calculate_psych_compatibility(
    request: Request,
    request_data: CompatibilityRequest,
    user: User = Depends(require_user),
    db: Session = Depends(get_session),
    psych_service: PsychCompatibilityService = Depends(get_psych_compatibility_service),
    astro_service: AstroService = Depends(get_astro_service),
    lite_service: LiteReportService = Depends(get_lite_report_service),
) -> models.PsychCompatibilityReport:
    """
    Calculate psychological compatibility between two people.
    
    Returns:
    - Conflict styles analysis
    - Closeness vs autonomy needs
    - Boundary themes
    - Communication recommendations
    - What you do perfectly
    - Where you'll argue
    - What saves you
    - Relationship rules
    """
    locale = request_locale(request)
    
    # Get both profiles
    profile_1 = db.query(AstroProfile).filter(
        AstroProfile.id == request_data.profile_id_1,
        AstroProfile.user_id == user.id
    ).first()
    
    profile_2 = db.query(AstroProfile).filter(
        AstroProfile.id == request_data.profile_id_2,
        AstroProfile.user_id == user.id
    ).first()
    
    if not profile_1:
        raise HTTPException(
            status_code=404,
            detail=translate("account.errors.profileNotFound", locale=locale, default=f"Profile {request_data.profile_id_1} not found")
        )
    if not profile_2:
        raise HTTPException(
            status_code=404,
            detail=translate("account.errors.profileNotFound", locale=locale, default=f"Profile {request_data.profile_id_2} not found")
        )
    
    # Compute natal charts
    chart1 = await _compute_chart_for_profile(profile_1, astro_service, locale, db)
    chart2 = await _compute_chart_for_profile(profile_2, astro_service, locale, db)
    
    # Get internal models and snapshots (need to compute lite reports or extract from existing)
    # For now, we'll compute them
    from todayflow_backend.core import models as core_models
    from todayflow_backend.services.mapping import InternalModelMapper
    
    birth_data1 = core_models.BirthData(
        date=profile_1.birth_date.isoformat(),
        time=profile_1.birth_time.isoformat() if profile_1.birth_time else None,
        location=profile_1.location_name or "",
        coordinates=core_models.Coordinates(
            latitude=profile_1.latitude or 0.0,
            longitude=profile_1.longitude or 0.0,
        ) if profile_1.latitude and profile_1.longitude else None,
    )
    
    birth_data2 = core_models.BirthData(
        date=profile_2.birth_date.isoformat(),
        time=profile_2.birth_time.isoformat() if profile_2.birth_time else None,
        location=profile_2.location_name or "",
        coordinates=core_models.Coordinates(
            latitude=profile_2.latitude or 0.0,
            longitude=profile_2.longitude or 0.0,
        ) if profile_2.latitude and profile_2.longitude else None,
    )
    
    # Compute internal models
    mapper = InternalModelMapper()
    internal_model1 = mapper.map(chart1.model_dump())
    internal_model2 = mapper.map(chart2.model_dump())
    
    # Create snapshots
    snapshot1 = core_models.ChartSnapshot(
        sun=next((p.get("sign") for p in chart1.positions if p.get("body") == "Sun"), "Unknown"),
        moon=next((p.get("sign") for p in chart1.positions if p.get("body") == "Moon"), "Unknown"),
        rising=next((p.get("sign") for p in chart1.positions if p.get("body") in _RISING_POSITION_BODIES), "Unknown"),
        houses=chart1.houses,
    )
    
    snapshot2 = core_models.ChartSnapshot(
        sun=next((p.get("sign") for p in chart2.positions if p.get("body") == "Sun"), "Unknown"),
        moon=next((p.get("sign") for p in chart2.positions if p.get("body") == "Moon"), "Unknown"),
        rising=next((p.get("sign") for p in chart2.positions if p.get("body") in _RISING_POSITION_BODIES), "Unknown"),
        houses=chart2.houses,
    )
    
    # Calculate psychological compatibility
    psych_report = await psych_service.analyze_compatibility(
        chart1, chart2,
        internal_model1, internal_model2,
        snapshot1, snapshot2,
        locale=locale
    )
    
    return psych_report


@router.get("/business-partnership", response_model=models.BusinessPartnershipReport)
async def get_business_partnership(
    request: Request,
    profile1_id: int = Query(..., description="ID первого астро профиля"),
    profile2_id: int = Query(..., description="ID второго астро профиля"),
    user: User = Depends(require_user),
    db: Session = Depends(get_session),
    astro_service: AstroService = Depends(get_astro_service),
) -> models.BusinessPartnershipReport:
    """Get business partnership compatibility analysis."""
    from todayflow_backend.services.business_partnership import BusinessPartnershipService
    
    locale = request_locale(request)
    
    # Get both profiles
    profile1 = db.query(AstroProfile).filter(
        AstroProfile.id == profile1_id,
        AstroProfile.user_id == user.id
    ).first()
    
    profile2 = db.query(AstroProfile).filter(
        AstroProfile.id == profile2_id,
        AstroProfile.user_id == user.id
    ).first()
    
    if not profile1:
        raise HTTPException(
            status_code=404,
            detail=translate("account.errors.profileNotFound", locale=locale, default=f"Profile {profile1_id} not found")
        )
    if not profile2:
        raise HTTPException(
            status_code=404,
            detail=translate("account.errors.profileNotFound", locale=locale, default=f"Profile {profile2_id} not found")
        )
    
    # Compute charts
    chart1 = await _compute_chart_for_profile(profile1, astro_service, locale, db)
    chart2 = await _compute_chart_for_profile(profile2, astro_service, locale, db)
    
    # Analyze business partnership
    service = BusinessPartnershipService(astro_service=astro_service)
    report = await service.analyze_business_partnership(
        chart1=chart1,
        chart2=chart2,
        locale=locale,
    )
    
    return report


@router.post("/group", response_model=models.GroupCompatibilityReport)
async def get_group_compatibility(
    request: Request,
    body: GroupCompatibilityRequest,
    user: User = Depends(require_user),
    db: Session = Depends(get_session),
    astro_service: AstroService = Depends(get_astro_service),
    group_service: GroupCompatibilityService = Depends(get_group_compatibility_service),
) -> models.GroupCompatibilityReport:
    """
    Get group compatibility analysis for 3+ people.
    
    Analyzes:
    - Pairwise synastry between all members
    - Group roles and dynamics
    - Tension zones and conflict areas
    - Recommendations for the group
    """
    locale = request_locale(request)
    
    if len(body.profile_ids) < 3:
        raise HTTPException(
            status_code=400,
            detail=translate("compatibility.group.minimum", locale=locale, default="Group compatibility requires at least 3 people")
        )
    
    # Get all profiles
    profiles = db.query(AstroProfile).filter(
        AstroProfile.id.in_(body.profile_ids),
        AstroProfile.user_id == user.id
    ).all()
    
    if len(profiles) != len(body.profile_ids):
        raise HTTPException(
            status_code=404,
            detail=translate("compatibility.group.profilesNotFound", locale=locale, default="One or more profiles not found")
        )
    
    # Compute charts for all profiles
    charts = []
    profile_labels = []
    for profile in profiles:
        chart = await _compute_chart_for_profile(profile, astro_service, locale, db)
        charts.append(chart)
        profile_labels.append(profile.label or f"Profile {profile.id}")
    
    # Analyze group compatibility
    report = await group_service.analyze_group(
        charts=charts,
        profile_labels=profile_labels,
        locale=locale,
    )
    
    return report

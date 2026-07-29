"""Единый API для цикла дня: Утро → День → Вечер."""

import logging
import time
from datetime import date, datetime, timedelta
from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy import and_, func

from todayflow_backend.api.auth import require_user
from todayflow_backend.api.date_utils import parse_iso_date_or_400
from todayflow_backend.api.morning_ritual import get_morning_ritual, MorningRitualResponse
from todayflow_backend.api.day_connection import get_day_connection, DayConnectionResponse
from todayflow_backend.api.tracking import (
    DayRitualResponse,
    FusionIndexResponse,
    get_daily_fusion_index,
    get_day_ritual,
    get_progress_entries,
)
from todayflow_backend.services import astro
from todayflow_backend.services.geocode import Geocoder
from todayflow_backend.services.personal_transits import get_personal_transit_service
from todayflow_backend.api.journal import get_journal_entries
from todayflow_backend.db.session import get_session
from todayflow_backend.db import models as db_models
from todayflow_backend.db.models import User
from todayflow_backend.i18n import request_locale
from todayflow_backend.services.core_profile import CoreProfileService, get_core_profile_service
from todayflow_backend.services.interpretation_orchestrator import (
    InterpretationOrchestrator,
    get_interpretation_orchestrator,
)
from todayflow_backend.services.numerology import NumerologyService, get_numerology_service
from todayflow_backend.services.insight_depth import get_insight_depth_tier
from todayflow_backend.services.generation_orchestrator import run_today_narrative_pipeline
from todayflow_backend.services.today_narrative import _normalize_depth_level
from todayflow_backend.constants.reward_rings import REWARD_RING_THRESHOLDS, compute_reward_rings_earned
from todayflow_backend.services.meaning_progress import (
    build_archetype_progress,
    build_growth_index_from_rings,
    build_meaning_progress_snapshot,
    compute_consistency_bonus,
    resolve_archetype_level,
)
from todayflow_backend.services.day_story_wire_v1 import build_day_story_v1_wire
from todayflow_backend.services.today_contract_wire_v1 import build_today_contract_v1_wire

router = APIRouter(prefix="/today", tags=["today"])
logger = logging.getLogger(__name__)


def _effective_narrative_depth_level(db, user: User, requested: str | None) -> str:
    """DE-8: явный depth_level в теле запроса переопределяет сохранённую настройку; если поле не передано — из user_settings."""
    if requested is not None:
        return _normalize_depth_level(requested)
    row = (
        db.query(db_models.UserSettings)
        .filter(db_models.UserSettings.user_id == user.id)
        .first()
    )
    stored = getattr(row, "today_narrative_depth_level", None) if row else None
    return _normalize_depth_level(str(stored) if stored else None)

class TodayCycleResponse(BaseModel):
    """Полный цикл дня: Утро → День → Вечер."""
    date: str
    
    # Утро
    morning: Optional[MorningRitualResponse] = None
    morning_completed: bool = False
    
    # День
    day_connection: Optional[DayConnectionResponse] = None
    day_trackers: list = []  # Быстрые трекеры
    day_journal_entries: list = []  # Записи дневника за день
    day_completed: bool = False
    
    # Вечер
    evening: Optional[DayRitualResponse] = None
    evening_completed: bool = False
    
    # Статус доступа
    morning_available: bool = True
    day_available: bool = False
    evening_available: bool = False
    core_profile: Optional[dict] = None
    consistency: Optional[dict] = None
    rewards: Optional[dict] = None
    reward_milestones: list[dict] = []


class TodayOpeningResponse(BaseModel):
    """Минимальный слой первого кадра дня: связка дня и флаги доступности без тяжёлых агрегатов."""

    date: str
    day_connection: Optional[DayConnectionResponse] = None
    morning_completed: bool = False
    day_completed: bool = False
    evening_completed: bool = False
    morning_available: bool = True
    day_available: bool = False
    evening_available: bool = False


class TodayCheckinPromptResponse(BaseModel):
    """Следующий логичный микро-чекин по данным DayConnection (без тяжёлой генерации)."""

    date: str
    primary_kind: str
    title: str
    subtitle: Optional[str] = None
    input_hint: Optional[str] = None
    evening_window: bool = False
    slots_filled: dict[str, bool] = Field(default_factory=dict)


class DailyFoundationCore(BaseModel):
    """Стержень дня без сценариев по сферам — для progressive load."""

    headline: Optional[str] = None
    profile_prism: Optional[str] = None
    spine: Optional[dict[str, Any]] = None


class TodayCoreResponse(BaseModel):
    """Утренний слой дня без списка сценариев (таро, число, стержень, decision_engine, профиль)."""

    date: str
    tarot_card: dict
    tarot_explanation: dict
    numerology_number: dict
    numerology_explanation: dict
    daily_forecast_link: Optional[str] = None
    daily_forecast_summary: Optional[dict] = None
    daily_foundation: DailyFoundationCore
    daily_horoscope_generation_log_id: Optional[int] = None
    celestial_events: Optional[dict] = None
    daily_recommendations: Optional[dict] = None
    decision_engine: Optional[dict] = None
    consistency: Optional[dict] = None
    core_profile: Optional[dict] = None


class TodayScenariosResponse(BaseModel):
    """Сценарии дня по сферам (поверх стержня); клиент дергает после /today/core при необходимости."""

    date: str
    headline: Optional[str] = None
    profile_prism: Optional[str] = None
    scenarios: list = Field(default_factory=list)
    daily_horoscope_generation_log_id: Optional[int] = None


class TodayProgressiveBundleResponse(BaseModel):
    """Один проход morning-ritual: core + scenarios (предпочтительно для мобильного клиента)."""

    date: str
    core: TodayCoreResponse
    scenarios: TodayScenariosResponse


class TodayEveningResponse(BaseModel):
    """Вечерний слой: связка + объект ritual закрытия дня."""

    date: str
    evening_available: bool = False
    evening_completed: bool = False
    evening_reflection: Optional[str] = None
    evening_observations: Optional[dict] = None
    connection_thread: Optional[str] = None
    ritual: Optional[DayRitualResponse] = None


def _build_checkin_prompt(
    *,
    target_date: str,
    dc: Optional[DayConnectionResponse],
    target_date_obj: date,
    today_date: date,
    hour: int,
    locale: str,
) -> TodayCheckinPromptResponse:
    en = str(locale).lower().startswith("en")

    def _filled() -> dict[str, bool]:
        return {
            "morning_intention": bool(dc and (dc.morning_intention or "").strip()),
            "ritual_feedback": bool(dc and (dc.ritual_feedback or "").strip()),
            "quick_decision": bool(dc and (dc.quick_decision_answer or "").strip()),
            "question_of_day": bool(dc and (dc.question_of_day_answer or "").strip()),
            "evening_reflection": bool(dc and (dc.evening_reflection or "").strip()),
        }

    slots = _filled()
    evening_window = (target_date_obj < today_date) or (target_date_obj == today_date and hour >= 18)

    if not slots["morning_intention"]:
        if en:
            title, subtitle, hint = (
                "One line for today",
                "What do you want to hold — not a full weekly plan.",
                "e.g. stay calm before an important talk",
            )
        else:
            title, subtitle, hint = (
                "Одна строка на день",
                "Что важно удержать сегодня — без плана на неделю.",
                "Например: спокойно подготовиться к разговору",
            )
        return TodayCheckinPromptResponse(
            date=target_date,
            primary_kind="morning_intention",
            title=title,
            subtitle=subtitle,
            input_hint=hint,
            evening_window=evening_window,
            slots_filled=slots,
        )

    if not slots["ritual_feedback"]:
        if en:
            title, subtitle = ("How did the day land?", "A quick mark is enough — no essay needed.")
        else:
            title, subtitle = ("Как день лёг?", "Достаточно короткой отметки — без развёрнутого текста.")
        return TodayCheckinPromptResponse(
            date=target_date,
            primary_kind="ritual_feedback",
            title=title,
            subtitle=subtitle,
            evening_window=evening_window,
            slots_filled=slots,
        )

    if not slots["quick_decision"]:
        if en:
            title, subtitle = (
                "Optional add-on today?",
                "Yes / no / unclear — about one extra task, ask, or impulse, not your whole plan.",
            )
        else:
            title, subtitle = (
                "Взять ли ещё одно в день?",
                "Да / нет / неясно — про один лишний шаг (задача, просьба, импульс), не про весь план дня.",
            )
        return TodayCheckinPromptResponse(
            date=target_date,
            primary_kind="quick_decision",
            title=title,
            subtitle=subtitle,
            evening_window=evening_window,
            slots_filled=slots,
        )

    if not slots["question_of_day"]:
        if en:
            title, subtitle = (
                "Soft check-in",
                "One optional answer — helps us understand your context over time.",
            )
        else:
            title, subtitle = (
                "Чуть лучше узнать тебя",
                "Один ненавязчивый ответ — со временем точнее инсайты про ритм и среду, не только про сегодня.",
            )
        return TodayCheckinPromptResponse(
            date=target_date,
            primary_kind="question_of_day",
            title=title,
            subtitle=subtitle,
            evening_window=evening_window,
            slots_filled=slots,
        )

    if evening_window and not slots["evening_reflection"]:
        if en:
            title, subtitle, hint = (
                "Close the day in one breath",
                "What shifted — even in one sentence.",
                "e.g. I held my boundary once",
            )
        else:
            title, subtitle, hint = (
                "Закрыть день в одном дыхании",
                "Что сдвинулось — хотя бы одной фразой.",
                "Например: один раз удержала границу",
            )
        return TodayCheckinPromptResponse(
            date=target_date,
            primary_kind="evening_reflection",
            title=title,
            subtitle=subtitle,
            input_hint=hint,
            evening_window=True,
            slots_filled=slots,
        )

    if en:
        title, subtitle = ("You are caught up for now", "Come back later or deepen Today when you want more.")
    else:
        title, subtitle = ("На сейчас фиксаций достаточно", "Можно вернуться позже или углубиться в Today, когда захочется.")
    return TodayCheckinPromptResponse(
        date=target_date,
        primary_kind="complete",
        title=title,
        subtitle=subtitle,
        evening_window=evening_window,
        slots_filled=slots,
    )


def _strip_daily_foundation_core(daily_horoscope: Optional[dict]) -> DailyFoundationCore:
    if not isinstance(daily_horoscope, dict):
        return DailyFoundationCore()
    return DailyFoundationCore(
        headline=daily_horoscope.get("headline"),
        profile_prism=daily_horoscope.get("profile_prism"),
        spine=daily_horoscope.get("spine") if isinstance(daily_horoscope.get("spine"), dict) else None,
    )


def _morning_to_core_response(m: MorningRitualResponse) -> TodayCoreResponse:
    return TodayCoreResponse(
        date=m.date,
        tarot_card=m.tarot_card,
        tarot_explanation=m.tarot_explanation,
        numerology_number=m.numerology_number,
        numerology_explanation=m.numerology_explanation,
        daily_forecast_link=m.daily_forecast_link,
        daily_forecast_summary=m.daily_forecast_summary,
        daily_foundation=_strip_daily_foundation_core(m.daily_horoscope),
        daily_horoscope_generation_log_id=m.daily_horoscope_generation_log_id,
        celestial_events=m.celestial_events,
        daily_recommendations=m.daily_recommendations,
        decision_engine=m.decision_engine,
        consistency=m.consistency,
        core_profile=m.core_profile,
    )


def _morning_to_scenarios_response(m: MorningRitualResponse) -> TodayScenariosResponse:
    dh = m.daily_horoscope if isinstance(m.daily_horoscope, dict) else {}
    scenarios = dh.get("scenarios") if isinstance(dh.get("scenarios"), list) else []
    return TodayScenariosResponse(
        date=m.date,
        headline=dh.get("headline"),
        profile_prism=dh.get("profile_prism"),
        scenarios=scenarios,
        daily_horoscope_generation_log_id=m.daily_horoscope_generation_log_id,
    )


_MORNING_RITUAL_CACHE: dict[tuple[int, str, str], tuple[float, MorningRitualResponse]] = {}
_MORNING_CACHE_TTL = 6 * 60 * 60.0  # same calendar morning: reuse until evening
_MAX_MORNING_CACHE_ENTRIES = 320


async def _fetch_morning_ritual_fast(
    *,
    request: Request,
    target_date: str,
    user: User,
    db,
    numerology_service: NumerologyService,
    core_profile_service: CoreProfileService,
    orchestrator: InterpretationOrchestrator,
) -> MorningRitualResponse:
    transit_service = await get_personal_transit_service()
    astro_service = astro.AstroService()
    geocoder = Geocoder()
    try:
        return await get_morning_ritual(
            request=request,
            target_date=target_date,
            fast_mode=True,
            user=user,
            db=db,
            numerology_service=numerology_service,
            transit_service=transit_service,
            astro_service=astro_service,
            geocoder=geocoder,
            core_profile_service=core_profile_service,
            orchestrator=orchestrator,
        )
    finally:
        await astro_service.close()


async def get_morning_ritual_cached(
    *,
    request: Request,
    target_date: str,
    user: User,
    db,
    numerology_service: NumerologyService,
    core_profile_service: CoreProfileService,
    orchestrator: InterpretationOrchestrator,
) -> MorningRitualResponse:
    """Короткий TTL-кеш на (user, date, locale), чтобы /core + /scenarios и bundle не дублировали тяжёлую сборку."""
    loc = request_locale(request)
    key = (user.id, target_date, loc)
    wall = time.time()
    hit = _MORNING_RITUAL_CACHE.get(key)
    if hit and wall - hit[0] < _MORNING_CACHE_TTL:
        return hit[1]
    m = await _fetch_morning_ritual_fast(
        request=request,
        target_date=target_date,
        user=user,
        db=db,
        numerology_service=numerology_service,
        core_profile_service=core_profile_service,
        orchestrator=orchestrator,
    )
    _MORNING_RITUAL_CACHE[key] = (wall, m)
    if len(_MORNING_RITUAL_CACHE) > _MAX_MORNING_CACHE_ENTRIES:
        for stale_key, _ in sorted(_MORNING_RITUAL_CACHE.items(), key=lambda kv: kv[1][0])[
            : _MAX_MORNING_CACHE_ENTRIES // 2
        ]:
            _MORNING_RITUAL_CACHE.pop(stale_key, None)
    return m


def invalidate_morning_cache_for_user(user_id: int) -> None:
    """Сброс кеша morning-ritual при изменении связки дня / цели (см. day-connection)."""
    for k in list(_MORNING_RITUAL_CACHE.keys()):
        if k[0] == user_id:
            _MORNING_RITUAL_CACHE.pop(k, None)


@router.get("/opening", response_model=TodayOpeningResponse)
def get_today_opening(
    target_date: Optional[str] = None,
    user: User = Depends(require_user),
    db=Depends(get_session),
) -> TodayOpeningResponse:
    """
    Быстрый первый запрос для мобильного first paint: только DayConnection и логика доступности этапов.
    Полный контент дня — через GET /today или GET /morning-ritual/today.
    """
    if not target_date:
        target_date = date.today().isoformat()
    target_date_obj = parse_iso_date_or_400(target_date)
    today_date = date.today()

    day_connection_data: Optional[DayConnectionResponse] = None
    try:
        day_connection_data = get_day_connection(
            target_date=target_date,
            user=user,
            db=db,
        )
    except Exception as e:
        logger.warning("Failed to get day connection in /today/opening: %s", e, exc_info=True)

    morning_completed = day_connection_data.morning_completed if day_connection_data else False
    day_completed = day_connection_data.day_completed if day_connection_data else False
    evening_completed = day_connection_data.evening_completed if day_connection_data else False
    morning_available = True
    day_available = morning_completed or target_date_obj < today_date
    current_hour = datetime.now().hour
    evening_available = (day_completed or target_date_obj < today_date) or (
        target_date_obj == today_date and current_hour >= 18
    )

    return TodayOpeningResponse(
        date=target_date,
        day_connection=day_connection_data,
        morning_completed=morning_completed,
        day_completed=day_completed,
        evening_completed=evening_completed,
        morning_available=morning_available,
        day_available=day_available,
        evening_available=evening_available,
    )


@router.get("/checkin-prompt", response_model=TodayCheckinPromptResponse)
def get_today_checkin_prompt(
    request: Request,
    target_date: Optional[str] = None,
    user: User = Depends(require_user),
    db=Depends(get_session),
) -> TodayCheckinPromptResponse:
    """
    Следующий микро-чекин по сохранённой связке дня (без вызова morning-ritual / LLM).
    """
    if not target_date:
        target_date = date.today().isoformat()
    target_date_obj = parse_iso_date_or_400(target_date)
    today_date = date.today()
    hour = datetime.now().hour
    locale = request_locale(request)

    dc: Optional[DayConnectionResponse] = None
    try:
        dc = get_day_connection(target_date=target_date, user=user, db=db)
    except Exception as e:
        logger.warning("Failed to get day connection in /today/checkin-prompt: %s", e, exc_info=True)

    return _build_checkin_prompt(
        target_date=target_date,
        dc=dc,
        target_date_obj=target_date_obj,
        today_date=today_date,
        hour=hour,
        locale=locale,
    )


@router.get("/core", response_model=TodayCoreResponse)
async def get_today_core(
    request: Request,
    target_date: Optional[str] = None,
    user: User = Depends(require_user),
    db=Depends(get_session),
    numerology_service: NumerologyService = Depends(get_numerology_service),
    core_profile_service: CoreProfileService = Depends(get_core_profile_service),
    orchestrator: InterpretationOrchestrator = Depends(get_interpretation_orchestrator),
) -> TodayCoreResponse:
    """
    Основной дневной слой без списка сценариев по сферам (уменьшенный JSON для мобильного шага после opening/check-in).
    """
    if not target_date:
        target_date = date.today().isoformat()
    parse_iso_date_or_400(target_date)
    m = await get_morning_ritual_cached(
        request=request,
        target_date=target_date,
        user=user,
        db=db,
        numerology_service=numerology_service,
        core_profile_service=core_profile_service,
        orchestrator=orchestrator,
    )
    return _morning_to_core_response(m)


@router.get("/bundle", response_model=TodayProgressiveBundleResponse)
async def get_today_progressive_bundle(
    request: Request,
    target_date: Optional[str] = None,
    user: User = Depends(require_user),
    db=Depends(get_session),
    numerology_service: NumerologyService = Depends(get_numerology_service),
    core_profile_service: CoreProfileService = Depends(get_core_profile_service),
    orchestrator: InterpretationOrchestrator = Depends(get_interpretation_orchestrator),
) -> TodayProgressiveBundleResponse:
    """Один запрос: стержень дня + сценарии (одна сборка morning-ritual с кешем)."""
    if not target_date:
        target_date = date.today().isoformat()
    parse_iso_date_or_400(target_date)
    m = await get_morning_ritual_cached(
        request=request,
        target_date=target_date,
        user=user,
        db=db,
        numerology_service=numerology_service,
        core_profile_service=core_profile_service,
        orchestrator=orchestrator,
    )
    return TodayProgressiveBundleResponse(
        date=m.date,
        core=_morning_to_core_response(m),
        scenarios=_morning_to_scenarios_response(m),
    )


@router.get("/scenarios", response_model=TodayScenariosResponse)
async def get_today_scenarios(
    request: Request,
    target_date: Optional[str] = None,
    user: User = Depends(require_user),
    db=Depends(get_session),
    numerology_service: NumerologyService = Depends(get_numerology_service),
    core_profile_service: CoreProfileService = Depends(get_core_profile_service),
    orchestrator: InterpretationOrchestrator = Depends(get_interpretation_orchestrator),
) -> TodayScenariosResponse:
    """Сценарии дня по сферам; типично второй запрос после /today/core (кеш generation обычно уже тёплый)."""
    if not target_date:
        target_date = date.today().isoformat()
    parse_iso_date_or_400(target_date)
    m = await get_morning_ritual_cached(
        request=request,
        target_date=target_date,
        user=user,
        db=db,
        numerology_service=numerology_service,
        core_profile_service=core_profile_service,
        orchestrator=orchestrator,
    )
    return _morning_to_scenarios_response(m)


@router.get("/state-map", response_model=FusionIndexResponse)
def get_today_state_map(
    target_date: Optional[str] = None,
    user: User = Depends(require_user),
    db=Depends(get_session),
) -> FusionIndexResponse:
    """Алиас к tracking/fusion/{date} под префиксом /today для одного контракта progressive load."""
    if not target_date:
        target_date = date.today().isoformat()
    parse_iso_date_or_400(target_date)
    return get_daily_fusion_index(target_date=target_date, current_user=user, db=db)


class RitualContextRequest(BaseModel):
    """Выбор пользователя в утреннем ритуале — для surface=guide пересобирает «Главное» с учётом карты, числа, настроения и фактов дня."""

    tarot_main_id: Optional[int] = Field(None, description="Id карты в колоде Today (рубрика tarot today ru)")
    tarot_name_ru: Optional[str] = Field(None, max_length=160, description="Название карты на русском")
    numerology_value: Optional[str] = Field(None, max_length=24, description="Число дня / выбранная цифра")
    mood: Optional[str] = Field(None, max_length=80, description="id настроения из чек-ина ритуала")
    head_topic: Optional[str] = Field(
        None,
        max_length=120,
        description="Тема «в голове» после ритуала — в intent и DayContext; можно передавать с любым surface",
    )
    day_events: list[str] = Field(default_factory=list, description="Короткие строки: фокус, трекеры, дневник и т.п.")

    @field_validator("day_events", mode="before")
    @classmethod
    def _cap_day_events(cls, v: Any) -> list[str]:
        if not isinstance(v, list):
            return []
        out: list[str] = []
        for x in v[:30]:
            s = str(x).strip()
            if s:
                out.append(s[:240])
        return out


class TodayNarrativeRequest(BaseModel):
    """Запрос связных текстов для вкладок «Сегодня». parent_generation_id — id ответа предыдущего вызова (обычно guide)."""

    target_date: Optional[str] = None
    surface: str = Field("guide", description="guide | day_layer | spheres | evening | deepen")
    parent_generation_id: Optional[int] = Field(None, description="Связь с прошлым ответом today/narrative для контекста")
    deepen_topic: Optional[str] = Field(
        None,
        description=(
            "Для surface=deepen: money | intimacy | love | career | family | full_day. "
            "Генерация extra-слоя — Trial/Paid; Free получает CTA (base day не режется)."
        ),
    )
    depth_level: Optional[str] = Field(
        default=None,
        description="DE-8: quick | normal | deep. Не передавай поле — возьмётся из настроек аккаунта (`today_narrative_depth_level`).",
    )
    policy_version: Optional[str] = Field("clean-info-v1", description="Версия контент-политики")
    voice_profile: Optional[str] = Field("live-clean-supportive-v1", description="Голос генерации текста")
    ritual_context: Optional[RitualContextRequest] = Field(
        None,
        description="Ритуал «Твой день»: для guide — полный контекст (карта, число, настроение, head_topic, day_events). Для day_layer/spheres/evening/deepen — при необходимости slim (например head_topic) чтобы intent в narrative совпадал с утром.",
    )

    @field_validator("depth_level", mode="before")
    @classmethod
    def _normalize_depth_level_field(cls, v: Any) -> str | None:
        if v is None or v == "":
            return None
        s = str(v).strip().lower()
        if s in ("quick", "normal", "deep"):
            return s
        return None


class TodayNarrativeResponse(BaseModel):
    """Ответ POST /today/narrative. Для ``surface=guide`` в ``payload`` часто есть ``day_engine_brief``, ``day_model`` (``day_model_v0``) и ``narrative_hierarchy`` (O2: ``primary_anchor`` = ``day_engine_brief``); у других surface эти поля не добавляются в ответ, но участвуют во входе LLM."""

    generation_id: int = Field(..., description="Сохраняем для совместимости; равен generation_log_id.")
    generation_log_id: int = Field(
        ...,
        description="ID строки generation_logs; передайте в POST /learning/feedback как generation_log_id.",
    )
    surface: str
    used_fallback: bool
    payload: dict[str, Any]
    profile_selector: dict[str, Any] | None = Field(
        default=None,
        description="Урезанный срез profile_selector (task, topic, generation_rules, …); для эха в POST /learning/feedback.",
    )


class DomainLensContractV1(BaseModel):
    status: str = ""
    opportunity: str = ""
    risk: str = ""
    action: str = ""
    evidence_status: str = "present"


class TodayContractDomainsV1(BaseModel):
    relationships: DomainLensContractV1
    money_work: DomainLensContractV1
    family: DomainLensContractV1


class TodayContractGlobalContextV1(BaseModel):
    period: str


class TodayContractPersonalGrowthV1(BaseModel):
    development_point: str


class TodayContractDayStoryV1(BaseModel):
    model_config = ConfigDict(extra="allow")

    contract_version: str
    theme: str = ""
    direction: str = ""
    story: str = ""
    expect: str = ""
    trap: str = ""
    events_lead: str = ""
    primary_conflict: str = ""
    headline_anchor: str = ""
    day_thesis: dict[str, Any] | None = None
    do: list[str] = Field(default_factory=list)
    avoid: list[str] = Field(default_factory=list)
    advantage: str = ""
    abstain: str = ""
    today_move: str = ""
    vibe_closing: str = ""
    vibe_strokes: list[str] = Field(default_factory=list)
    talisman: dict[str, Any] | None = Field(default_factory=dict)
    practice_recommendation: dict[str, Any] | None = Field(default_factory=dict)
    symbolic_note: str = ""
    supports_story: str = ""
    day_foundation: dict[str, Any] | None = None
    day_personal: dict[str, Any] | None = None
    day_scenario: dict[str, Any] | None = None
    interpretive_chorus: dict[str, Any] | None = None
    editorial: dict[str, Any] | None = None
    interpretation_status: str | None = None
    interpretation_unavailable_message: str | None = None
    domains: dict[str, Any] | None = None
    global_period: str = ""
    development_point: str = ""
    primary_action: str = ""
    evening_closure: str = ""
    trace: dict[str, Any] = Field(default_factory=dict)


class TodayContractDepthLayerV1(BaseModel):
    """Optional subscriber deepen offer — never hides base day."""

    version: str
    can_generate: bool
    access: str = Field(description="available | cta")
    menu: list[dict[str, str]] = Field(default_factory=list)
    subscribe_path: str = "/account/subscriptions"


class TodayContractV1Response(BaseModel):
    """P0.1 — Model B wire contract; legacy Today fields are not exposed."""

    contract_version: str
    global_context: TodayContractGlobalContextV1
    personal_growth: TodayContractPersonalGrowthV1
    domains: TodayContractDomainsV1
    primary_action: str
    progress: dict[str, Any] = Field(default_factory=dict)
    generation_id: str
    day_story: TodayContractDayStoryV1 | None = None
    depth_layer: TodayContractDepthLayerV1 | None = None


def _attach_depth_layer_offer(contract: dict[str, Any], *, user: User, db, locale: str) -> dict[str, Any]:
    """Additive Today Depth Layer offer (canon TODAY_DEPTH_LAYER_V1)."""
    from todayflow_backend.services.today_depth_layer_v1 import (
        DEPTH_LAYER_VERSION,
        build_depth_layer_menu,
        can_generate_depth_layer,
    )

    can = can_generate_depth_layer(user, db)
    out = dict(contract) if isinstance(contract, dict) else {}
    out["depth_layer"] = {
        "version": DEPTH_LAYER_VERSION,
        "can_generate": can,
        "access": "available" if can else "cta",
        "menu": build_depth_layer_menu(locale=locale),
        "subscribe_path": "/account/subscriptions",
    }
    return out


@router.get("/contract", response_model=TodayContractV1Response)
async def get_today_contract(
    request: Request,
    target_date: Optional[str] = None,
    timezone: Optional[str] = None,
    user: User = Depends(require_user),
    db=Depends(get_session),
    numerology_service: NumerologyService = Depends(get_numerology_service),
    core_profile_service: CoreProfileService = Depends(get_core_profile_service),
    orchestrator: InterpretationOrchestrator = Depends(get_interpretation_orchestrator),
) -> TodayContractV1Response:
    """
    Единый DTO для экрана Today (Model B): global_context, personal_growth, 3 DomainLens.
    Собирается на сервере из legacy inputs; клиент не должен мержить morning/fusion/narrative.

    C5: before local ready_at on the current local date → day_not_ready shell (no day_story).
    """
    from todayflow_backend.services.day_lifecycle_clock_c5 import (
        DAY_STATUS_NOT_READY,
        build_day_assembling_contract,
        build_day_not_ready_contract,
        compute_day_lifecycle_c5,
        local_now,
        resolve_user_ready_time,
        resolve_user_timezone,
    )

    locale = request_locale(request)
    tz_name = resolve_user_timezone(db, user_id=int(user.id), explicit=timezone)
    ready_time = resolve_user_ready_time(db, user_id=int(user.id))
    if not target_date:
        target_date = local_now(timezone_name=tz_name).date().isoformat()
    target_date_obj = parse_iso_date_or_400(target_date)
    dc_for_lifecycle = (
        db.query(db_models.DayConnection)
        .filter(
            db_models.DayConnection.user_id == user.id,
            db_models.DayConnection.date == target_date_obj,
        )
        .first()
    )
    day_lifecycle = compute_day_lifecycle_c5(
        timezone_name=tz_name,
        ready_time=ready_time,
        target_date=target_date_obj,
        closed=bool(dc_for_lifecycle and dc_for_lifecycle.evening_completed),
    )
    if day_lifecycle.get("status") == DAY_STATUS_NOT_READY:
        shell = build_day_not_ready_contract(lifecycle=day_lifecycle, locale=locale)
        return TodayContractV1Response(**_attach_depth_layer_offer(shell, user=user, db=db, locale=locale))

    morning = await get_morning_ritual_cached(
        request=request,
        target_date=target_date,
        user=user,
        db=db,
        numerology_service=numerology_service,
        core_profile_service=core_profile_service,
        orchestrator=orchestrator,
    )
    fusion = get_daily_fusion_index(target_date=target_date, current_user=user, db=db)
    # Side surface: do not trigger portrait LLM on Today first paint.
    core_profile = core_profile_service.build_cached_or_baseline(db, user)

    fusion_dump = fusion.model_dump()
    try:
        contract, gen_log_id, _ = build_day_story_v1_wire(
            db,
            user=user,
            target_date=target_date_obj,
            locale=locale,
            morning=morning,
            fusion_dump=fusion_dump,
            core_profile=core_profile,
            timezone_name=tz_name,
            allow_rebuild_on_miss=False,
        )
    except ValueError as exc:
        # Assemble-once: never build on user GET — wait for cron / show assembling.
        if "day_story_missing" in str(exc):
            shell = build_day_assembling_contract(lifecycle=day_lifecycle, locale=locale)
            return TodayContractV1Response(
                **_attach_depth_layer_offer(shell, user=user, db=db, locale=locale)
            )
        logger.error("GET /today/contract assembly failed: %s", exc)
        raise HTTPException(status_code=500, detail="today_contract_v1 assembly failed") from exc

    # Attach lifecycle; do not enqueue enrichment from user GET (cron owns assemble).
    try:
        progress = dict(contract.get("progress") or {})
        progress["day_lifecycle"] = day_lifecycle
        contract["progress"] = progress
    except Exception:
        pass
    _ = gen_log_id
    return TodayContractV1Response(
        **_attach_depth_layer_offer(contract, user=user, db=db, locale=locale)
    )


class TodayStoryRefreshPayload(BaseModel):
    local_date: Optional[str] = None
    timezone: str = "UTC"
    force: bool = False


class TodayStoryRefreshResponse(BaseModel):
    rebuilt: bool
    story_status: str
    story_refresh_required: bool
    story_fingerprint: str | None = None
    generation_id: str = ""
    contract: TodayContractV1Response | None = None
    error: str | None = None
    generation_lifecycle: dict[str, Any] | None = None


class TodayGenerationJobResponse(BaseModel):
    job: dict[str, Any]
    contract: TodayContractV1Response | None = None


@router.get("/jobs/{job_id}", response_model=TodayGenerationJobResponse)
def get_today_generation_job(
    job_id: int,
    user: User = Depends(require_user),
    db=Depends(get_session),
) -> TodayGenerationJobResponse:
    from todayflow_backend.db.models import GenerationJob
    from todayflow_backend.services.generation_jobs_v0 import job_to_public

    job = db.query(GenerationJob).filter(GenerationJob.id == job_id).first()
    if job is None or job.module != "today":
        raise HTTPException(status_code=404, detail="job_not_found")
    if job.user_id != user.id:
        raise HTTPException(status_code=403, detail="job_forbidden")
    contract = None
    if job.status == "enriched" and isinstance(job.result_payload, dict):
        raw = job.result_payload.get("contract")
        if isinstance(raw, dict):
            try:
                contract = TodayContractV1Response(**raw)
            except Exception:
                contract = None
    return TodayGenerationJobResponse(job=job_to_public(job), contract=contract)


@router.post("/story/refresh", response_model=TodayStoryRefreshResponse)
async def refresh_today_story(
    request: Request,
    payload: TodayStoryRefreshPayload | None = None,
    user: User = Depends(require_user),
    db=Depends(get_session),
    numerology_service: NumerologyService = Depends(get_numerology_service),
    core_profile_service: CoreProfileService = Depends(get_core_profile_service),
    orchestrator: InterpretationOrchestrator = Depends(get_interpretation_orchestrator),
) -> TodayStoryRefreshResponse:
    """Rebuild day_story when fingerprint is stale. Never called inside symbol reveal."""
    from todayflow_backend.services import day_symbol_state_v1 as day_symbols
    from todayflow_backend.services.day_story_refresh_v1 import refresh_day_story_for_user
    from todayflow_backend.services.day_story_v1 import day_story_to_today_contract_v1
    from todayflow_backend.services.day_story_wire_v1 import build_day_story_record_for_refresh
    from todayflow_backend.services.today_contract_assembler_v1 import validate_today_contract_v1

    body = payload or TodayStoryRefreshPayload()
    locale = request_locale(request)
    day = day_symbols.resolve_local_date(local_date=body.local_date, timezone_name=body.timezone)
    target_date = day.isoformat()

    # Fresh morning payloads (revealed symbols) — bust short process cache for this user/date.
    invalidate_morning_cache_for_user(user.id)
    morning = await get_morning_ritual_cached(
        request=request,
        target_date=target_date,
        user=user,
        db=db,
        numerology_service=numerology_service,
        core_profile_service=core_profile_service,
        orchestrator=orchestrator,
    )
    fusion = get_daily_fusion_index(target_date=target_date, current_user=user, db=db)
    core_profile = core_profile_service.build_cached_or_baseline(db, user)
    fusion_dump = fusion.model_dump()

    def _build(db_sess, **kwargs):
        return build_day_story_record_for_refresh(
            db_sess,
            user=kwargs["user"],
            target_date=kwargs["target_date"],
            locale=kwargs["locale"],
            morning=morning,
            fusion_dump=fusion_dump,
            core_profile=core_profile,
            force_rebuild=kwargs.get("force_rebuild", True),
            expected_fingerprint=kwargs.get("expected_fingerprint"),
            fingerprint_payload=kwargs.get("fingerprint_payload"),
            timezone_name=body.timezone,
        )

    result = refresh_day_story_for_user(
        db,
        user=user,
        local_date=day,
        timezone_name=body.timezone,
        locale=locale,
        build_fn=_build,
        force=bool(body.force),
    )
    story = result.get("story")
    contract_model = None
    if isinstance(story, dict):
        contract = day_story_to_today_contract_v1(
            story,
            generation_id=str(result.get("generation_id") or ""),
            progress={
                "story_status": result.get("story_status"),
                "story_refresh_required": result.get("story_refresh_required"),
                "story_fingerprint": result.get("story_fingerprint"),
            },
        )
        errors = validate_today_contract_v1(contract)
        if not errors:
            contract_model = TodayContractV1Response(**contract)
    return TodayStoryRefreshResponse(
        rebuilt=bool(result.get("rebuilt")),
        story_status=str(result.get("story_status") or "unknown"),
        story_refresh_required=bool(result.get("story_refresh_required")),
        story_fingerprint=result.get("story_fingerprint"),
        generation_id=str(result.get("generation_id") or ""),
        contract=contract_model,
        error=result.get("error"),
    )


@router.post("/narrative", response_model=TodayNarrativeResponse)
def post_today_narrative(
    request: Request,
    body: TodayNarrativeRequest,
    user: User = Depends(require_user),
    db=Depends(get_session),
    core_profile_service: CoreProfileService = Depends(get_core_profile_service),
) -> TodayNarrativeResponse:
    """
    Генерирует (или отдаёт из кэша) тексты для экрана «Сегодня».
    Для surface=guide при настроенном LLM: воронка из трёх узких вызовов (interpretation → core text → satellites);
    при сбое step3 ядро подставляется из ``guide_decision_v0``; при сбое воронки — монолитный guide.
    Цепочка: сначала surface=guide, затем day_layer/spheres/evening с тем же target_date и parent_generation_id=id ответа guide.
    Для углубления темы: surface=deepen, deepen_topic, parent_generation_id от guide.
    **Today Depth Layer:** deepen — опциональный слой поверх полного дня. Free получает soft CTA
    (``payload.depth_layer.access=cta``); Trial/Paid генерирует pack. Base day / day_story не режется.
    Во входном JSON к LLM для day_layer/spheres/evening/deepen передаются ``day_model`` и ``day_engine_brief`` (паритет с guide); в HTTP-ответе они есть только у guide. У guide в ``payload`` также ``narrative_hierarchy`` (O2: ``primary_anchor`` = ``day_engine_brief``).
    Поле ``depth_level`` (quick | normal | deep, DE-8) задаёт объём текста за один вызов. Если **не** передано — используется ``user_settings.today_narrative_depth_level`` (по умолчанию ``normal``). На стороне генерации ``deep`` для пользователей с ``insight_depth_tier=free`` приводится к ``normal`` (гейт DE-8). Не путать с тарифом ``insight_depth_tier``.
    """
    locale = request_locale(request)
    td = body.target_date or date.today().isoformat()
    d0 = parse_iso_date_or_400(td)
    surface = (body.surface or "guide").strip().lower()
    allowed = {"guide", "day_layer", "spheres", "evening", "deepen"}
    if surface not in allowed:
        raise HTTPException(status_code=400, detail=f"surface must be one of {sorted(allowed)}")

    if surface == "deepen":
        from todayflow_backend.services.today_depth_layer_v1 import (
            build_depth_layer_cta_payload,
            can_generate_depth_layer,
            normalize_depth_topic,
        )

        topic_norm = normalize_depth_topic(body.deepen_topic)
        if not can_generate_depth_layer(user, db):
            return TodayNarrativeResponse(
                generation_id=0,
                generation_log_id=0,
                surface="deepen",
                used_fallback=True,
                payload=build_depth_layer_cta_payload(topic_norm, locale=locale),
                profile_selector=None,
            )

    fusion = get_daily_fusion_index(target_date=td, current_user=user, db=db)
    fusion_dump = fusion.model_dump()
    core_profile = core_profile_service.build_cached_or_baseline(db, user)
    insight_tier = get_insight_depth_tier(user, db)
    ritual_dict: dict[str, Any] | None = None
    if body.ritual_context is not None:
        rc = body.ritual_context.model_dump(exclude_none=True)
        rc = {k: v for k, v in rc.items() if v not in (None, "", [])}
        ritual_dict = rc or None
    depth_eff = _effective_narrative_depth_level(db, user, body.depth_level)
    deepen_topic_eff = body.deepen_topic
    if surface == "deepen":
        from todayflow_backend.services.today_depth_layer_v1 import normalize_depth_topic

        deepen_topic_eff = normalize_depth_topic(body.deepen_topic)
    payload, gen_id, used_fb, profile_sel = run_today_narrative_pipeline(
        db,
        user_id=user.id,
        insight_depth_tier=insight_tier,
        target_date=d0,
        locale=locale,
        surface=surface,  # type: ignore[arg-type]
        core_profile=core_profile,
        fusion_dump=fusion_dump,
        parent_generation_id=body.parent_generation_id,
        deepen_topic=deepen_topic_eff,
        policy_version=body.policy_version,
        voice_profile=body.voice_profile,
        ritual_context=ritual_dict,
        depth_level=depth_eff,
    )
    if surface == "deepen" and isinstance(payload, dict):
        from todayflow_backend.services.today_depth_layer_v1 import annotate_depth_layer_payload

        payload = annotate_depth_layer_payload(
            payload, topic=str(deepen_topic_eff or "full_day"), locale=locale
        )
    return TodayNarrativeResponse(
        generation_id=gen_id,
        generation_log_id=gen_id,
        surface=surface,
        used_fallback=used_fb,
        payload=payload,
        profile_selector=profile_sel,
    )


@router.get("/evening", response_model=TodayEveningResponse)
def get_today_evening(
    target_date: Optional[str] = None,
    user: User = Depends(require_user),
    db=Depends(get_session),
) -> TodayEveningResponse:
    """Вечерняя связка и ritual закрытия дня без утреннего payload."""
    if not target_date:
        target_date = date.today().isoformat()
    target_date_obj = parse_iso_date_or_400(target_date)
    today_date = date.today()
    current_hour = datetime.now().hour

    dc: Optional[DayConnectionResponse] = None
    try:
        dc = get_day_connection(target_date=target_date, user=user, db=db)
    except Exception as e:
        logger.warning("Failed to get day connection in /today/evening: %s", e, exc_info=True)

    day_completed = dc.day_completed if dc else False
    evening_available = (day_completed or target_date_obj < today_date) or (
        target_date_obj == today_date and current_hour >= 18
    )

    ritual: Optional[DayRitualResponse] = None
    try:
        ritual = get_day_ritual(date=target_date, current_user=user, db=db)
    except Exception as e:
        logger.warning("Failed to get day ritual in /today/evening: %s", e, exc_info=True)

    evening_completed = bool(dc.evening_completed if dc else False)
    if ritual and ritual.completed:
        evening_completed = True

    return TodayEveningResponse(
        date=target_date,
        evening_available=evening_available,
        evening_completed=evening_completed,
        evening_reflection=dc.evening_reflection if dc else None,
        evening_observations=dc.evening_observations if dc else None,
        connection_thread=dc.connection_thread if dc else None,
        ritual=ritual,
    )


@router.get("", response_model=TodayCycleResponse)
async def get_today_cycle(
    request: Request,
    target_date: Optional[str] = None,
    light: bool = Query(
        False,
        description="If true, skip trackers, journal slice, evening ritual payload, and rewards aggregation for a faster payload (e.g. mobile progressive load).",
    ),
    user: User = Depends(require_user),
    db=Depends(get_session),
    core_profile_service: CoreProfileService = Depends(get_core_profile_service),
    orchestrator: InterpretationOrchestrator = Depends(get_interpretation_orchestrator),
    numerology_service: NumerologyService = Depends(get_numerology_service),
):
    """
    Получить полный цикл дня: утро, день, вечер.
    
    Логика доступности:
    - Утро: всегда доступно
    - День: доступно после завершения утра
    - Вечер: доступно после завершения дня (или вечером автоматически)
    """
    if not target_date:
        target_date = date.today().isoformat()

    target_date_obj = parse_iso_date_or_400(target_date) if isinstance(target_date, str) else target_date
    today_date = date.today()
    
    # Получаем утренний ритуал
    morning_data = None
    morning_completed = False
    try:
        morning_data = await get_morning_ritual_cached(
            request=request,
            target_date=target_date,
            user=user,
            db=db,
            numerology_service=numerology_service,
            core_profile_service=core_profile_service,
            orchestrator=orchestrator,
        )
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Failed to get morning ritual: {e}", exc_info=True)
    
    # Получаем связку дня
    day_connection_data = None
    try:
        day_connection_data = get_day_connection(
            target_date=target_date,
            user=user,
            db=db,
        )
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Failed to get day connection: {e}", exc_info=True)
    
    # Определяем статус утра
    morning_completed = day_connection_data.morning_completed if day_connection_data else False
    
    # Если нет day_connection, но есть morning_data, считаем что утро доступно
    if not day_connection_data and morning_data:
        morning_completed = False
    
    # Получаем трекеры за день
    day_trackers: list = []
    if not light:
        try:
            progress_entries = get_progress_entries(
                from_date=target_date,
                to_date=target_date,
                current_user=user,
                db=db,
            )
            day_trackers = [
                {
                    "id": entry.id,
                    "date": entry.date,
                    "type": "asceticism" if entry.asceticism_id else "affirmation",
                    "activity_id": entry.asceticism_id or entry.affirmation_id,
                    "completed": entry.completed,
                    "state": entry.state,
                    "state_scale": entry.state_scale,
                }
                for entry in progress_entries
            ]
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to get day trackers: {e}", exc_info=True)

    # Получаем записи дневника за день
    day_journal_entries: list = []
    if not light:
        try:
            journal_entries = get_journal_entries(
                entry_type=None,
                limit=10,
                current_user=user,
                db=db,
            )
            # Фильтруем по дате
            day_journal_entries = [
                {
                    "id": entry.id,
                    "type": entry.type,
                    "content": entry.content,
                    "created_at": entry.created_at.isoformat(),
                }
                for entry in journal_entries
                if entry.day and entry.day == target_date_obj
            ]
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to get journal entries: {e}", exc_info=True)
    
    # Определяем статус дня
    day_completed = day_connection_data.day_completed if day_connection_data else False
    
    # Получаем вечерний ритуал
    evening_data = None
    evening_completed = False
    if light:
        evening_completed = day_connection_data.evening_completed if day_connection_data else False
    else:
        try:
            evening_data = get_day_ritual(
                date=target_date,
                current_user=user,
                db=db,
            )
            if evening_data:
                evening_completed = evening_data.completed
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to get evening ritual: {e}", exc_info=True)
    
    # Логика доступности этапов
    morning_available = True  # Утро всегда доступно
    day_available = morning_completed or target_date_obj < today_date  # День доступен после утра или для прошлых дат
    
    # Вечер доступен после 18:00 для сегодня или для прошлых дат
    current_hour = datetime.now().hour
    evening_available = (day_completed or target_date_obj < today_date) or (
        target_date_obj == today_date and current_hour >= 18
    )
    core_profile = None
    try:
        core_profile = core_profile_service.build_cached_or_baseline(db, user)
    except Exception as e:
        logger.warning("Failed to build core profile in /today: %s", e, exc_info=True)

    consistency = None
    try:
        consistency = orchestrator.build_daily_guidance(
            core_profile=core_profile,
            numerology=morning_data.numerology_number if morning_data else None,
            needs=None,
        )
    except Exception as e:
        logger.warning("Failed to build consistency in /today: %s", e, exc_info=True)

    rewards = None
    reward_milestones: list[dict] = []
    if not light:
        try:
            rewards, reward_milestones = _build_rewards_snapshot(
                db=db,
                user=user,
                target_date=target_date_obj,
                core_profile=core_profile or {},
                today_connection=day_connection_data,
                today_trackers=day_trackers,
                today_journal_entries=day_journal_entries,
            )
        except Exception as e:
            logger.warning("Failed to build rewards snapshot in /today: %s", e, exc_info=True)
    
    return TodayCycleResponse(
        date=target_date,
        morning=morning_data,
        morning_completed=morning_completed,
        day_connection=day_connection_data,
        day_trackers=day_trackers,
        day_journal_entries=day_journal_entries,
        day_completed=day_completed,
        evening=evening_data,
        evening_completed=evening_completed,
        morning_available=morning_available,
        day_available=day_available,
        evening_available=evening_available,
        core_profile=core_profile,
        consistency=consistency,
        rewards=rewards,
        reward_milestones=reward_milestones,
    )


def _sync_reward_evolution_peak(db, user_id: int, evolution_index: int) -> int:
    """Обновляет пик индекса роста пользователя и возвращает его для расчёта колец (кольца не гаснут при просадке)."""
    safe = max(0, min(100, int(round(evolution_index))))
    row = db.query(db_models.User).filter(db_models.User.id == user_id).first()
    if row is None:
        return safe
    prev = int(getattr(row, "reward_evolution_index_peak", 0) or 0)
    peak = max(prev, safe)
    if peak > prev:
        row.reward_evolution_index_peak = peak
        db.commit()
    _record_newly_reached_ring_tiers(db, user_id, peak)
    return peak


def _record_newly_reached_ring_tiers(db, user_id: int, peak: int) -> None:
    """Idempotent: insert (user_id, tier_key, reached_at) the first time peak covers a tier."""
    safe_peak = max(0, min(100, int(peak)))
    existing = {
        r.tier_key
        for r in db.query(db_models.RewardRingTierReached.tier_key)
        .filter(db_models.RewardRingTierReached.user_id == user_id)
        .all()
    }
    now = db_models.utc_naive_now()
    inserted = False
    for min_idx, tier_key in REWARD_RING_THRESHOLDS:
        if safe_peak < min_idx or tier_key in existing:
            continue
        db.add(
            db_models.RewardRingTierReached(
                user_id=user_id,
                tier_key=tier_key,
                reached_at=now,
            )
        )
        inserted = True
    if inserted:
        try:
            db.commit()
        except Exception:
            db.rollback()
            # Concurrent insert on unique (user_id, tier_key) — already recorded.


def _build_rewards_snapshot(
    db,
    user: db_models.User,
    target_date: date,
    core_profile: dict,
    today_connection: Optional[DayConnectionResponse],
    today_trackers: list[dict],
    today_journal_entries: list[dict],
) -> tuple[dict, list[dict]]:
    window_days = 180
    start_date = target_date - timedelta(days=window_days - 1)

    # Daily activity backbone across trackers, journals, practices, habits, day connections.
    daily_active_dates: set[date] = set()

    progress_dates = db.query(db_models.ProgressTrackerEntry.date).filter(
        and_(
            db_models.ProgressTrackerEntry.user_id == user.id,
            db_models.ProgressTrackerEntry.date >= start_date,
            db_models.ProgressTrackerEntry.date <= target_date,
            db_models.ProgressTrackerEntry.completed.is_(True),
        )
    ).all()
    for row in progress_dates:
        daily_active_dates.add(row[0])

    habit_dates = db.query(db_models.HabitEntry.date).filter(
        and_(
            db_models.HabitEntry.user_id == user.id,
            db_models.HabitEntry.date >= start_date,
            db_models.HabitEntry.date <= target_date,
            db_models.HabitEntry.completed.is_(True),
        )
    ).all()
    for row in habit_dates:
        daily_active_dates.add(row[0])

    practice_dates = db.query(func.date(db_models.PracticeUsage.completed_at)).filter(
        and_(
            db_models.PracticeUsage.user_id == user.id,
            func.date(db_models.PracticeUsage.completed_at) >= start_date,
            func.date(db_models.PracticeUsage.completed_at) <= target_date,
        )
    ).all()
    for row in practice_dates:
        if row[0]:
            daily_active_dates.add(row[0])

    day_connection_rows = db.query(
        db_models.DayConnection.date,
        db_models.DayConnection.morning_completed,
        db_models.DayConnection.day_completed,
        db_models.DayConnection.evening_completed,
    ).filter(
        and_(
            db_models.DayConnection.user_id == user.id,
            db_models.DayConnection.date >= start_date,
            db_models.DayConnection.date <= target_date,
        )
    ).all()
    for row in day_connection_rows:
        if row[1] or row[2] or row[3]:
            daily_active_dates.add(row[0])

    journal_rows = db.query(
        db_models.JournalEntry.day,
        db_models.JournalEntry.created_at,
    ).filter(
        and_(
            db_models.JournalEntry.user_id == user.id,
            func.date(db_models.JournalEntry.created_at) >= start_date,
            func.date(db_models.JournalEntry.created_at) <= target_date,
        )
    ).all()
    for row in journal_rows:
        journal_date = row[0] or row[1].date()
        if journal_date:
            daily_active_dates.add(journal_date)

    today_practice_completed = db.query(func.count(db_models.PracticeUsage.id)).filter(
        and_(
            db_models.PracticeUsage.user_id == user.id,
            func.date(db_models.PracticeUsage.completed_at) == target_date,
        )
    ).scalar() or 0

    # Ensure today's client-side actions are reflected immediately in rewards.
    if (
        (today_connection and (today_connection.morning_completed or today_connection.day_completed or today_connection.evening_completed))
        or bool(today_trackers)
        or bool(today_journal_entries)
        or today_practice_completed > 0
    ):
        daily_active_dates.add(target_date)

    daily_streak = _calculate_daily_streak(daily_active_dates, target_date)
    weekly_streak = _calculate_weekly_streak(daily_active_dates, target_date)

    # Feature-level streaks.
    max_habit_streak = _max_habit_streak(db, user.id)
    max_ascetic_streak = _max_ascetic_streak(db, user.id)
    tarot_streak = _tarot_streak(db, user.id, target_date)

    meaning_snapshot = build_meaning_progress_snapshot(
        db=db,
        user_id=user.id,
        target_date=target_date,
        window_days=28,
    )
    score_window_start = target_date - timedelta(days=29)
    practice_30 = db.query(func.count(db_models.PracticeUsage.id)).filter(
        and_(
            db_models.PracticeUsage.user_id == user.id,
            func.date(db_models.PracticeUsage.completed_at) >= score_window_start,
            func.date(db_models.PracticeUsage.completed_at) <= target_date,
        )
    ).scalar() or 0
    consistency_bonus = compute_consistency_bonus(daily_streak=daily_streak, active_days_28=meaning_snapshot.active_days)
    evolution_index = build_growth_index_from_rings(
        ring_scores=meaning_snapshot.ring_scores,
        confidence=meaning_snapshot.ring_confidence,
        consistency_bonus=consistency_bonus,
    )

    # Keep legacy 4-chip UI shape, but derive chips from 6-ring model.
    discipline_score = int(round((meaning_snapshot.ring_scores["Body"] + meaning_snapshot.ring_scores["Wealth"]) / 2))
    reflection_score = int(round((meaning_snapshot.ring_scores["Mind"] + meaning_snapshot.ring_scores["Love"] + meaning_snapshot.ring_scores["Purpose"]) / 3))
    energy_score = meaning_snapshot.ring_scores["Energy"]
    mind_score = meaning_snapshot.ring_scores["Mind"]

    reward_peak = _sync_reward_evolution_peak(db, user.id, evolution_index)

    archetype_level = resolve_archetype_level(
        evolution_index=evolution_index,
        confidence=meaning_snapshot.ring_confidence,
        active_days_28=meaning_snapshot.active_days,
    )
    seals = _resolve_seals(
        core_profile=core_profile,
        daily_streak=daily_streak,
        practice_30=practice_30,
        reflection_score=reflection_score,
    )

    rewards = {
        "archetype_seed": (core_profile or {}).get("baseline", {}).get("archetype_seed"),
        "archetype_level": archetype_level,
        "archetype_progress": build_archetype_progress(
            evolution_index=evolution_index,
            confidence=meaning_snapshot.ring_confidence,
            active_days_28=meaning_snapshot.active_days,
        ),
        "reward_rings_earned": compute_reward_rings_earned(reward_peak),
        "streaks": {
            "daily_current": daily_streak,
            "weekly_current": weekly_streak,
            "habit_best": max_habit_streak,
            "ascetic_best": max_ascetic_streak,
            "tarot_current": tarot_streak,
        },
        "scores": {
            "mind": mind_score,
            "energy": energy_score,
            "discipline": discipline_score,
            "reflection": reflection_score,
        },
        "evolution_index": evolution_index,
        "reward_evolution_index_peak": reward_peak,
        "seals": seals,
        "message": _build_rewards_message(archetype_level=archetype_level, daily_streak=daily_streak, evolution_index=evolution_index),
    }
    return rewards, _build_milestones(daily_streak)


def _calculate_daily_streak(active_dates: set[date], target_date: date) -> int:
    streak = 0
    cursor = target_date
    while cursor in active_dates:
        streak += 1
        cursor -= timedelta(days=1)
    return streak


def _calculate_weekly_streak(active_dates: set[date], target_date: date) -> int:
    # Week counts as active if user has at least 3 active days.
    streak = 0
    cursor = target_date
    while True:
        week_start = cursor - timedelta(days=cursor.weekday())
        week_end = week_start + timedelta(days=6)
        active_count = sum(1 for d in active_dates if week_start <= d <= week_end)
        if active_count >= 3:
            streak += 1
            cursor = week_start - timedelta(days=1)
        else:
            break
    return streak


def _max_habit_streak(db, user_id: int) -> int:
    entries = db.query(
        db_models.HabitEntry.habit_id,
        db_models.HabitEntry.date,
    ).filter(
        and_(
            db_models.HabitEntry.user_id == user_id,
            db_models.HabitEntry.completed.is_(True),
        )
    ).order_by(db_models.HabitEntry.habit_id.asc(), db_models.HabitEntry.date.asc()).all()
    if not entries:
        return 0

    best = 0
    current = 0
    prev_habit = None
    prev_date = None
    for habit_id, entry_date in entries:
        if prev_habit != habit_id:
            current = 1
        elif prev_date and entry_date == prev_date + timedelta(days=1):
            current += 1
        else:
            current = 1
        best = max(best, current)
        prev_habit = habit_id
        prev_date = entry_date
    return best


def _max_ascetic_streak(db, user_id: int) -> int:
    row = db.query(func.max(db_models.AsceticContract.streak_days)).filter(
        db_models.AsceticContract.user_id == user_id
    ).scalar()
    return int(row or 0)


def _tarot_streak(db, user_id: int, target_date: date) -> int:
    draw_dates = db.query(db_models.TarotDraw.draw_date).filter(
        and_(
            db_models.TarotDraw.user_id == user_id,
            db_models.TarotDraw.draw_date <= target_date,
        )
    ).order_by(db_models.TarotDraw.draw_date.desc()).all()
    if not draw_dates:
        return 0
    draw_set = {row[0] for row in draw_dates}
    return _calculate_daily_streak(draw_set, target_date)


def _resolve_seals(core_profile: dict, daily_streak: int, practice_30: int, reflection_score: int) -> list[dict]:
    astro = (core_profile or {}).get("astro", {}) or {}
    sun_element = (astro.get("sun_element") or "").lower()
    sun_modality = (astro.get("sun_modality") or "").lower()

    seals: list[dict] = []
    if daily_streak >= 7:
        seals.append({"code": "saturn_seal", "title": "Saturn Seal", "strength": min(100, daily_streak * 3)})
    if practice_30 >= 10:
        seals.append({"code": "mars_seal", "title": "Mars Seal", "strength": min(100, practice_30 * 4)})
    if reflection_score >= 35:
        seals.append({"code": "moon_seal", "title": "Moon Seal", "strength": min(100, reflection_score * 2)})

    if sun_element in {"water", "air"}:
        seals.append({"code": "venus_aura", "title": "Venus Aura", "strength": 62 if daily_streak >= 7 else 45})
    if sun_modality == "fixed":
        seals.append({"code": "stability_ring", "title": "Stability Ring", "strength": 55})

    # Unique by code
    unique: dict[str, dict] = {}
    for seal in seals:
        prev = unique.get(seal["code"])
        if not prev or seal["strength"] > prev["strength"]:
            unique[seal["code"]] = seal
    return list(unique.values())[:4]


def _build_rewards_message(archetype_level: str, daily_streak: int, evolution_index: int) -> str:
    if daily_streak >= 21:
        return f"{archetype_level}: ты удерживаешь стабильный цикл {daily_streak} дней. Поле дисциплины закреплено."
    if daily_streak >= 7:
        return f"{archetype_level}: серия {daily_streak} дней уже формирует устойчивый ритм. Продолжай без перегруза."
    if evolution_index >= 55:
        return f"{archetype_level}: база собрана, теперь ключ к росту — ежедневная фиксация в Today."
    return f"{archetype_level}: собери первые 3 дня подряд, чтобы активировать устойчивый контур."


def _build_milestones(daily_streak: int) -> list[dict]:
    milestones = [
        (7, "Spark"),
        (21, "Flame"),
        (40, "Radiance"),
        (90, "Solar Cycle"),
        (180, "Lunar Master"),
        (365, "Inner Architect"),
    ]
    payload: list[dict] = []
    for days, name in milestones:
        if daily_streak >= days:
            payload.append({"name": name, "target_days": days, "status": "done", "days_left": 0})
        else:
            payload.append({"name": name, "target_days": days, "status": "next", "days_left": days - daily_streak})
    return payload


# --- Wave 2 Phase A: tap_event_v1 + accuracy summary ---

class TodayTapWidgetResponsePayload(BaseModel):
    local_date: str = Field(..., description="User local date YYYY-MM-DD")
    scene_id: str
    prompted_text: str
    response: str = Field(..., description="avoided_trap|fell_into_trap|not_applicable|skipped")
    domain: str | None = Field(default=None, description="work|money|relationships|energy")
    free_text: str | None = None
    day_facts_id: str | None = None
    timezone: str | None = None


class TodayTapEventResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    schema_version: str = "tap_event_v1"
    event_id: str
    user_id: str
    day_facts_id: str
    local_date: str
    scene_id: str
    domain: str
    prompted_text: str
    response: str
    free_text: str | None = None
    responded_at: str | None = None


class AccuracyDomainBucket(BaseModel):
    correct: int = 0
    total: int = 0


class TodayAccuracySummaryResponse(BaseModel):
    schema_version: str = "accuracy_summary_v1"
    window: str
    from_date: str
    to_date: str
    overall: AccuracyDomainBucket
    by_domain: dict[str, AccuracyDomainBucket]


@router.post("/tap-widget/response", response_model=TodayTapEventResponse)
def post_today_tap_widget_response(
    payload: TodayTapWidgetResponsePayload,
    user: User = Depends(require_user),
    db=Depends(get_session),
) -> TodayTapEventResponse:
    """Wave 2 Phase A — record trap accuracy tap (tap_event_v1)."""
    from todayflow_backend.services import today_tap_widget_v1 as tap_svc

    day = parse_iso_date_or_400(payload.local_date)
    try:
        row = tap_svc.upsert_tap_event(
            db,
            user_id=user.id,
            local_date=day,
            scene_id=payload.scene_id,
            prompted_text=payload.prompted_text,
            response=payload.response,
            domain=payload.domain or "work",
            free_text=payload.free_text,
            day_facts_id=payload.day_facts_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return TodayTapEventResponse(**row)


@router.get("/accuracy-summary", response_model=TodayAccuracySummaryResponse)
def get_today_accuracy_summary(
    window: str = Query(default="14d", description="e.g. 14d"),
    user: User = Depends(require_user),
    db=Depends(get_session),
) -> TodayAccuracySummaryResponse:
    """Wave 2 Phase A — personal trap accuracy over a rolling window."""
    from todayflow_backend.services import today_tap_widget_v1 as tap_svc

    raw = (window or "14d").strip().lower()
    days = 14
    if raw.endswith("d") and raw[:-1].isdigit():
        days = int(raw[:-1])
    summary = tap_svc.build_accuracy_summary(db, user_id=user.id, window_days=days)
    by_domain = {
        key: AccuracyDomainBucket(**bucket)
        for key, bucket in (summary.get("by_domain") or {}).items()
    }
    return TodayAccuracySummaryResponse(
        schema_version=summary["schema_version"],
        window=summary["window"],
        from_date=summary["from_date"],
        to_date=summary["to_date"],
        overall=AccuracyDomainBucket(**summary["overall"]),
        by_domain=by_domain,
    )

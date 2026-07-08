"""Compatibility endpoints for comparing astrological profiles."""

from hashlib import sha1
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import date, time

from todayflow_backend.api.auth import get_optional_user, require_user
from todayflow_backend.db.session import get_session
from todayflow_backend.db.models import AstroProfile, CachedCompatibility, Subscription, User
from todayflow_backend.data.astrology import lookup_sign_metadata
from todayflow_backend.services.chinese_horoscope import get_chinese_horoscope_service
from todayflow_backend.services.zoroastrian_horoscope import get_zoroastrian_horoscope_service
from todayflow_backend.services.tibetan_horoscope import get_tibetan_horoscope_service
from todayflow_backend.services import astro
from todayflow_backend.services.astro import AstroService
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
from todayflow_backend.services.mapping import InternalModelMapper
from todayflow_backend.services.interpretation_orchestrator import (
    InterpretationOrchestrator,
    get_interpretation_orchestrator,
)
from todayflow_backend.services.compatibility_editorial import generate_compatibility_editorial
from todayflow_backend.core import models
from todayflow_backend.i18n import request_locale, translate

router = APIRouter(prefix="/compatibility", tags=["compatibility"])
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


class CompatibilityRequest(BaseModel):
    profile_id_1: int
    profile_id_2: int
    relation_mode: str | None = None


class GroupCompatibilityRequest(BaseModel):
    profile_ids: List[int]  # 3+ profile IDs


class CompatibilityResponse(BaseModel):
    profile_1: dict
    profile_2: dict
    compatibility: dict  # Результаты совместимости


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


@router.get("/signs", response_model=SignCompatibilityResponse)
def signs_compatibility(
    from_sign: str = Query(..., alias="from"),
    to_sign: str = Query(..., alias="to"),
    from_gender: Optional[str] = Query(None),
    to_gender: Optional[str] = Query(None),
    include_personalized: bool = Query(True),
    user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_session),
    core_profile_service: CoreProfileService = Depends(get_core_profile_service),
    orchestrator: InterpretationOrchestrator = Depends(get_interpretation_orchestrator),
) -> SignCompatibilityResponse:
    from_meta = lookup_sign_metadata(from_sign)
    to_meta = lookup_sign_metadata(to_sign)
    if not from_meta or not to_meta:
        raise HTTPException(status_code=400, detail="invalid_sign_pair")

    static_payload = _build_static_sign_report(
        from_sign=from_meta["id"],
        to_sign=to_meta["id"],
        from_name=from_meta["name"],
        to_name=to_meta["name"],
        from_element=from_meta.get("element", ""),
        to_element=to_meta.get("element", ""),
        from_modality=from_meta.get("modality", ""),
        to_modality=to_meta.get("modality", ""),
    )
    paid = _is_paid_user(user, db)
    personalized = None

    if include_personalized and user is not None:
        core_profile = core_profile_service.build(db, user)
        consistency = orchestrator.build_daily_guidance(
            core_profile=core_profile,
            numerology=None,
            needs="love",
        )
        user_sun = (core_profile.get("astro") or {}).get("sun_sign")
        personal_focus = _compatibility_personal_focus_phrase(consistency.get("focus"))
        personalized = {
            "profile_ready": core_profile.get("is_ready"),
            "profile_hash": core_profile.get("profile_hash"),
            "headline": f"Через твой обычный ритм этой паре сейчас полезнее опираться на {personal_focus}.",
            "hint": _compatibility_personal_hint(user_sun, to_meta["name"]),
            "focus": personal_focus,
            "do_focus": _compatibility_clean_personal_line(consistency.get("do_focus"), fallback=_quick_sign_strongest_text(static_payload["score"], _element_relation(from_meta.get("element", ""), to_meta.get("element", "")))),
            "avoid_focus": _compatibility_clean_personal_line(consistency.get("avoid_focus"), fallback=_quick_sign_friction_text(static_payload["score"], _rhythm_relation(from_meta.get("modality", ""), to_meta.get("modality", "")))),
        }

    return SignCompatibilityResponse(
        from_sign=from_meta["id"],
        to_sign=to_meta["id"],
        from_sign_name=from_meta["name"],
        to_sign_name=to_meta["name"],
        from_gender=from_gender,
        to_gender=to_gender,
        score=static_payload["score"],
        summary=static_payload["summary"],
        quick_reading=static_payload["quick_reading"],
        free_paragraphs=static_payload["paragraphs"][:3],
        full_paragraphs=static_payload["paragraphs"] if paid else static_payload["paragraphs"][:3],
        is_paid=paid,
        content_id=static_payload["content_id"],
        personalized=personalized,
    )


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

    element_relation = _element_relation(from_element, to_element)
    rhythm_relation = _rhythm_relation(from_modality, to_modality)
    summary = (
        f"{from_name} и {to_name}: {element_relation}, а в повседневном ритме важнее всего {rhythm_relation}."
    )
    strongest = _quick_sign_strongest_text(score, element_relation)
    friction = _quick_sign_friction_text(score, rhythm_relation)
    next_step = _quick_sign_next_step(score)

    paragraphs = [
        f"{from_name} и {to_name} быстрее совпадают там, где не пытаются переделать темп друг друга под себя.",
        f"Сильная сторона пары — {element_relation}. Это обычно чувствуется в первом контакте, общей химии или в том, как легко снова вернуться в диалог.",
        f"Главная зона трения — {rhythm_relation}. Чем яснее вы проговариваете ожидания и скорость решений, тем меньше ненужного напряжения.",
        "Лучше всего эта связка держится на простых договоренностях: что важно, где нужна инициатива и как вы обсуждаете сложное без угадывания.",
        "Если хочется понять пару глубже, следующий уровень уже не про знаки, а про реальные даты, профиль и живой сценарий контакта.",
    ]

    return {
        "content_id": content_id,
        "score": score,
        "summary": summary,
        "quick_reading": {
            "headline": _quick_sign_headline(score),
            "strongest": strongest,
            "friction": friction,
            "next_step": next_step,
            "strengths": [
                strongest,
                "Этой связи помогает прямой разговор без лишних догадок.",
            ],
            "cautions": [
                friction,
                "Не стоит ждать, что совпадение случится само, если темп и ожидания не названы вслух.",
            ],
        },
        "paragraphs": paragraphs,
    }


def _element_relation(from_element: str, to_element: str) -> str:
    if from_element == to_element:
        return "естественное взаимопонимание"
    if {from_element, to_element} == {"fire", "air"}:
        return "быстрая взаимная подпитка"
    if {from_element, to_element} == {"earth", "water"}:
        return "мягкое укрепление и опора"
    if {from_element, to_element} == {"fire", "water"}:
        return "контраст импульса и чувств"
    if {from_element, to_element} == {"earth", "air"}:
        return "конфликт логики и практичности"
    return "переменная синхронизация"


def _rhythm_relation(from_modality: str, to_modality: str) -> str:
    if from_modality == to_modality:
        return "общий рабочий ритм"
    if {from_modality, to_modality} == {"cardinal", "fixed"}:
        return "баланс старта и удержания"
    if {from_modality, to_modality} == {"cardinal", "mutable"}:
        return "быстрая адаптация с риском спешки"
    if {from_modality, to_modality} == {"fixed", "mutable"}:
        return "разница в гибкости и инерции"
    return "нестабильная, но управляемая динамика"


def _quick_sign_headline(score: int) -> str:
    if score >= 82:
        return "Между вами связь возникает быстро и держится легче, чем у большинства пар."
    if score >= 68:
        return "Потенциал хороший, но эта пара раскрывается лучше через настройку, чем сама по себе."
    if score >= 55:
        return "Связь рабочая, если вы не пускаете контакт на самотек и заранее договариваетесь о важном."
    return "Эта пара требует больше бережности, ясности и терпения, чем мгновенного совпадения."


def _quick_sign_strongest_text(score: int, element_relation: str) -> str:
    if score >= 82:
        return f"Лучше всего здесь работает {element_relation}: вам проще поймать общий тон и снова вернуться в контакт."
    if score >= 68:
        return f"Сильная сторона пары — {element_relation}. На этом можно строить доверие, если не терять ясность в общении."
    if score >= 55:
        return f"Опора пары — {element_relation}. Это дает точку, от которой можно выстраивать контакт без лишнего давления."
    return f"Даже в непростом сочетании остается опора — {element_relation}. На нее и стоит опираться, а не на идею мгновенного совпадения."


def _quick_sign_friction_text(score: int, rhythm_relation: str) -> str:
    if score >= 82:
        return f"Трение обычно начинается не в чувствах, а там, где включается {rhythm_relation} и вы перестаете сверяться по темпу."
    if score >= 68:
        return f"Главный риск пары — {rhythm_relation}. Именно здесь проще всего накопить обиду из-за разных ожиданий."
    if score >= 55:
        return f"Слабое место этой связи — {rhythm_relation}. Без проговоренных правил это быстро превращается в качели."
    return f"Главное напряжение здесь дает {rhythm_relation}. Если это не замечать, связь быстрее уходит в упрямство или отстранение."


def _quick_sign_next_step(score: int) -> str:
    if score >= 82:
        return "Не полагайтесь только на легкость. Лучше сразу договориться, как вы держите контакт в обычных бытовых темах."
    if score >= 68:
        return "Следующий шаг здесь — прояснить ожидания и темп: кто быстрее включается, кому нужно больше времени и как вы обсуждаете напряжение."
    if score >= 55:
        return "Лучше заранее обозначить границы и способ разговора о сложном. Именно это делает такую пару устойчивее."
    return "Не форсируйте сближение. Сначала полезнее понять, где вы по-разному входите в контакт и как не ранить друг друга этой разницей."


def _compatibility_personal_focus_phrase(raw_focus: object) -> str:
    value = str(raw_focus or "").strip().lower()
    mapping = {
        "ясный старт и первый шаг": "ясный и спокойный старт",
        "устойчивость через понятный ритм": "устойчивый и предсказуемый ритм",
        "гибкость и мягкая перенастройка": "гибкость без лишней суеты",
        "ритм через базовые микро-шаги": "один понятный ритм",
    }
    return mapping.get(value, str(raw_focus or "").strip() or "ритм общения")


def _compatibility_personal_hint(user_sun: object, target_name: str) -> str:
    sun = str(user_sun or "").strip()
    if sun:
        return f"Твой обычный способ входить в контакт здесь важен не меньше самих знаков: рядом с {target_name} лучше работают спокойный темп и проговорённые ожидания."
    return f"Здесь полезно смотреть не только на пару знаков, но и на то, как ты сам входишь в контакт рядом с {target_name}."


def _compatibility_clean_personal_line(raw_line: object, fallback: str) -> str:
    text = str(raw_line or "").strip()
    if not text:
        return fallback
    cleaned = text.replace("; ", ". ").replace("  ", " ").strip()
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
        return CompatibilityResponse(**cached)
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
    compatibility_results = compatibility_engine.build_quick_payload(
        profile_1=profile_1,
        profile_2=profile_2,
        horoscopes_1=horoscopes_1,
        horoscopes_2=horoscopes_2,
        relation_mode=request.relation_mode,
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
    astro_service: AstroService = Depends(lambda: AstroService()),
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

    response_payload = compatibility_engine.build_deep_payload(
        profile_1=profile_1,
        profile_2=profile_2,
        chart1=chart1,
        chart2=chart2,
        synastry_report=synastry_report,
        relation_mode=request_data.relation_mode,
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
    
    # Сначала проверяем кеш
    from todayflow_backend.services.natal_chart_cache import get_natal_chart_cache_service
    cache_service = get_natal_chart_cache_service(db)
    cached = cache_service.get_cached_natal_chart(profile.id)
    
    if cached and cached.positions:
        # Сервис кеша уже возвращает готовый ChartResponse.
        return cached
    
    # Если нет в кеше, вычисляем
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
        chart_response = await astro_service.compute_chart(birth_payload=birth_payload, coordinates=coordinates)
        return chart_response
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
) -> str:
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
    if record.expires_at <= datetime.utcnow():
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
    expires_at = datetime.utcnow() + timedelta(hours=COMPATIBILITY_CACHE_TTL_HOURS)
    current_memory = _compatibility_memory_from_payload(result_data)
    merged_memory = _merge_compatibility_memory(prior_memory, current_memory)
    stored_payload = _wrap_cached_compatibility_payload(
        payload=result_data,
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
    astro_service: AstroService = Depends(lambda: AstroService()),
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
    astro_service: AstroService = Depends(lambda: AstroService()),
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
    astro_service: AstroService = Depends(lambda: AstroService()),
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
    astro_service: AstroService = Depends(lambda: AstroService()),
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
    astro_service: AstroService = Depends(lambda: AstroService()),
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

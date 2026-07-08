"""Question-first JTBD answer endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from todayflow_backend.api.auth import get_optional_user, require_user
from todayflow_backend.db import models as db_models
from todayflow_backend.db.session import get_session
from todayflow_backend.core import models as core_models
from todayflow_backend.services.core_profile import CoreProfileService, get_core_profile_service
from todayflow_backend.services.question_editorial import (
    build_questions_hub_context,
    build_question_memory_context,
    generate_question_editorial,
)
from todayflow_backend.services.learning import LearningService, get_learning_service
from todayflow_backend.services.questions import JTBD_LANES, QuestionService, get_question_service
from todayflow_backend.services.tarot import TarotService, get_tarot_service
from todayflow_backend.i18n import request_locale

router = APIRouter(prefix="/questions", tags=["questions"])


class QuestionRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=500)
    preferred_lane: str | None = Field(default=None)
    hub_lane_hint: str | None = Field(default=None)


class QuestionAnswerBlock(BaseModel):
    clarity: str
    explanation: str
    forecast: str
    decision: str
    today: str


class SuggestedRoute(BaseModel):
    href: str
    label: str
    reason: str


class QuestionEditorial(BaseModel):
    current_focus: str
    carried_context: str | None = None
    next_step: str


class QuestionMemoryItem(BaseModel):
    question: str
    thesis: str | None = None
    next_step: str | None = None


class QuestionMemoryContext(BaseModel):
    lane: str
    question_signature: str
    repeated_questions_count: int = 0
    history: list[QuestionMemoryItem] = Field(default_factory=list)
    prior_summary: str | None = None
    focus_hint: str | None = None


class QuestionsHubLaneSuggestion(BaseModel):
    lane: str
    count: int
    last_question: str | None = None
    last_thesis: str | None = None
    focus_hint: str | None = None


class QuestionsHubContextResponse(BaseModel):
    preferred_lane: str | None = None
    summary: str
    lane_suggestions: list[QuestionsHubLaneSuggestion] = Field(default_factory=list)


class QuestionAnswerResponse(BaseModel):
    generation_log_id: int | None = None
    question: str
    lane: str
    lane_title: str
    profile_ready: bool
    answer: QuestionAnswerBlock
    suggested_route: SuggestedRoute
    editorial: QuestionEditorial | None = None
    memory_context: QuestionMemoryContext | None = None


class DecisionRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=500)
    option_a: str | None = Field(default=None, max_length=200)
    option_b: str | None = Field(default=None, max_length=200)


class DecisionAnswerBlock(BaseModel):
    window: str
    risk: str
    best_next_step: str
    check_before_deciding: str
    revisit_when: str


class DecisionAnswerResponse(BaseModel):
    generation_log_id: int | None = None
    question: str
    profile_ready: bool
    option_a: str | None = None
    option_b: str | None = None
    answer: DecisionAnswerBlock
    suggested_route: SuggestedRoute
    editorial: QuestionEditorial | None = None
    memory_context: QuestionMemoryContext | None = None


class GuidanceTarotPick(BaseModel):
    card_id: int
    orientation: str = "upright"


class GuidanceReadingRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=500)
    spread_id: str = Field(default="one_card")
    """Same picks as in POST /tarot/spread (after the user has revealed cards client-side)."""
    selected_cards: list[GuidanceTarotPick] = Field(default_factory=list)
    preferred_lane: str | None = Field(default=None)
    hub_lane_hint: str | None = Field(default=None)


class GuidanceTarotCardPreview(BaseModel):
    name: str
    orientation: str
    position: str
    meaning: str


class GuidanceReadingResponse(BaseModel):
    generation_log_id: int | None = None
    question: str
    spread_id: str
    lane: str
    lane_title: str
    profile_ready: bool
    answer: QuestionAnswerBlock
    suggested_route: SuggestedRoute
    editorial: QuestionEditorial | None = None
    memory_context: QuestionMemoryContext | None = None
    tarot_cards: list[GuidanceTarotCardPreview] = Field(default_factory=list)


class QuestionsHistoryItem(BaseModel):
    generation_log_id: int
    created_at: str
    mode: str
    lane: str | None = None
    question: str
    focus: str | None = None
    next_step: str | None = None
    route_label: str | None = None


class QuestionsHistoryResponse(BaseModel):
    history: list[QuestionsHistoryItem]


@router.get("/context", response_model=QuestionsHubContextResponse)
def get_questions_context(
    db: Session = Depends(get_session),
    user=Depends(get_optional_user),
) -> QuestionsHubContextResponse:
    context = build_questions_hub_context(
        db,
        user_id=user.id if user is not None else None,
    )
    return QuestionsHubContextResponse(**context)


def _spread_position_label(position: str | core_models.TarotSpreadPosition | None) -> str:
    if isinstance(position, str):
        return position
    if isinstance(position, core_models.TarotSpreadPosition):
        return position.title
    return "Позиция"


@router.post("/reading", response_model=GuidanceReadingResponse)
def guidance_reading(
    payload: GuidanceReadingRequest,
    request: Request,
    db: Session = Depends(get_session),
    user=Depends(require_user),
    core_profile_service: CoreProfileService = Depends(get_core_profile_service),
    question_service: QuestionService = Depends(get_question_service),
    learning_service: LearningService = Depends(get_learning_service),
    tarot_service: TarotService = Depends(get_tarot_service),
) -> GuidanceReadingResponse:
    locale = request_locale(request)
    question = " ".join(payload.question.split()).strip()
    if len(question) < 3:
        raise HTTPException(status_code=400, detail="Question is too short.")

    spread_id = (payload.spread_id or "one_card").strip() or "one_card"
    if not payload.selected_cards:
        raise HTTPException(
            status_code=400,
            detail="Сначала раздайте расклад и откройте карты — без этого разбор недоступен.",
        )

    selected_models = [
        core_models.TarotSelectedCard(card_id=item.card_id, orientation=item.orientation)
        for item in payload.selected_cards
    ]
    spread = tarot_service.generate_spread(
        spread_id,
        user,
        locale=locale,
        selected_cards=selected_models,
    )

    core_profile = core_profile_service.build(db, user)
    preferred_lane = payload.preferred_lane if payload.preferred_lane in JTBD_LANES else None
    hub_lane_hint = payload.hub_lane_hint if payload.hub_lane_hint in JTBD_LANES else None
    response = question_service.answer(
        question,
        preferred_lane=preferred_lane,
        route_lane_hint=hub_lane_hint,
        core_profile=core_profile,
        locale=locale,
    )

    tarot_cards: list[GuidanceTarotCardPreview] = []
    tarot_signal = ""
    for card in (spread.cards or [])[:3]:
        tarot_cards.append(
            GuidanceTarotCardPreview(
                name=card.card.name,
                orientation=card.orientation,
                position=_spread_position_label(card.position),
                meaning=card.meaning,
            )
        )
    if tarot_cards:
        first = tarot_cards[0]
        tarot_signal = f"Сигнал расклада: «{first.name}» ({first.orientation}) в позиции «{first.position}»."

    if tarot_signal:
        answer_payload = response.get("answer") if isinstance(response.get("answer"), dict) else {}
        explanation = answer_payload.get("explanation")
        today = answer_payload.get("today")
        if isinstance(explanation, str):
            answer_payload["explanation"] = f"{explanation} {tarot_signal}"
        if isinstance(today, str):
            answer_payload["today"] = f"{today} Проверь это на одном конкретном действии в ближайшие часы."
        response["answer"] = answer_payload

    response["memory_context"] = build_question_memory_context(
        db,
        user_id=user.id,
        lane=response["lane"],
        question=question,
    )
    response["editorial"] = generate_question_editorial(
        db,
        user=user,
        lane=response["lane"],
        question=question,
        answer_payload=response,
        memory_context=response["memory_context"],
        locale=locale,
        surface="guidance_reading",
    )
    generation_log = _log_question_generation(
        db=db,
        learning_service=learning_service,
        user=user,
        surface="guidance_reading",
        prompt_kind="guidance_reading",
        input_payload={
            "question": question,
            "preferred_lane": preferred_lane,
            "hub_lane_hint": hub_lane_hint,
            "spread_id": spread_id,
            "selected_cards": [item.model_dump() for item in payload.selected_cards],
            "lane": response["lane"],
        },
        normalized_response={**response, "spread_id": spread_id, "tarot_cards": [c.model_dump() for c in tarot_cards]},
        locale=locale,
    )
    response["generation_log_id"] = generation_log.id if generation_log is not None else None

    return GuidanceReadingResponse(
        **response,
        spread_id=spread_id,
        tarot_cards=tarot_cards,
    )


@router.post("/answer", response_model=QuestionAnswerResponse)
def answer_question(
    payload: QuestionRequest,
    request: Request,
    db: Session = Depends(get_session),
    user=Depends(get_optional_user),
    core_profile_service: CoreProfileService = Depends(get_core_profile_service),
    question_service: QuestionService = Depends(get_question_service),
    learning_service: LearningService = Depends(get_learning_service),
) -> QuestionAnswerResponse:
    locale = request_locale(request)
    question = " ".join(payload.question.split()).strip()
    if len(question) < 3:
        raise HTTPException(status_code=400, detail="Question is too short.")

    core_profile = core_profile_service.build(db, user) if user is not None else None
    preferred_lane = payload.preferred_lane if payload.preferred_lane in JTBD_LANES else None
    hub_lane_hint = payload.hub_lane_hint if payload.hub_lane_hint in JTBD_LANES else None
    response = question_service.answer(
        question,
        preferred_lane=preferred_lane,
        route_lane_hint=hub_lane_hint,
        core_profile=core_profile,
        locale=locale,
    )
    response["memory_context"] = build_question_memory_context(
        db,
        user_id=user.id if user is not None else None,
        lane=response["lane"],
        question=question,
    )
    response["editorial"] = generate_question_editorial(
        db,
        user=user,
        lane=response["lane"],
        question=question,
        answer_payload=response,
        memory_context=response["memory_context"],
        locale=locale,
        surface="questions_answer",
    )
    generation_log = _log_question_generation(
        db=db,
        learning_service=learning_service,
        user=user,
        surface="questions_answer",
        prompt_kind="jtbd_answer",
        input_payload={
            "question": question,
            "preferred_lane": preferred_lane,
            "hub_lane_hint": hub_lane_hint,
            "lane": response["lane"],
        },
        normalized_response=response,
        locale=locale,
    )
    response["generation_log_id"] = generation_log.id if generation_log is not None else None
    return QuestionAnswerResponse(**response)


@router.post("/decision", response_model=DecisionAnswerResponse)
def answer_decision(
    payload: DecisionRequest,
    request: Request,
    db: Session = Depends(get_session),
    user=Depends(get_optional_user),
    core_profile_service: CoreProfileService = Depends(get_core_profile_service),
    question_service: QuestionService = Depends(get_question_service),
    learning_service: LearningService = Depends(get_learning_service),
) -> DecisionAnswerResponse:
    locale = request_locale(request)
    question = " ".join(payload.question.split()).strip()
    if len(question) < 3:
        raise HTTPException(status_code=400, detail="Question is too short.")

    core_profile = core_profile_service.build(db, user) if user is not None else None
    response = question_service.decision_answer(
        question,
        option_a=payload.option_a,
        option_b=payload.option_b,
        core_profile=core_profile,
        locale=locale,
    )
    response["memory_context"] = build_question_memory_context(
        db,
        user_id=user.id if user is not None else None,
        lane="decision",
        question=question,
    )
    response["editorial"] = generate_question_editorial(
        db,
        user=user,
        lane="decision",
        question=question,
        answer_payload=response,
        memory_context=response["memory_context"],
        locale=locale,
        surface="decision_os",
    )
    generation_log = _log_question_generation(
        db=db,
        learning_service=learning_service,
        user=user,
        surface="decision_os",
        prompt_kind="decision_answer",
        input_payload={
            "question": question,
            "option_a": payload.option_a,
            "option_b": payload.option_b,
        },
        normalized_response=response,
        locale=locale,
    )
    response["generation_log_id"] = generation_log.id if generation_log is not None else None
    return DecisionAnswerResponse(**response)


@router.get("/history", response_model=QuestionsHistoryResponse)
def get_questions_history(
    limit: int = Query(30, ge=1, le=100),
    db: Session = Depends(get_session),
    user=Depends(require_user),
) -> QuestionsHistoryResponse:
    rows = (
        db.query(db_models.GenerationLog)
        .filter(
            db_models.GenerationLog.user_id == user.id,
            db_models.GenerationLog.module == "questions",
            db_models.GenerationLog.surface.in_(["questions_answer", "decision_os"]),
            db_models.GenerationLog.status == "success",
        )
        .order_by(db_models.GenerationLog.created_at.desc())
        .limit(limit)
        .all()
    )

    history: list[QuestionsHistoryItem] = []
    for row in rows:
        payload = row.normalized_response if isinstance(row.normalized_response, dict) else {}
        answer_payload = payload.get("answer") if isinstance(payload.get("answer"), dict) else {}
        editorial_payload = payload.get("editorial") if isinstance(payload.get("editorial"), dict) else {}
        route_payload = payload.get("suggested_route") if isinstance(payload.get("suggested_route"), dict) else {}
        mode = "decision" if row.surface == "decision_os" else "question"
        question = payload.get("question")
        if not isinstance(question, str) or not question.strip():
            continue
        focus = editorial_payload.get("current_focus")
        if not isinstance(focus, str):
            focus = answer_payload.get("clarity") if isinstance(answer_payload.get("clarity"), str) else None
        next_step = editorial_payload.get("next_step")
        if not isinstance(next_step, str):
            next_step = answer_payload.get("today") if isinstance(answer_payload.get("today"), str) else None
            if not isinstance(next_step, str):
                next_step = answer_payload.get("best_next_step") if isinstance(answer_payload.get("best_next_step"), str) else None
        lane_value = payload.get("lane")
        lane = lane_value if isinstance(lane_value, str) else None
        route_label_value = route_payload.get("label")
        route_label = route_label_value if isinstance(route_label_value, str) else None

        history.append(
            QuestionsHistoryItem(
                generation_log_id=row.id,
                created_at=row.created_at.isoformat() if row.created_at else "",
                mode=mode,
                lane=lane,
                question=question.strip(),
                focus=focus,
                next_step=next_step,
                route_label=route_label,
            )
        )

    return QuestionsHistoryResponse(history=history)


def _log_question_generation(
    *,
    db: Session,
    learning_service: LearningService,
    user: db_models.User | None,
    surface: str,
    prompt_kind: str,
    input_payload: dict,
    normalized_response: dict,
    locale: str | None,
) -> db_models.GenerationLog | None:
    try:
        prompt = learning_service.get_or_create_prompt_version(
            db,
            module="questions",
            version="v1",
            prompt_kind=prompt_kind,
            prompt_text="Question-first JTBD routing and response assembly.",
            label=f"Questions {prompt_kind}",
            metadata={"surface": surface},
            is_active=True,
        )
        return learning_service.log_generation(
            db,
            module="questions",
            surface=surface,
            user_id=user.id if user is not None else None,
            prompt_version_id=prompt.id,
            model="deterministic-jtbd-router",
            locale=locale,
            input_payload=input_payload,
            normalized_response=normalized_response,
            status="success",
            used_fallback=False,
        )
    except Exception:
        db.rollback()
        return None

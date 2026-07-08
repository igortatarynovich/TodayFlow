"""Question-first JTBD answer endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field, field_validator
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
from todayflow_backend.services.guidance_spread_engine import (
    CLARIFICATION_GOALS,
    assess_guidance_question,
    build_spread_schema,
    clarification_goal_label,
    compose_guidance_clarification,
    compose_guidance_reading,
    structural_spread_analysis,
)
from todayflow_backend.services.guidance_flow_bridge import build_guidance_flow_bridge
from todayflow_backend.services.generation_orchestrator import (
    run_guidance_answer_pipeline,
    run_guidance_clarification_pipeline,
)
from todayflow_backend.services.guidance_profile_modules import select_guidance_profile_modules
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


class GuidanceFlowBridge(BaseModel):
    """Явный мост в дневной Flow / OS (дополнительно к `suggested_route`)."""

    href: str
    label: str
    reason: str
    kind: str


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


class GuidanceClarifyRequest(BaseModel):
    """Одна уточняющая карта к успешному основному Guidance (`guidance_reading`)."""

    parent_generation_log_id: int = Field(..., ge=1)
    clarification_goal: str = Field(
        ...,
        max_length=48,
        description="blind_spot | next_step | risk | boundary",
    )
    selected_cards: list[GuidanceTarotPick] = Field(
        ...,
        description="Ровно одна карта (расклад one_card).",
    )

    @field_validator("selected_cards")
    @classmethod
    def _exactly_one_card(cls, v: list[GuidanceTarotPick]) -> list[GuidanceTarotPick]:
        if len(v) != 1:
            raise ValueError("Передай ровно одну карту для уточнения.")
        return v


class GuidanceReadingRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=500)
    spread_id: str = Field(default="one_card", description="Идентификатор расклада, как в POST /tarot/spread.")
    selected_cards: list[GuidanceTarotPick] = Field(
        default_factory=list,
        description="Карты и ориентации по позициям после открытия на клиенте.",
    )
    preferred_lane: str | None = Field(default=None)
    hub_lane_hint: str | None = Field(default=None)
    topic: str | None = Field(default=None, max_length=48)
    desired_outcome: str | None = Field(default=None, max_length=48)
    relationship_context: str | None = Field(default=None, max_length=48)
    intimacy_focus: str | None = Field(default=None, max_length=48)
    user_intent: str | None = Field(
        default=None,
        max_length=48,
        description="Цель расклада (spread session intent); см. guidance_spread_engine.GUIDANCE_SPREAD_GOALS.",
    )
    requested_depth: str | None = Field(
        default=None,
        max_length=16,
        description="quick | normal | deep — влияет на длину формулировок.",
    )
    today_context_summary: str | None = Field(
        default=None,
        max_length=400,
        description="Короткий контекст дня с клиента (Today), если вопрос задан оттуда.",
    )


class GuidanceTarotCardPreview(BaseModel):
    name: str
    orientation: str
    position: str
    position_id: str | None = None
    position_prompt: str | None = None
    meaning: str
    card_id: int
    keywords: list[str] = Field(default_factory=list)


class GuidanceQuestionAssessmentFlags(BaseModel):
    too_general: bool = False
    fortune_telling_tone: bool = False
    low_actionability: bool = False
    possible_repeat: bool = False


class GuidanceQuestionAssessment(BaseModel):
    flags: GuidanceQuestionAssessmentFlags
    suggestion: str | None = None
    weak_reading_warning: str | None = None


class GuidanceSpreadSchemaPosition(BaseModel):
    id: str
    title: str
    prompt: str | None = None
    weight: float


class GuidanceSpreadSchema(BaseModel):
    spread_id: str
    spread_title: str
    positions: list[GuidanceSpreadSchemaPosition]


class GuidanceSpreadStructuralAnalysis(BaseModel):
    dominant_position_id: str | None = None
    dominant_card_name: str | None = None
    tension_position_id: str | None = None
    support_position_id: str | None = None
    conflict_note: str = ""
    themes: list[str] = Field(default_factory=list)


class GuidanceInterpretationContract(BaseModel):
    summary: str
    core_insight: str
    profile_bridge: str
    action: str
    avoid: str
    continue_hint: str
    why_outline: str
    position_weights_note: str


class GuidanceReadingResponse(BaseModel):
    generation_log_id: int | None = None
    question: str
    spread_id: str
    lane: str
    lane_title: str
    profile_ready: bool
    answer: QuestionAnswerBlock
    suggested_route: SuggestedRoute
    flow_bridge: GuidanceFlowBridge | None = None
    editorial: QuestionEditorial | None = None
    memory_context: QuestionMemoryContext | None = None
    tarot_cards: list[GuidanceTarotCardPreview] = Field(default_factory=list)
    spread_schema: GuidanceSpreadSchema | None = None
    question_assessment: GuidanceQuestionAssessment | None = None
    spread_analysis: GuidanceSpreadStructuralAnalysis | None = None
    interpretation: GuidanceInterpretationContract | None = None
    is_clarification: bool = False
    clarification_parent_log_id: int | None = None
    clarification_goal: str | None = None


class QuestionsHistoryItem(BaseModel):
    generation_log_id: int
    created_at: str
    mode: str
    lane: str | None = None
    question: str
    focus: str | None = None
    next_step: str | None = None
    route_label: str | None = None
    surface: str | None = None
    spread_id: str | None = None
    topic: str | None = None
    lead_card_name: str | None = None
    lead_card_orientation: str | None = None


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


def _guidance_context_suffix(payload: GuidanceReadingRequest) -> str:
    parts: list[str] = []
    if payload.topic and payload.topic.strip():
        parts.append(f"Тема: {payload.topic.strip()}")
    if payload.desired_outcome and payload.desired_outcome.strip():
        parts.append(f"Что хочу получить от расклада: {payload.desired_outcome.strip()}")
    if payload.relationship_context and payload.relationship_context.strip():
        parts.append(f"Кто этот человек: {payload.relationship_context.strip()}")
    if payload.intimacy_focus and payload.intimacy_focus.strip():
        parts.append(f"Фокус близости: {payload.intimacy_focus.strip()}")
    if payload.user_intent and payload.user_intent.strip():
        parts.append(f"Цель расклада (intent): {payload.user_intent.strip()}")
    if payload.today_context_summary and payload.today_context_summary.strip():
        parts.append(f"Контекст Today: {payload.today_context_summary.strip()}")
    if not parts:
        return ""
    return "\n".join(parts)


def _learning_context_from_core_profile(core_profile: dict | None) -> dict:
    if not core_profile:
        return {}
    living = core_profile.get("living") if isinstance(core_profile.get("living"), dict) else {}
    learning = living.get("learning_context") if isinstance(living, dict) else {}
    return learning if isinstance(learning, dict) else {}


def _guidance_clarification_exists_for_parent(db: Session, *, user_id: int, parent_log_id: int) -> bool:
    rows = (
        db.query(db_models.GenerationLog)
        .filter(
            db_models.GenerationLog.user_id == user_id,
            db_models.GenerationLog.module == "questions",
            db_models.GenerationLog.surface == "guidance_clarify",
            db_models.GenerationLog.status == "success",
        )
        .all()
    )
    for row in rows:
        inp = row.input_payload if isinstance(row.input_payload, dict) else {}
        if inp.get("parent_generation_log_id") == parent_log_id:
            return True
    return False


def _question_with_guidance_context(question: str, payload: GuidanceReadingRequest) -> str:
    suffix = _guidance_context_suffix(payload)
    if not suffix:
        return question
    return f"{question}\n\n{suffix}"


@router.post("/reading/clarify", response_model=GuidanceReadingResponse)
def guidance_reading_clarify(
    payload: GuidanceClarifyRequest,
    request: Request,
    db: Session = Depends(get_session),
    user=Depends(require_user),
    core_profile_service: CoreProfileService = Depends(get_core_profile_service),
    question_service: QuestionService = Depends(get_question_service),
    learning_service: LearningService = Depends(get_learning_service),
    tarot_service: TarotService = Depends(get_tarot_service),
) -> GuidanceReadingResponse:
    """Ровно одна уточняющая карта на успешный основной `guidance_reading` (проверка по generation_logs)."""
    locale = request_locale(request)
    goal_raw = (payload.clarification_goal or "").strip().lower()
    if goal_raw not in CLARIFICATION_GOALS:
        raise HTTPException(
            status_code=400,
            detail=f"clarification_goal должен быть одним из: {', '.join(sorted(CLARIFICATION_GOALS))}.",
        )

    parent = (
        db.query(db_models.GenerationLog)
        .filter(
            db_models.GenerationLog.id == payload.parent_generation_log_id,
            db_models.GenerationLog.user_id == user.id,
            db_models.GenerationLog.module == "questions",
            db_models.GenerationLog.surface == "guidance_reading",
            db_models.GenerationLog.status == "success",
        )
        .first()
    )
    if parent is None:
        raise HTTPException(
            status_code=404,
            detail="Основной разбор Guidance не найден или недоступен.",
        )
    if _guidance_clarification_exists_for_parent(db, user_id=user.id, parent_log_id=parent.id):
        raise HTTPException(
            status_code=409,
            detail="Уточняющая карта к этому разбору уже была — повторно нельзя.",
        )

    parent_norm = parent.normalized_response if isinstance(parent.normalized_response, dict) else {}
    parent_inp = parent.input_payload if isinstance(parent.input_payload, dict) else {}
    parent_question = parent_norm.get("question")
    if not isinstance(parent_question, str) or len(parent_question.strip()) < 3:
        parent_question = parent_inp.get("question")
    if not isinstance(parent_question, str) or len(parent_question.strip()) < 3:
        raise HTTPException(status_code=400, detail="В основном разборе нет текста вопроса.")
    parent_question = " ".join(parent_question.split()).strip()

    lane_val = parent_norm.get("lane")
    lane = lane_val if isinstance(lane_val, str) and lane_val in JTBD_LANES else question_service.classify(parent_question)

    parent_summary = ""
    interp = parent_norm.get("interpretation") if isinstance(parent_norm.get("interpretation"), dict) else {}
    if isinstance(interp.get("summary"), str) and interp["summary"].strip():
        parent_summary = interp["summary"].strip()
    if not parent_summary:
        ans = parent_norm.get("answer") if isinstance(parent_norm.get("answer"), dict) else {}
        if isinstance(ans.get("clarity"), str) and ans["clarity"].strip():
            parent_summary = ans["clarity"].strip()

    topic_val = parent_inp.get("topic")
    topic_str = topic_val.strip() if isinstance(topic_val, str) and topic_val.strip() else None

    glabel = clarification_goal_label(goal_raw, locale=locale)
    if (locale or "").startswith("en"):
        clarify_q = f"Clarification focus: {glabel}. Original question: {parent_question}"
    else:
        clarify_q = f"Уточняющая карта: {glabel}. К основному вопросу: {parent_question}"

    spread_id = "one_card"
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
    if len(spread.cards or []) != 1 or len(payload.selected_cards) != 1:
        raise HTTPException(
            status_code=400,
            detail="Уточнение допускает ровно одну карту (расклад one_card).",
        )
    if str(payload.selected_cards[0].card_id) not in tarot_service.card_map:
        raise HTTPException(status_code=400, detail=f"Неизвестный card_id: {payload.selected_cards[0].card_id}.")

    core_profile = core_profile_service.build(db, user)
    hub_lane_hint = lane if lane in JTBD_LANES else None
    response = question_service.answer(
        clarify_q,
        preferred_lane=lane if lane in JTBD_LANES else None,
        route_lane_hint=hub_lane_hint,
        core_profile=core_profile,
        locale=locale,
    )
    response["question"] = clarify_q

    route_payload = parent_norm.get("suggested_route") if isinstance(parent_norm.get("suggested_route"), dict) else {}
    if (
        isinstance(route_payload.get("href"), str)
        and route_payload["href"].strip()
        and isinstance(route_payload.get("label"), str)
        and route_payload["label"].strip()
    ):
        response["suggested_route"] = {
            "href": route_payload["href"].strip(),
            "label": route_payload["label"].strip(),
            "reason": route_payload.get("reason") if isinstance(route_payload.get("reason"), str) else "",
        }

    tarot_cards: list[GuidanceTarotCardPreview] = []
    for card in spread.cards or []:
        pos = card.position
        pos_prompt = pos.prompt if isinstance(pos, core_models.TarotSpreadPosition) else None
        tarot_cards.append(
            GuidanceTarotCardPreview(
                name=card.card.name,
                orientation=card.orientation,
                position=_spread_position_label(pos),
                position_id=pos.id if isinstance(pos, core_models.TarotSpreadPosition) else None,
                position_prompt=pos_prompt,
                meaning=card.meaning,
                card_id=card.card.id,
                keywords=list(card.card.keywords or []),
            )
        )

    spread_schema_raw = build_spread_schema(spread.spread_id, spread.title, list(spread.cards or []))
    spread_schema = GuidanceSpreadSchema(
        spread_id=spread_schema_raw["spread_id"],
        spread_title=spread_schema_raw["spread_title"],
        positions=[GuidanceSpreadSchemaPosition(**p) for p in spread_schema_raw["positions"]],
    )
    structural_raw = structural_spread_analysis(list(spread.cards or []), locale=locale)
    spread_analysis = GuidanceSpreadStructuralAnalysis(**structural_raw)

    modular_profile = select_guidance_profile_modules(
        core_profile,
        topic=topic_str,
        lane=lane,
        user_intent=None,
    )
    _template_ans = {k: str(v) for k, v in (response.get("answer") or {}).items() if k in {"clarity", "explanation", "forecast", "decision", "today"}}
    _refined_c = run_guidance_clarification_pipeline(
        parent_question=parent_question,
        clarification_goal=goal_raw,
        goal_label=glabel,
        template_answer=_template_ans,
        modular_profile=modular_profile,
        cards=list(spread.cards or []),
        parent_summary=parent_summary or parent_question,
        locale=locale,
        learning_service=learning_service,
        db=db,
        user_id=user.id,
    )
    if _refined_c:
        response["answer"] = _refined_c

    base_answer = response.get("answer") if isinstance(response.get("answer"), dict) else {}
    base_answer = {k: str(v) for k, v in base_answer.items() if k in {"clarity", "explanation", "forecast", "decision", "today"}}

    remapped, interpretation_raw = compose_guidance_clarification(
        parent_question=parent_question,
        parent_summary=parent_summary or parent_question,
        clarification_goal=goal_raw,
        spread_title=spread.title,
        cards=list(spread.cards or []),
        lane=lane,
        base_answer=base_answer,
        core_profile=core_profile,
        topic=topic_str,
        learning_context=_learning_context_from_core_profile(core_profile),
        locale=locale,
    )
    response["answer"] = remapped

    assessment_raw = {
        "flags": {
            "too_general": False,
            "fortune_telling_tone": False,
            "low_actionability": False,
            "possible_repeat": False,
        },
        "suggestion": None,
        "weak_reading_warning": None,
    }
    question_assessment = GuidanceQuestionAssessment(
        flags=GuidanceQuestionAssessmentFlags(**assessment_raw["flags"]),
        suggestion=assessment_raw.get("suggestion"),
        weak_reading_warning=assessment_raw.get("weak_reading_warning"),
    )

    response["memory_context"] = build_question_memory_context(
        db,
        user_id=user.id,
        lane=lane,
        question=parent_question,
    )
    _fb_clarify = build_guidance_flow_bridge(lane=lane, topic=topic_str, locale=locale)
    _flow_bridge_clarify = GuidanceFlowBridge(**_fb_clarify) if _fb_clarify else None
    response["editorial"] = generate_question_editorial(
        db,
        user=user,
        lane=lane,
        question=clarify_q,
        answer_payload={
            **response,
            "tarot_cards": [c.model_dump() for c in tarot_cards],
            "spread_analysis": spread_analysis.model_dump(),
        },
        memory_context=response["memory_context"],
        locale=locale,
        surface="guidance_clarify",
    )
    generation_log = _log_question_generation(
        db=db,
        learning_service=learning_service,
        user=user,
        surface="guidance_clarify",
        prompt_kind="guidance_clarify",
        input_payload={
            "parent_generation_log_id": parent.id,
            "clarification_goal": goal_raw,
            "parent_question": parent_question,
            "spread_id": spread_id,
            "selected_cards": [item.model_dump() for item in payload.selected_cards],
            "lane": lane,
        },
        normalized_response={
            **response,
            "spread_id": spread_id,
            "tarot_cards": [c.model_dump() for c in tarot_cards],
            "spread_schema": spread_schema.model_dump(),
            "question_assessment": question_assessment.model_dump(),
            "spread_analysis": spread_analysis.model_dump(),
            "interpretation": interpretation_raw,
            "is_clarification": True,
            "clarification_parent_log_id": parent.id,
            "clarification_goal": goal_raw,
            "flow_bridge": _fb_clarify,
        },
        locale=locale,
    )
    response["generation_log_id"] = generation_log.id if generation_log is not None else None

    interpretation = GuidanceInterpretationContract(**interpretation_raw)

    return GuidanceReadingResponse(
        **response,
        spread_id=spread_id,
        tarot_cards=tarot_cards,
        spread_schema=spread_schema,
        question_assessment=question_assessment,
        spread_analysis=spread_analysis,
        interpretation=interpretation,
        is_clarification=True,
        clarification_parent_log_id=parent.id,
        clarification_goal=goal_raw,
        flow_bridge=_flow_bridge_clarify,
    )


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

    slot_count = len(spread.cards or [])
    if slot_count == 0:
        raise HTTPException(status_code=400, detail="Расклад не содержит позиций.")
    if len(payload.selected_cards) != slot_count:
        raise HTTPException(
            status_code=400,
            detail=f"Для Guidance нужно передать ровно {slot_count} карт с ориентациями (по одной на каждую позицию расклада).",
        )
    for pick in payload.selected_cards:
        if str(pick.card_id) not in tarot_service.card_map:
            raise HTTPException(status_code=400, detail=f"Неизвестный card_id: {pick.card_id}.")

    core_profile = core_profile_service.build(db, user)
    preferred_lane = payload.preferred_lane if payload.preferred_lane in JTBD_LANES else None
    hub_lane_hint = payload.hub_lane_hint if payload.hub_lane_hint in JTBD_LANES else None

    pre_lane = question_service.classify(question)
    memory_for_assessment = build_question_memory_context(
        db,
        user_id=user.id,
        lane=pre_lane,
        question=question,
    )
    assessment_raw = assess_guidance_question(question, memory_context=memory_for_assessment, locale=locale)
    question_assessment = GuidanceQuestionAssessment(
        flags=GuidanceQuestionAssessmentFlags(**assessment_raw["flags"]),
        suggestion=assessment_raw.get("suggestion"),
        weak_reading_warning=assessment_raw.get("weak_reading_warning"),
    )

    question_for_model = _question_with_guidance_context(question, payload)
    response = question_service.answer(
        question_for_model,
        preferred_lane=preferred_lane,
        route_lane_hint=hub_lane_hint,
        core_profile=core_profile,
        locale=locale,
    )
    response["question"] = question

    tarot_cards: list[GuidanceTarotCardPreview] = []
    for card in spread.cards or []:
        pos = card.position
        pos_prompt = pos.prompt if isinstance(pos, core_models.TarotSpreadPosition) else None
        tarot_cards.append(
            GuidanceTarotCardPreview(
                name=card.card.name,
                orientation=card.orientation,
                position=_spread_position_label(pos),
                position_id=pos.id if isinstance(pos, core_models.TarotSpreadPosition) else None,
                position_prompt=pos_prompt,
                meaning=card.meaning,
                card_id=card.card.id,
                keywords=list(card.card.keywords or []),
            )
        )

    spread_schema_raw = build_spread_schema(spread.spread_id, spread.title, list(spread.cards or []))
    spread_schema = GuidanceSpreadSchema(
        spread_id=spread_schema_raw["spread_id"],
        spread_title=spread_schema_raw["spread_title"],
        positions=[GuidanceSpreadSchemaPosition(**p) for p in spread_schema_raw["positions"]],
    )
    structural_raw = structural_spread_analysis(list(spread.cards or []), locale=locale)
    spread_analysis = GuidanceSpreadStructuralAnalysis(**structural_raw)

    modular_profile = select_guidance_profile_modules(
        core_profile,
        topic=payload.topic,
        lane=response["lane"],
        user_intent=payload.user_intent,
    )
    _template_main = {k: str(v) for k, v in (response.get("answer") or {}).items() if k in {"clarity", "explanation", "forecast", "decision", "today"}}
    _refined_main = run_guidance_answer_pipeline(
        question=question,
        lane=response["lane"],
        spread_title=spread.title,
        template_answer=_template_main,
        modular_profile=modular_profile,
        cards=list(spread.cards or []),
        structural=structural_raw,
        question_assessment=assessment_raw,
        today_context=payload.today_context_summary,
        locale=locale,
        learning_service=learning_service,
        db=db,
        user_id=user.id,
    )
    if _refined_main:
        response["answer"] = _refined_main

    _fb_main = build_guidance_flow_bridge(lane=response["lane"], topic=payload.topic, locale=locale)
    _flow_bridge_main = GuidanceFlowBridge(**_fb_main) if _fb_main else None

    base_answer = response.get("answer") if isinstance(response.get("answer"), dict) else {}
    base_answer = {k: str(v) for k, v in base_answer.items() if k in {"clarity", "explanation", "forecast", "decision", "today"}}

    remapped, interpretation_raw = compose_guidance_reading(
        question=question,
        spread_id=spread.spread_id,
        spread_title=spread.title,
        cards=list(spread.cards or []),
        lane=response["lane"],
        base_answer=base_answer,
        core_profile=core_profile,
        topic=payload.topic,
        user_intent=payload.user_intent,
        requested_depth=payload.requested_depth,
        question_assessment=assessment_raw,
        structural=structural_raw,
        learning_context=_learning_context_from_core_profile(core_profile),
        today_context=payload.today_context_summary,
        locale=locale,
    )
    response["answer"] = remapped

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
        answer_payload={
            **response,
            "tarot_cards": [c.model_dump() for c in tarot_cards],
            "spread_analysis": spread_analysis.model_dump(),
        },
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
            "question_model": question_for_model,
            "preferred_lane": preferred_lane,
            "hub_lane_hint": hub_lane_hint,
            "spread_id": spread_id,
            "selected_cards": [item.model_dump() for item in payload.selected_cards],
            "lane": response["lane"],
            "topic": payload.topic,
            "desired_outcome": payload.desired_outcome,
            "relationship_context": payload.relationship_context,
            "intimacy_focus": payload.intimacy_focus,
            "user_intent": payload.user_intent,
            "requested_depth": payload.requested_depth,
            "today_context_summary": payload.today_context_summary,
        },
        normalized_response={
            **response,
            "spread_id": spread_id,
            "tarot_cards": [c.model_dump() for c in tarot_cards],
            "spread_schema": spread_schema.model_dump(),
            "question_assessment": question_assessment.model_dump(),
            "spread_analysis": spread_analysis.model_dump(),
            "interpretation": interpretation_raw,
            "is_clarification": False,
            "clarification_parent_log_id": None,
            "clarification_goal": None,
            "flow_bridge": _fb_main,
        },
        locale=locale,
    )
    response["generation_log_id"] = generation_log.id if generation_log is not None else None

    interpretation = GuidanceInterpretationContract(**interpretation_raw)

    return GuidanceReadingResponse(
        **response,
        spread_id=spread_id,
        tarot_cards=tarot_cards,
        spread_schema=spread_schema,
        question_assessment=question_assessment,
        spread_analysis=spread_analysis,
        interpretation=interpretation,
        is_clarification=False,
        clarification_parent_log_id=None,
        clarification_goal=None,
        flow_bridge=_flow_bridge_main,
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
            db_models.GenerationLog.surface.in_(
                ["questions_answer", "decision_os", "guidance_reading", "guidance_clarify"]
            ),
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
        if row.surface == "decision_os":
            mode = "decision"
        elif row.surface == "guidance_reading":
            mode = "guidance"
        elif row.surface == "guidance_clarify":
            mode = "guidance_clarify"
        else:
            mode = "question"
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

        spread_id_val: str | None = None
        topic_val: str | None = None
        lead_card_name: str | None = None
        lead_card_orientation: str | None = None
        if row.surface in ("guidance_reading", "guidance_clarify"):
            sid = payload.get("spread_id")
            spread_id_val = sid.strip() if isinstance(sid, str) and sid.strip() else None
            inp = row.input_payload if isinstance(row.input_payload, dict) else {}
            top = inp.get("topic")
            topic_val = top.strip() if isinstance(top, str) and top.strip() else None
            cards = payload.get("tarot_cards")
            if isinstance(cards, list) and cards:
                first = cards[0]
                if isinstance(first, dict):
                    name = first.get("name")
                    orient = first.get("orientation")
                    lead_card_name = name.strip() if isinstance(name, str) and name.strip() else None
                    lead_card_orientation = orient.strip() if isinstance(orient, str) and orient.strip() else None

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
                surface=row.surface,
                spread_id=spread_id_val,
                topic=topic_val,
                lead_card_name=lead_card_name,
                lead_card_orientation=lead_card_orientation,
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

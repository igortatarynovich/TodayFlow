"""Compact memory and editorial layer for question surfaces."""

from __future__ import annotations

import json
import logging
import re
from time import perf_counter
from typing import Any

from sqlalchemy.orm import Session

from todayflow_backend.core.config import settings
from todayflow_backend.db import models as db_models
from todayflow_backend.db.models import CoreProfileSnapshot
from todayflow_backend.services.learning import get_learning_service

logger = logging.getLogger(__name__)

PROMPT_VERSION = "questions-editorial-v1"
MODEL_NAME = "gpt-4o-mini"
QUESTION_SURFACES = {"questions_answer", "decision_os"}
MAX_HISTORY_ITEMS = 4
STOP_WORDS = {
    "и", "в", "во", "на", "не", "но", "а", "или", "ли", "что", "как", "я", "мне", "меня", "мой",
    "моя", "мои", "мы", "ты", "он", "она", "они", "это", "этот", "эта", "эти", "по", "про", "с",
    "со", "к", "ко", "от", "из", "за", "у", "о", "об", "для", "уже", "сейчас", "могу", "стоит",
    "нужно", "надо", "бы", "быть", "есть", "лишь", "только",
}
LANE_MEMORY_HINTS: dict[str, dict[str, Any]] = {
    "love": {
        "focus_hint": "Держать в памяти динамику контакта, повтор ожиданий, инициативу и реальные сигналы связи.",
        "keywords": {"отнош", "связ", "контакт", "чувств", "партнер", "люб", "близ", "дистан", "сближ", "игнор", "надежд"},
    },
    "money_career": {
        "focus_hint": "Держать в памяти роль, цену усилий, доход, офферы, рост и рычаг карьерного решения.",
        "keywords": {"работ", "карьер", "доход", "деньг", "оффер", "проект", "роль", "рост", "бизнес", "позицион"},
    },
    "self": {
        "focus_hint": "Держать в памяти устойчивые внутренние паттерны, самоощущение, сильные стороны и свой ритм.",
        "keywords": {"потенц", "мисси", "сильн", "слаб", "путь", "я", "сам", "себ", "личн", "характер"},
    },
    "future": {
        "focus_hint": "Держать в памяти сроки, окно перемен, ожидание поворота периода и вопрос темпа.",
        "keywords": {"когда", "будущ", "период", "скоро", "срок", "начнет", "законч", "переезд", "поворот"},
    },
    "decision": {
        "focus_hint": "Держать в памяти повторяющиеся развилки, цену неопределенности, обратимость и критерий выбора.",
        "keywords": {"решен", "выбор", "вариант", "уйти", "остать", "принять", "рисков", "ошиб", "сравн", "критер"},
    },
    "daily": {
        "focus_hint": "Держать в памяти главный фокус дня, ритм, перегруз второстепенными решениями и проверяемый шаг.",
        "keywords": {"сегодн", "день", "фокус", "ритм", "план", "сделать", "шаг", "вниман"},
    },
    "state": {
        "focus_hint": "Держать в памяти перегруз, тревогу, опору, восстановление и реальную емкость системы.",
        "keywords": {"трев", "устал", "перегруз", "состоя", "сил", "ресурс", "опор", "выгор", "тяжел", "спокой"},
    },
    "pattern": {
        "focus_hint": "Держать в памяти повторяющийся сценарий, триггер, автоматическую реакцию и цену привычного ответа.",
        "keywords": {"паттерн", "повтор", "снова", "одни", "сценар", "триггер", "привыч", "реакц", "токсич"},
    },
}

SYSTEM_PROMPT = """Ты пишешь короткий редакторский слой для раздела вопросов TodayFlow.

Твоя задача:
- не пересказывать весь ответ;
- собрать суть текущего вопроса в одном человеческом фокусе;
- учитывать накопленный контекст прошлых вопросов только тезисно;
- не копировать старые формулировки дословно;
- держать язык ясным, коротким и практичным.

Верни только JSON:
{"current_focus":"...","carried_context":"...","next_step":"..."}"""


def _normalize_question_signature(question: str) -> str:
    normalized = re.sub(r"\s+", " ", (question or "").strip().lower())
    normalized = re.sub(r"[^\w\sа-яё-]", "", normalized, flags=re.IGNORECASE)
    return normalized[:180]


def _tokenize(text: str) -> set[str]:
    normalized = _normalize_question_signature(text)
    tokens = {
        token for token in normalized.split(" ")
        if len(token) > 2 and token not in STOP_WORDS
    }
    return tokens


def _short_text(value: Any, limit: int = 220) -> str | None:
    if not isinstance(value, str):
        return None
    compact = " ".join(value.split()).strip()
    if not compact:
        return None
    return compact[:limit]


def _derive_memory_item(normalized_response: dict[str, Any], fallback_input: dict[str, Any] | None = None) -> dict[str, Any] | None:
    question = _short_text(normalized_response.get("question")) or _short_text((fallback_input or {}).get("question"))
    if not question:
        return None

    answer = normalized_response.get("answer") if isinstance(normalized_response.get("answer"), dict) else {}
    editorial = normalized_response.get("editorial") if isinstance(normalized_response.get("editorial"), dict) else {}
    suggested_route = normalized_response.get("suggested_route") if isinstance(normalized_response.get("suggested_route"), dict) else {}
    lane = _short_text(normalized_response.get("lane")) or _short_text((fallback_input or {}).get("lane")) or "decision"

    thesis = (
        _short_text(editorial.get("current_focus"))
        or _short_text(answer.get("clarity"))
        or _short_text(answer.get("window"))
        or _short_text(answer.get("explanation"))
    )
    next_step = (
        _short_text(editorial.get("next_step"))
        or _short_text(answer.get("today"))
        or _short_text(answer.get("best_next_step"))
        or _short_text(suggested_route.get("reason"))
    )

    return {
        "question": question,
        "question_signature": _normalize_question_signature(question),
        "lane": lane,
        "thesis": thesis,
        "next_step": next_step,
    }


def build_question_memory_context(
    db: Session,
    *,
    user_id: int | None,
    lane: str,
    question: str,
) -> dict[str, Any]:
    signature = _normalize_question_signature(question)
    empty_context = {
        "lane": lane,
        "question_signature": signature,
        "repeated_questions_count": 0,
        "history": [],
        "prior_summary": None,
    }
    if user_id is None:
        empty_context["focus_hint"] = LANE_MEMORY_HINTS.get(lane, {}).get("focus_hint")
        return empty_context

    rows = (
        db.query(db_models.GenerationLog)
        .filter(
            db_models.GenerationLog.user_id == user_id,
            db_models.GenerationLog.module == "questions",
            db_models.GenerationLog.surface.in_(QUESTION_SURFACES),
            db_models.GenerationLog.status == "success",
        )
        .order_by(db_models.GenerationLog.created_at.desc())
        .limit(24)
        .all()
    )

    same_signature = 0
    history_candidates: list[tuple[int, dict[str, Any]]] = []
    seen_signatures: set[str] = set()
    current_tokens = _tokenize(question)
    lane_keywords = set(LANE_MEMORY_HINTS.get(lane, {}).get("keywords") or [])

    for index, row in enumerate(rows):
        normalized_response = row.normalized_response if isinstance(row.normalized_response, dict) else {}
        input_payload = row.input_payload if isinstance(row.input_payload, dict) else {}
        item = _derive_memory_item(normalized_response, input_payload)
        if not item or item["lane"] != lane:
            continue
        item_signature = item.get("question_signature")
        if item_signature == signature:
            same_signature += 1
        if item_signature in seen_signatures:
            continue
        seen_signatures.add(item_signature)
        item_question = str(item.get("question") or "")
        item_thesis = str(item.get("thesis") or "")
        item_tokens = _tokenize(f"{item_question} {item_thesis}")
        overlap_score = len(current_tokens & item_tokens)
        lane_score = sum(1 for keyword in lane_keywords if keyword in item_question.lower() or keyword in item_thesis.lower())
        score = overlap_score * 4 + lane_score * 3 + (3 if item_signature == signature else 0) + (1 if item.get("thesis") else 0)
        score -= index
        history_candidates.append(
            (
                score,
                {
                    "question": item.get("question"),
                    "thesis": item.get("thesis"),
                    "next_step": item.get("next_step"),
                },
            )
        )

    history_candidates.sort(key=lambda entry: entry[0], reverse=True)
    history = [item for _, item in history_candidates[:MAX_HISTORY_ITEMS]]

    prior_summary = None
    if same_signature > 0:
        prior_summary = "Пользователь уже возвращался к почти такому же вопросу, поэтому важно не начать ответ заново, а сдвинуть его к следующей ясности."
    elif history:
        prior_summary = "У пользователя уже есть накопленный контекст по этому типу вопросов, поэтому новый ответ должен продолжать линию, а не звучать как изолированный совет."

    return {
        "lane": lane,
        "question_signature": signature,
        "repeated_questions_count": same_signature,
        "history": history,
        "prior_summary": prior_summary,
        "focus_hint": LANE_MEMORY_HINTS.get(lane, {}).get("focus_hint"),
    }


def build_questions_hub_context(
    db: Session,
    *,
    user_id: int | None,
) -> dict[str, Any]:
    empty = {
        "preferred_lane": None,
        "summary": "Хаб вопросов пока не видит накопленной линии и будет ориентироваться по самому вопросу.",
        "lane_suggestions": [],
    }
    if user_id is None:
        return empty

    rows = (
        db.query(db_models.GenerationLog)
        .filter(
            db_models.GenerationLog.user_id == user_id,
            db_models.GenerationLog.module == "questions",
            db_models.GenerationLog.surface.in_(QUESTION_SURFACES),
            db_models.GenerationLog.status == "success",
        )
        .order_by(db_models.GenerationLog.created_at.desc())
        .limit(30)
        .all()
    )
    if not rows:
        return empty

    lane_buckets: dict[str, dict[str, Any]] = {}
    for index, row in enumerate(rows):
        normalized_response = row.normalized_response if isinstance(row.normalized_response, dict) else {}
        input_payload = row.input_payload if isinstance(row.input_payload, dict) else {}
        item = _derive_memory_item(normalized_response, input_payload)
        if not item:
            continue
        lane = str(item.get("lane") or "").strip()
        if not lane:
            continue
        bucket = lane_buckets.setdefault(
            lane,
            {
                "lane": lane,
                "score": 0,
                "count": 0,
                "last_question": None,
                "last_thesis": None,
                "focus_hint": LANE_MEMORY_HINTS.get(lane, {}).get("focus_hint"),
            },
        )
        recency_weight = max(1, 6 - min(index, 5))
        bucket["score"] += recency_weight
        bucket["count"] += 1
        if bucket["last_question"] is None:
            bucket["last_question"] = item.get("question")
        if bucket["last_thesis"] is None:
            bucket["last_thesis"] = item.get("thesis")

    ranked = sorted(lane_buckets.values(), key=lambda item: (item["score"], item["count"]), reverse=True)
    top = ranked[:3]
    preferred_lane = top[0]["lane"] if top else None

    lane_suggestions = [
        {
            "lane": item["lane"],
            "count": item["count"],
            "last_question": item["last_question"],
            "last_thesis": item["last_thesis"],
            "focus_hint": item["focus_hint"],
        }
        for item in top
    ]

    if preferred_lane:
        summary = f"Сейчас у пользователя чаще всего звучит линия `{preferred_lane}`, поэтому хаб может заранее подталкивать к этому типу разбора, но не должен жёстко навязывать его."
    else:
        summary = empty["summary"]

    return {
        "preferred_lane": preferred_lane,
        "summary": summary,
        "lane_suggestions": lane_suggestions,
    }


def _editorial_fallback(
    *,
    lane: str,
    answer_payload: dict[str, Any],
    memory_context: dict[str, Any] | None,
) -> dict[str, str | None]:
    answer = answer_payload.get("answer") if isinstance(answer_payload.get("answer"), dict) else {}
    suggested_route = answer_payload.get("suggested_route") if isinstance(answer_payload.get("suggested_route"), dict) else {}
    current_focus = (
        _short_text(answer.get("clarity"))
        or _short_text(answer.get("window"))
        or _short_text(answer.get("explanation"))
        or _short_text(answer.get("risk"))
        or "Сейчас вопрос стоит сузить до одного рабочего фокуса."
    )
    carried_context = (
        _short_text((memory_context or {}).get("prior_summary"))
        or _short_text((memory_context or {}).get("focus_hint"))
        or ("Это первый зафиксированный вопрос в этой линии, поэтому контекст только начинает накапливаться." if lane != "decision" else "Это первый зафиксированный decision-разбор в этой линии, поэтому контекст только начинает накапливаться.")
    )
    next_step = (
        _short_text(answer.get("today"))
        or _short_text(answer.get("best_next_step"))
        or _short_text(suggested_route.get("reason"))
        or "Следующий шаг должен уменьшать неопределенность, а не добавлять новый шум."
    )
    return {
        "current_focus": current_focus,
        "carried_context": carried_context,
        "next_step": next_step,
    }


def _build_prompt(
    *,
    lane: str,
    question: str,
    answer_payload: dict[str, Any],
    memory_context: dict[str, Any] | None,
    learning_context: dict[str, Any] | None,
) -> str:
    answer = answer_payload.get("answer") if isinstance(answer_payload.get("answer"), dict) else {}
    suggested_route = answer_payload.get("suggested_route") if isinstance(answer_payload.get("suggested_route"), dict) else {}
    history = (memory_context or {}).get("history") if isinstance((memory_context or {}).get("history"), list) else []
    compact_history = []
    for item in history[:3]:
        if not isinstance(item, dict):
            continue
        compact_history.append(
            {
                "question": item.get("question"),
                "thesis": item.get("thesis"),
                "next_step": item.get("next_step"),
            }
        )

    prompt_payload = {
        "lane": lane,
        "question": question,
        "answer_blocks": {
            "clarity": answer.get("clarity"),
            "explanation": answer.get("explanation"),
            "forecast": answer.get("forecast"),
            "decision": answer.get("decision"),
            "today": answer.get("today"),
            "window": answer.get("window"),
            "risk": answer.get("risk"),
            "best_next_step": answer.get("best_next_step"),
            "check_before_deciding": answer.get("check_before_deciding"),
            "revisit_when": answer.get("revisit_when"),
        },
        "suggested_route": {
            "label": suggested_route.get("label"),
            "reason": suggested_route.get("reason"),
        },
        "memory_context": {
            "repeated_questions_count": (memory_context or {}).get("repeated_questions_count"),
            "prior_summary": (memory_context or {}).get("prior_summary"),
            "focus_hint": (memory_context or {}).get("focus_hint"),
            "history": compact_history,
        },
        "learning_summary": _short_text((learning_context or {}).get("summary")),
    }
    return (
        "Собери короткий editorial layer для ответа на вопрос.\n"
        "Не повторяй весь ответ, а выдели: главный фокус сейчас, какой контекст уже накоплен и какой следующий шаг полезнее всего.\n"
        "Если есть прошлые вопросы, используй их только тезисно.\n"
        f"{json.dumps(prompt_payload, ensure_ascii=False)}"
    )


def _parse_editorial_json(raw: str) -> dict[str, Any] | None:
    try:
        parsed = json.loads(raw.strip())
    except json.JSONDecodeError:
        return None
    if not isinstance(parsed, dict):
        return None
    if not isinstance(parsed.get("current_focus"), str):
        return None
    if not isinstance(parsed.get("next_step"), str):
        return None
    carried_context = parsed.get("carried_context")
    if carried_context is not None and not isinstance(carried_context, str):
        return None
    return parsed


def generate_question_editorial(
    db: Session,
    *,
    user: db_models.User | None,
    lane: str,
    question: str,
    answer_payload: dict[str, Any],
    memory_context: dict[str, Any] | None,
    locale: str = "ru",
    surface: str,
) -> dict[str, str | None]:
    fallback = _editorial_fallback(
        lane=lane,
        answer_payload=answer_payload,
        memory_context=memory_context,
    )
    learning_service = get_learning_service()

    learning_context = None
    latest_snapshot = None
    if user is not None:
        learning_context = learning_service.build_user_learning_context(db, user_id=user.id)
        latest_snapshot = (
            db.query(CoreProfileSnapshot)
            .filter(CoreProfileSnapshot.user_id == user.id)
            .order_by(CoreProfileSnapshot.updated_at.desc())
            .first()
        )

    user_prompt = _build_prompt(
        lane=lane,
        question=question,
        answer_payload=answer_payload,
        memory_context=memory_context,
        learning_context=learning_context,
    )
    prompt_version = learning_service.get_or_create_prompt_version(
        db,
        module="questions",
        version=PROMPT_VERSION,
        prompt_kind="system",
        prompt_text=SYSTEM_PROMPT,
        label="questions_editorial",
        metadata={"surface": surface},
    )

    if not settings.openai_api_key:
        return fallback

    try:
        import openai
    except ImportError:
        return fallback

    started_at = perf_counter()
    try:
        client = openai.OpenAI(api_key=settings.openai_api_key)
        resp = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.4,
            max_tokens=260,
            response_format={"type": "json_object"},
        )
        content = (resp.choices[0].message.content or "").strip()
        parsed = _parse_editorial_json(content) if content else None
        if not parsed:
            return fallback

        editorial = {
            "current_focus": _short_text(parsed.get("current_focus")),
            "carried_context": _short_text(parsed.get("carried_context")),
            "next_step": _short_text(parsed.get("next_step")),
        }
        learning_service.log_generation(
            db,
            module="questions",
            surface=f"{surface}_editorial",
            user_id=user.id if user is not None else None,
            core_profile_snapshot_id=latest_snapshot.id if latest_snapshot else None,
            prompt_version_id=prompt_version.id,
            model=MODEL_NAME,
            locale=locale,
            input_payload={"lane": lane, "question": question, "memory_context": memory_context},
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            raw_response=content,
            normalized_response=editorial,
            status="success",
            used_fallback=False,
            duration_ms=int((perf_counter() - started_at) * 1000),
        )
        return editorial
    except Exception as exc:
        logger.warning("Question editorial generation failed: %s", exc, exc_info=True)
        try:
            learning_service.log_generation(
                db,
                module="questions",
                surface=f"{surface}_editorial",
                user_id=user.id if user is not None else None,
                core_profile_snapshot_id=latest_snapshot.id if latest_snapshot else None,
                prompt_version_id=prompt_version.id,
                model=MODEL_NAME,
                locale=locale,
                input_payload={"lane": lane, "question": question, "memory_context": memory_context},
                system_prompt=SYSTEM_PROMPT,
                user_prompt=user_prompt,
                normalized_response=fallback,
                status="error",
                used_fallback=True,
                error_message=str(exc),
                duration_ms=int((perf_counter() - started_at) * 1000),
            )
        except Exception:
            logger.debug("Failed to log question editorial fallback", exc_info=True)
        return fallback

"""AI editorial layer for compatibility payloads.

Generates a compact compatibility narrative from structured engine output.
Uses only condensed prior memory, not full previous responses, to control token usage.
"""

from __future__ import annotations

import json
import logging
from time import perf_counter
from typing import Any

from sqlalchemy.orm import Session

from todayflow_backend.core import models
from todayflow_backend.core.config import settings
from todayflow_backend.db import models as db_models
from todayflow_backend.db.models import CoreProfileSnapshot
from todayflow_backend.services.learning import get_learning_service

logger = logging.getLogger(__name__)

PROMPT_VERSION = "compatibility-editorial-v1"
MODEL_NAME = "gpt-4o-mini"

SYSTEM_PROMPT = """Ты пишешь короткий редакторский слой для результата совместимости TodayFlow.

Твоя задача:
- не пересказывать весь технический payload;
- собрать суть связи человеческим языком;
- различать режимы romantic, family, parent_child, business;
- использовать прошлую память по паре только как короткие тезисы, а не как текст для копирования.

Правила:
- никакой эзотерической воды;
- никакой перегрузки аспектами и терминами;
- писать ясно, по делу, в живом русском языке;
- strengths и tensions — короткие буллеты по 1 предложению;
- next_step — один практический следующий шаг;
- не дублировать одно и то же разными словами.

Верни только JSON:
{"mode_focus":"...","pair_thesis":"...","strengths":["...","..."],"tensions":["...","..."],"next_step":"..."}"""


def _editorial_fallback(payload: dict[str, Any]) -> models.CompatibilityEditorial:
    deep_dive = payload.get("deep_dive") if isinstance(payload.get("deep_dive"), dict) else {}
    knowledge = deep_dive.get("knowledge") if isinstance(deep_dive.get("knowledge"), dict) else {}
    strengths = [item for item in (deep_dive.get("strengths") or []) if isinstance(item, str)][:2]
    tensions = [item for item in (deep_dive.get("challenges") or []) if isinstance(item, str)][:2]
    guidance = [item for item in (deep_dive.get("guidance") or []) if isinstance(item, str)]
    summary = str(payload.get("summary") or "Связь уже собрана в структурированный результат совместимости.")
    return models.CompatibilityEditorial(
        mode_focus=str(knowledge.get("mode_summary") or knowledge.get("mode_title") or "").strip() or None,
        pair_thesis=summary,
        strengths=strengths or ["У пары есть рабочая опора, если держать ясность в контакте и не полагаться только на инерцию."],
        tensions=tensions or ["Связь чаще ломается там, где ожидания и темп не проговариваются прямо."],
        next_step=guidance[0] if guidance else "Следующий шаг здесь — выбрать одну зону контакта и договориться о ней прямо, без догадок.",
    )


def _build_prompt(
    *,
    relation_mode: str,
    payload: dict[str, Any],
    prior_memory: dict[str, Any] | None,
    learning_context: dict[str, Any] | None,
) -> str:
    deep_dive = payload.get("deep_dive") if isinstance(payload.get("deep_dive"), dict) else {}
    knowledge = deep_dive.get("knowledge") if isinstance(deep_dive.get("knowledge"), dict) else {}
    dimensions = deep_dive.get("dimensions") if isinstance(deep_dive.get("dimensions"), list) else []
    compact_dimensions = []
    for item in dimensions[:5]:
        if not isinstance(item, dict):
            continue
        compact_dimensions.append(
            {
                "label": item.get("label"),
                "score": item.get("score"),
                "summary": item.get("summary"),
            }
        )

    prior_history = prior_memory.get("history") if isinstance(prior_memory, dict) and isinstance(prior_memory.get("history"), list) else []
    prior_history_compact = []
    for item in prior_history[:3]:
        if not isinstance(item, dict):
            continue
        prior_history_compact.append(
            {
                "summary": item.get("summary"),
                "relationship_archetype": item.get("relationship_archetype"),
                "strongest_axis": item.get("strongest_axis"),
                "tension_axis": item.get("tension_axis"),
            }
        )

    learning_summary = ""
    if isinstance(learning_context, dict):
        learning_summary = str(learning_context.get("summary") or "").strip()

    prompt_payload = {
        "relation_mode": relation_mode,
        "mode_title": knowledge.get("mode_title"),
        "mode_summary": knowledge.get("mode_summary"),
        "overall_score": payload.get("overall_score"),
        "relationship_type": payload.get("relationship_type"),
        "summary": payload.get("summary"),
        "relationship_archetype": deep_dive.get("relationship_archetype"),
        "strongest_axis": deep_dive.get("strongest_axis"),
        "tension_axis": deep_dive.get("tension_axis"),
        "strengths": [item for item in (deep_dive.get("strengths") or []) if isinstance(item, str)][:4],
        "challenges": [item for item in (deep_dive.get("challenges") or []) if isinstance(item, str)][:4],
        "guidance": [item for item in (deep_dive.get("guidance") or []) if isinstance(item, str)][:4],
        "dimensions": compact_dimensions,
        "prior_memory": {
            "summary": prior_memory.get("summary") if isinstance(prior_memory, dict) else None,
            "relationship_archetype": prior_memory.get("relationship_archetype") if isinstance(prior_memory, dict) else None,
            "strongest_axis": prior_memory.get("strongest_axis") if isinstance(prior_memory, dict) else None,
            "tension_axis": prior_memory.get("tension_axis") if isinstance(prior_memory, dict) else None,
            "history": prior_history_compact,
        },
        "learning_summary": learning_summary,
    }

    return (
        "Собери компактный editorial layer для совместимости.\n"
        "Используй только текущий structured payload и прошлую thesis-memory.\n"
        "Если прошлые тезисы повторяются, не расширяй их бессмысленно; добавляй только то, что уточняет картину.\n"
        "Не копируй прошлые формулировки дословно.\n"
        "Данные:\n"
        f"{json.dumps(prompt_payload, ensure_ascii=False)}"
    )


def _parse_editorial_json(raw: str) -> dict[str, Any] | None:
    try:
        parsed = json.loads(raw.strip())
    except json.JSONDecodeError:
        return None
    if not isinstance(parsed, dict):
        return None
    if not isinstance(parsed.get("pair_thesis"), str) or not isinstance(parsed.get("next_step"), str):
        return None
    strengths = parsed.get("strengths")
    tensions = parsed.get("tensions")
    if strengths is not None and not isinstance(strengths, list):
        return None
    if tensions is not None and not isinstance(tensions, list):
        return None
    return parsed


def generate_compatibility_editorial(
    db: Session,
    *,
    user: db_models.User,
    relation_mode: str,
    payload: dict[str, Any],
    prior_memory: dict[str, Any] | None = None,
    locale: str = "ru",
) -> models.CompatibilityEditorial:
    learning_service = get_learning_service()
    prompt_version = learning_service.get_or_create_prompt_version(
        db,
        module="compatibility",
        version=PROMPT_VERSION,
        prompt_kind="system",
        prompt_text=SYSTEM_PROMPT,
        label="compatibility_editorial",
        metadata={"surface": "compatibility_editorial"},
    )

    fallback = _editorial_fallback(payload)
    learning_context = learning_service.build_user_learning_context(db, user_id=user.id)
    user_prompt = _build_prompt(
        relation_mode=relation_mode,
        payload=payload,
        prior_memory=prior_memory,
        learning_context=learning_context,
    )

    if not settings.openai_api_key:
        return fallback

    try:
        import openai
    except ImportError:
        return fallback

    started_at = perf_counter()
    latest_snapshot = (
        db.query(CoreProfileSnapshot)
        .filter(CoreProfileSnapshot.user_id == user.id)
        .order_by(CoreProfileSnapshot.updated_at.desc())
        .first()
    )

    try:
        client = openai.OpenAI(api_key=settings.openai_api_key)
        resp = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.5,
            max_tokens=500,
            response_format={"type": "json_object"},
        )
        content = (resp.choices[0].message.content or "").strip()
        parsed = _parse_editorial_json(content) if content else None
        if parsed:
            editorial = models.CompatibilityEditorial(
                mode_focus=str(parsed.get("mode_focus") or "").strip() or None,
                pair_thesis=str(parsed.get("pair_thesis") or "").strip(),
                strengths=[item for item in (parsed.get("strengths") or []) if isinstance(item, str)][:3],
                tensions=[item for item in (parsed.get("tensions") or []) if isinstance(item, str)][:3],
                next_step=str(parsed.get("next_step") or "").strip(),
            )
            learning_service.log_generation(
                db,
                module="compatibility",
                surface="compatibility_editorial",
                user_id=user.id,
                core_profile_snapshot_id=latest_snapshot.id if latest_snapshot else None,
                prompt_version_id=prompt_version.id,
                model=MODEL_NAME,
                locale=locale,
                input_payload={
                    "relation_mode": relation_mode,
                    "overall_score": payload.get("overall_score"),
                    "prior_memory": prior_memory,
                },
                system_prompt=SYSTEM_PROMPT,
                user_prompt=user_prompt,
                raw_response=content,
                normalized_response=editorial.model_dump(),
                status="success",
                used_fallback=False,
                duration_ms=int((perf_counter() - started_at) * 1000),
            )
            return editorial

        learning_service.log_generation(
            db,
            module="compatibility",
            surface="compatibility_editorial",
            user_id=user.id,
            core_profile_snapshot_id=latest_snapshot.id if latest_snapshot else None,
            prompt_version_id=prompt_version.id,
            model=MODEL_NAME,
            locale=locale,
            input_payload={"relation_mode": relation_mode, "overall_score": payload.get("overall_score"), "prior_memory": prior_memory},
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            raw_response=content,
            normalized_response=fallback.model_dump(),
            status="fallback",
            used_fallback=True,
            error_message="invalid_or_unusable_response",
            duration_ms=int((perf_counter() - started_at) * 1000),
        )
        return fallback
    except Exception as exc:
        logger.warning("Compatibility editorial generation failed: %s", exc, exc_info=True)
        try:
            learning_service.log_generation(
                db,
                module="compatibility",
                surface="compatibility_editorial",
                user_id=user.id,
                core_profile_snapshot_id=latest_snapshot.id if latest_snapshot else None,
                prompt_version_id=prompt_version.id,
                model=MODEL_NAME,
                locale=locale,
                input_payload={"relation_mode": relation_mode, "overall_score": payload.get("overall_score"), "prior_memory": prior_memory},
                system_prompt=SYSTEM_PROMPT,
                user_prompt=user_prompt,
                normalized_response=fallback.model_dump(),
                status="error",
                used_fallback=True,
                error_message=str(exc),
                duration_ms=int((perf_counter() - started_at) * 1000),
            )
        except Exception:
            logger.debug("Failed to log compatibility editorial fallback", exc_info=True)
        return fallback

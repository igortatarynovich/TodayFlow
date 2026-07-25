"""Tarot interpretation LLM — author of reading prose from Context Pack.

Canon: docs/tarot/TAROT_INTERPRETATION_ENGINE_V1.md
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any

from todayflow_backend.core.llm_openai_compatible import (
    chat_completion_text,
    get_openai_compatible_client,
    is_llm_chat_configured,
    resolve_default_chat_model,
    resolve_max_tokens,
)
from todayflow_backend.core.text_quality import is_meaningful_sentence

logger = logging.getLogger(__name__)

TAROT_INTERPRETATION_PROMPT_VER = "tarot-interpretation-v1.0"

_BANNED_SUBSTRINGS = (
    "аркан",
    "то, что просит быть замеченным",
    "учитывая твой стиль решений:",
    "справочное значение",
    "линия расклада",
    "диалог карт",
)

_SYSTEM_RU = """Ты — интерпретатор расклада Таро для продукта TodayFlow.

Тебе дают Deterministic Context Pack (факты): карты, масти, ориентации, роли позиций, диапазоны смыслов, вопрос, тип расклада, короткий фрагмент профиля.

Твои четыре действия:
1) Объясни, что обычно символизируют ключевые карты и масти.
2) Покажи, как значения меняются из‑за позиции и ориентации.
3) Свяжи карты с вопросом и только релевантной частью профиля (если она есть) — без дословного копипаста профиля.
4) Дай прямой, но не категоричный ответ и один конкретный следующий шаг.

Правила голоса:
- Не пересказывай карты по одной как список «карта 1 = …, карта 2 = …».
- Сначала символический материал, затем единая картина, затем ответ на вопрос.
- Пиши по-русски, конкретно, без мистической категоричности и без «система/ИИ/алгоритм».
- Запрещено писать «Аркан» или «то, что просит быть замеченным».
- Для spread_kind=choice внутри question_story сравни пути A и B (gain vs risk), затем сведи к одному выводу.
- Позиция step = действие; позиция risk = опасность пути, не совет.

Верни ТОЛЬКО валидный JSON:
{
  "symbols_overview": "Что здесь показывают карты — 2–5 предложений",
  "question_story": "Как это связано с вопросом — единая история; для choice — сравнение A/B",
  "direct_answer": "Ответ на вопрос — ясный, без фатализма",
  "next_step": "Один применимый шаг",
  "option_a_note": null,
  "option_b_note": null,
  "confidence_note": "Короткая оговорка или null"
}
"""


def _parse_json_content(raw: str) -> dict[str, Any] | None:
    text = (raw or "").strip()
    if not text:
        return None
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start < 0 or end <= start:
            return None
        try:
            parsed = json.loads(text[start : end + 1])
        except json.JSONDecodeError:
            return None
    return parsed if isinstance(parsed, dict) else None


def _clean_field(value: Any, *, min_words: int = 6) -> str | None:
    if not isinstance(value, str):
        return None
    text = re.sub(r"\s+", " ", value).strip()
    if not text:
        return None
    low = text.lower()
    if any(b in low for b in _BANNED_SUBSTRINGS):
        return None
    ok, _ = is_meaningful_sentence(text, min_words=min_words)
    if not ok:
        return None
    return text


def validate_interpretation(payload: dict[str, Any] | None) -> dict[str, str] | None:
    if not isinstance(payload, dict):
        return None
    symbols = _clean_field(payload.get("symbols_overview"), min_words=8)
    story = _clean_field(payload.get("question_story"), min_words=8)
    answer = _clean_field(payload.get("direct_answer"), min_words=6)
    step = _clean_field(payload.get("next_step"), min_words=5)
    if not (symbols and story and answer and step):
        return None
    out: dict[str, str] = {
        "symbols_overview": symbols,
        "question_story": story,
        "direct_answer": answer,
        "next_step": step,
    }
    for opt_key in ("option_a_note", "option_b_note", "confidence_note", "holding", "shifting"):
        cleaned = _clean_field(payload.get(opt_key), min_words=4)
        if cleaned:
            out[opt_key] = cleaned
    return out


def choice_story_from_interpretation(interp: dict[str, str], pack: dict[str, Any]) -> dict[str, Any] | None:
    if pack.get("spread_kind") != "choice":
        return None
    return {
        "option_a_summary": interp.get("option_a_note") or "",
        "option_b_summary": interp.get("option_b_note") or "",
        "option_a_gain": "",
        "option_a_risk": "",
        "option_b_gain": "",
        "option_b_risk": "",
        "hidden_tension": interp.get("holding") or "",
        "recommended_next_step": interp.get("next_step") or "",
        "confidence_note": interp.get("confidence_note") or "",
    }


def call_tarot_interpretation_llm_v1(
    pack: dict[str, Any],
    *,
    max_attempts: int = 2,
) -> dict[str, str] | None:
    """Generate interpretation from context pack. None if LLM unavailable/invalid."""
    if not is_llm_chat_configured():
        return None
    client = get_openai_compatible_client()
    if client is None:
        return None

    user_full = json.dumps(pack, ensure_ascii=False)
    user_sent = user_full[:16000]
    attempts = max(1, min(int(max_attempts or 1), 3))
    model = resolve_default_chat_model()

    for attempt_idx in range(attempts):
        content = chat_completion_text(
            client,
            model=model,
            messages=[
                {"role": "system", "content": _SYSTEM_RU},
                {"role": "user", "content": user_sent},
            ],
            temperature=0.55,
            max_tokens=resolve_max_tokens(1400, model=model),
            json_object=True,
        )
        if not content:
            logger.warning("tarot_llm empty response attempt=%s", attempt_idx)
            continue
        parsed = _parse_json_content(content)
        validated = validate_interpretation(parsed)
        if validated:
            return validated
        logger.warning("tarot_llm validation failed attempt=%s", attempt_idx)
    return None

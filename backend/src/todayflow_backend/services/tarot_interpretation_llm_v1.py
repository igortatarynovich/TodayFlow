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

TAROT_INTERPRETATION_PROMPT_VER = "tarot-interpretation-v1.1"

_BANNED_SUBSTRINGS = (
    "аркан",
    "то, что просит быть замеченным",
    "что-то просит быть замеченным",
    "учитывая твой стиль решений:",
    "справочное значение",
    "линия расклада",
    "диалог карт",
    "карты говорят тебе факт",
    "карты сообщают факт",
)

_EMPTY_FORMULAS = (
    "важно заметить",
    "что-то важное",
    "слушай себя",
    "просто доверься",
    "вселенная подсказывает",
    "энергия дня",
)

_ACTION_MARKERS = (
    "запиш",
    "сделай",
    "зада",
    "позвон",
    "отправ",
    "обнов",
    "назов",
    "провер",
    "назнач",
    "поговор",
    "сформулир",
    "открой",
    "отправь",
    "один ",
    "разговор",
    "срок",
    "резюме",
    "отклик",
)

_SYSTEM_RU = """Ты — интерпретатор расклада Таро для TodayFlow.

Вход: Deterministic Context Pack — факты (карты, свет/тень, upright/reversed, масть, стихия, роль позиции, question_lens, короткий profile_relevant). Это материал, не готовый ответ.

Порядок работы (обязателен):
1) Собери общий конфликт расклада из символов и мастей.
2) Покажи, как позиции и ориентации меняют значение (без механического списка).
3) Свяжи картину с вопросом; профиль используй только как тон/склонность — не цитируй.
4) Дай прямой, но не категоричный ответ и один конкретный следующий шаг.

Жёсткие запреты:
- не разбирай карты механически по очереди («карта 1… карта 2…»);
- не повторяй вопрос пользователя больше одного раза во всём ответе;
- не повторяй названия позиций в каждом абзаце;
- не цитируй profile_relevant дословно;
- не выдавай карты за факты о внешнем мире («он точно…», «уволят…»);
- не используй пустые формулы («что-то просит быть замеченным», «просто доверься»);
- запрещено слово «Аркан» как имя карты;
- сначала конфликт/картина, потом ответ — не наоборот.

Для spread_kind=choice:
- в question_story явно сравни A и B (что даёт / риск);
- option_a_note и option_b_note обязательны и должны различаться;
- затем один общий вывод в direct_answer.

Верни ТОЛЬКО валидный JSON:
{
  "symbols_overview": "символы и напряжения — 2–5 предложений",
  "question_story": "единая история под вопрос; для choice — сравнение A/B",
  "direct_answer": "прямой ответ на вопрос без фатализма",
  "next_step": "один конкретный применимый шаг",
  "option_a_note": "null или отличие пути A",
  "option_b_note": "null или отличие пути B",
  "confidence_note": "короткая оговорка или null"
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


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip().lower())


def _clean_field(value: Any, *, min_words: int = 6) -> str | None:
    if not isinstance(value, str):
        return None
    text = re.sub(r"\s+", " ", value).strip()
    if not text:
        return None
    low = text.lower()
    if any(b in low for b in _BANNED_SUBSTRINGS):
        return None
    if any(f in low for f in _EMPTY_FORMULAS):
        return None
    ok, _ = is_meaningful_sentence(text, min_words=min_words)
    if not ok:
        return None
    return text


def _count_question_mentions(blob: str, question: str) -> int:
    q = (question or "").strip()
    if len(q) < 8:
        return 0
    core = q.strip(" «»\"'?.!:")
    if len(core) < 8:
        return 0
    return blob.lower().count(core.lower())


def _near_dup(a: str, b: str) -> bool:
    na, nb = _norm(a), _norm(b)
    if not na or not nb:
        return False
    if na == nb:
        return True
    if len(na) > 40 and (na in nb or nb in na):
        return True
    return False


def _profile_leaked(blob: str, pack: dict[str, Any]) -> bool:
    profile = pack.get("profile_relevant") if isinstance(pack.get("profile_relevant"), dict) else {}
    for val in profile.values():
        text = str(val or "").strip()
        if len(text) >= 24 and text.lower() in blob.lower():
            return True
    lens = str(pack.get("profile_lens") or "").strip()
    if len(lens) >= 24 and lens.lower() in blob.lower():
        return True
    return False


def _cards_linked(blob: str, pack: dict[str, Any]) -> bool:
    names = []
    for card in pack.get("cards") or []:
        if not isinstance(card, dict):
            continue
        name = str(card.get("name_ru") or "")
        # strip orientation suffix for matching base name
        base = re.sub(r"\s*\(перевёрнутый\)\s*$", "", name, flags=re.I).strip()
        if base:
            names.append(base.lower())
    if len(names) < 2:
        return True
    hits = sum(1 for n in dict.fromkeys(names) if n and n in blob.lower())
    return hits >= 2


def _step_concrete(step: str) -> bool:
    low = step.lower()
    if any(m in low for m in _ACTION_MARKERS):
        return True
    # Digit / list cue often means concrete criteria.
    if re.search(r"\d", step):
        return True
    return len(step.split()) >= 8


def _position_title_spam(blob: str, pack: dict[str, Any]) -> bool:
    titles = []
    for card in pack.get("cards") or []:
        if isinstance(card, dict):
            t = str(card.get("position_title") or "").strip()
            if len(t) >= 6:
                titles.append(t.lower())
    for title in dict.fromkeys(titles):
        if blob.lower().count(title) >= 3:
            return True
    return False


def quality_reject_reason(fields: dict[str, str], pack: dict[str, Any]) -> str | None:
    """Return reject reason or None if quality gates pass."""
    symbols = fields["symbols_overview"]
    story = fields["question_story"]
    answer = fields["direct_answer"]
    step = fields["next_step"]
    blob = f"{symbols} {story} {answer} {step}"

    for key, text in fields.items():
        if len(text) > 900:
            return f"too_long:{key}"
        if len(text) < 20 and key in {"symbols_overview", "question_story", "direct_answer"}:
            return f"too_short:{key}"

    if _near_dup(symbols, story) or _near_dup(story, answer) or _near_dup(answer, step):
        return "cross_field_duplicate"

    q = str(pack.get("question") or "")
    if _count_question_mentions(blob, q) > 1:
        return "question_repeated"

    if _profile_leaked(blob, pack):
        return "profile_verbatim"

    if not _cards_linked(blob, pack):
        return "cards_not_linked"

    if not _step_concrete(step):
        return "next_step_vague"

    if _position_title_spam(blob, pack):
        return "position_title_spam"

    # Mechanical enumeration heuristic: many "карта" / numbered card retells.
    if len(re.findall(r"карта\s*\d|карта\s+[«\"]", blob.lower())) >= 2:
        return "mechanical_card_list"

    if pack.get("spread_kind") == "choice" or pack.get("response_shape", {}).get("choice_compare"):
        a = fields.get("option_a_note") or ""
        b = fields.get("option_b_note") or ""
        story_l = story.lower()
        has_contrast = (
            ("вариант a" in story_l and "вариант b" in story_l)
            or ("путь a" in story_l and "путь b" in story_l)
            or ("option a" in story_l and "option b" in story_l)
        )
        if not a or not b:
            if not has_contrast:
                return "choice_missing_contrast"
        elif _near_dup(a, b):
            return "choice_options_same"

    return None


def validate_interpretation(
    payload: dict[str, Any] | None,
    *,
    pack: dict[str, Any] | None = None,
) -> dict[str, str] | None:
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

    if pack is not None:
        reason = quality_reject_reason(out, pack)
        if reason:
            logger.info("tarot_llm quality reject reason=%s", reason)
            return None
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
        validated = validate_interpretation(parsed, pack=pack)
        if validated:
            return validated
        logger.warning("tarot_llm validation failed attempt=%s", attempt_idx)
    return None

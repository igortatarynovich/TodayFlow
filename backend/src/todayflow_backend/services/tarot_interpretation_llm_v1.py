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
    llm_operation,
    resolve_default_chat_model,
    resolve_max_tokens,
)
from todayflow_backend.core.text_quality import is_meaningful_sentence

logger = logging.getLogger(__name__)

TAROT_INTERPRETATION_PROMPT_VER = "tarot-interpretation-v1.10"

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

# Lexicon banned in direct_answer / next_step (user-facing first fields).
_USER_FACING_JARGON = (
    "аркан",
    "расклад",
    "перевёрнут",
    "перевернут",
    "масть",
    "позиции",
    "позиция ",
    "кубков",
    "жезлов",
    "мечей",
    "пентакл",
    "мажорн",
    "минорн",
    "старший аркан",
    "младший аркан",
)

_NEXT_STEP_MAX_CHARS = 220
_OPTION_NOTE_MAX_CHARS = 180

# Empty solemnity / wellness mush — cleaned fields reject if present.
_EMPTY_FORMULAS = (
    "важно заметить",
    "что-то важное",
    "слушай себя",
    "просто доверься",
    "вселенная подсказывает",
    "энергия дня",
    "послание карт",
    "мудрость карт",
    "карты шепчут",
    "судьбоносн",
    "сакральн",
    "предназначение зовёт",
    "истинный путь",
    "глубинный смысл всего",
    "пространство смысла",
    "энергетическ",
    "вибрац",
    "просит внимания вселенной",
    "самый тяжёлый вес",
    "на горизонте маячит",
)

# Rhetorical antithesis hard-gate (owner editorial, 2026-07-26):
# short parallel verbs «не кричит, а греет». Noun advice contrasts stay allowed.
# Broader «это не …, а …» remains prompt-only (hard reject over-killed live).
_ANTITHESIS_NE_A_RE = re.compile(
    r"(?:(?<=[\s«\"(\[{])|^)не\s+([а-яёa-z]{3,18}),\s*а\s+([а-яёa-z]{3,18})"
    r"(?=[\s»\")\]}.,!?;:—-]|$)",
    re.IGNORECASE | re.UNICODE,
)
_ANTITHESIS_VERBISH_RE = re.compile(
    r"(?:ет|ит|ат|ут|ют|ешь|ишь|ал|ала|или|ый|ая|ое|ть)$",
    re.IGNORECASE | re.UNICODE,
)
_ANTITHESIS_NOT_BUT_RE = re.compile(
    r"\bnot\s+([a-z]{3,18}),\s*but\s+([a-z]{3,18})\b",
    re.IGNORECASE,
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

_SYSTEM_RU = """Ты — голос TodayFlow в раскладе Таро.

Вход: один Context Pack = Question Ontology + Position Semantics + Knowledge Base + короткий profile tint.
Оставайся в ОДНОМ авторском режиме — не переключайся на отдельный шаблон «под тип вопроса».

Голос — мудрый аналитический разбор (Voice Canon):
- Пиши как ясный разбор: наблюдаемый паттерн → конфликт/цена → вывод по вопросу → один проверяемый шаг.
- Каждый абзац должен нести содержание, которое можно пересказать без пафоса: поведение, критерий, риск, цена бездействия, что проверить.
- Метафора допустима только если сразу раскрывается в человеческий паттерн
  (не «туман судьбы», а «откладывание решения из‑за страха ошибки»).
- Запрещена напускная важность без смысла: торжественные формулы, «судьбоносность», пустая глубина,
  нагнетание («самый тяжёлый вес», «на горизонте маячит судьба») без механизма.
- «Научность» = точность, калибровка, проверяемость — не жаргон и не механизм продукта.
- Уверенность калибруй: тенденция / гипотеза / наблюдение — не приговор и не мистический вердикт.
- Близость/секс: спокойно, конкретно, без стыда, пошлости и медицинских советов.
- Друг: на стороне человека; без морализаторства и без пустой поддержки («просто доверься»).

question_ontology задаёт логику ответа:
- central_task, direct_answer_means, must_show, allowed_specificity, must_not_claim, next_step_kind
- question_type / domain / intent / decision_horizon

position_semantics задаёт, КАК читать каждую карту в позиции (purpose / extract_from_card / do_not / result_type).
meaning_range — семантические факты карты (central_symbol, light/shadow, inner_conflict, domain_lens,
reversed_*, intensifies_drawn / softens_drawn; для младших — Q1: core_scene, central_conflict,
driving_need, shadow_pattern, growth_direction, *_lens, reversed_shift, adjacent_distinction).
Используй Q1 как уникальный архетип карты, не как формулу масть×ранг.
Не обязательно называть карты по имени: опирайся на core_scene / central_conflict / adjacent_distinction.
Если называешь карты — только в symbols_overview / question_story; запрещён механический список «карта 1… карта 2…».

Порядок рассуждения (внутренний, обязателен):
1) Собери конфликт расклада из символов и ролей позиций — назови механизм, не атмосферу.
2) Примени логику question_ontology (сравнение для choice; гипотеза≠факт для relationship_intent; без даты для timing_readiness).
3) Свяжи с вопросом; профиль — только тон, не цитата.
4) Сформулируй прямой ответ и один шаг для человека — уже без таро-жаргона.

Порядок полей для человека (answer-first): сначала direct_answer и next_step понятны без карт;
тарология и имена карт — только в symbols_overview / question_story.

Поля direct_answer и next_step (жёстко):
- пиши так, чтобы человек, который НЕ видел карт и НЕ знает таро, сразу понял вывод и шаг;
- запрещены имена карт, масти (кубков/жезлов/мечей/пентаклей), «аркан», «перевёрнут*», «расклад»,
  «позиция», отсылки вроде «картина десятки кубков», «умеренность говорит»;
- direct_answer: 1–2 короткие фразы — вывод + критерий проверки, без фатализма;
- next_step: ОДИН конкретный шаг + один критерий «как понять, что сработало»; 1–2 предложения.
  Многонедельные протоколы («три раза по 15 минут на неделю…») клади в question_story, не сюда.

Жёсткие запреты:
- не разбирай карты механически по очереди («карта 1… карта 2…»);
- не повторяй вопрос пользователя больше одного раза во всём ответе;
- не повторяй названия позиций в каждом абзаце;
- не цитируй profile_relevant дословно;
- не выдавай карты за факты о внешнем мире («он точно…», «уволят…»);
- не используй пустые формулы («что-то просит быть замеченным», «просто доверься», «послание карт»);
- не строй фразы на антитезе «не X, а Y» / «это не …, а …» (напр. «не кричит, а греет») —
  говори прямо, что есть, без риторического отрицания;
- запрещено слово «Аркан» как имя карты;
- соблюдай do_not каждой position_semantics и must_not_claim question_ontology;
- не называй точные даты при timing_readiness;
- не читай мысли другого как факт при relationship_intent;
- не ставь клинический диагноз и не давай медицинских/фармакологических советов.

Для choice (question_type=choice или spread_kind=choice):
- в question_story — короткий общий конфликт выбора (2–4 предложения), без полного разбора всех позиций;
- option_a_note / option_b_note: ровно две короткие клаузы без украшений —
  «Даёт: … Стоит: …» (или два коротких предложения). Без прилагательных вроде «непроштампованный», «живой»;
- затем один общий вывод в direct_answer (без имён карт);
- держи question_story компактным: не раздувай сравнение внутри story, если оно уже в option_*_note.

Верни ТОЛЬКО валидный JSON:
{
  "symbols_overview": "наблюдаемые напряжения расклада — 2–5 предложений, без пустой торжественности",
  "question_story": "единая история под вопрос как разбор паттерна; для choice — сжатый конфликт выбора",
  "direct_answer": "прямой ответ без таро-жаргона: вывод + критерий",
  "next_step": "один короткий применимый и проверяемый шаг без таро-жаргона",
  "option_a_note": "null или «Даёт: … Стоит: …»",
  "option_b_note": "null или «Даёт: … Стоит: …»",
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


_ANCHOR_STOP = {
    "против",
    "через",
    "когда",
    "чтобы",
    "этот",
    "этого",
    "эта",
    "эти",
    "человек",
    "людей",
    "карта",
    "карты",
    "жизнь",
    "сейчас",
    "может",
    "нужно",
    "важно",
}


def _tokens_from_texts(texts: list[str], *, limit: int = 10) -> list[str]:
    anchors: list[str] = []
    for text in texts:
        for tok in re.findall(r"[^\W\d_]{4,}", str(text or "").lower(), flags=re.UNICODE):
            if tok in _ANCHOR_STOP:
                continue
            anchors.append(tok)
    return list(dict.fromkeys(anchors))[:limit]


def _list_texts(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value if str(item or "").strip()]
    text = str(value or "").strip()
    return [text] if text else []


def _upright_anchor_texts(rng: dict[str, Any]) -> list[str]:
    """Upright / shared-scene pole — excludes reverse-only KB fields."""
    # Q1 / themes first so distinctive tokens survive the cap; catalog prose last.
    texts: list[str] = [
        str(rng.get("central_symbol") or ""),
        str(rng.get("core_scene") or ""),
        str(rng.get("central_conflict") or ""),
        str(rng.get("driving_need") or ""),
        str(rng.get("growth_direction") or ""),
    ]
    texts.extend(_list_texts(rng.get("light_side")))
    texts.extend(_list_texts(rng.get("upright_themes")))
    texts.append(str(rng.get("upright_meaning") or ""))
    return [t for t in texts if str(t).strip()]


def _reversed_anchor_texts(rng: dict[str, Any]) -> list[str]:
    """Reverse pole — minors Q1 + majors reversed.* projected into meaning_range."""
    texts: list[str] = [
        str(rng.get("reversed_shift") or ""),
        str(rng.get("reversed_central") or ""),
        str(rng.get("reversed_trap") or ""),
    ]
    texts.extend(_list_texts(rng.get("reversed_themes")))
    texts.append(str(rng.get("reversed_meaning") or ""))
    return [t for t in texts if str(t).strip()]


def _card_display_base(card: dict[str, Any]) -> str:
    name = str(card.get("name_ru") or "")
    return re.sub(r"\s*\(перевёрнутый\)\s*$", "", name, flags=re.I).strip()


def _card_semantic_anchors(card: dict[str, Any]) -> list[str]:
    """Distinctive tokens from KB/Q1 facts (+ optional name) for grounding checks."""
    rng = card.get("meaning_range") if isinstance(card.get("meaning_range"), dict) else {}
    # Prefer Q1 / conflict tokens before long catalog prose (cap otherwise drops them).
    texts = [
        str(rng.get("core_scene") or ""),
        str(rng.get("central_conflict") or ""),
        str(rng.get("central_symbol") or ""),
        str(rng.get("driving_need") or ""),
        str(rng.get("growth_direction") or ""),
        str(rng.get("inner_conflict") or ""),
        str(rng.get("outer_expression") or ""),
        *_list_texts(rng.get("light_side")),
        *_list_texts(rng.get("shadow_side")),
        *_list_texts(rng.get("upright_themes")),
        *_list_texts(rng.get("reversed_themes")),
        str(rng.get("reversed_shift") or ""),
        str(rng.get("reversed_central") or ""),
        str(rng.get("reversed_trap") or ""),
        str(rng.get("shadow_pattern") or ""),
        str(rng.get("upright_meaning") or ""),
        str(rng.get("reversed_meaning") or ""),
    ]
    base = _card_display_base(card)
    if base:
        texts.append(base)
    return _tokens_from_texts(texts, limit=24)


def _card_pole_anchors(card: dict[str, Any]) -> tuple[list[str], list[str]]:
    """Return (upright_anchors, reversed_anchors) without shared name tokens."""
    rng = card.get("meaning_range") if isinstance(card.get("meaning_range"), dict) else {}
    upright = _tokens_from_texts(_upright_anchor_texts(rng), limit=24)
    reversed_ = _tokens_from_texts(_reversed_anchor_texts(rng), limit=24)
    # Tokens that appear in both poles cannot prove orientation either way.
    shared = set(upright) & set(reversed_)
    upright = [t for t in upright if t not in shared]
    reversed_ = [t for t in reversed_ if t not in shared]
    return upright, reversed_


def _cards_linked(blob: str, pack: dict[str, Any]) -> bool:
    """Grounding in card semantics — not a card-name checklist.

    Card-name ablation principle: good answers may omit names if scenes/conflicts land.
    """
    cards = [c for c in (pack.get("cards") or []) if isinstance(c, dict)]
    if len(cards) < 2:
        return True
    low = blob.lower()
    hits = 0
    for card in cards:
        anchors = _card_semantic_anchors(card)
        if anchors and any(a in low for a in anchors):
            hits += 1
            continue
        # Fallback: full name present
        base = _card_display_base(card).lower()
        if base and base in low:
            hits += 1
    return hits >= min(2, len(cards))


def _orientation_grounded(blob: str, pack: dict[str, Any]) -> bool:
    """Reject upright-pole prose for reversed cards (and the reverse).

    A card is orientation-mismatched when the blob hits only the wrong pole's
    distinctive anchors. Unmentioned cards are ignored here; ``_cards_linked``
    still enforces overall semantic presence.
    """
    cards = [c for c in (pack.get("cards") or []) if isinstance(c, dict)]
    if not cards:
        return True
    low = blob.lower()
    for card in cards:
        upright, reversed_ = _card_pole_anchors(card)
        orient = str(card.get("orientation") or "upright").strip().lower()
        hits_up = bool(upright) and any(a in low for a in upright)
        hits_rev = bool(reversed_) and any(a in low for a in reversed_)
        if orient == "reversed":
            if not reversed_:
                continue
            if hits_up and not hits_rev:
                return False
        else:
            if not upright:
                continue
            if hits_rev and not hits_up:
                return False
    return True


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


def _card_name_needles(pack: dict[str, Any]) -> list[str]:
    needles: list[str] = []
    for card in pack.get("cards") or []:
        if not isinstance(card, dict):
            continue
        for key in ("name_ru", "name"):
            raw = str(card.get(key) or "").strip()
            base = re.sub(r"\s*\(перевёрнутый\)\s*$", "", raw, flags=re.I).strip().lower()
            if len(base) >= 4:
                needles.append(base)
            # Distinctive last token: «десятка кубков» → «кубков» already in lexicon;
            # keep full name and first significant word ≥4.
            for tok in re.findall(r"[^\W\d_]{4,}", base, flags=re.UNICODE):
                if tok not in _ANCHOR_STOP and tok not in {"карта", "карты"}:
                    needles.append(tok)
    return list(dict.fromkeys(needles))


def _user_facing_jargon_hit(answer: str, step: str, pack: dict[str, Any]) -> bool:
    """True when direct_answer / next_step leak tarot jargon or card names."""
    blob = f"{answer} {step}".lower()
    if any(j in blob for j in _USER_FACING_JARGON):
        return True
    # Spread metaphors that require knowing the draw.
    if re.search(r"картин\w*\s+(десятк|паж|рыцар|корол|дам|туз)", blob):
        return True
    for needle in _card_name_needles(pack):
        if needle and needle in blob:
            return True
    return False


# Soft length budget: choice spreads often need slightly longer story before
# option notes absorb A/B detail; hard reject only past this ceiling.
_FIELD_MAX_CHARS = 1200
_FIELD_MAX_CHARS_CHOICE_STORY = 1400


def _antithesis_formula_hits(text: str) -> int:
    """Count rhetorical short verb/adjective «не X, а Y» / «not X, but Y»."""
    blob = str(text or "")
    hits = 0
    for match in _ANTITHESIS_NE_A_RE.finditer(blob):
        left, right = match.group(1), match.group(2)
        if _ANTITHESIS_VERBISH_RE.search(left) and _ANTITHESIS_VERBISH_RE.search(right):
            hits += 1
    for match in _ANTITHESIS_NOT_BUT_RE.finditer(blob):
        left, right = match.group(1), match.group(2)
        if len(left) >= 3 and len(right) >= 3:
            hits += 1
    return hits


def quality_reject_reason(fields: dict[str, str], pack: dict[str, Any]) -> str | None:
    """Return reject reason or None if quality gates pass."""
    symbols = fields["symbols_overview"]
    story = fields["question_story"]
    answer = fields["direct_answer"]
    step = fields["next_step"]
    option_a = fields.get("option_a_note") or ""
    option_b = fields.get("option_b_note") or ""
    blob = f"{symbols} {story} {answer} {step} {option_a} {option_b}"

    is_choice = bool(
        pack.get("spread_kind") == "choice" or pack.get("response_shape", {}).get("choice_compare")
    )
    for key, text in fields.items():
        limit = _FIELD_MAX_CHARS
        if is_choice and key == "question_story":
            limit = _FIELD_MAX_CHARS_CHOICE_STORY
        if key == "next_step":
            limit = _NEXT_STEP_MAX_CHARS
        if key in {"option_a_note", "option_b_note"}:
            limit = _OPTION_NOTE_MAX_CHARS
        if len(text) > limit:
            return f"too_long:{key}"
        if len(text) < 20 and key in {"symbols_overview", "question_story", "direct_answer"}:
            return f"too_short:{key}"

    # Prose voice: antithesis in story/answer/symbols — not in option notes (choice may contrast).
    prose = f"{symbols} {story} {answer}"
    if _antithesis_formula_hits(prose) >= 1:
        return "antithesis_formula"

    if _near_dup(symbols, story) or _near_dup(story, answer) or _near_dup(answer, step):
        return "cross_field_duplicate"

    q = str(pack.get("question") or "")
    if _count_question_mentions(blob, q) > 1:
        return "question_repeated"

    if _profile_leaked(blob, pack):
        return "profile_verbatim"

    if not _cards_linked(blob, pack):
        return "cards_not_linked"

    if not _orientation_grounded(blob, pack):
        return "orientation_not_grounded"

    if _user_facing_jargon_hit(answer, step, pack):
        return "user_facing_jargon"

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
    max_attempts: int = 3,
) -> dict[str, str] | None:
    """Generate interpretation from context pack. None if LLM unavailable/invalid.

    Uses ``background`` LLM timeout budget — DeepSeek-V4-Pro + ~16k pack typically
    needs ~20s; default sync 12s was cutting successful generations mid-flight.
    """
    if not is_llm_chat_configured():
        return None
    with llm_operation("background"):
        client = get_openai_compatible_client()
    if client is None:
        return None

    user_full = json.dumps(pack, ensure_ascii=False)
    user_sent = user_full[:16000]
    attempts = max(1, min(int(max_attempts or 1), 3))
    model = resolve_default_chat_model()
    from todayflow_backend.services.llm_practitioner_persona_v1 import with_practitioner_persona

    system = with_practitioner_persona(_SYSTEM_RU, locale="ru")

    for attempt_idx in range(attempts):
        content = chat_completion_text(
            client,
            model=model,
            messages=[
                {"role": "system", "content": system},
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
        # Distinguishes empty/parse/clean failures from quality rejects for ops/eval.
        if not content:
            reason = "empty_content"
        elif not parsed:
            reason = "json_parse"
        else:
            probe = {
                k: _clean_field(parsed.get(k), min_words=mw)
                for k, mw in (
                    ("symbols_overview", 8),
                    ("question_story", 8),
                    ("direct_answer", 6),
                    ("next_step", 5),
                )
            }
            missing = [k for k, v in probe.items() if not v]
            if missing:
                reason = f"clean_failed:{','.join(missing)}"
            else:
                cleaned_fields = {k: str(v) for k, v in probe.items() if v}
                reason = quality_reject_reason(cleaned_fields, pack) or "unknown_reject"
        logger.warning("tarot_llm validation failed attempt=%s reason=%s", attempt_idx, reason)
    return None

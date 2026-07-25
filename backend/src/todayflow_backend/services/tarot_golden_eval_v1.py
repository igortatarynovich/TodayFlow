"""Tarot Golden Eval v1 — rubric + shape checks over Golden Dataset answers.

Canon: docs/tarot/TAROT_GOLDEN_EVAL_V1.md
Does not change public tarot_answer_v1 or the interpretation pipeline.
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from typing import Any

RUBRIC_KEYS = (
    "answered_question",
    "clarity",
    "story_not_card_list",
    "symbolism_natural",
    "practical_use",
    "no_repetition",
    "no_false_confidence",
    "want_to_finish",
)

_CARD_LIST_RE = re.compile(
    r"(карта\s*\d|карта\s*[一二三]|сначала\s+карта|затем\s+карта|позиция\s+\d)",
    re.IGNORECASE,
)
_ARKAN_RE = re.compile(r"\bаркан\b", re.IGNORECASE)
_FALSE_CONF_RE = re.compile(
    r"(точно\s+(уйд|любит|уволят|думает)|гарантированно|обязательно\s+случится|"
    r"он\s+точно|она\s+точно|он\s+думает|она\s+думает|он\s+хочет\s+только)",
    re.IGNORECASE,
)
_DATE_RE = re.compile(
    r"(\b\d{1,2}[./]\d{1,2}([./]\d{2,4})?\b|\b(понедельник|вторник|среда|четверг|пятница|суббота|воскресенье)\s+\d{1,2}\b|"
    r"\b\d{1,2}\s+(января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря)\b)",
    re.IGNORECASE,
)
_OPTION_RE = re.compile(r"(вариант\s*[abаб]|путь\s*[abаб]|остаться|уйти|с одной стороны|с другой)", re.IGNORECASE)


def _norm(text: str | None) -> str:
    return re.sub(r"\s+", " ", (text or "").strip().lower())


def _tokens(text: str) -> set[str]:
    return {t for t in re.findall(r"[a-zA-Zа-яА-ЯёЁ0-9]{3,}", text.lower())}


def _word_count(text: str) -> int:
    return len(re.findall(r"\S+", text or ""))


def _clamp_score(value: float) -> int:
    return max(1, min(5, int(round(value))))


def _sentence_chunks(text: str) -> list[str]:
    parts = re.split(r"[.!?…]+", text or "")
    return [p.strip() for p in parts if len(p.strip()) > 12]


def jaccard(a: str, b: str) -> float:
    ta, tb = _tokens(a), _tokens(b)
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def mean_pairwise_similarity(texts: Iterable[str]) -> float | None:
    items = [t for t in texts if _norm(t)]
    if len(items) < 2:
        return None
    total = 0.0
    n = 0
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            total += jaccard(items[i], items[j])
            n += 1
    return total / n if n else None


def check_answer_shape(
    *,
    flags: list[str] | None,
    interpretation: dict[str, str] | None,
    pack: dict[str, Any] | None,
    scenario: dict[str, Any] | None = None,
) -> dict[str, bool]:
    """Structural checks from Dataset expect.answer_shape."""
    flags = list(flags or [])
    interp = interpretation or {}
    pack = pack or {}
    text = " ".join(
        str(interp.get(k) or "")
        for k in ("symbols_overview", "question_story", "direct_answer", "next_step")
    )
    out: dict[str, bool] = {}

    for flag in flags:
        if flag == "no_arkan_label":
            blob = text + " " + str(pack)
            out[flag] = "аркан" not in blob.lower()
        elif flag == "direct_answer":
            out[flag] = _word_count(interp.get("direct_answer") or "") >= 6
        elif flag == "next_step":
            out[flag] = _word_count(interp.get("next_step") or "") >= 5
        elif flag == "one_story":
            out[flag] = not bool(_CARD_LIST_RE.search(text))
        elif flag == "compare_options":
            out[flag] = bool(_OPTION_RE.search(text)) if interp else False
        elif flag == "no_other_mind_as_fact":
            out[flag] = not bool(
                re.search(r"\b(он|она)\s+(точно\s+)?(думает|хочет|любит|изменит)\b", text, re.I)
            )
        elif flag == "no_exact_date":
            out[flag] = not bool(_DATE_RE.search(text))
        elif flag == "distinct_minors":
            cards = (pack.get("cards") or []) if pack else []
            scenes = []
            for card in cards:
                rng = card.get("meaning_range") if isinstance(card, dict) else None
                if not isinstance(rng, dict):
                    continue
                cid = int(card.get("card_id") or -1)
                if cid >= 22:
                    scenes.append(_norm(str(rng.get("core_scene") or "")))
            scenes = [s for s in scenes if s]
            out[flag] = len(scenes) < 2 or len(set(scenes)) == len(scenes)
        elif flag == "card_name_ablation_ready":
            # Heuristic: after stripping known card names, remaining text still long enough
            # and not identical to a pure name list.
            names = []
            for card in (scenario or {}).get("cards") or []:
                names.append(str(card.get("title") or ""))
            for card in pack.get("cards") or []:
                if isinstance(card, dict):
                    names.append(str(card.get("name_ru") or ""))
            stripped = text
            for name in names:
                if name:
                    stripped = stripped.replace(name, " ")
            stripped = _norm(stripped)
            out[flag] = _word_count(stripped) >= 20 and not bool(_CARD_LIST_RE.search(stripped))
        else:
            out[flag] = False
    return out


def score_rubric_heuristic(
    interpretation: dict[str, str] | None,
    *,
    question: str | None = None,
    answer_shape: dict[str, bool] | None = None,
) -> dict[str, int | None]:
    """Map answer text → 1–5 rubric using deterministic heuristics (not human judgment)."""
    if not interpretation:
        return {k: None for k in RUBRIC_KEYS}

    symbols = interpretation.get("symbols_overview") or ""
    story = interpretation.get("question_story") or ""
    answer = interpretation.get("direct_answer") or ""
    step = interpretation.get("next_step") or ""
    text = f"{symbols} {story} {answer} {step}".strip()
    shape = answer_shape or {}

    q_tokens = _tokens(question or "")
    a_tokens = _tokens(answer)
    overlap = (len(q_tokens & a_tokens) / max(1, len(q_tokens))) if q_tokens else 0.0

    answered = 2.0 + overlap * 4.0
    if shape.get("direct_answer"):
        answered += 0.5
    if "не удалось собрать полноценную интерпретацию" in _norm(answer):
        answered = 1.0

    clarity = 2.0
    wc = _word_count(answer)
    if 25 <= wc <= 180:
        clarity = 4.5
    elif 12 <= wc < 25 or 180 < wc <= 260:
        clarity = 3.5
    elif wc > 260:
        clarity = 2.5

    story_score = 2.0 if _CARD_LIST_RE.search(text) else 4.5
    if shape.get("one_story") is True:
        story_score = max(story_score, 4.0)
    if shape.get("one_story") is False:
        story_score = min(story_score, 2.0)

    symbolism = 4.0
    if _ARKAN_RE.search(text):
        symbolism = 1.0
    elif _word_count(symbols) < 8:
        symbolism = 2.5
    elif shape.get("distinct_minors") is False:
        symbolism = 2.0

    practical = 4.5 if _word_count(step) >= 5 else 1.5
    if shape.get("next_step") is False:
        practical = 1.0

    chunks = _sentence_chunks(text)
    if len(chunks) >= 2:
        sims = [jaccard(chunks[i], chunks[i + 1]) for i in range(len(chunks) - 1)]
        avg = sum(sims) / len(sims)
        no_rep = 4.5 if avg < 0.45 else (3.0 if avg < 0.65 else 1.5)
    else:
        no_rep = 3.0

    false_conf = 2.0 if _FALSE_CONF_RE.search(text) else 4.5
    if shape.get("no_other_mind_as_fact") is False or shape.get("no_false_confidence") is False:
        false_conf = min(false_conf, 2.0)
    if shape.get("no_exact_date") is False:
        false_conf = min(false_conf, 2.5)

    finish = 2.0
    total_wc = _word_count(text)
    if 60 <= total_wc <= 420 and _word_count(step) >= 5:
        finish = 4.5
    elif total_wc >= 40:
        finish = 3.5

    return {
        "answered_question": _clamp_score(answered),
        "clarity": _clamp_score(clarity),
        "story_not_card_list": _clamp_score(story_score),
        "symbolism_natural": _clamp_score(symbolism),
        "practical_use": _clamp_score(practical),
        "no_repetition": _clamp_score(no_rep),
        "no_false_confidence": _clamp_score(false_conf),
        "want_to_finish": _clamp_score(finish),
    }


def rubric_mean(scores: dict[str, int | None]) -> float | None:
    vals = [int(v) for v in scores.values() if isinstance(v, int)]
    if not vals:
        return None
    return sum(vals) / len(vals)


def paid_worth_heuristic(scores: dict[str, int | None]) -> bool | None:
    """Auto paid-worth only when rubric is complete; conservative."""
    mean = rubric_mean(scores)
    if mean is None:
        return None
    return mean >= 4.0 and all((scores.get(k) or 0) >= 3 for k in RUBRIC_KEYS)


def summarize_gates(
    *,
    shape_results: list[dict[str, bool]],
    rubric_means: list[float],
    anti_sameness_mean: float | None,
    anti_sameness_threshold: float = 0.55,
    rubric_threshold: float = 3.5,
) -> dict[str, bool]:
    critical_flags = ("no_arkan_label", "direct_answer", "next_step")
    shape_ok = True
    for shape in shape_results:
        for flag in critical_flags:
            if flag in shape and shape[flag] is False:
                shape_ok = False
    anti_ok = True if anti_sameness_mean is None else anti_sameness_mean < anti_sameness_threshold
    rubric_ok = bool(rubric_means) and (sum(rubric_means) / len(rubric_means) >= rubric_threshold)
    return {
        "critical_shape_pass": shape_ok,
        "anti_sameness_pass": anti_ok,
        "rubric_mean_pass": rubric_ok,
        "freeze_lift_ready": shape_ok and anti_ok and rubric_ok,
    }

"""Tarot Question Ontology v1 — what kind of decision the reading must serve.

Canon: docs/tarot/TAROT_QUESTION_ONTOLOGY_V1.md
Data: DATA/reference/tarot/question_ontology_v1/types.json
"""

from __future__ import annotations

import json
import logging
import os
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

CONTRACT_VERSION = "tarot_question_ontology_v1"

DEFAULT_DATA_ROOT = Path(__file__).resolve().parents[4] / "DATA"
TYPES_PATH = (
    Path(os.getenv("TODAYFLOW_DATA_DIR", DEFAULT_DATA_ROOT))
    / "reference"
    / "tarot"
    / "question_ontology_v1"
    / "types.json"
)

QUESTION_TYPES = frozenset(
    {
        "choice",
        "relationship_state",
        "relationship_intent",
        "work_decision",
        "money_decision",
        "conflict",
        "self_state",
        "direction",
        "timing_readiness",
        "open_reflection",
    }
)

DOMAINS = frozenset({"work", "relationship", "money", "self", "family", "creative", "general"})
INTENTS = frozenset({"understand", "choose", "act", "clarify", "prepare"})
HORIZONS = frozenset({"near_term", "mid_term", "open"})

# concern_domain / legacy UI chips → ontology domain
_CONCERN_TO_DOMAIN: dict[str, str] = {
    "work": "work",
    "work_change": "work",
    "career": "work",
    "relationships": "relationship",
    "relationship": "relationship",
    "love": "relationship",
    "money": "money",
    "finance": "money",
    "family": "family",
    "growth": "self",
    "inner_state": "self",
    "self": "self",
    "decision": "general",
    "conflict": "general",
    "creative": "creative",
    "other": "general",
    "general": "general",
}

# ontology domain → legacy question_domain (profile / KB facet bridge)
_DOMAIN_TO_LEGACY: dict[str, str] = {
    "work": "work",
    "relationship": "relationships",
    "money": "money",
    "self": "inner_state",
    "family": "family",
    "creative": "growth",
    "general": "general",
}

_DEFAULT_INTENT_BY_TYPE: dict[str, str] = {
    "choice": "choose",
    "relationship_state": "understand",
    "relationship_intent": "clarify",
    "work_decision": "choose",
    "money_decision": "choose",
    "conflict": "clarify",
    "self_state": "understand",
    "direction": "act",
    "timing_readiness": "prepare",
    "open_reflection": "understand",
}


@lru_cache(maxsize=1)
def _load_payload() -> dict[str, Any]:
    if not TYPES_PATH.is_file():
        logger.warning("tarot_question_ontology_v1 missing at %s", TYPES_PATH)
        return {}
    with TYPES_PATH.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        return {}
    if data.get("contract_version") != CONTRACT_VERSION:
        logger.warning(
            "tarot_question_ontology_v1 unexpected contract_version=%s",
            data.get("contract_version"),
        )
    return data


@lru_cache(maxsize=1)
def types_by_id() -> dict[str, dict[str, Any]]:
    payload = _load_payload()
    rows = payload.get("types") if isinstance(payload, dict) else None
    if not isinstance(rows, list):
        return {}
    out: dict[str, dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        tid = str(row.get("question_type") or "").strip()
        if tid:
            out[tid] = row
    return out


def _norm(text: str | None) -> str:
    return re.sub(r"\s+", " ", (text or "").strip().lower())


def _infer_domain(text: str, concern_domain: str | None) -> str:
    chip = _CONCERN_TO_DOMAIN.get((concern_domain or "").strip().lower())
    # Text overrides chip when clear.
    if any(w in text for w in ("работ", "карьер", "увольн", "начальник", "коллег", "оффер", "должност")):
        return "work"
    if any(w in text for w in ("деньг", "доход", "финанс", "трат", "бюджет", "долг", "вложен")):
        return "money"
    if any(w in text for w in ("семь", "родител", "ребён", "ребен", "мама", "папа")):
        return "family"
    if any(
        w in text
        for w in (
            "отношен",
            "партнёр",
            "партнер",
            "любов",
            "бывш",
            "муж",
            "жен",
            "он ",
            "она ",
            "его ",
            "её ",
            "ее ",
        )
    ):
        return "relationship"
    if any(w in text for w in ("творч", "проект", "книг", "музык", "рис")):
        return "creative"
    if any(w in text for w in ("тревог", "апати", "настроен", "устал", "устала", "себе", "мне внутри")):
        return "self"
    if chip in DOMAINS:
        return chip
    return "general"


def _infer_horizon(text: str) -> str:
    if any(w in text for w in ("сегодня", "завтра", "на этой неделе", "в ближайш", "сейчас же", "срочн")):
        return "near_term"
    if any(w in text for w in ("в этом году", "через месяц", "к лету", "долгосроч", "через год")):
        return "mid_term"
    if any(w in text for w in ("когда", "в какой момент", "пора ли", "время ли")):
        return "near_term"
    return "open"


def _infer_intent(text: str, question_type: str) -> str:
    if any(w in text for w in ("стоит ли", "выбрат", "или ", " какой вариант", "что выбрать")):
        return "choose"
    if any(w in text for w in ("что сделать", "как действ", "какой шаг", "как поступ")):
        return "act"
    if any(w in text for w in ("проясн", "понять точнее", "разобрат", "в чём дело")):
        return "clarify"
    if any(w in text for w in ("подготов", "к чему готов", "как подготовиться", "пора ли")):
        return "prepare"
    if any(w in text for w in ("что происходит", "как обстоят", "что важно понять", "что значит")):
        return "understand"
    return _DEFAULT_INTENT_BY_TYPE.get(question_type, "understand")


def _infer_question_type(text: str, *, spread_kind: str | None, domain: str) -> str:
    # Relationship intent — mind-reading pressure (before timing/"когда").
    if any(
        w in text
        for w in (
            "что он думает",
            "что она думает",
            "что он хочет",
            "что она хочет",
            "его намерен",
            "её намерен",
            "ее намерен",
            "что у него на уме",
            "что у неё на уме",
            "что у нее на уме",
            "любит ли он",
            "любит ли она",
            "вернётся ли он",
            "вернется ли он",
            "какие у него чувств",
            "какие у неё чувств",
            "какие у нее чувств",
        )
    ):
        return "relationship_intent"

    # Timing readiness — readiness of the moment, not a calendar date.
    timing_hit = bool(
        re.search(r"(^|\s)когда(\s|\?|$)", text)
        or any(
            w in text
            for w in (
                "в какой момент",
                "пора ли",
                "время ли",
                "готов ли момент",
                "сейчас подходящ",
                "рано ли",
                "поздно ли",
                "готовность момента",
            )
        )
    )
    if timing_hit:
        return "timing_readiness"

    # Choice / fork.
    choice_markers = (
        " или ",
        "стоит ли",
        "выбор между",
        "выбрать между",
        "какой вариант",
        "что выбрать",
        "уйти или",
        "остаться или",
        "сменить или",
        "а или б",
        "вариант a",
        "вариант б",
    )
    if any(m in text for m in choice_markers) or (spread_kind or "").strip().lower() == "choice":
        return "choice"

    if any(w in text for w in ("конфликт", "ссор", "спор", "руга", "война с", "не договарива")):
        return "conflict"

    if domain == "money" or any(w in text for w in ("деньг", "доход", "трат", "бюджет", "вложен", "кредит")):
        return "money_decision"

    if domain == "work" or any(w in text for w in ("работ", "карьер", "увольн", "начальник", "коллег", "оффер")):
        return "work_decision"

    if domain == "relationship" or any(
        w in text for w in ("отношен", "партнёр", "партнер", "любов", "бывш", "близост")
    ):
        return "relationship_state"

    if any(w in text for w in ("тревог", "апати", "настроен", "устал", "устала", "внутри", "мне плохо", "мне тяжело")):
        return "self_state"

    if (
        any(
            w in text
            for w in (
                "куда двигаться",
                "в каком направлен",
                "какой путь",
                "куда идти",
                "куда дальше",
                "вектор",
            )
        )
        or ("куда" in text and any(w in text for w in ("двига", "йти", "путь", "направлен")))
    ):
        return "direction"

    if any(
        w in text
        for w in (
            "что мне важно",
            "что важно увидеть",
            "что происходит в моей жизни",
            "общий совет",
            "что сказать карты",
            "что мне нужно знать",
        )
    ) or len(text) < 18:
        return "open_reflection"

    if domain == "self":
        return "self_state"
    if domain == "family":
        return "relationship_state"
    return "open_reflection"


def classify_question(
    question: str | None,
    *,
    concern_domain: str | None = None,
    spread_kind: str | None = None,
) -> dict[str, Any]:
    """Deterministic ontology classification + interpretation instructions for the pack."""
    text = _norm(question)
    domain = _infer_domain(text, concern_domain)
    qtype = _infer_question_type(text, spread_kind=spread_kind, domain=domain)
    if qtype not in QUESTION_TYPES:
        qtype = "open_reflection"
    intent = _infer_intent(text, qtype)
    if intent not in INTENTS:
        intent = _DEFAULT_INTENT_BY_TYPE.get(qtype, "understand")
    horizon = _infer_horizon(text)
    if horizon not in HORIZONS:
        horizon = "open"

    # Special case from owner: work change choice.
    if qtype == "choice" and domain == "work":
        intent = "choose"
        if horizon == "open":
            horizon = "near_term"

    type_row = types_by_id().get(qtype) or types_by_id().get("open_reflection") or {}
    legacy = _DOMAIN_TO_LEGACY.get(domain, "general")
    if qtype == "choice" and domain == "work":
        legacy = "work_change"
    elif qtype == "conflict":
        legacy = "conflict"
    elif qtype == "self_state":
        legacy = "inner_state"
    elif qtype in {"relationship_state", "relationship_intent"}:
        legacy = "relationships"

    must_show = [str(x).strip() for x in (type_row.get("must_show") or []) if str(x).strip()]
    must_not = [str(x).strip() for x in (type_row.get("must_not_claim") or []) if str(x).strip()]

    return {
        "question_type": qtype,
        "domain": domain,
        "intent": intent,
        "decision_horizon": horizon,
        "central_task": str(type_row.get("central_task") or "").strip(),
        "direct_answer_means": str(type_row.get("direct_answer_means") or "").strip(),
        "must_show": must_show,
        "allowed_specificity": str(type_row.get("allowed_specificity") or "").strip(),
        "must_not_claim": must_not,
        "next_step_kind": str(type_row.get("next_step_kind") or "").strip(),
        "legacy_question_domain": legacy,
    }


def pack_question_ontology(
    question: str | None,
    *,
    concern_domain: str | None = None,
    spread_kind: str | None = None,
) -> dict[str, Any]:
    """Subset for Context Pack (no internal bridge fields required by LLM)."""
    full = classify_question(question, concern_domain=concern_domain, spread_kind=spread_kind)
    return {
        "question_type": full["question_type"],
        "domain": full["domain"],
        "intent": full["intent"],
        "decision_horizon": full["decision_horizon"],
        "central_task": full["central_task"],
        "direct_answer_means": full["direct_answer_means"],
        "must_show": full["must_show"],
        "allowed_specificity": full["allowed_specificity"],
        "must_not_claim": full["must_not_claim"],
        "next_step_kind": full["next_step_kind"],
    }

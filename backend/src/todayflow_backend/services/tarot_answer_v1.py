"""Tarot Answer v1 — single canonical artifact for spread result (question-first reading)."""

from __future__ import annotations

from typing import Any

from todayflow_backend.core import models
from todayflow_backend.services.tarot_reading_synthesis import compose_question_first_reading

TAROT_ANSWER_V1_CONTRACT = "tarot_answer_v1"
TAROT_ANSWER_PROMPT_VER = "tarot-answer-v1-template"


def tarot_reading_to_answer_v1(
    reading: models.TarotSpreadReading | dict[str, Any],
    *,
    question: str | None = None,
    concern_domain: str | None = None,
    spread_id: str | None = None,
    generation_id: str | None = None,
) -> dict[str, Any]:
    """Normalize spread reading → tarot_answer_v1 contract."""
    src = reading.model_dump() if hasattr(reading, "model_dump") else dict(reading)
    main = str(src.get("meaning") or "").strip()
    story = str(src.get("synthesis_why") or "").strip()
    holding = str(src.get("insight_holding") or "").strip()
    shifting = str(src.get("insight_shifting") or "").strip()
    attention = str(src.get("insight_attention") or "").strip()
    today = str(src.get("today_suggestion") or src.get("next_step") or "").strip()
    chips_raw = src.get("follow_up_chips") if isinstance(src.get("follow_up_chips"), list) else []
    chips: list[dict[str, str]] = []
    for c in chips_raw:
        if hasattr(c, "model_dump"):
            chips.append(c.model_dump())
        elif isinstance(c, dict):
            chips.append({"id": str(c.get("id") or ""), "label": str(c.get("label") or "")})

    return {
        "contract_version": TAROT_ANSWER_V1_CONTRACT,
        "question_text": (question or "").strip(),
        "concern_domain": (concern_domain or "").strip(),
        "spread_id": (spread_id or "").strip(),
        "main_answer": main,
        "story_narrative": story,
        "new_angle": main,
        "hidden_factor": holding,
        "risk": shifting,
        "attention": attention,
        "next_step": today,
        "today_suggestion": today,
        "insights": {
            "holding": holding,
            "shifting": shifting,
            "attention": attention,
        },
        "follow_up_prompt": str(src.get("follow_up_prompt") or "").strip(),
        "follow_up_chips": chips,
        "generation_id": generation_id or "",
        "synthesis_mode": "template_v1",
    }


def compose_tarot_answer_v1(
    spread: models.TarotSpreadResult,
    *,
    question: str | None = None,
    concern_domain: str | None = None,
    consistency: dict | None = None,
    core_profile: dict | None = None,
    generation_id: str | None = None,
) -> tuple[models.TarotSpreadReading, dict[str, Any]]:
    """Build legacy reading + canonical tarot_answer_v1 from one synthesis pass."""
    reading = compose_question_first_reading(
        spread,
        question=question,
        concern_domain=concern_domain,
        consistency=consistency,
        core_profile=core_profile,
    )
    answer = tarot_reading_to_answer_v1(
        reading,
        question=question,
        concern_domain=concern_domain,
        spread_id=spread.spread_id,
        generation_id=generation_id,
    )
    return reading, answer

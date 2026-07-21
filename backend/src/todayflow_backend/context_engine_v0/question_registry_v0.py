"""Question → sphere mapping for profile spheres synthesis (three questions).

Frozen helper — not a product-wide registry to grow.
"""

from __future__ import annotations

from todayflow_backend.context_engine_v0.types_v0 import QuestionSpec

QUESTION_REGISTRY_VERSION = "question_registry_v0.1"

# question_id → spec
QUESTION_SPECS: dict[str, QuestionSpec] = {
    "q.relationships.v1": {
        "question_id": "q.relationships.v1",
        "domain": "relationships",
        "sphere_id": "love",
        "user_question": "Как базовые особенности проявляются в близости и любви?",
        "user_value": (
            "Понять, как ты входишь в близость, какое условие тебе нужно, "
            "где возникает напряжение и какой один шаг помогает"
        ),
        "prompt_id": "profile.spheres.synthesis.v1",
        "style_fact_id": "profile.style.relationship",
        "style_key": "relationship_style",
        "natal_planets": ["venus", "sun"],
        "house_numbers": ["7"],
        "living_fact_ids": [],
        "patterns_fact_ids": [],
    },
    "q.money.v1": {
        "question_id": "q.money.v1",
        "domain": "money",
        "sphere_id": "money",
        "user_question": "Как базовые особенности проявляются в деньгах и чувстве ценности?",
        "user_value": (
            "Понять, как ты обращаешься с ресурсом, где риск, "
            "и какой один практический фокус помогает"
        ),
        "prompt_id": "profile.spheres.synthesis.v1",
        "style_fact_id": "profile.style.money",
        "style_key": "money_style",
        "natal_planets": ["jupiter", "saturn", "sun"],
        "house_numbers": ["2", "8"],
        "living_fact_ids": [],
        "patterns_fact_ids": [],
    },
    "q.decisions.v1": {
        "question_id": "q.decisions.v1",
        "domain": "decision_making",
        "sphere_id": "decisions",
        "user_question": "Как базовые особенности проявляются в решениях и дисциплине выбора?",
        "user_value": (
            "Понять, как ты выбираешь, где застреваешь, "
            "и какой один шаг гигиены решения помогает"
        ),
        "prompt_id": "profile.spheres.synthesis.v1",
        "style_fact_id": "profile.style.decision",
        "style_key": "decision_style",
        "natal_planets": ["saturn", "mercury", "sun"],
        "house_numbers": ["9"],
        "living_fact_ids": [],
        "patterns_fact_ids": [],
    },
}

# Legacy sphere chrome → question_id
SPHERE_TO_QUESTION: dict[str, str] = {
    "love": "q.relationships.v1",
    "money": "q.money.v1",
    "decisions": "q.decisions.v1",
}


def get_question_spec(question_id: str) -> QuestionSpec | None:
    return QUESTION_SPECS.get(question_id)


def question_id_for_sphere(sphere_id: str) -> str | None:
    return SPHERE_TO_QUESTION.get(sphere_id)


def list_question_ids() -> list[str]:
    return sorted(QUESTION_SPECS.keys())

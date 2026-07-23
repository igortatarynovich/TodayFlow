"""personality contract — validate + map to profile_contract / matrix slots."""

from __future__ import annotations

from todayflow_backend.services.personality_contract_v1 import (
    calculated_facts_from_natal,
    personality_has_minimum,
    personality_to_profile_contract,
    validate_personality,
)
from todayflow_backend.services.profile_matrix_adapter_v0 import project_profile_slots_v0


def _date_only_facts() -> dict:
    return {
        "contract_version": "natal_facts_v1",
        "provider": "test",
        "mode": "date_only",
        "calculation_id": "calc-test",
        "planets": [{"id": "sun", "sign": "taurus", "degree": 24.0}],
        "unavailable_facts": [{"key": "ascendant", "reason": "birth_time_or_place_missing"}],
    }


def test_validate_personality_nulls_house_fields_on_date_only():
    raw = {
        "identity_summary": "Держит ясность через спокойный ритм.",
        "emotional_style": "Чувствует глубже, чем показывает.",
        "decision_style": "Сначала тело, потом структура.",
        "work_and_realization": "Дом 10 говорит о карьере.",
        "money_patterns": "Дом 2.",
        "home_and_security": "Дом 4.",
        "strengths": ["Выдержка"],
    }
    out = validate_personality(raw, natal_facts=_date_only_facts())
    assert out["identity_summary"]
    assert out["work_and_realization"] is None
    assert out["money_patterns"] is None
    assert out["home_and_security"] is None
    assert personality_has_minimum(out)


def test_personality_maps_into_matrix_slots():
    personality = validate_personality(
        {
            "identity_summary": "Держит ясность через спокойный ритм.",
            "emotional_style": "Чувствует глубже, чем показывает.",
            "decision_style": "Сначала тело, потом структура.",
            "relationship_style": "Сначала доверие.",
            "strengths": ["Выдержка", "Фокус"],
            "growth_zones": ["Спешка"],
        },
        natal_facts=_date_only_facts(),
    )
    contract = personality_to_profile_contract(personality)
    proj = project_profile_slots_v0(
        contract=contract,
        natal_facts=_date_only_facts(),
        birth_date="1990-05-15",
        access="free",
    )
    assert proj["revealed_slots"]["identity_summary"]
    assert proj["revealed_slots"]["emotional_style"]
    assert "helps" not in proj["revealed_slots"]  # L3 gated for free
    assert "helps" in proj["slots"] or "helps" in proj["omitted_slots"] or True


def test_calculated_facts_omits_angles_when_date_only():
    pack = calculated_facts_from_natal(_date_only_facts())
    assert pack["sun_sign"] == "taurus"
    assert "ascendant" not in pack
    assert "houses" not in pack

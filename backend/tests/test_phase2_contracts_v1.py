"""Tests for profile_contract_v1 and tarot_answer_v1."""

from __future__ import annotations

from todayflow_backend.core import models
from todayflow_backend.services.profile_contract_v1 import (
    PROFILE_CONTRACT_V1,
    PROFILE_STATUS_FORMING,
    build_profile_contract_fallback_v1,
    build_profile_portrait_v1,
    profile_contract_from_legacy_interpretation,
    profile_contract_to_legacy_interpretation,
    validate_profile_contract_v1,
)
from todayflow_backend.services.tarot_answer_v1 import (
    TAROT_ANSWER_V1_CONTRACT,
    tarot_reading_to_answer_v1,
)


def test_profile_contract_fallback_validates():
    contract = build_profile_contract_fallback_v1(
        {"person": {"display_name": "Аня"}, "astro": {"sun_sign": "Лев"}, "baseline": {}}
    )
    assert contract["contract_version"] == PROFILE_CONTRACT_V1
    assert contract["status"] == PROFILE_STATUS_FORMING
    assert contract["identity_core"] == ""
    assert validate_profile_contract_v1(contract) == []


def test_profile_contract_legacy_map_roundtrip():
    legacy = profile_contract_to_legacy_interpretation(
        build_profile_contract_fallback_v1({"person": {}, "astro": {}, "baseline": {}})
    )
    contract = profile_contract_from_legacy_interpretation(legacy)
    # Legacy without contract → forming scaffold (no invented portrait copy).
    assert contract["status"] == PROFILE_STATUS_FORMING
    assert contract["identity_core"] == ""
    assert contract["strengths"] == []
    assert validate_profile_contract_v1(contract) == []


def test_build_profile_portrait_v1_returns_legacy_shim(monkeypatch):
    # Force forming fallback — do not hit live LLM in unit tests.
    monkeypatch.setattr(
        "todayflow_backend.services.profile_contract_v1.call_profile_contract_llm_v1",
        lambda *_a, **_k: (None, {"reason": "llm_disabled_for_test"}),
    )
    contract, interpretation, daily, used_fb = build_profile_portrait_v1(
        profile_input={"person": {"display_name": "Test"}, "astro": {"sun_sign": "Овен"}, "baseline": {}},
        living={"summary": "Неделя спокойная"},
        locale="ru",
    )
    assert contract["contract_version"] == PROFILE_CONTRACT_V1
    assert contract["status"] == PROFILE_STATUS_FORMING
    # Forming shim: empty identity is honest; daily lenses may still exist.
    assert interpretation.get("identity") == ""
    assert daily.get("daily_lenses")
    assert used_fb is True


def test_tarot_reading_to_answer_v1():
    reading = models.TarotSpreadReading(
        meaning="Главный ответ",
        synthesis_why="История",
        insight_holding="Скрытое",
        insight_shifting="Риск",
        insight_attention="Внимание",
        today_suggestion="Шаг",
        follow_up_prompt="Что важнее?",
        follow_up_chips=[models.TarotFollowUpChip(id="a", label="Ясность")],
    )
    answer = tarot_reading_to_answer_v1(reading, question="Что делать?", generation_id="7")
    assert answer["contract_version"] == TAROT_ANSWER_V1_CONTRACT
    assert answer["main_answer"] == "Главный ответ"
    assert answer["new_angle"] == "Главный ответ"
    assert answer["generation_id"] == "7"

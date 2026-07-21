"""Profile disclosure funnel — identity/styles/patterns + deterministic spheres."""

from __future__ import annotations

from typing import Any

from todayflow_backend.core.config import settings
from todayflow_backend.services import profile_disclosure_funnel_v0 as funnel
from todayflow_backend.services.profile_contract_v1 import (
    PROFILE_CONTRACT_PROMPT_VER,
    _normalize_profile_contract,
    profile_contract_to_legacy_interpretation,
)


def _living_eligible() -> dict[str, Any]:
    """Enough check-in signal for patterns generation_gate."""
    return {
        "summary": "Часто отмечаете перегруз к вечеру; сложные разговоры откладываются.",
        "signals": [
            {"day": "2026-07-14", "mood": "tired", "note": "не стала писать коллеге"},
            {"day": "2026-07-15", "mood": "ok", "note": "сделала дела по списку"},
            {"day": "2026-07-16", "mood": "anxious", "note": "разговор перенесла"},
        ],
        "signal_profile": {"signals_days": 8},
        "insights": ["откладывание сложных разговоров"],
    }


def _fake_call_factory(responses: list[Any]):
    def fake_call(
        system: str,
        user: str,
        *,
        depth_level: str = "normal",
        temperature: float = 0.48,
    ) -> tuple[dict[str, Any] | None, str | None]:
        assert system
        assert user
        assert temperature >= 0
        parsed = responses.pop(0) if responses else None
        if parsed is None:
            return None, None
        return parsed, "{}"

    return fake_call


def _identity() -> dict[str, Any]:
    return {
        "contract_version": funnel.IDENTITY_CONTRACT,
        "identity_core": "Человек держит смысл через ясный фокус и живой контакт.",
        "strengths": ["Фокус", "Контакт", "Доведение"],
        "growth_zones": ["Распыление", "Контроль", "Откладывание"],
    }


def _styles() -> dict[str, Any]:
    return {
        "contract_version": funnel.STYLES_CONTRACT,
        "relationship_style": "Близость через прямые слова и предсказуемость.",
        "money_style": "Деньги как ценность и спокойный шаг без импульса.",
        "decision_style": "Решения через один критерий и короткий дедлайн.",
    }


def _patterns() -> dict[str, Any]:
    return {
        "contract_version": funnel.PATTERNS_CONTRACT,
        "recurring_patterns": ["Часто берёт второй приоритет без слота."],
        "living_changes": "Сейчас усиливается запрос на один главный фокус и меньше параллельных обещаний.",
        "life_mission": "Удерживать свой ритм и не растворяться в чужих задачах.",
        "helps": ["Один фокус на день", "Пауза перед новым да"],
    }


def test_profile_funnel_patterns_then_deterministic_spheres(monkeypatch) -> None:
    monkeypatch.setattr(settings, "llm_quality_mode", "rich")
    monkeypatch.setattr(funnel, "is_llm_chat_configured", lambda: True)
    monkeypatch.setattr(funnel, "prefer_multi_step_funnels", lambda: True)
    responses = [_identity(), _styles(), _patterns()]

    monkeypatch.setattr(funnel, "_call", _fake_call_factory(responses))
    merged, meta = funnel.run_profile_disclosure_funnel_v0(
        {
            "person": {"display_name": "Игорь", "birth_date": "1990-01-01"},
            "astro": {"sun_sign": "Leo"},
            "living": _living_eligible(),
        },
        locale="ru",
    )
    assert meta["partial"] is True  # slice ≠ global ready
    assert meta["completed_steps"] == ["identity", "styles", "patterns", "spheres"]
    assert meta.get("spheres_source") == "deterministic_projector_v0_1"
    assert len(responses) == 0  # no LLM spheres call
    assert merged is not None
    assert merged["life_mission"]
    assert set(merged["life_spheres"].keys()) == {"love", "money", "decisions"}

    contract = _normalize_profile_contract(merged)
    assert contract["profile_snapshot_version"] == PROFILE_CONTRACT_PROMPT_VER
    assert contract["life_spheres"]["love"]["need"]
    legacy = profile_contract_to_legacy_interpretation(contract)
    assert "любв" in legacy["life_areas"]["love"].lower()
    assert len(legacy["life_areas"]["love"]) >= 20


def test_economize_skips_profile_funnel(monkeypatch) -> None:
    monkeypatch.setattr(settings, "llm_quality_mode", "economize")
    merged, meta = funnel.run_profile_disclosure_funnel_v0({}, locale="ru")
    assert merged is None
    assert meta["reason"] == "quality_mode_economize"


def test_patterns_failed_still_projects_spheres(monkeypatch) -> None:
    monkeypatch.setattr(settings, "llm_quality_mode", "rich")
    monkeypatch.setattr(funnel, "is_llm_chat_configured", lambda: True)
    monkeypatch.setattr(funnel, "prefer_multi_step_funnels", lambda: True)
    responses: list[dict[str, Any] | None] = [
        _identity(),
        _styles(),
        None,  # patterns fail (+ retry)
        None,
    ]

    monkeypatch.setattr(funnel, "_call", _fake_call_factory(responses))
    merged, meta = funnel.run_profile_disclosure_funnel_v0(
        {
            "person": {"display_name": "Игорь", "birth_date": "1990-01-01"},
            "astro": {"sun_sign": "Leo"},
            "living": _living_eligible(),
        },
        locale="ru",
    )
    assert meta["partial"] is True
    assert meta["reason"] == "patterns_failed"
    assert "spheres" in meta["completed_steps"]
    assert merged is not None
    assert merged["identity_core"]
    assert merged["relationship_style"]
    assert set(merged.get("life_spheres") or {}) == {"love", "money", "decisions"}
    assert merged.get("recurring_patterns") == []


def test_patterns_skipped_when_birth_only_projects_spheres(monkeypatch) -> None:
    """GENERATION_GATE patterns skip must not block deterministic spheres."""
    monkeypatch.setattr(settings, "llm_quality_mode", "rich")
    monkeypatch.setattr(funnel, "is_llm_chat_configured", lambda: True)
    monkeypatch.setattr(funnel, "prefer_multi_step_funnels", lambda: True)
    calls: list[str] = []
    responses = [_identity(), _styles()]

    def fake_call(
        system: str,
        user: str,
        *,
        depth_level: str = "normal",
        temperature: float = 0.48,
    ) -> tuple[dict[str, Any] | None, str | None]:
        calls.append(user[:80])
        parsed = responses.pop(0)
        return parsed, "{}"

    monkeypatch.setattr(funnel, "_call", fake_call)
    merged, meta = funnel.run_profile_disclosure_funnel_v0(
        {
            "person": {"first_name": "Аня", "birth_date": "1992-03-04"},
            "astro": {"sun_sign": "aries"},
            "numerology": {"life_path": 1},
            "baseline": {"archetype_seed": "initiator"},
            "living": None,
        },
        locale="ru",
    )
    assert len(calls) == 2  # identity + styles only (no patterns, no LLM spheres)
    assert meta["reason"] == "patterns_skipped_ineligible"
    assert meta["patterns_omitted"] is True
    assert meta["partial"] is True
    assert meta["completed_steps"] == ["identity", "styles", "spheres"]
    skip = meta["steps"][2]
    assert skip.get("skipped") is True
    assert skip.get("skip_reason") == "generation_gate_ineligible"
    assert merged is not None
    assert merged["relationship_style"]
    assert merged.get("recurring_patterns") == []
    assert merged.get("living_changes") is None
    assert set(merged.get("life_spheres") or {}) == {"love", "money", "decisions"}
    assert meta.get("spheres_source") == "deterministic_projector_v0_1"
    proj = meta["steps"][3]
    assert proj.get("spheres_source") == "deterministic_projector_v0_1"
    assert proj.get("ok") is True

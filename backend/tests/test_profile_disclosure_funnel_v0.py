"""Profile disclosure funnel — 4 LLM steps without live network."""

from __future__ import annotations

from typing import Any

from todayflow_backend.core.config import settings
from todayflow_backend.services import profile_disclosure_funnel_v0 as funnel
from todayflow_backend.services.profile_contract_v1 import (
    PROFILE_CONTRACT_PROMPT_VER,
    _normalize_profile_contract,
    profile_contract_to_legacy_interpretation,
)


def _sphere_row(tag: str) -> dict[str, str]:
    return {
        "how": f"{tag} how manifests in daily life with a clear situation.",
        "need": f"{tag} needs clarity and one honest boundary.",
        "risk": f"{tag} risk is overloading without a pause.",
        "turns_on": f"{tag} turns on with calm structure.",
        "turns_off": f"{tag} turns off with vague pressure.",
        "helps": f"{tag} helps with one small step.",
    }


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


def test_profile_funnel_four_steps(monkeypatch) -> None:
    monkeypatch.setattr(settings, "llm_quality_mode", "rich")
    monkeypatch.setattr(funnel, "is_llm_chat_configured", lambda: True)
    monkeypatch.setattr(funnel, "prefer_multi_step_funnels", lambda: True)
    responses = [
        {
            "contract_version": funnel.IDENTITY_CONTRACT,
            "identity_core": "Человек держит смысл через ясный фокус и живой контакт.",
            "strengths": ["Фокус", "Контакт", "Доведение"],
            "growth_zones": ["Распыление", "Контроль", "Откладывание"],
        },
        {
            "contract_version": funnel.STYLES_CONTRACT,
            "relationship_style": "Близость через прямые слова и предсказуемость.",
            "money_style": "Деньги как ценность и спокойный шаг без импульса.",
            "decision_style": "Решения через один критерий и короткий дедлайн.",
        },
        {
            "contract_version": funnel.PATTERNS_CONTRACT,
            "recurring_patterns": ["Часто берёт второй приоритет без слота."],
            "living_changes": "Сейчас усиливается запрос на один главный фокус и меньше параллельных обещаний.",
            "life_mission": "Удерживать свой ритм и не растворяться в чужих задачах.",
            "helps": ["Один фокус на день", "Пауза перед новым да"],
        },
        {
            "contract_version": funnel.SPHERES_CONTRACT,
            "life_spheres": {
                sid: {
                    **_sphere_row(sid),
                    "how": f"В сфере {sid} проявляется сценарий с глаголом и границей #{i}.",
                }
                for i, sid in enumerate(funnel.SPHERE_IDS)
            },
        },
    ]

    monkeypatch.setattr(funnel, "_call", _fake_call_factory(responses))
    merged, meta = funnel.run_profile_disclosure_funnel_v0(
        {
            "person": {"display_name": "Игорь"},
            "astro": {"sun_sign": "Leo"},
            "living": _living_eligible(),
        },
        locale="ru",
    )
    assert meta["failed"] is False
    assert meta["completed_steps"] == ["identity", "styles", "patterns", "spheres"]
    assert len(meta["steps"]) == 4
    assert all(s.get("prompt_version") or s.get("skipped") for s in meta["steps"])
    assert merged is not None
    assert merged["life_mission"]
    assert len(merged["life_spheres"]) == 9

    contract = _normalize_profile_contract(merged)
    assert contract["profile_snapshot_version"] == PROFILE_CONTRACT_PROMPT_VER
    assert contract["life_spheres"]["love"]["need"]
    legacy = profile_contract_to_legacy_interpretation(contract)
    assert "love" in legacy["life_areas"]["love"]
    assert "work" in legacy["life_areas"]["career"]
    assert legacy["life_areas"]["love"].startswith("В сфере love")


def test_economize_skips_profile_funnel(monkeypatch) -> None:
    monkeypatch.setattr(settings, "llm_quality_mode", "economize")
    merged, meta = funnel.run_profile_disclosure_funnel_v0({}, locale="ru")
    assert merged is None
    assert meta["reason"] == "quality_mode_economize"


def test_partial_failure_keeps_prior_steps(monkeypatch) -> None:
    monkeypatch.setattr(settings, "llm_quality_mode", "rich")
    monkeypatch.setattr(funnel, "is_llm_chat_configured", lambda: True)
    monkeypatch.setattr(funnel, "prefer_multi_step_funnels", lambda: True)
    responses: list[dict[str, Any] | None] = [
        {
            "contract_version": funnel.IDENTITY_CONTRACT,
            "identity_core": "Человек держит смысл через ясный фокус и живой контакт.",
            "strengths": ["Фокус", "Контакт", "Доведение"],
            "growth_zones": ["Распыление", "Контроль", "Откладывание"],
        },
        {
            "contract_version": funnel.STYLES_CONTRACT,
            "relationship_style": "Близость через прямые слова и предсказуемость.",
            "money_style": "Деньги как ценность и спокойный шаг без импульса.",
            "decision_style": "Решения через один критерий и короткий дедлайн.",
        },
        None,  # patterns fail (also retry → second None)
        None,
    ]

    monkeypatch.setattr(funnel, "_call", _fake_call_factory(responses))
    merged, meta = funnel.run_profile_disclosure_funnel_v0(
        {
            "person": {"display_name": "Игорь"},
            "astro": {"sun_sign": "Leo"},
            "living": _living_eligible(),
        },
        locale="ru",
    )
    assert meta["failed"] is True
    assert meta["partial"] is True
    assert meta["reason"] == "patterns_failed"
    assert meta["completed_steps"] == ["identity", "styles"]
    assert merged is not None
    assert merged["identity_core"]
    assert merged["relationship_style"]
    assert "life_mission" not in merged or not merged.get("life_mission")


def test_patterns_skipped_when_birth_only(monkeypatch) -> None:
    """GENERATION_GATE: birth_data_only must not call profile.patterns.v1."""
    monkeypatch.setattr(settings, "llm_quality_mode", "rich")
    monkeypatch.setattr(funnel, "is_llm_chat_configured", lambda: True)
    monkeypatch.setattr(funnel, "prefer_multi_step_funnels", lambda: True)
    calls: list[str] = []
    responses = [
        {
            "contract_version": funnel.IDENTITY_CONTRACT,
            "identity_core": "Человек держит смысл через ясный фокус и живой контакт.",
            "strengths": ["Фокус", "Контакт", "Доведение"],
            "growth_zones": ["Распыление", "Контроль", "Откладывание"],
        },
        {
            "contract_version": funnel.STYLES_CONTRACT,
            "relationship_style": "Близость через прямые слова и предсказуемость.",
            "money_style": "Деньги как ценность и спокойный шаг без импульса.",
            "decision_style": "Решения через один критерий и короткий дедлайн.",
        },
    ]

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
            "person": {"first_name": "Аня"},
            "astro": {"sun_sign": "aries"},
            "numerology": {"life_path": 1},
            "baseline": {"archetype_seed": "initiator"},
            "living": None,
        },
        locale="ru",
    )
    assert len(calls) == 2  # identity + styles only
    assert meta["reason"] == "patterns_skipped_ineligible"
    assert meta["patterns_omitted"] is True
    assert meta["partial"] is True
    assert meta["completed_steps"] == ["identity", "styles"]
    skip = meta["steps"][2]
    assert skip.get("skipped") is True
    assert skip.get("skip_reason") == "generation_gate_ineligible"
    assert merged is not None
    assert merged["relationship_style"]
    assert merged.get("recurring_patterns") == []
    assert merged.get("living_changes") is None
    assert "life_spheres" not in merged or not merged.get("life_spheres")

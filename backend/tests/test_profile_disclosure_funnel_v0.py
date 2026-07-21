"""Profile disclosure funnel — identity/styles/patterns + spheres synthesis."""

from __future__ import annotations

from typing import Any

from todayflow_backend.core.config import settings
from todayflow_backend.services import profile_disclosure_funnel_v0 as funnel
from todayflow_backend.services.life_spheres_synthesis_run_v0 import SPHERES_SOURCE
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


def _sphere_row(tag: str) -> dict[str, str]:
    return {
        "how": f"В сфере {tag} ты действуешь через ясный шаг и проверяемый контакт с реальностью рядом.",
        "need": f"Тебе нужно условие устойчивости в {tag}, где темп не форсируют без твоей опоры.",
        "risk": f"Сила в {tag} может превратиться в застревание, если молчать о дискомфорте слишком долго.",
        "turns_on": f"Включает участие в {tag} конкретная ясность и выполненное обещание.",
        "turns_off": f"Выключает в {tag} давление на скорость и непредсказуемые исчезновения.",
        "helps": f"Назови один критерий для {tag} вслух и зафиксируй ближайший шаг на сегодня.",
    }


def _fake_synthesis_ok(foundations: dict[str, Any]) -> tuple[dict[str, dict[str, str]], dict[str, Any]]:
    spheres = {
        "love": _sphere_row("love"),
        "money": _sphere_row("money"),
        "decisions": _sphere_row("decisions"),
    }
    meta = {
        "synthesis_version": "life_spheres_synthesis_v1.0.0",
        "spheres_source": SPHERES_SOURCE,
        "prompt_id": "profile.spheres.synthesis.v1",
        "spheres_projected": ["love", "money", "decisions"],
        "spheres_omitted": [],
        "per_sphere": {sid: {"ok": True, "cues_ok": True, "attempts": 1} for sid in spheres},
        "ms": 1,
        "ok": True,
        "gate": True,
    }
    return spheres, meta


def test_profile_funnel_patterns_then_synthesis_spheres(monkeypatch) -> None:
    monkeypatch.setattr(settings, "llm_quality_mode", "rich")
    monkeypatch.setattr(funnel, "is_llm_chat_configured", lambda: True)
    monkeypatch.setattr(funnel, "prefer_multi_step_funnels", lambda: True)
    monkeypatch.setattr(funnel, "synthesize_life_spheres_v0", _fake_synthesis_ok)
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
    assert meta.get("spheres_source") == SPHERES_SOURCE
    assert len(responses) == 0  # identity/styles/patterns only; synthesis mocked
    assert merged is not None
    assert merged["life_mission"]
    assert set(merged["life_spheres"].keys()) == {"love", "money", "decisions"}

    contract = _normalize_profile_contract(merged)
    assert contract["profile_snapshot_version"] == PROFILE_CONTRACT_PROMPT_VER
    assert contract["life_spheres"]["love"]["need"]
    legacy = profile_contract_to_legacy_interpretation(contract)
    love_legacy = legacy["life_areas"]["love"].lower()
    assert "love" in love_legacy or "близ" in love_legacy or "сфер" in love_legacy
    assert len(legacy["life_areas"]["love"]) >= 20


def test_economize_skips_profile_funnel(monkeypatch) -> None:
    monkeypatch.setattr(settings, "llm_quality_mode", "economize")
    merged, meta = funnel.run_profile_disclosure_funnel_v0({}, locale="ru")
    assert merged is None
    assert meta["reason"] == "quality_mode_economize"


def test_identity_skipped_without_birth_foundations(monkeypatch) -> None:
    """GENERATION_GATE: identity LLM must not run without birth + usable facts."""
    monkeypatch.setattr(settings, "llm_quality_mode", "rich")
    monkeypatch.setattr(funnel, "is_llm_chat_configured", lambda: True)
    monkeypatch.setattr(funnel, "prefer_multi_step_funnels", lambda: True)
    calls: list[str] = []

    def fake_call(*_a, **_k):
        calls.append("called")
        return None, None

    monkeypatch.setattr(funnel, "_call", fake_call)
    merged, meta = funnel.run_profile_disclosure_funnel_v0(
        {"person": {"display_name": "Гость"}, "astro": {}, "living": None},
        locale="ru",
    )
    assert calls == []
    assert merged is None
    assert meta["reason"] == "identity_skipped_ineligible"
    assert meta["steps"][0].get("skipped") is True
    assert meta["steps"][0].get("skip_reason") == "generation_gate_ineligible"


def test_identity_system_uses_profile_voice_not_day_chain() -> None:
    from todayflow_backend.prompts import profile_disclosure_v1 as prompts

    system = prompts.identity_system("ru")
    assert "чего ждать" not in system
    assert "сферы сегодня" not in system
    assert "не повестка" in system.lower() or "устойчив" in system.lower()


def test_patterns_failed_still_synthesizes_spheres(monkeypatch) -> None:
    monkeypatch.setattr(settings, "llm_quality_mode", "rich")
    monkeypatch.setattr(funnel, "is_llm_chat_configured", lambda: True)
    monkeypatch.setattr(funnel, "prefer_multi_step_funnels", lambda: True)
    monkeypatch.setattr(funnel, "synthesize_life_spheres_v0", _fake_synthesis_ok)
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


def test_patterns_skipped_when_birth_only_synthesizes_spheres(monkeypatch) -> None:
    """GENERATION_GATE patterns skip must not block sphere synthesis."""
    monkeypatch.setattr(settings, "llm_quality_mode", "rich")
    monkeypatch.setattr(funnel, "is_llm_chat_configured", lambda: True)
    monkeypatch.setattr(funnel, "prefer_multi_step_funnels", lambda: True)
    monkeypatch.setattr(funnel, "synthesize_life_spheres_v0", _fake_synthesis_ok)
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
    assert len(calls) == 2  # identity + styles only (no patterns)
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
    assert meta.get("spheres_source") == SPHERES_SOURCE
    syn = meta["steps"][3]
    assert syn.get("spheres_source") == SPHERES_SOURCE
    assert syn.get("prompt_id") == "profile.spheres.synthesis.v1"
    assert syn.get("ok") is True


def test_synthesis_fail_does_not_fallback_to_projector(monkeypatch) -> None:
    """Validator/LLM fail ⇒ omit spheres; never fill from projector tables."""
    monkeypatch.setattr(settings, "llm_quality_mode", "rich")
    monkeypatch.setattr(funnel, "is_llm_chat_configured", lambda: True)
    monkeypatch.setattr(funnel, "prefer_multi_step_funnels", lambda: True)

    def empty_synthesis(foundations: dict[str, Any]) -> tuple[dict, dict]:
        return {}, {
            "spheres_source": SPHERES_SOURCE,
            "ok": False,
            "spheres_projected": [],
            "spheres_omitted": [
                {"id": "love", "reason": "synthesis_validation_failed"},
                {"id": "money", "reason": "synthesis_validation_failed"},
                {"id": "decisions", "reason": "synthesis_validation_failed"},
            ],
            "per_sphere": {},
            "ms": 1,
            "gate": True,
        }

    monkeypatch.setattr(funnel, "synthesize_life_spheres_v0", empty_synthesis)
    monkeypatch.setattr(funnel, "_call", _fake_call_factory([_identity(), _styles()]))
    merged, meta = funnel.run_profile_disclosure_funnel_v0(
        {
            "person": {"first_name": "Аня", "birth_date": "1992-03-04"},
            "astro": {"sun_sign": "aries", "venus_sign": "Taurus"},
            "living": None,
        },
        locale="ru",
    )
    assert merged is not None
    assert not merged.get("life_spheres")
    assert meta.get("spheres_omitted") is True
    assert meta.get("spheres_source") == SPHERES_SOURCE
    assert "deterministic_projector" not in json_dumps_safe(meta)


def json_dumps_safe(obj: Any) -> str:
    import json

    return json.dumps(obj, ensure_ascii=False, default=str)

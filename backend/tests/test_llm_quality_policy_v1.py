"""LLM quality policy + Nebius provider wiring."""

from __future__ import annotations

from todayflow_backend.core.config import settings
from todayflow_backend.core import llm_openai_compatible as llm
from todayflow_backend.prompts.registry_v1 import get_prompt, list_prompt_ids, prompt_registry_snapshot
from todayflow_backend.services.llm_quality_policy_v1 import (
    context_depth_for_surface,
    funnel_step_max_tokens,
    is_rich_quality_mode,
    max_tokens_for_surface,
    model_tier_for_surface,
    prefer_multi_step_funnels,
)
from todayflow_backend.services.today_narrative_llm_gate_v1 import decide_today_narrative_llm_call_v1


def test_rich_mode_default() -> None:
    assert is_rich_quality_mode()
    assert prefer_multi_step_funnels()
    assert max_tokens_for_surface("guide", "normal") >= 3000
    assert funnel_step_max_tokens("normal") >= 3000


def test_economize_mode_tight_caps(monkeypatch) -> None:
    monkeypatch.setattr(settings, "llm_quality_mode", "economize")
    assert not is_rich_quality_mode()
    assert max_tokens_for_surface("guide", "normal") == 1750
    assert model_tier_for_surface("spheres", "normal") == "cheap"
    assert not prefer_multi_step_funnels()


def test_gate_uses_rich_budgets() -> None:
    gate = decide_today_narrative_llm_call_v1(
        surface="guide",
        llm_configured=True,
        user_context={"has_day_context": True, "context_slice_id": "sha"},
        depth_level="normal",
    )
    assert gate["gate_decision"] == "call_llm"
    assert gate["max_tokens"] >= 3000
    assert gate["allowed_model_tier"] == "standard"


def test_gate_spheres_no_longer_cheap_in_rich() -> None:
    gate = decide_today_narrative_llm_call_v1(
        surface="spheres",
        llm_configured=True,
        depth_level="normal",
    )
    assert gate["allowed_model_tier"] == "standard"
    assert gate["max_tokens"] >= 2000


def test_gate_economize_cheap_spheres(monkeypatch) -> None:
    monkeypatch.setattr(settings, "llm_quality_mode", "economize")
    gate = decide_today_narrative_llm_call_v1(
        surface="spheres",
        llm_configured=True,
        depth_level="normal",
    )
    assert gate["allowed_model_tier"] == "cheap"
    assert gate["max_tokens"] == 800


def test_rich_context_depth_standard_with_day_context() -> None:
    depth = context_depth_for_surface("day_layer", {"has_day_context": True})
    assert depth == "standard"


def test_prompt_registry_has_disclosure_ids() -> None:
    ids = list_prompt_ids()
    assert "day.day_layer.funnel.personalize.v1" in ids
    assert "profile.identity.v1" in ids
    snap = prompt_registry_snapshot()
    assert snap["contract_version"] == "prompt_registry_v1"
    text, ver = get_prompt("day.spheres.funnel.render.v1", locale="ru")
    assert "Сферы" in text or "сферы" in text.lower()
    assert ver == "1.0.0"


def test_nebius_credentials(monkeypatch) -> None:
    monkeypatch.setattr(settings, "llm_provider", "nebius")
    monkeypatch.setattr(settings, "nebius_api_key", "neb-test-key")
    monkeypatch.setattr(settings, "nebius_base_url", "https://api.tokenfactory.nebius.com/v1/")
    monkeypatch.setattr(settings, "nebius_model", "meta-llama/Meta-Llama-3.1-70B-Instruct")
    assert llm.is_llm_chat_configured()
    creds = llm._resolve_llm_credentials()
    assert creds is not None
    key, base = creds
    assert key == "neb-test-key"
    assert "nebius" in base
    assert llm.resolve_default_chat_model() == "meta-llama/Meta-Llama-3.1-70B-Instruct"

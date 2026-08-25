"""Cost Containment: router policy, K3 allowlist, retry cap, tenant USD ceiling."""

from types import SimpleNamespace
from unittest.mock import MagicMock

from todayflow_backend.core import config as config_module
from todayflow_backend.core.llm_cost_guard_v1 import (
    apply_provider_policy,
    classify_feature,
    is_synthetic_production_email,
    reset_ledger_for_tests,
    snapshot_ledger,
    trip_daily_ceiling,
)
from todayflow_backend.core.llm_openai_compatible import chat_completion_plain_with_status
from todayflow_backend.core.llm_usage_telemetry_v1 import (
    clear_recent_llm_usage_events,
    llm_call_context,
    recent_llm_usage_events,
)


def _patch(monkeypatch, s, tmp_path=None) -> None:
    from todayflow_backend.core import llm_cost_guard_v1 as guard
    from todayflow_backend.core import llm_openai_compatible as llm_mod

    if tmp_path is not None:
        s = s.model_copy(update={"llm_spend_ledger_path": str(tmp_path / "llm_spend.json")})
    monkeypatch.setattr(config_module, "settings", s)
    monkeypatch.setattr(guard, "settings", s)
    monkeypatch.setattr(llm_mod, "settings", s)
    reset_ledger_for_tests()


def _nebius_settings(**over):
    kw = dict(
        llm_provider="nebius",
        nebius_api_key="sk-test",
        nebius_model="moonshotai/Kimi-K2.6",
        nebius_complex_model="moonshotai/Kimi-K3",
        nebius_fallback_model="",
        llm_cost_guard_enabled=True,
        llm_daily_usd_ceiling=5.0,
        llm_downgrade_model="Qwen/Qwen3-30B-A3B-Instruct-2507",
        llm_stream_completions=False,
    )
    kw.update(over)
    return config_module.Settings(**kw)


def test_example_com_is_synthetic():
    assert is_synthetic_production_email("p0compat@example.com") is True
    assert is_synthetic_production_email("n@sub.example.com") is True
    assert is_synthetic_production_email("victoria.tatarynovich@gmail.com") is False
    assert is_synthetic_production_email("pakistandiller@gmail.com") is False


def test_classify_today_vs_natal():
    assert classify_feature("today.native_day_story") == "today_daily"
    assert classify_feature("today.prewarm") == "today_daily"
    assert classify_feature("natal.decode") == "natal_ce"
    assert classify_feature("ce.stage2") == "natal_ce"
    assert classify_feature("tarot.interpretation") == "tarot"
    assert classify_feature("profile.disclosure") == "on_demand"
    assert classify_feature("unlabeled") == "other"


def test_k3_stripped_from_today(monkeypatch, tmp_path):
    s = _nebius_settings()
    _patch(monkeypatch, s, tmp_path)
    with llm_call_context(feature="today.native_day_story"):
        d = apply_provider_policy(model="moonshotai/Kimi-K3", max_tokens=16000, prompt_chars=40)
    assert d.model == "moonshotai/Kimi-K2.6"
    assert d.action == "k3_denied"
    assert d.max_tokens == 1400


def test_k3_allowed_for_natal_but_capped(monkeypatch, tmp_path):
    s = _nebius_settings()
    _patch(monkeypatch, s, tmp_path)
    with llm_call_context(feature="natal.decode"):
        d = apply_provider_policy(model="moonshotai/Kimi-K3", max_tokens=16000, prompt_chars=40)
    assert d.model == "moonshotai/Kimi-K3"
    assert d.max_tokens == 2500
    assert d.action == "clamp"


def test_retry_uses_smaller_cap(monkeypatch, tmp_path):
    s = _nebius_settings()
    _patch(monkeypatch, s, tmp_path)
    with llm_call_context(feature="today.native_day_story", attempt=1, retry_reason="gate_retry"):
        d = apply_provider_policy(model="moonshotai/Kimi-K2.6", max_tokens=4800, prompt_chars=40)
    assert d.max_tokens == 600
    assert d.model == "moonshotai/Kimi-K2.6"


def test_daily_ceiling_denies_without_provider(monkeypatch, tmp_path):
    s = _nebius_settings(llm_daily_usd_ceiling=0.0)
    _patch(monkeypatch, s, tmp_path)
    clear_recent_llm_usage_events()
    mock_client = MagicMock()
    with llm_call_context(feature="today.native_day_story"):
        text, kind, mid = chat_completion_plain_with_status(
            mock_client,
            model="moonshotai/Kimi-K2.6",
            messages=[{"role": "user", "content": "hello"}],
            temperature=0.1,
            max_tokens=1400,
        )
    assert text is None
    assert kind == "budget_exhausted"
    mock_client.chat.completions.create.assert_not_called()
    events = recent_llm_usage_events()
    assert events
    assert events[-1]["failure_class"] == "budget_exhausted"
    assert events[-1]["ok"] is False
    assert events[-1]["cost_guard_action"] == "deny"


def test_ceiling_downgrades_instead_of_k3_retry(monkeypatch, tmp_path):
    s = _nebius_settings(llm_daily_usd_ceiling=0.0004)
    _patch(monkeypatch, s, tmp_path)
    mock_client = MagicMock()
    ok_msg = SimpleNamespace(content='{"ok":true}')
    mock_client.chat.completions.create.return_value = SimpleNamespace(
        choices=[SimpleNamespace(message=ok_msg)],
        usage=SimpleNamespace(prompt_tokens=10, completion_tokens=20),
    )
    with llm_call_context(feature="today.native_day_story"):
        text, kind, _mid = chat_completion_plain_with_status(
            mock_client,
            model="moonshotai/Kimi-K2.6",
            messages=[{"role": "user", "content": "x"}],
            temperature=0.1,
            max_tokens=1400,
        )
    assert text
    assert kind is None
    assert mock_client.chat.completions.create.call_args.kwargs["model"] == (
        "Qwen/Qwen3-30B-A3B-Instruct-2507"
    )
    assert mock_client.chat.completions.create.call_args.kwargs["max_tokens"] <= 800


def test_trip_blocks_further_spend(monkeypatch, tmp_path):
    s = _nebius_settings(llm_daily_usd_ceiling=5.0)
    _patch(monkeypatch, s, tmp_path)
    trip_daily_ceiling(reason="test")
    snap = snapshot_ledger()
    assert snap["tripped"] is True
    with llm_call_context(feature="natal.decode"):
        d = apply_provider_policy(model="moonshotai/Kimi-K3", max_tokens=100, prompt_chars=10)
    assert d.action == "deny"


def test_router_clamps_today_even_if_caller_asks_16k(monkeypatch, tmp_path):
    s = _nebius_settings()
    _patch(monkeypatch, s, tmp_path)
    mock_client = MagicMock()
    ok_msg = SimpleNamespace(content='{"scene":"ok"}')
    mock_client.chat.completions.create.return_value = SimpleNamespace(
        choices=[SimpleNamespace(message=ok_msg)],
        usage=SimpleNamespace(prompt_tokens=50, completion_tokens=80),
    )
    with llm_call_context(feature="today.native_day_story"):
        text, kind, _mid = chat_completion_plain_with_status(
            mock_client,
            model="moonshotai/Kimi-K2.6",
            messages=[{"role": "user", "content": "x"}],
            temperature=0.1,
            max_tokens=16000,
        )
    assert text
    assert kind is None
    kw = mock_client.chat.completions.create.call_args.kwargs
    assert kw["max_tokens"] == 1400
    assert kw["model"] == "moonshotai/Kimi-K2.6"
    ev = recent_llm_usage_events()[-1]
    assert ev["requested_max_tokens"] == 16000
    assert ev["max_tokens"] == 1400
    assert ev["cost_class"] == "today_daily"

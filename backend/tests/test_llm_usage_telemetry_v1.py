"""AI COGS telemetry: billed output, operation_id, retry metadata, triggers."""

from types import SimpleNamespace
from unittest.mock import MagicMock

from todayflow_backend.core import config as config_module
from todayflow_backend.core.llm_openai_compatible import chat_completion_text
from todayflow_backend.core.llm_usage_telemetry_v1 import (
    clear_recent_llm_usage_events,
    emit_llm_usage_v1,
    estimate_cost_usd,
    llm_call_context,
    parse_usage_obj,
    recent_llm_usage_events,
)


def test_k26_output_dominates_cost():
    cost = estimate_cost_usd(
        model="moonshotai/Kimi-K2.6",
        input_tokens=1_450_000,
        output_tokens=2_530_000,
    )
    assert 11.0 < cost < 12.0
    out_share = (2.53 * 4.00) / cost
    assert out_share > 0.85


def test_reasoning_not_added_twice_to_cost():
    billed = estimate_cost_usd(
        model="moonshotai/Kimi-K2.6",
        input_tokens=80,
        output_tokens=220,
        reasoning_tokens=150,
    )
    doubled = estimate_cost_usd(
        model="moonshotai/Kimi-K2.6",
        input_tokens=80,
        output_tokens=370,
    )
    assert billed < doubled
    ev = emit_llm_usage_v1(
        model="moonshotai/Kimi-K2.6",
        input_tokens=80,
        output_tokens=220,
        reasoning_tokens=150,
        ok=True,
    )
    assert ev["output_tokens"] == 220
    assert ev["reasoning_tokens"] == 150
    assert ev["content_tokens"] == 70
    assert ev["reasoning_included_in_output"] is True
    assert ev["estimated_cost_usd"] == billed


def test_parse_usage_reasoning_and_cached():
    usage = SimpleNamespace(
        prompt_tokens=100,
        completion_tokens=400,
        total_tokens=500,
        completion_tokens_details=SimpleNamespace(reasoning_tokens=280),
        prompt_tokens_details=SimpleNamespace(cached_tokens=40),
    )
    parsed = parse_usage_obj(usage)
    assert parsed["prompt_tokens"] == 100
    assert parsed["completion_tokens"] == 400
    assert parsed["reasoning_tokens"] == 280
    assert parsed["cached_tokens"] == 40


def test_operation_id_inherited_and_retry_flags():
    clear_recent_llm_usage_events()
    with llm_call_context(
        trigger="prewarm",
        user_id=7,
        ensure_operation=True,
        operation="today.generate",
    ):
        with llm_call_context(feature="today.native_day_story"):
            first = emit_llm_usage_v1(
                model="moonshotai/Kimi-K2.6",
                input_tokens=10,
                output_tokens=20,
                ok=True,
            )
        with llm_call_context(
            feature="today.native_day_story",
            attempt=1,
            retry_reason="gate_retry",
        ):
            second = emit_llm_usage_v1(
                model="moonshotai/Kimi-K2.6",
                input_tokens=12,
                output_tokens=40,
                ok=True,
            )
    assert first["trigger"] == "prewarm"
    assert first["operation"] == "today.generate"
    assert first["operation_id"]
    assert first["attempt"] == 0
    assert first["retry_reason"] is None
    assert first["gate_retry"] is False
    assert second["operation_id"] == first["operation_id"]
    assert second["attempt"] == 1
    assert second["retry_reason"] == "gate_retry"
    assert second["gate_retry"] is True
    assert second["parse_failed"] is False
    assert second["empty_content"] is False


def test_explicit_prewarm_overwrites_user_trigger():
    clear_recent_llm_usage_events()
    with llm_call_context(trigger="user", request_id="http-1"):
        with llm_call_context(trigger="prewarm", ensure_operation=True, operation="today.generate"):
            ev = emit_llm_usage_v1(
                model="moonshotai/Kimi-K2.6",
                input_tokens=1,
                output_tokens=1,
                ok=True,
            )
    assert ev["trigger"] == "prewarm"
    assert ev["request_id"] == "http-1"


def test_kimi_stream_records_usage_and_reasoning_chars(monkeypatch, tmp_path):
    from todayflow_backend.core import llm_cost_guard_v1 as guard
    from todayflow_backend.core import llm_openai_compatible as llm_mod

    s = config_module.Settings(
        llm_provider="nebius",
        nebius_api_key="sk-test",
        nebius_model="moonshotai/Kimi-K2.6",
        nebius_fallback_model="",
        llm_stream_completions=True,
        llm_cost_guard_enabled=True,
        llm_daily_usd_ceiling=50.0,
        llm_spend_ledger_path=str(tmp_path / "spend.json"),
    )
    monkeypatch.setattr(config_module, "settings", s)
    monkeypatch.setattr(llm_mod, "settings", s)
    monkeypatch.setattr(guard, "settings", s)
    guard.reset_ledger_for_tests()
    clear_recent_llm_usage_events()

    def _chunk(*, content=None, reasoning=None, usage=None, finish=None):
        delta = SimpleNamespace(content=content, reasoning_content=reasoning)
        choice = SimpleNamespace(delta=delta, finish_reason=finish)
        return SimpleNamespace(choices=[choice], usage=usage)

    usage_tail = SimpleNamespace(
        prompt_tokens=80,
        completion_tokens=220,
        completion_tokens_details=SimpleNamespace(reasoning_tokens=150),
        prompt_tokens_details=None,
    )
    stream = [
        _chunk(reasoning="think " * 20),
        _chunk(content='{"ok":true}'),
        SimpleNamespace(choices=[], usage=usage_tail),
    ]
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = iter(stream)

    with llm_call_context(feature="today.native_day_story", trigger="user"):
        text = chat_completion_text(
            mock_client,
            model="moonshotai/Kimi-K2.6",
            messages=[{"role": "user", "content": "x" * 40}],
            temperature=0.1,
            max_tokens=100,
            json_object=False,
        )
    assert text == '{"ok":true}'
    kw = mock_client.chat.completions.create.call_args.kwargs
    assert kw.get("stream") is True
    assert kw.get("stream_options") == {"include_usage": True}

    events = recent_llm_usage_events()
    assert events, "expected llm_usage_v1 event"
    ev = events[-1]
    assert ev["feature"] == "today.native_day_story"
    assert ev["trigger"] == "user"
    assert ev["model"] == "moonshotai/Kimi-K2.6"
    assert ev["input_tokens"] == 80
    assert ev["output_tokens"] == 220
    assert ev["reasoning_tokens"] == 150
    assert ev["content_tokens"] == 70
    assert ev["reasoning_chars"] > 0
    assert ev["tokens_source"] == "provider_usage"
    assert ev["ok"] is True
    assert ev["streamed"] is True
    assert ev["max_tokens"] == 100
    billed = estimate_cost_usd(
        model="moonshotai/Kimi-K2.6",
        input_tokens=80,
        output_tokens=220,
    )
    assert ev["estimated_cost_usd"] == billed

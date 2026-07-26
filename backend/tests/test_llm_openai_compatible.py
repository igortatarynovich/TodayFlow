"""Конфигурация OpenAI-совместимого LLM для Guidance."""

from types import SimpleNamespace
from unittest.mock import MagicMock

from todayflow_backend.core import config as config_module
from todayflow_backend.core.llm_openai_compatible import (
    chat_completion_text,
    get_openai_compatible_client,
    is_llm_chat_configured,
    resolve_max_tokens,
)


def test_get_openai_compatible_client_background_uses_longer_timeout(monkeypatch):
    from todayflow_backend.core.llm_openai_compatible import llm_operation

    s = config_module.Settings(
        openai_api_key="sk-test",
        llm_http_timeout_seconds=12.0,
        llm_background_timeout_seconds=45.0,
    )
    monkeypatch.setattr(config_module, "settings", s)
    sync_client = get_openai_compatible_client()
    assert float(sync_client.timeout) == 12.0
    with llm_operation("background"):
        bg_client = get_openai_compatible_client()
    assert float(bg_client.timeout) == 45.0


def test_resolve_max_tokens_bumps_reasoning_models(monkeypatch):
    s = config_module.Settings(openai_api_key="sk-test", llm_default_model="gpt-5.5")
    monkeypatch.setattr(config_module, "settings", s)
    assert resolve_max_tokens(2800, model="gpt-5.5") >= 8192


def test_chat_completion_json_fallback_without_response_format(monkeypatch):
    s = config_module.Settings(openai_api_key="sk-test")
    monkeypatch.setattr(config_module, "settings", s)

    mock_client = MagicMock()
    first = MagicMock()
    first.message.content = None
    fail_resp = SimpleNamespace(choices=[SimpleNamespace(message=first)])
    ok_msg = SimpleNamespace(content='{"clarity":"a","explanation":"b","forecast":"c","decision":"d","today":"e"}')
    ok_resp = SimpleNamespace(choices=[SimpleNamespace(message=ok_msg)])

    mock_client.chat.completions.create.side_effect = [ValueError("no json mode"), ok_resp]

    text = chat_completion_text(
        mock_client,
        model="my-model",
        messages=[{"role": "user", "content": "x"}],
        temperature=0.1,
        max_tokens=100,
        json_object=True,
    )
    assert text and "clarity" in text
    assert mock_client.chat.completions.create.call_count == 2


def test_chat_completion_json_does_not_plain_retry_on_timeout(monkeypatch):
    from todayflow_backend.core.llm_openai_compatible import classify_llm_call_failure

    s = config_module.Settings(openai_api_key="sk-test")
    monkeypatch.setattr(config_module, "settings", s)

    class FakeTimeout(Exception):
        pass

    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = FakeTimeout("Request timed out.")

    text = chat_completion_text(
        mock_client,
        model="my-model",
        messages=[{"role": "user", "content": "x"}],
        temperature=0.1,
        max_tokens=100,
        json_object=True,
    )
    assert text is None
    assert mock_client.chat.completions.create.call_count == 1
    assert classify_llm_call_failure(FakeTimeout("Request timed out.")) == "timeout"


def test_chat_completion_json_retries_when_json_mode_returns_empty(monkeypatch):
    s = config_module.Settings(openai_api_key="sk-test", llm_default_model="gpt-5.5")
    monkeypatch.setattr(config_module, "settings", s)

    mock_client = MagicMock()
    empty_msg = SimpleNamespace(content=None)
    empty_resp = SimpleNamespace(choices=[SimpleNamespace(message=empty_msg)])
    ok_msg = SimpleNamespace(content='{"score_tagline":"ok"}')
    ok_resp = SimpleNamespace(choices=[SimpleNamespace(message=ok_msg)])

    mock_client.chat.completions.create.side_effect = [empty_resp, ok_resp]

    text = chat_completion_text(
        mock_client,
        model="gpt-5.5",
        messages=[{"role": "user", "content": "x"}],
        temperature=0.1,
        max_tokens=2800,
        json_object=True,
    )
    assert text == '{"score_tagline":"ok"}'
    assert mock_client.chat.completions.create.call_count == 2
    plain_call = mock_client.chat.completions.create.call_args_list[1].kwargs
    assert "response_format" not in plain_call
    assert plain_call.get("reasoning_effort") == "none"
    assert plain_call.get("max_completion_tokens", 0) >= 8192

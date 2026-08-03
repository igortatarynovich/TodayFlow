"""Конфигурация OpenAI-совместимого LLM для Guidance."""

from types import SimpleNamespace
from unittest.mock import MagicMock

from todayflow_backend.core import config as config_module
from todayflow_backend.core.llm_openai_compatible import (
    chat_completion_plain_with_status,
    chat_completion_text,
    get_openai_compatible_client,
    is_llm_chat_configured,
    resolve_max_tokens,
)


def _patch_settings(monkeypatch, s) -> None:
    from todayflow_backend.core import llm_openai_compatible as llm_mod

    monkeypatch.setattr(config_module, "settings", s)
    monkeypatch.setattr(llm_mod, "settings", s)


def test_get_openai_compatible_client_background_uses_longer_timeout(monkeypatch):
    from todayflow_backend.core.llm_openai_compatible import llm_operation

    s = config_module.Settings(
        openai_api_key="sk-test",
        llm_http_timeout_seconds=12.0,
        llm_background_timeout_seconds=45.0,
    )
    _patch_settings(monkeypatch, s)
    sync_client = get_openai_compatible_client()
    assert float(sync_client.timeout) == 12.0
    with llm_operation("background"):
        bg_client = get_openai_compatible_client()
    assert float(bg_client.timeout) == 45.0


def test_resolve_max_tokens_bumps_reasoning_models(monkeypatch):
    s = config_module.Settings(openai_api_key="sk-test", llm_default_model="gpt-5.5")
    _patch_settings(monkeypatch, s)
    assert resolve_max_tokens(2800, model="gpt-5.5") >= 8192


def test_chat_completion_json_fallback_without_response_format(monkeypatch):
    s = config_module.Settings(
        openai_api_key="sk-test",
        llm_provider="openai",
        nebius_fallback_model="",
    )
    _patch_settings(monkeypatch, s)

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

    # No Nebius fallback chain — assert only that timeout skips plain retry.
    s = config_module.Settings(
        openai_api_key="sk-test",
        llm_provider="openai",
        nebius_fallback_model="",
    )
    _patch_settings(monkeypatch, s)

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
    s = config_module.Settings(
        openai_api_key="sk-test",
        llm_default_model="gpt-5.5",
        llm_provider="openai",
        nebius_fallback_model="",
    )
    _patch_settings(monkeypatch, s)

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


def test_nebius_model_fallback_on_404(monkeypatch):
    from todayflow_backend.core.llm_openai_compatible import (
        classify_llm_call_failure,
        resolve_chat_model_chain,
    )

    s = config_module.Settings(
        llm_provider="nebius",
        nebius_api_key="sk-test",
        nebius_model="moonshotai/Kimi-K3",
        nebius_fallback_model="deepseek-ai/DeepSeek-V4-Pro",
    )
    _patch_settings(monkeypatch, s)
    assert resolve_chat_model_chain("moonshotai/Kimi-K3") == [
        "moonshotai/Kimi-K3",
        "deepseek-ai/DeepSeek-V4-Pro",
    ]

    class FakeNotFound(Exception):
        status_code = 404

        def __str__(self) -> str:
            return "Error code: 404 - {'detail': 'The model `moonshotai/Kimi-K3` does not exist.'}"

    assert classify_llm_call_failure(FakeNotFound()) == "model_unavailable"

    mock_client = MagicMock()
    ok_msg = SimpleNamespace(content='{"direct_answer":"ok"}')
    ok_resp = SimpleNamespace(choices=[SimpleNamespace(message=ok_msg)])
    mock_client.chat.completions.create.side_effect = [FakeNotFound(), ok_resp]

    text = chat_completion_text(
        mock_client,
        model="moonshotai/Kimi-K3",
        messages=[{"role": "user", "content": "x"}],
        temperature=0.1,
        max_tokens=100,
        json_object=True,
    )
    assert text and "direct_answer" in text
    assert mock_client.chat.completions.create.call_count == 2
    assert mock_client.chat.completions.create.call_args_list[0].kwargs["model"] == "moonshotai/Kimi-K3"
    assert mock_client.chat.completions.create.call_args_list[1].kwargs["model"] == (
        "deepseek-ai/DeepSeek-V4-Pro"
    )


def test_nebius_model_fallback_on_timeout_tries_deepseek(monkeypatch):
    s = config_module.Settings(
        llm_provider="nebius",
        nebius_api_key="sk-test",
        nebius_model="moonshotai/Kimi-K3",
        nebius_fallback_model="deepseek-ai/DeepSeek-V4-Pro",
    )
    _patch_settings(monkeypatch, s)

    class FakeTimeout(Exception):
        pass

    mock_client = MagicMock()
    ok_msg = SimpleNamespace(content='{"ok":true}')
    ok_resp = SimpleNamespace(choices=[SimpleNamespace(message=ok_msg)])
    mock_client.chat.completions.create.side_effect = [FakeTimeout("Request timed out."), ok_resp]

    text = chat_completion_text(
        mock_client,
        model="moonshotai/Kimi-K3",
        messages=[{"role": "user", "content": "x"}],
        temperature=0.1,
        max_tokens=100,
        json_object=True,
    )
    assert text and "ok" in text
    assert mock_client.chat.completions.create.call_count == 2
    assert mock_client.chat.completions.create.call_args_list[1].kwargs["model"] == (
        "deepseek-ai/DeepSeek-V4-Pro"
    )


def test_plain_allow_model_fallback_false_skips_chain(monkeypatch):
    s = config_module.Settings(
        llm_provider="nebius",
        nebius_api_key="sk-test",
        nebius_model="moonshotai/Kimi-K3",
        nebius_fallback_model="deepseek-ai/DeepSeek-V4-Pro",
    )
    _patch_settings(monkeypatch, s)

    class FakeTimeout(Exception):
        pass

    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = FakeTimeout("Request timed out.")

    text, kind, mid = chat_completion_plain_with_status(
        mock_client,
        model="moonshotai/Kimi-K3",
        messages=[{"role": "user", "content": "x"}],
        temperature=0.1,
        max_tokens=100,
        allow_model_fallback=False,
    )
    assert text is None
    assert kind == "timeout"
    assert mid == "moonshotai/Kimi-K3"
    assert mock_client.chat.completions.create.call_count == 1



def test_is_llm_chat_configured_nebius(monkeypatch):
    s = config_module.Settings(llm_provider="nebius", nebius_api_key="sk-test")
    _patch_settings(monkeypatch, s)
    assert is_llm_chat_configured() is True

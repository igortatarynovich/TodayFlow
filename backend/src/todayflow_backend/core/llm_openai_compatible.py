"""OpenAI-совместимый chat-клиент: официальный API, vLLM, LiteLLM, прокси и т.п.

Ключ и base_url читаются из настроек; Guidance и другие модули могут вызывать один и тот же клиент.
"""

from __future__ import annotations

import logging
from typing import Any

from todayflow_backend.core.config import settings

logger = logging.getLogger(__name__)


def is_gemini_configured() -> bool:
    return bool((settings.gemini_api_key or "").strip())


def is_llm_chat_configured() -> bool:
    provider = (settings.llm_provider or "openai").strip().lower()
    if provider == "gemini":
        return is_gemini_configured()
    key = (settings.llm_chat_api_key or settings.openai_api_key or "").strip()
    return bool(key)


def _resolve_llm_credentials() -> tuple[str, str] | None:
    """Возвращает (api_key, base_url) для активного chat-провайдера."""
    provider = (settings.llm_provider or "openai").strip().lower()
    if provider == "gemini":
        key = (settings.gemini_api_key or "").strip()
        if not key:
            return None
        return key, settings.gemini_base_url.rstrip("/")

    key = (settings.llm_chat_api_key or settings.openai_api_key or "").strip()
    if not key:
        return None
    base = (settings.openai_base_url or "").strip()
    return key, base.rstrip("/") if base else ""


def get_openai_compatible_client() -> Any | None:
    """Собирает `openai.OpenAI` с опциональным `base_url` для своего провайдера."""
    creds = _resolve_llm_credentials()
    if creds is None:
        return None
    try:
        import openai
    except ImportError:
        return None
    key, base_url = creds
    kw: dict[str, Any] = {"api_key": key}
    if base_url:
        kw["base_url"] = base_url
    return openai.OpenAI(**kw)


def get_gemini_compatible_client() -> Any | None:
    """Отдельный клиент Gemini — для A/B-тестов без смены LLM_PROVIDER."""
    key = (settings.gemini_api_key or "").strip()
    if not key:
        return None
    try:
        import openai
    except ImportError:
        return None
    return openai.OpenAI(api_key=key, base_url=settings.gemini_base_url.rstrip("/"))


def resolve_default_chat_model() -> str:
    provider = (settings.llm_provider or "openai").strip().lower()
    if provider == "gemini":
        return settings.gemini_model
    return settings.llm_default_model


def resolve_guidance_chat_model() -> str:
    provider = (settings.llm_provider or "openai").strip().lower()
    if provider == "gemini":
        return settings.gemini_model
    return settings.guidance_llm_model


def resolve_max_tokens(requested: int, *, model: str | None = None) -> int:
    """Поднимает лимит для провайдеров, где часть budget уходит на thinking/reasoning."""
    requested = max(1, int(requested))
    provider = (settings.llm_provider or "openai").strip().lower()
    if provider == "gemini":
        if requested >= 800:
            return max(requested, settings.gemini_max_tokens)
        return requested
    mid = (model or resolve_default_chat_model()).strip().lower()
    if _uses_max_completion_tokens(mid):
        # GPT-5 / o-series: reasoning tokens входят в max_completion_tokens.
        return max(requested + 4096, 8192)
    return requested


def _uses_max_completion_tokens(model: str) -> bool:
    """OpenAI reasoning / GPT-5+ chat models reject legacy `max_tokens`."""
    mid = (model or "").strip().lower()
    return mid.startswith(("gpt-5", "o1", "o3", "o4"))


def _apply_token_limit(kw: dict[str, Any], *, model: str, max_tokens: int) -> None:
    if _uses_max_completion_tokens(model):
        kw["max_completion_tokens"] = max_tokens
    else:
        kw["max_tokens"] = max_tokens


def _json_reasoning_effort(model: str) -> str | None:
    """Снижаем reasoning budget для structured JSON — иначе content может быть пустым."""
    mid = (model or "").strip().lower()
    if not mid.startswith("gpt-5"):
        return None
    # gpt-5.1+ поддерживают none; базовый gpt-5 — только low/medium/high.
    if mid.startswith(("gpt-5.1", "gpt-5.2", "gpt-5.5")):
        return "none"
    return "low"


def _message_content(resp: Any) -> str | None:
    try:
        return (resp.choices[0].message.content or "").strip() or None
    except (AttributeError, IndexError, TypeError):
        return None


def _build_chat_kwargs(
    *,
    model: str,
    messages: list[dict[str, str]],
    temperature: float,
    max_tokens: int,
    reasoning_effort: str | None = None,
) -> dict[str, Any]:
    kw: dict[str, Any] = {"model": model, "messages": messages}
    _apply_token_limit(kw, model=model, max_tokens=max_tokens)
    # GPT-5+ chat accepts only the default temperature; omit custom values.
    if not _uses_max_completion_tokens(model):
        kw["temperature"] = temperature
    if reasoning_effort and _uses_max_completion_tokens(model):
        kw["reasoning_effort"] = reasoning_effort
    return kw


def chat_completion_text(
    client: Any,
    *,
    model: str,
    messages: list[dict[str, str]],
    temperature: float,
    max_tokens: int,
    json_object: bool,
) -> str | None:
    """Возвращает текст ответа ассистента или None при полном сбое."""
    effective_max = resolve_max_tokens(max_tokens, model=model)
    reasoning_effort = _json_reasoning_effort(model) if json_object else None
    base_kw = _build_chat_kwargs(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=effective_max,
        reasoning_effort=reasoning_effort,
    )
    if json_object:
        try:
            resp = client.chat.completions.create(
                **base_kw,
                response_format={"type": "json_object"},
            )
            text = _message_content(resp)
            if text:
                return text
            logger.warning(
                "LLM json_object returned empty content (model=%s); retrying without JSON mode",
                model,
            )
        except Exception as exc:
            logger.warning(
                "LLM chat with response_format=json_object failed (%s); retrying without JSON mode",
                exc,
            )
    try:
        resp = client.chat.completions.create(**base_kw)
        return _message_content(resp)
    except Exception as exc:
        logger.warning("LLM chat completion failed: %s", exc, exc_info=True)
        return None


def chat_completion_plain(
    client: Any,
    *,
    model: str,
    messages: list[dict[str, str]],
    temperature: float,
    max_tokens: int,
) -> str | None:
    """Обычный chat completion без `response_format` (narrative, таро, прогнозы и т.д.)."""
    try:
        kw = _build_chat_kwargs(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=resolve_max_tokens(max_tokens, model=model),
        )
        resp = client.chat.completions.create(**kw)
        return _message_content(resp)
    except Exception as exc:
        logger.warning("LLM chat completion failed: %s", exc, exc_info=True)
        return None

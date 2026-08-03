"""OpenAI-совместимый chat-клиент: официальный API, vLLM, LiteLLM, прокси и т.п.

Ключ и base_url читаются из настроек; Guidance и другие модули могут вызывать один и тот же клиент.
"""

from __future__ import annotations

import logging
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Any, Iterator

from todayflow_backend.core.config import settings

logger = logging.getLogger(__name__)

_llm_operation_ctx: ContextVar[str] = ContextVar("llm_operation", default="sync")


@contextmanager
def llm_operation(operation: str) -> Iterator[None]:
    """Scope LLM client policy (sync vs background) for nested calls."""
    token = _llm_operation_ctx.set((operation or "sync").strip().lower() or "sync")
    try:
        yield
    finally:
        _llm_operation_ctx.reset(token)


def is_gemini_configured() -> bool:
    return bool((settings.gemini_api_key or "").strip())


def is_nebius_configured() -> bool:
    return bool((settings.nebius_api_key or "").strip())


def is_llm_chat_configured() -> bool:
    provider = (settings.llm_provider or "openai").strip().lower()
    if provider == "gemini":
        return is_gemini_configured()
    if provider == "nebius":
        return is_nebius_configured()
    key = (settings.llm_chat_api_key or settings.openai_api_key or settings.nebius_api_key or "").strip()
    return bool(key)


def _resolve_llm_credentials() -> tuple[str, str] | None:
    """Возвращает (api_key, base_url) для активного chat-провайдера."""
    provider = (settings.llm_provider or "openai").strip().lower()
    if provider == "gemini":
        key = (settings.gemini_api_key or "").strip()
        if not key:
            return None
        return key, settings.gemini_base_url.rstrip("/")

    if provider == "nebius":
        key = (settings.nebius_api_key or "").strip()
        if not key:
            return None
        base = (settings.nebius_base_url or "https://api.tokenfactory.nebius.com/v1/").strip()
        return key, base.rstrip("/")

    key = (settings.llm_chat_api_key or settings.openai_api_key or "").strip()
    if not key:
        # Convenience: NEBIUS_API_KEY alone + OPENAI_BASE_URL pointing at Token Factory.
        nebius_key = (settings.nebius_api_key or "").strip()
        base_hint = (settings.openai_base_url or "").strip().lower()
        if nebius_key and "nebius" in base_hint:
            return nebius_key, settings.openai_base_url.strip().rstrip("/")
        return None
    base = (settings.openai_base_url or "").strip()
    return key, base.rstrip("/") if base else ""


def get_openai_compatible_client(*, operation: str | None = None) -> Any | None:
    """Собирает `openai.OpenAI` с опциональным `base_url` для своего провайдера.

    operation:
      sync — read-path / accidental calls: short timeout, no SDK retries
      background — enrichment jobs: longer timeout, still no SDK retries
        (job-level attempt_count owns retries)
    """
    creds = _resolve_llm_credentials()
    if creds is None:
        return None
    try:
        import openai
    except ImportError:
        return None
    key, base_url = creds
    # SDK default retries (2) multiply each ReadTimeout into multi-minute hangs — stay off.
    # Job runners may re-attempt via GenerationJob.max_attempts instead.
    op = (operation or _llm_operation_ctx.get() or "sync").strip().lower()
    base_timeout = float(getattr(settings, "llm_http_timeout_seconds", 12.0) or 12.0)
    if op == "background":
        timeout_s = float(getattr(settings, "llm_background_timeout_seconds", 180.0) or 180.0)
    else:
        timeout_s = base_timeout
    kw: dict[str, Any] = {"api_key": key, "timeout": timeout_s, "max_retries": 0}
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
    timeout_s = float(getattr(settings, "llm_http_timeout_seconds", 22.0) or 22.0)
    return openai.OpenAI(
        api_key=key,
        base_url=settings.gemini_base_url.rstrip("/"),
        timeout=timeout_s,
        max_retries=0,
    )


def resolve_default_chat_model() -> str:
    provider = (settings.llm_provider or "openai").strip().lower()
    if provider == "gemini":
        return settings.gemini_model
    if provider == "nebius":
        # Explicit LLM_DEFAULT_MODEL wins when operator overrides the Nebius catalog id.
        override = (settings.llm_default_model or "").strip()
        if override and override not in ("gpt-4o-mini", "gpt-5.5"):
            return override
        return settings.nebius_model
    return settings.llm_default_model


def resolve_guidance_chat_model() -> str:
    provider = (settings.llm_provider or "openai").strip().lower()
    if provider == "gemini":
        return settings.gemini_model
    if provider == "nebius":
        override = (settings.guidance_llm_model or "").strip()
        if override and override not in ("gpt-4o-mini", "gpt-5.5"):
            return override
        return settings.nebius_model
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
    if mid.startswith("moonshotai/kimi") or "/kimi" in mid:
        # Kimi often spends a large share of the budget on hidden reasoning before content;
        # truncated JSON is common below ~3.5–4k completion tokens for rich day_story contracts.
        return max(requested * 2 + 800, 4000)
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


def _is_timeout_like_error(exc: BaseException) -> bool:
    """Client/server deadline — do not burn a second plain completion in the same attempt."""
    name = type(exc).__name__.lower()
    msg = str(exc).lower()
    tokens = (
        "timeout",
        "timed out",
        "deadline_exceeded",
        "deadline exceeded",
        "readtimeout",
        "apitimeouterror",
    )
    if any(t in name for t in ("timeout", "deadline")):
        return True
    return any(t in msg for t in tokens)


def classify_llm_call_failure(exc: BaseException | None = None, *, http_status: int | None = None) -> str:
    """Coarse failure class for ops logs (timeout vs throttle vs upstream vs other)."""
    status = http_status
    if status is None and exc is not None:
        status = getattr(exc, "status_code", None)
        if status is None:
            resp = getattr(exc, "response", None)
            status = getattr(resp, "status_code", None)
    if status == 429:
        return "rate_limited"
    if status in {408, 504}:
        return "timeout"
    if status == 404 or (exc is not None and _is_model_not_found_error(exc)):
        return "model_unavailable"
    if status in {502, 503}:
        return "upstream_unavailable"
    if exc is not None and _is_timeout_like_error(exc):
        return "timeout"
    if exc is not None:
        msg = str(exc).lower()
        if "429" in msg or "rate limit" in msg or "too many requests" in msg:
            return "rate_limited"
        if "finish_reason" in msg:
            return "stream_incomplete"
        if any(code in msg for code in ("502", "503", "504", "bad gateway", "unavailable")):
            return "upstream_unavailable"
    return "other"


def _is_model_not_found_error(exc: BaseException) -> bool:
    msg = str(exc).lower()
    tokens = (
        "does not exist",
        "model_not_found",
        "model not found",
        "unknown model",
        "invalid model",
        "no such model",
    )
    return any(t in msg for t in tokens)


def resolve_chat_model_chain(primary: str) -> list[str]:
    """Primary model, then optional Nebius fallback when catalog/maintenance drops primary."""
    chain: list[str] = []
    primary_id = (primary or "").strip()
    if primary_id:
        chain.append(primary_id)
    provider = (settings.llm_provider or "openai").strip().lower()
    if provider != "nebius":
        return chain or [primary_id or settings.llm_default_model]
    fallback = (getattr(settings, "nebius_fallback_model", None) or "").strip()
    if fallback and fallback not in chain:
        chain.append(fallback)
    return chain or [settings.nebius_model]


def _should_try_model_fallback(failure_kind: str | None) -> bool:
    """Fallback to NEBIUS_FALLBACK_MODEL (Kimi) when primary has a provider problem.

    Includes timeout/empty/upstream/missing-model. Does **not** include throttle (429)
    — a second model under rate limit usually fails the same way.
    Identical retry of the same model on timeout is still forbidden at the native
    attempt loop; this only switches DeepSeek → Kimi once.
    """
    return failure_kind in {
        "model_unavailable",
        "upstream_unavailable",
        "empty",
        "timeout",
        "other",
    }


def chat_completion_text(
    client: Any,
    *,
    model: str,
    messages: list[dict[str, str]],
    temperature: float,
    max_tokens: int,
    json_object: bool,
) -> str | None:
    """Возвращает текст ответа ассистента или None при полном сбое.

    JSON mode may fall back to plain completion when the provider rejects
    ``response_format`` or returns empty content.

    When ``LLM_PROVIDER=nebius``, primary is DeepSeek-V4-Pro; on provider failure
    (including timeout/empty/upstream/missing model) retries once with
    ``NEBIUS_FALLBACK_MODEL`` (Kimi-K2.6). Throttle (429) does not switch models.
    """
    chain = resolve_chat_model_chain(model)
    last_kind: str | None = None
    for idx, mid in enumerate(chain):
        text, kind = _chat_completion_text_once(
            client,
            model=mid,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            json_object=json_object,
        )
        if text:
            if idx > 0:
                logger.warning(
                    "LLM model fallback succeeded primary=%s fallback=%s",
                    chain[0],
                    mid,
                )
            return text
        last_kind = kind
        next_mid = chain[idx + 1] if idx + 1 < len(chain) else None
        if next_mid and _should_try_model_fallback(kind):
            logger.warning(
                "LLM primary model failed kind=%s model=%s; trying fallback=%s",
                kind,
                mid,
                next_mid,
            )
            continue
        break
    if last_kind:
        logger.warning("LLM chat completion exhausted models kind=%s chain=%s", last_kind, chain)
    return None


def _chat_completion_text_once(
    client: Any,
    *,
    model: str,
    messages: list[dict[str, str]],
    temperature: float,
    max_tokens: int,
    json_object: bool,
) -> tuple[str | None, str | None]:
    """Single-model attempt. Returns (text, failure_kind). failure_kind is None on success."""
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
                return text, None
            logger.warning(
                "LLM json_object returned empty content (model=%s); retrying without JSON mode",
                model,
            )
        except Exception as exc:
            kind = classify_llm_call_failure(exc)
            if kind == "timeout":
                logger.warning(
                    "LLM json_object failed class=%s model=%s err=%s; skip plain retry in same attempt",
                    kind,
                    model,
                    exc,
                )
                return None, kind
            if kind == "model_unavailable":
                logger.warning(
                    "LLM json_object failed class=%s model=%s (%s); skip plain retry",
                    kind,
                    model,
                    exc,
                )
                return None, kind
            logger.warning(
                "LLM chat with response_format=json_object failed class=%s (%s); retrying without JSON mode",
                kind,
                exc,
            )
    try:
        resp = client.chat.completions.create(**base_kw)
        text = _message_content(resp)
        if text:
            return text, None
        return None, "empty"
    except Exception as exc:
        kind = classify_llm_call_failure(exc)
        logger.warning(
            "LLM chat completion failed class=%s model=%s: %s",
            kind,
            model,
            exc,
            exc_info=True,
        )
        return None, kind


def chat_completion_plain(
    client: Any,
    *,
    model: str,
    messages: list[dict[str, str]],
    temperature: float,
    max_tokens: int,
) -> str | None:
    """Обычный chat completion без `response_format` (narrative, таро, прогнозы и т.д.)."""
    text, _kind, _mid = chat_completion_plain_with_status(
        client,
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return text


def chat_completion_plain_with_status(
    client: Any,
    *,
    model: str,
    messages: list[dict[str, str]],
    temperature: float,
    max_tokens: int,
) -> tuple[str | None, str | None, str | None]:
    """Plain chat completion with failure class for ops instrumentation.

    Returns ``(text, failure_class, model_id)``.
    ``failure_class`` is set when text is None: timeout | empty | throttle |
    model_unavailable | upstream_unavailable | other.
    Nebius chain: primary then Kimi on provider failure including timeout
    (via ``_should_try_model_fallback``).
    """
    chain = resolve_chat_model_chain(model)
    last_kind: str | None = None
    last_mid: str | None = None
    for idx, mid in enumerate(chain):
        last_mid = mid
        try:
            kw = _build_chat_kwargs(
                model=mid,
                messages=messages,
                temperature=temperature,
                max_tokens=resolve_max_tokens(max_tokens, model=mid),
            )
            resp = client.chat.completions.create(**kw)
            text = _message_content(resp)
            if text:
                if idx > 0:
                    logger.warning(
                        "LLM plain model fallback succeeded primary=%s fallback=%s",
                        chain[0],
                        mid,
                    )
                return text, None, mid
            last_kind = "empty"
        except Exception as exc:
            last_kind = classify_llm_call_failure(exc)
            logger.warning(
                "LLM chat completion failed class=%s model=%s: %s",
                last_kind,
                mid,
                exc,
                exc_info=True,
            )
        next_mid = chain[idx + 1] if idx + 1 < len(chain) else None
        if next_mid and _should_try_model_fallback(last_kind):
            logger.warning(
                "LLM plain primary failed kind=%s model=%s; trying fallback=%s",
                last_kind,
                mid,
                next_mid,
            )
            continue
        break
    return None, last_kind or "other", last_mid

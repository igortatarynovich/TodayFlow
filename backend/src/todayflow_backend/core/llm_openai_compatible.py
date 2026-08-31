"""OpenAI-совместимый chat-клиент: официальный API, vLLM, LiteLLM, прокси и т.п.

Ключ и base_url читаются из настроек; Guidance и другие модули могут вызывать один и тот же клиент.
"""

from __future__ import annotations

import logging
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field
from time import perf_counter
from typing import Any, Iterator

from todayflow_backend.core.config import settings
from todayflow_backend.core.llm_usage_telemetry_v1 import (
    emit_llm_usage_v1,
    llm_call_context,
    parse_usage_obj,
)

logger = logging.getLogger(__name__)

_llm_operation_ctx: ContextVar[str] = ContextVar("llm_operation", default="sync")

# Re-export so call sites can tag feature/user without a second import.
_ = llm_call_context


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


def _resolve_llm_credentials(*, model: str | None = None) -> tuple[str, str] | None:
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
        base = (settings.nebius_base_url or "https://api.tokenfactory.us-central1.nebius.com/v1/").strip()
        complex_mid = (getattr(settings, "nebius_complex_model", None) or "").strip()
        complex_base = (getattr(settings, "nebius_complex_base_url", None) or "").strip()
        mid = (model or "").strip()
        if mid and complex_mid and mid == complex_mid and complex_base:
            base = complex_base
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


def get_openai_compatible_client(*, operation: str | None = None, model: str | None = None) -> Any | None:
    """Собирает `openai.OpenAI` с опциональным `base_url` для своего провайдера.

    operation:
      sync — read-path / accidental calls: short timeout, no SDK retries
      background — enrichment jobs: longer timeout, still no SDK retries
        (job-level attempt_count owns retries)
    model:
      When Nebius + matches ``NEBIUS_COMPLEX_MODEL``, uses ``NEBIUS_COMPLEX_BASE_URL``
      (K3 on eu-west2). Otherwise primary ``NEBIUS_BASE_URL`` (K2.6 on us-central1).
    """
    creds = _resolve_llm_credentials(model=model)
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
        # Streaming Kimi: read = idle between SSE chunks (not total wall).
        # Non-stream still uses the same read budget as a full-response wait.
        read_s = float(getattr(settings, "llm_stream_read_timeout_seconds", 90.0) or 90.0)
        try:
            import httpx

            timeout_s: Any = httpx.Timeout(
                connect=30.0,
                read=read_s,
                write=read_s,
                pool=30.0,
            )
        except ImportError:
            timeout_s = read_s
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
    """Primary model for routine generation (day native, windows, narrative, …).

    Nebius SoT: ``NEBIUS_MODEL`` = Kimi-K2.6. Do not use this for CE portrait /
    natal-decode — call ``resolve_complex_chat_model`` instead.
    """
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


def resolve_complex_chat_model() -> str:
    """K3 (or ``NEBIUS_COMPLEX_MODEL``) for multi-step portrait / natal-decode only.

    Gate: use only where quality delta vs K2.6 is product-visible and the call is a
    user-justified operation (CE Stage 2–4 publish, profile disclosure funnel,
    natal decode depth). Empty ``NEBIUS_COMPLEX_MODEL`` → same as primary.
    """
    provider = (settings.llm_provider or "openai").strip().lower()
    if provider == "nebius":
        complex_id = (getattr(settings, "nebius_complex_model", None) or "").strip()
        if complex_id:
            return complex_id
        return settings.nebius_model
    return resolve_default_chat_model()


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
    """Legacy thinking pad. Not cost SoT — ``llm_cost_guard_v1`` clamps before the provider.

    When the cost guard is on, these floors are irrelevant: the router min()s against
    the operation class cap. Kept for ``LLM_COST_GUARD=0`` protocol tests.
    """
    requested = max(1, int(requested))
    try:
        from todayflow_backend.core.llm_cost_guard_v1 import is_cost_guard_enabled

        if is_cost_guard_enabled():
            return requested
    except Exception:
        pass
    provider = (settings.llm_provider or "openai").strip().lower()
    if provider == "gemini":
        if requested >= 800:
            return max(requested, settings.gemini_max_tokens)
        return requested
    mid = (model or resolve_default_chat_model()).strip().lower()
    if _uses_max_completion_tokens(mid):
        return max(requested + 4096, 8192)
    if _is_kimi_k3(mid):
        return max(requested * 2 + 800, 16000)
    if _is_kimi_model(mid):
        return max(requested * 2 + 800, 4000)
    return requested


def _is_kimi_model(model: str) -> bool:
    mid = (model or "").strip().lower()
    return mid.startswith("moonshotai/kimi") or "/kimi" in mid or mid.startswith("kimi-")


def _is_kimi_k3(model: str) -> bool:
    mid = (model or "").strip().lower()
    return "kimi-k3" in mid


def _should_stream_completion(model: str) -> bool:
    """Moonshot: thinking models sit silent until done unless streamed — use SSE."""
    if not bool(getattr(settings, "llm_stream_completions", True)):
        return False
    return _is_kimi_model(model)


def _uses_max_completion_tokens(model: str) -> bool:
    """OpenAI reasoning / GPT-5+ chat models reject legacy `max_tokens`."""
    mid = (model or "").strip().lower()
    return mid.startswith(("gpt-5", "o1", "o3", "o4"))


def _apply_token_limit(kw: dict[str, Any], *, model: str, max_tokens: int) -> None:
    if _uses_max_completion_tokens(model):
        kw["max_completion_tokens"] = max_tokens
    else:
        kw["max_tokens"] = max_tokens


def _reasoning_effort_for_model(model: str, *, json_object: bool = False) -> str | None:
    """Cap always-on / heavy reasoning so content arrives before idle timeouts."""
    mid = (model or "").strip().lower()
    if _is_kimi_k3(mid):
        # K3 thinking cannot be disabled; low keeps product JSON latency usable.
        return "low"
    if not mid.startswith("gpt-5"):
        return None
    if not json_object:
        return None
    # gpt-5.1+ поддерживают none; базовый gpt-5 — только low/medium/high.
    if mid.startswith(("gpt-5.1", "gpt-5.2", "gpt-5.5")):
        return "none"
    return "low"


def _json_reasoning_effort(model: str) -> str | None:
    """Back-compat alias for structured JSON paths."""
    return _reasoning_effort_for_model(model, json_object=True)


def _message_content(resp: Any) -> str | None:
    try:
        return (resp.choices[0].message.content or "").strip() or None
    except (AttributeError, IndexError, TypeError):
        return None


@dataclass
class _StreamCollect:
    text: str | None
    usage: dict[str, int] = field(default_factory=dict)
    reasoning_chars: int = 0
    content_chars: int = 0
    finish_reason: str | None = None


def _delta_text(delta: Any, *names: str) -> str:
    for name in names:
        piece = getattr(delta, name, None)
        if piece:
            return str(piece)
        if isinstance(delta, dict) and delta.get(name):
            return str(delta.get(name))
    return ""


def _consume_chat_stream(stream: Any) -> _StreamCollect:
    """Accumulate assistant ``content``; count ``reasoning_content`` for COGS, do not return it."""
    parts: list[str] = []
    reasoning_chars = 0
    usage: dict[str, int] = {}
    finish_reason: str | None = None
    for chunk in stream:
        chunk_usage = parse_usage_obj(getattr(chunk, "usage", None))
        if chunk_usage:
            usage = chunk_usage
        try:
            choices = chunk.choices or []
        except (AttributeError, TypeError):
            continue
        if not choices:
            continue
        choice0 = choices[0]
        fr = getattr(choice0, "finish_reason", None)
        if fr:
            finish_reason = str(fr)
        delta = getattr(choice0, "delta", None)
        if delta is None:
            continue
        piece = _delta_text(delta, "content")
        if piece:
            parts.append(piece)
        reasoning_chars += len(_delta_text(delta, "reasoning_content", "reasoning"))
    text = "".join(parts).strip() or None
    return _StreamCollect(
        text=text,
        usage=usage,
        reasoning_chars=reasoning_chars,
        content_chars=len(text or ""),
        finish_reason=finish_reason,
    )


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
    # GPT-5+ and Kimi-K3: omit custom temperature (provider-fixed / rejected).
    if not _uses_max_completion_tokens(model) and not _is_kimi_k3(model):
        kw["temperature"] = temperature
    if reasoning_effort and (_uses_max_completion_tokens(model) or _is_kimi_k3(model)):
        kw["reasoning_effort"] = reasoning_effort
    return kw


def _prompt_chars(messages: list[dict[str, str]]) -> int:
    return sum(len(str(m.get("content") or "")) for m in messages)


def _is_stream_options_rejected(exc: BaseException) -> bool:
    msg = str(exc).lower()
    return "stream_options" in msg or "include_usage" in msg


def _create_chat_collect(
    client: Any,
    *,
    model: str,
    messages: list[dict[str, str]],
    temperature: float,
    max_tokens: int,
    reasoning_effort: str | None = None,
    response_format: dict[str, Any] | None = None,
) -> str | None:
    """One provider call; streams Kimi to avoid idle ReadTimeout during thinking."""
    t0 = perf_counter()
    streamed = _should_stream_completion(model)
    json_object = bool(response_format)
    usage: dict[str, int] = {}
    reasoning_chars = 0
    content_chars = 0
    text: str | None = None
    failure: str | None = None
    tokens_source = "provider_usage"
    reservation_usd = 0.0
    requested_model = model
    requested_max = max_tokens

    try:
        from todayflow_backend.core.llm_cost_guard_v1 import (
            apply_provider_policy,
            is_cost_guard_enabled,
            settle_reservation,
            trip_daily_ceiling,
        )
    except Exception:
        apply_provider_policy = None  # type: ignore[assignment]
        is_cost_guard_enabled = lambda: False  # noqa: E731
        settle_reservation = lambda *_a, **_k: None  # noqa: E731
        trip_daily_ceiling = lambda **_k: None  # noqa: E731

    if is_cost_guard_enabled() and apply_provider_policy is not None:
        decision = apply_provider_policy(
            model=model,
            max_tokens=max_tokens,
            prompt_chars=_prompt_chars(messages),
        )
        reservation_usd = decision.reservation_usd
        if decision.action == "deny":
            failure = "budget_exhausted"
            emit_llm_usage_v1(
                model=decision.model,
                prompt_chars=_prompt_chars(messages),
                tokens_source="denied",
                max_tokens=decision.max_tokens,
                latency_ms=int((perf_counter() - t0) * 1000),
                ok=False,
                failure_class=failure,
                streamed=False,
                json_object=json_object,
            )
            settle_reservation(reservation_usd, 0.0)
            return None
        model = decision.model
        max_tokens = decision.max_tokens
        streamed = _should_stream_completion(model)
        if decision.rebind_client:
            from unittest.mock import Mock

            if not isinstance(client, Mock):
                rebound = get_openai_compatible_client(model=model)
                if rebound is not None:
                    client = rebound

    def _emit(*, ok: bool) -> float:
        event = emit_llm_usage_v1(
            model=model,
            input_tokens=usage.get("prompt_tokens") or None,
            output_tokens=usage.get("completion_tokens") or None,
            reasoning_tokens=usage.get("reasoning_tokens") or None,
            cached_tokens=usage.get("cached_tokens") or 0,
            prompt_chars=_prompt_chars(messages),
            content_chars=content_chars,
            reasoning_chars=reasoning_chars,
            tokens_source=tokens_source if usage else "estimated_chars",
            max_tokens=max_tokens,
            latency_ms=int((perf_counter() - t0) * 1000),
            ok=ok,
            failure_class=failure,
            streamed=streamed,
            json_object=json_object,
        )
        return float(event.get("estimated_cost_usd") or 0.0)

    kw = _build_chat_kwargs(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        reasoning_effort=reasoning_effort,
    )
    if response_format is not None:
        kw["response_format"] = response_format
    try:
        if streamed:
            kw["stream"] = True
            kw["stream_options"] = {"include_usage": True}
            try:
                stream = client.chat.completions.create(**kw)
            except Exception as exc:
                if not _is_stream_options_rejected(exc):
                    raise
                kw.pop("stream_options", None)
                stream = client.chat.completions.create(**kw)
            collected = _consume_chat_stream(stream)
            text = collected.text
            usage = collected.usage
            reasoning_chars = collected.reasoning_chars
            content_chars = collected.content_chars
        else:
            resp = client.chat.completions.create(**kw)
            text = _message_content(resp)
            usage = parse_usage_obj(getattr(resp, "usage", None))
            content_chars = len(text or "")
        if not usage:
            tokens_source = "estimated_chars"
        if not text:
            failure = "empty"
        cost = _emit(ok=bool(text))
        settle_reservation(reservation_usd, cost)
        return text
    except Exception as exc:
        failure = classify_llm_call_failure(exc)
        cost = _emit(ok=False)
        settle_reservation(reservation_usd, cost)
        if failure == "billing_suspended":
            trip_daily_ceiling(reason="provider_402")
        raise


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
    if status == 402:
        return "billing_suspended"
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
        if status == 402 or "402" in msg or "payment required" in msg:
            return "billing_suspended"
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
    """Fallback to NEBIUS_FALLBACK_MODEL when primary has a provider problem.

    Includes timeout/empty/upstream/missing-model. Does **not** include throttle (429)
    — a second model under rate limit usually fails the same way.
    Identical retry of the same model on timeout is still forbidden at the native
    attempt loop; this only switches primary → fallback once on attempt0.
    """
    if failure_kind in {"budget_exhausted", "billing_suspended"}:
        return False
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

    When ``LLM_PROVIDER=nebius``, primary is ``NEBIUS_MODEL`` (K2.6). Optional
    ``NEBIUS_FALLBACK_MODEL`` retries once on provider failure when set.
    Throttle (429) does not switch models. Kimi calls stream by default.
    Pass ``resolve_complex_chat_model()`` as ``model`` only for CE/natal ops.
    """
    chain = resolve_chat_model_chain(model)
    last_kind: str | None = None
    for idx, mid in enumerate(chain):
        with llm_call_context(retry_reason="model_fallback" if idx > 0 else None):
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
    reasoning_effort = _reasoning_effort_for_model(model, json_object=json_object)
    if json_object:
        try:
            text = _create_chat_collect(
                client,
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=effective_max,
                reasoning_effort=reasoning_effort,
                response_format={"type": "json_object"},
            )
            if text:
                return text, None
            try:
                from todayflow_backend.core.llm_cost_guard_v1 import current_guard_meta

                if current_guard_meta().get("cost_guard_action") == "deny":
                    return None, "budget_exhausted"
            except Exception:
                pass
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
        plain_retry = bool(json_object)
        with llm_call_context(retry_reason="json_mode_fallback" if plain_retry else None):
            text = _create_chat_collect(
                client,
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=effective_max,
                reasoning_effort=reasoning_effort,
            )
        if text:
            return text, None
        try:
            from todayflow_backend.core.llm_cost_guard_v1 import current_guard_meta

            if current_guard_meta().get("cost_guard_action") == "deny":
                return None, "budget_exhausted"
        except Exception:
            pass
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
    allow_model_fallback: bool = True,
) -> str | None:
    """Обычный chat completion без `response_format` (narrative, таро, прогнозы и т.д.)."""
    text, _kind, _mid = chat_completion_plain_with_status(
        client,
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        allow_model_fallback=allow_model_fallback,
    )
    return text


def chat_completion_plain_with_status(
    client: Any,
    *,
    model: str,
    messages: list[dict[str, str]],
    temperature: float,
    max_tokens: int,
    allow_model_fallback: bool = True,
) -> tuple[str | None, str | None, str | None]:
    """Plain chat completion with failure class for ops instrumentation.

    Returns ``(text, failure_class, model_id)``.
    ``failure_class`` is set when text is None: timeout | empty | throttle |
    model_unavailable | upstream_unavailable | other.
    Nebius chain (when ``allow_model_fallback`` and fallback configured):
    primary then fallback on provider failure including timeout.
    Kimi uses SSE streaming so thinking does not idle-timeout the HTTP client.
    """
    mid0 = (model or "").strip()
    chain = resolve_chat_model_chain(mid0) if allow_model_fallback else ([mid0] if mid0 else [])
    last_kind: str | None = None
    last_mid: str | None = None
    for idx, mid in enumerate(chain):
        last_mid = mid
        try:
            with llm_call_context(retry_reason="model_fallback" if idx > 0 else None):
                text = _create_chat_collect(
                    client,
                    model=mid,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=resolve_max_tokens(max_tokens, model=mid),
                    reasoning_effort=_reasoning_effort_for_model(mid, json_object=False),
                )
            if text:
                if idx > 0:
                    logger.warning(
                        "LLM plain model fallback succeeded primary=%s fallback=%s",
                        chain[0],
                        mid,
                    )
                return text, None, mid
            last_kind = "empty"
            try:
                from todayflow_backend.core.llm_cost_guard_v1 import current_guard_meta

                if current_guard_meta().get("cost_guard_action") == "deny":
                    last_kind = "budget_exhausted"
            except Exception:
                pass
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

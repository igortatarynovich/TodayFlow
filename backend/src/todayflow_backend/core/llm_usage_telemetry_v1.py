"""Per-request LLM usage / AI COGS telemetry.

Every provider call in ``llm_openai_compatible`` emits one ``llm_usage_v1`` event:
feature, model, token counts (incl. reasoning/cached when the provider reports them),
latency, estimated USD. This is ops instrumentation — not a generation SoT.

Canon: docs/API_MEMORY_AND_LEARNING_LAYER.md §10 · docs/LLM_QUALITY_AND_PROMPT_EVOLUTION.md
(AI COGS). Prices are observed Nebius Token Factory rates (HostFlow bill 2026-07-19..08-18),
not a live catalog fetch.
"""

from __future__ import annotations

import json
import logging
import os
import sys
import threading
from collections import deque
from contextlib import contextmanager
from contextvars import ContextVar
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterator
from uuid import uuid4

logger = logging.getLogger(__name__)

LLM_USAGE_EVENT_V1 = "llm_usage_v1"
DEFAULT_FEATURE = "unlabeled"

# Product vs infra. Outer trigger wins once set; emit infers eval/script if still empty.
ALLOWED_TRIGGERS = frozenset({"user", "prewarm", "eval", "script", "background"})
RETRY_REASONS = frozenset(
    {
        "empty_content",
        "parse_failed",
        "gate_retry",
        "json_mode_fallback",
        "model_fallback",
        "schema_retry",
        "quality_retry",
        "timeout",
        "budget_downgrade",
    }
)

# USD per 1M tokens: (input, output). Output includes billed reasoning.
# Source: Nebius Token Factory invoice HostFlow-nh2, 19.07.2026–18.08.2026.
_USD_PER_M: dict[str, tuple[float, float]] = {
    "moonshotai/kimi-k2.6": (0.95, 4.00),
    "moonshotai/kimi-k3": (3.00, 15.00),
    "deepseek-ai/deepseek-v4-pro": (1.75, 3.48),
    "qwen/qwen3-235b-a22b-instruct-2507": (0.23, 0.60),
    "qwen/qwen3-30b-a3b-instruct-2507": (0.10, 0.32),
}

_DEFAULT_USD_PER_M = (1.00, 4.00)

_ctx: ContextVar[dict[str, Any]] = ContextVar("llm_usage_ctx", default={})
_recent: deque[dict[str, Any]] = deque(maxlen=512)
_recent_lock = threading.Lock()
_file_lock = threading.Lock()


def _normalize_model_key(model: str) -> str:
    return (model or "").strip().lower()


def usd_per_million(model: str) -> tuple[float, float]:
    mid = _normalize_model_key(model)
    if mid in _USD_PER_M:
        return _USD_PER_M[mid]
    for key, pair in _USD_PER_M.items():
        if key in mid or mid.endswith(key.split("/", 1)[-1]):
            return pair
    return _DEFAULT_USD_PER_M


def estimate_cost_usd(
    *,
    model: str,
    input_tokens: int,
    output_tokens: int,
    reasoning_tokens: int = 0,
) -> float:
    """USD from **billed** tokens.

    ``output_tokens`` is provider ``completion_tokens`` (reasoning already inside
    on OpenAI-compatible / Moonshot). ``reasoning_tokens`` is breakdown only —
    never added on top of output.
    """
    _ = reasoning_tokens
    inp_rate, out_rate = usd_per_million(model)
    cost = (max(0, int(input_tokens)) / 1_000_000.0) * inp_rate
    cost += (max(0, int(output_tokens)) / 1_000_000.0) * out_rate
    return round(cost, 6)


def estimate_tokens_from_chars(chars: int) -> int:
    """Rough token estimate when the provider omits usage (mixed RU/JSON ≈ 4 chars)."""
    n = max(0, int(chars or 0))
    if n <= 0:
        return 0
    return max(1, n // 4)


def normalize_trigger(raw: str | None) -> str:
    t = (raw or "").strip().lower()
    aliases = {"cron": "background", "job": "background", "cli": "script", "http": "user"}
    t = aliases.get(t, t)
    if t in ALLOWED_TRIGGERS:
        return t
    return ""


def infer_process_trigger() -> str:
    env = (os.environ.get("LLM_TRIGGER") or os.environ.get("TODAYFLOW_LLM_TRIGGER") or "").strip()
    hit = normalize_trigger(env)
    if hit:
        return hit
    argv = " ".join(sys.argv).replace("\\", "/")
    if "/evals/" in argv or argv.startswith("evals/"):
        return "eval"
    if "/scripts/" in argv:
        return "script"
    return ""


def normalize_retry_reason(raw: str | None) -> str | None:
    t = (raw or "").strip().lower()
    if not t:
        return None
    aliases = {
        "empty": "empty_content",
        "empty_llm_content": "empty_content",
        "parse": "parse_failed",
        "json_parse": "parse_failed",
        "json_parse_failed": "parse_failed",
        "gate": "gate_retry",
        "json_fallback": "json_mode_fallback",
        "fallback": "model_fallback",
    }
    t = aliases.get(t, t)
    return t


@contextmanager
def llm_call_context(
    *,
    feature: str | None = None,
    user_id: int | str | None = None,
    request_id: str | None = None,
    trigger: str | None = None,
    operation: str | None = None,
    operation_id: str | None = None,
    ensure_operation: bool = False,
    attempt: int | None = None,
    retry_reason: str | None = None,
) -> Iterator[None]:
    """Tag nested LLM provider calls.

    Inherit: feature / attempt / retry_reason — inner wins.
    trigger — explicit inner overwrites (prewarm vs leaked HTTP user).
    operation_id — fill-if-empty unless passed; ``ensure_operation`` mints if missing.
    """
    parent = dict(_ctx.get() or {})
    child = dict(parent)
    if feature and str(feature).strip():
        child["feature"] = str(feature).strip()
    if user_id is not None and str(user_id).strip():
        child["user_id"] = str(user_id).strip()
    if request_id and str(request_id).strip():
        child["request_id"] = str(request_id).strip()
    trig = normalize_trigger(trigger)
    if trig:
        child["trigger"] = trig
    if operation and str(operation).strip() and not child.get("operation"):
        child["operation"] = str(operation).strip()
    if operation_id and str(operation_id).strip():
        child["operation_id"] = str(operation_id).strip()
    elif ensure_operation and not child.get("operation_id"):
        child["operation_id"] = str(uuid4())
        if operation and str(operation).strip():
            child["operation"] = str(operation).strip()
        elif feature and str(feature).strip() and not child.get("operation"):
            child["operation"] = str(feature).strip()
    if attempt is not None:
        child["attempt"] = max(0, int(attempt))
    if retry_reason is not None:
        child["retry_reason"] = normalize_retry_reason(retry_reason)
    token = _ctx.set(child)
    try:
        yield
    finally:
        _ctx.reset(token)


def current_llm_call_context() -> dict[str, Any]:
    return dict(_ctx.get() or {})


def parse_usage_obj(usage: Any) -> dict[str, int]:
    """Extract prompt/completion/reasoning/cached token counts from SDK usage objects."""
    if usage is None:
        return {}
    prompt = _int_attr(usage, "prompt_tokens", "input_tokens")
    completion = _int_attr(usage, "completion_tokens", "output_tokens")
    total = _int_attr(usage, "total_tokens")
    reasoning = _int_attr(usage, "reasoning_tokens")
    cached = _int_attr(usage, "cached_tokens", "prompt_cache_hit_tokens")

    details = _attr(usage, "completion_tokens_details")
    if details is not None:
        reasoning = reasoning or _int_attr(details, "reasoning_tokens")

    pdetails = _attr(usage, "prompt_tokens_details")
    if pdetails is not None:
        cached = cached or _int_attr(pdetails, "cached_tokens")

    out: dict[str, int] = {}
    if prompt:
        out["prompt_tokens"] = prompt
    if completion:
        out["completion_tokens"] = completion
    if total:
        out["total_tokens"] = total
    if reasoning:
        out["reasoning_tokens"] = reasoning
    if cached:
        out["cached_tokens"] = cached
    return out


def emit_llm_usage_v1(
    *,
    model: str,
    input_tokens: int | None = None,
    output_tokens: int | None = None,
    reasoning_tokens: int | None = None,
    cached_tokens: int | None = None,
    prompt_chars: int = 0,
    content_chars: int = 0,
    reasoning_chars: int = 0,
    tokens_source: str = "provider_usage",
    max_tokens: int | None = None,
    latency_ms: int = 0,
    ok: bool = False,
    failure_class: str | None = None,
    streamed: bool = False,
    json_object: bool = False,
    feature: str | None = None,
    user_id: str | None = None,
    request_id: str | None = None,
    trigger: str | None = None,
    operation_id: str | None = None,
    attempt: int | None = None,
    retry_reason: str | None = None,
    cost_guard_action: str | None = None,
    cost_class: str | None = None,
    requested_model: str | None = None,
    requested_max_tokens: int | None = None,
    daily_spent_usd: float | None = None,
    daily_ceiling_usd: float | None = None,
) -> dict[str, Any]:
    ctx = current_llm_call_context()
    feat = (feature or ctx.get("feature") or DEFAULT_FEATURE).strip() or DEFAULT_FEATURE
    uid = user_id if user_id is not None else ctx.get("user_id")
    rid = (request_id or ctx.get("request_id") or "").strip() or None
    trig = normalize_trigger(trigger) or normalize_trigger(ctx.get("trigger")) or infer_process_trigger() or "unknown"
    op_id = (operation_id or ctx.get("operation_id") or rid or "").strip() or None
    op_name = (ctx.get("operation") or "").strip() or None
    attempt_n = int(attempt) if attempt is not None else int(ctx.get("attempt") or 0)
    retry = normalize_retry_reason(
        retry_reason if retry_reason is not None else ctx.get("retry_reason")
    )

    src = (tokens_source or "provider_usage").strip() or "provider_usage"
    in_tok = int(input_tokens or 0)
    out_tok = int(output_tokens or 0)
    has_provider_out = output_tokens is not None and int(output_tokens) > 0
    reason_tok = int(reasoning_tokens or 0) if reasoning_tokens is not None else 0
    cache_tok = int(cached_tokens or 0)

    if src == "denied":
        in_tok = 0
        out_tok = 0
        reason_tok = 0
        cost = 0.0
    elif not has_provider_out:
        # Estimate billed completion as content+reasoning; do not add reasoning again at cost time.
        content_est = estimate_tokens_from_chars(content_chars)
        reason_est = estimate_tokens_from_chars(reasoning_chars)
        if in_tok <= 0:
            in_tok = estimate_tokens_from_chars(prompt_chars)
        out_tok = content_est + reason_est
        if reason_tok <= 0:
            reason_tok = reason_est
        if in_tok or out_tok:
            src = "estimated_chars"
    elif reason_tok > out_tok:
        # Provider billed completion is SoT; clamp breakdown so reports cannot imply extra output.
        reason_tok = out_tok

    content_tok = max(0, out_tok - reason_tok) if reason_tok else out_tok
    if src != "denied":
        cost = estimate_cost_usd(
            model=model,
            input_tokens=in_tok,
            output_tokens=out_tok,
            reasoning_tokens=reason_tok,
        )
    empty_content = retry == "empty_content"
    parse_failed = retry == "parse_failed"
    gate_retry = retry == "gate_retry"
    event = {
        "event": LLM_USAGE_EVENT_V1,
        "ts": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "feature": feat,
        "operation": op_name,
        "operation_id": op_id,
        "model": (model or "").strip() or "unknown",
        "input_tokens": in_tok,
        "output_tokens": out_tok,
        "content_tokens": content_tok,
        "reasoning_tokens": reason_tok,
        "cached_tokens": cache_tok,
        "reasoning_included_in_output": True,
        "prompt_chars": int(prompt_chars or 0),
        "content_chars": int(content_chars or 0),
        "reasoning_chars": int(reasoning_chars or 0),
        "tokens_source": src,
        "max_tokens": int(max_tokens) if max_tokens else None,
        "latency_ms": int(latency_ms or 0),
        "estimated_cost_usd": cost,
        "user_id": str(uid) if uid not in (None, "") else None,
        "request_id": rid,
        "trigger": trig,
        "attempt": attempt_n,
        "retry_reason": retry,
        "parse_failed": parse_failed,
        "empty_content": empty_content,
        "gate_retry": gate_retry,
        "ok": bool(ok),
        "failure_class": failure_class,
        "streamed": bool(streamed),
        "json_object": bool(json_object),
    }
    try:
        from todayflow_backend.core.llm_cost_guard_v1 import current_guard_meta

        guard = current_guard_meta()
    except Exception:
        guard = {}
    event["cost_guard_action"] = (cost_guard_action or guard.get("cost_guard_action") or "").strip() or None
    event["cost_class"] = (cost_class or guard.get("cost_class") or "").strip() or None
    event["requested_model"] = (requested_model or guard.get("requested_model") or "").strip() or None
    req_max = requested_max_tokens if requested_max_tokens is not None else guard.get("requested_max_tokens")
    event["requested_max_tokens"] = int(req_max) if req_max else None
    spent = daily_spent_usd if daily_spent_usd is not None else guard.get("daily_spent_usd")
    event["daily_spent_usd"] = float(spent) if spent is not None else None
    ceil = daily_ceiling_usd if daily_ceiling_usd is not None else guard.get("daily_ceiling_usd")
    event["daily_ceiling_usd"] = float(ceil) if ceil is not None else None
    _store_event(event)
    return event


def recent_llm_usage_events() -> list[dict[str, Any]]:
    with _recent_lock:
        return list(_recent)


def clear_recent_llm_usage_events() -> None:
    with _recent_lock:
        _recent.clear()


def _store_event(event: dict[str, Any]) -> None:
    with _recent_lock:
        _recent.append(event)
    try:
        logger.info("%s %s", LLM_USAGE_EVENT_V1, json.dumps(event, ensure_ascii=False, default=str))
    except Exception:
        logger.info("%s emit_failed", LLM_USAGE_EVENT_V1)
    path = _log_path()
    if not path:
        return
    line = json.dumps(event, ensure_ascii=False, default=str) + "\n"
    try:
        with _file_lock:
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("a", encoding="utf-8") as fh:
                fh.write(line)
    except OSError:
        logger.warning("llm_usage_v1 jsonl write failed path=%s", path, exc_info=True)


def _log_path() -> Path | None:
    try:
        from todayflow_backend.core.config import settings

        raw = getattr(settings, "llm_usage_log_path", None)
    except Exception:
        return None
    text = str(raw or "").strip()
    if not text:
        return None
    return Path(text)


def _attr(obj: Any, *names: str) -> Any:
    if obj is None:
        return None
    if isinstance(obj, dict):
        for name in names:
            if name in obj and obj[name] is not None:
                return obj[name]
        return None
    for name in names:
        val = getattr(obj, name, None)
        if val is not None:
            return val
    return None


def _int_attr(obj: Any, *names: str) -> int:
    val = _attr(obj, *names)
    try:
        n = int(val or 0)
    except (TypeError, ValueError):
        return 0
    return n if n > 0 else 0

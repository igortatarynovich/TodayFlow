"""LLM cost guard — router policy before any provider call.

Pipeline: request → policy → budget check → provider/model → usage accounting.

This is ops/cost SoT for model class, output ceiling, retry ceiling, and tenant
USD cap. It does not change generation meaning, prompts, or I0 split.

Canon: docs/LLM_QUALITY_AND_PROMPT_EVOLUTION.md (Cost Containment).
"""

from __future__ import annotations

import json
import logging
import threading
from contextvars import ContextVar
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

from todayflow_backend.core.config import settings
from todayflow_backend.core.llm_usage_telemetry_v1 import (
    current_llm_call_context,
    estimate_cost_usd,
    estimate_tokens_from_chars,
)

logger = logging.getLogger(__name__)

CostAction = Literal["allow", "clamp", "k3_denied", "downgrade", "deny"]
CostClass = Literal["today_daily", "natal_ce", "tarot", "on_demand", "other"]

K3_ALLOWED_FEATURES = frozenset(
    {
        "natal.decode",
        "ce.stage2",
        "ce.stage3",
        "ce.stage4",
    }
)

# Recurring daily generation — never K3, small output ceiling.
_TODAY_PREFIXES = (
    "today.",
    "day_story",
    "day_flow",
)

_TAROT_PREFIXES = ("tarot.",)
_ON_DEMAND_PREFIXES = (
    "compatibility.",
    "guidance.",
    "natal.",
    "profile.",
    "numerology.",
)

# Content-token ceilings (provider max_tokens). Retry is a separate, smaller cap —
# not another full budget. Thinking models cannot grow past these caps.
CLASS_CAPS: dict[CostClass, tuple[int, int]] = {
    "today_daily": (1400, 600),
    "natal_ce": (2500, 900),
    "tarot": (1200, 500),
    "on_demand": (1600, 700),
    "other": (1600, 700),
}

DEFAULT_DAILY_USD_CEILING = 5.0
DEFAULT_DOWNGRADE_MODEL = "Qwen/Qwen3-30B-A3B-Instruct-2507"

_guard_meta: ContextVar[dict[str, Any]] = ContextVar("llm_cost_guard_meta", default={})
_ledger_lock = threading.Lock()
_ledger: dict[str, Any] = {"date": "", "spent_usd": 0.0, "reserved_usd": 0.0, "tripped": False}


@dataclass(frozen=True)
class CostGuardDecision:
    action: CostAction
    cost_class: CostClass
    model: str
    max_tokens: int
    requested_model: str
    requested_max_tokens: int
    reservation_usd: float
    daily_spent_usd: float
    daily_ceiling_usd: float
    deny_reason: str | None = None
    rebind_client: bool = False


def is_cost_guard_enabled() -> bool:
    return bool(getattr(settings, "llm_cost_guard_enabled", True))


def current_guard_meta() -> dict[str, Any]:
    return dict(_guard_meta.get() or {})


def is_synthetic_production_email(email: str | None) -> bool:
    """RFC 2606 example.com — never production prewarm / tenant spend."""
    text = (email or "").strip().lower()
    if "@" not in text:
        return False
    host = text.rsplit("@", 1)[-1]
    return host == "example.com" or host.endswith(".example.com")


def classify_feature(feature: str | None) -> CostClass:
    feat = (feature or "").strip().lower()
    if feat in K3_ALLOWED_FEATURES or feat.startswith("ce.stage"):
        if feat in K3_ALLOWED_FEATURES:
            return "natal_ce"
    if feat.startswith(_TODAY_PREFIXES) or feat.startswith("today"):
        return "today_daily"
    if any(feat.startswith(p) for p in _TAROT_PREFIXES):
        return "tarot"
    if any(feat.startswith(p) for p in _ON_DEMAND_PREFIXES):
        # natal.decode already returned natal_ce
        if feat == "natal.decode":
            return "natal_ce"
        return "on_demand"
    return "other"


def _is_k3(model: str) -> bool:
    return "kimi-k3" in (model or "").strip().lower()


def _k3_allowed_for(feature: str | None) -> bool:
    feat = (feature or "").strip().lower()
    return feat in K3_ALLOWED_FEATURES


def primary_model() -> str:
    from todayflow_backend.core.llm_openai_compatible import resolve_default_chat_model

    return resolve_default_chat_model()


def downgrade_model() -> str:
    mid = (getattr(settings, "llm_downgrade_model", None) or "").strip()
    return mid or DEFAULT_DOWNGRADE_MODEL


def daily_usd_ceiling() -> float:
    raw = getattr(settings, "llm_daily_usd_ceiling", None)
    try:
        val = float(raw) if raw is not None else DEFAULT_DAILY_USD_CEILING
    except (TypeError, ValueError):
        val = DEFAULT_DAILY_USD_CEILING
    return max(0.0, val)


def _utc_date() -> str:
    return datetime.now(UTC).date().isoformat()


def _ledger_path() -> Path | None:
    raw = (getattr(settings, "llm_spend_ledger_path", None) or "").strip()
    if raw:
        return Path(raw)
    usage = (getattr(settings, "llm_usage_log_path", None) or "").strip()
    if usage:
        return Path(usage).with_name("llm_spend.json")
    return Path("/tmp/todayflow_llm_spend.json")


def _load_ledger_unlocked() -> None:
    day = _utc_date()
    if _ledger.get("date") == day:
        return
    path = _ledger_path()
    spent = 0.0
    tripped = False
    if path is not None:
        try:
            if path.is_file():
                data = json.loads(path.read_text(encoding="utf-8"))
                if str(data.get("date") or "") == day:
                    spent = float(data.get("spent_usd") or 0.0)
                    tripped = bool(data.get("tripped"))
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            spent = 0.0
    _ledger.update({"date": day, "spent_usd": spent, "reserved_usd": 0.0, "tripped": tripped})


def _persist_ledger_unlocked() -> None:
    path = _ledger_path()
    if path is None:
        return
    payload = {
        "date": _ledger.get("date"),
        "spent_usd": round(float(_ledger.get("spent_usd") or 0.0), 6),
        "reserved_usd": round(float(_ledger.get("reserved_usd") or 0.0), 6),
        "tripped": bool(_ledger.get("tripped")),
    }
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload), encoding="utf-8")
    except OSError:
        logger.warning("llm spend ledger write failed path=%s", path, exc_info=True)


def snapshot_ledger() -> dict[str, Any]:
    with _ledger_lock:
        _load_ledger_unlocked()
        return dict(_ledger)


def reset_ledger_for_tests() -> None:
    with _ledger_lock:
        _ledger.update({"date": _utc_date(), "spent_usd": 0.0, "reserved_usd": 0.0, "tripped": False})


def trip_daily_ceiling(*, reason: str = "billing_suspended") -> None:
    """Hard-stop further expensive calls (402 / operator). Remaining budget = 0."""
    with _ledger_lock:
        _load_ledger_unlocked()
        _ledger["tripped"] = True
        _ledger["spent_usd"] = max(float(_ledger.get("spent_usd") or 0.0), daily_usd_ceiling())
        _persist_ledger_unlocked()
    logger.error("llm cost guard tripped reason=%s spent>=ceiling", reason)


def _committed_usd_unlocked() -> float:
    return float(_ledger.get("spent_usd") or 0.0) + float(_ledger.get("reserved_usd") or 0.0)


def _try_reserve_unlocked(amount: float) -> bool:
    _load_ledger_unlocked()
    ceiling = daily_usd_ceiling()
    if bool(_ledger.get("tripped")):
        return False
    if _committed_usd_unlocked() + amount > ceiling + 1e-9:
        return False
    _ledger["reserved_usd"] = float(_ledger.get("reserved_usd") or 0.0) + amount
    return True


def settle_reservation(reserved: float, actual: float) -> None:
    if reserved <= 0 and actual <= 0:
        return
    with _ledger_lock:
        _load_ledger_unlocked()
        cur_res = float(_ledger.get("reserved_usd") or 0.0)
        _ledger["reserved_usd"] = max(0.0, cur_res - max(0.0, reserved))
        _ledger["spent_usd"] = float(_ledger.get("spent_usd") or 0.0) + max(0.0, actual)
        _persist_ledger_unlocked()


def _non_k3_model(candidate: str) -> str:
    if not _is_k3(candidate):
        return candidate
    primary = primary_model()
    if not _is_k3(primary):
        return primary
    return downgrade_model()


def apply_provider_policy(
    *,
    model: str,
    max_tokens: int,
    prompt_chars: int = 0,
) -> CostGuardDecision:
    """Decide model + max_tokens + whether the tenant may spend.

    Always records guard meta for llm_usage_v1. Caller must settle_reservation.
    """
    ctx = current_llm_call_context()
    feature = str(ctx.get("feature") or "")
    attempt = int(ctx.get("attempt") or 0)
    forced = str(ctx.get("forced_model") or "").strip()
    cost_class = classify_feature(feature)
    requested_model = (model or "").strip() or primary_model()
    requested_max = max(1, int(max_tokens or 1))
    content_cap, retry_cap = CLASS_CAPS[cost_class]
    cap = retry_cap if attempt > 0 else content_cap
    action: CostAction = "allow"
    deny_reason: str | None = None
    chosen = forced or requested_model
    rebind = False

    if _is_k3(chosen) and not _k3_allowed_for(feature):
        chosen = _non_k3_model(chosen)
        action = "k3_denied"
        rebind = chosen != requested_model

    applied_max = min(requested_max, cap)
    if applied_max < requested_max and action == "allow":
        action = "clamp"
    if applied_max < requested_max and action == "k3_denied":
        pass  # keep k3_denied as the stronger signal

    input_est = estimate_tokens_from_chars(prompt_chars)
    worst = estimate_cost_usd(model=chosen, input_tokens=input_est, output_tokens=applied_max)

    spent_snap = 0.0
    ceiling = daily_usd_ceiling()
    reserved = 0.0
    with _ledger_lock:
        _load_ledger_unlocked()
        spent_snap = float(_ledger.get("spent_usd") or 0.0)
        if not _try_reserve_unlocked(worst):
            cheap = downgrade_model()
            cheap_max = min(applied_max, retry_cap if retry_cap else 600, 800)
            cheap_worst = estimate_cost_usd(
                model=cheap, input_tokens=input_est, output_tokens=cheap_max
            )
            if cheap.lower() != chosen.lower() and _try_reserve_unlocked(cheap_worst):
                chosen = cheap
                applied_max = cheap_max
                worst = cheap_worst
                action = "downgrade"
                rebind = True
                reserved = cheap_worst
            else:
                action = "deny"
                deny_reason = "daily_usd_ceiling"
                reserved = 0.0
        else:
            reserved = worst

    meta = {
        "cost_guard_action": action,
        "cost_class": cost_class,
        "requested_model": requested_model,
        "requested_max_tokens": requested_max,
        "daily_spent_usd": round(spent_snap, 6),
        "daily_ceiling_usd": ceiling,
        "reservation_usd": round(reserved, 6),
        "forced_model": chosen if action == "downgrade" else forced or None,
    }
    _guard_meta.set(meta)

    if action == "deny":
        logger.warning(
            "llm cost guard deny class=%s feature=%s spent=%.4f ceiling=%.4f",
            cost_class,
            feature or "unlabeled",
            spent_snap,
            ceiling,
        )
    elif action in {"k3_denied", "downgrade", "clamp"}:
        logger.info(
            "llm cost guard action=%s class=%s feature=%s model=%s→%s max=%s→%s",
            action,
            cost_class,
            feature or "unlabeled",
            requested_model,
            chosen,
            requested_max,
            applied_max,
        )

    return CostGuardDecision(
        action=action,
        cost_class=cost_class,
        model=chosen,
        max_tokens=applied_max,
        requested_model=requested_model,
        requested_max_tokens=requested_max,
        reservation_usd=reserved,
        daily_spent_usd=spent_snap,
        daily_ceiling_usd=ceiling,
        deny_reason=deny_reason,
        rebind_client=rebind or (chosen != requested_model),
    )

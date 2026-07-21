"""Structured logs for compatibility request lifecycle (P0 diagnostics)."""

from __future__ import annotations

import logging
import uuid
from typing import Any

logger = logging.getLogger("todayflow.compatibility")

COMPAT_OBS_CONTRACT = "compatibility_observability_v0"


def new_compat_request_id() -> str:
    return uuid.uuid4().hex[:16]


def log_compat(
    stage: str,
    *,
    request_id: str,
    **fields: Any,
) -> None:
    """Emit one structured log line for a pipeline stage."""
    payload = {
        "contract_version": COMPAT_OBS_CONTRACT,
        "stage": stage,
        "request_id": request_id,
        **{k: v for k, v in fields.items() if v is not None},
    }
    # Keep message short; details in extra for JSON loggers / greppable key=value.
    flat = " ".join(f"{k}={payload[k]!r}" for k in sorted(payload.keys()))
    logger.info("compatibility_%s %s", stage, flat)

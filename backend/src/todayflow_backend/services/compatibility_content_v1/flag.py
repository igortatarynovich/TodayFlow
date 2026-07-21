"""Feature flag — content v1 is off until eval beats legacy baseline."""

from __future__ import annotations

from todayflow_backend.core.config import settings


def content_v1_enabled() -> bool:
    return bool(getattr(settings, "compatibility_content_v1", False))

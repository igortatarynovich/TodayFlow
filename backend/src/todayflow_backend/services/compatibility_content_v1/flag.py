"""Feature flag for Compatibility content v1.1.

Human review approved guest + registered under this flag.
Premium remains excluded from wide enable (separate premium job / path).
Set COMPATIBILITY_CONTENT_V1=1 to turn on.
"""

from __future__ import annotations

from todayflow_backend.core.config import settings


def content_v1_enabled() -> bool:
    return bool(getattr(settings, "compatibility_content_v1", False))

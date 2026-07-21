"""Compatibility Content System v1 (C2) — contracts, prompts, validators.

Not the production default until evaluation passes.
See docs/COMPATIBILITY_CONTENT_CANON_V1.md.

Enable draft guest surface with COMPATIBILITY_CONTENT_V1=1.
"""

from todayflow_backend.services.compatibility_content_v1.contracts import (
    CONTENT_CONTRACT_VERSION,
    GuestContentV1,
    PremiumContentV1,
    RegisteredContentV1,
    SourceDepth,
)
from todayflow_backend.services.compatibility_content_v1.flag import content_v1_enabled
from todayflow_backend.services.compatibility_content_v1.guest_baseline_v1 import build_guest_content_v1
from todayflow_backend.services.compatibility_content_v1.source_depth import resolve_source_depth

__all__ = [
    "CONTENT_CONTRACT_VERSION",
    "GuestContentV1",
    "RegisteredContentV1",
    "PremiumContentV1",
    "SourceDepth",
    "resolve_source_depth",
    "build_guest_content_v1",
    "content_v1_enabled",
]

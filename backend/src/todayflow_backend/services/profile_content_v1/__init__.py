"""Profile Content System v1 (C3) — contracts, depth, architecture rules.

See docs/PROFILE_CONTENT_CANON_V1.md. Not production default until review packs pass.
"""

from todayflow_backend.services.profile_content_v1.contracts import (
    PROFILE_CONTENT_CONTRACT,
    ProfileBaseContentV1,
    ProfileExtendedContentV1,
    ProfilePremiumContentV1,
    ProfileSourceDepth,
)
from todayflow_backend.services.profile_content_v1.source_depth import resolve_profile_source_depth

__all__ = [
    "PROFILE_CONTENT_CONTRACT",
    "ProfileBaseContentV1",
    "ProfileExtendedContentV1",
    "ProfilePremiumContentV1",
    "ProfileSourceDepth",
    "resolve_profile_source_depth",
]

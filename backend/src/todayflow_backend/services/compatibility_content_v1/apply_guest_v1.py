"""Apply finished guest contract when COMPATIBILITY_CONTENT_V1=1."""

from __future__ import annotations

from typing import Any, Optional

from todayflow_backend.services.compatibility_content_v1.flag import content_v1_enabled
from todayflow_backend.services.compatibility_content_v1.guest_baseline_v1 import build_guest_content_v1
from todayflow_backend.services.compatibility_content_v1.source_depth import depth_honesty_line
from todayflow_backend.services.compatibility_content_v1.surface_adapter import guest_to_product_surface
from todayflow_backend.services.sign_compatibility_product import SignCompatibilityProductSurface


def maybe_replace_guest_surface(
    surface: SignCompatibilityProductSurface,
    *,
    tier: str,
    from_sign: str,
    to_sign: str,
    relationship_context: str | None,
    locale: str,
    score: int,
    has_birth_dates: bool = False,
    access_disclosure: dict[str, Any] | None = None,
) -> tuple[SignCompatibilityProductSurface, Optional[dict[str, Any]], dict[str, Any]]:
    """If flag+guest: return finished guest surface + content_v1 meta; else passthrough."""
    meta = access_disclosure or {}
    if not content_v1_enabled() or tier != "guest":
        return surface, None, meta

    content = build_guest_content_v1(
        from_sign=from_sign,
        to_sign=to_sign,
        relationship_context=relationship_context,
        locale=locale,
        has_birth_dates=has_birth_dates,
        score=score,
    )
    shaped = guest_to_product_surface(content)
    out_meta = dict(meta)
    out_meta["content_contract"] = "compatibility_content_v1"
    out_meta["source_depth"] = content.source_depth
    out_meta["locked_preview"] = list(content.locked_preview)
    out_meta["honesty_line"] = depth_honesty_line(content.source_depth, locale=locale)
    # Keep freemium locked_layers / upsell from access_v0 if present.
    if "locked_layers" not in out_meta:
        out_meta["locked_layers"] = [
            "full_overview",
            "conflicts",
            "scenarios",
            "yes_no",
            "do_dont_how",
        ]
    return shaped, content.model_dump(), out_meta

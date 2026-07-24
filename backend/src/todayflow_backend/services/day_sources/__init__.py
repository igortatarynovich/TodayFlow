"""Day Source Registry — normalized Source Families for Day Foundation.

See docs/DAY_SOURCES_CANON.md and docs/DAY_SOURCE_REGISTRY.md.
"""

from todayflow_backend.services.day_sources.registry import (
    DaySourceRegistry,
    default_registry,
    collect_foundation_sources,
    collect_personal_sources,
)
from todayflow_backend.services.day_sources.types import (
    DAY_SOURCES_CONTRACT,
    DaySourceInputs,
    SourceResult,
)

__all__ = [
    "DAY_SOURCES_CONTRACT",
    "DaySourceInputs",
    "DaySourceRegistry",
    "SourceResult",
    "collect_foundation_sources",
    "collect_personal_sources",
    "default_registry",
]

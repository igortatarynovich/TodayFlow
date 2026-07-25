"""Deprecated alias — use day_thesis_v1. Kept for import compatibility during migration."""

from __future__ import annotations

from todayflow_backend.services.day_thesis_v1 import (  # noqa: F401
    DAY_THESIS_V1,
    build_day_thesis_v1,
    conflict_label,
    pick_primary_conflict,
)

DAY_CONFLICT_REGISTRY_V1 = "day_conflict_registry_v1"

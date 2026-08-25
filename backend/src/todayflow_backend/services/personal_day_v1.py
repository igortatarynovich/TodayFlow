"""Personal Day identity — one reusable overlay per user × local_date × semantic_version.

Key MUST NOT include expression/prompt, mood, goals, profile hash, or behavior_version.
Force rebuild regenerates the same key (engineering ledger). Failed/402 is not reusable.

Canon: docs/COMPUTE_LIFECYCLE_AND_ARTIFACT_ECONOMICS_V1.md · TODAY_CONTENT_PIPELINE_V1 I0.
"""

from __future__ import annotations

import hashlib
import json
from datetime import date
from typing import Any

from sqlalchemy.orm import Session

from todayflow_backend.db import models as db_models

PERSONAL_DAY_SEMANTIC_VERSION = "personal-day-semantic.v1"
MODULE = "day_story_v1"
SURFACE = "day_story"
READY_GENERATION_SOURCES = frozenset({"native_llm_c1"})
FAIL_GENERATION_SOURCES = frozenset(
    {
        "kept_prior_native",
        "unavailable_after_llm",
        "facts_only_no_llm",
        "deterministic_no_llm",
        "facts_only_unavailable",
    }
)


def normalize_local_date(local_date: date | str) -> str:
    if isinstance(local_date, date):
        return local_date.isoformat()
    return str(local_date or "").strip()[:10]


def personal_day_ledger(*, force_rebuild: bool, had_ready_artifact: bool) -> str:
    """Engineering only when force-rebuilding an already ready Personal artifact."""
    if force_rebuild and had_ready_artifact:
        return "engineering"
    return "product"


def personal_day_key(
    *,
    user_id: int | None,
    local_date: date | str,
    semantic_version: str = PERSONAL_DAY_SEMANTIC_VERSION,
    owner_key: str | None = None,
) -> str:
    """Identity of Personal Day. No expression, mood, behavior, or profile hash."""
    if user_id is not None:
        ident: dict[str, Any] = {"user_id": int(user_id)}
    else:
        ident = {"owner_key": str(owner_key or "").strip()}
    payload = {
        **ident,
        "local_date": normalize_local_date(local_date),
        "semantic_version": str(semantic_version or PERSONAL_DAY_SEMANTIC_VERSION).strip(),
    }
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:32]


def is_reusable_personal_payload(
    *,
    status: str | None,
    used_fallback: bool,
    input_payload: dict[str, Any] | None,
    story: dict[str, Any] | None,
) -> bool:
    """Accepted Personal only. 402 / fallback / kept-prior are not cache hits."""
    if str(status or "") != "success" or bool(used_fallback):
        return False
    ip = input_payload if isinstance(input_payload, dict) else {}
    src = str(ip.get("generation_source") or "")
    if src in FAIL_GENERATION_SOURCES:
        return False
    body = story if isinstance(story, dict) else {}
    scen = body.get("day_scenario") if isinstance(body.get("day_scenario"), dict) else {}
    if src in READY_GENERATION_SOURCES:
        return bool(scen.get("ready") and scen.get("scenes"))
    # Legacy natives before personal_day_key: native prompt + ready scenes.
    pv = str(ip.get("prompt_version") or "")
    if pv.startswith("day-scenario-native-") and scen.get("ready") and scen.get("scenes"):
        return True
    return False


def is_reusable_personal_row(row: db_models.GenerationLog) -> bool:
    nr = row.normalized_response if isinstance(row.normalized_response, dict) else None
    ip = row.input_payload if isinstance(row.input_payload, dict) else None
    return is_reusable_personal_payload(
        status=getattr(row, "status", None),
        used_fallback=bool(getattr(row, "used_fallback", False)),
        input_payload=ip,
        story=nr,
    )


def row_matches_personal_key(
    row: db_models.GenerationLog,
    *,
    key: str,
    target_date: date | str,
) -> bool:
    ip = row.input_payload if isinstance(row.input_payload, dict) else {}
    if str(ip.get("target_date") or "") != normalize_local_date(target_date):
        return False
    stored = str(ip.get("personal_day_key") or "")
    if stored:
        return stored == key
    # Legacy identity fallback: same user+date reusable native, ignore fat fingerprint.
    return True

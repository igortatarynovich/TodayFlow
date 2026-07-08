"""P1.14 — Surface candidate audit record (selection snapshot for exposure/reaction chain)."""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from typing import Any

from todayflow_backend.services.day_model_v1_surface_candidate import (
    DAY_SURFACE_CANDIDATE_V1_CONTRACT,
    SELECTED_SOURCE_BLOCKED,
    SELECTED_SOURCE_DETERMINISTIC,
    SELECTED_SOURCE_LLM_REFINED,
)

DAY_SURFACE_CANDIDATE_AUDIT_V1_CONTRACT = "day_surface_candidate_audit_v1"

AUDIT_STATUS_RECORDED = "recorded"

DAY_SURFACE_CANDIDATE_AUDIT_V1_KEYS = frozenset(
    {
        "contract_version",
        "audit_id",
        "candidate_id",
        "surface",
        "selected_source",
        "display_text",
        "display_text_hash",
        "selection_reason",
        "quality_score",
        "confidence",
        "degraded",
        "used_llm",
        "dataset_candidate",
        "generation_id",
        "source_keys",
        "render_trace",
        "llm_trace",
        "status",
        "created_at",
    }
)


class DaySurfaceCandidateAuditError(ValueError):
    """Raised when audit record inputs or payload are invalid."""


def hash_display_text(text: str | None) -> str | None:
    if text is None:
        return None
    normalized = text.strip()
    if not normalized:
        return None
    digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:32]
    return f"txt-{digest}"


def derive_candidate_id(
    surface: str,
    selected_source: str,
    display_text_hash: str | None,
) -> str:
    payload = f"{surface}:{selected_source}:{display_text_hash or 'none'}"
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]
    return f"cand-{digest}"


def derive_audit_id(candidate_id: str, created_at: str) -> str:
    payload = f"{candidate_id}:{created_at}"
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]
    return f"audit-{digest}"


def _utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_day_surface_candidate_audit_v1(
    candidate: dict[str, Any],
    *,
    audit_id: str | None = None,
    candidate_id: str | None = None,
    created_at: str | None = None,
) -> dict[str, Any]:
    """
    P1.14 — persist audit snapshot of selected (or blocked) surface candidate.

    No UI, exposure, learning signals, or memory writes.
    """
    if candidate.get("contract_version") != DAY_SURFACE_CANDIDATE_V1_CONTRACT:
        raise DaySurfaceCandidateAuditError("candidate has invalid contract_version")

    selected_source = candidate.get("selected_source")
    if selected_source not in {
        SELECTED_SOURCE_DETERMINISTIC,
        SELECTED_SOURCE_LLM_REFINED,
        SELECTED_SOURCE_BLOCKED,
    }:
        raise DaySurfaceCandidateAuditError(f"invalid selected_source: {selected_source!r}")

    display_text = candidate.get("display_text")
    if selected_source != SELECTED_SOURCE_BLOCKED and not display_text:
        raise DaySurfaceCandidateAuditError("non-blocked candidate requires display_text")

    text_hash = hash_display_text(display_text if isinstance(display_text, str) else None)
    timestamp = created_at or _utc_now_iso()
    cid = candidate_id or derive_candidate_id(
        candidate["surface"],
        selected_source,
        text_hash,
    )
    aid = audit_id or derive_audit_id(cid, timestamp)

    audit = {
        "contract_version": DAY_SURFACE_CANDIDATE_AUDIT_V1_CONTRACT,
        "audit_id": aid,
        "candidate_id": cid,
        "surface": candidate["surface"],
        "selected_source": selected_source,
        "display_text": display_text,
        "display_text_hash": text_hash,
        "selection_reason": candidate.get("selection_reason"),
        "quality_score": candidate.get("quality_score"),
        "confidence": candidate.get("confidence"),
        "degraded": bool(candidate.get("degraded", False)),
        "used_llm": bool(candidate.get("used_llm", False)),
        "dataset_candidate": bool(candidate.get("dataset_candidate", False)),
        "generation_id": candidate.get("generation_id"),
        "source_keys": list(candidate.get("source_keys") or []),
        "render_trace": dict(candidate.get("render_trace") or {}),
        "llm_trace": dict(candidate.get("llm_trace") or {}),
        "status": AUDIT_STATUS_RECORDED,
        "created_at": timestamp,
    }

    errors = validate_day_surface_candidate_audit_v1(audit)
    if errors:
        raise DaySurfaceCandidateAuditError("; ".join(errors))
    return audit


def validate_day_surface_candidate_audit_v1(audit: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if audit.get("contract_version") != DAY_SURFACE_CANDIDATE_AUDIT_V1_CONTRACT:
        errors.append("invalid contract_version")
    for key in DAY_SURFACE_CANDIDATE_AUDIT_V1_KEYS:
        if key not in audit:
            errors.append(f"missing field: {key}")

    if not audit.get("audit_id"):
        errors.append("audit_id required")
    if not audit.get("candidate_id"):
        errors.append("candidate_id required")

    selected = audit.get("selected_source")
    text = audit.get("display_text")
    text_hash = audit.get("display_text_hash")

    if selected == SELECTED_SOURCE_BLOCKED:
        if text is not None:
            errors.append("blocked audit must have display_text=null")
        if text_hash is not None:
            errors.append("blocked audit must have display_text_hash=null")
    else:
        if not text:
            errors.append("non-blocked audit requires display_text")
        if hash_display_text(str(text)) != text_hash:
            errors.append("display_text_hash mismatch")

    if audit.get("status") != AUDIT_STATUS_RECORDED:
        errors.append("status must be recorded")

    return errors

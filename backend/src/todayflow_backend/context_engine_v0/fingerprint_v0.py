"""Stable fingerprint for ContextPack inputs."""

from __future__ import annotations

import hashlib
import json
from typing import Any


def context_pack_fingerprint(payload: dict[str, Any]) -> str:
    """Hash canonical subset — exclude volatile kitchen timestamps."""
    body = {
        "question_id": payload.get("question_id"),
        "domain": payload.get("domain"),
        "locale": payload.get("locale"),
        "identity_core": payload.get("identity_core"),
        "strengths": payload.get("strengths") or [],
        "growth_zones": payload.get("growth_zones") or [],
        "relevant_style": payload.get("relevant_style"),
        "cue_texts": [c.get("text") for c in (payload.get("cues") or []) if isinstance(c, dict)],
        "house_cue_texts": [
            c.get("text") for c in (payload.get("house_cues") or []) if isinstance(c, dict)
        ],
        "fact_ids": sorted(payload.get("fact_ids") or []),
        "context_version": payload.get("context_version"),
    }
    raw = json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:32]

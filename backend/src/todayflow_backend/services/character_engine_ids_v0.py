"""Deterministic Character Engine identity helpers (no LLM prose in fingerprints).

Canon: docs/audits/CHARACTER_ENGINE_SCHEMA_CONTRACTS_V0.md §1
"""

from __future__ import annotations

import hashlib
import json
from typing import Iterable, Mapping, Sequence


def _canon(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _digest(parts: Sequence[str], *, prefix: str, length: int = 24) -> str:
    h = hashlib.sha256()
    for part in parts:
        h.update(part.encode("utf-8"))
        h.update(b"\0")
    return f"{prefix}:{h.hexdigest()[:length]}"


def fingerprint_ids(ids: Iterable[str]) -> str:
    """Order-independent fingerprint of id lists."""
    return _canon(sorted({str(x) for x in ids}))


def make_fact_id(
    *,
    fact_type: str,
    normalized_key: str,
    authority: str,
    calc_version: str,
) -> str:
    """Stable raw-fact id. Must not include surface/LLM text."""
    return _digest(
        [
            "fact_v1",
            fact_type.strip(),
            normalized_key.strip(),
            authority.strip(),
            calc_version.strip(),
        ],
        prefix="fact",
    )


def make_claim_id(
    *,
    claim_kind: str,
    thesis_key: str,
    primary_fact_ids: Iterable[str],
) -> str:
    """Stable claim id from kind + thesis_key + supporting facts — not surface_text."""
    return _digest(
        [
            "claim_v1",
            claim_kind.strip(),
            thesis_key.strip(),
            fingerprint_ids(primary_fact_ids),
        ],
        prefix="claim",
    )


def make_edge_id(*, fact_id: str, claim_id: str, edge_type: str) -> str:
    return _digest(
        ["edge_v1", fact_id.strip(), claim_id.strip(), edge_type.strip()],
        prefix="edge",
    )


def make_scene_id(*, scene_kind: str, tension_or_mechanism_ref: str) -> str:
    return _digest(
        ["scene_v1", scene_kind.strip(), tension_or_mechanism_ref.strip()],
        prefix="scene",
    )


def make_compass_item_id(
    *,
    item_kind: str,
    source_refs: Mapping[str, Iterable[str]] | None = None,
) -> str:
    refs = source_refs or {}
    payload = {
        key: sorted({str(v) for v in (refs.get(key) or [])})
        for key in ("claim_ids", "scene_ids", "mechanism_slots")
    }
    return _digest(
        ["compass_item_v1", item_kind.strip(), _canon(payload)],
        prefix="compass",
    )

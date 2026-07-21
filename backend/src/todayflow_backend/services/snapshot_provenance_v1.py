"""Snapshot provenance for generation logs — Personal Model read-path diagnostics."""

from __future__ import annotations

from typing import Any


def build_snapshot_provenance(
    core_profile: dict[str, Any] | None,
    *,
    source_depth: str | None = None,
    snapshot_id: int | None = None,
) -> dict[str, Any]:
    """Fields every module generation should leave in ``input_payload`` / logs."""
    payload = core_profile if isinstance(core_profile, dict) else {}
    sid = snapshot_id
    if sid is None:
        raw = payload.get("snapshot_id")
        if isinstance(raw, int):
            sid = raw
        elif raw is not None:
            try:
                sid = int(raw)
            except (TypeError, ValueError):
                sid = None

    profile_hash = str(payload.get("profile_hash") or "").strip() or None
    profile_version = str(payload.get("profile_version") or "").strip() or None
    has_contract = isinstance(payload.get("profile_contract_v1"), dict)
    generated_from_snapshot = bool(sid) or (bool(profile_hash) and has_contract)

    out: dict[str, Any] = {
        "generated_from_snapshot": generated_from_snapshot,
    }
    if sid is not None:
        out["core_profile_snapshot_id"] = sid
    if profile_hash:
        out["profile_hash"] = profile_hash
    if profile_version:
        out["profile_version"] = profile_version
    if source_depth:
        out["source_depth"] = source_depth
    return out


def merge_snapshot_provenance(
    input_payload: dict[str, Any] | None,
    core_profile: dict[str, Any] | None,
    *,
    source_depth: str | None = None,
    snapshot_id: int | None = None,
) -> dict[str, Any]:
    base = dict(input_payload or {})
    prov = build_snapshot_provenance(
        core_profile,
        source_depth=source_depth or (str(base.get("source_depth") or "").strip() or None),
        snapshot_id=snapshot_id,
    )
    # Provenance wins for identity keys; keep module-specific fields.
    for key, value in prov.items():
        if key not in base or base.get(key) in (None, "", False):
            base[key] = value
        elif key in ("core_profile_snapshot_id", "profile_hash", "profile_version", "generated_from_snapshot"):
            base[key] = value
    return base

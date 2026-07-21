"""Experience Contract assembler v0 — single Snapshot → Contract path for Experiences.

Blind to Experiences: knows only Personal Snapshot / shell, Experience Contract fields,
and contract versions. Experience-specific field selection lives in declarative allowlists.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, Final, Mapping

EXPERIENCE_CONTRACT_VERSION: Final = "experience_contract_v0"

# Fields assembled once from Snapshot/shell. Order is fingerprint-stable.
EXPERIENCE_CONTRACT_FIELDS: Final[tuple[str, ...]] = (
    "decision_style",
    "conflict_style",
    "communication_style",
    "motivation",
    "energy_source",
    "helps",
    "strengths",
    "identity_line",
    "life_path",
    "sun_sign",
    "rhythm",
    "display_name",
    "living_summary",
    # provenance
    "snapshot_id",
    "profile_hash",
    "profile_version",
    "source_depth",
    "generated_from_snapshot",
    "is_ready",
    "missing_fields",
)

# Consistency-critical personality fields (public CI contract).
CONSISTENCY_FIELDS: Final[tuple[str, ...]] = (
    "decision_style",
    "conflict_style",
    "communication_style",
    "motivation",
    "energy_source",
)

PROVENANCE_FIELDS: Final[tuple[str, ...]] = (
    "snapshot_id",
    "profile_hash",
    "profile_version",
    "source_depth",
    "generated_from_snapshot",
)

# Declarative allowlists: new Snapshot fields never leak until listed here.
EXPERIENCE_ALLOWLISTS: Final[dict[str, frozenset[str]]] = {
    "today": frozenset(
        {
            "decision_style",
            "conflict_style",
            "communication_style",
            "motivation",
            "energy_source",
            "helps",
            "strengths",
            "identity_line",
            "life_path",
            "sun_sign",
            "rhythm",
            "display_name",
            "living_summary",
            *PROVENANCE_FIELDS,
            "is_ready",
            "missing_fields",
        }
    ),
    "compatibility": frozenset(
        {
            "decision_style",
            "conflict_style",
            "communication_style",
            "motivation",
            "energy_source",
            "helps",
            "strengths",
            "identity_line",
            "life_path",
            "sun_sign",
            "rhythm",
            *PROVENANCE_FIELDS,
            "is_ready",
            "missing_fields",
        }
    ),
    "tarot": frozenset(
        {
            "decision_style",
            "conflict_style",
            "communication_style",
            "motivation",
            "energy_source",
            "helps",
            "identity_line",
            "sun_sign",
            *PROVENANCE_FIELDS,
            "is_ready",
            "missing_fields",
        }
    ),
}

KNOWN_EXPERIENCE_IDS: Final[frozenset[str]] = frozenset(EXPERIENCE_ALLOWLISTS)


def _clip(value: Any, max_len: int) -> str | None:
    text = str(value or "").strip()
    if not text:
        return None
    if len(text) <= max_len:
        return text
    return text[: max_len - 1].rstrip() + "…"


def _clip_list(raw: Any, *, max_items: int, item_len: int) -> list[str]:
    if not isinstance(raw, list):
        return []
    out: list[str] = []
    for item in raw:
        clipped = _clip(item, item_len)
        if clipped and clipped not in out:
            out.append(clipped)
        if len(out) >= max_items:
            break
    return out


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _snapshot_id(payload: Mapping[str, Any]) -> int | None:
    raw = payload.get("snapshot_id")
    if isinstance(raw, int):
        return raw
    if raw is None:
        return None
    try:
        return int(raw)
    except (TypeError, ValueError):
        return None


def _profile_contract(snapshot: Mapping[str, Any]) -> dict[str, Any]:
    pc = snapshot.get("profile_contract_v1")
    return pc if isinstance(pc, dict) else {}


def _baseline(snapshot: Mapping[str, Any]) -> dict[str, Any]:
    return _as_dict(snapshot.get("baseline"))


def _living(snapshot: Mapping[str, Any]) -> dict[str, Any]:
    return _as_dict(snapshot.get("living"))


def _energy_source_from_snapshot(snapshot: Mapping[str, Any], contract: Mapping[str, Any]) -> str | None:
    baseline = _baseline(snapshot)
    for key in ("element_focus", "rhythm", "energy_pattern"):
        hit = _clip(baseline.get(key), 280)
        if hit:
            return hit
    living = _living(snapshot)
    signal = _as_dict(living.get("signal_profile"))
    for key in ("energy_source", "dominant_energy", "energy_pattern"):
        hit = _clip(signal.get(key), 280)
        if hit:
            return hit
    helps = contract.get("helps") if isinstance(contract.get("helps"), list) else []
    if helps:
        return _clip(helps[0], 280)
    return None


def _communication_style_from_snapshot(
    snapshot: Mapping[str, Any], contract: Mapping[str, Any]
) -> str | None:
    # Prefer explicit future field; until then relationship_style is the stable SoI proxy.
    for src in (contract, _baseline(snapshot), _as_dict(snapshot.get("interpretation"))):
        hit = _clip(src.get("communication_style"), 520)
        if hit:
            return hit
    return _clip(contract.get("relationship_style"), 520)


def _conflict_style_from_snapshot(
    snapshot: Mapping[str, Any], contract: Mapping[str, Any]
) -> str | None:
    for src in (contract, _baseline(snapshot), _as_dict(snapshot.get("interpretation"))):
        hit = _clip(src.get("conflict_style"), 520)
        if hit:
            return hit
    # Closest stable personal-model field today.
    return _clip(contract.get("relationship_style"), 520)


def _identity_line_from_snapshot(
    snapshot: Mapping[str, Any], contract: Mapping[str, Any]
) -> str | None:
    hit = _clip(contract.get("identity_core"), 420)
    if hit:
        return hit
    interp = _as_dict(snapshot.get("interpretation"))
    return _clip(interp.get("identity"), 420)


def _rhythm_from_snapshot(snapshot: Mapping[str, Any]) -> str | None:
    baseline = _baseline(snapshot)
    hit = _clip(baseline.get("rhythm"), 280)
    if hit:
        return hit
    living = _living(snapshot)
    signal = _as_dict(living.get("signal_profile"))
    return _clip(signal.get("rhythm") or signal.get("tempo"), 280)


def _source_depth(snapshot: Mapping[str, Any]) -> str | None:
    raw = snapshot.get("source_depth")
    if isinstance(raw, str) and raw.strip():
        return raw.strip()[:64]
    if _snapshot_id(snapshot) is not None and isinstance(snapshot.get("profile_contract_v1"), dict):
        return "snapshot"
    if snapshot.get("is_ready"):
        return "shell_ready"
    return "shell"


def fingerprint_experience_contract(contract: Mapping[str, Any]) -> str:
    """Fingerprint of Experience Contract fields only (not the full Snapshot)."""
    payload = {
        key: contract.get(key)
        for key in EXPERIENCE_CONTRACT_FIELDS
        if key in contract
    }
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]


def fingerprint_experience_slice(slice_payload: Mapping[str, Any]) -> str:
    """Fingerprint of projected ExperienceSlice (allowlisted fields + experience_id)."""
    keys = sorted(k for k in slice_payload.keys() if k != "experience_slice_fingerprint")
    payload = {k: slice_payload.get(k) for k in keys}
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]


def assemble_experience_contract(
    snapshot: Mapping[str, Any] | None,
) -> dict[str, Any]:
    """Build Experience Contract from Personal Snapshot / shell. Experience-blind."""
    src = dict(snapshot) if isinstance(snapshot, Mapping) else {}
    pc = _profile_contract(src)
    person = _as_dict(src.get("person"))
    astro = _as_dict(src.get("astro"))
    numerology = _as_dict(src.get("numerology"))
    living = _living(src)

    snapshot_id = _snapshot_id(src)
    profile_hash = _clip(src.get("profile_hash"), 128)
    profile_version = src.get("profile_version")
    if profile_version is not None:
        profile_version = str(profile_version).strip() or None
    generated_from_snapshot = bool(snapshot_id) or (
        bool(profile_hash) and bool(pc)
    )

    missing = src.get("missing_fields")
    missing_fields = (
        [str(x) for x in missing[:12] if str(x).strip()]
        if isinstance(missing, list)
        else []
    )

    life_path = numerology.get("life_path")
    if life_path is None:
        life_path = _baseline(src).get("life_path")

    contract: dict[str, Any] = {
        "contract_version": EXPERIENCE_CONTRACT_VERSION,
        "decision_style": _clip(pc.get("decision_style"), 520),
        "conflict_style": _conflict_style_from_snapshot(src, pc),
        "communication_style": _communication_style_from_snapshot(src, pc),
        "motivation": _clip(pc.get("life_mission") or pc.get("motivation"), 420),
        "energy_source": _energy_source_from_snapshot(src, pc),
        "helps": _clip_list(pc.get("helps"), max_items=5, item_len=220),
        "strengths": _clip_list(pc.get("strengths"), max_items=6, item_len=200),
        "identity_line": _identity_line_from_snapshot(src, pc),
        "life_path": life_path,
        "sun_sign": _clip(astro.get("sun_sign"), 48),
        "rhythm": _rhythm_from_snapshot(src),
        "display_name": _clip(
            person.get("display_name") or person.get("first_name"), 64
        ),
        "living_summary": _clip(living.get("summary"), 720),
        "snapshot_id": snapshot_id,
        "profile_hash": profile_hash,
        "profile_version": profile_version,
        "source_depth": _source_depth(src),
        "generated_from_snapshot": generated_from_snapshot,
        "is_ready": bool(src.get("is_ready")),
        "missing_fields": missing_fields,
    }
    contract["contract_fingerprint"] = fingerprint_experience_contract(contract)
    return contract


def project_experience_slice(
    contract: Mapping[str, Any] | None,
    *,
    experience_id: str,
) -> dict[str, Any]:
    """Project Experience Contract → ExperienceSlice via declarative allowlist."""
    exp = (experience_id or "").strip().lower()
    if exp not in EXPERIENCE_ALLOWLISTS:
        raise ValueError(
            f"unknown experience_id={experience_id!r}; "
            f"known={sorted(EXPERIENCE_ALLOWLISTS)}"
        )
    src = dict(contract) if isinstance(contract, Mapping) else {}
    allow = EXPERIENCE_ALLOWLISTS[exp]
    out: dict[str, Any] = {
        "experience_id": exp,
        "contract_version": EXPERIENCE_CONTRACT_VERSION,
        "source_contract_fingerprint": src.get("contract_fingerprint"),
    }
    for key in EXPERIENCE_CONTRACT_FIELDS:
        if key in allow and key in src:
            out[key] = src[key]
    out["experience_slice_fingerprint"] = fingerprint_experience_slice(out)
    return out


def assemble_experience_slice(
    snapshot: Mapping[str, Any] | None,
    *,
    experience_id: str,
) -> dict[str, Any]:
    """Convenience: Snapshot → Contract → Slice (still one assembler underneath)."""
    contract = assemble_experience_contract(snapshot)
    return project_experience_slice(contract, experience_id=experience_id)


def slice_log_fields(slice_payload: Mapping[str, Any] | None) -> dict[str, Any]:
    """Keys for GenerationLog / telemetry from an ExperienceSlice."""
    src = dict(slice_payload) if isinstance(slice_payload, Mapping) else {}
    out: dict[str, Any] = {}
    for key in (
        "experience_id",
        "experience_slice_fingerprint",
        "source_contract_fingerprint",
        "snapshot_id",
        "profile_hash",
        "profile_version",
        "source_depth",
        "generated_from_snapshot",
    ):
        if src.get(key) is not None:
            out[key] = src[key]
    # Align with existing provenance key naming in logs.
    if "snapshot_id" in out and "core_profile_snapshot_id" not in out:
        out["core_profile_snapshot_id"] = out["snapshot_id"]
    return out

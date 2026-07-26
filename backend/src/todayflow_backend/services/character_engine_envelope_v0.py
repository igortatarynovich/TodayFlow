"""Compose ``payload.character_engine_v1`` from Stage 0–5 diagnostics nests.

Canon home: CHARACTER_ENGINE_SCHEMA_CONTRACTS_V0 · Architecture Impact D1.
Assemble-once: attach only when nest missing (or fingerprint mismatch on publish).

``status=ready`` only when CHARACTER_ENGINE_PUBLISH_READY is on and Stage 5 grounded.
Otherwise ``forming`` — full cascade may still be present for shadow validation.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from todayflow_backend.core.config import settings
from todayflow_backend.services.character_engine_stage2_shadow_v0 import (
    character_engine_publish_ready_enabled,
)
from todayflow_backend.services.character_engine_stage5_assembly_v0 import ADAPTER_VERSION

logger = logging.getLogger(__name__)

ENVELOPE_VERSION = "character_engine_envelope_v0"
SCHEMA_VERSION = "character_engine_v1"
RECIPE_VERSION = "character_engine_recipe_v1"

_MECH_SLOTS = (
    "decision",
    "perception",
    "stress",
    "risk",
    "recovery",
    "growth",
    "burnout",
)


_CLAIM_KEYS = (
    "claim_id",
    "claim_kind",
    "thesis_key",
    "surface_text",
    "cascade_role",
    "supporting_fact_ids",
    "contradicting_fact_ids",
    "confidence",
    "capability_floor",
    "produced_by_stage",
    "evidence_status",
    "exclusion_reason",
)
_FACT_KEYS = (
    "fact_id",
    "fact_type",
    "value",
    "display_key",
    "authority",
    "calc_version",
    "capability_required",
    "confidence",
    "provenance",
    "unavailable_reason",
)
_EDGE_KEYS = ("edge_id", "fact_id", "claim_id", "edge_type", "note_key")


def _pick(d: dict[str, Any], keys: tuple[str, ...]) -> dict[str, Any]:
    return {k: d[k] for k in keys if k in d}


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _claim_ids(raw: Any) -> list[str]:
    out: list[str] = []
    if isinstance(raw, list):
        for x in raw:
            s = str(x or "").strip()
            if s.startswith("claim:") and s not in out:
                out.append(s)
    return out


def _diag_nests(diagnostics: dict[str, Any]) -> dict[str, Any]:
    s2 = diagnostics.get("character_engine_stage2")
    s3 = diagnostics.get("character_engine_stage3")
    s4 = diagnostics.get("character_engine_stage4")
    s5 = diagnostics.get("character_engine_stage5")
    return {
        "stage0": (s2 or {}).get("stage0") if isinstance(s2, dict) else None,
        "stage1": (s2 or {}).get("stage1") if isinstance(s2, dict) else None,
        "stage2": (s2 or {}).get("stage2") if isinstance(s2, dict) else None,
        "stage3": (s3 or {}).get("stage3") if isinstance(s3, dict) else None,
        "stage4": (s4 or {}).get("stage4") if isinstance(s4, dict) else None,
        "stage5": (s5 or {}).get("stage5") if isinstance(s5, dict) else None,
    }


def _build_cascade(
    *,
    identity: dict[str, Any],
    stage1: dict[str, Any],
    stage3: dict[str, Any],
    stage4: dict[str, Any],
) -> dict[str, Any] | None:
    core = identity.get("identity_core") if isinstance(identity.get("identity_core"), dict) else None
    if not isinstance(core, dict):
        return None
    primary = str(core.get("claim_id") or core.get("primary_claim_id") or "").strip()
    support = _claim_ids(core.get("supporting_claim_ids"))
    if primary and primary not in support:
        support = [primary, *support]
    if not support:
        return None

    identity_block = {
        "claim_ids": support[:],
        "surface_text": str(core.get("surface_text") or "").strip() or None,
    }
    if identity_block["surface_text"] is None:
        identity_block.pop("surface_text")

    source_roles: list[dict[str, Any]] = []
    for c in stage1.get("claims") or []:
        if not isinstance(c, dict) or c.get("evidence_status") != "grounded":
            continue
        cid = str(c.get("claim_id") or "").strip()
        fids = [str(f).strip() for f in (c.get("supporting_fact_ids") or []) if str(f).strip()]
        role = str(c.get("thesis_key") or c.get("cascade_role") or "").strip()
        if not cid or not fids or not role:
            continue
        row: dict[str, Any] = {
            "role_key": role[:64],
            "fact_ids": fids,
            "claim_ids": [cid],
        }
        surf = str(c.get("surface_text") or "").strip()
        if surf:
            row["surface_text"] = surf
        source_roles.append(row)

    engine = stage3.get("internal_engine") if isinstance(stage3.get("internal_engine"), dict) else {}
    internal: list[dict[str, Any]] = []
    for slot in _MECH_SLOTS:
        row = engine.get(slot) if isinstance(engine.get(slot), dict) else None
        if not row:
            continue
        cids = _claim_ids(row.get("supporting_claim_ids")) or support[:1]
        if not cids:
            continue
        item: dict[str, Any] = {"slot": slot, "claim_ids": cids}
        surf = str(row.get("surface_text") or "").strip()
        if surf:
            item["surface_text"] = surf
        internal.append(item)
    if not internal:
        return None

    pt = stage3.get("primary_tension") if isinstance(stage3.get("primary_tension"), dict) else {}
    pt_key = str(pt.get("tension_key") or pt.get("thesis_key") or "").strip()
    pt_cids = _claim_ids(pt.get("supporting_claim_ids") or pt.get("claim_ids")) or support[:1]
    if not pt_key or not pt_cids:
        return None
    primary_tension: dict[str, Any] = {
        "tension_key": pt_key[:64],
        "claim_ids": pt_cids,
    }
    surf = str(pt.get("surface_text") or "").strip()
    if surf:
        primary_tension["surface_text"] = surf

    secondary: list[dict[str, Any]] = []
    for t in stage3.get("secondary_tensions") or []:
        if not isinstance(t, dict):
            continue
        key = str(t.get("tension_key") or t.get("thesis_key") or "").strip()
        cids = _claim_ids(t.get("supporting_claim_ids") or t.get("claim_ids"))
        if not key or not cids:
            continue
        item = {"tension_key": key[:64], "claim_ids": cids}
        ts = str(t.get("surface_text") or "").strip()
        if ts:
            item["surface_text"] = ts
        secondary.append(item)
        if len(secondary) >= 3:
            break

    scenes_out: list[dict[str, Any]] = []
    for sc in stage4.get("scenes") or []:
        if not isinstance(sc, dict):
            continue
        sid = str(sc.get("scene_id") or "").strip()
        kind = str(sc.get("scene_kind") or "").strip()
        cids = _claim_ids(sc.get("supporting_claim_ids") or sc.get("claim_ids")) or support[:1]
        if not sid.startswith("scene:") or not kind or not cids:
            continue
        item = {"scene_id": sid, "scene_kind": kind, "claim_ids": cids}
        ss = str(sc.get("surface_text") or "").strip()
        if ss:
            item["surface_text"] = ss
        scenes_out.append(item)
    if not scenes_out:
        return None

    pot = stage4.get("potential") if isinstance(stage4.get("potential"), dict) else {}
    pot_cids = _claim_ids(pot.get("supporting_claim_ids") or pot.get("claim_ids")) or support[:1]
    potential: dict[str, Any] = {"claim_ids": pot_cids}
    ps = str(pot.get("surface_text") or "").strip()
    if ps:
        potential["surface_text"] = ps

    blinds: list[dict[str, Any]] = []
    for b in stage4.get("blind_spots") or []:
        if not isinstance(b, dict):
            continue
        cids = _claim_ids(b.get("supporting_claim_ids") or b.get("claim_ids")) or support[:1]
        item = {"claim_ids": cids}
        bs = str(b.get("surface_text") or "").strip()
        if bs:
            item["surface_text"] = bs
        blinds.append(item)

    return {
        "identity_core": identity_block,
        "source_roles": source_roles,
        "internal_engine": internal,
        "primary_tension": primary_tension,
        "secondary_tensions": secondary,
        "scenes": scenes_out,
        "potential": potential,
        "blind_spots": blinds,
    }


def build_character_engine_envelope_v0(
    *,
    diagnostics: dict[str, Any],
    profile_fingerprint: str,
) -> dict[str, Any]:
    """Build schema-shaped envelope from diagnostics Stage nests. Pure / no LLM."""
    nests = _diag_nests(diagnostics if isinstance(diagnostics, dict) else {})
    stage0 = nests["stage0"] if isinstance(nests["stage0"], dict) else {}
    stage1 = nests["stage1"] if isinstance(nests["stage1"], dict) else {}
    stage2 = nests["stage2"] if isinstance(nests["stage2"], dict) else {}
    stage3 = nests["stage3"] if isinstance(nests["stage3"], dict) else {}
    stage4 = nests["stage4"] if isinstance(nests["stage4"], dict) else {}
    stage5 = nests["stage5"] if isinstance(nests["stage5"], dict) else {}

    pf = str(
        profile_fingerprint
        or stage0.get("profile_fingerprint")
        or ""
    ).strip() or "unknown_profile"
    fact_set = str(stage0.get("input_fact_set_version") or "facts_pack_unknown").strip()

    meta: dict[str, Any] = {
        "adapter_version": ADAPTER_VERSION,
        "stage_prompt_ids": {
            "stage0": str(stage0.get("stage_version") or ""),
            "stage1": str(stage1.get("stage_version") or ""),
            "stage2": str((stage2.get("artifact_version") or stage2.get("stage_version") or "")),
            "stage3": str(stage3.get("artifact_version") or ""),
            "stage4": str(stage4.get("artifact_version") or ""),
            "stage5": str(stage5.get("artifact_version") or ""),
            "envelope": ENVELOPE_VERSION,
        },
    }
    # Drop empty prompt id strings — keep object small.
    meta["stage_prompt_ids"] = {k: v for k, v in meta["stage_prompt_ids"].items() if v}

    envelope: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "recipe_version": RECIPE_VERSION,
        "status": "forming",
        "profile_fingerprint": pf[:128],
        "input_fact_set_version": fact_set[:128],
        "generated_at": _now_iso(),
        "meta": meta,
    }

    if isinstance(stage0.get("calc_authority"), dict):
        envelope["calc_authority"] = dict(stage0["calc_authority"])
    if isinstance(stage0.get("capability"), dict):
        envelope["capability"] = dict(stage0["capability"])
    raw_facts = stage0.get("raw_facts")
    if isinstance(raw_facts, list) and raw_facts:
        envelope["raw_facts"] = [
            _pick(f, _FACT_KEYS) for f in raw_facts if isinstance(f, dict) and f.get("fact_id")
        ]

    claims = stage1.get("claims") if isinstance(stage1.get("claims"), list) else []
    edges = stage1.get("edges") if isinstance(stage1.get("edges"), list) else []
    if claims or edges:
        envelope["evidence"] = {
            "schema_version": "evidence_graph_v1",
            "claims": [
                _pick(c, _CLAIM_KEYS) for c in claims if isinstance(c, dict) and c.get("claim_id")
            ],
            "edges": [
                _pick(e, _EDGE_KEYS) for e in edges if isinstance(e, dict) and e.get("edge_id")
            ],
        }

    cascade = None
    if str(stage2.get("status") or "") == "grounded":
        cascade = _build_cascade(
            identity=stage2, stage1=stage1, stage3=stage3, stage4=stage4
        )
    if cascade is not None:
        envelope["cascade"] = cascade

    if str(stage5.get("status") or "") == "grounded":
        compass = stage5.get("compass")
        if isinstance(compass, dict):
            envelope["compass"] = compass
        legacy = stage5.get("legacy_map")
        if isinstance(legacy, dict):
            # Schema: adapter_version + fields only.
            fields = legacy.get("fields") if isinstance(legacy.get("fields"), dict) else {}
            envelope["legacy_projections"] = {
                "adapter_version": str(legacy.get("adapter_version") or ADAPTER_VERSION),
                "fields": fields,
            }

    publish_ready = character_engine_publish_ready_enabled()
    complete = (
        str(stage5.get("status") or "") == "grounded"
        and isinstance(envelope.get("cascade"), dict)
        and isinstance(envelope.get("compass"), dict)
        and isinstance(envelope.get("raw_facts"), list)
        and isinstance(envelope.get("evidence"), dict)
        and isinstance(envelope.get("calc_authority"), dict)
        and isinstance(envelope.get("capability"), dict)
    )
    if publish_ready and complete:
        envelope["status"] = "ready"
    else:
        envelope["status"] = "forming"
        if complete:
            envelope["diagnostics"] = {
                "shadow": {
                    "schema_version": "ce_shadow_v1",
                    "compared_at": _now_iso(),
                    "ce_recipe_version": RECIPE_VERSION,
                    "recommendation": "hold",
                    "metrics": {
                        "publish_ready_flag": False,
                        "cascade_complete": True,
                        "envelope_version": ENVELOPE_VERSION,
                    },
                }
            }

    return envelope


def maybe_attach_character_engine_envelope_v0(
    profile_payload: dict[str, Any],
    *,
    profile_fingerprint: str,
    force: bool = False,
) -> dict[str, Any]:
    """Attach ``character_engine_v1`` when Stage nests exist and envelope missing."""
    if not (
        getattr(settings, "character_engine_stage5_shadow", False)
        or getattr(settings, "character_engine_stage5_enabled", False)
        or getattr(settings, "character_engine_profile_consumption", False)
        or character_engine_publish_ready_enabled()
    ):
        return profile_payload

    existing = profile_payload.get("character_engine_v1")
    if (
        not force
        and isinstance(existing, dict)
        and existing.get("schema_version") == SCHEMA_VERSION
        and str(existing.get("profile_fingerprint") or "") == str(profile_fingerprint or "")
    ):
        # Assemble-once: never rebuild for same fingerprint.
        if existing.get("status") == "ready" and not character_engine_publish_ready_enabled():
            # Defensive: ready without flag is not allowed.
            existing = {**existing, "status": "forming"}
            profile_payload["character_engine_v1"] = existing
        return profile_payload

    diagnostics = (
        profile_payload.get("diagnostics")
        if isinstance(profile_payload.get("diagnostics"), dict)
        else {}
    )
    stage5 = (diagnostics.get("character_engine_stage5") or {}).get("stage5")
    stage2 = (diagnostics.get("character_engine_stage2") or {}).get("stage2")
    if not isinstance(stage5, dict) and not isinstance(stage2, dict):
        return profile_payload

    try:
        envelope = build_character_engine_envelope_v0(
            diagnostics=diagnostics,
            profile_fingerprint=profile_fingerprint,
        )
    except Exception:
        logger.exception("character_engine_envelope_v0 failed")
        return profile_payload

    profile_payload["character_engine_v1"] = envelope
    return profile_payload

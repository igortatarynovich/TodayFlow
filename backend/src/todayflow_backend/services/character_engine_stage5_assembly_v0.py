"""Character Engine Stage 5 — deterministic assembly (Compass + legacy adapters).

Canon: CHARACTER_ENGINE_SCHEMA_CONTRACTS_V0.md §6–§7 · Architecture Impact Stage 5.
No LLM. No new claims. Expand-only projection of Stage 2–4 artifacts.
Never sets character_engine_v1 status=ready (that requires PUBLISH_READY cutover).
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from todayflow_backend.services.character_engine_ids_v0 import make_compass_item_id

STAGE5_VERSION = "character_engine_stage5_assembly_v0"
ADAPTER_VERSION = "character_engine_adapter_v1"
ASSEMBLER_VERSION = "character_engine_compass_assembler_v0"
COMPASS_SCHEMA = "compass_v1"

# item_kind → (surface path in stage3 engine or stage4)
_ENGINE_TO_COMPASS: tuple[tuple[str, str], ...] = (
    ("decision", "work_style"),
    ("perception", "communication_style"),
    ("recovery", "recovery"),
    ("stress", "triggers"),
    ("risk", "red_flags"),
    ("growth", "growth_directions"),
    ("burnout", "energy_sources"),
)


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _adapter_out(
    value: Any,
    *,
    claim_ids: list[str] | None = None,
    scene_ids: list[str] | None = None,
    compass_item_ids: list[str] | None = None,
    omit_reason: str | None = None,
) -> dict[str, Any]:
    if value is None or value == "" or value == []:
        return {
            "value": None,
            "source_refs": {
                "claim_ids": claim_ids or [],
                "scene_ids": scene_ids or [],
                "compass_item_ids": compass_item_ids or [],
            },
            "omit_reason": omit_reason or "empty",
        }
    return {
        "value": value,
        "source_refs": {
            "claim_ids": list(claim_ids or []),
            "scene_ids": list(scene_ids or []),
            "compass_item_ids": list(compass_item_ids or []),
        },
    }


def _scene_by_kind(stage4: dict[str, Any], *kinds: str) -> dict[str, Any] | None:
    scenes = stage4.get("scenes") if isinstance(stage4.get("scenes"), list) else []
    for want in kinds:
        for sc in scenes:
            if isinstance(sc, dict) and str(sc.get("scene_kind") or "") == want:
                if str(sc.get("surface_text") or "").strip():
                    return sc
    return None


def build_character_engine_assembly_v0(
    *,
    identity: dict[str, Any],
    stage3: dict[str, Any],
    stage4: dict[str, Any],
) -> dict[str, Any]:
    """Assemble Compass + LegacyMap from grounded Stage 2–4. Pure / no LLM."""
    errors: list[dict[str, Any]] = []

    if str(identity.get("status") or "") != "grounded":
        errors.append({"code": "identity_core_not_grounded"})
    if str(stage3.get("status") or "") != "grounded":
        errors.append({"code": "stage3_not_grounded"})
    if str(stage4.get("status") or "") != "grounded":
        errors.append({"code": "stage4_not_grounded"})

    if errors:
        return {
            "artifact_version": STAGE5_VERSION,
            "status": "insufficient_assembly",
            "compass": None,
            "legacy_map": None,
            "validation": {"ok": False, "no_new_claims": True, "deterministic": True},
            "diagnostics": {"contract_errors": errors},
            "generated_at": _now_iso(),
        }

    core = identity.get("identity_core") if isinstance(identity.get("identity_core"), dict) else {}
    identity_thesis = str(core.get("thesis_key") or "").strip()
    primary_claim = str(core.get("primary_claim_id") or "").strip()
    support_claims = [primary_claim] if primary_claim else []
    for cid in core.get("supporting_claim_ids") or []:
        c = str(cid or "").strip()
        if c and c not in support_claims:
            support_claims.append(c)

    engine = stage3.get("internal_engine") if isinstance(stage3.get("internal_engine"), dict) else {}
    pt = stage3.get("primary_tension") if isinstance(stage3.get("primary_tension"), dict) else {}
    potential = stage4.get("potential") if isinstance(stage4.get("potential"), dict) else {}
    blind_spots = stage4.get("blind_spots") if isinstance(stage4.get("blind_spots"), list) else []

    compass_items: list[dict[str, Any]] = []
    all_scene_ids: list[str] = []
    mechanism_slots_used: list[str] = []

    for slot, item_kind in _ENGINE_TO_COMPASS:
        row = engine.get(slot) if isinstance(engine.get(slot), dict) else None
        text = str((row or {}).get("surface_text") or "").strip()
        if not text:
            continue
        refs = {
            "claim_ids": list((row or {}).get("supporting_claim_ids") or support_claims[:1]),
            "scene_ids": [],
            "mechanism_slots": [slot],
        }
        item_id = make_compass_item_id(item_kind=item_kind, source_refs=refs)
        compass_items.append(
            {
                "item_id": item_id,
                "item_kind": item_kind,
                "value": text,
                "derived_from": refs,
            }
        )
        mechanism_slots_used.append(slot)

    # Growth from Stage 4 potential (may reinforce growth_directions).
    pot_text = str(potential.get("surface_text") or "").strip()
    if pot_text:
        refs = {
            "claim_ids": list(potential.get("supporting_claim_ids") or support_claims[:1]),
            "scene_ids": [],
            "mechanism_slots": ["growth"],
        }
        item_id = make_compass_item_id(item_kind="growth_directions", source_refs=refs)
        # Prefer potential as primary growth_directions if engine growth also present —
        # keep both only if distinct item_ids (fingerprint differs by refs).
        if not any(i["item_id"] == item_id for i in compass_items):
            compass_items.append(
                {
                    "item_id": item_id,
                    "item_kind": "growth_directions",
                    "value": pot_text,
                    "derived_from": refs,
                }
            )

    # Strengths stay empty in Stage5 adapters — consumption essays own them.
    # Do not reuse Identity Core surface as "strengths" (duplicates recognition).
    core_surface = str(core.get("surface_text") or "").strip()

    intimacy = _scene_by_kind(stage4, "intimacy")
    resource = _scene_by_kind(stage4, "risk", "responsibility", "uncertainty")
    for sc in (intimacy, resource):
        if isinstance(sc, dict) and sc.get("scene_id"):
            all_scene_ids.append(str(sc["scene_id"]))

    compass = {
        "schema_version": COMPASS_SCHEMA,
        "assembler_version": ASSEMBLER_VERSION,
        "items": compass_items,
        "source_refs": {
            "claim_ids": support_claims[:],
            "scene_ids": sorted(set(all_scene_ids)),
            "mechanism_slots": sorted(set(mechanism_slots_used)),
        },
    }

    def _compass_ids_for(*kinds: str) -> list[str]:
        return [i["item_id"] for i in compass_items if i.get("item_kind") in kinds]

    decision_text = str((engine.get("decision") or {}).get("surface_text") or "").strip()
    perception_text = str((engine.get("perception") or {}).get("surface_text") or "").strip()
    stress_text = str((engine.get("stress") or {}).get("surface_text") or "").strip()
    emotional = perception_text or stress_text
    recovery_text = str((engine.get("recovery") or {}).get("surface_text") or "").strip()
    growth_text = pot_text or str((engine.get("growth") or {}).get("surface_text") or "").strip()
    trap_text = str(pt.get("surface_text") or "").strip()
    intimacy_text = str((intimacy or {}).get("surface_text") or "").strip()
    resource_text = str((resource or {}).get("surface_text") or "").strip()
    blind_texts = [
        str(b.get("surface_text") or "").strip()
        for b in blind_spots
        if isinstance(b, dict) and str(b.get("surface_text") or "").strip()
    ][:4]

    legacy_fields: dict[str, Any] = {
        "identity_core": _adapter_out(core_surface, claim_ids=support_claims),
        "recognition_line": _adapter_out(core_surface, claim_ids=support_claims),
        "decision_style": _adapter_out(
            decision_text or None,
            claim_ids=list((engine.get("decision") or {}).get("supporting_claim_ids") or support_claims[:1]),
            compass_item_ids=_compass_ids_for("work_style"),
        ),
        "emotional_style": _adapter_out(
            emotional or None,
            claim_ids=support_claims[:1],
            compass_item_ids=_compass_ids_for("communication_style", "triggers"),
        ),
        "relationship_style": _adapter_out(
            intimacy_text or None,
            claim_ids=list((intimacy or {}).get("supporting_claim_ids") or support_claims[:1]),
            scene_ids=[str(intimacy["scene_id"])] if intimacy and intimacy.get("scene_id") else [],
        ),
        "money_patterns": _adapter_out(
            resource_text or None,
            claim_ids=list((resource or {}).get("supporting_claim_ids") or support_claims[:1]),
            scene_ids=[str(resource["scene_id"])] if resource and resource.get("scene_id") else [],
        ),
        "strengths": _adapter_out(
            None,
            claim_ids=support_claims,
            compass_item_ids=_compass_ids_for("strengths"),
        ),
        "growth_zones": _adapter_out(
            [growth_text] if growth_text else None,
            claim_ids=list(potential.get("supporting_claim_ids") or support_claims[:1]),
            compass_item_ids=_compass_ids_for("growth_directions"),
        ),
        "blind_spots": _adapter_out(
            blind_texts or None,
            claim_ids=support_claims[:1],
            compass_item_ids=_compass_ids_for("red_flags"),
        ),
        "helps": _adapter_out(
            [t for t in (growth_text, recovery_text) if t] or None,
            claim_ids=support_claims[:1],
            compass_item_ids=_compass_ids_for("growth_directions", "recovery"),
        ),
        "recurring_patterns": _adapter_out(
            [trap_text] if trap_text else None,
            claim_ids=list(pt.get("supporting_claim_ids") or support_claims[:1]),
        ),
    }

    legacy_map = {
        "adapter_version": ADAPTER_VERSION,
        "fields": legacy_fields,
        "identity_thesis": identity_thesis,
        "rooted_in_stages": ["stage2", "stage3", "stage4"],
    }

    return {
        "artifact_version": STAGE5_VERSION,
        "status": "grounded",
        "identity_thesis": identity_thesis,
        "compass": compass,
        "legacy_map": legacy_map,
        "validation": {
            "ok": True,
            "no_new_claims": True,
            "deterministic": True,
            "expand_only": True,
            "ready_publish_blocked": True,
        },
        "diagnostics": {
            "contract_errors": [],
            "compass_item_count": len(compass_items),
            "adapter_field_count": len(legacy_fields),
            "note": "Assembly only — CHARACTER_ENGINE_PUBLISH_READY required for CE ready SoT",
        },
        "generated_at": _now_iso(),
    }

"""Character Engine Stage 1 — evidence candidates from deterministic registry.

No identity_core, scenes, Compass, or life-area essays.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from todayflow_backend.knowledge.calc_il_wire_v1 import skyfacts_from_calc
from todayflow_backend.knowledge.il2_composition_v1 import load_objects
from todayflow_backend.knowledge.il3_interpretation_v1 import interpret
from todayflow_backend.knowledge.il4_expression_v1 import express
from todayflow_backend.services.character_engine_evidence_registry_v0 import (
    EVIDENCE_RULES_V0,
    FORBIDDEN_STAGE1_CLAIM_KINDS,
    EvidenceRule,
)
from todayflow_backend.services.character_engine_ids_v0 import make_claim_id, make_edge_id

STAGE1_VERSION = "character_engine_stage1_evidence_v0"
# Occupancy only — not aspects, transits, or angles.
_IL_OCCUPANCY = frozenset({"planet_in_sign", "planet_in_house"})


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _index_facts(raw_facts: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    by_type: dict[str, dict[str, Any]] = {}
    for row in raw_facts:
        if not isinstance(row, dict):
            continue
        ft = str(row.get("fact_type") or "").strip()
        if not ft:
            continue
        # First wins within type after Stage 0 already deduped by fact_key;
        # if duplicates remain, prefer higher-confidence swiss-like via sort later.
        prev = by_type.get(ft)
        if prev is None:
            by_type[ft] = row
            continue
        rank = {"high": 3, "medium": 2, "low": 1}
        if rank.get(str(row.get("confidence")), 0) > rank.get(str(prev.get("confidence")), 0):
            by_type[ft] = row
    return by_type


def _capability_ok(floor: str, capability: dict[str, Any] | None) -> bool:
    mode = str((capability or {}).get("natal_mode") or "none").lower()
    if floor == "full_natal":
        return mode == "full"
    if floor == "name":
        return bool((capability or {}).get("has_name")) or mode in {"date_only", "full"}
    if floor == "date_only":
        return mode in {"date_only", "full"}
    return True


def _collect_ids(
    facts_by_type: dict[str, dict[str, Any]],
    fact_types: tuple[str, ...],
) -> list[str]:
    ids: list[str] = []
    for ft in fact_types:
        row = facts_by_type.get(ft)
        if row and row.get("fact_id"):
            ids.append(str(row["fact_id"]))
    # Stable unique order
    return sorted(set(ids))


def _snapshot_from_stage0(raw_facts: list[dict[str, Any]]) -> dict[str, Any]:
    """Rebuild a calc snapshot from Stage 0 planet_sign rows. No longitudes → no aspects."""
    positions: list[dict[str, Any]] = []
    for row in raw_facts:
        ft = str(row.get("fact_type") or "")
        if not ft.startswith("planet_sign:"):
            continue
        value = row.get("value") if isinstance(row.get("value"), dict) else {}
        body = str(value.get("body") or ft.split(":", 1)[-1]).strip().lower()
        sign = str(value.get("sign") or "").strip().lower()
        if not body or not sign:
            continue
        pos: dict[str, Any] = {"body": body, "sign": sign}
        house = value.get("house")
        if house is not None:
            pos["house"] = house
        positions.append(pos)
    return {"positions": positions, "houses": {}}


def _il_occupancy_thesis(construction: str, parts: tuple[str, ...]) -> str | None:
    if construction == "planet_in_sign" and len(parts) >= 2:
        planet = str(parts[0]).rsplit(".", 1)[-1]
        sign = str(parts[1]).rsplit(".", 1)[-1]
        return f"planet_in_sign:{planet}:{sign}"
    if construction == "planet_in_house" and len(parts) >= 2:
        planet = str(parts[0]).rsplit(".", 1)[-1]
        house = str(parts[1]).rsplit(".", 1)[-1]
        return f"planet_in_house:{planet}:{house}"
    return None


def _mint_il_occupancy_claims(
    *,
    facts_by_type: dict[str, dict[str, Any]],
    raw_facts: list[dict[str, Any]],
    capability: dict[str, Any] | None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    """IL-3 planet_in_sign / planet_in_house from Stage 0 facts. Omit if compose refuses."""
    snapshot = _snapshot_from_stage0(raw_facts)
    if not snapshot["positions"]:
        return [], [], []
    sky = tuple(
        fact
        for fact in skyfacts_from_calc(snapshot)
        if fact.construction in _IL_OCCUPANCY
    )
    if not sky:
        return [], [], []
    catalog = load_objects()
    themes = interpret(catalog, sky)
    pack = express(themes, "profile")
    claims: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    excluded: list[dict[str, Any]] = []
    by_rank = {theme.rank: theme for theme in themes.themes}
    cap_floor = "full_natal" if _capability_ok("full_natal", capability) else "date_only"
    for line in pack.lines:
        if line.construction not in _IL_OCCUPANCY:
            continue
        theme = by_rank.get(line.rank)
        parts: tuple[str, ...] = ()
        if theme is not None and theme.frame.construction == "planet_in_sign":
            what = theme.frame.jobs.get("what")
            how = theme.frame.jobs.get("how")
            if what is not None and how is not None:
                parts = (what.object_id, how.object_id)
        elif theme is not None and theme.frame.construction == "planet_in_house":
            what = theme.frame.jobs.get("what")
            where = theme.frame.jobs.get("where")
            if what is not None and where is not None:
                parts = (what.object_id, where.object_id)
        thesis = _il_occupancy_thesis(line.construction, parts)
        if not thesis:
            excluded.append(
                {
                    "rule_key": "il3_occupancy",
                    "reason": "thesis_unmapped",
                    "construction": line.construction,
                }
            )
            continue
        planet = thesis.split(":")[1]
        supporting = _collect_ids(facts_by_type, (f"planet_sign:{planet}",))
        if not supporting:
            excluded.append(
                {
                    "rule_key": "il3_occupancy",
                    "reason": "supporting_facts_missing",
                    "thesis_key": thesis,
                }
            )
            continue
        claim_id = make_claim_id(
            claim_kind="mechanism",
            thesis_key=thesis,
            primary_fact_ids=supporting,
        )
        claim = {
            "claim_id": claim_id,
            "claim_kind": "mechanism",
            "thesis_key": thesis,
            "cascade_role": "mechanism",
            "supporting_fact_ids": supporting,
            "confidence": "medium",
            "capability_floor": cap_floor,
            "produced_by_stage": 1,
            "evidence_status": "grounded",
            "il_line": line.text,
            "_rule_key": "il3_occupancy",
        }
        claims.append(claim)
        for fid in supporting:
            edges.append(
                {
                    "edge_id": make_edge_id(fact_id=fid, claim_id=claim_id, edge_type="supports"),
                    "fact_id": fid,
                    "claim_id": claim_id,
                    "edge_type": "supports",
                }
            )
    return claims, edges, excluded


def _apply_rule(
    rule: EvidenceRule,
    *,
    facts_by_type: dict[str, dict[str, Any]],
    capability: dict[str, Any] | None,
) -> tuple[dict[str, Any] | None, dict[str, Any] | None, list[dict[str, Any]]]:
    """Return (claim, exclusion, edges)."""
    if rule.claim_kind in FORBIDDEN_STAGE1_CLAIM_KINDS:
        return None, {
            "rule_key": rule.rule_key,
            "reason": "forbidden_claim_kind",
            "claim_kind": rule.claim_kind,
        }, []

    if not _capability_ok(rule.capability_floor, capability):
        return None, {
            "rule_key": rule.rule_key,
            "reason": "capability_insufficient",
            "required": rule.capability_floor,
        }, []

    if not rule.match(facts_by_type):
        return None, {
            "rule_key": rule.rule_key,
            "reason": "pattern_not_matched",
        }, []

    supporting = _collect_ids(facts_by_type, rule.supporting_fact_types)
    if not supporting:
        return None, {
            "rule_key": rule.rule_key,
            "reason": "supporting_facts_missing",
        }, []

    claim_id = make_claim_id(
        claim_kind=rule.claim_kind,
        thesis_key=rule.thesis_key,
        primary_fact_ids=supporting,
    )
    claim = {
        "claim_id": claim_id,
        "claim_kind": rule.claim_kind,
        "thesis_key": rule.thesis_key,
        "cascade_role": rule.claim_kind,
        "supporting_fact_ids": supporting,
        "confidence": rule.confidence,
        "capability_floor": rule.capability_floor,
        "produced_by_stage": 1,
        "evidence_status": "grounded",
        # surface_text intentionally omitted — Stage 1 candidates are not prose.
        # rule_key lives in diagnostics (not public claim schema).
    }

    edges: list[dict[str, Any]] = []
    for fid in supporting:
        edges.append(
            {
                "edge_id": make_edge_id(fact_id=fid, claim_id=claim_id, edge_type=rule.edge_type),
                "fact_id": fid,
                "claim_id": claim_id,
                "edge_type": rule.edge_type,
            }
        )
    for ft in rule.strengthen_fact_types:
        row = facts_by_type.get(ft)
        if not row:
            continue
        fid = str(row["fact_id"])
        edges.append(
            {
                "edge_id": make_edge_id(fact_id=fid, claim_id=claim_id, edge_type="strengthens"),
                "fact_id": fid,
                "claim_id": claim_id,
                "edge_type": "strengthens",
            }
        )
    for ft in rule.qualify_fact_types:
        row = facts_by_type.get(ft)
        if not row:
            continue
        fid = str(row["fact_id"])
        edges.append(
            {
                "edge_id": make_edge_id(fact_id=fid, claim_id=claim_id, edge_type="qualifies"),
                "fact_id": fid,
                "claim_id": claim_id,
                "edge_type": "qualifies",
            }
        )
    contradicting: list[str] = []
    for ft in rule.contradict_fact_types:
        row = facts_by_type.get(ft)
        if not row:
            continue
        fid = str(row["fact_id"])
        contradicting.append(fid)
        edges.append(
            {
                "edge_id": make_edge_id(fact_id=fid, claim_id=claim_id, edge_type="contradicts"),
                "fact_id": fid,
                "claim_id": claim_id,
                "edge_type": "contradicts",
            }
        )
    if contradicting:
        claim["contradicting_fact_ids"] = sorted(set(contradicting))

    return claim, None, edges


def build_character_engine_evidence_candidates_v0(
    facts_pack: dict[str, Any],
) -> dict[str, Any]:
    raw_facts = facts_pack.get("raw_facts") if isinstance(facts_pack.get("raw_facts"), list) else []
    capability = facts_pack.get("capability") if isinstance(facts_pack.get("capability"), dict) else {}
    facts_by_type = _index_facts([f for f in raw_facts if isinstance(f, dict)])

    claims: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    excluded: list[dict[str, Any]] = []

    for rule in EVIDENCE_RULES_V0:
        claim, exclusion, rule_edges = _apply_rule(
            rule, facts_by_type=facts_by_type, capability=capability
        )
        if exclusion:
            excluded.append(exclusion)
            continue
        if claim:
            claims.append(claim)
            edges.extend(rule_edges)
            # Track rule provenance outside public claim shape.
            claim["_rule_key"] = rule.rule_key

    il_claims, il_edges, il_excluded = _mint_il_occupancy_claims(
        facts_by_type=facts_by_type,
        raw_facts=[f for f in raw_facts if isinstance(f, dict)],
        capability=capability,
    )
    claims.extend(il_claims)
    edges.extend(il_edges)
    excluded.extend(il_excluded)

    # Stable ordering
    claims.sort(key=lambda c: (c["claim_kind"], c["thesis_key"], c["claim_id"]))
    edges.sort(key=lambda e: e["edge_id"])
    excluded.sort(key=lambda e: (e.get("rule_key") or "", e.get("reason") or ""))

    rule_by_claim = {
        str(c["claim_id"]): str(c.pop("_rule_key"))
        for c in claims
        if c.get("_rule_key")
    }

    fact_ids = {str(f.get("fact_id")) for f in raw_facts if isinstance(f, dict) and f.get("fact_id")}
    validation = {
        "all_supporting_facts_exist": all(
            all(fid in fact_ids for fid in (c.get("supporting_fact_ids") or [])) for c in claims
        ),
        "all_edges_resolve": all(
            (e.get("fact_id") in fact_ids) and any(c["claim_id"] == e.get("claim_id") for c in claims)
            for e in edges
        ),
        "forbidden_kinds_absent": all(c["claim_kind"] not in FORBIDDEN_STAGE1_CLAIM_KINDS for c in claims),
        "has_cascade_sections": False,
        "has_identity_core": False,
        "has_compass": False,
    }

    return {
        "stage": 1,
        "stage_version": STAGE1_VERSION,
        "schema_version": "evidence_graph_v1",
        "claims": claims,
        "edges": edges,
        "excluded_candidates": excluded,
        "capability": capability,
        "diagnostics": {
            "rules_evaluated": len(EVIDENCE_RULES_V0),
            "claims_emitted": len(claims),
            "excluded": len(excluded),
            "il_occupancy_emitted": len(il_claims),
            "rule_by_claim_id": rule_by_claim,
            "validation": validation,
        },
        "generated_at": _now_iso(),
    }

"""Character Engine Stage 1 — evidence candidates from deterministic registry.

No identity_core, scenes, Compass, or life-area essays.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from todayflow_backend.knowledge.il2_composition_v1 import (
    ComposedFrame,
    compose_aspect_pair,
    compose_planet_in_house,
    compose_planet_in_sign,
    load_objects,
)
from todayflow_backend.services.character_engine_evidence_registry_v0 import (
    EVIDENCE_RULES_V0,
    FORBIDDEN_STAGE1_CLAIM_KINDS,
    EvidenceRule,
)
from todayflow_backend.services.character_engine_ids_v0 import make_claim_id, make_edge_id

STAGE1_VERSION = "character_engine_stage1_evidence_v0"
# PIC: docs/profile/PROFILE_INFORMATION_CONTRACT_V1.md
PIC_K = ("K01", "K02", "K05")
PIC_F = ("F03", "F06", "F07")
# Occupancy Sun–Saturn + one hard aspect_pair tension. Not transits, not K06 secondaries.
_OCCUPANCY_BODIES = ("sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn")
_HARD_ASPECTS = {"opposition": 0, "square": 1}


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


def _occupancy_line(frame: ComposedFrame) -> str:
    """Sign manner / house arena lemmas. Planet function is already in the 13-key thesis."""
    bits: list[str] = []
    for job_name in ("how", "where"):
        payload = frame.jobs.get(job_name)
        if payload is None:
            continue
        bits.extend(str(lemma) for lemma in payload.lemmas if lemma)
    return " ".join(bits)


def _emit_occupancy_claim(
    *,
    construction: str,
    thesis: str,
    frame: ComposedFrame,
    supporting: list[str],
    capability_floor: str,
) -> tuple[dict[str, Any] | None, dict[str, Any] | None, list[dict[str, Any]]]:
    if frame.status != "composed":
        return None, {
            "rule_key": "il2_occupancy",
            "reason": frame.reason or "compose_refused",
            "thesis_key": thesis,
            "construction": construction,
        }, []
    line = _occupancy_line(frame)
    if not line:
        return None, {
            "rule_key": "il2_occupancy",
            "reason": "lemmas_empty",
            "thesis_key": thesis,
        }, []
    if not supporting:
        return None, {
            "rule_key": "il2_occupancy",
            "reason": "supporting_facts_missing",
            "thesis_key": thesis,
        }, []
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
        "capability_floor": capability_floor,
        "produced_by_stage": 1,
        "evidence_status": "grounded",
        "il_line": line,
        "_rule_key": "il2_occupancy",
    }
    edges = [
        {
            "edge_id": make_edge_id(fact_id=fid, claim_id=claim_id, edge_type="supports"),
            "fact_id": fid,
            "claim_id": claim_id,
            "edge_type": "supports",
        }
        for fid in supporting
    ]
    return claim, None, edges


def _mint_il_occupancy_claims(
    *,
    facts_by_type: dict[str, dict[str, Any]],
    capability: dict[str, Any] | None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    """IL-2 planet_in_sign / planet_in_house from Stage 0 F03/F06. Omit if compose refuses."""
    catalog = load_objects()
    natal_full = _capability_ok("full_natal", capability)
    claims: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    excluded: list[dict[str, Any]] = []
    for body in _OCCUPANCY_BODIES:
        row = facts_by_type.get(f"planet_sign:{body}")
        if not row:
            continue
        value = row.get("value") if isinstance(row.get("value"), dict) else {}
        supporting = _collect_ids(facts_by_type, (f"planet_sign:{body}",))
        sign = str(value.get("sign") or "").strip().lower()
        if sign:
            frame = compose_planet_in_sign(
                catalog, f"astro.object.{body}", f"astro.sign.{sign}"
            )
            claim, exclusion, claim_edges = _emit_occupancy_claim(
                construction="planet_in_sign",
                thesis=f"planet_in_sign:{body}:{sign}",
                frame=frame,
                supporting=supporting,
                capability_floor="date_only",
            )
            if exclusion:
                excluded.append(exclusion)
            elif claim:
                claims.append(claim)
                edges.extend(claim_edges)
        if not natal_full:
            continue
        try:
            house_n = int(value.get("house"))
        except (TypeError, ValueError):
            continue
        if not (1 <= house_n <= 12):
            continue
        house_id = f"{house_n:02d}"
        frame = compose_planet_in_house(
            catalog, f"astro.object.{body}", f"astro.house.{house_id}"
        )
        claim, exclusion, claim_edges = _emit_occupancy_claim(
            construction="planet_in_house",
            thesis=f"planet_in_house:{body}:{house_id}",
            frame=frame,
            supporting=supporting,
            capability_floor="full_natal",
        )
        if exclusion:
            excluded.append(exclusion)
        elif claim:
            claims.append(claim)
            edges.extend(claim_edges)
    return claims, edges, excluded


def _first_lemma(frame: ComposedFrame, job_name: str) -> str:
    payload = frame.jobs.get(job_name)
    if payload is None:
        return ""
    for lemma in payload.lemmas:
        token = str(lemma).strip()
        if token:
            return token
    return ""


def _aspect_tension_line(frame: ComposedFrame) -> str:
    """Keep both poles A↔B. Do not collapse into a one-sided trait."""
    what_a = _first_lemma(frame, "what_a")
    what_b = _first_lemma(frame, "what_b")
    relation = _first_lemma(frame, "relation")
    if not what_a or not what_b or not relation:
        return ""
    return f"{what_a} ↔ {what_b} — {relation}."


def _parse_aspect_fact(row: dict[str, Any]) -> tuple[str, str, str, float] | None:
    value = row.get("value") if isinstance(row.get("value"), dict) else {}
    body_a = str(value.get("body_a") or "").strip().lower()
    body_b = str(value.get("body_b") or "").strip().lower()
    aspect = str(value.get("aspect") or "").strip().lower()
    if not body_a or not body_b or aspect not in _HARD_ASPECTS:
        return None
    try:
        orb = float(value.get("orb"))
    except (TypeError, ValueError):
        orb = 99.0
    if body_a > body_b:
        body_a, body_b = body_b, body_a
    return body_a, body_b, aspect, orb


def _mint_il_aspect_tension_claim(
    *,
    facts_by_type: dict[str, dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    """Exactly one primary K05 tension from grounded hard F07. Harmonics omitted, not secondary."""
    catalog = load_objects()
    ranked: list[tuple[int, float, str, dict[str, Any], tuple[str, str, str]]] = []
    excluded: list[dict[str, Any]] = []
    for fact_type, row in facts_by_type.items():
        if not str(fact_type).startswith("aspect_pair:"):
            continue
        parsed = _parse_aspect_fact(row)
        if parsed is None:
            excluded.append(
                {
                    "rule_key": "il2_aspect_pair",
                    "reason": "not_hard_aspect",
                    "thesis_key": fact_type,
                }
            )
            continue
        body_a, body_b, aspect, orb = parsed
        thesis = f"aspect_pair:{body_a}:{body_b}:{aspect}"
        ranked.append(
            (
                _HARD_ASPECTS[aspect],
                orb,
                thesis,
                row,
                (body_a, body_b, aspect),
            )
        )
    ranked.sort(key=lambda item: (item[0], item[1], item[2]))
    for _rank, _orb, thesis, row, (body_a, body_b, aspect) in ranked:
        supporting = [str(row["fact_id"])] if row.get("fact_id") else []
        if not supporting:
            excluded.append(
                {
                    "rule_key": "il2_aspect_pair",
                    "reason": "supporting_facts_missing",
                    "thesis_key": thesis,
                }
            )
            continue
        frame = compose_aspect_pair(
            catalog,
            f"astro.object.{body_a}",
            f"astro.object.{body_b}",
            f"astro.aspect.{aspect}",
        )
        if frame.status != "composed":
            excluded.append(
                {
                    "rule_key": "il2_aspect_pair",
                    "reason": frame.reason or "compose_refused",
                    "thesis_key": thesis,
                }
            )
            continue
        line = _aspect_tension_line(frame)
        if not line:
            excluded.append(
                {
                    "rule_key": "il2_aspect_pair",
                    "reason": "lemmas_empty",
                    "thesis_key": thesis,
                }
            )
            continue
        claim_id = make_claim_id(
            claim_kind="tension",
            thesis_key=thesis,
            primary_fact_ids=supporting,
        )
        claim = {
            "claim_id": claim_id,
            "claim_kind": "tension",
            "thesis_key": thesis,
            "cascade_role": "tension",
            "supporting_fact_ids": supporting,
            "confidence": str(row.get("confidence") or "medium"),
            "capability_floor": "date_only",
            "produced_by_stage": 1,
            "evidence_status": "grounded",
            "il_line": line,
            "_rule_key": "il2_aspect_pair",
        }
        edges = [
            {
                "edge_id": make_edge_id(fact_id=fid, claim_id=claim_id, edge_type="supports"),
                "fact_id": fid,
                "claim_id": claim_id,
                "edge_type": "supports",
            }
            for fid in supporting
        ]
        for leftover in ranked:
            leftover_thesis = leftover[2]
            if leftover_thesis == thesis:
                continue
            excluded.append(
                {
                    "rule_key": "il2_aspect_pair",
                    "reason": "not_primary_k05",
                    "thesis_key": leftover_thesis,
                }
            )
        return [claim], edges, excluded
    return [], [], excluded


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
        capability=capability,
    )
    claims.extend(il_claims)
    edges.extend(il_edges)
    excluded.extend(il_excluded)

    tension_claims, tension_edges, tension_excluded = _mint_il_aspect_tension_claim(
        facts_by_type=facts_by_type,
    )
    claims.extend(tension_claims)
    edges.extend(tension_edges)
    excluded.extend(tension_excluded)

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
            "il_aspect_tension_emitted": len(tension_claims),
            "rule_by_claim_id": rule_by_claim,
            "validation": validation,
        },
        "generated_at": _now_iso(),
    }

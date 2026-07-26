"""Character Engine Stage 2 — Identity Core (LLM-first, structural validation only).

Quality of the logline and claim selection lives in prompt
`profile.character_engine.stage2.v1`. Code checks JSON contract + provenance:
existing claim_id / fact_id refs, no invented claims, required fields.
"""

from __future__ import annotations

import json
import logging
import re
from datetime import datetime, timezone
from typing import Any

from todayflow_backend.core.llm_openai_compatible import (
    chat_completion_text,
    get_openai_compatible_client,
    is_llm_chat_configured,
    resolve_default_chat_model,
)
from todayflow_backend.prompts.registry_v1 import get_prompt
from todayflow_backend.services.character_engine_ids_v0 import make_claim_id
from todayflow_backend.services.character_engine_identity_thesis_registry_v0 import (
    ALLOWED_IDENTITY_THESIS_KEYS,
    ALLOWED_SOURCE_ROLES,
    normalize_identity_thesis_key,
)

logger = logging.getLogger(__name__)

STAGE2_VERSION = "character_engine_stage2_identity_v0"
STAGE2_PROMPT_ID = "profile.character_engine.stage2.v1"
RECIPE_VERSION = "character_engine_recipe_v1"


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _parse_json_object(raw: str) -> dict[str, Any] | None:
    text = (raw or "").strip()
    if not text:
        return None
    try:
        data = json.loads(text)
        return data if isinstance(data, dict) else None
    except json.JSONDecodeError:
        match = re.search(r"\{[\s\S]*\}", text)
        if not match:
            return None
        try:
            data = json.loads(match.group(0))
            return data if isinstance(data, dict) else None
        except json.JSONDecodeError:
            return None


def build_stage2_context_pack(
    *,
    facts_pack: dict[str, Any],
    evidence: dict[str, Any],
) -> dict[str, Any]:
    """Deterministic context for the Stage 2 prompt — Facts + Evidence Graph only."""
    raw_facts = facts_pack.get("raw_facts") if isinstance(facts_pack.get("raw_facts"), list) else []
    claims = evidence.get("claims") if isinstance(evidence.get("claims"), list) else []
    edges = evidence.get("edges") if isinstance(evidence.get("edges"), list) else []
    capability = facts_pack.get("capability") if isinstance(facts_pack.get("capability"), dict) else {}

    grounded = [
        {
            "claim_id": c.get("claim_id"),
            "claim_kind": c.get("claim_kind"),
            "thesis_key": c.get("thesis_key"),
            "supporting_fact_ids": list(c.get("supporting_fact_ids") or []),
            "contradicting_fact_ids": list(c.get("contradicting_fact_ids") or []),
            "confidence": c.get("confidence"),
            "capability_floor": c.get("capability_floor"),
            "evidence_status": c.get("evidence_status"),
        }
        for c in claims
        if isinstance(c, dict) and c.get("evidence_status") == "grounded" and c.get("claim_id")
    ]
    fact_rows = [
        {
            "fact_id": f.get("fact_id"),
            "fact_type": f.get("fact_type"),
            "value": f.get("value"),
            "authority": f.get("authority"),
            "confidence": f.get("confidence"),
        }
        for f in raw_facts
        if isinstance(f, dict) and f.get("fact_id")
    ]
    edge_rows = [
        {
            "edge_id": e.get("edge_id"),
            "fact_id": e.get("fact_id"),
            "claim_id": e.get("claim_id"),
            "edge_type": e.get("edge_type"),
        }
        for e in edges
        if isinstance(e, dict) and e.get("edge_id")
    ]
    return {
        "recipe_version": RECIPE_VERSION,
        "prompt_id": STAGE2_PROMPT_ID,
        "capability": capability,
        "raw_facts": fact_rows,
        "claims": grounded,
        "edges": edge_rows,
        "allowed_primary_claim_ids": [c["claim_id"] for c in grounded],
        "allowed_thesis_keys": sorted({str(c["thesis_key"]) for c in grounded if c.get("thesis_key")}),
        # Explicitly absent — prompt must not reconstruct old portrait roots.
        "forbidden_inputs": [
            "profile_contract_v1",
            "disclosure_funnel",
            "personality_prose",
            "career_love_money_blocks",
            "ui_taxonomy",
        ],
    }


def validate_stage2_identity_contract(
    raw: dict[str, Any],
    *,
    facts_pack: dict[str, Any],
    evidence: dict[str, Any],
    prompt_version: str,
) -> dict[str, Any]:
    """
    Structural + provenance validation only.

    Does NOT score wording quality, trait-list heuristics, or claim ranking.
    """
    raw_facts = facts_pack.get("raw_facts") if isinstance(facts_pack.get("raw_facts"), list) else []
    claims = evidence.get("claims") if isinstance(evidence.get("claims"), list) else []
    fact_ids = {str(f.get("fact_id")) for f in raw_facts if isinstance(f, dict) and f.get("fact_id")}
    claims_by_id = {
        str(c["claim_id"]): c
        for c in claims
        if isinstance(c, dict) and c.get("claim_id") and c.get("evidence_status") == "grounded"
    }
    claim_ids = set(claims_by_id.keys())

    status = str(raw.get("status") or "").strip()
    diagnostics = {
        "prompt_id": STAGE2_PROMPT_ID,
        "prompt_version": prompt_version,
        "recipe_version": RECIPE_VERSION,
        "selection_rationale": str(raw.get("selection_rationale") or "").strip() or None,
        "contract_errors": [],
    }
    capability = facts_pack.get("capability") if isinstance(facts_pack.get("capability"), dict) else {}

    def _fail(code: str, **extra: Any) -> dict[str, Any]:
        diagnostics["contract_errors"].append({"code": code, **extra})
        return {
            "stage": 2,
            "stage_version": STAGE2_VERSION,
            "status": "insufficient_identity_core",
            "identity_core": None,
            "source_roles": [],
            "capability": capability,
            "diagnostics": diagnostics,
            "validation": {
                "json_shape_ok": False,
                "refs_resolve": False,
                "no_invented_claims": False,
                "required_fields_ok": False,
                "thesis_matches_primary": False,
            },
            "generated_at": _now_iso(),
        }

    if status not in {"grounded", "insufficient_identity_core"}:
        return _fail("invalid_status", got=status)

    source_roles_raw = raw.get("source_roles") if isinstance(raw.get("source_roles"), list) else []
    source_roles: list[dict[str, Any]] = []
    for row in source_roles_raw:
        if not isinstance(row, dict):
            return _fail("source_role_not_object")
        cid = str(row.get("claim_id") or "").strip()
        role = str(row.get("role") or "").strip()
        if cid not in claim_ids:
            return _fail("source_role_unknown_claim", claim_id=cid)
        if role not in ALLOWED_SOURCE_ROLES:
            return _fail("source_role_unknown_role", role=role)
        source_roles.append({"role": role, "claim_id": cid})

    if status == "insufficient_identity_core":
        if raw.get("identity_core") not in (None, {}):
            return _fail("insufficient_must_null_core")
        return {
            "stage": 2,
            "stage_version": STAGE2_VERSION,
            "status": "insufficient_identity_core",
            "identity_core": None,
            "source_roles": source_roles,
            "capability": capability,
            "diagnostics": diagnostics,
            "validation": {
                "json_shape_ok": True,
                "refs_resolve": True,
                "no_invented_claims": True,
                "required_fields_ok": True,
                "thesis_matches_primary": True,
            },
            "generated_at": _now_iso(),
        }

    core_raw = raw.get("identity_core")
    if not isinstance(core_raw, dict):
        return _fail("grounded_requires_identity_core")

    primary_claim_id = str(core_raw.get("primary_claim_id") or "").strip()
    if primary_claim_id not in claim_ids:
        return _fail("primary_claim_unknown", claim_id=primary_claim_id)
    primary = claims_by_id[primary_claim_id]

    thesis_key_in = str(core_raw.get("thesis_key") or "").strip()
    primary_thesis = str(primary.get("thesis_key") or "").strip()
    if not thesis_key_in or thesis_key_in != primary_thesis:
        return _fail(
            "thesis_mismatch_primary",
            got=thesis_key_in,
            expected=primary_thesis,
        )

    identity_thesis = normalize_identity_thesis_key(primary_thesis)
    if identity_thesis is None or identity_thesis not in ALLOWED_IDENTITY_THESIS_KEYS:
        return _fail("thesis_not_normalizable", stage1_thesis_key=primary_thesis)

    def _claim_list(key: str) -> list[str] | None:
        val = core_raw.get(key)
        if val is None:
            return []
        if not isinstance(val, list):
            return None
        out: list[str] = []
        for item in val:
            cid = str(item or "").strip()
            if not cid:
                continue
            if cid not in claim_ids:
                return None
            out.append(cid)
        return sorted(set(out))

    supporting_claim_ids = _claim_list("supporting_claim_ids")
    qualifying_claim_ids = _claim_list("qualifying_claim_ids")
    contradicting_claim_ids = _claim_list("contradicting_claim_ids")
    if supporting_claim_ids is None:
        return _fail("supporting_claim_ids_invalid")
    if qualifying_claim_ids is None:
        return _fail("qualifying_claim_ids_invalid")
    if contradicting_claim_ids is None:
        return _fail("contradicting_claim_ids_invalid")
    if primary_claim_id not in supporting_claim_ids:
        supporting_claim_ids = sorted(set(supporting_claim_ids + [primary_claim_id]))

    surface = str(core_raw.get("surface_text") or "").strip()
    if not surface:
        return _fail("surface_text_required")
    if len(surface) > 2000:
        surface = surface[:1999].rstrip() + "…"

    confidence = str(core_raw.get("confidence") or primary.get("confidence") or "medium").strip()
    if confidence not in {"high", "medium", "low"}:
        return _fail("invalid_confidence", got=confidence)

    supporting_facts = sorted(
        {
            str(fid)
            for cid in supporting_claim_ids
            for fid in (claims_by_id[cid].get("supporting_fact_ids") or [])
            if str(fid) in fact_ids
        }
    )
    if not supporting_facts:
        return _fail("supporting_facts_missing")

    # Stable identity id — surface_text never enters the fingerprint.
    claim_id = make_claim_id(
        claim_kind="identity_core",
        thesis_key=identity_thesis,
        primary_fact_ids=supporting_facts,
    )

    identity_core = {
        "claim_id": claim_id,
        "claim_kind": "identity_core",
        "thesis_key": identity_thesis,
        "surface_text": surface,
        "cascade_role": "identity_core",
        "primary_claim_id": primary_claim_id,
        "supporting_claim_ids": supporting_claim_ids,
        "supporting_fact_ids": supporting_facts,
        "contradicting_claim_ids": contradicting_claim_ids,
        "qualifying_claim_ids": qualifying_claim_ids,
        "confidence": confidence,
        "capability_floor": primary.get("capability_floor") or "date_only",
        "produced_by_stage": 2,
        "evidence_status": "grounded",
    }

    return {
        "stage": 2,
        "stage_version": STAGE2_VERSION,
        "status": "grounded",
        "identity_core": identity_core,
        "source_roles": source_roles,
        "capability": capability,
        "diagnostics": diagnostics,
        "validation": {
            "json_shape_ok": True,
            "refs_resolve": True,
            "no_invented_claims": True,
            "required_fields_ok": True,
            "thesis_matches_primary": True,
            "surface_not_in_id": True,
        },
        "generated_at": _now_iso(),
    }


def build_character_engine_identity_core_v0(
    *,
    facts_pack: dict[str, Any],
    evidence: dict[str, Any],
    locale: str = "ru",
    llm_raw: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Run Stage 2 Identity Core.

    Pass ``llm_raw`` in tests to inject a model response without calling the network.
    Without LLM config and without ``llm_raw`` → insufficient_identity_core (no invented core).
    """
    context = build_stage2_context_pack(facts_pack=facts_pack, evidence=evidence)
    prompt_version = "0"

    if llm_raw is not None:
        return validate_stage2_identity_contract(
            llm_raw,
            facts_pack=facts_pack,
            evidence=evidence,
            prompt_version="test_inject",
        )

    if not context["allowed_primary_claim_ids"]:
        return validate_stage2_identity_contract(
            {
                "status": "insufficient_identity_core",
                "identity_core": None,
                "source_roles": [],
                "selection_rationale": "no_grounded_stage1_claims",
            },
            facts_pack=facts_pack,
            evidence=evidence,
            prompt_version="n/a",
        )

    if not is_llm_chat_configured():
        logger.info("character_engine_stage2: LLM not configured — insufficient_identity_core")
        return validate_stage2_identity_contract(
            {
                "status": "insufficient_identity_core",
                "identity_core": None,
                "source_roles": [],
                "selection_rationale": "llm_not_configured",
            },
            facts_pack=facts_pack,
            evidence=evidence,
            prompt_version="n/a",
        )

    system, prompt_version = get_prompt(STAGE2_PROMPT_ID, locale=locale)
    client = get_openai_compatible_client(operation="background")
    model = resolve_default_chat_model()
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": json.dumps(context, ensure_ascii=False)},
    ]
    raw_text = chat_completion_text(
        client,
        model=model,
        messages=messages,
        temperature=0.35,
        max_tokens=900,
        json_object=True,
    )
    if not raw_text:
        # One retry — staging/live saw intermittent read timeouts → empty JSON.
        logger.info("character_engine_stage2: empty LLM text — retrying once")
        raw_text = chat_completion_text(
            client,
            model=model,
            messages=messages,
            temperature=0.2,
            max_tokens=900,
            json_object=True,
        )
    parsed = _parse_json_object(raw_text or "")
    if not parsed:
        logger.warning("character_engine_stage2: empty/invalid LLM JSON")
        return validate_stage2_identity_contract(
            {
                "status": "insufficient_identity_core",
                "identity_core": None,
                "source_roles": [],
                "selection_rationale": "llm_json_invalid",
            },
            facts_pack=facts_pack,
            evidence=evidence,
            prompt_version=prompt_version,
        )
    return validate_stage2_identity_contract(
        parsed,
        facts_pack=facts_pack,
        evidence=evidence,
        prompt_version=prompt_version,
    )

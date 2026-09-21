"""Character Engine Stage 2 — Identity Core.

PIC-K01 meaning is IL-2 role composition (`compose_k01_identity_v0`).
Code checks JSON contract + provenance: existing claim_id / fact_id refs,
no invented claims, required fields. LLM cannot overwrite a composed surface.
The 13-key registry is fallback only when sun cannot compose.
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
    llm_call_context,
    resolve_complex_chat_model,
)
from todayflow_backend.prompts.registry_v1 import get_prompt
from todayflow_backend.services.character_engine_ids_v0 import make_claim_id
from todayflow_backend.services.character_engine_identity_thesis_registry_v0 import (
    ALLOWED_IDENTITY_THESIS_KEYS,
    ALLOWED_SOURCE_ROLES,
    normalize_identity_thesis_key,
)
from todayflow_backend.services.character_engine_k01_composition_v0 import (
    compose_k01_identity_v0,
    is_k01_identity_thesis,
)

logger = logging.getLogger(__name__)

STAGE2_VERSION = "character_engine_stage2_identity_v0"
STAGE2_PROMPT_ID = "profile.character_engine.stage2.v1"
RECIPE_VERSION = "character_engine_recipe_v1"
# PIC: docs/profile/PROFILE_INFORMATION_CONTRACT_V1.md
PIC_K = ("K01", "K02")
PIC_F = ("F01", "F03", "F04", "F05", "F06", "F09")

# Editorial surface when LLM is down — Identity thesis → readable core (fill-empty, not overwrite of good LLM).
_DETERMINISTIC_SURFACE_BY_IDENTITY: dict[str, str] = {
    "builds_through_autonomy": (
        "Ты строишь жизнь через собственную систему и автономию — "
        "ясность важнее чужого темпа."
    ),
    "builds_through_analysis": (
        "Ты строишь через анализ до шага — сначала понять устройство, потом выбрать."
    ),
    "builds_through_air_mind": (
        "Ты идёшь через идеи и связи — направление собирается в уме раньше, чем в действии."
    ),
    "builds_through_earth_stability": (
        "Ты опираешься на осязаемое и прочное — устойчивость важнее скорости."
    ),
    "builds_through_water_care": (
        "Ты строишь мир через заботу и проницаемость — чужая боль входит в поле раньше границ."
    ),
    "builds_through_emotional_depth": (
        "Ты проживаешь глубже обычного — чувства заполняют поле до любого внешнего шага."
    ),
    "builds_through_earth_anchor": (
        "Ты якоришься в привычном порядке — опора даёт ритм, но может держать на месте."
    ),
    "builds_through_freedom_vs_stability": (
        "В тебе тянутся свобода и опора — характер держит это напряжение как ось."
    ),
    "builds_through_fire_drive": (
        "Ты движешься импульсом — сила в старте, риск в отсутствии выбранного направления."
    ),
    "builds_through_air_presence": (
        "Ты входишь в мир через лёгкий контакт и разговор — присутствие начинается с воздуха."
    ),
    "builds_through_fire_presence": (
        "Ты входишь прямо и с напором — первый контакт задаёт температуру поля."
    ),
    "builds_through_earth_presence": (
        "Ты показываешь плотную, надёжную форму — присутствие читается как опора."
    ),
    "builds_through_water_presence": (
        "Ты встречаешь мир через чуткую оболочку — контакт мягкий, желания часто неназванные."
    ),
}


def _confidence_rank(value: Any) -> int:
    key = str(value or "").strip().lower()
    if key == "high":
        return 0
    if key == "medium":
        return 1
    if key == "low":
        return 2
    return 3


def _pick_primary_grounded_claim(evidence: dict[str, Any]) -> dict[str, Any] | None:
    claims = evidence.get("claims") if isinstance(evidence.get("claims"), list) else []
    grounded = [
        c
        for c in claims
        if isinstance(c, dict)
        and c.get("evidence_status") == "grounded"
        and c.get("claim_id")
        and is_k01_identity_thesis(str(c.get("thesis_key") or ""))
    ]
    if not grounded:
        return None

    def _rank(claim: dict[str, Any]) -> tuple[int, int, str]:
        thesis = str(claim.get("thesis_key") or "")
        occupancy_sun = 0 if thesis.startswith("planet_in_sign:sun:") else 1
        return (occupancy_sun, _confidence_rank(claim.get("confidence")), str(claim.get("claim_id")))

    grounded.sort(key=_rank)
    return grounded[0]


def _is_occupancy_thesis(thesis: Any) -> bool:
    token = str(thesis or "")
    return token.startswith("planet_in_sign:") or token.startswith("planet_in_house:")


def _occupancy_claims(evidence: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        c
        for c in (evidence.get("claims") or [])
        if isinstance(c, dict)
        and c.get("evidence_status") == "grounded"
        and c.get("claim_id")
        and _is_occupancy_thesis(c.get("thesis_key"))
    ]


def _fill_surface_with_il_occupancy(out: dict[str, Any], evidence: dict[str, Any]) -> dict[str, Any]:
    """Occupancy claim ids stay qualifiers. Surface meaning comes from K01 composition, not a lemma dump."""
    occupancy = _occupancy_claims(evidence)
    occupancy_ids = [str(c["claim_id"]) for c in occupancy]
    roles = list(out.get("source_roles") or []) if isinstance(out.get("source_roles"), list) else []
    have = {
        str(row.get("claim_id"))
        for row in roles
        if isinstance(row, dict) and row.get("claim_id")
    }
    for cid in occupancy_ids:
        if cid not in have:
            roles.append({"claim_id": cid, "role": "qualifier"})
            have.add(cid)
    out["source_roles"] = roles
    core = out.get("identity_core") if isinstance(out.get("identity_core"), dict) else None
    if not core:
        return out
    if occupancy_ids:
        qualifying = [
            str(cid)
            for cid in (core.get("qualifying_claim_ids") or [])
            if str(cid).strip()
        ]
        for cid in occupancy_ids:
            if cid not in qualifying:
                qualifying.append(cid)
        core["qualifying_claim_ids"] = qualifying
    return out


def build_deterministic_stage2_raw_v0(
    evidence: dict[str, Any],
    *,
    facts_pack: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    """K01 from IL-2 roles. 13-key surface bank is fallback only when sun cannot compose."""
    composed = compose_k01_identity_v0(facts_pack=facts_pack or {}, evidence=evidence)
    if composed.get("status") == "grounded":
        primary_id = str(composed["primary_claim_id"])
        return {
            "status": "grounded",
            "identity_core": {
                "primary_claim_id": primary_id,
                "thesis_key": str(composed.get("thesis_key") or ""),
                "surface_text": str(composed.get("surface_text") or ""),
                "recognition_line": str(composed.get("recognition_line") or ""),
                "supporting_claim_ids": list(composed.get("supporting_claim_ids") or [primary_id]),
                "qualifying_claim_ids": list(composed.get("qualifying_claim_ids") or []),
                "contradicting_claim_ids": [],
                "confidence": "medium",
                "k01_source": composed.get("k01_source"),
                "k01_pieces": list(composed.get("pieces") or []),
            },
            "source_roles": list(composed.get("source_roles") or []),
            "selection_rationale": "k01_il2_composed_roles",
        }
    if composed.get("status") != "fallback":
        return None
    fallback_claim = composed.get("fallback_claim") if isinstance(composed.get("fallback_claim"), dict) else None
    primary = fallback_claim or _pick_primary_grounded_claim(evidence)
    if not primary:
        return None
    stage1_thesis = str(primary.get("thesis_key") or "").strip()
    identity_thesis = normalize_identity_thesis_key(stage1_thesis)
    surface = _DETERMINISTIC_SURFACE_BY_IDENTITY.get(identity_thesis or "")
    if not surface:
        return None
    primary_id = str(primary.get("claim_id"))
    occupancy_ids = [str(c["claim_id"]) for c in _occupancy_claims(evidence)]
    occupancy_set = set(occupancy_ids)
    others = [
        str(c.get("claim_id"))
        for c in (evidence.get("claims") or [])
        if isinstance(c, dict)
        and c.get("evidence_status") == "grounded"
        and str(c.get("claim_id") or "") != primary_id
        and c.get("claim_id")
        and str(c.get("claim_id")) not in occupancy_set
    ]
    return {
        "status": "grounded",
        "identity_core": {
            "primary_claim_id": primary_id,
            "thesis_key": stage1_thesis,
            "surface_text": surface,
            "supporting_claim_ids": [primary_id, *others[:2]],
            "qualifying_claim_ids": occupancy_ids or others[2:3],
            "contradicting_claim_ids": [],
            "confidence": str(primary.get("confidence") or "medium"),
            "k01_source": "fallback_13key_insufficient_il2",
            "k01_pieces": [],
        },
        "source_roles": [
            {"claim_id": primary_id, "role": "dominant_mechanism"},
            *[
                {"claim_id": cid, "role": "supporting_claim"}
                for cid in others[:2]
            ],
            *[
                {"claim_id": cid, "role": "qualifier"}
                for cid in occupancy_ids
            ],
        ],
        "selection_rationale": "fallback_13key_insufficient_il2",
    }


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
            "il_line": c.get("il_line"),
        }
        for c in claims
        if isinstance(c, dict) and c.get("evidence_status") == "grounded" and c.get("claim_id")
    ]
    identity_primaries = [
        c for c in grounded if is_k01_identity_thesis(str(c.get("thesis_key") or ""))
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
        "allowed_primary_claim_ids": [c["claim_id"] for c in identity_primaries],
        "allowed_thesis_keys": sorted(
            {str(c["thesis_key"]) for c in identity_primaries if c.get("thesis_key")}
        ),
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
    if identity_thesis is None and primary_thesis.startswith("planet_in_sign:sun:"):
        identity_thesis = primary_thesis
    if identity_thesis is None or (
        identity_thesis not in ALLOWED_IDENTITY_THESIS_KEYS
        and not identity_thesis.startswith("planet_in_sign:sun:")
    ):
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

    recognition_line = str(core_raw.get("recognition_line") or "").strip() or surface
    k01_source = str(core_raw.get("k01_source") or "").strip() or None
    k01_pieces = [
        row
        for row in (core_raw.get("k01_pieces") or [])
        if isinstance(row, dict) and row.get("role") and row.get("text")
    ]
    identity_core = {
        "claim_id": claim_id,
        "claim_kind": "identity_core",
        "thesis_key": identity_thesis,
        "surface_text": surface,
        "recognition_line": recognition_line,
        "k01_source": k01_source,
        "k01_pieces": k01_pieces,
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
    deterministic_only: bool = False,
) -> dict[str, Any]:
    """
    Run Stage 2 Identity Core.

    Pass ``llm_raw`` in tests to inject a model response without calling the network.
    Meaning SoT is IL-2 role composition (PIC-K01). LLM/13-key cannot overwrite a
    composed surface. 13-key bank is fallback only when sun cannot compose.
    ``deterministic_only=True`` skips LLM (Profile GET fill-once).
    """
    context = build_stage2_context_pack(facts_pack=facts_pack, evidence=evidence)
    prompt_version = "0"

    def _apply_k01_meaning(out: dict[str, Any]) -> dict[str, Any]:
        if str(out.get("status") or "") != "grounded":
            return out
        core = out.get("identity_core") if isinstance(out.get("identity_core"), dict) else None
        if not core:
            return out
        composed = compose_k01_identity_v0(facts_pack=facts_pack, evidence=evidence)
        if composed.get("k01_source") != "il2_composed_roles":
            core.setdefault("k01_source", composed.get("k01_source") or "fallback_13key_insufficient_il2")
            return out
        core["surface_text"] = str(composed.get("surface_text") or core.get("surface_text") or "")
        core["recognition_line"] = str(composed.get("recognition_line") or core["surface_text"])
        core["k01_source"] = "il2_composed_roles"
        core["k01_pieces"] = list(composed.get("pieces") or [])
        return out

    def _done(out: dict[str, Any]) -> dict[str, Any]:
        return _apply_k01_meaning(_fill_surface_with_il_occupancy(out, evidence))

    if llm_raw is not None:
        return _done(
            validate_stage2_identity_contract(
                llm_raw,
                facts_pack=facts_pack,
                evidence=evidence,
                prompt_version="test_inject",
            )
        )

    if not context["allowed_primary_claim_ids"]:
        return _done(
            validate_stage2_identity_contract(
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
        )

    def _deterministic(*, reason: str, prompt_ver: str) -> dict[str, Any]:
        raw = build_deterministic_stage2_raw_v0(evidence, facts_pack=facts_pack)
        if raw is None:
            return _done(
                validate_stage2_identity_contract(
                    {
                        "status": "insufficient_identity_core",
                        "identity_core": None,
                        "source_roles": [],
                        "selection_rationale": reason,
                    },
                    facts_pack=facts_pack,
                    evidence=evidence,
                    prompt_version=prompt_ver,
                )
            )
        logger.warning(
            "character_engine_stage2: using deterministic Identity Core (%s)",
            reason,
        )
        out = validate_stage2_identity_contract(
            raw,
            facts_pack=facts_pack,
            evidence=evidence,
            prompt_version=prompt_ver,
        )
        if isinstance(out.get("validation"), dict):
            out["validation"] = {
                **out["validation"],
                "deterministic_fallback": True,
                "fallback_reason": reason,
            }
        return _done(out)

    if deterministic_only or not is_llm_chat_configured():
        reason = "deterministic_only_read_path" if deterministic_only else "llm_not_configured"
        if not deterministic_only:
            logger.info("character_engine_stage2: LLM not configured — deterministic fallback")
        return _deterministic(reason=reason, prompt_ver="n/a")

    system, prompt_version = get_prompt(STAGE2_PROMPT_ID, locale=locale)
    from todayflow_backend.services.llm_practitioner_persona_v1 import with_practitioner_persona

    system = with_practitioner_persona(system, locale=locale)
    client = get_openai_compatible_client(operation="background", model=resolve_complex_chat_model())
    model = resolve_complex_chat_model()
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": json.dumps(context, ensure_ascii=False)},
    ]
    with llm_call_context(feature="ce.stage2", ensure_operation=True, operation="ce.stage2"):
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
            with llm_call_context(attempt=1, retry_reason="empty_content"):
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
        logger.warning("character_engine_stage2: empty/invalid LLM JSON — deterministic fallback")
        return _deterministic(reason="llm_json_invalid", prompt_ver=prompt_version)
    return _done(
        validate_stage2_identity_contract(
            parsed,
            facts_pack=facts_pack,
            evidence=evidence,
            prompt_version=prompt_version,
        )
    )

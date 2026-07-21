"""Context Builder v0 — question_id + foundations → ContextPack.

Cue rendering reuses life_spheres_cues_v0 (no duplicate tables).
"""

from __future__ import annotations

from typing import Any

from todayflow_backend.context_engine_v0.fingerprint_v0 import context_pack_fingerprint
from todayflow_backend.context_engine_v0.question_registry_v0 import (
    QUESTION_REGISTRY_VERSION,
    get_question_spec,
    question_id_for_sphere,
)
from todayflow_backend.context_engine_v0.types_v0 import (
    CONTEXT_ENGINE_VERSION,
    CONTEXT_PACK_CONTRACT,
    ContextPack,
    Cue,
)
from todayflow_backend.services.life_spheres_cues_v0 import build_sphere_cues
from todayflow_backend.services.life_spheres_projector_v0 import spheres_projection_allowed


def _cue(cid: str, text: str, fact_ids: list[str]) -> Cue:
    return {"id": cid, "text": text, "fact_ids": fact_ids}


def _fact_ids_from_cue_id(cue_id: str, style_fact_id: str) -> list[str]:
    """Map cue:/house:/trait: ids onto registry-ish fact ids."""
    out: list[str] = [style_fact_id, "profile.identity.core"]
    cid = str(cue_id or "")
    if cid.startswith("cue:"):
        # cue:love.venus.cancer.0 → natal.venus.sign
        parts = cid.split(".")
        if len(parts) >= 3:
            planet = parts[1]
            sign = parts[2]
            out.append(f"natal.{planet}.sign")
            out.append(f"natal.{planet}.{sign}")
    elif cid.startswith("house:"):
        n = cid.split(":", 1)[-1]
        out.append(f"natal.house.{n}")
    elif cid.startswith("trait:"):
        out.append(cid.replace("trait:", "natal.trait."))
    return out


def build_context_pack_v0(
    question_id: str,
    foundations: dict[str, Any],
) -> dict[str, Any]:
    """Return ContextPack-like dict. ok=False when ineligible or cues empty."""
    spec = get_question_spec(question_id)
    if not spec:
        return {
            "ok": False,
            "reason": "unknown_question",
            "question_id": question_id,
            "contract_version": CONTEXT_PACK_CONTRACT,
            "context_version": CONTEXT_ENGINE_VERSION,
        }

    if not spheres_projection_allowed(foundations):
        return {
            "ok": False,
            "reason": "foundations_gate_ineligible",
            "question_id": question_id,
            "contract_version": CONTEXT_PACK_CONTRACT,
            "context_version": CONTEXT_ENGINE_VERSION,
            "omitted_facts": [{"id": "*", "reason": "spheres_projection_gate_ineligible"}],
        }

    sphere_id = str(spec.get("sphere_id") or "")
    raw = build_sphere_cues(sphere_id, foundations)
    if not raw.get("ok"):
        return {
            "ok": False,
            "reason": str(raw.get("reason") or "cues_empty"),
            "question_id": question_id,
            "sphere_id": sphere_id,
            "contract_version": CONTEXT_PACK_CONTRACT,
            "context_version": CONTEXT_ENGINE_VERSION,
            "kitchen": raw.get("kitchen"),
        }

    style_fact_id = str(spec.get("style_fact_id") or "")
    cues: list[Cue] = []
    fact_ids: list[str] = []
    for c in raw.get("sphere_cues") or []:
        if not isinstance(c, dict):
            continue
        text = str(c.get("text") or "").strip()
        cid = str(c.get("id") or "")
        if not text:
            continue
        fids = _fact_ids_from_cue_id(cid, style_fact_id)
        cues.append(_cue(cid, text, fids))
        fact_ids.extend(fids)

    house_cues: list[Cue] = []
    for c in raw.get("house_cues") or []:
        if not isinstance(c, dict):
            continue
        text = str(c.get("text") or "").strip()
        cid = str(c.get("id") or "")
        if not text:
            continue
        fids = _fact_ids_from_cue_id(cid, style_fact_id)
        house_cues.append(_cue(cid, text, fids))
        fact_ids.extend(fids)

    # Dedupe fact ids preserving order
    seen: set[str] = set()
    uniq_facts: list[str] = []
    for fid in fact_ids:
        if fid not in seen:
            seen.add(fid)
            uniq_facts.append(fid)

    omitted: list[dict[str, str]] = []
    natal = foundations.get("natal") if isinstance(foundations.get("natal"), dict) else {}
    if not natal.get("houses_available"):
        for n in spec.get("house_numbers") or []:
            omitted.append({"id": f"natal.house.{n}", "reason": "houses_unavailable"})

    pack: ContextPack = {
        "contract_version": CONTEXT_PACK_CONTRACT,
        "question_id": question_id,
        "domain": str(spec.get("domain") or ""),
        "sphere_id": sphere_id,
        "locale": str(raw.get("locale") or foundations.get("locale") or "ru"),
        "user_question": str(spec.get("user_question") or raw.get("user_question") or ""),
        "user_value": str(spec.get("user_value") or raw.get("user_value") or ""),
        "identity_core": str(raw.get("identity_core") or ""),
        "strengths": list(raw.get("strengths") or []),
        "growth_zones": list(raw.get("growth_zones") or []),
        "relevant_style": str(raw.get("relevant_style") or ""),
        "cues": cues,
        "house_cues": house_cues,
        "fact_ids": uniq_facts,
        "omitted_facts": omitted,
        "context_version": CONTEXT_ENGINE_VERSION,
        "kitchen": {
            **(raw.get("kitchen") if isinstance(raw.get("kitchen"), dict) else {}),
            "question_registry_version": QUESTION_REGISTRY_VERSION,
            "cue_source_module": "life_spheres_cues_v0",
        },
    }
    pack["fingerprint"] = context_pack_fingerprint(dict(pack))
    return {"ok": True, **pack}


def build_context_pack_for_sphere(
    sphere_id: str,
    foundations: dict[str, Any],
) -> dict[str, Any]:
    qid = question_id_for_sphere(sphere_id)
    if not qid:
        return {
            "ok": False,
            "reason": "unknown_sphere",
            "sphere_id": sphere_id,
            "contract_version": CONTEXT_PACK_CONTRACT,
            "context_version": CONTEXT_ENGINE_VERSION,
        }
    return build_context_pack_v0(qid, foundations)


def context_pack_to_synthesis_input(pack: dict[str, Any]) -> dict[str, Any]:
    """Adapt ContextPack → shape expected by profile_spheres_synthesis_v1 formatters."""
    cues = pack.get("cues") if isinstance(pack.get("cues"), list) else []
    houses = pack.get("house_cues") if isinstance(pack.get("house_cues"), list) else []
    return {
        "ok": bool(pack.get("ok")),
        "sphere_id": pack.get("sphere_id"),
        "sphere_name": {
            "love": "Любовь",
            "money": "Деньги",
            "decisions": "Решения",
        }.get(str(pack.get("sphere_id") or ""), str(pack.get("domain") or "")),
        "user_question": pack.get("user_question"),
        "user_value": pack.get("user_value"),
        "identity_core": pack.get("identity_core"),
        "strengths": pack.get("strengths") or [],
        "growth_zones": pack.get("growth_zones") or [],
        "relevant_style": pack.get("relevant_style"),
        "sphere_cues": [{"id": c.get("id"), "text": c.get("text")} for c in cues if isinstance(c, dict)],
        "house_cues": [{"id": c.get("id"), "text": c.get("text")} for c in houses if isinstance(c, dict)],
        "locale": pack.get("locale") or "ru",
        "kitchen": {
            **(pack.get("kitchen") if isinstance(pack.get("kitchen"), dict) else {}),
            "question_id": pack.get("question_id"),
            "fact_ids": pack.get("fact_ids") or [],
            "context_fingerprint": pack.get("fingerprint"),
            "context_version": pack.get("context_version"),
            "omitted_facts": pack.get("omitted_facts") or [],
        },
    }

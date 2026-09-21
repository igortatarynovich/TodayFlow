"""PIC-K01 Identity Core composition from allowed facts.

F01–F04 (+ F05 full, F09 contribution) → IL-2 roles → one observable mechanism.
Occupancy (F03/F06) qualifies; it does not replace the mechanism.
The 13-key registry is not meaning SoT — fallback only when IL-2 sun cannot compose.
Not IL-3 rank. Not IL-4 voice. Not a traits list. Not K03 applied how/do.

SoT: docs/profile/PROFILE_INFORMATION_CONTRACT_V1.md
"""

from __future__ import annotations

from typing import Any

from todayflow_backend.data.number_base_v1 import get_number_base
from todayflow_backend.knowledge.il2_composition_v1 import (
    compose_planet_in_house,
    compose_planet_in_sign,
    load_objects,
)
from todayflow_backend.services.character_engine_identity_thesis_registry_v0 import (
    STAGE1_TO_IDENTITY_THESIS,
    normalize_identity_thesis_key,
)
from todayflow_backend.services.prose_clip_v1 import clip_prose

# PIC: docs/profile/PROFILE_INFORMATION_CONTRACT_V1.md
PIC_K = ("K01",)
PIC_F = ("F01", "F03", "F04", "F05", "F06", "F09")

_RECOG_MAX = 220
_CORE_MAX = 480
_QUALIFIER_RANK = ("mars", "mercury", "venus", "jupiter", "saturn")


def _clip(text: str, limit: int) -> str:
    return clip_prose(" ".join(str(text or "").split()).strip(), limit)


def _lemmas(frame: Any, job_name: str, *, limit: int = 2) -> list[str]:
    payload = frame.jobs.get(job_name) if frame is not None else None
    if payload is None:
        return []
    out: list[str] = []
    for lemma in payload.lemmas:
        token = str(lemma).strip()
        if token:
            out.append(token)
        if len(out) >= limit:
            break
    return out


def _object_lemmas(catalog: dict[str, Any], object_id: str, slot: str, *, limit: int = 2) -> list[str]:
    obj = catalog.get(object_id)
    if not isinstance(obj, dict):
        return []
    canon = obj.get("canon") if isinstance(obj.get("canon"), dict) else {}
    raw = canon.get(slot)
    if not isinstance(raw, list):
        return []
    out: list[str] = []
    for item in raw:
        token = str(item).strip()
        if token:
            out.append(token)
        if len(out) >= limit:
            break
    return out


def _grounded_claims(evidence: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        c
        for c in (evidence.get("claims") or [])
        if isinstance(c, dict) and c.get("evidence_status") == "grounded" and c.get("claim_id")
    ]


def _claim_starting(evidence: dict[str, Any], prefix: str) -> dict[str, Any] | None:
    for claim in _grounded_claims(evidence):
        if str(claim.get("thesis_key") or "").startswith(prefix):
            return claim
    return None


def _fact(facts_pack: dict[str, Any], fact_type: str) -> dict[str, Any] | None:
    for row in facts_pack.get("raw_facts") or []:
        if isinstance(row, dict) and str(row.get("fact_type") or "") == fact_type:
            return row
    return None


def _sign_of(row: dict[str, Any] | None) -> str | None:
    if not row:
        return None
    value = row.get("value")
    if isinstance(value, dict):
        token = str(value.get("sign") or "").strip().lower()
        return token or None
    token = str(value or "").strip().lower()
    return token or None


def _natal_full(facts_pack: dict[str, Any]) -> bool:
    capability = facts_pack.get("capability") if isinstance(facts_pack.get("capability"), dict) else {}
    return str(capability.get("natal_mode") or "").strip().lower() == "full"


def _piece(
    *,
    role: str,
    text: str,
    lemmas: list[str],
    claim_id: str | None = None,
    fact_ids: list[str] | None = None,
    fact_types: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "role": role,
        "text": text,
        "lemmas": list(lemmas),
        "claim_id": claim_id,
        "fact_ids": [fid for fid in (fact_ids or []) if fid],
        "fact_types": list(fact_types or []),
    }


def _pick_thirteen_key_claim(evidence: dict[str, Any]) -> dict[str, Any] | None:
    grounded = [
        c
        for c in _grounded_claims(evidence)
        if str(c.get("thesis_key") or "") in STAGE1_TO_IDENTITY_THESIS
    ]
    if not grounded:
        return None
    grounded.sort(key=lambda c: str(c.get("claim_id")))
    return grounded[0]


def compose_k01_identity_v0(
    *,
    facts_pack: dict[str, Any],
    evidence: dict[str, Any],
) -> dict[str, Any]:
    """Grounded K01 pack, or omit/fallback. Does not invent personality essays."""
    catalog = load_objects()
    pieces: list[dict[str, Any]] = []
    sun_claim = _claim_starting(evidence, "planet_in_sign:sun:")
    sun_fact = _fact(facts_pack, "planet_sign:sun")
    sun_sign = _sign_of(sun_fact)
    mechanism_text = ""
    if sun_sign:
        frame = compose_planet_in_sign(catalog, "astro.object.sun", f"astro.sign.{sun_sign}")
        what = _lemmas(frame, "what", limit=1)
        how = _lemmas(frame, "how", limit=2)
        if frame.status == "composed" and what and how:
            mechanism_text = f"Ты {what[0]} через {', '.join(how)}."
            pieces.append(
                _piece(
                    role="mechanism",
                    text=mechanism_text,
                    lemmas=what + how,
                    claim_id=str(sun_claim["claim_id"]) if sun_claim else None,
                    fact_ids=[str(sun_fact.get("fact_id") or "")] if sun_fact else None,
                    fact_types=["planet_sign:sun"],
                )
            )

    if not mechanism_text:
        fallback_claim = _pick_thirteen_key_claim(evidence)
        if not fallback_claim:
            return {
                "status": "insufficient",
                "k01_source": "omitted_no_grounded_atom",
                "pieces": [],
            }
        return {
            "status": "fallback",
            "k01_source": "fallback_13key_insufficient_il2",
            "primary_claim_id": str(fallback_claim["claim_id"]),
            "thesis_key": str(fallback_claim.get("thesis_key") or ""),
            "pieces": [],
            "fallback_claim": fallback_claim,
        }

    moon_claim = _claim_starting(evidence, "planet_in_sign:moon:")
    moon_fact = _fact(facts_pack, "planet_sign:moon")
    moon_sign = _sign_of(moon_fact)
    hold_text = ""
    if moon_sign:
        frame = compose_planet_in_sign(catalog, "astro.object.moon", f"astro.sign.{moon_sign}")
        how = _lemmas(frame, "how", limit=2)
        if frame.status == "composed" and how:
            hold_text = f"Держишь это {', '.join(how)}."
            pieces.append(
                _piece(
                    role="hold",
                    text=hold_text,
                    lemmas=how,
                    claim_id=str(moon_claim["claim_id"]) if moon_claim else None,
                    fact_ids=[str(moon_fact.get("fact_id") or "")] if moon_fact else None,
                    fact_types=["planet_sign:moon"],
                )
            )

    doorway_text = ""
    if _natal_full(facts_pack):
        asc_fact = _fact(facts_pack, "angle_sign:ascendant")
        asc_sign = _sign_of(asc_fact)
        if asc_sign:
            orientation = _object_lemmas(catalog, "astro.object.asc", "orientation", limit=1)
            manner = _object_lemmas(catalog, f"astro.sign.{asc_sign}", "manner", limit=2)
            if orientation and manner:
                doorway_text = f"Встречаешь мир: {orientation[0]} — {', '.join(manner)}."
                pieces.append(
                    _piece(
                        role="doorway",
                        text=doorway_text,
                        lemmas=orientation + manner,
                        fact_ids=[str(asc_fact.get("fact_id") or "")] if asc_fact else None,
                        fact_types=["angle_sign:ascendant"],
                    )
                )

    qualifier_text = ""
    qualifier_claim: dict[str, Any] | None = None
    for body in _QUALIFIER_RANK:
        house_claim = _claim_starting(evidence, f"planet_in_house:{body}:") if _natal_full(facts_pack) else None
        sign_claim = _claim_starting(evidence, f"planet_in_sign:{body}:")
        chosen = house_claim or sign_claim
        if not chosen:
            continue
        thesis = str(chosen.get("thesis_key") or "")
        body_fact = _fact(facts_pack, f"planet_sign:{body}")
        if house_claim and thesis.startswith("planet_in_house:"):
            house_id = thesis.rsplit(":", 1)[-1]
            frame = compose_planet_in_house(
                catalog, f"astro.object.{body}", f"astro.house.{house_id}"
            )
            what = _lemmas(frame, "what", limit=1)
            where = _lemmas(frame, "where", limit=2)
            if frame.status == "composed" and what and where:
                qualifier_text = f"{what[0]} — {', '.join(where)}."
                qualifier_claim = house_claim
                pieces.append(
                    _piece(
                        role="qualifier",
                        text=qualifier_text,
                        lemmas=what + where,
                        claim_id=str(house_claim["claim_id"]),
                        fact_ids=[str(body_fact.get("fact_id") or "")] if body_fact else None,
                        fact_types=[f"planet_sign:{body}"],
                    )
                )
                break
        if sign_claim:
            sign = _sign_of(body_fact)
            if not sign:
                continue
            frame = compose_planet_in_sign(catalog, f"astro.object.{body}", f"astro.sign.{sign}")
            what = _lemmas(frame, "what", limit=1)
            how = _lemmas(frame, "how", limit=2)
            if frame.status == "composed" and what and how:
                qualifier_text = f"{what[0]} через {', '.join(how)}."
                qualifier_claim = sign_claim
                pieces.append(
                    _piece(
                        role="qualifier",
                        text=qualifier_text,
                        lemmas=what + how,
                        claim_id=str(sign_claim["claim_id"]),
                        fact_ids=[str(body_fact.get("fact_id") or "")] if body_fact else None,
                        fact_types=[f"planet_sign:{body}"],
                    )
                )
                break

    contribution_text = ""
    lp_fact = _fact(facts_pack, "life_path_number")
    lp_value = None
    if lp_fact is not None:
        try:
            lp_value = int(lp_fact.get("value"))
        except (TypeError, ValueError):
            lp_value = None
    if lp_value is not None:
        row = get_number_base(lp_value)
        keywords = [str(k).strip() for k in (row.get("keywords") or []) if str(k).strip()] if row else []
        if keywords:
            contribution_text = f"Вклад пути: {keywords[0]}."
            pieces.append(
                _piece(
                    role="contribution",
                    text=contribution_text,
                    lemmas=keywords[:1],
                    fact_ids=[str(lp_fact.get("fact_id") or "")] if lp_fact else None,
                    fact_types=["life_path_number"],
                )
            )

    recognition = _clip(" ".join(part for part in (mechanism_text, hold_text, doorway_text) if part), _RECOG_MAX)
    surface = _clip(
        " ".join(part for part in (recognition, qualifier_text, contribution_text) if part),
        _CORE_MAX,
    )
    if not recognition:
        return {
            "status": "insufficient",
            "k01_source": "omitted_no_grounded_atom",
            "pieces": pieces,
        }

    primary = sun_claim or _pick_thirteen_key_claim(evidence)
    if not primary:
        return {
            "status": "insufficient",
            "k01_source": "omitted_no_grounded_atom",
            "pieces": pieces,
        }

    occupancy_ids = [
        str(c["claim_id"])
        for c in _grounded_claims(evidence)
        if str(c.get("thesis_key") or "").startswith(("planet_in_sign:", "planet_in_house:"))
        and str(c["claim_id"]) != str(primary["claim_id"])
    ]
    moon_id = str(moon_claim["claim_id"]) if moon_claim else None
    supporting = [str(primary["claim_id"])]
    if moon_id and moon_id not in supporting:
        supporting.append(moon_id)
    qualifying = []
    if qualifier_claim:
        qualifying.append(str(qualifier_claim["claim_id"]))
    for cid in occupancy_ids:
        if cid not in supporting and cid not in qualifying:
            qualifying.append(cid)
        if len(qualifying) >= 8:
            break

    source_roles = [{"claim_id": str(primary["claim_id"]), "role": "dominant_mechanism"}]
    if moon_id:
        source_roles.append({"claim_id": moon_id, "role": "supporting_claim"})
    for cid in qualifying:
        source_roles.append({"claim_id": cid, "role": "qualifier"})

    return {
        "status": "grounded",
        "k01_source": "il2_composed_roles",
        "recognition_line": recognition,
        "surface_text": surface,
        "pieces": pieces,
        "primary_claim_id": str(primary["claim_id"]),
        "thesis_key": str(primary.get("thesis_key") or ""),
        "supporting_claim_ids": supporting,
        "qualifying_claim_ids": qualifying,
        "source_roles": source_roles,
        "identity_thesis": str(primary.get("thesis_key") or ""),
    }


def is_k01_identity_thesis(key: str) -> bool:
    token = str(key or "").strip()
    if token in STAGE1_TO_IDENTITY_THESIS or normalize_identity_thesis_key(token):
        return True
    return token.startswith("planet_in_sign:sun:")

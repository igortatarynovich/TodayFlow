"""Phase C3.3b — Pairwise production eval for personalization depth.

Same day facts × (profile A, profile B, no-profile control).
Scores structural divergence, evidence isolation, depth honesty.
Does not call Nebius — fixtures / captured scenarios only.

Canon: docs/audits/DAY_SCENARIO_SPHERE_SELECTION_C33B.md
"""

from __future__ import annotations

from typing import Any

from todayflow_backend.services.day_scenario_personalization_c33 import (
    DEPTH_DEEP,
    DEPTH_GENERAL,
    DEPTH_LIGHT,
    _PERSONAL_CLAIM_RE,
    _as_dict,
    _as_list,
    _clip,
    _public_blobs,
    _structural_fingerprint,
    count_structural_personalization_dimensions,
    pack_allowed_refs,
    run_personalization_gate_c33,
)
from todayflow_backend.services.day_scenario_sphere_selection_c33b import (
    build_sphere_selection_c33b,
    run_sphere_selection_gate_c33b,
)

EVAL_CONTRACT = "day_scenario_pairwise_eval_c33b"


def _scene_spheres(native: dict[str, Any]) -> list[str]:
    return [str(s.get("sphere") or "") for s in _as_list(native.get("scenes")) if isinstance(s, dict)]


def _habitual(native: dict[str, Any]) -> str:
    c = _as_dict(native.get("conflict"))
    tr = _as_dict(c.get("personalization"))
    return str(tr.get("habitual_force") or "")


def _actions(native: dict[str, Any]) -> list[str]:
    return [
        _clip(s.get("recommended_action"), 120)
        for s in _as_list(native.get("scenes"))
        if isinstance(s, dict)
    ]


def _traps(native: dict[str, Any]) -> list[str]:
    return [
        _clip(s.get("trap"), 120)
        for s in _as_list(native.get("scenes"))
        if isinstance(s, dict)
    ]


def _personal_refs_used(native: dict[str, Any]) -> set[str]:
    refs: set[str] = set()
    c = _as_dict(native.get("conflict"))
    refs.update(str(x) for x in _as_list(_as_dict(c.get("personalization")).get("personalization_evidence_refs")))
    for s in _as_list(native.get("scenes")):
        if isinstance(s, dict):
            refs.update(
                str(x)
                for x in _as_list(_as_dict(s.get("personalization")).get("personalization_evidence_refs"))
            )
    for row in _as_list(_as_dict(native.get("interpretive_chorus")).get("natal")):
        if isinstance(row, dict):
            refs.update(str(x) for x in _as_list(row.get("evidence_refs")))
    return {r for r in refs if r.startswith("claim.personal") or "natal." in r}


def structural_diff_dimensions(a: dict[str, Any], b: dict[str, Any]) -> list[str]:
    """Which structural axes differ between two scenarios."""
    dims: list[str] = []
    if _scene_spheres(a) != _scene_spheres(b):
        dims.append("spheres")
    if _as_dict(a.get("conflict")).get("force_a") != _as_dict(b.get("conflict")).get("force_a") or _as_dict(
        a.get("conflict")
    ).get("force_b") != _as_dict(b.get("conflict")).get("force_b"):
        dims.append("forces")
    if _habitual(a) != _habitual(b):
        dims.append("habitual_force")
    if _traps(a) != _traps(b):
        dims.append("traps")
    if _actions(a) != _actions(b):
        dims.append("actions")
    return dims


def score_single_profile(
    *,
    label: str,
    native: dict[str, Any],
    pack: dict[str, Any],
) -> dict[str, Any]:
    """Score one profile scenario against its pack."""
    depth = str(pack.get("evidence_depth") or DEPTH_GENERAL)
    declared = str(native.get("personalization_depth") or _as_dict(native.get("personalization")).get("depth") or "")
    pers_defects = run_personalization_gate_c33(native, pack)
    sphere_defects = run_sphere_selection_gate_c33b(native, pack)
    public = _public_blobs(native)
    personal_claims = bool(_PERSONAL_CLAIM_RE.search(public))
    dims = count_structural_personalization_dimensions(native)
    used = _personal_refs_used(native)
    allowed = pack_allowed_refs(pack)
    orphans = sorted(r for r in used if allowed and r not in allowed and r.startswith("claim.personal"))

    checks = {
        "depth_matches_pack": declared in {"", depth} or (depth == DEPTH_GENERAL and declared == DEPTH_GENERAL),
        "no_personal_claims_when_general": not (depth == DEPTH_GENERAL and personal_claims),
        "deep_has_two_structural_dims": depth != DEPTH_DEEP or dims >= 2,
        "no_evidence_orphans": not orphans,
        "gate_clean": not pers_defects and not sphere_defects,
    }
    score = sum(1 for v in checks.values() if v) / max(1, len(checks))
    return {
        "label": label,
        "evidence_depth": depth,
        "declared_depth": declared or depth,
        "structural_personalization_dims": dims,
        "spheres": _scene_spheres(native),
        "habitual_force": _habitual(native),
        "checks": checks,
        "score": round(score, 3),
        "pers_defect_codes": sorted({str(d.get("code")) for d in pers_defects}),
        "sphere_defect_codes": sorted({str(d.get("code")) for d in sphere_defects}),
        "orphan_refs": orphans,
        "fingerprint": _structural_fingerprint(native),
    }


def run_pairwise_eval_c33b(
    *,
    shared_day: dict[str, Any],
    control: dict[str, Any],
    profile_a: dict[str, Any],
    profile_b: dict[str, Any],
    pack_control: dict[str, Any],
    pack_a: dict[str, Any],
    pack_b: dict[str, Any],
) -> dict[str, Any]:
    """Compare three scenarios for the same day facts.

    shared_day: metadata only (date, location, card, number) — for report.
    """
    # Ensure sphere_selection on packs
    for pack, key in (
        (pack_control, "control"),
        (pack_a, "a"),
        (pack_b, "b"),
    ):
        if "sphere_selection" not in _as_dict(pack):
            pack["sphere_selection"] = build_sphere_selection_c33b(
                pack,
                day_domains=_as_list(shared_day.get("day_domains")),
                ritual_head_topic=str(shared_day.get("ritual_head_topic") or "") or None,
                thesis_family=str(shared_day.get("thesis_family") or "") or None,
            )

    sc_control = score_single_profile(label="control", native=control, pack=pack_control)
    sc_a = score_single_profile(label="profile_a", native=profile_a, pack=pack_a)
    sc_b = score_single_profile(label="profile_b", native=profile_b, pack=pack_b)

    diff_ab = structural_diff_dimensions(profile_a, profile_b)
    refs_a = _personal_refs_used(profile_a)
    refs_b = _personal_refs_used(profile_b)
    cross = sorted(refs_a & refs_b)

    pairwise_checks = {
        "control_is_general": str(pack_control.get("evidence_depth")) == DEPTH_GENERAL
        and sc_control["checks"]["no_personal_claims_when_general"],
        "a_and_b_differ_structurally": len(diff_ab) >= 2,
        "no_cross_profile_evidence": not cross,
        "depths_match_evidence": (
            str(pack_a.get("evidence_depth")) in {DEPTH_LIGHT, DEPTH_DEEP}
            and str(pack_b.get("evidence_depth")) in {DEPTH_LIGHT, DEPTH_DEEP}
        )
        or (
            # allow both deep
            str(pack_a.get("evidence_depth")) == str(pack_b.get("evidence_depth"))
        ),
        "sphere_selections_differ_when_deep": (
            str(pack_a.get("evidence_depth")) != DEPTH_DEEP
            or str(pack_b.get("evidence_depth")) != DEPTH_DEEP
            or set(_as_list(_as_dict(pack_a.get("sphere_selection")).get("primary_candidates")))
            != set(_as_list(_as_dict(pack_b.get("sphere_selection")).get("primary_candidates")))
            or "spheres" in diff_ab
        ),
        "each_profile_gate_clean": sc_a["checks"]["gate_clean"] and sc_b["checks"]["gate_clean"],
    }
    pair_score = sum(1 for v in pairwise_checks.values() if v) / max(1, len(pairwise_checks))

    return {
        "contract_version": EVAL_CONTRACT,
        "shared_day": {
            "date": shared_day.get("date"),
            "location": shared_day.get("location"),
            "card": shared_day.get("card"),
            "number": shared_day.get("number"),
            "thesis_family": shared_day.get("thesis_family"),
        },
        "profiles": {
            "control": sc_control,
            "profile_a": sc_a,
            "profile_b": sc_b,
        },
        "diff_ab_dimensions": diff_ab,
        "cross_profile_refs": cross,
        "pairwise_checks": pairwise_checks,
        "pairwise_score": round(pair_score, 3),
        "pass": pair_score >= 0.8 and sc_control["score"] >= 0.8,
    }

"""Phase C3.3b — Justified sphere selection from personalization evidence + day facts.

Does **not** rank every life sphere every day. Builds a short candidate list with
reasons and evidence_refs for the LLM and the personalization gate.

Canon: docs/audits/DAY_SCENARIO_SPHERE_SELECTION_C33B.md
"""

from __future__ import annotations

from typing import Any

from todayflow_backend.services.day_scenario_personalization_c33 import (
    DEPTH_DEEP,
    DEPTH_GENERAL,
    DEPTH_LIGHT,
    _as_dict,
    _as_list,
    _clip,
)
from todayflow_backend.services.day_scenario_v1 import (
    PRODUCT_SPHERE_IDS,
    WIRE_DOMAIN_TO_SPHERES,
    _FAMILY_SPHERES,
    _SPHERE_LABEL_RU,
)

CONTRACT_VERSION = "day_scenario_sphere_selection_c33b"

# Tendency → preferred spheres (personal baseline, not a second forecast)
TENDENCY_SPHERES: dict[str, tuple[str, ...]] = {
    "smooth_conflict": ("relationships", "communication"),
    "over_control": ("work_decisions", "relationships"),
    "rejection_sensitivity": ("relationships", "communication"),
    "direct_action": ("work_decisions", "communication"),
    "need_processing_time": ("communication", "work_decisions"),
    "responsibility_overload": ("work_decisions", "home"),
    "high_social_responsiveness": ("relationships", "communication"),
}

DEFECT_SPHERE_OUTSIDE_PACK = "PERSONALIZATION_SPHERE_OUTSIDE_PACK"
DEFECT_SPHERE_CROSS_PROFILE = "PERSONALIZATION_SPHERE_CROSS_PROFILE"
DEFECT_SPHERE_SELECTION_EMPTY = "PERSONALIZATION_SPHERE_SELECTION_EMPTY"


def _add_ranked(
    ordered: list[dict[str, Any]],
    seen: set[str],
    *,
    sphere: str,
    reason: str,
    evidence_refs: list[str],
    source: str,
    weight: float,
) -> None:
    if sphere not in PRODUCT_SPHERE_IDS or sphere in seen:
        return
    seen.add(sphere)
    ordered.append(
        {
            "sphere": sphere,
            "label_ru": _SPHERE_LABEL_RU.get(sphere, sphere),
            "reason": _clip(reason, 180),
            "evidence_refs": [str(x) for x in evidence_refs if str(x).strip()][:6],
            "source": source,
            "weight": round(weight, 3),
        }
    )


def build_sphere_selection_c33b(
    pack: dict[str, Any] | None,
    *,
    day_domains: list[str] | None = None,
    ritual_head_topic: str | None = None,
    thesis_family: str | None = None,
    max_spheres: int = 4,
) -> dict[str, Any]:
    """Rank a short sphere candidate list for today + this person.

    general → day/family only.
    light → day + at most one personal sensitive domain boost.
    deep → tendencies + sensitive_domains can reorder; still capped.
    """
    p = _as_dict(pack)
    depth = str(p.get("evidence_depth") or DEPTH_GENERAL)
    domains = [str(d) for d in (day_domains or []) if str(d).strip()]
    family = str(thesis_family or "momentum").strip() or "momentum"
    head = str(ritual_head_topic or "").strip()

    ranked: list[dict[str, Any]] = []
    seen: set[str] = set()

    # 1) Day domains / ritual head (shared across profiles for same day)
    for domain in domains:
        for sid in WIRE_DOMAIN_TO_SPHERES.get(domain, ()):
            _add_ranked(
                ranked,
                seen,
                sphere=sid,
                reason=f"day domain «{domain}»",
                evidence_refs=[f"domain.{domain}"],
                source="day",
                weight=0.9,
            )
    if head in PRODUCT_SPHERE_IDS:
        _add_ranked(
            ranked,
            seen,
            sphere=head,
            reason="ritual head_topic",
            evidence_refs=["ritual.head_topic"],
            source="day",
            weight=0.85,
        )
    elif head in WIRE_DOMAIN_TO_SPHERES:
        for sid in WIRE_DOMAIN_TO_SPHERES[head]:
            _add_ranked(
                ranked,
                seen,
                sphere=sid,
                reason=f"ritual head domain «{head}»",
                evidence_refs=["ritual.head_topic"],
                source="day",
                weight=0.85,
            )

    # 2) Personal sensitive domains / tendencies (depth-gated)
    if depth in {DEPTH_LIGHT, DEPTH_DEEP}:
        for sid in _as_list(p.get("sensitive_domains")):
            sphere = str(sid).strip()
            if sphere not in PRODUCT_SPHERE_IDS:
                continue
            refs = list(p.get("evidence_refs") or [])[:4]
            _add_ranked(
                ranked,
                seen,
                sphere=sphere,
                reason="personal sensitive domain",
                evidence_refs=refs,
                source="personal",
                weight=0.95 if depth == DEPTH_DEEP else 0.7,
            )
            if depth == DEPTH_LIGHT:
                break  # light: at most one personal sphere boost via this loop + tendencies below

    if depth == DEPTH_DEEP:
        for t in _as_list(p.get("behavioral_tendencies")):
            if not isinstance(t, dict):
                continue
            tid = str(t.get("id") or "")
            for sid in TENDENCY_SPHERES.get(tid, ()):
                _add_ranked(
                    ranked,
                    seen,
                    sphere=sid,
                    reason=f"tendency «{t.get('label') or tid}»",
                    evidence_refs=list(t.get("source_refs") or [])[:4],
                    source="personal",
                    weight=0.8 + 0.1 * float(t.get("confidence") or 0.5),
                )

    # 3) Thesis family fallback (always available)
    for sid in _FAMILY_SPHERES.get(family, ("work_decisions", "communication")):
        _add_ranked(
            ranked,
            seen,
            sphere=sid,
            reason=f"thesis family «{family}»",
            evidence_refs=[f"thesis.{family}"],
            source="family",
            weight=0.55,
        )

    if not ranked:
        _add_ranked(
            ranked,
            seen,
            sphere="communication",
            reason="default fallback",
            evidence_refs=[],
            source="family",
            weight=0.4,
        )
        _add_ranked(
            ranked,
            seen,
            sphere="work_decisions",
            reason="default fallback",
            evidence_refs=[],
            source="family",
            weight=0.4,
        )

    # Sort by weight desc, stable by PRODUCT_SPHERE_IDS order as tiebreak
    order_idx = {s: i for i, s in enumerate(PRODUCT_SPHERE_IDS)}
    ranked.sort(key=lambda r: (-float(r.get("weight") or 0), order_idx.get(str(r.get("sphere")), 99)))
    ranked = ranked[: max(2, min(int(max_spheres or 4), 4))]
    for i, row in enumerate(ranked):
        row["rank"] = i + 1

    personal_count = sum(1 for r in ranked if r.get("source") == "personal")
    return {
        "contract_version": CONTRACT_VERSION,
        "evidence_depth": depth,
        "ranked_spheres": ranked,
        "primary_candidates": [r["sphere"] for r in ranked[:2]],
        "allowed_spheres": [r["sphere"] for r in ranked],
        "personal_sphere_count": personal_count,
        "must_justify_outside": depth in {DEPTH_LIGHT, DEPTH_DEEP},
        "notes": "prefer listed spheres; outside list requires sphere_reason + evidence_refs",
    }


def attach_sphere_selection_to_pack(
    pack: dict[str, Any] | None,
    *,
    day_domains: list[str] | None = None,
    ritual_head_topic: str | None = None,
    thesis_family: str | None = None,
) -> dict[str, Any]:
    """Return pack copy with sphere_selection nest."""
    p = dict(_as_dict(pack))
    selection = build_sphere_selection_c33b(
        p,
        day_domains=day_domains,
        ritual_head_topic=ritual_head_topic,
        thesis_family=thesis_family,
    )
    p["sphere_selection"] = selection
    return p


def run_sphere_selection_gate_c33b(
    native: dict[str, Any] | None,
    pack: dict[str, Any] | None,
) -> list[dict[str, str]]:
    """Sphere-specific defects (complement personalization gate)."""
    from todayflow_backend.services.day_scenario_personalization_c33 import (
        DEFECT_SPHERE_UNJUSTIFIED,
        _defect,
    )

    if not isinstance(native, dict):
        return []
    p = _as_dict(pack)
    selection = _as_dict(p.get("sphere_selection"))
    if not selection:
        # Build ephemeral selection if missing
        selection = build_sphere_selection_c33b(p)
    depth = str(p.get("evidence_depth") or selection.get("evidence_depth") or DEPTH_GENERAL)
    allowed = {str(x) for x in _as_list(selection.get("allowed_spheres")) if str(x)}
    defects: list[dict[str, str]] = []

    if depth != DEPTH_GENERAL and not allowed:
        defects.append(
            _defect(
                DEFECT_SPHERE_SELECTION_EMPTY,
                field="sphere_selection",
                message="personalization depth set but sphere selection empty",
            )
        )
        return defects

    scenes = [s for s in _as_list(native.get("scenes")) if isinstance(s, dict)]
    if not scenes:
        return defects

    for i, sc in enumerate(scenes):
        sphere = str(sc.get("sphere") or "").strip()
        tr = _as_dict(sc.get("personalization"))
        level = str(tr.get("personalization_level") or "")
        reason = str(tr.get("sphere_reason") or tr.get("personalization_reason") or "").strip()
        refs = _as_list(tr.get("personalization_evidence_refs"))
        if depth == DEPTH_GENERAL:
            continue
        if sphere and allowed and sphere not in allowed:
            if not reason or (depth == DEPTH_DEEP and not refs):
                defects.append(
                    _defect(
                        DEFECT_SPHERE_OUTSIDE_PACK,
                        field=f"scenes[{i}]",
                        message=f"sphere «{sphere}» outside selection without justification/refs",
                    )
                )
            elif not reason:
                defects.append(
                    _defect(
                        DEFECT_SPHERE_UNJUSTIFIED,
                        field=f"scenes[{i}]",
                        message=f"sphere «{sphere}» outside pack needs sphere_reason",
                    )
                )
        if level in {DEPTH_LIGHT, DEPTH_DEEP} and sphere in allowed and not reason:
            # Personalized scene inside pack still needs a reason at deep
            if depth == DEPTH_DEEP and i == 0:
                defects.append(
                    _defect(
                        DEFECT_SPHERE_UNJUSTIFIED,
                        field=f"scenes[{i}]",
                        message="primary personalized scene missing sphere_reason",
                    )
                )

    return defects

"""Phase C3.6.2 — Reviewer agreement and adjudication detection (eval-only)."""

from __future__ import annotations

from collections import Counter
from typing import Any

from todayflow_backend.services.day_scenario_human_golden_c362 import (
    DEFECT_PRESENCES,
    OVERALL_BANDS,
)

# Ordinal weights for weighted overall agreement (cannot_assess excluded from pairs)
_BAND_ORDER = {
    "pass": 0,
    "acceptable_with_issues": 1,
    "reject": 2,
}


def reviews_require_adjudication(reviewers: list[dict[str, Any]]) -> bool:
    if len(reviewers) < 2:
        return False
    a, b = reviewers[0], reviewers[1]
    if a.get("overall_band") != b.get("overall_band"):
        return True
    da = a.get("defects") if isinstance(a.get("defects"), dict) else {}
    db = b.get("defects") if isinstance(b.get("defects"), dict) else {}
    codes = set(da) | set(db)
    for code in codes:
        ra = da.get(code) if isinstance(da.get(code), dict) else {}
        rb = db.get(code) if isinstance(db.get(code), dict) else {}
        pa = ra.get("presence")
        pb = rb.get("presence")
        if pa != pb:
            # uncertain vs confident, present vs absent, applicability mismatch
            return True
        if pa == "present" and ra.get("severity") != rb.get("severity"):
            return True
    return False


def exact_overall_agreement(reviewers: list[dict[str, Any]]) -> bool | None:
    if len(reviewers) < 2:
        return None
    return reviewers[0].get("overall_band") == reviewers[1].get("overall_band")


def weighted_overall_distance(reviewers: list[dict[str, Any]]) -> float | None:
    """0 = exact; larger = farther. None if cannot_assess involved or missing."""
    if len(reviewers) < 2:
        return None
    ba = reviewers[0].get("overall_band")
    bb = reviewers[1].get("overall_band")
    if ba not in _BAND_ORDER or bb not in _BAND_ORDER:
        return None
    return abs(_BAND_ORDER[str(ba)] - _BAND_ORDER[str(bb)]) / 2.0


def defect_agreement_table(reviewers: list[dict[str, Any]]) -> dict[str, Any]:
    if len(reviewers) < 2:
        return {"codes": {}, "exact_match_rate": None}
    da = reviewers[0].get("defects") if isinstance(reviewers[0].get("defects"), dict) else {}
    db = reviewers[1].get("defects") if isinstance(reviewers[1].get("defects"), dict) else {}
    codes = sorted(set(da) | set(db))
    rows: dict[str, Any] = {}
    matches = 0
    compared = 0
    for code in codes:
        pa = (da.get(code) or {}).get("presence") if isinstance(da.get(code), dict) else None
        pb = (db.get(code) or {}).get("presence") if isinstance(db.get(code), dict) else None
        # Skip pairs where either is missing entirely
        if pa is None or pb is None:
            continue
        compared += 1
        agree = pa == pb
        if agree:
            matches += 1
        rows[code] = {
            "a": pa,
            "b": pb,
            "agree": agree,
            "involves_uncertain": "uncertain" in {pa, pb},
            "involves_not_applicable": "not_applicable" in {pa, pb},
        }
    return {
        "codes": rows,
        "exact_match_rate": (matches / compared) if compared else None,
        "compared": compared,
        "matches": matches,
    }


def cohens_kappa_binary(pairs: list[tuple[str, str]]) -> float | None:
    """Cohen's kappa for two raters on categorical labels (unstable on rare classes)."""
    if len(pairs) < 2:
        return None
    labels = sorted({x for p in pairs for x in p})
    if len(labels) < 2:
        # Perfect constant agreement → undefined/unstable
        return 1.0 if all(a == b for a, b in pairs) else None
    n = len(pairs)
    po = sum(1 for a, b in pairs if a == b) / n
    ca = Counter(a for a, _ in pairs)
    cb = Counter(b for _, b in pairs)
    pe = sum((ca[l] / n) * (cb[l] / n) for l in labels)
    if abs(1.0 - pe) < 1e-12:
        return None
    return (po - pe) / (1.0 - pe)


def agreement_report_for_case(case: dict[str, Any]) -> dict[str, Any]:
    reviewers = [r for r in (case.get("reviewers") or []) if isinstance(r, dict)]
    defect_tbl = defect_agreement_table(reviewers)
    presence_pairs: list[tuple[str, str]] = []
    for row in (defect_tbl.get("codes") or {}).values():
        if row.get("a") in DEFECT_PRESENCES and row.get("b") in DEFECT_PRESENCES:
            presence_pairs.append((str(row["a"]), str(row["b"])))
    overall_pairs: list[tuple[str, str]] = []
    if len(reviewers) >= 2:
        ba, bb = reviewers[0].get("overall_band"), reviewers[1].get("overall_band")
        if ba in OVERALL_BANDS and bb in OVERALL_BANDS:
            overall_pairs.append((str(ba), str(bb)))

    uncertain_n = 0
    total_presence = 0
    for r in reviewers:
        for row in (r.get("defects") or {}).values():
            if not isinstance(row, dict):
                continue
            total_presence += 1
            if row.get("presence") == "uncertain":
                uncertain_n += 1

    return {
        "case_id": case.get("case_id"),
        "reviewer_count": len(reviewers),
        "exact_overall_agreement": exact_overall_agreement(reviewers),
        "weighted_overall_distance": weighted_overall_distance(reviewers),
        "requires_adjudication": reviews_require_adjudication(reviewers) if len(reviewers) >= 2 else None,
        "defect_agreement": defect_tbl,
        "cohens_kappa_defect_presence": cohens_kappa_binary(presence_pairs),
        "cohens_kappa_overall": cohens_kappa_binary(overall_pairs) if overall_pairs else None,
        "uncertain_rate": (uncertain_n / total_presence) if total_presence else None,
        "cannot_assess_involved": any(
            r.get("overall_band") == "cannot_assess" for r in reviewers
        ),
        "note": (
            "Kappa is unstable for rare defects — use alongside exact agreement "
            "and support counts; never as sole promotion evidence."
        ),
    }


def inventory_agreement_summary(cases: list[dict[str, Any]]) -> dict[str, Any]:
    reports = [agreement_report_for_case(c) for c in cases]
    adjud = sum(1 for r in reports if r.get("requires_adjudication") is True)
    cannot = sum(1 for r in reports if r.get("cannot_assess_involved"))
    exact = [r.get("exact_overall_agreement") for r in reports if r.get("exact_overall_agreement") is not None]
    by_locale: dict[str, int] = {}
    by_profile: dict[str, int] = {}
    by_source: dict[str, int] = {}
    for c in cases:
        loc = str(c.get("locale") or "?")
        by_locale[loc] = by_locale.get(loc, 0) + 1
        pt = str(c.get("profile_type") or "?")
        by_profile[pt] = by_profile.get(pt, 0) + 1
        st = str(c.get("source_type") or "?")
        by_source[st] = by_source.get(st, 0) + 1
    return {
        "case_count": len(cases),
        "adjudication_rate": (adjud / len(cases)) if cases else None,
        "cannot_assess_case_share": (cannot / len(cases)) if cases else None,
        "exact_overall_agreement_rate": (
            sum(1 for x in exact if x) / len(exact) if exact else None
        ),
        "by_locale": by_locale,
        "by_profile_type": by_profile,
        "by_source_type": by_source,
        "cases": reports,
    }

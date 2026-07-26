#!/usr/bin/env python3
"""Import dual reviewer templates and seal C3.6.2 consensus (eval-only).

Usage:
  PYTHONPATH=src python evals/day_scenario_quality/import_human_reviews_seal_c362.py \\
    --batch ../../docs/audits/day_scenario_human_golden/batches/c362_blind_pilot_20260726

Does not invent labels. Reads filled reviewer_templates/*.json only.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from todayflow_backend.services.day_scenario_human_golden_c362 import (  # noqa: E402
    append_reviewer_submission,
    attach_analyzer_after_seal,
    build_consensus,
    verify_case_integrity,
)
from todayflow_backend.services.day_scenario_review_agreement_c362 import (  # noqa: E402
    agreement_report_for_case,
    reviews_require_adjudication,
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, obj: dict[str, Any]) -> None:
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _is_filled(sub: dict[str, Any]) -> bool:
    if sub.get("overall_band") not in {"pass", "acceptable_with_issues", "reject", "cannot_assess"}:
        return False
    defects = sub.get("defects")
    if not isinstance(defects, dict) or not defects:
        return False
    # At least one concrete presence
    return any(
        isinstance(v, dict) and v.get("presence") in {"present", "absent", "uncertain", "not_applicable"}
        for v in defects.values()
    )


def process_batch(batch_dir: Path, *, attach_empty_analyzer: bool = True) -> dict[str, Any]:
    cases_dir = batch_dir / "cases"
    tmpl_dir = batch_dir / "reviewer_templates"
    sealed_dir = batch_dir / "sealed"
    sealed_dir.mkdir(parents=True, exist_ok=True)
    report: dict[str, Any] = {"batch": batch_dir.name, "cases": []}

    for case_path in sorted(cases_dir.glob("hg-*.json")):
        case = _load(case_path)
        cid = case["case_id"]
        subs = []
        for tmpl in sorted(tmpl_dir.glob(f"{cid}.reviewer_*.json")):
            sub = _load(tmpl)
            if _is_filled(sub):
                subs.append(sub)
        entry: dict[str, Any] = {
            "case_id": cid,
            "filled_reviews": len(subs),
            "status": "waiting_reviews",
        }
        if len(subs) < 2:
            entry["missing"] = 2 - len(subs)
            report["cases"].append(entry)
            continue

        # Reset reviewers for re-import from templates (idempotent seal path).
        case["reviewers"] = []
        case["review_history"] = list(case.get("review_history") or [])
        case["adjudicator"] = None
        case["final_consensus"] = None
        case["analyzer_attachment"] = None
        case["review_status"] = "reviews_in_progress"

        for sub in subs:
            case = append_reviewer_submission(case, sub, allow_duplicate_reviewer=False)

        needs_adj = reviews_require_adjudication(case.get("reviewers") or [])
        agreement = agreement_report_for_case(case)
        entry["agreement"] = agreement
        if needs_adj:
            case["review_status"] = "needs_adjudication"
            entry["status"] = "needs_adjudication"
            _write(sealed_dir / f"{cid}.needs_adjudication.json", case)
            _write(case_path, case)
            report["cases"].append(entry)
            continue

        case = build_consensus(case)
        if attach_empty_analyzer:
            case = attach_analyzer_after_seal(
                case,
                {
                    "note": "analyzer deferred — attach pack scores in a later pass",
                    "defect_codes": [],
                },
            )
        errs = verify_case_integrity(case)
        entry["integrity_errors"] = errs
        entry["status"] = "sealed" if not errs else "sealed_with_warnings"
        entry["consensus_band"] = (case.get("final_consensus") or {}).get("overall_band")
        _write(sealed_dir / f"{cid}.sealed.json", case)
        _write(case_path, case)
        report["cases"].append(entry)

    _write(batch_dir / "seal_report.json", report)
    return report


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch", type=Path, required=True)
    args = ap.parse_args()
    report = process_batch(args.batch.resolve())
    sealed = sum(1 for c in report["cases"] if str(c["status"]).startswith("sealed"))
    waiting = sum(1 for c in report["cases"] if c["status"] == "waiting_reviews")
    adj = sum(1 for c in report["cases"] if c["status"] == "needs_adjudication")
    print(json.dumps({"ok": True, "sealed": sealed, "waiting": waiting, "needs_adjudication": adj}, ensure_ascii=False))


if __name__ == "__main__":
    main()

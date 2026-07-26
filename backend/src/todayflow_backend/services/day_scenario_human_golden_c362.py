"""Phase C3.6.2 — Human golden set contract, blind export, consensus (eval-only).

Extends the C3.5c golden scaffold with a reproducible human review protocol.
Does **not** change runtime, maturity registry, or generation.

Canon: docs/audits/DAY_SCENARIO_HUMAN_GOLDEN_C362.md
       docs/audits/DAY_SCENARIO_HUMAN_REVIEW_RUBRIC_C362.md
"""

from __future__ import annotations

import hashlib
import json
import re
from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Literal

from todayflow_backend.services.day_scenario_gate_maturity_c36 import GATE_RULES
from todayflow_backend.services.day_scenario_native_llm_c1 import NATIVE_LLM_SCHEMA_VERSION

# ---------------------------------------------------------------------------
# Versions (bump independently; mismatched labels are not silently equivalent)
# ---------------------------------------------------------------------------

GOLDEN_CONTRACT_VERSION = "day_scenario_human_golden_c362"
RUBRIC_VERSION = "day_scenario_human_review_rubric_c362.1"
DEFECT_CATALOG_VERSION = f"gate_rules_c36.{len(GATE_RULES)}"
REVIEW_PROTOCOL_VERSION = "day_scenario_review_protocol_c362.1"
SCENARIO_CONTRACT_VERSION = NATIVE_LLM_SCHEMA_VERSION
ANALYZER_VERSION = "day_scenario_eval_pack_c35.1+gate_maturity_c36"

LABEL_SOURCE_HUMAN = "human"
LABEL_SOURCE_SYNTHETIC = "synthetic_bootstrap"  # never mixed into consensus calibration

OverallBand = Literal["pass", "acceptable_with_issues", "reject", "cannot_assess"]
DefectPresence = Literal["present", "absent", "uncertain", "not_applicable"]
Severity = Literal["minor", "material", "severe"]
SourceType = Literal["synthetic", "live_capture", "curated"]
ReviewStatus = Literal[
    "draft",
    "exported_blind",
    "reviews_in_progress",
    "needs_adjudication",
    "consensus_ready",
    "sealed",
]

OVERALL_BANDS: frozenset[str] = frozenset(
    {"pass", "acceptable_with_issues", "reject", "cannot_assess"}
)
DEFECT_PRESENCES: frozenset[str] = frozenset(
    {"present", "absent", "uncertain", "not_applicable"}
)

# Keys stripped from blind reviewer export (analyzer / synthetic / policy leakage).
_BLIND_FORBIDDEN_KEYS = frozenset(
    {
        "editorial_defects",
        "editorial_score",
        "personalization_defects",
        "personalization_score",
        "gate_maturity",
        "runtime_action",
        "expected",
        "expected_defects",
        "primary_defects",
        "synthetic_expected",
        "mutation_id",
        "negative_id",
        "native_factory",
        "analyzer_defects",
        "defect_codes",
        "maturity",
        "gate_family",
        "promotion_eligible_hint",
        "label_source",  # reviewer must not see synthetic vs human intent
    }
)

_PII_KEY_HINTS = frozenset(
    {
        "birth_date",
        "birth_time",
        "latitude",
        "longitude",
        "email",
        "phone",
        "user_id",
        "raw_profile",
        "day_personal",
        "natal_chart",
        "full_name",
        "passport",
    }
)

_PII_TEXT_RE = re.compile(
    r"\b(\d{4}-\d{2}-\d{2}|\d{1,3}\.\d{4,}|@\w+\.\w+|birth_date|latitude|longitude)\b",
    re.I,
)


def version_bundle() -> dict[str, str]:
    return {
        "golden_contract_version": GOLDEN_CONTRACT_VERSION,
        "rubric_version": RUBRIC_VERSION,
        "defect_catalog_version": DEFECT_CATALOG_VERSION,
        "review_protocol_version": REVIEW_PROTOCOL_VERSION,
        "scenario_contract_version": SCENARIO_CONTRACT_VERSION,
        "analyzer_version": ANALYZER_VERSION,
    }


def defect_catalog_codes() -> list[str]:
    return sorted(GATE_RULES.keys())


def canonical_json(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def scenario_hash(scenario: dict[str, Any] | None) -> str:
    payload = scenario if isinstance(scenario, dict) else {}
    digest = hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()
    return f"sha256:{digest}"


def _strip_pii(obj: Any) -> Any:
    if isinstance(obj, dict):
        out: dict[str, Any] = {}
        for k, v in obj.items():
            key = str(k)
            if key.lower() in _PII_KEY_HINTS or any(h in key.lower() for h in _PII_KEY_HINTS):
                out[key] = "[redacted]"
                continue
            out[key] = _strip_pii(v)
        return out
    if isinstance(obj, list):
        return [_strip_pii(x) for x in obj]
    if isinstance(obj, str) and _PII_TEXT_RE.search(obj):
        return _PII_TEXT_RE.sub("[redacted]", obj)
    return obj


def _strip_blind_leakage(obj: Any) -> Any:
    if isinstance(obj, dict):
        out: dict[str, Any] = {}
        for k, v in obj.items():
            if str(k) in _BLIND_FORBIDDEN_KEYS:
                continue
            out[str(k)] = _strip_blind_leakage(v)
        return out
    if isinstance(obj, list):
        return [_strip_blind_leakage(x) for x in obj]
    return obj


def new_neutral_case_id(*, seed: str = "") -> str:
    """Neutral randomized-looking id — never good/bad/abstract/clone."""
    base = seed or datetime.now(timezone.utc).isoformat()
    h = hashlib.sha256(base.encode("utf-8")).hexdigest()[:12]
    return f"hg-{h}"


def build_human_case_shell(
    *,
    case_id: str,
    scenario: dict[str, Any],
    locale: str,
    profile_type: str,
    evidence_depth: str,
    source_type: SourceType,
    generator_version: str | None = None,
    generation_seed: str | None = None,
    scenario_id: str | None = None,
    evidence_pack_ref: str | None = None,
    contract_valid: bool = True,
    hard_gate_result: str = "accept",
) -> dict[str, Any]:
    """Create a machine-readable human golden case shell (no reviews yet)."""
    clean_scenario = _strip_pii(deepcopy(scenario if isinstance(scenario, dict) else {}))
    # Remove any analyzer meta nests if present on scenario
    for k in ("editorial_meta", "editorial_defects", "personalization_defects"):
        clean_scenario.pop(k, None)
    sh = scenario_hash(clean_scenario)
    now = datetime.now(timezone.utc).isoformat()
    return {
        **version_bundle(),
        "case_id": case_id,
        "scenario_id": scenario_id or case_id,
        "scenario_hash": sh,
        "locale": locale,
        "profile_type": profile_type,
        "evidence_depth": evidence_depth,
        "source_type": source_type,
        "generator_version": generator_version or SCENARIO_CONTRACT_VERSION,
        "generation_seed": generation_seed,
        "created_at": now,
        "scenario": clean_scenario,
        "evidence_pack_snapshot": None,
        "evidence_pack_ref": evidence_pack_ref,
        "contract_valid": bool(contract_valid),
        "hard_gate_result": hard_gate_result,
        "review_status": "draft",
        "label_source": LABEL_SOURCE_HUMAN,
        "reviewers": [],
        "adjudicator": None,
        "final_consensus": None,
        "review_history": [],
        "analyzer_attachment": None,  # filled only after human review sealed
    }


def export_blind_review_packet(case: dict[str, Any]) -> dict[str, Any]:
    """Export for reviewers: scenario + catalog codes, no analyzer/synthetic leakage."""
    scenario = _strip_blind_leakage(_strip_pii(deepcopy(case.get("scenario") or {})))
    packet = {
        "export_kind": "blind_human_review_c362",
        "case_id": case.get("case_id"),
        "scenario_id": case.get("scenario_id"),
        "scenario_hash": case.get("scenario_hash"),
        "locale": case.get("locale"),
        "profile_type": case.get("profile_type"),
        "evidence_depth": case.get("evidence_depth"),
        "source_type": case.get("source_type"),
        "rubric_version": case.get("rubric_version") or RUBRIC_VERSION,
        "golden_contract_version": case.get("golden_contract_version") or GOLDEN_CONTRACT_VERSION,
        "defect_catalog_version": case.get("defect_catalog_version") or DEFECT_CATALOG_VERSION,
        "review_protocol_version": case.get("review_protocol_version") or REVIEW_PROTOCOL_VERSION,
        "scenario_contract_version": case.get("scenario_contract_version") or SCENARIO_CONTRACT_VERSION,
        "defect_codes_for_labeling": defect_catalog_codes(),
        "scenario": scenario,
        "instructions": {
            "overall_band": sorted(OVERALL_BANDS),
            "defect_presence": sorted(DEFECT_PRESENCES),
            "severity": ["minor", "material", "severe"],
            "blind": True,
            "do_not_infer_from_filename": True,
        },
    }
    # Hard assert: no forbidden keys leaked
    blob = canonical_json(packet)
    for bad in (
        "SCENE_ABSTRACT expected",
        "gate_maturity",
        "synthetic_expected",
        "mutation_id",
        "negative_id",
        "editorial_score",
    ):
        if bad in blob:
            raise ValueError(f"blind export leakage: {bad}")
    return packet


def validate_reviewer_submission(
    submission: dict[str, Any],
    *,
    case: dict[str, Any],
    allowed_codes: list[str] | None = None,
) -> list[str]:
    errors: list[str] = []
    if not isinstance(submission, dict):
        return ["submission_not_dict"]
    if str(submission.get("case_id")) != str(case.get("case_id")):
        errors.append("case_id_mismatch")
    if str(submission.get("scenario_hash")) != str(case.get("scenario_hash")):
        errors.append("scenario_hash_mismatch")
    for key in (
        "golden_contract_version",
        "rubric_version",
        "defect_catalog_version",
        "review_protocol_version",
    ):
        if submission.get(key) and submission.get(key) != case.get(key):
            errors.append(f"version_mismatch:{key}")
    band = submission.get("overall_band")
    if band not in OVERALL_BANDS:
        errors.append("bad_overall_band")
    if not submission.get("reviewer_id"):
        errors.append("missing_reviewer_id")
    codes = allowed_codes or defect_catalog_codes()
    defects = submission.get("defects")
    if not isinstance(defects, dict):
        errors.append("defects_not_dict")
        return errors
    for code, row in defects.items():
        if code not in codes and code not in GATE_RULES:
            # allow unknown but mark
            pass
        if not isinstance(row, dict):
            errors.append(f"defect_row_not_dict:{code}")
            continue
        if row.get("presence") not in DEFECT_PRESENCES:
            errors.append(f"bad_presence:{code}")
        if row.get("presence") == "present" and row.get("severity") not in {
            "minor",
            "material",
            "severe",
            None,
        }:
            if row.get("severity") not in {"minor", "material", "severe"}:
                errors.append(f"bad_severity:{code}")
    return errors


def append_reviewer_submission(
    case: dict[str, Any],
    submission: dict[str, Any],
    *,
    allow_duplicate_reviewer: bool = False,
) -> dict[str, Any]:
    """Append an independent reviewer label; history is append-only."""
    out = deepcopy(case)
    errors = validate_reviewer_submission(submission, case=out)
    if errors:
        raise ValueError(";".join(errors))
    rid = str(submission["reviewer_id"])
    existing = [r for r in (out.get("reviewers") or []) if isinstance(r, dict)]
    if not allow_duplicate_reviewer and any(str(r.get("reviewer_id")) == rid for r in existing):
        raise ValueError("duplicate_reviewer_id")
    record = {
        "reviewer_id": rid,
        "submitted_at": datetime.now(timezone.utc).isoformat(),
        "overall_band": submission["overall_band"],
        "defects": deepcopy(submission.get("defects") or {}),
        "notes": submission.get("notes"),
        "versions": {
            k: submission.get(k)
            for k in (
                "golden_contract_version",
                "rubric_version",
                "defect_catalog_version",
                "review_protocol_version",
            )
        },
    }
    history = list(out.get("review_history") or [])
    history.append({"event": "reviewer_submission", "payload": deepcopy(record)})
    out["review_history"] = history
    out["reviewers"] = existing + [record]
    n = len(out["reviewers"])
    if n < 2:
        out["review_status"] = "reviews_in_progress"
    else:
        from todayflow_backend.services.day_scenario_review_agreement_c362 import (
            reviews_require_adjudication,
        )

        if reviews_require_adjudication(out["reviewers"]):
            out["review_status"] = "needs_adjudication"
        else:
            out["review_status"] = "consensus_ready"
    return out


def apply_adjudication(
    case: dict[str, Any],
    *,
    adjudicator_id: str,
    overall_band: OverallBand,
    defects: dict[str, Any],
    rationale: str,
    overrides: list[dict[str, Any]] | None = None,
    confidence: float = 0.8,
) -> dict[str, Any]:
    out = deepcopy(case)
    if len(out.get("reviewers") or []) < 2:
        raise ValueError("adjudication_requires_quorum")
    if overall_band not in OVERALL_BANDS:
        raise ValueError("bad_overall_band")
    adj = {
        "adjudicator_id": adjudicator_id,
        "submitted_at": datetime.now(timezone.utc).isoformat(),
        "overall_band": overall_band,
        "defects": deepcopy(defects),
        "rationale": rationale,
        "overrides": list(overrides or []),
        "confidence": confidence,
    }
    history = list(out.get("review_history") or [])
    history.append({"event": "adjudication", "payload": deepcopy(adj)})
    out["review_history"] = history
    out["adjudicator"] = adj
    out["review_status"] = "consensus_ready"
    return out


def build_consensus(
    case: dict[str, Any],
    *,
    require_adjudication_if_disagreement: bool = True,
) -> dict[str, Any]:
    """Seal immutable final_consensus from agreement or adjudication."""
    out = deepcopy(case)
    reviewers = [r for r in (out.get("reviewers") or []) if isinstance(r, dict)]
    if len(reviewers) < 2:
        raise ValueError("consensus_requires_quorum")
    from todayflow_backend.services.day_scenario_review_agreement_c362 import (
        reviews_require_adjudication,
    )

    needs = reviews_require_adjudication(reviewers)
    if needs and require_adjudication_if_disagreement and not out.get("adjudicator"):
        raise ValueError("disagreement_requires_adjudication")

    if out.get("adjudicator"):
        adj = out["adjudicator"]
        consensus = {
            "overall_band": adj["overall_band"],
            "defects": deepcopy(adj.get("defects") or {}),
            "source": "adjudication",
            "adjudicator_id": adj.get("adjudicator_id"),
            "sealed_at": datetime.now(timezone.utc).isoformat(),
            "scenario_hash": out.get("scenario_hash"),
            "label_source": LABEL_SOURCE_HUMAN,
            **{k: out.get(k) for k in version_bundle()},
        }
    else:
        # Exact agreement path: copy reviewer A (identical to B by definition)
        a = reviewers[0]
        consensus = {
            "overall_band": a["overall_band"],
            "defects": deepcopy(a.get("defects") or {}),
            "source": "exact_agreement",
            "adjudicator_id": None,
            "sealed_at": datetime.now(timezone.utc).isoformat(),
            "scenario_hash": out.get("scenario_hash"),
            "label_source": LABEL_SOURCE_HUMAN,
            **{k: out.get(k) for k in version_bundle()},
        }
    history = list(out.get("review_history") or [])
    history.append({"event": "consensus_sealed", "payload": deepcopy(consensus)})
    out["review_history"] = history
    out["final_consensus"] = consensus
    out["review_status"] = "sealed"
    return out


def attach_analyzer_after_seal(
    case: dict[str, Any],
    analyzer_output: dict[str, Any],
) -> dict[str, Any]:
    """Analyzer output may attach only after human consensus is sealed."""
    out = deepcopy(case)
    if out.get("review_status") != "sealed" or not out.get("final_consensus"):
        raise ValueError("analyzer_attach_requires_sealed_consensus")
    out["analyzer_attachment"] = {
        "attached_at": datetime.now(timezone.utc).isoformat(),
        "output": deepcopy(analyzer_output),
    }
    history = list(out.get("review_history") or [])
    history.append({"event": "analyzer_attached_post_review", "payload": {"keys": sorted(analyzer_output.keys())}})
    out["review_history"] = history
    return out


def verify_case_integrity(case: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    scen = case.get("scenario")
    if not isinstance(scen, dict):
        errors.append("scenario_missing")
        return errors
    if scenario_hash(scen) != str(case.get("scenario_hash") or ""):
        errors.append("scenario_hash_drift")
    for key, expected in version_bundle().items():
        # drift vs current tooling is a soft warning for old labels — hard if consensus present
        # with mismatched stored versions vs declared bundle when sealing new ones
        if case.get(key) and case.get("final_consensus") and case.get(key) != expected:
            # historical labels allowed; flag for calibration adapter
            errors.append(f"version_stale:{key}")
    return errors


def detect_duplicate_scenario_hashes(cases: list[dict[str, Any]]) -> list[str]:
    seen: dict[str, str] = {}
    dups: list[str] = []
    for c in cases:
        h = str(c.get("scenario_hash") or "")
        cid = str(c.get("case_id") or "")
        if not h:
            continue
        if h in seen:
            dups.append(f"{seen[h]}|{cid}")
        else:
            seen[h] = cid
    return dups


def consensus_to_calibration_case(case: dict[str, Any]) -> dict[str, Any] | None:
    """Map sealed human consensus → C3.6.1 calibration input shape.

    Skips cannot_assess. Uses only present/absent (not uncertain/N/A) for defect support.
    Never mixes synthetic_bootstrap.
    """
    if str(case.get("label_source") or "") == LABEL_SOURCE_SYNTHETIC:
        return None
    consensus = case.get("final_consensus")
    if not isinstance(consensus, dict):
        return None
    band = str(consensus.get("overall_band") or "")
    if band == "cannot_assess":
        return None
    # Map overall → calibration band used by c361 (pass/reject); acceptable kept as pass-like
    # for "clean negative" only when pass; acceptable is NOT auto-negative for every defect.
    if band == "pass":
        calib_band = "pass"
        primary: list[str] = []
    elif band == "reject":
        calib_band = "reject"
        primary = [
            code
            for code, row in (consensus.get("defects") or {}).items()
            if isinstance(row, dict) and row.get("presence") == "present"
        ]
    elif band == "acceptable_with_issues":
        # Useful scenario — do not treat as reject; only explicit present defects as soft notes
        calib_band = "pass"
        primary = []
    else:
        return None

    # Exclude uncertain / n_a from negative support accounting via explicit fields
    absent_codes = [
        code
        for code, row in (consensus.get("defects") or {}).items()
        if isinstance(row, dict) and row.get("presence") == "absent"
    ]
    uncertain_codes = [
        code
        for code, row in (consensus.get("defects") or {}).items()
        if isinstance(row, dict) and row.get("presence") == "uncertain"
    ]
    na_codes = [
        code
        for code, row in (consensus.get("defects") or {}).items()
        if isinstance(row, dict) and row.get("presence") == "not_applicable"
    ]

    return {
        "case_id": case.get("case_id"),
        "locale": case.get("locale"),
        "profile_id": case.get("profile_type"),
        "profile_type": case.get("profile_type"),
        "source": case.get("source_type"),
        "label_source": LABEL_SOURCE_HUMAN,
        "native_ref": case.get("scenario_id"),
        "scenario_hash": case.get("scenario_hash"),
        "expected": {
            "band": calib_band,
            "primary_defects": primary,
            "absent_defects": absent_codes,
            "uncertain_defects": uncertain_codes,
            "not_applicable_defects": na_codes,
            "human_overall_band": band,
        },
        "consensus_band": calib_band,
        "human_overall_band": band,
        **{k: case.get(k) for k in version_bundle()},
    }


def example_review_cycle_fixture() -> dict[str, Any]:
    """One complete blind→agree→consensus cycle (no PII, no analyzer until seal)."""
    scenario = {
        "schema_version": NATIVE_LLM_SCHEMA_VERSION,
        "conflict": {
            "title": "Clarity versus smoothing",
            "force_a": "smooth for quiet",
            "force_b": "name one fact",
            "thesis": "Today a short honest reply beats false harmony.",
        },
        "scenes": [
            {
                "scene_id": "scene.relationships",
                "sphere": "relationships",
                "setup": "A chat asks “are you okay?” when you want to answer “fine”.",
                "opportunity": "Reply with one precise sentence.",
                "trap": "Agree for quiet, then resent.",
                "recommended_action": "Send one paragraph after a short pause.",
                "everyday_example": "Partner message at 21:40: “where are you?”",
            }
        ],
    }
    case = build_human_case_shell(
        case_id=new_neutral_case_id(seed="example-c362-cycle"),
        scenario=scenario,
        locale="en",
        profile_type="smooth_conflict",
        evidence_depth="deep_personalized",
        source_type="curated",
        generation_seed="example-c362",
    )
    blind = export_blind_review_packet(case)
    codes = blind["defect_codes_for_labeling"]
    # Minimal defect map: absent for catalog sample, present for one illustrative code if listed
    def _absent_map(extra_present: str | None = None) -> dict[str, Any]:
        m: dict[str, Any] = {}
        for c in codes[:8]:
            m[c] = {
                "presence": "present" if c == extra_present else "absent",
                "severity": "material" if c == extra_present else None,
                "evidence_location": "scenes[0].setup" if c == extra_present else None,
                "rationale": "example",
                "affects_overall_band": bool(c == extra_present),
            }
        return m

    present_code = "SCENE_ABSTRACT" if "SCENE_ABSTRACT" in codes else None
    sub_a = {
        "case_id": case["case_id"],
        "scenario_hash": case["scenario_hash"],
        "reviewer_id": "reviewer_a",
        "overall_band": "pass",
        "defects": _absent_map(None),
        "notes": "Clear everyday scene.",
        **version_bundle(),
    }
    sub_b = {
        "case_id": case["case_id"],
        "scenario_hash": case["scenario_hash"],
        "reviewer_id": "reviewer_b",
        "overall_band": "pass",
        "defects": _absent_map(None),
        "notes": "Agree — usable as-is.",
        **version_bundle(),
    }
    case = append_reviewer_submission(case, sub_a)
    case = append_reviewer_submission(case, sub_b)
    case = build_consensus(case)
    case = attach_analyzer_after_seal(
        case,
        {"defect_codes": [], "note": "attached only after seal"},
    )
    return {
        "blind_packet": blind,
        "case": case,
        "calibration_row": consensus_to_calibration_case(case),
        "illustrative_present_code": present_code,
    }

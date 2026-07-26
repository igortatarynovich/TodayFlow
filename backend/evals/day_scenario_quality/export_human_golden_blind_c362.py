#!/usr/bin/env python3
"""Export C3.6.2 blind human-review packets from live day_scenario generations.

Eval-only. No runtime changes. Strips PII and analyzer leakage.

Usage (from backend/):
  PYTHONPATH=src .venv/bin/python evals/day_scenario_quality/export_human_golden_blind_c362.py \\
    --limit 12 --out ../../docs/audits/day_scenario_human_golden/batches/BATCH_ID

  # Or against docker DB:
  DATABASE_URL=postgresql+psycopg://... PYTHONPATH=src ...
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
REPO = ROOT.parent
sys.path.insert(0, str(ROOT / "src"))

from todayflow_backend.services.day_scenario_human_golden_c362 import (  # noqa: E402
    build_human_case_shell,
    detect_duplicate_scenario_hashes,
    export_blind_review_packet,
    new_neutral_case_id,
    scenario_hash,
    version_bundle,
)


def _infer_profile_type(story: dict[str, Any]) -> str:
    personal = story.get("day_personal") if isinstance(story.get("day_personal"), dict) else {}
    if personal:
        return "live_registered_personal"
    return "live_registered"


def _infer_evidence_depth(story: dict[str, Any], scenario: dict[str, Any]) -> str:
    personal = story.get("day_personal") if isinstance(story.get("day_personal"), dict) else {}
    if personal.get("summary_ru") or personal.get("personal_astrology"):
        return "deep_personalized"
    if scenario.get("personalization") or scenario.get("sphere_selection"):
        return "general_personalized"
    return "general"


def _load_candidates(*, limit: int, include_deterministic: bool) -> list[dict[str, Any]]:
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker

    url = os.environ.get("DATABASE_URL") or ""
    if not url:
        raise SystemExit("DATABASE_URL required")
    # Runtime app uses postgresql+psycopg; SQLAlchemy URL ok as-is.
    eng = create_engine(url)
    Session = sessionmaker(bind=eng)
    # Native success only + optional B5 (often logged as fallback when LLM timed out).
    if include_deterministic:
        q = text(
            """
            SELECT id, user_id, locale, input_payload, normalized_response, created_at, status, used_fallback
            FROM generation_logs
            WHERE module = 'day_story_v1'
              AND status IN ('success', 'fallback')
              AND (
                (COALESCE(used_fallback, false) = false
                  AND normalized_response->'day_scenario'->>'generation_source' = 'native_llm_c1')
                OR normalized_response->'day_scenario'->>'generation_source' = 'deterministic_engine_b5'
              )
            ORDER BY created_at DESC
            LIMIT :lim
            """
        )
        params: dict[str, Any] = {"lim": max(limit * 6, 60)}
    else:
        q = text(
            """
            SELECT id, user_id, locale, input_payload, normalized_response, created_at, status, used_fallback
            FROM generation_logs
            WHERE module = 'day_story_v1'
              AND status = 'success'
              AND COALESCE(used_fallback, false) = false
              AND normalized_response->'day_scenario'->>'generation_source' = 'native_llm_c1'
            ORDER BY created_at DESC
            LIMIT :lim
            """
        )
        params = {"lim": max(limit * 4, 40)}
    rows: list[dict[str, Any]] = []
    with Session() as db:
        for r in db.execute(q, params).mappings():
            nr = r["normalized_response"] if isinstance(r["normalized_response"], dict) else {}
            sc = nr.get("day_scenario") if isinstance(nr.get("day_scenario"), dict) else {}
            scenes = sc.get("scenes") if isinstance(sc.get("scenes"), list) else []
            if not sc.get("ready") or len(scenes) < 2:
                continue
            rows.append(dict(r))
            if len(rows) >= limit * 4:
                break
    return rows


def _dedupe_keep_diverse(rows: list[dict[str, Any]], *, limit: int) -> list[dict[str, Any]]:
    seen_hash: set[str] = set()
    seen_theme: set[str] = set()
    out: list[dict[str, Any]] = []
    b5_hotspot: dict[str, Any] | None = None
    for r in rows:
        nr = r["normalized_response"] if isinstance(r["normalized_response"], dict) else {}
        sc = nr.get("day_scenario") if isinstance(nr.get("day_scenario"), dict) else {}
        src = str(sc.get("generation_source") or "")
        theme = str(nr.get("theme") or "").strip().lower()
        h = scenario_hash(sc)
        if h in seen_hash:
            continue
        if src == "deterministic_engine_b5" and b5_hotspot is None:
            b5_hotspot = r
        if theme in seen_theme:
            continue
        seen_hash.add(h)
        if theme:
            seen_theme.add(theme)
        out.append(r)
        if len(out) >= limit:
            break
    # Ensure at least one B5 sample when room remains (quality hotspot coverage).
    if b5_hotspot is not None and len(out) < limit:
        nr = b5_hotspot["normalized_response"]
        sc = nr.get("day_scenario") if isinstance(nr, dict) else {}
        h = scenario_hash(sc if isinstance(sc, dict) else {})
        if h not in seen_hash:
            out.append(b5_hotspot)
    return out[:limit]


def export_batch(
    *,
    out_dir: Path,
    limit: int = 10,
    include_deterministic: bool = True,
    batch_id: str | None = None,
) -> dict[str, Any]:
    rows = _dedupe_keep_diverse(
        _load_candidates(limit=limit, include_deterministic=include_deterministic),
        limit=limit,
    )
    if not rows:
        raise SystemExit("no live candidates found")

    bid = batch_id or datetime.now(timezone.utc).strftime("c362_blind_%Y%m%dT%H%M%SZ")
    root = out_dir / bid
    cases_dir = root / "cases"
    blind_dir = root / "blind"
    templates_dir = root / "reviewer_templates"
    cases_dir.mkdir(parents=True, exist_ok=True)
    blind_dir.mkdir(parents=True, exist_ok=True)
    templates_dir.mkdir(parents=True, exist_ok=True)

    index_cases: list[dict[str, Any]] = []
    case_shells: list[dict[str, Any]] = []

    for r in rows:
        nr = r["normalized_response"] if isinstance(r["normalized_response"], dict) else {}
        sc = nr.get("day_scenario") if isinstance(nr.get("day_scenario"), dict) else {}
        ip = r["input_payload"] if isinstance(r["input_payload"], dict) else {}
        gen_id = int(r["id"])
        locale = str(r.get("locale") or "ru")[:8] or "ru"
        seed = f"live-genlog-{gen_id}-{ip.get('target_date')}-{ip.get('prompt_version')}"
        case_id = new_neutral_case_id(seed=seed)
        case = build_human_case_shell(
            case_id=case_id,
            scenario=sc,
            locale=locale,
            profile_type=_infer_profile_type(nr),
            evidence_depth=_infer_evidence_depth(nr, sc),
            source_type="live_capture",
            generator_version=str(ip.get("prompt_version") or sc.get("generation_source") or ""),
            generation_seed=seed,
            scenario_id=case_id,
            evidence_pack_ref=f"sha256_genlog:{scenario_hash({'id': gen_id})[7:19]}",
            contract_valid=True,
            hard_gate_result="accept",
        )
        case["review_status"] = "exported_blind"
        case["live_meta"] = {
            "target_date": ip.get("target_date"),
            "prompt_version": ip.get("prompt_version"),
            "theme": nr.get("theme"),
            "generation_source": sc.get("generation_source"),
            "scene_count": len(sc.get("scenes") or []),
            # Never store raw user_id in committed packs — anonymized ordinal only.
            "capture_slot": f"u{int(r['user_id']) % 97}",
        }
        blind = export_blind_review_packet(case)
        (cases_dir / f"{case_id}.json").write_text(
            json.dumps(case, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        (blind_dir / f"{case_id}.blind.json").write_text(
            json.dumps(blind, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        # Empty dual-reviewer templates (fill offline / in review tool).
        for rid in ("reviewer_a", "reviewer_b"):
            tmpl = {
                "case_id": case_id,
                "scenario_hash": case["scenario_hash"],
                "reviewer_id": rid,
                "overall_band": None,
                "defects": {
                    code: {
                        "presence": None,
                        "severity": None,
                        "evidence_location": None,
                        "rationale": None,
                        "affects_overall_band": None,
                    }
                    for code in blind["defect_codes_for_labeling"]
                },
                "notes": None,
                **version_bundle(),
            }
            (templates_dir / f"{case_id}.{rid}.json").write_text(
                json.dumps(tmpl, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
        case_shells.append(case)
        index_cases.append(
            {
                "case_id": case_id,
                "locale": locale,
                "source_type": "live_capture",
                "profile_type": case["profile_type"],
                "evidence_depth": case["evidence_depth"],
                "generation_source": sc.get("generation_source"),
                "theme": nr.get("theme"),
                "scene_count": len(sc.get("scenes") or []),
                "scenario_hash": case["scenario_hash"],
                "blind_path": f"blind/{case_id}.blind.json",
                "case_path": f"cases/{case_id}.json",
            }
        )

    dups = detect_duplicate_scenario_hashes(case_shells)
    manifest = {
        "batch_id": bid,
        "export_kind": "c362_human_golden_blind_batch",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "versions": version_bundle(),
        "case_count": len(index_cases),
        "duplicate_scenario_hashes": dups,
        "instructions": {
            "quorum": 2,
            "rubric": "docs/audits/DAY_SCENARIO_HUMAN_REVIEW_RUBRIC_C362.md",
            "protocol": "docs/audits/DAY_SCENARIO_HUMAN_GOLDEN_C362.md",
            "blind_dir": "blind/",
            "do_not_open_cases_dir_as_reviewer": True,
            "fill_templates": "reviewer_templates/*.json then return to operator",
            "next_target": "grow to 40 after process check (20 RU / 20 EN mix)",
        },
        "cases": index_cases,
    }
    (root / "index.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    readme = f"""# Human golden blind batch `{bid}`

Pilot export from **live** `day_scenario` generations (C3.6.2).

## For reviewers

1. Open only files under `blind/` (and the rubric).
2. Do **not** open `cases/` — it may contain operator meta.
3. Fill `reviewer_templates/<case_id>.reviewer_a.json` and `.reviewer_b.json`.
4. Set `overall_band` + each defect `presence` (`present`/`absent`/`uncertain`/`not_applicable`).
5. Return filled templates to the operator (no chat with the other reviewer).

Rubric: `docs/audits/DAY_SCENARIO_HUMAN_REVIEW_RUBRIC_C362.md`

## Inventory

- Cases: **{len(index_cases)}** (pilot — not the full 40 target)
- Locales: see `index.json`
- Source: `live_capture` only in this batch

## Operator

After dual reviews: `append_reviewer_submission` → adjudicate if needed → `build_consensus` → attach analyzer.
"""
    (root / "README.md").write_text(readme, encoding="utf-8")
    return manifest


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--out",
        type=Path,
        default=REPO / "docs" / "audits" / "day_scenario_human_golden" / "batches",
    )
    ap.add_argument("--limit", type=int, default=8)
    ap.add_argument("--batch-id", default=None)
    ap.add_argument("--native-only", action="store_true")
    args = ap.parse_args()
    manifest = export_batch(
        out_dir=args.out,
        limit=args.limit,
        include_deterministic=not args.native_only,
        batch_id=args.batch_id,
    )
    print(json.dumps({"ok": True, "batch_id": manifest["batch_id"], "case_count": manifest["case_count"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Export +N RU live golden cases excluding prior sealed batches. Eval-only."""

from __future__ import annotations

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


def _write_sheet(blind: dict[str, Any], path: Path) -> None:
    sc = blind.get("scenario") if isinstance(blind.get("scenario"), dict) else {}
    conflict = sc.get("conflict") if isinstance(sc.get("conflict"), dict) else {}
    scenes = sc.get("scenes") if isinstance(sc.get("scenes"), list) else []
    lines = [
        f"# Review sheet — `{blind.get('case_id')}`",
        "",
        f"- scenario_hash: `{blind.get('scenario_hash')}`",
        f"- locale: {blind.get('locale')}",
        f"- Fill: `reviewer_templates/{blind.get('case_id')}.reviewer_*.json`",
        "- Rubric: `docs/audits/DAY_SCENARIO_HUMAN_REVIEW_RUBRIC_C362.md`",
        "- **Blind:** do not open `cases/` or the other reviewer's template",
        "",
        "## Conflict",
        f"- short_name: {conflict.get('title') or conflict.get('short_name') or ''}",
        f"- thesis: {conflict.get('thesis') or ''}",
        "",
        "## Scenes",
    ]
    for i, raw in enumerate(scenes, start=1):
        if not isinstance(raw, dict):
            continue
        lines.extend(
            [
                f"### Scene {i}: {raw.get('scene_id')} / {raw.get('sphere')}",
                f"- **setup:** {raw.get('setup') or raw.get('what_happens') or ''}",
                f"- **everyday_example:** {raw.get('everyday_example') or ''}",
                f"- **opportunity:** {raw.get('opportunity') or ''}",
                f"- **trap:** {raw.get('trap') or ''}",
                f"- **recommended_action:** {raw.get('recommended_action') or ''}",
                f"- **avoid_action:** {raw.get('avoid_action') or ''}",
                "",
            ]
        )
    lines.extend(
        [
            "## Your labels",
            "",
            "- overall_band: `pass` | `acceptable_with_issues` | `reject` | `cannot_assess`",
            "- Priority: SCENE_ABSTRACT, SCENE_CLONE, SCENE_MISSING_EVERYDAY, SCENE_UNIVERSAL_ADVICE, ASTRO_JARGON_BARE",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    from sqlalchemy import create_engine, text

    batch_id = "c362_ru_live_expansion_20260727"
    limit = 13
    out_root = REPO / "docs" / "audits" / "day_scenario_human_golden" / "batches" / batch_id
    exclude_paths = [
        REPO / "docs/audits/day_scenario_human_golden/batches/c362_blind_pilot_20260726/index.json",
        REPO / "docs/audits/day_scenario_human_golden/batches/c362_en_expansion_20260726/index.json",
    ]
    exclude: set[str] = set()
    for p in exclude_paths:
        if p.exists():
            for c in json.loads(p.read_text(encoding="utf-8")).get("cases") or []:
                if c.get("scenario_hash"):
                    exclude.add(str(c["scenario_hash"]))

    url = os.environ.get("DATABASE_URL") or ""
    if not url:
        raise SystemExit("DATABASE_URL required")
    eng = create_engine(url)
    q = text(
        """
        SELECT id, user_id, locale, input_payload, normalized_response, created_at
        FROM generation_logs
        WHERE module = 'day_story_v1'
          AND status IN ('success', 'fallback')
          AND COALESCE(locale, 'ru') = 'ru'
          AND (
            (COALESCE(used_fallback, false) = false
              AND normalized_response->'day_scenario'->>'generation_source' = 'native_llm_c1')
            OR normalized_response->'day_scenario'->>'generation_source' = 'deterministic_engine_b5'
          )
        ORDER BY created_at DESC
        LIMIT 120
        """
    )
    candidates: list[dict[str, Any]] = []
    seen_hash: set[str] = set()
    with eng.connect() as db:
        for r in db.execute(q).mappings():
            nr = r["normalized_response"] if isinstance(r["normalized_response"], dict) else {}
            sc = nr.get("day_scenario") if isinstance(nr.get("day_scenario"), dict) else {}
            scenes = sc.get("scenes") if isinstance(sc.get("scenes"), list) else []
            if not sc.get("ready") or len(scenes) < 2:
                continue
            h = scenario_hash(sc)
            if h in exclude or h in seen_hash:
                continue
            seen_hash.add(h)
            candidates.append(dict(r))
            if len(candidates) >= limit:
                break

    if len(candidates) < limit:
        raise SystemExit(f"only {len(candidates)} candidates available, need {limit}")

    cases_dir = out_root / "cases"
    blind_dir = out_root / "blind"
    templates_dir = out_root / "reviewer_templates"
    sheets_dir = out_root / "review_sheets"
    for d in (cases_dir, blind_dir, templates_dir, sheets_dir):
        d.mkdir(parents=True, exist_ok=True)

    index_cases: list[dict[str, Any]] = []
    shells: list[dict[str, Any]] = []
    for r in candidates:
        nr = r["normalized_response"] if isinstance(r["normalized_response"], dict) else {}
        sc = nr.get("day_scenario") if isinstance(nr.get("day_scenario"), dict) else {}
        ip = r["input_payload"] if isinstance(r["input_payload"], dict) else {}
        gen_id = int(r["id"])
        seed = f"live-ru-{gen_id}-{ip.get('target_date')}-{ip.get('prompt_version')}"
        case_id = new_neutral_case_id(seed=seed)
        personal = nr.get("day_personal") if isinstance(nr.get("day_personal"), dict) else {}
        depth = (
            "deep_personalized"
            if personal.get("summary_ru") or personal.get("personal_astrology")
            else "general_personalized"
            if sc.get("personalization") or sc.get("sphere_selection")
            else "general"
        )
        case = build_human_case_shell(
            case_id=case_id,
            scenario=sc,
            locale="ru",
            profile_type="live_registered_personal" if personal else "live_registered",
            evidence_depth=depth,
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
            "capture_slot": f"u{int(r['user_id']) % 97}",
        }
        blind = export_blind_review_packet(case)
        (cases_dir / f"{case_id}.json").write_text(
            json.dumps(case, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        (blind_dir / f"{case_id}.blind.json").write_text(
            json.dumps(blind, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        _write_sheet(blind, sheets_dir / f"{case_id}.md")
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
                json.dumps(tmpl, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )
        shells.append(case)
        index_cases.append(
            {
                "case_id": case_id,
                "locale": "ru",
                "source_type": "live_capture",
                "profile_type": case["profile_type"],
                "evidence_depth": case["evidence_depth"],
                "generation_source": sc.get("generation_source"),
                "theme": nr.get("theme"),
                "scene_count": len(sc.get("scenes") or []),
                "scenario_hash": case["scenario_hash"],
                "blind_path": f"blind/{case_id}.blind.json",
                "sheet_path": f"review_sheets/{case_id}.md",
                "case_path": f"cases/{case_id}.json",
            }
        )

    manifest = {
        "batch_id": batch_id,
        "export_kind": "c362_human_golden_ru_live_expansion",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "versions": version_bundle(),
        "case_count": len(index_cases),
        "excluded_hash_count": len(exclude),
        "duplicate_scenario_hashes": detect_duplicate_scenario_hashes(shells),
        "inventory_note": "RU live expansion toward 20 RU / 40 total (pilot 7 + this 13).",
        "cases": index_cases,
    }
    (out_root / "index.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out_root / "README.md").write_text(
        f"""# Human golden RU live expansion `{batch_id}`

Live RU captures excluding sealed pilot + EN batches.

## Status

| Role | State |
|------|--------|
| Reviewer A | pending |
| Reviewer B | pending |
| Seal | pending |

## Inventory

- Cases: **{len(index_cases)}** RU live
- Prior sealed: pilot 7 RU + EN 20 = 27 → this batch targets **40**
""",
        encoding="utf-8",
    )
    (out_root / "REVIEWER_B_INSTRUCTIONS.md").write_text(
        f"""# Reviewer B — `{batch_id}`

1. Open only `review_sheets/*.md` or `blind/*.json` + rubric.
2. Do **not** open `cases/` or `*.reviewer_a.json`.
3. Fill `reviewer_templates/<case_id>.reviewer_b.json`.
""",
        encoding="utf-8",
    )
    print(json.dumps({"ok": True, "batch_id": batch_id, "case_count": len(index_cases)}, ensure_ascii=False))


if __name__ == "__main__":
    main()

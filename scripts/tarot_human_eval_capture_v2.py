#!/usr/bin/env python3
"""Capture live Tarot answers into Human Golden Eval v2 fixture (unscored).

Editorial Phase only — does not invent human labels.

Usage (repo root):
  set -a && source .env && set +a
  PYTHONPATH=backend/src backend/.venv/bin/python scripts/tarot_human_eval_capture_v2.py --limit 2
  PYTHONPATH=backend/src backend/.venv/bin/python scripts/tarot_human_eval_capture_v2.py --write-fixture
  PYTHONPATH=backend/src backend/.venv/bin/python scripts/tarot_human_eval_capture_v2.py --worksheet docs/audits/TAROT_HUMAN_EVAL_V2_SCORECARD.md
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "backend" / "tests" / "fixtures" / "tarot_golden_dataset_v1.json"
FIXTURE = ROOT / "backend" / "tests" / "fixtures" / "tarot_golden_eval_human_v2.json"
SCHEMA = ROOT / "docs" / "schemas" / "tarot_golden_eval_human_v2.schema.json"


def _spread_from_scenario(sc: dict[str, Any]):
    from todayflow_backend.core import models

    cards = []
    for item in sc["cards"]:
        cards.append(
            models.TarotSpreadCard(
                card=models.TarotCard(
                    id=int(item["card_id"]),
                    name=f"Card {item['card_id']}",
                    keywords=[],
                    upright="",
                    reversed="",
                ),
                orientation=str(item.get("orientation") or "upright"),
                position=models.TarotSpreadPosition(
                    id=str(item["position_id"]),
                    title=str(item.get("title") or item["position_id"]),
                    prompt=str(item.get("title") or ""),
                ),
                meaning="",
            )
        )
    return models.TarotSpreadResult(
        spread_id=str(sc["spread_id"]),
        title=str(sc.get("label") or sc["id"]),
        cards=cards,
    )


def _card_name_ru(card_id: int) -> str | None:
    try:
        from todayflow_backend.services.tarot_knowledge_base_v1 import get_card_record_v1

        rec = get_card_record_v1(card_id)
        if not rec:
            return None
        return str(rec.get("name_ru") or rec.get("title_ru") or "") or None
    except Exception:
        return None


def _case_id(scenario_id: str) -> str:
    return f"hv2_ds_{scenario_id}"


def scenario_to_case(
    sc: dict[str, Any],
    interp: dict[str, str],
    *,
    prompt_version: str,
    model: str | None,
    captured_at: str,
) -> dict[str, Any]:
    cards_out = []
    for item in sc["cards"]:
        cid = int(item["card_id"])
        row: dict[str, Any] = {
            "card_id": cid,
            "orientation": str(item.get("orientation") or "upright"),
            "position_id": str(item["position_id"]),
            "title": str(item.get("title") or item["position_id"]),
        }
        name = _card_name_ru(cid)
        if name:
            row["name_ru"] = name
        cards_out.append(row)

    case: dict[str, Any] = {
        "id": _case_id(str(sc["id"])),
        "label": str(sc.get("label") or sc["id"]),
        "locale": "ru",
        "question": str(sc["question"]),
        "concern_domain": str(sc.get("concern_domain") or ""),
        "spread_id": str(sc["spread_id"]),
        "cards": cards_out,
        "answer": {
            "symbols_overview": str(interp.get("symbols_overview") or "").strip(),
            "question_story": str(interp.get("question_story") or "").strip(),
            "direct_answer": str(interp.get("direct_answer") or "").strip(),
            "next_step": str(interp.get("next_step") or "").strip(),
        },
        "capture": {
            "prompt_version": prompt_version,
            "synthesis_mode": "tarot_llm_v1",
            "source": "live_cli",
            "captured_at": captured_at,
        },
    }
    if model:
        case["capture"]["model"] = model
    return case


def merge_cases(existing: list[dict[str, Any]], new_cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_id = {c["id"]: c for c in existing}
    order = [c["id"] for c in existing]
    for case in new_cases:
        cid = case["id"]
        # Never overwrite a case that already has human scores.
        prev = by_id.get(cid)
        if prev and isinstance(prev.get("human"), dict) and prev["human"].get("scored_by"):
            continue
        if cid not in by_id:
            order.append(cid)
        by_id[cid] = case
    return [by_id[i] for i in order if i in by_id]


def write_worksheet(cases: list[dict[str, Any]], path: Path) -> None:
    lines = [
        "# Tarot Human Eval v2 — scorecard",
        "",
        "Ответь на три вопроса по каждому кейсу: `yes` · `partial` · `no`.",
        "",
        "| id | question | symbols? | answered? | would pay? | notes |",
        "|----|----------|----------|-----------|------------|-------|",
    ]
    for c in cases:
        q = (c.get("question") or "").replace("|", "/").replace("\n", " ")
        human = c.get("human") or {}
        scored = all(
            human.get(k) in {"yes", "partial", "no"}
            for k in ("understood_symbols", "answered_my_question", "would_pay")
        )
        if scored:
            a = human.get("understood_symbols")
            b = human.get("answered_my_question")
            w = human.get("would_pay")
            note = (human.get("editor_notes") or "")[:80]
        else:
            a = b = w = ""
            note = "⬜ score"
        lines.append(f"| `{c['id']}` | {q[:72]} | {a} | {b} | {w} | {note} |")
    lines.extend(
        [
            "",
            "## How to score",
            "",
            "1. Read `answer.symbols_overview` → `question_story` → `direct_answer` → `next_step` in the fixture.",
            "2. Fill the three columns (or patch `human` on the case in JSON).",
            "3. Optional voice flags: `antithesis_formula` · `sees_self` · `warmth_without_mush`.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Capture Human Golden Eval v2 cases from live LLM")
    parser.add_argument("--limit", type=int, default=0, help="Limit dataset scenarios")
    parser.add_argument("--ids", type=str, default="", help="Comma-separated dataset scenario ids")
    parser.add_argument("--write-fixture", action="store_true", help="Merge into human v2 fixture")
    parser.add_argument("--out", type=Path, help="Write capture JSON (default: docs/audits/…)")
    parser.add_argument("--worksheet", type=Path, help="Write markdown scorecard")
    parser.add_argument("--dry-run", action="store_true", help="Build cases from offline thin fallback")
    args = parser.parse_args()

    live = not args.dry_run
    if live:
        os.environ.setdefault("LLM_HTTP_TIMEOUT_SECONDS", "120")
        os.environ.setdefault("LLM_BACKGROUND_TIMEOUT_SECONDS", "180")

    sys.path.insert(0, str(ROOT / "backend" / "src"))
    from todayflow_backend.core.config import settings
    from todayflow_backend.services import tarot_interpretation_engine_v1 as engine
    from todayflow_backend.services import tarot_interpretation_llm_v1 as tarot_llm
    from todayflow_backend.services.tarot_interpretation_llm_v1 import TAROT_INTERPRETATION_PROMPT_VER

    payload = json.loads(DATASET.read_text(encoding="utf-8"))
    scenarios = list(payload.get("scenarios") or [])
    if args.ids.strip():
        wanted = {x.strip() for x in args.ids.split(",") if x.strip()}
        scenarios = [s for s in scenarios if s.get("id") in wanted]
    if args.limit > 0:
        scenarios = scenarios[: args.limit]

    model = getattr(settings, "nebius_model", None) or getattr(settings, "llm_default_model", None)
    captured_at = datetime.now(timezone.utc).date().isoformat()
    cases: list[dict[str, Any]] = []
    failures: list[str] = []

    print(f"human_eval_capture live={live} scenarios={len(scenarios)} prompt={TAROT_INTERPRETATION_PROMPT_VER}")

    for sc in scenarios:
        spread = _spread_from_scenario(sc)
        pack = engine.build_context_pack(
            spread,
            question=sc.get("question"),
            concern_domain=sc.get("concern_domain"),
            experience_slice=sc.get("profile") or {},
        )
        if not pack:
            failures.append(f"{sc['id']}:pack")
            print(f"- {sc['id']}: FAIL pack")
            continue
        if live:
            interp = tarot_llm.call_tarot_interpretation_llm_v1(pack)
            if not interp:
                failures.append(f"{sc['id']}:llm")
                print(f"- {sc['id']}: FAIL llm")
                continue
        else:
            interp = engine.thin_fallback_from_pack(pack)
            assert interp

        case = scenario_to_case(
            sc,
            interp,
            prompt_version=TAROT_INTERPRETATION_PROMPT_VER,
            model=str(model) if model else None,
            captured_at=captured_at,
        )
        # Drop empty answer fields early so schema stays honest
        ans = case["answer"]
        if min(len(ans[k]) for k in ans) < 8:
            failures.append(f"{sc['id']}:thin_answer")
            print(f"- {sc['id']}: FAIL thin_answer")
            continue
        cases.append(case)
        print(f"- {sc['id']}: ok → {case['id']} ({len(ans['direct_answer'])} chars answer)")

    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    out_path = args.out or (ROOT / "docs" / "audits" / f"TAROT_HUMAN_EVAL_V2_CAPTURE_{stamp}.json")
    capture_doc = {
        "contract_version": "tarot_golden_eval_human_v2",
        "notes": "Live capture for Human Eval v2. human scores intentionally absent — owner fills later.",
        "cases": cases,
        "failures": failures,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(capture_doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {out_path} cases={len(cases)} failures={len(failures)}")

    if args.write_fixture and cases:
        existing = json.loads(FIXTURE.read_text(encoding="utf-8"))
        merged = merge_cases(list(existing.get("cases") or []), cases)
        existing["cases"] = merged
        existing["notes"] = (
            "Human Golden Eval v2. Scored owner seed + live CLI captures (unscored until owner labels)."
        )
        FIXTURE.write_text(json.dumps(existing, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"merged fixture → {FIXTURE} total_cases={len(merged)}")
        try:
            import jsonschema

            schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
            jsonschema.validate(existing, schema)
            print("schema: ok")
        except Exception as exc:
            print(f"schema: FAIL {exc}")
            return 1

    worksheet_cases = cases
    if args.write_fixture and FIXTURE.exists():
        worksheet_cases = json.loads(FIXTURE.read_text(encoding="utf-8")).get("cases") or cases
    if args.worksheet:
        write_worksheet(worksheet_cases, args.worksheet)
        print(f"wrote worksheet {args.worksheet}")
    elif args.write_fixture:
        default_ws = ROOT / "docs" / "audits" / "TAROT_HUMAN_EVAL_V2_SCORECARD.md"
        write_worksheet(worksheet_cases, default_ws)
        print(f"wrote worksheet {default_ws}")

    return 1 if failures and not cases else 0


if __name__ == "__main__":
    raise SystemExit(main())

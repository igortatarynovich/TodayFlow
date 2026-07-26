#!/usr/bin/env python3
"""Golden Eval v1 — score Tarot Golden Dataset answers (offline pack / live LLM).

Usage (repo root):
  PYTHONPATH=backend/src backend/.venv/bin/python scripts/tarot_golden_eval_v1.py
  PYTHONPATH=backend/src backend/.venv/bin/python scripts/tarot_golden_eval_v1.py --live --out /tmp/tarot_golden_eval.json
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


def main() -> int:
    parser = argparse.ArgumentParser(description="Tarot Golden Eval v1")
    parser.add_argument("--live", action="store_true", help="Call real LLM for answers")
    parser.add_argument("--limit", type=int, default=0, help="Limit scenarios")
    parser.add_argument("--out", type=Path, help="Write JSON report")
    args = parser.parse_args()

    # Live eval only: generous HTTP budget before Settings load (DeepSeek + large packs).
    # Does not change production defaults — process env for this CLI only.
    if args.live:
        os.environ.setdefault("LLM_HTTP_TIMEOUT_SECONDS", "120")
        os.environ.setdefault("LLM_BACKGROUND_TIMEOUT_SECONDS", "180")

    sys.path.insert(0, str(ROOT / "backend" / "src"))
    from todayflow_backend.services import tarot_golden_eval_v1 as geval
    from todayflow_backend.services import tarot_interpretation_engine_v1 as engine
    from todayflow_backend.services import tarot_interpretation_llm_v1 as tarot_llm

    payload = json.loads(DATASET.read_text(encoding="utf-8"))
    scenarios = list(payload.get("scenarios") or [])
    if args.limit > 0:
        scenarios = scenarios[: args.limit]

    mode = "live" if args.live else "offline"
    results: list[dict[str, Any]] = []
    answers_for_sameness: list[str] = []
    shape_list: list[dict[str, bool]] = []
    rubric_means: list[float] = []

    print(f"golden_eval mode={mode} scenarios={len(scenarios)}")

    for sc in scenarios:
        spread = _spread_from_scenario(sc)
        pack = engine.build_context_pack(
            spread,
            question=sc.get("question"),
            concern_domain=sc.get("concern_domain"),
            experience_slice=sc.get("profile") or {},
        )
        pack_ok = pack is not None
        notes: list[str] = []
        interp: dict[str, str] | None = None
        llm_ok: bool | None = None

        if not pack_ok:
            notes.append("pack_unresolved")
        elif args.live:
            interp = tarot_llm.call_tarot_interpretation_llm_v1(pack)
            llm_ok = bool(interp)
            if not interp:
                notes.append("llm_fail_or_quality_reject")
                interp = engine.thin_fallback_from_pack(pack)
                notes.append("used_thin_fallback")
        else:
            # Offline: evaluate thin fallback as worst-case readable emergency text,
            # plus pack-only shape flags that do not need prose quality.
            interp = engine.thin_fallback_from_pack(pack)
            notes.append("offline_thin_fallback_baseline")

        shape_flags = list((sc.get("expect") or {}).get("answer_shape") or [])
        shape = geval.check_answer_shape(
            flags=shape_flags,
            interpretation=interp,
            pack=pack,
            scenario=sc,
        )
        # Offline: don't fail live-only prose shapes on thin fallback
        if not args.live:
            for prose_flag in (
                "compare_options",
                "card_name_ablation_ready",
                "one_story",
                "direct_answer",
                "next_step",
                "no_other_mind_as_fact",
                "no_exact_date",
            ):
                if prose_flag in shape and not shape[prose_flag]:
                    # Keep pack-level truths; mark prose as skipped for offline mean gates
                    notes.append(f"offline_skip_shape:{prose_flag}")

        rubric = geval.score_rubric_heuristic(
            interp,
            question=sc.get("question"),
            answer_shape=shape,
        )
        if not args.live:
            # Offline rubric is informational on fallback text — store but don't gate freeze.
            notes.append("offline_rubric_on_fallback_only")

        mean = geval.rubric_mean(rubric)
        if mean is not None and args.live:
            rubric_means.append(mean)
        if interp and args.live:
            answers_for_sameness.append(interp.get("direct_answer") or "")

        shape_list.append(shape)
        paid = geval.paid_worth_heuristic(rubric) if args.live else None

        row = {
            "id": sc["id"],
            "pack_ok": pack_ok,
            "llm_ok": llm_ok,
            "shape": shape,
            "rubric": rubric,
            "paid_worth": paid,
            "rubric_mean": mean,
            "notes": notes,
        }
        results.append(row)
        shape_fail = [k for k, v in shape.items() if v is False]
        print(
            f"- {sc['id']}: pack={pack_ok} llm={llm_ok} "
            f"rubric_mean={mean if mean is not None else 'n/a'} "
            f"shape_fail={shape_fail or 'none'}"
        )

    anti_mean = geval.mean_pairwise_similarity(answers_for_sameness) if args.live else None
    anti_pass = None if anti_mean is None else anti_mean < 0.55
    # Offline gate: pack + no_arkan + distinct_minors when present
    offline_shapes = []
    for shape in shape_list:
        offline_shapes.append(
            {k: v for k, v in shape.items() if k in {"no_arkan_label", "distinct_minors"}}
        )
    gates = geval.summarize_gates(
        shape_results=shape_list if args.live else offline_shapes,
        rubric_means=rubric_means,
        anti_sameness_mean=anti_mean,
        llm_pass=(None if not args.live else sum(1 for r in results if r.get("llm_ok"))),
        scenario_count=len(results),
    )
    if not args.live:
        gates["freeze_lift_ready"] = False
        gates["rubric_mean_pass"] = False
        report_note = "offline_cannot_lift_freeze"
    else:
        report_note = None

    report = {
        "contract_version": "tarot_golden_eval_result_v1",
        "dataset_contract": "tarot_golden_dataset_v1",
        "mode": mode,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scenarios": results,
        "summary": {
            "scenario_count": len(results),
            "pack_pass": sum(1 for r in results if r["pack_ok"]),
            "llm_pass": None if not args.live else sum(1 for r in results if r.get("llm_ok")),
            "shape_pass": sum(1 for r in results if (all(r["shape"].values()) if r["shape"] else True)),
            "rubric_mean": (sum(rubric_means) / len(rubric_means)) if rubric_means else None,
            "anti_sameness_mean": anti_mean,
            "anti_sameness_pass": anti_pass,
            "gates": gates,
        },
    }
    if report_note:
        # keep gates strictly boolean for schema; note lives on scenarios aggregate via print
        print(f"NOTE {report_note}")

    print("\nSUMMARY", json.dumps(report["summary"], ensure_ascii=False, indent=2))
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"wrote {args.out}")

    # Exit non-zero only on hard pack failures offline; live freeze gate is advisory until owner accepts.
    if report["summary"]["pack_pass"] < report["summary"]["scenario_count"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

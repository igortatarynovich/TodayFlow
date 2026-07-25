#!/usr/bin/env python3
"""Live / offline eval for Tarot Interpretation Engine scenarios.

Usage (from repo root):
  PYTHONPATH=backend/src backend/.venv/bin/python scripts/tarot_interpretation_live_eval.py
  PYTHONPATH=backend/src backend/.venv/bin/python scripts/tarot_interpretation_live_eval.py --live

Without --live: builds Context Packs and prints pack richness + offline gate smoke.
With --live: calls LLM (requires configured chat provider) and prints scored readings.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "backend/tests/fixtures/tarot_interpretation_scenarios_v1.json"


def _load_scenarios() -> list[dict]:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def _spread_from_scenario(sc: dict):
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


def _pack_score(pack: dict) -> list[str]:
    issues: list[str] = []
    if not pack.get("question"):
        issues.append("missing_question")
    cards = pack.get("cards") or []
    if not cards:
        issues.append("no_cards")
    for card in cards:
        rng = card.get("meaning_range") or {}
        for key in ("central_symbol", "light_side", "shadow_side", "upright_themes", "reversed_themes"):
            if not rng.get(key):
                issues.append(f"card_{card.get('card_id')}_missing_{key}")
        if not card.get("question_lens"):
            issues.append(f"card_{card.get('card_id')}_missing_question_lens")
        if not card.get("position_role"):
            issues.append(f"card_{card.get('card_id')}_missing_role")
    return issues


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true", help="Call real LLM")
    parser.add_argument("--limit", type=int, default=0, help="Limit scenarios")
    args = parser.parse_args()

    sys.path.insert(0, str(ROOT / "backend/src"))
    from todayflow_backend.services import tarot_interpretation_engine_v1 as engine
    from todayflow_backend.services import tarot_interpretation_llm_v1 as tarot_llm

    scenarios = _load_scenarios()
    if args.limit > 0:
        scenarios = scenarios[: args.limit]

    print(f"scenarios={len(scenarios)} live={args.live}")
    failures = 0
    for sc in scenarios:
        spread = _spread_from_scenario(sc)
        pack = engine.build_context_pack(
            spread,
            question=sc.get("question"),
            concern_domain=sc.get("concern_domain"),
            experience_slice={
                "decision_style": "Сверяется с телом, потом фиксирует выбор",
                "motivation": "Нужна стабильность без потери смысла",
                "communication_style": "Коротко и по делу",
                "conflict_style": "Сначала пауза, потом ясная формулировка",
            },
        )
        print("\n===", sc["id"], "|", sc.get("label"))
        if pack is None:
            print("PACK FAIL unresolved")
            failures += 1
            continue
        issues = _pack_score(pack)
        print(
            "pack_ok" if not issues else f"pack_issues={issues}",
            "| domain=",
            pack.get("question_domain"),
            "| profile_keys=",
            list((pack.get("profile_relevant") or {}).keys()),
        )
        if issues:
            failures += 1

        if not args.live:
            fb = engine.thin_fallback_from_pack(pack)
            assert "Не удалось собрать полноценную интерпретацию" in fb["direct_answer"]
            continue

        interp = tarot_llm.call_tarot_interpretation_llm_v1(pack)
        if not interp:
            print("LLM FAIL / quality reject")
            failures += 1
            continue
        print("ANSWER:", interp["direct_answer"][:220])
        print("STEP:", interp["next_step"][:180])
        print("SYMBOLS:", interp["symbols_overview"][:180])

    print(f"\nDONE failures={failures}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())

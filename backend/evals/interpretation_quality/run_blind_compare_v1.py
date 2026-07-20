#!/usr/bin/env python3
"""Blind day_story quality compare: DeepSeek-V4-Pro vs Kimi-K2.6.

Usage (from backend container):
  PYTHONPATH=src python evals/interpretation_quality/run_blind_compare_v1.py --limit 6

Writes under evals/interpretation_quality/runs/:
  - results_raw_<ts>.jsonl  (model-tagged)
  - results_blind_<ts>.json (A/B for human scoring)
"""

from __future__ import annotations

import argparse
import json
import random
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from todayflow_backend.core.llm_openai_compatible import (  # noqa: E402
    chat_completion_plain,
    get_openai_compatible_client,
    resolve_max_tokens,
)
from todayflow_backend.services.day_narrative_brief_v0 import (  # noqa: E402
    build_day_narrative_brief_v0,
    slim_day_engine_brief_for_story_llm,
)
from todayflow_backend.services.day_story_v1 import (  # noqa: E402
    DAY_STORY_PROMPT_VER,
    _DAY_STORY_SYS_RU,
    build_day_story_llm_input,
)


MODELS = [
    "deepseek-ai/DeepSeek-V4-Pro",
    "moonshotai/Kimi-K2.6",
]


def _scenario_to_llm_input(sc: dict) -> dict:
    ritual: dict = {
        "mood": sc.get("mood"),
        "head_topic": (sc.get("goals") or ["день"])[0] if sc.get("goals") else "день",
    }
    rev = sc.get("reveal") or {}
    if rev.get("card") and sc.get("card_id"):
        ritual["tarot_main_id"] = sc["card_id"]
        ritual["tarot_name_ru"] = sc["card_id"]
    if rev.get("number") and sc.get("number") is not None:
        ritual["numerology_value"] = str(sc["number"])

    profile = sc.get("profile") or {}
    fields = profile.get("fields") or {}
    brief = build_day_narrative_brief_v0(
        foundation={
            "spine": {
                "day_axis": fields.get("sun") or "день",
                "first_move": "держи фокус на одном шаге",
            }
        },
        ritual=ritual,
        fusion_scores={"energy": 50},
        intent_slice={"what_matters_line": "; ".join(sc.get("goals") or []) or None},
        locale=sc.get("locale") or "ru",
    )
    safe_ritual = {k: v for k, v in ritual.items() if v not in (None, "", [])}
    story_brief = slim_day_engine_brief_for_story_llm(
        brief,
        ritual_has_card=bool(safe_ritual.get("tarot_main_id") or safe_ritual.get("tarot_name_ru")),
        ritual_has_number=safe_ritual.get("numerology_value") is not None,
    )
    return build_day_story_llm_input(
        day_engine_brief=story_brief,
        ritual_context=safe_ritual,
        user_core_slim={
            "display_name": fields.get("name"),
            "sun_sign": fields.get("sun"),
            "moon_sign": fields.get("moon"),
            "ascendant": fields.get("asc"),
        },
        intent_slice={"goals": sc.get("goals") or []},
        behavior_patterns=None,
        rhythm_context={"goals": sc.get("goals") or []},
        locale=sc.get("locale") or "ru",
    )


def _extract_json_obj(raw: str) -> dict | None:
    text = (raw or "").strip()
    if not text:
        return None
    if text.startswith("```"):
        text = text.split("\n", 1)[-1]
        if text.rstrip().endswith("```"):
            text = text.rstrip()[:-3].rstrip()
    try:
        obj = json.loads(text)
        return obj if isinstance(obj, dict) else None
    except Exception:
        pass
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        try:
            obj = json.loads(text[start : end + 1])
            return obj if isinstance(obj, dict) else None
        except Exception:
            return None
    return None


def _call_model(client, model: str, llm_input: dict) -> tuple[str, dict]:
    t0 = time.perf_counter()
    max_tok = resolve_max_tokens(1800, model=model)
    raw = (
        chat_completion_plain(
            client,
            model=model,
            messages=[
                {"role": "system", "content": _DAY_STORY_SYS_RU},
                {
                    "role": "user",
                    "content": json.dumps(llm_input, ensure_ascii=False)[:12000],
                },
            ],
            temperature=0.52,
            max_tokens=max_tok,
        )
        or ""
    )
    latency_ms = int((time.perf_counter() - t0) * 1000)
    parsed = _extract_json_obj(raw)
    ok = isinstance(parsed, dict) and bool(parsed.get("story") or parsed.get("theme"))
    theme = str((parsed or {}).get("theme") or "")
    story = str((parsed or {}).get("story") or "") or raw[:800]
    meta = {
        "latency_ms": latency_ms,
        "chars": len(raw),
        "max_tokens": max_tok,
        "theme": theme,
        "story_preview": story[:400],
        "prompt_version": DAY_STORY_PROMPT_VER,
        "ok_json": ok,
        "truncated_hint": (not ok) and raw.strip().startswith("{") and not raw.rstrip().endswith("}"),
    }
    return raw, meta


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=6)
    ap.add_argument(
        "--scenarios",
        default=str(Path(__file__).parent / "scenarios_v1.json"),
    )
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    client = get_openai_compatible_client()
    if client is None:
        print("ERROR: LLM client unavailable (check NEBIUS_API_KEY / provider)", file=sys.stderr)
        return 2

    data = json.loads(Path(args.scenarios).read_text(encoding="utf-8"))
    scenarios = data["scenarios"][: args.limit]
    rng = random.Random(args.seed)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = Path(__file__).parent / "runs"
    out_dir.mkdir(parents=True, exist_ok=True)
    raw_path = out_dir / f"results_raw_{ts}.jsonl"
    blind_path = out_dir / f"results_blind_{ts}.json"

    blind_items = []
    with raw_path.open("w", encoding="utf-8") as raw_f:
        for sc in scenarios:
            llm_input = _scenario_to_llm_input(sc)
            metas: dict = {}
            for model in MODELS:
                try:
                    raw, meta = _call_model(client, model, llm_input)
                except Exception as exc:  # noqa: BLE001
                    raw, meta = "", {
                        "ok_json": False,
                        "error": str(exc),
                        "latency_ms": 0,
                        "theme": "",
                        "story_preview": "",
                    }
                metas[model] = meta
                raw_f.write(
                    json.dumps(
                        {
                            "scenario_id": sc["id"],
                            "model": model,
                            "meta": meta,
                            "output": raw[:6000],
                            "groups": sc.get("group"),
                        },
                        ensure_ascii=False,
                    )
                    + "\n"
                )
                raw_f.flush()
                print(
                    f"{sc['id']} {model}: ok={meta.get('ok_json')} "
                    f"{meta.get('latency_ms')}ms err={meta.get('error', '')}"
                )

            order = MODELS[:]
            rng.shuffle(order)
            mapping = {"A": order[0], "B": order[1]}
            blind_items.append(
                {
                    "scenario_id": sc["id"],
                    "groups": sc.get("group"),
                    "locale": sc.get("locale"),
                    "reveal": sc.get("reveal"),
                    "mood": sc.get("mood"),
                    "goals": sc.get("goals"),
                    "A": {
                        "theme": metas[mapping["A"]].get("theme"),
                        "story_preview": metas[mapping["A"]].get("story_preview"),
                        "latency_ms": metas[mapping["A"]].get("latency_ms"),
                        "ok_json": metas[mapping["A"]].get("ok_json"),
                    },
                    "B": {
                        "theme": metas[mapping["B"]].get("theme"),
                        "story_preview": metas[mapping["B"]].get("story_preview"),
                        "latency_ms": metas[mapping["B"]].get("latency_ms"),
                        "ok_json": metas[mapping["B"]].get("ok_json"),
                    },
                    "_key": mapping,
                    "score_sheet": {
                        "prefer": None,
                        "shippable_A": None,
                        "shippable_B": None,
                        "notes": "",
                    },
                }
            )

    blind_path.write_text(
        json.dumps(
            {
                "protocol": "blind A/B — model names in _key for unblinding after scoring",
                "prompt_version": DAY_STORY_PROMPT_VER,
                "models": MODELS,
                "count": len(blind_items),
                "items": blind_items,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"wrote {raw_path}")
    print(f"wrote {blind_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

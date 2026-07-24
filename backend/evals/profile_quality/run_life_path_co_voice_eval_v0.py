#!/usr/bin/env python3
"""Life Path co-voice eval — matrix A/B/C/D × 2 runs (identity step).

Fail conditions (release gate):
  F1 — claimed LP not detectable in any field
  F2 — LP9 in B not distinct (reserved; detector enforces distinctness inside F1)
  F3 — A ≈ C (same natal, different LP) with no theme shift
  F4 — both B and D fail F1 (strong natal silences any LP)

Usage (LLM required):
  docker compose exec -T backend python evals/profile_quality/run_life_path_co_voice_eval_v0.py
  # or from backend venv with cwd=backend and PYTHONPATH=src
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) > 2 else Path("/app")
SRC = ROOT / "src"
if SRC.is_dir() and str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from todayflow_backend.services.life_path_visibility_v0 import (  # noqa: E402
    IDENTITY_FIELDS,
    detect_life_path_visibility,
    themes_shift,
)
from todayflow_backend.services.profile_disclosure_funnel_v0 import (  # noqa: E402
    _call_with_retry,
    _identity_ok,
    _repair_identity_life_path_co_voice,
    build_shared_profile_input,
)

RUNS_DIR = Path(__file__).resolve().parent / "runs"
if not RUNS_DIR.parent.exists():
    RUNS_DIR = Path("/tmp/life_path_co_voice_runs")
NATAL_SOFT = {"sun": "Pisces", "moon": "Cancer", "asc": "Virgo"}
NATAL_STRONG = {"sun": "Aries", "moon": "Capricorn", "asc": "Leo"}

CASES = {
    "A": {**NATAL_SOFT, "life_path": 9},
    "B": {**NATAL_STRONG, "life_path": 9},
    "C": {**NATAL_SOFT, "life_path": 1},
    "D": {**NATAL_STRONG, "life_path": 1},
}


def _user_json(case_id: str, *, sun: str, moon: str, asc: str, life_path: int) -> dict[str, Any]:
    return {
        "person": {
            "display_name": "Мария",
            "birth_date": "1990-03-14",
            "birth_time": "07:15",
            "birth_place": "Краснодар",
        },
        "astro": {"sun_sign": sun, "moon_sign": moon, "ascendant_sign": asc},
        "natal": {
            "summary": {
                "positions": [
                    {"body": "sun", "sign": sun},
                    {"body": "moon", "sign": moon},
                    {"body": "ascendant", "sign": asc},
                ]
            }
        },
        "numerology": {"life_path": life_path},
        "baseline": {"archetype_label": "Seeker"},
        "locale": "ru",
        "profile_hash": f"lp-co-voice-{case_id}",
    }


def run_identity(case_id: str, spec: dict[str, Any], *, temperature: float = 0.35) -> dict[str, Any]:
    user_json = _user_json(case_id, **spec)
    shared = build_shared_profile_input(user_json)
    result, meta = _call_with_retry(
        prompt_id="profile.identity.v1",
        locale="ru",
        user_payload={"shared": shared, "step": "identity"},
        depth_level="normal",
        ok_fn=_identity_ok,
        temperature=temperature,
    )
    repair_meta = None
    if result:
        result, repair_meta = _repair_identity_life_path_co_voice(
            shared=shared,
            locale="ru",
            draft=result,
        )
    det = detect_life_path_visibility(result or {}, int(spec["life_path"]), fields=IDENTITY_FIELDS)
    return {
        "case": case_id,
        "inputs": spec,
        "ok": bool(result),
        "ms": meta.get("ms"),
        "prompt_version": meta.get("prompt_version"),
        "repaired": bool(repair_meta and repair_meta.get("repair")),
        "repair_visible": (repair_meta or {}).get("repair_visible"),
        "result": result,
        "visibility": det,
        "f1_fail": not bool(det.get("visible")),
    }


def evaluate_matrix(pass_results: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    """Aggregate fail conditions across runs (a case fails F1 if ANY run fails F1)."""
    def any_f1(cid: str) -> bool:
        return any(r.get("f1_fail") for r in pass_results.get(cid, []))

    f1 = {cid: any_f1(cid) for cid in CASES}
    # F3: for each run index, compare A vs C theme shift; fail if any paired run lacks shift
    f3 = False
    a_runs = pass_results.get("A") or []
    c_runs = pass_results.get("C") or []
    for i in range(min(len(a_runs), len(c_runs))):
        ra, rc = a_runs[i].get("result") or {}, c_runs[i].get("result") or {}
        if not themes_shift(
            ra,
            rc,
            fields=("recognition_line", "identity_core", "strengths", "growth_zones"),
        ):
            f3 = True
            break

    f4 = f1.get("B") and f1.get("D")
    fails = {
        "F1": {k: v for k, v in f1.items() if v},
        "F3_A_approx_C": f3,
        "F4_natal_silences_any_lp": bool(f4),
    }
    # Release: no F1 on A/B/C/D, no F3, no F4
    release_ok = (
        not any(f1.values())
        and not f3
        and not f4
    )
    return {"fails": fails, "f1_by_case": f1, "release_ok": release_ok}


def main() -> int:
    runs_per_case = 2
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = RUNS_DIR / f"life_path_co_voice_{stamp}"
    out_dir.mkdir(parents=True, exist_ok=True)

    pack: dict[str, list[dict[str, Any]]] = {cid: [] for cid in CASES}
    for run_i in range(1, runs_per_case + 1):
        for cid, spec in CASES.items():
            print(f"run={run_i} case={cid} lp={spec['life_path']} …", flush=True)
            row = run_identity(cid, spec)
            row["run"] = run_i
            pack[cid].append(row)
            (out_dir / f"case_{cid}_run{run_i}.json").write_text(
                json.dumps(row, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            vis = "VISIBLE" if not row["f1_fail"] else "F1_FAIL"
            print(f"  → {vis} fields={row['visibility'].get('visible_fields')}", flush=True)

    summary = evaluate_matrix(pack)
    summary["stamp"] = stamp
    summary["runs_per_case"] = runs_per_case
    (out_dir / "summary.json").write_text(
        json.dumps({"summary": summary, "pack_keys": list(pack.keys())}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2), flush=True)
    return 0 if summary["release_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

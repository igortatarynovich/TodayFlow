#!/usr/bin/env python3
"""Production-faithful Profile capture harness (sidecar packs).

Runs the *same* production path as portrait publish:
  build_profile_portrait_v1 → funnel 4 steps → quality → contract/legacy shims

Does NOT:
  - change prompts / frame / Snapshot schema / UI
  - write personal prompts into generation_logs
  - invent an alternate funnel

Off by default: only records when entered via profile_capture_session.

Usage:
  python evals/profile_quality/run_production_capture_v0.py --cases pq-001,pq-007
  python evals/profile_quality/run_production_capture_v0.py --cases A,B --redact
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
REPO = ROOT.parent
sys.path.insert(0, str(ROOT / "src"))

# Eval/capture-only HTTP budget for DeepSeek multi-step funnel.
# Does NOT change production Settings defaults — only process env for this CLI.
# Override with LLM_HTTP_TIMEOUT_SECONDS / LLM_BACKGROUND_TIMEOUT_SECONDS if needed.
os.environ.setdefault("LLM_HTTP_TIMEOUT_SECONDS", "120")
os.environ.setdefault("LLM_BACKGROUND_TIMEOUT_SECONDS", "180")

from todayflow_backend.services.profile_capture_session_v0 import (  # noqa: E402
    profile_capture_session,
)
from todayflow_backend.services.profile_content_v1.architecture import (  # noqa: E402
    classify_allowed_claims,
)
from todayflow_backend.services.profile_content_v1.source_depth import (  # noqa: E402
    depth_from_scenario,
)
from todayflow_backend.services.profile_contract_v1 import (  # noqa: E402
    build_profile_portrait_v1,
)

CASE_ALIASES = {
    "A": "pq-001",
    "B": "pq-007",
    "case-a": "pq-001",
    "case-b": "pq-007",
    "birth-only": "pq-001",
    "longitudinal": "pq-007",
    # life_spheres Freeze captures (block passport)
    "spheres-A": "spheres-freeze-A",
    "spheres-B": "spheres-freeze-B",
    "spheres-C": "spheres-freeze-C",
    "SA": "spheres-freeze-A",
    "SB": "spheres-freeze-B",
    "SC": "spheres-freeze-C",
}

DEFAULT_CASES = ("pq-001", "pq-007")


def _load_scenarios() -> dict[str, dict[str, Any]]:
    path = Path(__file__).resolve().parent / "scenarios_v1.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    return {s["id"]: s for s in data.get("scenarios") or []}


def _scenario_to_profile_input(sc: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any] | None]:
    living = sc.get("living")
    if sc.get("onboarding"):
        living = dict(living or {})
        living["onboarding"] = sc["onboarding"]
        living.setdefault("summary", living.get("summary") or "Есть ответы онбординга.")
    person = dict(sc.get("person") or {})
    person.setdefault("locale", sc.get("locale") or "ru")
    if sc.get("birth_date"):
        person.setdefault("birth_date", sc["birth_date"])
    if sc.get("birth_time") is not None:
        person.setdefault("birth_time", sc.get("birth_time"))
    if "time_unknown" in sc or sc.get("birth_time") in (None, ""):
        person.setdefault("time_unknown", True if sc.get("birth_time") in (None, "") else bool(sc.get("time_unknown")))
    natal = sc.get("natal") if isinstance(sc.get("natal"), dict) else {}
    profile_input = {
        "profile_version": "capture_v0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "is_ready": True,
        "missing_fields": list(sc.get("missing_or_hidden") or []),
        "profile_hash": f"capture-{sc['id']}",
        "person": person,
        "astro": sc.get("astro") or {},
        "natal": natal,
        "numerology": sc.get("numerology") or {},
        "baseline": sc.get("baseline") or {},
        "profiles": {},
    }
    return profile_input, living if isinstance(living, dict) else living


def _assemble_snapshot_like_payload(
    *,
    profile_input: dict[str, Any],
    living: dict[str, Any] | None,
    contract: dict[str, Any],
    interpretation: dict[str, Any],
    daily: dict[str, Any],
) -> dict[str, Any]:
    """Mirror CoreProfileService publish payload shape (no DB write)."""
    return {
        "profile_version": profile_input.get("profile_version"),
        "generated_at": profile_input.get("generated_at"),
        "is_ready": profile_input.get("is_ready"),
        "missing_fields": profile_input.get("missing_fields") or [],
        "profile_hash": profile_input.get("profile_hash"),
        "person": profile_input.get("person"),
        "astro": profile_input.get("astro"),
        "numerology": profile_input.get("numerology"),
        "baseline": profile_input.get("baseline"),
        "profiles": profile_input.get("profiles") or {},
        "profile_contract_v1": contract,
        "interpretation": interpretation,
        "daily_interpretation": daily,
        "living": living,
        "capture_note": "assembled_without_db; shape matches CoreProfileService._publish_portrait",
    }


def _resolve_node_bin() -> str | None:
    import shutil

    candidates = [
        os.environ.get("NODE_BIN"),
        "node",
        "/usr/local/bin/node",
        "/usr/bin/node",
    ]
    # Cursor/server node (dev hosts without system node)
    cursor_root = Path("/root/.cursor-server/bin")
    if cursor_root.is_dir():
        cursor_nodes = sorted(cursor_root.glob("linux-*/**/node"))
        candidates.extend(str(p) for p in cursor_nodes[-3:])
    for c in candidates:
        if not c:
            continue
        if str(c).startswith("/"):
            path = Path(c)
            if path.is_file() and os.access(path, os.X_OK):
                return str(path)
            continue
        resolved = shutil.which(str(c))
        if resolved:
            return resolved
    return None


def _run_fe_projection(pack_path: Path, *, skip: bool) -> dict[str, Any] | None:
    if skip:
        return None
    script = REPO / "frontend" / "scripts" / "run_profile_capture_projection.mjs"
    if not script.is_file():
        return {"error": "fe_harness_missing", "path": str(script)}
    node = _resolve_node_bin()
    if not node:
        return {"error": "node_not_found"}
    env = {
        **os.environ,
        "PATH": f"{REPO / 'frontend' / 'node_modules' / '.bin'}:{os.environ.get('PATH', '')}",
    }
    try:
        proc = subprocess.run(
            [node, str(script), str(pack_path)],
            cwd=str(REPO / "frontend"),
            capture_output=True,
            text=True,
            timeout=180,
            check=False,
            env=env,
        )
    except FileNotFoundError:
        return {"error": "node_not_found", "node": node}
    except subprocess.TimeoutExpired:
        return {"error": "fe_projection_timeout"}
    if proc.returncode != 0:
        return {
            "error": "fe_projection_failed",
            "stdout": (proc.stdout or "")[-2000:],
            "stderr": (proc.stderr or "")[-2000:],
        }
    try:
        return json.loads(proc.stdout.strip().splitlines()[-1])
    except json.JSONDecodeError:
        return {"error": "fe_projection_bad_json", "stdout": (proc.stdout or "")[-2000:]}


def run_case(
    sc: dict[str, Any],
    *,
    out_dir: Path,
    redact: bool,
    skip_fe: bool,
) -> Path | None:
    case_id = sc["id"]
    depth = depth_from_scenario(sc)
    allowed = classify_allowed_claims(depth)
    profile_input, living = _scenario_to_profile_input(sc)
    locale = str(sc.get("locale") or "ru")

    with profile_capture_session(
        case_id=case_id,
        label=str(sc.get("label") or ""),
        redact=redact,
        out_dir=out_dir,
    ) as session:
        session.set_inputs(
            inputs={
                "scenario_id": case_id,
                "person": profile_input.get("person"),
                "astro": profile_input.get("astro"),
                "natal": profile_input.get("natal"),
                "numerology": profile_input.get("numerology"),
                "baseline": profile_input.get("baseline"),
                "living": living,
                "locale": locale,
                "profile_hash": profile_input.get("profile_hash"),
                "birth_date": sc.get("birth_date"),
                "checkin_days": sc.get("checkin_days"),
                "longitudinal_days": sc.get("longitudinal_days"),
            },
            calculated_facts={
                "astro": profile_input.get("astro"),
                "natal": profile_input.get("natal"),
                "numerology": profile_input.get("numerology"),
                "baseline": profile_input.get("baseline"),
            },
            source_depth=depth,
            missing_fields=list(sc.get("missing_or_hidden") or []),
            allowed_claims=allowed,
        )
        # Formal defect seed (known architectural conflict) — capture proves/disproves.
        if depth == "birth_data_only":
            session.add_defect(
                "invariant_patterns_schema_vs_source_depth",
                "patterns step is invoked and RESPONSE_SCHEMA/_patterns_ok require "
                "recurring_patterns + living_changes even when source_depth=birth_data_only. "
                "Correct design: do not generate the block — not 'ask model not to invent'.",
                cls="GENERATION_GATE",
            )
            session.add_defect(
                "invariant_patterns_required_fields_without_evidence",
                "step validator requires filled recurring_patterns/living_changes without evidence.",
                cls="RESPONSE_SCHEMA",
            )

        contract, interpretation, daily, used_fallback = build_profile_portrait_v1(
            profile_input=profile_input,
            living=living,
            locale=locale,
        )
        snapshot = _assemble_snapshot_like_payload(
            profile_input=profile_input,
            living=living,
            contract=contract,
            interpretation=interpretation,
            daily=daily,
        )
        session.record_snapshot(snapshot, persisted=False)
        # GET body ≈ publish return without natal attach (eval has no DB natal).
        session.record_get_response(snapshot)
        session.pack["generation_metadata"] = {
            **(session.pack.get("generation_metadata") or {}),
            "used_forming_fallback": used_fallback,
            "entry": "build_profile_portrait_v1",
            "production_faithful": True,
            "db_publish": False,
        }

        pack_path = session.write()
        if pack_path is None:
            return None

        fe = _run_fe_projection(pack_path, skip=skip_fe)
        if fe is not None:
            # reopen pack and attach FE layers
            pack = json.loads(pack_path.read_text(encoding="utf-8"))
            if fe.get("error"):
                pack["frontend_projection"] = None
                pack["visible_blocks"] = None
                pack.setdefault("defects", []).append(
                    {
                        "code": "fe_projection_failed",
                        "class": "PROJECTION",
                        "detail": json.dumps(fe, ensure_ascii=False)[:500],
                    }
                )
            else:
                pack["frontend_projection"] = fe.get("frontend_projection")
                pack["visible_blocks"] = fe.get("visible_blocks")
                for div in fe.get("divergences") or []:
                    pack.setdefault("divergences", []).append(div)
            pack_path.write_text(json.dumps(pack, ensure_ascii=False, indent=2), encoding="utf-8")
            # refresh md summary lightly
            md = pack_path.with_suffix(".md")
            if md.is_file():
                extra = [
                    "",
                    "## Frontend projection",
                    f"- ok: {not bool(fe.get('error'))}",
                    f"- visible_blocks keys: {list((pack.get('visible_blocks') or {}).keys())}",
                    "",
                ]
                md.write_text(md.read_text(encoding="utf-8") + "\n".join(extra), encoding="utf-8")
        return pack_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Production-faithful Profile capture packs")
    parser.add_argument(
        "--cases",
        default=",".join(DEFAULT_CASES),
        help="Comma-separated scenario ids or aliases A/B (default: pq-001,pq-007)",
    )
    parser.add_argument(
        "--out",
        default="",
        help="Output directory (default: evals/profile_quality/runs/capture_<UTC>/)",
    )
    parser.add_argument("--redact", action="store_true", help="Redact name/date/geo in pack")
    parser.add_argument("--skip-fe", action="store_true", help="Skip frontend QuickMap projection")
    args = parser.parse_args()

    scenarios = _load_scenarios()
    raw_ids = [x.strip() for x in args.cases.split(",") if x.strip()]
    case_ids = [CASE_ALIASES.get(x, x) for x in raw_ids]

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = Path(args.out) if args.out else (Path(__file__).resolve().parent / "runs" / f"capture_{stamp}")
    out_dir.mkdir(parents=True, exist_ok=True)

    index: list[dict[str, Any]] = []
    for cid in case_ids:
        sc = scenarios.get(cid)
        if not sc:
            print(f"unknown case: {cid}", file=sys.stderr)
            index.append({"case_id": cid, "error": "unknown_scenario"})
            continue
        print(f"capture {cid} → {out_dir}")
        path = run_case(sc, out_dir=out_dir, redact=bool(args.redact), skip_fe=bool(args.skip_fe))
        index.append({"case_id": cid, "pack": str(path) if path else None})

    (out_dir / "index.json").write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"out_dir": str(out_dir), "cases": index}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Eval: profile.spheres.synthesis.v1 on life_spheres quality cases.

Pipeline per sphere:
  eligibility → sphere_cues → synthesis prompt → validate → compare projector

Usage:
  cd backend && .venv/bin/python evals/profile_quality/run_life_spheres_synthesis_eval_v0.py
  cd backend && .venv/bin/python evals/profile_quality/run_life_spheres_synthesis_eval_v0.py --dry-run
  cd backend && .venv/bin/python evals/profile_quality/run_life_spheres_synthesis_eval_v0.py --repeats 2
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from todayflow_backend.core.llm_openai_compatible import (  # noqa: E402
    chat_completion_text,
    get_openai_compatible_client,
    resolve_default_chat_model,
)
from todayflow_backend.core.config import settings  # noqa: E402
from todayflow_backend.prompts.profile_spheres_synthesis_v1 import (  # noqa: E402
    format_synthesis_user_message,
)
from todayflow_backend.prompts.registry_v1 import get_prompt  # noqa: E402
from todayflow_backend.services.life_spheres_cues_v0 import (  # noqa: E402
    SPHERE_CONTRACTS,
    build_sphere_cues,
)
from todayflow_backend.services.life_spheres_projector_v0 import (  # noqa: E402
    project_life_spheres_v0,
    spheres_projection_allowed,
)
from todayflow_backend.services.life_spheres_synthesis_validate_v0 import (  # noqa: E402
    SPHERE_FIELDS,
    jaccard as _jaccard,
    normalize_text as _norm,
    validate_sphere_synthesis_v0,
)

CASES_PATH = Path(__file__).resolve().parent / "life_spheres_quality_cases_v0.json"
RUNS_DIR = Path(__file__).resolve().parent / "runs"
PROMPT_ID = "profile.spheres.synthesis.v1"
SCOPE = ("love", "money", "decisions")


def _parse_json(raw: str | None) -> dict[str, Any] | None:
    if not raw:
        return None
    text = raw.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:].strip()
    try:
        obj = json.loads(text)
        return obj if isinstance(obj, dict) else None
    except json.JSONDecodeError:
        start, end = text.find("{"), text.rfind("}")
        if start >= 0 and end > start:
            try:
                obj = json.loads(text[start : end + 1])
                return obj if isinstance(obj, dict) else None
            except json.JSONDecodeError:
                return None
        return None


def _call_synthesis(
    pack: dict[str, Any],
    *,
    temperature: float,
    max_tokens: int,
) -> dict[str, Any]:
    locale = str(pack.get("locale") or "ru")
    system, version = get_prompt(PROMPT_ID, locale=locale)
    user = format_synthesis_user_message(pack, locale=locale)
    tech: dict[str, Any] = {
        "prompt_id": PROMPT_ID,
        "prompt_version": version,
        "model": None,
        "provider": getattr(settings, "llm_provider", None),
        "temperature": temperature,
        "max_tokens": max_tokens,
        "latency_ms": None,
        "error": None,
    }
    client = get_openai_compatible_client(operation="background")
    if client is None:
        tech["error"] = "llm_client_unavailable"
        return {"raw": None, "parsed": None, "tech": tech}
    model = resolve_default_chat_model()
    tech["model"] = model
    t0 = time.perf_counter()
    try:
        raw = chat_completion_text(
            client,
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            json_object=True,
        )
    except Exception as exc:  # noqa: BLE001
        tech["error"] = str(exc)[:500]
        tech["latency_ms"] = int((time.perf_counter() - t0) * 1000)
        return {"raw": None, "parsed": None, "tech": tech}
    tech["latency_ms"] = int((time.perf_counter() - t0) * 1000)
    return {"raw": raw, "parsed": _parse_json(raw), "tech": tech}


def _compare_to_projector(
    synth: dict[str, str],
    proj: dict[str, str] | None,
) -> dict[str, Any]:
    if not proj:
        return {"has_projector": False, "field_jaccard": {}, "mean_jaccard": None, "near_clone": False}
    jacs = {f: round(_jaccard(synth.get(f) or "", proj.get(f) or ""), 3) for f in SPHERE_FIELDS}
    mean = round(sum(jacs.values()) / len(jacs), 3)
    return {
        "has_projector": True,
        "field_jaccard": jacs,
        "mean_jaccard": mean,
        "near_clone": mean >= 0.72,
    }


def _stability(a: dict[str, str], b: dict[str, str]) -> dict[str, Any]:
    jacs = {f: round(_jaccard(a.get(f) or "", b.get(f) or ""), 3) for f in SPHERE_FIELDS}
    mean = round(sum(jacs.values()) / len(jacs), 3)
    return {"field_jaccard": jacs, "mean_jaccard": mean, "stable_enough": mean >= 0.35}


def evaluate_case(
    case: dict[str, Any],
    *,
    dry_run: bool,
    repeats: int,
    temperature: float,
    max_tokens: int,
) -> dict[str, Any]:
    foundations = case["foundations"]
    gate = spheres_projection_allowed(foundations)
    proj_spheres, proj_meta = project_life_spheres_v0(foundations)
    natal = foundations.get("natal") if isinstance(foundations.get("natal"), dict) else {}
    houses_available = bool(natal.get("houses_available"))

    per_sphere: dict[str, Any] = {}
    case_pass = gate

    for sid in SCOPE:
        pack = build_sphere_cues(sid, foundations)
        entry: dict[str, Any] = {
            "sphere_id": sid,
            "contract": SPHERE_CONTRACTS.get(sid),
            "cues_ok": bool(pack.get("ok")),
            "cues_reason": pack.get("reason"),
            "cue_ids": [c.get("id") for c in (pack.get("sphere_cues") or [])],
            "cue_texts": [c.get("text") for c in (pack.get("sphere_cues") or [])],
            "kitchen": pack.get("kitchen"),
            "runs": [],
            "validation": None,
            "vs_projector": None,
            "stability": None,
            "quality_result": "fail",
        }
        if not gate:
            entry["quality_result"] = "fail_gate"
            entry["omit_reason"] = "spheres_projection_not_allowed"
            case_pass = False
            per_sphere[sid] = entry
            continue
        if not pack.get("ok"):
            # Incomplete styles: omit is correct (same as projector pack lsq-07).
            expected_omit = pack.get("reason") == "style_missing"
            entry["expected_omit"] = expected_omit
            entry["quality_result"] = "pass_omit" if expected_omit else "fail_cues"
            if not expected_omit:
                case_pass = False
            per_sphere[sid] = entry
            continue

        if dry_run:
            entry["quality_result"] = "dry_run_cues_ok"
            entry["user_message_preview"] = format_synthesis_user_message(pack)[:800]
            per_sphere[sid] = entry
            continue

        run_fields: list[dict[str, str]] = []
        for r_i in range(max(1, repeats)):
            call = _call_synthesis(pack, temperature=temperature, max_tokens=max_tokens)
            parsed = call["parsed"]
            cue_texts = [str(c.get("text") or "") for c in pack.get("sphere_cues") or []]
            validation = validate_sphere_synthesis_v0(
                parsed,
                identity_core=str(pack.get("identity_core") or ""),
                relevant_style=str(pack.get("relevant_style") or ""),
                sphere_cues=cue_texts,
                houses_available=houses_available,
            )
            run_rec = {
                "run": r_i + 1,
                "tech": call["tech"],
                "raw": call["raw"],
                "parsed": parsed,
                "validation": validation,
            }
            entry["runs"].append(run_rec)
            if validation.get("ok") and validation.get("fields"):
                run_fields.append(validation["fields"])

        best = None
        for run in entry["runs"]:
            v = run.get("validation") or {}
            if v.get("ok"):
                best = run
                break
        if best is None and entry["runs"]:
            best = entry["runs"][0]

        entry["validation"] = (best or {}).get("validation")
        fields = ((best or {}).get("validation") or {}).get("fields") or {}
        proj_row = proj_spheres.get(sid) if isinstance(proj_spheres.get(sid), dict) else None
        entry["vs_projector"] = _compare_to_projector(fields, proj_row)
        entry["projector_fields"] = proj_row
        if len(run_fields) >= 2:
            entry["stability"] = _stability(run_fields[0], run_fields[1])

        ok = bool((entry["validation"] or {}).get("ok"))
        entry["quality_result"] = "pass" if ok else "fail_validation"
        if not ok:
            case_pass = False
        per_sphere[sid] = entry

    # Contrast pairs at pack level handled by caller
    return {
        "case_id": case["id"],
        "label": case.get("label"),
        "contrast": case.get("contrast"),
        "gate": gate,
        "projector_meta_version": (proj_meta or {}).get("projection_version"),
        "per_sphere": per_sphere,
        "case_pass": case_pass if not dry_run else gate
        and all(
            per_sphere[s].get("cues_ok") or per_sphere[s].get("quality_result") == "pass_omit"
            for s in SCOPE
        ),
    }


def _contrast_love_divergence(
    results: list[dict[str, Any]],
    *,
    dry_run: bool,
) -> list[dict[str, Any]]:
    """lsq-01 vs lsq-02 love must diverge on natal cues; lsq-03 vs lsq-04 on synthesis (styles)."""
    by_id = {r["case_id"]: r for r in results}
    out: list[dict[str, Any]] = []

    def love_how(cid: str) -> str:
        sp = ((by_id.get(cid) or {}).get("per_sphere") or {}).get("love") or {}
        fields = (sp.get("validation") or {}).get("fields") or {}
        if fields.get("how"):
            return str(fields["how"])
        return ""

    def love_cues(cid: str) -> str:
        sp = ((by_id.get(cid) or {}).get("per_sphere") or {}).get("love") or {}
        return " | ".join(str(x) for x in (sp.get("cue_texts") or []))

    # Natal contrast: cues (and synthesis) must diverge
    if "lsq-01" in by_id and "lsq-02" in by_id:
        ha = love_how("lsq-01") or love_cues("lsq-01")
        hb = love_how("lsq-02") or love_cues("lsq-02")
        jac = round(_jaccard(ha, hb), 3) if ha and hb else None
        ok = jac is not None and jac < 0.55 and _norm(ha) != _norm(hb)
        out.append(
            {
                "pair": "same_sun_different_venus",
                "a": "lsq-01",
                "b": "lsq-02",
                "love_how_jaccard": jac,
                "pass": ok,
            }
        )

    # Style contrast: same natal cues by design — only LLM how must diverge
    if "lsq-03" in by_id and "lsq-04" in by_id:
        if dry_run:
            out.append(
                {
                    "pair": "same_natal_different_styles",
                    "a": "lsq-03",
                    "b": "lsq-04",
                    "love_how_jaccard": None,
                    "pass": True,
                    "note": "dry-run: cues identical by design; style divergence requires LLM",
                }
            )
        else:
            ha, hb = love_how("lsq-03"), love_how("lsq-04")
            jac = round(_jaccard(ha, hb), 3) if ha and hb else None
            ok = jac is not None and jac < 0.55 and _norm(ha) != _norm(hb)
            out.append(
                {
                    "pair": "same_natal_different_styles",
                    "a": "lsq-03",
                    "b": "lsq-04",
                    "love_how_jaccard": jac,
                    "pass": ok,
                }
            )
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="Build cues + prompts only, no LLM")
    ap.add_argument("--repeats", type=int, default=1, help="LLM calls per sphere for stability")
    ap.add_argument("--temperature", type=float, default=0.4)
    ap.add_argument("--max-tokens", type=int, default=900)
    ap.add_argument("--case", action="append", help="Filter case id (repeatable)")
    args = ap.parse_args()

    pack = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    cases = pack["cases"]
    if args.case:
        want = set(args.case)
        cases = [c for c in cases if c["id"] in want]

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = RUNS_DIR / f"life_spheres_synthesis_{stamp}"
    out_dir.mkdir(parents=True, exist_ok=True)

    results: list[dict[str, Any]] = []
    for case in cases:
        print(f"… {case['id']} ({'dry-run' if args.dry_run else 'llm'})", flush=True)
        results.append(
            evaluate_case(
                case,
                dry_run=args.dry_run,
                repeats=args.repeats,
                temperature=args.temperature,
                max_tokens=args.max_tokens,
            )
        )

    contrasts = _contrast_love_divergence(results, dry_run=args.dry_run)
    passed = sum(1 for r in results if r.get("case_pass"))
    summary = {
        "version": "life_spheres_synthesis_eval_v0",
        "prompt_id": PROMPT_ID,
        "dry_run": args.dry_run,
        "repeats": args.repeats,
        "cases_total": len(results),
        "cases_pass": passed,
        "contrasts": contrasts,
        "contrasts_pass": sum(1 for c in contrasts if c.get("pass")),
        "created_at": stamp,
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "results.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")

    md: list[str] = [
        f"# Life spheres synthesis eval — {stamp}",
        "",
        f"- prompt: `{PROMPT_ID}`",
        f"- dry_run: {args.dry_run}",
        f"- cases: **{passed}/{len(results)}** pass",
        f"- contrasts: **{summary['contrasts_pass']}/{len(contrasts)}**",
        "",
        "## Cases",
        "",
    ]
    for r in results:
        md.append(f"### {r['case_id']} — {'PASS' if r.get('case_pass') else 'FAIL'}")
        md.append(f"{r.get('label')}")
        for sid in SCOPE:
            sp = r["per_sphere"][sid]
            md.append(f"- **{sid}**: {sp.get('quality_result')} · cues={sp.get('cues_ok')}")
            if sp.get("validation") and not args.dry_run:
                v = sp["validation"]
                md.append(f"  - checks: `{json.dumps(v.get('checks'), ensure_ascii=False)}`")
                if v.get("defects"):
                    md.append(f"  - defects: {v['defects']}")
                fields = v.get("fields") or {}
                if fields.get("how"):
                    md.append(f"  - how: {fields['how'][:220]}")
            elif sp.get("cue_texts"):
                md.append(f"  - cues: {sp['cue_texts'][:3]}")
            if sp.get("vs_projector") and sp["vs_projector"].get("mean_jaccard") is not None:
                md.append(
                    f"  - vs projector mean Jaccard: {sp['vs_projector']['mean_jaccard']} "
                    f"(near_clone={sp['vs_projector']['near_clone']})"
                )
            if sp.get("stability"):
                md.append(f"  - stability mean Jaccard: {sp['stability']['mean_jaccard']}")
        md.append("")
    if contrasts:
        md.append("## Contrasts")
        for c in contrasts:
            md.append(
                f"- {c['pair']} ({c['a']} vs {c['b']}): jaccard={c['love_how_jaccard']} → "
                f"{'PASS' if c['pass'] else 'FAIL'}"
            )
        md.append("")
    md_path = out_dir / "SUMMARY.md"
    md_path.write_text("\n".join(md), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"wrote {md_path}")
    if args.dry_run:
        return 0 if passed == len(results) else 1
    return 0 if passed == len(results) and summary["contrasts_pass"] == len(contrasts) else 1


if __name__ == "__main__":
    raise SystemExit(main())

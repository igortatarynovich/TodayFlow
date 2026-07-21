#!/usr/bin/env python3
"""Life spheres quality pack v0 — contrastive projector review (no LLM).

Produces JSON pack under runs/ + prints markdown summary path hint.
SoT report: docs/audits/PROFILE_LIFE_SPHERES_QUALITY_REVIEW_V0.md (authored from pack).

Usage:
  cd backend && .venv/bin/python evals/profile_quality/run_life_spheres_quality_pack_v0.py
"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from todayflow_backend.services.life_spheres_projector_v0 import (  # noqa: E402
    PROJECTION_VERSION,
    SPHERE_FIELDS,
    project_life_spheres_v0,
    spheres_projection_allowed,
)
from todayflow_backend.services.profile_contract_v1 import (  # noqa: E402
    _normalize_life_spheres,
)

CASES_PATH = Path(__file__).resolve().parent / "life_spheres_quality_cases_v0.json"
RUNS_DIR = Path(__file__).resolve().parent / "runs"

SPHERE_PURPOSE = {
    "love": {
        "user_question": "Как базовые особенности проявляются в любви и близости?",
        "must_differ_from": "identity_core (who) and relationship_style (lens) — sphere = manifestation map",
        "user_value": "Понять, как входит в близость, что нужно, где ломается, один практический шаг",
    },
    "money": {
        "user_question": "Как базовые особенности проявляются в деньгах и ценности?",
        "must_differ_from": "identity_core and money_style — sphere = resource manifestation",
        "user_value": "Опора: правила ценности, риск, один денежный фокус",
    },
    "decisions": {
        "user_question": "Как базовые особенности проявляются в решениях и дисциплине?",
        "must_differ_from": "identity_core and decision_style — sphere = decision hygiene in life",
        "user_value": "Понятный способ выбирать и один hygiene-шаг",
    },
}

VOICE_BANS = (
    "система не",
    "система знает",
    "llm",
    "алгоритм",
    "воронк",
    "funnel",
    "snapshot",
    "projector",
    "правило id",
    "rule:",
    "недостаточно данных",
)
# Avoid matching user-facing words like «взаиморасчётах».
VOICE_BAN_RES = (
    re.compile(r"\bрасчёт[а-я]*\b"),
    re.compile(r"\bсистем[аыу]\b"),
)
HOUSE_MARKERS = ("в доме", "асцендент", "ascendant", "7 дом", "2 дом", "9 дом", "доме:")
LONGITUDINAL = ("регулярно", "каждый раз", "по чек-инам", "as your days show")


def _norm(t: str) -> str:
    return re.sub(r"\s+", " ", (t or "").strip().lower())


def _tokens(t: str) -> set[str]:
    return {x for x in re.findall(r"[a-zа-яё]{3,}", _norm(t))}


def _jaccard(a: str, b: str) -> float:
    sa, sb = _tokens(a), _tokens(b)
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def _style_quote_present(field_text: str, style: str) -> bool:
    """Specificity proxy: template embeds ≤40-char quote from style."""
    s = (style or "").strip()
    if len(s) < 12:
        return False
    # first 12+ chars chunk appearing in field
    chunk = s[:24].strip()
    return _norm(chunk[:16]) in _norm(field_text) if len(chunk) >= 12 else False


def score_field(
    *,
    sphere_id: str,
    field: str,
    text: str,
    evidence: list[str],
    style: str,
    identity_core: str,
    houses_available: bool,
    other_sphere_texts: list[str],
) -> dict[str, Any]:
    defects: list[dict[str, str]] = []
    checks: dict[str, bool] = {}
    blob = _norm(text)

    # Grounding
    grounded = bool(evidence) and (
        any(f"rule:{sphere_id}.{field}" in e or f".{field}." in e for e in evidence)
        or (field == "how" and any(e.startswith("planet:") or e.startswith("house:") for e in evidence))
        or any(e.startswith("rule:") for e in evidence)
    )
    checks["grounding"] = grounded
    if not grounded:
        defects.append({"class": "RULESET", "note": f"{sphere_id}.{field}: no rule/source evidence attached"})

    # Specificity — style quote in need/risk/on/off/helps; how must go beyond sign boilerplate
    if field == "how":
        boilerplate = "задаёт тон проявления" in blob or "sets a base tone" in blob or "colors how this area" in blob
        has_planet = any(e.startswith("planet:") for e in evidence)
        has_house = any(e.startswith("house:") for e in evidence)
        # Planet×sign name alone with fixed boilerplate = weak specificity (architectural RULESET)
        specific = has_planet and (has_house or not boilerplate)
        if has_planet and boilerplate and not has_house:
            checks["specificity"] = False
            defects.append(
                {
                    "class": "RULESET",
                    "note": (
                        f"{sphere_id}.how uses planet-in-sign boilerplate without trait content "
                        "(only sign label changes — weak personal binding)"
                    ),
                }
            )
        else:
            checks["specificity"] = specific
            if not specific:
                defects.append(
                    {
                        "class": "RULESET",
                        "note": f"{sphere_id}.how: interchangeable for most users (weak personal binding)",
                    }
                )
    else:
        specific = _style_quote_present(text, style) or len(_tokens(text) - _tokens(style)) >= 3
        checks["specificity"] = specific
        if not specific:
            defects.append(
                {
                    "class": "RULESET",
                    "note": f"{sphere_id}.{field}: interchangeable for most users (weak personal binding)",
                }
            )

    # Distinctness vs identity
    if field == "how" and identity_core and _jaccard(text, identity_core) >= 0.45:
        checks["distinct_identity"] = False
        defects.append({"class": "VALIDATION", "note": f"{sphere_id}.how too close to identity_core"})
    else:
        checks["distinct_identity"] = True

    # Distinctness vs other spheres (same field)
    dup = False
    for other in other_sphere_texts:
        if other and (_norm(text) == _norm(other) or (len(text) > 40 and _jaccard(text, other) >= 0.75)):
            dup = True
            break
    checks["distinct_spheres"] = not dup
    if dup:
        defects.append({"class": "VALIDATION", "note": f"{sphere_id}.{field} near-duplicate across spheres"})

    # Honesty
    if not houses_available and any(m in blob for m in HOUSE_MARKERS):
        checks["honesty_houses"] = False
        defects.append({"class": "RULESET", "note": f"{sphere_id}.{field} house/ASC claim without houses_available"})
    else:
        checks["honesty_houses"] = True
    if any(m in blob for m in LONGITUDINAL):
        checks["honesty_longitudinal"] = False
        defects.append({"class": "BLOCK_PURPOSE", "note": f"{sphere_id}.{field} longitudinal claim without living"})
    else:
        checks["honesty_longitudinal"] = True

    # Voice
    voice_ok = not any(b in blob for b in VOICE_BANS) and not any(r.search(blob) for r in VOICE_BAN_RES)
    checks["voice"] = voice_ok
    if not voice_ok:
        defects.append({"class": "VOICE", "note": f"{sphere_id}.{field} system/calculation language"})

    # Usefulness — helps must be doable; need is allowed as concrete support need (not action)
    if field == "helps":
        useful = bool(
            re.search(
                r"(шаг|договор|запис|критер|фокус|назови|оставь|постав|реши |собери |ограничь|держа|один |one |write |name )",
                blob,
            )
        )
        checks["usefulness"] = useful
        if not useful:
            defects.append({"class": "RULESET", "note": f"{sphere_id}.helps lacks actionable support"})
    elif field == "need":
        # Concrete sphere need (not empty abstraction)
        useful = len(_tokens(text)) >= 5 and not any(
            x in blob for x in ("гармония во всём", "просто доверьтесь", "энергия вселенной")
        )
        checks["usefulness"] = useful
        if not useful:
            defects.append({"class": "RULESET", "note": f"{sphere_id}.need too abstract for user support"})
    else:
        checks["usefulness"] = True

    passed = all(checks.values())
    return {"field": field, "text": text, "checks": checks, "pass": passed, "defects": defects}


def score_sphere_coherence(row: dict[str, str]) -> dict[str, Any]:
    """Lightweight coherence: need/risk should not share the same first 40 chars; on/off differ."""
    defects: list[dict[str, str]] = []
    need, risk = _norm(row.get("need") or ""), _norm(row.get("risk") or "")
    on, off = _norm(row.get("turns_on") or ""), _norm(row.get("turns_off") or "")
    ok = True
    if need and risk and (need == risk or _jaccard(need, risk) >= 0.85):
        ok = False
        defects.append({"class": "RULESET", "note": "need≈risk — internal incoherence / template collapse"})
    if on and off and (on == off or _jaccard(on, off) >= 0.85):
        ok = False
        defects.append({"class": "RULESET", "note": "turns_on≈turns_off — template collapse"})
    return {"pass": ok, "defects": defects}


def evaluate_case(case: dict[str, Any]) -> dict[str, Any]:
    foundations = case["foundations"]
    gate = spheres_projection_allowed(foundations)
    spheres, meta = project_life_spheres_v0(foundations)
    snapshot_spheres = _normalize_life_spheres(spheres)

    identity = str((foundations.get("identity") or {}).get("identity_core") or "")
    styles = foundations.get("styles") if isinstance(foundations.get("styles"), dict) else {}
    natal = foundations.get("natal") if isinstance(foundations.get("natal"), dict) else {}
    houses_available = bool(natal.get("houses_available"))

    style_by = {
        "love": str(styles.get("relationship_style") or ""),
        "money": str(styles.get("money_style") or ""),
        "decisions": str(styles.get("decision_style") or ""),
    }

    per_sphere_out: dict[str, Any] = {}
    all_defects: list[dict[str, str]] = []

    for sid in ("love", "money", "decisions"):
        purpose = SPHERE_PURPOSE[sid]
        row = spheres.get(sid)
        info = (meta.get("per_sphere") or {}).get(sid) or {}
        evidence = list(info.get("evidence") or [])
        if row is None:
            omit_reason = next(
                (o.get("reason") for o in (meta.get("spheres_omitted") or []) if o.get("id") == sid),
                "omitted",
            )
            # Incomplete styles: omit is correct architecture
            expected_omit = not style_by[sid].strip() or len(style_by[sid].strip()) < 12
            entry = {
                "emitted": False,
                "omit_reason": omit_reason,
                "purpose": purpose,
                "expected_omit": expected_omit,
                "quality_result": "pass_omit" if expected_omit else "fail_missing",
                "defects": []
                if expected_omit
                else [{"class": "RULESET", "note": f"{sid} omitted unexpectedly: {omit_reason}"}],
                "fields": {},
            }
            if not expected_omit:
                all_defects.extend(entry["defects"])
            per_sphere_out[sid] = entry
            continue

        others_by_field = {
            f: [str((spheres.get(o) or {}).get(f) or "") for o in ("love", "money", "decisions") if o != sid]
            for f in SPHERE_FIELDS
        }
        field_scores = []
        for field in SPHERE_FIELDS:
            fs = score_field(
                sphere_id=sid,
                field=field,
                text=str(row.get(field) or ""),
                evidence=evidence,
                style=style_by[sid],
                identity_core=identity,
                houses_available=houses_available,
                other_sphere_texts=others_by_field[field],
            )
            field_scores.append(fs)
            all_defects.extend(fs["defects"])

        coherence = score_sphere_coherence(row)
        all_defects.extend(coherence["defects"])

        # UI projection note (contract → FE frame)
        ui_how = row["how"]
        if sid == "love" and not _norm(ui_how).startswith("в отношениях"):
            ui_note = "FE withLifeSphereHowFrame may prefix «В отношениях» (PROJECTION chrome, not claim invent)"
        elif sid == "money" and not _norm(ui_how).startswith("в реализации"):
            ui_note = "FE may prefix «В реализации» for money how"
        else:
            ui_note = "FE maps fields 1:1 when contract present; partial map OK"

        field_pass = all(f["pass"] for f in field_scores) and coherence["pass"]
        per_sphere_out[sid] = {
            "emitted": True,
            "purpose": purpose,
            "claim_depth": info.get("claim_depth"),
            "style_class": info.get("style_class"),
            "rule_ids": [e for e in evidence if e.startswith("rule:")],
            "evidence": evidence,
            "influencing_inputs": {
                "style": style_by[sid][:120],
                "planets_in_evidence": [e for e in evidence if e.startswith("planet:")],
                "houses_in_evidence": [e for e in evidence if e.startswith("house:")],
                "identity_used_as_how": False,
            },
            "output": row,
            "snapshot_row": snapshot_spheres.get(sid),
            "fields": {f["field"]: f for f in field_scores},
            "coherence": coherence,
            "ui_projection_note": ui_note,
            "quality_result": "pass" if field_pass else "fail",
            "defects": [d for f in field_scores for d in f["defects"]] + coherence["defects"],
        }

    # Pairwise sensitivity hooks filled later at pack level
    return {
        "id": case["id"],
        "contrast": case.get("contrast"),
        "label": case.get("label"),
        "intent": case.get("intent"),
        "gate_allowed": gate,
        "projection_version": meta.get("projection_version") or PROJECTION_VERSION,
        "fingerprint": meta.get("fingerprint"),
        "spheres_projected": meta.get("spheres_projected"),
        "spheres_omitted": meta.get("spheres_omitted"),
        "spheres": per_sphere_out,
        "defects": all_defects,
        "case_pass": gate
        and all(
            s.get("quality_result") in ("pass", "pass_omit") for s in per_sphere_out.values()
        )
        and not any(d.get("class") == "BLOCK_PURPOSE" for d in all_defects),
    }


def compare_pair(a: dict[str, Any], b: dict[str, Any], *, expect_divergence: str) -> dict[str, Any]:
    """expect_divergence: love | styles_all | how_houses"""
    diffs: dict[str, Any] = {}
    for sid in ("love", "money", "decisions"):
        ra = (a["spheres"].get(sid) or {}).get("output") or {}
        rb = (b["spheres"].get(sid) or {}).get("output") or {}
        if not ra or not rb:
            diffs[sid] = {"comparable": False}
            continue
        field_diff = {
            f: _norm(str(ra.get(f) or "")) != _norm(str(rb.get(f) or "")) for f in SPHERE_FIELDS
        }
        diffs[sid] = {
            "comparable": True,
            "fields_differ": field_diff,
            "any_differ": any(field_diff.values()),
            "how_jaccard": round(_jaccard(str(ra.get("how") or ""), str(rb.get("how") or "")), 3),
            "need_jaccard": round(_jaccard(str(ra.get("need") or ""), str(rb.get("need") or "")), 3),
        }

    ok = True
    notes: list[str] = []
    if expect_divergence == "love_emphasis":
        # same sun different venus — love need/how should differ
        love = diffs.get("love") or {}
        if love.get("comparable") and not love.get("any_differ"):
            ok = False
            notes.append("RULESET: same Sun pair produced identical love sphere")
        elif love.get("comparable") and love.get("need_jaccard", 1) > 0.9 and love.get("how_jaccard", 1) > 0.9:
            ok = False
            notes.append("RULESET: love barely sensitive to Venus/Moon/style contrast")
    elif expect_divergence == "styles_all":
        for sid in ("love", "money", "decisions"):
            d = diffs.get(sid) or {}
            if d.get("comparable") and not (
                d.get("fields_differ", {}).get("need")
                or d.get("fields_differ", {}).get("helps")
                or d.get("fields_differ", {}).get("risk")
            ):
                ok = False
                notes.append(f"RULESET: {sid} need/risk/helps unchanged when only styles change")
    elif expect_divergence == "houses_vs_sign":
        pass  # checked inside case honesty

    return {
        "pair": [a["id"], b["id"]],
        "expect": expect_divergence,
        "diffs": diffs,
        "pass": ok,
        "notes": notes,
        "defects": [{"class": "RULESET", "note": n} for n in notes],
    }


def main() -> int:
    payload = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    cases = payload["cases"]
    evaluated = [evaluate_case(c) for c in cases]
    by_id = {e["id"]: e for e in evaluated}

    comparisons = [
        compare_pair(by_id["lsq-01"], by_id["lsq-02"], expect_divergence="love_emphasis"),
        compare_pair(by_id["lsq-03"], by_id["lsq-04"], expect_divergence="styles_all"),
    ]

    # Cross-user collapse: lsq-01 vs lsq-06 should not be identical outputs
    collapse_defects: list[dict[str, str]] = []
    for sid in ("love", "money", "decisions"):
        o1 = (by_id["lsq-01"]["spheres"].get(sid) or {}).get("output") or {}
        o6 = (by_id["lsq-06"]["spheres"].get(sid) or {}).get("output") or {}
        if o1 and o6 and _norm(o1.get("how") or "") == _norm(o6.get("how") or "") and _norm(
            o1.get("need") or ""
        ) == _norm(o6.get("need") or ""):
            collapse_defects.append(
                {"class": "RULESET", "note": f"{sid} identical across maximally different profiles lsq-01/lsq-06"}
            )

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = RUNS_DIR / f"life_spheres_quality_{ts}"
    out_dir.mkdir(parents=True, exist_ok=True)

    pack = {
        "manifest": {
            "pack": "life_spheres_quality_v0",
            "created_at": ts,
            "projection_version": PROJECTION_VERSION,
            "cases_file": str(CASES_PATH.name),
            "criteria": [
                "grounding",
                "specificity",
                "distinctness",
                "usefulness",
                "internal_coherence",
                "voice",
                "honesty",
            ],
            "defect_classes": [
                "BLOCK_PURPOSE",
                "INPUT",
                "RULESET",
                "RESPONSE_SCHEMA",
                "VALIDATION",
                "PROJECTION",
                "UI_GATE",
                "VOICE",
            ],
        },
        "cases": evaluated,
        "comparisons": comparisons,
        "collapse_checks": collapse_defects,
        "summary": {
            "case_count": len(evaluated),
            "cases_pass": sum(1 for e in evaluated if e["case_pass"]),
            "cases_fail": sum(1 for e in evaluated if not e["case_pass"]),
            "comparison_pass": sum(1 for c in comparisons if c["pass"]),
            "total_defects": sum(len(e["defects"]) for e in evaluated)
            + sum(len(c["defects"]) for c in comparisons)
            + len(collapse_defects),
        },
    }

    json_path = out_dir / "pack.json"
    json_path.write_text(json.dumps(pack, ensure_ascii=False, indent=2), encoding="utf-8")

    # Compact markdown for authoring the SoT review
    lines = [
        f"# Life spheres quality pack run {ts}",
        "",
        f"projection_version: `{PROJECTION_VERSION}`",
        f"cases_pass: {pack['summary']['cases_pass']}/{pack['summary']['case_count']}",
        f"comparisons_pass: {pack['summary']['comparison_pass']}/{len(comparisons)}",
        f"total_defects: {pack['summary']['total_defects']}",
        "",
    ]
    for e in evaluated:
        lines.append(f"## {e['id']} — {e['label']} — {'PASS' if e['case_pass'] else 'FAIL'}")
        lines.append(f"intent: {e['intent']}")
        lines.append(f"fingerprint: `{e['fingerprint']}`")
        for sid, s in e["spheres"].items():
            lines.append(f"### {sid} — {s.get('quality_result')}")
            if not s.get("emitted"):
                lines.append(f"omitted: {s.get('omit_reason')} (expected={s.get('expected_omit')})")
                continue
            lines.append(f"style_class: {s.get('style_class')} · depth: {s.get('claim_depth')}")
            lines.append(f"rules: {', '.join(s.get('rule_ids') or [])}")
            for field in SPHERE_FIELDS:
                fd = (s.get("fields") or {}).get(field) or {}
                mark = "✓" if fd.get("pass") else "✗"
                lines.append(f"- {mark} **{field}**: {fd.get('text')}")
                for d in fd.get("defects") or []:
                    lines.append(f"  - `{d['class']}` {d['note']}")
            for d in (s.get("coherence") or {}).get("defects") or []:
                lines.append(f"- coherence `{d['class']}` {d['note']}")
            lines.append(f"UI: {s.get('ui_projection_note')}")
        lines.append("")
    for c in comparisons:
        lines.append(f"## Compare {c['pair'][0]} vs {c['pair'][1]} — {'PASS' if c['pass'] else 'FAIL'}")
        lines.append(json.dumps(c["diffs"], ensure_ascii=False, indent=2))
        for n in c.get("notes") or []:
            lines.append(f"- {n}")
        lines.append("")
    if collapse_defects:
        lines.append("## Collapse defects")
        for d in collapse_defects:
            lines.append(f"- `{d['class']}` {d['note']}")

    md_path = out_dir / "pack.md"
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json_path)
    print(md_path)
    print(json.dumps(pack["summary"], ensure_ascii=False))
    return 0 if pack["summary"]["cases_fail"] == 0 and all(c["pass"] for c in comparisons) else 1


if __name__ == "__main__":
    raise SystemExit(main())

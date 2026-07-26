"""C3.5.1 — Baseline eval report builder (machine + markdown). Eval-only."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

# Provisional cell/pack bands (document; calibrate via golden set later)
THRESHOLD_REJECT = 0.60
THRESHOLD_REVIEW = 0.79  # inclusive upper bound of review band → pass at >= 0.80
THRESHOLD_PASS = 0.80
THRESHOLDS_PROVISIONAL = {
    "reject_lt": THRESHOLD_REJECT,
    "review_range": [THRESHOLD_REJECT, THRESHOLD_REVIEW],
    "pass_gte": THRESHOLD_PASS,
    "note": "PROVISIONAL — calibrate after golden-set labeling (C3.5c)",
}


def _as_dict(v: Any) -> dict[str, Any]:
    return v if isinstance(v, dict) else {}


def _band(score: float) -> str:
    if score < THRESHOLD_REJECT:
        return "reject"
    if score < THRESHOLD_PASS:
        return "review"
    return "pass"


def _mean(vals: list[float]) -> float:
    return round(sum(vals) / max(1, len(vals)), 3) if vals else 0.0


def _group_means(cells: list[dict[str, Any]], key: str) -> dict[str, float]:
    buckets: dict[str, list[float]] = {}
    for c in cells:
        k = str(c.get(key) or "")
        if not k:
            continue
        buckets.setdefault(k, []).append(float(c.get("score") or 0.0))
    return {k: _mean(v) for k, v in sorted(buckets.items())}


def _collect_defect_codes(cell: dict[str, Any]) -> list[str]:
    codes: list[str] = []
    details = _as_dict(cell.get("details"))
    for section in details.values():
        if not isinstance(section, dict):
            continue
        for c in section.get("defect_codes") or []:
            if c:
                codes.append(str(c))
    for c in cell.get("defect_codes") or []:
        if c:
            codes.append(str(c))
    for c in cell.get("all_defect_codes") or []:
        if c:
            codes.append(str(c))
    return codes


def build_baseline_report(eval_report: dict[str, Any]) -> dict[str, Any]:
    """Machine-readable summary from ``run_eval_pack_c35`` output."""
    cells = list(eval_report.get("cells") or [])
    axes = _as_dict(eval_report.get("aggregate_axes"))
    shape = _as_dict(eval_report.get("shape"))

    worst = sorted(cells, key=lambda c: float(c.get("score") or 0.0))[:20]
    worst_cells = [
        {
            "date": c.get("date"),
            "profile_id": c.get("profile_id"),
            "locale": c.get("locale"),
            "day_type": c.get("day_type"),
            "score": c.get("score"),
            "contract_score": c.get("contract_score"),
            "editorial_score": c.get("editorial_score"),
            "axes": c.get("axes"),
            "defect_codes": sorted(set(_collect_defect_codes(c)))[:12],
        }
        for c in worst
    ]

    defect_counter: Counter[str] = Counter()
    for c in cells:
        defect_counter.update(_collect_defect_codes(c))

    by_day_type = _group_means(cells, "day_type")
    band_counts = Counter(_band(float(c.get("score") or 0.0)) for c in cells)

    return {
        "eval_version": eval_report.get("eval_version"),
        "contract_version": eval_report.get("contract_version"),
        "pack_score": eval_report.get("pack_score"),
        "mean_cell_score": eval_report.get("mean_cell_score"),
        "pass": eval_report.get("pass"),
        "pass_threshold": eval_report.get("pass_threshold"),
        "thresholds_provisional": {
            **THRESHOLDS_PROVISIONAL,
            **_as_dict(eval_report.get("thresholds_provisional")),
        },
        "shape": shape,
        "aggregate_axes": axes,
        "by_locale": _group_means(cells, "locale"),
        "by_profile": _group_means(cells, "profile_id"),
        "by_day_type": by_day_type,
        "band_counts": dict(band_counts),
        "worst_cells": worst_cells,
        "defect_counts": dict(defect_counter.most_common()),
        "cell_count": len(cells),
    }


def render_baseline_markdown(report: dict[str, Any]) -> str:
    """Human-readable baseline note from ``build_baseline_report``."""
    thr = _as_dict(report.get("thresholds_provisional"))
    shape = _as_dict(report.get("shape"))
    lines: list[str] = [
        "# Day Scenario Eval Baseline C3.5.1",
        "",
        f"**Eval version:** `{report.get('eval_version')}`  ",
        f"**Pack score:** `{report.get('pack_score')}` · mean cell `{report.get('mean_cell_score')}`  ",
        f"**Pass:** `{report.get('pass')}` (pack threshold `{report.get('pass_threshold')}`)  ",
        f"**Cells:** `{report.get('cell_count')}` · days `{shape.get('days')}` · "
        f"profiles `{len(shape.get('profiles') or [])}` · locales `{shape.get('locales')}`",
        "",
        "## Thresholds (PROVISIONAL)",
        "",
        f"- reject `< {thr.get('reject_lt', THRESHOLD_REJECT)}`",
        f"- review `{thr.get('reject_lt', THRESHOLD_REJECT)}`–`{thr.get('review_range', [THRESHOLD_REJECT, THRESHOLD_REVIEW])[1] if isinstance(thr.get('review_range'), list) and len(thr.get('review_range') or []) > 1 else THRESHOLD_REVIEW}`",
        f"- pass `≥ {thr.get('pass_gte', THRESHOLD_PASS)}`",
        f"- note: {thr.get('note', THRESHOLDS_PROVISIONAL['note'])}",
        "",
        "## Aggregate axes",
        "",
    ]
    for k, v in sorted(_as_dict(report.get("aggregate_axes")).items()):
        lines.append(f"- `{k}`: `{v}`")

    lines.extend(["", "## By locale", ""])
    for k, v in sorted(_as_dict(report.get("by_locale")).items()):
        lines.append(f"- `{k}`: `{v}`")

    lines.extend(["", "## By profile", ""])
    for k, v in sorted(_as_dict(report.get("by_profile")).items()):
        lines.append(f"- `{k}`: `{v}`")

    by_dt = _as_dict(report.get("by_day_type"))
    if by_dt:
        lines.extend(["", "## By day_type", ""])
        for k, v in sorted(by_dt.items()):
            lines.append(f"- `{k}`: `{v}`")

    lines.extend(["", "## Band counts (cell score)", ""])
    for k, v in sorted(_as_dict(report.get("band_counts")).items()):
        lines.append(f"- `{k}`: `{v}`")

    lines.extend(["", "## Defect code frequency", ""])
    defects = _as_dict(report.get("defect_counts"))
    if not defects:
        lines.append("_none_")
    else:
        for code, count in list(defects.items())[:40]:
            lines.append(f"- `{code}`: `{count}`")

    lines.extend(["", "## Worst 20 cells", ""])
    for i, c in enumerate(report.get("worst_cells") or [], 1):
        codes = ", ".join(f"`{x}`" for x in (c.get("defect_codes") or [])[:6]) or "—"
        lines.append(
            f"{i}. `{c.get('date')}` · `{c.get('profile_id')}` · `{c.get('locale')}`"
            f" · day_type=`{c.get('day_type') or '—'}` · score=`{c.get('score')}`"
            f" · contract=`{c.get('contract_score')}` · editorial=`{c.get('editorial_score')}`"
            f" · defects: {codes}"
        )

    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- Synthetic matrix baseline — not live Nebius.",
            "- Runtime LLM / today.py / Nebius paths untouched in C3.5.1.",
            "- Next: golden-set labeling (C3.5c) → live shadow.",
            "",
        ]
    )
    return "\n".join(lines)


def write_baseline_artifacts(
    report: dict[str, Any],
    docs_path: str | Path | None = None,
    json_path: str | Path | None = None,
) -> dict[str, str]:
    """Optional helpers: write markdown and/or JSON baseline artifacts."""
    import json

    written: dict[str, str] = {}
    if docs_path is not None:
        p = Path(docs_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        text = render_baseline_markdown(report)
        p.write_text(text, encoding="utf-8")
        written["docs"] = str(p)
    if json_path is not None:
        p = Path(json_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        written["json"] = str(p)
    return written

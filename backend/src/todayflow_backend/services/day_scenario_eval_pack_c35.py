"""Phase C3.5 / C3.5.1 — Multi-day × multi-profile × multi-locale eval pack.

Comparative harness over fixture/captured scenarios (no Nebius in CI):

C3.5.0 legacy: 14 consecutive days × 4 profiles × ru/en
C3.5.1:        28 days × ≥10 profiles × ru/en (≥400 cells)

Scores: conflict recognizability · scene concreteness · chorus coherence ·
user differentiation · formulation repeatability · recommendation provenance ·
no parallel forecasts · day-closure quality.

Canon: docs/audits/DAY_SCENARIO_EVAL_PACK_C35.md
       docs/audits/DAY_SCENARIO_EVAL_HARDENING_C351.md
"""

from __future__ import annotations

import re
from copy import deepcopy
from datetime import date, timedelta
from typing import Any, Iterable

from todayflow_backend.services.day_scenario_editorial_gate_c31 import (
    DEFECT_CHORUS_PARALLEL_FORECAST,
    DEFECT_CHORUS_SEMANTIC_DUPLICATION,
    CRITICAL_DEFECTS,
    conflict_anchor_id,
    run_editorial_quality_gate_c31,
    score_editorial_quality_c31,
)
from todayflow_backend.services.day_scenario_eval_editorial_en_c351 import (
    DEFECT_LOCALE_LANGUAGE_MISMATCH,
    run_editorial_quality_gate_en_c351,
    score_editorial_en_c351,
)
from todayflow_backend.services.day_scenario_eval_provenance_c351 import (
    score_day_closure_c351,
    score_provenance_c351,
)
from todayflow_backend.services.day_scenario_eval_report_c351 import (
    THRESHOLDS_PROVISIONAL,
)
from todayflow_backend.services.day_scenario_native_llm_c1 import (
    NATIVE_LLM_SCHEMA_VERSION,
    normalize_native_scenario_llm_c1,
)
from todayflow_backend.services.day_scenario_pairwise_eval_c33b import (
    structural_diff_dimensions,
)
from todayflow_backend.services.day_scenario_personalization_c33 import (
    DEPTH_DEEP,
    DEPTH_GENERAL,
    DEPTH_LIGHT,
    _as_dict,
    _as_list,
    _clip,
    run_personalization_gate_c33,
)

EVAL_CONTRACT = "day_scenario_eval_pack_c35"
EVAL_VERSION = "c35.1"

# 8 behavioral + no_birth_time + controls (no_profile, birth_date_only) + incomplete_evidence
PROFILE_IDS = (
    "smooth_conflict",
    "demand_clarity",
    "analyze_first",
    "act_first",
    "over_responsible",
    "rejection_sensitive",
    "autonomy_oriented",
    "no_birth_time",
    "no_profile",
    "birth_date_only",
    "incomplete_evidence",
)

# Legacy C3.5.0 profile set for backward-compat matrix wrapper
PROFILE_IDS_C35_LEGACY = (
    "smooth_conflict",
    "demand_clarity",
    "analyze_first",
    "no_birth_time",
)

CONTROL_PROFILE_IDS = frozenset(
    {"no_birth_time", "no_profile", "birth_date_only", "incomplete_evidence"}
)

LOCALES = ("ru", "en")

AXIS_IDS = (
    "conflict_recognizability",
    "scene_concreteness",
    "chorus_coherence",
    "user_differentiation",
    "formulation_repeatability",
    "recommendation_provenance",
    "no_parallel_forecasts",
    "day_closure_quality",
)

# Pass bar for aggregate pack (fixture CI). PROVISIONAL — calibrate via golden set.
PACK_PASS_THRESHOLD = 0.75  # provisional pack gate (cell bands: reject<0.60, review 0.60–0.79, pass≥0.80)
DAY_DIFF_MIN_DIMENSIONS = 2
REPEAT_JACCARD_SOFT_MAX = 0.55  # same-profile consecutive days

# C3.5.1 matrix shape gates
C351_MIN_DAYS = 28
C351_MIN_PROFILES = 8
C351_MIN_CELLS = 400

DAY_TYPES = (
    "calm",
    "single_driver",
    "competing_drivers",
    "moon_sign_change",
    "station_tension",
    "strong_natal",
    "weak_personal",
    "insufficient_data",
    "honest_general_better",
    "boundary_pressure",
    "tempo_overload",
    "clarity_vs_smooth",
    "work_deadline",
    "relationship_ask",
    "family_minute",
    "client_now",
    "draft_send",
    "standup_extra",
    "evening_checkin",
    "morning_email",
    "mixed_signals",
    "low_evidence",
    "high_evidence",
    "card_shift",
    "number_shift",
    "astro_loud",
    "quiet_sky",
    "recovery_day",
)

_TOKEN_RE = re.compile(r"[\wа-яё]+", re.I)


def _tokens(text: str) -> set[str]:
    return {t.lower() for t in _TOKEN_RE.findall(text or "") if len(t) > 2}


def token_jaccard(a: str, b: str) -> float:
    ta, tb = _tokens(a), _tokens(b)
    if not ta and not tb:
        return 1.0
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / max(1, len(ta | tb))


def _conflict_blob(native: dict[str, Any]) -> str:
    c = _as_dict(native.get("conflict"))
    return " ".join(
        str(c.get(k) or "")
        for k in ("title", "thesis", "force_a", "force_b", "why_today")
    )


def _scenes_blob(native: dict[str, Any]) -> str:
    parts: list[str] = []
    for s in _as_list(native.get("scenes")):
        if not isinstance(s, dict):
            continue
        parts.extend(
            str(s.get(k) or "")
            for k in (
                "setup",
                "opportunity",
                "trap",
                "recommended_action",
                "everyday_example",
            )
        )
    return " ".join(parts)


def _collect_codes(*sections: dict[str, Any]) -> list[str]:
    codes: list[str] = []
    for sec in sections:
        for c in sec.get("defect_codes") or []:
            if c:
                codes.append(str(c))
    return codes


def score_conflict_recognizability(native: dict[str, Any]) -> dict[str, Any]:
    c = _as_dict(native.get("conflict"))
    title = _clip(c.get("title"), 120)
    force_a = _clip(c.get("force_a"), 120)
    force_b = _clip(c.get("force_b"), 120)
    thesis = _clip(c.get("thesis"), 200)
    contract_checks = {
        "has_title": bool(title),
        "has_opposing_forces": bool(force_a) and bool(force_b) and force_a != force_b,
        "thesis_not_empty": len(thesis) >= 24,
    }
    editorial_checks = {
        "forces_not_echo_title": force_a.lower() not in title.lower()
        or force_b.lower() not in title.lower()
        or len(force_a) > 8,
        "forces_distinct_tokens": bool(force_a)
        and bool(force_b)
        and token_jaccard(force_a, force_b) < 0.85,
    }
    contract_score = sum(1 for v in contract_checks.values() if v) / max(1, len(contract_checks))
    editorial_score = sum(1 for v in editorial_checks.values() if v) / max(1, len(editorial_checks))
    score = round(0.55 * contract_score + 0.45 * editorial_score, 3)
    defect_codes: list[str] = []
    if not contract_checks["has_opposing_forces"]:
        defect_codes.append("CONFLICT_NO_OPPOSITION")
    if not contract_checks["has_title"]:
        defect_codes.append("CONFLICT_MISSING_TITLE")
    if not contract_checks["thesis_not_empty"]:
        defect_codes.append("CONFLICT_WEAK_THESIS")
    return {
        "score": score,
        "contract_score": round(contract_score, 3),
        "editorial_score": round(editorial_score, 3),
        "checks": {**contract_checks, **editorial_checks},
        "defect_codes": defect_codes,
    }


def score_scene_concreteness(
    native: dict[str, Any],
    *,
    locale: str = "ru",
) -> dict[str, Any]:
    """RU → C3.1 editorial gate; EN → C3.5.1 EN editorial gate (parity)."""
    loc = (locale or "ru").strip().lower()
    if loc == "en":
        scored = score_editorial_en_c351(native, locale="en")
        scene_codes = {
            c
            for c in (scored.get("defect_codes") or [])
            if str(c).startswith("SCENE_")
            or str(c) in {"THESIS_ECHO", DEFECT_LOCALE_LANGUAGE_MISMATCH}
        }
        return {
            "score": scored["editorial_score"],
            "contract_score": scored.get("contract_score", scored["editorial_score"]),
            "editorial_score": scored["editorial_score"],
            "mode": "editorial_gate_en_c351",
            "defect_codes": sorted(scene_codes),
            "checks": scored.get("checks") or {},
            "defects": scored.get("defects") or [],
        }

    defects = run_editorial_quality_gate_c31(native)
    scene_defs = [
        d
        for d in defects
        if str(d.get("code") or "").startswith("SCENE_") or str(d.get("code")) == "THESIS_ECHO"
    ]
    ed = score_editorial_quality_c31(scene_defs)
    scene_codes = {str(d.get("code") or "") for d in scene_defs}
    return {
        "score": ed["editorial_score"],
        "contract_score": ed.get("contract_score", ed["editorial_score"]),
        "editorial_score": ed["editorial_score"],
        "mode": "editorial_gate_c31",
        "defect_codes": sorted(scene_codes),
        "checks": {"editorial_clean": not scene_codes.intersection(CRITICAL_DEFECTS)},
        "defects": scene_defs,
    }


def score_chorus_coherence(
    native: dict[str, Any],
    *,
    locale: str = "ru",
) -> dict[str, Any]:
    loc = (locale or "ru").strip().lower()
    if loc == "en":
        defects = run_editorial_quality_gate_en_c351(native)
    else:
        defects = run_editorial_quality_gate_c31(native)
    chorus = [
        d
        for d in defects
        if str(d.get("code") or "").startswith("CHORUS_")
        or str(d.get("code") or "") in {"ASTRO_JARGON_BARE", "NATAL_WITHOUT_EVIDENCE"}
    ]
    parallel = any(
        str(d.get("code")) in {DEFECT_CHORUS_PARALLEL_FORECAST, DEFECT_CHORUS_SEMANTIC_DUPLICATION}
        for d in chorus
    )
    ed = score_editorial_quality_c31(chorus)
    return {
        "score": ed["editorial_score"],
        "contract_score": ed.get("contract_score", ed["editorial_score"]),
        "editorial_score": ed["editorial_score"],
        "checks": {
            "no_parallel_forecast": not parallel,
            "chorus_critical_clean": not any(
                str(d.get("code")) in CRITICAL_DEFECTS for d in chorus
            ),
        },
        "defect_codes": sorted({str(d.get("code")) for d in chorus}),
        "defects": chorus,
        "mode": "editorial_gate_en_c351" if loc == "en" else "editorial_gate_c31",
    }


def score_recommendation_provenance(
    native: dict[str, Any],
    pack: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """C3.5.1 provenance dual score (contract + editorial)."""
    return score_provenance_c351(native, pack)


def score_day_closure_quality(native: dict[str, Any]) -> dict[str, Any]:
    """C3.5.1 day_closure dual score — scenes alone cannot pass."""
    return score_day_closure_c351(native)


def score_cell(
    *,
    native: dict[str, Any],
    pack: dict[str, Any] | None = None,
    locale: str = "ru",
    profile_id: str = "",
) -> dict[str, Any]:
    """Score one (day × profile × locale) cell."""
    raw = _as_dict(native)
    n = normalize_native_scenario_llm_c1(deepcopy(raw)) if raw else {}
    # Eval-only: normalize currently drops day_closure / color props — reattach for scoring.
    if raw.get("day_closure") and not n.get("day_closure"):
        n["day_closure"] = deepcopy(raw["day_closure"])
    elif raw.get("closure") and not n.get("day_closure"):
        n["day_closure"] = deepcopy(raw["closure"])
    raw_props = _as_dict(raw.get("prop_material") or raw.get("props"))
    norm_props = _as_dict(n.get("prop_material"))
    for key in ("color", "avoid_color"):
        if raw_props.get(key) and not norm_props.get(key):
            norm_props[key] = deepcopy(raw_props[key])
    if norm_props:
        n["prop_material"] = norm_props
    pack = pack or {"evidence_depth": DEPTH_GENERAL, "evidence_refs": []}
    conflict = score_conflict_recognizability(n)
    scenes = score_scene_concreteness(n, locale=locale)
    chorus = score_chorus_coherence(n, locale=locale)
    provenance = score_recommendation_provenance(n, pack)
    closure = score_day_closure_quality(n)
    pers_defects = run_personalization_gate_c33(n, pack) if pack else []
    depth = str(pack.get("evidence_depth") or DEPTH_GENERAL)
    declared = str(n.get("personalization_depth") or "")
    is_control = profile_id in CONTROL_PROFILE_IDS
    honesty = {
        "control_stays_honest": (not is_control)
        or depth in {DEPTH_GENERAL, DEPTH_LIGHT},
        "depth_not_overclaim": declared in {"", depth}
        or (depth == DEPTH_GENERAL and declared in {"", DEPTH_GENERAL}),
        "pers_gate_tolerable": len(pers_defects) <= 2,
    }
    honesty_score = sum(1 for v in honesty.values() if v) / max(1, len(honesty))

    axes = {
        "conflict_recognizability": conflict["score"],
        "scene_concreteness": scenes["score"],
        "chorus_coherence": chorus["score"],
        "recommendation_provenance": provenance["score"],
        "day_closure_quality": closure["score"],
        "personalization_honesty": round(honesty_score, 3),
        "no_parallel_forecasts": 1.0 if chorus["checks"]["no_parallel_forecast"] else 0.0,
    }
    cell_score = sum(axes.values()) / max(1, len(axes))

    dual_sections = (conflict, scenes, chorus, provenance, closure)
    contract_vals = [float(s.get("contract_score") or s.get("score") or 0.0) for s in dual_sections]
    editorial_vals = [float(s.get("editorial_score") or s.get("score") or 0.0) for s in dual_sections]
    all_defects = _collect_codes(conflict, scenes, chorus, provenance, closure)
    all_defects.extend(str(d.get("code")) for d in pers_defects if d.get("code"))

    return {
        "profile_id": profile_id,
        "locale": locale,
        "axes": axes,
        "contract_score": round(sum(contract_vals) / max(1, len(contract_vals)), 3),
        "editorial_score": round(sum(editorial_vals) / max(1, len(editorial_vals)), 3),
        "defect_codes": sorted(set(all_defects)),
        "all_defect_codes": sorted(set(all_defects)),
        "details": {
            "conflict": conflict,
            "scenes": scenes,
            "chorus": chorus,
            "provenance": provenance,
            "closure": closure,
            "honesty": honesty,
            "pers_defect_codes": sorted({str(d.get("code")) for d in pers_defects}),
        },
        "score": round(cell_score, 3),
    }


def score_user_differentiation(
    cells_same_day: list[dict[str, Any]],
    natives_by_profile: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Same date: deep profiles must differ structurally; controls stay general."""
    profiles = [p for p in PROFILE_IDS if p in natives_by_profile]
    deep = [p for p in profiles if p not in CONTROL_PROFILE_IDS]
    diffs: list[dict[str, Any]] = []
    for i, a in enumerate(deep):
        for b in deep[i + 1 :]:
            dims = structural_diff_dimensions(natives_by_profile[a], natives_by_profile[b])
            diffs.append({"a": a, "b": b, "dimensions": dims, "ok": len(dims) >= DAY_DIFF_MIN_DIMENSIONS})
    control_ok = True
    for cid in CONTROL_PROFILE_IDS:
        control = natives_by_profile.get(cid)
        if control is None:
            continue
        depth = str(control.get("personalization_depth") or DEPTH_GENERAL)
        if depth not in {DEPTH_GENERAL, DEPTH_LIGHT, ""}:
            control_ok = False
            break
    ok_pairs = sum(1 for d in diffs if d["ok"])
    pair_score = ok_pairs / max(1, len(diffs)) if diffs else 0.0
    score = round(0.8 * pair_score + 0.2 * (1.0 if control_ok else 0.0), 3)
    return {
        "score": score,
        "pairs": diffs,
        "control_honest": control_ok,
        "checks": {"enough_pairs_differ": pair_score >= 0.66, "control_honest": control_ok},
    }


def score_formulation_repeatability(
    natives_by_day: list[dict[str, Any]],
) -> dict[str, Any]:
    """Consecutive days for one profile should not clone phrasing."""
    if len(natives_by_day) < 2:
        return {"score": 1.0, "checks": {"enough_days": False}, "max_jaccard": 0.0}
    jaccards: list[float] = []
    for i in range(1, len(natives_by_day)):
        prev = _conflict_blob(natives_by_day[i - 1]) + " " + _scenes_blob(natives_by_day[i - 1])
        cur = _conflict_blob(natives_by_day[i]) + " " + _scenes_blob(natives_by_day[i])
        jaccards.append(token_jaccard(prev, cur))
    max_j = max(jaccards) if jaccards else 0.0
    mean_j = sum(jaccards) / max(1, len(jaccards))
    score = max(0.0, min(1.0, 1.0 - mean_j))
    if max_j > REPEAT_JACCARD_SOFT_MAX:
        score = min(score, 0.55)
    return {
        "score": round(score, 3),
        "mean_jaccard": round(mean_j, 3),
        "max_jaccard": round(max_j, 3),
        "checks": {"no_day_clone": max_j <= REPEAT_JACCARD_SOFT_MAX},
    }


def _shape_ok(dates: list[str], profiles: list[str], locales: list[str], cells: int) -> bool:
    """Accept legacy C3.5.0 (14×4×2) or C3.5.1 (≥28×≥8×ru+en, ≥400 cells)."""
    locales_ok = set(locales) >= {"ru", "en"}
    has_control = bool(CONTROL_PROFILE_IDS.intersection(profiles)) or "no_birth_time" in profiles
    legacy = len(dates) >= 14 and len(profiles) >= 4 and has_control and locales_ok
    c351 = (
        len(dates) >= C351_MIN_DAYS
        and len(profiles) >= C351_MIN_PROFILES
        and locales_ok
        and cells >= C351_MIN_CELLS
    )
    return legacy or c351


def _defect_histogram(rows: list[dict[str, Any]]) -> dict[str, int]:
    from collections import Counter

    ctr: Counter[str] = Counter()
    for r in rows:
        for c in r.get("all_defect_codes") or r.get("defect_codes") or []:
            if c:
                ctr[str(c)] += 1
        details = _as_dict(r.get("details"))
        for sec in details.values():
            if isinstance(sec, dict):
                for c in sec.get("defect_codes") or []:
                    if c:
                        ctr[str(c)] += 1
    return dict(ctr.most_common())


def run_eval_pack_c35(
    cells: Iterable[dict[str, Any]],
    *,
    pass_threshold: float = PACK_PASS_THRESHOLD,
) -> dict[str, Any]:
    """Run full pack.

    Each cell: {date, profile_id, locale, native, pack?, day_type?}
    """
    raw_cells = list(cells)
    rows: list[dict[str, Any]] = []
    for raw in raw_cells:
        d = str(raw.get("date") or "")
        pid = str(raw.get("profile_id") or "")
        loc = str(raw.get("locale") or "ru")
        native = _as_dict(raw.get("native"))
        pack = _as_dict(raw.get("pack")) if raw.get("pack") is not None else None
        scored = score_cell(native=native, pack=pack, locale=loc, profile_id=pid)
        row = {"date": d, "profile_id": pid, "locale": loc, **scored}
        if raw.get("day_type"):
            row["day_type"] = str(raw.get("day_type"))
        rows.append(row)

    dates = sorted({r["date"] for r in rows})
    locales = sorted({r["locale"] for r in rows})
    profiles = sorted({r["profile_id"] for r in rows})

    day_diff_scores: list[float] = []
    day_diff_reports: list[dict[str, Any]] = []

    for loc in locales:
        for day in dates:
            natives: dict[str, dict[str, Any]] = {}
            day_rows = [r for r in rows if r["date"] == day and r["locale"] == loc]
            for c in raw_cells:
                if str(c.get("date")) == day and str(c.get("locale") or "ru") == loc:
                    natives[str(c.get("profile_id"))] = normalize_native_scenario_llm_c1(
                        deepcopy(_as_dict(c.get("native")))
                    )
            if len(natives) < 2:
                continue
            report = score_user_differentiation(day_rows, natives)
            day_diff_scores.append(report["score"])
            day_diff_reports.append({"date": day, "locale": loc, **report})

    repeat_scores: list[float] = []
    repeat_reports: list[dict[str, Any]] = []
    for loc in locales:
        for pid in profiles:
            seq = []
            for day in dates:
                for c in raw_cells:
                    if (
                        str(c.get("date")) == day
                        and str(c.get("profile_id")) == pid
                        and str(c.get("locale") or "ru") == loc
                    ):
                        seq.append(normalize_native_scenario_llm_c1(deepcopy(_as_dict(c.get("native")))))
                        break
            if len(seq) < 2:
                continue
            rep = score_formulation_repeatability(seq)
            repeat_scores.append(rep["score"])
            repeat_reports.append({"profile_id": pid, "locale": loc, **rep})

    mean_cell = sum(r["score"] for r in rows) / max(1, len(rows))
    mean_diff = sum(day_diff_scores) / max(1, len(day_diff_scores)) if day_diff_scores else 0.0
    mean_rep = sum(repeat_scores) / max(1, len(repeat_scores)) if repeat_scores else 0.0

    aggregate_axes = {
        "conflict_recognizability": _mean_axis(rows, "conflict_recognizability"),
        "scene_concreteness": _mean_axis(rows, "scene_concreteness"),
        "chorus_coherence": _mean_axis(rows, "chorus_coherence"),
        "user_differentiation": round(mean_diff, 3),
        "formulation_repeatability": round(mean_rep, 3),
        "recommendation_provenance": _mean_axis(rows, "recommendation_provenance"),
        "no_parallel_forecasts": _mean_axis(rows, "no_parallel_forecasts"),
        "day_closure_quality": _mean_axis(rows, "day_closure_quality"),
    }
    pack_score = sum(aggregate_axes.values()) / max(1, len(aggregate_axes))

    shape_ok = _shape_ok(dates, profiles, locales, len(rows))
    worst = sorted(rows, key=lambda r: float(r.get("score") or 0.0))[:20]
    worst_cells = [
        {
            "date": r.get("date"),
            "profile_id": r.get("profile_id"),
            "locale": r.get("locale"),
            "day_type": r.get("day_type"),
            "score": r.get("score"),
            "contract_score": r.get("contract_score"),
            "editorial_score": r.get("editorial_score"),
            "defect_codes": (r.get("defect_codes") or [])[:12],
        }
        for r in worst
    ]

    return {
        "contract_version": EVAL_CONTRACT,
        "eval_version": EVAL_VERSION,
        "thresholds_provisional": {
            **THRESHOLDS_PROVISIONAL,
            "pack_pass_threshold": pass_threshold,
            "pack_pass_note": "PROVISIONAL pack gate 0.75; cell bands reject/review/pass documented separately",
        },
        "shape": {
            "days": len(dates),
            "profiles": profiles,
            "locales": locales,
            "cells": len(rows),
            "shape_ok": shape_ok,
            "c351_shape_ok": (
                len(dates) >= C351_MIN_DAYS
                and len(profiles) >= C351_MIN_PROFILES
                and set(locales) >= {"ru", "en"}
                and len(rows) >= C351_MIN_CELLS
            ),
        },
        "aggregate_axes": aggregate_axes,
        "mean_cell_score": round(mean_cell, 3),
        "pack_score": round(pack_score, 3),
        "pass": bool(shape_ok and pack_score >= pass_threshold),
        "pass_threshold": pass_threshold,
        "cells": rows,
        "day_differentiation": day_diff_reports,
        "repeatability": repeat_reports,
        "worst_cells": worst_cells,
        "defect_histogram": _defect_histogram(rows),
    }


def _mean_axis(rows: list[dict[str, Any]], axis: str) -> float:
    vals = [float(_as_dict(r.get("axes")).get(axis) or 0.0) for r in rows]
    return round(sum(vals) / max(1, len(vals)), 3)


# ---------------------------------------------------------------------------
# Synthetic fixture matrix (CI — no Nebius)
# ---------------------------------------------------------------------------

_DAY_VARIANTS_RU = [
    {
        "title": "Прояснение против сглаживания",
        "setup_rel": "В мессенджере спрашивают «всё ли в порядке?» именно когда хочется ответить «нормально».",
        "example_rel": "Сообщение от партнёра в 21:40: вопрос «ты где?»",
        "setup_work": "Коллега в чате просит «быстро окнуть» письмо, которое вы ещё не дочитали.",
        "example_work": "Рабочий чат, 11:15: «ок?» под длинным письмом.",
        "card": "Отшельник",
        "number": 7,
        "astro": "Луна в Рыбах",
    },
    {
        "title": "Темп против перегруза",
        "setup_rel": "Друг зовёт «на пять минут» созвон, а у вас уже третий незакрытый разговор.",
        "example_rel": "Звонок в 19:05 после длинного дня.",
        "setup_work": "На планёрке просят «ещё один апдейт» до обеда.",
        "example_work": "Созвон 12:40: «и ещё слайд про риски».",
        "card": "Умеренность",
        "number": 5,
        "astro": "Меркурий в Деве",
    },
    {
        "title": "Граница против удобства",
        "setup_rel": "Мама пишет: «зайди на минутку», зная, что минутка растянется на час.",
        "example_rel": "Сообщение в 18:20 у подъезда.",
        "setup_work": "Клиент просит созвон «прямо сейчас» без повестки.",
        "example_work": "Письмо 09:50: «срочно созвонимся?».",
        "card": "Император",
        "number": 4,
        "astro": "Сатурн аспект к Луне",
    },
    {
        "title": "Действие против откладывания",
        "setup_rel": "Партнёр ждёт ответа на приглашение, а вы снова открываете переписку без отправки.",
        "example_rel": "Черновик ответа в мессенджере с 15:10.",
        "setup_work": "Тикет висит «in progress» третий день без комментария.",
        "example_work": "Jira 16:00: статус без апдейта.",
        "card": "Колесница",
        "number": 1,
        "astro": "Марс в Овне",
    },
    {
        "title": "Автономия против согласия",
        "setup_rel": "Друзья решают за вас маршрут вечера в общем чате.",
        "example_rel": "Групповой чат 20:10: «мы уже заказали столик».",
        "setup_work": "Руководитель меняет приоритет задачи без вашего ок.",
        "example_work": "Слак 10:05: «переключаемся на X».",
        "card": "Сила",
        "number": 8,
        "astro": "Уран аспект к Солнцу",
    },
    {
        "title": "Ответственность против делегирования",
        "setup_rel": "Сосед просит «помочь с бумагами», хотя задача не ваша.",
        "example_rel": "Сообщение у двери в 17:40.",
        "setup_work": "Коллега скидывает свой отчёт «на глаз на пять минут».",
        "example_work": "Почта 14:20: вложение без контекста.",
        "card": "Справедливость",
        "number": 6,
        "astro": "Сатурн в Козероге",
    },
    {
        "title": "Близость против самозащиты",
        "setup_rel": "Партнёр предлагает серьёзный разговор после лёгкой шутки в чате.",
        "example_rel": "Сообщение 22:05: «можем поговорить?»",
        "setup_work": "На ревью хвалят и сразу просят «ещё чуть больше».",
        "example_work": "Комментарий в доке 13:30.",
        "card": "Влюблённые",
        "number": 2,
        "astro": "Венера в Раке",
    },
]

_DAY_VARIANTS_EN = [
    {
        "title": "Clarity versus smoothing",
        "setup_rel": "A chat message asks “are you okay?” exactly when you want to answer “fine”.",
        "example_rel": "Partner message at 21:40: “where are you?”",
        "setup_work": "A colleague in chat asks you to quickly OK an email you have not finished reading.",
        "example_work": "Work chat, 11:15: “ok?” under a long email.",
        "card": "The Hermit",
        "number": 7,
        "astro": "Moon in Pisces",
    },
    {
        "title": "Pace versus overload",
        "setup_rel": "A friend asks for a “five-minute” call when you already have three open threads.",
        "example_rel": "Phone call at 19:05 after a long day.",
        "setup_work": "In the standup they ask for “one more update” before lunch.",
        "example_work": "Meeting at 12:40: “and one more risk slide”.",
        "card": "Temperance",
        "number": 5,
        "astro": "Mercury in Virgo",
    },
    {
        "title": "Boundary versus convenience",
        "setup_rel": "A parent texts “just stop by for a minute,” knowing a minute becomes an hour.",
        "example_rel": "Message at 18:20 by the door.",
        "setup_work": "A client asks for a call “right now” with no agenda.",
        "example_work": "Email at 09:50: “can we jump on a call?”",
        "card": "The Emperor",
        "number": 4,
        "astro": "Saturn aspect to Moon",
    },
    {
        "title": "Action versus delay",
        "setup_rel": "A partner waits on an invite reply while you reopen the thread without sending.",
        "example_rel": "Draft reply sitting since 15:10.",
        "setup_work": "A ticket sits “in progress” for a third day with no comment.",
        "example_work": "Jira at 16:00: status with no update.",
        "card": "The Chariot",
        "number": 1,
        "astro": "Mars in Aries",
    },
    {
        "title": "Autonomy versus agreement",
        "setup_rel": "Friends decide the evening plan for you in the group chat.",
        "example_rel": "Group chat 20:10: “we already booked a table”.",
        "setup_work": "A manager switches your priority without your ok.",
        "example_work": "Slack 10:05: “we’re switching to X”.",
        "card": "Strength",
        "number": 8,
        "astro": "Uranus aspect to Sun",
    },
    {
        "title": "Responsibility versus delegation",
        "setup_rel": "A neighbor asks for “help with paperwork” that is not yours.",
        "example_rel": "Door message at 17:40.",
        "setup_work": "A colleague dumps their report “for a five-minute look”.",
        "example_work": "Email 14:20: attachment with no context.",
        "card": "Justice",
        "number": 6,
        "astro": "Saturn in Capricorn",
    },
    {
        "title": "Closeness versus self-protection",
        "setup_rel": "A partner asks for a serious talk after a light joke in chat.",
        "example_rel": "Message at 22:05: “can we talk?”",
        "setup_work": "In review they praise you and immediately ask for “a bit more”.",
        "example_work": "Doc comment at 13:30.",
        "card": "The Lovers",
        "number": 2,
        "astro": "Venus in Cancer",
    },
]


def _conflict_id_for(title: str) -> str:
    return conflict_anchor_id({"title": title})


def _day_closure_for(variant: dict[str, Any], *, day_i: int, locale: str) -> dict[str, str]:
    title = variant["title"]
    if locale == "en":
        return {
            "resolution": f"By evening you chose one clear side of “{title}” (day {day_i + 1}).",
            "remaining_tension": "A mild pull toward the habitual force remains.",
            "evening_state": "Quieter contact without false harmony.",
            "conflict_callback": f"The conflict “{title}” closed through one concrete reply.",
        }
    return {
        "resolution": f"К вечеру вы выбрали одну ясную сторону «{title}» (день {day_i + 1}).",
        "remaining_tension": "Остаётся лёгкое тяготение к привычной силе.",
        "evening_state": "Тише контакт без ложной гармонии.",
        "conflict_callback": f"Конфликт «{title}» закрыт одним конкретным ответом.",
    }


def _profile_pack(profile_id: str) -> dict[str, Any]:
    if profile_id in {"no_birth_time", "no_profile", "birth_date_only"}:
        return {
            "evidence_depth": DEPTH_GENERAL,
            "evidence_refs": [],
            "behavioral_tendencies": [],
            "sensitive_domains": [],
            "confidence": 0.15 if profile_id == "no_profile" else 0.2,
        }
    if profile_id == "incomplete_evidence":
        return {
            "evidence_depth": DEPTH_LIGHT,
            "evidence_refs": ["claim.personal.partial"],
            "behavioral_tendencies": [],
            "sensitive_domains": [],
            "confidence": 0.35,
            "incomplete": True,
        }

    packs = {
        "smooth_conflict": {
            "evidence_depth": DEPTH_DEEP,
            "evidence_refs": ["claim.personal.moon7.smooth", "claim.personal.venus.reject"],
            "behavioral_tendencies": [
                {
                    "id": "smooth_conflict",
                    "label": "smooth",
                    "confidence": 0.8,
                    "source_refs": ["claim.personal.moon7.smooth"],
                }
            ],
            "sensitive_domains": [{"sphere": "relationships", "reason": "rejection sensitivity"}],
            "confidence": 0.75,
        },
        "demand_clarity": {
            "evidence_depth": DEPTH_DEEP,
            "evidence_refs": ["claim.personal.mars1.direct", "claim.personal.sat.overload"],
            "behavioral_tendencies": [
                {
                    "id": "over_control",
                    "label": "control",
                    "confidence": 0.8,
                    "source_refs": ["claim.personal.mars1.direct"],
                }
            ],
            "sensitive_domains": [{"sphere": "work_decisions", "reason": "overload"}],
            "confidence": 0.78,
        },
        "analyze_first": {
            "evidence_depth": DEPTH_DEEP,
            "evidence_refs": ["claim.personal.merc.analyze", "claim.personal.sat.delay"],
            "behavioral_tendencies": [
                {
                    "id": "analyze_first",
                    "label": "analyze",
                    "confidence": 0.77,
                    "source_refs": ["claim.personal.merc.analyze"],
                }
            ],
            "sensitive_domains": [{"sphere": "communication", "reason": "overthink"}],
            "confidence": 0.7,
        },
        "act_first": {
            "evidence_depth": DEPTH_DEEP,
            "evidence_refs": ["claim.personal.mars.act", "claim.personal.fire.tempo"],
            "behavioral_tendencies": [
                {
                    "id": "act_first",
                    "label": "act",
                    "confidence": 0.76,
                    "source_refs": ["claim.personal.mars.act"],
                }
            ],
            "sensitive_domains": [{"sphere": "work_decisions", "reason": "impulse"}],
            "confidence": 0.72,
        },
        "over_responsible": {
            "evidence_depth": DEPTH_DEEP,
            "evidence_refs": ["claim.personal.sat.duty", "claim.personal.moon.care"],
            "behavioral_tendencies": [
                {
                    "id": "over_responsible",
                    "label": "carry",
                    "confidence": 0.79,
                    "source_refs": ["claim.personal.sat.duty"],
                }
            ],
            "sensitive_domains": [{"sphere": "family", "reason": "duty load"}],
            "confidence": 0.74,
        },
        "rejection_sensitive": {
            "evidence_depth": DEPTH_DEEP,
            "evidence_refs": ["claim.personal.venus.reject", "claim.personal.moon7.smooth"],
            "behavioral_tendencies": [
                {
                    "id": "rejection_sensitive",
                    "label": "guard",
                    "confidence": 0.78,
                    "source_refs": ["claim.personal.venus.reject"],
                }
            ],
            "sensitive_domains": [{"sphere": "relationships", "reason": "rejection"}],
            "confidence": 0.73,
        },
        "autonomy_oriented": {
            "evidence_depth": DEPTH_DEEP,
            "evidence_refs": ["claim.personal.uranus.auto", "claim.personal.sun.self"],
            "behavioral_tendencies": [
                {
                    "id": "autonomy_oriented",
                    "label": "autonomy",
                    "confidence": 0.77,
                    "source_refs": ["claim.personal.uranus.auto"],
                }
            ],
            "sensitive_domains": [{"sphere": "work_decisions", "reason": "control friction"}],
            "confidence": 0.71,
        },
    }
    return packs.get(
        profile_id,
        {
            "evidence_depth": DEPTH_DEEP,
            "evidence_refs": ["claim.personal.generic"],
            "behavioral_tendencies": [],
            "sensitive_domains": [],
            "confidence": 0.6,
        },
    )


def _apply_profile_core(
    out: dict[str, Any],
    profile_id: str,
    *,
    day_i: int,
    locale: str,
) -> dict[str, Any]:
    ru = locale == "ru"
    if profile_id in CONTROL_PROFILE_IDS:
        out["personalization_depth"] = DEPTH_GENERAL if profile_id != "incomplete_evidence" else DEPTH_LIGHT
        out["interpretive_chorus"]["natal"] = []
        out["conflict"]["why_personal"] = ""
        return out

    out["personalization_depth"] = DEPTH_DEEP
    specs: dict[str, dict[str, Any]] = {
        "smooth_conflict": {
            "force_a": "сгладить ради тишины" if ru else "smooth for quiet",
            "force_b": "сказать коротко и честно" if ru else "say it short and honest",
            "sphere": "relationships",
            "scene_id": "scene.relationships",
            "action": (
                f"Сказать одну конкретную фразу вместо молчания (день {day_i + 1})."
                if ru
                else f"Send one concrete sentence instead of silence (day {day_i + 1})."
            ),
            "refs": ["claim.personal.moon7.smooth", "claim.personal.venus.reject"],
            "pattern": "smooth_conflict",
        },
        "demand_clarity": {
            "force_a": "давить ясностью" if ru else "push for clarity",
            "force_b": "один вопрос до ответа" if ru else "one question before answering",
            "sphere": "work_decisions",
            "scene_id": "scene.work_decisions",
            "action": (
                f"Задать один вопрос до ответа; не решать за коллегу (день {day_i + 1})."
                if ru
                else f"Ask one question before answering; do not decide for them (day {day_i + 1})."
            ),
            "refs": ["claim.personal.mars1.direct", "claim.personal.sat.overload"],
            "pattern": "over_control",
            "trap": "Превратить ясность в давление." if ru else "Turn clarity into pressure.",
        },
        "analyze_first": {
            "force_a": "ещё один анализ" if ru else "one more analysis pass",
            "force_b": "маленький видимый шаг" if ru else "a small visible step",
            "sphere": "communication",
            "scene_id": "scene.communication",
            "action": (
                f"Отправить черновик из трёх предложений без второго прохода (день {day_i + 1})."
                if ru
                else f"Send a three-sentence draft without a second pass (day {day_i + 1})."
            ),
            "refs": ["claim.personal.merc.analyze", "claim.personal.sat.delay"],
            "pattern": "analyze_first",
        },
        "act_first": {
            "force_a": "сразу рвануть" if ru else "jump immediately",
            "force_b": "одна проверка перед шагом" if ru else "one check before stepping",
            "sphere": "work_decisions",
            "scene_id": "scene.work_decisions",
            "action": (
                f"Сделать один шаг и написать статус через 10 минут (день {day_i + 1})."
                if ru
                else f"Take one step and post a status in 10 minutes (day {day_i + 1})."
            ),
            "refs": ["claim.personal.mars.act", "claim.personal.fire.tempo"],
            "pattern": "act_first",
        },
        "over_responsible": {
            "force_a": "взять всё на себя" if ru else "carry everything",
            "force_b": "вернуть задачу владельцу" if ru else "return the task to its owner",
            "sphere": "family",
            "scene_id": "scene.family",
            "action": (
                f"Назвать границу одним предложением и не брать чужой список (день {day_i + 1})."
                if ru
                else f"Name one boundary sentence and do not take their list (day {day_i + 1})."
            ),
            "refs": ["claim.personal.sat.duty", "claim.personal.moon.care"],
            "pattern": "over_responsible",
        },
        "rejection_sensitive": {
            "force_a": "закрыться заранее" if ru else "close up early",
            "force_b": "один честный факт" if ru else "one honest fact",
            "sphere": "relationships",
            "scene_id": "scene.relationships",
            "action": (
                f"Ответить одним фактом без самообесценивания (день {day_i + 1})."
                if ru
                else f"Reply with one fact without self-discounting (day {day_i + 1})."
            ),
            "refs": ["claim.personal.venus.reject", "claim.personal.moon7.smooth"],
            "pattern": "rejection_sensitive",
        },
        "autonomy_oriented": {
            "force_a": "уйти в отказ молча" if ru else "refuse in silence",
            "force_b": "назвать своё условие" if ru else "name your condition",
            "sphere": "work_decisions",
            "scene_id": "scene.work_decisions",
            "action": (
                f"Написать одно условие участия до согласия (день {day_i + 1})."
                if ru
                else f"Write one participation condition before agreeing (day {day_i + 1})."
            ),
            "refs": ["claim.personal.uranus.auto", "claim.personal.sun.self"],
            "pattern": "autonomy_oriented",
        },
    }
    spec = specs.get(profile_id) or specs["smooth_conflict"]
    out["conflict"]["force_a"] = spec["force_a"]
    out["conflict"]["force_b"] = spec["force_b"]
    out["conflict"]["personalization"] = {
        "personalization_level": DEPTH_DEEP,
        "personalization_reason": spec["pattern"],
        "personalization_evidence_refs": [spec["refs"][0]],
        "habitual_force": "a",
        "required_movement": "b",
        "general_fallback_available": True,
    }
    # Prefer matching scene; else mutate first
    scenes = out.get("scenes") or []
    target_i = 0
    for i, s in enumerate(scenes):
        if isinstance(s, dict) and s.get("scene_id") == spec["scene_id"]:
            target_i = i
            break
    if scenes and isinstance(scenes[target_i], dict):
        scenes[target_i]["sphere"] = spec["sphere"]
        scenes[target_i]["scene_id"] = spec["scene_id"]
        scenes[target_i]["recommended_action"] = spec["action"]
        if spec.get("trap"):
            scenes[target_i]["trap"] = spec["trap"]
        scenes[target_i]["personalization"] = {
            "personalization_level": DEPTH_DEEP,
            "personalization_reason": spec["sphere"],
            "personalization_evidence_refs": [spec["refs"][-1]],
            "sphere_reason": spec["pattern"],
            "response_pattern": spec["pattern"],
            "general_fallback_available": True,
        }
        if "evidence_refs" not in scenes[target_i]:
            scenes[target_i]["evidence_refs"] = ["sky-factor"]
        # ensure personal ref present for provenance
        refs = list(scenes[target_i].get("evidence_refs") or [])
        for r in spec["refs"]:
            if r not in refs:
                refs.append(r)
        scenes[target_i]["evidence_refs"] = refs
        # Keep props bound to an existing scene_id
        props = _as_dict(out.get("prop_material"))
        props["color_scene_candidates"] = [spec["scene_id"]]
        aff = _as_dict(props.get("affirmation_tension"))
        if aff:
            aff["scene_id"] = spec["scene_id"]
            props["affirmation_tension"] = aff
        color = _as_dict(props.get("color"))
        if color:
            color["scene_id"] = spec["scene_id"]
            props["color"] = color
        out["prop_material"] = props
    out["interpretive_chorus"]["natal"] = [
        {
            "named_factor": spec["pattern"],
            "human_meaning": (
                "Личная привычка тянет к силе A в том же конфликте."
                if ru
                else "Personal habit pulls toward force A in the same conflict."
            ),
            "link_to_conflict": (
                f"Поэтому в конфликте «{out['conflict']['title']}» важна сила B."
                if ru
                else f"That is why conflict “{out['conflict']['title']}” needs force B."
            ),
            "evidence_refs": [spec["refs"][0]],
            "conflict_id": _conflict_id_for(str(out["conflict"]["title"])),
        }
    ]
    return out


def _apply_profile(native: dict[str, Any], profile_id: str, *, day_i: int) -> dict[str, Any]:
    return _apply_profile_core(deepcopy(native), profile_id, day_i=day_i, locale="ru")


def _apply_profile_en(native: dict[str, Any], profile_id: str, *, day_i: int) -> dict[str, Any]:
    return _apply_profile_core(deepcopy(native), profile_id, day_i=day_i, locale="en")


def _base_native_ru(variant: dict[str, Any], *, day_i: int) -> dict[str, Any]:
    return {
        "schema_version": NATIVE_LLM_SCHEMA_VERSION,
        "interpretive_chorus": {
            "astrology": [
                {
                    "named_factor": variant["astro"],
                    "human_meaning": "Эмоциональный подтекст становится заметнее прямых слов.",
                    "link_to_conflict": f"Поэтому в конфликте «{variant['title']}» хочется выбрать одну сторону.",
                    "evidence_refs": ["sky-factor"],
                    "conflict_id": _conflict_id_for(variant["title"]),
                }
            ],
            "day_card": {
                "named_factor": f"Карта дня — {variant['card']}",
                "archetype_role": "Архетип реакции на конфликт дня.",
                "link_to_conflict": "Карта называет, как проходить тот же выбор.",
                "evidence_refs": ["day_card"],
                "conflict_id": _conflict_id_for(variant["title"]),
            },
            "day_number": {
                "named_factor": f"Число дня — {variant['number']}",
                "tempo": "сначала понять" if day_i % 2 == 0 else "короткий шаг",
                "style": "без спешки",
                "link_to_conflict": "Число задаёт темп прохождения конфликта.",
                "evidence_refs": ["day_number"],
                "conflict_id": _conflict_id_for(variant["title"]),
            },
            "natal": [],
        },
        "conflict": {
            "title": variant["title"],
            "thesis": f"Сегодня важнее выбрать сторону конфликта: {variant['title']}.",
            "force_a": "привычный путь",
            "force_b": "нужное движение",
            "why_today": f"{variant['astro']} усиливает тему дня.",
            "why_personal": "",
            "driver_refs": ["sky-factor"],
            "evidence_refs": ["sky-factor"],
        },
        "scenes": [
            {
                "scene_id": "scene.relationships",
                "sphere": "relationships",
                "role_in_story": "primary",
                "setup": variant["setup_rel"],
                "opportunity": "Назвать факт одним коротким сообщением.",
                "trap": "Согласиться ради тишины и потом злиться.",
                "recommended_action": f"Открыть черновик и отправить один абзац (вариант {day_i + 1}).",
                "avoid_action": "Не отвечать автоматическим «всё ок».",
                "everyday_example": variant["example_rel"],
                "evidence_refs": ["sky-factor"],
                "chorus_refs": ["conflict", "day_card"],
            },
            {
                "scene_id": "scene.work_decisions",
                "sphere": "work_decisions",
                "role_in_story": "support",
                "setup": variant["setup_work"],
                "opportunity": "Вернуться с точным временем ответа.",
                "trap": "Поставить «ок» и чинить чужие ожидания.",
                "recommended_action": f"Одно сообщение с временем возврата (день {day_i + 1}).",
                "avoid_action": "Не ставить реакцию без чтения.",
                "everyday_example": variant["example_work"],
                "evidence_refs": ["sky-factor"],
                "chorus_refs": ["conflict", "astrology"],
            },
        ],
        "prop_material": {
            "color_scene_candidates": ["scene.relationships"],
            "affirmation_tension": {
                "scene_id": "scene.relationships",
                "trap": "сгладить",
                "text": f"Я могу выбрать ясность без давления (день {day_i + 1}).",
            },
            "color": {
                "scene_id": "scene.relationships",
                "name": "синий",
                "note": "Цвет паузы перед ясным ответом.",
            },
        },
        "day_closure": _day_closure_for(variant, day_i=day_i, locale="ru"),
    }


def _base_native_en(variant: dict[str, Any], *, day_i: int) -> dict[str, Any]:
    return {
        "schema_version": NATIVE_LLM_SCHEMA_VERSION,
        "interpretive_chorus": {
            "astrology": [
                {
                    "named_factor": variant["astro"],
                    "human_meaning": "Emotional subtext becomes louder than direct words.",
                    "link_to_conflict": f"That is why the conflict “{variant['title']}” asks for one clear side.",
                    "evidence_refs": ["sky-factor"],
                    "conflict_id": _conflict_id_for(variant["title"]),
                }
            ],
            "day_card": {
                "named_factor": f"Day card — {variant['card']}",
                "archetype_role": "Archetype of how to meet the day's conflict.",
                "link_to_conflict": "The card names the reaction style for the same choice.",
                "evidence_refs": ["day_card"],
                "conflict_id": _conflict_id_for(variant["title"]),
            },
            "day_number": {
                "named_factor": f"Day number — {variant['number']}",
                "tempo": "understand first" if day_i % 2 == 0 else "one short step",
                "style": "without rush",
                "link_to_conflict": "The number sets the tempo through the conflict.",
                "evidence_refs": ["day_number"],
                "conflict_id": _conflict_id_for(variant["title"]),
            },
            "natal": [],
        },
        "conflict": {
            "title": variant["title"],
            "thesis": f"Today it matters more to pick a side: {variant['title']}.",
            "force_a": "habitual path",
            "force_b": "needed movement",
            "why_today": f"{variant['astro']} amplifies the day's theme.",
            "why_personal": "",
            "driver_refs": ["sky-factor"],
            "evidence_refs": ["sky-factor"],
        },
        "scenes": [
            {
                "scene_id": "scene.relationships",
                "sphere": "relationships",
                "role_in_story": "primary",
                "setup": variant["setup_rel"],
                "opportunity": "Name one fact in a short message.",
                "trap": "Agree for quiet and resent it later.",
                "recommended_action": f"Open a draft and send one paragraph (variant {day_i + 1}).",
                "avoid_action": "Do not reply with automatic “I'm fine”.",
                "everyday_example": variant["example_rel"],
                "evidence_refs": ["sky-factor"],
                "chorus_refs": ["conflict", "day_card"],
            },
            {
                "scene_id": "scene.work_decisions",
                "sphere": "work_decisions",
                "role_in_story": "support",
                "setup": variant["setup_work"],
                "opportunity": "Come back with an exact reply time.",
                "trap": "Hit “ok” and then repair expectations.",
                "recommended_action": f"One message with a return time (day {day_i + 1}).",
                "avoid_action": "Do not react before reading.",
                "everyday_example": variant["example_work"],
                "evidence_refs": ["sky-factor"],
                "chorus_refs": ["conflict", "astrology"],
            },
        ],
        "prop_material": {
            "color_scene_candidates": ["scene.relationships"],
            "affirmation_tension": {
                "scene_id": "scene.relationships",
                "trap": "smooth",
                "text": f"I can choose clarity without pressure (day {day_i + 1}).",
            },
            "color": {
                "scene_id": "scene.relationships",
                "name": "blue",
                "note": "Color of the pause before a clear reply.",
            },
        },
        "day_closure": _day_closure_for(variant, day_i=day_i, locale="en"),
    }


def _build_matrix(
    *,
    start: date,
    days: int,
    profile_ids: tuple[str, ...],
) -> list[dict[str, Any]]:
    cells: list[dict[str, Any]] = []
    for i in range(days):
        d = start + timedelta(days=i)
        date_s = d.isoformat()
        day_type = DAY_TYPES[i % len(DAY_TYPES)]
        v_ru = _DAY_VARIANTS_RU[i % len(_DAY_VARIANTS_RU)]
        v_ru = {
            **v_ru,
            "title": f"{v_ru['title']} · {i + 1}",
            "setup_rel": f"{v_ru['setup_rel']} (день {i + 1})",
            "setup_work": f"{v_ru['setup_work']} (день {i + 1})",
        }
        v_en = _DAY_VARIANTS_EN[i % len(_DAY_VARIANTS_EN)]
        v_en = {
            **v_en,
            "title": f"{v_en['title']} · {i + 1}",
            "setup_rel": f"{v_en['setup_rel']} (day {i + 1})",
            "setup_work": f"{v_en['setup_work']} (day {i + 1})",
        }
        for pid in profile_ids:
            pack = _profile_pack(pid)
            native_ru = _apply_profile(_base_native_ru(v_ru, day_i=i), pid, day_i=i)
            native_en = _apply_profile_en(_base_native_en(v_en, day_i=i), pid, day_i=i)
            shared_ru = {
                "date": date_s,
                "card": v_ru["card"],
                "number": v_ru["number"],
                "thesis_family": "communication",
                "day_type": day_type,
            }
            shared_en = {
                "date": date_s,
                "card": v_en["card"],
                "number": v_en["number"],
                "thesis_family": "communication",
                "day_type": day_type,
            }
            cells.append(
                {
                    "date": date_s,
                    "profile_id": pid,
                    "locale": "ru",
                    "day_type": day_type,
                    "native": native_ru,
                    "pack": pack,
                    "shared_day": shared_ru,
                }
            )
            cells.append(
                {
                    "date": date_s,
                    "profile_id": pid,
                    "locale": "en",
                    "day_type": day_type,
                    "native": native_en,
                    "pack": pack,
                    "shared_day": shared_en,
                }
            )
    return cells


def build_synthetic_eval_matrix_c351(
    *,
    start: date | None = None,
    days: int = 28,
    profile_ids: tuple[str, ...] | None = None,
) -> list[dict[str, Any]]:
    """C3.5.1 CI matrix: days × profiles × locales (≥400 cells at defaults)."""
    start = start or date(2026, 7, 12)
    pids = profile_ids or PROFILE_IDS
    return _build_matrix(start=start, days=days, profile_ids=pids)


def build_synthetic_eval_matrix_c35(
    *,
    start: date | None = None,
    days: int = 14,
) -> list[dict[str, Any]]:
    """Legacy C3.5.0 wrapper: 14 × first-4 profiles × ru/en (112 cells)."""
    start = start or date(2026, 7, 12)
    return _build_matrix(start=start, days=days, profile_ids=PROFILE_IDS_C35_LEGACY)

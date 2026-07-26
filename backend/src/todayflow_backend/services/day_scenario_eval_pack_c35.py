"""Phase C3.5 — Multi-day × multi-profile × multi-locale eval pack.

Comparative harness over fixture/captured scenarios (no Nebius in CI):

- 14 consecutive days
- ≥3 natal-dynamic profiles + 1 without birth time
- ru + en
- same dates across profiles for personalization compare

Scores: conflict recognizability · scene concreteness · chorus coherence ·
user differentiation · formulation repeatability · recommendation provenance ·
no parallel forecasts · day-closure quality.

Canon: docs/audits/DAY_SCENARIO_EVAL_PACK_C35.md
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
    run_editorial_quality_gate_c31,
    score_editorial_quality_c31,
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
    _public_blobs,
    run_personalization_gate_c33,
)

EVAL_CONTRACT = "day_scenario_eval_pack_c35"
EVAL_VERSION = "c35.0"

PROFILE_IDS = (
    "smooth_conflict",  # natal A — tends to smooth
    "demand_clarity",  # natal B — presses for clarity
    "analyze_first",  # natal C — analysis before action
    "no_birth_time",  # honest general / light at most
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

# Pass bar for aggregate pack (fixture CI). Live Nebius packs may tune separately.
PACK_PASS_THRESHOLD = 0.75
DAY_DIFF_MIN_DIMENSIONS = 2
REPEAT_JACCARD_SOFT_MAX = 0.55  # same-profile consecutive days

_EN_CONCRETE_RE = re.compile(
    r"("
    r"message|chat|email|call|colleague|partner|deadline|draft|"
    r"kitchen|door|phone|meeting|invoice|reply|ask|when\s+you|"
    r"\"[^\"]{4,}\"|"
    r"moment\s+when|exactly\s+when"
    r")",
    re.I,
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


def _closure_blob(native: dict[str, Any]) -> str:
    props = _as_dict(native.get("props") or native.get("prop_material"))
    bits: list[str] = []
    aff = _as_dict(props.get("affirmation_tension") or props.get("affirmation"))
    if aff:
        bits.append(str(aff.get("text") or ""))
    for a in _as_list(props.get("affirmations")):
        if isinstance(a, dict):
            bits.append(str(a.get("text") or a.get("line") or ""))
        else:
            bits.append(str(a))
    return " ".join(bits)


def score_conflict_recognizability(native: dict[str, Any]) -> dict[str, Any]:
    c = _as_dict(native.get("conflict"))
    title = _clip(c.get("title"), 120)
    force_a = _clip(c.get("force_a"), 120)
    force_b = _clip(c.get("force_b"), 120)
    thesis = _clip(c.get("thesis"), 200)
    checks = {
        "has_title": bool(title),
        "has_opposing_forces": bool(force_a) and bool(force_b) and force_a != force_b,
        "thesis_not_empty": len(thesis) >= 24,
        "forces_not_echo_title": force_a.lower() not in title.lower()
        or force_b.lower() not in title.lower()
        or len(force_a) > 8,
    }
    score = sum(1 for v in checks.values() if v) / max(1, len(checks))
    return {"score": round(score, 3), "checks": checks}


def score_scene_concreteness(
    native: dict[str, Any],
    *,
    locale: str = "ru",
) -> dict[str, Any]:
    """RU uses production editorial gate; EN uses eval-side concrete heuristic."""
    loc = (locale or "ru").strip().lower()
    if loc == "ru":
        defects = run_editorial_quality_gate_c31(native)
        scene_codes = {
            c
            for c in (str(d.get("code") or "") for d in defects)
            if c.startswith("SCENE_") or c == "THESIS_ECHO"
        }
        ed = score_editorial_quality_c31(
            [d for d in defects if str(d.get("code") or "").startswith("SCENE_") or str(d.get("code")) == "THESIS_ECHO"]
        )
        return {
            "score": ed["editorial_score"],
            "mode": "editorial_gate_c31",
            "defect_codes": sorted(scene_codes),
            "checks": {"editorial_clean": not scene_codes.intersection(CRITICAL_DEFECTS)},
        }

    # EN eval-only (production gate remains RU-primary until language expansion)
    scenes = [s for s in _as_list(native.get("scenes")) if isinstance(s, dict)]
    if not scenes:
        return {"score": 0.0, "mode": "en_heuristic", "checks": {"has_scenes": False}}
    ok = 0
    for s in scenes:
        blob = " ".join(
            str(s.get(k) or "")
            for k in ("setup", "everyday_example", "opportunity", "trap", "recommended_action")
        )
        concrete = bool(_EN_CONCRETE_RE.search(blob)) and len(blob) >= 80
        has_choice = bool(str(s.get("opportunity") or "").strip()) and bool(str(s.get("trap") or "").strip())
        has_action = bool(str(s.get("recommended_action") or "").strip())
        if concrete and has_choice and has_action:
            ok += 1
    score = ok / max(1, len(scenes))
    return {
        "score": round(score, 3),
        "mode": "en_heuristic",
        "checks": {"concrete_scenes": ok, "scene_count": len(scenes)},
    }


def score_chorus_coherence(native: dict[str, Any]) -> dict[str, Any]:
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
        "checks": {
            "no_parallel_forecast": not parallel,
            "chorus_critical_clean": not any(
                str(d.get("code")) in CRITICAL_DEFECTS for d in chorus
            ),
        },
        "defect_codes": sorted({str(d.get("code")) for d in chorus}),
    }


def score_recommendation_provenance(native: dict[str, Any]) -> dict[str, Any]:
    scenes = [s for s in _as_list(native.get("scenes")) if isinstance(s, dict)]
    with_refs = 0
    with_action = 0
    for s in scenes:
        action = str(s.get("recommended_action") or "").strip()
        if action:
            with_action += 1
        refs = _as_list(s.get("evidence_refs")) + _as_list(s.get("chorus_refs"))
        pers = _as_list(_as_dict(s.get("personalization")).get("personalization_evidence_refs"))
        if action and (refs or pers or s.get("origin_scene_id") or s.get("scene_id")):
            with_refs += 1
    props = _as_dict(native.get("props") or native.get("prop_material"))
    color_ok = bool(_as_list(props.get("color_scene_candidates"))) or bool(
        _as_dict(props.get("color")).get("origin_scene_id")
    )
    aff = _as_dict(props.get("affirmation_tension") or props.get("affirmation"))
    aff_ok = bool(aff.get("scene_id") or aff.get("origin_scene_id") or aff.get("text"))
    checks = {
        "actions_have_scene_anchor": with_action == 0 or with_refs >= max(1, with_action // 1),
        "color_or_affirmation_tied": color_ok or aff_ok,
    }
    score = sum(1 for v in checks.values() if v) / max(1, len(checks))
    if scenes and with_action:
        score = round(0.5 * score + 0.5 * (with_refs / max(1, with_action)), 3)
    return {"score": round(score, 3), "checks": checks, "anchored_actions": with_refs}


def score_day_closure_quality(native: dict[str, Any]) -> dict[str, Any]:
    blob = _closure_blob(native)
    scenes = _as_list(native.get("scenes"))
    has_aff = len(blob.strip()) >= 12
    # Closure should not be empty wellness mush only
    mush = bool(
        re.search(
            r"(доверьтесь\s+вселенной|everything\s+happens\s+for\s+a\s+reason|вы\s+достаточны)",
            blob,
            re.I,
        )
    )
    checks = {
        "has_closure_text": has_aff or bool(scenes),
        "not_mush_only": not mush,
        "prop_material_present": bool(_as_dict(native.get("prop_material") or native.get("props"))),
    }
    score = sum(1 for v in checks.values() if v) / max(1, len(checks))
    return {"score": round(score, 3), "checks": checks}


def score_cell(
    *,
    native: dict[str, Any],
    pack: dict[str, Any] | None = None,
    locale: str = "ru",
    profile_id: str = "",
) -> dict[str, Any]:
    """Score one (day × profile × locale) cell."""
    n = normalize_native_scenario_llm_c1(deepcopy(native)) if native else {}
    pack = pack or {"evidence_depth": DEPTH_GENERAL, "evidence_refs": []}
    conflict = score_conflict_recognizability(n)
    scenes = score_scene_concreteness(n, locale=locale)
    chorus = score_chorus_coherence(n)
    provenance = score_recommendation_provenance(n)
    closure = score_day_closure_quality(n)
    pers_defects = run_personalization_gate_c33(n, pack) if pack else []
    depth = str(pack.get("evidence_depth") or DEPTH_GENERAL)
    declared = str(n.get("personalization_depth") or "")
    honesty = {
        "no_birth_time_stays_honest": profile_id != "no_birth_time"
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
    }
    # Parallel-forecast axis mirrors chorus
    axes["no_parallel_forecasts"] = 1.0 if chorus["checks"]["no_parallel_forecast"] else 0.0

    cell_score = sum(axes.values()) / max(1, len(axes))
    return {
        "profile_id": profile_id,
        "locale": locale,
        "axes": axes,
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
    """Same date: deep profiles must differ structurally; control stays general."""
    profiles = [p for p in PROFILE_IDS if p in natives_by_profile]
    deep = [p for p in profiles if p != "no_birth_time"]
    diffs: list[dict[str, Any]] = []
    for i, a in enumerate(deep):
        for b in deep[i + 1 :]:
            dims = structural_diff_dimensions(natives_by_profile[a], natives_by_profile[b])
            diffs.append({"a": a, "b": b, "dimensions": dims, "ok": len(dims) >= DAY_DIFF_MIN_DIMENSIONS})
    control = natives_by_profile.get("no_birth_time")
    control_ok = True
    if control is not None:
        depth = str(control.get("personalization_depth") or DEPTH_GENERAL)
        control_ok = depth in {DEPTH_GENERAL, DEPTH_LIGHT, ""}
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
    # Lower Jaccard = better diversity → higher score
    score = max(0.0, min(1.0, 1.0 - mean_j))
    if max_j > REPEAT_JACCARD_SOFT_MAX:
        score = min(score, 0.55)
    return {
        "score": round(score, 3),
        "mean_jaccard": round(mean_j, 3),
        "max_jaccard": round(max_j, 3),
        "checks": {"no_day_clone": max_j <= REPEAT_JACCARD_SOFT_MAX},
    }


def run_eval_pack_c35(
    cells: Iterable[dict[str, Any]],
    *,
    pass_threshold: float = PACK_PASS_THRESHOLD,
) -> dict[str, Any]:
    """Run full pack.

    Each cell: {date, profile_id, locale, native, pack?}
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
        rows.append({"date": d, "profile_id": pid, "locale": loc, **scored})

    dates = sorted({r["date"] for r in rows})
    locales = sorted({r["locale"] for r in rows})
    profiles = sorted({r["profile_id"] for r in rows})

    # Per-day differentiation (ru primary; en mirrored if present)
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

    # Per-profile repeatability across days
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

    shape_ok = (
        len(dates) >= 14
        and len(profiles) >= 4
        and "no_birth_time" in profiles
        and set(locales) >= {"ru", "en"}
    )

    return {
        "contract_version": EVAL_CONTRACT,
        "eval_version": EVAL_VERSION,
        "shape": {
            "days": len(dates),
            "profiles": profiles,
            "locales": locales,
            "cells": len(rows),
            "shape_ok": shape_ok,
        },
        "aggregate_axes": aggregate_axes,
        "mean_cell_score": round(mean_cell, 3),
        "pack_score": round(pack_score, 3),
        "pass": bool(shape_ok and pack_score >= pass_threshold),
        "pass_threshold": pass_threshold,
        "cells": rows,
        "day_differentiation": day_diff_reports,
        "repeatability": repeat_reports,
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
]


def _profile_pack(profile_id: str) -> dict[str, Any]:
    if profile_id == "no_birth_time":
        return {
            "evidence_depth": DEPTH_GENERAL,
            "evidence_refs": [],
            "behavioral_tendencies": [],
            "sensitive_domains": [],
            "confidence": 0.2,
        }
    if profile_id == "smooth_conflict":
        return {
            "evidence_depth": DEPTH_DEEP,
            "evidence_refs": ["claim.personal.moon7.smooth", "claim.personal.venus.reject"],
            "behavioral_tendencies": [
                {"id": "smooth_conflict", "label": "smooth", "confidence": 0.8, "source_refs": ["claim.personal.moon7.smooth"]}
            ],
            "sensitive_domains": [{"sphere": "relationships", "reason": "rejection sensitivity"}],
            "confidence": 0.75,
        }
    if profile_id == "demand_clarity":
        return {
            "evidence_depth": DEPTH_DEEP,
            "evidence_refs": ["claim.personal.mars1.direct", "claim.personal.sat.overload"],
            "behavioral_tendencies": [
                {"id": "over_control", "label": "control", "confidence": 0.8, "source_refs": ["claim.personal.mars1.direct"]}
            ],
            "sensitive_domains": [{"sphere": "work_decisions", "reason": "overload"}],
            "confidence": 0.78,
        }
    # analyze_first
    return {
        "evidence_depth": DEPTH_DEEP,
        "evidence_refs": ["claim.personal.merc.analyze", "claim.personal.sat.delay"],
        "behavioral_tendencies": [
            {"id": "analyze_first", "label": "analyze", "confidence": 0.77, "source_refs": ["claim.personal.merc.analyze"]}
        ],
        "sensitive_domains": [{"sphere": "communication", "reason": "overthink"}],
        "confidence": 0.7,
    }


def _apply_profile(native: dict[str, Any], profile_id: str, *, day_i: int) -> dict[str, Any]:
    out = deepcopy(native)
    if profile_id == "no_birth_time":
        out["personalization_depth"] = DEPTH_GENERAL
        out["interpretive_chorus"]["natal"] = []
        out["conflict"]["why_personal"] = ""
        return out

    out["personalization_depth"] = DEPTH_DEEP
    if profile_id == "smooth_conflict":
        out["conflict"]["force_a"] = "сгладить ради тишины" if day_i % 2 == 0 else "уйти в мягкость"
        out["conflict"]["force_b"] = "сказать коротко и честно"
        out["conflict"]["personalization"] = {
            "personalization_level": DEPTH_DEEP,
            "personalization_reason": "stop smoothing",
            "personalization_evidence_refs": ["claim.personal.moon7.smooth"],
            "habitual_force": "a",
            "required_movement": "b",
            "general_fallback_available": True,
        }
        out["scenes"][0]["sphere"] = "relationships"
        out["scenes"][0]["scene_id"] = "scene.relationships"
        out["scenes"][0]["recommended_action"] = (
            f"Сказать одну конкретную фразу вместо молчания (день {day_i + 1})."
        )
        out["scenes"][0]["personalization"] = {
            "personalization_level": DEPTH_DEEP,
            "personalization_reason": "relationships",
            "personalization_evidence_refs": ["claim.personal.venus.reject"],
            "sphere_reason": "sensitive relationships",
            "response_pattern": "smooth_conflict",
            "trap_pattern": "agree_for_silence",
            "general_fallback_available": True,
        }
    elif profile_id == "demand_clarity":
        out["conflict"]["force_a"] = "давить ясностью"
        out["conflict"]["force_b"] = "один вопрос до ответа"
        out["conflict"]["personalization"] = {
            "personalization_level": DEPTH_DEEP,
            "personalization_reason": "do not pressure",
            "personalization_evidence_refs": ["claim.personal.mars1.direct"],
            "habitual_force": "a",
            "required_movement": "b",
            "general_fallback_available": True,
        }
        out["scenes"][0]["sphere"] = "work_decisions"
        out["scenes"][0]["scene_id"] = "scene.work_decisions"
        out["scenes"][0]["trap"] = "Превратить ясность в давление."
        out["scenes"][0]["recommended_action"] = (
            f"Задать один вопрос до ответа; не решать за коллегу (день {day_i + 1})."
        )
        out["scenes"][0]["personalization"] = {
            "personalization_level": DEPTH_DEEP,
            "personalization_reason": "work",
            "personalization_evidence_refs": ["claim.personal.sat.overload"],
            "sphere_reason": "responsibility overload",
            "response_pattern": "over_control",
            "trap_pattern": "pressure_clarity",
            "general_fallback_available": True,
        }
    else:  # analyze_first
        out["conflict"]["force_a"] = "ещё один анализ"
        out["conflict"]["force_b"] = "маленький видимый шаг"
        out["conflict"]["personalization"] = {
            "personalization_level": DEPTH_DEEP,
            "personalization_reason": "stop endless analysis",
            "personalization_evidence_refs": ["claim.personal.merc.analyze"],
            "habitual_force": "a",
            "required_movement": "b",
            "general_fallback_available": True,
        }
        out["scenes"][0]["sphere"] = "communication"
        out["scenes"][0]["scene_id"] = "scene.communication"
        out["scenes"][0]["recommended_action"] = (
            f"Отправить черновик из трёх предложений без второго прохода (день {day_i + 1})."
        )
        out["scenes"][0]["personalization"] = {
            "personalization_level": DEPTH_DEEP,
            "personalization_reason": "communication",
            "personalization_evidence_refs": ["claim.personal.sat.delay"],
            "sphere_reason": "overthink before speak",
            "response_pattern": "analyze_first",
            "trap_pattern": "delay_send",
            "general_fallback_available": True,
        }
    return out


def _apply_profile_en(native: dict[str, Any], profile_id: str, *, day_i: int) -> dict[str, Any]:
    out = deepcopy(native)
    if profile_id == "no_birth_time":
        out["personalization_depth"] = DEPTH_GENERAL
        out["interpretive_chorus"]["natal"] = []
        out["conflict"]["why_personal"] = ""
        return out
    out["personalization_depth"] = DEPTH_DEEP
    if profile_id == "smooth_conflict":
        out["conflict"]["force_a"] = "smooth for quiet"
        out["conflict"]["force_b"] = "say it short and honest"
        out["conflict"]["personalization"] = {
            "personalization_level": DEPTH_DEEP,
            "personalization_reason": "stop smoothing",
            "personalization_evidence_refs": ["claim.personal.moon7.smooth"],
            "habitual_force": "a",
            "required_movement": "b",
            "general_fallback_available": True,
        }
        out["scenes"][0]["sphere"] = "relationships"
        out["scenes"][0]["recommended_action"] = f"Send one concrete sentence instead of silence (day {day_i + 1})."
        out["scenes"][0]["personalization"] = {
            "personalization_level": DEPTH_DEEP,
            "personalization_reason": "relationships",
            "personalization_evidence_refs": ["claim.personal.venus.reject"],
            "sphere_reason": "sensitive relationships",
            "response_pattern": "smooth_conflict",
            "general_fallback_available": True,
        }
    elif profile_id == "demand_clarity":
        out["conflict"]["force_a"] = "push for clarity"
        out["conflict"]["force_b"] = "one question before answering"
        out["conflict"]["personalization"] = {
            "personalization_level": DEPTH_DEEP,
            "personalization_reason": "do not pressure",
            "personalization_evidence_refs": ["claim.personal.mars1.direct"],
            "habitual_force": "a",
            "required_movement": "b",
            "general_fallback_available": True,
        }
        out["scenes"][0]["sphere"] = "work_decisions"
        out["scenes"][0]["recommended_action"] = f"Ask one question before answering; do not decide for them (day {day_i + 1})."
        out["scenes"][0]["personalization"] = {
            "personalization_level": DEPTH_DEEP,
            "personalization_reason": "work",
            "personalization_evidence_refs": ["claim.personal.sat.overload"],
            "sphere_reason": "overload",
            "response_pattern": "over_control",
            "general_fallback_available": True,
        }
    else:
        out["conflict"]["force_a"] = "one more analysis pass"
        out["conflict"]["force_b"] = "a small visible step"
        out["conflict"]["personalization"] = {
            "personalization_level": DEPTH_DEEP,
            "personalization_reason": "stop endless analysis",
            "personalization_evidence_refs": ["claim.personal.merc.analyze"],
            "habitual_force": "a",
            "required_movement": "b",
            "general_fallback_available": True,
        }
        out["scenes"][0]["sphere"] = "communication"
        out["scenes"][0]["recommended_action"] = f"Send a three-sentence draft without a second pass (day {day_i + 1})."
        out["scenes"][0]["personalization"] = {
            "personalization_level": DEPTH_DEEP,
            "personalization_reason": "communication",
            "personalization_evidence_refs": ["claim.personal.sat.delay"],
            "sphere_reason": "overthink",
            "response_pattern": "analyze_first",
            "general_fallback_available": True,
        }
    return out


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
                    "conflict_id": re.sub(r"\s+", "-", variant["title"].lower())[:48],
                }
            ],
            "day_card": {
                "named_factor": f"Карта дня — {variant['card']}",
                "archetype_role": "Архетип реакции на конфликт дня.",
                "link_to_conflict": "Карта называет, как проходить тот же выбор.",
                "evidence_refs": ["day_card"],
                "conflict_id": re.sub(r"\s+", "-", variant["title"].lower())[:48],
            },
            "day_number": {
                "named_factor": f"Число дня — {variant['number']}",
                "tempo": "сначала понять" if day_i % 2 == 0 else "короткий шаг",
                "style": "без спешки",
                "link_to_conflict": "Число задаёт темп прохождения конфликта.",
                "evidence_refs": ["day_number"],
                "conflict_id": re.sub(r"\s+", "-", variant["title"].lower())[:48],
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
        },
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
                    "conflict_id": re.sub(r"\s+", "-", variant["title"].lower())[:48],
                }
            ],
            "day_card": {
                "named_factor": f"Day card — {variant['card']}",
                "archetype_role": "Archetype of how to meet the day's conflict.",
                "link_to_conflict": "The card names the reaction style for the same choice.",
                "evidence_refs": ["day_card"],
                "conflict_id": re.sub(r"\s+", "-", variant["title"].lower())[:48],
            },
            "day_number": {
                "named_factor": f"Day number — {variant['number']}",
                "tempo": "understand first" if day_i % 2 == 0 else "one short step",
                "style": "without rush",
                "link_to_conflict": "The number sets the tempo through the conflict.",
                "evidence_refs": ["day_number"],
                "conflict_id": re.sub(r"\s+", "-", variant["title"].lower())[:48],
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
        },
    }


def build_synthetic_eval_matrix_c35(
    *,
    start: date | None = None,
    days: int = 14,
) -> list[dict[str, Any]]:
    """Build CI fixture matrix: days × PROFILE_IDS × LOCALES."""
    start = start or date(2026, 7, 12)
    cells: list[dict[str, Any]] = []
    for i in range(days):
        d = start + timedelta(days=i)
        date_s = d.isoformat()
        v_ru = _DAY_VARIANTS_RU[i % len(_DAY_VARIANTS_RU)]
        # rotate wording slightly per day so consecutive days are not clones
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
        for pid in PROFILE_IDS:
            pack = _profile_pack(pid)
            native_ru = _apply_profile(_base_native_ru(v_ru, day_i=i), pid, day_i=i)
            native_en = _apply_profile_en(_base_native_en(v_en, day_i=i), pid, day_i=i)
            cells.append(
                {
                    "date": date_s,
                    "profile_id": pid,
                    "locale": "ru",
                    "native": native_ru,
                    "pack": pack,
                    "shared_day": {
                        "date": date_s,
                        "card": v_ru["card"],
                        "number": v_ru["number"],
                        "thesis_family": "communication",
                    },
                }
            )
            cells.append(
                {
                    "date": date_s,
                    "profile_id": pid,
                    "locale": "en",
                    "native": native_en,
                    "pack": pack,
                    "shared_day": {
                        "date": date_s,
                        "card": v_en["card"],
                        "number": v_en["number"],
                        "thesis_family": "communication",
                    },
                }
            )
    return cells

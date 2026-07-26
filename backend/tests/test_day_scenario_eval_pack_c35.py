"""C3.5 — multi-day × multi-profile × multi-locale eval pack."""

from __future__ import annotations

from copy import deepcopy

from todayflow_backend.services.day_scenario_eval_pack_c35 import (
    LOCALES,
    PROFILE_IDS_C35_LEGACY,
    build_synthetic_eval_matrix_c35,
    run_eval_pack_c35,
    score_formulation_repeatability,
    score_user_differentiation,
    token_jaccard,
)
from todayflow_backend.services.day_scenario_native_llm_c1 import normalize_native_scenario_llm_c1


def test_token_jaccard_identical_and_distinct():
    assert token_jaccard("alpha beta gamma", "alpha beta gamma") == 1.0
    assert token_jaccard("alpha beta", "delta epsilon") == 0.0


def test_synthetic_matrix_shape():
    matrix = build_synthetic_eval_matrix_c35(days=14)
    assert len(matrix) == 14 * len(PROFILE_IDS_C35_LEGACY) * len(LOCALES)
    dates = {c["date"] for c in matrix}
    assert len(dates) == 14
    assert set(c["profile_id"] for c in matrix) == set(PROFILE_IDS_C35_LEGACY)
    assert set(c["locale"] for c in matrix) == set(LOCALES)
    assert "no_birth_time" in PROFILE_IDS_C35_LEGACY


def test_eval_pack_passes_on_synthetic_fixtures():
    matrix = build_synthetic_eval_matrix_c35(days=14)
    report = run_eval_pack_c35(matrix)
    assert report["shape"]["shape_ok"] is True
    assert report["shape"]["days"] == 14
    assert report["shape"]["cells"] == 14 * 4 * 2
    assert report["aggregate_axes"]["user_differentiation"] >= 0.66
    assert report["aggregate_axes"]["formulation_repeatability"] >= 0.4
    assert report["pass"] is True, {
        "pack_score": report["pack_score"],
        "axes": report["aggregate_axes"],
        "sample_cell": report["cells"][0],
    }


def test_no_birth_time_cells_are_general():
    matrix = build_synthetic_eval_matrix_c35(days=2)
    for c in matrix:
        if c["profile_id"] != "no_birth_time":
            continue
        native = normalize_native_scenario_llm_c1(c["native"])
        assert native.get("personalization_depth") in {"general", "", None} or str(
            native.get("personalization_depth")
        ) == "general"
        assert c["pack"]["evidence_depth"] == "general"


def test_clone_days_fail_repeatability():
    matrix = build_synthetic_eval_matrix_c35(days=3)
    # Force same native for one profile across days
    base = None
    for c in matrix:
        if c["profile_id"] == "smooth_conflict" and c["locale"] == "ru":
            if base is None:
                base = deepcopy(c["native"])
            else:
                c["native"] = deepcopy(base)
    seq = [
        normalize_native_scenario_llm_c1(c["native"])
        for c in matrix
        if c["profile_id"] == "smooth_conflict" and c["locale"] == "ru"
    ]
    rep = score_formulation_repeatability(seq)
    assert rep["checks"]["no_day_clone"] is False
    assert rep["max_jaccard"] > 0.55


def test_identical_profiles_fail_differentiation():
    matrix = build_synthetic_eval_matrix_c35(days=1)
    day = matrix[0]["date"]
    natives = {}
    for c in matrix:
        if c["date"] == day and c["locale"] == "ru":
            natives[c["profile_id"]] = normalize_native_scenario_llm_c1(c["native"])
    # Collapse deep profiles to the same scenario
    shared = deepcopy(natives["smooth_conflict"])
    natives["demand_clarity"] = deepcopy(shared)
    natives["analyze_first"] = deepcopy(shared)
    report = score_user_differentiation([], natives)
    assert report["checks"]["enough_pairs_differ"] is False

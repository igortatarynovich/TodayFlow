"""C3.5.1 — eval hardening: fixtures, dual scores, expanded matrix, report (no Nebius)."""

from __future__ import annotations

from copy import deepcopy

from todayflow_backend.services.day_scenario_editorial_gate_c31 import (
    DEFECT_CHORUS_PARALLEL_FORECAST,
    DEFECT_SCENE_ABSTRACT,
    DEFECT_SCENE_CLONE,
    DEFECT_SCENE_UNIVERSAL_ADVICE,
    run_editorial_quality_gate_c31,
)
from todayflow_backend.services.day_scenario_eval_editorial_en_c351 import (
    DEFECT_LOCALE_LANGUAGE_MISMATCH,
    run_editorial_quality_gate_en_c351,
    score_editorial_en_c351,
)
from todayflow_backend.services.day_scenario_eval_fixtures_c351 import (
    NEGATIVE_FIXTURES,
    apply_mutation,
    good_native_en,
    good_native_ru,
)
from todayflow_backend.services.day_scenario_eval_pack_c35 import (
    EVAL_VERSION,
    LOCALES,
    PROFILE_IDS,
    PROFILE_IDS_C35_LEGACY,
    build_synthetic_eval_matrix_c35,
    build_synthetic_eval_matrix_c351,
    run_eval_pack_c35,
    score_cell,
    score_chorus_coherence,
    score_conflict_recognizability,
    score_day_closure_quality,
    score_recommendation_provenance,
    score_scene_concreteness,
)
from todayflow_backend.services.day_scenario_eval_provenance_c351 import (
    DEFECT_CLOSURE_MISSING,
    DEFECT_CLOSURE_WELLNESS_MUSH,
    DEFECT_PROVENANCE_REF_MISSING,
    DEFECT_PROVENANCE_REF_ORPHAN,
    run_provenance_gate_c351,
    score_day_closure_c351,
    score_provenance_c351,
)
from todayflow_backend.services.day_scenario_eval_report_c351 import (
    build_baseline_report,
    render_baseline_markdown,
)
from todayflow_backend.services.day_scenario_personalization_c33 import DEPTH_DEEP, DEPTH_GENERAL


def _pack_deep() -> dict:
    return {
        "evidence_depth": DEPTH_DEEP,
        "evidence_refs": ["claim.personal.moon7.smooth", "claim.personal.venus.reject"],
        "behavioral_tendencies": [],
        "sensitive_domains": [],
        "confidence": 0.75,
    }


def _pack_general() -> dict:
    return {
        "evidence_depth": DEPTH_GENERAL,
        "evidence_refs": [],
        "behavioral_tendencies": [],
        "sensitive_domains": [],
        "confidence": 0.2,
    }


# ---------------------------------------------------------------------------
# Negative fixtures → expected axis / defect
# ---------------------------------------------------------------------------


def test_negative_conflict_no_opposition():
    n = NEGATIVE_FIXTURES["conflict_no_opposition"]
    scored = score_conflict_recognizability(n)
    assert scored["score"] < 0.75
    assert "CONFLICT_NO_OPPOSITION" in scored["defect_codes"]
    assert scored["checks"]["has_opposing_forces"] is False


def test_negative_abstract_scenes():
    n = NEGATIVE_FIXTURES["abstract_scenes"]
    scored = score_scene_concreteness(n, locale="ru")
    assert scored["score"] < 0.85
    assert any(c.startswith("SCENE_") for c in scored["defect_codes"])


def test_negative_clone_scenes():
    n = NEGATIVE_FIXTURES["clone_scenes"]
    scored = score_scene_concreteness(n, locale="ru")
    assert DEFECT_SCENE_CLONE in scored["defect_codes"]


def test_negative_parallel_chorus():
    n = NEGATIVE_FIXTURES["parallel_chorus"]
    scored = score_chorus_coherence(n, locale="ru")
    assert scored["checks"]["no_parallel_forecast"] is False
    assert DEFECT_CHORUS_PARALLEL_FORECAST in scored["defect_codes"]


def test_negative_decorative_personalization():
    n = NEGATIVE_FIXTURES["decorative_personalization"]
    scored = score_provenance_c351(n, _pack_general())
    assert scored["score"] < score_provenance_c351(good_native_ru(), _pack_deep())["score"]
    codes = set(scored["defect_codes"])
    assert codes & {
        "PROVENANCE_WRONG_PROFILE",
        DEFECT_PROVENANCE_REF_ORPHAN,
        DEFECT_PROVENANCE_REF_MISSING,
    } or scored["editorial_score"] < 0.85


def test_negative_recommendation_without_evidence():
    n = NEGATIVE_FIXTURES["recommendation_without_evidence"]
    scored = score_recommendation_provenance(n, _pack_deep())
    assert DEFECT_PROVENANCE_REF_MISSING in scored["defect_codes"]
    assert scored["score"] < 0.9


def test_negative_missing_day_closure():
    n = NEGATIVE_FIXTURES["missing_day_closure"]
    scored = score_day_closure_quality(n)
    assert DEFECT_CLOSURE_MISSING in scored["defect_codes"]
    assert scored["score"] < 0.5
    assert scored["checks"]["not_relying_on_scenes_alone"] is False


def test_negative_wellness_closure():
    n = NEGATIVE_FIXTURES["wellness_closure"]
    scored = score_day_closure_quality(n)
    assert DEFECT_CLOSURE_WELLNESS_MUSH in scored["defect_codes"]


def test_negative_locale_mismatch_en_cyrillic():
    n = NEGATIVE_FIXTURES["locale_mismatch_en_cyrillic"]
    scored = score_editorial_en_c351(n, locale="en")
    assert DEFECT_LOCALE_LANGUAGE_MISMATCH in scored["defect_codes"]


def test_negative_locale_mismatch_ru_latin():
    n = NEGATIVE_FIXTURES["locale_mismatch_ru_latin"]
    scored = score_editorial_en_c351(n, locale="ru")
    assert DEFECT_LOCALE_LANGUAGE_MISMATCH in scored["defect_codes"]


def test_negative_no_birth_time_deep_natal():
    n = NEGATIVE_FIXTURES["no_birth_time_deep_natal"]
    cell = score_cell(
        native=n,
        pack=_pack_general(),
        locale="ru",
        profile_id="no_birth_time",
    )
    # Control pack + deep natal prose should hurt honesty and/or personalization gate
    assert (
        cell["axes"]["personalization_honesty"] < 1.0
        or cell["details"]["pers_defect_codes"]
        or cell["score"] < score_cell(native=good_native_ru(), pack=_pack_deep(), locale="ru", profile_id="smooth_conflict")["score"]
    )


# ---------------------------------------------------------------------------
# Mutations worsen expected metric vs good baseline
# ---------------------------------------------------------------------------


def test_mutations_worsen_expected_metric():
    good_ru = good_native_ru()
    good_en = good_native_en()
    base_conflict = score_conflict_recognizability(good_ru)["score"]
    base_scene_ru = score_scene_concreteness(good_ru, locale="ru")["score"]
    base_scene_en = score_scene_concreteness(good_en, locale="en")["score"]
    base_chorus = score_chorus_coherence(good_ru, locale="ru")["score"]
    base_prov = score_recommendation_provenance(good_ru, _pack_deep())["score"]
    base_closure = score_day_closure_quality(good_ru)["score"]

    assert score_conflict_recognizability(apply_mutation(good_ru, "drop_force_b"))["score"] < base_conflict
    assert (
        score_scene_concreteness(apply_mutation(good_en, "universal_advice_example"), locale="en")["score"]
        < base_scene_en
    )
    assert score_chorus_coherence(apply_mutation(good_ru, "drop_link_to_conflict"), locale="ru")["score"] < base_chorus
    assert score_scene_concreteness(apply_mutation(good_ru, "clone_scene_into_second"), locale="ru")["score"] < base_scene_ru
    soft = apply_mutation(good_ru, "soft_generic_action")
    soft_score = score_scene_concreteness(soft, locale="ru")["score"]
    # soft generic may be soft severity; still should not improve
    assert soft_score <= base_scene_ru
    assert score_recommendation_provenance(apply_mutation(good_ru, "drop_evidence_refs"), _pack_deep())["score"] < base_prov
    assert score_day_closure_quality(apply_mutation(good_ru, "drop_day_closure"))["score"] < base_closure
    assert score_day_closure_quality(apply_mutation(good_ru, "mush_closure"))["score"] < base_closure


# ---------------------------------------------------------------------------
# Closure / provenance contracts
# ---------------------------------------------------------------------------


def test_closure_cannot_pass_on_scenes_alone():
    n = good_native_ru()
    n.pop("day_closure", None)
    assert n.get("scenes")
    scored = score_day_closure_c351(n)
    assert scored["score"] < 0.5
    assert DEFECT_CLOSURE_MISSING in scored["defect_codes"]
    assert scored["contract_score"] <= 0.2


def test_provenance_orphan_and_missing_refs_fail():
    n = good_native_ru()
    n["scenes"][0]["evidence_refs"] = ["claim.personal.unknown.orphan"]
    n["scenes"][0]["personalization"] = {
        "personalization_level": "deep_personalized",
        "personalization_evidence_refs": ["claim.personal.unknown.orphan"],
    }
    pack = _pack_deep()  # allowed refs do not include orphan
    defects = run_provenance_gate_c351(n, pack)
    codes = {d["code"] for d in defects}
    assert DEFECT_PROVENANCE_REF_ORPHAN in codes

    n2 = good_native_ru()
    for s in n2["scenes"]:
        s.pop("evidence_refs", None)
        s.pop("personalization", None)
    defects2 = run_provenance_gate_c351(n2, pack)
    assert DEFECT_PROVENANCE_REF_MISSING in {d["code"] for d in defects2}


# ---------------------------------------------------------------------------
# EN + RU gates catch universal / abstract
# ---------------------------------------------------------------------------


def test_en_and_ru_gates_catch_universal_and_abstract():
    ru = apply_mutation(good_native_ru(), "universal_advice_example")
    # Force RU-shaped universal advice for RU gate
    ru["scenes"][0]["recommended_action"] = "Не торопитесь и сохраняйте баланс."
    ru["scenes"][0]["opportunity"] = "Слушайте себя."
    ru["scenes"][0]["everyday_example"] = "Будьте осторожны сегодня."
    ru["scenes"][0]["setup"] = "В отношениях возможна напряжённость."
    ru_codes = {d["code"] for d in run_editorial_quality_gate_c31(ru)}
    assert ru_codes & {DEFECT_SCENE_UNIVERSAL_ADVICE, DEFECT_SCENE_ABSTRACT}

    en = apply_mutation(good_native_en(), "universal_advice_example")
    en_codes = {d["code"] for d in run_editorial_quality_gate_en_c351(en)}
    assert en_codes & {DEFECT_SCENE_UNIVERSAL_ADVICE, DEFECT_SCENE_ABSTRACT}


# ---------------------------------------------------------------------------
# Expanded matrix + dual scores + report
# ---------------------------------------------------------------------------


def test_c351_matrix_shape():
    matrix = build_synthetic_eval_matrix_c351(days=28)
    assert len(matrix) >= 400
    assert len(matrix) == 28 * len(PROFILE_IDS) * len(LOCALES)
    dates = {c["date"] for c in matrix}
    assert len(dates) == 28
    assert len(set(c["profile_id"] for c in matrix)) >= 8
    assert set(c["locale"] for c in matrix) >= {"ru", "en"}
    # day_closure present on synthetic good natives
    assert all(_as_has_closure(c["native"]) for c in matrix[:4])


def _as_has_closure(native: dict) -> bool:
    dc = native.get("day_closure") or {}
    return bool(dc.get("resolution") and dc.get("conflict_callback"))


def test_dual_scores_present_on_cell():
    cell = score_cell(
        native=good_native_ru(),
        pack=_pack_deep(),
        locale="ru",
        profile_id="smooth_conflict",
    )
    assert "contract_score" in cell
    assert "editorial_score" in cell
    assert "axes" in cell
    assert "defect_codes" in cell
    for key in ("conflict", "provenance", "closure"):
        detail = cell["details"][key]
        assert "score" in detail
        assert "contract_score" in detail
        assert "editorial_score" in detail
    assert "score" in cell["details"]["scenes"]
    assert "score" in cell["details"]["chorus"]


def test_report_builder_worst_cells_and_defect_counts():
    matrix = build_synthetic_eval_matrix_c351(days=2)  # small slice for speed
    # Inject one bad cell for defect frequency
    bad = deepcopy(matrix[0])
    bad["native"] = NEGATIVE_FIXTURES["missing_day_closure"]
    matrix.append(bad)
    eval_report = run_eval_pack_c35(matrix)
    assert eval_report["eval_version"] == EVAL_VERSION
    assert "worst_cells" in eval_report
    assert "defect_histogram" in eval_report
    assert "thresholds_provisional" in eval_report

    report = build_baseline_report(eval_report)
    assert report["worst_cells"]
    assert isinstance(report["defect_counts"], dict)
    md = render_baseline_markdown(report)
    assert "Worst 20 cells" in md
    assert "PROVISIONAL" in md


def test_legacy_c35_wrapper_still_112():
    matrix = build_synthetic_eval_matrix_c35(days=14)
    assert len(matrix) == 14 * len(PROFILE_IDS_C35_LEGACY) * 2
    assert set(c["profile_id"] for c in matrix) == set(PROFILE_IDS_C35_LEGACY)


def test_c351_eval_pack_shape_flag():
    matrix = build_synthetic_eval_matrix_c351(days=28)
    report = run_eval_pack_c35(matrix)
    assert report["shape"]["c351_shape_ok"] is True
    assert report["shape"]["cells"] >= 400
    assert report["shape"]["days"] == 28
    assert len(report["shape"]["profiles"]) >= 8

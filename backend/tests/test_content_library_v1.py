"""Practice content library seed — taxonomy + coverage ledger."""

from __future__ import annotations

import json
from pathlib import Path

from todayflow_backend.data.content_library_validator_v1 import (
    first_empty_p0_cell,
    first_empty_p0_type,
    first_p0_type_needing_context_density,
    first_p0_type_needing_density,
    load_json,
    validate_content_library_v1,
    validate_technique_canon_v1,
    validate_technique_landscape_v1,
    validate_technique_shortlist_criteria_v1,
    validate_technique_shortlist_v1,
    validate_technique_ingest_v1,
    validate_technique_normalization_v1,
    validate_technique_targeted_shortlist_v1,
    validate_technique_targeted_ingest_v1,
    validate_technique_normalization_v1_1,
    validate_technique_safety_review_v1,
    validate_technique_targeted_safety_shortlist_v1,
    validate_technique_targeted_safety_ingest_v1,
)
from todayflow_backend.data.reference_machine_loader import DATA_ROOT

PRACTICE_REF = DATA_ROOT / "reference" / "practice"
VOCAB_PATH = PRACTICE_REF / "content_taxonomy_v1.json"
LIBRARY_PATH = PRACTICE_REF / "content_library_v1.json"
COVERAGE_PATH = PRACTICE_REF / "content_coverage_matrix_v1.json"
TECHNIQUE_PATH = PRACTICE_REF / "technique_canon_v1.json"
TECHNIQUE_CONTRACT_PATH = PRACTICE_REF / "technique_canon_contract_v1.json"
LANDSCAPE_PATH = PRACTICE_REF / "technique_landscape_v1.json"
LANDSCAPE_CONTRACT_PATH = PRACTICE_REF / "technique_landscape_contract_v1.json"
PROVENANCE_CANON = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "practices"
    / "PRACTICE_TECHNIQUE_PROVENANCE_V1.md"
)
LANDSCAPE_CANON = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "practices"
    / "PRACTICE_TECHNIQUE_LANDSCAPE_V1.md"
)
CRITERIA_PATH = PRACTICE_REF / "technique_shortlist_criteria_v1.json"
SHORTLIST_PATH = PRACTICE_REF / "technique_shortlist_v1.json"
SHORTLIST_CONTRACT_PATH = PRACTICE_REF / "technique_shortlist_contract_v1.json"
CRITERIA_CANON = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "practices"
    / "PRACTICE_TECHNIQUE_SHORTLIST_CRITERIA_V1.md"
)
SHORTLIST_CANON = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "practices"
    / "PRACTICE_TECHNIQUE_SHORTLIST_V1.md"
)
INGEST_PATH = PRACTICE_REF / "technique_ingest_v1.json"
INGEST_CONTRACT_PATH = PRACTICE_REF / "technique_ingest_contract_v1.json"
INGEST_CANON = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "practices"
    / "PRACTICE_TECHNIQUE_INGEST_V1.md"
)
NORMALIZATION_PATH = PRACTICE_REF / "technique_normalization_v1.json"
NORMALIZATION_CONTRACT_PATH = PRACTICE_REF / "technique_normalization_contract_v1.json"
NORMALIZATION_CANON = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "practices"
    / "PRACTICE_TECHNIQUE_NORMALIZATION_V1.md"
)
TARGETED_SHORTLIST_PATH = PRACTICE_REF / "technique_targeted_shortlist_v1.json"
TARGETED_SHORTLIST_CONTRACT_PATH = (
    PRACTICE_REF / "technique_targeted_shortlist_contract_v1.json"
)
TARGETED_SHORTLIST_CANON = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "practices"
    / "PRACTICE_TECHNIQUE_TARGETED_SHORTLIST_V1.md"
)
TARGETED_INGEST_PATH = PRACTICE_REF / "technique_targeted_ingest_v1.json"
TARGETED_INGEST_CONTRACT_PATH = PRACTICE_REF / "technique_targeted_ingest_contract_v1.json"
TARGETED_INGEST_CANON = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "practices"
    / "PRACTICE_TECHNIQUE_TARGETED_INGEST_V1.md"
)
NORMALIZATION_V1_1_PATH = PRACTICE_REF / "technique_normalization_v1_1.json"
NORMALIZATION_V1_1_CONTRACT_PATH = (
    PRACTICE_REF / "technique_normalization_v1_1_contract_v1.json"
)
NORMALIZATION_V1_1_CANON = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "practices"
    / "PRACTICE_TECHNIQUE_NORMALIZATION_V1_1.md"
)
SAFETY_REVIEW_PATH = PRACTICE_REF / "technique_safety_review_v1.json"
SAFETY_REVIEW_CONTRACT_PATH = (
    PRACTICE_REF / "technique_safety_review_contract_v1.json"
)
SAFETY_REVIEW_CANON = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "practices"
    / "PRACTICE_TECHNIQUE_SAFETY_REVIEW_V1.md"
)
SAFETY_SHORTLIST_PATH = PRACTICE_REF / "technique_targeted_safety_shortlist_v1.json"
SAFETY_SHORTLIST_CONTRACT_PATH = (
    PRACTICE_REF / "technique_targeted_safety_shortlist_contract_v1.json"
)
SAFETY_SHORTLIST_CANON = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "practices"
    / "PRACTICE_TECHNIQUE_TARGETED_SAFETY_SHORTLIST_V1.md"
)
SAFETY_INGEST_PATH = PRACTICE_REF / "technique_targeted_safety_ingest_v1.json"
SAFETY_INGEST_CONTRACT_PATH = (
    PRACTICE_REF / "technique_targeted_safety_ingest_contract_v1.json"
)
SAFETY_INGEST_CANON = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "practices"
    / "PRACTICE_TECHNIQUE_TARGETED_SAFETY_INGEST_V1.md"
)
FILL_CANON = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "practices"
    / "PRACTICE_LIBRARY_FILL_V1.md"
)
ARCHIVE_CANON = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "practices"
    / "PRACTICE_TECHNIQUE_RESEARCH_ARCHIVE_V1.md"
)

SEED_1_ID = "practice.sensory_grounding.001"
SEED_1_CELL = "need.grounding.stabilize"
SEED_2_ID = "practice.extended_exhale.001"
SEED_2_CELL = "need.calm.downregulate"
SEED_3_ID = "practice.box_breathing.001"
SEED_3_CELL = "need.focus.focus"
SEED_4_ID = "practice.energizing_breath.001"
SEED_4_CELL = "need.energy.activate"
SEED_5_ID = "practice.prompted_reflection.001"
SEED_5_CELL = "need.clarity.reflect"
SEED_6_ID = "affirmation.capability.001"
SEED_6_CELL = "need.confidence.open"
SEED_7_ID = "practice.body_release.001"
SEED_7_CELL = "need.release.release"
SEED_8_ID = "meditation.relaxation.001"
SEED_8_CELL = "need.rest.downregulate"
SEED_9_ID = "meditation.sleep.001"
SEED_9_CELL = "need.sleep.prepare"
SEED_10_ID = "discipline.sleep_discipline.001"
SEED_10_CELL = "need.sleep.discipline"
SEED_11_ID = "practice.micro_action.001"
SEED_11_CELL = "need.motivation.activate"
SEED_12_ID = "practice.self_check_in.001"
SEED_12_CELL = "need.emotional_awareness.reflect"
SEED_13_ID = "practice.journaling.001"
SEED_13_CELL = "need.self_connection.reflect"
SEED_14_ID = "practice.connection_action.001"
SEED_14_CELL = "need.connection.connect"
SEED_15_ID = "practice.creative_prompt.001"
SEED_15_CELL = "need.creativity.open"
SEED_16_ID = "practice.priority_setting.001"
SEED_16_CELL = "need.decision_making.focus"
SEED_17_ID = "practice.transition_ritual.001"
SEED_17_CELL = "need.transition.prepare"
SEED_18_ID = "practice.progressive_relaxation.001"
SEED_18_CELL = "need.recovery.recover"
SEED_19_ID = "discipline.routine_commitment.001"
SEED_19_CELL = "need.discipline.prepare"
SEED_20_ID = "discipline.attention_discipline.001"
SEED_20_CELL = "need.self_control.stabilize"
SEED_21_ID = "discipline.abstinence.001"
PROBE_21_ID = "meditation.acceptance.001"
SEED_21_CELL = "need.detachment.release"
SEED_22_ID = "discipline.consistency_challenge.001"
SEED_22_CELL = "need.consistency.prepare"
SEED_23_ID = "discipline.reduction.001"
SEED_23_CELL = "need.simplicity.release"
SEED_24_ID = "practice.digital_pause.001"
SEED_24_CELL = "need.reset.release"
SEED_25_ID = "meditation.mindfulness.001"
SEED_25_CELL = "need.presence.stabilize"
SEED_26_ID = "discipline.consistency_challenge.002"
SEED_26_CELL = "need.habit_change.prepare"

SPINE_SPECS = (
    ("practice.mobility.001", "need.energy.activate", "practice", "mobility", "movement", ["energy"], ["activate"]),
    ("practice.intention_setting.001", "need.decision_making.focus", "practice", "intention_setting", "intention", ["decision_making"], ["focus"]),
    ("practice.environment_reset.001", "need.reset.release", "practice", "environment_reset", "behavioral", ["reset"], ["release"]),
    ("practice.free_writing.001", "need.creativity.open", "practice", "free_writing", "creative", ["creativity"], ["open"]),
    ("practice.morning_ritual.001", "need.transition.prepare", "practice", "morning_ritual", "ritual", ["transition"], ["prepare"]),
    ("practice.evening_ritual.001", "need.sleep.prepare", "practice", "evening_ritual", "ritual", ["sleep"], ["prepare"]),
    ("meditation.breath_awareness.001", "need.presence.stabilize", "meditation", "breath_awareness", None, ["presence"], ["stabilize"]),
    ("meditation.body_scan.001", "need.self_connection.reflect", "meditation", "body_scan", None, ["self_connection"], ["reflect"]),
    ("meditation.open_awareness.001", "need.emotional_awareness.reflect", "meditation", "open_awareness", None, ["emotional_awareness"], ["reflect"]),
    ("meditation.focused_attention.001", "need.focus.focus", "meditation", "focused_attention", None, ["focus"], ["focus"]),
    ("meditation.grounding.001", "need.grounding.stabilize", "meditation", "grounding", None, ["grounding"], ["stabilize"]),
    ("meditation.acceptance.001", "need.detachment.release", "meditation", "acceptance", None, ["detachment"], ["release"]),
    ("meditation.letting_go.001", "need.release.release", "meditation", "letting_go", None, ["release"], ["release"]),
    ("meditation.reflection_meditation.001", "need.clarity.reflect", "meditation", "reflection_meditation", None, ["clarity"], ["reflect"]),
    ("affirmation.self_trust.001", "need.confidence.open", "affirmation", "self_trust", None, ["confidence"], ["open"]),
    ("affirmation.agency.001", "need.motivation.activate", "affirmation", "agency", None, ["motivation"], ["activate"]),
    ("affirmation.relationship.001", "need.connection.connect", "affirmation", "relationship", None, ["connection"], ["connect"]),
    ("discipline.digital_limit.001", "need.self_control.stabilize", "discipline", "digital_limit", None, ["self_control"], ["stabilize"]),
    ("discipline.consumption_limit.001", "need.simplicity.release", "discipline", "consumption_limit", None, ["simplicity"], ["release"]),
)


def _load() -> tuple[dict, dict, dict]:
    return (
        load_json(VOCAB_PATH),
        load_json(LIBRARY_PATH),
        load_json(COVERAGE_PATH),
    )


def _techniques() -> dict:
    return load_json(TECHNIQUE_PATH)


def test_library_valid_against_taxonomy_and_ledger() -> None:
    vocab, library, coverage = _load()
    assert (
        validate_content_library_v1(
            library, vocab=vocab, coverage=coverage, techniques=_techniques()
        )
        == []
    )


def test_technique_canon_lightweight_skip_box() -> None:
    techniques = _techniques()
    assert validate_technique_canon_v1(techniques) == []
    assert techniques["research_ladder_required"] is False
    rows = techniques["techniques"]
    assert rows
    by_id = {row["technique_id"]: row for row in rows}
    box = by_id["technique.box_breathing"]
    assert box["status"] == "skipped"
    assert box["skip_reason"] == "skipped_for_now"
    assert box["type"] == "box_breathing"
    exhale = by_id["technique.extended_exhale"]
    assert exhale["status"] == "accepted"
    assert exhale["type"] == "extended_exhale"
    assert exhale["allowed_claims"] == []
    assert exhale["source_refs"]
    assert exhale["canonical_description"].strip()
    fa = by_id["technique.focused_attention"]
    assert fa["status"] == "accepted"
    assert fa["type"] == "focused_attention"
    assert fa["allowed_claims"] == []
    assert fa["source_refs"]
    assert fa["canonical_description"].strip()
    energy = by_id["technique.energizing_breath"]
    assert energy["status"] == "skipped"
    assert energy["skip_reason"] == "skipped_for_now"
    assert energy["type"] == "energizing_breath"
    mobility = by_id["technique.mobility"]
    assert mobility["status"] == "accepted"
    assert mobility["type"] == "mobility"
    assert mobility["allowed_claims"] == []
    assert mobility["source_refs"]
    assert mobility["canonical_description"].strip()
    sensory = by_id["technique.sensory_grounding"]
    assert sensory["status"] == "accepted"
    assert sensory["type"] == "sensory_grounding"
    assert sensory["allowed_claims"] == []
    assert sensory["source_refs"]
    assert sensory["canonical_description"].strip()
    assert "5-4-3-2-1" in sensory["canonical_description"] or "3-2-1" in sensory["canonical_description"]
    prompted = by_id["technique.prompted_reflection"]
    assert prompted["status"] == "accepted"
    assert prompted["type"] == "prompted_reflection"
    assert prompted["allowed_claims"] == []
    assert prompted["source_refs"]
    assert prompted["canonical_description"].strip()


def test_fill_unfrozen_provisional_probes() -> None:
    _vocab, library, coverage = _load()
    techniques = _techniques()
    assert library["status"] == "provisional"
    assert library["fill_frozen"] is False
    assert library["content_origin"] == "llm_provisional"
    assert coverage["fill_frozen"] is False
    assert coverage["next_pass"] == "library_fill_lightweight_provenance"
    assert coverage["next_fill_cell"] == "need.consistency.prepare"
    assert "box_breathing" in coverage["skipped_types"]
    assert "energizing_breath" in coverage["skipped_types"]
    probes = library["architecture_probe_item_ids"]
    assert probes == [
        SEED_1_ID,
        SEED_2_ID,
        SEED_3_ID,
        SEED_4_ID,
        SEED_5_ID,
        SEED_6_ID,
        SEED_7_ID,
        SEED_8_ID,
        SEED_9_ID,
        SEED_10_ID,
        SEED_11_ID,
        SEED_12_ID,
        SEED_13_ID,
        SEED_14_ID,
        SEED_15_ID,
        SEED_16_ID,
        SEED_17_ID,
        SEED_18_ID,
        SEED_19_ID,
        SEED_20_ID,
        PROBE_21_ID,
    ]
    item_ids = {item["identity"]["item_id"] for item in library["items"]}
    assert set(probes) <= item_ids
    sourced = {
        item["identity"]["item_id"]: item["identity"].get("technique_id")
        for item in library["items"]
        if "technique_id" in item["identity"]
    }
    assert sourced == {
        "practice.extended_exhale.001": "technique.extended_exhale",
        "practice.extended_exhale.002": "technique.extended_exhale",
        "practice.extended_exhale.003": "technique.extended_exhale",
        "meditation.focused_attention.001": "technique.focused_attention",
        "meditation.focused_attention.002": "technique.focused_attention",
        "meditation.focused_attention.003": "technique.focused_attention",
        "practice.mobility.001": "technique.mobility",
        "practice.mobility.002": "technique.mobility",
        "practice.mobility.003": "technique.mobility",
        "practice.sensory_grounding.001": "technique.sensory_grounding",
        "practice.sensory_grounding.002": "technique.sensory_grounding",
        "practice.sensory_grounding.003": "technique.sensory_grounding",
        "practice.prompted_reflection.001": "technique.prompted_reflection",
        "practice.prompted_reflection.002": "technique.prompted_reflection",
        "practice.prompted_reflection.003": "technique.prompted_reflection",
        "affirmation.capability.001": "technique.capability",
        "affirmation.capability.002": "technique.capability",
        "affirmation.capability.003": "technique.capability",
        "practice.body_release.001": "technique.body_release",
        "practice.body_release.002": "technique.body_release",
        "practice.body_release.003": "technique.body_release",
        "meditation.relaxation.001": "technique.relaxation",
        "meditation.relaxation.002": "technique.relaxation",
        "meditation.relaxation.003": "technique.relaxation",
        "meditation.sleep.001": "technique.sleep",
        "meditation.sleep.002": "technique.sleep",
        "meditation.sleep.003": "technique.sleep",
        "discipline.sleep_discipline.001": "technique.sleep_discipline",
        "discipline.sleep_discipline.002": "technique.sleep_discipline",
        "discipline.sleep_discipline.003": "technique.sleep_discipline",
        "practice.micro_action.001": "technique.micro_action",
        "practice.micro_action.002": "technique.micro_action",
        "practice.micro_action.003": "technique.micro_action",
        "practice.self_check_in.001": "technique.self_check_in",
        "practice.self_check_in.002": "technique.self_check_in",
        "practice.self_check_in.003": "technique.self_check_in",
        "practice.journaling.001": "technique.journaling",
        "practice.journaling.002": "technique.journaling",
        "practice.journaling.003": "technique.journaling",
        "practice.connection_action.001": "technique.connection_action",
        "practice.connection_action.002": "technique.connection_action",
        "practice.connection_action.003": "technique.connection_action",
        "practice.creative_prompt.001": "technique.creative_prompt",
        "practice.creative_prompt.002": "technique.creative_prompt",
        "practice.creative_prompt.003": "technique.creative_prompt",
        "practice.priority_setting.001": "technique.priority_setting",
        "practice.priority_setting.002": "technique.priority_setting",
        "practice.priority_setting.003": "technique.priority_setting",
        "practice.transition_ritual.001": "technique.transition_ritual",
        "practice.transition_ritual.002": "technique.transition_ritual",
        "practice.transition_ritual.003": "technique.transition_ritual",
        "practice.progressive_relaxation.001": "technique.progressive_relaxation",
        "practice.progressive_relaxation.002": "technique.progressive_relaxation",
        "practice.progressive_relaxation.003": "technique.progressive_relaxation",
        "discipline.routine_commitment.001": "technique.routine_commitment",
        "discipline.routine_commitment.002": "technique.routine_commitment",
        "discipline.routine_commitment.003": "technique.routine_commitment",
        "discipline.attention_discipline.001": "technique.attention_discipline",
        "discipline.attention_discipline.002": "technique.attention_discipline",
        "discipline.attention_discipline.003": "technique.attention_discipline",
        "meditation.acceptance.001": "technique.acceptance",
        "meditation.acceptance.002": "technique.acceptance",
        "meditation.acceptance.003": "technique.acceptance",
    }
    assert any(r.get("status") == "accepted" for r in techniques["techniques"])


def test_unknown_technique_id_rejected() -> None:
    vocab, library, coverage = _load()
    library["items"][0]["identity"] = {
        **library["items"][0]["identity"],
        "technique_id": "technique.does_not_exist",
    }
    errors = validate_content_library_v1(
        library, vocab=vocab, coverage=coverage, techniques=_techniques()
    )
    assert any("not in technique canon" in e for e in errors)


def test_skipped_technique_id_rejected() -> None:
    vocab, library, coverage = _load()
    library["items"][0]["identity"] = {
        **library["items"][0]["identity"],
        "technique_id": "technique.box_breathing",
    }
    errors = validate_content_library_v1(
        library, vocab=vocab, coverage=coverage, techniques=_techniques()
    )
    assert any("must not attach skipped technique_id" in e for e in errors)


def test_provenance_paths_exist() -> None:
    assert PROVENANCE_CANON.is_file()
    assert LANDSCAPE_CANON.is_file()
    assert CRITERIA_CANON.is_file()
    assert SHORTLIST_CANON.is_file()
    assert INGEST_CANON.is_file()
    assert NORMALIZATION_CANON.is_file()
    assert TECHNIQUE_PATH.is_file()
    assert TECHNIQUE_CONTRACT_PATH.is_file()
    assert LANDSCAPE_PATH.is_file()
    assert LANDSCAPE_CONTRACT_PATH.is_file()
    assert CRITERIA_PATH.is_file()
    assert SHORTLIST_PATH.is_file()
    assert SHORTLIST_CONTRACT_PATH.is_file()
    assert INGEST_PATH.is_file()
    assert INGEST_CONTRACT_PATH.is_file()
    assert NORMALIZATION_PATH.is_file()
    assert NORMALIZATION_CONTRACT_PATH.is_file()
    assert TARGETED_SHORTLIST_CANON.is_file()
    assert TARGETED_SHORTLIST_PATH.is_file()
    assert TARGETED_SHORTLIST_CONTRACT_PATH.is_file()
    assert TARGETED_INGEST_CANON.is_file()
    assert TARGETED_INGEST_PATH.is_file()
    assert TARGETED_INGEST_CONTRACT_PATH.is_file()
    assert NORMALIZATION_V1_1_CANON.is_file()
    assert NORMALIZATION_V1_1_PATH.is_file()
    assert NORMALIZATION_V1_1_CONTRACT_PATH.is_file()
    assert SAFETY_REVIEW_CANON.is_file()
    assert SAFETY_REVIEW_PATH.is_file()
    assert SAFETY_REVIEW_CONTRACT_PATH.is_file()
    assert SAFETY_SHORTLIST_CANON.is_file()
    assert SAFETY_SHORTLIST_PATH.is_file()
    assert SAFETY_SHORTLIST_CONTRACT_PATH.is_file()
    assert SAFETY_INGEST_CANON.is_file()
    assert FILL_CANON.is_file()
    assert ARCHIVE_CANON.is_file()
    assert SAFETY_INGEST_PATH.is_file()
    assert SAFETY_INGEST_CONTRACT_PATH.is_file()


def test_technique_landscape_v1_splits_probe_families() -> None:
    vocab, _library, _coverage = _load()
    landscape = load_json(LANDSCAPE_PATH)
    assert validate_technique_landscape_v1(landscape, vocab=vocab) == []
    assert landscape["shortlist_opened"] is False
    assert landscape["writes_technique_canon"] is False
    assert landscape["shortlist_mode"] == "vertical_slice"
    assert landscape["shortlist_slice_family"] == "family.practice.equal_count_breath"
    assert next(
        r["status"]
        for r in _techniques()["techniques"]
        if r["technique_id"] == "technique.box_breathing"
    ) == "skipped"
    classes = {row["content_class"] for row in landscape["families"]}
    assert classes == {"practice", "meditation", "affirmation", "discipline"}
    by_id = {row["family_id"]: row for row in landscape["families"]}
    assert by_id["family.practice.equal_count_breath"]["shortlist_status"] == "sliced"
    assert all(
        row["shortlist_status"] == "not_opened"
        for row in landscape["families"]
        if row["family_id"] != "family.practice.equal_count_breath"
    )
    assert landscape["criteria_canon"] == "PRACTICE_TECHNIQUE_SHORTLIST_CRITERIA_V1"
    assert landscape["shortlist_canon"] == "PRACTICE_TECHNIQUE_SHORTLIST_V1"
    assert landscape["ingest_canon"] == "PRACTICE_TECHNIQUE_INGEST_V1"
    assert landscape["normalization_canon"] == "PRACTICE_TECHNIQUE_NORMALIZATION_V1"
    assert landscape["targeted_shortlist_canon"] == (
        "PRACTICE_TECHNIQUE_TARGETED_SHORTLIST_V1"
    )
    assert landscape["targeted_ingest_canon"] == "PRACTICE_TECHNIQUE_TARGETED_INGEST_V1"
    assert landscape["normalization_v1_1_canon"] == (
        "PRACTICE_TECHNIQUE_NORMALIZATION_V1_1"
    )
    assert landscape["safety_review_canon"] == "PRACTICE_TECHNIQUE_SAFETY_REVIEW_V1"
    assert landscape["targeted_safety_shortlist_canon"] == (
        "PRACTICE_TECHNIQUE_TARGETED_SAFETY_SHORTLIST_V1"
    )
    assert landscape["targeted_safety_ingest_canon"] == (
        "PRACTICE_TECHNIQUE_TARGETED_SAFETY_INGEST_V1"
    )
    assert landscape["next_named_pass"] == "library_fill_lightweight_provenance"
    assert landscape["workflow_status"] == "research_archive"
    assert landscape["blocks_fill"] is False
    eq = by_id["family.practice.equal_count_breath"]
    assert eq["normalization_status"] == "normalize_one"
    assert eq["safety_review_status"] == "insufficient_safety"
    assert eq["mechanism_shape_at_landscape_v1"].startswith("four equal phases")
    assert eq["mechanism_shape"].startswith("four timed phases")
    assert "common parameter" in eq["mechanism_shape"]
    assert "energizing_breath" in by_id["family.practice.unattested_short_exhale"]["candidate_types"]
    assert by_id["family.practice.activating_forceful_breath"]["candidate_types"] == []
    assert by_id["family.practice.unattested_short_exhale"]["likely_disposition"] == "reject_or_remap"
    assert "capability" in by_id["family.affirmation.coping_statement"]["candidate_types"]
    assert by_id["family.affirmation.values_self_affirmation"]["candidate_types"] == []
    assert "body_release" in by_id["family.practice.informal_somatic_release"]["candidate_types"]
    assert "body_release" not in by_id["family.practice.progressive_muscle_relaxation"]["candidate_types"]
    assert "sleep_discipline" in by_id["family.discipline.schedule_window"]["candidate_types"]
    assert by_id["family.discipline.clinical_insomnia_protocol"]["candidate_types"] == []


def test_shortlist_criteria_v1_does_not_open_shortlist() -> None:
    criteria = load_json(CRITERIA_PATH)
    assert validate_technique_shortlist_criteria_v1(criteria) == []
    assert criteria["shortlist_opened"] is False
    assert criteria["unit_of_shortlist"] == "candidate_family"
    assert criteria["technique_id_allowed_at"] == "canonical"
    assert criteria["pipeline_after_open"][0] == "candidate_family"
    assert criteria["pipeline_after_open"][-1] == "canonical_or_rejected"
    assert [g["id"] for g in criteria["gates"]] == [f"C{i}" for i in range(1, 10)]
    assert next(
        r["status"]
        for r in _techniques()["techniques"]
        if r["technique_id"] == "technique.box_breathing"
    ) == "skipped"
    landscape = load_json(LANDSCAPE_PATH)
    assert landscape["shortlist_opened"] is False
    assert criteria["shortlist_opened"] is False


def test_technique_shortlist_v1_equal_count_slice_not_canon() -> None:
    shortlist = load_json(SHORTLIST_PATH)
    landscape = load_json(LANDSCAPE_PATH)
    assert validate_technique_shortlist_v1(shortlist) == []
    assert shortlist["writes_technique_canon"] is False
    assert shortlist["technique_id_allowed"] is False
    assert shortlist["selected_means"] == "allowed_for_next_ingest_pass"
    assert (
        shortlist["boundary_held"]
        == "landscape_candidate_family_to_selected_loci_not_canonical"
    )
    family = shortlist["families"][0]
    assert family["family_id"] == "family.practice.equal_count_breath"
    assert family["expression_hypothesis"]["status"] == "not_attested"
    assert family["expression_hypothesis"]["type"] == "box_breathing"
    decisions = {src["source_id"]: src["selection_decision"] for src in family["candidate_sources"]}
    assert decisions["src.bhf.heart_matters.box"] == "selected"
    assert decisions["src.nhs.sfh.box_leaflet"] == "selected"
    assert decisions["src.nhs.newcastle.square"] == "selected"
    assert decisions["src.clevelandclinic.box"] == "supporting"
    assert decisions["src.iyengar.light_on_pranayama.ch18"] == "supporting"
    assert decisions["src.harvard.tactical_breather"] == "rejected"
    assert family["selected_loci"] == [
        "src.bhf.heart_matters.box",
        "src.nhs.sfh.box_leaflet",
        "src.nhs.newcastle.square",
    ]
    conflict_ids = {c["id"] for c in family["conflicts"]}
    assert "conflict.phase_count" in conflict_ids
    assert "conflict.holds_as_kernel_vs_later_ratio" in conflict_ids
    assert landscape["shortlist_slice_family"] == family["family_id"]
    assert next(
        r["status"]
        for r in _techniques()["techniques"]
        if r["technique_id"] == "technique.box_breathing"
    ) == "skipped"
    _vocab, library, _coverage = _load()
    for item in library["items"]:
        if item["identity"]["type"] == "box_breathing":
            assert "technique_id" not in item["identity"]


def test_technique_ingest_v1_equal_count_evidence_not_kernel() -> None:
    ingest = load_json(INGEST_PATH)
    shortlist = load_json(SHORTLIST_PATH)
    assert validate_technique_ingest_v1(ingest, shortlist=shortlist) == []
    assert ingest["writes_technique_canon"] is False
    assert ingest["does_not_normalize"] is True
    assert ingest["family_id"] == "family.practice.equal_count_breath"
    assert len(ingest["evidence"]) == 3
    by_src = {row["source_ref"]["source_id"]: row for row in ingest["evidence"]}
    assert [row["source_ref"]["source_id"] for row in ingest["evidence"]] == shortlist[
        "families"
    ][0]["selected_loci"]
    bhf = by_src["src.bhf.heart_matters.box"]
    sfh = by_src["src.nhs.sfh.box_leaflet"]
    newcastle = by_src["src.nhs.newcastle.square"]
    assert bhf["claim_scope"] == "method_sequence_only"
    assert bhf["observed_safety"] == []
    assert sfh["claim_scope"] == "method_sequence_and_stop_rules"
    assert sfh["observed_safety"]
    assert "grounding" not in " ".join(sfh["observed_steps"]).lower()
    assert newcastle["claim_scope"] == "conflicting_method_sequence"
    assert newcastle["observed_variants"] == []
    assert "recorded_as_conflicting_description_not_variant" in newcastle["conflict_tags"]
    assert all(row["ingest_status"] == "ingested" for row in ingest["evidence"])
    assert next(
        r["status"]
        for r in _techniques()["techniques"]
        if r["technique_id"] == "technique.box_breathing"
    ) == "skipped"
    _vocab, library, _coverage = _load()
    probe = next(i for i in library["items"] if i["identity"]["item_id"] == SEED_3_ID)
    assert library["status"] == "provisional"
    assert "technique_id" not in probe["identity"]
    assert probe["identity"]["type"] == "box_breathing"


def test_technique_normalization_v1_insufficient_evidence_not_canon() -> None:
    ingest = load_json(INGEST_PATH)
    normalization = load_json(NORMALIZATION_PATH)
    assert validate_technique_normalization_v1(normalization, ingest=ingest) == []
    assert normalization["decision"] == "insufficient_evidence"
    assert normalization["writes_technique_canon"] is False
    assert normalization["technique_id_allowed"] is False
    assert normalization["normalize_one_is_not_canonical"] is True
    assert list(normalization["comparison"]) == [
        "mechanism",
        "identity_bearing_steps",
        "bounds",
        "variants_vs_conflicts",
    ]
    assert normalization["comparison"]["identity_bearing_steps"]["status"] == "unresolved"
    assert "post-exhale hold" in normalization["research_question"].lower()
    assert (
        normalization["next_named_pass"]
        == "targeted_shortlist_post_exhale_hold_identity"
    )
    assert "safety_review" in normalization["not_next"]
    assert next(
        r["status"]
        for r in _techniques()["techniques"]
        if r["technique_id"] == "technique.box_breathing"
    ) == "skipped"
    _vocab, library, _coverage = _load()
    probe = next(i for i in library["items"] if i["identity"]["item_id"] == SEED_3_ID)
    assert "technique_id" not in probe["identity"]
    landscape = load_json(LANDSCAPE_PATH)
    eq = next(
        r
        for r in landscape["families"]
        if r["family_id"] == "family.practice.equal_count_breath"
    )
    assert eq["mechanism_shape_at_landscape_v1"].startswith("four equal phases")
    assert eq["shortlist_status"] == "sliced"


def test_technique_targeted_shortlist_v1_hold_identity_not_canon() -> None:
    ingest = load_json(INGEST_PATH)
    targeted = load_json(TARGETED_SHORTLIST_PATH)
    assert validate_technique_targeted_shortlist_v1(targeted, ingest=ingest) == []
    assert targeted["writes_technique_canon"] is False
    assert targeted["technique_id_allowed"] is False
    assert targeted["unit_of_shortlist"] == "research_question"
    assert targeted["selected_means"] == "allowed_for_targeted_ingest_pass"
    assert targeted["stop_reason"] == "resolution_candidates_found_for_targeted_ingest"
    assert targeted["variant_found_in_preferred_class"] is False
    assert targeted["repeat_insufficient_evidence_after_v1_1_is_allowed"] is True
    assert targeted["next_named_pass"] == "targeted_ingest_post_exhale_hold_identity"
    assert "safety_review" in targeted["not_next"]
    assert "box_breathing_in_general" in targeted["not_in_scope"]
    by_id = {row["source_id"]: row for row in targeted["candidate_loci"]}
    assert by_id["src.bhf.heart_matters.box"]["resolution_role"] == "replication"
    assert by_id["src.nhs.sfh.box_leaflet"]["resolution_role"] == "replication"
    assert by_id["src.nhs.newcastle.square"]["identity_statement"] == (
        "absent_but_unaddressed"
    )
    assert by_id["src.byu.marchant.2025.square"]["resolution_role"] == "contrast"
    assert by_id["src.nhs.wales.cavuhb.square"]["resolution_role"] == "definition"
    assert by_id["src.growtherapy.square"]["selection_decision"] == "rejected"
    assert targeted["selected_loci"] == [
        "src.byu.marchant.2025.square",
        "src.nhs.wales.cavuhb.square",
    ]
    assert next(
        r["status"]
        for r in _techniques()["techniques"]
        if r["technique_id"] == "technique.box_breathing"
    ) == "skipped"
    _vocab, library, _coverage = _load()
    probe = next(i for i in library["items"] if i["identity"]["item_id"] == SEED_3_ID)
    assert "technique_id" not in probe["identity"]
    landscape = load_json(LANDSCAPE_PATH)
    eq = next(
        r
        for r in landscape["families"]
        if r["family_id"] == "family.practice.equal_count_breath"
    )
    assert eq["mechanism_shape_at_landscape_v1"].startswith("four equal phases")
    assert eq["normalization_status"] == "normalize_one"


def test_technique_targeted_ingest_v1_two_loci_not_kernel() -> None:
    targeted = load_json(TARGETED_SHORTLIST_PATH)
    family_ingest = load_json(INGEST_PATH)
    ingest = load_json(TARGETED_INGEST_PATH)
    assert validate_technique_targeted_ingest_v1(
        ingest, targeted_shortlist=targeted, family_ingest=family_ingest
    ) == []
    assert ingest["writes_technique_canon"] is False
    assert ingest["does_not_normalize"] is True
    assert ingest["does_not_glue_axes"] is True
    assert ingest["does_not_replace_family_ingest"] is True
    assert ingest["next_named_pass"] == "technique_normalization_v1_1"
    assert "safety_review" in ingest["not_next"]
    assert [a["axis_id"] for a in ingest["axes_observed_not_decided"]] == [
        "shape_phase_structure",
        "timing_ratio",
    ]
    assert all(a["status"] == "signal_only" for a in ingest["axes_observed_not_decided"])
    qids = [q["id"] for q in ingest["v1_1_identity_questions"]]
    assert qids == ["post_exhale_hold", "equal_count"]
    assert ingest["v1_1_overall_verdict_unchanged"] == [
        "normalize_one",
        "split_family",
        "insufficient_evidence",
    ]
    by_src = {row["source_ref"]["source_id"]: row for row in ingest["evidence"]}
    assert list(by_src) == targeted["selected_loci"]
    marchant = by_src["src.byu.marchant.2025.square"]
    cavuhb = by_src["src.nhs.wales.cavuhb.square"]
    assert marchant["claim_scope"] == "experimental_named_conditions"
    assert marchant["does_not_generalize_author_contrast"] is True
    assert marchant["observed_variants"] == []
    names = [c["name_in_source"] for c in marchant["observed_named_conditions"]]
    assert names == ["Square breathing", "5:5 breathing"]
    assert marchant["observed_contrast_condition"]["name_in_source"] == "5:5 breathing"
    assert cavuhb["claim_scope"] == "method_sequence_and_label"
    assert cavuhb["does_not_treat_unequal_counts_as_variant"] is True
    assert cavuhb["observed_variants"] == []
    assert "recorded_as_label_observation_not_variant" in cavuhb["conflict_tags"]
    assert next(
        r["status"]
        for r in _techniques()["techniques"]
        if r["technique_id"] == "technique.box_breathing"
    ) == "skipped"
    _vocab, library, _coverage = _load()
    probe = next(i for i in library["items"] if i["identity"]["item_id"] == SEED_3_ID)
    assert "technique_id" not in probe["identity"]
    landscape = load_json(LANDSCAPE_PATH)
    eq = next(
        r
        for r in landscape["families"]
        if r["family_id"] == "family.practice.equal_count_breath"
    )
    assert eq["mechanism_shape_at_landscape_v1"].startswith("four equal phases")
    assert eq["normalization_status"] == "normalize_one"


def test_technique_normalization_v1_1_normalize_one_candidate_not_canon() -> None:
    family_ingest = load_json(INGEST_PATH)
    targeted_ingest = load_json(TARGETED_INGEST_PATH)
    landscape = load_json(LANDSCAPE_PATH)
    normalization = load_json(NORMALIZATION_V1_1_PATH)
    assert validate_technique_normalization_v1_1(
        normalization,
        family_ingest=family_ingest,
        targeted_ingest=targeted_ingest,
        landscape=landscape,
    ) == []
    assert normalization["decision"] == "normalize_one"
    assert normalization["writes_technique_canon"] is False
    assert normalization["technique_id_allowed"] is False
    assert normalization["normalize_one_is_not_canonical"] is True
    assert normalization["does_not_erase_v1"] is True
    assert normalization["prior_decision"]["decision"] == "insufficient_evidence"
    assert normalization["axes"]["post_exhale_hold"]["decision"] == "required"
    assert normalization["axes"]["post_exhale_hold"]["criterion"] == "N-H1"
    assert normalization["axes"]["equal_count"]["decision"] == "common_parameter"
    assert normalization["axes"]["equal_count"]["criterion"] == "N-E2"
    candidate = normalization["normalized_candidate"]
    assert candidate["status"] == "normalized_candidate"
    assert candidate["not_canonical"] is True
    assert candidate["identity_kernel"]["shape"] == "four_timed_phases"
    assert candidate["identity_kernel"]["post_exhale_hold"] == "required"
    assert candidate["identity_kernel"]["equal_count"] == "common_parameter"
    assert normalization["next_named_pass"] == "technique_safety_review_v1"
    assert "canonical" in normalization["not_next"]
    assert next(
        r["status"]
        for r in _techniques()["techniques"]
        if r["technique_id"] == "technique.box_breathing"
    ) == "skipped"
    _vocab, library, _coverage = _load()
    probe = next(i for i in library["items"] if i["identity"]["item_id"] == SEED_3_ID)
    assert "technique_id" not in probe["identity"]
    eq = next(
        r
        for r in landscape["families"]
        if r["family_id"] == "family.practice.equal_count_breath"
    )
    assert eq["mechanism_shape_at_landscape_v1"].startswith("four equal phases")
    assert eq["mechanism_shape"].startswith("four timed phases")
    assert eq["normalization_status"] == "normalize_one"
    v1 = load_json(NORMALIZATION_PATH)
    assert v1["decision"] == "insufficient_evidence"


def test_technique_safety_review_v1_insufficient_safety_not_canon() -> None:
    family_ingest = load_json(INGEST_PATH)
    targeted_ingest = load_json(TARGETED_INGEST_PATH)
    landscape = load_json(LANDSCAPE_PATH)
    normalization = load_json(NORMALIZATION_V1_1_PATH)
    review = load_json(SAFETY_REVIEW_PATH)
    assert validate_technique_safety_review_v1(
        review,
        family_ingest=family_ingest,
        targeted_ingest=targeted_ingest,
        normalization_v1_1=normalization,
        landscape=landscape,
    ) == []
    assert review["decision"] == "insufficient_safety"
    assert review["writes_technique_canon"] is False
    assert review["technique_id_allowed"] is False
    assert review["safety_review_is_not_canonical"] is True
    assert review["does_not_reopen_kernel"] is True
    assert review["does_not_open_next_pass"] is True
    assert review["prior_decision"]["decision"] == "normalize_one"
    assert review["identity_kernel_unchanged"]["post_exhale_hold"] == "required"
    assert review["axes"]["stop_rules"]["decision"] == "present"
    assert review["axes"]["stop_rules"]["not_mixed_into_kernel"] is True
    assert review["axes"]["who_must_not_hold"]["decision"] == "unknown"
    assert review["axes"]["who_must_not_hold"]["locked_rule"] == "S-B2"
    assert review["axes"]["prohibition"]["decision"] == "none"
    assert review["axes"]["claim_surface"]["allowed_claims"] == []
    assert review["axes"]["claim_surface"]["efficacy_claim_level"] == "not_claimed"
    assert review["candidate_review_status"] == "normalized"
    assert review["next_named_pass"] == "owner_decides_next_named_pass"
    assert "canonical" in review["not_next"]
    assert "auto_open_targeted_safety_research" in review["not_next"]
    assert next(
        r["status"]
        for r in _techniques()["techniques"]
        if r["technique_id"] == "technique.box_breathing"
    ) == "skipped"
    _vocab, library, _coverage = _load()
    probe = next(i for i in library["items"] if i["identity"]["item_id"] == SEED_3_ID)
    assert "technique_id" not in probe["identity"]
    eq = next(
        r
        for r in landscape["families"]
        if r["family_id"] == "family.practice.equal_count_breath"
    )
    assert eq["mechanism_shape_at_landscape_v1"].startswith("four equal phases")
    assert eq["mechanism_shape"].startswith("four timed phases")
    assert eq["normalization_status"] == "normalize_one"
    assert eq["safety_review_status"] == "insufficient_safety"
    v1 = load_json(NORMALIZATION_PATH)
    assert v1["decision"] == "insufficient_evidence"


def test_technique_targeted_safety_shortlist_v1_who_must_not_not_canon() -> None:
    family_ingest = load_json(INGEST_PATH)
    targeted_ingest = load_json(TARGETED_INGEST_PATH)
    normalization = load_json(NORMALIZATION_V1_1_PATH)
    targeted = load_json(SAFETY_SHORTLIST_PATH)
    assert validate_technique_targeted_safety_shortlist_v1(
        targeted,
        family_ingest=family_ingest,
        targeted_ingest=targeted_ingest,
        normalization_v1_1=normalization,
    ) == []
    assert targeted["writes_technique_canon"] is False
    assert targeted["technique_id_allowed"] is False
    assert targeted["does_not_reopen_kernel"] is True
    assert targeted["does_not_rewrite_safety_contract"] is True
    assert targeted["stop_reason"] == (
        "preferred_class_hold_evidence_found_for_targeted_safety_ingest"
    )
    assert targeted["selected_loci"] == [
        "src.wjm.joshi.2024.yoga_hypertension",
        "src.nivethitha.2017.bahir_kumbhaka",
    ]
    assert targeted["next_named_pass"] == "targeted_safety_ingest_who_must_not_hold"
    assert "rewrite_safety_contract_inside_shortlist" in targeted["not_next"]
    by_id = {row["source_id"]: row for row in targeted["candidate_loci"]}
    assert by_id["src.wjm.joshi.2024.yoga_hypertension"]["safety_speech"] == (
        "hold_exclusion"
    )
    assert by_id["src.nivethitha.2017.bahir_kumbhaka"]["safety_speech"] == (
        "hold_precaution"
    )
    assert by_id["src.bts.2009.physio_spontaneously_breathing"]["selection_decision"] == (
        "supporting"
    )
    assert by_id["src.healthline.box"]["selection_decision"] == "rejected"
    assert by_id["src.nhs.sfh.box_leaflet"]["safety_speech"] == (
        "general_breathwork_precaution"
    )
    assert targeted["identity_kernel_unchanged"]["post_exhale_hold"] == "required"
    assert next(
        r["status"]
        for r in _techniques()["techniques"]
        if r["technique_id"] == "technique.box_breathing"
    ) == "skipped"
    _vocab, library, _coverage = _load()
    probe = next(i for i in library["items"] if i["identity"]["item_id"] == SEED_3_ID)
    assert "technique_id" not in probe["identity"]
    landscape = load_json(LANDSCAPE_PATH)
    eq = next(
        r
        for r in landscape["families"]
        if r["family_id"] == "family.practice.equal_count_breath"
    )
    assert eq["mechanism_shape_at_landscape_v1"].startswith("four equal phases")
    assert eq["safety_review_status"] == "insufficient_safety"
    v1 = load_json(NORMALIZATION_PATH)
    assert v1["decision"] == "insufficient_evidence"


def test_technique_targeted_safety_ingest_v1_observations_not_who_list() -> None:
    shortlist = load_json(SAFETY_SHORTLIST_PATH)
    normalization = load_json(NORMALIZATION_V1_1_PATH)
    ingest = load_json(SAFETY_INGEST_PATH)
    assert validate_technique_targeted_safety_ingest_v1(
        ingest,
        targeted_safety_shortlist=shortlist,
        normalization_v1_1=normalization,
    ) == []
    assert ingest["writes_technique_canon"] is False
    assert ingest["technique_id_allowed"] is False
    assert ingest["does_not_write_who_must_not_hold"] is True
    assert ingest["does_not_write_safety_rules"] is True
    assert ingest["does_not_transfer_onto_four_phase_candidate"] is True
    assert ingest["next_named_pass"] == "technique_safety_review_v1_1"
    assert "write_who_must_not_hold" in ingest["not_next"]
    assert "may_release" in ingest["not_next"]
    by_src = {row["source_ref"]["source_id"]: row for row in ingest["evidence"]}
    assert list(by_src) == shortlist["selected_loci"]
    joshi = by_src["src.wjm.joshi.2024.yoga_hypertension"]
    nive = by_src["src.nivethitha.2017.bahir_kumbhaka"]
    assert joshi["speech_type"] == "hold_exclusion"
    assert joshi["practice_context"] == "kumbhaka"
    assert joshi["is_not_who_must_not_hold_candidate"] is True
    assert {
        item["condition"] for item in joshi["observed_exclusions"]
    } == {
        "hypertension",
        "heart disease",
        "recovering from an illness, surgery, or injury",
    }
    assert all(item["practice_context"] == "kumbhaka" for item in joshi["observed_exclusions"])
    assert nive["speech_type"] == "observed_physiological_response"
    assert nive["observed_exclusions"] == []
    assert nive["dose_or_duration"] == "unspecified_in_this_legally_readable_locus"
    assert "study response is not a contraindication" in nive["transfer_limits"]
    assert ingest["identity_kernel_unchanged"]["post_exhale_hold"] == "required"
    assert next(
        r["status"]
        for r in _techniques()["techniques"]
        if r["technique_id"] == "technique.box_breathing"
    ) == "skipped"
    _vocab, library, _coverage = _load()
    probe = next(i for i in library["items"] if i["identity"]["item_id"] == SEED_3_ID)
    assert "technique_id" not in probe["identity"]
    landscape = load_json(LANDSCAPE_PATH)
    eq = next(
        r
        for r in landscape["families"]
        if r["family_id"] == "family.practice.equal_count_breath"
    )
    assert eq["mechanism_shape_at_landscape_v1"].startswith("four equal phases")
    assert eq["safety_review_status"] == "insufficient_safety"
    v1 = load_json(NORMALIZATION_PATH)
    assert v1["decision"] == "insufficient_evidence"


def test_seed_pass_closes_exactly_one_cell_per_item() -> None:
    _vocab, library, coverage = _load()
    items = {item["identity"]["item_id"]: item for item in library["items"]}
    listed: dict[str, list[str]] = {}
    for cell in coverage["need_cells"]:
        for iid in cell.get("item_ids") or []:
            listed.setdefault(iid, []).append(cell["id"])
    for iid, item in items.items():
        assert listed.get(iid) == [item["identity"]["seed_cell"]]


def test_p0_seed_1_grounding_stabilize() -> None:
    _vocab, library, coverage = _load()
    item = next(i for i in library["items"] if i["identity"]["item_id"] == SEED_1_ID)
    assert item["identity"]["seed_cell"] == SEED_1_CELL
    assert item["identity"]["type"] == "sensory_grounding"
    assert item["identity"]["technique_id"] == "technique.sensory_grounding"
    assert item["identity"]["status"] == "active"
    cell = next(c for c in coverage["need_cells"] if c["id"] == SEED_1_CELL)
    assert cell["status"] == "covered"
    assert cell.get("fill_status") == "sourced"
    assert cell["primary"]["type"] == "sensory_grounding"
    assert cell["item_ids"][0] == SEED_1_ID


def test_p0_seed_2_is_first_ledger_empty_cell_calm() -> None:
    _vocab, library, coverage = _load()
    item = next(i for i in library["items"] if i["identity"]["item_id"] == SEED_2_ID)
    assert item["identity"]["content_class"] == "practice"
    assert item["identity"]["family"] == "breathwork"
    assert item["identity"]["type"] == "extended_exhale"
    assert item["identity"]["seed_cell"] == SEED_2_CELL
    assert item["retrieval"]["purpose"] == ["calm"]
    assert item["retrieval"]["direction"] == ["downregulate"]
    assert "tense" in item["retrieval"]["input_state"]

    cell = next(c for c in coverage["need_cells"] if c["id"] == SEED_2_CELL)
    assert cell["status"] == "covered"
    assert cell.get("fill_status") == "sourced"
    assert cell["item_ids"][0] == SEED_2_ID
    assert item["identity"]["technique_id"] == "technique.extended_exhale"
    assert item["identity"]["status"] == "active"
    assert coverage["need_cells"][0]["id"] == SEED_2_CELL


def test_p0_seed_3_is_first_ledger_empty_cell_focus() -> None:
    _vocab, library, coverage = _load()
    item = next(i for i in library["items"] if i["identity"]["item_id"] == SEED_3_ID)
    assert item["identity"]["content_class"] == "practice"
    assert item["identity"]["family"] == "breathwork"
    assert item["identity"]["type"] == "box_breathing"
    assert item["identity"]["seed_cell"] == SEED_3_CELL
    assert "technique_id" not in item["identity"]
    assert item["retrieval"]["purpose"] == ["focus"]
    assert item["retrieval"]["direction"] == ["focus"]
    assert item["retrieval"]["input_state"] == ["scattered"]

    cell = next(c for c in coverage["need_cells"] if c["id"] == SEED_3_CELL)
    assert cell["status"] == "covered"
    assert cell.get("fill_status") == "sourced"
    assert cell["primary"]["type"] == "focused_attention"
    assert SEED_3_ID in cell["item_ids"]
    assert "meditation.focused_attention.001" in cell["item_ids"]
    fa = next(
        i
        for i in library["items"]
        if i["identity"]["item_id"] == "meditation.focused_attention.001"
    )
    assert fa["identity"]["technique_id"] == "technique.focused_attention"
    assert fa["identity"]["status"] == "active"
    assert coverage["need_cells"][1]["id"] == SEED_3_CELL


def test_p0_seed_4_is_first_ledger_empty_cell_energy() -> None:
    _vocab, library, coverage = _load()
    item = next(i for i in library["items"] if i["identity"]["item_id"] == SEED_4_ID)
    assert item["identity"]["content_class"] == "practice"
    assert item["identity"]["family"] == "breathwork"
    assert item["identity"]["type"] == "energizing_breath"
    assert item["identity"]["seed_cell"] == SEED_4_CELL
    assert "technique_id" not in item["identity"]
    assert item["retrieval"]["purpose"] == ["energy"]
    assert item["retrieval"]["direction"] == ["activate"]
    assert item["retrieval"]["input_state"] == ["low_energy"]

    cell = next(c for c in coverage["need_cells"] if c["id"] == SEED_4_CELL)
    assert cell["status"] == "covered"
    assert cell.get("fill_status") == "sourced"
    assert cell["primary"]["type"] == "mobility"
    assert SEED_4_ID in cell["item_ids"]
    assert "practice.mobility.001" in cell["item_ids"]
    mobility = next(
        i
        for i in library["items"]
        if i["identity"]["item_id"] == "practice.mobility.001"
    )
    assert mobility["identity"]["technique_id"] == "technique.mobility"
    assert mobility["identity"]["status"] == "active"
    assert coverage["need_cells"][2]["id"] == SEED_4_CELL


def test_p0_seed_5_is_first_ledger_empty_cell_clarity() -> None:
    _vocab, library, coverage = _load()
    item = next(i for i in library["items"] if i["identity"]["item_id"] == SEED_5_ID)
    assert item["identity"]["content_class"] == "practice"
    assert item["identity"]["family"] == "reflection"
    assert item["identity"]["type"] == "prompted_reflection"
    assert item["identity"]["seed_cell"] == SEED_5_CELL
    assert item["identity"]["technique_id"] == "technique.prompted_reflection"
    assert item["identity"]["status"] == "active"
    assert item["retrieval"]["purpose"] == ["clarity"]
    assert item["retrieval"]["direction"] == ["reflect"]
    assert item["retrieval"]["input_state"] == ["uncertain"]

    cell = next(c for c in coverage["need_cells"] if c["id"] == SEED_5_CELL)
    assert cell["status"] == "covered"
    assert cell.get("fill_status") == "sourced"
    assert cell["primary"]["type"] == "prompted_reflection"
    assert cell["item_ids"][0] == SEED_5_ID
    assert coverage["need_cells"][4]["id"] == SEED_5_CELL


def test_p0_seed_6_is_first_ledger_empty_cell_confidence() -> None:
    _vocab, library, coverage = _load()
    item = next(i for i in library["items"] if i["identity"]["item_id"] == SEED_6_ID)
    assert item["identity"]["content_class"] == "affirmation"
    assert "family" not in item["identity"]
    assert item["identity"]["type"] == "capability"
    assert item["identity"]["seed_cell"] == SEED_6_CELL
    assert item["retrieval"]["purpose"] == ["confidence"]
    assert item["retrieval"]["direction"] == ["open"]
    assert item["retrieval"]["input_state"] == ["uncertain"]
    assert item["payload"]["body_kind"] == "affirmation_text"

    assert item["identity"]["technique_id"] == "technique.capability"
    assert item["identity"]["status"] == "active"

    cell = next(c for c in coverage["need_cells"] if c["id"] == SEED_6_CELL)
    assert cell["status"] == "covered"
    assert cell.get("fill_status") == "sourced"
    assert cell["item_ids"][0] == SEED_6_ID
    assert coverage["need_cells"][5]["id"] == SEED_6_CELL


def test_p0_seed_7_release_cell_sourced() -> None:
    _vocab, library, coverage = _load()
    item = next(i for i in library["items"] if i["identity"]["item_id"] == SEED_7_ID)
    assert item["identity"]["content_class"] == "practice"
    assert item["identity"]["family"] == "somatic"
    assert item["identity"]["type"] == "body_release"
    assert item["identity"]["seed_cell"] == SEED_7_CELL
    assert item["retrieval"]["purpose"] == ["release"]
    assert item["retrieval"]["direction"] == ["release"]
    assert item["retrieval"]["input_state"] == ["emotionally_heavy", "stuck"]

    assert item["identity"]["technique_id"] == "technique.body_release"
    assert item["identity"]["status"] == "active"

    cell = next(c for c in coverage["need_cells"] if c["id"] == SEED_7_CELL)
    assert cell["status"] == "covered"
    assert cell.get("fill_status") == "sourced"
    assert cell["item_ids"][0] == SEED_7_ID
    assert coverage["need_cells"][6]["id"] == SEED_7_CELL


def test_p0_seed_8_rest_cell_sourced() -> None:
    _vocab, library, coverage = _load()
    item = next(i for i in library["items"] if i["identity"]["item_id"] == SEED_8_ID)
    assert item["identity"]["content_class"] == "meditation"
    assert "family" not in item["identity"]
    assert item["identity"]["type"] == "relaxation"
    assert item["identity"]["seed_cell"] == SEED_8_CELL
    assert item["retrieval"]["purpose"] == ["rest"]
    assert item["retrieval"]["direction"] == ["downregulate"]
    assert item["retrieval"]["input_state"] == ["overstimulated"]
    assert item["payload"]["body_kind"] == "script"

    assert item["identity"]["technique_id"] == "technique.relaxation"
    assert item["identity"]["status"] == "active"

    cell = next(c for c in coverage["need_cells"] if c["id"] == SEED_8_CELL)
    assert cell["status"] == "covered"
    assert cell.get("fill_status") == "sourced"
    assert cell["item_ids"][0] == SEED_8_ID
    assert coverage["need_cells"][7]["id"] == SEED_8_CELL


def test_p0_seed_9_sleep_prepare_cell_sourced() -> None:
    _vocab, library, coverage = _load()
    item = next(i for i in library["items"] if i["identity"]["item_id"] == SEED_9_ID)
    assert item["identity"]["content_class"] == "meditation"
    assert "family" not in item["identity"]
    assert item["identity"]["type"] == "sleep"
    assert item["identity"]["seed_cell"] == SEED_9_CELL
    assert item["retrieval"]["purpose"] == ["sleep"]
    assert item["retrieval"]["direction"] == ["prepare"]
    assert item["retrieval"]["input_state"] == ["restless", "overstimulated"]
    assert item["payload"]["body_kind"] == "script"

    assert item["identity"]["technique_id"] == "technique.sleep"
    assert item["identity"]["status"] == "active"

    cell = next(c for c in coverage["need_cells"] if c["id"] == SEED_9_CELL)
    assert cell["status"] == "covered"
    assert cell.get("fill_status") == "sourced"
    assert cell["item_ids"][0] == SEED_9_ID
    assert coverage["need_cells"][8]["id"] == SEED_9_CELL

    sleep_discipline = next(
        c for c in coverage["need_cells"] if c["id"] == SEED_10_CELL
    )
    assert SEED_9_ID not in (sleep_discipline.get("item_ids") or [])


def test_p0_seed_10_sleep_discipline_cell_sourced() -> None:
    _vocab, library, coverage = _load()
    item = next(i for i in library["items"] if i["identity"]["item_id"] == SEED_10_ID)
    assert item["identity"]["content_class"] == "discipline"
    assert "family" not in item["identity"]
    assert item["identity"]["type"] == "sleep_discipline"
    assert item["identity"]["seed_cell"] == SEED_10_CELL
    assert item["retrieval"]["purpose"] == ["sleep"]
    assert item["retrieval"]["direction"] == ["prepare"]
    assert item["retrieval"]["input_state"] == ["restless"]
    assert "duration" not in item["retrieval"]
    assert "duration_unit" not in item["retrieval"]
    assert item["retrieval"]["duration_days"] == 7
    assert item["retrieval"]["frequency"] == "daily"
    assert item["retrieval"]["difficulty"] == "low"
    assert item["retrieval"]["failure_policy"] == "continue"
    assert item["retrieval"]["check_in_frequency"] == "daily"
    assert item["payload"]["body_kind"] == "commitment_rule"
    assert item["payload"]["commitment_rule"]
    assert item["payload"]["restriction"]
    assert item["payload"]["start_condition"]
    assert item["payload"]["completion_condition"]

    assert item["identity"]["technique_id"] == "technique.sleep_discipline"
    assert item["identity"]["status"] == "active"

    cell = next(c for c in coverage["need_cells"] if c["id"] == SEED_10_CELL)
    assert cell["status"] == "covered"
    assert cell.get("fill_status") == "sourced"
    assert cell["item_ids"][0] == SEED_10_ID
    assert coverage["need_cells"][9]["id"] == SEED_10_CELL
    assert cell["job"] == "period"

    sleep_prepare = next(c for c in coverage["need_cells"] if c["id"] == SEED_9_CELL)
    assert SEED_10_ID not in (sleep_prepare.get("item_ids") or [])
    assert sleep_prepare["item_ids"][0] == SEED_9_ID


def test_p0_seed_11_motivation_cell_sourced() -> None:
    _vocab, library, coverage = _load()
    item = next(i for i in library["items"] if i["identity"]["item_id"] == SEED_11_ID)
    assert item["identity"]["content_class"] == "practice"
    assert item["identity"]["family"] == "behavioral"
    assert item["identity"]["type"] == "micro_action"
    assert item["identity"]["seed_cell"] == SEED_11_CELL
    assert item["retrieval"]["purpose"] == ["motivation"]
    assert item["retrieval"]["direction"] == ["activate"]
    assert item["retrieval"]["input_state"] == ["stuck", "low_energy"]
    assert item["payload"]["body_kind"] == "instruction"

    assert item["identity"]["technique_id"] == "technique.micro_action"
    assert item["identity"]["status"] == "active"

    cell = next(c for c in coverage["need_cells"] if c["id"] == SEED_11_CELL)
    assert cell["status"] == "covered"
    assert cell.get("fill_status") == "sourced"
    assert cell["item_ids"][0] == SEED_11_ID
    assert coverage["need_cells"][10]["id"] == SEED_11_CELL


def test_p0_seed_12_emotional_awareness_cell_sourced() -> None:
    _vocab, library, coverage = _load()
    item = next(i for i in library["items"] if i["identity"]["item_id"] == SEED_12_ID)
    assert item["identity"]["content_class"] == "practice"
    assert item["identity"]["family"] == "reflection"
    assert item["identity"]["type"] == "self_check_in"
    assert item["identity"]["seed_cell"] == SEED_12_CELL
    assert item["retrieval"]["purpose"] == ["emotional_awareness"]
    assert item["retrieval"]["direction"] == ["reflect"]
    assert item["retrieval"]["input_state"] == ["emotionally_heavy"]
    assert item["payload"]["body_kind"] == "instruction"

    assert item["identity"]["technique_id"] == "technique.self_check_in"
    assert item["identity"]["status"] == "active"

    cell = next(c for c in coverage["need_cells"] if c["id"] == SEED_12_CELL)
    assert cell["status"] == "covered"
    assert cell.get("fill_status") == "sourced"
    assert cell["item_ids"][0] == SEED_12_ID
    assert coverage["need_cells"][11]["id"] == SEED_12_CELL


def test_p0_seed_13_self_connection_cell_sourced() -> None:
    _vocab, library, coverage = _load()
    item = next(i for i in library["items"] if i["identity"]["item_id"] == SEED_13_ID)
    assert item["identity"]["content_class"] == "practice"
    assert item["identity"]["family"] == "reflection"
    assert item["identity"]["type"] == "journaling"
    assert item["identity"]["seed_cell"] == SEED_13_CELL
    assert item["retrieval"]["purpose"] == ["self_connection"]
    assert item["retrieval"]["direction"] == ["reflect"]
    assert item["retrieval"]["input_state"] == ["disconnected"]
    assert item["payload"]["body_kind"] == "instruction"

    assert item["identity"]["technique_id"] == "technique.journaling"
    assert item["identity"]["status"] == "active"

    cell = next(c for c in coverage["need_cells"] if c["id"] == SEED_13_CELL)
    assert cell["status"] == "covered"
    assert cell.get("fill_status") == "sourced"
    assert cell["item_ids"][0] == SEED_13_ID
    assert coverage["need_cells"][12]["id"] == SEED_13_CELL


def test_p0_seed_14_connection_cell_sourced() -> None:
    _vocab, library, coverage = _load()
    item = next(i for i in library["items"] if i["identity"]["item_id"] == SEED_14_ID)
    assert item["identity"]["content_class"] == "practice"
    assert item["identity"]["family"] == "behavioral"
    assert item["identity"]["type"] == "connection_action"
    assert item["identity"]["seed_cell"] == SEED_14_CELL
    assert item["retrieval"]["purpose"] == ["connection"]
    assert item["retrieval"]["direction"] == ["connect"]
    assert item["retrieval"]["input_state"] == ["disconnected"]
    assert item["payload"]["body_kind"] == "instruction"

    assert item["identity"]["technique_id"] == "technique.connection_action"
    assert item["identity"]["status"] == "active"

    cell = next(c for c in coverage["need_cells"] if c["id"] == SEED_14_CELL)
    assert cell["status"] == "covered"
    assert cell.get("fill_status") == "sourced"
    assert cell["item_ids"][0] == SEED_14_ID
    assert coverage["need_cells"][13]["id"] == SEED_14_CELL


def test_p0_seed_15_creativity_cell_sourced() -> None:
    _vocab, library, coverage = _load()
    item = next(i for i in library["items"] if i["identity"]["item_id"] == SEED_15_ID)
    assert item["identity"]["content_class"] == "practice"
    assert item["identity"]["family"] == "creative"
    assert item["identity"]["type"] == "creative_prompt"
    assert item["identity"]["seed_cell"] == SEED_15_CELL
    assert item["retrieval"]["purpose"] == ["creativity"]
    assert item["retrieval"]["direction"] == ["open"]
    assert item["retrieval"]["input_state"] == ["stuck"]
    assert item["payload"]["body_kind"] == "instruction"

    assert item["identity"]["technique_id"] == "technique.creative_prompt"
    assert item["identity"]["status"] == "active"

    cell = next(c for c in coverage["need_cells"] if c["id"] == SEED_15_CELL)
    assert cell["status"] == "covered"
    assert cell.get("fill_status") == "sourced"
    assert cell["item_ids"][0] == SEED_15_ID
    assert coverage["need_cells"][14]["id"] == SEED_15_CELL


def test_p0_seed_16_decision_making_cell_sourced() -> None:
    _vocab, library, coverage = _load()
    item = next(i for i in library["items"] if i["identity"]["item_id"] == SEED_16_ID)
    assert item["identity"]["content_class"] == "practice"
    assert item["identity"]["family"] == "intention"
    assert item["identity"]["type"] == "priority_setting"
    assert item["identity"]["seed_cell"] == SEED_16_CELL
    assert item["retrieval"]["purpose"] == ["decision_making"]
    assert item["retrieval"]["direction"] == ["focus"]
    assert item["retrieval"]["input_state"] == ["uncertain"]
    assert item["payload"]["body_kind"] == "instruction"

    assert item["identity"]["technique_id"] == "technique.priority_setting"
    assert item["identity"]["status"] == "active"

    cell = next(c for c in coverage["need_cells"] if c["id"] == SEED_16_CELL)
    assert cell["status"] == "covered"
    assert cell.get("fill_status") == "sourced"
    assert cell["item_ids"][0] == SEED_16_ID
    assert coverage["need_cells"][15]["id"] == SEED_16_CELL


def test_p0_seed_17_transition_cell_sourced() -> None:
    _vocab, library, coverage = _load()
    item = next(i for i in library["items"] if i["identity"]["item_id"] == SEED_17_ID)
    assert item["identity"]["content_class"] == "practice"
    assert item["identity"]["family"] == "ritual"
    assert item["identity"]["type"] == "transition_ritual"
    assert item["identity"]["seed_cell"] == SEED_17_CELL
    assert item["retrieval"]["purpose"] == ["transition"]
    assert item["retrieval"]["direction"] == ["prepare"]
    assert item["retrieval"]["input_state"] == ["scattered"]
    assert item["payload"]["body_kind"] == "instruction"

    assert item["identity"]["technique_id"] == "technique.transition_ritual"
    assert item["identity"]["status"] == "active"

    cell = next(c for c in coverage["need_cells"] if c["id"] == SEED_17_CELL)
    assert cell["status"] == "covered"
    assert cell.get("fill_status") == "sourced"
    assert cell["item_ids"][0] == SEED_17_ID
    assert coverage["need_cells"][16]["id"] == SEED_17_CELL


def test_p0_seed_18_recovery_cell_sourced() -> None:
    _vocab, library, coverage = _load()
    item = next(i for i in library["items"] if i["identity"]["item_id"] == SEED_18_ID)
    assert item["identity"]["content_class"] == "practice"
    assert item["identity"]["family"] == "somatic"
    assert item["identity"]["type"] == "progressive_relaxation"
    assert item["identity"]["seed_cell"] == SEED_18_CELL
    assert item["retrieval"]["purpose"] == ["recovery"]
    assert item["retrieval"]["direction"] == ["recover"]
    assert item["retrieval"]["input_state"] == ["tense", "low_energy"]
    assert item["payload"]["body_kind"] == "instruction"

    assert item["identity"]["technique_id"] == "technique.progressive_relaxation"
    assert item["identity"]["status"] == "active"

    cell = next(c for c in coverage["need_cells"] if c["id"] == SEED_18_CELL)
    assert cell["status"] == "covered"
    assert cell.get("fill_status") == "sourced"
    assert cell["item_ids"][0] == SEED_18_ID
    assert coverage["need_cells"][17]["id"] == SEED_18_CELL


def test_p0_seed_19_discipline_cell_sourced() -> None:
    _vocab, library, coverage = _load()
    item = next(i for i in library["items"] if i["identity"]["item_id"] == SEED_19_ID)
    assert item["identity"]["content_class"] == "discipline"
    assert "family" not in item["identity"]
    assert item["identity"]["type"] == "routine_commitment"
    assert item["identity"]["seed_cell"] == SEED_19_CELL
    assert item["retrieval"]["purpose"] == ["discipline"]
    assert item["retrieval"]["direction"] == ["prepare"]
    assert item["retrieval"]["input_state"] == ["restless"]
    assert item["retrieval"]["duration_days"] == 7
    assert "duration" not in item["retrieval"]
    assert item["payload"]["body_kind"] == "commitment_rule"

    assert item["identity"]["technique_id"] == "technique.routine_commitment"
    assert item["identity"]["status"] == "active"

    cell = next(c for c in coverage["need_cells"] if c["id"] == SEED_19_CELL)
    assert cell["status"] == "covered"
    assert cell.get("fill_status") == "sourced"
    assert cell["item_ids"][0] == SEED_19_ID
    assert coverage["need_cells"][18]["id"] == SEED_19_CELL


def test_p0_seed_20_self_control_cell_sourced() -> None:
    _vocab, library, coverage = _load()
    item = next(i for i in library["items"] if i["identity"]["item_id"] == SEED_20_ID)
    assert item["identity"]["content_class"] == "discipline"
    assert item["identity"]["type"] == "attention_discipline"
    assert item["identity"]["seed_cell"] == SEED_20_CELL
    assert item["retrieval"]["purpose"] == ["self_control"]
    assert item["retrieval"]["direction"] == ["stabilize"]
    assert item["retrieval"]["input_state"] == ["restless"]
    assert item["payload"]["body_kind"] == "commitment_rule"

    assert item["identity"]["technique_id"] == "technique.attention_discipline"
    assert item["identity"]["status"] == "active"

    cell = next(c for c in coverage["need_cells"] if c["id"] == SEED_20_CELL)
    assert cell["status"] == "covered"
    assert cell.get("fill_status") == "sourced"
    assert cell["item_ids"][0] == SEED_20_ID
    assert coverage["need_cells"][19]["id"] == SEED_20_CELL


def test_p0_seed_21_detachment_cell_sourced_via_acceptance() -> None:
    _vocab, library, coverage = _load()
    seed = next(i for i in library["items"] if i["identity"]["item_id"] == SEED_21_ID)
    assert seed["identity"]["content_class"] == "discipline"
    assert seed["identity"]["type"] == "abstinence"
    assert seed["identity"]["seed_cell"] == SEED_21_CELL
    assert seed["retrieval"]["purpose"] == ["detachment"]
    assert seed["retrieval"]["direction"] == ["release"]
    assert seed["retrieval"]["input_state"] == ["overstimulated"]
    assert seed["payload"]["body_kind"] == "commitment_rule"

    assert seed["identity"].get("technique_id") is None
    assert seed["identity"]["status"] == "draft"

    sourced = next(i for i in library["items"] if i["identity"]["item_id"] == PROBE_21_ID)
    assert sourced["identity"]["content_class"] == "meditation"
    assert sourced["identity"]["type"] == "acceptance"
    assert sourced["identity"]["seed_cell"] == SEED_21_CELL
    assert sourced["identity"]["technique_id"] == "technique.acceptance"
    assert sourced["identity"]["status"] == "active"

    cell = next(c for c in coverage["need_cells"] if c["id"] == SEED_21_CELL)
    assert cell["status"] == "covered"
    assert cell.get("fill_status") == "sourced"
    assert cell["item_ids"][0] == SEED_21_ID
    assert PROBE_21_ID in cell["item_ids"]
    assert coverage["need_cells"][20]["id"] == SEED_21_CELL


def test_p0_seed_22_is_first_ledger_empty_cell_consistency() -> None:
    _vocab, library, coverage = _load()
    item = next(i for i in library["items"] if i["identity"]["item_id"] == SEED_22_ID)
    assert item["identity"]["content_class"] == "discipline"
    assert item["identity"]["type"] == "consistency_challenge"
    assert item["identity"]["seed_cell"] == SEED_22_CELL
    assert item["retrieval"]["purpose"] == ["consistency"]
    assert item["retrieval"]["direction"] == ["prepare"]
    assert item["retrieval"]["input_state"] == ["scattered"]
    assert item["payload"]["body_kind"] == "commitment_rule"

    cell = next(c for c in coverage["need_cells"] if c["id"] == SEED_22_CELL)
    assert cell["status"] == "seed"
    assert cell["item_ids"][0] == SEED_22_ID
    assert coverage["need_cells"][21]["id"] == SEED_22_CELL


def test_p0_seed_23_is_first_ledger_empty_cell_simplicity() -> None:
    _vocab, library, coverage = _load()
    item = next(i for i in library["items"] if i["identity"]["item_id"] == SEED_23_ID)
    assert item["identity"]["content_class"] == "discipline"
    assert item["identity"]["type"] == "reduction"
    assert item["identity"]["seed_cell"] == SEED_23_CELL
    assert item["retrieval"]["purpose"] == ["simplicity"]
    assert item["retrieval"]["direction"] == ["release"]
    assert item["retrieval"]["input_state"] == ["overstimulated"]
    assert item["payload"]["body_kind"] == "commitment_rule"

    cell = next(c for c in coverage["need_cells"] if c["id"] == SEED_23_CELL)
    assert cell["status"] == "seed"
    assert cell["item_ids"][0] == SEED_23_ID
    assert coverage["need_cells"][22]["id"] == SEED_23_CELL


def test_p0_seed_24_is_first_ledger_empty_cell_reset() -> None:
    _vocab, library, coverage = _load()
    item = next(i for i in library["items"] if i["identity"]["item_id"] == SEED_24_ID)
    assert item["identity"]["content_class"] == "practice"
    assert item["identity"]["family"] == "behavioral"
    assert item["identity"]["type"] == "digital_pause"
    assert item["identity"]["seed_cell"] == SEED_24_CELL
    assert item["retrieval"]["purpose"] == ["reset"]
    assert item["retrieval"]["direction"] == ["release"]
    assert item["retrieval"]["input_state"] == ["stuck"]
    assert item["payload"]["body_kind"] == "instruction"

    cell = next(c for c in coverage["need_cells"] if c["id"] == SEED_24_CELL)
    assert cell["status"] == "seed"
    assert cell["item_ids"][0] == SEED_24_ID
    assert coverage["need_cells"][23]["id"] == SEED_24_CELL


def test_p0_seed_25_is_first_ledger_empty_cell_presence() -> None:
    _vocab, library, coverage = _load()
    item = next(i for i in library["items"] if i["identity"]["item_id"] == SEED_25_ID)
    assert item["identity"]["content_class"] == "meditation"
    assert "family" not in item["identity"]
    assert item["identity"]["type"] == "mindfulness"
    assert item["identity"]["seed_cell"] == SEED_25_CELL
    assert item["retrieval"]["purpose"] == ["presence"]
    assert item["retrieval"]["direction"] == ["stabilize"]
    assert item["retrieval"]["input_state"] == ["scattered", "balanced"]
    assert item["payload"]["body_kind"] == "script"

    cell = next(c for c in coverage["need_cells"] if c["id"] == SEED_25_CELL)
    assert cell["status"] == "seed"
    assert cell["item_ids"][0] == SEED_25_ID
    assert coverage["need_cells"][24]["id"] == SEED_25_CELL


def test_p0_seed_26_is_first_ledger_empty_cell_habit_change() -> None:
    _vocab, library, coverage = _load()
    item = next(i for i in library["items"] if i["identity"]["item_id"] == SEED_26_ID)
    assert item["identity"]["content_class"] == "discipline"
    assert item["identity"]["type"] == "consistency_challenge"
    assert item["identity"]["seed_cell"] == SEED_26_CELL
    assert item["retrieval"]["purpose"] == ["habit_change"]
    assert item["retrieval"]["direction"] == ["prepare"]
    assert item["retrieval"]["input_state"] == ["stuck"]
    assert item["payload"]["body_kind"] == "commitment_rule"

    cell = next(c for c in coverage["need_cells"] if c["id"] == SEED_26_CELL)
    assert cell["status"] == "seed"
    assert cell["item_ids"][0] == SEED_26_ID
    assert coverage["need_cells"][25]["id"] == SEED_26_CELL

    next_empty = first_empty_p0_cell(coverage)
    assert next_empty is None


def test_p0_spine_fills_remaining_types_in_ledger_order() -> None:
    _vocab, library, coverage = _load()
    items = {item["identity"]["item_id"]: item for item in library["items"]}
    for item_id, seed_cell, content_class, type_code, family, purpose, direction in SPINE_SPECS:
        item = items[item_id]
        assert item["identity"]["content_class"] == content_class
        assert item["identity"]["type"] == type_code
        assert item["identity"]["seed_cell"] == seed_cell
        if family is None:
            assert "family" not in item["identity"]
        else:
            assert item["identity"]["family"] == family
        assert item["retrieval"]["purpose"] == purpose
        assert item["retrieval"]["direction"] == direction
        cell = next(c for c in coverage["need_cells"] if c["id"] == seed_cell)
        assert item_id in (cell.get("item_ids") or [])
        if (
            cell.get("fill_status") == "sourced"
            and cell.get("primary", {}).get("type") == type_code
        ):
            assert cell["item_ids"][0] == item_id
        else:
            assert cell["item_ids"][0] != item_id
        spine_row = next(
            r
            for r in coverage["type_spine"]
            if r["content_class"] == content_class and r["type"] == type_code
        )
        assert spine_row["item_ids"][0] == item_id
        listed_on = [
            c["id"]
            for c in coverage["need_cells"]
            if item_id in (c.get("item_ids") or [])
        ]
        assert listed_on == [seed_cell]

    assert first_empty_p0_type(coverage) is None
    p0_empty = [
        f"{r['content_class']}.{r['type']}"
        for r in coverage["type_spine"]
        if r.get("phase") == "P0" and not (r.get("item_ids") or [])
    ]
    assert p0_empty == []


def test_p1_density_one_axis_per_p0_type() -> None:
    _vocab, library, coverage = _load()
    items = {item["identity"]["item_id"]: item for item in library["items"]}
    assert first_p0_type_needing_density(coverage, library) is None
    p1_empty = [
        f"{r['content_class']}.{r['type']}"
        for r in coverage["type_spine"]
        if r.get("phase") == "P1" and not (r.get("item_ids") or [])
    ]
    assert len(p1_empty) == 42
    first = items["practice.extended_exhale.002"]
    assert first["identity"]["seed_cell"] == SEED_2_CELL
    assert first["retrieval"]["duration"] == 5
    assert first["retrieval"]["purpose"] == ["calm"]
    assert "practice.extended_exhale.002" in next(
        c for c in coverage["need_cells"] if c["id"] == SEED_2_CELL
    )["item_ids"]
    sleep = items["meditation.sleep.002"]
    assert sleep["retrieval"]["duration"] == 5
    assert sleep["retrieval"]["delivery"] == ["audio", "guided"]
    assert "sleep" not in json.dumps(sleep["payload"]).lower()
    period = items["discipline.sleep_discipline.002"]
    assert period["retrieval"]["duration_days"] == 14
    assert "duration" not in period["retrieval"]
    streak = items["discipline.consistency_challenge.003"]
    assert streak["identity"]["seed_cell"] == SEED_22_CELL
    assert streak["retrieval"]["duration_days"] == 14
    recovery = next(c for c in coverage["need_cells"] if c["id"] == SEED_18_CELL)
    assert "meditation.body_scan.002" not in (recovery.get("item_ids") or [])


def test_p1_density_en_locale_on_all_items() -> None:
    _vocab, library, coverage = _load()
    for item in library["items"]:
        en = item["payload"]["locales"].get("en")
        assert isinstance(en, dict), item["identity"]["item_id"]
        assert str(en.get("title") or "").strip()
        assert str(en.get("body") or "").strip()
        assert str(item["payload"]["locales"]["ru"].get("title") or "").strip()
        label = (item["payload"].get("presentation") or {}).get("outcome_label") or {}
        assert str(label.get("en") or "").strip(), item["identity"]["item_id"]
    sleep = next(i for i in library["items"] if i["identity"]["item_id"] == "meditation.sleep.001")
    assert "sleep" not in json.dumps(sleep["payload"]).lower()
    p1_empty = [
        r for r in coverage["type_spine"]
        if r.get("phase") == "P1" and not (r.get("item_ids") or [])
    ]
    assert len(p1_empty) == 42


def test_p1_density_context_work_vs_evening() -> None:
    _vocab, library, coverage = _load()
    items = {item["identity"]["item_id"]: item for item in library["items"]}
    assert first_p0_type_needing_context_density(coverage, library) is None
    evening = items["practice.extended_exhale.003"]
    assert evening["identity"]["seed_cell"] == SEED_2_CELL
    assert evening["retrieval"]["context"] == ["evening", "anytime"]
    assert evening["retrieval"]["duration"] == items["practice.extended_exhale.001"]["retrieval"]["duration"]
    assert evening["payload"]["locales"]["en"]["title"]
    work_sleep = items["meditation.sleep.003"]
    assert work_sleep["retrieval"]["context"] == ["work", "anytime"]
    assert "sleep" not in json.dumps(work_sleep["payload"]).lower()
    morning = items["practice.morning_ritual.003"]
    assert morning["retrieval"]["context"] == ["evening", "anytime"]
    streak = items["discipline.consistency_challenge.004"]
    assert streak["identity"]["seed_cell"] == SEED_22_CELL
    assert streak["retrieval"]["context"] == ["evening"]
    recovery = next(c for c in coverage["need_cells"] if c["id"] == SEED_18_CELL)
    assert "meditation.body_scan.003" not in (recovery.get("item_ids") or [])
    p1_empty = [
        r for r in coverage["type_spine"]
        if r.get("phase") == "P1" and not (r.get("item_ids") or [])
    ]
    assert len(p1_empty) == 42
    _vocab, _library, coverage = _load()
    recovery = next(c for c in coverage["need_cells"] if c["id"] == SEED_18_CELL)
    self_connection = next(c for c in coverage["need_cells"] if c["id"] == SEED_13_CELL)
    assert "meditation.body_scan.001" in (self_connection.get("item_ids") or [])
    assert "meditation.body_scan.001" not in (recovery.get("item_ids") or [])


def test_overlapping_state_does_not_close_other_cells() -> None:
    _vocab, _library, coverage = _load()
    calm = next(c for c in coverage["need_cells"] if c["id"] == SEED_2_CELL)
    grounding = next(c for c in coverage["need_cells"] if c["id"] == SEED_1_CELL)
    focus = next(c for c in coverage["need_cells"] if c["id"] == SEED_3_CELL)
    energy = next(c for c in coverage["need_cells"] if c["id"] == SEED_4_CELL)
    clarity = next(c for c in coverage["need_cells"] if c["id"] == SEED_5_CELL)
    motivation = next(c for c in coverage["need_cells"] if c["id"] == SEED_11_CELL)
    recovery = next(c for c in coverage["need_cells"] if c["id"] == SEED_18_CELL)
    confidence = next(c for c in coverage["need_cells"] if c["id"] == SEED_6_CELL)
    decision = next(c for c in coverage["need_cells"] if c["id"] == SEED_16_CELL)
    awareness = next(c for c in coverage["need_cells"] if c["id"] == SEED_12_CELL)
    self_connection = next(c for c in coverage["need_cells"] if c["id"] == SEED_13_CELL)
    reset = next(c for c in coverage["need_cells"] if c["id"] == SEED_24_CELL)
    sleep_prepare = next(c for c in coverage["need_cells"] if c["id"] == SEED_9_CELL)
    sleep_discipline = next(c for c in coverage["need_cells"] if c["id"] == SEED_10_CELL)
    rest = next(c for c in coverage["need_cells"] if c["id"] == SEED_8_CELL)
    detachment = next(c for c in coverage["need_cells"] if c["id"] == SEED_21_CELL)
    simplicity = next(c for c in coverage["need_cells"] if c["id"] == SEED_23_CELL)
    release = next(c for c in coverage["need_cells"] if c["id"] == SEED_7_CELL)
    connection = next(c for c in coverage["need_cells"] if c["id"] == SEED_14_CELL)
    creativity = next(c for c in coverage["need_cells"] if c["id"] == SEED_15_CELL)
    transition = next(c for c in coverage["need_cells"] if c["id"] == SEED_17_CELL)
    discipline = next(c for c in coverage["need_cells"] if c["id"] == SEED_19_CELL)
    self_control = next(c for c in coverage["need_cells"] if c["id"] == SEED_20_CELL)
    consistency = next(c for c in coverage["need_cells"] if c["id"] == SEED_22_CELL)
    presence = next(c for c in coverage["need_cells"] if c["id"] == SEED_25_CELL)
    habit_change = next(c for c in coverage["need_cells"] if c["id"] == SEED_26_CELL)
    assert SEED_1_ID not in (calm.get("item_ids") or [])
    assert SEED_2_ID not in (grounding.get("item_ids") or [])
    assert SEED_1_ID not in (focus.get("item_ids") or [])
    assert SEED_3_ID not in (grounding.get("item_ids") or [])
    assert SEED_4_ID not in (motivation.get("item_ids") or [])
    assert SEED_4_ID not in (recovery.get("item_ids") or [])
    assert SEED_5_ID not in (confidence.get("item_ids") or [])
    assert SEED_6_ID not in (clarity.get("item_ids") or [])
    assert SEED_6_ID not in (decision.get("item_ids") or [])
    assert SEED_7_ID not in (motivation.get("item_ids") or [])
    assert SEED_7_ID not in (awareness.get("item_ids") or [])
    assert SEED_7_ID not in (reset.get("item_ids") or [])
    assert SEED_8_ID not in (calm.get("item_ids") or [])
    assert SEED_8_ID not in (sleep_prepare.get("item_ids") or [])
    assert SEED_8_ID not in (detachment.get("item_ids") or [])
    assert SEED_8_ID not in (simplicity.get("item_ids") or [])
    assert SEED_9_ID not in (rest.get("item_ids") or [])
    assert SEED_9_ID not in (sleep_discipline.get("item_ids") or [])
    assert SEED_10_ID not in (sleep_prepare.get("item_ids") or [])
    assert SEED_11_ID not in (energy.get("item_ids") or [])
    assert SEED_11_ID not in (release.get("item_ids") or [])
    assert SEED_11_ID not in (recovery.get("item_ids") or [])
    assert SEED_11_ID not in (reset.get("item_ids") or [])
    assert SEED_12_ID not in (release.get("item_ids") or [])
    assert SEED_13_ID not in (grounding.get("item_ids") or [])
    assert SEED_13_ID not in (connection.get("item_ids") or [])
    assert SEED_14_ID not in (grounding.get("item_ids") or [])
    assert SEED_14_ID not in (self_connection.get("item_ids") or [])
    assert SEED_15_ID not in (release.get("item_ids") or [])
    assert SEED_15_ID not in (motivation.get("item_ids") or [])
    assert SEED_15_ID not in (reset.get("item_ids") or [])
    assert SEED_16_ID not in (clarity.get("item_ids") or [])
    assert SEED_16_ID not in (confidence.get("item_ids") or [])
    assert SEED_16_ID not in (focus.get("item_ids") or [])
    assert SEED_17_ID not in (focus.get("item_ids") or [])
    assert SEED_17_ID not in (grounding.get("item_ids") or [])
    assert SEED_17_ID not in (presence.get("item_ids") or [])
    assert SEED_17_ID not in (consistency.get("item_ids") or [])
    assert SEED_18_ID not in (grounding.get("item_ids") or [])
    assert SEED_18_ID not in (calm.get("item_ids") or [])
    assert SEED_18_ID not in (energy.get("item_ids") or [])
    assert SEED_18_ID not in (motivation.get("item_ids") or [])
    assert SEED_19_ID not in (sleep_prepare.get("item_ids") or [])
    assert SEED_19_ID not in (sleep_discipline.get("item_ids") or [])
    assert SEED_19_ID not in (self_control.get("item_ids") or [])
    assert SEED_19_ID not in (transition.get("item_ids") or [])
    assert SEED_19_ID not in (consistency.get("item_ids") or [])
    assert SEED_20_ID not in (sleep_discipline.get("item_ids") or [])
    assert SEED_20_ID not in (discipline.get("item_ids") or [])
    assert SEED_20_ID not in (grounding.get("item_ids") or [])
    assert SEED_20_ID not in (presence.get("item_ids") or [])
    assert SEED_21_ID not in (calm.get("item_ids") or [])
    assert SEED_21_ID not in (rest.get("item_ids") or [])
    assert SEED_21_ID not in (simplicity.get("item_ids") or [])
    assert SEED_21_ID not in (release.get("item_ids") or [])
    assert SEED_21_ID not in (reset.get("item_ids") or [])
    assert SEED_22_ID not in (transition.get("item_ids") or [])
    assert SEED_22_ID not in (focus.get("item_ids") or [])
    assert SEED_22_ID not in (presence.get("item_ids") or [])
    assert SEED_22_ID not in (habit_change.get("item_ids") or [])
    assert SEED_22_ID not in (discipline.get("item_ids") or [])
    assert SEED_23_ID not in (detachment.get("item_ids") or [])
    assert SEED_23_ID not in (rest.get("item_ids") or [])
    assert SEED_23_ID not in (calm.get("item_ids") or [])
    assert SEED_23_ID not in (reset.get("item_ids") or [])
    assert SEED_24_ID not in (release.get("item_ids") or [])
    assert SEED_24_ID not in (motivation.get("item_ids") or [])
    assert SEED_24_ID not in (creativity.get("item_ids") or [])
    assert SEED_24_ID not in (habit_change.get("item_ids") or [])
    assert SEED_24_ID not in (detachment.get("item_ids") or [])
    assert SEED_24_ID not in (simplicity.get("item_ids") or [])
    assert SEED_25_ID not in (focus.get("item_ids") or [])
    assert SEED_25_ID not in (grounding.get("item_ids") or [])
    assert SEED_25_ID not in (transition.get("item_ids") or [])
    assert SEED_25_ID not in (consistency.get("item_ids") or [])
    assert SEED_25_ID not in (self_control.get("item_ids") or [])
    assert SEED_26_ID not in (reset.get("item_ids") or [])
    assert SEED_26_ID not in (creativity.get("item_ids") or [])
    assert SEED_26_ID not in (motivation.get("item_ids") or [])
    assert SEED_26_ID not in (release.get("item_ids") or [])
    assert SEED_26_ID not in (consistency.get("item_ids") or [])
    assert SEED_26_ID not in (discipline.get("item_ids") or [])
    assert energy["item_ids"][0] == "practice.mobility.001"
    assert confidence["item_ids"][0] == SEED_6_ID
    assert calm["item_ids"][0] == SEED_2_ID
    assert sleep_prepare["item_ids"][0] == SEED_9_ID
    assert sleep_discipline["item_ids"][0] == SEED_10_ID
    assert motivation["item_ids"][0] == SEED_11_ID
    assert awareness["item_ids"][0] == SEED_12_ID
    assert self_connection["item_ids"][0] == SEED_13_ID
    assert connection["item_ids"][0] == SEED_14_ID
    assert creativity["item_ids"][0] == SEED_15_ID
    assert decision["item_ids"][0] == SEED_16_ID
    assert transition["item_ids"][0] == SEED_17_ID
    assert recovery["item_ids"][0] == SEED_18_ID
    assert discipline["item_ids"][0] == SEED_19_ID
    assert self_control["item_ids"][0] == SEED_20_ID
    assert detachment["item_ids"][0] == SEED_21_ID
    assert consistency["item_ids"][0] == SEED_22_ID
    assert simplicity["item_ids"][0] == SEED_23_ID
    assert reset["item_ids"][0] == SEED_24_ID
    assert presence["item_ids"][0] == SEED_25_ID
    assert habit_change["item_ids"][0] == SEED_26_ID
    assert "practice.mobility.001" in (energy.get("item_ids") or [])
    assert "meditation.focused_attention.001" in (focus.get("item_ids") or [])
    assert "meditation.body_scan.001" not in (recovery.get("item_ids") or [])
    assert "practice.evening_ritual.001" in (sleep_prepare.get("item_ids") or [])
    assert "practice.evening_ritual.001" not in (sleep_discipline.get("item_ids") or [])
    assert "meditation.acceptance.001" in (detachment.get("item_ids") or [])
    assert "meditation.acceptance.001" not in (simplicity.get("item_ids") or [])
    assert "discipline.digital_limit.001" not in (discipline.get("item_ids") or [])
    assert "practice.morning_ritual.001" not in (consistency.get("item_ids") or [])


def test_coverage_counts() -> None:
    _vocab, library, coverage = _load()
    assert coverage["counts"]["library_items"] == 133
    assert coverage["counts"]["need_cells_empty"] == 0
    assert coverage["counts"]["need_cells_seed"] == 5
    assert coverage["counts"]["need_cells_covered"] == 21
    assert library["status"] == "provisional"
    assert library["fill_frozen"] is False
    assert len(library["items"]) == 133


def test_repo_paths_exist() -> None:
    for path in (
        VOCAB_PATH,
        LIBRARY_PATH,
        COVERAGE_PATH,
        TECHNIQUE_PATH,
        LANDSCAPE_PATH,
        CRITERIA_PATH,
        SHORTLIST_PATH,
        INGEST_PATH,
        NORMALIZATION_PATH,
    ):
        assert Path(path).is_file()

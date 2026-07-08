"""P1.16 — Reaction to learning signal mapping tests."""

from __future__ import annotations

import copy

import pytest

from todayflow_backend.data.day_content_registry_loader import clear_day_content_registry_cache
from todayflow_backend.data.day_llm_prompt_template_loader import (
    clear_day_llm_prompt_template_registry_cache,
)
from todayflow_backend.data.reference_machine_loader import clear_reference_machine_cache
from todayflow_backend.services.day_model_v1_aggregator import aggregate_day_model_v1
from todayflow_backend.services.day_model_v1_content_assembler import assemble_day_content_package_v1
from todayflow_backend.services.day_model_v1_content_evaluator import (
    RECOMMENDATION_USE,
    evaluate_day_content_package_v1,
)
from todayflow_backend.services.day_model_v1_content_mapper import (
    map_day_model_interpretation_to_content_keys,
)
from todayflow_backend.services.day_model_v1_content_renderer import render_day_content_package_v1
from todayflow_backend.services.day_model_v1_content_resolver import (
    resolve_content_entries_from_mapping,
)
from todayflow_backend.services.day_model_v1_interpreter import interpret_day_model_v1
from todayflow_backend.services.day_model_v1_llm_call_gate import (
    DECISION_NO_CALL,
    decide_day_content_llm_call_v1,
)
from todayflow_backend.services.day_model_v1_surface_candidate import (
    select_day_surface_candidate_v1,
)
from todayflow_backend.services.day_model_v1_surface_candidate_audit import (
    build_day_surface_candidate_audit_v1,
)
from todayflow_backend.services.day_model_v1_surface_exposure_reaction import (
    REACTION_SOURCE_TIMEOUT,
    REACTION_SOURCE_USER,
    REACTION_TYPE_ASK_FOLLOWUP,
    REACTION_TYPE_COMPLETE,
    REACTION_TYPE_DISMISS,
    REACTION_TYPE_IGNORE,
    REACTION_TYPE_OPEN,
    REACTION_TYPE_RATE_NEGATIVE,
    REACTION_TYPE_RATE_POSITIVE,
    REACTION_TYPE_SAVE,
    REACTION_TYPE_VIEW,
    build_day_surface_exposure_v1,
    build_day_surface_reaction_v1,
)
from todayflow_backend.services.day_model_v1_surface_learning_signal import (
    CONFIDENCE_HIGH,
    CONFIDENCE_LOW,
    CONFIDENCE_LOW_MEDIUM,
    DATASET_EFFECT_KEEP,
    DATASET_EFFECT_NEEDS_EVIDENCE,
    DATASET_EFFECT_REJECT,
    DAY_SURFACE_LEARNING_SIGNAL_V1_CONTRACT,
    DAY_SURFACE_LEARNING_SIGNAL_V1_KEYS,
    EVIDENCE_TYPE_BEHAVIORAL,
    EVIDENCE_TYPE_EXPLICIT,
    EVIDENCE_TYPE_TIMEOUT,
    SIGNAL_DIRECTION_NEGATIVE,
    SIGNAL_DIRECTION_NEUTRAL,
    SIGNAL_DIRECTION_POSITIVE,
    SIGNAL_TYPE_CURIOSITY,
    SIGNAL_TYPE_EFFECTIVE,
    SIGNAL_TYPE_IGNORED,
    SIGNAL_TYPE_NEGATIVE,
    SIGNAL_TYPE_USEFUL,
    DaySurfaceLearningSignalError,
    build_day_surface_learning_signal_v1,
)

from tests.test_cross_domain_machine_validation import (
    ANCHOR_NUMEROLOGY,
    ANCHOR_PLANET,
    ANCHOR_SIGN,
    ANCHOR_TAROT,
)

REF_IDS = {
    "render_id": "render-test-001",
    "package_id": "package-test-001",
    "evaluation_id": "evaluation-test-001",
}


@pytest.fixture(autouse=True)
def _clear_caches():
    clear_reference_machine_cache()
    clear_day_content_registry_cache()
    clear_day_llm_prompt_template_registry_cache()
    yield
    clear_reference_machine_cache()
    clear_day_content_registry_cache()
    clear_day_llm_prompt_template_registry_cache()


def _audit(surface="today_hero"):
    dm = aggregate_day_model_v1(
        tarot_entity_code=ANCHOR_TAROT,
        numerology_entity_code=ANCHOR_NUMEROLOGY,
        astrology_planet_code=ANCHOR_PLANET,
        astrology_sign_code=ANCHOR_SIGN,
    )
    interpretation = interpret_day_model_v1(dm)
    mapping = map_day_model_interpretation_to_content_keys(interpretation)
    resolution = resolve_content_entries_from_mapping(mapping)
    package = assemble_day_content_package_v1(interpretation, mapping, resolution)
    evaluation = evaluate_day_content_package_v1(package)
    evaluation = copy.deepcopy(evaluation)
    evaluation["recommendation"] = RECOMMENDATION_USE
    evaluation["degraded"] = False
    evaluation["issues"] = []
    render = render_day_content_package_v1(package, evaluation)
    gate = decide_day_content_llm_call_v1(render, evaluation, surface=surface)
    assert gate["decision"] == DECISION_NO_CALL
    candidate = select_day_surface_candidate_v1(
        render,
        evaluation,
        gate,
        surface=surface,
        render_trace=REF_IDS,
    )
    return build_day_surface_candidate_audit_v1(candidate)


def _chain(reaction_type, *, surface="today_hero", source=REACTION_SOURCE_USER):
    audit = _audit(surface=surface)
    exposure = build_day_surface_exposure_v1(audit, placement="hero")
    reaction = build_day_surface_reaction_v1(
        exposure,
        audit,
        reaction_type=reaction_type,
        source=source,
    )
    return audit, exposure, reaction


def test_save_maps_to_useful_positive():
    audit, exposure, reaction = _chain(REACTION_TYPE_SAVE)
    signal = build_day_surface_learning_signal_v1(reaction, exposure, audit)
    assert signal["signal_type"] == SIGNAL_TYPE_USEFUL
    assert signal["signal_direction"] == SIGNAL_DIRECTION_POSITIVE
    assert signal["dataset_candidate_effect"] == DATASET_EFFECT_KEEP
    assert signal["signal_strength"] == 0.7


def test_complete_maps_to_effective_positive():
    audit, exposure, reaction = _chain(REACTION_TYPE_COMPLETE, surface="action_card")
    signal = build_day_surface_learning_signal_v1(reaction, exposure, audit)
    assert signal["signal_type"] == SIGNAL_TYPE_EFFECTIVE
    assert signal["signal_direction"] == SIGNAL_DIRECTION_POSITIVE
    assert signal["confidence"] == CONFIDENCE_HIGH
    assert signal["dataset_candidate_effect"] == DATASET_EFFECT_KEEP


def test_rate_positive_maps_to_useful_positive():
    audit, exposure, reaction = _chain(REACTION_TYPE_RATE_POSITIVE)
    signal = build_day_surface_learning_signal_v1(reaction, exposure, audit)
    assert signal["signal_type"] == SIGNAL_TYPE_USEFUL
    assert signal["signal_direction"] == SIGNAL_DIRECTION_POSITIVE
    assert signal["evidence_type"] == EVIDENCE_TYPE_EXPLICIT
    assert signal["dataset_candidate_effect"] == DATASET_EFFECT_KEEP


def test_dismiss_maps_to_negative():
    audit, exposure, reaction = _chain(REACTION_TYPE_DISMISS)
    signal = build_day_surface_learning_signal_v1(reaction, exposure, audit)
    assert signal["signal_type"] == SIGNAL_TYPE_NEGATIVE
    assert signal["signal_direction"] == SIGNAL_DIRECTION_NEGATIVE
    assert signal["dataset_candidate_effect"] == DATASET_EFFECT_REJECT


def test_rate_negative_maps_to_negative():
    audit, exposure, reaction = _chain(REACTION_TYPE_RATE_NEGATIVE)
    signal = build_day_surface_learning_signal_v1(reaction, exposure, audit)
    assert signal["signal_type"] == SIGNAL_TYPE_NEGATIVE
    assert signal["signal_direction"] == SIGNAL_DIRECTION_NEGATIVE
    assert signal["evidence_type"] == EVIDENCE_TYPE_EXPLICIT
    assert signal["dataset_candidate_effect"] == DATASET_EFFECT_REJECT


def test_ignore_maps_to_ignored_timeout():
    audit, exposure, reaction = _chain(REACTION_TYPE_IGNORE, source=REACTION_SOURCE_TIMEOUT)
    signal = build_day_surface_learning_signal_v1(reaction, exposure, audit)
    assert signal["signal_type"] == SIGNAL_TYPE_IGNORED
    assert signal["evidence_type"] == EVIDENCE_TYPE_TIMEOUT
    assert signal["confidence"] == CONFIDENCE_LOW_MEDIUM
    assert signal["dataset_candidate_effect"] == DATASET_EFFECT_NEEDS_EVIDENCE


def test_ask_followup_is_curiosity_not_positive():
    audit, exposure, reaction = _chain(REACTION_TYPE_ASK_FOLLOWUP)
    signal = build_day_surface_learning_signal_v1(reaction, exposure, audit)
    assert signal["signal_type"] == SIGNAL_TYPE_CURIOSITY
    assert signal["signal_direction"] == SIGNAL_DIRECTION_NEUTRAL
    assert signal["dataset_candidate_effect"] == DATASET_EFFECT_NEEDS_EVIDENCE


def test_view_has_low_confidence():
    audit, exposure, reaction = _chain(REACTION_TYPE_VIEW)
    signal = build_day_surface_learning_signal_v1(reaction, exposure, audit)
    assert signal["confidence"] == CONFIDENCE_LOW
    assert signal["evidence_type"] == EVIDENCE_TYPE_BEHAVIORAL
    assert signal["dataset_candidate_effect"] == DATASET_EFFECT_NEEDS_EVIDENCE


def test_memory_and_ranking_flags_always_false():
    audit, exposure, reaction = _chain(REACTION_TYPE_SAVE)
    signal = build_day_surface_learning_signal_v1(reaction, exposure, audit)
    assert signal["memory_update_allowed"] is False
    assert signal["ranking_update_allowed"] is False


def test_source_trace_preserved():
    audit, exposure, reaction = _chain(REACTION_TYPE_OPEN)
    signal = build_day_surface_learning_signal_v1(reaction, exposure, audit)
    assert signal["source_keys"] == audit["source_keys"]
    assert signal["selected_source"] == audit["selected_source"]
    assert signal["used_llm"] == audit["used_llm"]
    assert signal["surface"] == audit["surface"]
    assert signal["audit_id"] == audit["audit_id"]
    assert signal["exposure_id"] == exposure["exposure_id"]
    assert signal["reaction_id"] == reaction["reaction_id"]


def test_output_shape_stable():
    audit, exposure, reaction = _chain(REACTION_TYPE_SAVE)
    signal = build_day_surface_learning_signal_v1(reaction, exposure, audit)
    assert signal["contract_version"] == DAY_SURFACE_LEARNING_SIGNAL_V1_CONTRACT
    assert set(signal.keys()) == set(DAY_SURFACE_LEARNING_SIGNAL_V1_KEYS)


def test_signal_requires_reaction():
    audit = _audit()
    exposure = build_day_surface_exposure_v1(audit, placement="hero")
    fake_reaction = {
        "contract_version": "day_surface_reaction_v1",
        "reaction_id": "react-fake",
    }
    with pytest.raises(DaySurfaceLearningSignalError):
        build_day_surface_learning_signal_v1(fake_reaction, exposure, audit)

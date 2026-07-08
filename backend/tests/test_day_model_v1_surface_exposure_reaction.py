"""P1.15 — User exposure and reaction contract tests."""

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
    RECOMMENDATION_BLOCK,
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
    DAY_SURFACE_EXPOSURE_V1_CONTRACT,
    DAY_SURFACE_EXPOSURE_V1_KEYS,
    DAY_SURFACE_REACTION_V1_CONTRACT,
    DAY_SURFACE_REACTION_V1_KEYS,
    REACTION_SOURCE_TIMEOUT,
    REACTION_SOURCE_USER,
    REACTION_TYPE_COMPLETE,
    REACTION_TYPE_IGNORE,
    REACTION_TYPE_OPEN,
    REACTION_TYPE_SAVE,
    REACTION_TYPE_VIEW,
    REACTION_WEIGHTS,
    DaySurfaceExposureReactionError,
    build_day_surface_exposure_v1,
    build_day_surface_reaction_v1,
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


def _deterministic_audit(surface="today_hero"):
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


def _blocked_audit():
    package, evaluation, render = _base_blocked()
    gate = decide_day_content_llm_call_v1(render, evaluation, surface="day_guidance_card")
    assert gate["decision"] == "blocked"
    candidate = select_day_surface_candidate_v1(
        render,
        evaluation,
        gate,
        surface="day_guidance_card",
        render_trace=REF_IDS,
    )
    return build_day_surface_candidate_audit_v1(candidate)


def _base_blocked():
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
    evaluation["recommendation"] = RECOMMENDATION_BLOCK
    render = render_day_content_package_v1(package, evaluation)
    return package, evaluation, render


def test_exposure_from_valid_audit():
    audit = _deterministic_audit()
    exposure = build_day_surface_exposure_v1(audit, placement="hero")
    assert exposure["audit_id"] == audit["audit_id"]
    assert exposure["display_text_hash"] == audit["display_text_hash"]
    assert exposure["exposure_status"] == "shown"
    assert exposure["reaction_status"] == "pending"


def test_blocked_audit_cannot_be_shown():
    audit = _blocked_audit()
    with pytest.raises(DaySurfaceExposureReactionError):
        build_day_surface_exposure_v1(audit, placement="card", exposure_status="shown")


def test_hash_mismatch_invalid():
    audit = _deterministic_audit()
    broken = copy.deepcopy(audit)
    broken["display_text_hash"] = "txt-deadbeef"
    with pytest.raises(DaySurfaceExposureReactionError):
        build_day_surface_exposure_v1(broken, placement="card")


def test_reaction_requires_exposure():
    audit = _deterministic_audit()
    fake_exposure = {
        "contract_version": DAY_SURFACE_EXPOSURE_V1_CONTRACT,
        "exposure_id": "exp-fake",
        "audit_id": audit["audit_id"],
        "exposure_status": "shown",
    }
    with pytest.raises(DaySurfaceExposureReactionError):
        build_day_surface_reaction_v1(
            fake_exposure,
            audit,
            reaction_type=REACTION_TYPE_OPEN,
            source=REACTION_SOURCE_USER,
        )


def test_ignore_only_system_timeout():
    audit = _deterministic_audit()
    exposure = build_day_surface_exposure_v1(audit, placement="card")
    with pytest.raises(DaySurfaceExposureReactionError):
        build_day_surface_reaction_v1(
            exposure,
            audit,
            reaction_type=REACTION_TYPE_IGNORE,
            source=REACTION_SOURCE_USER,
        )
    reaction = build_day_surface_reaction_v1(
        exposure,
        audit,
        reaction_type=REACTION_TYPE_IGNORE,
        source=REACTION_SOURCE_TIMEOUT,
    )
    assert reaction["source"] == REACTION_SOURCE_TIMEOUT


def test_complete_only_action_surfaces():
    audit = _deterministic_audit(surface="today_hero")
    exposure = build_day_surface_exposure_v1(audit, placement="hero")
    with pytest.raises(DaySurfaceExposureReactionError):
        build_day_surface_reaction_v1(
            exposure,
            audit,
            reaction_type=REACTION_TYPE_COMPLETE,
            source=REACTION_SOURCE_USER,
        )

    action_audit = _deterministic_audit(surface="action_card")
    action_exposure = build_day_surface_exposure_v1(action_audit, placement="card")
    complete = build_day_surface_reaction_v1(
        action_exposure,
        action_audit,
        reaction_type=REACTION_TYPE_COMPLETE,
        source=REACTION_SOURCE_USER,
    )
    assert complete["reaction_type"] == REACTION_TYPE_COMPLETE


def test_reaction_weight_assigned():
    audit = _deterministic_audit()
    exposure = build_day_surface_exposure_v1(audit, placement="card")
    reaction = build_day_surface_reaction_v1(
        exposure,
        audit,
        reaction_type=REACTION_TYPE_SAVE,
        source=REACTION_SOURCE_USER,
    )
    assert reaction["reaction_weight"] == REACTION_WEIGHTS[REACTION_TYPE_SAVE]


def test_notes_reject_personal_data():
    audit = _deterministic_audit()
    exposure = build_day_surface_exposure_v1(audit, placement="card")
    with pytest.raises(DaySurfaceExposureReactionError):
        build_day_surface_reaction_v1(
            exposure,
            audit,
            reaction_type=REACTION_TYPE_OPEN,
            source=REACTION_SOURCE_USER,
            notes="user email test@example.com noted",
        )


def test_multiple_reactions_same_exposure():
    audit = _deterministic_audit()
    exposure = build_day_surface_exposure_v1(audit, placement="list")
    first = build_day_surface_reaction_v1(
        exposure,
        audit,
        reaction_type=REACTION_TYPE_VIEW,
        source=REACTION_SOURCE_USER,
    )
    second = build_day_surface_reaction_v1(
        exposure,
        audit,
        reaction_type=REACTION_TYPE_OPEN,
        source=REACTION_SOURCE_USER,
    )
    assert first["exposure_id"] == second["exposure_id"] == exposure["exposure_id"]
    assert first["reaction_id"] != second["reaction_id"]


def test_output_shape_stable():
    audit = _deterministic_audit()
    exposure = build_day_surface_exposure_v1(audit, placement="hero")
    reaction = build_day_surface_reaction_v1(
        exposure,
        audit,
        reaction_type=REACTION_TYPE_VIEW,
        source=REACTION_SOURCE_USER,
    )
    assert set(exposure.keys()) == DAY_SURFACE_EXPOSURE_V1_KEYS
    assert exposure["contract_version"] == DAY_SURFACE_EXPOSURE_V1_CONTRACT
    assert set(reaction.keys()) == DAY_SURFACE_REACTION_V1_KEYS
    assert reaction["contract_version"] == DAY_SURFACE_REACTION_V1_CONTRACT

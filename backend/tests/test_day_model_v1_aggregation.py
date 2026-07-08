"""P0.4/P0.5 — DayModel v1 aggregation contract (single-source preview per domain)."""

from __future__ import annotations

import pytest

from todayflow_backend.data.reference_machine_loader import (
    EMOTIONAL_LOAD_VALUES,
    EXPECTED_ASTROLOGY_MACHINE_COUNT,
    EXPECTED_NUMEROLOGY_MACHINE_COUNT,
    EXPECTED_TAROT_MAJOR_COUNT,
    RISK_VALUES,
    TEMPO_VALUES,
    VECTOR_AXIS_KEYS,
    ReferenceMachineNotFoundError,
    clear_reference_machine_cache,
    load_astrology_machine_contracts,
    load_numerology_machine_contracts,
    load_reference_machine_contract,
    load_tarot_major_machine_contracts,
)
from todayflow_backend.services.day_model_v1_aggregator import (
    DAY_MODEL_V1_PREVIEW_KEYS,
    PREVIEW_CONTRACT_VERSION,
    PREVIEW_MODE_ASTROLOGY_ONLY,
    PREVIEW_MODE_NUMEROLOGY_ONLY,
    PREVIEW_MODE_TAROT_ONLY,
    aggregate_day_model_v1_preview_astrology,
    aggregate_day_model_v1_preview_numerology,
    aggregate_day_model_v1_preview_tarot,
    build_day_model_v1_preview_from_record,
)


@pytest.fixture(autouse=True)
def _clear_loader_cache():
    clear_reference_machine_cache()
    yield
    clear_reference_machine_cache()


def test_load_tarot_major_machine_contracts_count():
    records = load_tarot_major_machine_contracts()
    assert len(records) == EXPECTED_TAROT_MAJOR_COUNT


def test_each_tarot_major_contract_has_four_vector_axes_in_range():
    for record in load_tarot_major_machine_contracts():
        vec = record.machine_contract.vector.as_dict()
        assert set(vec.keys()) == set(VECTOR_AXIS_KEYS)
        for key, value in vec.items():
            assert -1.0 <= value <= 1.0, f"{record.entity_code}.{key}={value}"


def test_each_tarot_major_contract_enums_and_confidence():
    for record in load_tarot_major_machine_contracts():
        mc = record.machine_contract
        assert mc.tempo in TEMPO_VALUES
        assert mc.risk in RISK_VALUES
        assert mc.emotional_load in EMOTIONAL_LOAD_VALUES
        assert 0.0 <= mc.confidence <= 1.0
        assert -1.0 <= mc.risk_modifier <= 1.0


def test_aggregator_preview_stable_shape():
    preview = aggregate_day_model_v1_preview_tarot("tarot.major.07")
    assert set(preview.keys()) == DAY_MODEL_V1_PREVIEW_KEYS
    assert preview["contract_version"] == PREVIEW_CONTRACT_VERSION
    assert preview["mode"] == PREVIEW_MODE_TAROT_ONLY
    assert preview["entity_code"] == "tarot.major.07"
    assert preview["sources"] == ["tarot.major.07"]
    assert set(preview["vector"].keys()) == set(VECTOR_AXIS_KEYS)


def test_aggregator_tarot_major_07_matches_machine_json():
    record = load_reference_machine_contract("tarot", "tarot.major.07")
    preview = build_day_model_v1_preview_from_record(record)
    mc = record.machine_contract
    assert preview["vector"] == mc.vector.as_dict()
    assert preview["tempo"] == mc.tempo
    assert preview["risk"] == mc.risk
    assert preview["risk_modifier"] == mc.risk_modifier
    assert preview["emotional_load"] == mc.emotional_load
    assert preview["confidence"] == mc.confidence


def test_unknown_entity_code_raises_not_found():
    with pytest.raises(ReferenceMachineNotFoundError) as exc:
        aggregate_day_model_v1_preview_tarot("tarot.major.99")
    assert exc.value.domain == "tarot"
    assert exc.value.entity_code == "tarot.major.99"


def test_load_reference_machine_contract_by_entity_code():
    record = load_reference_machine_contract("tarot", "tarot.major.00")
    assert record.entity_code == "tarot.major.00"
    assert record.status == "draft"
    assert record.contract_version == "reference_machine_contract_v1"


def test_load_numerology_machine_contracts_count():
    records = load_numerology_machine_contracts()
    assert len(records) == EXPECTED_NUMEROLOGY_MACHINE_COUNT


def test_each_numerology_contract_has_four_vector_axes_in_range():
    for record in load_numerology_machine_contracts():
        vec = record.machine_contract.vector.as_dict()
        assert set(vec.keys()) == set(VECTOR_AXIS_KEYS)
        for key, value in vec.items():
            assert -1.0 <= value <= 1.0, f"{record.entity_code}.{key}={value}"


def test_aggregator_numerology_personal_day_preview():
    preview = aggregate_day_model_v1_preview_numerology("numerology.personal_day.7")
    assert set(preview.keys()) == DAY_MODEL_V1_PREVIEW_KEYS
    assert preview["contract_version"] == PREVIEW_CONTRACT_VERSION
    assert preview["mode"] == PREVIEW_MODE_NUMEROLOGY_ONLY
    assert preview["entity_code"] == "numerology.personal_day.7"
    assert preview["sources"] == ["numerology.personal_day.7"]


def test_aggregator_numerology_core_7_matches_machine_json():
    record = load_reference_machine_contract("numerology", "numerology.core.7")
    preview = build_day_model_v1_preview_from_record(record)
    mc = record.machine_contract
    assert preview["mode"] == PREVIEW_MODE_NUMEROLOGY_ONLY
    assert preview["vector"] == mc.vector.as_dict()
    assert preview["tempo"] == mc.tempo
    assert preview["confidence"] == mc.confidence


def test_unknown_numerology_entity_code_raises_not_found():
    with pytest.raises(ReferenceMachineNotFoundError) as exc:
        aggregate_day_model_v1_preview_numerology("numerology.personal_day.99")
    assert exc.value.domain == "numerology"
    assert exc.value.entity_code == "numerology.personal_day.99"


def test_load_astrology_machine_contracts_count():
    records = load_astrology_machine_contracts()
    assert len(records) == EXPECTED_ASTROLOGY_MACHINE_COUNT


def test_each_astrology_atomic_contract_has_four_vector_axes_in_range():
    for record in load_astrology_machine_contracts():
        vec = record.machine_contract.vector.as_dict()
        assert set(vec.keys()) == set(VECTOR_AXIS_KEYS)
        for key, value in vec.items():
            assert -1.0 <= value <= 1.0, f"{record.entity_code}.{key}={value}"


def test_aggregator_astrology_planet_mars_preview():
    preview = aggregate_day_model_v1_preview_astrology("astrology.planet.mars")
    assert set(preview.keys()) == DAY_MODEL_V1_PREVIEW_KEYS
    assert preview["mode"] == PREVIEW_MODE_ASTROLOGY_ONLY
    assert preview["entity_code"] == "astrology.planet.mars"
    assert preview["sources"] == ["astrology.planet.mars"]


def test_aggregator_astrology_sign_aries_matches_machine_json():
    record = load_reference_machine_contract("astrology", "astrology.sign.aries")
    preview = build_day_model_v1_preview_from_record(record)
    assert preview["mode"] == PREVIEW_MODE_ASTROLOGY_ONLY
    assert preview["vector"] == record.machine_contract.vector.as_dict()

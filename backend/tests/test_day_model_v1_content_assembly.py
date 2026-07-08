"""P1.4 — Deterministic day content assembly tests."""

from __future__ import annotations

import copy

import pytest

from todayflow_backend.data.day_content_registry_loader import (
    clear_day_content_registry_cache,
    load_day_content_registry,
)
from todayflow_backend.data.reference_machine_loader import clear_reference_machine_cache
from todayflow_backend.services.day_model_v1_aggregator import aggregate_day_model_v1
from todayflow_backend.services.day_model_v1_content_assembler import (
    DAY_CONTENT_PACKAGE_V1_CONTRACT,
    DAY_CONTENT_PACKAGE_V1_KEYS,
    ENTRY_OUTPUT_FIELDS,
    assemble_day_content_package_v1,
)
from todayflow_backend.services.day_model_v1_content_mapper import (
    map_day_model_interpretation_to_content_keys,
)
from todayflow_backend.services.day_model_v1_content_resolver import (
    resolve_content_entries_from_mapping,
)
from todayflow_backend.services.day_model_v1_interpreter import interpret_day_model_v1
from tests.test_cross_domain_machine_validation import (
    ANCHOR_NUMEROLOGY,
    ANCHOR_PLANET,
    ANCHOR_SIGN,
    ANCHOR_TAROT,
    CONTRAST_ASTRO,
    CONTRAST_NUMEROLOGY,
    CONTRAST_TAROT,
)

CONTRAST_SIGN = "astrology.sign.capricorn"
REQUIRED_SLOTS = ("headline", "guidance", "risk_warning", "action_hint", "tempo_hint")


@pytest.fixture(autouse=True)
def _clear_caches():
    clear_reference_machine_cache()
    clear_day_content_registry_cache()
    yield
    clear_reference_machine_cache()
    clear_day_content_registry_cache()


def _pipeline(tarot, numerology, planet, sign):
    dm = aggregate_day_model_v1(
        tarot_entity_code=tarot,
        numerology_entity_code=numerology,
        astrology_planet_code=planet,
        astrology_sign_code=sign,
    )
    interpretation = interpret_day_model_v1(dm)
    mapping = map_day_model_interpretation_to_content_keys(interpretation)
    resolution = resolve_content_entries_from_mapping(mapping)
    package = assemble_day_content_package_v1(interpretation, mapping, resolution)
    return interpretation, mapping, resolution, package


def _collect_package_entries(package: dict) -> list[dict]:
    entries: list[dict] = []
    if package["headline"]:
        entries.append(package["headline"])
    entries.extend(package["guidance"])
    for slot in ("risk_warning", "action_hint", "tempo_hint", "reflection_hint"):
        entry = package.get(slot)
        if entry:
            entries.append(entry)
    return entries


def test_anchor_full_package():
    _, _, _, package = _pipeline(ANCHOR_TAROT, ANCHOR_NUMEROLOGY, ANCHOR_PLANET, ANCHOR_SIGN)
    assert package["degraded"] is False
    assert package["headline"]["key"].startswith("day.strategy.")
    assert len(package["guidance"]) == 3
    assert package["risk_warning"] is not None
    assert package["action_hint"] is not None
    assert package["tempo_hint"] is not None


def test_contrast_full_package():
    interpretation, mapping, _, package = _pipeline(
        CONTRAST_TAROT, CONTRAST_NUMEROLOGY, CONTRAST_ASTRO, CONTRAST_SIGN
    )
    assert package["degraded"] is False
    for slot in REQUIRED_SLOTS:
        assert package[slot] is not None or slot == "guidance"
    assert len(package["guidance"]) == 3
    if mapping["optional_slots"].get("reflection_hint"):
        assert package["reflection_hint"] is not None
    assert interpretation["strategy"] == "observe"


def test_required_slots_always_filled_for_anchor():
    _, _, _, package = _pipeline(ANCHOR_TAROT, ANCHOR_NUMEROLOGY, ANCHOR_PLANET, ANCHOR_SIGN)
    assert package["headline"] is not None
    assert len(package["guidance"]) >= 3
    assert package["risk_warning"] is not None
    assert package["action_hint"] is not None
    assert package["tempo_hint"] is not None


def test_reflection_optional_only_when_key_present():
    _, anchor_mapping, _, anchor_pkg = _pipeline(
        ANCHOR_TAROT, ANCHOR_NUMEROLOGY, ANCHOR_PLANET, ANCHOR_SIGN
    )
    _, contrast_mapping, _, contrast_pkg = _pipeline(
        CONTRAST_TAROT, CONTRAST_NUMEROLOGY, CONTRAST_ASTRO, CONTRAST_SIGN
    )
    if not anchor_mapping["optional_slots"].get("reflection_hint"):
        assert anchor_pkg["reflection_hint"] is None
    if contrast_mapping["optional_slots"].get("reflection_hint"):
        assert contrast_pkg["reflection_hint"] is not None
        assert contrast_pkg["reflection_hint"]["key"].startswith("day.reflection.")


def test_missing_required_slot_degraded_package():
    interpretation, mapping, resolution, _ = _pipeline(
        ANCHOR_TAROT, ANCHOR_NUMEROLOGY, ANCHOR_PLANET, ANCHOR_SIGN
    )
    broken_resolution = copy.deepcopy(resolution)
    risk_key = mapping["required_slots"]["risk_warning"][0]
    broken_resolution["entries_by_key"].pop(risk_key, None)
    package = assemble_day_content_package_v1(interpretation, mapping, broken_resolution)
    assert package["degraded"] is True
    assert package["risk_warning"] is None
    assert "risk_warning" in package["metadata"]["missing_slots"]


def test_entries_preserve_projected_fields():
    registry = load_day_content_registry()["keys"]
    _, _, _, package = _pipeline(ANCHOR_TAROT, ANCHOR_NUMEROLOGY, ANCHOR_PLANET, ANCHOR_SIGN)
    for entry in _collect_package_entries(package):
        assert set(entry.keys()) == set(ENTRY_OUTPUT_FIELDS)
        source = registry[entry["key"]]
        for field in ENTRY_OUTPUT_FIELDS:
            assert entry[field] == source[field]


def test_metadata_contains_interpretation_summary():
    interpretation, _, _, package = _pipeline(
        ANCHOR_TAROT, ANCHOR_NUMEROLOGY, ANCHOR_PLANET, ANCHOR_SIGN
    )
    meta = package["metadata"]
    assert meta["strategy"] == interpretation["strategy"]
    assert meta["risk_class"] == interpretation["risk_class"]
    assert meta["confidence"] == interpretation["confidence"]
    assert meta["tempo_instruction"] == interpretation["tempo_instruction"]


def test_metadata_contains_content_keys():
    _, mapping, _, package = _pipeline(ANCHOR_TAROT, ANCHOR_NUMEROLOGY, ANCHOR_PLANET, ANCHOR_SIGN)
    assert package["metadata"]["content_keys"] == mapping["content_keys"]


def test_output_shape_stable():
    _, _, _, package = _pipeline(ANCHOR_TAROT, ANCHOR_NUMEROLOGY, ANCHOR_PLANET, ANCHOR_SIGN)
    assert set(package.keys()) == DAY_CONTENT_PACKAGE_V1_KEYS
    assert package["contract_version"] == DAY_CONTENT_PACKAGE_V1_CONTRACT
    assert isinstance(package["metadata"], dict)


def test_no_generated_new_texts():
    registry = load_day_content_registry()["keys"]
    _, _, _, package = _pipeline(ANCHOR_TAROT, ANCHOR_NUMEROLOGY, ANCHOR_PLANET, ANCHOR_SIGN)
    registry_texts = {
        (entry["text_short"], entry["text_medium"])
        for entry in registry.values()
    }
    for entry in _collect_package_entries(package):
        assert (entry["text_short"], entry["text_medium"]) in registry_texts

"""P1.3 — DayModel content seed texts tests."""

from __future__ import annotations

import pytest

from todayflow_backend.data.day_content_registry_loader import (
    clear_day_content_registry_cache,
    load_day_content_registry,
)
from todayflow_backend.data.day_content_registry_validator import (
    ENTRY_VERSION,
    EXPECTED_DAY_CONTENT_KEY_COUNT,
    PROHIBITED_PHRASE_PATTERNS,
    validate_day_content_registry_payload,
)
from todayflow_backend.data.reference_machine_loader import clear_reference_machine_cache
from todayflow_backend.services.day_model_v1_aggregator import aggregate_day_model_v1
from todayflow_backend.services.day_model_v1_content_mapper import (
    map_day_model_interpretation_to_content_keys,
)
from todayflow_backend.services.day_model_v1_content_resolver import (
    DAY_MODEL_CONTENT_RESOLUTION_V1_KEYS,
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
    return interpretation, mapping, resolution


@pytest.fixture
def registry():
    return load_day_content_registry()


def test_all_keys_have_texts(registry):
    assert len(registry["keys"]) == EXPECTED_DAY_CONTENT_KEY_COUNT
    for key, entry in registry["keys"].items():
        assert entry["key"] == key
        assert entry["text_short"].strip()
        assert entry["text_medium"].strip()


def test_all_text_short_within_max_chars(registry):
    for key, entry in registry["keys"].items():
        assert len(entry["text_short"]) <= entry["max_chars"], key


def test_no_empty_text_short(registry):
    for key, entry in registry["keys"].items():
        assert entry["text_short"].strip(), key


def test_no_prohibited_phrases(registry):
    for key, entry in registry["keys"].items():
        for field in ("text_short", "text_medium"):
            text = entry[field]
            for pattern in PROHIBITED_PHRASE_PATTERNS:
                assert not pattern.search(text), f"{key}.{field}: {pattern.pattern}"


def test_all_slots_valid(registry):
    valid = {"headline", "guidance", "risk_warning", "action_hint", "reflection_hint", "tempo_hint"}
    for key, entry in registry["keys"].items():
        assert entry["slot"] in valid, key


def test_all_statuses_draft(registry):
    for key, entry in registry["keys"].items():
        assert entry["status"] == "draft", key


def test_all_versions(registry):
    for key, entry in registry["keys"].items():
        assert entry["version"] == ENTRY_VERSION, key


def test_validator_passes_on_registry(registry):
    assert validate_day_content_registry_payload(registry) == []


def test_mapping_finds_real_content_entries(registry):
    _, mapping, resolution = _pipeline(ANCHOR_TAROT, ANCHOR_NUMEROLOGY, ANCHOR_PLANET, ANCHOR_SIGN)
    assert mapping["missing_keys"] == []
    assert resolution["missing_keys"] == []
    slot_keys: set[str] = set()
    for keys in mapping["required_slots"].values():
        slot_keys.update(keys)
    for keys in mapping.get("optional_slots", {}).values():
        slot_keys.update(keys)
    for content_key in slot_keys:
        assert content_key in resolution["entries_by_key"]
        assert resolution["entries_by_key"][content_key]["text_short"]


def test_anchor_full_content_set():
    _, mapping, resolution = _pipeline(ANCHOR_TAROT, ANCHOR_NUMEROLOGY, ANCHOR_PLANET, ANCHOR_SIGN)
    assert mapping["degraded"] is False
    for slot in REQUIRED_SLOTS:
        assert slot in resolution["entries_by_slot"]
        assert len(resolution["entries_by_slot"][slot]) >= 1
        for entry in resolution["entries_by_slot"][slot]:
            assert entry["text_short"].strip()


def test_contrast_full_content_set():
    _, mapping, resolution = _pipeline(
        CONTRAST_TAROT, CONTRAST_NUMEROLOGY, CONTRAST_ASTRO, CONTRAST_SIGN
    )
    assert mapping["degraded"] is False
    for slot in REQUIRED_SLOTS:
        assert slot in resolution["entries_by_slot"]
    if mapping["optional_slots"].get("reflection_hint"):
        assert "reflection_hint" in resolution["entries_by_slot"]


def test_resolution_output_shape():
    _, _, resolution = _pipeline(ANCHOR_TAROT, ANCHOR_NUMEROLOGY, ANCHOR_PLANET, ANCHOR_SIGN)
    assert set(resolution.keys()) == DAY_MODEL_CONTENT_RESOLUTION_V1_KEYS


def test_anchor_contrast_resolved_key_sets_differ():
    _, _, anchor = _pipeline(ANCHOR_TAROT, ANCHOR_NUMEROLOGY, ANCHOR_PLANET, ANCHOR_SIGN)
    _, _, contrast = _pipeline(CONTRAST_TAROT, CONTRAST_NUMEROLOGY, CONTRAST_ASTRO, CONTRAST_SIGN)
    assert set(anchor["entries_by_key"]) != set(contrast["entries_by_key"])

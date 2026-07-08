"""P1.6 — Deterministic day content renderer tests."""

from __future__ import annotations

import copy

import pytest

from todayflow_backend.data.day_content_registry_loader import clear_day_content_registry_cache
from todayflow_backend.data.reference_machine_loader import clear_reference_machine_cache
from todayflow_backend.services.day_model_v1_aggregator import aggregate_day_model_v1
from todayflow_backend.services.day_model_v1_content_assembler import (
    ENTRY_OUTPUT_FIELDS,
    assemble_day_content_package_v1,
)
from todayflow_backend.services.day_model_v1_content_evaluator import (
    RECOMMENDATION_BLOCK,
    RECOMMENDATION_USE,
    RECOMMENDATION_USE_WITH_CAUTION,
    evaluate_day_content_package_v1,
)
from todayflow_backend.services.day_model_v1_content_mapper import (
    map_day_model_interpretation_to_content_keys,
)
from todayflow_backend.services.day_model_v1_content_renderer import (
    DAY_CONTENT_RENDER_V1_CONTRACT,
    DAY_CONTENT_RENDER_V1_KEYS,
    RENDER_BLOCK_REASON,
    REQUIRED_RENDER_SURFACES,
    render_day_content_package_v1,
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
    evaluation = evaluate_day_content_package_v1(package)
    render = render_day_content_package_v1(package, evaluation)
    return package, evaluation, render


def _surface_entries(render, surface_id):
    return render["surfaces"][surface_id]["entries"]


def test_anchor_renderable_surfaces():
    _, _, render = _pipeline(ANCHOR_TAROT, ANCHOR_NUMEROLOGY, ANCHOR_PLANET, ANCHOR_SIGN)
    assert render["renderable"] is True
    assert render["mode"] == "use"
    assert render["degraded"] is False
    for surface in REQUIRED_RENDER_SURFACES:
        assert surface in render["surfaces"]


def test_contrast_renderable_surfaces():
    package, _, render = _pipeline(
        CONTRAST_TAROT, CONTRAST_NUMEROLOGY, CONTRAST_ASTRO, CONTRAST_SIGN
    )
    assert render["renderable"] is True
    assert render["mode"] == "use"
    if package.get("reflection_hint"):
        assert "reflection_card" in render["surfaces"]


def test_use_with_caution_renderable_degraded():
    package, evaluation, _ = _pipeline(ANCHOR_TAROT, ANCHOR_NUMEROLOGY, ANCHOR_PLANET, ANCHOR_SIGN)
    evaluation = copy.deepcopy(evaluation)
    evaluation["recommendation"] = RECOMMENDATION_USE_WITH_CAUTION
    evaluation["degraded"] = True
    render = render_day_content_package_v1(package, evaluation)
    assert render["renderable"] is True
    assert render["degraded"] is True
    assert render["mode"] == "use_with_caution"
    assert all(
        render["surfaces"][surface]["high_confidence_label"] is False
        for surface in REQUIRED_RENDER_SURFACES
    )
    hero = _surface_entries(render, "today_hero")[0]
    assert hero["display_text"] == hero["text_short"]


def test_block_not_renderable():
    package, evaluation, _ = _pipeline(ANCHOR_TAROT, ANCHOR_NUMEROLOGY, ANCHOR_PLANET, ANCHOR_SIGN)
    package = copy.deepcopy(package)
    package["risk_warning"] = None
    evaluation = evaluate_day_content_package_v1(package)
    assert evaluation["recommendation"] == RECOMMENDATION_BLOCK
    render = render_day_content_package_v1(package, evaluation)
    assert render["renderable"] is False
    assert render["reason"] == RENDER_BLOCK_REASON
    assert render["surfaces"] == {}


def test_required_surfaces_filled():
    package, _, render = _pipeline(ANCHOR_TAROT, ANCHOR_NUMEROLOGY, ANCHOR_PLANET, ANCHOR_SIGN)
    for surface in REQUIRED_RENDER_SURFACES:
        entries = _surface_entries(render, surface)
        assert len(entries) >= 1
        assert entries[0]["display_text"]
    assert len(_surface_entries(render, "day_guidance_card")) == len(package["guidance"])


def test_reflection_optional():
    anchor_pkg, anchor_eval, anchor_render = _pipeline(
        ANCHOR_TAROT, ANCHOR_NUMEROLOGY, ANCHOR_PLANET, ANCHOR_SIGN
    )
    contrast_pkg, contrast_eval, contrast_render = _pipeline(
        CONTRAST_TAROT, CONTRAST_NUMEROLOGY, CONTRAST_ASTRO, CONTRAST_SIGN
    )
    if not anchor_pkg.get("reflection_hint"):
        assert "reflection_card" not in anchor_render["surfaces"]
    if contrast_pkg.get("reflection_hint"):
        assert "reflection_card" in contrast_render["surfaces"]
        assert contrast_render["surfaces"]["reflection_card"]["entries"][0]["key"].startswith(
            "day.reflection."
        )


def test_renderer_does_not_create_new_texts():
    package, evaluation, render = _pipeline(ANCHOR_TAROT, ANCHOR_NUMEROLOGY, ANCHOR_PLANET, ANCHOR_SIGN)
    allowed_texts = set()
    for entry in [package["headline"], *package["guidance"], package["risk_warning"],
                  package["action_hint"], package["tempo_hint"]]:
        allowed_texts.add(entry["text_short"])
        allowed_texts.add(entry["text_medium"])
    if package.get("reflection_hint"):
        allowed_texts.add(package["reflection_hint"]["text_short"])
        allowed_texts.add(package["reflection_hint"]["text_medium"])

    for surface in render["surfaces"].values():
        for entry in surface["entries"]:
            assert entry["display_text"] in allowed_texts


def test_renderer_does_not_change_content_entries():
    package, evaluation, render = _pipeline(ANCHOR_TAROT, ANCHOR_NUMEROLOGY, ANCHOR_PLANET, ANCHOR_SIGN)
    package_by_key = {}
    for entry in [package["headline"], *package["guidance"], package["risk_warning"],
                  package["action_hint"], package["tempo_hint"]]:
        package_by_key[entry["key"]] = entry
    for surface in render["surfaces"].values():
        for entry in surface["entries"]:
            source = package_by_key[entry["key"]]
            for field in ENTRY_OUTPUT_FIELDS:
                assert entry[field] == source[field]


def test_metadata_preserves_source_keys_and_evaluation():
    package, evaluation, render = _pipeline(ANCHOR_TAROT, ANCHOR_NUMEROLOGY, ANCHOR_PLANET, ANCHOR_SIGN)
    meta = render["metadata"]
    assert meta["content_keys"] == package["metadata"]["content_keys"]
    assert meta["evaluation"]["recommendation"] == evaluation["recommendation"]
    assert meta["evaluation"]["score"] == evaluation["score"]
    assert meta["interpretation"]["strategy"] == package["metadata"]["strategy"]


def test_output_shape_stable():
    _, _, render = _pipeline(ANCHOR_TAROT, ANCHOR_NUMEROLOGY, ANCHOR_PLANET, ANCHOR_SIGN)
    assert set(render.keys()) == DAY_CONTENT_RENDER_V1_KEYS
    assert render["contract_version"] == DAY_CONTENT_RENDER_V1_CONTRACT

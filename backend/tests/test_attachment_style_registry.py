"""Import pilot — attachment style reference registry tests."""

from __future__ import annotations

import copy

import pytest

from todayflow_backend.data.attachment_style_registry_loader import (
    ATTACHMENT_STYLE_REGISTRY_V1_CONTRACT,
    clear_attachment_style_registry_cache,
    deep_block_bias_for_style,
    get_attachment_style,
    list_attachment_styles,
    load_attachment_style_registry_v1,
)
from todayflow_backend.data.attachment_style_registry_validator import (
    validate_attachment_style_registry_v1,
)


@pytest.fixture(autouse=True)
def _clear_cache() -> None:
    clear_attachment_style_registry_cache()
    yield
    clear_attachment_style_registry_cache()


@pytest.fixture
def registry() -> dict:
    return load_attachment_style_registry_v1()


def test_registry_contract_and_four_styles(registry: dict) -> None:
    assert registry["contract_version"] == ATTACHMENT_STYLE_REGISTRY_V1_CONTRACT
    assert registry["domain"] == "psychology"
    assert registry["status"] == "active"
    styles = list_attachment_styles(registry, allowed_statuses=frozenset({"active"}))
    assert len(styles) == 4
    assert {s["code"] for s in styles} == {
        "secure",
        "anxious",
        "dismissive_avoidant",
        "fearful_avoidant",
    }


def test_source_license_present(registry: dict) -> None:
    assert str(registry["source"]["license"]).strip()


def test_deep_block_bias_normalized() -> None:
    bias = deep_block_bias_for_style("secure", "communication")
    assert bias is not None
    assert 0 < bias < 1


def test_validator_requires_license(registry: dict) -> None:
    bad = copy.deepcopy(registry)
    bad["source"]["license"] = ""
    errors = validate_attachment_style_registry_v1(bad)
    assert any("license" in e for e in errors)


def test_get_style_by_code() -> None:
    style = get_attachment_style("anxious")
    assert style["label_en"] == "Anxious-preoccupied attachment"
    assert "contact_need" in style["relationship_signals"]

"""P0.1 — today_contract_v1 assembler acceptance tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from todayflow_backend.services.today_contract_assembler_v1 import (
    DOMAIN_IDS,
    DOMAIN_LENS_SLOTS,
    TODAY_CONTRACT_V1_CONTRACT,
    assemble_today_contract_v1,
    validate_today_contract_v1,
)
from todayflow_backend.services.today_contract_fallbacks_v1 import (
    FAMILY_ACTION_FALLBACK,
    FAMILY_STATUS_FALLBACK,
    RELATIONSHIPS_ACTION_FALLBACK,
)
from todayflow_backend.services.today_contract_text_quality_v1 import is_valid_action_text

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures" / "today_contract_v1"


def _load_fixture(name: str) -> dict:
    with (FIXTURES_DIR / name).open(encoding="utf-8") as f:
        return json.load(f)


def _assemble_from_fixture(name: str) -> dict:
    data = _load_fixture(name)
    return assemble_today_contract_v1(
        spheres=data.get("spheres"),
        narrative=data.get("narrative"),
        morning_ritual=data.get("morning_ritual"),
        fusion=data.get("fusion"),
        fallback_context=data.get("fallback_context"),
    )


@pytest.mark.parametrize(
    "fixture_name",
    [
        "full_legacy_payload.json",
        "missing_family.json",
        "missing_action_inputs.json",
    ],
)
def test_validate_today_contract_v1_green_on_fixtures(fixture_name: str):
    contract = _assemble_from_fixture(fixture_name)
    errors = validate_today_contract_v1(contract)
    assert errors == []


@pytest.mark.parametrize(
    "fixture_name",
    [
        "full_legacy_payload.json",
        "missing_family.json",
        "missing_action_inputs.json",
    ],
)
def test_each_domain_lens_has_four_slots(fixture_name: str):
    contract = _assemble_from_fixture(fixture_name)
    domains = contract["domains"]
    for domain_id in DOMAIN_IDS:
        lens = domains[domain_id]
        assert set(lens.keys()) == set(DOMAIN_LENS_SLOTS)
        for slot in DOMAIN_LENS_SLOTS:
            assert lens[slot].strip()


def test_full_legacy_payload_maps_real_sources():
    data = _load_fixture("full_legacy_payload.json")
    contract = _assemble_from_fixture("full_legacy_payload.json")

    assert contract["contract_version"] == TODAY_CONTRACT_V1_CONTRACT
    assert contract["generation_id"] == "gen-full-legacy-001"
    assert "ясность в отношениях" in contract["global_context"]["period"]
    growth_low = contract["personal_growth"]["development_point"].lower()
    assert growth_low.startswith("сегодня")
    assert "тренируй" in growth_low or "полезно" in growth_low or "ясност" in growth_low

    relationships = contract["domains"]["relationships"]
    assert relationships["status"].lower().startswith("сегодня")
    rel_status_low = relationships["status"].lower()
    assert (
        "честн" in rel_status_low
        or "контакт" in rel_status_low
        or "разговор" in rel_status_low
        or "угадыван" in rel_status_low
    )
    assert relationships["opportunity"]
    assert relationships["risk"]
    assert is_valid_action_text(relationships["action"])

    money_work = contract["domains"]["money_work"]
    assert "завершен" in money_work["status"].lower() or "линии" in money_work["status"].lower()
    assert "трат" in money_work["status"].lower() or "пауз" in money_work["status"].lower()
    assert money_work["opportunity"]
    assert money_work["risk"]
    assert money_work["action"]

    family = contract["domains"]["family"]
    assert "поддержк" in family["status"].lower() or "семь" in family["status"].lower()
    assert "семь" in family["opportunity"].lower() or "поддержк" in family["opportunity"].lower()
    assert family["action"]

    assert contract["primary_action"] == relationships["action"]
    assert contract["progress"] == data["fallback_context"]["progress"]


def test_missing_family_uses_fallback_not_love_alias():
    contract = _assemble_from_fixture("missing_family.json")
    family = contract["domains"]["family"]
    love_status = contract["domains"]["relationships"]["status"]

    assert family["status"].lower().startswith("сегодня")
    assert "дома" in family["status"].lower() or "семье" in family["status"].lower()
    assert family["status"] != love_status
    assert family["action"]
    assert "семь" in family["opportunity"].lower() or "поддержк" in family["opportunity"].lower()


def test_missing_action_inputs_synthesizes_or_fallback_actions():
    contract = _assemble_from_fixture("missing_action_inputs.json")

    for domain_id in DOMAIN_IDS:
        action = contract["domains"][domain_id]["action"]
        assert action.strip()

    relationships = contract["domains"]["relationships"]
    assert "честн" in relationships["action"].lower() or relationships["action"] == RELATIONSHIPS_ACTION_FALLBACK

    family = contract["domains"]["family"]
    assert "поддержк" in family["action"].lower() or family["action"] == FAMILY_ACTION_FALLBACK

    assert contract["primary_action"].strip()


def test_output_has_no_legacy_keys():
    contract = _assemble_from_fixture("full_legacy_payload.json")
    serialized = json.dumps(contract, ensure_ascii=False).lower()
    for forbidden in ("todayheadline", "todaydetail", '"insight"', '"watch"', '"reason"', '"spheres"'):
        assert forbidden not in serialized

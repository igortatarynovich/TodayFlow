"""P0.1.1 — Today contract text quality gate tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from todayflow_backend.services.today_contract_assembler_v1 import (
    assemble_today_contract_v1,
    validate_today_contract_v1,
)
from todayflow_backend.services.today_contract_text_quality_v1 import (
    is_headline_label,
    is_profile_trait_text,
    is_valid_action_text,
    normalize_action,
    normalize_domain_status,
    separate_growth_from_period,
)

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures" / "today_contract_v1"


def _load_fixture(name: str) -> dict:
    with (FIXTURES_DIR / name).open(encoding="utf-8") as f:
        return json.load(f)


def test_profile_trait_detection():
    assert is_profile_trait_text("Игорь отлично проявляет себя в профессиях связанных с коммуникацией.")
    assert is_profile_trait_text(
        "В семье Игорь стремится к гармонии и пониманию. Он заботится о близких и ценит тёплую атмосферу."
    )
    assert not is_profile_trait_text("Сегодня в работе важно не распыляться.")


def test_growth_not_duplicates_period():
    period = "Проживать день через устойчивость и последовательность."
    growth = separate_growth_from_period(
        period,
        "Проживать день через устойчивость и последовательность.",
        "Тренируй способность не ускоряться только из тревоги.",
    )
    assert growth.lower().startswith("тренируй")
    assert growth != period


def test_observation_growth_leak_rejected():
    data = _load_fixture("observation_growth_leak.json")
    contract = assemble_today_contract_v1(
        spheres=data.get("spheres"),
        narrative=data.get("narrative"),
        morning_ritual=data.get("morning_ritual"),
        fusion=data.get("fusion"),
        fallback_context=data.get("fallback_context"),
    )
    errors = validate_today_contract_v1(contract)
    assert errors == []

    growth = contract["personal_growth"]["development_point"].lower()
    assert "сон" not in growth
    assert "эмоциональный фон" not in growth
    assert "энергия" not in growth
    assert growth.startswith("сегодня")


def test_family_profile_leak_fixture_navigation_copy():
    data = _load_fixture("family_profile_leak.json")
    contract = assemble_today_contract_v1(
        spheres=data.get("spheres"),
        narrative=data.get("narrative"),
        morning_ritual=data.get("morning_ritual"),
        fusion=data.get("fusion"),
        fallback_context=data.get("fallback_context"),
    )
    errors = validate_today_contract_v1(contract)
    assert errors == []

    family = contract["domains"]["family"]
    status_low = family["status"].lower()
    assert "игорь" not in status_low
    assert "стремится" not in status_low
    assert "заботится" not in status_low
    assert "дома" in status_low or "семье" in status_low

    assert contract["personal_growth"]["development_point"] != contract["global_context"]["period"]

    rel_action = contract["domains"]["relationships"]["action"].lower()
    money_action = contract["domains"]["money_work"]["action"].lower()
    assert rel_action != money_action


def test_headline_label_not_action():
    assert is_headline_label("Тон близости и контакта")
    assert is_headline_label("Работа и решения")
    assert not is_valid_action_text("Тон близости и контакта")
    assert is_valid_action_text("Скажи прямо одну вещь, которую обычно обходишь.")


def test_literary_primary_action_and_domain_fallbacks_pass():
    from todayflow_backend.services.today_contract_fallbacks_v1 import (
        DOMAIN_FALLBACKS_V1,
        PRIMARY_ACTION_FALLBACK,
    )

    assert is_valid_action_text(PRIMARY_ACTION_FALLBACK)
    assert is_valid_action_text(
        "Если успеешь закрыть одну важную вещь до обеда, остаток дня обычно идёт легче."
    )
    assert is_valid_action_text("Имеет смысл взять одну задачу и довести до видимого результата.")
    for domain_id, fb in DOMAIN_FALLBACKS_V1.items():
        if domain_id.startswith("_"):
            continue
        assert is_valid_action_text(fb["action"]), domain_id


def test_normalize_action_rejects_headline():
    fb = "Выбери одну рабочую задачу и доведи её до видимого результата."
    assert normalize_action("Работа и решения", fb) == fb
    assert normalize_action("Дом и восстановление", fb) == fb


def test_profile_trait_leak_fixture_navigation_copy():
    data = _load_fixture("profile_trait_leak.json")
    contract = assemble_today_contract_v1(
        spheres=data.get("spheres"),
        narrative=data.get("narrative"),
        morning_ritual=data.get("morning_ritual"),
        fusion=data.get("fusion"),
        fallback_context=data.get("fallback_context"),
    )
    errors = validate_today_contract_v1(contract)
    assert errors == []

    money_status = contract["domains"]["money_work"]["status"].lower()
    assert "игорь" not in money_status
    assert "проявляет" not in money_status
    assert money_status.startswith("сегодня") or "сегодня" in money_status

    family = contract["domains"]["family"]
    assert family["status"] != family["opportunity"]
    assert family["opportunity"] != family["risk"]
    assert family["risk"] != family["action"]

    for domain_id in ("relationships", "money_work", "family"):
        action = contract["domains"][domain_id]["action"]
        assert is_valid_action_text(action)


def test_status_frames_with_today_prefix():
    out = normalize_domain_status(
        "money_work",
        "не распыляться и держать один понятный вектор",
        "fallback",
    )
    assert out.lower().startswith("сегодня в работе")

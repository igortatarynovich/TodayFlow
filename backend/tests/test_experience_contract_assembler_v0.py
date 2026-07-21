"""Unit tests for experience_contract_assembler_v0."""

from __future__ import annotations

import pytest

from todayflow_backend.services.experience_contract_assembler_v0 import (
    EXPERIENCE_ALLOWLISTS,
    EXPERIENCE_CONTRACT_VERSION,
    assemble_experience_contract,
    assemble_experience_slice,
    fingerprint_experience_contract,
    project_experience_slice,
)


def _fixture_snapshot(**overrides):
    base = {
        "snapshot_id": 42,
        "profile_hash": "abc123hash",
        "profile_version": "7",
        "is_ready": True,
        "missing_fields": [],
        "person": {"display_name": "Igor"},
        "astro": {"sun_sign": "Virgo"},
        "numerology": {"life_path": 7},
        "baseline": {"rhythm": "steady mornings", "element_focus": "earth"},
        "living": {"summary": "Недавний фокус на работе и ясности."},
        "profile_contract_v1": {
            "identity_core": "Думает прежде чем действует",
            "decision_style": "Сначала собирает факты, потом выбирает",
            "relationship_style": "Прямо и без давления",
            "life_mission": "Строить понятные системы",
            "helps": ["тишина", "структура"],
            "strengths": ["ясность", "терпение"],
        },
    }
    base.update(overrides)
    return base


def test_assembler_is_experience_blind_same_contract_for_all():
    snap = _fixture_snapshot()
    contract = assemble_experience_contract(snap)
    assert contract["contract_version"] == EXPERIENCE_CONTRACT_VERSION
    assert contract["decision_style"] == "Сначала собирает факты, потом выбирает"
    assert contract["conflict_style"] == "Прямо и без давления"
    assert contract["communication_style"] == "Прямо и без давления"
    assert contract["motivation"] == "Строить понятные системы"
    assert contract["energy_source"] == "earth"
    assert contract["contract_fingerprint"]
    # Re-assemble is stable
    assert assemble_experience_contract(snap)["contract_fingerprint"] == contract[
        "contract_fingerprint"
    ]


def test_fingerprint_ignores_unrelated_snapshot_noise():
    a = assemble_experience_contract(_fixture_snapshot())
    b = assemble_experience_contract(
        _fixture_snapshot(
            living={
                "summary": "Недавний фокус на работе и ясности.",
                "recent_insights": [{"text": "noise that is not in contract"}],
            },
            interpretation={"identity": "should not change contract if contract fields same"},
        )
    )
    # living_summary same → fingerprint same; interpretation dump is not a contract field
    assert a["contract_fingerprint"] == b["contract_fingerprint"]
    assert fingerprint_experience_contract(a) == a["contract_fingerprint"]


def test_fingerprint_changes_when_contract_field_changes():
    a = assemble_experience_contract(_fixture_snapshot())
    b = assemble_experience_contract(
        _fixture_snapshot(
            profile_contract_v1={
                "identity_core": "Думает прежде чем действует",
                "decision_style": "Другой стиль решений",
                "relationship_style": "Прямо и без давления",
                "life_mission": "Строить понятные системы",
                "helps": ["тишина", "структура"],
                "strengths": ["ясность", "терпение"],
            }
        )
    )
    assert a["contract_fingerprint"] != b["contract_fingerprint"]


def test_allowlist_today_excludes_unlisted_future_fields():
    contract = assemble_experience_contract(_fixture_snapshot())
    contract["risk_tolerance"] = "high"  # must not leak via projector
    today = project_experience_slice(contract, experience_id="today")
    assert "risk_tolerance" not in today
    for key in today:
        if key in (
            "experience_id",
            "contract_version",
            "source_contract_fingerprint",
            "experience_slice_fingerprint",
        ):
            continue
        assert key in EXPERIENCE_ALLOWLISTS["today"]


def test_tarot_allowlist_excludes_life_path_and_display_name():
    contract = assemble_experience_contract(_fixture_snapshot())
    tarot = project_experience_slice(contract, experience_id="tarot")
    assert "life_path" not in tarot
    assert "display_name" not in tarot
    assert "decision_style" in tarot
    assert tarot["experience_id"] == "tarot"


def test_unknown_experience_raises():
    contract = assemble_experience_contract(_fixture_snapshot())
    with pytest.raises(ValueError):
        project_experience_slice(contract, experience_id="practices")


def test_shell_without_snapshot_not_generated_from_snapshot():
    shell = assemble_experience_contract(
        {
            "is_ready": False,
            "missing_fields": ["birth_date"],
            "astro": {},
            "numerology": {},
            "baseline": {},
            "living": {},
        }
    )
    assert shell["generated_from_snapshot"] is False
    assert shell["source_depth"] == "shell"
    today = assemble_experience_slice(shell, experience_id="today")
    assert today["generated_from_snapshot"] is False

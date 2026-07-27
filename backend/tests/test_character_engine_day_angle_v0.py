"""Character continuity / day angle — CE §3.1 retention bridge."""

from __future__ import annotations

from datetime import date

from todayflow_backend.services.character_engine_day_angle_v0 import (
    build_character_continuity_v0,
    select_day_character_angle_v0,
)
from todayflow_backend.services.day_context import build_day_context_v0
from todayflow_backend.services.experience_contract_assembler_v0 import (
    assemble_experience_contract,
    assemble_experience_slice,
)


def test_day_angle_stable_for_same_date():
    a = select_day_character_angle_v0(
        target_date=date(2026, 7, 27),
        identity_line="Ты строишь через систему",
        primary_tension="держать курс ↔ лёгкость",
        locale="ru",
    )
    b = select_day_character_angle_v0(
        target_date=date(2026, 7, 27),
        identity_line="Ты строишь через систему",
        primary_tension="держать курс ↔ лёгкость",
        locale="ru",
    )
    assert a["id"] == b["id"]
    assert a["hint"] == b["hint"]
    assert a["id"] in {"mind", "feelings", "will", "growth", "presence", "structure"}


def test_day_angle_can_differ_across_dates():
    ids = {
        select_day_character_angle_v0(
            target_date=date(2026, 7, d),
            identity_line="same",
            primary_tension="axis",
        )["id"]
        for d in range(1, 15)
    }
    # Across two weeks expect more than one angle in practice (hash spread).
    assert len(ids) >= 2


def test_continuity_rewrites_identity_false():
    out = build_character_continuity_v0(
        target_date=date(2026, 7, 27),
        experience_slice={
            "identity_line": "Ты запускаешь идеи и доводишь до системы.",
            "primary_tension": "строить ↔ лёгкость",
        },
        locale="ru",
    )
    assert out is not None
    assert out["rewrites_identity"] is False
    assert out["identity_line"]
    assert out["primary_tension"]
    assert out["day_angle"]
    assert "не изобретай" in out["rule"].lower() or "нового героя" in out["rule"].lower()


def test_experience_contract_includes_primary_tension_from_patterns():
    contract = assemble_experience_contract(
        {
            "snapshot_id": 1,
            "is_ready": True,
            "profile_contract_v1": {
                "identity_core": "Ты думаешь прежде чем действовать.",
                "decision_style": "Сначала факты",
                "recurring_patterns": ["Строитель спорит с желанием лёгкости."],
            },
        }
    )
    assert contract["primary_tension"] == "Строитель спорит с желанием лёгкости."
    today = assemble_experience_slice(
        {
            "snapshot_id": 1,
            "is_ready": True,
            "profile_contract_v1": {
                "identity_core": "Ты думаешь прежде чем действовать.",
                "decision_style": "Сначала факты",
                "recurring_patterns": ["Строитель спорит с желанием лёгкости."],
            },
        },
        experience_id="today",
    )
    assert today["primary_tension"] == "Строитель спорит с желанием лёгкости."


def test_day_context_includes_character_continuity_layer():
    ctx = build_day_context_v0(
        target_date=date(2026, 7, 27),
        locale="ru",
        insight_depth_tier="free",
        core_profile={
            "snapshot_id": 9,
            "is_ready": True,
            "profile_contract_v1": {
                "identity_core": "Ты редко действуешь на кураже — сначала разрешаешь себе рискнуть.",
                "decision_style": "Нужно внутреннее разрешение",
                "recurring_patterns": ["Удержание курса ↔ первый шаг без гарантий."],
            },
        },
        fusion_dump={"date": "2026-07-27"},
    )
    cont = ctx["layers"].get("character_continuity")
    assert isinstance(cont, dict)
    assert cont["contract_version"] == "character_continuity_v0"
    assert cont["rewrites_identity"] is False
    assert "кураже" in (cont.get("identity_line") or "")
    assert cont.get("primary_tension")
    assert cont.get("day_angle")

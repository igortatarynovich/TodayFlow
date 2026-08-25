"""Natal Decode Depth — gates, no dual-root, house theses stay short."""

from __future__ import annotations

from todayflow_backend.prompts.registry_v1 import get_prompt, list_prompt_ids
from todayflow_backend.services.character_engine_profile_consumption_spheres_houses_v0 import (
    build_house_person_lines_for_identity_v0,
)
from todayflow_backend.services.natal_decode_depth_v0 import (
    build_offer_payload,
    extract_identity_core_for_decode,
    generate_natal_decode_depth_v0,
    _normalize_decode,
)


def _ce_payload(*, grounded: bool = True) -> dict:
    surface = "Ты строишь жизнь через собственную систему и дистанцию."
    return {
        "natal_summary": {
            "available": True,
            "angles": {"ascendant_sign": "gemini", "midheaven_sign": "aquarius"},
            "luminaries": [
                {"name": "Sun", "sign": "aquarius", "house": 10},
                {"name": "Moon", "sign": "libra", "house": 5},
            ],
            "personal_planets": [
                {"name": "Mercury", "sign": "aquarius", "house": 9},
            ],
        },
        "diagnostics": {
            "character_engine_stage2": {
                "stage2": {
                    "status": "grounded" if grounded else "insufficient_identity_core",
                    "identity_core": {
                        "thesis_key": "builds_through_autonomy",
                        "surface_text": surface,
                        "primary_claim_id": "c1",
                    },
                }
            }
        },
    }


def test_prompt_registered() -> None:
    assert "profile.natal_decode_depth.v1" in list_prompt_ids()
    system, version = get_prompt("profile.natal_decode_depth.v1", locale="ru")
    assert "Identity Core" in system or "ядро" in system.lower()
    assert "честн" in system.lower() or "day_hooks" in system.lower() or "сейчас" in system.lower()
    assert version == "1.1.0"


def test_extract_identity_requires_grounded() -> None:
    assert extract_identity_core_for_decode(_ce_payload(grounded=True))["thesis_key"] == (
        "builds_through_autonomy"
    )
    assert extract_identity_core_for_decode(_ce_payload(grounded=False)) is None
    assert extract_identity_core_for_decode({}) is None


def test_offer_blocked_without_identity() -> None:
    offer = build_offer_payload(identity_core=None, natal_available=True)
    assert offer["can_generate"] is False
    assert offer["access"] == "blocked"


def test_offer_ready_when_ce_and_natal() -> None:
    identity = extract_identity_core_for_decode(_ce_payload())
    offer = build_offer_payload(identity_core=identity, natal_available=True)
    assert offer["can_generate"] is True
    assert offer["access"] == "offer"


def test_generate_blocked_without_identity(db_session) -> None:
    out = generate_natal_decode_depth_v0(
        db_session,
        user_id=1,
        core_profile_payload={"natal_summary": {"available": True, "luminaries": [{"name": "Sun"}]}},
    )
    assert out["status"] == "blocked"
    assert out["reason"] == "identity_core_required"
    assert out["writes_character_engine"] is False
    assert out["sot_role"] == "depth_projection"


def test_generate_blocked_without_natal(db_session) -> None:
    out = generate_natal_decode_depth_v0(
        db_session,
        user_id=1,
        core_profile_payload={
            "diagnostics": _ce_payload()["diagnostics"],
            "natal_summary": {},
        },
    )
    assert out["status"] == "blocked"
    assert out["reason"] == "natal_facts_required"
    assert out["writes_character_engine"] is False


def test_normalize_keeps_ce_anchor_and_no_ce_write() -> None:
    identity = {
        "thesis_key": "builds_through_autonomy",
        "surface_text": "Ты строишь через автономию.",
    }
    parsed = {
        "status": "grounded",
        "pattern_thesis": "Строитель с лицом любопытного",
        "sections": [
            {
                "id": "mind",
                "title": "Разум",
                "thesis": "Мышление системное и отстранённое.",
                "because_core": "Это проявление автономии через идеи.",
            }
        ],
        "day_hooks": ["Дай место спонтанному жесту"],
        "limits": "Точность ASC зависит от времени рождения.",
    }
    out = _normalize_decode(parsed, identity_core=identity, fingerprint="abc")
    assert out["status"] == "grounded"
    assert out["writes_character_engine"] is False
    assert out["sot_role"] == "depth_projection"
    assert out["identity_core"]["thesis_key"] == "builds_through_autonomy"
    assert out["sections"][0]["because_core"]


def test_house_how_is_thesis_short() -> None:
    houses = build_house_person_lines_for_identity_v0("builds_through_autonomy")
    how1 = houses["1"]["how"]
    assert "перв" in how1.lower() or "1 дом" in how1.lower()
    # Thesis length — not encyclopedia paragraph
    assert len(how1) < 220
    assert "описывает стиль" not in how1.lower()

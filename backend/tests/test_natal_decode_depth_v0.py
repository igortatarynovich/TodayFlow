"""Natal Decode Depth — gates, no dual-root, house theses stay short."""

from __future__ import annotations

import json
from contextlib import nullcontext
from unittest.mock import MagicMock

from todayflow_backend.prompts.registry_v1 import get_prompt, list_prompt_ids
from todayflow_backend.services.character_engine_profile_consumption_spheres_houses_v0 import (
    build_house_person_lines_for_identity_v0,
)
from todayflow_backend.services.natal_decode_depth_v0 import (
    PIC_F,
    PIC_K,
    build_offer_payload,
    extract_identity_core_for_decode,
    extract_k05_tension_for_decode,
    extract_primary_tension_surface,
    generate_natal_decode_depth_v0,
    resolve_natal_decode_get,
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


def test_pic_k15_producer_cites_facts() -> None:
    assert PIC_K == ("K15",)
    assert "F03" in PIC_F
    assert "F07" in PIC_F


def test_k05_tension_from_insight_nodes_not_stage3_trap() -> None:
    payload = _ce_payload()
    payload["insight_nodes_v0"] = {
        "nodes": [
            {
                "id": "n1",
                "title": "Ясность vs скорость",
                "insight": "Сила в точности, а срыв — когда торопишь вывод.",
                "grounded_on": [{"id": "g1", "label": "Солнце квадрат Марс"}],
            }
        ]
    }
    payload["diagnostics"]["character_engine_stage3"] = {
        "stage3": {
            "primary_tension": {
                "surface_text": "TRAP-BANK essay must not become Decode meaning.",
            }
        }
    }
    k05 = extract_k05_tension_for_decode(payload)
    assert k05 is not None
    assert k05["insight"].startswith("Сила в точности")
    assert "Солнце квадрат Марс" in k05["grounded_on"]
    assert extract_primary_tension_surface(payload) == k05["insight"]
    assert "TRAP-BANK" not in (extract_primary_tension_surface(payload) or "")
    trap_only = _ce_payload()
    trap_only["diagnostics"]["character_engine_stage3"] = payload["diagnostics"][
        "character_engine_stage3"
    ]
    assert extract_k05_tension_for_decode(trap_only) is None
    assert extract_primary_tension_surface(trap_only) is None


def test_get_never_calls_llm(db_session, monkeypatch) -> None:
    called = {"llm": False}

    def _boom(*_args, **_kwargs):
        called["llm"] = True
        raise AssertionError("GET must not generate Decode")

    monkeypatch.setattr(
        "todayflow_backend.services.natal_decode_depth_v0.chat_completion_text",
        _boom,
    )
    monkeypatch.setattr(
        "todayflow_backend.services.natal_decode_depth_v0.is_llm_chat_configured",
        lambda: True,
    )
    out = resolve_natal_decode_get(
        db_session,
        user_id=1,
        core_profile_payload=_ce_payload(),
    )
    assert called["llm"] is False
    assert out["can_generate"] is True
    assert out.get("status") != "grounded"


def test_generate_explains_k01_k05_via_natal_not_trap(db_session, monkeypatch) -> None:
    payload = _ce_payload()
    payload["insight_nodes_v0"] = {
        "nodes": [
            {
                "id": "n1",
                "title": "Ясность vs скорость",
                "insight": "Сила в точности, а срыв — когда торопишь вывод.",
                "grounded_on": [{"label": "Солнце квадрат Марс"}],
            }
        ]
    }
    payload["diagnostics"]["character_engine_stage3"] = {
        "stage3": {"primary_tension": {"surface_text": "TRAP-BANK essay"}}
    }
    captured: dict[str, object] = {}

    def _fake_chat(client, *, model, messages, temperature, max_tokens, json_object):
        captured["messages"] = messages
        return json.dumps(
            {
                "status": "grounded",
                "pattern_thesis": "Карта объясняет уже известное ядро через квадрат.",
                "sections": [
                    {
                        "id": "mind",
                        "title": "Разум",
                        "thesis": "Точность держится, пока не торопишь вывод.",
                        "because_core": "Это то же ядро автономии, видимое в карте.",
                    }
                ],
                "day_hooks": ["Один тихий проход"],
                "limits": "Спешка ломает систему.",
            },
            ensure_ascii=False,
        )

    monkeypatch.setattr(
        "todayflow_backend.services.natal_decode_depth_v0.is_llm_chat_configured",
        lambda: True,
    )
    monkeypatch.setattr(
        "todayflow_backend.services.natal_decode_depth_v0.get_openai_compatible_client",
        lambda model=None: MagicMock(),
    )
    monkeypatch.setattr(
        "todayflow_backend.services.natal_decode_depth_v0.resolve_complex_chat_model",
        lambda: "test-model",
    )
    monkeypatch.setattr(
        "todayflow_backend.services.natal_decode_depth_v0.chat_completion_text",
        _fake_chat,
    )
    monkeypatch.setattr(
        "todayflow_backend.services.natal_decode_depth_v0.llm_call_context",
        lambda **kwargs: nullcontext(),
    )
    monkeypatch.setattr(
        "todayflow_backend.services.natal_decode_depth_v0._attach_profile_il4_pack",
        lambda *args, **kwargs: None,
    )

    out = generate_natal_decode_depth_v0(
        db_session,
        user_id=1,
        core_profile_payload=payload,
        locale="ru",
    )
    assert out["status"] == "grounded"
    assert out["writes_character_engine"] is False
    assert out["identity_core"]["thesis_key"] == "builds_through_autonomy"
    assert out["identity_core"]["surface_text"].startswith("Ты строишь жизнь")
    user_msg = str((captured["messages"] or [])[1]["content"])  # type: ignore[index]
    assert "builds_through_autonomy" in user_msg
    assert "Сила в точности" in user_msg
    assert "Солнце квадрат Марс" in user_msg
    assert "TRAP-BANK" not in user_msg
    assert "k05_tension" in user_msg
    assert "второй логлайн" in user_msg.lower() or "не создавай второй" in user_msg

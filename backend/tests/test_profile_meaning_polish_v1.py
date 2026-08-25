"""1.3.123 Profile meaning polish — natal decode sky theses bind to IL-4 packs."""

from __future__ import annotations

import json
from contextlib import nullcontext
from pathlib import Path
from unittest.mock import MagicMock

import jsonschema

from todayflow_backend.knowledge.il2_composition_v1 import load_objects
from todayflow_backend.knowledge.library_scale_v1 import runtime_is_not_wired
from todayflow_backend.prompts.registry_v1 import get_prompt
from todayflow_backend.services.il4_surface_attach_v1 import attach_il4_expression_pack
from todayflow_backend.services.natal_decode_depth_v0 import generate_natal_decode_depth_v0
from todayflow_backend.services.profile_meaning_polish_v1 import (
    POLISH_INSTRUCTION_RU,
    augment_decode_system,
    fill_empty_decode_theses,
    reject_invalid_decode,
)

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "docs" / "schemas" / "astrology_interpretation_v1.schema.json"
OBJECTS = ROOT / "DATA" / "reference" / "astrology" / "interpretation_v1" / "objects_v1.json"
POLISH = ROOT / "docs" / "profile" / "PROFILE_MEANING_POLISH_V1.md"
TODAY_POLISH = ROOT / "docs" / "today" / "TODAY_MEANING_POLISH_V1.md"
CONSUME = ROOT / "docs" / "astrology" / "IL4_EDITORIAL_CONSUME_V1.md"
IL = ROOT / "docs" / "astrology" / "INTERPRETATION_LIBRARY_V1.md"
INVENTORY = ROOT / "docs" / "astrology" / "KNOWLEDGE_CORE_V1_SEMANTIC_INVENTORY.md"
HANDOFF = ROOT / "docs" / "astrology" / "IL1_HANDOFF.md"
TRACKER = ROOT / "docs" / "PRODUCT_EXECUTION_TRACKER.md"
MODULE = ROOT / "backend" / "src" / "todayflow_backend" / "services" / "profile_meaning_polish_v1.py"
DECODE = ROOT / "backend" / "src" / "todayflow_backend" / "services" / "natal_decode_depth_v0.py"


def _pos(body: str, sign: str, longitude: float, house: int | None = None) -> dict:
    return {
        "body": body,
        "sign": sign,
        "degree": longitude % 30,
        "longitude": longitude,
        "house": house,
    }


def _natal() -> dict:
    return {
        "positions": [
            _pos("mars", "Aries", 1.0, 1),
            _pos("saturn", "Capricorn", 271.0, 10),
            _pos("venus", "Cancer", 91.0, 4),
            _pos("rising", "Aries", 0.0),
        ],
        "houses": {f"house_{i}": {"longitude": float((i - 1) * 30)} for i in range(1, 13)},
    }


def _ce_payload() -> dict:
    return {
        "natal_summary": {
            "available": True,
            "angles": {"ascendant_sign": "aries", "midheaven_sign": "capricorn"},
            "luminaries": [{"name": "Sun", "sign": "aries", "house": 1}],
            "personal_planets": [{"name": "Mars", "sign": "aries", "house": 1}],
        },
        "profiles": {"selected_profile_id": 1, "primary_profile_id": 1},
        "diagnostics": {
            "character_engine_stage2": {
                "stage2": {
                    "status": "grounded",
                    "identity_core": {
                        "thesis_key": "builds_through_autonomy",
                        "surface_text": "Ты строишь жизнь через собственную систему и дистанцию.",
                        "primary_claim_id": "c1",
                    },
                }
            }
        },
    }


def test_profile_meaning_polish_v1(monkeypatch, db_session):
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    payload = json.loads(OBJECTS.read_text(encoding="utf-8"))
    jsonschema.validate(payload, schema)
    load_objects(OBJECTS)

    pack = attach_il4_expression_pack(surface="profile", natal=_natal())
    assert pack is not None

    system = augment_decode_system("base", pack, locale="ru")
    assert POLISH_INSTRUCTION_RU in system
    assert augment_decode_system("base", None) == "base"

    assert reject_invalid_decode({"sections": []}, pack) == "empty_decode_thesis"
    assert (
        reject_invalid_decode({"sections": [{"id": "mind", "thesis": ""}]}, pack)
        == "empty_decode_thesis"
    )
    assert (
        reject_invalid_decode({"sections": [{"id": "mind", "thesis": "ok"}]}, pack) is None
    )
    assert reject_invalid_decode({"sections": []}, None) is None

    filled = fill_empty_decode_theses(
        {"pattern_thesis": "", "sections": [{"thesis": "", "because_core": "ядро"}]},
        pack,
    )
    assert filled["pattern_thesis"] == pack["lines"][0]["text"]
    assert filled["sections"][0]["thesis"] == pack["lines"][0]["text"]

    kept = fill_empty_decode_theses(
        {"pattern_thesis": "уже сказано", "sections": [{"thesis": "уже тезис"}]},
        pack,
    )
    assert kept["pattern_thesis"] == "уже сказано"
    assert kept["sections"][0]["thesis"] == "уже тезис"

    src = MODULE.read_text(encoding="utf-8")
    assert "calc_il_wire_v1" not in src
    assert "openai" not in src.lower()
    assert "identity_core" in src.lower() or "Character Engine" in src

    src_root = ROOT / "backend" / "src" / "todayflow_backend"
    assert runtime_is_not_wired(src_root)
    decode_src = DECODE.read_text(encoding="utf-8")
    assert "profile_meaning_polish_v1" in decode_src
    assert "il4_editorial_consume_v1" in decode_src
    assert "il4_surface_attach_v1" in decode_src

    _, prompt_version = get_prompt("profile.natal_decode_depth.v1", locale="ru")
    assert prompt_version == "1.1.0"

    captured: dict[str, object] = {}

    def _fake_chat(client, *, model, messages, temperature, max_tokens, json_object):
        captured["messages"] = messages
        return json.dumps(
            {
                "status": "grounded",
                "pattern_thesis": "Ты держишь дистанцию как рабочий инструмент.",
                "sections": [
                    {
                        "id": "will",
                        "title": "Воля",
                        "thesis": "Действие идёт напрямую, без согласования очереди.",
                        "because_core": "Это проявление автономии через действие.",
                    }
                ],
                "day_hooks": ["Проверь, не прячешься ли ты в системе"],
                "limits": "Прямой ход может обойти чужую скорость.",
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

    out = generate_natal_decode_depth_v0(
        db_session,
        user_id=1,
        core_profile_payload=_ce_payload(),
        natal_chart=_natal(),
        locale="ru",
    )
    assert out["status"] == "grounded"
    assert out["writes_character_engine"] is False
    assert out["identity_core"]["thesis_key"] == "builds_through_autonomy"
    messages = captured["messages"]
    assert isinstance(messages, list)
    system_text = str(messages[0]["content"])
    user_text = str(messages[1]["content"])
    assert POLISH_INSTRUCTION_RU in system_text
    assert "IL4_MEANING" in system_text or "IL4_MEANING" in user_text
    assert "il4_expression_pack" not in json.dumps(out, ensure_ascii=False)

    def _empty_chat(client, *, model, messages, temperature, max_tokens, json_object):
        return json.dumps({"status": "grounded", "pattern_thesis": "", "sections": []})

    monkeypatch.setattr(
        "todayflow_backend.services.natal_decode_depth_v0.chat_completion_text",
        _empty_chat,
    )
    monkeypatch.setattr(
        "todayflow_backend.services.natal_decode_depth_v0.load_cached_natal_decode",
        lambda *a, **k: None,
    )
    rejected = generate_natal_decode_depth_v0(
        db_session,
        user_id=99,
        core_profile_payload=_ce_payload(),
        natal_chart=_natal(),
        locale="ru",
    )
    assert rejected["status"] == "unavailable"
    assert str(rejected.get("reason") or "").startswith("profile_polish:")

    rules = POLISH.read_text(encoding="utf-8")
    assert "## Architecture impact" in rules
    assert "1.3.123" in rules
    assert "Public contract changed?** no" in rules
    assert "identity_core" in rules
    assert "1.3.114" in TODAY_POLISH.read_text(encoding="utf-8")
    assert "1.3.113" in CONSUME.read_text(encoding="utf-8")

    il_text = IL.read_text(encoding="utf-8")
    assert "### 6.71" in il_text
    assert "1.3.123" in il_text

    inventory = INVENTORY.read_text(encoding="utf-8")
    assert "45. Profile meaning polish" in inventory
    assert "✅ 1.3.123" in inventory
    assert "KC-C-PROFILE-POLISH" in inventory

    handoff = HANDOFF.read_text(encoding="utf-8")
    assert "1.3.123" in handoff or "Profile meaning polish" in handoff

    tracker = TRACKER.read_text(encoding="utf-8")
    assert "1.3.123" in tracker or "Profile meaning polish" in tracker

"""1.3.115 Compatibility synastry editorial IL-4 — phrases packs when charts supplied."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock

import jsonschema

from todayflow_backend.knowledge.il2_composition_v1 import load_objects
from todayflow_backend.services.compatibility_editorial import (
    PROMPT_VERSION,
    SYSTEM_PROMPT,
    generate_compatibility_editorial,
)
from todayflow_backend.services.il4_surface_attach_v1 import attach_from_chart_pair

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "docs" / "schemas" / "astrology_interpretation_v1.schema.json"
OBJECTS = ROOT / "DATA" / "reference" / "astrology" / "interpretation_v1" / "objects_v1.json"
CANON = ROOT / "docs" / "astrology" / "COMPAT_SYNASTRY_EDITORIAL_IL4_V1.md"
IL = ROOT / "docs" / "astrology" / "INTERPRETATION_LIBRARY_V1.md"
INVENTORY = ROOT / "docs" / "astrology" / "KNOWLEDGE_CORE_V1_SEMANTIC_INVENTORY.md"
EDITORIAL = ROOT / "backend" / "src" / "todayflow_backend" / "services" / "compatibility_editorial.py"
API = ROOT / "backend" / "src" / "todayflow_backend" / "api" / "compatibility.py"


def _pos(body: str, sign: str, longitude: float, house: int | None = None) -> dict:
    return {
        "body": body,
        "sign": sign,
        "degree": longitude % 30,
        "longitude": longitude,
        "house": house,
    }


def _chart() -> dict:
    return {
        "positions": [
            _pos("sun", "Aries", 1.0, 1),
            _pos("moon", "Cancer", 91.0, 4),
            _pos("mars", "Libra", 181.0, 7),
            _pos("rising", "Aries", 0.0),
        ],
        "houses": {f"house_{i}": {"longitude": float((i - 1) * 30)} for i in range(1, 13)},
    }


def test_compat_synastry_editorial_il4_v1(monkeypatch):
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    payload = json.loads(OBJECTS.read_text(encoding="utf-8"))
    jsonschema.validate(payload, schema)
    load_objects(OBJECTS)

    chart1 = _chart()
    chart2 = _chart()
    chart2["positions"][0] = _pos("sun", "Leo", 121.0, 5)
    pack = attach_from_chart_pair(chart1, chart2, surface="compatibility")
    assert pack is not None

    captured: dict[str, object] = {}

    def _fake_chat(client, *, model, messages, temperature, max_tokens, json_object):
        captured["messages"] = messages
        return json.dumps(
            {
                "mode_focus": "romantic",
                "pair_thesis": "Тест.",
                "strengths": ["Сила."],
                "tensions": ["Напряжение."],
                "next_step": "Шаг.",
            },
            ensure_ascii=False,
        )

    monkeypatch.setattr(
        "todayflow_backend.services.compatibility_editorial.is_llm_chat_configured",
        lambda: True,
    )
    monkeypatch.setattr(
        "todayflow_backend.services.compatibility_editorial.get_openai_compatible_client",
        lambda: MagicMock(),
    )
    monkeypatch.setattr(
        "todayflow_backend.services.compatibility_editorial.chat_completion_text",
        _fake_chat,
    )
    monkeypatch.setattr(
        "todayflow_backend.services.compatibility_editorial.resolve_default_chat_model",
        lambda: "test-model",
    )

    learning = MagicMock()
    learning.get_or_create_prompt_version.return_value = MagicMock(id=1)
    learning.build_user_learning_context.return_value = {}
    monkeypatch.setattr(
        "todayflow_backend.services.compatibility_editorial.get_learning_service",
        lambda: learning,
    )
    monkeypatch.setattr(
        "todayflow_backend.services.compatibility_editorial.CoreProfileSnapshot",
        MagicMock(),
    )

    db = MagicMock()
    db.query.return_value.filter.return_value.order_by.return_value.first.return_value = None
    user = MagicMock()
    user.id = 1

    editorial = generate_compatibility_editorial(
        db,
        user=user,
        relation_mode="romantic",
        payload={"overall_score": 72, "summary": "test", "deep_dive": {}},
        chart1=chart1,
        chart2=chart2,
    )
    assert editorial.pair_thesis == "Тест."
    messages = captured["messages"]
    assert isinstance(messages, list)
    system = messages[0]["content"]
    user_msg = messages[1]["content"]
    assert "IL4_MEANING" in user_msg
    assert system != SYSTEM_PROMPT
    assert "IL4_MEANING" in system or "астрологический смысл" in system

    assert PROMPT_VERSION == "compatibility-editorial-v1.1"
    assert "chart1" in API.read_text(encoding="utf-8")
    assert "attach_from_chart_pair" in EDITORIAL.read_text(encoding="utf-8")

    rules = CANON.read_text(encoding="utf-8")
    assert "1.3.115" in rules
    assert "**Версия:** 1.3.115" in IL.read_text(encoding="utf-8")
    assert "### 6.69" in IL.read_text(encoding="utf-8")
    inventory = INVENTORY.read_text(encoding="utf-8")
    assert "43. Compatibility synastry editorial IL-4" in inventory
    assert "✅ 1.3.115" in inventory

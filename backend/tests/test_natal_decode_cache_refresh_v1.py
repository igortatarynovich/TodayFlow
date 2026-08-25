"""1.3.124 Natal Decode cache refresh — ops one-shot, not a semantic pass."""

from __future__ import annotations

import json
from contextlib import nullcontext
from pathlib import Path
from unittest.mock import MagicMock

from todayflow_backend.db.models import GenerationLog, User
from todayflow_backend.knowledge.il2_composition_v1 import load_objects
from todayflow_backend.services.natal_decode_depth_v0 import (
    DECODE_VERSION,
    LAYER_KIND,
    _fingerprint,
    _inputs_for_payload,
    decode_cache_state,
    generate_natal_decode_depth_v0,
    list_latest_natal_decode_by_user,
    persisted_decode_version,
)

ROOT = Path(__file__).resolve().parents[2]
CANON = ROOT / "docs" / "profile" / "PROFILE_NATAL_DECODE_CACHE_REFRESH_V1.md"
POLISH = ROOT / "docs" / "profile" / "PROFILE_MEANING_POLISH_V1.md"
IL = ROOT / "docs" / "astrology" / "INTERPRETATION_LIBRARY_V1.md"
INVENTORY = ROOT / "docs" / "astrology" / "KNOWLEDGE_CORE_V1_SEMANTIC_INVENTORY.md"
HANDOFF = ROOT / "docs" / "astrology" / "IL1_HANDOFF.md"
TRACKER = ROOT / "docs" / "PRODUCT_EXECUTION_TRACKER.md"
SCRIPT = ROOT / "backend" / "scripts" / "natal_decode_cache_refresh_v1.py"
DECODE = ROOT / "backend" / "src" / "todayflow_backend" / "services" / "natal_decode_depth_v0.py"


def _ce_payload() -> dict:
    return {
        "natal_summary": {
            "available": True,
            "angles": {"ascendant_sign": "aries", "midheaven_sign": "capricorn"},
            "luminaries": [{"name": "Sun", "sign": "aries", "house": 1}],
            "personal_planets": [{"name": "Mars", "sign": "aries", "house": 1}],
        },
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


def _grounded_body(*, version: str, thesis: str = "cached thesis") -> dict:
    return {
        "layer": LAYER_KIND,
        "version": version,
        "status": "grounded",
        "identity_core": {
            "thesis_key": "builds_through_autonomy",
            "surface_text": "Ты строишь жизнь через собственную систему и дистанцию.",
        },
        "pattern_thesis": thesis,
        "sections": [
            {
                "id": "mind",
                "title": "Разум",
                "thesis": thesis,
                "because_core": "Это проявление автономии.",
            }
        ],
        "day_hooks": ["Пауза"],
        "writes_character_engine": False,
        "sot_role": "depth_projection",
    }


def test_decode_cache_state_stale_vs_current() -> None:
    stale = _grounded_body(version="natal_decode_depth_v0.2")
    current = _grounded_body(version=DECODE_VERSION)
    assert decode_cache_state(stale, {"decode_version": "natal_decode_depth_v0.2"}) == "stale"
    assert decode_cache_state(current, {"decode_version": DECODE_VERSION}) == "current"
    assert persisted_decode_version(stale, {}) == "natal_decode_depth_v0.2"
    assert decode_cache_state({"status": "grounded", "sections": []}, {}) == "invalid"


def test_list_latest_and_ops_force_skips_cache(monkeypatch, db_session) -> None:
    user = User(id=41, email="decode-refresh@test.local", password_hash="x")
    db_session.add(user)
    db_session.commit()

    identity, natal_pack, numerology_pack, _avail, fingerprint = _inputs_for_payload(_ce_payload(), None)
    assert identity and fingerprint
    db_session.add(
        GenerationLog(
            user_id=41,
            module="profile",
            surface=LAYER_KIND,
            status="success",
            input_payload={"fingerprint": fingerprint, "decode_version": DECODE_VERSION, "prompt_version": "1.1.0"},
            normalized_response=_grounded_body(version=DECODE_VERSION, thesis="FROM_CACHE"),
        )
    )
    db_session.commit()

    inventory = list_latest_natal_decode_by_user(db_session)
    assert any(row["user_id"] == 41 and row["state"] == "current" for row in inventory)

    cached = generate_natal_decode_depth_v0(
        db_session,
        user_id=41,
        core_profile_payload=_ce_payload(),
        force_refresh=True,
    )
    assert cached["pattern_thesis"] == "FROM_CACHE"

    captured: dict = {}

    def _chat(client, *, model, messages, temperature, max_tokens, json_object):
        captured["called"] = True
        return json.dumps(
            {
                "status": "grounded",
                "pattern_thesis": "FROM_OPS",
                "sections": [
                    {
                        "id": "mind",
                        "title": "Разум",
                        "thesis": "FROM_OPS thesis",
                        "because_core": "Это проявление автономии.",
                    }
                ],
                "day_hooks": ["Пауза"],
            }
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
        _chat,
    )
    monkeypatch.setattr(
        "todayflow_backend.services.natal_decode_depth_v0.llm_call_context",
        lambda **kwargs: nullcontext(),
    )

    refreshed = generate_natal_decode_depth_v0(
        db_session,
        user_id=41,
        core_profile_payload=_ce_payload(),
        ops_force=True,
        locale="ru",
    )
    assert captured.get("called") is True
    assert refreshed["pattern_thesis"] == "FROM_OPS"
    assert refreshed["version"] == DECODE_VERSION
    assert refreshed["writes_character_engine"] is False
    assert refreshed["identity_core"]["thesis_key"] == "builds_through_autonomy"
    assert _fingerprint(identity, natal_pack, numerology_pack) == fingerprint


def test_load_objects_honors_todayflow_data_dir(monkeypatch, tmp_path) -> None:
    src = ROOT / "DATA" / "reference" / "astrology" / "interpretation_v1" / "objects_v1.json"
    dest_root = tmp_path / "data"
    dest = dest_root / "reference" / "astrology" / "interpretation_v1"
    dest.mkdir(parents=True)
    dest.joinpath("objects_v1.json").write_bytes(src.read_bytes())
    monkeypatch.setenv("TODAYFLOW_DATA_DIR", str(dest_root))
    catalog = load_objects()
    assert "astro.object.sun" in catalog


def test_canon_lock_1_3_124() -> None:
    rules = CANON.read_text(encoding="utf-8")
    assert "## Architecture impact" in rules
    assert "1.3.124" in rules
    assert "ops_force" in rules
    assert "GET never rebuilds" in rules
    assert "TODAYFLOW_DATA_DIR" in rules
    assert "Public contract changed?** no" in rules
    assert "1.3.123" in POLISH.read_text(encoding="utf-8")
    assert SCRIPT.is_file()
    assert "ops_force" in DECODE.read_text(encoding="utf-8")
    assert "list_latest_natal_decode_by_user" in DECODE.read_text(encoding="utf-8")

    il_text = IL.read_text(encoding="utf-8")
    assert "### 6.72" in il_text
    assert "1.3.124" in il_text

    inventory = INVENTORY.read_text(encoding="utf-8")
    assert "46. Natal Decode cache refresh" in inventory
    assert "✅ 1.3.124" in inventory
    assert "KC-C-DECODE-CACHE-REFRESH" in inventory

    assert "1.3.124" in HANDOFF.read_text(encoding="utf-8")
    assert "1.3.124" in TRACKER.read_text(encoding="utf-8")

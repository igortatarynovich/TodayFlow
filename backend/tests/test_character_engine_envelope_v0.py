"""character_engine_v1 envelope from Stage 0–5 diagnostics."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from unittest.mock import patch

from todayflow_backend.services.character_engine_envelope_v0 import (
    SCHEMA_VERSION,
    build_character_engine_envelope_v0,
    maybe_attach_character_engine_envelope_v0,
)


def _minimal_diagnostics(*, grounded: bool = True) -> dict:
    claim = "claim:aaaaaaaaaaaaaaaaaaaaaaaa"
    fact = "fact:bbbbbbbbbbbbbbbbbbbbbbbb"
    status = "grounded" if grounded else "insufficient_identity_core"
    return {
        "character_engine_stage2": {
            "stage0": {
                "stage_version": "facts_v0",
                "profile_fingerprint": "pf_test_envelope_01",
                "input_fact_set_version": "facts_pack_v0_test",
                "calc_authority": {"swiss": "swiss_ephe_v1", "numerology": "num_v1"},
                "capability": {
                    "natal_mode": "date_only",
                    "has_name": True,
                    "has_birth_time": False,
                    "has_birth_place": False,
                },
                "raw_facts": [
                    {
                        "fact_id": fact,
                        "fact_type": "sun_sign",
                        "value": "Aquarius",
                        "authority": "swiss",
                        "calc_version": "swiss_ephe_v1",
                        "capability_required": "date_only",
                        "confidence": "high",
                        "provenance": {
                            "source_system": "swiss",
                            "input_fingerprint": "in_test",
                            "computed_at": "2026-07-26T12:00:00Z",
                        },
                    }
                ],
            },
            "stage1": {
                "stage_version": "evidence_v0",
                "schema_version": "evidence_graph_v1",
                "claims": [
                    {
                        "claim_id": claim,
                        "claim_kind": "autonomy_need",
                        "thesis_key": "autonomy_high",
                        "cascade_role": "source_roles",
                        "supporting_fact_ids": [fact],
                        "confidence": "medium",
                        "capability_floor": "date_only",
                        "produced_by_stage": 1,
                        "evidence_status": "grounded",
                    }
                ],
                "edges": [
                    {
                        "edge_id": "edge:cccccccccccccccccccccccc",
                        "fact_id": fact,
                        "claim_id": claim,
                        "edge_type": "supports",
                    }
                ],
            },
            "stage2": {
                "status": status,
                "identity_core": {
                    "claim_id": "claim:dddddddddddddddddddddddd",
                    "claim_kind": "identity_core",
                    "thesis_key": "builds_through_autonomy",
                    "surface_text": "Builds through autonomy.",
                    "cascade_role": "identity_core",
                    "primary_claim_id": claim,
                    "supporting_claim_ids": [claim],
                    "supporting_fact_ids": [fact],
                    "confidence": "high",
                    "capability_floor": "date_only",
                    "produced_by_stage": 2,
                    "evidence_status": "grounded",
                }
                if grounded
                else None,
            },
        },
        "character_engine_stage3": {
            "stage3": {
                "artifact_version": "stage3_v0",
                "status": status,
                "internal_engine": {
                    "decision": {
                        "slot": "decision",
                        "surface_text": "Decide from own contour.",
                        "supporting_claim_ids": [claim],
                    }
                },
                "primary_tension": {
                    "thesis_key": "autonomy_vs_contact",
                    "surface_text": "Distance protects clarity.",
                    "supporting_claim_ids": [claim],
                },
                "secondary_tensions": [],
            }
        },
        "character_engine_stage4": {
            "stage4": {
                "artifact_version": "stage4_v0",
                "status": status,
                "scenes": [
                    {
                        "scene_id": "scene:eeeeeeeeeeeeeeeeeeeeeeee",
                        "scene_kind": "intimacy",
                        "surface_text": "Intimacy via distance.",
                        "supporting_claim_ids": [claim],
                    }
                ],
                "potential": {
                    "surface_text": "Enter contact without surrender.",
                    "supporting_claim_ids": [claim],
                },
                "blind_spots": [
                    {
                        "surface_text": "Clarity becomes delay.",
                        "supporting_claim_ids": [claim],
                    }
                ],
            }
        },
        "character_engine_stage5": {
            "stage5": {
                "artifact_version": "stage5_v0",
                "status": status,
                "compass": {
                    "schema_version": "compass_v1",
                    "assembler_version": "character_engine_compass_assembler_v0",
                    "items": [
                        {
                            "item_id": "compass:ffffffffffffffffffffffff",
                            "item_kind": "work_style",
                            "value": "Own tempo",
                            "derived_from": {"claim_ids": [claim], "mechanism_slots": ["decision"]},
                        }
                    ],
                    "source_refs": {"claim_ids": [claim], "scene_ids": [], "mechanism_slots": ["decision"]},
                },
                "legacy_map": {
                    "adapter_version": "character_engine_adapter_v1",
                    "fields": {
                        "identity_core": {
                            "value": "Builds through autonomy.",
                            "source_refs": {"claim_ids": [claim]},
                        }
                    },
                    "identity_thesis": "builds_through_autonomy",
                    "rooted_in_stages": ["stage2", "stage3", "stage4"],
                },
            }
        },
    }


def test_envelope_forming_when_publish_ready_off() -> None:
    with patch(
        "todayflow_backend.services.character_engine_envelope_v0.character_engine_publish_ready_enabled",
        return_value=False,
    ):
        env = build_character_engine_envelope_v0(
            diagnostics=_minimal_diagnostics(grounded=True),
            profile_fingerprint="pf_test_envelope_01",
        )
    assert env["schema_version"] == SCHEMA_VERSION
    assert env["status"] == "forming"
    assert isinstance(env.get("cascade"), dict)
    assert isinstance(env.get("compass"), dict)
    assert env["legacy_projections"]["adapter_version"] == "character_engine_adapter_v1"
    assert "identity_thesis" not in env["legacy_projections"]
    assert env["diagnostics"]["shadow"]["recommendation"] == "hold"


def test_envelope_ready_when_publish_ready_on() -> None:
    with patch(
        "todayflow_backend.services.character_engine_envelope_v0.character_engine_publish_ready_enabled",
        return_value=True,
    ):
        env = build_character_engine_envelope_v0(
            diagnostics=_minimal_diagnostics(grounded=True),
            profile_fingerprint="pf_test_envelope_01",
        )
    assert env["status"] == "ready"
    assert isinstance(env.get("cascade"), dict)


def test_envelope_validates_against_machine_schema() -> None:
    jsonschema = pytest.importorskip("jsonschema")
    schema_path = (
        Path(__file__).resolve().parents[2] / "docs" / "schemas" / "character_engine_v1.schema.json"
    )
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    with patch(
        "todayflow_backend.services.character_engine_envelope_v0.character_engine_publish_ready_enabled",
        return_value=False,
    ):
        env = build_character_engine_envelope_v0(
            diagnostics=_minimal_diagnostics(grounded=True),
            profile_fingerprint="pf_test_envelope_01",
        )
    jsonschema.validate(instance=env, schema=schema)


def test_envelope_attach_is_assemble_once() -> None:
    payload = {"diagnostics": _minimal_diagnostics(grounded=True)}
    once = maybe_attach_character_engine_envelope_v0(
        payload, profile_fingerprint="pf_test_envelope_01"
    )
    first = once["character_engine_v1"]
    once["character_engine_v1"] = {**first, "meta": {**first["meta"], "marker": "keep"}}
    twice = maybe_attach_character_engine_envelope_v0(
        once, profile_fingerprint="pf_test_envelope_01"
    )
    assert twice["character_engine_v1"]["meta"].get("marker") == "keep"

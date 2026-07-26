"""PUBLISH_READY cutover: CE SoT, legacy portrait gated."""

from __future__ import annotations

from unittest.mock import patch

from todayflow_backend.services.character_engine_contract_projection_v0 import (
    project_profile_contract_from_character_engine_v0,
)
from todayflow_backend.services.profile_contract_v1 import build_profile_portrait_v1


def test_build_profile_portrait_blocked_when_publish_ready() -> None:
    with patch(
        "todayflow_backend.core.config.settings.character_engine_publish_ready",
        True,
    ):
        contract, interp, daily, forming = build_profile_portrait_v1(
            profile_input={"person": {"locale": "ru"}},
            living=None,
            locale="ru",
        )
    assert forming is True
    assert contract["generation_meta"]["sot"] == "character_engine_v1"
    assert interp["source"] == "character_engine_v1_gate"
    assert daily.get("deferred") is True


def test_project_contract_from_ready_envelope() -> None:
    payload = {
        "character_engine_v1": {
            "status": "ready",
            "legacy_projections": {
                "adapter_version": "character_engine_adapter_v1",
                "fields": {
                    "identity_core": {"value": "Core line", "source_refs": {"claim_ids": []}},
                    "recognition_line": {"value": "Core line", "source_refs": {"claim_ids": []}},
                    "strengths": {"value": ["A", "B", "C"], "source_refs": {"claim_ids": []}},
                    "growth_zones": {"value": ["G1", "G2", "G3"], "source_refs": {"claim_ids": []}},
                    "helps": {"value": ["H1"], "source_refs": {"claim_ids": []}},
                    "decision_style": {"value": "Decide alone", "source_refs": {"claim_ids": []}},
                    "relationship_style": {"value": "Slow trust", "source_refs": {"claim_ids": []}},
                    "money_patterns": {"value": "Independence", "source_refs": {"claim_ids": []}},
                    "recurring_patterns": {"value": ["Trap"], "source_refs": {"claim_ids": []}},
                },
            },
        }
    }
    contract = project_profile_contract_from_character_engine_v0(payload)
    assert contract["status"] == "ready"
    assert contract["identity_core"] == "Core line"
    assert contract["generation_meta"]["sot"] == "character_engine_v1"
    assert contract["decision_style"] == "Decide alone"

"""guide_contract_v2 — HTTP envelope for surface=guide."""

from __future__ import annotations

from todayflow_backend.services.guide_contract_v2 import (
    GUIDE_CONTRACT_V2,
    GUIDE_PIPELINE_V0,
    attach_guide_contract_v2,
    build_guide_pipeline_v0,
    guide_funnel_core_is_llm_locked,
)


def test_build_guide_pipeline_v0_monolith() -> None:
    pipe = build_guide_pipeline_v0(generation_mode="monolith", input_payload={})
    assert pipe["contract_version"] == GUIDE_PIPELINE_V0
    assert pipe["generation_mode"] == "monolith"
    assert "steps" not in pipe


def test_build_guide_pipeline_v0_funnel() -> None:
    ip = {
        "guide_funnel_used": True,
        "guide_funnel_contract": "guide_narrative_funnel_v0",
        "guide_funnel_parent_log_id": 10,
        "guide_funnel_step3_log_id": 12,
        "guide_funnel_step2_log_id": 13,
        "guide_funnel_step1_cache_hit": True,
        "guide_funnel_step3_cache_hit": False,
        "guide_funnel_step2_cache_hit": True,
        "guide_funnel_core_source": "funnel_core_text_v0",
    }
    pipe = build_guide_pipeline_v0(
        generation_mode="funnel",
        input_payload=ip,
        context_for_next_surfaces="Тезис дня: один фокус без распыления по параллельным стартам.",
    )
    assert pipe["generation_mode"] == "funnel"
    assert pipe["steps"]["interpretation"]["generation_log_id"] == 10
    assert pipe["steps"]["core_text"]["source"] == "funnel_core_text_v0"
    assert pipe["child_chain"]["context_for_next_surfaces"].startswith("Тезис дня")


def test_attach_guide_contract_v2() -> None:
    payload: dict = {"headline": "x", "context_for_next_surfaces": "Тезис дня для child surfaces достаточно длинный."}
    attach_guide_contract_v2(
        payload,
        input_payload={"guide_funnel_used": True, "guide_funnel_core_source": "guide_decision_v0"},
    )
    assert payload["contract_version"] == GUIDE_CONTRACT_V2
    assert payload["guide_pipeline"]["generation_mode"] == "funnel"


def test_guide_funnel_core_is_llm_locked() -> None:
    assert guide_funnel_core_is_llm_locked({"guide_funnel_core_source": "funnel_core_text_v0"}) is True
    assert guide_funnel_core_is_llm_locked({"guide_funnel_core_source": "guide_decision_v0"}) is False

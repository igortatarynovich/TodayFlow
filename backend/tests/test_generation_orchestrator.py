"""O12 / GE-1: merge-pass, narrative outcome, Guidance/Compatibility facades."""

from __future__ import annotations

from todayflow_backend.services.generation_orchestrator import (
    DAY_MODEL_ORCHESTRATION_TRACE,
    FUNNEL_HANDOFF_CONTRACT,
    MERGE_PASS_CONTRACT,
    NARRATIVE_OUTCOME_CONTRACT,
    ORCHESTRATOR_VERSION,
    PIPELINE_COMPATIBILITY,
    PIPELINE_GUIDANCE,
    SEMANTIC_QUALITY_CONTRACT,
    attach_narrative_outcome_to_orchestration,
    attach_semantic_quality_to_orchestration,
    build_compatibility_orchestration_meta,
    build_guidance_orchestration_meta,
    build_narrative_semantic_quality_trace,
    build_today_narrative_orchestration_meta,
    narrative_merge_pass_plan,
    record_guide_funnel_step_handoffs,
    slim_funnel_step_handoff,
)


def test_narrative_merge_pass_plan_known_surfaces():
    guide = narrative_merge_pass_plan("guide")
    assert guide[0] == "funnel_interpretation_v0"
    assert "funnel_core_text_v0" in guide
    assert "attach_guide_contract_v2" in guide
    assert "apply_funnel_core_or_guide_decision_v0" in guide
    assert "finalize_day_layer_o8" in narrative_merge_pass_plan("day_layer")
    assert "ru_spheres_rhythm_grounding_o11" in narrative_merge_pass_plan("spheres")
    assert narrative_merge_pass_plan("evening")[-1] == "ru_evening_concrete_gate"
    assert narrative_merge_pass_plan("deepen")[-1] == "ru_deepen_concrete_gate"


def test_merge_pass_contract_constant():
    assert MERGE_PASS_CONTRACT == "GE-1_v1"


def test_build_orchestration_includes_day_model_trace():
    meta = build_today_narrative_orchestration_meta(
        surface="guide",
        day_ctx={
            "contract_version": "day_context_v0",
            "layers": {
                "day_model": {
                    "contract_version": "day_model_v0",
                    "vector": {"summary": "Focus on steady pace today."},
                    "tension": {"summary": "Work vs rest pull."},
                    "risk": {"summary": "Overcommit risk."},
                    "strategy": {"one_focus": "One clear priority."},
                    "gate": {"passed": True},
                }
            },
        },
        profile_selector_slim={"task": "today_summary"},
        profile_selector_full={"task": "today_summary", "overall_confidence": 0.8},
        day_context_sha256="a" * 64,
    )
    assert meta["orchestrator_version"] == ORCHESTRATOR_VERSION
    rt = meta.get("reasoning_trace")
    assert isinstance(rt, dict)
    dm = rt.get("day_model")
    assert isinstance(dm, dict)
    assert dm.get("contract_version") == DAY_MODEL_ORCHESTRATION_TRACE
    assert "Focus on steady pace" in (dm.get("vector_summary") or "")
    assert "Work vs rest" in (dm.get("tension_summary") or "")
    assert dm.get("gate_passed") is True


def test_attach_narrative_outcome_funnel_guide():
    base = build_today_narrative_orchestration_meta(
        surface="guide",
        day_ctx={"contract_version": "day_context_v0", "layers": {}},
        profile_selector_slim=None,
        profile_selector_full=None,
        day_context_sha256="b" * 64,
    )
    ip = {
        "guide_funnel_used": True,
        "guide_funnel_contract": "guide_funnel_v0",
        "guide_funnel_parent_log_id": 101,
        "guide_funnel_step3_log_id": 103,
        "guide_funnel_step2_log_id": 102,
        "guide_funnel_step1_cache_hit": True,
        "guide_funnel_step3_cache_hit": False,
        "guide_funnel_step2_cache_hit": True,
        "guide_funnel_core_source": "funnel_core_text_v0",
    }
    payload = {
        "contract_version": "guide_contract_v2",
        "guide_pipeline": {"contract_version": "guide_pipeline_v0", "generation_mode": "funnel"},
    }
    out = attach_narrative_outcome_to_orchestration(
        base, input_payload=ip, surface="guide", payload=payload, used_fallback=False
    )
    no = out.get("narrative_outcome")
    assert isinstance(no, dict)
    assert no.get("contract_version") == NARRATIVE_OUTCOME_CONTRACT
    assert no.get("generation_mode") == "funnel"
    assert no["funnel"]["step1_log_id"] == 101
    assert no["funnel"]["core_source"] == "funnel_core_text_v0"
    assert "funnel_interpretation_v0" in out.get("stages", [])


def test_attach_narrative_outcome_child_chain():
    base = build_today_narrative_orchestration_meta(
        surface="spheres",
        day_ctx={"contract_version": "day_context_v0", "layers": {}},
        profile_selector_slim=None,
        profile_selector_full=None,
        day_context_sha256="c" * 64,
    )
    ip = {
        "guide_funnel_chain_used": True,
        "guide_funnel_child_chain_contract": "guide_funnel_child_chain_v0",
        "guide_funnel_step1_log_id": 55,
    }
    out = attach_narrative_outcome_to_orchestration(
        base, input_payload=ip, surface="spheres", payload={"spheres": []}, used_fallback=True
    )
    no = out.get("narrative_outcome")
    assert no.get("used_fallback") is True
    assert no.get("child_funnel_chain", {}).get("step1_log_id") == 55


def test_build_guidance_orchestration_meta():
    meta = build_guidance_orchestration_meta(
        lane="decision",
        spread_title="Три карты",
        prompt_version="guidance-session-answer-v1",
        structural={
            "dominant_card_name": "The Sun",
            "tension_position_id": "block",
            "conflict_note": "Card A vs Card B tension.",
        },
        question_assessment={"weak_reading_warning": False, "flags": ["specific"]},
    )
    assert meta["orchestrator_version"] == ORCHESTRATOR_VERSION
    assert meta["pipeline"] == PIPELINE_GUIDANCE
    assert "llm_answer_refinement" in meta["stages"]
    rt = meta.get("reasoning_trace")
    assert rt["spread_structural"]["dominant_card_name"] == "The Sun"


def test_build_compatibility_orchestration_meta():
    meta = build_compatibility_orchestration_meta(
        relationship_context="dating",
        signals={"overall_score": 72, "conflict_repair_score": 55, "stability_index": 80},
        pair_dynamics={"leader_guess": "user_1", "withdrawer_guess": "user_2", "element_pair": "fire_water"},
    )
    assert meta["pipeline"] == PIPELINE_COMPATIBILITY
    assert meta["reasoning_trace"]["signals"]["overall_score"] == 72


def test_slim_funnel_step_handoffs():
    ip: dict = {}
    record_guide_funnel_step_handoffs(
        ip,
        interp={"what_happens": "Focus on one thread today.", "one_concrete_move": "Write the list."},
        core={"headline": "One clear line", "subline": "Supporting detail here."},
        satellites={"headline": "Sat headline", "do_items": ["a"], "action_options": []},
    )
    ho = ip.get("guide_funnel_step_handoffs")
    assert ho.get("contract_version") == FUNNEL_HANDOFF_CONTRACT
    assert "Focus on one thread" in ho["interpretation_v0"]["what_happens_excerpt"]
    assert ho["satellites_v0"]["has_do_items"] is True


def test_semantic_quality_trace_guide_incomplete():
    trace = build_narrative_semantic_quality_trace(
        "guide",
        locale="ru",
        payload={
            "headline": "Сегодня держим одну линию по работе",
            "do_items": ["Закрыть один пункт до обеда"],
        },
    )
    assert trace["contract_version"] == SEMANTIC_QUALITY_CONTRACT
    assert trace["passed"] is False
    assert trace["checks"]["payload_present"] is True
    assert trace["checks"]["shape"] is False


def test_semantic_quality_trace_rejects_banned_phrase(monkeypatch):
    monkeypatch.setattr(
        "todayflow_backend.services.today_narrative.settings.today_narrative_quality_mode",
        "strict",
    )
    payload = {
        "headline": "Смысл и коммуникация — главное сегодня",
        "subline": "Поддержка второстепенного",
        "energy_line": "energy line here",
        "focus_line": "focus line here",
        "risk_line": "risk line here",
        "risk_detail": "risk detail text",
        "do_items": ["Закрыть один пункт до обеда"],
        "avoid_items": ["Новые задачи без приоритета"],
        "header_disclaimer": "disclaimer",
        "context_for_next_surfaces": "context for child surfaces",
        "pattern_insight": "pattern insight text",
        "life_context_insight": "life context insight",
        "core_message": {"title": "Core title", "body": "Core body long enough"},
        "action_options": [
            {"title": "Шаг один до обеда"},
            {"title": "Шаг два после обеда"},
            {"title": "Шаг три вечером"},
        ],
        "sphere_triad": [
            {"area": "work", "stance": "up", "line": "Работа — один законченный кусок важнее десяти начатых."},
            {"area": "love", "stance": "down", "line": "Отношения — лучше сказать прямо, чем угадывать."},
            {"area": "money", "stance": "neutral", "line": "Деньги — проверь цифры и границы без импульса."},
        ],
        "support_hooks": ["support hook one"],
    }
    trace = build_narrative_semantic_quality_trace("guide", locale="ru", payload=payload)
    assert trace["checks"].get("shape") is True
    assert trace["checks"].get("concrete") is False
    assert trace["passed"] is False


def test_semantic_quality_trace_trust_llm_skips_concrete_gate(monkeypatch):
    monkeypatch.setattr(
        "todayflow_backend.services.today_narrative.settings.today_narrative_quality_mode",
        "trust_llm",
    )
    payload = {
        "headline": "Смысл и коммуникация — главное сегодня",
        "subline": "Поддержка второстепенного",
        "energy_line": "energy line here",
        "focus_line": "focus line here",
        "risk_line": "risk line here",
        "risk_detail": "risk detail text",
        "do_items": ["Закрыть один пункт до обеда"],
        "avoid_items": ["Новые задачи без приоритета"],
        "header_disclaimer": "disclaimer",
        "context_for_next_surfaces": "context for child surfaces",
        "pattern_insight": "pattern insight text",
        "life_context_insight": "life context insight",
        "core_message": {"title": "Core title", "body": "Core body long enough"},
        "action_options": [
            {"title": "Шаг один до обеда"},
            {"title": "Шаг два после обеда"},
            {"title": "Шаг три вечером"},
        ],
        "sphere_triad": [
            {"area": "work", "stance": "up", "line": "Работа — один законченный кусок важнее десяти начатых."},
            {"area": "love", "stance": "down", "line": "Отношения — лучше сказать прямо, чем угадывать."},
            {"area": "money", "stance": "neutral", "line": "Деньги — проверь цифры и границы без импульса."},
        ],
        "support_hooks": ["support hook one"],
    }
    trace = build_narrative_semantic_quality_trace("guide", locale="ru", payload=payload)
    assert trace["checks"].get("quality_mode") == "trust_llm"
    assert trace["checks"].get("concrete") is True
    assert trace["passed"] is True


def test_attach_semantic_quality_to_orchestration():
    base = {"orchestrator_version": ORCHESTRATOR_VERSION}
    out = attach_semantic_quality_to_orchestration(
        base,
        surface="guide",
        locale="ru",
        payload={"headline": "Сегодня держим одну линию по работе"},
    )
    sq = out.get("semantic_quality")
    assert isinstance(sq, dict)
    assert sq.get("contract_version") == SEMANTIC_QUALITY_CONTRACT
    assert "checks" in sq

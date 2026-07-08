"""Generation Orchestrator v0 — единая мета-воронка для генераций (канон: docs/SOURCE_OF_TRUTH_PIPELINE.md §10.1).

Пока не заменяет вызовы narrative/guidance из API, а **документирует и логирует** фактический
порядок этапов и контракты, чтобы все новые слои навешивались сюда, а не разъезжались по модулям.

O12: в `input_payload.orchestration` пишутся `merge_pass_contract` и `merge_pass_steps` (план пост-обработки
перед ответом/кэшем; исполнение по-прежнему в `today_narrative.build_today_narrative`).

Единая точка входа для HTTP: `run_today_narrative_pipeline` (оборачивает `build_today_narrative`).
"""

from __future__ import annotations

from datetime import date
from typing import Any

from sqlalchemy.orm import Session

ORCHESTRATOR_VERSION = "0.5.0"
PIPELINE_TODAY_NARRATIVE = "today_narrative_v1"
PIPELINE_GUIDANCE = "guidance_v1"
PIPELINE_COMPATIBILITY = "compatibility_v1"
SOURCE_OF_TRUTH_REF = "docs/SOURCE_OF_TRUTH_PIPELINE.md"
NARRATIVE_OUTCOME_CONTRACT = "narrative_outcome_v0"
DAY_MODEL_ORCHESTRATION_TRACE = "day_model_orchestration_trace_v0"
FUNNEL_HANDOFF_CONTRACT = "funnel_step_handoff_v0"
SEMANTIC_QUALITY_CONTRACT = "semantic_quality_v0"
# O12: канонический контракт «один задокументированный merge-pass» (фактические вызовы — в `today_narrative`).
MERGE_PASS_CONTRACT = "GE-1_v1"


def narrative_merge_pass_plan(surface: str) -> list[str]:
    """
    Стабильные id шагов пост-обработки перед ответом/кэшем (паритет O12 в логах `orchestration`).
    Совпадает по смыслу с цепочками в `build_today_narrative` (guide: `_guide_apply_final_processing_pass` и т.д.).
    """
    s = (surface or "").strip().lower()
    if s == "guide":
        return [
            "funnel_interpretation_v0",
            "funnel_core_text_v0",
            "funnel_satellites_v0",
            "ensure_guide_actionable_fields",
            "merge_guide_why_astrological_layers",
            "append_ritual_why_layers",
            "apply_funnel_core_or_guide_decision_v0",
            "dedupe_guide_payload_cross_fields",
            "strip_llm_meta_guide_payload",
            "normalize_guide_payload_for_tier",
            "attach_day_engine_brief_and_slices",
            "attach_guide_contract_v2",
            "optional_guide_brief_alignment_retry",
        ]
    if s == "day_layer":
        return [
            "finalize_day_layer_o8",
            "strip_llm_meta_day_layer",
            "validate_shape_language_concrete",
        ]
    if s == "spheres":
        return [
            "validate_shape_language_concrete",
            "ru_spheres_quality_gate",
            "ru_spheres_rhythm_grounding_o11",
        ]
    if s == "evening":
        return [
            "validate_shape_language_concrete",
            "ru_evening_concrete_gate",
        ]
    if s == "deepen":
        return [
            "validate_shape_language_concrete",
            "ru_deepen_concrete_gate",
        ]
    return ["validate_shape_language_concrete"]


def _reasoning_trace_from_selector(profile_selector_full: dict[str, Any] | None) -> dict[str, Any] | None:
    """Технический trace для отладки (не CoT для пользователя): селектор и разрешённые поля."""

    if not isinstance(profile_selector_full, dict):
        return None
    out: dict[str, Any] = {}
    dt = profile_selector_full.get("debug_trace")
    if isinstance(dt, dict):
        out["selector_debug"] = dict(dt)
    out["selector_resolution"] = {
        "task": profile_selector_full.get("task"),
        "topic": profile_selector_full.get("topic"),
        "current_mode": profile_selector_full.get("current_mode"),
        "overall_confidence": profile_selector_full.get("overall_confidence"),
    }
    gr = profile_selector_full.get("generation_rules")
    if isinstance(gr, dict):
        out["generation_rules"] = {
            k: gr.get(k)
            for k in ("tone", "depth", "max_actions", "must_include", "must_avoid")
            if k in gr
        }
    return out or None


def _day_model_trace_from_layers(layers: dict[str, Any]) -> dict[str, Any] | None:
    """GE-1 v0.3: dominant signal / tension / risk из day_model_v0 для reasoning_trace."""
    dm = layers.get("day_model")
    if not isinstance(dm, dict) or dm.get("contract_version") != "day_model_v0":
        return None
    vec = dm.get("vector") if isinstance(dm.get("vector"), dict) else {}
    ten = dm.get("tension") if isinstance(dm.get("tension"), dict) else {}
    risk = dm.get("risk") if isinstance(dm.get("risk"), dict) else {}
    strat = dm.get("strategy") if isinstance(dm.get("strategy"), dict) else {}
    gate = dm.get("gate") if isinstance(dm.get("gate"), dict) else {}
    trace: dict[str, Any] = {"contract_version": DAY_MODEL_ORCHESTRATION_TRACE}
    vs = str(vec.get("summary") or "").strip()
    if vs:
        trace["vector_summary"] = vs[:240]
    ts = str(ten.get("summary") or "").strip()
    if ts:
        trace["tension_summary"] = ts[:240]
    rs = str(risk.get("summary") or "").strip()
    if rs:
        trace["risk_summary"] = rs[:240]
    sf = str(strat.get("one_focus") or "").strip()
    if sf:
        trace["strategy_one_focus"] = sf[:180]
    if "passed" in gate:
        trace["gate_passed"] = bool(gate.get("passed"))
    return trace if len(trace) > 1 else None


def attach_narrative_outcome_to_orchestration(
    orchestration_meta: dict[str, Any],
    *,
    input_payload: dict[str, Any],
    surface: str,
    payload: dict[str, Any] | None,
    used_fallback: bool,
) -> dict[str, Any]:
    """GE-1 v0.3: после генерации — funnel/monolith outcome и child chain в orchestration log."""
    out = dict(orchestration_meta)
    ip = input_payload if isinstance(input_payload, dict) else {}
    s = (surface or "").strip().lower()
    outcome: dict[str, Any] = {
        "contract_version": NARRATIVE_OUTCOME_CONTRACT,
        "surface": s,
        "used_fallback": bool(used_fallback),
    }
    if s == "guide":
        if ip.get("guide_funnel_used"):
            outcome["generation_mode"] = "funnel"
            outcome["funnel"] = {
                "contract": ip.get("guide_funnel_contract"),
                "step1_log_id": ip.get("guide_funnel_parent_log_id"),
                "step3_log_id": ip.get("guide_funnel_step3_log_id"),
                "step2_log_id": ip.get("guide_funnel_step2_log_id"),
                "step1_cache_hit": bool(ip.get("guide_funnel_step1_cache_hit")),
                "step3_cache_hit": bool(ip.get("guide_funnel_step3_cache_hit")),
                "step2_cache_hit": bool(ip.get("guide_funnel_step2_cache_hit")),
                "core_source": ip.get("guide_funnel_core_source"),
            }
        else:
            outcome["generation_mode"] = "monolith"
        if isinstance(payload, dict) and payload.get("contract_version") == "guide_contract_v2":
            gp = payload.get("guide_pipeline")
            if isinstance(gp, dict):
                outcome["guide_pipeline_contract"] = gp.get("contract_version")
                outcome["guide_pipeline_mode"] = gp.get("generation_mode")
    elif s in ("day_layer", "spheres", "evening", "deepen") and ip.get("guide_funnel_chain_used"):
        outcome["child_funnel_chain"] = {
            "contract": ip.get("guide_funnel_child_chain_contract"),
            "step1_log_id": ip.get("guide_funnel_step1_log_id"),
        }
    handoffs = ip.get("guide_funnel_step_handoffs")
    if isinstance(handoffs, dict) and s == "guide":
        outcome["funnel_step_handoffs"] = handoffs
    out["narrative_outcome"] = outcome

    stages = list(out.get("stages") or [])
    if s == "guide":
        if ip.get("guide_funnel_used"):
            for step in (
                "funnel_interpretation_v0",
                "funnel_core_text_v0",
                "funnel_satellites_v0",
                "guide_contract_v2",
            ):
                if step not in stages:
                    insert_at = stages.index("merge_pass_documented") if "merge_pass_documented" in stages else len(stages)
                    stages.insert(insert_at, step)
        elif "llm_monolith_guide" not in stages:
            key = f"llm_surface:{s}"
            idx = stages.index(key) + 1 if key in stages else len(stages)
            stages.insert(idx, "llm_monolith_guide")
    out["stages"] = stages
    return out


def slim_funnel_step_handoff(step: str, part: dict[str, Any] | None) -> dict[str, Any] | None:
    """GE-1 v0.4: урезанный payload между шагами funnel для orchestration log (не full LLM output)."""
    if not isinstance(part, dict):
        return None
    s = (step or "").strip().lower()
    if s == "interpretation_v0":
        out: dict[str, Any] = {"step": s}
        wh = str(part.get("what_happens") or "").strip()
        if wh:
            out["what_happens_excerpt"] = wh[:120]
        ocm = str(part.get("one_concrete_move") or "").strip()
        if ocm:
            out["one_concrete_move_excerpt"] = ocm[:120]
        if part.get("why_layers"):
            out["has_why_layers"] = True
        return out
    if s == "core_text_v0":
        out = {"step": s}
        hl = str(part.get("headline") or "").strip()
        if hl:
            out["headline_excerpt"] = hl[:120]
        sl = str(part.get("subline") or "").strip()
        if sl:
            out["subline_excerpt"] = sl[:120]
        return out if len(out) > 1 else None
    if s == "satellites_v0":
        out = {"step": s}
        hl = str(part.get("headline") or "").strip()
        if hl:
            out["headline_excerpt"] = hl[:80]
        out["has_do_items"] = bool(part.get("do_items"))
        out["has_action_options"] = bool(part.get("action_options"))
        return out
    return None


def record_guide_funnel_step_handoffs(
    input_payload: dict[str, Any],
    *,
    interp: dict[str, Any] | None,
    core: dict[str, Any] | None,
    satellites: dict[str, Any] | None,
) -> None:
    """Записать slim handoffs в input_payload до финального orchestration attach."""
    handoffs: dict[str, Any] = {"contract_version": FUNNEL_HANDOFF_CONTRACT}
    i = slim_funnel_step_handoff("interpretation_v0", interp)
    c = slim_funnel_step_handoff("core_text_v0", core)
    s = slim_funnel_step_handoff("satellites_v0", satellites)
    if i:
        handoffs["interpretation_v0"] = i
    if c:
        handoffs["core_text_v0"] = c
    if s:
        handoffs["satellites_v0"] = s
    if len(handoffs) > 1:
        input_payload["guide_funnel_step_handoffs"] = handoffs


def build_narrative_semantic_quality_trace(
    surface: str,
    *,
    locale: str,
    payload: dict[str, Any] | None,
    ritual_norm: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """GE-1 v0.4: результат смысловых гейтов перед log/cache (Evaluation Engine trace)."""
    s = (surface or "").strip().lower()
    checks: dict[str, bool] = {"payload_present": isinstance(payload, dict)}
    if not checks["payload_present"]:
        return {
            "contract_version": SEMANTIC_QUALITY_CONTRACT,
            "surface": s,
            "passed": False,
            "checks": checks,
        }
    from todayflow_backend.services import today_narrative as tn

    assert payload is not None
    checks["shape"] = bool(tn._validate_payload_shape(s, payload))  # type: ignore[arg-type]
    checks["language"] = bool(tn._validate_payload_language(s, payload, locale))  # type: ignore[arg-type]
    checks["quality_mode"] = tn._narrative_quality_mode()
    if s == "guide":
        checks["concrete"] = bool(
            tn._guide_payload_concrete(locale, payload, ritual_norm=ritual_norm)
        ) if tn._narrative_quality_strict() else True
    elif s == "spheres":
        checks["concrete"] = bool(tn._spheres_payload_concrete(locale, payload)) if tn._narrative_quality_strict() else True
    elif s in ("evening", "deepen"):
        texts = tn._payload_text_values(s, payload)  # type: ignore[arg-type]
        checks["concrete"] = (not tn._ru_narrative_quality_reject(texts)) if tn._narrative_quality_strict() else True
    passed = all(checks.values())
    return {
        "contract_version": SEMANTIC_QUALITY_CONTRACT,
        "surface": s,
        "passed": passed,
        "checks": checks,
    }


def attach_semantic_quality_to_orchestration(
    orchestration_meta: dict[str, Any],
    *,
    surface: str,
    locale: str,
    payload: dict[str, Any] | None,
    ritual_norm: dict[str, Any] | None = None,
) -> dict[str, Any]:
    out = dict(orchestration_meta)
    out["semantic_quality"] = build_narrative_semantic_quality_trace(
        surface,
        locale=locale,
        payload=payload,
        ritual_norm=ritual_norm,
    )
    return out


def build_guidance_orchestration_meta(
    *,
    lane: str,
    spread_title: str,
    prompt_version: str,
    structural: dict[str, Any] | None = None,
    question_assessment: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """GE-1 v0.4: снимок этапов Guidance LLM step1 до вызова модели."""
    reasoning_trace: dict[str, Any] | None = None
    if isinstance(structural, dict) or isinstance(question_assessment, dict):
        reasoning_trace = {}
        if isinstance(structural, dict):
            reasoning_trace["spread_structural"] = {
                "dominant_card_name": structural.get("dominant_card_name"),
                "tension_position_id": structural.get("tension_position_id"),
                "conflict_note_excerpt": str(structural.get("conflict_note") or "")[:240] or None,
            }
        if isinstance(question_assessment, dict):
            reasoning_trace["question_assessment"] = {
                "weak_reading_warning": question_assessment.get("weak_reading_warning"),
                "flags": question_assessment.get("flags"),
            }
    return {
        "orchestrator_version": ORCHESTRATOR_VERSION,
        "pipeline": PIPELINE_GUIDANCE,
        "stages": [
            "template_answer",
            "spread_structural_analysis",
            "profile_module_selection",
            "llm_answer_refinement",
            "compose_guidance_reading",
            "question_editorial",
        ],
        "canon_ref": SOURCE_OF_TRUTH_REF,
        "prompt_version": prompt_version,
        "lane": lane,
        "spread_title": spread_title,
        "reasoning_trace": reasoning_trace,
        "merge_pass_contract": MERGE_PASS_CONTRACT,
        "merge_pass_steps": ["refine_answer_llm", "compose_guidance_reading", "question_editorial"],
    }


def build_compatibility_orchestration_meta(
    *,
    relationship_context: str,
    signals: dict[str, Any] | None = None,
    pair_dynamics: dict[str, Any] | None = None,
    scenario_tone: Any | None = None,
) -> dict[str, Any]:
    """GE-1 v0.4: снимок этапов Compatibility dynamics LLM."""
    reasoning_trace: dict[str, Any] | None = None
    if isinstance(signals, dict) or isinstance(pair_dynamics, dict):
        reasoning_trace = {}
        if isinstance(signals, dict):
            reasoning_trace["signals"] = {
                "overall_score": signals.get("overall_score"),
                "conflict_repair_score": signals.get("conflict_repair_score"),
                "stability_index": signals.get("stability_index"),
            }
        if isinstance(pair_dynamics, dict):
            reasoning_trace["pair_dynamics"] = {
                "leader_guess": pair_dynamics.get("leader_guess"),
                "withdrawer_guess": pair_dynamics.get("withdrawer_guess"),
                "element_pair": pair_dynamics.get("element_pair"),
            }
    stages = ["sign_compatibility_template", "pair_dynamics", "signals", "llm_product_surface"]
    if scenario_tone is not None:
        stages.insert(-1, "scenario_tone")
    return {
        "orchestrator_version": ORCHESTRATOR_VERSION,
        "pipeline": PIPELINE_COMPATIBILITY,
        "stages": stages,
        "canon_ref": SOURCE_OF_TRUTH_REF,
        "relationship_context": relationship_context,
        "tone_mode": getattr(scenario_tone, "tone_mode", None) if scenario_tone else None,
        "format_id": getattr(scenario_tone, "format_id", None) if scenario_tone else None,
        "reasoning_trace": reasoning_trace,
        "merge_pass_contract": MERGE_PASS_CONTRACT,
        "merge_pass_steps": ["sanitize_copy", "blocks_roles_scenarios_merge"],
    }


def run_guidance_answer_pipeline(
    *,
    question: str,
    lane: str,
    spread_title: str,
    template_answer: dict[str, str],
    modular_profile: dict[str, Any],
    cards: list[Any],
    structural: dict[str, Any],
    question_assessment: dict[str, Any],
    today_context: str | None,
    locale: str | None,
    learning_service: Any | None = None,
    db: Any | None = None,
    user_id: int | None = None,
) -> dict[str, str] | None:
    """GE-1 v0.4: единая точка Guidance answer LLM (step1) + orchestration log."""
    from todayflow_backend.services.guidance_llm_pipeline import refine_guidance_session_answer

    return refine_guidance_session_answer(
        question=question,
        lane=lane,
        spread_title=spread_title,
        template_answer=template_answer,
        modular_profile=modular_profile,
        cards=cards,
        structural=structural,
        question_assessment=question_assessment,
        today_context=today_context,
        locale=locale,
        learning_service=learning_service,
        db=db,
        user_id=user_id,
    )


def run_guidance_clarification_pipeline(
    *,
    parent_question: str,
    clarification_goal: str,
    goal_label: str,
    template_answer: dict[str, str],
    modular_profile: dict[str, Any],
    cards: list[Any],
    parent_summary: str,
    locale: str | None,
    learning_service: Any | None = None,
    db: Any | None = None,
    user_id: int | None = None,
) -> dict[str, str] | None:
    """GE-1 v0.4: единая точка Guidance clarify LLM + orchestration log."""
    from todayflow_backend.services.guidance_llm_pipeline import refine_guidance_clarification_answer

    return refine_guidance_clarification_answer(
        parent_question=parent_question,
        clarification_goal=clarification_goal,
        goal_label=goal_label,
        template_answer=template_answer,
        modular_profile=modular_profile,
        cards=cards,
        parent_summary=parent_summary,
        locale=locale,
        learning_service=learning_service,
        db=db,
        user_id=user_id,
    )


def run_compatibility_dynamics_pipeline(
    db: Session | None,
    *,
    template_surface: Any,
    pair_display: str,
    user1_label: str,
    user2_label: str,
    relationship_context: str,
    pair_dynamics: dict[str, Any],
    signals: dict[str, Any],
    element_relation: str,
    rhythm_relation: str,
    block_feedback: dict[str, str] | None,
    user_id: int | None,
    locale: str = "ru",
    base_model_layer: dict[str, Any] | None = None,
    scenario_tone: Any | None = None,
    scenario_context: dict[str, Any] | None = None,
    compatibility_learning: dict[str, Any] | None = None,
) -> tuple[Any, str, dict[str, Any] | None]:
    """GE-1 v0.4: единая точка Compatibility dynamics LLM + orchestration log."""
    from todayflow_backend.services.compatibility_llm import generate_llm_product_surface

    return generate_llm_product_surface(
        db,
        template_surface=template_surface,
        pair_display=pair_display,
        user1_label=user1_label,
        user2_label=user2_label,
        relationship_context=relationship_context,
        pair_dynamics=pair_dynamics,
        signals=signals,
        element_relation=element_relation,
        rhythm_relation=rhythm_relation,
        block_feedback=block_feedback,
        user_id=user_id,
        locale=locale,
        base_model_layer=base_model_layer,
        scenario_tone=scenario_tone,
        scenario_context=scenario_context,
        compatibility_learning=compatibility_learning,
    )


def build_today_narrative_orchestration_meta(
    *,
    surface: str,
    day_ctx: dict[str, Any],
    profile_selector_slim: dict[str, Any] | None,
    profile_selector_full: dict[str, Any] | None,
    day_context_sha256: str,
) -> dict[str, Any]:
    """Снимок этапов до LLM для `POST /today/narrative` (расширяется по мере выделения шагов)."""

    layers = day_ctx.get("layers") if isinstance(day_ctx.get("layers"), dict) else {}
    dm = layers.get("day_model")
    gd = layers.get("guide_decision")

    stages: list[str] = [
        "intent_slice",
        "daily_foundation",
        "day_engine_brief",
        "behavior_patterns",
        "history_slice",
        "day_context_v0",
        "profile_selector",
    ]
    if isinstance(dm, dict) and dm.get("contract_version"):
        stages.append("day_model_v0")
    if isinstance(gd, dict) and gd.get("contract_version"):
        stages.append("guide_decision_v0")
    kcs = layers.get("knowledge_context_slice")
    kumt = layers.get("knowledge_usage_metrics_trace")
    if isinstance(kcs, dict):
        stages.append("knowledge_context_selection_a1_1")
    if layers.get("day_engine_knowledge_wiring"):
        stages.append("day_engine_knowledge_wiring_a1_3")
    if layers.get("profile_knowledge_personalization"):
        stages.append("profile_knowledge_personalization_a1_4")
    if isinstance(kumt, dict):
        stages.append("knowledge_usage_metrics_a1_7")
    stages.append(f"llm_surface:{surface}")
    stages.append("merge_pass_documented")

    reasoning_trace = _reasoning_trace_from_selector(profile_selector_full)
    dm_trace = _day_model_trace_from_layers(layers)
    if dm_trace is not None:
        if isinstance(reasoning_trace, dict):
            reasoning_trace = {**reasoning_trace, "day_model": dm_trace}
        else:
            reasoning_trace = {"day_model": dm_trace}
    merge_steps = narrative_merge_pass_plan(surface)

    knowledge_summary = None
    if isinstance(kumt, dict):
        from todayflow_backend.services.day_model_v1_narrative_knowledge_hot_path import (
            slim_knowledge_usage_metrics_for_log,
        )

        knowledge_summary = slim_knowledge_usage_metrics_for_log(kumt)

    return {
        "orchestrator_version": ORCHESTRATOR_VERSION,
        "pipeline": PIPELINE_TODAY_NARRATIVE,
        "stages": stages,
        "day_context_contract_version": day_ctx.get("contract_version"),
        "day_context_sha256": day_context_sha256,
        "has_day_model": isinstance(dm, dict),
        "has_guide_decision": isinstance(gd, dict),
        "has_profile_selector": bool(profile_selector_slim),
        "has_knowledge_hot_path": isinstance(kumt, dict),
        "knowledge_usage_metrics_summary": knowledge_summary,
        "reasoning_trace": reasoning_trace,
        "canon_ref": SOURCE_OF_TRUTH_REF,
        "merge_pass_contract": MERGE_PASS_CONTRACT,
        "merge_pass_steps": merge_steps,
        "primary_narrative_anchor": "day_engine_brief",
    }


def attach_amll_gate_to_orchestration(
    orchestration: dict[str, Any] | None,
    amll_gate: dict[str, Any],
) -> dict[str, Any]:
    """Attach AMLL Gate v1 decision trace to orchestration meta (GE-1 / AMLL §2)."""
    out = dict(orchestration) if isinstance(orchestration, dict) else {}
    out["amll_gate"] = amll_gate
    out["gate_decision"] = amll_gate.get("gate_decision")
    return out


def attach_pim_read_audit_to_orchestration(
    orchestration_meta: dict[str, Any],
    *,
    day_ctx: dict[str, Any],
    ritual_context: dict[str, Any] | None,
    fusion_dump: dict[str, Any] | None,
) -> dict[str, Any]:
    """PR1 — merge PIM read audit into orchestration log (Experience → PIM path)."""
    from todayflow_backend.services.today_pim_read_audit_v1 import build_pim_read_audit_v1

    audit = build_pim_read_audit_v1(
        day_ctx=day_ctx,
        ritual_context=ritual_context,
        fusion_dump=fusion_dump,
    )
    out = dict(orchestration_meta)
    out["pim_read_audit"] = audit
    return out


def run_today_narrative_pipeline(
    db: Session,
    *,
    user_id: int,
    insight_depth_tier: str,
    target_date: date,
    locale: str,
    surface: Any,
    core_profile: dict[str, Any] | None,
    fusion_dump: dict[str, Any],
    parent_generation_id: int | None,
    deepen_topic: str | None,
    policy_version: str | None = "clean-info-v1",
    voice_profile: str | None = "live-clean-supportive-v1",
    ritual_context: dict[str, Any] | None = None,
    depth_level: str | None = None,
) -> tuple[dict[str, Any], int, bool, dict[str, Any] | None]:
    """Единая точка входа API для Today narrative; внутри — существующий `build_today_narrative`."""

    from todayflow_backend.services.today_narrative import build_today_narrative

    return build_today_narrative(
        db,
        user_id=user_id,
        insight_depth_tier=insight_depth_tier,
        target_date=target_date,
        locale=locale,
        surface=surface,
        core_profile=core_profile,
        fusion_dump=fusion_dump,
        parent_generation_id=parent_generation_id,
        deepen_topic=deepen_topic,
        policy_version=policy_version,
        voice_profile=voice_profile,
        ritual_context=ritual_context,
        depth_level=depth_level,
    )

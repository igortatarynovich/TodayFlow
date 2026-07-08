"""DayContext v0 — единый пакет входа Day Engine (сборка фактов дня для narrative / explain)."""

from __future__ import annotations

from datetime import date
from typing import Any

from todayflow_backend.profile_engine.models import (
    ProfileContextSelectorInput,
    ProfilePromptSurface,
    ProfileTaskType,
    ProfileTopicDomain,
)
from todayflow_backend.profile_engine.selector import select_profile_context


def build_day_context_v0(
    *,
    target_date: date,
    locale: str,
    insight_depth_tier: str,
    core_profile: dict[str, Any] | None,
    fusion_dump: dict[str, Any],
    daily_foundation: dict[str, Any] | None = None,
    ritual_context: dict[str, Any] | None = None,
    behavior_patterns: dict[str, Any] | None = None,
    intent_slice: dict[str, Any] | None = None,
    history_slice: dict[str, Any] | None = None,  # DE-9: `day_history_v0` из `history_layer_v0`
    policy_version: str = "clean-info-v1",
    voice_profile: str = "live-clean-supportive-v1",
    profile_snapshot_id: int | None = None,
    ritual_context_fingerprint: str = "",
    depth_level: str = "normal",
    selector_surface: ProfilePromptSurface = ProfilePromptSurface.TODAY,
    selector_task: ProfileTaskType | None = None,
    selector_topic: ProfileTopicDomain | None = None,
    active_knowledge_list: list[dict[str, Any]] | None = None,
    evolution_stage: str | None = None,
    goals: list[dict[str, Any]] | None = None,
    practices: list[dict[str, Any]] | None = None,
    knowledge_target_surface: str = "day_guidance_card",
) -> dict[str, Any]:
    """
    Собирает объект, соответствующий docs/schemas/day_context_v0.schema.json.

    Не вызывает LLM и не пишет в БД. Вызывается из `build_today_narrative` перед всеми surface;
    для отладки и будущего публичного API (паритет web/iOS по полям).
    """
    # Lazy import avoids circular import: today_narrative may import this module.
    from todayflow_backend.services.day_model_v0 import build_day_model_v0
    from todayflow_backend.services.guide_decision_v0 import build_guide_decision_v0
    from todayflow_backend.services.profile_prompt_slices_v0 import (
        build_internal_profile_slice_v0,
        build_visible_profile_slice_v0,
    )
    from todayflow_backend.services.today_narrative import _core_context_for_narrative, _normalize_ritual_context

    tier = (insight_depth_tier or "free").strip().lower()
    if tier not in ("free", "pro", "premium"):
        tier = "free"
    loc = (locale or "ru").strip()[:32] or "ru"

    fusion: dict[str, Any] = dict(fusion_dump) if isinstance(fusion_dump, dict) else {}
    if not isinstance(fusion.get("scores"), dict):
        fusion["scores"] = {}
    if not isinstance(fusion.get("cycle_context"), dict):
        fusion["cycle_context"] = {}
    if not isinstance(fusion.get("activity_context"), dict):
        fusion["activity_context"] = {}
    if not isinstance(fusion.get("rhythm_context"), dict):
        fusion["rhythm_context"] = {}
    recs = fusion.get("recommendations")
    if not isinstance(recs, list):
        fusion["recommendations"] = []
    if fusion.get("encouragement") is None:
        fusion["encouragement"] = ""
    fusion["date"] = str(fusion.get("date") or target_date.isoformat())

    ritual = _normalize_ritual_context(ritual_context)
    user_core = _core_context_for_narrative(core_profile, locale=loc)

    bp = behavior_patterns if isinstance(behavior_patterns, dict) and behavior_patterns else None
    intent = intent_slice if isinstance(intent_slice, dict) and intent_slice.get("contract_version") else None
    hist: dict[str, Any] | None = None
    if isinstance(history_slice, dict) and history_slice.get("contract_version") == "day_history_v0":
        hist = history_slice
    layers: dict[str, Any] = {
        "fusion": fusion,
        "user_core": user_core,
        "daily_foundation": daily_foundation if isinstance(daily_foundation, dict) else None,
        "behavior_patterns": bp,
        "history": hist,
        "intent": intent,
        "health_signals": None,
    }
    if ritual:
        layers["ritual"] = ritual

    vp = build_visible_profile_slice_v0(
        core_profile=core_profile if isinstance(core_profile, dict) else None,
        intent_slice=intent,
        ritual=ritual if ritual else None,
        fusion_layer=fusion,
        locale=loc,
    )
    ip = build_internal_profile_slice_v0(
        core_profile=core_profile if isinstance(core_profile, dict) else None,
        behavior_patterns=bp,
        fusion_layer=fusion,
    )
    if vp is not None:
        layers["visible_profile"] = vp
    if ip is not None:
        layers["internal_profile"] = ip

    sel_inp = ProfileContextSelectorInput(
        surface=selector_surface,
        task=selector_task,
        topic=selector_topic,
        locale=loc,
    )
    layers["profile_selector"] = select_profile_context(
        sel_inp,
        core_profile=core_profile if isinstance(core_profile, dict) else None,
        fusion_dump=fusion,
        ritual_context=ritual if ritual else None,
        behavior_patterns=bp,
        history_slice=hist,
    ).model_dump(mode="json")

    layers["day_model"] = build_day_model_v0(
        foundation=daily_foundation if isinstance(daily_foundation, dict) else None,
        ritual=ritual if ritual else None,
        fusion_scores=fusion.get("scores") if isinstance(fusion.get("scores"), dict) else {},
        intent_slice=intent,
        internal_profile=ip if isinstance(ip, dict) else None,
        locale=loc,
        history_slice=hist,
    )
    layers["guide_decision"] = build_guide_decision_v0(
        day_model=layers["day_model"],
        ritual=ritual if ritual else None,
        foundation=daily_foundation if isinstance(daily_foundation, dict) else None,
        user_core=user_core,
        fusion_scores=fusion.get("scores") if isinstance(fusion.get("scores"), dict) else {},
        locale=loc,
    )

    if active_knowledge_list is not None:
        from todayflow_backend.services.day_model_v1_day_engine_knowledge_wiring import (
            wire_active_knowledge_into_day_context_layers,
        )

        wire_active_knowledge_into_day_context_layers(
            layers,
            active_knowledge_list,
            day_context={
                "surface": knowledge_target_surface,
                "content_keys": [],
            },
            goals=goals,
            practices=practices,
            evolution_stage=evolution_stage,
            target_surface=knowledge_target_surface,
        )

        from todayflow_backend.services.day_model_v1_profile_knowledge_personalization import (
            wire_profile_knowledge_into_day_context_layers,
        )

        wire_profile_knowledge_into_day_context_layers(layers)

        from todayflow_backend.services.day_model_v1_knowledge_usage_metrics import (
            wire_knowledge_usage_metrics_into_day_context_layers,
        )

        wire_knowledge_usage_metrics_into_day_context_layers(
            layers,
            pool_count=len(active_knowledge_list),
            target_surface=knowledge_target_surface,
        )

    _dl = (depth_level or "normal").strip().lower()
    depth = _dl if _dl in ("quick", "normal", "deep") else "normal"
    meta: dict[str, Any] = {
        "target_date": target_date.isoformat(),
        "locale": loc,
        "insight_depth_tier": tier,
        "depth_level": depth,
        "policy_version": (policy_version or "clean-info-v1").strip()[:64],
        "voice_profile": (voice_profile or "live-clean-supportive-v1").strip()[:64],
    }
    if profile_snapshot_id is not None:
        meta["profile_snapshot_id"] = int(profile_snapshot_id)
    fp = (ritual_context_fingerprint or "").strip()[:64]
    if fp:
        meta["ritual_context_fingerprint"] = fp

    return {
        "contract_version": "day_context_v0",
        "meta": meta,
        "layers": layers,
    }

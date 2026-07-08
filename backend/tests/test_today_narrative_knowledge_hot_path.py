"""A1.8 — Hot path wiring in build_today_narrative tests."""

from __future__ import annotations

from datetime import date

from todayflow_backend.db import models as db_models
from todayflow_backend.services import today_narrative as today_narrative_service
from todayflow_backend.services.day_model_v1_active_knowledge import (
    DAY_ACTIVE_KNOWLEDGE_V1_CONTRACT,
)
from todayflow_backend.services.day_model_v1_active_knowledge_loader import (
    upsert_user_active_knowledge_v1,
)
from todayflow_backend.services.day_model_v1_knowledge_candidate import (
    KNOWLEDGE_TYPE_RESPONSE_STYLE,
)
from todayflow_backend.services.day_model_v1_narrative_knowledge_hot_path import (
    narrative_surface_to_knowledge_target,
)
from todayflow_backend.services.today_narrative import build_today_narrative


def _active(**overrides):
    base = {
        "contract_version": DAY_ACTIVE_KNOWLEDGE_V1_CONTRACT,
        "knowledge_id": "know-hot-001",
        "source_knowledge_candidate_id": "kcand-hot-001",
        "knowledge_type": KNOWLEDGE_TYPE_RESPONSE_STYLE,
        "claim": "responds_to_surface:short_action",
        "confidence": 0.8,
        "evidence_count": 7,
        "evidence_window_days": 21,
        "evidence_signal_ids": [f"lsig-{i}" for i in range(7)],
        "source_pattern_id": "pat-hot-001",
        "status": "active",
        "created_at": "2026-05-31T12:00:00Z",
        "last_confirmed_at": "2026-05-31T12:00:00Z",
        "expires_at": None,
        "review_required": False,
        "profile_update_allowed": False,
        "memory_update_allowed": False,
        "ranking_update_allowed": False,
    }
    base.update(overrides)
    return base


def test_narrative_surface_mapping():
    assert narrative_surface_to_knowledge_target("guide") == "day_guidance_card"
    assert narrative_surface_to_knowledge_target("evening") == "reflection_card"


def test_build_today_narrative_without_active_knowledge_unchanged(db_session, monkeypatch):
    monkeypatch.setattr(today_narrative_service, "_openai_json", lambda *_a, **_k: None)

    user = db_models.User(email="hot-path-none@example.com", password_hash="x")
    db_session.add(user)
    db_session.commit()

    _, generation_id, _, _ = build_today_narrative(
        db_session,
        user_id=user.id,
        insight_depth_tier="free",
        target_date=date(2026, 5, 31),
        locale="ru",
        surface="guide",
        core_profile={},
        fusion_dump={"scores": {"energy": 50}, "encouragement": "ok"},
        parent_generation_id=None,
        deepen_topic=None,
    )

    log = db_session.query(db_models.GenerationLog).filter_by(id=generation_id).first()
    assert log is not None
    assert "knowledge_hot_path_active" not in (log.input_payload or {})


def test_build_today_narrative_wires_knowledge_hot_path(db_session, monkeypatch):
    monkeypatch.setattr(today_narrative_service, "_openai_json", lambda *_a, **_k: None)

    user = db_models.User(email="hot-path-ak@example.com", password_hash="x")
    db_session.add(user)
    db_session.commit()

    upsert_user_active_knowledge_v1(
        db_session, user_id=user.id, active_knowledge=_active()
    )

    payload, generation_id, _, _ = build_today_narrative(
        db_session,
        user_id=user.id,
        insight_depth_tier="free",
        target_date=date(2026, 5, 31),
        locale="ru",
        surface="guide",
        core_profile={},
        fusion_dump={"scores": {"energy": 55}, "encouragement": "ok"},
        parent_generation_id=None,
        deepen_topic=None,
    )

    log = db_session.query(db_models.GenerationLog).filter_by(id=generation_id).first()
    assert log is not None
    ip = log.input_payload or {}
    assert ip.get("knowledge_hot_path_active") is True
    assert ip.get("knowledge_target_surface") == "day_guidance_card"

    metrics = ip.get("knowledge_usage_metrics_trace")
    assert isinstance(metrics, dict)
    minimum = metrics.get("minimum_metrics")
    assert isinstance(minimum, dict)
    assert minimum.get("knowledge_pool_size") == 1
    assert minimum.get("personalization_summary_lines") >= 1
    assert metrics["selection_metrics"]["pool_count"] == 1
    assert metrics["personalization_metrics"]["summary_fact_count"] >= 1

    orch = ip.get("orchestration") or {}
    assert orch.get("has_knowledge_hot_path") is True
    assert isinstance(orch.get("knowledge_usage_metrics_summary"), dict)

    gd = payload.get("guide_decision")
    assert isinstance(gd, dict)
    assert isinstance(gd.get("knowledge_hints"), dict)

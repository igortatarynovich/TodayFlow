"""DE-13 v3: funnel artifact chain into child narrative surfaces."""

from __future__ import annotations

from datetime import date

import json

import pytest
from sqlalchemy.orm import Session

from todayflow_backend.db import models as db_models
from todayflow_backend.services.guide_narrative_funnel_v0 import (
    FUNNEL_CHILD_CHAIN_CONTRACT,
    FUNNEL_PROMPT_VER_STEP1,
    slim_funnel_interpretation_for_child,
)
from todayflow_backend.services import today_narrative as today_narrative_service
from todayflow_backend.services.today_narrative import (
    MODULE,
    _resolve_funnel_chain_from_guide_parent,
)
from tests.test_guide_narrative_funnel_v0 import _interp_ok, _sat_ok


def test_slim_funnel_interpretation_for_child_keeps_core_fields() -> None:
    slim = slim_funnel_interpretation_for_child(_interp_ok())
    assert slim is not None
    assert slim.get("contract_version") == "guide_funnel_interpretation_v0"
    assert slim.get("what_happens")
    assert isinstance(slim.get("why_layers"), list)


def test_resolve_funnel_chain_from_guide_parent_success(db_session: Session) -> None:
    db_models.GenerationLog.__table__.create(bind=db_session.get_bind(), checkfirst=True)
    user = db_models.User(email="funnel-child@example.com", password_hash="x")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    step1 = db_models.GenerationLog(
        user_id=user.id,
        module=MODULE,
        surface="guide_funnel_v0",
        status="success",
        model="test",
        normalized_response=_interp_ok(),
        input_payload={
            "target_date": "2026-07-03",
            "narrative_funnel_step": "interpretation_v0",
            "funnel_prompt_ver": FUNNEL_PROMPT_VER_STEP1,
        },
    )
    db_session.add(step1)
    db_session.commit()
    db_session.refresh(step1)

    guide_payload = {
        "headline": "Один фокус на день без распыления по параллельным стартам.",
        "context_for_next_surfaces": (
            "Тезис дня: сузиться и завершить одну линию. Сферы и углубление продолжают эту ось без нового приоритета."
        ),
        **_sat_ok(),
    }
    guide = db_models.GenerationLog(
        user_id=user.id,
        module=MODULE,
        surface="guide",
        status="success",
        model="test",
        normalized_response=guide_payload,
        input_payload={
            "guide_funnel_used": True,
            "guide_funnel_parent_log_id": step1.id,
            "guide_funnel_step2_log_id": 999,
        },
    )
    db_session.add(guide)
    db_session.commit()
    db_session.refresh(guide)

    chain = _resolve_funnel_chain_from_guide_parent(db_session, user.id, guide, guide_payload)
    assert chain is not None
    assert chain.get("contract_version") == FUNNEL_CHILD_CHAIN_CONTRACT
    assert chain.get("guide_funnel_step1_log_id") == step1.id
    assert chain.get("guide_funnel_step2_log_id") == 999
    assert chain.get("funnel_interpretation", {}).get("one_concrete_move")


def test_child_surface_user_json_includes_funnel_chain(db_session: Session, monkeypatch) -> None:
    captured: dict[str, str] = {}

    def capture_openai(system: str, user: str, **_kwargs) -> dict | None:
        captured["system"] = system
        captured["user"] = user
        return None

    monkeypatch.setattr(today_narrative_service, "_openai_json", capture_openai)
    db_models.PromptVersion.__table__.create(bind=db_session.get_bind(), checkfirst=True)
    db_models.GenerationLog.__table__.create(bind=db_session.get_bind(), checkfirst=True)

    user = db_models.User(email="funnel-child-dl@example.com", password_hash="x")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    step1 = db_models.GenerationLog(
        user_id=user.id,
        module=MODULE,
        surface="guide_funnel_v0",
        status="success",
        model="test",
        normalized_response=_interp_ok(),
        input_payload={"narrative_funnel_step": "interpretation_v0"},
    )
    db_session.add(step1)
    db_session.commit()
    db_session.refresh(step1)

    guide_payload = {
        "headline": "Один фокус на день без распыления по параллельным стартам.",
        "context_for_next_surfaces": (
            "Тезис дня: сузиться и завершить одну линию. Сферы и углубление продолжают эту ось без нового приоритета."
        ),
    }
    guide = db_models.GenerationLog(
        user_id=user.id,
        module=MODULE,
        surface="guide",
        status="success",
        model="test",
        normalized_response=guide_payload,
        input_payload={
            "guide_funnel_used": True,
            "guide_funnel_parent_log_id": step1.id,
        },
    )
    db_session.add(guide)
    db_session.commit()
    db_session.refresh(guide)

    _, gen_id, _, _ = today_narrative_service.build_today_narrative(
        db_session,
        user_id=user.id,
        insight_depth_tier="free",
        target_date=date(2026, 7, 3),
        locale="ru",
        surface="day_layer",
        core_profile={},
        fusion_dump={"scores": {"energy": 50}, "encouragement": "ok"},
        parent_generation_id=guide.id,
        deepen_topic=None,
    )

    u = json.loads(captured["user"])
    assert u.get("funnel_interpretation", {}).get("contract_version") == "guide_funnel_interpretation_v0"
    assert u.get("context_for_next_surfaces")
    assert "funnel_interpretation" in captured.get("system", "")

    log = db_session.query(db_models.GenerationLog).filter(db_models.GenerationLog.id == gen_id).first()
    assert log is not None
    assert log.input_payload.get("guide_funnel_chain_used") is True
    assert log.input_payload.get("guide_funnel_step1_log_id") == step1.id

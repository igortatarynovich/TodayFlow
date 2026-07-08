"""DE-13 v2: per-step funnel cache lookup in today_narrative."""

from __future__ import annotations

from datetime import date

import pytest
from sqlalchemy.orm import Session

from todayflow_backend.db import models as db_models
from todayflow_backend.services.guide_narrative_funnel_v0 import (
    FUNNEL_PROMPT_VER_STEP1,
    FUNNEL_PROMPT_VER_STEP2,
)
from todayflow_backend.services.today_narrative import MODULE, _load_funnel_step_cache
from tests.test_guide_narrative_funnel_v0 import _interp_ok, _sat_ok


def _interp_response() -> dict:
    return _interp_ok()


def _sat_response() -> dict:
    return _sat_ok()


@pytest.fixture
def funnel_user(db_session: Session) -> db_models.User:
    user = db_models.User(email="funnel-cache@example.com", password_hash="x", is_paid=False)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def _base_input(*, target: str, step: str, prompt_ver: str, sha: str, parent_id: int | None = None) -> dict:
    payload = {
        "target_date": target,
        "narrative_funnel_step": step,
        "funnel_prompt_ver": prompt_ver,
        "locale": "ru",
        "ritual_context_fp": "ritual-fp-1",
        "intent_context_fp": "intent-fp-1",
        "insight_depth_tier": "free",
        "depth_level": "normal",
        "day_context_sha256": sha,
    }
    if parent_id is not None:
        payload["parent_generation_log_id"] = parent_id
    return payload


def test_load_funnel_step_cache_step1_match(db_session: Session, funnel_user: db_models.User) -> None:
    db_models.GenerationLog.__table__.create(bind=db_session.get_bind(), checkfirst=True)
    target = date(2026, 7, 3)
    sha = "abc123"
    log = db_models.GenerationLog(
        user_id=funnel_user.id,
        module=MODULE,
        surface="guide_funnel_v0",
        status="success",
        model="test",
        normalized_response=_interp_response(),
        input_payload=_base_input(
            target=target.isoformat(),
            step="interpretation_v0",
            prompt_ver=FUNNEL_PROMPT_VER_STEP1,
            sha=sha,
        ),
    )
    db_session.add(log)
    db_session.commit()

    hit = _load_funnel_step_cache(
        db_session,
        funnel_user.id,
        target,
        funnel_step="interpretation_v0",
        funnel_prompt_ver=FUNNEL_PROMPT_VER_STEP1,
        snapshot_id=None,
        tier_norm="free",
        depth_norm="normal",
        locale="ru",
        ritual_fp="ritual-fp-1",
        intent_fp="intent-fp-1",
        day_context_sha256=sha,
    )
    assert hit is not None
    assert hit.id == log.id


def test_load_funnel_step_cache_step1_reuses_on_sha_drift(
    db_session: Session, funnel_user: db_models.User
) -> None:
    """Same-day reuse: `day_context_sha256` drift (fusion/history moves as the user
    interacts) must NOT force a miss, otherwise the narrative regenerates on every
    visit. Stable key (date/step/prompt_ver/locale/ritual_fp/intent_fp/tier/depth)
    still matches, so the prior step output is reused."""
    db_models.GenerationLog.__table__.create(bind=db_session.get_bind(), checkfirst=True)
    target = date(2026, 7, 3)
    log = db_models.GenerationLog(
        user_id=funnel_user.id,
        module=MODULE,
        surface="guide_funnel_v0",
        status="success",
        model="test",
        normalized_response=_interp_response(),
        input_payload=_base_input(
            target=target.isoformat(),
            step="interpretation_v0",
            prompt_ver=FUNNEL_PROMPT_VER_STEP1,
            sha="old-sha",
        ),
    )
    db_session.add(log)
    db_session.commit()

    hit = _load_funnel_step_cache(
        db_session,
        funnel_user.id,
        target,
        funnel_step="interpretation_v0",
        funnel_prompt_ver=FUNNEL_PROMPT_VER_STEP1,
        snapshot_id=None,
        tier_norm="free",
        depth_norm="normal",
        locale="ru",
        ritual_fp="ritual-fp-1",
        intent_fp="intent-fp-1",
        day_context_sha256="new-sha",
    )
    assert hit is not None
    assert hit.id == log.id


def test_load_funnel_step_cache_step1_miss_on_ritual_change(
    db_session: Session, funnel_user: db_models.User
) -> None:
    """A change in the *stable* key (here ritual_fp) still yields a miss — meaningful
    inputs correctly trigger regeneration, unlike volatile fusion/history drift."""
    db_models.GenerationLog.__table__.create(bind=db_session.get_bind(), checkfirst=True)
    target = date(2026, 7, 3)
    log = db_models.GenerationLog(
        user_id=funnel_user.id,
        module=MODULE,
        surface="guide_funnel_v0",
        status="success",
        model="test",
        normalized_response=_interp_response(),
        input_payload=_base_input(
            target=target.isoformat(),
            step="interpretation_v0",
            prompt_ver=FUNNEL_PROMPT_VER_STEP1,
            sha="old-sha",
        ),
    )
    db_session.add(log)
    db_session.commit()

    miss = _load_funnel_step_cache(
        db_session,
        funnel_user.id,
        target,
        funnel_step="interpretation_v0",
        funnel_prompt_ver=FUNNEL_PROMPT_VER_STEP1,
        snapshot_id=None,
        tier_norm="free",
        depth_norm="normal",
        locale="ru",
        ritual_fp="ritual-fp-CHANGED",
        intent_fp="intent-fp-1",
        day_context_sha256="old-sha",
    )
    assert miss is None


def test_load_funnel_step_cache_step2_requires_parent(
    db_session: Session, funnel_user: db_models.User
) -> None:
    db_models.GenerationLog.__table__.create(bind=db_session.get_bind(), checkfirst=True)
    target = date(2026, 7, 3)
    sha = "sha-step2"
    parent = db_models.GenerationLog(
        user_id=funnel_user.id,
        module=MODULE,
        surface="guide_funnel_v0",
        status="success",
        model="test",
        normalized_response=_interp_response(),
        input_payload=_base_input(
            target=target.isoformat(),
            step="interpretation_v0",
            prompt_ver=FUNNEL_PROMPT_VER_STEP1,
            sha=sha,
        ),
    )
    db_session.add(parent)
    db_session.commit()
    db_session.refresh(parent)

    child = db_models.GenerationLog(
        user_id=funnel_user.id,
        module=MODULE,
        surface="guide_funnel_v0",
        status="success",
        model="test",
        normalized_response=_sat_response(),
        input_payload=_base_input(
            target=target.isoformat(),
            step="satellites_v0",
            prompt_ver=FUNNEL_PROMPT_VER_STEP2,
            sha=sha,
            parent_id=parent.id,
        ),
    )
    db_session.add(child)
    db_session.commit()

    hit = _load_funnel_step_cache(
        db_session,
        funnel_user.id,
        target,
        funnel_step="satellites_v0",
        funnel_prompt_ver=FUNNEL_PROMPT_VER_STEP2,
        snapshot_id=None,
        tier_norm="free",
        depth_norm="normal",
        locale="ru",
        ritual_fp="ritual-fp-1",
        intent_fp="intent-fp-1",
        day_context_sha256=sha,
        parent_generation_log_id=parent.id,
    )
    assert hit is not None
    assert hit.id == child.id

    wrong_parent = _load_funnel_step_cache(
        db_session,
        funnel_user.id,
        target,
        funnel_step="satellites_v0",
        funnel_prompt_ver=FUNNEL_PROMPT_VER_STEP2,
        snapshot_id=None,
        tier_norm="free",
        depth_norm="normal",
        locale="ru",
        ritual_fp="ritual-fp-1",
        intent_fp="intent-fp-1",
        day_context_sha256=sha,
        parent_generation_log_id=parent.id + 999,
    )
    assert wrong_parent is None

"""Shared Global Day: key = local_date + locale + semantic_version. No user in identity."""

from __future__ import annotations

from datetime import date
from unittest.mock import patch

from todayflow_backend.db import models as db_models
from todayflow_backend.services.day_scenario_native_llm_c1 import (
    normalize_native_scenario_llm_c1,
)
from todayflow_backend.services.native_c1_i0_generation_split_v1 import enforce_global_only
from todayflow_backend.services.shared_global_day_v1 import (
    GLOBAL_DAY_SEMANTIC_VERSION,
    MODULE,
    SURFACE,
    global_day_key,
    load_shared_global_day,
    save_shared_global_day,
)
from tests.test_native_c1_i0_generation_split_v1 import _global_native


def _artifact() -> dict:
    return enforce_global_only(normalize_native_scenario_llm_c1(_global_native()))


def test_global_day_key_excludes_user_and_expression():
    a = global_day_key(local_date="2026-08-25", locale="ru")
    b = global_day_key(local_date=date(2026, 8, 25), locale="RU")
    c = global_day_key(local_date="2026-08-25", locale="en")
    d = global_day_key(
        local_date="2026-08-25",
        locale="ru",
        semantic_version="global-day-semantic.v2",
    )
    assert a == b
    assert a != c
    assert a != d
    blob = str(
        {
            "local_date": "2026-08-25",
            "locale": "ru",
            "semantic_version": GLOBAL_DAY_SEMANTIC_VERSION,
        }
    )
    assert "user_id" not in blob
    assert "profile_hash" not in blob
    assert "expression" not in blob
    same_users_would_share = global_day_key(local_date="2026-08-25", locale="ru")
    assert same_users_would_share == a


def test_save_load_roundtrip_and_force_rebuild_keeps_key(db_session):
    day = date(2026, 8, 25)
    art = _artifact()
    key1 = save_shared_global_day(
        db_session, local_date=day, locale="ru", artifact=art, force_rebuild=False
    )
    loaded = load_shared_global_day(db_session, local_date=day, locale="ru")
    assert loaded is not None
    assert loaded["conflict"]["title"] == art["conflict"]["title"]

    key2 = save_shared_global_day(
        db_session, local_date=day, locale="ru", artifact=art, force_rebuild=True
    )
    assert key1 == key2
    rows = (
        db_session.query(db_models.GenerationLog)
        .filter(
            db_models.GenerationLog.module == MODULE,
            db_models.GenerationLog.surface == SURFACE,
            db_models.GenerationLog.user_id.is_(None),
        )
        .order_by(db_models.GenerationLog.id.asc())
        .all()
    )
    assert len(rows) == 2
    assert rows[0].input_payload["global_day_key"] == rows[1].input_payload["global_day_key"]
    assert rows[0].input_payload["ledger"] == "product"
    assert rows[1].input_payload["ledger"] == "engineering"
    assert rows[1].input_payload["force_rebuild"] is True


def _native_payload() -> dict:
    return {
        "locale": "ru",
        "target_date": "2026-08-25",
        "interpretation": {
            "target_date": "2026-08-25",
            "locale": "ru",
            "day_thesis": {
                "family": "momentum",
                "variant": "steady",
                "mode": "stability",
                "label_ru": "Ось",
                "driver_ids": ["moon-pisces"],
            },
            "day_events_pack": {"ranked_drivers": [{"id": "moon-pisces"}]},
        },
    }


def test_second_user_reuses_shared_global_without_new_key(db_session):
    art = _artifact()
    global_norm = art
    orch_calls: list[dict] = []

    def fake_orch(**kwargs):
        orch_calls.append(kwargs)
        cached = kwargs.get("cached_global_norm")
        accepted = kwargs.get("on_global_accepted")
        if cached:
            return (
                cached,
                [{"stage": "global", "status": "shared_hit"}],
                {
                    "i0_split": True,
                    "stages_run": ["global"],
                    "personal_skipped": True,
                    "personal_degraded": False,
                    "shared_global_hit": True,
                },
            )
        if accepted is not None:
            accepted(global_norm)
        return (
            global_norm,
            [{"stage": "global", "status": "accepted_global"}],
            {
                "i0_split": True,
                "stages_run": ["global"],
                "personal_skipped": True,
                "personal_degraded": False,
                "shared_global_hit": False,
            },
        )

    with (
        patch(
            "todayflow_backend.services.day_scenario_native_llm_c1.is_llm_chat_configured",
            return_value=True,
        ),
        patch(
            "todayflow_backend.services.day_scenario_native_llm_c1.get_openai_compatible_client",
            return_value=object(),
        ),
        patch(
            "todayflow_backend.services.native_c1_i0_generation_split_v1.orchestrate_i0_split_generation",
            side_effect=fake_orch,
        ),
        patch(
            "todayflow_backend.services.day_story_capture_session_v0.get_day_story_capture_session",
            return_value=None,
        ),
    ):
        from todayflow_backend.services.day_scenario_native_llm_c1 import (
            call_day_scenario_native_llm_c1,
        )

        interp = _native_payload()["interpretation"]
        ritual = {"tarot_name_ru": "Отшельник", "numerology_value": 7}
        first = call_day_scenario_native_llm_c1(
            _native_payload(),
            interpretation=interp,
            ritual_context=ritual,
            max_attempts=1,
            db=db_session,
            local_date=date(2026, 8, 25),
            locale="ru",
        )
        second = call_day_scenario_native_llm_c1(
            _native_payload(),
            interpretation=interp,
            ritual_context=ritual,
            max_attempts=1,
            db=db_session,
            local_date=date(2026, 8, 25),
            locale="ru",
        )
        assert first is not None
        assert second is not None
        assert orch_calls[0]["cached_global_norm"] is None
        assert orch_calls[0]["on_global_accepted"] is not None
        assert orch_calls[1]["cached_global_norm"] is not None
        assert orch_calls[1]["on_global_accepted"] is None
        assert orch_calls[1]["cached_global_norm"]["conflict"]["title"] == art["conflict"]["title"]

        forced = call_day_scenario_native_llm_c1(
            _native_payload(),
            interpretation=interp,
            ritual_context=ritual,
            max_attempts=1,
            db=db_session,
            local_date=date(2026, 8, 25),
            locale="ru",
            force_global_rebuild=True,
        )
        assert forced is not None
        assert orch_calls[2]["cached_global_norm"] is None
        assert orch_calls[2]["on_global_accepted"] is not None
        keys = {
            row.input_payload["global_day_key"]
            for row in db_session.query(db_models.GenerationLog)
            .filter(db_models.GenerationLog.surface == SURFACE)
            .all()
        }
        assert len(keys) == 1
        assert keys == {global_day_key(local_date="2026-08-25", locale="ru")}

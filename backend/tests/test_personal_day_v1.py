"""Personal Day lifecycle: identity, persist/reuse, 402, force rebuild, GET miss."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from unittest.mock import patch

from fastapi.testclient import TestClient

from todayflow_backend.db.models import GenerationLog, User
from todayflow_backend.services.day_story_fingerprint_v1 import (
    build_fingerprint_payload,
    compute_day_story_fingerprint,
)
from todayflow_backend.services.day_story_v1 import DAY_STORY_V1_CONTRACT
from todayflow_backend.services.day_story_wire_v1 import (
    MODULE,
    SURFACE,
    _build_day_story_record,
    _load_cached_day_story,
)
from todayflow_backend.services.personal_day_v1 import (
    PERSONAL_DAY_SEMANTIC_VERSION,
    is_reusable_personal_payload,
    personal_day_key,
    personal_day_ledger,
)
from tests.conftest import login_bearer_token
from tests.test_native_c1_i0_generation_split_v1 import _global_native
from todayflow_backend.services.day_scenario_native_llm_c1 import (
    native_llm_to_day_scenario_v1,
)


def _fake_native_success(*_args, meta_out=None, **kwargs):
    if isinstance(meta_out, dict):
        meta_out["success"] = True
        meta_out["attempt_count"] = 3
        meta_out["model"] = "test-model"
        meta_out["failure_class"] = None
    native = native_llm_to_day_scenario_v1(
        _global_native(),
        interpretation=kwargs.get("interpretation"),
        ritual_context=kwargs.get("ritual_context"),
        celestial_events=kwargs.get("celestial_events"),
    )
    assert native.get("ready") and native.get("scenes")
    native["generation_source"] = "native_llm_c1"
    return native


def _user(db, uid: int = 91) -> User:
    u = User(id=uid, email=f"personal-day-{uid}@test.local", password_hash="x")
    db.add(u)
    db.commit()
    return u


def _ready_story(theme: str = "Прояснение против сглаживания") -> dict:
    return {
        "contract_version": DAY_STORY_V1_CONTRACT,
        "theme": theme,
        "direction": "Назвать точно.",
        "story": "Короткий сюжет дня без формул.",
        "expect": "Ожидание дня: ясная формулировка.",
        "trap": "Ловушка: согласиться ради тишины.",
        "primary_conflict": theme,
        "development_point": "Одна точная фраза вместо сглаживания.",
        "primary_action": "Написать черновик и отправить.",
        "today_move": "Написать черновик и отправить.",
        "global_period": "День прояснения.",
        "do": ["Написать черновик"],
        "avoid": ["Сгладить смысл"],
        "domains": {
            "relationships": {
                "status": "Близкий ждёт ясности.",
                "opportunity": "Одно короткое сообщение.",
                "risk": "Согласиться ради тишины.",
                "action": "Назвать, как есть.",
            },
            "work": {
                "status": "Письмо ждёт ответа.",
                "opportunity": "Один абзац с запросом.",
                "risk": "Отложить формулировку.",
                "action": "Отправить черновик.",
            },
            "money": {
                "status": "Счёт можно закрыть сегодня.",
                "opportunity": "Одна оплата без торгов.",
                "risk": "Размыть сумму.",
                "action": "Провести платёж.",
            },
            "energy": {
                "status": "Темп медленный.",
                "opportunity": "Один завершённый шаг.",
                "risk": "Размазать день.",
                "action": "Довести одно дело.",
            },
        },
        "day_scenario": {
            "contract_version": "day_scenario_v1",
            "ready": True,
            "generation_source": "native_llm_c1",
            "scenes": [{"scene_id": "scene.relationships", "what_happens": "Близкий спрашивает."}],
            "conflict": {"short_name": theme},
        },
    }


def _insert_personal(
    db,
    *,
    user_id: int,
    local_date: date,
    story: dict,
    status: str = "success",
    used_fallback: bool = False,
    generation_source: str = "native_llm_c1",
    expression_version: str = "day-scenario-native-c5.5",
    ledger: str = "product",
    force_rebuild: bool = False,
    created_offset_s: int = 0,
) -> GenerationLog:
    key = personal_day_key(user_id=user_id, local_date=local_date)
    row = GenerationLog(
        user_id=user_id,
        module=MODULE,
        surface=SURFACE,
        status=status,
        used_fallback=used_fallback,
        input_payload={
            "target_date": local_date.isoformat(),
            "personal_day_key": key,
            "semantic_version": PERSONAL_DAY_SEMANTIC_VERSION,
            "expression_version": expression_version,
            "prompt_version": expression_version,
            "generation_source": generation_source,
            "ledger": ledger,
            "force_rebuild": force_rebuild,
            "day_story_fingerprint": key,
        },
        normalized_response=story,
        created_at=datetime(2026, 8, 25, 10, 0, 0) + timedelta(seconds=created_offset_s),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def test_personal_day_key_is_user_date_semantic_only():
    a = personal_day_key(user_id=1, local_date="2026-08-25")
    b = personal_day_key(user_id=1, local_date=date(2026, 8, 25))
    c = personal_day_key(user_id=2, local_date="2026-08-25")
    d = personal_day_key(user_id=1, local_date="2026-08-26")
    e = personal_day_key(
        user_id=1,
        local_date="2026-08-25",
        semantic_version="personal-day-semantic.v2",
    )
    assert a == b
    assert a != c
    assert a != d
    assert a != e
    assert a == personal_day_key(user_id=1, local_date="2026-08-25", owner_key="ignored")


def test_expression_mood_prompt_are_stamps_not_identity():
    day = date(2026, 8, 25)
    base = build_fingerprint_payload(
        local_date=day,
        timezone_name="UTC",
        locale="ru",
        mood=None,
        goals=[],
        profile_snapshot_id=None,
        user_id=7,
        owner_key="u7",
        prompt_version="day-scenario-native-c5.5",
        expression_version="day-scenario-native-c5.5",
    )
    other = build_fingerprint_payload(
        local_date=day,
        timezone_name="Europe/Moscow",
        locale="en",
        mood=4,
        goals=["finish one thing"],
        profile_snapshot_id=99,
        user_id=7,
        owner_key="u7",
        prompt_version="day-scenario-native-c9.9",
        expression_version="day-scenario-native-c9.9",
        sky_digest="abc",
        color_name="синий",
    )
    assert compute_day_story_fingerprint(base) == compute_day_story_fingerprint(other)
    assert compute_day_story_fingerprint(base) == personal_day_key(
        user_id=7, local_date=day
    )
    assert "behavior_version" not in base
    assert other["expression_version"] != base["expression_version"]
    assert other["mood"] == 4


def test_402_and_fallback_are_not_reusable_cache_hits(db_session):
    user = _user(db_session)
    day = date(2026, 8, 25)
    fail = _insert_personal(
        db_session,
        user_id=user.id,
        local_date=day,
        story=_ready_story(),
        status="fallback",
        used_fallback=True,
        generation_source="unavailable_after_llm",
        ledger="product",
    )
    assert is_reusable_personal_payload(
        status=fail.status,
        used_fallback=fail.used_fallback,
        input_payload=fail.input_payload,
        story=fail.normalized_response,
    ) is False
    assert _load_cached_day_story(db_session, user_id=user.id, target_date=day) is None

    kept = _insert_personal(
        db_session,
        user_id=user.id,
        local_date=day,
        story=_ready_story("kept"),
        status="fallback",
        used_fallback=True,
        generation_source="kept_prior_native",
        created_offset_s=30,
    )
    assert _load_cached_day_story(db_session, user_id=user.id, target_date=day) is None
    assert kept.id != fail.id


def test_accepted_personal_is_reused_across_expression_stamp(db_session):
    user = _user(db_session, uid=92)
    day = date(2026, 8, 25)
    row = _insert_personal(
        db_session,
        user_id=user.id,
        local_date=day,
        story=_ready_story(),
        expression_version="day-scenario-native-c5.5",
    )
    expected = personal_day_key(user_id=user.id, local_date=day)
    hit = _load_cached_day_story(
        db_session,
        user_id=user.id,
        target_date=day,
        day_story_fingerprint=expected,
    )
    assert hit is not None
    assert hit[1] == row.id
    bumped = personal_day_key(user_id=user.id, local_date=day)
    assert bumped == expected
    again = _load_cached_day_story(
        db_session,
        user_id=user.id,
        target_date=day,
        day_story_fingerprint=bumped,
    )
    assert again is not None
    assert again[1] == row.id


def test_force_rebuild_same_key_engineering_ledger():
    assert personal_day_ledger(force_rebuild=True, had_ready_artifact=False) == "product"
    assert personal_day_ledger(force_rebuild=True, had_ready_artifact=True) == "engineering"
    assert personal_day_ledger(force_rebuild=False, had_ready_artifact=True) == "product"


def test_product_then_force_persist_keeps_key(db_session):
    user = _user(db_session, uid=93)
    day = date(2026, 8, 25)
    key = personal_day_key(user_id=user.id, local_date=day)
    first = _insert_personal(
        db_session,
        user_id=user.id,
        local_date=day,
        story=_ready_story("first"),
        ledger="product",
        force_rebuild=True,
    )
    second = _insert_personal(
        db_session,
        user_id=user.id,
        local_date=day,
        story=_ready_story("force"),
        ledger="engineering",
        force_rebuild=True,
        created_offset_s=60,
    )
    assert first.input_payload["personal_day_key"] == key
    assert second.input_payload["personal_day_key"] == key
    assert first.input_payload["ledger"] == "product"
    assert second.input_payload["ledger"] == "engineering"
    hit = _load_cached_day_story(db_session, user_id=user.id, target_date=day)
    assert hit is not None
    assert hit[1] == second.id
    assert hit[0]["theme"] == "force"


def _fake_native_402(*_args, meta_out=None, **_kwargs):
    if isinstance(meta_out, dict):
        meta_out["success"] = False
        meta_out["attempt_count"] = 2
        meta_out["failure_class"] = "provider_http_402"
        meta_out["reject_reason"] = "billing_suspended"
    return None


def test_build_persists_ready_and_reopen_skips_llm(db_session):
    user = _user(db_session, uid=94)
    day = date(2026, 8, 25)
    calls: list[str] = []

    def counting_native(*args, **kwargs):
        calls.append("llm")
        return _fake_native_success(*args, **kwargs)

    with (
        patch(
            "todayflow_backend.services.day_story_wire_v1.is_llm_chat_configured",
            return_value=True,
        ),
        patch(
            "todayflow_backend.services.day_scenario_native_llm_c1.call_day_scenario_native_llm_c1",
            side_effect=counting_native,
        ),
    ):
        story1, gen1, fallback1 = _build_day_story_record(
            db_session,
            user=user,
            target_date=day,
            locale="ru",
            fusion_dump={},
            core_profile={},
            ritual_norm={},
            force_rebuild=True,
        )
        assert fallback1 is False
        assert (story1.get("day_scenario") or {}).get("generation_source") == "native_llm_c1"
        row1 = db_session.query(GenerationLog).filter(GenerationLog.id == gen1).one()
        assert row1.input_payload["ledger"] == "product"
        assert row1.input_payload["personal_day_key"] == personal_day_key(
            user_id=user.id, local_date=day
        )
        assert row1.status == "success"
        assert not row1.used_fallback
        # Native retries stay inside one generation attempt.
        assert row1.input_payload["native_llm_c1_meta"]["attempt_count"] == 3

        story2, gen2, fallback2 = _build_day_story_record(
            db_session,
            user=user,
            target_date=day,
            locale="ru",
            fusion_dump={},
            core_profile={},
            ritual_norm={},
            force_rebuild=False,
        )
        assert fallback2 is False
        assert gen2 == gen1
        assert calls == ["llm"]

        story3, gen3, fallback3 = _build_day_story_record(
            db_session,
            user=user,
            target_date=day,
            locale="ru",
            fusion_dump={},
            core_profile={},
            ritual_norm={},
            force_rebuild=True,
        )
        assert fallback3 is False
        assert gen3 != gen1
        row3 = db_session.query(GenerationLog).filter(GenerationLog.id == gen3).one()
        assert row3.input_payload["personal_day_key"] == row1.input_payload["personal_day_key"]
        assert row3.input_payload["ledger"] == "engineering"
        assert calls == ["llm", "llm"]


def test_failed_generation_is_not_ready_artifact(db_session):
    user = _user(db_session, uid=95)
    day = date(2026, 8, 25)
    with (
        patch(
            "todayflow_backend.services.day_story_wire_v1.is_llm_chat_configured",
            return_value=True,
        ),
        patch(
            "todayflow_backend.services.day_scenario_native_llm_c1.call_day_scenario_native_llm_c1",
            side_effect=_fake_native_402,
        ),
    ):
        _story, gen_id, used_fallback = _build_day_story_record(
            db_session,
            user=user,
            target_date=day,
            locale="ru",
            fusion_dump={},
            core_profile={},
            ritual_norm={},
            force_rebuild=True,
        )
    assert used_fallback is True
    row = db_session.query(GenerationLog).filter(GenerationLog.id == gen_id).one()
    assert row.status == "fallback"
    assert bool(row.used_fallback) is True
    assert row.input_payload["generation_source"] != "native_llm_c1"
    assert _load_cached_day_story(db_session, user_id=user.id, target_date=day) is None


def test_get_miss_does_not_enqueue_prewarm(client: TestClient):
    email = "personal-day-get-miss@example.com"
    password = "testpassword123"
    signup = client.post("/auth/signup", json={"email": email, "password": password})
    assert signup.status_code in (200, 201), signup.text
    token = login_bearer_token(client, email, password)
    headers = {"Authorization": f"Bearer {token}"}
    with (
        patch(
            "todayflow_backend.api.today.build_day_story_v1_wire",
            side_effect=ValueError("day_story_missing"),
        ),
        patch(
            "todayflow_backend.services.day_prewarm_job_c5.enqueue_day_prewarm"
        ) as enqueue,
    ):
        response = client.get(
            "/today/contract",
            params={"target_date": "2026-08-20"},
            headers=headers,
        )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body.get("generation_id") == "day-assembling-c5"
    assert body.get("progress", {}).get("story_status") == "assembling"
    assert enqueue.call_count == 0

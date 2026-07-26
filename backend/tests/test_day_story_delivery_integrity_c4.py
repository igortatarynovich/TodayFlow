"""Today delivery integrity — cache must serve native scenario, not slogan fallbacks."""

from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from todayflow_backend.db.models import Base, GenerationLog, User
from todayflow_backend.services.day_story_v1 import DAY_STORY_PROMPT_VER, DAY_STORY_V1_CONTRACT
from todayflow_backend.services.day_story_wire_v1 import MODULE, SURFACE, _load_cached_day_story


def _session():
    eng = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=eng)
    return sessionmaker(bind=eng)()


def _user(db, uid: int = 42) -> User:
    u = User(id=uid, email=f"delivery{uid}@test.local", password_hash="x")
    db.add(u)
    db.commit()
    return u


def _story(*, theme: str, generation_source: str | None) -> dict:
    scenario = None
    if generation_source:
        scenario = {
            "contract_version": "day_scenario_v1",
            "ready": True,
            "generation_source": generation_source,
            "scenes": [{"scene_id": "scene.communication", "what_happens": "Сцена дня."}],
            "conflict": {"short_name": theme},
        }
    return {
        "contract_version": DAY_STORY_V1_CONTRACT,
        "theme": theme,
        "direction": "Направление дня.",
        "story": "Короткий сюжет дня.",
        "expect": "Ожидание дня.",
        "trap": "Ловушка дня.",
        "primary_conflict": theme,
        "do": ["Шаг один"],
        "avoid": ["Стоп"],
        "day_scenario": scenario,
    }


def _insert_log(
    db,
    *,
    user_id: int,
    target_date: str,
    prompt_version: str,
    fingerprint: str,
    theme: str,
    status: str,
    used_fallback: bool,
    generation_source: str | None,
    created_at: datetime,
) -> int:
    row = GenerationLog(
        user_id=user_id,
        module=MODULE,
        surface=SURFACE,
        model="test",
        locale="ru",
        input_payload={
            "target_date": target_date,
            "prompt_version": prompt_version,
            "day_story_fingerprint": fingerprint,
        },
        system_prompt="test",
        normalized_response=_story(theme=theme, generation_source=generation_source),
        status=status,
        used_fallback=used_fallback,
        created_at=created_at,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return int(row.id)


def test_load_cached_prefers_native_success_over_legacy_fallback() -> None:
    """GET must not skip native C4 logs and resurrect slogan fallbacks."""
    db = _session()
    user = _user(db)
    target = date(2026, 7, 26)
    fp = "fp-same-day"
    _insert_log(
        db,
        user_id=user.id,
        target_date=target.isoformat(),
        prompt_version=DAY_STORY_PROMPT_VER,
        fingerprint=fp,
        theme="Прямота без фильтра",
        status="fallback",
        used_fallback=True,
        generation_source=None,
        created_at=datetime(2026, 7, 26, 8, 0, 0),
    )
    native_id = _insert_log(
        db,
        user_id=user.id,
        target_date=target.isoformat(),
        prompt_version="day-scenario-native-c4.0",
        fingerprint=fp,
        theme="Импульс ясности против страха чужой реакции",
        status="success",
        used_fallback=False,
        generation_source="native_llm_c1",
        created_at=datetime(2026, 7, 26, 10, 0, 0),
    )

    hit = _load_cached_day_story(
        db,
        user_id=user.id,
        target_date=target,
        day_story_fingerprint=fp,
    )
    assert hit is not None
    story, gen_id, stored_fp = hit
    assert gen_id == native_id
    assert stored_fp == fp
    assert story["theme"] == "Импульс ясности против страха чужой реакции"
    assert (story.get("day_scenario") or {}).get("generation_source") == "native_llm_c1"


def test_load_cached_accepts_native_prompt_when_no_legacy_match() -> None:
    db = _session()
    user = _user(db, uid=43)
    target = date(2026, 7, 26)
    fp = "fp-native-only"
    native_id = _insert_log(
        db,
        user_id=user.id,
        target_date=target.isoformat(),
        prompt_version="day-scenario-native-c4.0",
        fingerprint=fp,
        theme="Сигнал или шум",
        status="success",
        used_fallback=False,
        generation_source="native_llm_c1",
        created_at=datetime(2026, 7, 26, 11, 0, 0),
    )
    hit = _load_cached_day_story(
        db,
        user_id=user.id,
        target_date=target,
        day_story_fingerprint=fp,
    )
    assert hit is not None
    assert hit[1] == native_id
    assert hit[0]["theme"] == "Сигнал или шум"

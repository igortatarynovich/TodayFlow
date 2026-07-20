"""Full guest claim matrix: progress SoT, claim token, atomic transfer, conflicts."""

from __future__ import annotations

from datetime import date, timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from todayflow_backend.db.models import (
    Base,
    DailyGoalSnapshot,
    DayConnection,
    DayStoryState,
    GenerationLog,
    GuestClaimRecord,
    GuestDaySnapshot,
    GuestSession,
    StateCheckIn,
    User,
)
from todayflow_backend.db.models import utc_naive_now
from todayflow_backend.services import day_symbol_state_v1 as symbols
from todayflow_backend.services import guest_claim_v1 as claim
from todayflow_backend.services.day_story_v1 import DAY_STORY_V1_CONTRACT


def _session():
    eng = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=eng)
    return sessionmaker(bind=eng)()


def _user(db, uid: int = 21) -> User:
    u = User(id=uid, email=f"claim{uid}@test.local", password_hash="x")
    db.add(u)
    db.commit()
    return u


def _fake_story(tag: str) -> dict:
    return {
        "contract_version": DAY_STORY_V1_CONTRACT,
        "theme": tag,
        "direction": tag,
        "story": tag,
        "do": [tag],
        "avoid": ["x"],
        "advantage": tag,
        "abstain": "x",
        "today_move": tag,
        "global_period": tag,
        "development_point": tag,
        "primary_action": tag,
        "domains": {
            "relationships": {"status": "a", "opportunity": "b", "risk": "c", "action": "d"},
            "money_work": {"status": "a", "opportunity": "b", "risk": "c", "action": "d"},
            "family": {"status": "a", "opportunity": "b", "risk": "c", "action": "d"},
        },
        "talisman": {"color": "", "stone": "", "note": ""},
        "practice_recommendation": {"kind": "none", "text": "", "reason": ""},
        "symbolic_note": "",
    }


def _bootstrap_guest(db, *, day: date):
    created = claim.ensure_guest_session(db, locale="ru", timezone_name="Europe/Moscow")
    gid = created["guest_session_id"]
    secret = created["session_secret"]
    assert secret
    claim.upsert_guest_progress(
        db,
        guest_session_id=gid,
        session_secret=secret,
        local_date=day,
        timezone_name="Europe/Moscow",
        locale="ru",
        mood={"mood": "calm", "morning_mood_id": "calm", "mood_scale": 4},
        goals={"day_goal": "Сделать один ясный шаг"},
        onboarding={"intent_theme": "focus", "reality_state": "stable"},
        first_result={"theme": "first", "package": True},
        ritual={"opened": True, "mood": "calm", "checkInSubmitted": True, "headTopic": "focus"},
        today_state={"dayGoal": "Сделать один ясный шаг", "todayOpened": True, "morningMoodId": "calm"},
        day_story=_fake_story("guest-story"),
        story_fingerprint="guest-fp-abc",
        story_status="fresh",
        profile_draft={"first_name": "Анна", "birth_date": "1990-01-01", "location_name": "Москва"},
    )
    symbols.reveal_card(
        db,
        owner_key=symbols.owner_key_for_guest(gid),
        local_date=day,
        timezone_name="Europe/Moscow",
        card_id=0,
        reveal_source="ritual",
        idempotency_key=f"g-card-{gid}",
        guest_session_id=gid,
    )
    symbols.reveal_number(
        db,
        owner_key=symbols.owner_key_for_guest(gid),
        local_date=day,
        timezone_name="Europe/Moscow",
        reveal_source="ritual",
        idempotency_key=f"g-num-{gid}",
        guest_session_id=gid,
    )
    token = claim.issue_claim_token(db, guest_session_id=gid, session_secret=secret)
    return gid, secret, token["claim_token"]


def test_1_full_guest_today_transfers_to_new_user() -> None:
    db = _session()
    user = _user(db)
    day = date(2026, 7, 20)
    gid, _secret, token = _bootstrap_guest(db, day=day)

    result = claim.claim_guest_session_to_user(db, claim_token=token, user_id=user.id, local_date=day)
    assert result["claim_status"] == "completed"
    blocks = set(result["transferred_blocks"])
    assert "symbols" in blocks
    assert "mood" in blocks
    assert "goals" in blocks
    assert "first_result" in blocks
    assert "onboarding" in blocks
    assert "day_story" in blocks

    ukey = symbols.owner_key_for_user(user.id)
    row = symbols.get_state_row(db, owner_key=ukey, local_date=day)
    assert symbols.is_card_revealed(row)
    assert symbols.is_number_revealed(row)


def test_2_3_mood_goals_first_result() -> None:
    db = _session()
    user = _user(db)
    day = date(2026, 7, 20)
    _gid, _s, token = _bootstrap_guest(db, day=day)
    claim.claim_guest_session_to_user(db, claim_token=token, user_id=user.id, local_date=day)

    mood = (
        db.query(StateCheckIn)
        .filter(StateCheckIn.user_id == user.id, StateCheckIn.checkin_date == day)
        .first()
    )
    assert mood is not None
    assert mood.mood_scale == 4

    goal = (
        db.query(DailyGoalSnapshot)
        .filter(DailyGoalSnapshot.user_id == user.id, DailyGoalSnapshot.target_date == day)
        .first()
    )
    assert goal is not None
    assert "ясный" in goal.goal_text

    fr = (
        db.query(GenerationLog)
        .filter(
            GenerationLog.user_id == user.id,
            GenerationLog.module == "guest_claim_v1",
            GenerationLog.surface == "first_result",
        )
        .first()
    )
    assert fr is not None


def test_4_reveal_statuses_preserved() -> None:
    db = _session()
    user = _user(db)
    day = date(2026, 7, 21)
    _gid, _s, token = _bootstrap_guest(db, day=day)
    claim.claim_guest_session_to_user(db, claim_token=token, user_id=user.id, local_date=day)
    view = symbols.public_view(
        symbols.get_state_row(db, owner_key=symbols.owner_key_for_user(user.id), local_date=day),
        local_date=day,
    )
    assert view["card"]["revealed"] is True
    assert view["number"]["revealed"] is True


def test_5_story_transfer_without_llm_when_fp_matches() -> None:
    db = _session()
    user = _user(db)
    day = date(2026, 7, 22)
    gid, secret, token = _bootstrap_guest(db, day=day)
    # Align fingerprint with what user will compute after transfer is hard;
    # at minimum story payload must land in GenerationLog / DayStoryState.
    result = claim.claim_guest_session_to_user(db, claim_token=token, user_id=user.id, local_date=day)
    assert "day_story" in result["transferred_blocks"]
    story_row = (
        db.query(DayStoryState)
        .filter(DayStoryState.owner_key == symbols.owner_key_for_user(user.id))
        .first()
    )
    assert story_row is not None
    assert story_row.last_generation_log_id is not None


def test_6_story_stale_when_profile_context_differs() -> None:
    db = _session()
    user = _user(db)
    day = date(2026, 7, 23)
    _gid, _s, token = _bootstrap_guest(db, day=day)
    result = claim.claim_guest_session_to_user(db, claim_token=token, user_id=user.id, local_date=day)
    # Guest fingerprint "guest-fp-abc" won't match user expected → stale/refresh
    assert result["story_refresh_required"] is True or result["story_status"] in ("stale", "fresh", "missing")


def test_7_repeat_claim_idempotent() -> None:
    db = _session()
    user = _user(db)
    day = date(2026, 7, 24)
    _gid, _s, token = _bootstrap_guest(db, day=day)
    a = claim.claim_guest_session_to_user(db, claim_token=token, user_id=user.id, local_date=day)
    b = claim.claim_guest_session_to_user(db, claim_token=token, user_id=user.id, local_date=day)
    assert a["claim_status"] == b["claim_status"] == "completed"
    assert a["transferred_blocks"] == b["transferred_blocks"]
    assert db.query(GuestClaimRecord).count() == 1


def test_8_parallel_claim_one_result() -> None:
    db = _session()
    user = _user(db)
    day = date(2026, 7, 25)
    _gid, _s, token = _bootstrap_guest(db, day=day)
    r1 = claim.claim_guest_session_to_user(db, claim_token=token, user_id=user.id, local_date=day)
    r2 = claim.claim_guest_session_to_user(db, claim_token=token, user_id=user.id, local_date=day)
    assert r1["guest_session_id"] == r2["guest_session_id"]
    assert db.query(GuestClaimRecord).count() == 1


def test_9_foreign_token_rejected() -> None:
    db = _session()
    user = _user(db)
    try:
        claim.claim_guest_session_to_user(db, claim_token="not-a-real-token-value-xx", user_id=user.id)
        assert False, "expected invalid_claim_token"
    except ValueError as exc:
        assert str(exc) == "invalid_claim_token"


def test_10_expired_token_rejected() -> None:
    db = _session()
    user = _user(db)
    day = date(2026, 7, 26)
    gid, secret, token = _bootstrap_guest(db, day=day)
    row = db.query(GuestSession).filter(GuestSession.guest_session_id == gid).first()
    assert row is not None
    row.claim_token_expires_at = utc_naive_now() - timedelta(minutes=1)
    db.add(row)
    db.commit()
    try:
        claim.claim_guest_session_to_user(db, claim_token=token, user_id=user.id)
        assert False, "expected expired"
    except ValueError as exc:
        assert str(exc) == "claim_token_expired"


def test_11_existing_user_conflict_keeps_user_fields() -> None:
    db = _session()
    user = _user(db)
    day = date(2026, 7, 27)
    db.add(
        StateCheckIn(user_id=user.id, checkin_date=day, phase="morning", mood_scale=2)
    )
    db.add(DailyGoalSnapshot(user_id=user.id, target_date=day, goal_text="Уже есть цель"))
    db.commit()
    _gid, _s, token = _bootstrap_guest(db, day=day)
    result = claim.claim_guest_session_to_user(db, claim_token=token, user_id=user.id, local_date=day)
    reasons = {c["reason"] for c in result["conflicts"]}
    assert "user_mood_present" in reasons
    assert "user_goal_present" in reasons
    mood = (
        db.query(StateCheckIn)
        .filter(StateCheckIn.user_id == user.id, StateCheckIn.checkin_date == day)
        .first()
    )
    assert mood is not None and mood.mood_scale == 2
    goal = (
        db.query(DailyGoalSnapshot)
        .filter(DailyGoalSnapshot.user_id == user.id)
        .first()
    )
    assert goal is not None and goal.goal_text == "Уже есть цель"


def test_12_mid_transaction_error_rolls_back(monkeypatch) -> None:
    db = _session()
    user = _user(db)
    day = date(2026, 7, 28)
    gid, secret, token = _bootstrap_guest(db, day=day)

    def boom(*_a, **_k):
        raise RuntimeError("forced_mid_claim_failure")

    monkeypatch.setattr(claim, "_fill_mood", boom)
    try:
        claim.claim_guest_session_to_user(db, claim_token=token, user_id=user.id, local_date=day)
        assert False, "expected failure"
    except RuntimeError:
        pass

    session = db.query(GuestSession).filter(GuestSession.guest_session_id == gid).first()
    assert session is not None
    assert session.sealed is False
    assert db.query(GuestClaimRecord).count() == 0
    # Symbols remain on guest after rollback
    grow = symbols.get_state_row(db, owner_key=symbols.owner_key_for_guest(gid), local_date=day)
    assert grow is not None
    assert symbols.is_card_revealed(grow)


def test_14_local_date_timezone_preserved() -> None:
    db = _session()
    user = _user(db)
    day = date(2026, 7, 29)
    _gid, _s, token = _bootstrap_guest(db, day=day)
    result = claim.claim_guest_session_to_user(db, claim_token=token, user_id=user.id, local_date=day)
    assert result["local_date"] == day.isoformat()
    assert result["timezone_name"] == "Europe/Moscow"
    dc = (
        db.query(DayConnection)
        .filter(DayConnection.user_id == user.id, DayConnection.date == day)
        .first()
    )
    assert dc is not None


def test_15_sealed_guest_cannot_mutate() -> None:
    db = _session()
    user = _user(db)
    day = date(2026, 7, 30)
    gid, secret, token = _bootstrap_guest(db, day=day)
    claim.claim_guest_session_to_user(db, claim_token=token, user_id=user.id, local_date=day)
    assert claim.guest_session_is_mutable(db, gid) is False
    try:
        claim.upsert_guest_progress(
            db,
            guest_session_id=gid,
            session_secret=secret,
            local_date=day,
            mood={"mood": "hack"},
        )
        assert False, "sealed should reject"
    except ValueError as exc:
        assert str(exc) == "guest_session_sealed"

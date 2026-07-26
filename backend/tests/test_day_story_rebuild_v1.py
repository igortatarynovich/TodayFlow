"""Day story fingerprint + rebuild after reveal (P0 product consistency)."""

from __future__ import annotations

from datetime import date
from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from todayflow_backend.db.models import Base, GenerationLog, User
from todayflow_backend.services import day_story_fingerprint_v1 as fp
from todayflow_backend.services import day_story_refresh_v1 as refresh
from todayflow_backend.services import day_symbol_state_v1 as symbols
from todayflow_backend.services.day_story_v1 import DAY_STORY_V1_CONTRACT


def _session():
    eng = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=eng)
    return sessionmaker(bind=eng)()


def _user(db, uid: int = 7) -> User:
    u = User(id=uid, email=f"u{uid}@test.local", password_hash="x")
    db.add(u)
    db.commit()
    return u


def _fake_story(tag: str, *, card: int | None = None, number: int | None = None) -> dict[str, Any]:
    bits = [tag]
    if card is not None:
        bits.append(f"card:{card}")
    if number is not None:
        bits.append(f"num:{number}")
    text = " | ".join(bits)
    return {
        "contract_version": DAY_STORY_V1_CONTRACT,
        "theme": text,
        "direction": text,
        "story": text,
        "do": [text],
        "avoid": ["x"],
        "advantage": text,
        "abstain": "x",
        "today_move": text,
        "global_period": text,
        "development_point": text,
        "primary_action": text,
        "domains": {
            "relationships": {"status": "a", "opportunity": "b", "risk": "c", "action": "d"},
            "money_work": {"status": "a", "opportunity": "b", "risk": "c", "action": "d"},
            "family": {"status": "a", "opportunity": "b", "risk": "c", "action": "d"},
        },
        "talisman": {"color": "", "stone": "", "note": ""},
        "practice_recommendation": {"kind": "none", "text": "", "reason": ""},
        "symbolic_note": "",
    }


def _log_story(db, *, user_id: int, local_date: date, fingerprint: str, story: dict) -> int:
    row = GenerationLog(
        user_id=user_id,
        module="day_story_v1",
        surface="day_story",
        status="success",
        used_fallback=False,
        input_payload={
            "target_date": local_date.isoformat(),
            "day_story_fingerprint": fingerprint,
        },
        normalized_response=story,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return int(row.id)


def test_1_reveal_card_does_not_change_fingerprint_or_require_rebuild() -> None:
    """DAY_LIFECYCLE_V1: card reveal is overlay-only — no day_story reassemble."""
    db = _session()
    user = _user(db)
    day = date(2026, 7, 20)
    owner = symbols.owner_key_for_user(user.id)
    base_fp, _ = fp.compute_expected_day_story_fingerprint(
        db,
        user_id=user.id,
        owner_key=owner,
        local_date=day,
        timezone_name="Europe/Moscow",
        locale="ru",
    )
    story0 = _fake_story("base")
    gid0 = _log_story(db, user_id=user.id, local_date=day, fingerprint=base_fp, story=story0)
    st = refresh.ensure_story_state(db, owner_key=owner, local_date=day, user_id=user.id)
    st.fingerprint = base_fp
    st.expected_fingerprint = base_fp
    st.last_generation_log_id = gid0
    st.stale = False
    db.add(st)
    db.commit()

    symbols.reveal_card(
        db,
        owner_key=owner,
        local_date=day,
        timezone_name="Europe/Moscow",
        card_id=0,
        reveal_source="test",
        idempotency_key="card-once-1",
        user_id=user.id,
    )
    meta = refresh.mark_day_story_stale_after_input_change(
        db, owner_key=owner, local_date=day, timezone_name="Europe/Moscow", user_id=user.id
    )
    assert meta["story_refresh_required"] is False
    assert meta["story_fingerprint"] == base_fp

    calls: list[str] = []

    def build_fn(db_sess, **kwargs):
        calls.append("should-not-run")
        raise AssertionError("LLM must not run after card reveal")

    out = refresh.refresh_day_story_for_user(
        db,
        user=user,
        local_date=day,
        timezone_name="Europe/Moscow",
        locale="ru",
        build_fn=build_fn,
        llm_calls=calls,
    )
    assert out["rebuilt"] is False
    assert calls == []
    assert out["story"]["theme"] == "base"


def test_2_reveal_number_does_not_require_second_rebuild() -> None:
    db = _session()
    user = _user(db)
    day = date(2026, 7, 20)
    owner = symbols.owner_key_for_user(user.id)
    symbols.reveal_card(
        db,
        owner_key=owner,
        local_date=day,
        timezone_name="UTC",
        card_id=1,
        reveal_source="t",
        idempotency_key="c1",
        user_id=user.id,
    )
    card_fp, _ = fp.compute_expected_day_story_fingerprint(
        db, user_id=user.id, owner_key=owner, local_date=day
    )
    gid = _log_story(db, user_id=user.id, local_date=day, fingerprint=card_fp, story=_fake_story("c", card=1))
    st = refresh.ensure_story_state(db, owner_key=owner, local_date=day, user_id=user.id)
    st.fingerprint = card_fp
    st.last_generation_log_id = gid
    st.stale = False
    db.add(st)
    db.commit()

    symbols.reveal_number(
        db,
        owner_key=owner,
        local_date=day,
        timezone_name="UTC",
        reveal_source="t",
        idempotency_key="n1",
        user_id=user.id,
    )
    meta = refresh.mark_day_story_stale_after_input_change(
        db, owner_key=owner, local_date=day, user_id=user.id
    )
    assert meta["story_refresh_required"] is False
    assert meta["story_fingerprint"] == card_fp

    calls: list[str] = []

    def build_fn(db_sess, **kwargs):
        calls.append("nope")
        raise AssertionError("LLM must not run after number reveal")

    out = refresh.refresh_day_story_for_user(
        db, user=user, local_date=day, timezone_name="UTC", locale="ru", build_fn=build_fn, llm_calls=calls
    )
    assert out["rebuilt"] is False
    assert calls == []


def test_3_repeat_reveal_no_rebuild() -> None:
    db = _session()
    user = _user(db)
    day = date(2026, 7, 20)
    owner = symbols.owner_key_for_user(user.id)
    symbols.reveal_card(
        db,
        owner_key=owner,
        local_date=day,
        timezone_name="UTC",
        card_id=2,
        reveal_source="t",
        idempotency_key="c2a",
        user_id=user.id,
    )
    expected, _ = fp.compute_expected_day_story_fingerprint(
        db, user_id=user.id, owner_key=owner, local_date=day
    )
    gid = _log_story(db, user_id=user.id, local_date=day, fingerprint=expected, story=_fake_story("ok", card=2))
    st = refresh.ensure_story_state(db, owner_key=owner, local_date=day, user_id=user.id)
    st.fingerprint = expected
    st.expected_fingerprint = expected
    st.last_generation_log_id = gid
    st.stale = False
    db.add(st)
    db.commit()

    symbols.reveal_card(
        db,
        owner_key=owner,
        local_date=day,
        timezone_name="UTC",
        card_id=2,
        reveal_source="t",
        idempotency_key="c2b",
        user_id=user.id,
    )
    meta = refresh.mark_day_story_stale_after_input_change(
        db, owner_key=owner, local_date=day, user_id=user.id
    )
    assert meta["story_refresh_required"] is False

    calls: list[str] = []

    def build_fn(db_sess, **kwargs):
        calls.append("should-not-run")
        raise AssertionError("LLM must not run")

    out = refresh.refresh_day_story_for_user(
        db, user=user, local_date=day, timezone_name="UTC", locale="ru", build_fn=build_fn, llm_calls=calls
    )
    assert out["rebuilt"] is False
    assert calls == []


def test_4_parallel_reveal_keeps_base_story_without_rebuild() -> None:
    db = _session()
    user = _user(db)
    day = date(2026, 7, 21)
    owner = symbols.owner_key_for_user(user.id)
    base_fp, _ = fp.compute_expected_day_story_fingerprint(
        db, user_id=user.id, owner_key=owner, local_date=day
    )
    gid = _log_story(db, user_id=user.id, local_date=day, fingerprint=base_fp, story=_fake_story("base"))
    st = refresh.ensure_story_state(db, owner_key=owner, local_date=day, user_id=user.id)
    st.fingerprint = base_fp
    st.last_generation_log_id = gid
    db.add(st)
    db.commit()

    symbols.reveal_card(
        db,
        owner_key=owner,
        local_date=day,
        timezone_name="UTC",
        card_id=3,
        reveal_source="t",
        idempotency_key="pc",
        user_id=user.id,
    )
    symbols.reveal_number(
        db,
        owner_key=owner,
        local_date=day,
        timezone_name="UTC",
        reveal_source="t",
        idempotency_key="pn",
        user_id=user.id,
    )
    meta = refresh.mark_day_story_stale_after_input_change(
        db, owner_key=owner, local_date=day, user_id=user.id
    )
    assert meta["story_refresh_required"] is False

    calls: list[str] = []

    def build_fn(db_sess, **kwargs):
        calls.append("nope")
        raise AssertionError("no rebuild after symbol overlay")

    out = refresh.refresh_day_story_for_user(
        db, user=user, local_date=day, timezone_name="UTC", locale="ru", build_fn=build_fn, llm_calls=calls
    )
    assert out["rebuilt"] is False
    assert calls == []
    assert out["story"]["theme"] == "base"
    _fp2, payload = fp.compute_expected_day_story_fingerprint(
        db, user_id=user.id, owner_key=owner, local_date=day
    )
    assert "revealed_card_id" not in payload
    assert "revealed_number" not in payload
    view = symbols.public_view(symbols.get_state_row(db, owner_key=owner, local_date=day), local_date=day)
    assert view["card"]["revealed"] is True
    assert int(view["card"]["id"]) == 3
    assert view["number"]["revealed"] is True
    assert view["number"]["reduced_value"] is not None


def test_5_mood_change_still_can_require_rebuild() -> None:
    """Non-symbol inputs (mood) may still invalidate fingerprint — symbols must not."""
    db = _session()
    user = _user(db)
    day = date(2026, 7, 22)
    owner = symbols.owner_key_for_user(user.id)
    base_fp, base_payload = fp.compute_expected_day_story_fingerprint(
        db, user_id=user.id, owner_key=owner, local_date=day
    )
    gid = _log_story(db, user_id=user.id, local_date=day, fingerprint=base_fp, story=_fake_story("base"))
    st = refresh.ensure_story_state(db, owner_key=owner, local_date=day, user_id=user.id)
    st.fingerprint = base_fp
    st.last_generation_log_id = gid
    db.add(st)
    db.commit()

    symbols.reveal_card(
        db,
        owner_key=owner,
        local_date=day,
        timezone_name="UTC",
        card_id=4,
        reveal_source="t",
        idempotency_key="slow-c",
        user_id=user.id,
    )
    after_card_fp, _ = fp.compute_expected_day_story_fingerprint(
        db, user_id=user.id, owner_key=owner, local_date=day
    )
    assert after_card_fp == base_fp
    assert base_payload.get("mood") is None

    from todayflow_backend.db import models as db_models

    db.add(
        db_models.StateCheckIn(
            user_id=user.id,
            checkin_date=day,
            phase="morning",
            mood_scale=4,
        )
    )
    db.commit()
    mood_fp, mood_payload = fp.compute_expected_day_story_fingerprint(
        db, user_id=user.id, owner_key=owner, local_date=day
    )
    assert mood_payload.get("mood") == 4
    assert mood_fp != base_fp
    meta = refresh.mark_day_story_stale_after_input_change(
        db, owner_key=owner, local_date=day, user_id=user.id
    )
    assert meta["story_refresh_required"] is True


def test_6_matching_fingerprint_skips_llm() -> None:
    db = _session()
    user = _user(db)
    day = date(2026, 7, 23)
    owner = symbols.owner_key_for_user(user.id)
    expected, _ = fp.compute_expected_day_story_fingerprint(
        db, user_id=user.id, owner_key=owner, local_date=day
    )
    gid = _log_story(db, user_id=user.id, local_date=day, fingerprint=expected, story=_fake_story("cached"))
    st = refresh.ensure_story_state(db, owner_key=owner, local_date=day, user_id=user.id)
    st.fingerprint = expected
    st.expected_fingerprint = expected
    st.last_generation_log_id = gid
    st.stale = False
    db.add(st)
    db.commit()
    calls: list[str] = []

    def build_fn(db_sess, **kwargs):
        calls.append("nope")
        raise AssertionError("no llm")

    out = refresh.refresh_day_story_for_user(
        db, user=user, local_date=day, timezone_name="UTC", locale="ru", build_fn=build_fn, llm_calls=calls
    )
    assert out["rebuilt"] is False
    assert calls == []
    assert out["story"]["theme"] == "cached"


def test_7_llm_error_keeps_last_valid() -> None:
    db = _session()
    user = _user(db)
    day = date(2026, 7, 24)
    owner = symbols.owner_key_for_user(user.id)
    base_fp, _ = fp.compute_expected_day_story_fingerprint(
        db, user_id=user.id, owner_key=owner, local_date=day
    )
    gid = _log_story(db, user_id=user.id, local_date=day, fingerprint=base_fp, story=_fake_story("keep-me"))
    st = refresh.ensure_story_state(db, owner_key=owner, local_date=day, user_id=user.id)
    st.fingerprint = base_fp
    st.last_generation_log_id = gid
    db.add(st)
    db.commit()
    # Force stale via mismatched stored fingerprint (not via symbol reveal).
    st.fingerprint = "force-stale-mismatch"
    st.stale = True
    db.add(st)
    db.commit()

    def build_fn(db_sess, **kwargs):
        raise RuntimeError("llm down")

    out = refresh.refresh_day_story_for_user(
        db, user=user, local_date=day, timezone_name="UTC", locale="ru", build_fn=build_fn
    )
    assert out["story_status"] == "error"
    assert out["story_refresh_required"] is True
    assert out["story"]["theme"] == "keep-me"
    st2 = refresh.get_story_state_row(db, owner_key=owner, local_date=day)
    assert st2 is not None
    assert st2.last_generation_log_id == gid


def test_8_guest_claim_does_not_force_rebuild_from_symbols_alone() -> None:
    db = _session()
    user = _user(db, uid=11)
    day = date(2026, 7, 25)
    gid = "guest-claim-story-001"
    gkey = symbols.owner_key_for_guest(gid)
    symbols.reveal_card(
        db,
        owner_key=gkey,
        local_date=day,
        timezone_name="UTC",
        card_id=6,
        reveal_source="guest",
        idempotency_key="g-card",
        guest_session_id=gid,
    )
    symbols.claim_guest_symbols_to_user(db, guest_session_id=gid, user_id=user.id, local_date=day)
    ukey = symbols.owner_key_for_user(user.id)
    expected_fp, _ = fp.compute_expected_day_story_fingerprint(
        db, user_id=user.id, owner_key=ukey, local_date=day
    )
    log_id = _log_story(db, user_id=user.id, local_date=day, fingerprint=expected_fp, story=_fake_story("ok"))
    st = refresh.ensure_story_state(db, owner_key=ukey, local_date=day, user_id=user.id)
    st.fingerprint = expected_fp
    st.last_generation_log_id = log_id
    st.stale = False
    db.add(st)
    db.commit()
    meta = refresh.mark_day_story_stale_after_input_change(
        db, owner_key=ukey, local_date=day, user_id=user.id
    )
    assert meta["story_refresh_required"] is False


def test_9_and_10_prompt_symbols_only_when_revealed() -> None:
    db = _session()
    user = _user(db, uid=12)
    day = date(2026, 7, 26)
    owner = symbols.owner_key_for_user(user.id)
    before_fp, before_payload = fp.compute_expected_day_story_fingerprint(
        db, user_id=user.id, owner_key=owner, local_date=day
    )
    assert "revealed_card_id" not in before_payload
    assert "revealed_number" not in before_payload
    ritual = symbols.ritual_context_from_symbol_view(
        symbols.public_view(None, local_date=day)
    )
    assert "tarot_main_id" not in ritual
    assert "numerology_value" not in ritual

    symbols.reveal_card(
        db,
        owner_key=owner,
        local_date=day,
        timezone_name="UTC",
        card_id=7,
        reveal_source="t",
        idempotency_key="prompt-c",
        user_id=user.id,
    )
    after_fp, after_payload = fp.compute_expected_day_story_fingerprint(
        db, user_id=user.id, owner_key=owner, local_date=day
    )
    assert after_fp == before_fp
    assert "revealed_card_id" not in after_payload
    view = symbols.public_view(symbols.get_state_row(db, owner_key=owner, local_date=day), local_date=day)
    ritual2 = symbols.ritual_context_from_symbol_view(view)
    assert ritual2.get("tarot_main_id") == 7
    assert "numerology_value" not in ritual2

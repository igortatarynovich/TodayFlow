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


def test_1_base_then_reveal_card_changes_fingerprint_one_rebuild() -> None:
    db = _session()
    user = _user(db)
    day = date(2026, 7, 20)
    owner = symbols.owner_key_for_user(user.id)
    base_fp, _ = fp.compute_expected_day_story_fingerprint(
        db, user_id=user.id, owner_key=owner, local_date=day, locale="ru"
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
    assert meta["story_refresh_required"] is True
    card_fp = meta["story_fingerprint"]
    assert card_fp != base_fp

    builds = 0

    def build_fn(db_sess, **kwargs):
        nonlocal builds
        builds += 1
        s = _fake_story("with-card", card=0)
        gid = _log_story(
            db_sess,
            user_id=user.id,
            local_date=day,
            fingerprint=kwargs["expected_fingerprint"],
            story=s,
        )
        return s, gid, True

    out = refresh.refresh_day_story_for_user(
        db,
        user=user,
        local_date=day,
        timezone_name="Europe/Moscow",
        locale="ru",
        build_fn=build_fn,
    )
    assert out["rebuilt"] is True
    assert builds == 1
    assert "card:0" in out["story"]["story"]
    assert out["story_fingerprint"] == card_fp


def test_2_then_reveal_number_second_rebuild() -> None:
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
    assert meta["story_refresh_required"] is True
    builds = 0

    def build_fn(db_sess, **kwargs):
        nonlocal builds
        builds += 1
        view = symbols.public_view(
            symbols.get_state_row(db_sess, owner_key=owner, local_date=day),
            local_date=day,
        )
        num = view["number"].get("reduced_value")
        s = _fake_story("full", card=1, number=num)
        gid2 = _log_story(
            db_sess, user_id=user.id, local_date=day, fingerprint=kwargs["expected_fingerprint"], story=s
        )
        return s, gid2, True

    out = refresh.refresh_day_story_for_user(
        db, user=user, local_date=day, timezone_name="UTC", locale="ru", build_fn=build_fn
    )
    assert out["rebuilt"] is True
    assert builds == 1
    assert "card:1" in out["story"]["story"]
    assert "num:" in out["story"]["story"]


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


def test_4_parallel_reveal_final_story_has_both() -> None:
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
    refresh.mark_day_story_stale_after_input_change(db, owner_key=owner, local_date=day, user_id=user.id)

    def build_fn(db_sess, **kwargs):
        view = symbols.public_view(
            symbols.get_state_row(db_sess, owner_key=owner, local_date=day), local_date=day
        )
        s = _fake_story(
            "both",
            card=int(view["card"]["id"]),
            number=int(view["number"]["reduced_value"]),
        )
        gid2 = _log_story(
            db_sess, user_id=user.id, local_date=day, fingerprint=kwargs["expected_fingerprint"], story=s
        )
        return s, gid2, True

    out = refresh.refresh_day_story_for_user(
        db, user=user, local_date=day, timezone_name="UTC", locale="ru", build_fn=build_fn
    )
    assert "card:3" in out["story"]["story"]
    assert "num:" in out["story"]["story"]
    payload = out["fingerprint_payload"]
    assert payload["revealed_card_id"] == 3
    assert payload["revealed_number"] is not None


def test_5_slow_old_generation_does_not_overwrite_newer() -> None:
    db = _session()
    user = _user(db)
    day = date(2026, 7, 22)
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
        card_id=4,
        reveal_source="t",
        idempotency_key="slow-c",
        user_id=user.id,
    )
    refresh.mark_day_story_stale_after_input_change(db, owner_key=owner, local_date=day, user_id=user.id)
    builds: list[str] = []

    def build_fn(db_sess, **kwargs):
        builds.append(kwargs["expected_fingerprint"])
        if len(builds) == 1:
            # Mid-flight newer reveal — old generation must not become canonical alone.
            symbols.reveal_number(
                db_sess,
                owner_key=owner,
                local_date=day,
                timezone_name="UTC",
                reveal_source="t",
                idempotency_key="slow-n",
                user_id=user.id,
            )
            refresh.mark_day_story_stale_after_input_change(
                db_sess, owner_key=owner, local_date=day, user_id=user.id
            )
        view = symbols.public_view(
            symbols.get_state_row(db_sess, owner_key=owner, local_date=day), local_date=day
        )
        card = view["card"].get("id")
        num = view["number"].get("reduced_value") if view["number"].get("revealed") else None
        s = _fake_story("gen", card=int(card) if card is not None else None, number=num)
        gid2 = _log_story(
            db_sess, user_id=user.id, local_date=day, fingerprint=kwargs["expected_fingerprint"], story=s
        )
        return s, gid2, True

    out = refresh.refresh_day_story_for_user(
        db, user=user, local_date=day, timezone_name="UTC", locale="ru", build_fn=build_fn, max_attempts=2
    )
    final_fp, payload = fp.compute_expected_day_story_fingerprint(
        db, user_id=user.id, owner_key=owner, local_date=day
    )
    st2 = refresh.get_story_state_row(db, owner_key=owner, local_date=day)
    assert st2 is not None
    assert payload.get("revealed_number") is not None
    assert st2.fingerprint == final_fp
    assert "num:" in out["story"]["story"]
    assert len(builds) == 2


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
    symbols.reveal_card(
        db,
        owner_key=owner,
        local_date=day,
        timezone_name="UTC",
        card_id=5,
        reveal_source="t",
        idempotency_key="err-c",
        user_id=user.id,
    )
    refresh.mark_day_story_stale_after_input_change(db, owner_key=owner, local_date=day, user_id=user.id)

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


def test_8_guest_claim_marks_user_story_stale() -> None:
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
    # Seed a base user story that does not include the claimed card.
    base_fp = "old-base-fp"
    log_id = _log_story(db, user_id=user.id, local_date=day, fingerprint=base_fp, story=_fake_story("old"))
    st = refresh.ensure_story_state(db, owner_key=ukey, local_date=day, user_id=user.id)
    st.fingerprint = base_fp
    st.last_generation_log_id = log_id
    st.stale = False
    db.add(st)
    db.commit()
    meta = refresh.mark_day_story_stale_after_input_change(
        db, owner_key=ukey, local_date=day, user_id=user.id
    )
    assert meta["story_refresh_required"] is True


def test_9_and_10_prompt_symbols_only_when_revealed() -> None:
    db = _session()
    user = _user(db, uid=12)
    day = date(2026, 7, 26)
    owner = symbols.owner_key_for_user(user.id)
    before_fp, before_payload = fp.compute_expected_day_story_fingerprint(
        db, user_id=user.id, owner_key=owner, local_date=day
    )
    assert before_payload["revealed_card_id"] is None
    assert before_payload["revealed_number"] is None
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
    assert after_fp != before_fp
    assert after_payload["revealed_card_id"] == 7
    assert after_payload["revealed_number"] is None
    view = symbols.public_view(symbols.get_state_row(db, owner_key=owner, local_date=day), local_date=day)
    ritual2 = symbols.ritual_context_from_symbol_view(view)
    assert ritual2.get("tarot_main_id") == 7
    assert "numerology_value" not in ritual2

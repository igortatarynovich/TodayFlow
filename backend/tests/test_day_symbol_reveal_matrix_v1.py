"""Access matrix for day card/number reveal SoT (P0).

Uses in-memory SQLite + service layer (no WeasyPrint app import).
Searches serialized public views for forbidden identity leaks.
"""

from __future__ import annotations

import json
import re
from datetime import date

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from todayflow_backend.db.models import Base, DaySymbolState
from todayflow_backend.services import day_symbol_state_v1 as symbols
from todayflow_backend.services.day_narrative_brief_v0 import build_day_narrative_brief_v0
from todayflow_backend.services.tarot import TarotService


def _session():
    eng = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=eng)
    return sessionmaker(bind=eng)()


def _blob(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, default=str).lower()


_CARD_LEAK = re.compile(r"\b(шут|маг|жрица|императрица|император|иерофант|влюбленные|колесница)\b", re.I)
_NUMBER_LEAK = re.compile(r'"reduced_value"\s*:\s*[1-9]|число дня —\s*\d')


def test_matrix_guest_and_user_before_after_reveal() -> None:
    db = _session()
    day = date(2026, 7, 20)
    guest_key = symbols.owner_key_for_guest("guest-session-matrix-001")
    user_key = symbols.owner_key_for_user(42)

    for owner, uid, gid in (
        (guest_key, None, "guest-session-matrix-001"),
        (user_key, 42, None),
    ):
        before = symbols.public_view(
            symbols.get_state_row(db, owner_key=owner, local_date=day),
            local_date=day,
        )
        blob = _blob(before)
        assert before["card"]["revealed"] is False
        assert before["number"]["revealed"] is False
        assert '"id"' not in blob or before["card"].get("id") is None
        assert "reduced_value" not in before["number"]
        assert not _CARD_LEAK.search(blob)

        card_view = symbols.reveal_card(
            db,
            owner_key=owner,
            local_date=day,
            timezone_name="Europe/Moscow",
            card_id=0,
            orientation="upright",
            reveal_source="test",
            idempotency_key=f"card-{owner}-1",
            user_id=uid,
            guest_session_id=gid,
        )
        assert card_view["card"]["revealed"] is True
        assert card_view["card"]["id"] == 0
        assert card_view["card"]["name"]
        assert card_view["number"]["revealed"] is False

        # Partial: card only → brief must not include number
        ritual = symbols.ritual_context_from_symbol_view(card_view)
        brief = build_day_narrative_brief_v0(
            foundation=None,
            ritual=ritual,
            fusion_scores=None,
            intent_slice=None,
            locale="ru",
        )
        brief_blob = _blob(brief)
        assert "число дня —" not in brief_blob
        assert brief.get("thread_number") in (None, "")

        num_view = symbols.reveal_number(
            db,
            owner_key=owner,
            local_date=day,
            timezone_name="Europe/Moscow",
            reveal_source="test",
            idempotency_key=f"num-{owner}-1",
            user_id=uid,
            guest_session_id=gid,
        )
        assert num_view["number"]["revealed"] is True
        assert num_view["number"]["reduced_value"] is not None

        ritual2 = symbols.ritual_context_from_symbol_view(num_view)
        brief2 = build_day_narrative_brief_v0(
            foundation=None,
            ritual=ritual2,
            fusion_scores=None,
            intent_slice=None,
            locale="ru",
        )
        assert brief2.get("thread_card")
        assert brief2.get("thread_number")


def test_idempotent_and_parallel_reveal() -> None:
    db = _session()
    day = date(2026, 7, 20)
    key = symbols.owner_key_for_user(7)
    a = symbols.reveal_card(
        db,
        owner_key=key,
        local_date=day,
        timezone_name="UTC",
        card_id=1,
        reveal_source="a",
        idempotency_key="same-card-key",
        user_id=7,
    )
    b = symbols.reveal_card(
        db,
        owner_key=key,
        local_date=day,
        timezone_name="UTC",
        card_id=2,  # different card — must not swap
        reveal_source="b",
        idempotency_key="same-card-key",
        user_id=7,
    )
    assert a["card"]["id"] == b["card"]["id"] == 1

    n1 = symbols.reveal_number(
        db,
        owner_key=key,
        local_date=day,
        timezone_name="UTC",
        reveal_source="a",
        idempotency_key="same-num-key",
        user_id=7,
    )
    n2 = symbols.reveal_number(
        db,
        owner_key=key,
        local_date=day,
        timezone_name="UTC",
        reveal_source="b",
        idempotency_key="same-num-key",
        user_id=7,
    )
    assert n1["number"]["reduced_value"] == n2["number"]["reduced_value"]


def test_guest_claim_transfers_reveals() -> None:
    db = _session()
    day = date(2026, 7, 20)
    gid = "guest-claim-abc-12345"
    gkey = symbols.owner_key_for_guest(gid)
    symbols.reveal_card(
        db,
        owner_key=gkey,
        local_date=day,
        timezone_name="UTC",
        card_id=3,
        reveal_source="guest",
        idempotency_key="g-card-1",
        guest_session_id=gid,
    )
    symbols.reveal_number(
        db,
        owner_key=gkey,
        local_date=day,
        timezone_name="UTC",
        reveal_source="guest",
        idempotency_key="g-num-1",
        guest_session_id=gid,
    )
    result = symbols.claim_guest_symbols_to_user(db, guest_session_id=gid, user_id=99, local_date=day)
    assert result["transferred_rows"] >= 1
    ukey = symbols.owner_key_for_user(99)
    view = symbols.public_view(
        symbols.get_state_row(db, owner_key=ukey, local_date=day),
        local_date=day,
    )
    assert view["card"]["revealed"] is True
    assert view["card"]["id"] == 3
    assert view["number"]["revealed"] is True
    # Idempotent re-claim
    again = symbols.claim_guest_symbols_to_user(db, guest_session_id=gid, user_id=99, local_date=day)
    assert again["transferred_rows"] == 0


def test_morning_redacted_payloads_shape() -> None:
    db = _session()
    day = date(2026, 7, 20)
    view = symbols.public_view(None, local_date=day)
    tarot = symbols.redacted_tarot_card_dict(view)
    num = symbols.redacted_numerology_dict(view)
    blob = _blob({"tarot_card": tarot, "numerology_number": num})
    assert tarot["selection_status"] == "not_selected"
    assert num["selection_status"] == "not_selected"
    assert "name" not in tarot
    assert "reduced_value" not in num
    assert not _NUMBER_LEAK.search(blob)


def test_get_never_creates_row() -> None:
    db = _session()
    day = date(2026, 7, 21)
    key = symbols.owner_key_for_user(5)
    assert symbols.get_state_row(db, owner_key=key, local_date=day) is None
    view = symbols.public_view(None, local_date=day)
    assert view["card"]["status"] == symbols.STATUS_NOT_REVEALED
    assert db.query(DaySymbolState).count() == 0


def test_timezone_local_date_resolution() -> None:
    d = symbols.resolve_local_date(local_date="2026-12-31", timezone_name="America/New_York")
    assert d == date(2026, 12, 31)
    # Invalid TZ falls back without crashing
    d2 = symbols.resolve_local_date(local_date=None, timezone_name="Not/AZone")
    assert isinstance(d2, date)


def test_tarot_service_public_still_gated() -> None:
    svc = TarotService()
    gated = svc.get_daily_draw(
        type("U", (), {"id": 0, "email": "p@x"})(),
        assign_if_missing=False,
    )
    assert gated.selection_status == "not_selected"
    assert gated.card is None


def test_two_users_same_idempotency_key_stay_isolated() -> None:
    """P0 regression: shared client keys must not leak reveal across owners."""
    db = _session()
    day = date(2026, 7, 21)
    shared_card_key = "tarot_reveal:2026-07-21:0"
    shared_num_key = "number_reveal:2026-07-21"

    a_key = symbols.owner_key_for_user(101)
    b_key = symbols.owner_key_for_user(202)

    a_card = symbols.reveal_card(
        db,
        owner_key=a_key,
        local_date=day,
        timezone_name="UTC",
        card_id=0,
        reveal_source="a",
        idempotency_key=shared_card_key,
        user_id=101,
    )
    b_card = symbols.reveal_card(
        db,
        owner_key=b_key,
        local_date=day,
        timezone_name="UTC",
        card_id=5,
        reveal_source="b",
        idempotency_key=shared_card_key,
        user_id=202,
    )
    assert a_card["card"]["id"] == 0
    assert b_card["card"]["id"] == 5

    a_num = symbols.reveal_number(
        db,
        owner_key=a_key,
        local_date=day,
        timezone_name="UTC",
        reveal_source="a",
        idempotency_key=shared_num_key,
        user_id=101,
    )
    b_num = symbols.reveal_number(
        db,
        owner_key=b_key,
        local_date=day,
        timezone_name="UTC",
        reveal_source="b",
        idempotency_key=shared_num_key,
        user_id=202,
    )
    assert a_num["number"]["revealed"] is True
    assert b_num["number"]["revealed"] is True
    # Each owner has their own row — not a copy of the other owner's public_view owner identity.
    assert db.query(DaySymbolState).filter(DaySymbolState.owner_key == a_key).count() == 1
    assert db.query(DaySymbolState).filter(DaySymbolState.owner_key == b_key).count() == 1
    a_row = symbols.get_state_row(db, owner_key=a_key, local_date=day)
    b_row = symbols.get_state_row(db, owner_key=b_key, local_date=day)
    assert a_row is not None and b_row is not None
    assert a_row.id != b_row.id
    assert a_row.card_id == "0"
    assert b_row.card_id == "5"

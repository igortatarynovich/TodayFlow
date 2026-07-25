"""Full 78-card Waite-Smith deck is the draw source — minors included."""

from __future__ import annotations

from todayflow_backend.data import astrology as astrology_ref
from todayflow_backend.db.models import User
from todayflow_backend.services.tarot import TarotService


def test_tarot_full_deck_has_78_unique_ids():
    deck = astrology_ref.tarot_full_deck()
    ids = [int(c["id"]) for c in deck]
    assert len(ids) == 78
    assert len(set(ids)) == 78
    assert ids == list(range(78))
    assert sum(1 for i in ids if i <= 21) == 22
    assert sum(1 for i in ids if i >= 22) == 56


def test_tarot_service_uses_full_deck_and_draws_minors():
    service = TarotService()
    assert len(service.cards) == 78
    seen: set[int] = set()
    for user_id in range(1, 40):
        user = User(id=user_id, email=f"u{user_id}@test.local")
        for card in service.draw_cards_from_deck(user, count=10):
            seen.add(int(card.id))
    minors = {i for i in seen if i >= 22}
    majors = {i for i in seen if i <= 21}
    assert len(minors) >= 20, f"expected many minors in draws, got {sorted(minors)[:10]}"
    assert len(majors) >= 8
    assert max(seen) >= 22

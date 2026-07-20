"""DoD: card-of-day and day-number must not leak identity before reveal.

Service-level tests (no WeasyPrint/app import) + contract shape checks.
"""

from __future__ import annotations

from datetime import date
from types import SimpleNamespace

from todayflow_backend.services.numerology import NumerologyService
from todayflow_backend.services.tarot import TarotService


def test_public_module_draw_is_not_selected() -> None:
    svc = TarotService()
    public = SimpleNamespace(id=0, email="public@todayflow.app")
    gated = svc.get_daily_draw(public, assign_if_missing=False)
    assert gated.selection_status == "not_selected"
    assert gated.card is None
    assert gated.orientation is None
    assert svc.not_selected_daily_draw().selection_status == "not_selected"


def test_auth_draw_not_selected_until_reveal(monkeypatch) -> None:
    svc = TarotService()
    user = SimpleNamespace(id=4242, email="reveal@example.com")

    # Force empty lookup path without touching DB for GET-gated.
    monkeypatch.setattr(
        "todayflow_backend.services.tarot.SessionLocal",
        lambda: _EmptySession(),
    )
    gated = svc.get_daily_draw(user, assign_if_missing=False)
    assert gated.selection_status == "not_selected"
    assert gated.card is None


def test_numerology_daily_gated_until_reveal() -> None:
    svc = NumerologyService()
    gated = svc.daily_number(reveal=False)
    assert gated.selection_status == "not_selected"
    assert gated.number is None

    revealed = svc.daily_number(reveal=True, reference_date=date(2026, 7, 20))
    assert revealed.selection_status == "selected"
    assert revealed.number is not None
    assert revealed.number.reduced_value is not None


class _EmptySession:
    def query(self, *_a, **_k):
        return self

    def filter_by(self, **_k):
        return self

    def order_by(self, *_a, **_k):
        return self

    def first(self):
        return None

    def close(self):
        return None

"""card_base_v1 cutover — TarotService + explainer + interpretation catalog."""

from __future__ import annotations

from todayflow_backend.core import tarot_explainer
from todayflow_backend.data import card_base_v1
from todayflow_backend.services.tarot import TarotService
from todayflow_backend.services import tarot_interpretation_engine_v1 as eng


def test_prose_sides_covers_full_deck():
    assert card_base_v1.validate_card_base_v1() == []
    for cid in range(78):
        sides = card_base_v1.prose_sides(cid)
        assert sides, f"missing prose for {cid}"
        assert sides["upright"]
        assert sides["reversed"]
        assert sides["upright"] != sides["reversed"]


def test_minor_reversed_has_no_central_themes_glue():
    """Regression: id 22–77 must not show «blob — blob; …» or semicolon keywords."""
    for cid in range(22, 78):
        rev = card_base_v1.get_base_meaning(cid, "reversed")
        assert rev, cid
        meaning = rev["meaning"]
        assert " — " not in meaning or not meaning.split(" — ", 1)[1].startswith(
            meaning.split(" — ", 1)[0].strip()
        )
        for kw in rev["keywords"]:
            assert ";" not in kw, (cid, kw)
        assert "парanoia" not in meaning
        assert "paranoia" not in meaning.lower()


def test_tarot_service_meanings_from_card_base():
    svc = TarotService()
    card = svc.get_card_by_id(21)
    assert card is not None
    bank = card_base_v1.prose_sides(21)
    assert bank is not None
    assert card.upright == bank["upright"]
    assert card.reversed == bank["reversed"]
    # Product prose is RU (not EN deck sentence starting with "completion" etc.)
    assert any(ch.isalpha() and ord(ch) > 127 for ch in card.upright)


def test_spread_meaning_uses_card_base_orientation():
    from todayflow_backend.db import models as db_models
    from todayflow_backend.core import models as api_models

    svc = TarotService()
    user = db_models.User(id=1, email="cutover@example.com")
    selected = [
        api_models.TarotSelectedCard(card_id=0, orientation="reversed"),
    ]
    # one_card spread if present; else first spread with >=1 position
    spread_id = "one_card" if "one_card" in svc.spreads else next(iter(svc.spreads))
    from datetime import date

    result = svc._build_spread_result(
        spread_id,
        user,
        date(2026, 8, 1),
        selected_cards=selected,
    )
    assert result.cards
    first = result.cards[0]
    bank = card_base_v1.get_base_meaning(int(first.card.id), first.orientation)
    assert bank is not None
    assert first.meaning == bank["meaning"]


def test_explainer_forces_card_base_meaning():
    out = tarot_explainer._apply_base_meaning(
        {
            "meaning": "LLM invented traditional meaning",
            "what_to_do": "Сделай один конкретный шаг сегодня утром.",
            "what_to_avoid": "Не обещай лишнего только чтобы снять напряжение сейчас.",
            "possible_events": "Может возникнуть выбор между удобным и честным решением.",
            "how_day_looks": "День складывается спокойнее, когда не берёшь лишнего.",
            "why_this_card": "Карта просит точности, а не скорости в решениях дня.",
        },
        card_id=21,
        card_name="Мир",
        orientation="upright",
    )
    bank = card_base_v1.get_base_meaning(21, "upright")
    assert bank is not None
    assert out["meaning"] == bank["meaning"]
    assert out["meaning_source"] == "card_base_v1"


def test_interpretation_catalog_from_card_base():
    deck = eng._deck_by_id()
    row = deck[16]
    rng = eng._meaning_range(16, row, question_domain="general")
    bank = card_base_v1.prose_sides(16)
    assert bank is not None
    assert rng["upright_meaning"] == bank["upright"]
    assert rng["reversed_meaning"] == bank["reversed"]

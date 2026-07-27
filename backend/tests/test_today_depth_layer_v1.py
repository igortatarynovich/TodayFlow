"""Today Depth Layer v1 — catalog + Free CTA vs Paid generate."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

from todayflow_backend.services.today_depth_layer_v1 import (
    DEPTH_LAYER_MENU_V1,
    annotate_depth_layer_payload,
    build_depth_layer_cta_payload,
    build_depth_layer_menu,
    can_generate_depth_layer,
    normalize_depth_topic,
)


def test_normalize_depth_topic_accepts_intimacy_and_menu():
    assert normalize_depth_topic("intimacy") == "intimacy"
    assert normalize_depth_topic("MONEY") == "money"
    assert normalize_depth_topic("nope") == "full_day"
    assert set(DEPTH_LAYER_MENU_V1) <= {"money", "intimacy", "love", "career", "family"}


def test_menu_has_labels():
    menu = build_depth_layer_menu(locale="ru")
    assert len(menu) == len(DEPTH_LAYER_MENU_V1)
    assert all(row["topic"] and row["label"] and row["value"] for row in menu)


def test_free_cta_payload_marks_access_cta():
    payload = build_depth_layer_cta_payload("money", locale="ru")
    assert payload["depth_layer"]["access"] == "cta"
    assert payload["depth_layer"]["can_generate"] is False
    assert payload["depth_layer"]["topic"] == "money"
    assert "подписк" in payload["body"].lower() or "trial" in payload["body"].lower()
    assert payload["title"]


def test_annotate_generated_payload():
    out = annotate_depth_layer_payload({"title": "t", "body": "b"}, topic="intimacy", locale="en")
    assert out["depth_layer"]["access"] == "generated"
    assert out["depth_layer"]["can_generate"] is True
    assert out["depth_layer"]["topic"] == "intimacy"


def test_can_generate_depth_layer_by_billing(monkeypatch):
    user = SimpleNamespace(id=1)
    db = MagicMock()

    monkeypatch.setattr(
        "todayflow_backend.services.today_depth_layer_v1.get_subscription_level",
        lambda u, d: "free",
    )
    assert can_generate_depth_layer(user, db) is False

    monkeypatch.setattr(
        "todayflow_backend.services.today_depth_layer_v1.get_subscription_level",
        lambda u, d: "lite",
    )
    assert can_generate_depth_layer(user, db) is True

    monkeypatch.setattr(
        "todayflow_backend.services.today_depth_layer_v1.get_subscription_level",
        lambda u, d: "pro",
    )
    assert can_generate_depth_layer(user, db) is True

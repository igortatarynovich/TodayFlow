"""GET /compatibility/encyclopedia and topic-aware dynamics."""

from todayflow_backend.services.compatibility_encyclopedia import resolve_encyclopedia_selection


def test_compatibility_encyclopedia_catalog(client) -> None:
    response = client.get("/compatibility/encyclopedia", params={"locale": "ru"})
    assert response.status_code == 200
    data = response.json()
    assert data["content_locale"] == "ru"
    assert data["version"]
    assert len(data["categories"]) >= 10
    assert len(data["popular_readings"]) >= 8
    assert len(data["series"]) >= 8
    love = next(c for c in data["categories"] if c["id"] == "love")
    assert love["intro_blocks"]
    assert love["analyze_params"]["topic"] == "love"


def test_compatibility_dynamics_with_topic_id(client) -> None:
    response = client.post(
        "/compatibility/dynamics",
        json={
            "mode": "quick",
            "from_sign": "aries",
            "to_sign": "libra",
            "generation": "template",
            "topic_id": "conflicts",
            "locale": "ru",
        },
    )
    assert response.status_code == 200
    data = response.json()
    overview = data["product_surface"]["overview_paragraphs"]
    assert overview
    assert any("конфликт" in p.lower() or "конфлик" in p.lower() for p in overview)
    pair_dyn = data.get("pair_dynamics") or {}
    assert pair_dyn.get("encyclopedia_selection", {}).get("selection_id") == "conflicts"

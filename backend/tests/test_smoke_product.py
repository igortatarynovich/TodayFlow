"""Узкий smoke по публичным маршрутам из чеклиста приёмки (совместимость, см. фаза 4)."""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.smoke
def test_compatibility_signs_public_pair(client: TestClient) -> None:
    """GET /compatibility/signs — тот же контракт, что и фронт /compatibility/signs/result."""
    response = client.get("/compatibility/signs", params={"from": "aries", "to": "libra"})
    assert response.status_code == 200
    data = response.json()
    assert data.get("from_sign") == "aries"
    assert data.get("to_sign") == "libra"
    assert "score" in data
    assert "summary" in data
    assert "quick_reading" in data
    assert isinstance(data.get("full_paragraphs"), list)
    surface = data.get("product_surface")
    assert isinstance(surface, dict)
    assert "subscores" in surface and "overview_paragraphs" in surface
    # Public (guest) tier is a teaser by design (compat access v0): exactly one
    # emotions block with detail/risk/action stripped; full shape is gated and
    # covered in test_compatibility_access_v0.py.
    assert isinstance(surface.get("blocks"), list) and len(surface["blocks"]) >= 1
    assert all(not b.get("detail") and not b.get("action") for b in surface["blocks"])

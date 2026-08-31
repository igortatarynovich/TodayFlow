"""Tests for GET /practices/select — deterministic content library endpoint."""

from __future__ import annotations

from fastapi.testclient import TestClient


class TestPracticesSelectEndpoint:
    """Smoke tests for the deterministic content library selection endpoint."""

    def test_select_sleep_prepare(self, client: TestClient):
        response = client.get(
            "/practices/select",
            params={"purpose": "sleep", "direction": "prepare", "input_state": "restless"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["matched"] is True
        assert data["item_id"] == "meditation.sleep.001"
        assert data["content_class"] == "meditation"
        assert data["type"] == "sleep"
        assert data["title"] == "Челюсть мягче"
        assert data["duration"] == 5
        assert "purpose=sleep" in data["reason"]

    def test_select_calm_work_context(self, client: TestClient):
        response = client.get(
            "/practices/select",
            params={
                "purpose": "calm",
                "direction": "downregulate",
                "input_state": "tense",
                "context": "work",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["matched"] is True
        assert data["item_id"] == "practice.extended_exhale.001"
        assert data["content_class"] == "practice"
        assert data["type"] == "extended_exhale"

    def test_select_no_match(self, client: TestClient):
        response = client.get(
            "/practices/select",
            params={"purpose": "unknown", "direction": "nothing"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["matched"] is False
        assert data["item_id"] is None
        assert data["title"] == ""
        assert data["body"] == ""
        assert "unknown" in data["reason"]

    def test_select_english_locale(self, client: TestClient):
        response = client.get(
            "/practices/select",
            params={
                "purpose": "sleep",
                "direction": "prepare",
                "input_state": "restless",
                "locale": "en",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["matched"] is True
        assert data["title"] == "Softer jaw"
        assert "Close your eyes" in data["body"]

    def test_select_by_content_class(self, client: TestClient):
        response = client.get(
            "/practices/select",
            params={
                "purpose": "sleep",
                "direction": "prepare",
                "input_state": "restless",
                "content_class": "discipline",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["matched"] is True
        assert data["item_id"] == "discipline.sleep_discipline.001"
        assert data["content_class"] == "discipline"
        assert data["type"] == "sleep_discipline"

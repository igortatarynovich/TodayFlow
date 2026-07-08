"""Контракт: сгенерированная FastAPI OpenAPI схема и ключевые маршруты."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


# Маршруты из smoke / приёмки — регресс при переименовании префиксов
_CRITICAL_PATHS = frozenset(
    {
        "/auth/login",
        "/auth/signup",
        "/natal-chart/",
        "/tarot/daily/public",
        "/tarot/cards/{card_id}",
        "/reference/zodiac",
        "/reference/planets",
        "/compatibility/signs",
        "/compatibility/dynamics",
        "/compatibility/encyclopedia",
        "/compatibility/business-partnership",
        "/today",
        "/today/opening",
        "/today/checkin-prompt",
        "/today/core",
        "/today/scenarios",
        "/today/bundle",
        "/today/contract",
        "/today/state-map",
        "/today/evening",
        "/today/narrative",
        "/day-connection/{target_date}",
    }
)


@pytest.mark.smoke
def test_openapi_json_schema_and_critical_paths(client: TestClient):
    """OpenAPI 3.x, ключевые пути (smoke + контракт против случайного снятия маршрута)."""
    r = client.get("/openapi.json")
    assert r.status_code == 200, r.text
    spec = r.json()
    ver = spec.get("openapi") or spec.get("swagger")
    assert ver is not None
    assert str(ver).startswith("3."), f"expected OpenAPI 3.x, got {ver!r}"

    paths = spec.get("paths") or {}
    assert isinstance(paths, dict) and paths, "paths must be non-empty dict"
    missing = sorted(_CRITICAL_PATHS - set(paths))
    assert not missing, f"OpenAPI missing paths: {missing}"

    login = paths.get("/auth/login") or {}
    assert "post" in login, "/auth/login must declare POST"

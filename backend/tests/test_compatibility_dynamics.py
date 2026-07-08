"""POST /compatibility/dynamics — шаблонный режим без LLM."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


@pytest.mark.smoke
def test_compatibility_dynamics_template_quick(client: TestClient) -> None:
    r = client.post(
        "/compatibility/dynamics",
        json={
            "mode": "quick",
            "from_sign": "leo",
            "to_sign": "scorpio",
            "relationship_context": "unclear",
            "generation": "template",
        },
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert data.get("from_sign") == "leo"
    assert data.get("to_sign") == "scorpio"
    assert data.get("generation_source") == "template"
    assert isinstance(data.get("pair_dynamics"), dict)
    surface = data.get("product_surface")
    assert isinstance(surface, dict)
    assert len(surface.get("blocks", [])) >= 5
    fa = data.get("funnel_artifact")
    assert isinstance(fa, dict)
    assert fa.get("pipeline_version") == "funnel-v1"
    assert fa.get("accuracy_tier") == "signs_only"
    assert isinstance(fa.get("domain_scores"), list) and len(fa["domain_scores"]) >= 7
    assert isinstance(fa.get("timeline"), list) and len(fa["timeline"]) == 4


@pytest.mark.smoke
def test_compatibility_dynamics_precise_dates(client: TestClient) -> None:
    r = client.post(
        "/compatibility/dynamics",
        json={
            "mode": "precise",
            "birth_date_1": "1990-08-15",
            "birth_date_2": "1992-11-03",
            "generation": "template",
        },
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert data.get("from_sign")
    assert data.get("to_sign")
    fa = data.get("funnel_artifact")
    assert isinstance(fa, dict)
    assert fa.get("accuracy_tier") == "birth_dates"

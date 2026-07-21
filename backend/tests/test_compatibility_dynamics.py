"""POST /compatibility/dynamics — stability matrix (guest/registered, validation, LLM fallback)."""

from __future__ import annotations

from unittest.mock import patch

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
    assert len(surface.get("blocks", [])) == 1
    assert surface.get("scenarios") == []
    access = data.get("access_disclosure")
    assert isinstance(access, dict)
    assert access.get("tier") == "guest"
    assert "yes_no" in (access.get("locked_layers") or [])
    assert data.get("funnel_artifact") is None


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
    access = data.get("access_disclosure")
    assert isinstance(access, dict)
    assert access.get("tier") == "guest"
    assert data.get("funnel_artifact") is None


@pytest.mark.smoke
def test_compatibility_guest_llm_does_not_call_pipeline(client: TestClient) -> None:
    """Guest teaser must not wait on LLM — root cause of product hang."""
    with patch(
        "todayflow_backend.api.compatibility.run_compatibility_dynamics_pipeline"
    ) as pipeline, patch(
        "todayflow_backend.api.compatibility.generate_llm_base_model"
    ) as base_model:
        r = client.post(
            "/compatibility/dynamics",
            json={
                "mode": "quick",
                "from_sign": "aries",
                "to_sign": "libra",
                "generation": "llm",
                "locale": "ru",
            },
        )
    assert r.status_code == 200, r.text
    pipeline.assert_not_called()
    base_model.assert_not_called()
    data = r.json()
    assert data["generation_source"] == "template"
    assert data["access_disclosure"]["tier"] == "guest"


@pytest.mark.smoke
def test_compatibility_missing_sign_returns_422(client: TestClient) -> None:
    r = client.post(
        "/compatibility/dynamics",
        json={"mode": "quick", "from_sign": "leo", "generation": "template"},
    )
    assert r.status_code == 422
    detail = r.json().get("detail")
    assert isinstance(detail, dict)
    assert detail.get("code") == "signs_required"
    assert "знак" in str(detail.get("message", "")).lower()


@pytest.mark.smoke
def test_compatibility_missing_dates_returns_422(client: TestClient) -> None:
    r = client.post(
        "/compatibility/dynamics",
        json={"mode": "precise", "birth_date_1": "1990-08-15", "generation": "template"},
    )
    assert r.status_code == 422
    detail = r.json().get("detail")
    assert isinstance(detail, dict)
    assert detail.get("code") == "birth_dates_required"


@pytest.mark.smoke
def test_compatibility_llm_exception_falls_back_alive(client: TestClient) -> None:
    """Read path never calls LLM sync — Nebius down must not 500 baseline."""
    with patch(
        "todayflow_backend.api.compatibility.resolve_compat_access_tier",
        return_value="registered",
    ), patch(
        "todayflow_backend.api.compatibility.run_compatibility_dynamics_pipeline",
        side_effect=RuntimeError("llm_provider_down"),
    ), patch(
        "todayflow_backend.services.generation_jobs_v0.schedule_job_runner",
    ):
        r = client.post(
            "/compatibility/dynamics",
            json={
                "mode": "quick",
                "from_sign": "cancer",
                "to_sign": "pisces",
                "generation": "llm",
                "locale": "ru",
            },
        )
    assert r.status_code == 200, r.text
    data = r.json()
    assert data.get("product_surface")
    assert data.get("generation_source") == "template"
    lc = data.get("generation_lifecycle") or {}
    # Guest path when optional user is None — baseline_ready; registered needs auth override.
    assert lc.get("status") in ("baseline_ready", "enrichment_pending", "enrichment_failed")
    assert lc.get("is_fully_personal") is not True


@pytest.mark.smoke
def test_compatibility_personalized_uses_baseline_not_full_build(client: TestClient) -> None:
    """include_personalized must not call CoreProfileService.build (portrait LLM)."""
    from todayflow_backend.api.auth import get_optional_user
    from todayflow_backend.api.compatibility import get_core_profile_service
    from todayflow_backend.db.models import User
    from todayflow_backend.main import app

    fake_user = User(id=99999, email="compat-pers@example.com", password_hash="x")
    app.dependency_overrides[get_optional_user] = lambda: fake_user
    svc = get_core_profile_service()
    try:
        with patch.object(
            svc,
            "build",
            side_effect=AssertionError("full build must not run"),
        ), patch.object(
            svc,
            "build_cached_or_baseline",
            return_value={
                "is_ready": False,
                "profile_hash": "test",
                "astro": {"sun_sign": "leo"},
                "baseline": {"element_focus": "Огонь", "rhythm_style": "Импульс"},
                "numerology": {},
            },
        ), patch(
            "todayflow_backend.api.compatibility.resolve_compat_access_tier",
            return_value="registered",
        ):
            r = client.post(
                "/compatibility/dynamics",
                json={
                    "mode": "quick",
                    "from_sign": "leo",
                    "to_sign": "aquarius",
                    "generation": "template",
                    "include_personalized": True,
                    "locale": "ru",
                },
            )
        assert r.status_code == 200, r.text
        assert r.json().get("personalized") is not None
    finally:
        app.dependency_overrides.pop(get_optional_user, None)


@pytest.mark.smoke
def test_openai_compatible_client_disables_retries() -> None:
    """Retries multiply ReadTimeout into multi-minute hangs — must stay off."""
    from todayflow_backend.core import llm_openai_compatible as llm_mod

    with patch.object(llm_mod, "_resolve_llm_credentials", return_value=("sk-test", "https://example.test/v1")), patch(
        "openai.OpenAI"
    ) as openai_cls:
        llm_mod.get_openai_compatible_client()
    kwargs = openai_cls.call_args.kwargs
    assert kwargs.get("max_retries") == 0
    assert float(kwargs.get("timeout") or 0) > 0

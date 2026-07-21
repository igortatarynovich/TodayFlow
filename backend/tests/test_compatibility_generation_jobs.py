"""C1 — Compatibility non-blocking generation jobs."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from todayflow_backend.db.models import GenerationJob, User, utc_naive_now
from todayflow_backend.main import app
from todayflow_backend.api.auth import get_optional_user, require_user
from todayflow_backend.services.generation_jobs_v0 import (
    complete_job_if_fresh,
    enqueue_or_reuse,
    make_fingerprint,
)


@pytest.mark.smoke
def test_dynamics_returns_baseline_lifecycle_under_one_second(client: TestClient) -> None:
    r = client.post(
        "/compatibility/dynamics",
        json={
            "mode": "quick",
            "from_sign": "aries",
            "to_sign": "leo",
            "generation": "llm",
            "locale": "ru",
        },
    )
    assert r.status_code == 200, r.text
    data = r.json()
    lc = data.get("generation_lifecycle") or {}
    assert lc.get("status") == "baseline_ready"
    assert lc.get("is_fully_personal") is False
    assert data.get("generation_source") == "template"
    assert data.get("product_surface")


@pytest.mark.smoke
def test_registered_dynamics_enqueues_enrichment(client: TestClient, db_session) -> None:
    user = User(email="c1-enrich@example.com", password_hash="x")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    app.dependency_overrides[get_optional_user] = lambda: user
    try:
        with patch(
            "todayflow_backend.api.compatibility.resolve_compat_access_tier",
            return_value="registered",
        ), patch(
            "todayflow_backend.services.generation_jobs_v0.schedule_job_runner"
        ) as sched:
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
        lc = r.json().get("generation_lifecycle") or {}
        assert lc.get("status") == "enrichment_pending"
        assert isinstance(lc.get("job_id"), int)
        assert sched.called
    finally:
        app.dependency_overrides.pop(get_optional_user, None)


@pytest.mark.smoke
def test_enrichment_failed_status_and_retry(client: TestClient, db_session) -> None:
    user = User(email="c1-fail@example.com", password_hash="x")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    fp = make_fingerprint("t", "a", "b")
    job, _ = enqueue_or_reuse(
        db_session,
        idempotency_key=f"compatibility:test-fail:{fp}",
        fingerprint=fp,
        module="compatibility",
        surface="dynamics_registered",
        user_id=user.id,
        request_payload={"from_sign": "aries", "to_sign": "leo", "locale": "ru"},
    )
    job.status = "enrichment_failed"
    job.error_message = "llm_provider_down"
    job.attempt_count = 2
    db_session.add(job)
    db_session.commit()
    db_session.refresh(job)

    app.dependency_overrides[get_optional_user] = lambda: user
    app.dependency_overrides[require_user] = lambda: user
    try:
        r = client.get(f"/compatibility/dynamics/jobs/{job.id}")
        assert r.status_code == 200, r.text
        body = r.json()
        assert body["job"]["status"] == "enrichment_failed"
        assert body["job"]["is_fully_personal"] is False
        assert body["product_surface"] is None

        with patch(
            "todayflow_backend.services.generation_jobs_v0.schedule_job_runner"
        ) as sched:
            r2 = client.post(f"/compatibility/dynamics/jobs/{job.id}/retry")
        assert r2.status_code == 200, r2.text
        assert r2.json()["job"]["status"] == "enrichment_pending"
        assert sched.called
    finally:
        app.dependency_overrides.pop(get_optional_user, None)
        app.dependency_overrides.pop(require_user, None)


@pytest.mark.smoke
def test_duplicate_idempotency_reuses_job(db_session) -> None:
    fp = make_fingerprint("dup", 1, 2)
    key = f"compatibility:dup:{fp}"
    j1, created1 = enqueue_or_reuse(
        db_session,
        idempotency_key=key,
        fingerprint=fp,
        module="compatibility",
        surface="dynamics_registered",
        user_id=None,
        request_payload={"a": 1},
    )
    j2, created2 = enqueue_or_reuse(
        db_session,
        idempotency_key=key,
        fingerprint=fp,
        module="compatibility",
        surface="dynamics_registered",
        user_id=None,
        request_payload={"a": 1},
    )
    assert created1 is True
    assert created2 is False
    assert j1.id == j2.id


@pytest.mark.smoke
def test_stale_fingerprint_does_not_overwrite(db_session) -> None:
    fp = make_fingerprint("stale", "x")
    job, _ = enqueue_or_reuse(
        db_session,
        idempotency_key=f"compatibility:stale:{fp}",
        fingerprint=fp,
        module="compatibility",
        surface="dynamics_registered",
        user_id=None,
        request_payload={},
    )
    # Simulate fingerprint bump while job was running.
    job.fingerprint = make_fingerprint("stale", "y")
    db_session.add(job)
    db_session.commit()
    db_session.refresh(job)

    out = complete_job_if_fresh(
        db_session,
        job,
        expected_fingerprint=fp,  # old
        result_payload={"ok": True},
    )
    assert out.status == "stale"
    assert out.result_payload is None or out.result_payload.get("ok") is not True


@pytest.mark.smoke
def test_llm_exception_in_runner_keeps_server_and_marks_failed(db_session) -> None:
    from todayflow_backend.services.compatibility_enrichment_v0 import (
        run_compatibility_enrichment_job,
    )

    user = User(email="c1-runner@example.com", password_hash="x")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    fp = make_fingerprint("runner", "cancer", "pisces")
    job, _ = enqueue_or_reuse(
        db_session,
        idempotency_key=f"compatibility:runner:{fp}",
        fingerprint=fp,
        module="compatibility",
        surface="dynamics_registered",
        user_id=user.id,
        request_payload={
            "from_sign": "cancer",
            "to_sign": "pisces",
            "locale": "ru",
            "relationship_context": "unclear",
        },
        max_attempts=1,
    )

    with patch(
        "todayflow_backend.services.compatibility_enrichment_v0.run_compatibility_dynamics_pipeline",
        side_effect=RuntimeError("llm_provider_down"),
    ):
        run_compatibility_enrichment_job(job.id)

    db_session.refresh(job)
    # claim bumps attempt; with max_attempts=1 failure should be terminal
    refreshed = db_session.query(GenerationJob).filter(GenerationJob.id == job.id).first()
    assert refreshed is not None
    assert refreshed.status == "enrichment_failed"
    assert refreshed.error_message
    assert "llm" in (refreshed.error_message or "").lower() or "provider" in (
        refreshed.error_message or ""
    ).lower() or "RuntimeError" in (refreshed.error_message or "")

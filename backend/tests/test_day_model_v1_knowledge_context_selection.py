"""A1.1 — Knowledge context selection tests."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from todayflow_backend.services.day_model_v1_active_knowledge import (
    DAY_ACTIVE_KNOWLEDGE_V1_CONTRACT,
)
from todayflow_backend.services.day_model_v1_knowledge_context_selection import (
    DAY_CONTEXT_SLICE_V1_KEYS,
    EXCLUSION_CONFLICT_LOSER,
    EXCLUSION_INELIGIBLE,
    EXCLUSION_SOFT_CAP,
    HARD_CAP_DEFAULT,
    KNOWLEDGE_CONTEXT_SLICE_V1_CONTRACT,
    SOFT_CAP_DEFAULT,
    compute_freshness_score,
    compute_final_score,
    select_knowledge_context_v1,
    validate_knowledge_context_slice_v1,
)
from todayflow_backend.services.day_model_v1_knowledge_candidate import (
    KNOWLEDGE_TYPE_CONTENT_AFFINITY,
    KNOWLEDGE_TYPE_RESPONSE_STYLE,
)

NOW = datetime(2026, 5, 31, 12, 0, 0, tzinfo=UTC)


def _active(**overrides):
    base = {
        "contract_version": DAY_ACTIVE_KNOWLEDGE_V1_CONTRACT,
        "knowledge_id": "know-test-001",
        "source_knowledge_candidate_id": "kcand-test-001",
        "knowledge_type": KNOWLEDGE_TYPE_CONTENT_AFFINITY,
        "claim": "prefers_content_key_group:day.guidance",
        "confidence": 0.8,
        "evidence_count": 7,
        "evidence_window_days": 21,
        "evidence_signal_ids": [f"lsig-{i}" for i in range(7)],
        "source_pattern_id": "pat-test-001",
        "status": "active",
        "created_at": "2026-05-31T12:00:00Z",
        "last_confirmed_at": "2026-05-31T12:00:00Z",
        "expires_at": None,
        "review_required": False,
        "profile_update_allowed": False,
        "memory_update_allowed": False,
        "ranking_update_allowed": False,
    }
    base.update(overrides)
    return base


def test_freshness_today_vs_30_days():
    fresh = _active(last_confirmed_at="2026-05-31T12:00:00Z")
    stale = _active(
        knowledge_id="know-stale",
        last_confirmed_at="2026-05-01T12:00:00Z",
    )
    assert compute_freshness_score(fresh, now=NOW) == 1.0
    assert compute_freshness_score(stale, now=NOW) == 0.6


def test_final_score_is_confidence_times_freshness_times_relevance():
    score = compute_final_score(
        _active(confidence=0.8),
        freshness_score=0.9,
        relevance_score=0.5,
    )
    assert abs(score - 0.36) < 0.001


def test_eligibility_and_selection_produces_slice():
    pool = [
        _active(),
        _active(
            knowledge_id="know-002",
            claim="prefers_content_key_group:day.action",
        ),
    ]
    slice_out = select_knowledge_context_v1(
        pool,
        day_context={"content_keys": ["day.guidance"], "surface": "day_guidance_card"},
        target_surface="day_guidance_card",
        now=NOW,
    )
    assert slice_out["contract_version"] == KNOWLEDGE_CONTEXT_SLICE_V1_CONTRACT
    assert len(slice_out["selected_facts"]) >= 1
    assert slice_out["selected_facts"][0]["knowledge_id"] == "know-test-001"


def test_fresher_wins_conflict_same_prefix():
    pool = [
        _active(
            knowledge_id="know-old",
            claim="responds_to_surface:long_reflection",
            knowledge_type=KNOWLEDGE_TYPE_RESPONSE_STYLE,
            last_confirmed_at="2025-05-31T12:00:00Z",
            confidence=0.85,
        ),
        _active(
            knowledge_id="know-new",
            claim="responds_to_surface:short_action",
            knowledge_type=KNOWLEDGE_TYPE_RESPONSE_STYLE,
            last_confirmed_at="2026-05-30T12:00:00Z",
            confidence=0.75,
        ),
    ]
    slice_out = select_knowledge_context_v1(
        pool,
        day_context={"surface": "day_guidance_card"},
        target_surface="day_guidance_card",
        now=NOW,
    )
    selected_ids = {f["knowledge_id"] for f in slice_out["selected_facts"]}
    assert "know-new" in selected_ids
    assert "know-old" not in selected_ids
    assert any(r["winner_knowledge_id"] == "know-new" for r in slice_out["conflict_resolutions"])
    assert any(e["reason"] == EXCLUSION_CONFLICT_LOSER for e in slice_out["excluded_facts"])


def test_soft_cap_three_hard_cap_five():
    pool = [
        _active(
            knowledge_id=f"know-{i}",
            claim=f"prefers_content_key_group:day.topic{i}",
        )
        for i in range(6)
    ]
    slice_out = select_knowledge_context_v1(
        pool,
        day_context={"content_keys": [f"day.topic{i}" for i in range(6)]},
        target_surface="day_guidance_card",
        soft_cap=3,
        hard_cap=5,
        now=NOW,
    )
    assert len(slice_out["selected_facts"]) <= 5
    assert slice_out["soft_cap"] == 3
    assert slice_out["hard_cap"] == 5


def test_ineligible_surface_excluded():
    pool = [_active()]
    slice_out = select_knowledge_context_v1(
        pool,
        target_surface="content_ranker",
        now=NOW,
    )
    assert slice_out["selected_facts"] == []
    assert any(e["reason"] == EXCLUSION_INELIGIBLE for e in slice_out["excluded_facts"])


def test_relevance_boosts_matching_day_context():
    low = _active(
        knowledge_id="know-low",
        claim="prefers_content_key_group:day.other",
    )
    high = _active(
        knowledge_id="know-high",
        claim="prefers_content_key_group:day.guidance",
    )
    slice_out = select_knowledge_context_v1(
        [low, high],
        day_context={"content_keys": ["day.guidance"]},
        target_surface="day_guidance_card",
        now=NOW,
    )
    assert slice_out["selected_facts"][0]["knowledge_id"] == "know-high"
    assert slice_out["relevance_scores"]["know-high"] > slice_out["relevance_scores"]["know-low"]


def test_mutation_flags_false():
    slice_out = select_knowledge_context_v1([_active()], target_surface="day_guidance_card", now=NOW)
    assert slice_out["profile_update_allowed"] is False
    assert slice_out["memory_update_allowed"] is False
    assert slice_out["ranking_model_update_allowed"] is False


def test_output_shape_stable():
    slice_out = select_knowledge_context_v1(
        [_active()],
        day_context={"content_keys": ["day.guidance"]},
        goals=[{"tag": "day.guidance"}],
        practices=[{"completion_rate_high": True}],
        evolution_stage="seeker",
        target_surface="day_guidance_card",
        now=NOW,
    )
    assert set(slice_out.keys()) == set(DAY_CONTEXT_SLICE_V1_KEYS)
    assert validate_knowledge_context_slice_v1(slice_out) == []
    assert "freshness_scores" in slice_out
    assert "relevance_scores" in slice_out
    assert "final_scores" in slice_out
    assert slice_out["soft_cap"] == SOFT_CAP_DEFAULT
    assert slice_out["hard_cap"] == HARD_CAP_DEFAULT


def test_stale_knowledge_ranked_lower_than_fresh():
    fresh = _active(
        knowledge_id="know-fresh",
        last_confirmed_at="2026-05-31T12:00:00Z",
        confidence=0.8,
    )
    stale = _active(
        knowledge_id="know-stale",
        claim="prefers_content_key_group:day.action",
        last_confirmed_at=(NOW - timedelta(days=60)).isoformat().replace("+00:00", "Z"),
        confidence=0.8,
    )
    slice_out = select_knowledge_context_v1(
        [stale, fresh],
        day_context={"content_keys": ["day.guidance", "day.action"]},
        target_surface="day_guidance_card",
        now=NOW,
    )
    assert slice_out["final_scores"]["know-fresh"] > slice_out["final_scores"]["know-stale"]

"""Пик индекса роста для колец: не падает при ослаблении текущего дня."""

from todayflow_backend.api.today import _sync_reward_evolution_peak
from todayflow_backend.constants.reward_rings import compute_reward_rings_earned
from todayflow_backend.db import models as db_models


def test_sync_reward_evolution_peak_monotonic(db_session):
    user = db_models.User(email="peak@test.flow", password_hash="x")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    assert _sync_reward_evolution_peak(db_session, user.id, 55) == 55
    db_session.refresh(user)
    assert user.reward_evolution_index_peak == 55

    assert _sync_reward_evolution_peak(db_session, user.id, 40) == 55
    db_session.refresh(user)
    assert user.reward_evolution_index_peak == 55

    assert _sync_reward_evolution_peak(db_session, user.id, 72) == 72
    db_session.refresh(user)
    assert user.reward_evolution_index_peak == 72


def test_compute_rings_uses_peak_not_current():
    peak = 72
    current = 35
    rings_peak = compute_reward_rings_earned(peak)
    rings_current = compute_reward_rings_earned(current)
    assert len(rings_peak) > len(rings_current)
    assert "ring_oracle" in rings_peak
    assert "ring_oracle" not in rings_current


def test_sync_records_ring_tier_reached_at_once(db_session):
    user = db_models.User(email="tiers@test.flow", password_hash="x")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    _sync_reward_evolution_peak(db_session, user.id, 55)
    rows = (
        db_session.query(db_models.RewardRingTierReached)
        .filter(db_models.RewardRingTierReached.user_id == user.id)
        .order_by(db_models.RewardRingTierReached.tier_key)
        .all()
    )
    keys = {r.tier_key for r in rows}
    assert "ring_seeker" in keys
    assert "ring_initiate" in keys
    assert "ring_observer" in keys
    assert "ring_alchemist" not in keys
    first_observer = next(r for r in rows if r.tier_key == "ring_observer")
    first_at = first_observer.reached_at

    _sync_reward_evolution_peak(db_session, user.id, 40)
    _sync_reward_evolution_peak(db_session, user.id, 55)
    again = (
        db_session.query(db_models.RewardRingTierReached)
        .filter(
            db_models.RewardRingTierReached.user_id == user.id,
            db_models.RewardRingTierReached.tier_key == "ring_observer",
        )
        .one()
    )
    assert again.reached_at == first_at

    _sync_reward_evolution_peak(db_session, user.id, 72)
    keys_after = {
        r.tier_key
        for r in db_session.query(db_models.RewardRingTierReached)
        .filter(db_models.RewardRingTierReached.user_id == user.id)
        .all()
    }
    assert "ring_oracle" in keys_after
    assert again.reached_at == first_at

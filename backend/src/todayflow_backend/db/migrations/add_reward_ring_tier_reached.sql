-- Migration: persist first-cross timestamps for reward ring tiers (merch eligibility)
-- Date: 2026-07-24

CREATE TABLE IF NOT EXISTS reward_ring_tier_reached (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    tier_key VARCHAR(64) NOT NULL,
    reached_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_reward_ring_tier_user_tier UNIQUE (user_id, tier_key)
);

CREATE INDEX IF NOT EXISTS ix_reward_ring_tier_reached_user_id
    ON reward_ring_tier_reached (user_id);

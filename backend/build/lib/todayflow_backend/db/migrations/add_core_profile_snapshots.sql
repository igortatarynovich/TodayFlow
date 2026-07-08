-- Migration: Add persistent core profile snapshots
-- Date: 2026-02-15

CREATE TABLE IF NOT EXISTS core_profile_snapshots (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    profile_hash VARCHAR(64) NOT NULL,
    profile_version VARCHAR(32) NOT NULL DEFAULT 'core-v1',
    payload JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, profile_hash)
);

CREATE INDEX IF NOT EXISTS idx_core_profile_snapshots_user ON core_profile_snapshots(user_id);
CREATE INDEX IF NOT EXISTS idx_core_profile_snapshots_hash ON core_profile_snapshots(profile_hash);

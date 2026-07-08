CREATE TABLE IF NOT EXISTS cum_confidence_snapshots (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    snapshot_date DATE NOT NULL,
    overall DOUBLE PRECISION NOT NULL,
    by_domain JSONB NOT NULL DEFAULT '{}'::jsonb,
    meaning_events_28d INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_cum_confidence_snapshot_user_date UNIQUE (user_id, snapshot_date)
);

CREATE INDEX IF NOT EXISTS idx_cum_confidence_snapshots_user_date
    ON cum_confidence_snapshots(user_id, snapshot_date DESC);

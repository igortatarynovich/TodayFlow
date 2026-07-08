CREATE TABLE IF NOT EXISTS meaning_events (
    id SERIAL PRIMARY KEY,
    event_id VARCHAR(64) NOT NULL UNIQUE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    event_type VARCHAR(64) NOT NULL,
    event_source VARCHAR(32) NOT NULL,
    event_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    local_date DATE NOT NULL,
    quality_score DOUBLE PRECISION NOT NULL DEFAULT 1.0,
    payload JSONB,
    idempotency_key VARCHAR(128) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_meaning_event_user_idempotency UNIQUE (user_id, idempotency_key)
);

CREATE INDEX IF NOT EXISTS idx_meaning_events_user_local_date ON meaning_events(user_id, local_date DESC);
CREATE INDEX IF NOT EXISTS idx_meaning_events_user_event_time ON meaning_events(user_id, event_time DESC);
CREATE INDEX IF NOT EXISTS idx_meaning_events_user_type ON meaning_events(user_id, event_type);

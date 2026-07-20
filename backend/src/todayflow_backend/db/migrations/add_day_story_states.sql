-- Day story freshness SoT (fingerprint / stale / generation_seq).
CREATE TABLE IF NOT EXISTS day_story_states (
    id SERIAL PRIMARY KEY,
    owner_key VARCHAR(96) NOT NULL,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    guest_session_id VARCHAR(64),
    local_date DATE NOT NULL,
    timezone_name VARCHAR(64) NOT NULL DEFAULT 'UTC',
    locale VARCHAR(16) NOT NULL DEFAULT 'ru',
    fingerprint VARCHAR(64),
    expected_fingerprint VARCHAR(64),
    stale BOOLEAN NOT NULL DEFAULT FALSE,
    generation_seq INTEGER NOT NULL DEFAULT 0,
    last_generation_log_id INTEGER REFERENCES generation_logs(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
    CONSTRAINT uq_day_story_owner_date UNIQUE (owner_key, local_date)
);

CREATE INDEX IF NOT EXISTS ix_day_story_states_user_date ON day_story_states (user_id, local_date);

-- Ensure day_symbol_states exists on older deploys (create_all may already have it).
CREATE TABLE IF NOT EXISTS day_symbol_states (
    id SERIAL PRIMARY KEY,
    owner_key VARCHAR(96) NOT NULL,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    guest_session_id VARCHAR(64),
    local_date DATE NOT NULL,
    timezone_name VARCHAR(64) NOT NULL DEFAULT 'UTC',
    card_status VARCHAR(32) NOT NULL DEFAULT 'not_revealed',
    card_id VARCHAR(32),
    card_orientation VARCHAR(16),
    card_generated_at TIMESTAMP WITHOUT TIME ZONE,
    card_revealed_at TIMESTAMP WITHOUT TIME ZONE,
    card_reveal_source VARCHAR(64),
    card_idempotency_key VARCHAR(128),
    number_status VARCHAR(32) NOT NULL DEFAULT 'not_revealed',
    number_value INTEGER,
    number_reduced INTEGER,
    number_is_master BOOLEAN NOT NULL DEFAULT FALSE,
    number_title VARCHAR(120),
    number_summary TEXT,
    number_generated_at TIMESTAMP WITHOUT TIME ZONE,
    number_revealed_at TIMESTAMP WITHOUT TIME ZONE,
    number_reveal_source VARCHAR(64),
    number_idempotency_key VARCHAR(128),
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
    CONSTRAINT uq_day_symbol_owner_date UNIQUE (owner_key, local_date),
    CONSTRAINT uq_day_symbol_card_idem UNIQUE (card_idempotency_key),
    CONSTRAINT uq_day_symbol_number_idem UNIQUE (number_idempotency_key)
);

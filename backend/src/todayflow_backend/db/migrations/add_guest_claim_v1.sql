-- Full guest claim SoT (session + day snapshot + claim audit).
CREATE TABLE IF NOT EXISTS guest_sessions (
    id SERIAL PRIMARY KEY,
    guest_session_id VARCHAR(64) NOT NULL UNIQUE,
    session_secret_hash VARCHAR(128) NOT NULL,
    locale VARCHAR(16),
    timezone_name VARCHAR(64),
    claim_token_hash VARCHAR(128),
    claim_token_expires_at TIMESTAMP WITHOUT TIME ZONE,
    claim_nonce VARCHAR(64),
    claimed_at TIMESTAMP WITHOUT TIME ZONE,
    claimed_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    sealed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS guest_day_snapshots (
    id SERIAL PRIMARY KEY,
    guest_session_id VARCHAR(64) NOT NULL,
    local_date DATE NOT NULL,
    timezone_name VARCHAR(64) NOT NULL DEFAULT 'UTC',
    locale VARCHAR(16) NOT NULL DEFAULT 'ru',
    mood JSON,
    goals JSON,
    onboarding JSON,
    first_result JSON,
    ritual JSON,
    today_state JSON,
    day_story JSON,
    story_fingerprint VARCHAR(64),
    story_status VARCHAR(32),
    profile_draft JSON,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
    CONSTRAINT uq_guest_day_session_date UNIQUE (guest_session_id, local_date)
);

CREATE INDEX IF NOT EXISTS ix_guest_day_snapshots_session ON guest_day_snapshots (guest_session_id);

CREATE TABLE IF NOT EXISTS guest_claim_records (
    id SERIAL PRIMARY KEY,
    guest_session_id VARCHAR(64) NOT NULL,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    local_date DATE,
    claim_status VARCHAR(32) NOT NULL DEFAULT 'completed',
    transferred_blocks JSON NOT NULL DEFAULT '[]',
    conflicts JSON NOT NULL DEFAULT '[]',
    story_status VARCHAR(32),
    story_refresh_required BOOLEAN NOT NULL DEFAULT FALSE,
    redirect_target VARCHAR(256) NOT NULL DEFAULT '/today?first=1',
    result_payload JSON,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
    CONSTRAINT uq_guest_claim_session_user UNIQUE (guest_session_id, user_id)
);

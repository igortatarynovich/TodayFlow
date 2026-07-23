-- Access + Refresh token store (AUTH_SESSION_CONTRACT_V1).
CREATE TABLE IF NOT EXISTS refresh_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(128) NOT NULL UNIQUE,
    device_label VARCHAR(128),
    expires_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    revoked_at TIMESTAMP WITHOUT TIME ZONE,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
    last_used_at TIMESTAMP WITHOUT TIME ZONE
);

CREATE INDEX IF NOT EXISTS ix_refresh_tokens_user_id ON refresh_tokens (user_id);
CREATE INDEX IF NOT EXISTS ix_refresh_tokens_token_hash ON refresh_tokens (token_hash);

-- Durable guest profiles before email claim (PRODUCT_DATA_INTAKE).
CREATE TABLE IF NOT EXISTS guest_profiles (
    id SERIAL PRIMARY KEY,
    guest_session_id VARCHAR(64) NOT NULL,
    local_key VARCHAR(32) NOT NULL,
    display_name VARCHAR(128),
    birth_date DATE NOT NULL,
    birth_time TIME,
    birth_time_known BOOLEAN NOT NULL DEFAULT FALSE,
    location_name VARCHAR,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    timezone_name VARCHAR(64),
    relation VARCHAR(32),
    is_owner_candidate BOOLEAN NOT NULL DEFAULT FALSE,
    natal_facts JSON,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
    CONSTRAINT uq_guest_profiles_session_key UNIQUE (guest_session_id, local_key)
);

CREATE INDEX IF NOT EXISTS ix_guest_profiles_session ON guest_profiles (guest_session_id);

-- Non-blocking generation jobs (C1): baseline first, enrichment async.
CREATE TABLE IF NOT EXISTS generation_jobs (
    id SERIAL PRIMARY KEY,
    idempotency_key VARCHAR(255) NOT NULL,
    fingerprint VARCHAR(64) NOT NULL,
    module VARCHAR(64) NOT NULL,
    surface VARCHAR(64) NOT NULL,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    status VARCHAR(32) NOT NULL DEFAULT 'enrichment_pending',
    attempt_count INTEGER NOT NULL DEFAULT 0,
    max_attempts INTEGER NOT NULL DEFAULT 2,
    request_payload JSONB,
    result_payload JSONB,
    baseline_payload JSONB,
    error_message TEXT,
    generation_log_id INTEGER REFERENCES generation_logs(id) ON DELETE SET NULL,
    locked_at TIMESTAMP WITHOUT TIME ZONE,
    started_at TIMESTAMP WITHOUT TIME ZONE,
    finished_at TIMESTAMP WITHOUT TIME ZONE,
    expires_at TIMESTAMP WITHOUT TIME ZONE,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
    CONSTRAINT uq_generation_jobs_idempotency UNIQUE (idempotency_key)
);

CREATE INDEX IF NOT EXISTS ix_generation_jobs_user_module
    ON generation_jobs (user_id, module, status);
CREATE INDEX IF NOT EXISTS ix_generation_jobs_fingerprint
    ON generation_jobs (fingerprint);
CREATE INDEX IF NOT EXISTS ix_generation_jobs_status_updated
    ON generation_jobs (status, updated_at);

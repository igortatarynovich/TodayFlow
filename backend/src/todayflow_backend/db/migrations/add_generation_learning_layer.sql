-- Migration: Add prompt versions, generation logs and generation feedback
-- Date: 2026-03-25

CREATE TABLE IF NOT EXISTS prompt_versions (
    id SERIAL PRIMARY KEY,
    module VARCHAR(64) NOT NULL,
    version VARCHAR(64) NOT NULL,
    prompt_kind VARCHAR(32) NOT NULL DEFAULT 'system',
    label VARCHAR(255),
    prompt_text TEXT NOT NULL,
    metadata JSONB,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(module, version, prompt_kind)
);

CREATE INDEX IF NOT EXISTS idx_prompt_versions_module ON prompt_versions(module);
CREATE INDEX IF NOT EXISTS idx_prompt_versions_active ON prompt_versions(is_active);

CREATE TABLE IF NOT EXISTS generation_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    core_profile_snapshot_id INTEGER REFERENCES core_profile_snapshots(id) ON DELETE SET NULL,
    prompt_version_id INTEGER REFERENCES prompt_versions(id) ON DELETE SET NULL,
    module VARCHAR(64) NOT NULL,
    surface VARCHAR(64),
    model VARCHAR(128),
    locale VARCHAR(16),
    input_payload JSONB,
    system_prompt TEXT,
    user_prompt TEXT,
    raw_response TEXT,
    normalized_response JSONB,
    status VARCHAR(32) NOT NULL DEFAULT 'success',
    used_fallback BOOLEAN NOT NULL DEFAULT FALSE,
    error_message TEXT,
    duration_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_generation_logs_user ON generation_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_generation_logs_module ON generation_logs(module);
CREATE INDEX IF NOT EXISTS idx_generation_logs_snapshot ON generation_logs(core_profile_snapshot_id);
CREATE INDEX IF NOT EXISTS idx_generation_logs_created_at ON generation_logs(created_at DESC);

CREATE TABLE IF NOT EXISTS generation_feedback (
    id SERIAL PRIMARY KEY,
    generation_log_id INTEGER NOT NULL REFERENCES generation_logs(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    signal VARCHAR(64) NOT NULL,
    score INTEGER,
    note TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_generation_feedback_generation ON generation_feedback(generation_log_id);
CREATE INDEX IF NOT EXISTS idx_generation_feedback_user ON generation_feedback(user_id);
CREATE INDEX IF NOT EXISTS idx_generation_feedback_signal ON generation_feedback(signal);

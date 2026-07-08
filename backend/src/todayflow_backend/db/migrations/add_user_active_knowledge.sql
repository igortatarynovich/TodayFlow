CREATE TABLE IF NOT EXISTS user_active_knowledge (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    knowledge_id VARCHAR(64) NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'active',
    payload JSONB NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_user_active_knowledge UNIQUE (user_id, knowledge_id)
);

CREATE INDEX IF NOT EXISTS idx_user_active_knowledge_user_status
    ON user_active_knowledge(user_id, status);

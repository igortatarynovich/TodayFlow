-- Migration: Add tarot_favorites table
-- Date: 2024

CREATE TABLE IF NOT EXISTS tarot_favorites (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    card_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, card_id)
);

CREATE INDEX IF NOT EXISTS idx_tarot_favorites_user_id ON tarot_favorites(user_id);
CREATE INDEX IF NOT EXISTS idx_tarot_favorites_card_id ON tarot_favorites(card_id);


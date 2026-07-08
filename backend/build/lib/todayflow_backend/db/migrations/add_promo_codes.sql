-- Migration: Add promo_codes and promo_code_usages tables
-- Created: 2025-01-XX

CREATE TABLE IF NOT EXISTS promo_codes (
    id SERIAL PRIMARY KEY,
    code VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    discount_type VARCHAR(50) NOT NULL, -- 'percentage' or 'fixed_amount'
    discount_value FLOAT NOT NULL,
    min_amount INTEGER, -- Minimum purchase amount in cents
    max_discount INTEGER, -- Maximum discount in cents (for percentage)
    valid_from TIMESTAMP NOT NULL,
    valid_until TIMESTAMP,
    max_uses INTEGER, -- NULL = unlimited
    current_uses INTEGER DEFAULT 0,
    applicable_to VARCHAR(50) NOT NULL DEFAULT 'all', -- 'subscriptions', 'reports', 'all'
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS promo_code_usages (
    id SERIAL PRIMARY KEY,
    promo_code_id INTEGER NOT NULL REFERENCES promo_codes(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    order_id VARCHAR(255), -- Stripe order/subscription ID
    discount_amount INTEGER NOT NULL, -- Discount in cents
    original_amount INTEGER NOT NULL, -- Original amount in cents
    final_amount INTEGER NOT NULL, -- Final amount after discount
    used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_promo_codes_code ON promo_codes(code);
CREATE INDEX IF NOT EXISTS idx_promo_codes_active ON promo_codes(is_active);
CREATE INDEX IF NOT EXISTS idx_promo_code_usages_user_id ON promo_code_usages(user_id);
CREATE INDEX IF NOT EXISTS idx_promo_code_usages_promo_code_id ON promo_code_usages(promo_code_id);

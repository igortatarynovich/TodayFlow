-- Migration: Add personalization settings to user_settings table
-- Date: 2026-01-04

-- Add astrology_level column (beginner, intermediate, advanced)
ALTER TABLE user_settings
ADD COLUMN IF NOT EXISTS astrology_level VARCHAR(20) DEFAULT 'beginner';

-- Add text_preference column (brief, detailed, comprehensive)
ALTER TABLE user_settings
ADD COLUMN IF NOT EXISTS text_preference VARCHAR(20) DEFAULT 'detailed';

-- Add comment
COMMENT ON COLUMN user_settings.astrology_level IS 'User astrology knowledge level: beginner, intermediate, advanced';
COMMENT ON COLUMN user_settings.text_preference IS 'Preferred text detail level: brief, detailed, comprehensive';


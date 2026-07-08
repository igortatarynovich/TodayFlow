-- Migration: user gender for Russian copy agreement (female / male / unspecified)
-- Date: 2026-05-04

ALTER TABLE user_settings
ADD COLUMN IF NOT EXISTS gender VARCHAR(20);

COMMENT ON COLUMN user_settings.gender IS 'User gender for wording: female, male, unspecified';

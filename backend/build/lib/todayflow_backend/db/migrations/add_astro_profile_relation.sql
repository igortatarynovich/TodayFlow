-- Migration: Add relation field to astro_profiles for multi-profile contract
-- Date: 2026-03-27

ALTER TABLE astro_profiles
ADD COLUMN IF NOT EXISTS relation VARCHAR;

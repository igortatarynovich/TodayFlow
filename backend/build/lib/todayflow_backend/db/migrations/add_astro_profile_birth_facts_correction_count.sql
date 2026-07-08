-- Migration: limit repeated edits to birth date/time/place per astro profile (clarifications allowed, not constant churn)
-- Date: 2026-04-25

ALTER TABLE astro_profiles
ADD COLUMN IF NOT EXISTS birth_facts_correction_count INTEGER NOT NULL DEFAULT 0;

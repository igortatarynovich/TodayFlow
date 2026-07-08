-- Migration: cooldown between birth-facts corrections per astro profile (anti-abuse)
-- Date: 2026-04-25

ALTER TABLE astro_profiles
ADD COLUMN IF NOT EXISTS birth_facts_last_changed_at TIMESTAMP NULL;

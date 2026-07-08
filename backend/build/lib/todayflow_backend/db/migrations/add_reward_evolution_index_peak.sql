-- Migration: persist peak evolution index for reward rings (rings stay earned if index drops)
-- Date: 2026-03-29

ALTER TABLE users ADD COLUMN IF NOT EXISTS reward_evolution_index_peak INTEGER NOT NULL DEFAULT 0;

-- Migration: persist lightweight Today signal answers on day_connections
-- Date: 2026-03-28

ALTER TABLE day_connections
ADD COLUMN IF NOT EXISTS ritual_feedback VARCHAR(16);

ALTER TABLE day_connections
ADD COLUMN IF NOT EXISTS quick_decision_answer VARCHAR(16);

ALTER TABLE day_connections
ADD COLUMN IF NOT EXISTS question_of_day_answer VARCHAR(120);

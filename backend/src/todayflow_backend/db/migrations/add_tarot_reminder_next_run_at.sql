-- Migration: tarot reminder scheduling column (next run timestamp)
-- Date: 2026-08-31
-- The service layer (services/tarot.py) and admin API already read/write
-- next_run_at; the column was missing from the model and existing databases.

ALTER TABLE tarot_reminder_settings
ADD COLUMN IF NOT EXISTS next_run_at TIMESTAMP;

COMMENT ON COLUMN tarot_reminder_settings.next_run_at IS 'Next scheduled reminder send time (user timezone resolved to UTC)';

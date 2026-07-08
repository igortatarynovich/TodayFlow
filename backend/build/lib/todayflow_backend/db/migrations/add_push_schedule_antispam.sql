-- Anti-spam and category toggles for user_push_schedules
-- Date: 2026-03-30

ALTER TABLE user_push_schedules ADD COLUMN IF NOT EXISTS quiet_start VARCHAR(5) NOT NULL DEFAULT '22:00';
ALTER TABLE user_push_schedules ADD COLUMN IF NOT EXISTS quiet_end VARCHAR(5) NOT NULL DEFAULT '08:00';
ALTER TABLE user_push_schedules ADD COLUMN IF NOT EXISTS max_auto_per_day INTEGER NOT NULL DEFAULT 5;

ALTER TABLE user_push_schedules ADD COLUMN IF NOT EXISTS notify_rhythm_today BOOLEAN NOT NULL DEFAULT TRUE;
ALTER TABLE user_push_schedules ADD COLUMN IF NOT EXISTS notify_goal_nudges BOOLEAN NOT NULL DEFAULT TRUE;
ALTER TABLE user_push_schedules ADD COLUMN IF NOT EXISTS notify_goal_ack BOOLEAN NOT NULL DEFAULT TRUE;

ALTER TABLE user_push_schedules ADD COLUMN IF NOT EXISTS notify_streak_care BOOLEAN NOT NULL DEFAULT TRUE;
ALTER TABLE user_push_schedules ADD COLUMN IF NOT EXISTS notify_weekly_focus BOOLEAN NOT NULL DEFAULT TRUE;
ALTER TABLE user_push_schedules ADD COLUMN IF NOT EXISTS notify_tarot_card BOOLEAN NOT NULL DEFAULT TRUE;
ALTER TABLE user_push_schedules ADD COLUMN IF NOT EXISTS notify_habit_reminders BOOLEAN NOT NULL DEFAULT TRUE;
ALTER TABLE user_push_schedules ADD COLUMN IF NOT EXISTS notify_comeback BOOLEAN NOT NULL DEFAULT TRUE;

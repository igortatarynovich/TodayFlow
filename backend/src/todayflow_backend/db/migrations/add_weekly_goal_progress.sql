ALTER TABLE weekly_goals ADD COLUMN progress_days INTEGER NOT NULL DEFAULT 0;
ALTER TABLE weekly_goals ADD COLUMN last_progress_date DATE NULL;


-- Daily goal step marks + phased state check-ins (morning/day/evening)
-- PostgreSQL

CREATE TABLE IF NOT EXISTS weekly_goal_steps (
    id SERIAL PRIMARY KEY,
    weekly_goal_id INTEGER NOT NULL REFERENCES weekly_goals(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    step_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_weekly_goal_step_date UNIQUE (weekly_goal_id, step_date)
);

CREATE INDEX IF NOT EXISTS idx_weekly_goal_steps_user_date ON weekly_goal_steps (user_id, step_date);

CREATE TABLE IF NOT EXISTS state_check_ins (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    checkin_date DATE NOT NULL,
    phase VARCHAR(16) NOT NULL,
    mood_scale INTEGER,
    energy_scale INTEGER,
    note TEXT,
    tags JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_state_checkin_user_date_phase UNIQUE (user_id, checkin_date, phase)
);

CREATE INDEX IF NOT EXISTS idx_state_checkins_user_date ON state_check_ins (user_id, checkin_date);

ALTER TABLE weekly_goals ADD COLUMN IF NOT EXISTS scope VARCHAR(16) DEFAULT 'week';
ALTER TABLE weekly_goals ADD COLUMN IF NOT EXISTS period_end DATE;

-- Перенос последней известной отметки в историю шагов (если была до введения таблицы)
INSERT INTO weekly_goal_steps (weekly_goal_id, user_id, step_date)
SELECT id, user_id, last_progress_date
FROM weekly_goals
WHERE last_progress_date IS NOT NULL
ON CONFLICT (weekly_goal_id, step_date) DO NOTHING;

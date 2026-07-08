-- Push devices, per-user local schedule, daily goal text for nudges, dispatch dedupe log
-- Date: 2026-03-29

CREATE TABLE IF NOT EXISTS push_devices (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    platform VARCHAR(32) NOT NULL,
    token TEXT NOT NULL,
    device_label VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_push_device_user_token UNIQUE (user_id, token)
);

CREATE INDEX IF NOT EXISTS idx_push_devices_user ON push_devices(user_id);

CREATE TABLE IF NOT EXISTS user_push_schedules (
    user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    timezone VARCHAR(64) NOT NULL DEFAULT 'Europe/Moscow',
    morning_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    morning_time VARCHAR(5) NOT NULL DEFAULT '08:30',
    day_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    day_time VARCHAR(5) NOT NULL DEFAULT '13:00',
    evening_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    evening_time VARCHAR(5) NOT NULL DEFAULT '20:00',
    goal_midday_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    goal_midday_time VARCHAR(5) NOT NULL DEFAULT '12:30',
    goal_afternoon_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    goal_afternoon_time VARCHAR(5) NOT NULL DEFAULT '16:00',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS daily_goal_snapshots (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    target_date DATE NOT NULL,
    goal_text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_daily_goal_user_date UNIQUE (user_id, target_date)
);

CREATE INDEX IF NOT EXISTS idx_daily_goal_user_date ON daily_goal_snapshots(user_id, target_date);

CREATE TABLE IF NOT EXISTS push_dispatch_log (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    dispatch_date DATE NOT NULL,
    kind VARCHAR(32) NOT NULL,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_push_dispatch_user_date_kind UNIQUE (user_id, dispatch_date, kind)
);

CREATE INDEX IF NOT EXISTS idx_push_dispatch_user_date ON push_dispatch_log(user_id, dispatch_date);

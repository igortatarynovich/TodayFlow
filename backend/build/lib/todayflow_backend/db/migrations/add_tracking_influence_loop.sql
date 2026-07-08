-- Migration: Add tracking and influence loop tables
-- Created: 2026-01-25
-- Description: Таблицы для контура влияния TodayFlow (трекер, дневник, ритуал, инсайты, недельная интеграция)

-- Прогресс-трекер: фиксация выполнения аскез и аффирмаций
CREATE TABLE IF NOT EXISTS progress_tracker_entries (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    asceticism_id VARCHAR(255),
    affirmation_id VARCHAR(255),
    completed BOOLEAN NOT NULL DEFAULT 0,
    state VARCHAR(50),
    state_scale INTEGER CHECK (state_scale >= 1 AND state_scale <= 5),
    note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, date, asceticism_id, affirmation_id)
);

CREATE INDEX IF NOT EXISTS idx_progress_tracker_user_id ON progress_tracker_entries(user_id);
CREATE INDEX IF NOT EXISTS idx_progress_tracker_date ON progress_tracker_entries(date DESC);
CREATE INDEX IF NOT EXISTS idx_progress_tracker_completed ON progress_tracker_entries(completed);
CREATE INDEX IF NOT EXISTS idx_progress_tracker_affirmation_id ON progress_tracker_entries(affirmation_id);

-- Дневник наблюдений: простое отражение без анализа
CREATE TABLE IF NOT EXISTS observation_diary_entries (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    noticed TEXT NOT NULL,
    hardest TEXT NOT NULL,
    easier_than_expected TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, date)
);

CREATE INDEX IF NOT EXISTS idx_observation_diary_user_id ON observation_diary_entries(user_id);
CREATE INDEX IF NOT EXISTS idx_observation_diary_date ON observation_diary_entries(date DESC);

-- Ритуал закрытия дня: 1 экран, 10 секунд
CREATE TABLE IF NOT EXISTS day_rituals (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    completed BOOLEAN NOT NULL DEFAULT 0,
    closing_phrase_id VARCHAR(255),
    closing_phrase_text TEXT,
    sufficiency_confirmed BOOLEAN NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, date)
);

CREATE INDEX IF NOT EXISTS idx_day_rituals_user_id ON day_rituals(user_id);
CREATE INDEX IF NOT EXISTS idx_day_rituals_date ON day_rituals(date DESC);
CREATE INDEX IF NOT EXISTS idx_day_rituals_completed ON day_rituals(completed);

-- Автоматические инсайты: система говорит пользователю, что происходит
CREATE TABLE IF NOT EXISTS auto_insights (
    id VARCHAR(255) PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    type VARCHAR(50) NOT NULL CHECK (type IN ('streak', 'pattern', 'shift')),
    insight_text TEXT NOT NULL,
    data_points JSONB NOT NULL, -- JSON data
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_auto_insights_user_id ON auto_insights(user_id);
CREATE INDEX IF NOT EXISTS idx_auto_insights_date ON auto_insights(date DESC);
CREATE INDEX IF NOT EXISTS idx_auto_insights_type ON auto_insights(type);

-- Недельная интеграция: раз в 7 дней, один абзац
CREATE TABLE IF NOT EXISTS weekly_integrations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    week_start DATE NOT NULL,
    week_end DATE NOT NULL,
    integration_text TEXT NOT NULL,
    data_points JSONB NOT NULL, -- JSON data
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, week_start, week_end)
);

CREATE INDEX IF NOT EXISTS idx_weekly_integrations_user_id ON weekly_integrations(user_id);
CREATE INDEX IF NOT EXISTS idx_weekly_integrations_week_start ON weekly_integrations(week_start DESC);
CREATE INDEX IF NOT EXISTS idx_weekly_integrations_week_end ON weekly_integrations(week_end DESC);

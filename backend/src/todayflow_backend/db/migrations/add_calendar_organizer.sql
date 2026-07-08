-- Миграция: Календарь-органайзер (события, записи, трекинг менструального цикла)

-- Календарные события
CREATE TABLE IF NOT EXISTS calendar_events (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    date DATE NOT NULL,
    time TIME,
    is_all_day BOOLEAN DEFAULT FALSE,
    color VARCHAR(7),
    category VARCHAR(50),
    description TEXT,
    repeat_type VARCHAR(20),
    reminder_minutes INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_calendar_events_user_date ON calendar_events(user_id, date);
CREATE INDEX IF NOT EXISTS idx_calendar_events_user_id ON calendar_events(user_id);

-- Записи к дню или событию
CREATE TABLE IF NOT EXISTS calendar_notes (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    event_id INTEGER REFERENCES calendar_events(id) ON DELETE SET NULL,
    note_text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, date)
);

CREATE INDEX IF NOT EXISTS idx_calendar_notes_user_date ON calendar_notes(user_id, date);
CREATE INDEX IF NOT EXISTS idx_calendar_notes_event_id ON calendar_notes(event_id);

-- Трекинг менструального цикла (опционально)
CREATE TABLE IF NOT EXISTS menstrual_cycles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    cycle_day INTEGER,
    period_intensity VARCHAR(20),
    ovulation BOOLEAN DEFAULT FALSE,
    fertile_window BOOLEAN DEFAULT FALSE,
    symptoms JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, date)
);

CREATE INDEX IF NOT EXISTS idx_menstrual_cycles_user_date ON menstrual_cycles(user_id, date);
CREATE INDEX IF NOT EXISTS idx_menstrual_cycles_user_id ON menstrual_cycles(user_id);

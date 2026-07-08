-- Миграция: добавление таблицы day_connections для связки дня

CREATE TABLE IF NOT EXISTS day_connections (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    
    -- Утреннее намерение
    morning_intention TEXT,
    morning_focus VARCHAR(100),
    
    -- Вечернее отражение
    evening_reflection TEXT,
    evening_observations JSONB,
    
    -- Связующая нить
    connection_thread TEXT,
    
    -- Статус
    morning_completed BOOLEAN DEFAULT FALSE,
    day_completed BOOLEAN DEFAULT FALSE,
    evening_completed BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(user_id, date)
);

-- Индексы для быстрого поиска
CREATE INDEX IF NOT EXISTS idx_day_connections_user_date ON day_connections(user_id, date);
CREATE INDEX IF NOT EXISTS idx_day_connections_date ON day_connections(date);

-- Обновление таблицы day_rituals для кастомизации
ALTER TABLE day_rituals 
ADD COLUMN IF NOT EXISTS ritual_type VARCHAR(50) DEFAULT 'template',
ADD COLUMN IF NOT EXISTS custom_elements JSONB,
ADD COLUMN IF NOT EXISTS custom_closing_phrase TEXT,
ADD COLUMN IF NOT EXISTS day_connection_id INTEGER REFERENCES day_connections(id) ON DELETE SET NULL;

CREATE INDEX IF NOT EXISTS idx_day_rituals_day_connection ON day_rituals(day_connection_id);

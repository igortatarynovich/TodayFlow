-- Миграция: кеширование натальной карты и прогнозов
-- Создаёт таблицы для хранения вычисленных натальных карт и сгенерированных прогнозов

-- Таблица для кеширования натальной карты
CREATE TABLE IF NOT EXISTS cached_natal_charts (
    id SERIAL PRIMARY KEY,
    astro_profile_id INTEGER NOT NULL REFERENCES astro_profiles(id) ON DELETE CASCADE,
    positions JSONB NOT NULL,  -- Позиции планет
    houses JSONB NOT NULL,      -- Дома (включая асцендент, MC и т.д.)
    chart_metadata JSONB,       -- Метаданные (система домов, система координат и т.д.) - переименовано из metadata, т.к. metadata зарезервировано в SQLAlchemy
    computed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(astro_profile_id)
);

CREATE INDEX idx_cached_natal_charts_astro_profile ON cached_natal_charts(astro_profile_id);

-- Таблица для кеширования прогнозов
CREATE TABLE IF NOT EXISTS cached_forecasts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    astro_profile_id INTEGER NOT NULL REFERENCES astro_profiles(id) ON DELETE CASCADE,
    forecast_type VARCHAR(50) NOT NULL,  -- 'daily', 'weekly', 'monthly', 'yearly'
    forecast_date DATE NOT NULL,        -- Дата прогноза (для daily) или начальная дата (для weekly/monthly)
    locale VARCHAR(10) NOT NULL DEFAULT 'ru',
    use_ai BOOLEAN DEFAULT FALSE,        -- Был ли использован ИИ
    forecast_data JSONB NOT NULL,        -- Полные данные прогноза
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, astro_profile_id, forecast_type, forecast_date, locale, use_ai)
);

CREATE INDEX idx_cached_forecasts_user_date ON cached_forecasts(user_id, forecast_type, forecast_date);
CREATE INDEX idx_cached_forecasts_astro_profile ON cached_forecasts(astro_profile_id);

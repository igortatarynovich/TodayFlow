#!/bin/bash
# Скрипт для применения миграции контура влияния через psql (PostgreSQL)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MIGRATION_FILE="$SCRIPT_DIR/../src/todayflow_backend/db/migrations/add_tracking_influence_loop.sql"

if [ ! -f "$MIGRATION_FILE" ]; then
    echo "❌ Файл миграции не найден: $MIGRATION_FILE"
    exit 1
fi

# Получаем DATABASE_URL из .env или переменной окружения
if [ -f "$SCRIPT_DIR/../.env" ]; then
    source "$SCRIPT_DIR/../.env"
fi

if [ -z "$DATABASE_URL" ]; then
    echo "❌ DATABASE_URL не установлен. Установите переменную окружения или добавьте в .env"
    exit 1
fi

echo "🚀 Применение миграции контура влияния..."
echo "📄 Файл: $MIGRATION_FILE"
echo "🔗 БД: ${DATABASE_URL%%@*}"
echo ""

# Для PostgreSQL извлекаем параметры подключения
if [[ "$DATABASE_URL" == postgresql* ]]; then
    # Парсим DATABASE_URL: postgresql://user:password@host:port/dbname
    DB_URL_WITHOUT_SCHEME="${DATABASE_URL#postgresql://}"
    DB_CREDENTIALS="${DB_URL_WITHOUT_SCHEME%%@*}"
    DB_HOST_PORT_DB="${DB_URL_WITHOUT_SCHEME#*@}"
    DB_HOST_PORT="${DB_HOST_PORT_DB%%/*}"
    DB_NAME="${DB_HOST_PORT_DB#*/}"
    DB_NAME="${DB_NAME%%\?*}"  # Убираем query параметры
    
    DB_USER="${DB_CREDENTIALS%%:*}"
    DB_PASS="${DB_CREDENTIALS#*:}"
    DB_HOST="${DB_HOST_PORT%%:*}"
    DB_PORT="${DB_HOST_PORT#*:}"
    DB_PORT="${DB_PORT:-5432}"
    
    echo "📊 Параметры подключения:"
    echo "   Host: $DB_HOST"
    echo "   Port: $DB_PORT"
    echo "   Database: $DB_NAME"
    echo "   User: $DB_USER"
    echo ""
    
    # Применяем миграцию через psql
    export PGPASSWORD="$DB_PASS"
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f "$MIGRATION_FILE"
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ Миграция успешно применена!"
    else
        echo ""
        echo "❌ Ошибка при применении миграции"
        exit 1
    fi
else
    echo "⚠️  DATABASE_URL не является PostgreSQL. Используйте Python скрипт:"
    echo "   python scripts/apply_tracking_migration.py"
    exit 1
fi

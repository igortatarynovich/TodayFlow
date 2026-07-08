#!/usr/bin/env python3
"""Скрипт для применения миграции контура влияния к базе данных."""

import sys
from pathlib import Path
from sqlalchemy import text
from sqlalchemy.engine import Engine

# Добавляем путь к модулям проекта
sys.path.insert(0, str(Path(__file__).parent.parent))

from todayflow_backend.db.session import engine
from todayflow_backend.core.config import settings


def apply_migration():
    """Применяет миграцию add_tracking_influence_loop.sql к базе данных."""
    migration_file = Path(__file__).parent.parent / "src" / "todayflow_backend" / "db" / "migrations" / "add_tracking_influence_loop.sql"
    
    if not migration_file.exists():
        print(f"❌ Файл миграции не найден: {migration_file}")
        return False
    
    print(f"📄 Читаю миграцию из: {migration_file}")
    
    with open(migration_file, 'r', encoding='utf-8') as f:
        migration_sql = f.read()
    
    db_url_display = settings.database_url.split('@')[-1] if '@' in settings.database_url else settings.database_url
    # Скрываем пароль для безопасности
    if '://' in db_url_display:
        db_url_display = db_url_display.split('://')[-1]
    print(f"🔗 Подключаюсь к БД: {db_url_display}")
    
    try:
        # Проверяем подключение
        with engine.connect() as connection:
            print("✅ Подключение к БД установлено")
        
        # Применяем миграцию
        with engine.connect() as connection:
            # Для PostgreSQL нужно использовать транзакцию
            if 'postgresql' in settings.database_url or 'postgres' in settings.database_url:
                with connection.begin():
                    # Разделяем SQL на отдельные команды
                    statements = [s.strip() for s in migration_sql.split(';') if s.strip() and not s.strip().startswith('--')]
                    
                    for i, statement in enumerate(statements, 1):
                        if statement:
                            print(f"  ⏳ Выполняю команду {i}/{len(statements)}...")
                            connection.execute(text(statement))
                    
                    print("✅ Миграция успешно применена!")
                    return True
            elif 'sqlite' in settings.database_url:
                # Для SQLite - нужно адаптировать синтаксис
                print("⚠️  SQLite обнаружен. Адаптирую синтаксис миграции...")
                
                # Заменяем PostgreSQL-специфичные конструкции на SQLite
                sqlite_sql = migration_sql.replace('SERIAL PRIMARY KEY', 'INTEGER PRIMARY KEY AUTOINCREMENT')
                sqlite_sql = sqlite_sql.replace('JSONB', 'TEXT')  # JSONB → TEXT для SQLite
                sqlite_sql = sqlite_sql.replace('BOOLEAN NOT NULL DEFAULT 0', 'INTEGER NOT NULL DEFAULT 0')
                sqlite_sql = sqlite_sql.replace('BOOLEAN NOT NULL DEFAULT FALSE', 'INTEGER NOT NULL DEFAULT 0')
                sqlite_sql = sqlite_sql.replace('BOOLEAN DEFAULT FALSE', 'INTEGER DEFAULT 0')
                
                statements = [s.strip() for s in sqlite_sql.split(';') if s.strip() and not s.strip().startswith('--')]
                
                for i, statement in enumerate(statements, 1):
                    if statement:
                        print(f"  ⏳ Выполняю команду {i}/{len(statements)}...")
                        try:
                            connection.execute(text(statement))
                        except Exception as e:
                            # Игнорируем ошибки "table already exists"
                            if 'already exists' not in str(e).lower():
                                raise
                            print(f"    ℹ️  Таблица уже существует, пропускаю...")
                
                connection.commit()
                print("✅ Миграция успешно применена!")
                return True
            else:
                print(f"⚠️  Неизвестный тип БД: {settings.database_url}")
                print("Попробую применить миграцию как для PostgreSQL...")
                # Пробуем применить как PostgreSQL
                with connection.begin():
                    statements = [s.strip() for s in migration_sql.split(';') if s.strip() and not s.strip().startswith('--')]
                    
                    for i, statement in enumerate(statements, 1):
                        if statement:
                            print(f"  ⏳ Выполняю команду {i}/{len(statements)}...")
                            try:
                                connection.execute(text(statement))
                            except Exception as e:
                                if 'already exists' not in str(e).lower():
                                    raise
                                print(f"    ℹ️  Таблица уже существует, пропускаю...")
                    
                    print("✅ Миграция успешно применена!")
                    return True
                
    except Exception as e:
        print(f"❌ Ошибка при применении миграции: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🚀 Применение миграции контура влияния...")
    print("=" * 60)
    
    success = apply_migration()
    
    print("=" * 60)
    if success:
        print("✅ Миграция применена успешно!")
        sys.exit(0)
    else:
        print("❌ Ошибка при применении миграции")
        sys.exit(1)

#!/usr/bin/env python3
"""Скрипт для применения миграции контура влияния к SQLite базе данных."""

import sys
from pathlib import Path
import sqlite3

# Добавляем путь к модулям проекта
sys.path.insert(0, str(Path(__file__).parent.parent))

from todayflow_backend.core.config import settings


def apply_migration_sqlite():
    """Применяет миграцию add_tracking_influence_loop.sql к SQLite базе данных."""
    migration_file = Path(__file__).parent.parent / "src" / "todayflow_backend" / "db" / "migrations" / "add_tracking_influence_loop.sql"
    
    if not migration_file.exists():
        print(f"❌ Файл миграции не найден: {migration_file}")
        return False
    
    # Определяем путь к SQLite БД
    if 'sqlite' in settings.database_url:
        # Извлекаем путь из DATABASE_URL: sqlite:///path/to/db.db
        db_path = settings.database_url.replace('sqlite:///', '')
    else:
        # Пробуем найти dev.db в директории backend
        db_path = Path(__file__).parent.parent / "dev.db"
        if not db_path.exists():
            print(f"❌ SQLite база данных не найдена. Укажите DATABASE_URL или создайте dev.db")
            return False
    
    print(f"📄 Читаю миграцию из: {migration_file}")
    print(f"💾 База данных: {db_path}")
    
    with open(migration_file, 'r', encoding='utf-8') as f:
        migration_sql = f.read()
    
    # Адаптируем SQL для SQLite
    sqlite_sql = migration_sql.replace('SERIAL PRIMARY KEY', 'INTEGER PRIMARY KEY AUTOINCREMENT')
    sqlite_sql = sqlite_sql.replace('JSONB', 'TEXT')  # JSONB → TEXT для SQLite
    sqlite_sql = sqlite_sql.replace('BOOLEAN NOT NULL DEFAULT 0', 'INTEGER NOT NULL DEFAULT 0')
    sqlite_sql = sqlite_sql.replace('BOOLEAN NOT NULL DEFAULT FALSE', 'INTEGER NOT NULL DEFAULT 0')
    sqlite_sql = sqlite_sql.replace('BOOLEAN DEFAULT FALSE', 'INTEGER DEFAULT 0')
    sqlite_sql = sqlite_sql.replace('BOOLEAN DEFAULT TRUE', 'INTEGER DEFAULT 1')
    sqlite_sql = sqlite_sql.replace('TIMESTAMP DEFAULT CURRENT_TIMESTAMP', 'DATETIME DEFAULT CURRENT_TIMESTAMP')
    # SQLite не поддерживает DESC в CREATE INDEX, убираем
    sqlite_sql = sqlite_sql.replace('(date DESC)', '(date)')
    sqlite_sql = sqlite_sql.replace('(week_start DESC)', '(week_start)')
    sqlite_sql = sqlite_sql.replace('(week_end DESC)', '(week_end)')
    sqlite_sql = sqlite_sql.replace('(created_at DESC)', '(created_at)')
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Разделяем SQL на отдельные команды более аккуратно
        # Используем регулярное выражение для правильного разделения
        import re
        
        # Убираем комментарии
        sqlite_sql = re.sub(r'--.*$', '', sqlite_sql, flags=re.MULTILINE)
        
        # Разделяем по точкам с запятой, но учитываем, что они могут быть внутри строк
        statements = []
        current_statement = []
        in_string = False
        string_char = None
        
        for char in sqlite_sql:
            if char in ("'", '"') and (not current_statement or current_statement[-1] != '\\'):
                if not in_string:
                    in_string = True
                    string_char = char
                elif char == string_char:
                    in_string = False
                    string_char = None
            
            current_statement.append(char)
            
            if not in_string and char == ';':
                stmt = ''.join(current_statement).strip()
                if stmt:
                    statements.append(stmt)
                current_statement = []
        
        # Добавляем последнюю команду, если она есть
        if current_statement:
            stmt = ''.join(current_statement).strip()
            if stmt:
                statements.append(stmt)
        
        for i, statement in enumerate(statements, 1):
            if statement:
                print(f"  ⏳ Выполняю команду {i}/{len(statements)}...")
                try:
                    cursor.execute(statement)
                except sqlite3.OperationalError as e:
                    error_msg = str(e).lower()
                    # Игнорируем ошибки "table already exists" и "index already exists"
                    if 'already exists' in error_msg or 'duplicate' in error_msg:
                        print(f"    ℹ️  Уже существует, пропускаю...")
                    elif 'incomplete input' in error_msg:
                        print(f"    ⚠️  Неполная команда, пропускаю...")
                    else:
                        print(f"    ⚠️  Ошибка: {e}")
                        # Для индексов это может быть нормально, если таблица еще не создана
                        if 'no such table' in error_msg and 'index' in statement.lower():
                            print(f"    ℹ️  Пропускаю индекс (таблица будет создана позже)...")
                        else:
                            raise
        
        conn.commit()
        conn.close()
        
        print("✅ Миграция успешно применена!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при применении миграции: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🚀 Применение миграции контура влияния (SQLite)...")
    print("=" * 60)
    
    success = apply_migration_sqlite()
    
    print("=" * 60)
    if success:
        print("✅ Миграция применена успешно!")
        sys.exit(0)
    else:
        print("❌ Ошибка при применении миграции")
        sys.exit(1)

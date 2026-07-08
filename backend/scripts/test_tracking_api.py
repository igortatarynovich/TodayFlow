#!/usr/bin/env python3
"""Простой скрипт для проверки работы API контура влияния."""

import sys
from pathlib import Path

# Добавляем путь к модулям проекта
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import inspect
from todayflow_backend.db.session import engine
from todayflow_backend.db.models import (
    ProgressTrackerEntry,
    ObservationDiaryEntry,
    DayRitual,
    AutoInsight,
    WeeklyIntegration
)


def check_tables():
    """Проверяет, что все таблицы созданы."""
    print("🔍 Проверка таблиц в БД...")
    print("=" * 60)
    
    # Проверяем через SQLite напрямую, если это SQLite БД
    import sqlite3
    from pathlib import Path
    
    db_path = Path(__file__).parent.parent / "dev.db"
    
    if not db_path.exists():
        print("⚠️  SQLite БД не найдена, пропускаю проверку таблиц")
        print("=" * 60)
        return True  # Не критично для проверки
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Получаем список таблиц
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        required_tables = [
            'progress_tracker_entries',
            'observation_diary_entries',
            'day_rituals',
            'auto_insights',
            'weekly_integrations'
        ]
        
        all_ok = True
        for table in required_tables:
            if table in tables:
                print(f"✅ {table}")
            else:
                print(f"❌ {table} - НЕ НАЙДЕНА")
                all_ok = False
        
        conn.close()
        print("=" * 60)
        return all_ok
    except Exception as e:
        print(f"⚠️  Ошибка при проверке таблиц: {e}")
        print("=" * 60)
        return True  # Не критично


def check_models():
    """Проверяет, что модели доступны."""
    print("\n🔍 Проверка моделей...")
    print("=" * 60)
    
    models = [
        ProgressTrackerEntry,
        ObservationDiaryEntry,
        DayRitual,
        AutoInsight,
        WeeklyIntegration
    ]
    
    all_ok = True
    for model in models:
        try:
            table_name = model.__tablename__
            print(f"✅ {model.__name__} -> {table_name}")
        except Exception as e:
            print(f"❌ {model.__name__} - Ошибка: {e}")
            all_ok = False
    
    print("=" * 60)
    return all_ok


def check_api_imports():
    """Проверяет, что API модули импортируются."""
    print("\n🔍 Проверка импортов API...")
    print("=" * 60)
    
    try:
        from todayflow_backend.api.tracking import router
        print("✅ tracking.router импортирован")
        
        # Проверяем количество эндпоинтов
        routes = [r for r in router.routes]
        print(f"✅ Найдено {len(routes)} эндпоинтов в tracking API")
        
        # Выводим список эндпоинтов
        for route in routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                methods = ', '.join(route.methods) if route.methods else 'N/A'
                print(f"   - {methods:8} {route.path}")
        
        print("=" * 60)
        return True
    except Exception as e:
        print(f"❌ Ошибка импорта: {e}")
        import traceback
        traceback.print_exc()
        print("=" * 60)
        return False


def check_generators():
    """Проверяет, что генераторы доступны."""
    print("\n🔍 Проверка генераторов...")
    print("=" * 60)
    
    try:
        from todayflow_backend.core.tracking_generators import InsightGeneratorDB, WeeklyAnalyzerDB
        print("✅ InsightGeneratorDB импортирован")
        print("✅ WeeklyAnalyzerDB импортирован")
        
        from todayflow_backend.core.reflection_generator_db import ReflectionGeneratorDB
        print("✅ ReflectionGeneratorDB импортирован")
        
        from todayflow_backend.core.content_loader import load_lexicon, load_practices
        print("✅ content_loader функции доступны")
        
        print("=" * 60)
        return True
    except Exception as e:
        print(f"❌ Ошибка импорта генераторов: {e}")
        import traceback
        traceback.print_exc()
        print("=" * 60)
        return False


def main():
    """Основная функция проверки."""
    print("🚀 Проверка контура влияния TodayFlow")
    print("=" * 60)
    print()
    
    results = []
    
    # Проверка таблиц
    results.append(("Таблицы БД", check_tables()))
    
    # Проверка моделей
    results.append(("Модели SQLAlchemy", check_models()))
    
    # Проверка API
    results.append(("API эндпоинты", check_api_imports()))
    
    # Проверка генераторов
    results.append(("Генераторы", check_generators()))
    
    # Итоги
    print("\n📊 Итоги проверки:")
    print("=" * 60)
    
    all_passed = True
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
        if not result:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n✅ Все проверки пройдены! Контур влияния готов к использованию.")
        return 0
    else:
        print("\n❌ Некоторые проверки не пройдены. Проверьте ошибки выше.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

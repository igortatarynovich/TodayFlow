#!/usr/bin/env python3
"""
Создание структуры Daily-слоя в en.json

Создает placeholder ключи для всех слотов Daily-слоя.
Используется для начальной структуризации перед заполнением контентом.
"""

import json
from pathlib import Path

CONTENT_DIR = Path(__file__).parent.parent / "CONTENT" / "i18n"
EN_JSON = CONTENT_DIR / "en.json"

# Количественные цели (урезанный старт)
DAILY_STRUCTURE = {
    "DIGEST": 20,
    "FOCUS": 20,
    "WARNING": 20,
    "WIN": 20,
    "AFFIRMATION": 60,
    "PROMPT": 60,
    "PATTERN_TODAY": 30,
}

# Практики (intro + steps)
PRACTICES = {
    "BREATHING": {"intro": 15, "steps": 15},
    "MEDITATION": {"intro": 15, "steps": 15},
    "JOURNALING": {"intro": 10, "steps": 10},
    "MOVEMENT": {"intro": 10, "steps": 10},
}

PLACEHOLDER_TEXT = "[TODO: Add content]"

def create_daily_keys():
    """Создает структуру ключей Daily-слоя"""
    keys = {}
    
    # Базовые слоты
    for slot, count in DAILY_STRUCTURE.items():
        for i in range(1, count + 1):
            key = f"DAILY.{slot}.{i:03d}"
            keys[key] = PLACEHOLDER_TEXT
    
    # Практики
    for practice_type, counts in PRACTICES.items():
        for step_type, count in counts.items():
            for i in range(1, count + 1):
                key = f"DAILY.PRACTICE.{practice_type}.{step_type.upper()}.{i:03d}"
                keys[key] = PLACEHOLDER_TEXT
    
    return keys

def main():
    import sys
    
    dry_run = '--apply' not in sys.argv
    
    # Загружаем текущий en.json
    if not EN_JSON.exists():
        print(f"❌ Файл не найден: {EN_JSON}")
        return
    
    with open(EN_JSON, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Проверяем, есть ли уже Daily ключи
    existing_daily = [k for k in data.keys() if k.startswith("DAILY.")]
    if existing_daily:
        print(f"⚠️  Найдено {len(existing_daily)} существующих Daily ключей")
        print("Примеры:")
        for key in existing_daily[:5]:
            print(f"  {key}")
        if not dry_run:
            response = input("\nПродолжить и добавить новые ключи? (y/n): ")
            if response.lower() != 'y':
                return
    
    # Создаем новые ключи
    new_keys = create_daily_keys()
    
    # Проверяем конфликты
    conflicts = [k for k in new_keys.keys() if k in data]
    if conflicts:
        print(f"⚠️  Найдено {len(conflicts)} конфликтов (ключи уже существуют)")
        if not dry_run:
            response = input("Перезаписать существующие? (y/n): ")
            if response.lower() != 'y':
                return
    
    print(f"\n{'=' * 80}")
    print("Создание структуры Daily-слоя")
    print(f"{'=' * 80}")
    print(f"Новых ключей: {len(new_keys)}")
    print(f"Текущих ключей в файле: {len(data)}")
    print(f"Будет после добавления: {len(data) + len(new_keys) - len(conflicts)}")
    print()
    
    print("Структура:")
    for slot, count in DAILY_STRUCTURE.items():
        print(f"  DAILY.{slot}.*: {count} ключей")
    
    print("\nПрактики:")
    for practice_type, counts in PRACTICES.items():
        total = sum(counts.values())
        print(f"  DAILY.PRACTICE.{practice_type}.*: {total} ключей ({counts})")
    
    total_new = sum(DAILY_STRUCTURE.values()) + sum(
        sum(counts.values()) for counts in PRACTICES.values()
    )
    print(f"\nВсего новых ключей: {total_new}")
    
    if dry_run:
        print("\n🔍 DRY RUN - изменения не будут сохранены")
        print("Запустите с --apply для применения")
        return
    
    # Добавляем ключи
    data.update(new_keys)
    
    # Сохраняем
    with open(EN_JSON, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Структура создана: добавлено {len(new_keys)} ключей")
    print(f"📄 Файл: {EN_JSON}")

if __name__ == "__main__":
    main()


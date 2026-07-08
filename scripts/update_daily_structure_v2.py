#!/usr/bin/env python3
"""
Обновление структуры Daily-слоя до финальной модели v2 (990 ключей)

Заменяет существующую структуру (330 ключей) на финальную (990 ключей).
"""

import json
from pathlib import Path

CONTENT_DIR = Path(__file__).parent.parent / "CONTENT" / "i18n"
EN_JSON = CONTENT_DIR / "en.json"

# Финальная структура v2
DAILY_STRUCTURE_V2 = {
    "DIGEST": 80,
    "FOCUS": 80,
    "WARNING": 60,
    "WIN": 60,
    "AFFIRMATION": 150,
    "PROMPT": 150,
}

# PATTERN_TODAY (4 слоя × 50 ключей)
PATTERN_LAYERS = {
    "INSIGHT": 50,
    "ACTION": 50,
    "RISK": 50,
    "REFRAME": 50,
}

# Практики (8 типов × intro/steps/outcome)
PRACTICE_TYPES = [
    "BREATHING",
    "MEDITATION",
    "JOURNALING",
    "MOVEMENT",
    "BODY_SCAN",
    "MINDFULNESS",
    "REFLECTION",
    "GROUNDING",
]

PRACTICE_STRUCTURE = {
    "INTRO": 15,
    "STEPS": 4,
    "OUTCOME": 7,
}

PLACEHOLDER_TEXT = "[TODO: Add content]"

def create_daily_keys_v2():
    """Создает структуру ключей Daily-слоя v2 (990 ключей)"""
    keys = {}
    
    # Базовые слоты
    for slot, count in DAILY_STRUCTURE_V2.items():
        for i in range(1, count + 1):
            key = f"DAILY.{slot}.{i:03d}"
            keys[key] = PLACEHOLDER_TEXT
    
    # PATTERN_TODAY (4 слоя)
    for layer, count in PATTERN_LAYERS.items():
        for i in range(1, count + 1):
            key = f"DAILY.PATTERN_TODAY.{layer}.{i:03d}"
            keys[key] = PLACEHOLDER_TEXT
    
    # Практики (8 типов × 3 части)
    for practice_type in PRACTICE_TYPES:
        for part, count in PRACTICE_STRUCTURE.items():
            for i in range(1, count + 1):
                key = f"DAILY.PRACTICE.{practice_type}.{part}.{i:03d}"
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
    
    # Находим существующие Daily ключи
    existing_daily = {k: v for k, v in data.items() if k.startswith("DAILY.")}
    
    # Создаем новые ключи
    new_keys = create_daily_keys_v2()
    
    print(f"\n{'=' * 80}")
    print("Обновление Daily-слоя до v2 (финальная модель)")
    print(f"{'=' * 80}")
    print(f"Существующих Daily ключей: {len(existing_daily)}")
    print(f"Новых ключей (v2): {len(new_keys)}")
    print()
    
    print("Структура v2:")
    for slot, count in DAILY_STRUCTURE_V2.items():
        print(f"  DAILY.{slot}.*: {count} ключей")
    
    print(f"\n  DAILY.PATTERN_TODAY.*: 200 ключей (4 слоя × 50)")
    for layer, count in PATTERN_LAYERS.items():
        print(f"    - {layer}: {count} ключей")
    
    print(f"\n  DAILY.PRACTICE.*: ~210 ключей")
    print(f"    - Типов практик: {len(PRACTICE_TYPES)}")
    for part, count in PRACTICE_STRUCTURE.items():
        total = len(PRACTICE_TYPES) * count
        print(f"    - {part}: {total} ключей ({len(PRACTICE_TYPES)} × {count})")
    
    total_new = (
        sum(DAILY_STRUCTURE_V2.values()) +
        sum(PATTERN_LAYERS.values()) +
        len(PRACTICE_TYPES) * sum(PRACTICE_STRUCTURE.values())
    )
    print(f"\nВсего новых ключей: {total_new}")
    
    if dry_run:
        print("\n🔍 DRY RUN - изменения не будут сохранены")
        print("Запустите с --apply для применения")
        return
    
    # Удаляем старые Daily ключи
    for key in list(data.keys()):
        if key.startswith("DAILY."):
            del data[key]
    
    print(f"\n✅ Удалено старых Daily ключей: {len(existing_daily)}")
    
    # Добавляем новые ключи
    data.update(new_keys)
    
    # Сохраняем
    with open(EN_JSON, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Структура обновлена: добавлено {len(new_keys)} ключей")
    print(f"📄 Файл: {EN_JSON}")
    print(f"\n📊 Итоговая статистика:")
    print(f"   Всего ключей в en.json: {len(data)}")
    print(f"   Daily-слой (v2): {len(new_keys)} ключей")

if __name__ == "__main__":
    main()


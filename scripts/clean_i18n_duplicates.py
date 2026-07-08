#!/usr/bin/env python3
"""
Очистка дубликатов в en.json

Удаляет варианты .v1/.v2/.v3, которые имеют идентичный текст.
Оставляет один вариант (без .v*) для каждого уникального текста.

Создает резервную копию перед изменениями.
"""

import json
import re
import shutil
from collections import defaultdict
from datetime import datetime
from pathlib import Path

CONTENT_DIR = Path(__file__).parent.parent / "CONTENT" / "i18n"
EN_JSON = CONTENT_DIR / "en.json"
RU_JSON = CONTENT_DIR / "ru.json"

def normalize_text(text):
    """Нормализует текст для сравнения"""
    return ' '.join(text.strip().split())

def find_duplicates(data):
    """
    Находит дубликаты в вариантах .v1/.v2/.v3
    
    Возвращает:
    - keys_to_remove: список ключей для удаления
    - keys_to_rename: {old_key: new_key} - ключи, которые нужно переименовать (убрать .v*)
    """
    base_groups = defaultdict(list)
    
    # Группируем по базовому ключу
    for key in data.keys():
        base_key = re.sub(r'\.v[123]$', '', key)
        base_groups[base_key].append(key)
    
    keys_to_remove = []
    keys_to_rename = {}
    
    for base_key, variants in base_groups.items():
        if len(variants) <= 1:
            continue  # Нет вариантов для проверки
        
        # Группируем варианты по тексту
        text_groups = defaultdict(list)
        for variant in variants:
            text = normalize_text(data[variant])
            text_groups[text].append(variant)
        
        # Для каждого уникального текста оставляем один вариант
        for text, variant_list in text_groups.items():
            if len(variant_list) > 1:
                # Сортируем, чтобы предпочесть .v1, потом .v2, потом .v3
                variant_list.sort()
                keep_variant = variant_list[0]
                
                # Если keep_variant имеет .v*, переименовываем в базовый ключ
                if re.search(r'\.v[123]$', keep_variant):
                    keys_to_rename[keep_variant] = base_key
                
                # Остальные варианты помечаем на удаление
                for variant in variant_list[1:]:
                    keys_to_remove.append(variant)
    
    return keys_to_remove, keys_to_rename

def create_backup(file_path):
    """Создает резервную копию файла"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = file_path.parent / f"{file_path.stem}_backup_{timestamp}.json"
    shutil.copy2(file_path, backup_path)
    return backup_path

def clean_duplicates(file_path, dry_run=True):
    """
    Очищает дубликаты в JSON файле
    
    Args:
        file_path: путь к файлу
        dry_run: если True, только показывает изменения без сохранения
    """
    # Загружаем данные
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    original_count = len(data)
    
    # Находим дубликаты
    keys_to_remove, keys_to_rename = find_duplicates(data)
    
    if not keys_to_remove and not keys_to_rename:
        print(f"✅ В файле {file_path.name} дубликатов не найдено")
        return
    
    print(f"\n{'=' * 80}")
    print(f"Обработка: {file_path.name}")
    print(f"{'=' * 80}")
    print(f"Всего ключей: {original_count}")
    print(f"Ключей для удаления: {len(keys_to_remove)}")
    print(f"Ключей для переименования: {len(keys_to_rename)}")
    print(f"Останется ключей: {original_count - len(keys_to_remove)}")
    print()
    
    if dry_run:
        print("🔍 DRY RUN - изменения не будут сохранены")
        print("\nПримеры удаляемых ключей (первые 10):")
        for key in keys_to_remove[:10]:
            print(f"  - {key}")
            print(f"    Текст: {data[key][:80]}...")
        
        if len(keys_to_remove) > 10:
            print(f"  ... и ещё {len(keys_to_remove) - 10}")
        
        print("\nПримеры переименований (первые 10):")
        for old_key, new_key in list(keys_to_rename.items())[:10]:
            print(f"  {old_key} → {new_key}")
        
        if len(keys_to_rename) > 10:
            print(f"  ... и ещё {len(keys_to_rename) - 10}")
        
        return
    
    # Создаем резервную копию
    backup_path = create_backup(file_path)
    print(f"📦 Резервная копия создана: {backup_path.name}")
    
    # Применяем изменения
    cleaned_data = {}
    
    # Сначала переименовываем
    renamed_values = {}
    for old_key, new_key in keys_to_rename.items():
        renamed_values[new_key] = data[old_key]
    
    # Собираем финальные данные
    for key, value in data.items():
        if key in keys_to_remove:
            continue  # Пропускаем удаляемые ключи
        
        if key in keys_to_rename:
            # Этот ключ будет переименован, пропускаем
            continue
        
        if key in renamed_values:
            # Этот ключ уже добавлен через переименование, пропускаем
            continue
        
        cleaned_data[key] = value
    
    # Добавляем переименованные ключи
    for new_key, value in renamed_values.items():
        cleaned_data[new_key] = value
    
    # Сохраняем
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(cleaned_data, f, indent=2, ensure_ascii=False)
    
    final_count = len(cleaned_data)
    print(f"✅ Файл очищен: {original_count} → {final_count} ключей")
    print(f"   Удалено: {len(keys_to_remove)}")
    print(f"   Переименовано: {len(keys_to_rename)}")

def main():
    import sys
    
    dry_run = '--apply' not in sys.argv
    
    if dry_run:
        print("🔍 DRY RUN MODE")
        print("Запустите с --apply для применения изменений")
        print()
    else:
        print("⚙️  APPLY MODE - изменения будут сохранены")
        print()
    
    # Обрабатываем en.json
    if EN_JSON.exists():
        clean_duplicates(EN_JSON, dry_run=dry_run)
    else:
        print(f"❌ Файл не найден: {EN_JSON}")
    
    # Обрабатываем ru.json (по той же логике)
    if RU_JSON.exists():
        clean_duplicates(RU_JSON, dry_run=dry_run)
    else:
        print(f"⚠️  Файл не найден: {RU_JSON}")

if __name__ == "__main__":
    main()


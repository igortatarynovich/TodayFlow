#!/usr/bin/env python3
"""
Очистка мета-фраз из контента

Удаляет фразы типа "Your X axis shapes/influences how this pattern shows up"
из текстов, делая их более живыми и менее мета-описательными.

Создает резервную копию перед изменениями.
"""

import json
import re
import shutil
from datetime import datetime
from pathlib import Path

CONTENT_DIR = Path(__file__).parent.parent / "CONTENT" / "i18n"
EN_JSON = CONTENT_DIR / "en.json"
RU_JSON = CONTENT_DIR / "ru.json"

# Паттерны мета-фраз для удаления
META_PATTERNS = [
    # "Your X axis shapes how this pattern shows up for you"
    re.compile(
        r'\s*Your\s+(A[1-7]|M[1-4])\s+axis\s+(shapes|influences)\s+how\s+(this\s+pattern\s+shows\s+up|this\s+shows\s+up)\s*(for\s+you)?\.?\s*',
        re.I
    ),
    # "Your X axis influences how this shows up for you"
    re.compile(
        r'\s*Your\s+(A[1-7]|M[1-4])\s+axis\s+(shapes|influences)\s+how\s+this\s+shows\s+up\s*(for\s+you)?\.?\s*',
        re.I
    ),
    # "in your experience. Your X axis..."
    re.compile(
        r'\s+in\s+your\s+experience\.\s*Your\s+(A[1-7]|M[1-4])\s+axis\s+(shapes|influences)\s+how\s+(this\s+pattern\s+shows\s+up|this\s+shows\s+up)\s*(for\s+you)?\.?\s*',
        re.I
    ),
]

def clean_text(text):
    """Удаляет мета-фразы из текста"""
    cleaned = text
    changes = []
    
    for pattern in META_PATTERNS:
        matches = list(pattern.finditer(cleaned))
        if matches:
            # Удаляем с конца строки (обычно мета-фразы в конце)
            for match in reversed(matches):
                start, end = match.span()
                # Проверяем, что это действительно в конце или после точки
                before = cleaned[:start].rstrip()
                after = cleaned[end:].lstrip()
                
                # Если перед мета-фразой есть точка, убираем её тоже
                if before.endswith('.'):
                    before = before[:-1].rstrip()
                
                cleaned = before + (' ' if after and not before.endswith('.') else '') + after
                changes.append(match.group())
    
    # Убираем двойные пробелы
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    
    # Убираем точку в конце, если она осталась одна
    if cleaned.endswith('.'):
        cleaned = cleaned[:-1].strip()
    
    return cleaned, changes

def create_backup(file_path):
    """Создает резервную копию файла"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = file_path.parent / f"{file_path.stem}_backup_{timestamp}.json"
    shutil.copy2(file_path, backup_path)
    return backup_path

def clean_meta_phrases(file_path, dry_run=True):
    """Очищает мета-фразы из JSON файла"""
    # Загружаем данные
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    cleaned_data = {}
    changed_count = 0
    examples = []
    
    for key, value in data.items():
        cleaned_value, changes = clean_text(value)
        
        if changes:
            changed_count += 1
            if len(examples) < 10:
                examples.append({
                    'key': key,
                    'original': value,
                    'cleaned': cleaned_value,
                    'removed': changes[0] if changes else ''
                })
            cleaned_data[key] = cleaned_value
        else:
            cleaned_data[key] = value
    
    if changed_count == 0:
        print(f"✅ В файле {file_path.name} мета-фраз не найдено")
        return
    
    print(f"\n{'=' * 80}")
    print(f"Обработка: {file_path.name}")
    print(f"{'=' * 80}")
    print(f"Всего ключей: {len(data)}")
    print(f"Изменено ключей: {changed_count}")
    print()
    
    if dry_run:
        print("🔍 DRY RUN - изменения не будут сохранены")
        print("\nПримеры изменений:")
        for ex in examples[:5]:
            print(f"\n  {ex['key']}:")
            print(f"    Было: {ex['original'][:120]}...")
            print(f"    Стало: {ex['cleaned'][:120]}...")
            print(f"    Удалено: {ex['removed']}")
        return
    
    # Создаем резервную копию
    backup_path = create_backup(file_path)
    print(f"📦 Резервная копия создана: {backup_path.name}")
    
    # Сохраняем
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(cleaned_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Файл очищен: изменено {changed_count} ключей")

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
        clean_meta_phrases(EN_JSON, dry_run=dry_run)
    else:
        print(f"❌ Файл не найден: {EN_JSON}")
    
    # Для ru.json тоже можно применить, но там переводы могут быть другие
    # Пока пропускаем, можно добавить позже

if __name__ == "__main__":
    main()


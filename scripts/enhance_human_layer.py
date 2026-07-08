#!/usr/bin/env python3
"""
Скрипт для улучшения Human Layer

Добавляет human_text к существующим элементам контента,
которые еще не имеют human_text.
"""

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CONTENT_DIR = REPO_ROOT / "CONTENT"
sys.path.insert(0, str(CONTENT_DIR / "human_layer"))

from human_layer import process_content_item


def enhance_file(file_path: Path, dry_run: bool = True):
    """Улучшает файл, добавляя human_text."""
    if not file_path.exists():
        print(f"Файл не найден: {file_path}")
        return
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if not isinstance(data, list):
        print(f"Файл должен содержать массив: {file_path}")
        return
    
    enhanced_count = 0
    for item in data:
        # Пропускаем, если human_text уже есть
        if item.get('human_text'):
            continue
        
        # Обрабатываем через Human Layer
        enhanced = process_content_item(item)
        if enhanced.get('human_text') and enhanced['human_text'] != item.get('human_text'):
            item['human_text'] = enhanced['human_text']
            enhanced_count += 1
    
    if enhanced_count > 0:
        if dry_run:
            print(f"  [DRY RUN] Будет обновлено {enhanced_count} элементов в {file_path.name}")
        else:
            # Сохраняем обратно
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"  ✅ Обновлено {enhanced_count} элементов в {file_path.name}")
    else:
        print(f"  ℹ️  Все элементы уже имеют human_text в {file_path.name}")


def main():
    """Главная функция."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Улучшает контент через Human Layer')
    parser.add_argument('--apply', action='store_true', help='Применить изменения (по умолчанию dry-run)')
    args = parser.parse_args()
    
    print("=" * 70)
    print("УЛУЧШЕНИЕ КОНТЕНТА ЧЕРЕЗ HUMAN LAYER")
    print("=" * 70)
    print()
    
    if not args.apply:
        print("Режим: DRY RUN (изменения не будут сохранены)")
        print("Используйте --apply для применения изменений")
        print()
    
    # Файлы для обработки
    files_to_process = [
        CONTENT_DIR / "forecasts" / "moon_phases.json",
        CONTENT_DIR / "forecasts" / "weekly.json",
        CONTENT_DIR / "forecasts" / "planetary_events.json",
        CONTENT_DIR / "practices" / "mantras.json",
        CONTENT_DIR / "practices" / "check_ins.json",
        CONTENT_DIR / "practices" / "tarot_spreads.json",
        CONTENT_DIR / "rituals" / "rituals.json",
        CONTENT_DIR / "daily" / "daily_templates.json",
    ]
    
    for file_path in files_to_process:
        if file_path.exists():
            enhance_file(file_path, dry_run=not args.apply)
    
    print()
    print("=" * 70)
    if args.apply:
        print("✅ Изменения применены!")
    else:
        print("✅ Dry-run завершен (используйте --apply для применения)")
    print("=" * 70)


if __name__ == '__main__':
    main()


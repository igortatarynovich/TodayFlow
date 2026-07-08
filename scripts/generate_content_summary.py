#!/usr/bin/env python3
"""
Генерация сводки по контенту в Content System

Создает отчет о количестве элементов контента,
типах, статистике и структуре.
"""

import json
from pathlib import Path
from collections import defaultdict

REPO_ROOT = Path(__file__).resolve().parents[1]
CONTENT_DIR = REPO_ROOT / "CONTENT"


def count_items_in_file(file_path: Path) -> int:
    """Подсчитывает количество элементов в файле."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                return len(data)
            elif isinstance(data, dict):
                return 1
            return 0
    except Exception:
        return 0


def analyze_content():
    """Анализирует контент и создает сводку."""
    stats = defaultdict(lambda: {'files': 0, 'items': 0, 'types': set()})
    
    # Анализируем директории
    directories = {
        'forecasts': CONTENT_DIR / "forecasts",
        'practices': CONTENT_DIR / "practices",
        'rituals': CONTENT_DIR / "rituals",
        'daily': CONTENT_DIR / "daily",
    }
    
    for category, directory in directories.items():
        if not directory.exists():
            continue
        
        json_files = list(directory.glob("*.json"))
        # Пропускаем migrated файлы
        json_files = [f for f in json_files if 'migrated' not in f.name]
        
        for file_path in json_files:
            count = count_items_in_file(file_path)
            if count > 0:
                stats[category]['files'] += 1
                stats[category]['items'] += count
                stats[category]['types'].add(file_path.stem)
    
    return stats


def print_summary(stats):
    """Выводит сводку."""
    print("=" * 70)
    print("СВОДКА ПО CONTENT SYSTEM")
    print("=" * 70)
    print()
    
    total_files = sum(s['files'] for s in stats.values())
    total_items = sum(s['items'] for s in stats.values())
    
    for category in sorted(stats.keys()):
        data = stats[category]
        print(f"{category.upper()}:")
        print(f"  Файлов: {data['files']}")
        print(f"  Элементов: {data['items']}")
        if data['types']:
            print(f"  Типы: {', '.join(sorted(data['types']))}")
        print()
    
    print("-" * 70)
    print(f"ВСЕГО:")
    print(f"  Файлов: {total_files}")
    print(f"  Элементов: {total_items}")
    print()
    print("=" * 70)


def main():
    """Главная функция."""
    stats = analyze_content()
    print_summary(stats)


if __name__ == '__main__':
    main()


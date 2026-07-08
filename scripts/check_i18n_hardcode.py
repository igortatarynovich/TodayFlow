#!/usr/bin/env python3
"""
Скрипт для проверки хардкода текста в frontend файлах
Ищет русский текст, который должен быть через i18n
"""

import re
import json
import os
from pathlib import Path
from collections import defaultdict
from typing import List, Dict, Tuple

FRONTEND_SRC = Path(__file__).parent.parent / "frontend" / "src"
I18N_EN = Path(__file__).parent.parent / "CONTENT" / "i18n" / "app.en.json"
I18N_RU = Path(__file__).parent.parent / "CONTENT" / "i18n" / "app.ru.json"

# Паттерны для поиска хардкода русского текста
RUSSIAN_PATTERN = re.compile(r'[А-Яа-яЁё]{2,}')
# Исключения - технические строки, которые могут содержать кириллицу
EXCLUDE_PATTERNS = [
    r'\/\/.*',  # Комментарии
    r'console\.(log|error|warn).*',  # Консольные логи
    r'aria-label.*',  # Атрибуты доступности (пока пропускаем)
]

def is_excluded(line: str) -> bool:
    """Проверяет, должна ли строка быть исключена из проверки"""
    line_clean = line.strip()
    for pattern in EXCLUDE_PATTERNS:
        if re.search(pattern, line_clean):
            return True
    return False

def find_hardcoded_russian(file_path: Path) -> List[Tuple[int, str]]:
    """Находит строки с хардкодом русского текста"""
    issues = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for i, line in enumerate(lines, 1):
                if is_excluded(line):
                    continue
                # Ищем русский текст в строковых литералах
                # Паттерн для строк в кавычках и JSX текста
                if RUSSIAN_PATTERN.search(line):
                    # Проверяем, что это не ключ перевода (t("key"))
                    if not re.search(r't\(["\']', line) and not re.search(r'from.*i18n', line):
                        issues.append((i, line.strip()))
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    return issues

def load_i18n_keys(file_path: Path) -> set:
    """Загружает все ключи из i18n файла"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return set(data.keys())
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return set()

def check_all_files():
    """Проверяет все .tsx и .ts файлы на хардкод"""
    issues_by_file = defaultdict(list)
    tsx_files = list(FRONTEND_SRC.rglob("*.tsx")) + list(FRONTEND_SRC.rglob("*.ts"))
    
    for file_path in tsx_files:
        # Пропускаем node_modules и другие исключения
        if 'node_modules' in str(file_path) or '__tests__' in str(file_path):
            continue
        issues = find_hardcoded_russian(file_path)
        if issues:
            issues_by_file[file_path] = issues
    
    return issues_by_file

def check_i18n_parity():
    """Проверяет соответствие ключей между en и ru"""
    en_keys = load_i18n_keys(I18N_EN)
    ru_keys = load_i18n_keys(I18N_RU)
    
    missing_in_ru = en_keys - ru_keys
    missing_in_en = ru_keys - en_keys
    
    return {
        'en_keys_count': len(en_keys),
        'ru_keys_count': len(ru_keys),
        'missing_in_ru': missing_in_ru,
        'missing_in_en': missing_in_en,
        'common_keys': len(en_keys & ru_keys)
    }

def main():
    print("=" * 80)
    print("Проверка i18n и хардкода текста")
    print("=" * 80)
    print()
    
    # Проверка соответствия ключей
    print("1. Проверка соответствия ключей переводов:")
    print("-" * 80)
    parity = check_i18n_parity()
    print(f"Ключей в app.en.json: {parity['en_keys_count']}")
    print(f"Ключей в app.ru.json: {parity['ru_keys_count']}")
    print(f"Общих ключей: {parity['common_keys']}")
    
    if parity['missing_in_ru']:
        print(f"\n⚠️  Ключей, отсутствующих в app.ru.json: {len(parity['missing_in_ru'])}")
        for key in sorted(list(parity['missing_in_ru']))[:10]:
            print(f"   - {key}")
        if len(parity['missing_in_ru']) > 10:
            print(f"   ... и ещё {len(parity['missing_in_ru']) - 10}")
    
    if parity['missing_in_en']:
        print(f"\n⚠️  Ключей, отсутствующих в app.en.json: {len(parity['missing_in_en'])}")
        for key in sorted(list(parity['missing_in_en']))[:10]:
            print(f"   - {key}")
        if len(parity['missing_in_en']) > 10:
            print(f"   ... и ещё {len(parity['missing_in_en']) - 10}")
    
    print()
    print("2. Поиск хардкода русского текста в компонентах:")
    print("-" * 80)
    
    issues_by_file = check_all_files()
    
    if not issues_by_file:
        print("✅ Хардкод не найден!")
    else:
        print(f"⚠️  Найдено файлов с хардкодом: {len(issues_by_file)}\n")
        for file_path, issues in sorted(issues_by_file.items()):
            rel_path = file_path.relative_to(FRONTEND_SRC.parent)
            print(f"\n📄 {rel_path}:")
            for line_num, line_content in issues[:5]:  # Показываем первые 5
                # Обрезаем длинные строки
                display_line = line_content[:100] + "..." if len(line_content) > 100 else line_content
                print(f"   Строка {line_num}: {display_line}")
            if len(issues) > 5:
                print(f"   ... и ещё {len(issues) - 5} строк")

if __name__ == "__main__":
    main()


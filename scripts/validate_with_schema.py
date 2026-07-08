#!/usr/bin/env python3
"""
Валидация контента с использованием JSON схем

Проверяет контент на соответствие JSON схемам.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional

try:
    import jsonschema
    from jsonschema import validate, ValidationError
except ImportError:
    print("Ошибка: требуется установить jsonschema")
    print("Установите: pip install jsonschema")
    sys.exit(1)

REPO_ROOT = Path(__file__).resolve().parents[1]
CONTENT_DIR = REPO_ROOT / "CONTENT"
SCHEMAS_DIR = CONTENT_DIR / "schemas"


def load_schema(schema_name: str) -> Dict[str, Any]:
    """Загружает JSON схему."""
    schema_path = SCHEMAS_DIR / schema_name
    if not schema_path.exists():
        raise FileNotFoundError(f"Схема не найдена: {schema_path}")
    
    with open(schema_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def validate_file_with_schema(file_path: Path, schema_name: str) -> tuple[bool, list]:
    """Валидирует файл с использованием схемы."""
    schema = load_schema(schema_name)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return False, [f"Ошибка JSON: {e}"]
    
    errors = []
    try:
        validate(instance=data, schema=schema)
        return True, []
    except ValidationError as e:
        errors.append(f"Ошибка валидации: {e.message}")
        if e.path:
            errors.append(f"  Путь: {'.'.join(str(p) for p in e.path)}")
        return False, errors


def main():
    """Главная функция."""
    if not SCHEMAS_DIR.exists():
        print(f"Директория схем не найдена: {SCHEMAS_DIR}")
        sys.exit(1)
    
    print("=" * 70)
    print("ВАЛИДАЦИЯ КОНТЕНТА С ИСПОЛЬЗОВАНИЕМ JSON СХЕМ")
    print("=" * 70)
    print()
    
    # Маппинг файлов к схемам
    validations = [
        (CONTENT_DIR / "forecasts" / "moon_phases.json", "moon_phase.schema.json"),
        (CONTENT_DIR / "daily" / "daily_templates.json", "daily_template.schema.json"),
        (CONTENT_DIR / "rituals" / "rituals.json", "ritual.schema.json"),
    ]
    
    all_passed = True
    for file_path, schema_name in validations:
        if not file_path.exists():
            print(f"⚠️  Файл не найден: {file_path}")
            continue
        
        print(f"Валидация {file_path.name} с {schema_name}...")
        passed, errors = validate_file_with_schema(file_path, schema_name)
        
        if passed:
            print(f"  ✅ Валидация пройдена\n")
        else:
            all_passed = False
            print(f"  ❌ Ошибки валидации:")
            for error in errors:
                print(f"    • {error}")
            print()
    
    if all_passed:
        print("=" * 70)
        print("✅ Все файлы прошли валидацию!")
        print("=" * 70)
        sys.exit(0)
    else:
        print("=" * 70)
        print("❌ Некоторые файлы не прошли валидацию")
        print("=" * 70)
        sys.exit(1)


if __name__ == '__main__':
    main()


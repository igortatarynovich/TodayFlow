#!/usr/bin/env python3
"""
Скрипт валидации контента в Content System

Проверяет структуру, наличие обязательных полей,
качество human_text и соответствие стандартам.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

REPO_ROOT = Path(__file__).resolve().parents[1]
CONTENT_DIR = REPO_ROOT / "CONTENT"


class ContentValidator:
    """Валидатор контента."""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def validate_file(self, file_path: Path) -> bool:
        """Валидирует файл контента."""
        if not file_path.exists():
            self.errors.append(f"Файл не найден: {file_path}")
            return False
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            self.errors.append(f"Ошибка JSON в {file_path}: {e}")
            return False
        
        # Проверяем структуру
        if isinstance(data, list):
            for i, item in enumerate(data):
                self._validate_item(item, file_path, index=i)
        elif isinstance(data, dict):
            self._validate_item(data, file_path)
        else:
            self.errors.append(f"Неверная структура в {file_path}: должен быть dict или list")
            return False
        
        return len(self.errors) == 0
    
    def _validate_item(self, item: Dict[str, Any], file_path: Path, index: Optional[int] = None):
        """Валидирует элемент контента."""
        location = f"{file_path}"
        if index is not None:
            location += f"[{index}]"
        
        # Проверяем наличие обязательных полей
        if 'human_text' not in item or not item.get('human_text'):
            self.warnings.append(f"{location}: отсутствует human_text")
        
        # Проверяем качество human_text
        if 'human_text' in item and item['human_text']:
            human_text = item['human_text']
            self._validate_human_text(human_text, location)
        
        # Проверяем наличие ID
        id_fields = ['template_id', 'id', 'phase_id', 'spread_id', 'ritual_id', 'forecast_id', 'mantra_id', 'check_in_id']
        has_id = any(field in item for field in id_fields)
        if not has_id:
            self.warnings.append(f"{location}: отсутствует идентификатор")
        
        # Проверяем абстрактные фразы в human_text
        if 'human_text' in item and item['human_text']:
            self._check_abstract_phrases(item['human_text'], location)
    
    def _validate_human_text(self, text: str, location: str):
        """Валидирует качество human_text."""
        if len(text) < 10:
            self.warnings.append(f"{location}: human_text слишком короткий ({len(text)} символов)")
        
        if len(text) > 1000:
            self.warnings.append(f"{location}: human_text слишком длинный ({len(text)} символов)")
    
    def _check_abstract_phrases(self, text: str, location: str):
        """Проверяет наличие абстрактных фраз."""
        abstract_phrases = [
            "your system",
            "nervous system",
            "emotional system",
            "recalibrate",
            "metabolize",
            "restore equilibrium",
            "emotional access",
            "inner balance",
            "emotional atmosphere",
            "felt safety",
        ]
        
        text_lower = text.lower()
        for phrase in abstract_phrases:
            if phrase in text_lower:
                self.warnings.append(f"{location}: найдена абстрактная фраза '{phrase}' в human_text")
    
    def validate_directory(self, directory: Path, pattern: str = "*.json"):
        """Валидирует все файлы в директории."""
        if not directory.exists():
            self.errors.append(f"Директория не найдена: {directory}")
            return
        
        json_files = list(directory.rglob(pattern))
        for file_path in sorted(json_files):
            # Пропускаем migrated файлы
            if 'migrated' in file_path.name:
                continue
            self.validate_file(file_path)
    
    def print_report(self):
        """Выводит отчет о валидации."""
        print("=" * 70)
        print("ОТЧЕТ О ВАЛИДАЦИИ КОНТЕНТА")
        print("=" * 70)
        print()
        
        if self.errors:
            print(f"❌ ОШИБКИ ({len(self.errors)}):")
            for error in self.errors:
                print(f"  • {error}")
            print()
        
        if self.warnings:
            print(f"⚠️  ПРЕДУПРЕЖДЕНИЯ ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  • {warning}")
            print()
        
        if not self.errors and not self.warnings:
            print("✅ Все проверки пройдены успешно!")
            print()
        elif not self.errors:
            print(f"✅ Критических ошибок нет, но есть {len(self.warnings)} предупреждений")
            print()
        else:
            print(f"❌ Найдено {len(self.errors)} ошибок")
            print()


def main():
    """Главная функция."""
    validator = ContentValidator()
    
    # Валидируем основные директории контента
    directories = [
        CONTENT_DIR / "forecasts",
        CONTENT_DIR / "practices",
        CONTENT_DIR / "rituals",
        CONTENT_DIR / "daily",
    ]
    
    for directory in directories:
        if directory.exists():
            print(f"Валидация {directory.name}...")
            validator.validate_directory(directory)
    
    validator.print_report()
    
    # Возвращаем код выхода
    sys.exit(0 if len(validator.errors) == 0 else 1)


if __name__ == '__main__':
    main()


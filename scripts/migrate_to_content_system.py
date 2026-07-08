#!/usr/bin/env python3
"""
Скрипт миграции контента из i18n в Content System

Переносит контент из i18n/en.json и i18n/app.en.json
в структурированный формат Content System.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any

# Добавляем human_layer в путь
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "CONTENT" / "human_layer"))

from human_layer import process_content_item, transform_text


def load_i18n_file(path: Path) -> Dict[str, str]:
    """Загружает i18n файл."""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def extract_moon_phases(data: Dict[str, str]) -> List[Dict[str, Any]]:
    """Извлекает moon phases из app.en.json."""
    moon_phases = []
    
    for key, value in data.items():
        if key.startswith('moon_phase.'):
            parts = key.split('.')
            if len(parts) >= 3:
                phase_id = parts[1]  # new_moon, waxing_crescent, etc.
                field = parts[2]  # themes, guidance
                
                # Находим или создаем запись
                phase_entry = next(
                    (p for p in moon_phases if p.get('phase_id') == phase_id),
                    None
                )
                
                if not phase_entry:
                    phase_entry = {'phase_id': phase_id}
                    moon_phases.append(phase_entry)
                
                phase_entry[field] = value
    
    return moon_phases


def extract_daily_templates(data: Dict[str, str]) -> List[Dict[str, Any]]:
    """Извлекает DAILY templates из en.json."""
    daily_templates = []
    
    for key, value in data.items():
        if key.startswith('DAILY.'):
            parts = key.split('.')
            if len(parts) >= 2:
                template_type = parts[1]  # AFFIRMATION, DIGEST, etc.
                template_id = parts[2] if len(parts) > 2 else '001'
                
                template = {
                    'template_id': key,
                    'type': template_type,
                    'text': value
                }
                
                # Добавляем human_text
                template = process_content_item(template)
                daily_templates.append(template)
    
    return daily_templates


def migrate_moon_phases(i18n_path: Path, output_path: Path):
    """Мигрирует moon phases из i18n в Content System."""
    print(f"Миграция moon phases из {i18n_path}...")
    
    data = load_i18n_file(i18n_path)
    moon_phases = extract_moon_phases(data)
    
    # Обрабатываем через Human Layer
    processed_phases = []
    for phase in moon_phases:
        processed = process_content_item(phase)
        processed_phases.append(processed)
    
    # Сохраняем
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(processed_phases, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Мигрировано {len(processed_phases)} moon phases в {output_path}")
    return processed_phases


def migrate_daily_templates(i18n_path: Path, output_path: Path, limit: int = None):
    """Мигрирует DAILY templates из i18n в Content System."""
    print(f"Миграция DAILY templates из {i18n_path}...")
    
    data = load_i18n_file(i18n_path)
    daily_templates = extract_daily_templates(data)
    
    if limit:
        daily_templates = daily_templates[:limit]
        print(f"  (ограничено {limit} элементами для теста)")
    
    # Обрабатываем через Human Layer
    processed_templates = []
    for template in daily_templates:
        processed = process_content_item(template)
        processed_templates.append(processed)
    
    # Сохраняем
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(processed_templates, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Мигрировано {len(processed_templates)} DAILY templates в {output_path}")
    return processed_templates


def main():
    """Главная функция."""
    repo_root = Path(__file__).resolve().parents[1]
    
    i18n_dir = repo_root / "CONTENT" / "i18n"
    content_dir = repo_root / "CONTENT"
    
    app_en_path = i18n_dir / "app.en.json"
    en_path = i18n_dir / "en.json"
    
    print("=" * 70)
    print("МИГРАЦИЯ КОНТЕНТА ИЗ I18N В CONTENT SYSTEM")
    print("=" * 70)
    print()
    
    # Миграция moon phases (пример)
    if app_en_path.exists():
        output_path = content_dir / "forecasts" / "moon_phases_migrated.json"
        migrate_moon_phases(app_en_path, output_path)
        print()
    
    # Миграция DAILY templates (пример, первые 20)
    if en_path.exists():
        output_path = content_dir / "daily" / "daily_templates_migrated.json"
        migrate_daily_templates(en_path, output_path, limit=20)
        print()
    
    print("=" * 70)
    print("МИГРАЦИЯ ЗАВЕРШЕНА (пример)")
    print("=" * 70)
    print()
    print("Примечание: Это пример миграции.")
    print("Для полной миграции запустите скрипт без limit.")


if __name__ == '__main__':
    main()


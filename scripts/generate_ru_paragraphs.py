#!/usr/bin/env python3
"""
Generate Russian translations for paragraph templates.

This script creates proper Russian translations following i18n quality rules v1.
For production, this should use a translation API or manual translation.
"""

import json
from pathlib import Path
from typing import Dict

REPO_ROOT = Path(__file__).resolve().parents[1]
I18N_DIR = REPO_ROOT / "CONTENT" / "i18n"
EN_PATH = I18N_DIR / "en.json"
RU_PATH = I18N_DIR / "ru.json"


def translate_paragraph_to_ru(en_text: str, para_id: str) -> str:
    """
    Translate a paragraph template text to Russian.
    
    This is a placeholder that creates proper structure.
    In production, use translation API or manual translation.
    
    Rules:
    - Use "ты" (informal you) for second person
    - Avoid категоричность (always, never, must, should)
    - Use probabilistic language (может, склонен, часто)
    - Keep calm, grounded tone
    - Avoid психологизирующие формулировки
    """
    
    # For now, return empty string to enable EN fallback
    # Real translations should be added manually or via translation service
    return ""


def main():
    """Generate RU translations structure"""
    print("=" * 70)
    print("Generating Russian Translations Structure")
    print("=" * 70)
    
    # Load EN data
    print("\nLoading EN i18n data...")
    with open(EN_PATH, 'r', encoding='utf-8') as f:
        en_data = json.load(f)
    
    print(f"Loaded {len(en_data)} EN keys")
    
    # Extract paragraph template keys
    paragraph_keys = {}
    for key, value in en_data.items():
        if "." in key and key.split(".")[0].startswith(("EP-", "RL-", "CR-", "MS-", "LT-")):
            paragraph_keys[key] = value
    
    print(f"Found {len(paragraph_keys)} paragraph template keys")
    
    # Load existing RU data
    existing_ru = {}
    if RU_PATH.exists():
        try:
            with open(RU_PATH, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content and content != "{}":
                    existing_ru = json.loads(content)
            print(f"Found existing RU file with {len(existing_ru)} keys")
        except json.JSONDecodeError:
            print("Existing RU file is invalid, starting fresh")
    
    # Create RU translations (empty for now - will use EN fallback)
    # In production, fill these with actual translations
    ru_translations = {}
    for key, en_text in paragraph_keys.items():
        # For now, leave empty to use EN fallback
        # When ready, replace with: ru_translations[key] = translate_paragraph_to_ru(en_text, key.split('.')[0])
        ru_translations[key] = ""
    
    # Merge with existing
    final_ru = {**existing_ru}
    final_ru.update(ru_translations)
    
    # Save
    print(f"\nSaving RU translations structure...")
    with open(RU_PATH, 'w', encoding='utf-8') as f:
        json.dump(final_ru, f, ensure_ascii=False, indent=2)
    
    print(f"✓ Saved {len(ru_translations)} RU translation keys to {RU_PATH}")
    print(f"\nNote: All translations are empty - system will use EN fallback")
    print(f"To add translations, fill in the values manually or use translation service")


if __name__ == "__main__":
    main()


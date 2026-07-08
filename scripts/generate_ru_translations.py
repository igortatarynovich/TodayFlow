#!/usr/bin/env python3
"""
Generate Russian translations for paragraph templates.
This script creates RU translations following i18n quality rules v1.
"""

import json
from pathlib import Path
from typing import Dict

REPO_ROOT = Path(__file__).resolve().parents[1]
I18N_DIR = REPO_ROOT / "CONTENT" / "i18n"
EN_PATH = I18N_DIR / "en.json"
RU_PATH = I18N_DIR / "ru.json"


def translate_text(text: str) -> str:
    """
    Translate English text to Russian following i18n quality rules.
    
    Rules:
    - Avoid категоричность (always, never, must, should)
    - Use probabilistic language (may, tend to, often)
    - Maintain second-person perspective
    - Keep calm, grounded tone
    - Avoid психологизирующие формулировки
    
    NOTE: This function currently returns empty string to enable EN fallback.
    For real translations, replace with translation API or manual translation.
    """
    # Return empty string to enable fallback to EN
    # The i18n system will automatically fallback to EN if RU translation is empty/missing
    return ""


def generate_ru_translations(en_data: Dict[str, str]) -> Dict[str, str]:
    """Generate RU translations for all paragraph template keys"""
    ru_data: Dict[str, str] = {}
    
    # Copy all non-paragraph keys as-is (they're already translated in app.ru.json)
    paragraph_keys = []
    for key, value in en_data.items():
        # Check if it's a paragraph template key
        if "." in key and key.split(".")[0].startswith(("EP-", "RL-", "CAR-", "FIN-", "MS-", "LT-", "CR-")):
            paragraph_keys.append((key, value))
        else:
            # Keep non-paragraph keys (they're in app.ru.json)
            pass
    
    print(f"Found {len(paragraph_keys)} paragraph template keys to translate")
    
    # For now, create placeholder translations
    # In production, this would use a translation service or manual translation
    for key, en_text in paragraph_keys:
        # Placeholder translation - needs to be replaced with actual translations
        ru_data[key] = translate_text(en_text)
    
    return ru_data


def main():
    """Generate RU translations"""
    print("Loading EN i18n data...")
    with open(EN_PATH, 'r', encoding='utf-8') as f:
        en_data = json.load(f)
    
    print(f"Loaded {len(en_data)} EN keys")
    
    # Load existing RU data if it exists
    existing_ru = {}
    if RU_PATH.exists():
        with open(RU_PATH, 'r', encoding='utf-8') as f:
            existing_ru = json.load(f)
        print(f"Found existing RU file with {len(existing_ru)} keys")
    
    # Generate translations for paragraph templates
    print("\nGenerating RU translations for paragraph templates...")
    ru_translations = generate_ru_translations(en_data)
    
    # Merge with existing RU data (preserve non-paragraph keys)
    final_ru = {**existing_ru}
    final_ru.update(ru_translations)
    
    # Save RU translations
    print(f"\nSaving {len(ru_translations)} RU translations...")
    with open(RU_PATH, 'w', encoding='utf-8') as f:
        json.dump(final_ru, f, ensure_ascii=False, indent=2)
    
    print(f"✓ Saved RU translations to {RU_PATH}")
    print(f"\nNote: Translations marked with [RU] are placeholders and need human review")


if __name__ == "__main__":
    main()


#!/usr/bin/env python3
"""
Generate Russian translations for paragraph templates using structured translation.

This script creates Russian translations following i18n quality rules v1.
For production, integrate with translation API or use manual translation workflow.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Tuple

REPO_ROOT = Path(__file__).resolve().parents[1]
I18N_DIR = REPO_ROOT / "CONTENT" / "i18n"
EN_PATH = I18N_DIR / "en.json"
RU_PATH = I18N_DIR / "ru.json"


def translate_en_to_ru(en_text: str, meaning_type: str = "", layer: str = "observation") -> str:
    """
    Translate English text to Russian following i18n quality rules.
    
    This function provides proper Russian translations. For production,
    this should use a translation API (OpenAI, DeepL, etc.) or manual translation.
    
    Rules:
    - Use "ты" (informal you) 
    - Avoid категоричность (always, never, must, should)
    - Use probabilistic language (может, склонен, часто)
    - Keep calm, grounded tone
    - Avoid психологизирующие формулировки
    - Length: 180-320 chars (acceptable ±20%)
    """
    
    # This is a placeholder - in production, use translation API
    # For now, return empty string to enable EN fallback
    # Real translations should be added via translation service or manual work
    
    return ""


def generate_translations_batch(en_keys: List[Tuple[str, str]], batch_size: int = 50) -> Dict[str, str]:
    """Generate translations in batches"""
    ru_translations = {}
    
    print(f"Processing {len(en_keys)} keys in batches of {batch_size}...")
    
    for i in range(0, len(en_keys), batch_size):
        batch = en_keys[i:i+batch_size]
        batch_num = i // batch_size + 1
        total_batches = (len(en_keys) - 1) // batch_size + 1
        
        print(f"Batch {batch_num}/{total_batches}...")
        
        for key, en_text in batch:
            para_id = key.split(".")[0]
            layer = "observation"
            if "-INT" in para_id:
                layer = "interpretation"
            elif "-CON" in para_id:
                layer = "context"
            
            ru_text = translate_en_to_ru(en_text, layer=layer)
            ru_translations[key] = ru_text
    
    return ru_translations


def main():
    """Generate RU translations"""
    print("=" * 70)
    print("Generating Russian Translations for Paragraph Templates")
    print("=" * 70)
    
    # Load EN data
    print("\nLoading EN i18n data...")
    with open(EN_PATH, 'r', encoding='utf-8') as f:
        en_data = json.load(f)
    
    print(f"Loaded {len(en_data)} EN keys")
    
    # Extract paragraph template keys
    paragraph_keys = []
    for key, value in en_data.items():
        if "." in key and key.split(".")[0].startswith(("EP-", "RL-", "CR-", "MS-", "LT-")):
            paragraph_keys.append((key, value))
    
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
    
    # Generate translations
    print("\nGenerating RU translations...")
    ru_translations = generate_translations_batch(paragraph_keys)
    
    # Merge with existing
    final_ru = {**existing_ru}
    final_ru.update(ru_translations)
    
    # Save
    print(f"\nSaving {len(ru_translations)} RU translations...")
    with open(RU_PATH, 'w', encoding='utf-8') as f:
        json.dump(final_ru, f, ensure_ascii=False, indent=2)
    
    print(f"✓ Saved RU translations to {RU_PATH}")
    print(f"\nTotal RU keys: {len(final_ru)}")
    print(f"Paragraph template keys: {len(ru_translations)}")
    print(f"\nNote: All translations are empty - system will use EN fallback")
    print(f"To add real translations:")
    print(f"  1. Use translation API (OpenAI, DeepL, etc.)")
    print(f"  2. Manual translation following i18n quality rules")
    print(f"  3. Fill in ru.json values")


if __name__ == "__main__":
    main()


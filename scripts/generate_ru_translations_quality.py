#!/usr/bin/env python3
"""
Generate Russian translations for paragraph templates following i18n quality rules v1.

Rules for RU:
- Avoid категоричность (always, never, must, should)
- Use probabilistic language (may, tend to, often) -> может, склонен, часто
- Maintain second-person perspective (you -> ты/вы)
- Keep calm, grounded tone
- Avoid психологизирующие формулировки
- Length: 180-320 chars (acceptable ±20%)
- Variants must be diverse
"""

import json
import re
from pathlib import Path
from typing import Dict, List

REPO_ROOT = Path(__file__).resolve().parents[1]
I18N_DIR = REPO_ROOT / "CONTENT" / "i18n"
EN_PATH = I18N_DIR / "en.json"
RU_PATH = I18N_DIR / "ru.json"


def translate_text_to_ru(text: str, meaning_type: str = "", layer: str = "observation") -> str:
    """
    Translate English text to Russian following i18n quality rules.
    
    This is a placeholder function that creates proper Russian translations.
    In production, this would use a translation API or manual translation.
    """
    # Basic translation patterns following rules
    
    # Replace common patterns
    translations = {
        "You tend to": "Ты склонен",
        "You may notice": "Ты можешь заметить",
        "You often": "Ты часто",
        "You're not usually": "Обычно ты не",
        "Emotions can": "Эмоции могут",
        "Your emotional": "Твоя эмоциональная",
        "When": "Когда",
        "Under pressure": "Под давлением",
        "Stress can": "Стресс может",
        "You can be": "Ты можешь быть",
        "It can take": "Может потребоваться",
        "For you": "Для тебя",
    }
    
    # This is a simplified placeholder - real translation needs proper NLP/translation service
    # For now, return a marker that indicates translation is needed
    return f"[TRANSLATE] {text}"


def generate_ru_translations(en_data: Dict[str, str]) -> Dict[str, str]:
    """Generate RU translations for all paragraph template keys"""
    ru_data: Dict[str, str] = {}
    
    # Extract paragraph template keys
    paragraph_keys = []
    for key, value in en_data.items():
        if "." in key and key.split(".")[0].startswith(("EP-", "RL-", "CR-", "MS-", "LT-")):
            paragraph_keys.append((key, value))
    
    print(f"Found {len(paragraph_keys)} paragraph template keys to translate")
    
    # Group by paragraph_id to understand context
    by_paragraph = {}
    for key, text in paragraph_keys:
        para_id = key.split(".")[0]
        variant_id = key.split(".")[1]
        if para_id not in by_paragraph:
            by_paragraph[para_id] = {}
        by_paragraph[para_id][variant_id] = text
    
    # Generate translations
    translated_count = 0
    for para_id, variants in by_paragraph.items():
        # Determine layer and meaning from paragraph_id
        layer = "observation"
        if "-INT" in para_id:
            layer = "interpretation"
        elif "-CON" in para_id:
            layer = "context"
        
        for variant_id, en_text in variants.items():
            key = f"{para_id}.{variant_id}"
            # For now, create placeholder - needs real translation
            ru_data[key] = translate_text_to_ru(en_text, layer=layer)
            translated_count += 1
    
    print(f"Generated {translated_count} RU translations (placeholders)")
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
        try:
            with open(RU_PATH, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content and content != "{}":
                    existing_ru = json.loads(content)
            print(f"Found existing RU file with {len(existing_ru)} keys")
        except json.JSONDecodeError:
            print("Existing RU file is invalid, starting fresh")
    
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
    print(f"\nNote: Translations marked with [TRANSLATE] need human review")
    print(f"Total RU keys: {len(final_ru)}")


if __name__ == "__main__":
    main()


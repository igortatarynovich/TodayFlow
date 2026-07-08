#!/usr/bin/env python3
"""Translate missing RU translations using DeepL API or fallback method."""

import json
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

EN_FILE = REPO_ROOT / "CONTENT" / "i18n" / "en.json"
RU_FILE = REPO_ROOT / "CONTENT" / "i18n" / "ru.json"

def translate_text(text: str, method: str = "simple") -> str:
    """
    Translate text from EN to RU.
    For now, uses simple placeholder that preserves structure.
    In production, would use DeepL API or similar.
    """
    if method == "api":
        # TODO: Integrate DeepL API or similar
        # For now, return placeholder
        return f"[RU: {text[:50]}...]"
    else:
        # For now, return empty to indicate need for translation
        # User should use external translation service
        return ""

def main():
    """Main translation function."""
    # Load files
    with open(EN_FILE, 'r', encoding='utf-8') as f:
        en_data = json.load(f)
    
    with open(RU_FILE, 'r', encoding='utf-8') as f:
        ru_data = json.load(f)
    
    # Find empty translations
    empty_keys = []
    for key in en_data.keys():
        ru_value = ru_data.get(key, '')
        if not ru_value or (isinstance(ru_value, str) and ru_value.strip() == ''):
            empty_keys.append(key)
    
    print(f"Found {len(empty_keys)} empty translations")
    
    if not empty_keys:
        print("All translations are complete!")
        return
    
    # For now, we'll create a template file with EN texts
    # that can be used with external translation service
    print(f"\nCreating translation template...")
    
    template = {}
    for key in empty_keys:
        template[key] = en_data[key]
    
    template_file = REPO_ROOT / "CONTENT" / "i18n" / "translation_template.json"
    with open(template_file, 'w', encoding='utf-8') as f:
        json.dump(template, f, ensure_ascii=False, indent=2)
    
    print(f"Translation template saved to: {template_file}")
    print(f"\nTo translate:")
    print(f"1. Use DeepL API, Google Translate API, or similar")
    print(f"2. Translate the keys in {template_file}")
    print(f"3. Merge translations back into {RU_FILE}")
    
    # Ask if user wants to use a simple batch translation
    # For now, we'll use a placeholder approach
    print(f"\nNote: Automated translation requires API keys.")
    print(f"Manual translation recommended for quality control.")

if __name__ == "__main__":
    main()


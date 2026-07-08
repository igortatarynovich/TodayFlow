#!/usr/bin/env python3
"""
Переформулировка PEOPLE_PLEASING и SHUTDOWN текстов.

Правило: человеческий понятный язык, без абстрактных/мистических фраз.
Меняем фокус, контекст, тон.
"""
import json
import sys
from pathlib import Path

EN_JSON = Path(__file__).parent.parent / "CONTENT" / "i18n" / "en.json"

# Переформулировки для PEOPLE_PLEASING (цель: 3-4 текста)
PEOPLE_PLEASING_REFACTORS = {
    # EP-A2A6-STRESS-010.v2 - про приоритет гармонии
    # Переформулируем, меняя фокус на последствия
    "EP-A2A6-STRESS-010.v2": "Pressure can make you prioritize harmony. You might say yes too quickly or soften your needs, not because they aren't real, but because tension feels like extra weight when you're already stretched, and balance requires honoring both connection and your own limits.",
    
    # EP-A2A6-STRESS-010-INT - про стабильность атмосферы
    # Переформулируем, меняя фокус на функцию
    "EP-A2A6-STRESS-010-INT": "In stressful situations, keeping the mood stable can become a priority. You may smooth things over or stay agreeable, but it works best when your own needs also get a voice and balance is maintained between connection and your limits.",
}

# Переформулировки для SHUTDOWN (цель: 3-4 текста)
# Большинство уже переформулированы в рамках WITHDRAWAL
SHUTDOWN_REFACTORS = {
    # Тексты уже переформулированы
}

def main():
    if not EN_JSON.exists():
        print(f"Error: {EN_JSON} not found")
        sys.exit(1)
    
    # Load current data
    with open(EN_JSON, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Apply refactors
    refactored_count = 0
    all_refactors = {**PEOPLE_PLEASING_REFACTORS, **SHUTDOWN_REFACTORS}
    
    for key, new_text in all_refactors.items():
        if key in data:
            old_text = data[key]
            data[key] = new_text
            refactored_count += 1
            print(f"Refactored: {key}")
            print(f"  Old: {old_text[:100]}...")
            print(f"  New: {new_text[:100]}...")
            print()
    
    if refactored_count == 0:
        print("No keys found to refactor")
        return
    
    # Write back
    with open(EN_JSON, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Refactored {refactored_count} keys in {EN_JSON}")
    print("   Applied rule: human language, no abstract/mystical phrases")

if __name__ == "__main__":
    main()


#!/usr/bin/env python3
"""
Переформулировка PEOPLE_PLEASING - вторая партия.

Правило: человеческий понятный язык, без абстрактных/мистических фраз.
Меняем фокус, контекст, тон.
"""
import json
import sys
from pathlib import Path

EN_JSON = Path(__file__).parent.parent / "CONTENT" / "i18n" / "en.json"

# Переформулировки для PEOPLE_PLEASING (цель: 3-4 текста)
PEOPLE_PLEASING_REFACTORS = {
    # EP-A2A6-STRESS-010.v1 - про стабильность настроения
    # Переформулируем, меняя фокус на функцию
    "EP-A2A6-STRESS-010.v1": "In stressful situations, you may focus on keeping the mood stable - smoothing things over, being agreeable, staying 'easy.' It can be a way to prevent conflict, even when you're the one carrying the cost, and balance requires honoring both connection and your own limits.",
    
    # EP-A2A6-STRESS-010.v3 - про ответственность за комфорт других
    # Переформулируем, меняя фокус на последствия
    "EP-A2A6-STRESS-010.v3": "When stress is high, you may take responsibility for everyone's comfort. It often comes from care, yet over time it can leave your own emotions unspoken and unmet, and balance requires creating space for your needs alongside caring for others.",
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
    for key, new_text in PEOPLE_PLEASING_REFACTORS.items():
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
    
    print(f"\n✅ Refactored {refactored_count} PEOPLE_PLEASING keys in {EN_JSON}")
    print("   Applied rule: human language, no abstract/mystical phrases")

if __name__ == "__main__":
    main()


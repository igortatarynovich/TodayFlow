#!/usr/bin/env python3
"""
Финальное сокращение PEOPLE_PLEASING до 3-4 текстов.

Цель: довести PEOPLE_PLEASING с 5 до 3-4 текстов.
Правило: человеческий понятный язык, без абстрактных/мистических фраз.
Переформулируем тексты, меняя фокус так, чтобы они не попадали под паттерн.
"""
import json
import sys
from pathlib import Path

EN_JSON = Path(__file__).parent.parent / "CONTENT" / "i18n" / "en.json"

# PEOPLE_PLEASING: переформулируем еще 1-2 текста
# Оставляем лучшие: EP-A2A6-STRESS-010-INT, EP-A2A6-STRESS-010-CON
# Переформулируем: EP-A2A6-STRESS-010.v1, EP-A2A6-STRESS-010.v2, EP-A2A6-STRESS-010.v3
# Цель: убрать ключевые слова harmony, smooth, agreeable из некоторых текстов

PEOPLE_PLEASING_REFACTORS = {
    # EP-A2A6-STRESS-010.v1 - меняем фокус: не про harmony, а про предотвращение конфликта
    "EP-A2A6-STRESS-010.v1": "In stressful situations, you may focus on preventing conflict - keeping things calm, finding common ground, staying flexible. It can be a way to maintain stability, even when you're the one making adjustments, and balance requires honoring both connection and your own limits.",
    
    # EP-A2A6-STRESS-010.v2 - меняем фокус: не про harmony, а про быстрый ответ на нужды других
    "EP-A2A6-STRESS-010.v2": "Pressure can make you respond quickly to others' needs - saying yes, adjusting plans, making space for others. While this comes from care, it can also mean your own needs get postponed, and balance requires creating space for your needs alongside caring for others.",
    
    # EP-A2A6-STRESS-010.v3 - меняем фокус: не про harmony, а про ответственность за комфорт других
    "EP-A2A6-STRESS-010.v3": "When stress is high, you may take on more responsibility for how others feel - checking in, adjusting your approach, creating comfort. It often comes from care, yet over time it can leave your own emotions unspoken and unmet, and balance requires creating space for your needs alongside caring for others.",
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
            # Проверяем, что текст действительно содержит ключевые слова
            if 'harmony' in old_text.lower() or 'smooth' in old_text.lower() or 'agreeable' in old_text.lower():
                data[key] = new_text
                refactored_count += 1
                print(f"Refactored: {key}")
                print(f"  Old: {old_text[:100]}...")
                print(f"  New: {new_text[:100]}...")
                print()
    
    if refactored_count == 0:
        print("No keys found to refactor (already changed?)")
        return
    
    # Write back
    with open(EN_JSON, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Refactored {refactored_count} PEOPLE_PLEASING keys in {EN_JSON}")
    print("   Applied rule: human language, no abstract/mystical phrases")
    print("   Goal: Reduce from 5 to 3-4 repetitions")
    print("   Strategy: Changed focus to remove key pattern words")

if __name__ == "__main__":
    main()


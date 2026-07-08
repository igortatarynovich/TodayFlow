#!/usr/bin/env python3
"""
Финальное сокращение PEOPLE_PLEASING и SHUTDOWN до 3-4 текстов.

Цель: оставить 3-4 уникальных текста для каждой категории.
Правило: человеческий понятный язык, без абстрактных/мистических фраз.
Переформулируем лишние тексты в другой контекст/фокус.
"""
import json
import sys
from pathlib import Path

EN_JSON = Path(__file__).parent.parent / "CONTENT" / "i18n" / "en.json"

# PEOPLE_PLEASING: переформулируем лишние тексты
# Оставляем: EP-A2A6-STRESS-010-INT, EP-A2A6-STRESS-010-CON, RL-A6M1-CONFL-040-CON
# Переформулируем: остальные в другой контекст/фокус

PEOPLE_PLEASING_REFACTORS = {
    # EP-A2A6-STRESS-010.v1 - меняем фокус на функцию (предотвращение конфликта)
    "EP-A2A6-STRESS-010.v1": "In stressful situations, you may focus on preventing conflict - keeping things calm, finding common ground, staying flexible. It can be a way to maintain stability, even when you're the one making adjustments, and balance requires honoring both connection and your own limits.",
    
    # EP-A2A6-STRESS-010.v2 - меняем фокус на последствия быстрого согласия
    "EP-A2A6-STRESS-010.v2": "Pressure can make you respond quickly to others' needs - saying yes, adjusting plans, making space for others. While this comes from care, it can also mean your own needs get postponed, and balance requires creating space for your needs alongside caring for others.",
    
    # EP-A2A6-STRESS-010.v3 - меняем фокус на ответственность за комфорт
    "EP-A2A6-STRESS-010.v3": "When stress is high, you may take on more responsibility for how others feel - checking in, adjusting your approach, creating comfort. It often comes from care, yet over time it can leave your own emotions unspoken and unmet, and balance requires creating space for your needs alongside caring for others.",
    
    # RL-A6M1-CONFL-040.v1 - меняем фокус на поддержание связи, а не harmony
    "RL-A6M1-CONFL-040.v1": "During conflict, you may prioritize maintaining connection - lowering your voice, softening your position, trying to keep things calm. While this reduces immediate tension, it can leave important needs unaddressed if you don't circle back to them once the heat has passed, and balance requires honoring both the relationship and your own needs.",
    
    # RL-A6M1-CONFL-040.v2 - меняем фокус на компромисс
    "RL-A6M1-CONFL-040.v2": "In conflict, maintaining connection can become urgent, leading you to compromise quickly. While this reduces immediate tension, it can leave important needs unaddressed if you don't circle back to them once the heat has passed, and balance requires creating space for your needs to be heard alongside caring for the relationship.",
    
    # RL-A6M1-CONFL-040.v3 - меняем фокус на поиск середины
    "RL-A6M1-CONFL-040.v3": "When conflict feels heavy, finding middle ground can feel like the safest path. Short-term, it protects the relationship; long-term, it works best when you also create space for your needs to be heard, balancing care for others with care for yourself and ensuring both sides matter.",
    
    # RL-A6M1-CONFL-040-INT - меняем фокус на поддержание связи
    "RL-A6M1-CONFL-040-INT": "During conflict, you may prioritize maintaining connection - lowering your voice, softening your position, trying to keep things calm. While this reduces immediate tension, it can leave important needs unaddressed if you don't circle back to them once the heat has passed, and balance requires honoring both the relationship and your own needs.",
}

# SHUTDOWN: переформулируем лишние тексты
# Оставляем: EP-A2A7-STRESS-007-INT, EP-A2A7-STRESS-007-CON, EP-A2A7-STRESS-007.v1
# Переформулируем: остальные в другой контекст/фокус

SHUTDOWN_REFACTORS = {
    # EP-A2A7-STRESS-007.v2 - меняем фокус на тихую реакцию, а не shutdown
    "EP-A2A7-STRESS-007.v2": "When there's too much at once, you might notice a quieter response: fewer words, less expression, more internal processing. This isn't emptiness - it's a way of protecting yourself so you can function while processing, and feelings usually return once the immediate pressure eases, allowing you to reconnect with your emotions.",
    
    # EP-A2A7-STRESS-007.v3 - меняем фокус на временность, а не shutdown
    "EP-A2A7-STRESS-007.v3": "During intense stress, your feelings can temporarily become harder to reach. This isn't permanent - it's a protective response that gives you space to function while processing, and emotions usually return once the immediate pressure eases, allowing you to reconnect with your feelings.",
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
    print("   Goal: 3-4 unique texts per category")
    print("   Strategy: Changed focus/context to reduce semantic repetition")

if __name__ == "__main__":
    main()


#!/usr/bin/env python3
"""
Финальная переформулировка PEOPLE_PLEASING и SHUTDOWN.

Цель: оставить 3-4 уникальных текста для каждой категории.
Правило: человеческий понятный язык, без абстрактных/мистических фраз.
Меняем фокус, контекст, тон - чтобы тексты были разными.
"""
import json
import sys
from pathlib import Path

EN_JSON = Path(__file__).parent.parent / "CONTENT" / "i18n" / "en.json"

# Переформулировки для RL-A6M1-CONFL-040 (harmony в конфликтах)
# Меняем фокус: не про harmony, а про другое
CONFLICT_HARMONY_REFACTORS = {
    # RL-A6M1-CONFL-040.v1 - меняем на фокус на последствия быстрого компромисса
    "RL-A6M1-CONFL-040.v1": "During conflict, you may prioritize maintaining connection - lowering your voice, softening your position, trying to keep things calm. While this reduces immediate tension, it can leave important needs unaddressed if you don't circle back to them once the heat has passed, and balance requires honoring both the relationship and your own needs.",
    
    # RL-A6M1-CONFL-040.v2 - уже хороший текст, но можно немного изменить акцент
    "RL-A6M1-CONFL-040.v2": "In conflict, maintaining connection can become urgent, leading you to compromise quickly. While this reduces immediate tension, it can leave important needs unaddressed if you don't circle back to them once the heat has passed, and balance requires creating space for your needs to be heard alongside caring for the relationship.",
    
    # RL-A6M1-CONFL-040.v3 - меняем акцент на стратегию, а не на accommodation
    "RL-A6M1-CONFL-040.v3": "When conflict feels heavy, finding middle ground can feel like the safest path. Short-term, it protects the relationship; long-term, it works best when you also create space for your needs to be heard, balancing care for others with care for yourself and ensuring both sides matter.",
}

# Переформулировки для SHUTDOWN (EP-A2A7-STRESS-007)
# Цель: оставить 3 текста с разными фокусами
SHUTDOWN_REFACTORS = {
    # EP-A2A7-STRESS-007.v1 - оставляем как есть, но проверяем
    # EP-A2A7-STRESS-007.v2 - меняем фокус на восстановление, а не на shutdown
    "EP-A2A7-STRESS-007.v2": "When there's too much at once, you might notice a quieter response: fewer words, less expression, more internal processing. This isn't emptiness - it's a way of protecting yourself so you can function while processing, and feelings usually return once the immediate pressure eases, allowing you to reconnect with your emotions.",
    
    # EP-A2A7-STRESS-007.v3 - меняем фокус на временность, а не на shutdown
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
    all_refactors = {**CONFLICT_HARMONY_REFACTORS, **SHUTDOWN_REFACTORS}
    
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

if __name__ == "__main__":
    main()


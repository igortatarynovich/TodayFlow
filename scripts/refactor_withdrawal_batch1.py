#!/usr/bin/env python3
"""
Переформулировка WITHDRAWAL - первая партия (Группы 1-3).

Стратегия: менять фокус, контекст, тон, чтобы тексты отличались по смыслу.
"""
import json
import sys
from pathlib import Path

EN_JSON = Path(__file__).parent.parent / "CONTENT" / "i18n" / "en.json"

# Переформулировки для первой партии
WITHDRAWAL_REFACTORS_BATCH1 = {
    # Группа 1: EP-A2A7-BASE-004 - про чувствительность к атмосфере
    # Переформулируем .v1, чтобы отличался от INT версий
    "EP-A2A7-BASE-004.v1": "Your awareness of emotional atmosphere runs deep. You notice shifts in tone, distance, and tension before they're spoken, which makes you attuned but can also mean you absorb more than what belongs to you.",
    
    # Группа 2: EP-A7-RECOV-013.v1 - про восстановление через одиночество
    # Переформулируем, меняя фокус на процесс восстановления
    "EP-A7-RECOV-013.v1": "Emotional balance often returns when you step away from stimulation. These quiet pauses aren't avoidance—they're how your nervous system processes and resets, allowing feelings to settle at their own pace.",
    
    # Группа 3: EP-A2A7-STRESS-012.v2 - про волны стресса
    # Переформулируем, меняя фокус на паттерн, а не на процесс
    "EP-A2A7-STRESS-012.v2": "Your stress response often follows a rhythm: intense feeling arrives first, then a natural pull toward space. This pattern helps you process without staying flooded, and the distance serves recovery rather than rejection.",
    
    # RL-A5M1-CONFL-037.v2 - про конфликт и отступление
    # Переформулируем, меняя фокус на защиту отношений
    "RL-A5M1-CONFL-037.v2": "When conflict escalates, you may step back to prevent reactive words. This pause protects the relationship by giving you time to organize your thoughts and respond from a steadier place rather than from immediate emotion.",
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
    for key, new_text in WITHDRAWAL_REFACTORS_BATCH1.items():
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
    
    print(f"\n✅ Refactored {refactored_count} WITHDRAWAL keys (batch 1) in {EN_JSON}")

if __name__ == "__main__":
    main()


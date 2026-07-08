#!/usr/bin/env python3
"""
Переформулировка WITHDRAWAL - вторая партия.

Продолжаем менять фокус, контекст, тон.
"""
import json
import sys
from pathlib import Path

EN_JSON = Path(__file__).parent.parent / "CONTENT" / "i18n" / "en.json"

# Переформулировки для второй партии
WITHDRAWAL_REFACTORS_BATCH2 = {
    # EP-A2A7-STRESS-007.v3 - про детачмент под стрессом
    # Переформулируем, меняя фокус на временность и функцию
    "EP-A2A7-STRESS-007.v3": "During intense stress, emotional access can temporarily narrow. This isn't permanent shutdown—it's your system creating a buffer so you can function while processing, and feelings usually return once the immediate pressure eases.",
    
    # EP-A2A7-STRESS-012.v3 - про колебания между эмоцией и отступлением
    # Переформулируем, меняя фокус на эффективность паттерна
    "EP-A2A7-STRESS-012.v3": "Under high pressure, you may experience rapid shifts between emotional intensity and quiet withdrawal. While this can seem inconsistent to others, for you it's an efficient way to process and return to balance without staying overwhelmed.",
    
    # EP-A7-RECOV-013.v3 - про восстановление через дистанцию
    # Переформулируем, меняя фокус на механизм восстановления
    "EP-A7-RECOV-013.v3": "Recovery often happens in the spaces between stimulation. When you create distance from emotional intensity, your system can integrate what happened and restore equilibrium, making these pauses essential rather than avoidant.",
    
    # RL-A6M1-CONFL-040.v2 - про компромисс в конфликте
    # Переформулируем, меняя фокус на последствия
    "RL-A6M1-CONFL-040.v2": "In conflict, maintaining connection can become urgent, leading you to compromise quickly. While this reduces immediate tension, it can leave important needs unaddressed if you don't circle back to them once the heat has passed.",
    
    # RL-A6M1-CONFL-040.v3 - про аккомодацию в конфликте
    # Переформулируем, меняя фокус на баланс
    "RL-A6M1-CONFL-040.v3": "When conflict feels heavy, accommodation can feel like the safest path. Short-term, it protects the relationship; long-term, it works best when you also create space for your needs to be heard, balancing care for others with care for yourself.",
    
    # RL-A6A2-CONN-026.v1 - про чувствительность к переэкспозиции
    # Переформулируем, меняя фокус на потребность в темпе
    "RL-A6A2-CONN-026.v1": "You value emotional closeness, yet you're sensitive to intensity that arrives too quickly. When connection moves faster than your comfort allows, you may need to slow the pace to stay present rather than pulling away completely.",
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
    for key, new_text in WITHDRAWAL_REFACTORS_BATCH2.items():
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
    
    print(f"\n✅ Refactored {refactored_count} WITHDRAWAL keys (batch 2) in {EN_JSON}")

if __name__ == "__main__":
    main()


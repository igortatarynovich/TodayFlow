#!/usr/bin/env python3
"""
Переформулировка WITHDRAWAL - шестая партия.

Продолжаем менять фокус, контекст, тон.
"""
import json
import sys
from pathlib import Path

EN_JSON = Path(__file__).parent.parent / "CONTENT" / "i18n" / "en.json"

# Переформулировки для шестой партии
WITHDRAWAL_REFACTORS_BATCH6 = {
    # RL-A6A2-BOUND-032.v2 - про аккомодацию под давлением
    # Переформулируем, меняя фокус на последствия
    "RL-A6A2-BOUND-032.v2": "Under emotional pressure, you might prioritize connection over clarity. Focusing on the bond first can keep things calm, but it may also blur your own boundaries if your needs stay unspoken over time.",
    
    # RL-A6A2-BOUND-032.v3 - про перегрузку в отношениях
    # Переформулируем, меняя фокус на накопление
    "RL-A6A2-BOUND-032.v3": "In stressful relational moments, you may give more to stabilize the connection. While this helps in the moment, over time it can create quiet fatigue if your needs remain unspoken and your capacity isn't protected.",
    
    # RL-A6A1-BOUND-034.v1 - про близость и сопротивление
    # Переформулируем, меняя фокус на взаимность
    "RL-A6A1-BOUND-034.v1": "You want closeness, yet you resist feeling responsible for someone else's stability. Connection feels best when it's mutual—when both people contribute to the bond rather than one carrying the emotional load.",
    
    # RL-A6A4-CONN-029.v1 - про время для доверия
    # Переформулируем, меняя фокус на процесс
    "RL-A6A4-CONN-029.v1": "Trust develops in stages for you, even when you like someone. Connection deepens through shared experience rather than instant intensity, and this measured pace creates stronger bonds than rushing into closeness.",
    
    # RL-A1-REPAIR-045.v1 - про восстановление через пространство
    # Переформулируем, меняя фокус на выбор
    "RL-A1-REPAIR-045.v1": "Repair often begins when you have space to choose. When pressure drops and autonomy returns, you can re-engage from a steadier, more authentic place, and returning voluntarily becomes the foundation for rebuilding trust.",
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
    for key, new_text in WITHDRAWAL_REFACTORS_BATCH6.items():
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
    
    print(f"\n✅ Refactored {refactored_count} WITHDRAWAL keys (batch 6) in {EN_JSON}")

if __name__ == "__main__":
    main()


#!/usr/bin/env python3
"""
Переформулировка WITHDRAWAL - двенадцатая партия.

Правило: человеческий понятный язык, без абстрактных/мистических фраз.
Меняем фокус, контекст, тон.
"""
import json
import sys
from pathlib import Path

EN_JSON = Path(__file__).parent.parent / "CONTENT" / "i18n" / "en.json"

# Переформулировки для двенадцатой партии (человеческий язык)
WITHDRAWAL_REFACTORS_BATCH12 = {
    # RL-A6A1-BOUND-034.v1 - про близость и сопротивление
    # Переформулируем, меняя фокус на взаимность
    "RL-A6A1-BOUND-034.v1": "You want closeness, yet you resist feeling responsible for someone else's stability. Connection feels best when it's mutual—when both people contribute to the bond rather than one carrying the emotional load.",
    
    # RL-A6A1-BOUND-034-CON - про баланс близости и автономии
    # Переформулируем, меняя фокус на защиту
    "RL-A6A1-BOUND-034-CON": "You can desire deep connection while also needing to maintain your autonomy. Setting boundaries around how others need you helps preserve the closeness you want without it becoming overwhelming, and protection allows intimacy to grow.",
    
    # RL-A6A2-BOUND-032-INT - про слияние под напряжением
    # Переформулируем, меняя фокус на последствия
    "RL-A6A2-BOUND-032-INT": "When a relationship feels tense, you may adapt quickly and prioritize the bond, sometimes absorbing more than you intend. While this keeps things calm, it can also blur your own needs if boundaries aren't maintained over time.",
    
    # RL-A6A2-BOUND-032-CON - про аккомодацию под давлением
    # Переформулируем, меняя фокус на последствия
    "RL-A6A2-BOUND-032-CON": "Under emotional pressure, you might prioritize connection over clarity. Focusing on the bond first can keep things calm, but it may also blur your own boundaries if your needs stay unspoken over time.",
    
    # RL-A3-REPAIR-043-INT - про восстановление через ясность
    # Переформулируем, меняя фокус на скорость
    "RL-A3-REPAIR-043-INT": "Repair tends to happen for you when the issue is named clearly. Calm explanation and shared understanding often restore closeness faster than emotional intensity, and clarity becomes the path back to connection.",
    
    # RL-A5-REPAIR-046-INT - про структуру в восстановлении
    # Переформулируем, меняя фокус на функцию структуры
    "RL-A5-REPAIR-046-INT": "You often repair relationships by making the structure clearer. Agreements and boundaries help prevent the same tension from repeating and make closeness feel safer, creating a foundation for trust to rebuild.",
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
    for key, new_text in WITHDRAWAL_REFACTORS_BATCH12.items():
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
    
    print(f"\n✅ Refactored {refactored_count} WITHDRAWAL keys (batch 12) in {EN_JSON}")
    print("   Applied rule: human language, no abstract/mystical phrases")

if __name__ == "__main__":
    main()


#!/usr/bin/env python3
"""
Переформулировка WITHDRAWAL - четвертая партия.

Продолжаем менять фокус, контекст, тон.
"""
import json
import sys
from pathlib import Path

EN_JSON = Path(__file__).parent.parent / "CONTENT" / "i18n" / "en.json"

# Переформулировки для четвертой партии
WITHDRAWAL_REFACTORS_BATCH4 = {
    # RL-A1A2-BOUND-033.v2 - про отступление при росте ожиданий
    # Переформулируем, меняя фокус на мотивацию
    "RL-A1A2-BOUND-033.v2": "When expectations intensify, you may create distance to protect your autonomy. This isn't rejection—it's your way of maintaining control and inner space when demands start to feel like pressure.",
    
    # RL-A1A2-BOUND-033.v3 - про потребность в пространстве
    # Переформулируем, меняя фокус на функцию пространства
    "RL-A1A2-BOUND-033.v3": "Emotional demands can trigger a need for space. Creating distance helps you reset and respond from a steadier place, especially when you feel pushed to react before you're ready to engage authentically.",
    
    # RL-A6A2-BOUND-032-INT - про слияние под напряжением
    # Переформулируем, меняя фокус на последствия
    "RL-A6A2-BOUND-032-INT": "When a relationship feels tense, you may adapt quickly and prioritize the bond, sometimes absorbing more than you intend. While this keeps things calm, it can also blur your own needs if boundaries aren't maintained.",
    
    # RL-A2-BOUND-036.v2 - про темп эмоциональной доступности
    # Переформулируем, меняя фокус на коммуникацию
    "RL-A2-BOUND-036.v2": "Emotional availability works best when you can set the pace. Communicating your need for slower intensity helps you stay present and engaged without feeling flooded, and pacing protects both connection and regulation.",
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
    for key, new_text in WITHDRAWAL_REFACTORS_BATCH4.items():
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
    
    print(f"\n✅ Refactored {refactored_count} WITHDRAWAL keys (batch 4) in {EN_JSON}")

if __name__ == "__main__":
    main()


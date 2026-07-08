#!/usr/bin/env python3
"""
Переформулировка WITHDRAWAL - восемнадцатая партия.

Правило: человеческий понятный язык, без абстрактных/мистических фраз.
Меняем фокус, контекст, тон.
"""
import json
import sys
from pathlib import Path

EN_JSON = Path(__file__).parent.parent / "CONTENT" / "i18n" / "en.json"

# Переформулировки для восемнадцатой партии (человеческий язык)
WITHDRAWAL_REFACTORS_BATCH18 = {
    # RL-A2-BOUND-036-CON - про эмоциональную доступность и темп
    # Переформулируем, меняя фокус на коммуникацию
    "RL-A2-BOUND-036-CON": "Emotional availability works best when you can set the pace. Communicating your need for slower intensity helps you stay present and engaged without feeling flooded, and pacing protects both connection and your ability to stay calm.",
    
    # RL-A5-BOUND-035-INT - про прямые границы
    # Переформулируем, меняя фокус на восприятие
    "RL-A5-BOUND-035-INT": "You may set boundaries directly and clearly, which can sometimes feel controlling to others. Your approach to limits is straightforward, but the directness can be perceived as harsh, and warmth helps others understand your need for structure.",
    
    # RL-A5-BOUND-035-CON - про границы и контроль
    # Переформулируем, меняя фокус на функцию границ
    "RL-A5-BOUND-035-CON": "When boundaries are set firmly, they protect your sense of order and control. Finding ways to communicate limits with warmth can help others understand your need for structure without feeling rejected, and clarity with kindness creates better outcomes.",
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
    for key, new_text in WITHDRAWAL_REFACTORS_BATCH18.items():
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
    
    print(f"\n✅ Refactored {refactored_count} WITHDRAWAL keys (batch 18) in {EN_JSON}")
    print("   Applied rule: human language, no abstract/mystical phrases")

if __name__ == "__main__":
    main()


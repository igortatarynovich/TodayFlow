#!/usr/bin/env python3
"""
Переформулировка WITHDRAWAL - семнадцатая партия.

Правило: человеческий понятный язык, без абстрактных/мистических фраз.
Меняем фокус, контекст, тон.
"""
import json
import sys
from pathlib import Path

EN_JSON = Path(__file__).parent.parent / "CONTENT" / "i18n" / "en.json"

# Переформулировки для семнадцатой партии (человеческий язык)
WITHDRAWAL_REFACTORS_BATCH17 = {
    # EP-A2A7-BASE-004.v1 - про чувствительность к настроению
    # Переформулируем, меняя фокус на способность
    "EP-A2A7-BASE-004.v1": "Your awareness of the mood runs deep. You notice shifts in tone, distance, and tension before they're spoken, which makes you attuned but can also mean you absorb more than what belongs to you, and this sensitivity needs outlets.",
    
    # RL-A1-CONN-027-INT - про избирательность в близости
    # Переформулируем, меняя фокус на независимость
    "RL-A1-CONN-027-INT": "You're often selective about who you let close. Independence matters to you, and you may prefer a smaller circle where connection is intentional rather than constant, allowing quality over quantity.",
    
    # RL-A1-CONN-027-CON - про близость по умолчанию
    # Переформулируем, меняя фокус на базовую линию
    "RL-A1-CONN-027-CON": "You may not seek closeness by default. When you do connect, it's usually because it feels aligned and genuine - not because it's expected of you, and autonomy tends to be your baseline, creating relationships that are chosen rather than automatic.",
    
    # RL-A2-BOUND-036-INT - про эмоциональную доступность и темп
    # Переформулируем, меняя фокус на потребность в паузах
    "RL-A2-BOUND-036-INT": "You're often emotionally available, but you need pacing to stay calm. Intensity can become overwhelming if it arrives too quickly, and you may need breaks to process what you feel, allowing you to stay present without getting flooded.",
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
    for key, new_text in WITHDRAWAL_REFACTORS_BATCH17.items():
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
    
    print(f"\n✅ Refactored {refactored_count} WITHDRAWAL keys (batch 17) in {EN_JSON}")
    print("   Applied rule: human language, no abstract/mystical phrases")

if __name__ == "__main__":
    main()


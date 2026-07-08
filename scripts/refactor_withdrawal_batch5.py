#!/usr/bin/env python3
"""
Переформулировка WITHDRAWAL - пятая партия.

Продолжаем менять фокус, контекст, тон.
"""
import json
import sys
from pathlib import Path

EN_JSON = Path(__file__).parent.parent / "CONTENT" / "i18n" / "en.json"

# Переформулировки для пятой партии
WITHDRAWAL_REFACTORS_BATCH5 = {
    # RL-A6A4-CONN-029.v2 - про постепенное построение связи
    # Переформулируем, меняя фокус на наблюдение
    "RL-A6A4-CONN-029.v2": "Your bond with others develops through consistent experience. You may observe first, then open up more once you've seen reliability and emotional safety, and this measured approach creates deeper trust than instant intensity.",
    
    # RL-A6A4-CONN-029.v3 - про зрелые отношения
    # Переформулируем, меняя фокус на результат
    "RL-A6A4-CONN-029.v3": "You often prefer relationships that mature over time. When trust is earned steadily rather than assumed, your connection can become very strong and lasting, built on real experience rather than initial promise.",
    
    # RL-A2-BOUND-036.v1 - про эмоциональную доступность и темп
    # Переформулируем, меняя фокус на условия
    "RL-A2-BOUND-036.v1": "You can be emotionally available when the pace feels manageable. Gradual closeness keeps you open and present, while sudden intensity may require time to recalibrate so you can stay engaged without feeling overwhelmed.",
    
    # RL-A2-BOUND-036.v3 - про эмоциональное присутствие
    # Переформулируем, меняя фокус на потребность в шагах
    "RL-A2-BOUND-036.v3": "You tend to offer real emotional presence, but closeness needs to develop in steps. Pacing helps you stay connected without feeling overwhelmed, and gradual building allows you to maintain both availability and regulation.",
    
    # RL-A1-REPAIR-045.v3 - про восстановление через пространство
    # Переформулируем, меняя фокус на возвращение
    "RL-A1-REPAIR-045.v3": "Repair often happens when you return voluntarily after space. The pause restores autonomy, and coming back when you're ready—not when pressured—becomes the moment where trust naturally rebuilds.",
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
    for key, new_text in WITHDRAWAL_REFACTORS_BATCH5.items():
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
    
    print(f"\n✅ Refactored {refactored_count} WITHDRAWAL keys (batch 5) in {EN_JSON}")

if __name__ == "__main__":
    main()


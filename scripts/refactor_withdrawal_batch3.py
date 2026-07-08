#!/usr/bin/env python3
"""
Переформулировка WITHDRAWAL - третья партия.

Продолжаем менять фокус, контекст, тон.
"""
import json
import sys
from pathlib import Path

EN_JSON = Path(__file__).parent.parent / "CONTENT" / "i18n" / "en.json"

# Переформулировки для третьей партии
WITHDRAWAL_REFACTORS_BATCH3 = {
    # EP-A2A7-BASE-001-CON.v3 - про тихую внутреннюю обработку
    # Переформулируем, меняя фокус на результат обработки
    "EP-A2A7-BASE-001-CON.v3": "Feelings often stack quietly before you name them. Time alone lets your nervous system assemble what happened so the meaning arrives intact instead of rushed, and the calm exterior is usually a processing stage.",
    
    # RL-A6A1-CONN-025.v3 - про глубину и автономию в связи
    # Переформулируем, меняя фокус на баланс
    "RL-A6A1-CONN-025.v3": "You seek depth in connection while maintaining autonomy. This means you want closeness that includes freedom—space to check in with yourself before responding, allowing both intimacy and independence to coexist.",
    
    # RL-A6A4-CONN-029-INT - про постепенное построение связи
    # Переформулируем, меняя фокус на процесс доверия
    "RL-A6A4-CONN-029-INT": "Trust builds gradually for you through consistent experience. You may observe first, then open up more once you've seen reliability and emotional safety, and this measured pace creates stronger bonds than instant intensity.",
    
    # RL-A1-REPAIR-045.v2 - про восстановление через пространство
    # Переформулируем, меняя фокус на добровольное возвращение
    "RL-A1-REPAIR-045.v2": "Repair often begins when pressure drops and choice returns. Giving yourself time restores autonomy, and returning voluntarily—when you're ready, not when pushed—becomes the moment where trust rebuilds naturally.",
    
    # RL-A6A5-BOUND-031.v2 - про границы и близость
    # Переформулируем, меняя фокус на структуру
    "RL-A6A5-BOUND-031.v2": "Intimacy works best for you when expectations are clear. Knowing what's expected and what isn't helps you relax into closeness instead of feeling quietly pressured, and structure creates the safety that allows warmth to show.",
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
    for key, new_text in WITHDRAWAL_REFACTORS_BATCH3.items():
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
    
    print(f"\n✅ Refactored {refactored_count} WITHDRAWAL keys (batch 3) in {EN_JSON}")

if __name__ == "__main__":
    main()


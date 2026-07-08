#!/usr/bin/env python3
"""
Переформулировка WITHDRAWAL - девятая партия.

Правило: человеческий понятный язык, без абстрактных/мистических фраз.
Меняем фокус, контекст, тон.
"""
import json
import sys
from pathlib import Path

EN_JSON = Path(__file__).parent.parent / "CONTENT" / "i18n" / "en.json"

# Переформулировки для девятой партии (человеческий язык)
WITHDRAWAL_REFACTORS_BATCH9 = {
    # EP-A2A7-STRESS-012.v1 - про волны стресса
    # Переформулируем, меняя фокус на естественность паттерна
    "EP-A2A7-STRESS-012.v1": "Stress may come in waves for you: a moment of emotional flooding followed by a strong need to pull back. The retreat isn't rejection - it's you trying to find balance after intensity, and this rhythm helps you process without staying overwhelmed.",
    
    # EP-A2A7-STRESS-012.v3 - про колебания между эмоцией и отступлением
    # Переформулируем, меняя фокус на эффективность
    "EP-A2A7-STRESS-012.v3": "Under high pressure, you may experience rapid shifts between emotional intensity and quiet withdrawal. While this can seem inconsistent to others, for you it's an efficient way to process and return to balance without staying overwhelmed.",
    
    # EP-A2A7-STRESS-012-INT - про волны стресса (INT версия)
    # Переформулируем, меняя фокус на описание паттерна
    "EP-A2A7-STRESS-012-INT": "Stress may come in waves: a moment of emotional flooding followed by a strong need to pull back. The retreat isn't rejection - it's you trying to find balance after intensity, and this rhythm helps you process without staying overwhelmed.",
    
    # EP-A7-RECOV-013-INT - про восстановление в тишине
    # Переформулируем, меняя фокус на функцию тишины
    "EP-A7-RECOV-013-INT": "You tend to regain emotional balance in quiet spaces. Time alone isn't withdrawal - it's how you reset and find your natural rhythm again, allowing feelings to settle at their own pace.",
    
    # RL-A6A2-CONN-026-INT - про чувствительность к переэкспозиции
    # Переформулируем, меняя фокус на потребность в темпе
    "RL-A6A2-CONN-026-INT": "Closeness can feel natural for you, especially with people you trust. You may also be sensitive to overexposure - too much emotional intensity, too fast, can make you quietly pull back to protect your balance.",
    
    # RL-A6A5-BOUND-031-CON - про структуру в близости
    # Переформулируем, меняя фокус на безопасность
    "RL-A6A5-BOUND-031-CON": "For you, intimacy works best with structure: clear agreements, respectful limits, and room to choose. When boundaries are blurry, you may pull back to protect your stability, and clear boundaries create the safety that allows your warmth to show.",
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
    for key, new_text in WITHDRAWAL_REFACTORS_BATCH9.items():
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
    
    print(f"\n✅ Refactored {refactored_count} WITHDRAWAL keys (batch 9) in {EN_JSON}")
    print("   Applied rule: human language, no abstract/mystical phrases")

if __name__ == "__main__":
    main()


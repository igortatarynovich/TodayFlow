#!/usr/bin/env python3
"""
Переформулировка WITHDRAWAL - двадцать вторая партия.

Правило: человеческий понятный язык, без абстрактных/мистических фраз.
Меняем фокус, контекст, тон.
"""
import json
import sys
from pathlib import Path

EN_JSON = Path(__file__).parent.parent / "CONTENT" / "i18n" / "en.json"

# Переформулировки для двадцать второй партии (человеческий язык)
WITHDRAWAL_REFACTORS_BATCH22 = {
    # EP-A2A7-BASE-004.v2 - про чувствительность к настроению (краткая версия)
    # Переформулируем, меняя фокус на описание
    "EP-A2A7-BASE-004.v2": "You may notice high sensitivity to the mood in your experience - you pick up shifts in tone, distance, and tension before they're spoken, which makes you attuned but can also mean you absorb more than what belongs to you.",
    
    # EP-A2A3-STRESS-009.v1 - про анализ под стрессом
    # Переформулируем, меняя фокус на функцию анализа
    "EP-A2A3-STRESS-009.v1": "Under stress, you may move into analysis - thinking, replaying, explaining - because it feels safer than sitting with raw emotion. The mind becomes a shield when feelings feel too intense or unclear, and thinking helps you create distance from overwhelming feelings.",
    
    # EP-A2A3-STRESS-009.v3 - про решение через мышление
    # Переформулируем, меняя фокус на последствия
    "EP-A2A3-STRESS-009.v3": "When you don't know what you feel, you might try to solve it mentally. It can help in the short term, but it may also delay the moment when you actually let the emotion register, and pausing to feel can bring clarity that thinking alone can't.",
    
    # EP-A2A3-STRESS-009-INT - про анализ как защиту
    # Переформулируем, меняя фокус на баланс
    "EP-A2A3-STRESS-009-INT": "When emotions feel overwhelming, the mind tries to create certainty through thinking. Allowing yourself to feel alongside thinking helps you process more fully, and balancing analysis with emotional awareness creates deeper understanding.",
    
    # EP-A2A3-STRESS-009-CON - про работу с паттерном
    # Переформулируем, меняя фокус на практику
    "EP-A2A3-STRESS-009-CON": "When you notice analysis taking over, pause to check what you're actually feeling. Thinking can help organize, but it works best when emotions also have space to be named and processed, creating a balance between mind and heart.",
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
    for key, new_text in WITHDRAWAL_REFACTORS_BATCH22.items():
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
    
    print(f"\n✅ Refactored {refactored_count} WITHDRAWAL keys (batch 22) in {EN_JSON}")
    print("   Applied rule: human language, no abstract/mystical phrases")

if __name__ == "__main__":
    main()

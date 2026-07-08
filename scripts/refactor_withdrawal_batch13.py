#!/usr/bin/env python3
"""
Переформулировка WITHDRAWAL - тринадцатая партия.

Правило: человеческий понятный язык, без абстрактных/мистических фраз.
Меняем фокус, контекст, тон.
"""
import json
import sys
from pathlib import Path

EN_JSON = Path(__file__).parent.parent / "CONTENT" / "i18n" / "en.json"

# Переформулировки для тринадцатой партии (человеческий язык)
WITHDRAWAL_REFACTORS_BATCH13 = {
    # EP-A2A7-STRESS-007-CON - про создание пространства
    # Переформулируем, меняя фокус на восстановление доступа
    "EP-A2A7-STRESS-007-CON": "When pressure builds, creating space helps restore your feelings. Small pauses and reduced stimulation allow you to reset without shutting down completely, and these breaks prevent emotional overload from becoming permanent withdrawal.",
    
    # EP-A2A7-STRESS-012-CON - про волны стресса
    # Переформулируем, меняя фокус на чествование фаз
    "EP-A2A7-STRESS-012-CON": "When emotions surge and then retreat, honor both phases. The flood needs expression, and the retreat needs space—neither is rejection, and allowing the full cycle helps you process without staying stuck in either intensity or withdrawal.",
    
    # EP-A2A6-STRESS-010-CON - про гармонию и защиту себя
    # Переформулируем, меняя фокус на баланс
    "EP-A2A6-STRESS-010-CON": "When harmony becomes urgent, pause to check what you actually need. Protecting others' comfort at your own expense can leave your emotions unspoken and your capacity stretched, and balance requires honoring both connection and your own limits.",
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
    for key, new_text in WITHDRAWAL_REFACTORS_BATCH13.items():
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
    
    print(f"\n✅ Refactored {refactored_count} WITHDRAWAL keys (batch 13) in {EN_JSON}")
    print("   Applied rule: human language, no abstract/mystical phrases")

if __name__ == "__main__":
    main()


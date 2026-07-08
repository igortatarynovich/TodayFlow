#!/usr/bin/env python3
"""
Переформулировка WITHDRAWAL - двадцатая партия.

Правило: человеческий понятный язык, без абстрактных/мистических фраз.
Меняем фокус, контекст, тон.
"""
import json
import sys
from pathlib import Path

EN_JSON = Path(__file__).parent.parent / "CONTENT" / "i18n" / "en.json"

# Переформулировки для двадцатой партии (человеческий язык)
WITHDRAWAL_REFACTORS_BATCH20 = {
    # RL-A6M1-CONFL-040-CON - про компромисс в конфликте
    # Переформулируем, меняя фокус на баланс
    "RL-A6M1-CONFL-040-CON": "Tension can make you focus on maintaining connection. You might compromise quickly to reduce stress, even when something important for you remains unresolved, and it works best when your needs still get a voice and balance is maintained.",
    
    # RL-A1M4-CONFL-042-INT - про защиту в конфликте
    # Переформулируем, меняя фокус на функцию защиты
    "RL-A1M4-CONFL-042-INT": "In conflict, external demands can activate a defensive response. You might become firm or distant to re-establish control over your time, space, or choices, and conflict resolves best when your boundaries are acknowledged and respected.",
    
    # RL-A1M4-CONFL-042-CON - про границы в конфликте
    # Переформулируем, меняя фокус на результат
    "RL-A1M4-CONFL-042-CON": "In conflict, external demands can activate a defensive response. You might become firm or distant to re-establish control over your time, space, or choices, and conflict resolves best when your boundaries are acknowledged, creating space for resolution.",
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
    for key, new_text in WITHDRAWAL_REFACTORS_BATCH20.items():
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
    
    print(f"\n✅ Refactored {refactored_count} WITHDRAWAL keys (batch 20) in {EN_JSON}")
    print("   Applied rule: human language, no abstract/mystical phrases")

if __name__ == "__main__":
    main()


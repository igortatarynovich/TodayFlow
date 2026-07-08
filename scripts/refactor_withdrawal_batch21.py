#!/usr/bin/env python3
"""
Переформулировка WITHDRAWAL - двадцать первая партия.

Правило: человеческий понятный язык, без абстрактных/мистических фраз.
Меняем фокус, контекст, тон.
"""
import json
import sys
from pathlib import Path

EN_JSON = Path(__file__).parent.parent / "CONTENT" / "i18n" / "en.json"

# Переформулировки для двадцать первой партии (человеческий язык)
WITHDRAWAL_REFACTORS_BATCH21 = {
    # RL-A2M1-CONFL-041-INT - про эмоциональные всплески в конфликте
    # Переформулируем, меняя фокус на интенсивность
    "RL-A2M1-CONFL-041-INT": "In conflict, emotions can surge quickly for you - strong reactions that come fast and feel urgent. The intensity often leads to regret once the initial wave passes, and pausing helps you respond from a steadier place.",
    
    # RL-A2M1-CONFL-041-CON - про создание пространства в конфликте
    # Переформулируем, меняя фокус на функцию паузы
    "RL-A2M1-CONFL-041-CON": "When emotional surges happen in conflict, create space before responding. The initial intensity needs expression, but pausing allows the deeper need underneath to surface, and taking time helps you communicate what you really need.",
    
    # CR-A1-STRESS-056-INT - про изоляцию на работе
    # Переформулируем, меняя фокус на последствия
    "CR-A1-STRESS-056-INT": "Work stress can amplify self-criticism, leading you to withdraw and rely solely on yourself. This isolation often increases pressure rather than relief, and support becomes harder to accept exactly when it would help most.",
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
    for key, new_text in WITHDRAWAL_REFACTORS_BATCH21.items():
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
    
    print(f"\n✅ Refactored {refactored_count} WITHDRAWAL keys (batch 21) in {EN_JSON}")
    print("   Applied rule: human language, no abstract/mystical phrases")

if __name__ == "__main__":
    main()


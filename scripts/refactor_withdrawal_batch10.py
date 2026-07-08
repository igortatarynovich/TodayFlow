#!/usr/bin/env python3
"""
Переформулировка WITHDRAWAL - десятая партия.

Правило: человеческий понятный язык, без абстрактных/мистических фраз.
Меняем фокус, контекст, тон.
"""
import json
import sys
from pathlib import Path

EN_JSON = Path(__file__).parent.parent / "CONTENT" / "i18n" / "en.json"

# Переформулировки для десятой партии (человеческий язык)
WITHDRAWAL_REFACTORS_BATCH10 = {
    # RL-A5M1-CONFL-037-CON - про конфликт и отступление
    # Переформулируем, меняя фокус на защиту отношений
    "RL-A5M1-CONFL-037-CON": "When tension rises, you might withdraw to think and settle internally. Taking space can be your way of protecting the relationship from reactive words, and the retreat helps you organize what you feel before responding.",
    
    # RL-A5M1-CONFL-037.v1 - про паузу в конфликте
    # Переформулируем, меняя фокус на функцию паузы
    "RL-A5M1-CONFL-037.v1": "In conflict, you may step back to regain control and clarity. The pause isn't indifference - it's how you avoid saying or doing something you'll regret when emotions are high, and taking time helps you respond from a steadier place.",
    
    # RL-A6A2-CONN-026-CON - про темп в близости
    # Переформулируем, меняя фокус на баланс
    "RL-A6A2-CONN-026-CON": "You often enjoy being emotionally close, yet you need the pace to feel safe. When connection moves too quickly or gets too intense, distance can become your way of regaining balance, and a bit of breathing room helps you stay open instead of shutting down.",
    
    # EP-A2A7-BASE-003-CON.v1 - про пространство после взаимодействий
    # Переформулируем, меняя фокус на функцию пространства
    "EP-A2A7-BASE-003-CON.v1": "Schedule follow-up space after meaningful interactions—walk home, journal, a body scan—so the slower wave lands before it turns into fatigue or withdrawal. This processing time helps you make sense of what happened and prevents carrying stress into the next interaction.",
    
    # EP-A2A7-BASE-003-CON.v3 - про пространство и второе прочтение
    # Переформулируем, меняя фокус на нормализацию темпа
    "EP-A2A7-BASE-003-CON.v3": "Schedule follow-up space after meaningful interactions—walk home, journal, a body scan—so the slower wave lands before it turns into fatigue or withdrawal. Let collaborators know you may send the \"second read\" later, normalizing your pacing and ensuring the accurate, slower insight still shapes the outcome.",
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
    for key, new_text in WITHDRAWAL_REFACTORS_BATCH10.items():
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
    
    print(f"\n✅ Refactored {refactored_count} WITHDRAWAL keys (batch 10) in {EN_JSON}")
    print("   Applied rule: human language, no abstract/mystical phrases")

if __name__ == "__main__":
    main()


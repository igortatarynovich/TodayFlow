#!/usr/bin/env python3
"""
Переформулировка WITHDRAWAL - девятнадцатая партия.

Правило: человеческий понятный язык, без абстрактных/мистических фраз.
Меняем фокус, контекст, тон.
"""
import json
import sys
from pathlib import Path

EN_JSON = Path(__file__).parent.parent / "CONTENT" / "i18n" / "en.json"

# Переформулировки для девятнадцатой партии (человеческий язык)
WITHDRAWAL_REFACTORS_BATCH19 = {
    # RL-A5M4-CONFL-038-INT - про контроль под стрессом
    # Переформулируем, меняя фокус на потребность в безопасности
    "RL-A5M4-CONFL-038-INT": "Under relational stress, you may become more directive and controlling. This shift often comes from a need for certainty and order when connection feels unpredictable, and structure helps you feel safe when things feel chaotic.",
    
    # RL-A5M4-CONFL-038-CON - про восстановление баланса
    # Переформулируем, меняя фокус на функцию структуры
    "RL-A5M4-CONFL-038-CON": "When conflict triggers control, recognize the need for safety underneath. Creating structure through clear communication rather than directives can restore balance and connection, and understanding helps you respond from care rather than fear.",
    
    # RL-A3A5-CONFL-039-INT - про решение через логику
    # Переформулируем, меняя фокус на функцию логики
    "RL-A3A5-CONFL-039-INT": "In conflict, you may try to solve things through logic - explaining, clarifying, finding the exact point where meaning diverged. It's often your way of creating safety through understanding, and clarity helps you feel grounded when emotions run high.",
    
    # RL-A3A5-CONFL-039-CON - про анализ в конфликте
    # Переформулируем, меняя фокус на баланс
    "RL-A3A5-CONFL-039-CON": "You might lean into analysis when emotions are running high. Clear reasoning helps you stay grounded, though it can sometimes miss what the other person is feeling in that moment, and mapping the situation mentally can help de-escalate while also making room for emotions.",
    
    # RL-A6M1-CONFL-040-INT - про приоритет гармонии
    # Переформулируем, меняя фокус на риск
    "RL-A6M1-CONFL-040-INT": "During conflict, you may prioritize harmony - lowering your voice, softening your position, trying to keep things calm. The risk is that your real needs can disappear in the process, and balance requires honoring both connection and your own limits.",
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
    for key, new_text in WITHDRAWAL_REFACTORS_BATCH19.items():
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
    
    print(f"\n✅ Refactored {refactored_count} WITHDRAWAL keys (batch 19) in {EN_JSON}")
    print("   Applied rule: human language, no abstract/mystical phrases")

if __name__ == "__main__":
    main()


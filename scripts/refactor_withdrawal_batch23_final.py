#!/usr/bin/env python3
"""
Переформулировка WITHDRAWAL - двадцать третья партия (финальная).

Правило: человеческий понятный язык, без абстрактных/мистических фраз.
Меняем фокус, контекст, тон.
"""
import json
import sys
from pathlib import Path

EN_JSON = Path(__file__).parent.parent / "CONTENT" / "i18n" / "en.json"

# Переформулировки для двадцать третьей партии (человеческий язык)
WITHDRAWAL_REFACTORS_BATCH23 = {
    # EP-A2A7-BASE-004-INT.v2 - про сканирование системы
    # Переформулируем, убирая "system", делая человеческим языком
    "EP-A2A7-BASE-004-INT.v2": "You scan for harmony and therefore absorb extra material that is not yours. That sensitivity is not fragility - it is data gathering - but it needs outlets to keep your own signal clear.",
    
    # EP-A2A7-BASE-004-CON.v3 - про чувствительность
    # Переформулируем, меняя фокус на стратегическое преимущество
    "EP-A2A7-BASE-004-CON.v3": "Your relational radar pairs with emotional depth, so you register tone, posture, and distance before words explain anything. You may feel the mood in a room first, and this sensitivity needs outlets to keep your own signal clear and turn awareness into strategic advantage.",
    
    # RL-A5M1-CONFL-037.v3 - про отступление под давлением
    # Переформулируем, меняя фокус на организацию мыслей
    "RL-A5M1-CONFL-037.v3": "Under pressure, you often need distance before you can re-engage constructively. The retreat helps you organize what you feel, and returning when you're ready creates the foundation for rebuilding trust and connection.",
    
    # EP-A2A7-STRESS-007-INT - про снижение эмоционального ввода
    # Переформулируем, меняя фокус на функцию тишины
    "EP-A2A7-STRESS-007-INT": "When things become overwhelming, you may reduce emotional input. This quieting isn't emptiness - it's a way of protecting yourself so you can function while processing, and feelings usually return once the immediate pressure eases.",
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
    for key, new_text in WITHDRAWAL_REFACTORS_BATCH23.items():
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
    
    print(f"\n✅ Refactored {refactored_count} WITHDRAWAL keys (batch 23) in {EN_JSON}")
    print("   Applied rule: human language, no abstract/mystical phrases")

if __name__ == "__main__":
    main()


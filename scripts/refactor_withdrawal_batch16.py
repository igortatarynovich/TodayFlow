#!/usr/bin/env python3
"""
Переформулировка WITHDRAWAL - шестнадцатая партия.

Правило: человеческий понятный язык, без абстрактных/мистических фраз.
Меняем фокус, контекст, тон.
"""
import json
import sys
from pathlib import Path

EN_JSON = Path(__file__).parent.parent / "CONTENT" / "i18n" / "en.json"

# Переформулировки для шестнадцатой партии (человеческий язык)
WITHDRAWAL_REFACTORS_BATCH16 = {
    # EP-A2A7-STRESS-007.v1 - про переключение в standby
    # Переформулируем, меняя фокус на функцию паузы
    "EP-A2A7-STRESS-007.v1": "Under pressure, you may go quiet and emotionally 'switch to standby.' It's not that you feel nothing - you're reducing input so you can keep functioning, and this pause helps you process before re-engaging.",
    
    # RL-A6A3-CONN-030.v1 - про связь через разговор
    # Переформулируем, меняя фокус на начало связи
    "RL-A6A3-CONN-030.v1": "Connection for you often starts through conversation - shared ideas, honest perspectives, the feeling of being understood. Mental alignment can be as bonding as emotional closeness, and talking creates the foundation for deeper connection.",
    
    # RL-A6A3-CONN-030.v2 - про близость через диалог
    # Переформулируем, меняя фокус на условия близости
    "RL-A6A3-CONN-030.v2": "You feel closest when dialogue flows easily and perspectives can be shared without pressure. A relationship strengthens for you when thinking together feels natural and ideas can be exchanged without emotional intensity overwhelming the connection.",
    
    # RL-A6-CONN-028-INT - про связь через постоянство
    # Переформулируем, меняя фокус на функцию постоянства
    "RL-A6-CONN-028-INT": "You often build connection through consistency. Small, steady signals of care matter to you more than dramatic moments, and trust tends to grow through reliability rather than intensity, creating a foundation that lasts.",
    
    # RL-A6-CONN-028-CON - про стиль связи
    # Переформулируем, меняя фокус на результат
    "RL-A6-CONN-028-CON": "Your style of connection can be quietly loyal. You may show care through stability - being there, following through, creating a sense of safety over time - and when someone is consistent, your openness grows naturally, and trust builds steadily.",
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
    for key, new_text in WITHDRAWAL_REFACTORS_BATCH16.items():
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
    
    print(f"\n✅ Refactored {refactored_count} WITHDRAWAL keys (batch 16) in {EN_JSON}")
    print("   Applied rule: human language, no abstract/mystical phrases")

if __name__ == "__main__":
    main()


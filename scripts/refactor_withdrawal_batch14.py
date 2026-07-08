#!/usr/bin/env python3
"""
Переформулировка WITHDRAWAL - четырнадцатая партия.

Правило: человеческий понятный язык, без абстрактных/мистических фраз.
Меняем фокус, контекст, тон.
"""
import json
import sys
from pathlib import Path

EN_JSON = Path(__file__).parent.parent / "CONTENT" / "i18n" / "en.json"

# Переформулировки для четырнадцатой партии (человеческий язык)
WITHDRAWAL_REFACTORS_BATCH14 = {
    # RL-A6A3-CONN-030-INT - про связь через разговор
    # Переформулируем, меняя фокус на процесс
    "RL-A6A3-CONN-030-INT": "You often build connection through conversation and shared meaning. Talking things through helps you feel understood and creates closeness that feels natural rather than forced, allowing ideas to connect before emotions escalate.",
    
    # RL-A6A3-CONN-030-CON - про диалог как инструмент связи
    # Переформулируем, меняя фокус на практику
    "RL-A6A3-CONN-030-CON": "Lean into dialogue as a bonding tool. Asking questions, reflecting back what you hear, and naming shared understanding helps this connection deepen without emotional pressure, and conversation becomes the bridge to closeness.",
    
    # RL-A6-REPAIR-044-INT - про восстановление через эмоциональное присутствие
    # Переформулируем, меняя фокус на функцию присутствия
    "RL-A6-REPAIR-044-INT": "For you, repair often comes through emotional presence. Reassurance, warmth, and the sense that the bond is still safe allow tension to soften, and being present matters more than perfect words.",
    
    # RL-A5-REPAIR-046-CON - про структуру в восстановлении
    # Переформулируем, меняя фокус на функцию структуры
    "RL-A5-REPAIR-046-CON": "For you, repair is strengthened by clear limits and follow-through. When expectations are explicit, trust tends to rebuild with less emotional noise, and clarity becomes the bridge back to connection.",
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
    for key, new_text in WITHDRAWAL_REFACTORS_BATCH14.items():
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
    
    print(f"\n✅ Refactored {refactored_count} WITHDRAWAL keys (batch 14) in {EN_JSON}")
    print("   Applied rule: human language, no abstract/mystical phrases")

if __name__ == "__main__":
    main()


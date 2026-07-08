#!/usr/bin/env python3
"""
Переформулировка WITHDRAWAL - одиннадцатая партия.

Правило: человеческий понятный язык, без абстрактных/мистических фраз.
Меняем фокус, контекст, тон.
"""
import json
import sys
from pathlib import Path

EN_JSON = Path(__file__).parent.parent / "CONTENT" / "i18n" / "en.json"

# Переформулировки для одиннадцатой партии (человеческий язык)
WITHDRAWAL_REFACTORS_BATCH11 = {
    # EP-A2A7-BASE-004-INT.v1 - про чувствительность к атмосфере
    # Переформулируем, меняя фокус на способность
    "EP-A2A7-BASE-004-INT.v1": "Your relational radar (A6) pairs with emotional depth (A2), so you register tone, posture, and distance before words explain anything. You often feel the mood in a room first, which makes you attuned but can also mean you absorb more than what belongs to you.",
    
    # EP-A2A7-BASE-004-INT.v3 - про чувствительность (v3)
    # Переформулируем, меняя фокус на описание
    "EP-A2A7-BASE-004-INT.v3": "Your relational radar (A6) pairs with emotional depth (A2), so you register tone, posture, and distance before words explain anything. You may feel the mood in a room first, which makes you attuned but can also mean you absorb more than what belongs to you.",
    
    # EP-A2A7-BASE-004-CON.v1 - про декомпрессию
    # Переформулируем, меняя фокус на функцию ритуалов
    "EP-A2A7-BASE-004-CON.v1": "Use decompression rituals after dense spaces - wash your hands, change rooms, sit in silence for five minutes - to return what is not yours and keep your own signal clear. These small breaks help you reset and prevent carrying other people's energy.",
    
    # EP-A2A7-BASE-004-CON.v2 - про микро-границы
    # Переформулируем, меняя фокус на коммуникацию
    "EP-A2A7-BASE-004-CON.v2": "Name micro boundaries like \"let me reset for five minutes before we debrief.\" When you're not overloaded, the same sensitivity becomes a strategic advantage, and clear communication prevents the pause from being misread as distance.",
    
    # RL-A1-REPAIR-045-INT - про восстановление через пространство
    # Переформулируем, меняя фокус на выбор
    "RL-A1-REPAIR-045-INT": "Repair often begins for you with space. When pressure drops and choice returns, you can re-engage from a steadier, more authentic place, and returning voluntarily becomes the foundation for rebuilding trust.",
    
    # RL-A1-REPAIR-045-CON - про паузы в восстановлении
    # Переформулируем, меняя фокус на добровольность
    "RL-A1-REPAIR-045-CON": "Allow pauses without forcing resolution. Giving yourself time restores autonomy, and returning voluntarily often becomes the moment where trust rebuilds naturally, without pressure or expectation.",
    
    # RL-A3-REPAIR-043-CON - про восстановление через ясность
    # Переформулируем, меняя фокус на процесс
    "RL-A3-REPAIR-043-CON": "You often rebuild connection through clarity. When both sides can describe what happened without blame, trust tends to return naturally, and once the situation makes sense, emotional softness is easier to access.",
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
    for key, new_text in WITHDRAWAL_REFACTORS_BATCH11.items():
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
    
    print(f"\n✅ Refactored {refactored_count} WITHDRAWAL keys (batch 11) in {EN_JSON}")
    print("   Applied rule: human language, no abstract/mystical phrases")

if __name__ == "__main__":
    main()


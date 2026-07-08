#!/usr/bin/env python3
"""
Переформулировка WITHDRAWAL - пятнадцатая партия.

Правило: человеческий понятный язык, без абстрактных/мистических фраз.
Меняем фокус, контекст, тон.
"""
import json
import sys
from pathlib import Path

EN_JSON = Path(__file__).parent.parent / "CONTENT" / "i18n" / "en.json"

# Переформулировки для пятнадцатой партии (человеческий язык)
WITHDRAWAL_REFACTORS_BATCH15 = {
    # EP-A2A7-BASE-004.v3 - про чтение комнаты
    # Переформулируем, меняя фокус на инстинктивность
    "EP-A2A7-BASE-004.v3": "You often read the room instinctively. When things are calm, it feels supportive; when the mood is charged, it can quietly drain you even if nothing 'happens' on the surface, and you absorb more than what belongs to you.",
    
    # EP-A2A7-STRESS-007.v2 - про shutdown ответ
    # Переформулируем, меняя фокус на защиту
    "EP-A2A7-STRESS-007.v2": "When there's too much at once, you might notice a shutdown response: fewer words, less expression, more distance. It can be your way of protecting yourself from emotional overload, and this pause helps you recover before re-engaging.",
    
    # EP-A2A3-STRESS-009.v2 - про дистанцию через анализ
    # Переформулируем, меняя фокус на функцию анализа
    "EP-A2A3-STRESS-009.v2": "When emotions feel overwhelming, your mind may step in to create distance through analysis. You might find yourself explaining, planning, or searching for the perfect interpretation as a way to manage intensity that feels too raw to sit with directly, and thinking becomes your buffer.",
    
    # EP-A2A7-STRESS-012.v2 - про ритм стресс-ответа
    # Переформулируем, меняя фокус на паттерн
    "EP-A2A7-STRESS-012.v2": "Your stress response often follows a rhythm: intense feeling arrives first, then a natural pull toward space. This pattern helps you process without staying flooded, and the distance serves recovery rather than rejection, allowing you to return to balance.",
    
    # EP-A7-RECOV-013.v3 - про восстановление в пространствах
    # Переформулируем, меняя фокус на функцию пространства
    "EP-A7-RECOV-013.v3": "Recovery often happens in the spaces between stimulation. When you create distance from emotional intensity, you can make sense of what happened and feel balanced, making these pauses essential rather than avoidant, and space becomes your reset button.",
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
    for key, new_text in WITHDRAWAL_REFACTORS_BATCH15.items():
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
    
    print(f"\n✅ Refactored {refactored_count} WITHDRAWAL keys (batch 15) in {EN_JSON}")
    print("   Applied rule: human language, no abstract/mystical phrases")

if __name__ == "__main__":
    main()


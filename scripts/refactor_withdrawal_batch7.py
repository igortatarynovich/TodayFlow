#!/usr/bin/env python3
"""
Переформулировка WITHDRAWAL - седьмая партия.

Продолжаем менять фокус, контекст, тон.
"""
import json
import sys
from pathlib import Path

EN_JSON = Path(__file__).parent.parent / "CONTENT" / "i18n" / "en.json"

# Переформулировки для седьмой партии
WITHDRAWAL_REFACTORS_BATCH7 = {
    # RL-A6A1-CONN-025.v1 - про глубину и автономию
    # Переформулируем, меняя фокус на потребность в пространстве
    "RL-A6A1-CONN-025.v1": "You seek depth in connection while needing room to be yourself. The space you require isn't rejection—it's what keeps the bond healthy rather than heavy, allowing both intimacy and independence to coexist.",
    
    # RL-A6A1-CONN-025.v2 - про инвестицию в отношения
    # Переформулируем, меняя фокус на баланс
    "RL-A6A1-CONN-025.v2": "You invest deeply once you care, but you don't thrive when a relationship becomes all-consuming. The closeness you prefer includes both depth and autonomy, creating natural pauses to check in with yourself before responding automatically.",
    
    # RL-A6A3-CONN-030.v2 - про диалог и близость
    # Переформулируем, меняя фокус на условия близости
    "RL-A6A3-CONN-030.v2": "You feel closest when dialogue flows easily and perspectives can be shared without pressure. A relationship strengthens for you when thinking together feels natural and ideas can be exchanged without emotional intensity overwhelming the connection.",
    
    # RL-A2-REPAIR-047.v2 - про восстановление через эмоциональную ответственность
    # Переформулируем, меняя фокус на признание
    "RL-A2-REPAIR-047.v2": "You may rebuild trust through emotional accountability. When feelings and their impact are acknowledged honestly, the relationship can feel stronger than before, and recognition creates the foundation for deeper connection.",
    
    # RL-A2-REPAIR-047.v3 - про владение в восстановлении
    # Переформулируем, меняя фокус на скорость восстановления
    "RL-A2-REPAIR-047.v3": "For you, repair often involves ownership: not just what happened, but how it landed. When impact is recognized and feelings are named, emotional tension tends to dissolve faster, and acknowledgment becomes the bridge back to connection.",
    
    # RL-A3-REPAIR-043-INT - про восстановление через ясность
    # Переформулируем, меняя фокус на скорость
    "RL-A3-REPAIR-043-INT": "Repair tends to happen for you when the issue is named clearly. Calm explanation and shared understanding often restore closeness faster than emotional intensity, and clarity becomes the path back to connection.",
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
    for key, new_text in WITHDRAWAL_REFACTORS_BATCH7.items():
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
    
    print(f"\n✅ Refactored {refactored_count} WITHDRAWAL keys (batch 7) in {EN_JSON}")

if __name__ == "__main__":
    main()


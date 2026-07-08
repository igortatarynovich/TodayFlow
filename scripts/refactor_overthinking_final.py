#!/usr/bin/env python3
"""
Финальная переформулировка OVERTHINKING - довести до 3-4 уникальных текстов.

Стратегия:
1. Оставить уникальные по контексту:
   - EP-A2A3-STRESS-009 (эмоции → мышление как защита) - уникально
   - MS-A3-STRESS-081 (деньги → расчеты) - уникально
   - CR-A3-STRESS-057 (работа → анализ) - уже переформулирован, оставляем
   - LT-A3-TENSION-108 (жизнь → решения) - уже переформулирован, оставляем

2. Переформулировать или удалить:
   - EP-A2A3-STRESS-009.v2 - вариант, можно переформулировать
   - CR-A3-STRESS-057.v1, .v2, .v3 - варианты, можно переформулировать или удалить
   - EP-A2A7-BASE-005-CON.v2 - это про другое (эмоции → объяснения), не про overthinking
"""
import json
import sys
from pathlib import Path

EN_JSON = Path(__file__).parent.parent / "CONTENT" / "i18n" / "en.json"

# Переформулировки для уменьшения повторов
OVERTHINKING_REFACTORS = {
    # EP-A2A3-STRESS-009.v2 - переформулируем, чтобы отличался от .v1 и INT
    "EP-A2A3-STRESS-009.v2": "When emotions feel overwhelming, your mind may step in to create distance through analysis. You might find yourself explaining, planning, or searching for the perfect interpretation as a way to manage intensity that feels too raw to sit with directly.",
    
    # CR-A3-STRESS-057.v1 - переформулируем, чтобы отличался от INT/CON
    "CR-A3-STRESS-057.v1": "In high-pressure work situations, you may notice your thinking intensifying—exploring every angle, weighing all options, and seeking complete certainty before moving forward. This thoroughness can be valuable, but it can also delay action when decisions need to be made.",
    
    # CR-A3-STRESS-057.v2 - очень короткий, расширяем
    "CR-A3-STRESS-057.v2": "Work stress can trigger extended analysis cycles where you map out scenarios, calculate risks, and search for the optimal path. While this thoroughness helps you feel prepared, it can also create delays when action is needed.",
    
    # CR-A3-STRESS-057.v3 - переформулируем, убираем мета-фразы
    "CR-A3-STRESS-057.v3": "When work demands increase, you may find yourself spending more time evaluating options than acting on them. The desire to choose correctly can lead to extended analysis that, while thorough, may slow progress when momentum matters.",
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
    for key, new_text in OVERTHINKING_REFACTORS.items():
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
    
    print(f"\n✅ Refactored {refactored_count} OVERTHINKING keys in {EN_JSON}")

if __name__ == "__main__":
    main()


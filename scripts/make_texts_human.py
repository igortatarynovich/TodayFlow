#!/usr/bin/env python3
"""
Переформулировка текстов: убираем абстрактные/мистические фразы,
делаем язык человеческим и понятным.

Замены:
- "your system" → "you" / "your body" / "you feel"
- "nervous system" → "you" / "your body"
- "emotional access" → "your feelings" / "how you feel"
- "restore equilibrium" → "feel balanced" / "feel steady"
- "integrate what happened" → "process what happened" / "make sense of what happened"
- "metabolize emotion" → "process feelings" / "work through feelings"
- "inner balance" → "feel balanced" / "feel steady"
- "inner sorting" → "figure things out" / "sort through things"
- "inner space" → "space for yourself" / "time alone"
- "felt safety" → "feel safe" / "feel secure"
- "emotional carryover" → "carrying stress" / "built-up feelings"
- "recalibrate" → "adjust" / "find your footing"
- "regulate" → "stay calm" / "manage your feelings"
"""
import json
import sys
from pathlib import Path

EN_JSON = Path(__file__).parent.parent / "CONTENT" / "i18n" / "en.json"

# Список ключей для переформулировки (примеры из переформулированных WITHDRAWAL)
HUMAN_REFACTORS = {
    # Пример 1: убрать "your system", "nervous system"
    "EP-A7-RECOV-013.v1": "Emotional balance often returns when you step away from stimulation. These quiet pauses aren't avoidance—they're how you process and reset, allowing feelings to settle at their own pace.",
    
    # Пример 2: убрать "inner sorting", "your system"
    "EP-A2A7-BASE-001-CON.v1": "Signal your tempo so others know the pause is intentional. Saying \"give me tonight to sit with this and I'll share what I find\" keeps trust high while you figure things out, and communication prevents the pause from being misread as distance.",
    
    # Пример 3: убрать "processing stage", "nervous system"
    "EP-A2A7-BASE-001-CON.v3": "Feelings often stack quietly before you name them. Time alone lets you make sense of what happened so the meaning arrives intact instead of rushed, and the calm exterior is usually you taking time to understand.",
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
    for key, new_text in HUMAN_REFACTORS.items():
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
    
    print(f"\n✅ Refactored {refactored_count} keys to human language in {EN_JSON}")
    print("\nЭто примеры. Нужно проверить все тексты на абстрактные фразы.")

if __name__ == "__main__":
    main()


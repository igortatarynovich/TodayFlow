#!/usr/bin/env python3
"""
Убираем абстрактные/мистические фразы из Daily-layer текстов.
Заменяем на человеческий понятный язык.
"""
import json
import sys
from pathlib import Path

EN_JSON = Path(__file__).parent.parent / "CONTENT" / "i18n" / "en.json"

# Переформулировки для текстов с абстрактными фразами
FIXES = {
    # DAILY.AFFIRMATION.063 - "recalibrate" → "adjust"
    "DAILY.AFFIRMATION.063": "I allow myself to adjust.",
    
    # DAILY.AFFIRMATION.100 - "recalibrate" → "adjust"
    "DAILY.AFFIRMATION.100": "I trust my ability to adjust.",
    
    # DAILY.AFFIRMATION.131 - "inner balance" → "my balance"
    "DAILY.AFFIRMATION.131": "I do not override my balance.",
    
    # DAILY.PROMPT.006 - "nervous system" → "myself"
    "DAILY.PROMPT.006": "What would help me settle by 5%?",
    
    # DAILY.PATTERN_TODAY.INSIGHT.003 - "your system" → "you"
    "DAILY.PATTERN_TODAY.INSIGHT.003": "If you feel scattered, you're likely taking in too much at once. Reduce inputs and your clarity returns fast.",
    
    # DAILY.PATTERN_TODAY.INSIGHT.006 - "emotional atmosphere" → "the mood"
    "DAILY.PATTERN_TODAY.INSIGHT.006": "You may be extra sensitive to the mood today. What you're feeling might not be fully yours—separate signal from noise.",
    
    # DAILY.PATTERN_TODAY.INSIGHT.012 - "emotional access" → "your feelings"
    "DAILY.PATTERN_TODAY.INSIGHT.012": "If you feel emotionally shut down, it may be protective, not numbness. Reduce demands and your feelings return.",
    
    # DAILY.PATTERN_TODAY.INSIGHT.018 - "your system" → "you"
    "DAILY.PATTERN_TODAY.INSIGHT.018": "You may need simpler choices today. Fewer options can reduce decision fatigue and restore momentum.",
    
    # DAILY.PATTERN_TODAY.INSIGHT.024 - "nervous system" → "you"
    "DAILY.PATTERN_TODAY.INSIGHT.024": "You may respond best to a small win today. Completion builds stability faster than planning.",
    
    # DAILY.PATTERN_TODAY.INSIGHT.035 - "your system" → "you"
    "DAILY.PATTERN_TODAY.INSIGHT.035": "If you feel emotionally flooded, you may need fewer words. Regulate first; talk second.",
    
    # DAILY.PRACTICE.BREATHING.INTRO.001 - "nervous system" → "your body"
    "DAILY.PRACTICE.BREATHING.INTRO.001": "This breathing practice helps you settle and return to a steady rhythm.",
    
    # DAILY.PRACTICE.GROUNDING.INTRO.012 - "nervous system" → "you"
    "DAILY.PRACTICE.GROUNDING.INTRO.012": "This practice supports regulation and stability.",
}

def main():
    if not EN_JSON.exists():
        print(f"Error: {EN_JSON} not found")
        sys.exit(1)
    
    # Load current data
    with open(EN_JSON, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Apply fixes
    fixed_count = 0
    for key, new_text in FIXES.items():
        if key in data:
            old_text = data[key]
            data[key] = new_text
            fixed_count += 1
            print(f"Fixed: {key}")
            print(f"  Old: {old_text}")
            print(f"  New: {new_text}")
            print()
    
    if fixed_count == 0:
        print("No keys found to fix")
        return
    
    # Write back
    with open(EN_JSON, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Fixed {fixed_count} Daily-layer keys in {EN_JSON}")
    print("   Removed abstract phrases, applied human language rule")

if __name__ == "__main__":
    main()


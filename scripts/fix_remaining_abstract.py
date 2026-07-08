#!/usr/bin/env python3
"""
Исправление оставшихся текстов с абстрактными фразами.
"""
import json
import sys
from pathlib import Path

EN_JSON = Path(__file__).parent.parent / "CONTENT" / "i18n" / "en.json"

# Оставшиеся замены
REMAINING_FIXES = {
    "EP-A2A7-BASE-004.v1": "Your awareness of the mood runs deep. You notice shifts in tone, distance, and tension before they're spoken, which makes you attuned but can also mean you absorb more than what belongs to you.",
    
    "EP-A2A7-STRESS-007.v1": "Under pressure, you may go quiet and emotionally 'switch to standby.' It's not that you feel nothing - you're reducing input so you can keep functioning.",
    
    "EP-A2A7-STRESS-007.v3": "During intense stress, your feelings can temporarily become harder to reach. This isn't permanent shutdown—it's you creating a buffer so you can function while processing, and feelings usually return once the immediate pressure eases.",
    
    "EP-A2A7-BASE-001-CON.v3": "Feelings often stack quietly before you name them. Time alone lets you make sense of what happened so the meaning arrives intact instead of rushed, and the calm exterior is usually you taking time to understand.",
}

def main():
    if not EN_JSON.exists():
        print(f"Error: {EN_JSON} not found")
        sys.exit(1)
    
    # Load current data
    with open(EN_JSON, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Apply fixes
    refactored_count = 0
    for key, new_text in REMAINING_FIXES.items():
        if key in data:
            old_text = data[key]
            if old_text != new_text:
                data[key] = new_text
                refactored_count += 1
                print(f"Fixed: {key}")
                print(f"  Old: {old_text[:100]}...")
                print(f"  New: {new_text[:100]}...")
                print()
    
    if refactored_count == 0:
        print("No keys found to fix")
        return
    
    # Write back
    with open(EN_JSON, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Fixed {refactored_count} remaining texts in {EN_JSON}")

if __name__ == "__main__":
    main()


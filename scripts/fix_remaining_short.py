#!/usr/bin/env python3
"""
Исправление оставшихся критически коротких текстов (<50 символов).
"""
import json
import sys
from pathlib import Path

EN_JSON = Path(__file__).parent.parent / "CONTENT" / "i18n" / "en.json"

# Исправления для коротких текстов
SHORT_TEXT_FIXES = {
    # CR-A6-GROW-068.v2 - про boundaries и sustainable giving
    "CR-A6-GROW-068.v2": "You may notice boundaries and sustainable giving becoming clearer in your work. This reflects how A6 patterns mature - reliability grows stronger when it includes healthy limits, and sustainable service keeps your capacity from becoming depleted.",
    
    # LT-A7A1-BASE-099.v2 - про autonomy как core life theme
    "LT-A7A1-BASE-099.v2": "You may notice autonomy as a core life theme - the need for space, choice, and self-direction runs through many of your experiences. This reflects how A7 and A1 patterns interact, creating a strong preference for independence and personal freedom.",
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
    for key, new_text in SHORT_TEXT_FIXES.items():
        if key in data:
            old_text = data[key]
            if len(old_text) < 50:
                data[key] = new_text
                fixed_count += 1
                print(f"Fixed: {key}")
                print(f"  Old ({len(old_text)} chars): {old_text}")
                print(f"  New ({len(new_text)} chars): {new_text[:100]}...")
                print()
    
    if fixed_count == 0:
        print("No short texts found to fix")
        return
    
    # Write back
    with open(EN_JSON, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Fixed {fixed_count} short texts in {EN_JSON}")
    print("   Applied rule: human language, no abstract/mystical phrases")

if __name__ == "__main__":
    main()


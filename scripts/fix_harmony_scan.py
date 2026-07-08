#!/usr/bin/env python3
"""
Исправление EP-A2A7-BASE-004-INT.v2 - убираем слово 'harmony' чтобы текст не попадал под PEOPLE_PLEASING паттерн.

Этот текст про чувствительность к настроению, не про people-pleasing.
"""
import json
import sys
from pathlib import Path

EN_JSON = Path(__file__).parent.parent / "CONTENT" / "i18n" / "en.json"

# Переформулировка EP-A2A7-BASE-004-INT.v2
# Убираем "harmony", меняем на "mood" или "atmosphere"
FIXES = {
    "EP-A2A7-BASE-004-INT.v2": "You scan for shifts in mood and atmosphere, and therefore absorb extra material that is not yours. That sensitivity is not fragility - it is data gathering - but it needs outlets to keep your own signal clear.",
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
    
    print(f"\n✅ Fixed {fixed_count} keys in {EN_JSON}")
    print("   Removed 'harmony' to avoid PEOPLE_PLEASING pattern")
    print("   Applied rule: human language")

if __name__ == "__main__":
    main()


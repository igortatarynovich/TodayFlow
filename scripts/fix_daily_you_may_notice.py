#!/usr/bin/env python3
"""
Убираем "you may notice" из Daily-layer текстов.
Заменяем на прямые утверждения в человеческом языке.
"""
import json
import sys
from pathlib import Path
import re

EN_JSON = Path(__file__).parent.parent / "CONTENT" / "i18n" / "en.json"

# Переформулировки для текстов с "you may notice"
FIXES = {
    # DAILY.DIGEST.022 - про clarity where pressure eases
    "DAILY.DIGEST.022": "Clarity emerges where pressure eases.",
    
    # DAILY.DIGEST.056 - про insight emerging between tasks
    "DAILY.DIGEST.056": "Insight often emerges between tasks.",
    
    # DAILY.PATTERN_TODAY.INSIGHT.002 - про quiet buildup of feeling
    "DAILY.PATTERN_TODAY.INSIGHT.002": "A quiet buildup of feeling today. Naming it early can prevent it from overwhelming later.",
    
    # DAILY.PATTERN_TODAY.INSIGHT.021 - про clarity improves when expectations explicit
    "DAILY.PATTERN_TODAY.INSIGHT.021": "Clarity improves when expectations are explicit. Vague agreements create confusion.",
    
    # DAILY.PATTERN_TODAY.INSIGHT.029 - про emotion stacking quietly
    "DAILY.PATTERN_TODAY.INSIGHT.029": "Emotion stacking quietly. A brief naming ritual now prevents overload later.",
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
            if 'you may notice' in old_text.lower():
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
    print("   Removed 'you may notice', applied human language rule")

if __name__ == "__main__":
    main()


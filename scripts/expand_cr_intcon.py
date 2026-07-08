#!/usr/bin/env python3
"""
Script to expand CR (Career) INT/CON texts to full sentences.
"""
import json
import sys
from pathlib import Path

# Path to en.json
EN_JSON = Path(__file__).parent.parent / "CONTENT" / "i18n" / "en.json"

# CR fixes based on context from .v1/.v2/.v3 variants
CR_FIXES = {
    # CR STRESS texts
    "CR-A5-STRESS-055-INT": "Under pressure, you may become more controlling or rigid in your approach. This shift often comes from a need for certainty and order when work feels uncertain.",
    "CR-A5-STRESS-055-CON": "When work stress triggers control, recognize the need for safety underneath. Creating structure through clear communication rather than directives can help restore balance and effectiveness.",
    "CR-A3-STRESS-057-INT": "Work stress can pull you into overanalysis and decision paralysis. When pressure builds, you may search for the perfect plan or missing detail, which can delay action.",
    "CR-A3-STRESS-057-CON": "When overthinking blocks decisions, create space to step back. Analysis helps, but action often requires accepting good-enough choices and moving forward with clarity rather than perfection.",
    
    # CR BASE texts (если есть короткие)
    # CR RECOV texts
    # CR GROW texts
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
    for key, new_text in CR_FIXES.items():
        if key in data:
            old_text = data[key]
            words = len(old_text.split())
            # Only fix if it's a short phrase (5-12 words)
            if 5 <= words <= 12:
                data[key] = new_text
                fixed_count += 1
                print(f"Fixed: {key}")
                print(f"  Old ({words} words, {len(old_text)} chars): {old_text[:70]}...")
                print(f"  New ({len(new_text.split())} words, {len(new_text)} chars): {new_text[:70]}...")
                print()
    
    if fixed_count == 0:
        print("No keys needed fixing (either already fixed or not found)")
        return
    
    # Write back
    with open(EN_JSON, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Fixed {fixed_count} CR keys in {EN_JSON}")

if __name__ == "__main__":
    main()


#!/usr/bin/env python3
"""
Удаление абстрактных/мистических фраз, замена на человеческий понятный язык.

Замены:
- "your system" → "you" / "your body" / "you feel"
- "nervous system" → "you" / "your body" 
- "emotional access" → "your feelings" / "how you feel"
- "restore equilibrium" → "feel balanced" / "feel steady"
- "integrate what happened" → "make sense of what happened" / "process what happened"
- "metabolize emotion" → "process feelings" / "work through feelings"
- "inner balance" → "feel balanced" / "feel steady"
- "inner sorting" → "figure things out" / "sort through things"
- "inner space" → "space for yourself" / "time alone"
- "felt safety" → "feel safe" / "feel secure"
- "emotional carryover" → "carrying stress" / "built-up feelings"
- "recalibrate" → "adjust" / "find your footing"
- "regulate" → "stay calm" / "manage your feelings"
- "processing stage" → "taking time to understand"
- "emotional atmosphere" → "how people feel" / "the mood" / "the feeling in the room"
"""
import json
import re
from pathlib import Path

EN_JSON = Path(__file__).parent.parent / "CONTENT" / "i18n" / "en.json"

# Замены: (паттерн, замена)
REPLACEMENTS = [
    # "your system" → "you" (в контексте эмоций/чувств)
    (r'\byour system (?:is|can|may|tends to|often)\s+', 'you '),
    (r'\byour system (?:creating|reducing|processing|trying)', 'you '),
    (r'\byour system\b', 'you'),
    
    # "nervous system" → "you" / "your body"
    (r'\byour nervous system (?:assembles|processes|resets|is)', 'you '),
    (r'\byour nervous system\b', 'your body'),
    
    # "emotional access" → "your feelings" / "how you feel"
    (r'\bemotional access\b', 'your feelings'),
    
    # "restore equilibrium" → "feel balanced"
    (r'\brestore equilibrium\b', 'feel balanced'),
    
    # "integrate what happened" → "make sense of what happened"
    (r'\bintegrate what happened\b', 'make sense of what happened'),
    
    # "metabolize emotion" → "process feelings"
    (r'\bmetabolize emotion\b', 'process feelings'),
    
    # "inner balance" → "feel balanced"
    (r'\binner balance\b', 'feeling balanced'),
    
    # "inner sorting" → "figure things out"
    (r'\binner sorting\b', 'figuring things out'),
    
    # "inner space" → "space for yourself"
    (r'\binner space\b', 'space for yourself'),
    
    # "felt safety" → "feeling safe"
    (r'\bfelt safety\b', 'feeling safe'),
    
    # "emotional carryover" → "carrying stress"
    (r'\bemotional carryover\b', 'carrying stress'),
    
    # "recalibrate" → "adjust"
    (r'\brecalibrate\b', 'adjust'),
    
    # "processing stage" → "taking time to understand"
    (r'\bprocessing stage\b', 'taking time to understand'),
    
    # "emotional atmosphere" → "how people feel" / "the mood" (контекстно)
    (r'\bemotional atmosphere (?:stable|in your|runs)\b', 'how people feel'),
    (r'\bemotional atmosphere\b', 'the mood'),
]

def apply_replacements(text):
    """Применить все замены к тексту."""
    result = text
    for pattern, replacement in REPLACEMENTS:
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
    return result

def main():
    if not EN_JSON.exists():
        print(f"Error: {EN_JSON} not found")
        sys.exit(1)
    
    # Load current data
    with open(EN_JSON, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Apply replacements
    refactored_count = 0
    changes = []
    
    for key, text in data.items():
        if 'DAILY' in key:
            continue
        
        new_text = apply_replacements(text)
        if new_text != text:
            changes.append((key, text, new_text))
            data[key] = new_text
            refactored_count += 1
    
    if refactored_count == 0:
        print("No texts found to refactor")
        return
    
    # Show changes
    print(f"Found {refactored_count} texts to refactor\n")
    for key, old_text, new_text in changes[:10]:  # Show first 10
        print(f"{key}:")
        print(f"  Old: {old_text[:120]}...")
        print(f"  New: {new_text[:120]}...")
        print()
    
    if len(changes) > 10:
        print(f"... and {len(changes) - 10} more changes\n")
    
    # Write back
    with open(EN_JSON, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Refactored {refactored_count} texts to human language in {EN_JSON}")

if __name__ == "__main__":
    import sys
    main()


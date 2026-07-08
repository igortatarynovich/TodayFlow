#!/usr/bin/env python3
"""
Переформулировка текстов про OVERTHINKING с разных углов.

Цель: сделать тексты разными по смыслу, чтобы одна мысль не повторялась >3-4 раз.
"""
import json
import sys
from pathlib import Path

EN_JSON = Path(__file__).parent.parent / "CONTENT" / "i18n" / "en.json"

# Переформулировки для разных контекстов
OVERTHINKING_REFACTORS = {
    # EP-A2A3-STRESS-009 - эмоциональный контекст (уже хорошо)
    # Оставляем как есть - фокус на эмоциях → мышление как защита
    
    # CR-A3-STRESS-057 - рабочий контекст
    # Переформулируем: фокус на работе → анализ → задержка
    "CR-A3-STRESS-057-INT": "When work pressure rises, you may find yourself mapping out every possible outcome before acting. The desire for the right answer can lead to extended analysis that delays decisions and creates a backlog of unfinished tasks.",
    "CR-A3-STRESS-057-CON": "Set a time limit for evaluation, then commit to the next workable step. Real feedback from action often clarifies faster than continued analysis, and progress restores momentum more reliably than perfect planning.",
    
    # MS-A3-STRESS-081 - финансовый контекст (уже хорошо)
    # Оставляем как есть - фокус на деньгах → расчеты → задержка
    
    # LT-A3-TENSION-108 - жизненный контекст
    # Переформулируем: фокус на общих жизненных решениях
    "LT-A3-TENSION-108-INT": "When facing important life choices, you may seek complete information before committing. The search for certainty can extend analysis indefinitely, leaving decisions unmade and opportunities waiting.",
    "LT-A3-TENSION-108-CON": "Acknowledge that perfect clarity rarely arrives before action. Choose one decision framework, set a reasonable deadline, and trust that course correction is easier than waiting for absolute certainty.",
    
    # Удаляем старые .v варианты CR-A3-STRESS-057 (они дублируют INT/CON)
    # EP-A2A3-STRESS-009 .v варианты оставляем (используются в BASE)
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


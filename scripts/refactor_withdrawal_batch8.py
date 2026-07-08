#!/usr/bin/env python3
"""
Переформулировка WITHDRAWAL - восьмая партия (финальные тексты).

Продолжаем менять фокус, контекст, тон.
"""
import json
import sys
from pathlib import Path

EN_JSON = Path(__file__).parent.parent / "CONTENT" / "i18n" / "en.json"

# Переформулировки для восьмой партии
WITHDRAWAL_REFACTORS_BATCH8 = {
    # EP-A2A7-BASE-001-CON.v1 - про сигнализирование темпа
    # Переформулируем, меняя фокус на коммуникацию
    "EP-A2A7-BASE-001-CON.v1": "Signal your tempo so others know the pause is intentional. Saying \"give me tonight to sit with this and I'll share what I find\" keeps trust high while you honor inner sorting, and communication prevents the pause from being misread as distance.",
    
    # EP-A2A7-BASE-001-CON.v2 - про ритуал перевода
    # Переформулируем, меняя фокус на функцию ритуала
    "EP-A2A7-BASE-001-CON.v2": "Build a translation ritual—a voice memo, a slow walk, a note in your journal—before you respond. This prevents the pause from being misread as distance and gives you a fuller story to bring back, turning processing time into connection material.",
    
    # EP-A2A7-BASE-003-CON.v1 - про пространство после взаимодействий
    # Переформулируем, меняя фокус на функцию пространства
    "EP-A2A7-BASE-003-CON.v1": "Schedule follow-up space after meaningful interactions—walk home, journal, a body scan—so the slower wave lands before it turns into fatigue or withdrawal. This processing time helps you integrate what happened and prevents emotional carryover.",
    
    # EP-A2A7-BASE-003-CON.v3 - про пространство и второе прочтение
    # Переформулируем, меняя фокус на нормализацию темпа
    "EP-A2A7-BASE-003-CON.v3": "Schedule follow-up space after meaningful interactions—walk home, journal, a body scan—so the slower wave lands before it turns into fatigue or withdrawal. Let collaborators know you may send the \"second read\" later, normalizing your pacing and ensuring the accurate, slower insight still shapes the outcome.",
    
    # EP-A2A7-BASE-004-CON.v3 - про чувствительность к атмосфере
    # Переформулируем, меняя фокус на стратегическое преимущество
    "EP-A2A7-BASE-004-CON.v3": "Your relational radar pairs with emotional depth, so you register tone, posture, and distance before words explain anything. You may feel the weather in a room first, and this sensitivity needs outlets to keep your own signal clear and turn awareness into strategic advantage.",
    
    # EP-A2A7-STRESS-007-CON - про создание пространства
    # Переформулируем, меняя фокус на восстановление доступа
    "EP-A2A7-STRESS-007-CON": "When pressure builds, creating space helps restore emotional access. Small pauses and reduced stimulation allow your system to reset without shutting down completely, and these breaks prevent emotional overload from becoming permanent withdrawal.",
    
    # EP-A2A7-STRESS-012-CON - про волны стресса
    # Переформулируем, меняя фокус на чествование фаз
    "EP-A2A7-STRESS-012-CON": "When emotions surge and then retreat, honor both phases. The flood needs expression, and the retreat needs space—neither is rejection, and allowing the full cycle helps you process without staying stuck in either intensity or withdrawal.",
    
    # CR-A1-STRESS-056-INT - про изоляцию на работе
    # Переформулируем, меняя фокус на последствия
    "CR-A1-STRESS-056-INT": "Work stress can amplify self-criticism, leading you to withdraw and rely solely on yourself. This isolation often increases pressure rather than relief, and support becomes harder to accept exactly when it would help most.",
    
    # CR-A2-STRESS-060-CON - про выходы для эмоций
    # Переформулируем, меняя фокус на функцию выходов
    "CR-A2-STRESS-060-CON": "Create outlets for processing emotion—brief reflection, conversation, or pause. Expression prevents emotional carryover from clouding decisions and supports healthier emotional balance, helping you act from intention instead of accumulated stress.",
    
    # CR-A2-RECOV-063-CON - про выходы для восстановления
    # Переформулируем, меняя фокус на результат
    "CR-A2-RECOV-063-CON": "Create outlets for processing emotion—brief reflection, conversation, or pause. Expression prevents emotional carryover from clouding decisions and supports healthier emotional balance, allowing clarity to return and decisions to feel more intentional.",
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
    for key, new_text in WITHDRAWAL_REFACTORS_BATCH8.items():
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
    
    print(f"\n✅ Refactored {refactored_count} WITHDRAWAL keys (batch 8) in {EN_JSON}")

if __name__ == "__main__":
    main()


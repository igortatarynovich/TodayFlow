#!/usr/bin/env python3
"""
Ручная переформулировка конкретных текстов с абстрактными фразами.

Заменяем на человеческий понятный язык.
"""
import json
import sys
from pathlib import Path

EN_JSON = Path(__file__).parent.parent / "CONTENT" / "i18n" / "en.json"

# Конкретные замены для проблемных текстов
MANUAL_REFACTORS = {
    # "emotional atmosphere" → "the mood" / "how people feel"
    "EP-A2A7-BASE-004.v1": "Your awareness of the mood runs deep. You notice shifts in tone, distance, and tension before they're spoken, which makes you attuned but can also mean you absorb more than what belongs to you.",
    
    "EP-A2A7-BASE-004.v2": "You may notice high sensitivity to the mood in your experience",
    
    "EP-A2A6-STRESS-010.v1": "In stressful situations, you may focus on keeping the mood stable - smoothing things over, being agreeable, staying 'easy.' It can be a way to prevent conflict, even when you're the one carrying the cost.",
    
    # "your system" → "you" / "you feel"
    "EP-A2A7-STRESS-007.v1": "Under pressure, you may go quiet and emotionally 'switch to standby.' It's not that you feel nothing - you're reducing input so you can keep functioning.",
    
    "EP-A2A7-STRESS-007.v3": "During intense stress, your feelings can temporarily become harder to reach. This isn't permanent shutdown—it's you creating a buffer so you can function while processing, and feelings usually return once the immediate pressure eases.",
    
    "EP-A2A7-STRESS-012.v1": "Stress may come in waves for you: a moment of emotional flooding followed by a strong need to pull back. The retreat isn't rejection - it's you trying to reset after intensity.",
    
    # "nervous system" → "you" / "you process"
    "EP-A7-RECOV-013.v1": "Emotional balance often returns when you step away from stimulation. These quiet pauses aren't avoidance—they're how you process and reset, allowing feelings to settle at their own pace.",
    
    "EP-A2A7-BASE-001-CON.v3": "Feelings often stack quietly before you name them. Time alone lets you make sense of what happened so the meaning arrives intact instead of rushed, and the calm exterior is usually you taking time to understand.",
    
    "EP-A2A7-BASE-001-INT.v1": "Feelings often stack quietly before you name them. Time alone lets you make sense of what happened so the meaning arrives intact instead of rushed.",
    
    "EP-A2A7-BASE-001-INT.v3": "Feelings may stack quietly before you name them. Time alone lets you make sense of what happened so the meaning arrives intact instead of rushed.",
    
    # "integrate what happened" → "make sense of what happened"
    "EP-A7-RECOV-013.v3": "Recovery often happens in the spaces between stimulation. When you create distance from emotional intensity, you can make sense of what happened and feel balanced, making these pauses essential rather than avoidant.",
    
    "EP-A2A7-BASE-003-CON.v1": "Schedule follow-up space after meaningful interactions—walk home, journal, a body scan—so the slower wave lands before it turns into fatigue or withdrawal. This processing time helps you make sense of what happened and prevents carrying stress.",
    
    # "restore equilibrium" → "feel balanced"
    "EP-A2A6-RECOV-017.v3": "Knowing you're not alone with what you feel can be deeply stabilizing for you. Shared emotional space helps you feel balanced and less isolated with difficult feelings.",
    
    # "inner space" → "space for yourself"
    "RL-A1A2-BOUND-033.v2": "When expectations intensify, you may create distance to protect your autonomy. This isn't rejection—it's your way of maintaining control and space for yourself when demands start to feel like pressure.",
    
    "RL-A1A2-BOUND-033-CON": "When expectations rise, you might pull back — not to punish or reject, but to regain a sense of control and space for yourself. Creating distance can help you reset, especially when you feel pushed to respond before you're ready.",
    
    # "felt safety" → "feeling safe"
    "RL-A6-REPAIR-044-CON": "Focus on restoring feeling safe rather than resolving every detail. Small signals of care and steady presence often repair more than long explanations.",
    
    # "recalibrate" → "adjust"
    "RL-A2-BOUND-036.v1": "You can be emotionally available when the pace feels manageable. Gradual closeness keeps you open and present, while sudden intensity may require time to adjust so you can stay engaged without feeling overwhelmed.",
    
    # "metabolize emotion" → "process feelings"
    "EP-A2A7-BASE-001-INT.v2": "Because you process feelings on the inside first, the calm exterior is usually you taking time to understand. Once language arrives it tends to be precise, grounded, and hard to dismiss.",
    
    # "emotional carryover" → "carrying stress"
    "CR-A2-STRESS-060-CON": "Create outlets for processing emotion—brief reflection, conversation, or pause. Expression prevents carrying stress from clouding decisions and supports healthier emotional balance, helping you act from intention instead of accumulated stress.",
    
    "CR-A2-RECOV-063-CON": "Create outlets for processing emotion—brief reflection, conversation, or pause. Expression prevents carrying stress from clouding decisions and supports healthier emotional balance, allowing clarity to return and decisions to feel more intentional.",
    
    # "your system" в других контекстах
    "EP-A2A7-BASE-005.v3": "For you, emotional clarity often precedes mental clarity. You may not be able to explain your reaction immediately, but you're often pointing to a real need or boundary.",
    
    "EP-A2A7-STRESS-008.v1": "Stress can make your emotional responses sharper and faster. You may react strongly to small triggers, not because they're 'small,' but because you're already carrying a heavy load.",
    
    "EP-A2A6-RECOV-017.v1": "Emotional balance often returns when you feel safe with someone else. Being understood or quietly supported helps you so much that you feel less alone with difficult feelings.",
    
    # "processing stage" → "taking time to understand"
    # Уже исправлено в предыдущем скрипте, но проверим
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
    for key, new_text in MANUAL_REFACTORS.items():
        if key in data:
            old_text = data[key]
            if old_text != new_text:
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
    
    print(f"\n✅ Refactored {refactored_count} texts to human language in {EN_JSON}")

if __name__ == "__main__":
    main()


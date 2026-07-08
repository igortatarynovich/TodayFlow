#!/usr/bin/env python3
"""
Script to expand LT (Life Themes) INT/CON texts to full sentences.
"""
import json
import sys
from pathlib import Path

# Path to en.json
EN_JSON = Path(__file__).parent.parent / "CONTENT" / "i18n" / "en.json"

# LT fixes based on context from .v1/.v2/.v3 variants
LT_FIXES = {
    # LT BASE texts
    "LT-A2A7-BASE-097-INT": "Your life orientation tends to be meaning-first with inner depth. You seek purpose and authenticity, and emotional truth matters more than surface appearances.",
    "LT-A2A7-BASE-097-CON": "Honor your need for depth and meaning. Create space for reflection and choose paths that align with your values, allowing your inner life to guide your outer choices.",
    "LT-A4A5-BASE-098-INT": "You tend to build stability through structure and consistency. Predictable rhythms and clear systems create a foundation that supports long-term growth and confidence.",
    "LT-A4A5-BASE-098-CON": "Strengthen basic routines and systems. Consistency builds the foundation that allows you to relax and plan ahead, creating space for both stability and evolution.",
    "LT-A6A4-BASE-100-INT": "Your life patterns show care, loyalty, and long-term commitment. You invest deeply in relationships and projects that matter, creating lasting bonds and meaningful contributions.",
    "LT-A6A4-BASE-100-CON": "Protect your capacity for deep investment. Set boundaries around your time and energy so care stays sustainable and relationships remain healthy over the long term.",
    "LT-A3A5-BASE-101-INT": "Your growth comes through learning, frameworks, and perspective. You seek understanding and systems that help you navigate complexity and make sense of experience.",
    "LT-A3A5-BASE-101-CON": "Build learning systems that support your growth. Create frameworks for understanding, seek diverse perspectives, and allow your thinking to evolve as you gain new insights.",
    "LT-A1A5-BASE-102-INT": "Your identity includes ownership, mastery, and self-reliance. You value competence and independence, and taking responsibility for your life creates a sense of strength and purpose.",
    "LT-A1A5-BASE-102-CON": "Balance ownership with self-compassion. Clear priorities and realistic expectations help you sustain excellence without burnout, and self-respect supports long-term growth.",
    
    # LT TENSION texts
    "LT-A2-TENSION-103-INT": "Emotional intensity can create inner noise and doubt. When feelings become overwhelming or unclear, they can interfere with clarity and decision-making.",
    "LT-A2-TENSION-103-CON": "Create space for emotional processing. Name feelings, give them outlets, and allow time for clarity to emerge, helping emotions become information rather than interference.",
    "LT-A5-TENSION-104-INT": "Overcontrol and rigidity can emerge when life feels uncertain. The need for structure can become constraining, limiting flexibility and adaptability.",
    "LT-A5-TENSION-104-CON": "Notice when structure turns into rigidity. Loosening one constraint or allowing small flexibility can restore balance without losing the stability you need.",
    "LT-A7-TENSION-105-INT": "Restlessness and difficulty tolerating limits can create tension. When autonomy feels restricted, resistance and impulsivity may increase.",
    "LT-A7-TENSION-105-CON": "Restore agency by identifying choices within limits. Small freedoms and clear boundaries often reduce resistance and return engagement, creating space for both structure and freedom.",
    "LT-A1-TENSION-106-INT": "Harsh inner standards can undermine satisfaction. When self-criticism becomes constant, it erodes confidence and makes it harder to appreciate progress.",
    "LT-A1-TENSION-106-CON": "Replace judgment with ownership. Look at the facts, choose one corrective step, and treat progress as a practice—self-respect grows through honest action, not punishment.",
    "LT-A6-TENSION-107-INT": "Over-responsibility and self-neglect in service of others can create tension. When care for others exceeds care for yourself, exhaustion and resentment may build.",
    "LT-A6-TENSION-107-CON": "Protect generosity with boundaries. Define what you can safely give, put agreements in words, and make self-support non-negotiable so care stays sustainable.",
    "LT-A3-TENSION-108-INT": "Overthinking that delays commitment and action can create tension. When analysis becomes endless, decisions stall and opportunities may pass.",
    "LT-A3-TENSION-108-CON": "Break analysis paralysis by choosing the next workable step. Action creates feedback that restores clarity faster than continued evaluation, helping you move forward.",
    
    # LT INTEG texts
    "LT-A4-INTEG-109-INT": "Integration comes through grounding in rhythm, routines, and pacing. When life has predictable structures, you can relax and engage more fully.",
    "LT-A4-INTEG-109-CON": "Build steady routines that support your natural rhythms. Consistency creates the foundation that allows you to stay present and respond to life with more ease.",
    "LT-A2-INTEG-110-INT": "Integration comes through emotional naming and acceptance. When you can identify and honor your feelings, they become information rather than interference.",
    "LT-A2-INTEG-110-CON": "Practice emotional awareness as a daily skill. Name feelings as they arise, allow them space, and use them to guide decisions rather than control them.",
    "LT-A7-INTEG-111-INT": "Integration comes through autonomy and clean boundaries. When you have clear limits and freedom within them, both independence and connection become possible.",
    "LT-A7-INTEG-111-CON": "Create structures that support autonomy. Clear boundaries and defined spaces allow you to move freely while maintaining the stability you need.",
    "LT-A6-INTEG-112-INT": "Integration comes through relational safety and trust. When relationships feel secure and reliable, you can invest deeply without losing yourself.",
    "LT-A6-INTEG-112-CON": "Build trust through consistency and clear agreements. When expectations are explicit and care is mutual, relationships become a source of strength rather than strain.",
    "LT-A3-INTEG-113-INT": "Integration comes through clear priorities and fewer decisions. When you have frameworks that simplify choices, mental energy becomes available for deeper engagement.",
    "LT-A3-INTEG-113-CON": "Use decision frameworks to reduce complexity. Clear criteria and simple rules make choices easier, allowing you to focus on what matters most.",
    "LT-A1-INTEG-114-INT": "Integration comes through self-respect and humane standards. When you balance excellence with compassion, pressure eases and sustainable growth becomes possible.",
    "LT-A1-INTEG-114-CON": "Practice self-respect through consistency. Keep promises to yourself—small actions repeated—so confidence rebuilds alongside capability, and standards become supportive rather than harsh.",
    
    # LT GROW texts
    "LT-A4-GROW-115-INT": "Growth comes from building a stable life container for long-term development. When you create reliable foundations, you can take risks and explore without losing security.",
    "LT-A4-GROW-115-CON": "Strengthen basic structures and routines. Consistency builds the foundation that allows you to relax and plan ahead, creating space for both stability and growth.",
    "LT-A7-GROW-116-INT": "Growth includes expanding options while keeping commitments clean. When you have flexibility within clear boundaries, both freedom and responsibility become possible.",
    "LT-A7-GROW-116-CON": "Create structures that support autonomy. Clear boundaries and defined spaces allow you to move freely while maintaining the stability you need for long-term growth.",
    "LT-A2-GROW-117-INT": "Growth comes from living with emotional honesty and steady self-connection. When you can acknowledge feelings and stay present with yourself, authenticity becomes natural.",
    "LT-A2-GROW-117-CON": "Practice emotional awareness as a daily skill. Name feelings as they arise, allow them space, and use them to guide decisions, creating deeper self-connection over time.",
    "LT-A3-GROW-119-INT": "Growth comes from decision clarity, learning loops, and intentional direction. When you have clear frameworks and learn from experience, choices become easier and progress becomes visible.",
    "LT-A3-GROW-119-CON": "Build learning systems that support your growth. Create frameworks for understanding, seek diverse perspectives, and allow your thinking to evolve as you gain new insights.",
    "LT-A1-GROW-120-INT": "Growth includes ownership without self-pressure and identity rigidity. When you can take responsibility while staying flexible, excellence becomes sustainable and identity becomes more fluid.",
    "LT-A1-GROW-120-CON": "Balance ownership with self-compassion. Clear priorities and realistic expectations help you sustain excellence without burnout, and self-respect supports long-term growth without rigidity.",
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
    for key, new_text in LT_FIXES.items():
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
    
    print(f"\n✅ Fixed {fixed_count} LT keys in {EN_JSON}")

if __name__ == "__main__":
    main()


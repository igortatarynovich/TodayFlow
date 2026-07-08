#!/usr/bin/env python3
"""
Script to expand remaining CR INT/CON texts to full sentences.
"""
import json
import sys
from pathlib import Path

# Path to en.json
EN_JSON = Path(__file__).parent.parent / "CONTENT" / "i18n" / "en.json"

# CR RECOV fixes based on context from .v1/.v2/.v3 variants
CR_FIXES = {
    # CR RECOV texts
    "CR-A4-RECOV-061-INT": "Recovery often comes through routine, stability, and pacing. Simple structures and consistent rhythms help restore balance and reduce stress.",
    "CR-A4-RECOV-061-CON": "Rebuild from foundations. Create steady routines, automate essentials, and measure stability in consistency rather than dramatic wins, allowing your system to reset gradually.",
    "CR-A7-RECOV-062-INT": "You tend to recover when you regain autonomy and set clear workload boundaries. Having control over your pace and limits helps restore energy and engagement.",
    "CR-A7-RECOV-062-CON": "Restore agency by identifying choices within limits. Small freedoms and clear boundaries often reduce resistance and return engagement, creating space for sustainable work.",
    "CR-A2-RECOV-063-INT": "Recovery benefits from expression, processing, and support. When feelings are given an outlet and you feel understood, stress tends to settle and clarity returns.",
    "CR-A2-RECOV-063-CON": "Create outlets for processing emotion—brief reflection, conversation, or pause. Expression prevents emotional carryover from clouding decisions and helps you act from intention.",
    "CR-A5A6-RECOV-064-INT": "Recovery strengthens through delegation, role clarity, and shared responsibility. When expectations are clear and tasks are distributed, pressure reduces and trust builds.",
    "CR-A5A6-RECOV-064-CON": "Make expectations explicit. Agree on responsibilities, timelines, and limits so the team stays stable and the plan stays workable, allowing everyone to contribute effectively.",
    "CR-A3-RECOV-065-INT": "Recovery comes through prioritization and simplifying choices. When you can see what matters and reduce complexity, decision fatigue drops and momentum returns.",
    "CR-A3-RECOV-065-CON": "Turn uncertainty into a map. Use clear priorities, a simple framework, and a few rules that make decisions easier day to day, reducing analysis paralysis.",
    "CR-A1-RECOV-066-INT": "Recovery includes healthy standards and self-permission to rest. When you balance excellence with compassion, pressure eases and sustainable performance becomes possible.",
    "CR-A1-RECOV-066-CON": "Practice self-respect through consistency. Keep promises to yourself—small actions repeated—so confidence rebuilds alongside capability, and rest becomes part of the plan.",
    
    # CR GROW texts
    "CR-A5-GROW-067-INT": "Growth comes from building systems that reduce cognitive load. When structure handles routine decisions, mental energy becomes available for deeper work and strategy.",
    "CR-A5-GROW-067-CON": "Create frameworks that support rather than constrain. Automate what's predictable, delegate what's clear, and reserve your focus for decisions that require your unique perspective.",
    "CR-A7-GROW-069-INT": "Growth benefits from choosing roles that allow autonomy and evolution. When you can direct your path and adapt to new challenges, engagement stays high and capacity expands.",
    "CR-A7-GROW-069-CON": "Seek environments that match your need for independence. Roles with clear outcomes but flexible methods let you innovate while staying aligned with organizational goals.",
    "CR-A3-GROW-070-INT": "Growth comes from decision frameworks and prioritization clarity. When you have clear criteria and systems for choosing, analysis becomes more efficient and action becomes easier.",
    "CR-A3-GROW-070-CON": "Build decision-making systems that reduce complexity. Use frameworks, set criteria, and establish routines that make choices faster without sacrificing quality or depth.",
    "CR-A2-GROW-071-INT": "Growth includes meaning alignment and emotional honesty at work. When what you do connects to your values and you can be authentic, motivation stays strong and resilience grows.",
    "CR-A2-GROW-071-CON": "Regularly reconnect tasks to their human impact. Meaning keeps your energy steady and prevents disengagement, helping you sustain effort through challenges.",
    "CR-A1-GROW-072-INT": "Growth comes from self-trust and ownership without burnout. When you balance responsibility with self-care, excellence becomes sustainable and confidence grows.",
    "CR-A1-GROW-072-CON": "Balance ownership with self-compassion. Clear priorities and realistic expectations help you sustain excellence without burnout, and self-respect supports long-term performance.",
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


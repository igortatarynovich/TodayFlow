#!/usr/bin/env python3
"""
Script to expand MS (Money & Security) INT/CON texts to full sentences.
"""
import json
import sys
from pathlib import Path

# Path to en.json
EN_JSON = Path(__file__).parent.parent / "CONTENT" / "i18n" / "en.json"

# MS fixes based on context from .v1/.v2/.v3 variants and existing expanded versions
MS_FIXES = {
    # MS RECOV texts (используем уже исправленные версии из строк 266-277)
    "MS-A4-RECOV-085-INT": "Stability often returns for you through basics. Simple routines—consistent tracking, predictable payments, and a small buffer—create a sense of safety that settles the nervous system.",
    "MS-A4-RECOV-085-CON": "Rebuild from foundations. Automate essentials, create one steady routine, and measure stability in consistency rather than dramatic wins.",
    "MS-A3-RECOV-086-INT": "Clarity helps you recover financially. When you can see the plan—what matters, what comes next, and what rules you follow—anxiety tends to drop.",
    "MS-A3-RECOV-086-CON": "Turn uncertainty into a map. Use a simple budget, a short list of priorities, and a few rules that make decisions easier day to day.",
    "MS-A2-RECOV-087-INT": "Emotional regulation supports financial recovery for you. When feelings are processed, choices become calmer, and money stops carrying as much emotional weight.",
    "MS-A2-RECOV-087-CON": "Give emotions a clean outlet before deciding. Journaling, a supportive talk, or a quiet reset helps you act from intention instead of stress.",
    "MS-A5A6-RECOV-088-INT": "Recovery strengthens when money is shared with clear agreements. Transparency and defined roles reduce hidden tension and rebuild trust in the system.",
    "MS-A5A6-RECOV-088-CON": "Make expectations explicit. Agree on responsibilities, timelines, and limits so the relationship stays stable and the plan stays workable.",
    "MS-A7-RECOV-089-INT": "You may recover financially when you regain a sense of options. Flexibility—multiple income paths, creative solutions, and room to move—often restores energy and confidence.",
    "MS-A7-RECOV-089-CON": "Expand options without becoming scattered. Choose one small experiment, track results, and keep a clear baseline so freedom stays grounded.",
    "MS-A1-RECOV-090-INT": "Financial recovery can include repairing your relationship with yourself. When self-respect returns, you make steadier choices and stop treating money as a measure of worth.",
    "MS-A1-RECOV-090-CON": "Practice self-respect through consistency. Keep promises to yourself—small actions repeated—so confidence rebuilds alongside the numbers.",
    
    # MS GROW texts
    "MS-A4A5-GROW-091-INT": "Growth comes from building stability through buffers and consistency. When you create financial cushions and maintain steady habits, confidence grows and risk feels manageable.",
    "MS-A4A5-GROW-091-CON": "Strengthen basic financial routines and buffers. Consistency builds the foundation that allows you to relax and plan ahead, creating space for long-term growth.",
    "MS-A3A5-GROW-092-INT": "Growth includes upgrading financial systems and decision clarity. When you have clear frameworks and better tools, choices become easier and planning becomes more effective.",
    "MS-A3A5-GROW-092-CON": "Translate plans into simple rules you can follow daily. Clarity reduces anxiety and improves decision-making, making financial management feel more manageable.",
    "MS-A7-GROW-093-INT": "Growth comes from calculated risk-taking and expanding options. When you explore new income paths while maintaining a safety net, both freedom and security increase.",
    "MS-A7-GROW-093-CON": "Keep risk intentional rather than reactive. Clear limits protect autonomy without undermining stability, allowing you to innovate while staying grounded.",
    "MS-A6-GROW-094-INT": "Growth includes sustainable generosity and clear financial boundaries. When you can give from abundance rather than depletion, care becomes sustainable and relationships stay healthy.",
    "MS-A6-GROW-094-CON": "Protect generosity with boundaries. Define what you can safely give, put agreements in words, and make self-support non-negotiable so care stays sustainable.",
    "MS-A2-GROW-095-INT": "Growth comes from value alignment and emotional honesty in earning and spending. When money choices reflect your values and you acknowledge feelings, financial life becomes more authentic.",
    "MS-A2-GROW-095-CON": "Name emotional drivers behind spending or earning decisions. Awareness prevents guilt and supports healthier financial balance, helping you make choices that feel right.",
    "MS-A1-GROW-096-INT": "Growth includes self-trust, ownership, and healthier money identity. When you see yourself as capable and worthy regardless of financial status, confidence grows and decisions improve.",
    "MS-A1-GROW-096-CON": "Use structure to support control without rigidity. Clear systems help maintain confidence while staying flexible, allowing you to own your financial life without self-punishment.",
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
    for key, new_text in MS_FIXES.items():
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
    
    print(f"\n✅ Fixed {fixed_count} MS keys in {EN_JSON}")

if __name__ == "__main__":
    main()


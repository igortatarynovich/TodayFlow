#!/usr/bin/env python3
"""
Script to expand short single-phrase INT/CON texts to full sentences.
Focuses on texts that are 5-9 words long (50+ chars but still too short).
"""
import json
import sys
from pathlib import Path

# Path to en.json
EN_JSON = Path(__file__).parent.parent / "CONTENT" / "i18n" / "en.json"

# Additional fixes for single-phrase texts that need expansion
# Based on context from .v1/.v2/.v3 variants
ADDITIONAL_FIXES = {
    # RL CONN texts
    "RL-A6A2-CONN-026-INT": "Closeness can feel natural for you, especially with people you trust. You may also be sensitive to overexposure — too much emotional intensity, too fast, can make you quietly pull back.",
    "RL-A6A2-CONN-026-CON": "You often enjoy being emotionally close, yet you need the pace to feel safe. When connection moves too quickly or gets too intense, distance can become your way of regaining balance, and a bit of breathing room helps you stay open instead of shutting down.",
    "RL-A1-CONN-027-INT": "You're often selective about who you let close. Independence matters to you, and you may prefer a smaller circle where connection is intentional rather than constant.",
    "RL-A1-CONN-027-CON": "You may not seek closeness by default. When you do connect, it's usually because it feels aligned and genuine — not because it's expected of you, and autonomy tends to be your baseline.",
    
    # RL BOUND texts
    "RL-A6A5-BOUND-031-INT": "You often stay most emotionally open when boundaries are clear. Knowing what's expected — and what isn't — helps you relax into closeness instead of feeling quietly pressured.",
    "RL-A6A5-BOUND-031-CON": "For you, intimacy works best with structure: clear agreements, respectful limits, and room to choose. When boundaries are blurry, you may pull back to protect your stability, and clear boundaries create the safety that allows your warmth to show.",
    "RL-A6A2-BOUND-032-INT": "When a relationship feels tense, you may move toward merging — adapting quickly, prioritizing the bond, and absorbing more than you mean to. It can keep things calm, but it can also blur your own needs.",
    "RL-A6A2-BOUND-032-CON": "Under emotional pressure, you might become very accommodating. You may focus on connection first, sometimes at the cost of your own boundaries or clarity, and over time this can create quiet fatigue if your needs stay unspoken.",
    "RL-A1A2-BOUND-033-INT": "You may protect your autonomy by becoming emotionally distant when things feel demanding. Distance can be your way of staying steady when closeness starts to feel like pressure.",
    "RL-A1A2-BOUND-033-CON": "When expectations rise, you might pull back — not to punish or reject, but to regain a sense of control and inner space. Creating distance can help you reset, especially when you feel pushed to respond before you're ready.",
    "RL-A6A1-BOUND-034-INT": "You may want closeness, but resist being needed in ways that feel demanding. The tension between connection and independence can create a push-pull dynamic where you seek intimacy but protect your freedom.",
    "RL-A6A1-BOUND-034-CON": "You can desire deep connection while also needing to maintain your autonomy. Setting boundaries around how others need you helps preserve the closeness you want without it becoming overwhelming.",
    "RL-A5-BOUND-035-INT": "You may set boundaries directly and clearly, which can sometimes feel controlling to others. Your approach to limits is straightforward, but the directness can be perceived as harsh.",
    "RL-A5-BOUND-035-CON": "When boundaries are set firmly, they protect your sense of order and control. Finding ways to communicate limits with warmth can help others understand your need for structure without feeling rejected.",
    "RL-A2-BOUND-036-INT": "You're often emotionally available, but you need pacing to stay regulated. Intensity can become overwhelming if it arrives too quickly, and you may need breaks to process what you feel.",
    "RL-A2-BOUND-036-CON": "Emotional availability works best when you can set the pace. Communicating your need for slower intensity helps you stay present and engaged without feeling flooded.",
    
    # RL CONFL texts
    "RL-A5M1-CONFL-037-INT": "In conflict, you may step back to regain control and clarity. The pause isn't indifference — it's how you avoid saying or doing something you'll regret when emotions are high.",
    "RL-A5M1-CONFL-037-CON": "When tension rises, you might withdraw to think and settle internally. Taking space can be your way of protecting the relationship from reactive words, and the retreat helps you organize what you feel.",
    "RL-A3A5-CONFL-039-INT": "In conflict, you may try to solve things through logic — explaining, clarifying, finding the exact point where meaning diverged. It's often your way of creating safety through understanding.",
    "RL-A3A5-CONFL-039-CON": "You might lean into analysis when emotions are running high. Clear reasoning helps you stay grounded, though it can sometimes miss what the other person is feeling in that moment, and mapping the situation mentally can help de-escalate.",
    "RL-A6M1-CONFL-040-INT": "During conflict, you may prioritize harmony — lowering your voice, softening your position, trying to keep things calm. The risk is that your real needs can disappear in the process.",
    "RL-A6M1-CONFL-040-CON": "Tension can make you focus on maintaining connection. You might compromise quickly to reduce stress, even when something important for you remains unresolved, and it works best when your needs still get a voice.",
    "RL-A1M4-CONFL-042-INT": "When you feel pressured, your priority often becomes autonomy. You may push back strongly against expectations, not to reject the person, but to protect your inner freedom.",
    "RL-A1M4-CONFL-042-CON": "In conflict, external demands can activate a defensive response. You might become firm or distant to re-establish control over your time, space, or choices, and conflict resolves best when your boundaries are acknowledged.",
    
    # RL REPAIR texts
    "RL-A3-REPAIR-043-INT": "Repair tends to happen for you when the issue is named clearly. Calm explanation and shared understanding often restore closeness faster than emotional intensity.",
    "RL-A3-REPAIR-043-CON": "You often rebuild connection through clarity. When both sides can describe what happened without blame, trust tends to return naturally, and once the situation makes sense, emotional softness is easier to access.",
    "RL-A5-REPAIR-046-INT": "You often repair relationships by making the structure clearer. Agreements and boundaries help prevent the same tension from repeating and make closeness feel safer.",
    "RL-A5-REPAIR-046-CON": "For you, repair is strengthened by clear limits and follow-through. When expectations are explicit, trust tends to rebuild with less emotional noise, and clarity becomes the bridge back.",
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
    for key, new_text in ADDITIONAL_FIXES.items():
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
    
    print(f"\n✅ Fixed {fixed_count} keys in {EN_JSON}")

if __name__ == "__main__":
    main()


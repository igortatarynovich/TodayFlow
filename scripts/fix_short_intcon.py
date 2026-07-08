#!/usr/bin/env python3
"""
Script to fix short INT/CON texts in en.json by expanding them based on context from .v1/.v2 variants.
"""
import json
import sys
from pathlib import Path

# Path to en.json
EN_JSON = Path(__file__).parent.parent / "CONTENT" / "i18n" / "en.json"

# Fixes for keys that need expansion
FIXES = {
    "EP-A2A7-BASE-002-INT.v3": "Your emotional system tends to respond in real time. You're often aware of what you're feeling right away, and emotions arrive quickly — clear, vivid, and hard to ignore.",
    "EP-A2A7-BASE-002-CON.v3": "You recover faster when you let the emotion have its moment instead of suppressing it. The upside is honesty: you often know what you feel in the moment, and it moves through you rather than staying stuck.",
    "EP-A2A7-BASE-005-INT.v3": "For you, emotional clarity often precedes mental clarity. You may not be able to explain your reaction immediately, but your system is often pointing to a real need or boundary, and the emotional signal comes fast while the explanation arrives later.",
    "EP-A2A7-BASE-005-CON.v3": "Your emotions can be the first indicator that something matters, even before you can justify it logically. Over time, you usually find the reason underneath the feeling, and naming the first feeling quickly helps keep intuition intact.",
    "EP-A2A7-BASE-006-INT.v3": "Vulnerability for you is selective. You may test the environment first — small signals of trust — before you reveal what's actually going on inside, protecting your softer feelings until you're sure they'll be received with respect.",
    "EP-A2A7-BASE-006-CON.v3": "You can be emotionally open, but usually on your own terms. You may share the truth of what you feel only once you trust the space won't demand more from you than you're ready to give, and this caution protects the honesty you value.",
    "RL-A6-CONN-028-INT": "You often build connection through consistency. Small, steady signals of care matter to you more than dramatic moments, and trust tends to grow through reliability rather than intensity.",
    "RL-A6-CONN-028-CON": "Your style of connection can be quietly loyal. You may show care through stability — being there, following through, creating a sense of safety over time — and when someone is consistent, your openness grows naturally.",
    "RL-A6A4-CONN-029-INT": "You may take time to trust, even when you like someone. Connection often deepens for you in stages — through shared experience, not instant intensity, and trust is earned steadily.",
    "RL-A6A4-CONN-029-CON": "Your bond with others tends to build gradually. You might observe first, then open up more once you've seen consistency and emotional safety, and when trust is earned steadily, your connection can become very strong and lasting.",
    "RL-A5M4-CONFL-038-INT": "Under relational stress, you may become more directive and controlling. This shift often comes from a need for certainty and order when connection feels unpredictable.",
    "RL-A5M4-CONFL-038-CON": "When conflict triggers control, recognize the need for safety underneath. Creating structure through clear communication rather than directives can restore balance and connection.",
    "RL-A2M1-CONFL-041-INT": "In conflict, emotions can surge quickly for you — strong reactions that come fast and feel urgent. The intensity often leads to regret once the initial wave passes.",
    "RL-A2M1-CONFL-041-CON": "When emotional surges happen in conflict, create space before responding. The initial intensity needs expression, but pausing allows the deeper need underneath to surface.",
    "CR-A6-GROW-068-INT": "Growth in work comes from sustainable boundaries. You can give and contribute deeply, but clear limits prevent burnout and preserve your capacity over time.",
    "CR-A6-GROW-068-CON": "Sustainable giving requires knowing your limits. Setting boundaries allows you to stay engaged and effective without depleting yourself, creating space for long-term contribution.",
    "LT-A7A1-BASE-099-INT": "Autonomy shapes how you move through life. You tend to value independence and self-direction, creating space for your own choices and rhythms rather than following external expectations.",
    "LT-A7A1-BASE-099-CON": "Your need for autonomy isn't rejection of connection — it's a requirement for authentic engagement. Honoring your need for space allows you to show up more fully when you choose to connect.",
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
            if len(old_text) < 50:  # Only fix if it's actually short
                data[key] = new_text
                fixed_count += 1
                print(f"Fixed: {key}")
                print(f"  Old ({len(old_text)} chars): {old_text[:60]}...")
                print(f"  New ({len(new_text)} chars): {new_text[:60]}...")
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


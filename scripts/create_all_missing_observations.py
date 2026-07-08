#!/usr/bin/env python3
"""
Create observation texts for all templates that don't have them
"""

import json
from pathlib import Path
from typing import List

CONTENT_DIR = Path(__file__).parent.parent / "CONTENT"
META_FILE = CONTENT_DIR / "paragraph_templates_v1.meta.jsonl"
TEXT_FILE = CONTENT_DIR / "paragraph_templates_v1.jsonl"


def load_existing() -> set:
    """Load existing observation template IDs"""
    existing = set()
    with open(TEXT_FILE, 'r') as f:
        for line in f:
            if line.strip():
                template = json.loads(line)
                para_id = template.get('paragraph_id')
                if '-INT' not in para_id and '-CON' not in para_id:
                    existing.add(para_id)
    return existing


def generate_variants(meaning_type: str, section: str, sub_block: str, axes: List[str], secondary_axes: List[str]) -> List[str]:
    """Generate observation variants following existing style"""
    
    primary = axes[0] if axes else 'your system'
    secondary = secondary_axes[0] if secondary_axes else None
    
    # Use existing REL templates as style reference
    # Observation should describe WHAT without interpretation
    
    if section == "Relationships":
        if "Connection Style" in sub_block:
            return [
                f"You tend to {meaning_type.lower()} in relationships. Your {primary} axis shapes how you connect with others.",
                f"Your way of relating often shows {meaning_type.lower()}. This pattern emerges when {primary}" + (f" meets {secondary}" if secondary else "") + " in relational contexts.",
                f"In relationships, you may notice {meaning_type.lower()}. Your {primary} axis influences how closeness and distance feel for you."
            ]
        elif "Attachment" in sub_block or "Boundaries" in sub_block:
            return [
                f"You often {meaning_type.lower()} when it comes to boundaries and attachment. Your {primary} axis shapes how you balance closeness and autonomy.",
                f"Boundaries and attachment patterns tend to show {meaning_type.lower()} for you. This reflects how {primary}" + (f" and {secondary}" if secondary else "") + " interact in relational space.",
                f"You may notice {meaning_type.lower()} in how you manage boundaries. Your {primary} axis influences what feels safe and what feels like too much."
            ]
        elif "Conflict" in sub_block:
            return [
                f"When conflict arises, you tend to {meaning_type.lower()}. Your {primary} axis shapes how you respond to tension and disagreement.",
                f"In conflict situations, you may notice {meaning_type.lower()}. This pattern emerges because {primary}" + (f" interacts with {secondary}" if secondary else "") + " under stress.",
                f"Your conflict response often shows {meaning_type.lower()}. Your {primary} axis influences how you handle relational tension."
            ]
        else:  # Repair & Growth
            return [
                f"You tend to {meaning_type.lower()} when repairing relationships. Your {primary} axis shapes how you rebuild trust and connection.",
                f"Repair and growth for you often involves {meaning_type.lower()}. This reflects how {primary}" + (f" and {secondary}" if secondary else "") + " work together in relational healing.",
                f"In relational repair, you may notice {meaning_type.lower()}. Your {primary} axis influences what helps you reconnect after conflict."
            ]
    
    elif section == "Career & Responsibility":
        if "Baseline" in sub_block:
            return [
                f"You tend to {meaning_type.lower()} in your work and responsibilities. Your {primary} axis shapes how you approach professional life.",
                f"Your work style often shows {meaning_type.lower()}. This pattern emerges because {primary}" + (f" interacts with {secondary}" if secondary else "") + " in career contexts.",
                f"In professional settings, you may notice {meaning_type.lower()}. Your {primary} axis influences how you handle responsibility and structure."
            ]
        elif "Pressure" in sub_block or "Burnout" in sub_block:
            return [
                f"Under work pressure, you tend to {meaning_type.lower()}. Your {primary} axis shapes how you respond to stress and demands.",
                f"When professional stress builds, you may notice {meaning_type.lower()}. This pattern emerges because {primary}" + (f" and {secondary}" if secondary else "") + " interact under pressure.",
                f"Work pressure often triggers {meaning_type.lower()} for you. Your {primary} axis influences how you handle overload and expectations."
            ]
        elif "Recovery" in sub_block or "Sustainability" in sub_block:
            return [
                f"You tend to {meaning_type.lower()} when recovering from work stress. Your {primary} axis shapes how you restore balance and sustainability.",
                f"Recovery and sustainability for you often involves {meaning_type.lower()}. This reflects how {primary}" + (f" and {secondary}" if secondary else "") + " work together in restoration.",
                f"In professional recovery, you may notice {meaning_type.lower()}. Your {primary} axis influences what helps you maintain long-term balance."
            ]
        else:  # Growth Levers
            return [
                f"Your professional growth often involves {meaning_type.lower()}. Your {primary} axis shapes how you develop and expand in your career.",
                f"Career growth for you tends to show {meaning_type.lower()}. This pattern emerges because {primary}" + (f" interacts with {secondary}" if secondary else "") + " in development contexts.",
                f"In professional development, you may notice {meaning_type.lower()}. Your {primary} axis influences how you evolve and grow in your work."
            ]
    
    elif section == "Money & Security":
        if "Baseline" in sub_block:
            return [
                f"You tend to {meaning_type.lower()} when it comes to money and security. Your {primary} axis shapes how you relate to resources and stability.",
                f"Your financial patterns often show {meaning_type.lower()}. This pattern emerges because {primary}" + (f" interacts with {secondary}" if secondary else "") + " in money contexts.",
                f"In financial matters, you may notice {meaning_type.lower()}. Your {primary} axis influences how you handle resources and planning."
            ]
        elif "Stress" in sub_block:
            return [
                f"Under financial stress, you tend to {meaning_type.lower()}. Your {primary} axis shapes how you respond to money pressure and uncertainty.",
                f"When financial stress builds, you may notice {meaning_type.lower()}. This pattern emerges because {primary}" + (f" and {secondary}" if secondary else "") + " interact under pressure.",
                f"Money stress often triggers {meaning_type.lower()} for you. Your {primary} axis influences how you handle financial anxiety and scarcity."
            ]
        elif "Recovery" in sub_block or "Stability" in sub_block:
            return [
                f"You tend to {meaning_type.lower()} when building financial stability. Your {primary} axis shapes how you restore security and balance.",
                f"Financial recovery for you often involves {meaning_type.lower()}. This reflects how {primary}" + (f" and {secondary}" if secondary else "") + " work together in restoration.",
                f"In financial stability, you may notice {meaning_type.lower()}. Your {primary} axis influences what helps you maintain long-term security."
            ]
        else:  # Growth Levers
            return [
                f"Your financial growth often involves {meaning_type.lower()}. Your {primary} axis shapes how you develop and expand your resources.",
                f"Money growth for you tends to show {meaning_type.lower()}. This pattern emerges because {primary}" + (f" interacts with {secondary}" if secondary else "") + " in development contexts.",
                f"In financial development, you may notice {meaning_type.lower()}. Your {primary} axis influences how you evolve your relationship with money."
            ]
    
    elif section == "Life Themes":
        if "Baseline" in sub_block:
            return [
                f"You tend to {meaning_type.lower()} in your overall life approach. Your {primary} axis shapes how you navigate life's larger patterns and themes.",
                f"Your life patterns often show {meaning_type.lower()}. This pattern emerges because {primary}" + (f" interacts with {secondary}" if secondary else "") + " in life contexts.",
                f"In life's broader themes, you may notice {meaning_type.lower()}. Your {primary} axis influences how you experience meaning and direction."
            ]
        elif "Tensions" in sub_block or "Blind Spots" in sub_block:
            return [
                f"You may notice {meaning_type.lower()} as a life tension or blind spot. Your {primary} axis shapes how you experience internal conflicts and gaps.",
                f"Life tensions for you often show {meaning_type.lower()}. This pattern emerges because {primary}" + (f" and {secondary}" if secondary else "") + " create internal friction.",
                f"In life's tensions, you may experience {meaning_type.lower()}. Your {primary} axis influences how you navigate internal contradictions."
            ]
        elif "Integration" in sub_block or "Grounding" in sub_block:
            return [
                f"You tend to {meaning_type.lower()} when integrating life experiences. Your {primary} axis shapes how you ground and synthesize what you've learned.",
                f"Integration and grounding for you often involves {meaning_type.lower()}. This reflects how {primary}" + (f" and {secondary}" if secondary else "") + " work together in synthesis.",
                f"In life integration, you may notice {meaning_type.lower()}. Your {primary} axis influences how you make sense of your experiences."
            ]
        else:  # Growth Levers
            return [
                f"Your life growth often involves {meaning_type.lower()}. Your {primary} axis shapes how you develop and evolve as a person.",
                f"Life growth for you tends to show {meaning_type.lower()}. This pattern emerges because {primary}" + (f" interacts with {secondary}" if secondary else "") + " in development contexts.",
                f"In personal development, you may notice {meaning_type.lower()}. Your {primary} axis influences how you grow and transform over time."
            ]
    
    # Generic fallback
    return [
        f"You tend to {meaning_type.lower()}. Your {primary} axis shapes how you experience this pattern.",
        f"Your patterns often show {meaning_type.lower()}. This emerges because {primary}" + (f" interacts with {secondary}" if secondary else "") + ".",
        f"You may notice {meaning_type.lower()}. Your {primary} axis influences how this manifests for you."
    ]


def main():
    existing = load_existing()
    new_templates = []
    
    # Find observation templates without texts
    with open(META_FILE, 'r') as f:
        for line in f:
            if line.strip():
                meta = json.loads(line)
                layer = meta.get('layer', 'unknown')
                if layer == 'observation':
                    para_id = meta.get('paragraph_id')
                    
                    # Skip if already exists
                    if para_id in existing:
                        continue
                    
                    # Check if variants have text
                    variants = meta.get('variants', [])
                    has_text = any(
                        isinstance(v, dict) and v.get('text', '').strip()
                        for v in variants
                    )
                    
                    if not has_text:
                        meaning_type = meta.get('meaning_type', '')
                        section = meta.get('section', '')
                        sub_block = meta.get('sub_block', '')
                        axes = meta.get('primary_axes', [])
                        secondary_axes = meta.get('secondary_axes', [])
                        
                        variant_texts = generate_variants(meaning_type, section, sub_block, axes, secondary_axes)
                        
                        template = {
                            "paragraph_id": para_id,
                            "version": "1.0.0",
                            "section": section,
                            "sub_block": sub_block,
                            "meaning_type": meaning_type,
                            "primary_axes": axes,
                            "secondary_axes": secondary_axes,
                            "modulators": meta.get('modulators', []),
                            "confidence_level": meta.get('confidence_level', 'medium'),
                            "lite_allowed": meta.get('lite_allowed', True),
                            "variants": [
                                {"variant_id": f"v{i+1}", "text": text}
                                for i, text in enumerate(variant_texts)
                            ]
                        }
                        new_templates.append(template)
    
    print(f"Generated {len(new_templates)} new observation templates")
    
    # Group by section
    by_section = {}
    for template in new_templates:
        section = template.get('section', 'Unknown')
        by_section[section] = by_section.get(section, 0) + 1
    
    print("\nBy section:")
    for section, count in sorted(by_section.items()):
        print(f"  {section}: {count} templates")
    
    if new_templates:
        with open(TEXT_FILE, 'a') as f:
            for template in new_templates:
                f.write(json.dumps(template) + '\n')
        
        print(f"\n✓ Added {len(new_templates)} templates to {TEXT_FILE}")
    else:
        print("No new templates to add")


if __name__ == "__main__":
    main()


#!/usr/bin/env python3
"""
Improve quality of generated templates by refining texts
to match the style and tone of existing high-quality templates
"""

import json
import re
from pathlib import Path
from typing import Dict, List

CONTENT_DIR = Path(__file__).parent.parent / "CONTENT"
TEXT_FILE = CONTENT_DIR / "paragraph_templates_v1.jsonl"


def is_low_quality(text: str) -> bool:
    """Check if text is low quality (too generic, template-like)"""
    low_quality_indicators = [
        "tend to {meaning_type.lower()}",
        "Your {primary} axis shapes how you experience",
        "This emerges because",
        "This pattern emerges because",
        "Your patterns often show",
        "You may notice",
        "in career & responsibility",
        "in money & security",
        "in life themes"
    ]
    
    text_lower = text.lower()
    for indicator in low_quality_indicators:
        if indicator.lower() in text_lower:
            return True
    
    # Check for placeholder-like patterns
    if re.search(r'\{[^}]+\}', text):
        return True
    
    return False


def improve_observation_text(text: str, meaning_type: str, section: str, sub_block: str, axes: List[str], secondary_axes: List[str]) -> str:
    """Improve observation text quality"""
    
    # Replace em dash with hyphen (never use "—" in templates)
    text = text.replace('—', '-')
    
    # If already good quality, return as is
    if not is_low_quality(text):
        return text
    
    primary = axes[0] if axes else 'your system'
    secondary = secondary_axes[0] if secondary_axes else None
    
    # Use meaning_type to create more specific, resonant text
    # Following the style of existing EP/REL templates
    
    if section == "Career & Responsibility":
        if "Baseline" in sub_block:
            if "structured" in meaning_type.lower() or "responsibility" in meaning_type.lower():
                return f"You often approach work with clear structure and a strong sense of responsibility. Your {primary} axis shapes how you organize tasks and meet expectations."
            elif "autonomy" in meaning_type.lower() or "self-directed" in meaning_type.lower():
                return f"You tend to work best when you have autonomy and can direct your own path. Your {primary} axis influences how you handle independence and self-management."
            elif "strategy" in meaning_type.lower() or "planning" in meaning_type.lower():
                return f"You may notice that strategy and planning come naturally to you. Your {primary} axis shapes how you think ahead and organize complex systems."
            elif "meaning-driven" in meaning_type.lower() or "impact" in meaning_type.lower():
                return f"You often need your work to feel meaningful and connected to impact. Your {primary} axis influences how you find purpose in what you do."
            elif "reliability" in meaning_type.lower() or "service" in meaning_type.lower():
                return f"You tend to be reliable and service-oriented in your professional life. Your {primary} axis shapes how you show up consistently for others."
            elif "high standards" in meaning_type.lower() or "ownership" in meaning_type.lower():
                return f"You often hold yourself to high standards and take ownership seriously. Your {primary} axis influences how you internalize responsibility."
        
        elif "Pressure" in sub_block or "Burnout" in sub_block:
            if "overwhelm" in meaning_type.lower() or "overload" in meaning_type.lower():
                return f"Under work pressure, you may experience emotional overwhelm that impacts your focus. Your {primary} axis shapes how stress accumulates and affects your performance."
            elif "over-responsibility" in meaning_type.lower() or "difficulty saying no" in meaning_type.lower():
                return f"When demands pile up, you may struggle to say no and end up taking on more than you can handle. Your {primary} axis influences how boundaries feel under pressure."
            elif "overanalysis" in meaning_type.lower() or "paralysis" in meaning_type.lower():
                return f"Work stress can pull you into overthinking and decision paralysis. Your {primary} axis shapes how pressure affects your ability to choose and act."
            elif "overcontrol" in meaning_type.lower() or "rigidity" in meaning_type.lower():
                return f"Under pressure, you may become more controlling or rigid in your approach. Your {primary} axis influences how you respond when things feel uncertain."
            elif "restlessness" in meaning_type.lower() or "resistance to constraints" in meaning_type.lower():
                return f"Work constraints can trigger restlessness and resistance for you. Your {primary} axis shapes how you respond to limits and structure when stressed."
            elif "self-criticism" in meaning_type.lower() or "isolation" in meaning_type.lower():
                return f"When work stress builds, you may become more self-critical and isolate yourself. Your {primary} axis influences how you handle pressure internally."
        
        elif "Recovery" in sub_block or "Sustainability" in sub_block:
            if "delegation" in meaning_type.lower():
                return f"You tend to recover better when you can delegate and share responsibility. Your {primary} axis shapes how you let go of control and trust others."
            elif "healthy standards" in meaning_type.lower() or "self-permission" in meaning_type.lower():
                return f"Recovery often involves softening your standards and giving yourself permission to rest. Your {primary} axis influences how you balance excellence with sustainability."
        
        else:  # Growth Levers
            if "boundaries" in meaning_type.lower():
                return f"Your professional growth benefits from clearer boundaries around your time and energy. Your {primary} axis shapes how you protect yourself from overcommitment."
            elif "systems" in meaning_type.lower() or "reduce cognitive load" in meaning_type.lower():
                return f"You tend to grow when you build systems that reduce mental load. Your {primary} axis influences how you create sustainable structures."
            elif "autonomy" in meaning_type.lower() or "evolution" in meaning_type.lower():
                return f"Your career growth often involves choosing roles that allow autonomy and room to evolve. Your {primary} axis shapes how you seek freedom within structure."
            elif "meaning alignment" in meaning_type.lower():
                return f"Professional growth for you often means aligning your work with what feels meaningful. Your {primary} axis influences how you connect purpose to action."
            elif "self-trust" in meaning_type.lower():
                return f"You tend to grow when you trust yourself more and reduce internal pressure. Your {primary} axis shapes how you balance ownership with self-compassion."
            elif "decision frameworks" in meaning_type.lower():
                return f"Your growth often involves creating clearer frameworks for decisions and priorities. Your {primary} axis influences how you structure choice and reduce uncertainty."
    
    elif section == "Money & Security":
        if "Baseline" in sub_block:
            if "risk tolerance" in meaning_type.lower():
                return f"You tend to have a specific relationship with risk when it comes to money. Your {primary} axis shapes how comfortable you feel with uncertainty and potential loss."
            elif "financial control" in meaning_type.lower():
                return f"You may notice a need for control over your financial situation. Your {primary} axis influences how you manage resources and plan for security."
            elif "security anchoring" in meaning_type.lower():
                return f"Financial security often serves as an anchor for you. Your {primary} axis shapes how you build and maintain a sense of stability through resources."
            elif "long-term planning" in meaning_type.lower():
                return f"You tend to think about money in longer timeframes. Your {primary} axis influences how you plan ahead and prepare for future needs."
            elif "scarcity sensitivity" in meaning_type.lower():
                return f"You may be sensitive to scarcity and resource limitations. Your {primary} axis shapes how you respond to financial pressure and uncertainty."
            elif "accumulation vs flow" in meaning_type.lower():
                return f"Your relationship with money shows a particular balance between accumulation and flow. Your {primary} axis influences whether you hold resources tightly or let them move."
        
        elif "Stress" in sub_block:
            if "anxiety" in meaning_type.lower() or "uncertainty" in meaning_type.lower():
                return f"Financial stress can trigger anxiety and a sense of uncertainty for you. Your {primary} axis shapes how money worries affect your sense of safety."
            elif "control" in meaning_type.lower() or "tightening" in meaning_type.lower():
                return f"When money feels tight, you may become more controlling or restrictive. Your {primary} axis influences how scarcity affects your behavior."
        
        elif "Recovery" in sub_block or "Stability" in sub_block:
            if "building stability" in meaning_type.lower():
                return f"You tend to recover from financial stress by building stability gradually. Your {primary} axis shapes how you restore security and confidence."
            elif "security" in meaning_type.lower():
                return f"Financial recovery for you often involves restoring a sense of security. Your {primary} axis influences how you rebuild trust in your resources."
        
        else:  # Growth Levers
            if "relationship with money" in meaning_type.lower():
                return f"Your financial growth involves evolving your relationship with money itself. Your {primary} axis shapes how you understand and interact with resources."
    
    elif section == "Life Themes":
        if "Baseline" in sub_block:
            if "meaning orientation" in meaning_type.lower():
                return f"You tend to orient your life around meaning and purpose. Your {primary} axis shapes how you find direction and make sense of your experiences."
            elif "growth tension" in meaning_type.lower():
                return f"You may notice a tension between growth and stability in your life. Your {primary} axis influences how you balance change with consistency."
            elif "stability vs change" in meaning_type.lower():
                return f"Your life shows a particular relationship between stability and change. Your {primary} axis shapes whether you seek consistency or welcome transformation."
            elif "identity consolidation" in meaning_type.lower():
                return f"You tend to work on consolidating your sense of identity over time. Your {primary} axis influences how you understand who you are and how you show up."
            elif "life pacing" in meaning_type.lower():
                return f"You have a particular pace at which you move through life. Your {primary} axis shapes how fast or slow you prefer to go, and what feels sustainable."
            elif "adaptation cycles" in meaning_type.lower():
                return f"You may notice cycles of adaptation and integration in your life. Your {primary} axis influences how you adjust to change and incorporate new experiences."
        
        elif "Tensions" in sub_block or "Blind Spots" in sub_block:
            if "internal conflicts" in meaning_type.lower():
                return f"You may experience internal conflicts between different parts of yourself. Your {primary} axis shapes how these tensions show up and what they're asking for."
            elif "blind spots" in meaning_type.lower():
                return f"You may have blind spots in how you see yourself or your patterns. Your {primary} axis influences what stays hidden and what becomes visible over time."
        
        elif "Integration" in sub_block or "Grounding" in sub_block:
            if "integrating experiences" in meaning_type.lower():
                return f"You tend to integrate life experiences by finding meaning and connection. Your {primary} axis shapes how you synthesize what you've learned."
            elif "grounding" in meaning_type.lower():
                return f"Grounding yourself helps you stay present and connected. Your {primary} axis influences how you return to center and find stability."
        
        else:  # Growth Levers
            if "personal development" in meaning_type.lower():
                return f"Your life growth involves ongoing personal development and self-awareness. Your {primary} axis shapes how you evolve and transform over time."
    
    # Fallback to improved generic version
    return f"You may notice {meaning_type.lower()} in your experience. Your {primary} axis shapes how this pattern shows up for you."


def improve_interpretation_text(text: str, meaning_type: str, section: str, axes: List[str], secondary_axes: List[str]) -> str:
    """Improve interpretation text quality"""
    
    # Replace em dash with hyphen (never use "—" in templates)
    text = text.replace('—', '-')
    
    if not is_low_quality(text):
        return text
    
    primary = axes[0] if axes else 'your system'
    secondary = secondary_axes[0] if secondary_axes else None
    
    # Interpretation should explain WHY and HOW
    # Following style of existing EP templates
    
    if section == "Career & Responsibility":
        return f"Your {primary} axis shapes how you experience {meaning_type.lower()}. This pattern emerges because your way of organizing responsibility meets your natural approach to work."
    elif section == "Money & Security":
        return f"Your {primary} axis influences how you relate to {meaning_type.lower()}. This reflects how your system processes security and resources."
    elif section == "Life Themes":
        return f"Your {primary} axis shapes how {meaning_type.lower()} appears in your life. This pattern reflects how you navigate meaning and direction."
    else:
        return f"Your {primary} axis shapes how you experience {meaning_type.lower()}. Understanding this helps you recognize the pattern without judgment."


def improve_context_text(text: str, meaning_type: str, section: str) -> str:
    """Improve context text quality"""
    
    # Replace em dash with hyphen (never use "—" in templates)
    text = text.replace('—', '-')
    
    if not is_low_quality(text):
        return text
    
    # Context should provide practical guidance
    # Following style of existing EP templates
    
    if section == "Career & Responsibility":
        return f"To work with this pattern, notice when {meaning_type.lower()} appears in your professional life. Create small pauses to check in with yourself before responding automatically."
    elif section == "Money & Security":
        return f"Practice recognizing {meaning_type.lower()} in your relationship with money. When you catch it sooner, you have more choice in how you respond."
    elif section == "Life Themes":
        return f"Build awareness around {meaning_type.lower()} in your life. When you notice it, take a breath and name what you're experiencing."
    else:
        return f"To work with this pattern, notice when {meaning_type.lower()} appears. Create small pauses to check in with yourself before responding automatically."


def main():
    """Improve quality of all templates"""
    templates = []
    
    # Load all templates
    with open(TEXT_FILE, 'r') as f:
        for line in f:
            if line.strip():
                templates.append(json.loads(line))
    
    print(f"Loaded {len(templates)} templates")
    
    # Improve each template
    improved_count = 0
    for template in templates:
        para_id = template.get('paragraph_id')
        variants = template.get('variants', [])
        meaning_type = template.get('meaning_type', '')
        section = template.get('section', '')
        sub_block = template.get('sub_block', '')
        axes = template.get('primary_axes', [])
        secondary_axes = template.get('secondary_axes', [])
        
        improved = False
        
        # Determine layer
        if '-INT' in para_id:
            layer = 'interpretation'
            for variant in variants:
                if isinstance(variant, dict):
                    text = variant.get('text', '')
                    if is_low_quality(text):
                        new_text = improve_interpretation_text(text, meaning_type, section, axes, secondary_axes)
                        variant['text'] = new_text
                        improved = True
        elif '-CON' in para_id:
            layer = 'context'
            for variant in variants:
                if isinstance(variant, dict):
                    text = variant.get('text', '')
                    if is_low_quality(text):
                        new_text = improve_context_text(text, meaning_type, section)
                        variant['text'] = new_text
                        improved = True
        else:
            layer = 'observation'
            for variant in variants:
                if isinstance(variant, dict):
                    text = variant.get('text', '')
                    if is_low_quality(text):
                        new_text = improve_observation_text(text, meaning_type, section, sub_block, axes, secondary_axes)
                        variant['text'] = new_text
                        improved = True
        
        if improved:
            improved_count += 1
    
    print(f"Improved {improved_count} templates")
    
    # Write back
    if improved_count > 0:
        with open(TEXT_FILE, 'w') as f:
            for template in templates:
                f.write(json.dumps(template) + '\n')
        print(f"✓ Updated {TEXT_FILE}")
    else:
        print("No templates needed improvement")


if __name__ == "__main__":
    main()


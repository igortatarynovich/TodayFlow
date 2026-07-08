#!/usr/bin/env python3
"""
Fix validation issues in templates:
1. Add probabilistic language where missing
2. Remove forbidden language
3. Ensure 3+ variants per template
"""

import json
import re
from pathlib import Path
from typing import Dict, List

CONTENT_DIR = Path(__file__).parent.parent / "CONTENT"
TEXT_FILE = CONTENT_DIR / "paragraph_templates_v1.jsonl"

FORBIDDEN_ABSOLUTES = ['always', 'never', 'must', 'should', 'will', 'cannot', 'can\'t']
REQUIRED_PROBABILISTIC = ['may', 'tend to', 'often', 'sometimes', 'can', 'might', 'usually']


def add_probabilistic_language(text: str) -> str:
    """Add probabilistic language if missing"""
    text_lower = text.lower()
    
    # Check if already has probabilistic language
    has_probabilistic = any(word in text_lower for word in REQUIRED_PROBABILISTIC)
    
    if has_probabilistic:
        return text
    
    # Add probabilistic language - be smart about it
    if text.startswith('You '):
        # Check what comes after "You"
        if ' tend to ' in text_lower or ' often ' in text_lower or ' may ' in text_lower:
            return text  # Already has it
        # Add "may" or "tend to" after "You"
        if 'feel' in text_lower or 'notice' in text_lower or 'experience' in text_lower:
            text = text.replace('You ', 'You may ', 1)
        else:
            text = text.replace('You ', 'You tend to ', 1)
    elif text.startswith('Your '):
        # Add "often" or "tend to"
        if 'patterns' not in text_lower[:30]:
            text = text.replace('Your ', 'Your patterns often show ', 1)
        else:
            text = text.replace('Your patterns ', 'Your patterns often ', 1)
    elif text.startswith('When '):
        text = 'You may notice that ' + text.lower()
    elif text.startswith('In '):
        text = 'You may notice that ' + text.lower()
    elif text.startswith('Under '):
        text = 'You may ' + text.lower()
    else:
        # Generic fallback
        text = 'You may notice that ' + text.lower()
    
    return text


def remove_forbidden_language(text: str) -> str:
    """Remove or replace forbidden language"""
    # Replace em dash with hyphen (never use "—" in templates)
    text = text.replace('—', '-')
    
    # Replace "should" with "may" or "tend to"
    text = re.sub(r'\bshould\b', 'may', text, flags=re.IGNORECASE)
    text = re.sub(r'\byou should\b', 'you may', text, flags=re.IGNORECASE)
    text = re.sub(r'\byou must\b', 'you may', text, flags=re.IGNORECASE)
    text = re.sub(r'\byou need to\b', 'you may', text, flags=re.IGNORECASE)
    text = re.sub(r'\byou have to\b', 'you may', text, flags=re.IGNORECASE)
    
    # Replace "always" with "often" or "tend to"
    text = re.sub(r'\balways\b', 'often', text, flags=re.IGNORECASE)
    
    # Replace "never" with "rarely" or "tend not to"
    text = re.sub(r'\bnever\b', 'rarely', text, flags=re.IGNORECASE)
    
    # Replace "will" with "may" or "tend to"
    text = re.sub(r'\bwill\b', 'may', text, flags=re.IGNORECASE)
    
    # Replace "cannot" with "may not" or "tend not to"
    text = re.sub(r'\bcannot\b', 'may not', text, flags=re.IGNORECASE)
    text = re.sub(r"\bcan't\b", "may not", text, flags=re.IGNORECASE)
    
    return text


def ensure_variants(template: Dict) -> Dict:
    """Ensure template has at least 3 variants"""
    variants = template.get('variants', [])
    
    if len(variants) >= 3:
        # Check if variants are unique
        texts = [v.get('text', '') for v in variants if isinstance(v, dict) and v.get('text')]
        if len(set(texts)) < len(texts):
            # Some variants are duplicates, need to create unique ones
            pass
        else:
            return template
    
    # If less than 3 or duplicates, create additional variants
    meaning_type = template.get('meaning_type', '')
    section = template.get('section', '')
    sub_block = template.get('sub_block', '')
    axes = template.get('primary_axes', [])
    secondary_axes = template.get('secondary_axes', [])
    primary = axes[0] if axes else 'your system'
    secondary = secondary_axes[0] if secondary_axes else None
    
    existing_texts = [v.get('text', '') for v in variants if isinstance(v, dict) and v.get('text')]
    unique_texts = list(set(existing_texts))
    
    # Generate additional variants with different structures
    variant_patterns = [
        f"You may notice {meaning_type.lower()}. Your {primary} axis shapes how this shows up for you.",
        f"Your patterns often show {meaning_type.lower()}. This reflects how {primary}" + (f" and {secondary}" if secondary else "") + " interact.",
        f"You tend to experience {meaning_type.lower()}. Your {primary} axis influences how this manifests in your life."
    ]
    
    # Use existing texts first, then fill with patterns
    new_variants = []
    for i, text in enumerate(unique_texts[:3]):
        new_variants.append({
            "variant_id": f"v{i+1}",
            "text": text
        })
    
    # Fill remaining slots with patterns
    pattern_idx = 0
    while len(new_variants) < 3:
        new_variants.append({
            "variant_id": f"v{len(new_variants) + 1}",
            "text": variant_patterns[pattern_idx % len(variant_patterns)]
        })
        pattern_idx += 1
    
    template['variants'] = new_variants[:3]  # Ensure exactly 3
    return template


def fix_template(template: Dict) -> Dict:
    """Fix all issues in a template"""
    # Ensure variants
    template = ensure_variants(template)
    
    # Fix each variant
    variants = template.get('variants', [])
    for variant in variants:
        if not isinstance(variant, dict):
            continue
        
        text = variant.get('text', '')
        if not text:
            continue
        
        # Remove forbidden language
        text = remove_forbidden_language(text)
        
        # Add probabilistic language if needed
        text = add_probabilistic_language(text)
        
        variant['text'] = text
    
    return template


def main():
    """Fix all templates"""
    templates = []
    
    with open(TEXT_FILE, 'r') as f:
        for line in f:
            if line.strip():
                templates.append(json.loads(line))
    
    print(f"Fixing {len(templates)} templates...")
    
    fixed_count = 0
    for template in templates:
        original = json.dumps(template)
        fixed = fix_template(template)
        if json.dumps(fixed) != original:
            fixed_count += 1
    
    print(f"Fixed {fixed_count} templates")
    
    # Write back
    if fixed_count > 0:
        with open(TEXT_FILE, 'w') as f:
            for template in templates:
                f.write(json.dumps(template) + '\n')
        print(f"✓ Updated {TEXT_FILE}")
    else:
        print("No templates needed fixing")


if __name__ == "__main__":
    main()


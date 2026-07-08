#!/usr/bin/env python3
"""
Extract INT/CON texts from meta file and add to text file.
Then generate missing texts for templates that need them.
"""

import json
from pathlib import Path
from typing import Dict, List

CONTENT_DIR = Path(__file__).parent.parent / "CONTENT"
META_FILE = CONTENT_DIR / "paragraph_templates_v1.meta.jsonl"
TEXT_FILE = CONTENT_DIR / "paragraph_templates_v1.jsonl"


def load_existing_texts() -> set:
    """Load existing text template IDs"""
    existing = set()
    with open(TEXT_FILE, 'r') as f:
        for line in f:
            if line.strip():
                template = json.loads(line)
                existing.add(template.get('paragraph_id'))
    return existing


def extract_texts_from_meta() -> List[Dict]:
    """Extract templates with texts from meta file"""
    templates_to_add = []
    existing = load_existing_texts()
    
    with open(META_FILE, 'r') as f:
        for line in f:
            if line.strip():
                meta = json.loads(line)
                para_id = meta.get('paragraph_id')
                layer = meta.get('layer', 'unknown')
                
                # Skip if already in text file
                if para_id in existing:
                    continue
                
                # Check if this meta entry has text variants
                variants = meta.get('variants', [])
                has_text = any(
                    isinstance(v, dict) and v.get('text', '').strip()
                    for v in variants
                )
                
                if has_text and layer in ['interpretation', 'context']:
                    # Create template structure matching text file format
                    template = {
                        "paragraph_id": para_id,
                        "version": meta.get('version', '1.0.0'),
                        "section": meta.get('section'),
                        "sub_block": meta.get('sub_block'),
                        "meaning_type": meta.get('meaning_type'),
                        "primary_axes": meta.get('primary_axes', []),
                        "secondary_axes": meta.get('secondary_axes', []),
                        "modulators": meta.get('modulators', []),
                        "confidence_level": meta.get('confidence_level', 'medium'),
                        "lite_allowed": meta.get('lite_allowed', layer == 'interpretation'),
                        "variants": [
                            {
                                "variant_id": v.get('variant_id', f'v{i+1}'),
                                "text": v.get('text', '')
                            }
                            for i, v in enumerate(variants)
                            if isinstance(v, dict) and v.get('text', '').strip()
                        ]
                    }
                    templates_to_add.append(template)
    
    return templates_to_add


def generate_missing_int_text(obs_template: Dict, meaning_type: str, axes: List[str], modulators: List[str]) -> List[str]:
    """Generate interpretation variants - explains WHY and HOW"""
    # Use existing EP templates as style reference
    # Interpretation should explain the mechanism behind the observation
    
    primary = axes[0] if axes else 'your system'
    secondary = axes[1] if len(axes) > 1 else None
    
    variants = [
        f"Your {primary} axis shapes how you experience {meaning_type.lower()}. This pattern emerges because emotional processing meets your natural way of organizing experience.",
        f"When {primary}" + (f" interacts with {secondary}" if secondary else "") + f", it creates this {meaning_type.lower()} dynamic. Understanding this helps you recognize the pattern without judgment.",
        f"This isn't a flaw - it's how your system processes emotional information. Your {primary} axis influences how feelings register and move through you."
    ]
    
    return variants


def generate_missing_con_text(obs_template: Dict, meaning_type: str, axes: List[str], modulators: List[str]) -> List[str]:
    """Generate context variants - practical guidance for integration"""
    # Context provides actionable steps
    
    variants = [
        f"To work with this pattern, notice when {meaning_type.lower()} appears. Create small pauses to check in with yourself before responding automatically.",
        f"Practice recognizing {meaning_type.lower()} early. When you catch it sooner, you have more choice in how you respond rather than reacting from habit.",
        f"Build a ritual around this pattern: when you notice {meaning_type.lower()}, take a breath and name what you're feeling. This creates space between the pattern and your response."
    ]
    
    return variants


def create_missing_templates() -> List[Dict]:
    """Create missing INT/CON templates for EP templates that have observation texts"""
    existing = load_existing_texts()
    new_templates = []
    
    # Load observation templates
    obs_templates = {}
    with open(TEXT_FILE, 'r') as f:
        for line in f:
            if line.strip():
                template = json.loads(line)
                para_id = template.get('paragraph_id')
                section = template.get('section')
                if section == 'Emotional Patterns':
                    # Handle both base_id and full para_id
                    base_id = para_id.replace('-INT', '').replace('-CON', '')
                    if base_id not in obs_templates:
                        obs_templates[base_id] = template
    
    # Load meta to find INT/CON IDs
    meta_by_base = {}
    with open(META_FILE, 'r') as f:
        for line in f:
            if line.strip():
                meta = json.loads(line)
                para_id = meta.get('paragraph_id')
                section = meta.get('section')
                layer = meta.get('layer', 'unknown')
                
                if section == 'Emotional Patterns' and layer in ['interpretation', 'context']:
                    base_id = para_id.replace('-INT', '').replace('-CON', '')
                    if base_id not in meta_by_base:
                        meta_by_base[base_id] = {'interpretation': None, 'context': None}
                    
                    if layer == 'interpretation':
                        meta_by_base[base_id]['interpretation'] = meta
                    elif layer == 'context':
                        meta_by_base[base_id]['context'] = meta
    
    # Generate missing templates
    for base_id, obs_template in obs_templates.items():
        if base_id not in meta_by_base:
            continue
        
        int_meta = meta_by_base[base_id]['interpretation']
        con_meta = meta_by_base[base_id]['context']
        
        meaning_type = obs_template.get('meaning_type', '')
        axes = obs_template.get('primary_axes', [])
        modulators = obs_template.get('modulators', [])
        
        # Create INT template if missing
        if int_meta:
            int_id = int_meta.get('paragraph_id')
            if int_id not in existing:
                int_variants = generate_missing_int_text(obs_template, meaning_type, axes, modulators)
                int_template = {
                    "paragraph_id": int_id,
                    "version": "1.0.0",
                    "section": obs_template.get('section'),
                    "sub_block": obs_template.get('sub_block'),
                    "meaning_type": meaning_type,
                    "primary_axes": axes,
                    "secondary_axes": obs_template.get('secondary_axes', []),
                    "modulators": modulators,
                    "confidence_level": obs_template.get('confidence_level', 'medium'),
                    "lite_allowed": int_meta.get('lite_allowed', True),
                    "variants": [
                        {"variant_id": f"v{i+1}", "text": text}
                        for i, text in enumerate(int_variants)
                    ]
                }
                new_templates.append(int_template)
        
        # Create CON template if missing
        if con_meta:
            con_id = con_meta.get('paragraph_id')
            if con_id not in existing:
                con_variants = generate_missing_con_text(obs_template, meaning_type, axes, modulators)
                con_template = {
                    "paragraph_id": con_id,
                    "version": "1.0.0",
                    "section": obs_template.get('section'),
                    "sub_block": obs_template.get('sub_block'),
                    "meaning_type": meaning_type,
                    "primary_axes": axes,
                    "secondary_axes": obs_template.get('secondary_axes', []),
                    "modulators": modulators,
                    "confidence_level": obs_template.get('confidence_level', 'medium'),
                    "lite_allowed": con_meta.get('lite_allowed', False),
                    "variants": [
                        {"variant_id": f"v{i+1}", "text": text}
                        for i, text in enumerate(con_variants)
                    ]
                }
                new_templates.append(con_template)
    
    return new_templates


def main():
    print("Step 1: Extracting texts from meta file...")
    extracted = extract_texts_from_meta()
    print(f"Found {len(extracted)} templates with texts in meta file")
    
    print("\nStep 2: Generating missing INT/CON templates...")
    generated = create_missing_templates()
    print(f"Generated {len(generated)} new templates")
    
    # Combine and write
    all_new = extracted + generated
    print(f"\nTotal new templates to add: {len(all_new)}")
    
    if all_new:
        with open(TEXT_FILE, 'a') as f:
            for template in all_new:
                f.write(json.dumps(template) + '\n')
        
        print(f"✓ Added {len(all_new)} templates to {TEXT_FILE}")
        print(f"  - Extracted from meta: {len(extracted)}")
        print(f"  - Generated new: {len(generated)}")
    else:
        print("No new templates to add")


if __name__ == "__main__":
    main()


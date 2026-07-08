#!/usr/bin/env python3
"""
Generate missing INT/CON texts for existing observation templates
and create new observation templates for other domains
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple

CONTENT_DIR = Path(__file__).parent.parent / "CONTENT"
META_FILE = CONTENT_DIR / "paragraph_templates_v1.meta.jsonl"
TEXT_FILE = CONTENT_DIR / "paragraph_templates_v1.jsonl"


def load_templates():
    """Load all templates"""
    meta_templates = {}
    with open(META_FILE, 'r') as f:
        for line in f:
            if line.strip():
                meta = json.loads(line)
                para_id = meta.get('paragraph_id')
                layer = meta.get('layer', 'unknown')
                base_id = para_id.replace('-INT', '').replace('-CON', '')
                
                if base_id not in meta_templates:
                    meta_templates[base_id] = {
                        'observation': None,
                        'interpretation': None,
                        'context': None,
                        'section': meta.get('section'),
                        'sub_block': meta.get('sub_block'),
                        'meaning_type': meta.get('meaning_type'),
                        'primary_axes': meta.get('primary_axes', []),
                        'secondary_axes': meta.get('secondary_axes', []),
                        'modulators': meta.get('modulators', []),
                        'confidence_level': meta.get('confidence_level', 'medium'),
                        'lite_allowed': meta.get('lite_allowed', True)
                    }
                
                if layer == 'observation':
                    meta_templates[base_id]['observation'] = meta
                elif layer == 'interpretation':
                    meta_templates[base_id]['interpretation'] = meta
                elif layer == 'context':
                    meta_templates[base_id]['context'] = meta
    
    text_templates = {}
    with open(TEXT_FILE, 'r') as f:
        for line in f:
            if line.strip():
                template = json.loads(line)
                para_id = template.get('paragraph_id')
                text_templates[para_id] = template
    
    return meta_templates, text_templates


def generate_int_text(observation_text: str, meaning_type: str, axes: List[str]) -> List[str]:
    """
    Generate interpretation variants based on observation text
    Interpretation explains the 'why' and 'how' behind the pattern
    """
    # This is a placeholder - in production, this would use AI or manual writing
    # For now, we'll create structured templates that follow the pattern
    
    variants = [
        f"This pattern emerges because {meaning_type.lower()} connects with your {axes[0]} axis. The observation reflects how your system processes emotional information.",
        f"When {axes[0]} interacts with your emotional processing, it creates this {meaning_type.lower()} dynamic. Understanding this helps you recognize the pattern without judgment.",
        f"Your {axes[0]} axis shapes how you experience {meaning_type.lower()}. This isn't a flaw - it's how your system organizes emotional data."
    ]
    
    return variants


def generate_con_text(observation_text: str, meaning_type: str, axes: List[str]) -> List[str]:
    """
    Generate context variants - practical guidance for integration
    Context provides actionable steps and integration practices
    """
    variants = [
        f"To work with this pattern, notice when {meaning_type.lower()} appears. Create small pauses to check in with yourself before responding automatically.",
        f"Practice recognizing {meaning_type.lower()} early. When you catch it sooner, you have more choice in how you respond rather than reacting from habit.",
        f"Build a ritual around this pattern: when you notice {meaning_type.lower()}, take a breath and name what you're feeling. This creates space between the pattern and your response."
    ]
    
    return variants


def create_int_template(base_id: str, meta: Dict, observation_text: str) -> Dict:
    """Create interpretation template"""
    int_id = f"{base_id}-INT"
    int_meta = meta['interpretation']
    
    variants = generate_int_text(
        observation_text,
        meta['meaning_type'],
        meta['primary_axes']
    )
    
    template = {
        "paragraph_id": int_id,
        "version": "1.0.0",
        "section": meta['section'],
        "sub_block": meta['sub_block'],
        "meaning_type": meta['meaning_type'],
        "primary_axes": meta['primary_axes'],
        "secondary_axes": meta['secondary_axes'],
        "modulators": meta['modulators'],
        "confidence_level": meta['confidence_level'],
        "lite_allowed": int_meta.get('lite_allowed', True) if int_meta else True,
        "variants": [
            {"variant_id": f"v{i+1}", "text": text}
            for i, text in enumerate(variants)
        ]
    }
    
    return template


def create_con_template(base_id: str, meta: Dict, observation_text: str) -> Dict:
    """Create context template"""
    con_id = f"{base_id}-CON"
    con_meta = meta['context']
    
    variants = generate_con_text(
        observation_text,
        meta['meaning_type'],
        meta['primary_axes']
    )
    
    template = {
        "paragraph_id": con_id,
        "version": "1.0.0",
        "section": meta['section'],
        "sub_block": meta['sub_block'],
        "meaning_type": meta['meaning_type'],
        "primary_axes": meta['primary_axes'],
        "secondary_axes": meta['secondary_axes'],
        "modulators": meta['modulators'],
        "confidence_level": meta['confidence_level'],
        "lite_allowed": con_meta.get('lite_allowed', False) if con_meta else False,
        "variants": [
            {"variant_id": f"v{i+1}", "text": text}
            for i, text in enumerate(variants)
        ]
    }
    
    return template


def main():
    print("Loading templates...")
    meta_templates, text_templates = load_templates()
    
    # Find EP templates that need INT/CON texts
    new_templates = []
    
    for base_id, meta in meta_templates.items():
        if meta['section'] != 'Emotional Patterns':
            continue
        
        obs_meta = meta['observation']
        int_meta = meta['interpretation']
        con_meta = meta['context']
        
        if not obs_meta:
            continue
        
        # Check if observation has text
        obs_id = obs_meta.get('paragraph_id')
        has_obs_text = obs_id in text_templates or base_id in text_templates
        
        if not has_obs_text:
            continue
        
        # Get observation text
        obs_template = text_templates.get(obs_id) or text_templates.get(base_id)
        if not obs_template:
            continue
        
        obs_text = obs_template['variants'][0]['text'] if obs_template.get('variants') else ""
        
        # Check if INT text exists
        if int_meta:
            int_id = int_meta.get('paragraph_id')
            has_int_text = int_id in text_templates
            if not has_int_text:
                print(f"Creating INT template for {base_id}")
                int_template = create_int_template(base_id, meta, obs_text)
                new_templates.append(int_template)
        
        # Check if CON text exists
        if con_meta:
            con_id = con_meta.get('paragraph_id')
            has_con_text = con_id in text_templates
            if not has_con_text:
                print(f"Creating CON template for {base_id}")
                con_template = create_con_template(base_id, meta, obs_text)
                new_templates.append(con_template)
    
    print(f"\nGenerated {len(new_templates)} new templates")
    
    # Append to text file
    if new_templates:
        with open(TEXT_FILE, 'a') as f:
            for template in new_templates:
                f.write(json.dumps(template) + '\n')
        
        print(f"Appended {len(new_templates)} templates to {TEXT_FILE}")
    else:
        print("No new templates to create")


if __name__ == "__main__":
    main()


#!/usr/bin/env python3
"""
Normalize dashes in templates: replace all em dashes (—) with hyphens (-)
This ensures consistency and prevents em dash usage in future templates
"""

import json
from pathlib import Path

CONTENT_DIR = Path(__file__).parent.parent / "CONTENT"
TEXT_FILE = CONTENT_DIR / "paragraph_templates_v1.jsonl"


def normalize_dashes(template: dict) -> dict:
    """Replace all em dashes with hyphens in a template"""
    variants = template.get('variants', [])
    
    for variant in variants:
        if isinstance(variant, dict):
            text = variant.get('text', '')
            if '—' in text:
                variant['text'] = text.replace('—', '-')
    
    return template


def main():
    """Normalize dashes in all templates"""
    templates = []
    fixed_count = 0
    
    with open(TEXT_FILE, 'r') as f:
        for line in f:
            if line.strip():
                template = json.loads(line)
                para_id = template.get('paragraph_id')
                
                original = json.dumps(template)
                normalized = normalize_dashes(template)
                
                if json.dumps(normalized) != original:
                    fixed_count += 1
                
                templates.append(normalized)
    
    if fixed_count > 0:
        print(f"Fixed {fixed_count} templates with em dashes")
        
        with open(TEXT_FILE, 'w') as f:
            for template in templates:
                f.write(json.dumps(template) + '\n')
        
        print(f"✓ Updated {TEXT_FILE}")
    else:
        print("No em dashes found - all templates use hyphens")


if __name__ == "__main__":
    main()


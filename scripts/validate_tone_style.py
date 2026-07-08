#!/usr/bin/env python3
"""
Validate tone and style of all templates against Content Production System rules
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Tuple

CONTENT_DIR = Path(__file__).parent.parent / "CONTENT"
TEXT_FILE = CONTENT_DIR / "paragraph_templates_v1.jsonl"

# Forbidden words/phrases
FORBIDDEN_ABSOLUTES = ['always', 'never', 'must', 'should', 'will', 'cannot', 'can\'t']
FORBIDDEN_DIAGNOSTIC = ['diagnosis', 'disorder', 'syndrome', 'pathology', 'dysfunction']
FORBIDDEN_PRESCRIPTIVE = ['you should', 'you must', 'you need to', 'you have to']

# Required probabilistic language
REQUIRED_PROBABILISTIC = ['may', 'tend to', 'often', 'sometimes', 'can', 'might', 'usually']


def check_forbidden_language(text: str) -> List[str]:
    """Check for forbidden language patterns"""
    issues = []
    text_lower = text.lower()
    
    # Check absolutes
    for word in FORBIDDEN_ABSOLUTES:
        if re.search(r'\b' + word + r'\b', text_lower):
            issues.append(f"Forbidden absolute: '{word}'")
    
    # Check diagnostic language
    for word in FORBIDDEN_DIAGNOSTIC:
        if word in text_lower:
            issues.append(f"Forbidden diagnostic term: '{word}'")
    
    # Check prescriptive commands
    for phrase in FORBIDDEN_PRESCRIPTIVE:
        if phrase in text_lower:
            issues.append(f"Forbidden prescriptive: '{phrase}'")
    
    return issues


def check_probabilistic_language(text: str) -> bool:
    """Check if text uses probabilistic language"""
    text_lower = text.lower()
    return any(word in text_lower for word in REQUIRED_PROBABILISTIC)


def check_emotional_density(text: str) -> bool:
    """Check if text has controlled emotional density"""
    # Count strong emotional words
    strong_emotions = ['devastating', 'overwhelming', 'terrifying', 'crushing', 'destroying']
    count = sum(1 for word in strong_emotions if word in text.lower())
    return count <= 1  # Should have max 1 strong emotional insight


def validate_template(template: Dict) -> Tuple[bool, List[str]]:
    """Validate a single template"""
    issues = []
    para_id = template.get('paragraph_id', '')
    variants = template.get('variants', [])
    
    # Check variants
    if not variants or len(variants) < 3:
        issues.append(f"Template {para_id}: Less than 3 variants")
    
    for variant in variants:
        if not isinstance(variant, dict):
            continue
        
        text = variant.get('text', '')
        if not text or not text.strip():
            issues.append(f"Template {para_id}: Empty variant text")
            continue
        
        # Check forbidden language
        forbidden_issues = check_forbidden_language(text)
        issues.extend([f"{para_id}: {issue}" for issue in forbidden_issues])
        
        # Check probabilistic language
        if not check_probabilistic_language(text):
            issues.append(f"{para_id}: Missing probabilistic language (should use 'may', 'tend to', 'often', etc.)")
        
        # Check emotional density
        if not check_emotional_density(text):
            issues.append(f"{para_id}: High emotional density (too many strong emotional words)")
    
    return len(issues) == 0, issues


def main():
    """Validate all templates"""
    templates = []
    
    with open(TEXT_FILE, 'r') as f:
        for line in f:
            if line.strip():
                templates.append(json.loads(line))
    
    print(f"Validating {len(templates)} templates...")
    print("=" * 80)
    
    valid_count = 0
    invalid_count = 0
    all_issues = []
    
    for template in templates:
        is_valid, issues = validate_template(template)
        if is_valid:
            valid_count += 1
        else:
            invalid_count += 1
            all_issues.extend(issues)
    
    print(f"\nValidation Results:")
    print(f"  Valid: {valid_count}")
    print(f"  Invalid: {invalid_count}")
    print(f"  Total issues: {len(all_issues)}")
    
    if all_issues:
        print(f"\nIssues found (showing first 20):")
        for issue in all_issues[:20]:
            print(f"  - {issue}")
        
        if len(all_issues) > 20:
            print(f"  ... and {len(all_issues) - 20} more issues")
    else:
        print("\n✓ All templates pass validation!")
    
    # Save report
    report_path = CONTENT_DIR / "tone_style_validation.json"
    with open(report_path, 'w') as f:
        json.dump({
            "total": len(templates),
            "valid": valid_count,
            "invalid": invalid_count,
            "issues": all_issues
        }, f, indent=2)
    
    print(f"\nDetailed report saved to: {report_path}")


if __name__ == "__main__":
    main()


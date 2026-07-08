#!/usr/bin/env python3
"""Validate Narrative Engine output against Convention v1 rules."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import List

REPO_ROOT = Path(__file__).resolve().parents[1]
SPEC_DIR = REPO_ROOT / "SPEC"


class ValidationError(Exception):
    """Raised when validation fails."""
    pass


def validate_lite_structure(paragraphs: List[dict]) -> List[str]:
    """Validate Lite report structure according to Convention v1."""
    errors: List[str] = []
    
    # Lite should only contain Observation and Interpretation layers
    allowed_layers = {"observation", "interpretation"}
    
    for paragraph in paragraphs:
        meaning_type = paragraph.get("meaning_type", "").lower()
        # Check if paragraph is from forbidden layers
        if "recovery" in meaning_type.lower() or "growth" in meaning_type.lower():
            errors.append(
                f"Lite report contains forbidden layer: {paragraph.get('paragraph_id', 'unknown')} "
                f"(meaning_type: {meaning_type})"
            )
    
    return errors


def validate_full_structure(sections: List[dict]) -> List[str]:
    """Validate Full report structure according to Convention v1."""
    errors: List[str] = []
    
    # Full report should have all canonical sections
    required_sections = {
        "Executive Summary",
        "Core Personality",
        "Emotional Patterns",
        "Relationships",
        "Career & Responsibility",
        "Money & Security",
        "Life Themes",
        "Practical Integration",
    }
    
    found_sections = {section.get("section", "") for section in sections}
    missing_sections = required_sections - found_sections
    
    if missing_sections:
        errors.append(
            f"Full report missing required sections: {', '.join(sorted(missing_sections))}"
        )
    
    # Check section order (simplified - just verify Executive Summary is first)
    if sections and sections[0].get("section") != "Executive Summary":
        errors.append("Full report must start with Executive Summary section")
    
    return errors


def validate_selection_trace(paragraph: dict) -> List[str]:
    """Validate that SelectionTrace is complete and correct."""
    errors: List[str] = []
    
    trace = paragraph.get("selection_trace")
    if not trace:
        errors.append(
            f"Paragraph {paragraph.get('paragraph_id', 'unknown')} missing selection_trace"
        )
        return errors
    
    required_fields = ["paragraph_id", "meaning_type", "confidence_level", "rule_ids"]
    for field in required_fields:
        if field not in trace:
            errors.append(
                f"SelectionTrace for {paragraph.get('paragraph_id', 'unknown')} missing field: {field}"
            )
    
    if trace.get("confidence_level") not in ["high", "medium", "low"]:
        errors.append(
            f"Invalid confidence_level in SelectionTrace: {trace.get('confidence_level')}"
        )
    
    if not trace.get("rule_ids") or len(trace.get("rule_ids", [])) == 0:
        errors.append(
            f"SelectionTrace for {paragraph.get('paragraph_id', 'unknown')} missing rule_ids"
        )
    
    return errors


def validate_paragraph_text(paragraph: dict) -> List[str]:
    """Validate paragraph text quality."""
    errors: List[str] = []
    
    text = paragraph.get("text", "")
    if not text or not text.strip():
        errors.append(
            f"Paragraph {paragraph.get('paragraph_id', 'unknown')} has empty text"
        )
        return errors
    
    # Check for forbidden patterns (from Convention v1)
    forbidden_patterns = [
        ("must", "directive"),
        ("should", "directive"),
        ("always", "absolute"),
        ("never", "absolute"),
        ("destiny", "fatalistic"),
        ("fate", "fatalistic"),
        ("karma", "fatalistic"),
    ]
    
    text_lower = text.lower()
    for pattern, category in forbidden_patterns:
        if pattern in text_lower:
            errors.append(
                f"Paragraph {paragraph.get('paragraph_id', 'unknown')} contains forbidden {category} word: '{pattern}'"
            )
    
    return errors


def validate_report(report_data: dict, report_type: str = "lite") -> List[str]:
    """Validate a complete report against Convention v1."""
    all_errors: List[str] = []
    
    if report_type == "lite":
        paragraphs = report_data.get("paragraphs", [])
        all_errors.extend(validate_lite_structure(paragraphs))
        
        for paragraph in paragraphs:
            all_errors.extend(validate_selection_trace(paragraph))
            all_errors.extend(validate_paragraph_text(paragraph))
    
    elif report_type == "full":
        sections = report_data.get("sections", [])
        all_errors.extend(validate_full_structure(sections))
        
        for section in sections:
            for paragraph in section.get("paragraphs", []):
                all_errors.extend(validate_selection_trace(paragraph))
                all_errors.extend(validate_paragraph_text(paragraph))
    
    return all_errors


def main() -> None:
    """Main validation entry point."""
    if len(sys.argv) < 2:
        print("Usage: validate_narrative_convention.py <report.json> [lite|full]")
        sys.exit(1)
    
    report_path = Path(sys.argv[1])
    report_type = sys.argv[2] if len(sys.argv) > 2 else "lite"
    
    if not report_path.exists():
        print(f"Error: Report file not found: {report_path}")
        sys.exit(1)
    
    try:
        with report_path.open(encoding="utf-8") as f:
            report_data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {report_path}: {e}")
        sys.exit(1)
    
    errors = validate_report(report_data, report_type)
    
    if errors:
        print(f"Validation failed with {len(errors)} error(s):\n")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
    
    print(f"Validation passed: {report_type} report conforms to Convention v1")


if __name__ == "__main__":
    main()


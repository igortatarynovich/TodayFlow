# Paragraph Templates

Paragraph templates provide structured content for EP (Emotional Patterns), RL (Relationships), CR (Career), MS (Money & Security), and LT (Life Themes) sections.

## Existing Structure

Paragraph templates already exist in:
- `CONTENT/paragraph_templates_v1.jsonl` - Text variants
- `CONTENT/paragraph_templates_v1.meta.jsonl` - Metadata

## Current Format

Each paragraph template contains:

**Metadata:**
- `paragraph_id` - Unique identifier (e.g., `EP-A2A7-BASE-001`)
- `version` - Version number
- `section` - Section name (Emotional Patterns, Relationships, etc.)
- `sub_block` - Sub-block name
- `meaning_type` - Semantic description
- `primary_axes` - Primary axes (e.g., ["A2"])
- `secondary_axes` - Secondary axes (e.g., ["A7"])
- `modulators` - Modulators (e.g., ["M3"])
- `confidence_level` - Confidence level
- `lite_allowed` - Whether allowed in lite version
- `variants` - Array of variant objects

**Variants:**
- `variant_id` - Variant ID (v1, v2, v3)
- `text` - Text content

## Integration with Content System

Paragraph templates are already well-structured and can be integrated into the Content System with:

1. **Semantic fields** (already present):
   - `meaning_type`
   - `primary_axes`, `secondary_axes`
   - `modulators`
   - `section`, `sub_block`

2. **Human Layer** (to be added):
   - Transform `text` variants through Human Layer
   - Ensure human-understandable language
   - Remove abstract/mystical phrases

## Migration Notes

- Paragraph templates are already in JSONL format (good!)
- Need to ensure Human Layer is applied to all text variants
- Metadata structure is already well-designed
- Integration with Content System is straightforward


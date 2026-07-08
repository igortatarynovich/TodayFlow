# Human Layer

Human Layer transforms semantic instructions into human-readable, understandable text.

## Purpose

The Human Layer converts:
- Semantic fields (themes, guidance, description, intention, etc.) → human_text
- Removes abstract/mystical phrases
- Makes language human and understandable
- Adds context and coherence

## Principles

1. **Human-understandable language**
   - No abstract phrases like "your system", "nervous system", "emotional access"
   - No mystical language
   - Simple, concrete words

2. **Context and coherence**
   - Connect semantic pieces into flowing text
   - Add natural transitions
   - Make relationships clear

3. **Clarity over complexity**
   - Clear, direct statements
   - Avoid jargon
   - Focus on what matters to the user

## Example Transformation

**Input (semantic):**
```json
{
  "themes": "Fine-tuning strategy, securing resources",
  "guidance": "Check details, expectations, and resources"
}
```

**Output (human_text):**
```
This is a good moment to check details: agreements, timelines, and resources. Fine-tune your strategy, secure resources, and align collaborators.
```

## Implementation

Human Layer can be implemented as:

1. **Rule-based system** - Templates and patterns
2. **LLM-based system** - Transform semantic → human text
3. **Hybrid system** - Rules + LLM for complex cases

## Integration

Human Layer processes:
- `forecasts/*.json` - Adds `human_text` to moon_phases, weekly, planetary_events
- `practices/*.json` - Adds `human_text` to mantras, check_ins, tarot_spreads
- `rituals/*.json` - Adds `human_text` to rituals
- `daily/*.json` - Adds `human_text` to daily templates
- `paragraphs/*.jsonl` - Transforms variant texts

## Status

🚧 **In Development**

The Human Layer system is currently being designed and implemented.


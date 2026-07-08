# i18n Module - Translation Function Updates

## Changes After Cleanup

After cleaning up duplicate variants in `CONTENT/i18n/en.json`, the translation function was updated to handle mixed key structure:

### Before Cleanup
- All paragraph template keys had variant suffixes: `EP-A2A7-BASE-001.v1`, `EP-A2A7-BASE-001.v2`, etc.
- Code always used: `translate(f"{paragraph_id}.{variant_id}")`

### After Cleanup
- Keys with unique text: still have variants (`.v1`, `.v2`, `.v3`)
- Keys with duplicate text: converted to base key without suffix (e.g., `EP-A2A7-STRESS-007-INT`)

### Fallback Logic

The `translate()` function now implements fallback:

1. **Try exact key first**: `EP-A2A7-BASE-001.v1`
2. **If not found and key contains `.v`**: Try base key `EP-A2A7-BASE-001`
3. **English fallback**: Same logic for English locale
4. **Default**: Return provided default or key itself

This ensures backward compatibility while supporting the cleaned structure.

### Example

```python
# Key with variant that exists
translate("EP-A2A7-BASE-001.v1")  # Returns text for .v1

# Key with variant that was removed (duplicate), base key exists
translate("EP-A2A7-STRESS-007-INT.v1")  # Falls back to EP-A2A7-STRESS-007-INT

# Non-existent key
translate("NONEXISTENT.v1", default="Default text")  # Returns "Default text"
```


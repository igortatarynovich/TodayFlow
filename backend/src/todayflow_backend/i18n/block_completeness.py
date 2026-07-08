"""
Utilities for checking block completeness in translations.

Critical rule: Never mix languages within a single block.
If a block is incomplete in target locale, show entire block in EN or hide it.
"""

from typing import List, Set
from . import translate, _load_catalog, _get_base_locale, DEFAULT_LOCALE


def is_block_complete(keys: List[str], locale: str) -> bool:
    """
    Check if all keys for a block are available in locale.
    
    Checks in order:
    1. Exact locale
    2. Base locale (if regional variant)
    3. English (always complete)
    
    Args:
        keys: List of translation keys for a block
        locale: Target locale (e.g., "es-MX", "ru")
    
    Returns:
        True if all keys are available in locale (or base/EN fallback)
        False if any key is missing (would show [MISSING:key])
    """
    if not keys:
        return True
    
    # Load catalogs
    target_catalog = _load_catalog(locale)
    base_locale = _get_base_locale(locale)
    base_catalog = _load_catalog(base_locale) if base_locale and base_locale != locale else {}
    en_catalog = _load_catalog("en") if locale != "en" else {}
    
    # Check each key
    for key in keys:
        # Try exact key
        if _key_exists(key, target_catalog):
            continue
        
        # Try base locale
        if base_catalog and _key_exists(key, base_catalog):
            continue
        
        # Try English
        if en_catalog and _key_exists(key, en_catalog):
            continue
        
        # Key not found anywhere
        return False
    
    return True


def _key_exists(key: str, catalog: dict) -> bool:
    """Check if key exists in catalog (with variant fallback)."""
    if key in catalog:
        return True
    
    # For variant keys, check base key
    if ".v" in key:
        base_key = key.rsplit(".", 1)[0]
        if base_key in catalog:
            return True
    
    return False


def get_block_locale(keys: List[str], preferred_locale: str) -> str:
    """
    Determine which locale to use for a block.
    
    Returns:
        - preferred_locale if block is complete in it
        - base locale if block is complete in base
        - "en" if block is complete in English
        - "en" if block is incomplete (fallback to English)
    """
    if not keys:
        return preferred_locale
    
    # Check preferred locale
    if is_block_complete(keys, preferred_locale):
        return preferred_locale
    
    # Check base locale
    base_locale = _get_base_locale(preferred_locale)
    if base_locale and base_locale != preferred_locale:
        if is_block_complete(keys, base_locale):
            return base_locale
    
    # Fallback to English (always complete)
    return "en"


def get_missing_keys(keys: List[str], locale: str) -> Set[str]:
    """
    Get list of keys missing in locale (even with fallback).
    
    Useful for parity checking and coverage reports.
    """
    missing = set()
    
    target_catalog = _load_catalog(locale)
    base_locale = _get_base_locale(locale)
    base_catalog = _load_catalog(base_locale) if base_locale and base_locale != locale else {}
    en_catalog = _load_catalog("en")
    
    for key in keys:
        if _key_exists(key, target_catalog):
            continue
        if base_catalog and _key_exists(key, base_catalog):
            continue
        if _key_exists(key, en_catalog):
            continue
        missing.add(key)
    
    return missing


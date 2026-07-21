"""Lightweight application i18n catalog for non-paragraph copy."""

from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Set

from fastapi import Request

DEFAULT_LOCALE = os.getenv("TODAYFLOW_LOCALE", "ru")


def _content_root() -> Path:
    env_root = os.getenv("CONTENT_DIR")
    if env_root:
        return Path(env_root)
    module_path = Path(__file__).resolve()
    for depth in (4, 3, 2):
        if len(module_path.parents) > depth:
            candidate = module_path.parents[depth] / "CONTENT"
            if candidate.exists():
                return candidate
    return module_path.parents[3] / "CONTENT"


def _catalog_path(locale: str) -> Path:
    return _content_root() / "i18n" / f"app.{locale}.json"


def _get_base_locale(locale: str) -> str | None:
    """
    Extract base locale from regional variant.
    Examples: es-MX -> es, pt-BR -> pt, de-CH -> de
    """
    if "-" in locale:
        return locale.split("-")[0]
    return None


@lru_cache(maxsize=None)
def _load_catalog(locale: str) -> Dict[str, str]:
    """
    Load both app.{locale}.json (UI texts) and {locale}.json (paragraph templates)
    
    Supports locale fallback hierarchy:
    - es-MX → es → en
    - pt-BR → pt → en
    - etc.
    """
    catalog: Dict[str, str] = {}
    
    # Load app.{locale}.json (UI texts)
    app_path = _catalog_path(locale)
    if app_path.exists():
        try:
            app_data = json.loads(app_path.read_text(encoding="utf-8"))
            catalog.update(app_data)
        except json.JSONDecodeError:
            pass
    
    # Load {locale}.json (paragraph templates)
    para_path = _content_root() / "i18n" / f"{locale}.json"
    if para_path.exists():
        try:
            para_data = json.loads(para_path.read_text(encoding="utf-8"))
            catalog.update(para_data)
        except json.JSONDecodeError:
            pass
    
    return catalog


@lru_cache(maxsize=1)
def _available_locales() -> Set[str]:
    directory = _content_root() / "i18n"
    locales: Set[str] = set()
    if directory.exists():
        for file in directory.glob("app.*.json"):
            stem = file.stem  # e.g., "app.en"
            _, _, code = stem.partition(".")
            if code:
                locales.add(code)
    locales.add("en")
    return locales


def _pick_locale(candidate: str | None) -> str:
    if candidate and candidate in _available_locales():
        return candidate
    if DEFAULT_LOCALE in _available_locales():
        return DEFAULT_LOCALE
    return "ru" if "ru" in _available_locales() else "en"


def locale_from_accept_language(header_value: str | None) -> str | None:
    if not header_value:
        return None
    for token in header_value.split(","):
        lang = token.split(";")[0].strip().lower()
        if not lang:
            continue
        base = lang.split("-")[0]
        if base in _available_locales():
            return base
    return None


def localized_sign_name(sign_id: str, *, locale: str | None = None) -> str:
    """Display name for a zodiac sign id (e.g. aries) from the i18n catalog."""
    sid = (sign_id or "").strip().lower().replace(" ", "_")
    if not sid:
        return ""
    loc = locale or DEFAULT_LOCALE
    return translate(f"sign.{sid}.name", locale=loc, default=sid.replace("_", " ").title())


def request_locale(request: Request | None = None, preferred: str | None = None) -> str:
    if preferred:
        base = preferred.strip().split("-")[0].lower()
        return _pick_locale(base)
    if request is not None:
        header_locale = locale_from_accept_language(request.headers.get("accept-language"))
    else:
        header_locale = None
    if header_locale:
        return header_locale
    return _pick_locale(DEFAULT_LOCALE)


def translate(key: str, *, locale: str | None = None, default: str | None = None, log_missing: bool = True) -> str:
    """
    Return localized string for key with locale fallback hierarchy.
    
    Fallback order:
    1. Exact locale (e.g., es-MX)
    2. Base locale (e.g., es) - if regional variant
    3. English (en)
    4. Default or [MISSING:key]
    
    For paragraph templates (keys like "EP-A2A7-BASE-001.v1"):
    - First tries the exact key (with variant_id)
    - If not found and key contains ".v", tries base key without variant (e.g., "EP-A2A7-BASE-001")
    - This handles cases where duplicates were removed and only base key exists
    
    Args:
        key: Translation key
        locale: Target locale (e.g., "es-MX", "ru", "en")
        default: Default value if key not found
        log_missing: Whether to log missing keys (for debugging)
    """
    import logging
    
    target_locale = locale or DEFAULT_LOCALE
    
    # Try exact locale first
    catalog = _load_catalog(target_locale)
    result = _try_get_key(catalog, key)
    if result:
        return result
    
    # Try base locale if regional variant (e.g., es-MX → es)
    base_locale = _get_base_locale(target_locale)
    if base_locale and base_locale != target_locale:
        base_catalog = _load_catalog(base_locale)
        result = _try_get_key(base_catalog, key)
        if result:
            return result
    
    # Try English fallback
    if target_locale != "en":
        en_catalog = _load_catalog("en")
        result = _try_get_key(en_catalog, key)
        if result:
            return result
    
    # Not found anywhere
    if log_missing:
        logger = logging.getLogger(__name__)
        # Use debug level instead of warning - missing translations are non-critical
        # System continues to work with fallback values
        logger.debug(f"Missing translation key: {key} (locale: {target_locale})")
    
    if default is not None:
        return default
    return f"[MISSING:{key}]"


def _try_get_key(catalog: Dict[str, str], key: str) -> str | None:
    """
    Try to get key from catalog, with fallback for variant keys.
    
    For keys like "EP-A2A7-BASE-001.v1":
    - First tries exact key
    - If not found and key contains ".v", tries base key without variant
    """
    # Try exact key first
    if key in catalog:
        return catalog[key]
    
    # For paragraph template keys with variant (e.g., "EP-A2A7-BASE-001.v1"),
    # try base key without variant if exact key not found
    if ".v" in key:
        base_key = key.rsplit(".", 1)[0]  # Remove ".v1", ".v2", etc.
        if base_key in catalog:
            return catalog[base_key]
    
    return None


def _localize_sequence(prefix: str, values: List[str], *, locale: str | None = None) -> List[str]:
    return [translate(f"{prefix}.{idx}", locale=locale, default=value) for idx, value in enumerate(values, start=1)]


def localize_mantra(source: Dict, *, locale: str | None = None) -> Dict:
    if not source:
        return source
    prefix = f"mantra.{source['id']}"
    localized = dict(source)
    localized["title"] = translate(f"{prefix}.title", locale=locale, default=source.get("title", source["id"]))
    localized["intention"] = translate(f"{prefix}.intention", locale=locale, default=source.get("intention", ""))
    localized["guidance"] = translate(f"{prefix}.guidance", locale=locale, default=source.get("guidance", ""))
    if source.get("notes"):
        localized["notes"] = translate(f"{prefix}.notes", locale=locale, default=source.get("notes"))
    return localized


def localize_ritual(source: Dict, *, locale: str | None = None) -> Dict:
    if not source:
        return source
    prefix = f"ritual.{source['id']}"
    localized = dict(source)
    localized["title"] = translate(f"{prefix}.title", locale=locale, default=source.get("title", source["id"]))
    localized["intention"] = translate(f"{prefix}.intention", locale=locale, default=source.get("intention", ""))
    instructions = source.get("instructions", [])
    if instructions:
        localized["instructions"] = _localize_sequence(f"{prefix}.instructions", instructions, locale=locale)
    if source.get("notes"):
        localized["notes"] = translate(f"{prefix}.notes", locale=locale, default=source.get("notes"))
    return localized


def localize_checkin(prompt: Dict, *, locale: str | None = None) -> Dict:
    if not prompt:
        return prompt
    prefix = f"check_in.{prompt['id']}"
    localized = dict(prompt)
    localized["prompt"] = translate(f"{prefix}.prompt", locale=locale, default=prompt.get("prompt", ""))
    steps = prompt.get("reflection_steps", [])
    if steps:
        localized["reflection_steps"] = _localize_sequence(f"{prefix}.steps", steps, locale=locale)
    if prompt.get("cta"):
        localized["cta"] = translate(f"{prefix}.cta", locale=locale, default=prompt["cta"])
    return localized


def localize_spread_meta(spread: Dict, *, locale: str | None = None) -> Dict:
    prefix = f"tarot.spread.{spread['id']}"
    localized = dict(spread)
    localized["title"] = translate(f"{prefix}.title", locale=locale, default=spread.get("title", spread["id"]))
    localized["description"] = translate(f"{prefix}.description", locale=locale, default=spread.get("description"))
    positions = []
    for position in spread.get("positions", []):
        pos_prefix = f"{prefix}.positions.{position['id']}"
        position_copy = dict(position)
        position_copy["title"] = translate(f"{pos_prefix}.title", locale=locale, default=position.get("title", position["id"]))
        if position.get("prompt"):
            position_copy["prompt"] = translate(f"{pos_prefix}.prompt", locale=locale, default=position["prompt"])
        positions.append(position_copy)
    localized["positions"] = positions
    return localized

#!/usr/bin/env python3
"""
Parity check для i18n файлов.

Проверяет:
1. Какие ключи отсутствуют в других языках (относительно en.json)
2. Coverage по каждому слою: UI / Daily / EP / RL / CR
3. Соответствие структуры ключей
"""

import json
from collections import defaultdict
from pathlib import Path

CONTENT_DIR = Path(__file__).parent.parent / "CONTENT" / "i18n"

# Слои для анализа
LAYERS = {
    "UI": lambda k: k.startswith(("nav.", "footer.", "common.", "home.", "account.", "layout.")),
    "Daily": lambda k: k.startswith("DAILY."),
    "EP": lambda k: k.startswith("EP-"),
    "RL": lambda k: k.startswith("RL-"),
    "CR": lambda k: k.startswith("CR-"),
    "MS": lambda k: k.startswith("MS-"),
    "MC": lambda k: k.startswith("MC-"),
    "Other": lambda k: True,  # Catch-all
}

def load_catalog(locale: str) -> dict:
    """Load catalog for locale."""
    path = CONTENT_DIR / f"{locale}.json"
    if not path.exists():
        return {}
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}

def get_layer(key: str) -> str:
    """Determine which layer a key belongs to."""
    for layer_name, check in LAYERS.items():
        if layer_name == "Other":
            continue
        if check(key):
            return layer_name
    return "Other"

def analyze_parity():
    """Analyze parity between locales."""
    # Load master (EN)
    en_catalog = load_catalog("en")
    if not en_catalog:
        print("❌ en.json not found!")
        return
    
    print("=" * 80)
    print("i18n Parity Check")
    print("=" * 80)
    print(f"\nMaster (en.json): {len(en_catalog)} keys")
    
    # Find all locale files (exclude backups and app files)
    locale_files = list(CONTENT_DIR.glob("*.json"))
    locales = []
    for file in locale_files:
        stem = file.stem
        # Skip backups, app files, and templates
        if (stem == "en" or 
            stem.startswith("app.") or 
            "backup" in stem.lower() or 
            "template" in stem.lower()):
            continue
        locales.append(stem)
    
    if not locales:
        print("\n⚠️  No other locale files found")
        return
    
    print(f"\nChecking locales: {', '.join(sorted(locales))}")
    print()
    
    # Analyze each locale
    for locale in sorted(locales):
        catalog = load_catalog(locale)
        if not catalog:
            print(f"⚠️  {locale}.json not found or empty")
            continue
        
        missing = set(en_catalog.keys()) - set(catalog.keys())
        extra = set(catalog.keys()) - set(en_catalog.keys())
        
        print(f"{'=' * 80}")
        print(f"Locale: {locale}")
        print(f"{'=' * 80}")
        print(f"Total keys: {len(catalog)}")
        print(f"Missing keys: {len(missing)}")
        print(f"Extra keys: {len(extra)}")
        print(f"Coverage: {((len(catalog) - len(extra)) / len(en_catalog) * 100):.1f}%")
        print()
        
        # Coverage by layer
        print("Coverage by layer:")
        layer_stats = defaultdict(lambda: {"total": 0, "present": 0})
        
        for key in en_catalog.keys():
            layer = get_layer(key)
            layer_stats[layer]["total"] += 1
            if key in catalog:
                layer_stats[layer]["present"] += 1
        
        for layer in sorted(layer_stats.keys()):
            stats = layer_stats[layer]
            coverage = (stats["present"] / stats["total"] * 100) if stats["total"] > 0 else 0
            print(f"  {layer:10} {stats['present']:4}/{stats['total']:4} ({coverage:5.1f}%)")
        
        print()
        
        # Show missing keys by layer (first 10 per layer)
        if missing:
            print("Missing keys (sample, first 10 per layer):")
            missing_by_layer = defaultdict(list)
            for key in missing:
                layer = get_layer(key)
                missing_by_layer[layer].append(key)
            
            for layer in sorted(missing_by_layer.keys()):
                keys = sorted(missing_by_layer[layer])[:10]
                print(f"  {layer}: {len(missing_by_layer[layer])} missing")
                for key in keys:
                    print(f"    - {key}")
                if len(missing_by_layer[layer]) > 10:
                    print(f"    ... and {len(missing_by_layer[layer]) - 10} more")
            print()
        
        if extra:
            print(f"⚠️  Extra keys (not in en.json): {len(extra)}")
            for key in sorted(extra)[:10]:
                print(f"    - {key}")
            if len(extra) > 10:
                print(f"    ... and {len(extra) - 10} more")
            print()

def main():
    analyze_parity()

if __name__ == "__main__":
    main()


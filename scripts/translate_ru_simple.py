#!/usr/bin/env python3
"""
Simple batch translator using free translation API.
Translates missing RU translations from EN.
"""

import json
import sys
import time
import urllib.parse
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
EN_FILE = REPO_ROOT / "CONTENT" / "i18n" / "en.json"
RU_FILE = REPO_ROOT / "CONTENT" / "i18n" / "ru.json"

def translate_simple(text: str) -> str:
    """
    Simple translation using libretranslate API (free, open source).
    Fallback: returns empty string if service unavailable.
    """
    try:
        import requests
        url = "https://libretranslate.de/translate"
        data = {
            "q": text,
            "source": "en",
            "target": "ru",
            "format": "text"
        }
        response = requests.post(url, data=data, timeout=10)
        if response.status_code == 200:
            result = response.json()
            return result.get("translatedText", "")
        else:
            print(f"  API error: {response.status_code}")
            return ""
    except ImportError:
        print("  Install requests: pip3 install requests")
        return ""
    except Exception as e:
        print(f"  Error: {e}")
        return ""

def main():
    """Main translation function."""
    print("="*60)
    print("RU Translation Batch Processor")
    print("="*60)
    
    # Load files
    print("\nLoading translation files...")
    with open(EN_FILE, 'r', encoding='utf-8') as f:
        en_data = json.load(f)
    
    with open(RU_FILE, 'r', encoding='utf-8') as f:
        ru_data = json.load(f)
    
    # Find empty translations
    empty_keys = []
    for key in sorted(en_data.keys()):
        ru_value = ru_data.get(key, '')
        if not ru_value or (isinstance(ru_value, str) and ru_value.strip() == ''):
            empty_keys.append(key)
    
    total = len(empty_keys)
    print(f"Found {total} empty translations")
    
    if total == 0:
        print("\n✓ All translations are complete!")
        return
    
    print(f"\nNote: This will translate {total} keys.")
    print("This may take 30-60 minutes for large batches.")
    print("Press Ctrl+C at any time to stop and save progress.\n")
    
    # Start translation
    translated = 0
    failed = []
    start_time = time.time()
    
    try:
        for i, key in enumerate(empty_keys, 1):
            try:
                en_text = en_data[key]
                
                # Skip if text is too short or empty
                if not en_text or len(en_text.strip()) < 5:
                    ru_data[key] = ""
                    continue
                
                print(f"[{i}/{total}] Translating: {key[:50]}...")
                ru_text = translate_simple(en_text)
                
                if ru_text and len(ru_text.strip()) > 0:
                    ru_data[key] = ru_text
                    translated += 1
                    print(f"  ✓ Translated ({len(ru_text)} chars)")
                else:
                    failed.append(key)
                    print(f"  ✗ Translation failed")
                
                # Save progress every 10 translations
                if translated % 10 == 0:
                    with open(RU_FILE, 'w', encoding='utf-8') as f:
                        json.dump(ru_data, f, ensure_ascii=False, indent=2)
                    elapsed = time.time() - start_time
                    rate = translated / elapsed * 60 if elapsed > 0 else 0
                    print(f"  [Progress: {translated}/{total} | Rate: {rate:.1f}/min]")
                
                # Rate limiting
                time.sleep(0.5)
                
            except KeyboardInterrupt:
                print("\n\n⚠ Interrupted by user. Saving progress...")
                break
            except Exception as e:
                failed.append(key)
                print(f"  ✗ Error: {e}")
                time.sleep(1)
        
    except KeyboardInterrupt:
        print("\n\n⚠ Translation interrupted. Saving progress...")
    
    # Final save
    print("\nSaving translations...")
    with open(RU_FILE, 'w', encoding='utf-8') as f:
        json.dump(ru_data, f, ensure_ascii=False, indent=2)
    
    # Summary
    elapsed = time.time() - start_time
    print("\n" + "="*60)
    print("Translation Summary")
    print("="*60)
    print(f"Total keys: {total}")
    print(f"Translated: {translated}")
    print(f"Failed: {len(failed)}")
    print(f"Time elapsed: {elapsed/60:.1f} minutes")
    
    if failed:
        print(f"\n⚠ {len(failed)} keys failed to translate.")
        print("You may need to translate these manually or retry.")
        if len(failed) <= 20:
            print("\nFailed keys:")
            for key in failed:
                print(f"  - {key}")
    else:
        print("\n✓ All translations completed successfully!")

if __name__ == "__main__":
    main()


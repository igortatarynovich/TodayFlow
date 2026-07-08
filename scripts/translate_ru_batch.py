#!/usr/bin/env python3
"""
Batch translate missing RU translations.
Supports multiple translation methods.
"""

import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
EN_FILE = REPO_ROOT / "CONTENT" / "i18n" / "en.json"
RU_FILE = REPO_ROOT / "CONTENT" / "i18n" / "ru.json"

def translate_with_googletrans(text: str) -> str:
    """Translate using googletrans library (free, no API key needed)."""
    try:
        from googletrans import Translator
        translator = Translator()
        result = translator.translate(text, src='en', dest='ru')
        time.sleep(0.1)  # Rate limiting
        return result.text
    except ImportError:
        raise ImportError("Install googletrans: pip install googletrans==4.0.0rc1")
    except Exception as e:
        print(f"Translation error: {e}")
        return ""

def translate_with_deepl(text: str, api_key: str = None) -> str:
    """Translate using DeepL API (requires API key)."""
    if not api_key:
        api_key = os.getenv("DEEPL_API_KEY")
    
    if not api_key:
        raise ValueError("DeepL API key required. Set DEEPL_API_KEY env var or pass as parameter.")
    
    try:
        import requests
        url = "https://api-free.deepl.com/v2/translate"
        params = {
            "auth_key": api_key,
            "text": text,
            "source_lang": "EN",
            "target_lang": "RU"
        }
        response = requests.post(url, data=params)
        response.raise_for_status()
        return response.json()["translations"][0]["text"]
    except ImportError:
        raise ImportError("Install requests: pip install requests")
    except Exception as e:
        print(f"DeepL translation error: {e}")
        return ""

def main():
    """Main translation function."""
    import os
    
    # Load files
    print("Loading translation files...")
    with open(EN_FILE, 'r', encoding='utf-8') as f:
        en_data = json.load(f)
    
    with open(RU_FILE, 'r', encoding='utf-8') as f:
        ru_data = json.load(f)
    
    # Find empty translations
    empty_keys = []
    for key in en_data.keys():
        ru_value = ru_data.get(key, '')
        if not ru_value or (isinstance(ru_value, str) and ru_value.strip() == ''):
            empty_keys.append(key)
    
    total = len(empty_keys)
    print(f"Found {total} empty translations")
    
    if total == 0:
        print("All translations are complete!")
        return
    
    # Choose translation method
    method = os.getenv("TRANSLATE_METHOD", "googletrans")
    
    if method == "googletrans":
        print("\nUsing googletrans (free, no API key needed)...")
        print("Note: This may take a while for large batches...")
        translate_fn = translate_with_googletrans
    elif method == "deepl":
        print("\nUsing DeepL API...")
        translate_fn = lambda t: translate_with_deepl(t)
    else:
        print(f"Unknown method: {method}. Using googletrans.")
        translate_fn = translate_with_googletrans
    
    # Translate in batches
    batch_size = 10
    translated = 0
    failed = []
    
    print(f"\nTranslating {total} keys in batches of {batch_size}...")
    print("Press Ctrl+C to stop and save progress\n")
    
    try:
        for i in range(0, len(empty_keys), batch_size):
            batch = empty_keys[i:i+batch_size]
            print(f"Translating batch {i//batch_size + 1}/{(len(empty_keys)-1)//batch_size + 1}...")
            
            for key in batch:
                try:
                    en_text = en_data[key]
                    ru_text = translate_fn(en_text)
                    
                    if ru_text:
                        ru_data[key] = ru_text
                        translated += 1
                        print(f"  ✓ {key}")
                    else:
                        failed.append(key)
                        print(f"  ✗ {key} (failed)")
                except KeyboardInterrupt:
                    print("\n\nInterrupted by user. Saving progress...")
                    raise
                except Exception as e:
                    failed.append(key)
                    print(f"  ✗ {key}: {e}")
                    time.sleep(1)  # Delay on error
            
            # Save progress after each batch
            with open(RU_FILE, 'w', encoding='utf-8') as f:
                json.dump(ru_data, f, ensure_ascii=False, indent=2)
            
            print(f"  Progress: {translated}/{total} translated\n")
            time.sleep(0.5)  # Brief pause between batches
            
    except KeyboardInterrupt:
        print("\n\nTranslation interrupted. Progress saved.")
    
    # Final save
    with open(RU_FILE, 'w', encoding='utf-8') as f:
        json.dump(ru_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*50}")
    print(f"Translation complete!")
    print(f"Translated: {translated}/{total}")
    if failed:
        print(f"Failed: {len(failed)}")
        print(f"\nFailed keys saved for retry:")
        for key in failed[:10]:
            print(f"  {key}")
        if len(failed) > 10:
            print(f"  ... and {len(failed) - 10} more")

if __name__ == "__main__":
    main()


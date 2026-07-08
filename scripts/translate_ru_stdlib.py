#!/usr/bin/env python3
"""
Batch translator using only Python standard library.
Uses LibreTranslate API (free, no API key needed).
"""

import json
import time
import urllib.request
import urllib.parse
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
EN_FILE = REPO_ROOT / "CONTENT" / "i18n" / "en.json"
RU_FILE = REPO_ROOT / "CONTENT" / "i18n" / "ru.json"

def translate_text(text: str) -> str:
    """Translate text using LibreTranslate API (standard library only)."""
    try:
        url = "https://libretranslate.de/translate"
        data = urllib.parse.urlencode({
            "q": text,
            "source": "en",
            "target": "ru",
            "format": "text"
        }).encode('utf-8')
        
        req = urllib.request.Request(url, data=data, headers={
            'Content-Type': 'application/x-www-form-urlencoded'
        })
        
        with urllib.request.urlopen(req, timeout=15) as response:
            result = json.loads(response.read().decode())
            return result.get("translatedText", "")
    except Exception as e:
        print(f"    Error: {str(e)[:50]}")
        return ""

def main():
    """Main translation function."""
    print("="*70)
    print("RU Translation Batch Processor (Standard Library Only)")
    print("="*70)
    
    # Load files
    print("\n📂 Loading translation files...")
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
    print(f"✓ Loaded {len(en_data)} EN keys, {len(ru_data)} RU keys")
    print(f"⚠ Found {total} empty translations\n")
    
    if total == 0:
        print("✓ All translations are complete!")
        return
    
    print(f"📝 This will translate {total} keys.")
    print(f"⏱  Estimated time: {total * 1.5 / 60:.0f}-{total * 2 / 60:.0f} minutes")
    print(f"💾 Progress is saved every 10 translations")
    print(f"⚠  Press Ctrl+C at any time to stop and save progress\n")
    print("🚀 Starting translation...\n")
    
    # Start translation
    translated = 0
    failed = []
    start_time = time.time()
    
    try:
        for i, key in enumerate(empty_keys, 1):
            try:
                en_text = en_data[key]
                
                # Skip if text is too short
                if not en_text or len(en_text.strip()) < 5:
                    ru_data[key] = ""
                    continue
                
                # Progress indicator
                if i % 5 == 0 or i == 1:
                    elapsed = time.time() - start_time
                    rate = translated / elapsed * 60 if elapsed > 0 and translated > 0 else 0
                    eta = (total - translated) / (rate / 60) if rate > 0 else 0
                    print(f"[{i:4d}/{total}] {key[:45]:45s} | ✓{translated:4d} | {rate:4.1f}/min | ETA: {eta/60:.0f}min")
                
                ru_text = translate_text(en_text)
                
                if ru_text and len(ru_text.strip()) > 0:
                    ru_data[key] = ru_text
                    translated += 1
                else:
                    failed.append(key)
                
                # Save progress every 10 translations
                if translated % 10 == 0:
                    with open(RU_FILE, 'w', encoding='utf-8') as f:
                        json.dump(ru_data, f, ensure_ascii=False, indent=2)
                
                # Rate limiting
                time.sleep(0.8)
                
            except KeyboardInterrupt:
                print("\n\n⚠  Interrupted by user. Saving progress...")
                break
            except Exception as e:
                failed.append(key)
                print(f"    Error on {key}: {e}")
                time.sleep(2)
        
    except KeyboardInterrupt:
        print("\n\n⚠  Translation interrupted. Saving progress...")
    
    # Final save
    print("\n💾 Saving translations...")
    with open(RU_FILE, 'w', encoding='utf-8') as f:
        json.dump(ru_data, f, ensure_ascii=False, indent=2)
    
    # Summary
    elapsed = time.time() - start_time
    print("\n" + "="*70)
    print("Translation Summary")
    print("="*70)
    print(f"Total keys processed: {total}")
    print(f"Successfully translated: {translated} ({translated/total*100:.1f}%)")
    print(f"Failed: {len(failed)} ({len(failed)/total*100:.1f}%)")
    print(f"Time elapsed: {elapsed/60:.1f} minutes")
    print(f"Average rate: {translated/elapsed*60:.1f} translations/minute" if elapsed > 0 else "")
    
    if failed:
        print(f"\n⚠  {len(failed)} keys failed to translate.")
        print("You may need to translate these manually or retry.")
        if len(failed) <= 10:
            print("\nFirst failed keys:")
            for key in failed[:10]:
                print(f"  - {key}")
    else:
        print("\n✓ All translations completed successfully!")

if __name__ == "__main__":
    main()


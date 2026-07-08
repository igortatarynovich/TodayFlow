#!/usr/bin/env python3
"""
Translate remaining English texts in app.ru.json to Russian.
"""

import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
I18N_DIR = REPO_ROOT / "CONTENT" / "i18n"
EN_PATH = I18N_DIR / "app.en.json"
RU_PATH = I18N_DIR / "app.ru.json"


def translate_text(en_text: str, key: str = "") -> str:
    """
    Translate English text to Russian.
    Many technical terms and UI labels can remain in English or use transliteration.
    """
    
    # Dictionary of translations
    translations = {
        # Mantras
        "Solar Radiance": "Солнечное сияние",
        "Lunar Soften": "Лунное смягчение",
        
        # Rituals  
        "Grounding Salt Bath": "Заземляющая солевая ванна",
        "Solar Walk Intent": "Солнечная прогулка с намерением",
        
        # Tarot
        "Clarity Triad": "Триада ясности",
        "Origin": "Исток",
        "Pattern": "Паттерн",
        "Integration": "Интеграция",
        "Alignment Cross": "Крест выравнивания",
        "Mind": "Ум",
        "Heart": "Сердце",
        "Body": "Тело",
        
        # Dashboard
        "Weekly Insight": "Недельное прозрение",
        "Lite Preview": "Предпросмотр Lite",
        "Aspect Focus": "Фокус аспекта",
        "Guided Check-in": "Направленная проверка",
        
        # Orientation loops - могут оставаться на английском как брендинг
        "Loop A": "Петля A",
        "Loop B": "Петля B", 
        "Loop C": "Петля C",
        "TRANSIT · Loop C": "ТРАНЗИТ · Петля C",
        "ARCANA · Tarot Flow": "АРКАНЫ · Tarot Flow",
        
        # Facets
        "Facet Preview": "Предпросмотр грани",
        "Facet tease · unlock all facets": "Пробный фрагмент грани · разблокируй все грани",
        "Lite mode · Context locked": "Режим Lite · Контекст заблокирован",
    }
    
    # Check exact match
    if en_text in translations:
        return translations[en_text]
    
    # For template strings with placeholders, keep as is
    if '{' in en_text:
        return en_text
    
    # For technical terms that are commonly used in Russian tech context,
    # we can transliterate or keep in English
    # For now, return empty to indicate needs manual translation
    return ""


def main():
    """Translate English texts in app.ru.json"""
    print("=" * 70)
    print("Translating app.ru.json")
    print("=" * 70)
    
    # Load files
    with open(EN_PATH, 'r', encoding='utf-8') as f:
        en_data = json.load(f)
    
    with open(RU_PATH, 'r', encoding='utf-8') as f:
        ru_data = json.load(f)
    
    print(f"EN keys: {len(en_data)}")
    print(f"RU keys: {len(ru_data)}")
    
    # Find English texts
    cyrillic_pattern = re.compile(r'[А-Яа-яЁё]')
    english_keys = []
    for key in ru_data.keys():
        value = ru_data[key]
        if isinstance(value, str) and value.strip():
            if not cyrillic_pattern.search(value):
                english_keys.append(key)
    
    print(f"\nFound {len(english_keys)} keys with English text")
    
    # Translate
    translated_count = 0
    for key in english_keys:
        en_value = en_data.get(key, ru_data[key])
        ru_value = ru_data[key]
        
        # Translate if matches EN exactly
        if ru_value == en_value:
            translation = translate_text(en_value, key)
            if translation:
                ru_data[key] = translation
                translated_count += 1
    
    print(f"Translated {translated_count} keys")
    
    # Save
    with open(RU_PATH, 'w', encoding='utf-8') as f:
        json.dump(ru_data, f, ensure_ascii=False, indent=2)
    
    print(f"✓ Saved to {RU_PATH}")
    
    # Check remaining
    remaining = []
    for key in ru_data.keys():
        value = ru_data[key]
        if isinstance(value, str) and value.strip():
            if not cyrillic_pattern.search(value):
                remaining.append(key)
    
    if remaining:
        print(f"\nRemaining {len(remaining)} English keys (may be intentional - technical terms):")
        for key in remaining[:10]:
            print(f"  {key}: {ru_data[key]}")


if __name__ == "__main__":
    main()


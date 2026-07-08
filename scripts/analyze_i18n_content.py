#!/usr/bin/env python3
"""
Анализ контента в i18n файлах для реорганизации

Находит:
1. Точные дубликаты (.v1/.v2/.v3 с одинаковым текстом)
2. Мета-фразы ("Your X axis influences...")
3. Статистику по типам контента
"""

import json
import re
from collections import defaultdict
from pathlib import Path

CONTENT_DIR = Path(__file__).parent.parent / "CONTENT" / "i18n"
EN_JSON = CONTENT_DIR / "en.json"

def normalize_text(text):
    """Нормализует текст для сравнения"""
    return ' '.join(text.split())

def find_exact_duplicates(data):
    """Находит точные дубликаты в вариантах .v1/.v2/.v3"""
    base_groups = defaultdict(list)
    
    for key in data.keys():
        base_key = re.sub(r'\.v[123]$', '', key)
        base_groups[base_key].append(key)
    
    duplicates = []
    for base, variants in base_groups.items():
        if len(variants) > 1:
            texts = {}
            for variant in variants:
                text = normalize_text(data[variant])
                if text in texts:
                    duplicates.append({
                        'base': base,
                        'duplicate_variant': variant,
                        'original_variant': texts[text],
                        'text': text[:100] + '...' if len(text) > 100 else text
                    })
                else:
                    texts[text] = variant
    
    return duplicates

def find_meta_phrases(data):
    """Находит тексты с мета-фразами про axis"""
    meta_pattern = re.compile(
        r'Your\s+(A[1-7]|M[1-4])\s+axis\s+(shapes|influences)\s+how\s+(this\s+pattern\s+shows\s+up|this\s+shows\s+up)',
        re.I
    )
    
    found = []
    for key, value in data.items():
        if meta_pattern.search(value):
            # Находим начало мета-фразы
            match = meta_pattern.search(value)
            start_pos = match.start()
            context = value[max(0, start_pos-50):start_pos+100]
            
            found.append({
                'key': key,
                'text': value,
                'context': context
            })
    
    return found

def analyze_content_structure(data):
    """Анализирует структуру контента"""
    stats = defaultdict(int)
    patterns = {
        'EP': re.compile(r'^EP-'),
        'RL': re.compile(r'^RL-'),
        'CR': re.compile(r'^CR-'),
        'MS': re.compile(r'^MS-'),
        'MC': re.compile(r'^MC-'),
    }
    
    for key in data.keys():
        found = False
        for pattern_name, pattern in patterns.items():
            if pattern.match(key):
                stats[pattern_name] += 1
                found = True
                break
        if not found:
            stats['Other'] += 1
    
    return stats

def main():
    print("=" * 80)
    print("Анализ контента в en.json")
    print("=" * 80)
    print()
    
    # Загружаем данные
    with open(EN_JSON, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"Всего ключей: {len(data)}")
    print()
    
    # 1. Статистика по типам
    print("1. Структура контента:")
    print("-" * 80)
    stats = analyze_content_structure(data)
    for key, count in sorted(stats.items()):
        print(f"  {key}: {count} ключей")
    print()
    
    # 2. Дубликаты
    print("2. Поиск точных дубликатов:")
    print("-" * 80)
    duplicates = find_exact_duplicates(data)
    print(f"Найдено дубликатов: {len(duplicates)}")
    
    if duplicates:
        # Группируем по базовому ключу
        dup_by_base = defaultdict(list)
        for dup in duplicates:
            dup_by_base[dup['base']].append(dup)
        
        print(f"Уникальных базовых ключей с дубликатами: {len(dup_by_base)}")
        print("\nПримеры (первые 10):")
        for base, dups in list(dup_by_base.items())[:10]:
            print(f"\n  {base}:")
            for dup in dups[:2]:
                print(f"    - {dup['original_variant']} и {dup['duplicate_variant']}")
                print(f"      Текст: {dup['text'][:80]}...")
    print()
    
    # 3. Мета-фразы
    print("3. Поиск мета-фраз про 'axis':")
    print("-" * 80)
    meta_phrases = find_meta_phrases(data)
    print(f"Найдено текстов с мета-фразами: {len(meta_phrases)}")
    
    if meta_phrases:
        print("\nПримеры (первые 5):")
        for item in meta_phrases[:5]:
            print(f"\n  {item['key']}:")
            print(f"    {item['text'][:150]}...")
    print()
    
    # 4. Рекомендации
    print("4. Рекомендации:")
    print("-" * 80)
    print(f"  • Удалить {len(duplicates)} дублирующих вариантов")
    print(f"  • Очистить {len(meta_phrases)} текстов от мета-фраз")
    print(f"  • Потенциальная экономия: ~{len(duplicates) + len(meta_phrases)} ключей")
    
    # Сохраняем результаты
    output = {
        'total_keys': len(data),
        'structure': dict(stats),
        'duplicates_count': len(duplicates),
        'meta_phrases_count': len(meta_phrases),
        'duplicates_sample': duplicates[:20],
        'meta_phrases_sample': meta_phrases[:20]
    }
    
    output_file = CONTENT_DIR.parent / "i18n_analysis.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\nПодробные результаты сохранены в: {output_file}")

if __name__ == "__main__":
    main()


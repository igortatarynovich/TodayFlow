#!/usr/bin/env python3
"""
Анализ качества i18n текстов

Проверяет:
1. INT/CON тексты (длина, стиль)
2. Повторы "you may notice"
3. Семантические повторы
4. Короткие тексты-лейблы
"""

import json
import re
from collections import defaultdict, Counter
from pathlib import Path

CONTENT_DIR = Path(__file__).parent.parent / "CONTENT" / "i18n"
EN_JSON = CONTENT_DIR / "en.json"

# Паттерны для анализа
YOU_MAY_NOTICE = re.compile(r'\byou may notice\b', re.I)
SHORT_TEXT_THRESHOLD = 50  # символов
MIN_SENTENCE_WORDS = 10  # минимум слов для полноценного предложения

# Семантические паттерны (для поиска повторов)
SEMANTIC_PATTERNS = {
    'OVERTHINKING': [
        r'overthink',
        r'analysis loop',
        r'decision paralysis',
        r'thinking to avoid',
        r'mental.*shield',
    ],
    'WITHDRAWAL': [
        r'withdraw',
        r'pull back',
        r'distance',
        r'retreat',
    ],
    'SHUTDOWN': [
        r'shutdown',
        r'emotional.*off',
        r'reduce.*input',
        r'quieting',
    ],
    'PEOPLE_PLEASING': [
        r'people.*pleas',
        r'harmony.*cost',
        r'yes.*quickly',
        r'smooth.*over',
    ],
}

def analyze_int_con_quality(data):
    """Анализ качества INT/CON текстов"""
    int_keys = [k for k in data.keys() if '-INT' in k or '-CON' in k]
    
    issues = {
        'too_short': [],  # < 50 символов
        'single_phrase': [],  # одна фраза, не предложение
        'you_may_notice': [],  # содержит "you may notice"
        'meta_label': [],  # звучит как мета-лейбл
    }
    
    for key in int_keys:
        text = data[key]
        word_count = len(text.split())
        char_count = len(text)
        
        # Слишком короткий
        if char_count < SHORT_TEXT_THRESHOLD:
            issues['too_short'].append((key, text, char_count))
        
        # Одна фраза (нет точки или точка в конце одной фразы)
        if word_count < MIN_SENTENCE_WORDS and '.' not in text[:-1]:
            issues['single_phrase'].append((key, text, word_count))
        
        # "You may notice"
        if YOU_MAY_NOTICE.search(text):
            issues['you_may_notice'].append((key, text))
        
        # Мета-лейбл (очень короткий + звучит как лейбл)
        if char_count < 60 and (
            'as ' in text.lower() or
            'defense' in text.lower() or
            'pattern' in text.lower() and char_count < 50
        ):
            issues['meta_label'].append((key, text))
    
    return issues, len(int_keys)

def analyze_you_may_notice(data):
    """Подсчёт "you may notice" по слоям"""
    counts = defaultdict(int)
    total = defaultdict(int)
    examples = defaultdict(list)
    
    for key, text in data.items():
        # Определяем слой
        layer = 'Other'
        if key.startswith('EP-'):
            layer = 'EP'
        elif key.startswith('RL-'):
            layer = 'RL'
        elif key.startswith('CR-'):
            layer = 'CR'
        elif key.startswith('MS-'):
            layer = 'MS'
        elif key.startswith('DAILY.'):
            layer = 'Daily'
        
        total[layer] += 1
        
        if YOU_MAY_NOTICE.search(text):
            counts[layer] += 1
            if len(examples[layer]) < 5:
                examples[layer].append((key, text[:100]))
    
    return counts, total, examples

def find_semantic_repeats(data):
    """Поиск семантических повторов"""
    repeats = defaultdict(list)
    
    for key, text in data.items():
        text_lower = text.lower()
        
        for pattern_name, patterns in SEMANTIC_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    repeats[pattern_name].append((key, text[:100]))
                    break
    
    return repeats

def main():
    print("=" * 80)
    print("Анализ качества i18n текстов")
    print("=" * 80)
    print()
    
    # Загружаем данные
    with open(EN_JSON, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"Всего ключей: {len(data)}")
    print()
    
    # 1. Анализ INT/CON
    print("1. Анализ INT/CON текстов:")
    print("-" * 80)
    issues, total_int_con = analyze_int_con_quality(data)
    
    print(f"Всего INT/CON ключей: {total_int_con}")
    print(f"Слишком коротких (<{SHORT_TEXT_THRESHOLD} символов): {len(issues['too_short'])}")
    print(f"Одна фраза (<{MIN_SENTENCE_WORDS} слов): {len(issues['single_phrase'])}")
    print(f"Содержат 'you may notice': {len(issues['you_may_notice'])}")
    print(f"Звучат как мета-лейблы: {len(issues['meta_label'])}")
    print()
    
    if issues['too_short']:
        print("Примеры слишком коротких INT/CON:")
        for key, text, count in issues['too_short'][:5]:
            print(f"  {key} ({count} символов):")
            print(f"    {text}")
        print()
    
    if issues['meta_label']:
        print("Примеры мета-лейблов:")
        for key, text in issues['meta_label'][:5]:
            print(f"  {key}:")
            print(f"    {text}")
        print()
    
    # 2. "You may notice" по слоям
    print("2. Распределение 'you may notice' по слоям:")
    print("-" * 80)
    counts, total, examples = analyze_you_may_notice(data)
    
    for layer in sorted(counts.keys()):
        count = counts[layer]
        tot = total[layer]
        percentage = (count / tot * 100) if tot > 0 else 0
        status = "⚠️" if percentage > 40 else "✅"
        print(f"{status} {layer:10} {count:4}/{tot:4} ({percentage:5.1f}%)")
    print()
    
    # 3. Семантические повторы
    print("3. Семантические повторы:")
    print("-" * 80)
    repeats = find_semantic_repeats(data)
    
    for pattern_name, matches in sorted(repeats.items(), key=lambda x: len(x[1]), reverse=True):
        if len(matches) > 3:
            status = "⚠️" if len(matches) > 5 else "✓"
            print(f"{status} {pattern_name:20} {len(matches):3} повторений")
            if len(matches) > 3:
                print("   Примеры:")
                for key, text in matches[:3]:
                    print(f"     {key}: {text}...")
    print()
    
    # Рекомендации
    print("4. Рекомендации:")
    print("-" * 80)
    
    total_issues = (
        len(issues['too_short']) +
        len(issues['single_phrase']) +
        len(issues['meta_label'])
    )
    
    if total_issues > 0:
        print(f"⚠️  Критично исправить: {total_issues} INT/CON текстов")
        print("   - Привести к минимум 1 полноценному предложению")
        print("   - Убрать мета-лейблы")
        print()
    
    high_ynm_layers = [layer for layer in counts if total[layer] > 0 and (counts[layer] / total[layer] * 100) > 40]
    if high_ynm_layers:
        print(f"⚠️  Слишком много 'you may notice' в: {', '.join(high_ynm_layers)}")
        print("   - Уменьшить до <40%")
        print()
    
    high_repeats = [name for name, matches in repeats.items() if len(matches) > 5]
    if high_repeats:
        print(f"⚠️  Семантические повторы: {', '.join(high_repeats)}")
        print("   - Одна мысль не должна повторяться >3–4 раз")
        print()

if __name__ == "__main__":
    main()


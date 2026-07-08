#!/usr/bin/env python3
"""
Детальный анализ семантических повторов в i18n текстах.

Цель: найти тексты с одинаковой или очень похожей мыслью,
чтобы переформулировать их с разных углов.
"""
import json
import re
from collections import defaultdict
from pathlib import Path
from difflib import SequenceMatcher

EN_JSON = Path(__file__).parent.parent / "CONTENT" / "i18n" / "en.json"

# Семантические кластеры для анализа
SEMANTIC_CLUSTERS = {
    'WITHDRAWAL': {
        'keywords': ['withdraw', 'pull back', 'distance', 'retreat', 'shutdown', 
                     'go quiet', 'switch to standby', 'reduce input', 'quietly pull back',
                     'detachment', 'standby', 'shut down', 'step back', 'pause',
                     'quiet internal processing', 'quietly drain', 'carrying more',
                     'emotional.*off', 'reduce.*input', 'quieting'],
        'core_meaning': 'emotional withdrawal or distancing under stress'
    },
    'OVERTHINKING': {
        'keywords': ['overthink', 'analysis loop', 'decision paralysis', 'delays commitment',
                     'thinking can loop', 'analyze.*repeatedly', 'delaying action',
                     'endless analysis', 'searching for.*right.*interpretation',
                     'mental.*shield', 'analysis.*shield'],
        'core_meaning': 'excessive analysis leading to inaction or delay'
    },
}

def similarity(text1, text2):
    """Вычисляет схожесть двух текстов (0-1)"""
    return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()

def find_cluster_matches(data, cluster_name, keywords):
    """Находит все тексты, относящиеся к кластеру"""
    matches = []
    for key, text in data.items():
        text_lower = text.lower()
        for pattern in keywords:
            if re.search(pattern, text_lower):
                matches.append((key, text))
                break
    return matches

def group_similar_texts(texts, threshold=0.4):
    """Группирует похожие тексты"""
    groups = []
    used = set()
    
    for i, (key1, text1) in enumerate(texts):
        if i in used:
            continue
        
        group = [(key1, text1)]
        used.add(i)
        
        for j, (key2, text2) in enumerate(texts[i+1:], start=i+1):
            if j in used:
                continue
            
            sim = similarity(text1, text2)
            if sim >= threshold:
                group.append((key2, text2))
                used.add(j)
        
        if len(group) > 1:
            groups.append(group)
    
    return groups

def analyze_cluster(data, cluster_name, cluster_info):
    """Анализирует один семантический кластер"""
    keywords = cluster_info['keywords']
    matches = find_cluster_matches(data, cluster_name, keywords)
    
    if len(matches) <= 3:
        return matches, []
    
    # Группируем похожие тексты
    groups = group_similar_texts(matches, threshold=0.4)
    
    return matches, groups

def extract_layer(key):
    """Извлекает слой из ключа"""
    if key.startswith('EP-'):
        return 'EP'
    elif key.startswith('RL-'):
        return 'RL'
    elif key.startswith('CR-'):
        return 'CR'
    elif key.startswith('MS-'):
        return 'MS'
    elif key.startswith('LT-'):
        return 'LT'
    elif key.startswith('DAILY.'):
        return 'Daily'
    return 'Other'

def extract_section(key):
    """Извлекает секцию (BASE, STRESS, RECOV, GROW, etc.)"""
    parts = key.split('-')
    if len(parts) >= 3:
        return parts[-2] if parts[-1].startswith('INT') or parts[-1].startswith('CON') else parts[-1]
    return 'Unknown'

def main():
    print("=" * 80)
    print("Детальный анализ семантических повторов")
    print("=" * 80)
    print()
    
    # Загружаем данные
    with open(EN_JSON, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"Всего ключей: {len(data)}\n")
    
    # Анализируем каждый кластер
    for cluster_name, cluster_info in SEMANTIC_CLUSTERS.items():
        print(f"\n{'='*80}")
        print(f"Кластер: {cluster_name}")
        print(f"Смысл: {cluster_info['core_meaning']}")
        print(f"{'='*80}\n")
        
        matches, groups = analyze_cluster(data, cluster_name, cluster_info)
        
        print(f"Всего найдено текстов: {len(matches)}")
        print(f"Групп похожих текстов (>40% схожести): {len(groups)}\n")
        
        # Статистика по слоям
        layer_counts = defaultdict(int)
        section_counts = defaultdict(int)
        for key, text in matches:
            layer_counts[extract_layer(key)] += 1
            section_counts[extract_section(key)] += 1
        
        print("По слоям:")
        for layer, count in sorted(layer_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {layer:10} {count:3}")
        
        print("\nПо секциям:")
        for section, count in sorted(section_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {section:10} {count:3}")
        
        # Показываем группы похожих текстов
        if groups:
            print(f"\n⚠️  Найдено {len(groups)} групп похожих текстов (требуют переформулировки):\n")
            for i, group in enumerate(groups[:10], 1):  # Показываем первые 10
                print(f"Группа {i} ({len(group)} текстов):")
                for key, text in group[:3]:  # Показываем первые 3 из группы
                    layer = extract_layer(key)
                    section = extract_section(key)
                    print(f"  [{layer:6} {section:8}] {key}")
                    print(f"    {text[:120]}...")
                if len(group) > 3:
                    print(f"    ... и еще {len(group)-3} похожих текстов")
                print()
        
        # Рекомендации
        if len(matches) > 4:
            print(f"\n💡 Рекомендации для {cluster_name}:")
            print(f"   - Всего {len(matches)} текстов с этой темой (целевой максимум: 3-4)")
            print(f"   - Переформулировать {len(matches)-4} текстов с других углов")
            print(f"   - Оставить уникальные версии в разных секциях (BASE, STRESS, RECOV, GROW)")
            print()
    
    print("\n" + "="*80)
    print("Итоговые рекомендации:")
    print("="*80)
    print()
    print("1. Переформулировать повторяющиеся тексты с разных углов:")
    print("   - Разные секции → разные акценты (BASE vs STRESS vs RECOV)")
    print("   - Разные слои → разные контексты (EP vs RL vs CR)")
    print()
    print("2. Оставить максимум 3-4 уникальных выражения одной мысли")
    print()
    print("3. При переформулировке:")
    print("   - Менять фокус (процесс vs результат vs причина)")
    print("   - Менять тон (описательный vs рекомендательный)")
    print("   - Менять детализацию (общее vs конкретное)")

if __name__ == "__main__":
    main()


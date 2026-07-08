"""
TodayFlow Auto Insights Generator

Генерирует автоматические выводы на основе данных трекера и дневника.
Ключевая магия: "меня видят".
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from collections import Counter


class InsightGenerator:
    """Генератор автоматических инсайтов на основе данных трекера."""
    
    def __init__(self, tracker_path: str, diary_path: str, lexicon_path: str):
        self.tracker_path = tracker_path
        self.diary_path = diary_path
        self.lexicon_path = lexicon_path
        
    def load_data(self) -> Dict:
        """Загружает данные из JSON файлов."""
        with open(self.tracker_path, 'r', encoding='utf-8') as f:
            tracker_data = json.load(f)
        with open(self.diary_path, 'r', encoding='utf-8') as f:
            diary_data = json.load(f)
        return {
            'tracker': tracker_data,
            'diary': diary_data
        }
    
    def detect_streak(self, user_id: str, practice_id: str, days: int = 3) -> Optional[Dict]:
        """Обнаруживает серию выполнения практики."""
        data = self.load_data()
        entries = [e for e in data['tracker']['tracking_entries'] 
                  if e.get('user_id') == user_id and e.get('completed')]
        
        if len(entries) < days:
            return None
        
        # Сортируем по дате
        entries.sort(key=lambda x: x['date'])
        
        # Проверяем последние N дней подряд
        recent_dates = [datetime.strptime(e['date'], '%Y-%m-%d') for e in entries[-days:]]
        if len(recent_dates) < days:
            return None
        
        # Проверяем, что даты идут подряд
        is_streak = all(
            (recent_dates[i+1] - recent_dates[i]).days == 1 
            for i in range(len(recent_dates)-1)
        )
        
        if is_streak:
            return {
                'type': 'streak',
                'streak_days': days,
                'practice_id': practice_id,
                'completion_rate': 1.0,
                'insight_text': f"Ты держишь фокус уже {days} дня подряд — это меняет ритм."
            }
        return None
    
    def detect_pattern(self, user_id: str, lookback_days: int = 7) -> Optional[Dict]:
        """Обнаруживает паттерны в поведении."""
        data = self.load_data()
        entries = [e for e in data['tracker']['tracking_entries'] 
                  if e.get('user_id') == user_id and e.get('completed')]
        
        if len(entries) < 3:
            return None
        
        # Анализируем практики с паузой
        pause_practices = [e for e in entries if 'pause' in e.get('practice_id', '').lower() 
                          or 'practice.001' in e.get('practice_id', '')]
        
        if len(pause_practices) >= 3:
            # Проверяем улучшение состояния
            states = [e.get('state_scale', 3) for e in pause_practices if e.get('state_scale')]
            if len(states) >= 3:
                improvement = (states[-1] - states[0]) / 5.0 if states else 0
                if improvement > 0.2:
                    return {
                        'type': 'pattern',
                        'pattern': 'slowing_down',
                        'days_with_pause': len(pause_practices),
                        'state_improvement': improvement,
                        'insight_text': "Сопротивление снижается, когда ты не торопишься."
                    }
        return None
    
    def detect_shift(self, user_id: str, practice_id: str, baseline_days: int = 7) -> Optional[Dict]:
        """Обнаруживает изменение частоты выбора практики."""
        data = self.load_data()
        entries = [e for e in data['tracker']['tracking_entries'] 
                  if e.get('user_id') == user_id]
        
        if len(entries) < baseline_days * 2:
            return None
        
        # Разделяем на два периода
        mid_point = len(entries) // 2
        first_period = entries[:mid_point]
        second_period = entries[mid_point:]
        
        # Считаем частоту выбора практики
        first_freq = sum(1 for e in first_period if e.get('practice_id') == practice_id) / len(first_period)
        second_freq = sum(1 for e in second_period if e.get('practice_id') == practice_id) / len(second_period)
        
        if second_freq > first_freq * 1.3:  # Увеличение на 30%+
            return {
                'type': 'shift',
                'practice_id': practice_id,
                'frequency_increase': (second_freq - first_freq) / first_freq if first_freq > 0 else 0,
                'baseline_days': baseline_days,
                'insight_text': "Ты чаще выбираешь паузу, чем раньше."
            }
        return None
    
    def generate_insight(self, user_id: str, date: str) -> Optional[Dict]:
        """Генерирует инсайт для пользователя на дату."""
        insights = []
        
        # Проверяем серии
        streak = self.detect_streak(user_id, 'practice.001', days=3)
        if streak:
            insights.append(streak)
        
        # Проверяем паттерны
        pattern = self.detect_pattern(user_id, lookback_days=7)
        if pattern:
            insights.append(pattern)
        
        # Проверяем сдвиги
        shift = self.detect_shift(user_id, 'practice.001', baseline_days=7)
        if shift:
            insights.append(shift)
        
        # Возвращаем первый найденный инсайт
        if insights:
            insight = insights[0]
            return {
                'id': f"insight.{datetime.now().strftime('%Y%m%d%H%M%S')}",
                'user_id': user_id,
                'date': date,
                'type': insight['type'],
                'insight_text': insight['insight_text'],
                'data_points': {k: v for k, v in insight.items() if k != 'type' and k != 'insight_text'},
                'created_at': datetime.now().isoformat() + 'Z'
            }
        return None


if __name__ == '__main__':
    generator = InsightGenerator(
        tracker_path='progress_tracker.json',
        diary_path='observation_diary.json',
        lexicon_path='../lexicon/lexicon.json'
    )
    
    # Пример использования
    insight = generator.generate_insight('user.example', '2026-01-27')
    if insight:
        print(json.dumps(insight, indent=2, ensure_ascii=False))

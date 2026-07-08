"""
TodayFlow Reflection Generator

Генератор отражений на основе всех компонентов системы.
Интегрирует: Lexicon, Practices, Tracker, Diary, Insights, Weekly Integration.
"""

import json
from datetime import datetime
from typing import Dict, List, Optional
import random


class ReflectionGenerator:
    """Генератор отражений — финальный компонент контура влияния."""
    
    def __init__(
        self,
        lexicon_path: str,
        practices_path: str,
        tracker_path: str,
        diary_path: str,
        insights_path: str,
        weekly_path: str
    ):
        self.lexicon_path = lexicon_path
        self.practices_path = practices_path
        self.tracker_path = tracker_path
        self.diary_path = diary_path
        self.insights_path = insights_path
        self.weekly_path = weekly_path
    
    def load_all_data(self) -> Dict:
        """Загружает все данные из JSON файлов."""
        with open(self.lexicon_path, 'r', encoding='utf-8') as f:
            lexicon = json.load(f)
        with open(self.practices_path, 'r', encoding='utf-8') as f:
            practices = json.load(f)
        with open(self.tracker_path, 'r', encoding='utf-8') as f:
            tracker = json.load(f)
        with open(self.diary_path, 'r', encoding='utf-8') as f:
            diary = json.load(f)
        with open(self.insights_path, 'r', encoding='utf-8') as f:
            insights = json.load(f)
        with open(self.weekly_path, 'r', encoding='utf-8') as f:
            weekly = json.load(f)
        
        return {
            'lexicon': lexicon,
            'practices': practices,
            'tracker': tracker,
            'diary': diary,
            'insights': insights,
            'weekly': weekly
        }
    
    def generate_daily_reflection(
        self,
        user_id: str,
        date: str,
        forecast_type: str,
        layers: List[str]
    ) -> Dict:
        """Генерирует дневное отражение на основе всех данных."""
        data = self.load_all_data()
        
        # 1. Выбираем фразы из Lexicon по типу прогноза и слоям
        lexicon_phrases = [
            p for p in data['lexicon']['phrases']
            if forecast_type in p.get('forecast_types', [])
            and any(layer in p.get('layers', []) for layer in layers)
        ]
        
        if not lexicon_phrases:
            # Fallback: любые фразы для типа прогноза
            lexicon_phrases = [
                p for p in data['lexicon']['phrases']
                if forecast_type in p.get('forecast_types', [])
            ]
        
        # Выбираем случайную фразу для темы
        theme_phrase = random.choice(lexicon_phrases) if lexicon_phrases else None
        
        # 2. Выбираем практику на основе типа прогноза
        practices = [
            p for p in data['practices']['practices']
            if forecast_type in p.get('forecast_types', [])
            and any(layer in p.get('layers', []) for layer in layers)
        ]
        
        recommended_practice = random.choice(practices) if practices else None
        
        # 3. Проверяем последние инсайты пользователя
        user_insights = [
            i for i in data['insights']['insights']
            if i.get('user_id') == user_id
            and i.get('date') <= date
        ]
        latest_insight = user_insights[-1] if user_insights else None
        
        # 4. Проверяем последние записи дневника
        user_diary = [
            d for d in data['diary']['diary_entries']
            if d.get('user_id') == user_id
            and d.get('date') <= date
        ]
        latest_diary = user_diary[-1] if user_diary else None
        
        # 5. Собираем отражение
        reflection = {
            'date': date,
            'user_id': user_id,
            'forecast_type': forecast_type,
            'layers': layers,
            'theme': {
                'phrase_id': theme_phrase['id'] if theme_phrase else None,
                'phrase_text': theme_phrase['text'] if theme_phrase else None
            },
            'recommended_practice': {
                'practice_id': recommended_practice['id'] if recommended_practice else None,
                'practice_title': recommended_practice['title'] if recommended_practice else None,
                'practice_instruction': recommended_practice['instruction'] if recommended_practice else None
            },
            'insight': {
                'insight_text': latest_insight['insight_text'] if latest_insight else None,
                'insight_type': latest_insight['type'] if latest_insight else None
            },
            'diary_note': {
                'noticed': latest_diary['noticed'] if latest_diary else None,
                'hardest': latest_diary['hardest'] if latest_diary else None
            },
            'created_at': datetime.now().isoformat() + 'Z'
        }
        
        return reflection
    
    def generate_weekly_reflection(
        self,
        user_id: str,
        week_start: str,
        week_end: str
    ) -> Dict:
        """Генерирует недельное отражение."""
        data = self.load_all_data()
        
        # Находим недельную интеграцию
        weekly_integration = [
            w for w in data['weekly']['weekly_integrations']
            if w.get('user_id') == user_id
            and w.get('week_start') == week_start
            and w.get('week_end') == week_end
        ]
        
        if not weekly_integration:
            return None
        
        integration = weekly_integration[0]
        
        return {
            'week_start': week_start,
            'week_end': week_end,
            'user_id': user_id,
            'integration_text': integration['integration_text'],
            'data_points': integration['data_points'],
            'created_at': datetime.now().isoformat() + 'Z'
        }


if __name__ == '__main__':
    generator = ReflectionGenerator(
        lexicon_path='../lexicon/lexicon.json',
        practices_path='../practices/practices.json',
        tracker_path='progress_tracker.json',
        diary_path='observation_diary.json',
        insights_path='auto_insights.json',
        weekly_path='weekly_integration.json'
    )
    
    # Пример дневного отражения
    daily = generator.generate_daily_reflection(
        user_id='user.example',
        date='2026-01-27',
        forecast_type='workday_focus',
        layers=['L1', 'L2']
    )
    
    print("Daily Reflection:")
    print(json.dumps(daily, indent=2, ensure_ascii=False))
    
    # Пример недельного отражения
    weekly = generator.generate_weekly_reflection(
        user_id='user.example',
        week_start='2026-01-20',
        week_end='2026-01-26'
    )
    
    if weekly:
        print("\nWeekly Reflection:")
        print(json.dumps(weekly, indent=2, ensure_ascii=False))

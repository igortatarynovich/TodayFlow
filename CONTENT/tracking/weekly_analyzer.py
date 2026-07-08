"""
TodayFlow Weekly Integration Analyzer

Анализирует недельные данные и генерирует интеграционный текст.
Не отчёт, не разбор. Один абзац.
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from collections import Counter


class WeeklyAnalyzer:
    """Анализатор недельных данных для генерации интеграционного текста."""
    
    def __init__(self, tracker_path: str, diary_path: str):
        self.tracker_path = tracker_path
        self.diary_path = diary_path
    
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
    
    def analyze_week(self, user_id: str, week_start: str, week_end: str) -> Dict:
        """Анализирует неделю и генерирует интеграционный текст."""
        data = self.load_data()
        
        # Фильтруем записи за неделю
        week_entries = [
            e for e in data['tracker']['tracking_entries']
            if e.get('user_id') == user_id
            and week_start <= e.get('date', '') <= week_end
        ]
        
        diary_entries = [
            e for e in data['diary']['diary_entries']
            if e.get('user_id') == user_id
            and week_start <= e.get('date', '') <= week_end
        ]
        
        if not week_entries:
            return None
        
        # Анализируем состояния и триггеры
        states = [e.get('state', 'normal') for e in week_entries if e.get('state')]
        triggers = []
        for entry in week_entries:
            # Извлекаем триггеры из практик (если есть связь)
            if entry.get('practice_id'):
                triggers.append('practice_used')
        
        most_common_state = Counter(states).most_common(1)[0][0] if states else 'normal'
        most_common_trigger = Counter(triggers).most_common(1)[0][0] if triggers else 'general'
        
        # Анализируем практики
        practices_used = list(set([
            e.get('practice_id') for e in week_entries 
            if e.get('practice_id') and e.get('completed')
        ]))
        
        completion_rate = sum(1 for e in week_entries if e.get('completed')) / len(week_entries) if week_entries else 0
        
        # Определяем, где удержался и где отпустил
        completed_practices = [e.get('practice_id') for e in week_entries if e.get('completed')]
        where_held = 'pause_before_reaction' if 'practice.001' in completed_practices else 'general_practice'
        where_released = 'task_switching' if len(completed_practices) < len(week_entries) * 0.7 else None
        
        # Генерируем текст
        state_text = self._format_state(most_common_state)
        practice_text = self._format_practice(where_held)
        
        integration_text = f"За эту неделю ты чаще всего сталкивался с {state_text}. И всё же ты удерживал {practice_text}. Это формирует новый ритм."
        
        return {
            'week_start': week_start,
            'week_end': week_end,
            'user_id': user_id,
            'integration_text': integration_text,
            'data_points': {
                'most_common_state': most_common_state,
                'most_common_trigger': most_common_trigger,
                'practices_held': practices_used[:3],  # Топ-3
                'completion_rate': round(completion_rate, 2),
                'where_held': where_held,
                'where_released': where_released
            },
            'created_at': datetime.now().isoformat() + 'Z'
        }
    
    def _format_state(self, state: str) -> str:
        """Форматирует состояние для текста."""
        state_map = {
            'overload': 'перегрузом задач',
            'tension': 'напряжением',
            'uncertainty': 'неопределённостью',
            'waiting': 'ожиданием',
            'normal': 'обычным ритмом'
        }
        return state_map.get(state, state)
    
    def _format_practice(self, practice_key: str) -> str:
        """Форматирует практику для текста."""
        practice_map = {
            'pause_before_reaction': 'паузу перед реакцией',
            'focus_practice': 'фокус',
            'body_practice': 'связь с телом',
            'general_practice': 'практику'
        }
        return practice_map.get(practice_key, 'практику')


if __name__ == '__main__':
    analyzer = WeeklyAnalyzer(
        tracker_path='progress_tracker.json',
        diary_path='observation_diary.json'
    )
    
    # Пример использования
    week_analysis = analyzer.analyze_week(
        user_id='user.example',
        week_start='2026-01-20',
        week_end='2026-01-26'
    )
    
    if week_analysis:
        print(json.dumps(week_analysis, indent=2, ensure_ascii=False))

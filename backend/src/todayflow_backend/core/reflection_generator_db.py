"""Генератор отражений для контура влияния - адаптирован для работы с БД."""

import random
from datetime import datetime, date
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from todayflow_backend.db.models import (
    ProgressTrackerEntry,
    ObservationDiaryEntry,
    AutoInsight,
    WeeklyIntegration
)
from todayflow_backend.core.content_loader import load_lexicon, load_practices


class ReflectionGeneratorDB:
    """Генератор отражений — финальный компонент контура влияния."""
    
    def __init__(self, db: Session):
        self.db = db
        self._lexicon_cache = None
        self._practices_cache = None
    
    def _load_lexicon(self) -> Dict:
        """Загружает Lexicon (с кешированием)."""
        if self._lexicon_cache is None:
            self._lexicon_cache = load_lexicon()
        return self._lexicon_cache
    
    def _load_practices(self) -> Dict:
        """Загружает Practices (с кешированием)."""
        if self._practices_cache is None:
            self._practices_cache = load_practices()
        return self._practices_cache
    
    def generate_daily_reflection(
        self,
        user_id: int,
        target_date: str,
        forecast_type: str,
        layers: List[str]
    ) -> Dict:
        """Генерирует дневное отражение на основе всех данных."""
        lexicon = self._load_lexicon()
        practices = self._load_practices()
        
        target_date_obj = datetime.strptime(target_date, '%Y-%m-%d').date()
        
        # 1. Выбираем фразы из Lexicon по типу прогноза и слоям
        lexicon_phrases = [
            p for p in lexicon.get('phrases', [])
            if forecast_type in p.get('forecast_types', [])
            and any(layer in p.get('layers', []) for layer in layers)
        ]
        
        if not lexicon_phrases:
            # Fallback: любые фразы для типа прогноза
            lexicon_phrases = [
                p for p in lexicon.get('phrases', [])
                if forecast_type in p.get('forecast_types', [])
            ]
        
        # Выбираем случайную фразу для темы
        theme_phrase = random.choice(lexicon_phrases) if lexicon_phrases else None
        
        # 2. Выбираем практику на основе типа прогноза
        practices_list = [
            p for p in practices.get('practices', [])
            if forecast_type in p.get('forecast_types', [])
            and any(layer in p.get('layers', []) for layer in layers)
        ]
        
        recommended_practice = random.choice(practices_list) if practices_list else None
        
        # 3. Проверяем последние инсайты пользователя
        latest_insight = self.db.query(AutoInsight).filter(
            and_(
                AutoInsight.user_id == user_id,
                AutoInsight.date <= target_date_obj
            )
        ).order_by(AutoInsight.date.desc()).first()
        
        # 4. Проверяем последние записи дневника
        latest_diary = self.db.query(ObservationDiaryEntry).filter(
            and_(
                ObservationDiaryEntry.user_id == user_id,
                ObservationDiaryEntry.date <= target_date_obj
            )
        ).order_by(ObservationDiaryEntry.date.desc()).first()
        
        # 5. Собираем отражение
        reflection = {
            'date': target_date,
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
                'insight_text': latest_insight.insight_text if latest_insight else None,
                'insight_type': latest_insight.type if latest_insight else None
            } if latest_insight else None,
            'diary_note': {
                'noticed': latest_diary.noticed if latest_diary else None,
                'hardest': latest_diary.hardest if latest_diary else None
            } if latest_diary else None
        }
        
        return reflection
    
    def generate_weekly_reflection(
        self,
        user_id: int,
        week_start: str,
        week_end: str
    ) -> Optional[Dict]:
        """Генерирует недельное отражение."""
        week_start_date = datetime.strptime(week_start, '%Y-%m-%d').date()
        week_end_date = datetime.strptime(week_end, '%Y-%m-%d').date()
        
        # Находим недельную интеграцию
        weekly_integration = self.db.query(WeeklyIntegration).filter(
            and_(
                WeeklyIntegration.user_id == user_id,
                WeeklyIntegration.week_start == week_start_date,
                WeeklyIntegration.week_end == week_end_date
            )
        ).first()
        
        if not weekly_integration:
            return None
        
        return {
            'week_start': week_start,
            'week_end': week_end,
            'integration_text': weekly_integration.integration_text,
            'data_points': weekly_integration.data_points
        }

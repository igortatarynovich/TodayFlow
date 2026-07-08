"""Генераторы для контура влияния - адаптированы для работы с БД."""

import sys
from pathlib import Path
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional
from collections import Counter
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from todayflow_backend.db.models import (
    ProgressTrackerEntry,
    ObservationDiaryEntry,
    AutoInsight,
    WeeklyIntegration,
    DayConnection,
)
from todayflow_backend.core.content_loader import load_lexicon, load_practices


class InsightGeneratorDB:
    """Генератор автоматических инсайтов на основе данных из БД."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def detect_streak(self, user_id: int, practice_id: str, days: int = 3) -> Optional[Dict]:
        """Обнаруживает серию выполнения практики."""
        entries = self.db.query(ProgressTrackerEntry).filter(
            and_(
                ProgressTrackerEntry.user_id == user_id,
                ProgressTrackerEntry.completed == True,
                ProgressTrackerEntry.affirmation_id == practice_id
            )
        ).order_by(ProgressTrackerEntry.date.desc()).limit(days).all()
        
        if len(entries) < days:
            return None
        
        # Проверяем, что даты идут подряд
        dates = [e.date for e in entries]
        dates.sort()
        
        is_streak = all(
            (dates[i+1] - dates[i]).days == 1 
            for i in range(len(dates)-1)
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
    
    def detect_pattern(self, user_id: int, lookback_days: int = 7) -> Optional[Dict]:
        """Обнаруживает паттерны в поведении."""
        cutoff_date = date.today() - timedelta(days=lookback_days)
        
        entries = self.db.query(ProgressTrackerEntry).filter(
            and_(
                ProgressTrackerEntry.user_id == user_id,
                ProgressTrackerEntry.completed == True,
                ProgressTrackerEntry.date >= cutoff_date,
                ProgressTrackerEntry.affirmation_id.like('%pause%')
            )
        ).all()
        
        if len(entries) < 3:
            return None
        
        # Проверяем улучшение состояния
        states = [e.state_scale for e in entries if e.state_scale]
        if len(states) >= 3:
            improvement = (states[-1] - states[0]) / 5.0 if states else 0
            if improvement > 0.2:
                return {
                    'type': 'pattern',
                    'pattern': 'slowing_down',
                    'days_with_pause': len(entries),
                    'state_improvement': improvement,
                    'insight_text': "Сопротивление снижается, когда ты не торопишься."
                }
        return None
    
    def detect_shift(self, user_id: int, practice_id: str, baseline_days: int = 7) -> Optional[Dict]:
        """Обнаруживает изменение частоты выбора практики."""
        cutoff_date = date.today() - timedelta(days=baseline_days * 2)
        
        entries = self.db.query(ProgressTrackerEntry).filter(
            and_(
                ProgressTrackerEntry.user_id == user_id,
                ProgressTrackerEntry.date >= cutoff_date
            )
        ).order_by(ProgressTrackerEntry.date).all()
        
        if len(entries) < baseline_days * 2:
            return None
        
        # Разделяем на два периода
        mid_point = len(entries) // 2
        first_period = entries[:mid_point]
        second_period = entries[mid_point:]
        
        # Считаем частоту выбора практики
        first_freq = sum(1 for e in first_period if e.affirmation_id == practice_id) / len(first_period) if first_period else 0
        second_freq = sum(1 for e in second_period if e.affirmation_id == practice_id) / len(second_period) if second_period else 0
        
        if second_freq > first_freq * 1.3:  # Увеличение на 30%+
            return {
                'type': 'shift',
                'practice_id': practice_id,
                'frequency_increase': (second_freq - first_freq) / first_freq if first_freq > 0 else 0,
                'baseline_days': baseline_days,
                'insight_text': "Ты чаще выбираешь паузу, чем раньше."
            }
        return None
    
    def detect_correlation(self, user_id: int, lookback_days: int = 14) -> Optional[Dict]:
        """Обнаруживает корреляции между активностями и настроением (Daylio-style)."""
        cutoff_date = date.today() - timedelta(days=lookback_days)
        
        # Получаем все записи за период
        entries = self.db.query(ProgressTrackerEntry).filter(
            and_(
                ProgressTrackerEntry.user_id == user_id,
                ProgressTrackerEntry.date >= cutoff_date,
                ProgressTrackerEntry.state_scale.isnot(None)
            )
        ).all()
        
        if len(entries) < 7:  # Минимум 7 дней данных
            return None
        
        # Группируем по активности и считаем среднее настроение
        activity_mood_map: Dict[str, List[int]] = {}
        for entry in entries:
            if entry.affirmation_id:
                activity = entry.affirmation_id
            elif entry.asceticism_id:
                activity = entry.asceticism_id
            else:
                continue
            
            if activity not in activity_mood_map:
                activity_mood_map[activity] = []
            if entry.state_scale:
                activity_mood_map[activity].append(entry.state_scale)
        
        # Находим активность с самым высоким средним настроением
        best_activity = None
        best_avg_mood = 0
        confidence = "low"
        
        for activity, moods in activity_mood_map.items():
            if len(moods) >= 3:  # Минимум 3 записи для статистики
                avg_mood = sum(moods) / len(moods)
                if avg_mood > best_avg_mood:
                    best_avg_mood = avg_mood
                    best_activity = activity
                    # Уровень уверенности: больше записей = выше уверенность
                    if len(moods) >= 10:
                        confidence = "high"
                    elif len(moods) >= 5:
                        confidence = "medium"
        
        if best_activity and best_avg_mood >= 3.5:  # Только если настроение выше среднего
            activity_name = best_activity.replace('practice.', '').replace('affirmation.', '')
            return {
                'type': 'correlation',
                'activity': best_activity,
                'activity_name': activity_name,
                'avg_mood': round(best_avg_mood, 1),
                'data_points_count': len(activity_mood_map[best_activity]),
                'confidence': confidence,
                'insight_text': f"В дни с {activity_name} настроение в среднем выше ({best_avg_mood:.1f}/5)."
            }
        
        return None
    
    def detect_weekend_pattern(self, user_id: int, lookback_days: int = 30) -> Optional[Dict]:
        """Обнаруживает паттерн: дневник чаще в выходные."""
        cutoff_date = date.today() - timedelta(days=lookback_days)
        
        diary_entries = self.db.query(ObservationDiaryEntry).filter(
            and_(
                ObservationDiaryEntry.user_id == user_id,
                ObservationDiaryEntry.date >= cutoff_date
            )
        ).all()
        
        if len(diary_entries) < 5:
            return None
        
        # Считаем записи по дням недели (0 = понедельник, 6 = воскресенье)
        weekday_count = 0
        weekend_count = 0
        
        for entry in diary_entries:
            day_of_week = entry.date.weekday()
            if day_of_week < 5:  # Понедельник-пятница
                weekday_count += 1
            else:  # Суббота-воскресенье
                weekend_count += 1
        
        # Если выходных записей больше на 30%+
        total = weekday_count + weekend_count
        if total > 0 and weekend_count / total > 0.6:  # Больше 60% в выходные
            confidence = "high" if total >= 10 else "medium" if total >= 5 else "low"
            return {
                'type': 'weekend_pattern',
                'weekend_percentage': round((weekend_count / total) * 100, 1),
                'total_entries': total,
                'confidence': confidence,
                'insight_text': f"Дневник чаще в выходные ({weekend_count} из {total} записей)."
            }
        
        return None

    def detect_signal_closure_pattern(self, user_id: int, lookback_days: int = 10) -> Optional[Dict]:
        """Обнаруживает паттерн собранности/несобранности дня по ritual feedback."""
        cutoff_date = date.today() - timedelta(days=lookback_days)

        connections = self.db.query(DayConnection).filter(
            and_(
                DayConnection.user_id == user_id,
                DayConnection.date >= cutoff_date,
            )
        ).order_by(DayConnection.date.desc()).all()

        relevant = [item for item in connections if item.ritual_feedback]
        if len(relevant) < 3:
            return None

        yes_days = sum(1 for item in relevant if item.ritual_feedback == "yes")
        no_days = sum(1 for item in relevant if item.ritual_feedback == "no")
        partial_days = sum(1 for item in relevant if item.ritual_feedback == "partial")

        if no_days >= 3 and no_days >= yes_days:
            confidence = "high" if no_days >= 4 else "medium"
            return {
                "type": "signal_closure",
                "pattern": "closure_gap",
                "days_reviewed": len(relevant),
                "ritual_feedback_yes_days": yes_days,
                "ritual_feedback_no_days": no_days,
                "ritual_feedback_partial_days": partial_days,
                "confidence": confidence,
                "insight_text": "По ответам дня видно, что неделе часто не хватало спокойного завершения и сбора дня в целое."
            }

        if yes_days >= 3 and yes_days > no_days:
            confidence = "high" if yes_days >= 5 else "medium"
            return {
                "type": "signal_closure",
                "pattern": "closure_strength",
                "days_reviewed": len(relevant),
                "ritual_feedback_yes_days": yes_days,
                "ritual_feedback_no_days": no_days,
                "ritual_feedback_partial_days": partial_days,
                "confidence": confidence,
                "insight_text": "По ответам дня видно, что ты всё чаще собираешь день до чувства завершенности, а не просто доживаешь его."
            }
        return None

    def detect_signal_clarity_pattern(self, user_id: int, lookback_days: int = 10) -> Optional[Dict]:
        """Обнаруживает повторяющуюся неясность или ясность решений."""
        cutoff_date = date.today() - timedelta(days=lookback_days)

        connections = self.db.query(DayConnection).filter(
            and_(
                DayConnection.user_id == user_id,
                DayConnection.date >= cutoff_date,
            )
        ).order_by(DayConnection.date.desc()).all()

        relevant = [item for item in connections if item.quick_decision_answer]
        if len(relevant) < 3:
            return None

        unclear_days = sum(1 for item in relevant if item.quick_decision_answer == "unclear")
        yes_days = sum(1 for item in relevant if item.quick_decision_answer == "yes")

        if unclear_days >= 3:
            confidence = "high" if unclear_days >= 4 else "medium"
            return {
                "type": "signal_clarity",
                "pattern": "clarity_gap",
                "days_reviewed": len(relevant),
                "unclear_decision_days": unclear_days,
                "clear_decision_days": yes_days,
                "confidence": confidence,
                "insight_text": "В быстрых ответах дня повторяется одна тема: решение часто не собирается до ясного `да`, а зависает между вариантами."
            }

        if yes_days >= 3 and yes_days > unclear_days:
            confidence = "high" if yes_days >= 5 else "medium"
            return {
                "type": "signal_clarity",
                "pattern": "clarity_strength",
                "days_reviewed": len(relevant),
                "unclear_decision_days": unclear_days,
                "clear_decision_days": yes_days,
                "confidence": confidence,
                "insight_text": "Быстрые ответы дня показывают, что ты всё чаще доходишь до понятного решения, а не застреваешь в неясности."
            }
        return None

    def detect_signal_focus_pattern(self, user_id: int, lookback_days: int = 14) -> Optional[Dict]:
        """Обнаруживает доминирующий повторяющийся фокус в question of the day."""
        cutoff_date = date.today() - timedelta(days=lookback_days)

        connections = self.db.query(DayConnection).filter(
            and_(
                DayConnection.user_id == user_id,
                DayConnection.date >= cutoff_date,
                DayConnection.question_of_day_answer.isnot(None),
            )
        ).order_by(DayConnection.date.desc()).all()

        answers = [
            (item.question_of_day_answer or "").strip().lower()
            for item in connections
            if (item.question_of_day_answer or "").strip()
        ]
        if len(answers) < 4:
            return None

        top_answer, top_count = Counter(answers).most_common(1)[0]
        if top_count < 3:
            return None

        return {
            "type": "signal_focus",
            "dominant_focus": top_answer,
            "dominant_focus_count": top_count,
            "days_reviewed": len(answers),
            "confidence": "high" if top_count >= 4 else "medium",
            "insight_text": f"Ответы дня повторяют одну и ту же линию: сейчас у тебя снова и снова всплывает тема `{top_answer}`."
        }
    
    def generate_insight(self, user_id: int, target_date: str) -> Optional[Dict]:
        """Генерирует инсайт для пользователя на дату."""
        insights = []

        signal_closure = self.detect_signal_closure_pattern(user_id, lookback_days=10)
        if signal_closure:
            insights.append(signal_closure)

        signal_clarity = self.detect_signal_clarity_pattern(user_id, lookback_days=10)
        if signal_clarity:
            insights.append(signal_clarity)

        signal_focus = self.detect_signal_focus_pattern(user_id, lookback_days=14)
        if signal_focus:
            insights.append(signal_focus)
        
        # Проверяем корреляции (приоритет)
        correlation = self.detect_correlation(user_id, lookback_days=14)
        if correlation:
            insights.append(correlation)
        
        # Проверяем паттерн выходных
        weekend_pattern = self.detect_weekend_pattern(user_id, lookback_days=30)
        if weekend_pattern:
            insights.append(weekend_pattern)
        
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
            insight_id = f"insight.{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            return {
                'id': insight_id,
                'user_id': user_id,
                'date': target_date,
                'type': insight['type'],
                'insight_text': insight['insight_text'],
                'data_points': {k: v for k, v in insight.items() if k != 'type' and k != 'insight_text'},
                'confidence': insight.get('confidence', 'medium'),
                'created_at': datetime.now()
            }
        return None


class WeeklyAnalyzerDB:
    """Анализатор недельных данных для генерации интеграционного текста."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def analyze_week(self, user_id: int, week_start: str, week_end: str) -> Optional[Dict]:
        """Анализирует неделю и генерирует интеграционный текст."""
        week_start_date = datetime.strptime(week_start, '%Y-%m-%d').date()
        week_end_date = datetime.strptime(week_end, '%Y-%m-%d').date()
        
        # Фильтруем записи за неделю
        week_entries = self.db.query(ProgressTrackerEntry).filter(
            and_(
                ProgressTrackerEntry.user_id == user_id,
                ProgressTrackerEntry.date >= week_start_date,
                ProgressTrackerEntry.date <= week_end_date
            )
        ).all()

        week_signals = self.db.query(DayConnection).filter(
            and_(
                DayConnection.user_id == user_id,
                DayConnection.date >= week_start_date,
                DayConnection.date <= week_end_date,
            )
        ).all()
        
        if not week_entries and not week_signals:
            return None
        
        # Анализируем состояния
        states = [e.state for e in week_entries if e.state]
        most_common_state = Counter(states).most_common(1)[0][0] if states else 'normal'
        
        # Анализируем практики
        practices_used = list(set([
            e.affirmation_id for e in week_entries 
            if e.affirmation_id and e.completed
        ]))
        
        completion_rate = sum(1 for e in week_entries if e.completed) / len(week_entries) if week_entries else 0

        signal_summary = self._analyze_day_signals(week_signals)

        # Определяем, где удержался и где отпустил
        completed_practices = [e.affirmation_id for e in week_entries if e.completed]
        where_held = 'pause_before_reaction' if 'practice.001' in completed_practices else 'general_practice'
        where_released = 'task_switching' if len(completed_practices) < len(week_entries) * 0.7 else None

        if signal_summary["needs_closure"]:
            where_released = "daily_closure"
        elif signal_summary["clarity_gap"]:
            where_released = "decision_clarity"

        # Генерируем текст
        state_text = self._format_state(most_common_state)
        practice_text = self._format_practice(where_held)
        signal_text = self._format_signal_summary(signal_summary)

        integration_text = (
            f"За эту неделю ты чаще всего сталкивался с {state_text}. "
            f"И всё же ты удерживал {practice_text}. "
            f"{signal_text} Это формирует новый ритм."
        )
        
        return {
            'week_start': week_start,
            'week_end': week_end,
            'user_id': user_id,
            'integration_text': integration_text,
            'data_points': {
                'most_common_state': most_common_state,
                'practices_held': practices_used[:3],  # Топ-3
                'completion_rate': round(completion_rate, 2),
                'where_held': where_held,
                'where_released': where_released,
                'signals_days': signal_summary["signals_days"],
                'signals_completion_rate': signal_summary["signals_completion_rate"],
                'ritual_feedback_yes_days': signal_summary["ritual_feedback_yes_days"],
                'ritual_feedback_no_days': signal_summary["ritual_feedback_no_days"],
                'unclear_decision_days': signal_summary["unclear_decision_days"],
                'dominant_question_focus': signal_summary["dominant_question_focus"],
                'needs_closure': signal_summary["needs_closure"],
                'clarity_gap': signal_summary["clarity_gap"],
            },
            'created_at': datetime.now()
        }

    def _analyze_day_signals(self, connections: List[DayConnection]) -> Dict:
        relevant = []
        for connection in connections:
            signal_count = int(bool(connection.ritual_feedback)) + int(bool(connection.quick_decision_answer)) + int(bool(connection.question_of_day_answer))
            if signal_count == 0:
                continue
            relevant.append(connection)

        if not relevant:
            return {
                "signals_days": 0,
                "signals_completion_rate": 0.0,
                "ritual_feedback_yes_days": 0,
                "ritual_feedback_no_days": 0,
                "unclear_decision_days": 0,
                "dominant_question_focus": None,
                "needs_closure": False,
                "clarity_gap": False,
            }

        ritual_yes = sum(1 for item in relevant if item.ritual_feedback == "yes")
        ritual_no = sum(1 for item in relevant if item.ritual_feedback == "no")
        unclear_days = sum(1 for item in relevant if item.quick_decision_answer == "unclear")
        answer_counter = Counter(
            (item.question_of_day_answer or "").strip().lower()
            for item in relevant
            if (item.question_of_day_answer or "").strip()
        )
        dominant_question_focus = answer_counter.most_common(1)[0][0] if answer_counter else None

        return {
            "signals_days": len(relevant),
            "signals_completion_rate": round(len(relevant) / 7, 2),
            "ritual_feedback_yes_days": ritual_yes,
            "ritual_feedback_no_days": ritual_no,
            "unclear_decision_days": unclear_days,
            "dominant_question_focus": dominant_question_focus,
            "needs_closure": ritual_no >= 2,
            "clarity_gap": unclear_days >= 2,
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

    def _format_signal_summary(self, signal_summary: Dict) -> str:
        if signal_summary["signals_days"] == 0:
            return "На уровне ежедневных ответов картина недели пока почти не собрана."
        if signal_summary["needs_closure"]:
            return "По ответам дня видно, что неделе не хватало завершения и спокойного закрытия перегруза."
        if signal_summary["clarity_gap"]:
            return "По ответам дня видно, что несколько решений так и остались не до конца прояснены."
        if signal_summary["ritual_feedback_yes_days"] >= 3:
            return "По ежедневным сигналам видно, что ты чаще собирал день, чем терял его."
        return "Ежедневные сигналы недели еще неровные, но уже показывают, где ритм начинает собираться."

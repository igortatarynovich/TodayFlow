"""Сервис для построения смыслового состояния дня (DayMeaning).

Собирает данные из систем (астрология, нумерология, архетип) и формирует
единое смысловое состояние дня, которое является источником для прогноза.
"""

from __future__ import annotations

from datetime import date
from typing import Optional

from todayflow_backend.core.day_meaning import DayMeaning, AstroState, NumerologyContext
from todayflow_backend.services import astro
from todayflow_backend.services.personal_transits import PersonalTransitService
from todayflow_backend.services.numerology import NumerologyService
from todayflow_backend.services.tarot import TarotService
from todayflow_backend.services.lunar import LunarService
from todayflow_backend.core import models
from todayflow_backend.db.models import User
from sqlalchemy.orm import Session


class DayMeaningBuilder:
    """Строит смысловое состояние дня из систем."""
    
    def __init__(
        self,
        transit_service: PersonalTransitService,
        numerology_service: NumerologyService,
        tarot_service: Optional[TarotService] = None,
    ):
        self.transit_service = transit_service
        self.numerology_service = numerology_service
        self.tarot_service = tarot_service
    
    async def build(
        self,
        user: Optional[User],
        target_date: date,
        natal_chart: astro.ChartResponse,
        birth_data: Optional[models.BirthData] = None,
        locale: str = "ru",
        db: Optional[Session] = None,
    ) -> DayMeaning:
        """
        Строит смысловое состояние дня из всех доступных систем.
        
        Пайплайн:
        1. Астрология (всегда)
        2. Нумерология (если пользователь авторизован)
        3. Архетип/Таро (если пользователь авторизован)
        4. Определение направления интерпретации
        5. Определение фокусной области
        6. Вычисление интенсивности
        """
        # 1. Получаем астрологическое состояние
        astro_state = await self._build_astro_state(
            natal_chart, target_date, birth_data, locale
        )
        
        # 2. Получаем нумерологический контекст (если пользователь авторизован)
        numerology_context = None
        if user:
            numerology_context = await self._build_numerology_context(
                user, target_date, locale, db
            )
        
        # 3. Получаем архетип дня (если пользователь авторизован)
        archetype = None
        if user and self.tarot_service:
            archetype = await self._get_daily_archetype(
                user, target_date, locale
            )
        
        # 4. Определяем направление интерпретации
        interpretation_direction = self._determine_direction(astro_state)
        
        # 5. Определяем фокусную область
        focus_area = self._determine_focus(astro_state, numerology_context)
        
        # 6. Вычисляем интенсивность
        intensity = self._calculate_intensity(astro_state)
        
        return DayMeaning(
            date=target_date,
            astro_state=astro_state,
            numerology_context=numerology_context,
            archetype=archetype,
            interpretation_direction=interpretation_direction,
            focus_area=focus_area,
            intensity=intensity
        )
    
    async def _build_astro_state(
        self,
        natal_chart: astro.ChartResponse,
        target_date: date,
        birth_data: Optional[models.BirthData],
        locale: str,
    ) -> AstroState:
        """Строит астрологическое состояние дня."""
        # Получаем прогноз через transit service
        transit_forecast = await self.transit_service.get_daily_forecast(
            natal_chart=natal_chart,
            forecast_date=target_date,
            birth_data=birth_data,
            locale=locale,
        )
        
        # Извлекаем аспекты из транзитов
        aspects = []
        if transit_forecast.transits:
            for transit in transit_forecast.transits:
                # Если транзит содержит информацию об аспектах
                if isinstance(transit, dict):
                    if "aspects" in transit:
                        aspects.extend(transit["aspects"])
                    elif "aspect_type" in transit:
                        # Формируем аспект из транзита
                        aspects.append({
                            "type": transit.get("aspect_type"),
                            "planet": transit.get("planet"),
                            "target": transit.get("target"),
                            "orb": transit.get("orb"),
                            "description": transit.get("description"),
                        })
        
        # Получаем лунную фазу
        lunar_phase = None
        try:
            lunar_service = LunarService()
            moon_phase_response = lunar_service.current_phase(locale=locale)
            if moon_phase_response and moon_phase_response.current:
                lunar_phase = moon_phase_response.current.id  # или name, в зависимости от того, что нужно
        except Exception:
            pass  # Если не удалось получить лунную фазу, продолжаем без неё
        
        return AstroState(
            transits=transit_forecast.transits or [],
            aspects=aspects,
            tensions=transit_forecast.tensions or [],
            resources=transit_forecast.resources or [],
            lunar_phase=lunar_phase,
            intensity_score=transit_forecast.intensity_score or 0.0,
        )
    
    async def _build_numerology_context(
        self,
        user: User,
        target_date: date,
        locale: str,
        db: Optional[Session],
    ) -> Optional[NumerologyContext]:
        """Строит нумерологический контекст дня."""
        try:
            # Получаем число дня
            daily_insight = self.numerology_service.daily_number(
                reference_date=target_date,
                locale=locale
            )
            
            if not daily_insight or not daily_insight.number:
                return None
            
            # Получаем Personal Year (если есть профиль нумерологии)
            personal_year = None
            repeating_patterns = []
            
            if db:
                from todayflow_backend.db.models import NumerologyProfile
                profile = db.query(NumerologyProfile).filter(
                    NumerologyProfile.user_id == user.id,
                    NumerologyProfile.is_primary == True
                ).first()
                
                if profile and profile.birth_date:
                    personal_year = self.numerology_service.personal_year_calc(
                        profile.birth_date.day,
                        profile.birth_date.month,
                        target_date.year
                    )
                    
                    # Определяем повторяющиеся паттерны
                    # Сравниваем Personal Day с Personal Year
                    personal_day_value = daily_insight.number.value or daily_insight.number.reduced_value
                    personal_year_value = personal_year.number.value if personal_year and personal_year.number else None
                    
                    if personal_year_value:
                        # Если числа совпадают, это повторяющийся паттерн
                        if personal_day_value == personal_year_value:
                            repeating_patterns.append(f"День {personal_day_value} в году {personal_year_value}")
                        
                        # Проверяем, является ли Personal Day частью цикла Personal Year
                        if personal_year_value and personal_day_value:
                            # Если Personal Day кратен Personal Year или наоборот
                            if personal_year_value > 0 and personal_day_value % personal_year_value == 0:
                                repeating_patterns.append(f"День кратен году ({personal_day_value} кратно {personal_year_value})")
                            elif personal_day_value > 0 and personal_year_value % personal_day_value == 0:
                                repeating_patterns.append(f"Год кратен дню ({personal_year_value} кратно {personal_day_value})")
            
            return NumerologyContext(
                personal_day=daily_insight.number.value or daily_insight.number.reduced_value,
                personal_year=personal_year.number.value if personal_year and personal_year.number else None,
                repeating_patterns=repeating_patterns,
                day_number_title=daily_insight.number.title,
                day_number_summary=daily_insight.number.summary,
            )
        except Exception:
            return None
    
    async def _get_daily_archetype(
        self,
        user: User,
        target_date: date,
        locale: str,
    ) -> Optional[dict]:
        """Получает архетип дня (Таро карта)."""
        if not self.tarot_service:
            return None
        
        try:
            daily_draw = self.tarot_service.get_daily_draw(user, locale=locale)
            if daily_draw and daily_draw.card:
                return {
                    "card_id": daily_draw.card.id,
                    "name": daily_draw.card.name,
                    "orientation": daily_draw.card.orientation,
                    "keywords": daily_draw.card.keywords or [],
                }
        except Exception:
            pass
        
        return None
    
    def _determine_direction(self, astro_state: AstroState) -> str:
        """Определяет направление интерпретации: tension / release / transition / fixation / neutral."""
        # Анализируем напряжения и ресурсы
        tension_count = len(astro_state.tensions)
        resource_count = len(astro_state.resources)
        
        if tension_count > resource_count * 1.5:
            return "tension"
        elif resource_count > tension_count * 1.5:
            return "release"
        elif tension_count > 0 and resource_count > 0:
            return "transition"
        elif astro_state.intensity_score > 0.7:
            return "fixation"
        else:
            return "neutral"
    
    def _determine_focus(
        self,
        astro_state: AstroState,
        numerology_context: Optional[NumerologyContext],
    ) -> str:
        """Определяет фокусную область: work / body / dialogue / home / relationship / money / general.
        
        Улучшенная версия:
        - Анализирует транзиты, напряжения и ресурсы
        - Учитывает аспекты
        - Улучшенный маппинг домов
        - Учитывает нумерологический контекст
        """
        # Анализируем транзиты, напряжения и ресурсы для определения фокуса
        focus_scores = {
            "work": 0,
            "body": 0,
            "dialogue": 0,
            "home": 0,
            "relationship": 0,
            "money": 0,
        }
        
        # Маппинг домов на области фокуса
        house_to_focus = {
            1: ["body"],  # 1 дом - личность, тело, внешность
            2: ["money"],  # 2 дом - деньги, ресурсы, ценности
            3: ["dialogue"],  # 3 дом - общение, братья/сёстры, короткие поездки
            4: ["home"],  # 4 дом - дом, семья, корни
            5: ["relationship"],  # 5 дом - творчество, любовь, дети
            6: ["work", "body"],  # 6 дом - работа, здоровье, рутина
            7: ["relationship"],  # 7 дом - партнёрство, отношения
            8: ["money", "relationship"],  # 8 дом - чужие деньги, трансформация, интимность
            9: ["dialogue"],  # 9 дом - высшее образование, философия, дальние поездки
            10: ["work"],  # 10 дом - карьера, статус, репутация
            11: ["relationship", "dialogue"],  # 11 дом - друзья, сообщества, цели
            12: ["body", "home"],  # 12 дом - подсознание, уединение, тайны
        }
        
        # Анализируем транзиты
        for transit in astro_state.transits:
            if isinstance(transit, dict):
                planet = transit.get("planet", "").lower()
                target = transit.get("target", "").lower()
                house = transit.get("house")
                description = transit.get("description", "").lower()
                
                # Определяем фокус по дому (улучшенный маппинг)
                if house and house in house_to_focus:
                    for focus_area in house_to_focus[house]:
                        focus_scores[focus_area] += 2
                
                # Определяем фокус по планете (более точный)
                planet_focus = {
                    "mars": ["work", "body"],
                    "saturn": ["work"],
                    "venus": ["relationship", "money"],
                    "jupiter": ["relationship", "money", "dialogue"],
                    "mercury": ["dialogue", "work"],
                    "moon": ["home", "body"],
                    "neptune": ["home", "body"],
                    "pluto": ["relationship", "money"],
                    "uranus": ["dialogue", "work"],
                    "sun": ["work", "body"],
                }
                if planet in planet_focus:
                    for focus_area in planet_focus[planet]:
                        focus_scores[focus_area] += 1
                
                # Определяем фокус по описанию
                description_keywords = {
                    "work": ["работа", "карьера", "профессия", "work", "career", "job", "проект"],
                    "body": ["тело", "здоровье", "body", "health", "физическое", "энергия"],
                    "dialogue": ["общение", "диалог", "communication", "dialogue", "разговор", "идеи"],
                    "home": ["дом", "семья", "home", "family", "уют", "безопасность"],
                    "relationship": ["партнёр", "отношения", "relationship", "partner", "любовь", "близость"],
                    "money": ["деньги", "ресурсы", "money", "resources", "финансы", "материальное"],
                }
                for area, keywords in description_keywords.items():
                    if any(keyword in description for keyword in keywords):
                        focus_scores[area] += 1
        
        # Анализируем напряжения (более высокий вес, так как это важные моменты)
        for tension in astro_state.tensions:
            if isinstance(tension, dict):
                area = tension.get("area", "").lower()
                house = tension.get("house")
                
                # Определяем фокус по дому из напряжения
                if house and house in house_to_focus:
                    for focus_area in house_to_focus[house]:
                        focus_scores[focus_area] += 3  # Напряжения имеют больший вес
                
                # Определяем фокус по области из напряжения
                if area:
                    area_mapping = {
                        "work": "work",
                        "career": "work",
                        "body": "body",
                        "health": "body",
                        "dialogue": "dialogue",
                        "communication": "dialogue",
                        "home": "home",
                        "family": "home",
                        "relationship": "relationship",
                        "partnership": "relationship",
                        "money": "money",
                        "resources": "money",
                    }
                    for key, focus_area in area_mapping.items():
                        if key in area:
                            focus_scores[focus_area] += 2
        
        # Анализируем ресурсы (также важны, но с меньшим весом)
        for resource in astro_state.resources:
            if isinstance(resource, dict):
                house = resource.get("house")
                if house and house in house_to_focus:
                    for focus_area in house_to_focus[house]:
                        focus_scores[focus_area] += 1
        
        # Анализируем аспекты (дополнительная информация)
        for aspect in astro_state.aspects:
            if isinstance(aspect, dict):
                planet = aspect.get("planet", "").lower()
                if planet in planet_focus:
                    for focus_area in planet_focus[planet]:
                        focus_scores[focus_area] += 0.5
        
        # Учитываем нумерологический контекст
        if numerology_context:
            # Personal Day может указывать на фокус
            personal_day = numerology_context.personal_day
            if personal_day:
                # Числа, связанные с работой (4, 8, 10)
                if personal_day in [4, 8, 10]:
                    focus_scores["work"] += 1
                # Числа, связанные с отношениями (2, 6, 9)
                elif personal_day in [2, 6, 9]:
                    focus_scores["relationship"] += 1
                # Числа, связанные с общением (3, 5, 7)
                elif personal_day in [3, 5, 7]:
                    focus_scores["dialogue"] += 1
                # Числа, связанные с домом (1, 4)
                elif personal_day in [1, 4]:
                    focus_scores["home"] += 0.5
        
        # Находим максимальный фокус
        max_score = max(focus_scores.values())
        if max_score > 0:
            # Если есть несколько областей с одинаковым максимальным счетом, выбираем первую
            for area, score in focus_scores.items():
                if score == max_score:
                    return area
        
        return "general"
    
    def _calculate_intensity(self, astro_state: AstroState) -> float:
        """Вычисляет общую интенсивность дня (0-1)."""
        # Используем intensity_score из астрологического состояния
        return min(max(astro_state.intensity_score, 0.0), 1.0)

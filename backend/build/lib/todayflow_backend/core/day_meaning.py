"""Модель смыслового состояния дня (DayMeaning).

Это центральная сущность прогноза: состояние дня, выведенное из систем
(астрология, нумерология, архетип), до интерпретации и текста.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import List, Optional, Dict, Any


@dataclass
class AstroState:
    """Астрологическое состояние дня."""
    transits: List[Dict[str, Any]] = field(default_factory=list)
    aspects: List[Dict[str, Any]] = field(default_factory=list)
    tensions: List[Dict[str, Any]] = field(default_factory=list)
    resources: List[Dict[str, Any]] = field(default_factory=list)
    lunar_phase: Optional[str] = None
    intensity_score: float = 0.0


@dataclass
class NumerologyContext:
    """Нумерологический контекст дня."""
    personal_day: int
    personal_year: int
    repeating_patterns: List[str] = field(default_factory=list)
    day_number_title: Optional[str] = None
    day_number_summary: Optional[str] = None


@dataclass
class DayMeaning:
    """Смысловое состояние дня, выведенное из систем.
    
    Это источник смысла для прогноза. Всё остальное (лексикон, ИИ) 
    работает с этим состоянием, а не генерирует его.
    """
    date: date
    astro_state: AstroState
    numerology_context: Optional[NumerologyContext] = None
    archetype: Optional[Dict[str, Any]] = None  # Таро карта дня как архетип
    interpretation_direction: str = "neutral"  # tension / release / transition / fixation / neutral
    focus_area: str = "general"  # work / body / dialogue / home / relationship / money / general
    intensity: float = 0.0  # 0-1
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразует в словарь для сериализации."""
        return {
            "date": self.date.isoformat(),
            "astro_state": {
                "transits": self.astro_state.transits,
                "aspects": self.astro_state.aspects,
                "tensions": self.astro_state.tensions,
                "resources": self.astro_state.resources,
                "lunar_phase": self.astro_state.lunar_phase,
                "intensity_score": self.astro_state.intensity_score,
            },
            "numerology_context": {
                "personal_day": self.numerology_context.personal_day,
                "personal_year": self.numerology_context.personal_year,
                "repeating_patterns": self.numerology_context.repeating_patterns,
                "day_number_title": self.numerology_context.day_number_title,
                "day_number_summary": self.numerology_context.day_number_summary,
            } if self.numerology_context else None,
            "archetype": self.archetype,
            "interpretation_direction": self.interpretation_direction,
            "focus_area": self.focus_area,
            "intensity": self.intensity,
        }

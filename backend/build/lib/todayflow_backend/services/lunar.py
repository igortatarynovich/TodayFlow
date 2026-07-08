"""Lunar cycle helpers used for Moon Phase ribbon & solar strip."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import List, Tuple

from todayflow_backend.core import models
from todayflow_backend.data import astrology as astrology_ref
from todayflow_backend.data import content_system
from todayflow_backend.i18n import translate

SYNODIC_PERIOD_DAYS = 29.53058867
EPOCH = datetime(2000, 1, 6, 18, 14, tzinfo=timezone.utc)  # known new moon


class LunarService:
    def __init__(self) -> None:
        raw = astrology_ref.moon_phases()
        self.phases: List[Tuple[float, float, dict]] = []
        for record in raw:
            start_deg, end_deg = self._parse_range(record["degree_range"])
            self.phases.append((start_deg, end_deg, record))

    def current_phase(self, locale: str | None = None) -> models.MoonPhaseResponse:
        now = datetime.now(timezone.utc)
        age_days = ((now - EPOCH).total_seconds() / 86400.0) % SYNODIC_PERIOD_DAYS
        angle = (age_days / SYNODIC_PERIOD_DAYS) * 360.0

        start_deg, end_deg, record, index = self._phase_for_angle(angle)
        cycle_percent = age_days / SYNODIC_PERIOD_DAYS * 100

        next_index = (index + 1) % len(self.phases)
        next_start, _, next_record = self.phases[next_index]
        days_to_next = self._days_until(angle, next_start)
        next_date = (now + timedelta(days=days_to_next)).date().isoformat()

        upcoming = []
        cursor_index = next_index
        cursor_angle = next_start
        for _ in range(4):
            phase_start, _, phase_record = self.phases[cursor_index]
            days_until = self._days_until(angle, phase_start)
            upcoming.append(
                models.UpcomingPhase(
                    id=phase_record["id"],
                    name=self._phase_name(phase_record, locale),
                    date=(now + timedelta(days=days_until)).date().isoformat(),
                    in_days=round(days_until, 2),
                )
            )
            cursor_index = (cursor_index + 1) % len(self.phases)

        # Try to get human_text from Content System
        content_phase = content_system.get_moon_phase_by_id(record["id"])
        human_text = content_phase.get("human_text") if content_phase else None
        
        # Fallback to i18n if Content System doesn't have human_text
        themes = translate(f"moon_phase.{record['id']}.themes", locale=locale, default=record.get("themes", ""))
        guidance = translate(
            f"moon_phase.{record['id']}.guidance", locale=locale, default=record.get("guidance", "")
        )
        
        current_snapshot = models.MoonPhaseSnapshot(
            id=record["id"],
            name=self._phase_name(record, locale),
            keywords=record.get("keywords", []),
            themes=themes,
            guidance=guidance,
            human_text=human_text,
            angle_degrees=round(angle, 2),
            cycle_day=round(age_days, 2),
            cycle_percent=round(cycle_percent, 2),
        )
        next_phase = models.UpcomingPhase(
            id=next_record["id"],
            name=self._phase_name(next_record, locale),
            date=next_date,
            in_days=round(days_to_next, 2),
        )
        return models.MoonPhaseResponse(current=current_snapshot, next_phase=next_phase, upcoming=upcoming)

    def _phase_for_angle(self, angle: float) -> Tuple[float, float, dict, int]:
        for idx, (start, end, record) in enumerate(self.phases):
            if start <= end:
                in_range = start <= angle <= end
            else:
                in_range = angle >= start or angle <= end
            if in_range:
                return start, end, record, idx
        # fallback to first phase
        start, end, record = self.phases[0]
        return start, end, record, 0

    @staticmethod
    def _parse_range(value: str) -> Tuple[float, float]:
        parts = value.replace("°", "").split("-")
        start = float(parts[0])
        end = float(parts[1])
        return start, end

    @staticmethod
    def _days_until(current_angle: float, target_start: float) -> float:
        delta_degrees = (target_start - current_angle) % 360
        return (delta_degrees / 360.0) * SYNODIC_PERIOD_DAYS

    @staticmethod
    def _phase_name(record: dict, locale: str | None = None) -> str:
        return translate(f"moon_phase.{record['id']}.name", locale=locale, default=record.get("name", record["id"]))


async def get_lunar_service() -> LunarService:
    return LunarService()

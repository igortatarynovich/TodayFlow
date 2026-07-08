"""Weekly/lunar insight service."""

from __future__ import annotations

from typing import Dict, List

from todayflow_backend.core import models
from todayflow_backend.data import astrology as astrology_ref
from todayflow_backend.data import content_system
from todayflow_backend.i18n import translate
from todayflow_backend.services.lite_reports import LiteReportService, get_lite_report_service
from todayflow_backend.services.lunar import LunarService, get_lunar_service

AXIS_LABELS = {
    "A1": "Identity & Direction",
    "A2": "Emotional Processing",
    "A3": "Decision & Analysis",
    "A4": "Stability vs Change",
    "A5": "Control & Drive",
    "A6": "Relationships",
    "A7": "Energy & Vitality",
}


class WeeklyInsightService:
    def __init__(
        self,
        lunar_service: LunarService | None = None,
        lite_service: LiteReportService | None = None,
    ) -> None:
        self.lunar_service = lunar_service or LunarService()
        self.lite_service = lite_service or LiteReportService()
        self.entries = astrology_ref.weekly_insights()
        self.map = self._index_entries(self.entries)

    def get_insight(self, user, *, locale: str | None = None) -> models.WeeklyInsightResponse:
        lunar = self.lunar_service.current_phase(locale=locale)
        report = self.lite_service._get_latest_report(user)
        if not report or not report.internal_model or not report.internal_model.axes:
            raise ValueError("Lite report/internal model missing")
        axis = max(report.internal_model.axes, key=lambda ax: abs(ax.value))
        facet = self._match_entry(lunar.current.id, axis.axis_id) or self._match_entry(lunar.current.id, None)
        if facet:
            # Try to get human_text from Content System
            human_text = None
            try:
                weekly_forecasts = content_system.load_weekly_forecasts()
                # Match by phase and axis
                forecast_id = f"{lunar.current.id}.{axis.axis_id}" if facet.get("axis_id") else f"{lunar.current.id}"
                for forecast in weekly_forecasts:
                    if forecast.get("forecast_id") == forecast_id or (
                        forecast.get("phase") == lunar.current.id and 
                        forecast.get("axis") == (axis.axis_id if facet.get("axis_id") else None)
                    ):
                        human_text = forecast.get("human_text")
                        break
            except Exception:
                pass  # Fallback to old system
            
            insight = models.WeeklyInsight(
                phase_id=lunar.current.id,
                phase_name=lunar.current.name,
                axis_id=axis.axis_id if facet["axis_id"] else None,
                axis_label=AXIS_LABELS.get(axis.axis_id) if facet["axis_id"] else None,
                title=self._facet_text(facet, "title", facet["title"], locale),
                summary=self._facet_text(facet, "summary", facet["summary"], locale),
                cta=self._facet_text(facet, "cta", facet.get("cta"), locale),
                human_text=human_text,
            )
        else:
            insight = self._default_insight(lunar, axis, locale)
        return models.WeeklyInsightResponse(insight=insight, next_phase=lunar.next_phase)

    def _index_entries(self, entries: List[Dict]) -> Dict[str, List[Dict]]:
        mapping: Dict[str, List[Dict]] = {}
        for entry in entries:
            mapping.setdefault(entry["phase_id"], []).append(entry)
        return mapping

    def _match_entry(self, phase_id: str, axis_id: str | None) -> Dict | None:
        """Match entry with preference for axis-specific, then fallback to generic."""
        candidates = self.map.get(phase_id, [])
        # First try to find axis-specific entry
        axis_specific = [entry for entry in candidates if entry.get("axis_id") == axis_id]
        if axis_specific:
            # If multiple options, use deterministic selection based on phase_id + axis_id
            import hashlib
            seed = int(hashlib.md5(f"{phase_id}:{axis_id}".encode()).hexdigest()[:8], 16)
            return axis_specific[seed % len(axis_specific)]
        # Fallback to generic (axis_id is None)
        generic = [entry for entry in candidates if entry.get("axis_id") is None]
        if generic:
            import hashlib
            seed = int(hashlib.md5(f"{phase_id}:generic".encode()).hexdigest()[:8], 16)
            return generic[seed % len(generic)]
        return None

    def _facet_key(self, facet: Dict) -> str:
        axis_suffix = facet.get("axis_id") or "any"
        return f"weekly.{facet['phase_id']}.{axis_suffix}"

    def _facet_text(self, facet: Dict, field: str, default: str | None, locale: str | None) -> str | None:
        if default is None:
            return None
        key = f"{self._facet_key(facet)}.{field}"
        return translate(key, locale=locale, default=default)

    def _default_insight(
        self, lunar: models.MoonPhaseResponse, axis: models.AxisValue, locale: str | None
    ) -> models.WeeklyInsight:
        """Fallback copy when we do not yet have curated text for the current phase/axis pair."""
        axis_label = AXIS_LABELS.get(axis.axis_id, "core theme")
        phase_name = lunar.current.name
        title = f"{phase_name}: hold {axis_label}"
        summary = translate(
            "weekly.default.summary",
            locale=locale,
            default=f"В фазе {phase_name.lower()} особенно заметно, как тема «{axis_label}» проявляется в обычных решениях и реакциях. "
            "На этой неделе полезно поймать один конкретный сигнал, который покажет, что именно сейчас требует твоего внимания.",
        ).format(axis=axis_label)
        cta = translate(
            "weekly.default.cta",
            locale=locale,
            default="Запиши одно наблюдение о себе или неделе: оно поможет точнее войти в следующий цикл, чем попытка просто все удержать в голове.",
        )
        # Try to get human_text from Content System for default insight
        human_text = None
        try:
            weekly_forecasts = content_system.load_weekly_forecasts()
            forecast_id = f"{lunar.current.id}.{axis.axis_id}"
            for forecast in weekly_forecasts:
                if forecast.get("forecast_id") == forecast_id or (
                    forecast.get("phase") == lunar.current.id and 
                    forecast.get("axis") == axis.axis_id
                ):
                    human_text = forecast.get("human_text")
                    break
        except Exception:
            pass  # Fallback to old system
        
        return models.WeeklyInsight(
            phase_id=lunar.current.id,
            phase_name=phase_name,
            axis_id=axis.axis_id,
            axis_label=axis_label,
            title=title,
            summary=summary,
            cta=cta,
            human_text=human_text,
        )


async def get_weekly_service() -> WeeklyInsightService:
    return WeeklyInsightService()

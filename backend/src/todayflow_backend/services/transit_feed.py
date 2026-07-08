"""Aggregated daily transit feed service (moon focus + planetary highlights)."""

from __future__ import annotations

from datetime import datetime
from typing import List

from todayflow_backend.core import models
from todayflow_backend.i18n import translate
from todayflow_backend.services.lunar import LunarService
from todayflow_backend.services.planetary import PlanetaryService


class TransitFeedService:
    def __init__(self) -> None:
        self._lunar = LunarService()
        self._planetary = PlanetaryService()

    def get_feed(self, *, locale: str | None = None) -> models.TransitFeedResponse:
        focus = self._lunar.current_phase(locale=locale)
        timeline = self._planetary.upcoming_events(limit=5, window_limit=2, locale=locale)
        highlights: List[models.TransitHighlight] = []
        for event in timeline.upcoming:
            highlights.append(self._build_event_highlight(event, locale))
        for window in timeline.windows:
            highlights.append(self._build_window_highlight(window, locale))
        return models.TransitFeedResponse(
            focus=focus,
            highlights=highlights,
            events=timeline.upcoming,
            windows=timeline.windows,
        )

    def _build_event_highlight(self, event: models.PlanetEvent, locale: str | None) -> models.TransitHighlight:
        event_label = event.event_type.replace("_", " ").title()
        title_template = translate("transit.event.title", locale=locale, default="{planet} {event}")
        title = title_template.format(planet=event.planet, event=event_label).strip()
        meta_parts: List[str] = []
        if event.sign:
            sign_template = translate("transit.event.meta.sign", locale=locale, default="Sign: {sign}")
            meta_parts.append(sign_template.format(sign=event.sign))
        if event.aspect:
            aspect_template = translate("transit.event.meta.aspect", locale=locale, default="Aspect: {aspect}")
            meta_parts.append(aspect_template.format(aspect=event.aspect))
        meta = " · ".join(meta_parts) if meta_parts else None
        tags: List[str] = [event.planet]
        if event.sign:
            tags.append(event.sign)
        tags.extend(event.keywords or [])
        return models.TransitHighlight(
            id=event.id,
            title=title,
            description=event.description,
            timestamp=event.timestamp,
            kind="event",
            meta=meta,
            tags=tags,
        )

    def _build_window_highlight(self, window: models.PlanetaryWindow, locale: str | None) -> models.TransitHighlight:
        default_title = translate("transit.window.defaultTitle", locale=locale, default="{planet} {type}")
        title = window.label or default_title.format(planet=window.planet, type=window.window_type.title())
        start_label = self._format_date_label(window.start_timestamp)
        end_label = self._format_date_label(window.end_timestamp)
        range_template = translate("transit.window.range", locale=locale, default="{start} → {end}")
        range_label = range_template.format(start=start_label, end=end_label)
        status_key = (
            "transit.window.status.active" if window.status == "active" else "transit.window.status.upcoming"
        )
        status_label = translate(status_key, locale=locale, default=window.status.title())
        meta_template = translate("transit.window.meta", locale=locale, default="{status} · {range}")
        meta = meta_template.format(status=status_label, range=range_label)
        tags: List[str] = [window.planet, window.status]
        if window.sign:
            tags.append(window.sign)
        tags.extend(window.keywords or [])
        return models.TransitHighlight(
            id=window.id,
            title=title,
            description=window.description,
            timestamp=window.start_timestamp,
            kind="window",
            meta=meta,
            tags=tags,
        )

    @staticmethod
    def _format_date_label(timestamp: str) -> str:
        try:
            dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        except ValueError:
            return timestamp[:10]
        return dt.strftime("%b %d")


async def get_transit_feed_service() -> TransitFeedService:
    return TransitFeedService()

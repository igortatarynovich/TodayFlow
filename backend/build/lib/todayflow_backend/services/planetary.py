"""Planetary calendar helpers for the Solar System strip."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Tuple

from todayflow_backend.core import models
from todayflow_backend.data import astrology as astrology_ref
from todayflow_backend.data import content_system
from todayflow_backend.i18n import translate


class PlanetaryService:
    def __init__(self) -> None:
        entries = astrology_ref.planetary_cycles()
        self.point_events = [entry for entry in entries if "start_timestamp" not in entry]
        self.window_entries = [entry for entry in entries if "start_timestamp" in entry]

    def upcoming_events(
        self, limit: int = 6, window_limit: int = 2, *, locale: str | None = None
    ) -> models.PlanetaryTimeline:
        now = datetime.now(timezone.utc)
        point_models = self._build_point_events(now, limit=limit, locale=locale)
        window_models = self._build_windows(now, limit=window_limit, locale=locale)
        return models.PlanetaryTimeline(upcoming=point_models, windows=window_models)

    def _build_point_events(
        self, now: datetime, *, limit: int, locale: str | None
    ) -> List[models.PlanetEvent]:
        parsed: List[tuple[datetime, dict]] = []
        for event in self.point_events:
            parsed_dt = self._parse_timestamp(event.get("timestamp"))
            if not parsed_dt:
                continue
            parsed.append((parsed_dt, event))
        parsed.sort(key=lambda item: item[0])
        filtered = [event for event_dt, event in parsed if event_dt >= now][:limit]
        result = []
        for event in filtered:
            # Get human_text from Content System
            human_text = None
            event_id = event.get("id") or event.get("event_id")
            if event_id:
                try:
                    content_event = content_system.get_planetary_event_by_id(event_id)
                    if content_event and content_event.get("human_text"):
                        human_text = content_event["human_text"]
                except Exception:
                    pass  # Fallback to existing data
            
            result.append(
                models.PlanetEvent(
                    id=event["id"],
                    planet=event["planet"],
                    event_type=event.get("event_type", ""),
                    timestamp=event["timestamp"],
                    description=translate(
                        f"planetary.{event['id']}.description", locale=locale, default=event.get("description")
                    ),
                    sign=event.get("sign"),
                    aspect=event.get("aspect"),
                    keywords=event.get("keywords", []),
                    human_text=human_text,
                )
            )
        return result

    def _build_windows(
        self, now: datetime, *, limit: int, locale: str | None
    ) -> List[models.PlanetaryWindow]:
        if limit <= 0:
            return []
        parsed: List[Tuple[datetime, datetime, dict]] = []
        for window in self.window_entries:
            start = self._parse_timestamp(window.get("start_timestamp"))
            end = self._parse_timestamp(window.get("end_timestamp"))
            if not start or not end:
                continue
            parsed.append((start, end, window))
        parsed.sort(key=lambda item: item[0])
        windows: List[models.PlanetaryWindow] = []
        for start, end, entry in parsed:
            if end < now:
                continue
            status = "active" if start <= now <= end else "upcoming"
            description = translate(
                f"planetary.{entry['id']}.description",
                locale=locale,
                default=entry.get("description"),
            )
            windows.append(
                models.PlanetaryWindow(
                    id=entry["id"],
                    planet=entry["planet"],
                    window_type=entry.get("event_type", "window"),
                    status=status,
                    start_timestamp=entry["start_timestamp"],
                    end_timestamp=entry["end_timestamp"],
                    label=entry.get("window_label"),
                    sign=entry.get("sign"),
                    description=description,
                    keywords=entry.get("keywords", []),
                )
            )
            if len(windows) >= limit:
                break
        return windows

    @staticmethod
    def _parse_timestamp(value: str | None) -> datetime | None:
        if not value:
            return None
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None


async def get_planetary_service() -> PlanetaryService:
    return PlanetaryService()

"""Content System loader - loads content from CONTENT directory."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

# Find CONTENT directory
def _find_content_dir() -> Path:
    """Find CONTENT directory relative to this module.
    Prefer repo root CONTENT (TodayFlow/CONTENT) — same as config.paragraph_templates_path.
    """
    env_root = os.getenv("CONTENT_DIR")
    if env_root:
        env_path = Path(env_root)
        if env_path.exists():
            return env_path
    
    module_path = Path(__file__).resolve()
    # Prefer repo root (parents[4] = TodayFlow) so we use TodayFlow/CONTENT, not todayflow_backend/content
    for depth in (4, 3, 2, 1, 0):
        if depth >= len(module_path.parents):
            continue
        candidate = module_path.parents[depth] / "CONTENT"
        if candidate.exists():
            return candidate
    
    # Fallback для Docker: пробуем /CONTENT
    docker_content = Path("/CONTENT")
    if docker_content.exists():
        return docker_content
    
    return Path("CONTENT")


CONTENT_DIR = _find_content_dir()


def load_moon_phases() -> List[Dict[str, Any]]:
    """Load moon phases from Content System."""
    file_path = CONTENT_DIR / "forecasts" / "moon_phases.json"
    if not file_path.exists():
        return []
    
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_moon_phase_by_id(phase_id: str) -> Optional[Dict[str, Any]]:
    """Get moon phase by phase_id from Content System.
    
    Supports both 'id' (from old system) and 'phase_id' (from new system).
    """
    phases = load_moon_phases()
    for phase in phases:
        # Try phase_id first (new system), then id (old system)
        if phase.get("phase_id") == phase_id or phase.get("id") == phase_id:
            return phase
    return None


def load_daily_templates() -> List[Dict[str, Any]]:
    """Load daily templates from Content System."""
    file_path = CONTENT_DIR / "daily" / "daily_templates.json"
    if not file_path.exists():
        return []
    
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_daily_template_by_id(template_id: str) -> Optional[Dict[str, Any]]:
    """Get daily template by template_id from Content System."""
    templates = load_daily_templates()
    for template in templates:
        if template.get("template_id") == template_id:
            return template
    return None


def load_rituals() -> List[Dict[str, Any]]:
    """Load rituals from Content System."""
    file_path = CONTENT_DIR / "rituals" / "rituals.json"
    if not file_path.exists():
        return []
    
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_ritual_by_id(ritual_id: str) -> Optional[Dict[str, Any]]:
    """Get ritual by ritual_id from Content System.
    
    Supports both 'id' (from old system) and 'ritual_id' (from new system).
    """
    rituals = load_rituals()
    for ritual in rituals:
        # Try ritual_id first (new system), then id (old system)
        if ritual.get("ritual_id") == ritual_id or ritual.get("id") == ritual_id:
            return ritual
    return None


def load_practices_mantras() -> List[Dict[str, Any]]:
    """Load mantras from Content System."""
    file_path = CONTENT_DIR / "practices" / "mantras.json"
    if not file_path.exists():
        return []
    
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_mantra_by_id(mantra_id: str) -> Optional[Dict[str, Any]]:
    """Get mantra by mantra_id from Content System.
    
    Supports both 'id' (from old system) and 'mantra_id' (from new system).
    """
    mantras = load_practices_mantras()
    for mantra in mantras:
        # Try mantra_id first (new system), then id (old system)
        if mantra.get("mantra_id") == mantra_id or mantra.get("id") == mantra_id:
            return mantra
    return None


def load_weekly_forecasts() -> List[Dict[str, Any]]:
    """Load weekly forecasts from Content System."""
    file_path = CONTENT_DIR / "forecasts" / "weekly.json"
    if not file_path.exists():
        return []
    
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_planetary_events() -> List[Dict[str, Any]]:
    """Load planetary events from Content System."""
    file_path = CONTENT_DIR / "forecasts" / "planetary_events.json"
    if not file_path.exists():
        return []
    
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_tarot_spreads() -> List[Dict[str, Any]]:
    """Load tarot spreads from Content System."""
    file_path = CONTENT_DIR / "practices" / "tarot_spreads.json"
    if not file_path.exists():
        return []
    
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_weekly_forecast_by_id(forecast_id: str) -> Optional[Dict[str, Any]]:
    """Get weekly forecast by forecast_id from Content System.
    
    Supports both 'forecast_id' (new system) and 'id' (old system).
    """
    forecasts = load_weekly_forecasts()
    for forecast in forecasts:
        if forecast.get("forecast_id") == forecast_id or forecast.get("id") == forecast_id:
            return forecast
    return None


def get_planetary_event_by_id(event_id: str) -> Optional[Dict[str, Any]]:
    """Get planetary event by event_id from Content System.
    
    Supports both 'event_id' (new system) and 'id' (old system).
    """
    events = load_planetary_events()
    for event in events:
        if event.get("event_id") == event_id or event.get("id") == event_id:
            return event
    return None


def get_tarot_spread_by_id(spread_id: str) -> Optional[Dict[str, Any]]:
    """Get tarot spread by spread_id from Content System.
    
    Supports both 'spread_id' (new system) and 'id' (old system).
    """
    spreads = load_tarot_spreads()
    for spread in spreads:
        if spread.get("spread_id") == spread_id or spread.get("id") == spread_id:
            return spread
    return None


# -----------------------------------------------------------------------------
# DailyForecast (Web Canon v1) — редакционный контент на дату
# Series/Weekly (weekly.json) остаётся отдельно как Discover/Weekly Themes.
# -----------------------------------------------------------------------------

def _load_json_array(path: Path) -> List[Any]:
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data if isinstance(data, list) else []


def _load_json_object(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data if isinstance(data, dict) else {}


def load_dictionary(name: str) -> List[str]:
    """Загрузить словарь маркеров: body_markers, social_markers, domestic_details, micro_actions."""
    path = CONTENT_DIR / "dictionaries" / f"{name}.json"
    arr = _load_json_array(path)
    return [str(x).strip() for x in arr if isinstance(x, str) and x.strip()]


def load_lexicon() -> Dict[str, Any]:
    """Загрузить лексикон (banned_words, tags_allow_list, phrases)."""
    path = CONTENT_DIR / "lexicon" / "lexicon.json"
    return _load_json_object(path)


def load_daily_forecasts_raw() -> List[Dict[str, Any]]:
    """Загрузить все DailyForecast из CONTENT/forecasts/daily_forecasts.json (без Quality Gate)."""
    path = CONTENT_DIR / "forecasts" / "daily_forecasts.json"
    arr = _load_json_array(path)
    return [x for x in arr if isinstance(x, dict)]


def _quality_gate_sets() -> tuple:
    """Подготовить множества для Quality Gate из словарей и лексикона."""
    body = set(load_dictionary("body_markers"))
    social = set(load_dictionary("social_markers"))
    domestic = set(load_dictionary("domestic_details"))
    micro = set(load_dictionary("micro_actions"))
    lex = load_lexicon()
    banned = lex.get("banned_words") or []
    tags_allow = lex.get("tags_allow_list") or []
    return body, social, domestic, micro, banned, tags_allow


def _validate_daily_forecast(forecast: Dict[str, Any]) -> bool:
    """Проверить один DailyForecast через Quality Gate. True = ok."""
    from todayflow_backend.data.quality_gate import validate_daily_forecast

    body, social, domestic, micro, banned, tags_allow = _quality_gate_sets()
    result = validate_daily_forecast(
        forecast,
        body_markers=body,
        social_markers=social,
        domestic_markers=domestic,
        micro_action_markers=micro,
        banned_words=banned,
        tags_allow_list=tags_allow,
    )
    return result.ok


def load_daily_forecasts(
    locale: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    published_only: bool = True,
) -> List[Dict[str, Any]]:
    """
    Список DailyForecast. Фильтр по locale, from_date, to_date.
    Если published_only=True — только published и прошедшие Quality Gate.
    """
    raw = load_daily_forecasts_raw()
    out: List[Dict[str, Any]] = []
    for f in raw:
        if published_only and not f.get("published"):
            continue
        if published_only and not _validate_daily_forecast(f):
            continue
        if locale is not None and f.get("locale") != locale:
            continue
        d = f.get("date")
        if not isinstance(d, str):
            continue
        if from_date is not None and d < from_date:
            continue
        if to_date is not None and d > to_date:
            continue
        out.append(f)
    out.sort(key=lambda x: x.get("date") or "")
    return out


def get_daily_forecast_by_date(date: str, locale: str) -> Optional[Dict[str, Any]]:
    """
    Один DailyForecast по дате и языку.
    Только published и прошедшие Quality Gate.
    """
    raw = load_daily_forecasts_raw()
    for f in raw:
        if f.get("date") != date or f.get("locale") != locale:
            continue
        if not f.get("published"):
            return None
        if not _validate_daily_forecast(f):
            return None
        return f
    return None


def list_daily_forecasts(
    locale: str,
    from_date: str,
    to_date: str,
    published_only: bool = True,
) -> List[Dict[str, Any]]:
    """Удобная обёртка: список за период."""
    return load_daily_forecasts(
        locale=locale,
        from_date=from_date,
        to_date=to_date,
        published_only=published_only,
    )


def save_daily_forecasts(forecasts: List[Dict[str, Any]]) -> None:
    """Сохранить список DailyForecast в CONTENT/forecasts/daily_forecasts.json (admin)."""
    path = CONTENT_DIR / "forecasts" / "daily_forecasts.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(forecasts, f, ensure_ascii=False, indent=2)


def save_lexicon(data: Dict[str, Any]) -> None:
    """Сохранить лексикон в CONTENT/lexicon/lexicon.json (admin)."""
    path = CONTENT_DIR / "lexicon" / "lexicon.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


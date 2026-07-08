"""Safety validator for generated forecast payloads.

Legacy "quality gate" is no longer the source of meaning or style.
Its role is intentionally narrow:
- verify payload shape,
- reject empty/broken blocks,
- reject banned garbage,
- reject invalid tags/markers,
- reject duplicate lines.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Set

from todayflow_backend.core.text_quality import contains_dead_pattern, find_duplicate_lines, normalize_text


# Ограничения
THEME_MAX_LEN = 300
NOTICE_MIN = 1
NOTICE_MAX = 4
SCENE_MIN = 1
SCENE_MAX = 4
MICRO_ACTION_MAX_LEN = 200


@dataclass
class QualityGateResult:
    ok: bool
    errors: List[str] = field(default_factory=list)

    def add(self, msg: str) -> None:
        self.errors.append(msg)
        self.ok = False


def _collect_text(forecast: Dict[str, Any]) -> str:
    """Собрать весь текст прогноза для проверки стоп-слов."""
    parts: List[str] = []
    blocks = forecast.get("blocks") or {}
    if isinstance(blocks.get("theme"), str):
        parts.append(blocks["theme"])
    for key in ("notice", "scene"):
        items = blocks.get(key)
        if isinstance(items, list):
            parts.extend(str(x) for x in items if isinstance(x, str))
    if isinstance(blocks.get("micro_action"), str):
        parts.append(blocks["micro_action"])
    return " ".join(parts).lower()


def validate_daily_forecast(
    forecast: Dict[str, Any],
    *,
    body_markers: Set[str],
    social_markers: Set[str],
    domestic_markers: Set[str],
    micro_action_markers: Set[str],
    banned_words: List[str],
    tags_allow_list: List[str],
) -> QualityGateResult:
    """Валидировать один DailyForecast."""
    r = QualityGateResult(ok=True)
    blocks = forecast.get("blocks") or {}
    markers = forecast.get("markers") or {}
    tags = forecast.get("tags") or []

    text_lines: List[str] = []

    # 1. theme — непустая строка с ограничением по длине
    theme = blocks.get("theme")
    if not isinstance(theme, str) or not theme.strip():
        r.add("blocks.theme: должна быть одна непустая строка")
    elif len(theme) > THEME_MAX_LEN:
        r.add(f"blocks.theme: длина не более {THEME_MAX_LEN} символов")
    else:
        text_lines.append(theme.strip())

    # 2. notice — массив непустых строк
    notice = blocks.get("notice")
    if not isinstance(notice, list):
        r.add("blocks.notice: должен быть массив строк")
    else:
        notice_strs = [x for x in notice if isinstance(x, str) and x.strip()]
        if len(notice_strs) < NOTICE_MIN or len(notice_strs) > NOTICE_MAX:
            r.add(f"blocks.notice: должно быть от {NOTICE_MIN} до {NOTICE_MAX} пунктов")
        for idx, line in enumerate(notice_strs, start=1):
            text_lines.append(line.strip())

    # 3. scene — массив непустых строк
    scene = blocks.get("scene")
    if not isinstance(scene, list):
        r.add("blocks.scene: должен быть массив строк")
    else:
        scene_strs = [x for x in scene if isinstance(x, str) and x.strip()]
        if len(scene_strs) < SCENE_MIN or len(scene_strs) > SCENE_MAX:
            r.add(f"blocks.scene: должно быть от {SCENE_MIN} до {SCENE_MAX} пунктов")
        for idx, line in enumerate(scene_strs, start=1):
            text_lines.append(line.strip())

    # 4. micro_action — непустая строка
    ma = blocks.get("micro_action")
    if not isinstance(ma, str) or not ma.strip():
        r.add("blocks.micro_action: должна быть одна непустая строка")
    elif len(ma) > MICRO_ACTION_MAX_LEN:
        r.add(f"blocks.micro_action: длина не более {MICRO_ACTION_MAX_LEN} символов")
    elif contains_dead_pattern(normalize_text(ma.strip())):
        r.add("blocks.micro_action: шаблонная формулировка")
    else:
        text_lines.append(ma.strip())

    # 5. markers — если переданы, должны быть массивами допустимых значений
    for key, allowed in (
        ("body", body_markers),
        ("social", social_markers),
        ("domestic", domestic_markers),
        ("micro_action", micro_action_markers),
    ):
        arr = markers.get(key)
        if arr is None:
            continue
        if not isinstance(arr, list):
            r.add(f"markers.{key}: должен быть массив")
        else:
            vals = [x for x in arr if isinstance(x, str) and x.strip()]
            for v in vals:
                if v not in allowed:
                    r.add(f"markers.{key}: '{v}' не найден в словаре")

    # 6. стоп-слова
    text = _collect_text(forecast)
    for bw in banned_words:
        if bw.lower() in text:
            r.add(f"стоп-слово: '{bw}'")

    # 7. теги только из allow-list
    allow_set = set(tags_allow_list)
    for t in tags:
        if not isinstance(t, str) or t not in allow_set:
            r.add(f"тег '{t}' не в allow-list")

    # 8. Внутренние повторы в блоках
    if find_duplicate_lines(text_lines):
        r.add("дублирование: повторяющиеся строки в блоках")

    return r

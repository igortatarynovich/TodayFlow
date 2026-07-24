"""Planet returns soft layer (canon §5.3 `planet_returns`).

School freeze v0:
- Classical bodies Sun…Saturn via soft mean longitudes (noon).
- Find last/next civil date when mean lon ≈ natal mean lon.
- Highlight Mars / Jupiter / Saturn; include Mercury/Venus/Sun/Moon in pack.
- Not a full return chart — period event markers only.
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from todayflow_backend.services.day_sources.classical_longitudes import (
    ang_dist,
    classical_bodies,
    classical_longitude,
    period_days,
)

_PLANET_RU = {
    "Sun": "Солнце",
    "Moon": "Луна",
    "Mercury": "Меркурий",
    "Venus": "Венера",
    "Mars": "Марс",
    "Jupiter": "Юпитер",
    "Saturn": "Сатурн",
}

_HIGHLIGHT = ("Mars", "Jupiter", "Saturn")


def _best_in_window(
    natal_lon: float,
    center: date,
    body: str,
    *,
    half_window: int,
) -> tuple[date, float, float]:
    best_d = center
    best_lon = classical_longitude(body, center)
    best_err = ang_dist(best_lon, natal_lon)
    for delta in range(-half_window, half_window + 1):
        if delta == 0:
            continue
        d = center + timedelta(days=delta)
        lon = classical_longitude(body, d)
        err = ang_dist(lon, natal_lon)
        if err < best_err:
            best_err = err
            best_d = d
            best_lon = lon
    return best_d, best_lon, best_err


def find_return_for_cycle(
    body: str,
    birth_date: date,
    cycle: int,
) -> tuple[date, float, float]:
    """Return (date, lon, err) for the N-th soft return after birth (cycle≥0 = birth itself)."""
    natal = classical_longitude(body, birth_date)
    period = period_days(body)
    c = max(0, int(cycle))
    seed = birth_date + timedelta(days=round(c * period))
    window = 2 if body == "Moon" else (3 if body == "Sun" else min(14, max(5, int(period * 0.015))))
    return _best_in_window(natal, seed, body, half_window=window)


def nearest_cycle_index(body: str, birth_date: date, around: date) -> int:
    period = period_days(body)
    days = max(0, (around - birth_date).days)
    return max(0, int(round(days / period)))


def find_return_near(body: str, birth_date: date, around: date) -> tuple[date, float, float]:
    """Closest soft return date to `around` among neighboring cycles."""
    base = nearest_cycle_index(body, birth_date, around)
    best: tuple[date, float, float] | None = None
    best_dist: int | None = None
    for c in (base - 1, base, base + 1):
        if c < 0:
            continue
        d, lon, err = find_return_for_cycle(body, birth_date, c)
        dist = abs((d - around).days)
        if best is None or dist < (best_dist or 10**9) or (
            dist == best_dist and err < best[2]
        ):
            best = (d, lon, err)
            best_dist = dist
    assert best is not None
    return best


def build_body_return(
    body: str,
    birth_date: date,
    target_date: date,
) -> dict[str, Any]:
    natal_lon = classical_longitude(body, birth_date)
    base = nearest_cycle_index(body, birth_date, target_date)

    # Evaluate neighboring cycles; pick last ≤ target and next > target.
    candidates: list[tuple[int, date, float, float]] = []
    for c in range(max(0, base - 1), base + 3):
        d, lon, err = find_return_for_cycle(body, birth_date, c)
        candidates.append((c, d, lon, err))

    last_row = None
    next_row = None
    for row in candidates:
        _c, d, _lon, _err = row
        if d <= target_date:
            last_row = row
        elif next_row is None and d > target_date:
            next_row = row
            break

    if last_row is None:
        # Target before first post-birth return refinement — use cycle 0 as last.
        last_row = candidates[0]
    if next_row is None:
        c_last = last_row[0]
        d, lon, err = find_return_for_cycle(body, birth_date, c_last + 1)
        next_row = (c_last + 1, d, lon, err)

    _lc, last_d, last_lon, last_err = last_row
    _nc, next_d, next_lon, next_err = next_row

    days_since = (target_date - last_d).days
    days_until = (next_d - target_date).days
    band = min(45, max(14, int(period_days(body) * 0.03)))
    active = days_since <= band or days_until <= band

    return {
        "body": body,
        "body_ru": _PLANET_RU[body],
        "natal_longitude": round(natal_lon, 4),
        "return_date": last_d.isoformat(),
        "next_return_date": next_d.isoformat(),
        "days_since_return": days_since,
        "days_until_next": days_until,
        "noon_error_deg": round(last_err, 4),
        "next_noon_error_deg": round(next_err, 4),
        "active_band_days": band,
        "in_return_window": active,
        "return_longitude": round(last_lon, 4),
        "cycle_last": _lc,
        "cycle_next": _nc,
    }


def build_planet_returns(
    birth_date: date,
    target_date: date,
) -> dict[str, Any]:
    returns = [build_body_return(b, birth_date, target_date) for b in classical_bodies()]
    by_body = {r["body"]: r for r in returns}
    highlights = [by_body[b] for b in _HIGHLIGHT if b in by_body]
    active = [r for r in returns if r["in_return_window"]]

    if active:
        labels = ", ".join(f"{r['body_ru']}" for r in active[:3])
        summary = f"Возвраты планет (soft): в окне — {labels}."
    else:
        nearest = min(highlights, key=lambda r: min(r["days_since_return"], r["days_until_next"]))
        side = (
            f"последний {nearest['days_since_return']} дн. назад"
            if nearest["days_since_return"] <= nearest["days_until_next"]
            else f"через {nearest['days_until_next']} дн."
        )
        summary = (
            f"Возвраты планет (soft): окно тихо. Ближайший акцент — "
            f"{nearest['body_ru']} ({side})."
        )

    beat = {
        "id": "planet-returns-soft",
        "kind": "planet_returns",
        "title": "Возвраты планет",
        "story_ru": summary,
        "evidence_ref": "personal_astrology.planet_returns",
    }

    return {
        "capability_id": "planet_returns",
        "school_canon": "classical_mean_longitude_returns_v0",
        "depth": "mean_longitude_noon",
        "returns": returns,
        "highlights": highlights,
        "active": active,
        "limitation_ru": (
            "Mean-longitude noon soft (не точный Swiss return). "
            "Solar/lunar return charts — отдельные capabilities."
        ),
        "beats": [beat],
        "summary_ru": summary[:420],
    }

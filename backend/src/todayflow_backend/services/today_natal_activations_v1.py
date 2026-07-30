"""Wave 2 — single SoT for natal transit activations (schema pool for Strip / Act 3 / Glance).

compute_natal_activations is pure (no DB). resolve_* loads geometry once and TTL-caches
the snapshot so Act 1 strip and day_scenario foundation share the same list within a Today load.
Full day_facts_v1 materialization remains Phase D.
"""

from __future__ import annotations

import logging
import threading
import time
from datetime import date
from typing import Any, Iterable

logger = logging.getLogger(__name__)

TTL_SECONDS = 7 * 60  # 5–10 min window; 7m midpoint
_LOCK = threading.Lock()
# key → (expires_at_monotonic, activations, degraded)
_SNAPSHOT: dict[str, tuple[float, list[dict[str, Any]], bool]] = {}

_STRENGTH_RANK = {"exact": 0, "strong": 1, "medium": 2, "weak": 3}


def _norm(name: str | None) -> str:
    return (name or "").strip().lower().replace(" ", "_")


def cache_key_for(user_id: int, local_date: date) -> str:
    return f"{int(user_id)}:{local_date.isoformat()}"


def get_snapshot(key: str) -> tuple[list[dict[str, Any]], bool] | None:
    """Return (activations, degraded) or None on miss/expiry."""
    now = time.monotonic()
    with _LOCK:
        hit = _SNAPSHOT.get(key)
        if not hit:
            return None
        expires_at, rows, degraded = hit
        if now >= expires_at:
            _SNAPSHOT.pop(key, None)
            return None
        return [dict(r) for r in rows], bool(degraded)


def put_snapshot(key: str, rows: list[dict[str, Any]], *, degraded: bool = False) -> None:
    """Cache a successful (or explicitly degraded) snapshot. Do not call on unexpected exceptions."""
    payload = [dict(r) for r in rows]
    with _LOCK:
        _SNAPSHOT[key] = (time.monotonic() + TTL_SECONDS, payload, bool(degraded))


def clear_snapshots() -> None:
    """Test helper."""
    with _LOCK:
        _SNAPSHOT.clear()


def compute_natal_activations(transits: Iterable[Any]) -> list[dict[str, Any]]:
    """
    Pure: TransitToNatal-like objects / dicts → Wave2 Activation rows.

    Fields: id, transiting_planet, aspect, natal_point, orb_deg,
            exact_time_local (null until Phase C), rank (1 = strongest).
    """
    raw: list[dict[str, Any]] = []
    for i, t in enumerate(transits):
        if isinstance(t, dict):
            transiting = t.get("transiting_planet") or t.get("planet")
            natal = t.get("natal_planet") or t.get("natal_point")
            aspect = t.get("aspect") or t.get("aspect_id")
            orb = t.get("orb_deg")
            if orb is None:
                orb = t.get("orb_delta")
            strength = t.get("strength")
            tid = t.get("id")
        else:
            transiting = getattr(t, "transiting_planet", None)
            natal = getattr(t, "natal_planet", None) or getattr(t, "natal_point", None)
            aspect = getattr(t, "aspect_id", None) or getattr(t, "aspect", None)
            orb = getattr(t, "orb_delta", None)
            if orb is None:
                orb = getattr(t, "orb_deg", 0.0)
            strength = getattr(t, "strength", None)
            tid = getattr(t, "id", None)
        if not transiting or not natal or not aspect:
            continue
        t_s = str(transiting)
        n_s = str(natal)
        a_s = str(aspect)
        stable = str(tid) if tid else f"pt-{t_s}-{a_s}-{n_s}".lower().replace(" ", "_")
        raw.append(
            {
                "id": stable,
                "transiting_planet": t_s,
                "aspect": a_s,
                "natal_point": n_s,
                "orb_deg": float(orb or 0.0),
                "exact_time_local": None,
                "strength": str(strength or "medium"),
            }
        )

    raw.sort(
        key=lambda r: (
            _STRENGTH_RANK.get(str(r.get("strength") or "").lower(), 9),
            float(r.get("orb_deg") or 99.0),
            _norm(str(r.get("transiting_planet"))),
            _norm(str(r.get("natal_point"))),
        )
    )
    out: list[dict[str, Any]] = []
    for rank, row in enumerate(raw, start=1):
        item = {
            "id": row["id"],
            "transiting_planet": row["transiting_planet"],
            "aspect": row["aspect"],
            "natal_point": row["natal_point"],
            "orb_deg": row["orb_deg"],
            "exact_time_local": None,
            "rank": rank,
        }
        out.append(item)
    return out


def foundation_rows_from_activations(activations: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    """Project geometric activations into day_scenario foundation personal_natal_activations shape."""
    from todayflow_backend.services.today_domain_verdicts_v1 import why_short_for

    out: list[dict[str, Any]] = []
    for act in activations:
        if not isinstance(act, dict):
            continue
        tid = str(act.get("id") or "").strip()
        if not tid:
            continue
        t = str(act.get("transiting_planet") or "")
        a = str(act.get("aspect") or "")
        n = str(act.get("natal_point") or "")
        text = why_short_for(t, a, n) if (t and a and n) else str(act.get("text") or "").strip()
        if not text:
            continue
        out.append(
            {
                "id": tid,
                "text": text,
                "evidence_ids": [tid],
                "layer": "personal",
                "transiting_planet": t or None,
                "aspect": a or None,
                "natal_point": n or None,
                "orb_deg": act.get("orb_deg"),
                "rank": act.get("rank"),
                "exact_time_local": act.get("exact_time_local"),
            }
        )
    return out


def natal_conflict_driver_ids(
    personal_natal_activations: Iterable[dict[str, Any]] | None,
    *,
    limit: int = 3,
) -> list[str]:
    """Wave 2 D.2b — conflict.driver_ids SoT = top natal activation ids (`pt-*`).

    Pack ranked_drivers stay on foundation for dramaturgy provenance. Claim/prose
    ids (claim.*, day_personal.*) are not Strip pool members — skip them.
    """
    rows: list[dict[str, Any]] = []
    for row in personal_natal_activations or []:
        if not isinstance(row, dict):
            continue
        tid = str(row.get("id") or "").strip()
        if not tid.lower().startswith("pt-"):
            continue
        rows.append(row)

    def _rank_key(row: dict[str, Any]) -> tuple[int, str]:
        raw = row.get("rank")
        try:
            rk = int(raw) if raw is not None else 10_000
        except (TypeError, ValueError):
            rk = 10_000
        return (rk, str(row.get("id") or ""))

    rows.sort(key=_rank_key)
    out: list[str] = []
    seen: set[str] = set()
    for row in rows:
        tid = str(row.get("id") or "").strip()
        if not tid or tid in seen:
            continue
        seen.add(tid)
        out.append(tid)
        if len(out) >= max(1, int(limit)):
            break
    return out


async def resolve_natal_activations(
    *,
    user_id: int,
    local_date: date,
    natal_chart: Any | None,
    birth_data: Any | None,
    transit_service: Any,
) -> tuple[list[dict[str, Any]], bool]:
    """
    Return (activations, degraded).
    Uses TTL snapshot so strip + day_scenario see the same list within one Today load.
    """
    key = cache_key_for(user_id, local_date)
    hit = get_snapshot(key)
    if hit is not None:
        return hit

    try:
        if not natal_chart or not getattr(natal_chart, "positions", None):
            # Honest no-natal — cache as degraded so we don't flip to silent calm.
            put_snapshot(key, [], degraded=True)
            return [], True
        raw = await transit_service._calculate_transits(
            natal_chart, local_date, birth_data=birth_data
        )
        rows = compute_natal_activations(raw)
        put_snapshot(key, rows, degraded=False)
        return [dict(r) for r in rows], False
    except Exception:
        logger.exception(
            "natal_activations_resolve_failed user=%s date=%s", user_id, local_date.isoformat()
        )
        # Do NOT cache exceptions — retry next request; avoid silent calm poison.
        return [], True


async def resolve_natal_activations_for_user(
    *,
    user: Any,
    local_date: date,
    db: Any,
    locale: str,
) -> tuple[list[dict[str, Any]], bool]:
    """Load natal + compute (or cache hit). Used by GET /today/domain-verdicts."""
    key = cache_key_for(int(user.id), local_date)
    hit = get_snapshot(key)
    if hit is not None:
        return hit

    from todayflow_backend.api import reports as reports_api
    from todayflow_backend.services import astro as astro_mod
    from todayflow_backend.services.geocode import Geocoder
    from todayflow_backend.services.personal_transits import get_personal_transit_service

    try:
        transit_service = await get_personal_transit_service()
        geocoder = Geocoder()
        astro_service = astro_mod.AstroService()
        astro_profile = await reports_api._get_user_astro_profile(user, db, None, locale)
        birth_data = await reports_api._prepare_birth_data(astro_profile, geocoder, locale)
        natal_chart = await reports_api._compute_natal_chart(
            birth_data, astro_service, astro_profile, db
        )
        return await resolve_natal_activations(
            user_id=int(user.id),
            local_date=local_date,
            natal_chart=natal_chart,
            birth_data=birth_data,
            transit_service=transit_service,
        )
    except Exception:
        logger.exception(
            "natal_activations_user_resolve_failed user=%s date=%s",
            getattr(user, "id", None),
            local_date.isoformat(),
        )
        # Do NOT cache exceptions — next call retries.
        return [], True

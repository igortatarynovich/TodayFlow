"""Wave 2 Phase D.1 / D.1b — assemble day_facts_v1.

D.1: activations + domain_verdicts + glance_timeline.
D.1b: project cached day_scenario narrative when conflict drivers ⊆ fresh pool.
"""

from __future__ import annotations

import logging
from datetime import date, datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)

SCHEMA_VERSION = "day_facts_v1"


def _empty_envelope(
    *,
    facts_id: str,
    user_id: int,
    local_date: date,
    timezone_name: str,
    degraded: bool,
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "id": facts_id,
        "user_id": str(user_id),
        "date": local_date.isoformat(),
        "timezone": timezone_name,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "natal_activations": [],
        "domain_verdicts": [],
        "glance_timeline": [],
        "conflict": None,
        "scenes": [],
        "props": None,
        "sky_drivers": [],
        "moon_phase": None,
        "numerology": None,
        "generation_provenance": {
            "conflict_driver_ids": [],
            "verdict_driver_ids": {
                "work": [],
                "money": [],
                "relationships": [],
                "energy": [],
            },
            "timeline_driver_ids": [],
        },
        "degraded": degraded,
        "is_fallback": degraded,
        "partial": True,
    }


def _verdict_provenance(domain_verdicts: list[dict[str, Any]]) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {
        "work": [],
        "money": [],
        "relationships": [],
        "energy": [],
    }
    for row in domain_verdicts:
        domain = str(row.get("domain") or "")
        if domain in out:
            ids = [str(x) for x in (row.get("driver_ids") or []) if x]
            out[domain] = ids
    return out


async def assemble_day_facts_v1(
    *,
    user: Any,
    local_date: date,
    db: Any,
    locale: str,
    timezone_name: str | None = None,
) -> dict[str, Any]:
    """Build day_facts_v1: slots always; narrative when temporal gate passes."""
    from todayflow_backend.api import reports as reports_api
    from todayflow_backend.services import astro as astro_mod
    from todayflow_backend.services import today_day_facts_project_v1 as project_svc
    from todayflow_backend.services import today_domain_verdicts_v1 as verdict_svc
    from todayflow_backend.services import today_glance_timeline_v1 as glance_svc
    from todayflow_backend.services import today_natal_activations_v1 as act_svc
    from todayflow_backend.services import today_tap_widget_v1 as tap_svc
    from todayflow_backend.services.day_lifecycle_clock_c5 import resolve_user_timezone
    from todayflow_backend.services.geocode import Geocoder
    from todayflow_backend.services.personal_transits import get_personal_transit_service

    user_id = int(user.id)
    facts_id = tap_svc.day_facts_id_for(user_id, local_date)
    tz_name = resolve_user_timezone(db, user_id=user_id, explicit=timezone_name)

    try:
        transit_service = await get_personal_transit_service()
        geocoder = Geocoder()
        astro_service = astro_mod.AstroService()
        astro_profile = await reports_api._get_user_astro_profile(user, db, None, locale)
        birth_data = await reports_api._prepare_birth_data(astro_profile, geocoder, locale)
        natal_chart = await reports_api._compute_natal_chart(
            birth_data, astro_service, astro_profile, db
        )
        activations, degraded = await act_svc.resolve_natal_activations(
            user_id=user_id,
            local_date=local_date,
            natal_chart=natal_chart,
            birth_data=birth_data,
            transit_service=transit_service,
        )
    except Exception:
        logger.exception(
            "day_facts_assemble_failed user=%s date=%s", user_id, local_date.isoformat()
        )
        return _empty_envelope(
            facts_id=facts_id,
            user_id=user_id,
            local_date=local_date,
            timezone_name=tz_name,
            degraded=True,
        )

    if degraded:
        return _empty_envelope(
            facts_id=facts_id,
            user_id=user_id,
            local_date=local_date,
            timezone_name=tz_name,
            degraded=True,
        )

    domain_verdicts = verdict_svc.compute_domain_verdicts(activations)

    coords = None
    if birth_data and getattr(birth_data, "coordinates", None):
        coords = {
            "latitude": float(birth_data.coordinates.latitude),
            "longitude": float(birth_data.coordinates.longitude),
        }

    glance_rows: list[dict[str, Any]] = []
    enriched = activations
    try:
        glance_rows, enriched = await glance_svc.compute_glance_timeline(
            activations=activations,
            natal_chart=natal_chart,
            local_date=local_date,
            timezone_name=tz_name,
            astro_service=astro_service,
            coordinates=coords,
        )
    except Exception:
        logger.exception(
            "day_facts_glance_failed user=%s date=%s", user_id, local_date.isoformat()
        )
        glance_rows = []
        enriched = activations

    # Kimi activity-window titles/details from prewarm cache; bank fill-empty on miss.
    try:
        from todayflow_backend.services import day_flow_windows_kimi_v1 as flow_win

        glance_rows = flow_win.apply_cached_or_bank(
            db,
            user_id=user_id,
            local_date=local_date,
            glance_rows=glance_rows,
        )
    except Exception:
        logger.exception(
            "day_facts_flow_windows_merge_failed user=%s date=%s",
            user_id,
            local_date.isoformat(),
        )

    timeline_ids = [str(r.get("driver_id") or "") for r in glance_rows if r.get("driver_id")]

    conflict = None
    scenes: list[dict[str, Any]] = []
    props = None
    sky_drivers: list[dict[str, Any]] = []
    moon_phase = None
    numerology = None
    conflict_driver_ids: list[str] = []
    partial = True

    try:
        scenario = project_svc.load_ready_day_scenario(
            db, user_id=user_id, local_date=local_date
        )
        if scenario:
            blob = project_svc.project_narrative_blob(scenario, activations=enriched)
            if blob:
                conflict = blob.get("conflict")
                scenes = list(blob.get("scenes") or [])
                props = blob.get("props")
                sky_drivers = list(blob.get("sky_drivers") or [])
                moon_phase = blob.get("moon_phase")
                numerology = blob.get("numerology")
                conflict_driver_ids = list((conflict or {}).get("driver_ids") or [])
                partial = False
    except Exception:
        logger.exception(
            "day_facts_narrative_project_failed user=%s date=%s",
            user_id,
            local_date.isoformat(),
        )

    return {
        "schema_version": SCHEMA_VERSION,
        "id": facts_id,
        "user_id": str(user_id),
        "date": local_date.isoformat(),
        "timezone": tz_name,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "natal_activations": [dict(a) for a in enriched],
        "domain_verdicts": domain_verdicts,
        "glance_timeline": glance_rows,
        "conflict": conflict,
        "scenes": scenes,
        "props": props,
        "sky_drivers": sky_drivers,
        "moon_phase": moon_phase,
        "numerology": numerology,
        "generation_provenance": {
            "conflict_driver_ids": conflict_driver_ids,
            "verdict_driver_ids": _verdict_provenance(domain_verdicts),
            "timeline_driver_ids": timeline_ids,
        },
        "degraded": False,
        "is_fallback": False,
        "partial": partial,
    }

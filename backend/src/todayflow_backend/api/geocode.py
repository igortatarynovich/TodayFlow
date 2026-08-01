"""Simple geocoding lookup endpoint."""

from fastapi import APIRouter, HTTPException, Query, Request

from todayflow_backend.i18n import request_locale, translate
from todayflow_backend.services.geocode import Geocoder

router = APIRouter(prefix="/astro", tags=["geocode"])
geocoder = Geocoder()


@router.get("/geocode")
def lookup_location(request: Request, q: str = Query(..., min_length=2, alias="q")) -> dict:
    """Resolve one place. Ambiguous matches return 409 + candidates (no silent pick)."""
    result = geocoder.lookup(q)
    if not result:
        raise HTTPException(
            status_code=404, detail=translate("geocode.errors.notFound", locale=request_locale(request))
        )
    if result.get("need_choice"):
        raise HTTPException(
            status_code=409,
            detail={
                "code": "geocode_ambiguous",
                "message": result.get("message")
                or translate(
                    "geocode.errors.ambiguous",
                    locale=request_locale(request),
                    default="Several places match — choose country/region.",
                ),
                "candidates": result.get("candidates") or [],
            },
        )
    return result


@router.get("/geocode/suggest")
def suggest_locations(q: str = Query(..., min_length=2, alias="q"), limit: int = Query(8, ge=1, le=12)) -> list[dict]:
    return geocoder.suggest(q, limit=limit)

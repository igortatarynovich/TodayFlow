"""Simple geocoding lookup endpoint."""

from fastapi import APIRouter, HTTPException, Query, Request

from todayflow_backend.i18n import request_locale, translate
from todayflow_backend.services.geocode import Geocoder

router = APIRouter(prefix="/astro", tags=["geocode"])
geocoder = Geocoder()


@router.get("/geocode")
def lookup_location(request: Request, q: str = Query(..., min_length=2, alias="q")) -> dict:
    result = geocoder.lookup(q)
    if not result:
        raise HTTPException(
            status_code=404, detail=translate("geocode.errors.notFound", locale=request_locale(request))
        )
    return result


@router.get("/geocode/suggest")
def suggest_locations(q: str = Query(..., min_length=2, alias="q"), limit: int = Query(8, ge=1, le=12)) -> list[dict]:
    return geocoder.suggest(q, limit=limit)

"""Reference data endpoints exposing canonical astrology metadata."""

from fastapi import APIRouter, Request

from todayflow_backend.data import astrology
from todayflow_backend.i18n import request_locale, translate

router = APIRouter(prefix="/reference", tags=["reference"])


@router.get("/zodiac")
def get_zodiac_signs(request: Request) -> list[dict]:
    """Return canonical zodiac sign metadata."""
    locale = request_locale(request)
    records = astrology.zodiac_signs()
    for record in records:
        record["name"] = translate(f"sign.{record['id']}.name", locale=locale, default=record.get("name", record["id"]))
        if "element" in record:
            record["element"] = translate(f"sign.{record['id']}.element", locale=locale, default=record["element"])
        if "modality" in record:
            record["modality"] = translate(f"sign.{record['id']}.modality", locale=locale, default=record["modality"])
        if "themes" in record and isinstance(record["themes"], list):
            record["themes"] = [
                translate(f"sign.{record['id']}.themes.{idx}", locale=locale, default=value)
                for idx, value in enumerate(record["themes"], start=1)
            ]
    return records


@router.get("/planets")
def get_planets(request: Request) -> list[dict]:
    """Return canonical planet metadata."""
    locale = request_locale(request)
    planets = astrology.planets()
    for planet in planets:
        prefix = f"planet.{planet['id']}"
        planet["name"] = translate(f"{prefix}.name", locale=locale, default=planet.get("name", planet["id"]))
        if "keywords" in planet:
            planet["keywords"] = [
                translate(f"{prefix}.keywords.{idx}", locale=locale, default=value)
                for idx, value in enumerate(planet.get("keywords", []), start=1)
            ]
        if "psychology" in planet:
            planet["psychology"] = translate(
                f"{prefix}.psychology", locale=locale, default=planet.get("psychology", "")
            )
    return planets


@router.get("/houses")
def get_houses(request: Request) -> list[dict]:
    """Return canonical house metadata."""
    locale = request_locale(request)
    houses = astrology.houses()
    for house in houses:
        prefix = f"house.{house['id']}"
        house["name"] = translate(f"{prefix}.name", locale=locale, default=house.get("name", house["id"]))
        house["description"] = translate(
            f"{prefix}.description", locale=locale, default=house.get("description", "")
        )
    return houses


@router.get("/mantras")
def get_mantras(request: Request) -> list[dict]:
    """Return all mantras from the library."""
    from todayflow_backend.i18n import localize_mantra
    locale = request_locale(request)
    mantras = astrology.mantras()
    # Локализуем каждую мантру
    localized = []
    # Try to get human_text from Content System
    from todayflow_backend.data import content_system
    
    for mantra in mantras:
        localized_mantra = localize_mantra(mantra, locale=locale)
        
        # Try to get human_text from Content System
        mantra_id = mantra.get("id") or mantra.get("mantra_id")
        if mantra_id:
            try:
                content_mantra = content_system.get_mantra_by_id(mantra_id)
                if content_mantra and content_mantra.get("human_text"):
                    localized_mantra["human_text"] = content_mantra["human_text"]
            except Exception:
                pass  # Fallback to existing data
        
        localized.append(localized_mantra)
    return localized

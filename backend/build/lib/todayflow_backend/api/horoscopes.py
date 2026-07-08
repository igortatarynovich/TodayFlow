"""Multi-horoscope endpoints for birth chart preview."""

from fastapi import APIRouter, Request
from pydantic import BaseModel
from datetime import date, datetime, time
from typing import Optional

from todayflow_backend.services.chinese_horoscope import get_chinese_horoscope_service
from todayflow_backend.services.zoroastrian_horoscope import get_zoroastrian_horoscope_service
from todayflow_backend.services.tibetan_horoscope import get_tibetan_horoscope_service
from todayflow_backend.services.numerology import get_numerology_service

router = APIRouter(prefix="/horoscopes", tags=["horoscopes"])


class BirthDatePayload(BaseModel):
    birth_date: date
    birth_time: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    full_name: str | None = None  # For numerology


@router.post("/all")
async def get_all_horoscopes(request: Request, payload: BirthDatePayload) -> dict:
    """Get all horoscope information for a birth date."""
    chinese_service = get_chinese_horoscope_service()
    zoroastrian_service = get_zoroastrian_horoscope_service()
    tibetan_service = get_tibetan_horoscope_service()
    
    results = {
        "chinese": chinese_service.calculate(payload.birth_date),
        "zoroastrian": zoroastrian_service.calculate(payload.birth_date),
        "tibetan": tibetan_service.calculate(payload.birth_date),
    }
    
    # Add Western astrology if time and coordinates are provided
    if payload.birth_time and payload.latitude is not None and payload.longitude is not None:
        try:
            from todayflow_backend.services.astro import AstroService
            astro_service = AstroService()
            
            # Parse time string (HH:MM format)
            time_parts = payload.birth_time.split(":")
            birth_time_str = f"{time_parts[0]}:{time_parts[1] if len(time_parts) > 1 else '00'}:00"
            
            birth_payload = {
                "date": payload.birth_date.isoformat(),
                "time": birth_time_str,
            }
            coordinates = {
                "latitude": payload.latitude,
                "longitude": payload.longitude,
            }
            
            chart_response = await astro_service.compute_chart(birth_payload=birth_payload, coordinates=coordinates)
            await astro_service.close()
            
            if chart_response and chart_response.positions:
                sun_sign = next((p.get("sign") for p in chart_response.positions if p.get("body") == "Sun"), None)
                moon_sign = next((p.get("sign") for p in chart_response.positions if p.get("body") == "Moon"), None)
                rising_sign = next(
                    (p.get("sign") for p in chart_response.positions if p.get("body") in {"Ascendant", "ASC", "rising", "Rising"}),
                    None,
                )
                
                if sun_sign or moon_sign or rising_sign:
                    results["astrology"] = {
                        "sun": sun_sign,
                        "moon": moon_sign,
                        "rising": rising_sign,
                        "description": f"Ваш знак Солнца: {sun_sign}" + (f", Луны: {moon_sign}" if moon_sign else "") + (f", Восходящий: {rising_sign}" if rising_sign else ""),
                    }
        except Exception as e:
            # Astrology is optional, don't fail if it errors
            import logging
            logging.getLogger(__name__).warning(f"Failed to calculate astrology: {e}")
            pass
    
    # Add numerology if full name is provided
    if payload.full_name:
        numerology_service = get_numerology_service()
        try:
            numerology_result = numerology_service.compute_profile(
                full_name=payload.full_name,
                birth_date=payload.birth_date.isoformat()
            )
            results["numerology"] = {
                "life_path": numerology_result.life_path.value,
                "life_path_summary": numerology_result.life_path.summary,
                "expression": numerology_result.expression.value,
                "expression_summary": numerology_result.expression.summary,
            }
        except Exception:
            pass  # Numerology is optional
    
    return results


"""Birth intake wizard endpoints."""

from fastapi import APIRouter

from todayflow_backend.core import models

router = APIRouter(prefix="/intake", tags=["intake"])


@router.post("/preview", response_model=models.BirthIntakePreview)
def preview_birth_intake(payload: models.BirthIntakePayload) -> models.BirthIntakePreview:
    warnings: list[str] = []
    if payload.birth_time is None and not payload.time_unknown:
        warnings.append("time_missing")

    return models.BirthIntakePreview(
        normalized_label=payload.label.strip(),
        birth_date=payload.birth_date,
        birth_time=None if payload.time_unknown else payload.birth_time,
        time_unknown=payload.time_unknown,
        timezone_name=payload.timezone_name,
        timezone_offset_minutes=payload.timezone_offset_minutes,
        location=payload.location.strip(),
        latitude=payload.latitude,
        longitude=payload.longitude,
        warnings=warnings,
    )

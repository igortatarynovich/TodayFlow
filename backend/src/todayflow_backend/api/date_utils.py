from __future__ import annotations

from datetime import date

from fastapi import HTTPException


def parse_iso_date_or_400(value: str, *, field_name: str = "target_date") -> date:
    """Parse YYYY-MM-DD date and raise uniform HTTP 400 on invalid value."""
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f"invalid {field_name}") from exc


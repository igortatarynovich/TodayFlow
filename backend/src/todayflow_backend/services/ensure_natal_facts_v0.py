"""Ensure natal_facts exist on an AstroProfile before personality / matrix attach.

Birth save and portrait publish must not rely only on a client-sent guest payload.
"""

from __future__ import annotations

import logging
from typing import Any

from sqlalchemy.orm import Session

from todayflow_backend.db import models as db_models
from todayflow_backend.services.natal_facts_contract_v1 import (
    build_available_input,
    generate_natal_facts,
    persist_natal_facts_on_profile,
    validate_natal_facts,
)

logger = logging.getLogger(__name__)


def load_cached_natal_facts(db: Session, astro_profile_id: int) -> dict[str, Any] | None:
    cached = (
        db.query(db_models.CachedNatalChart)
        .filter(db_models.CachedNatalChart.astro_profile_id == astro_profile_id)
        .first()
    )
    if not cached or not isinstance(cached.chart_metadata, dict):
        return None
    nf = cached.chart_metadata.get("natal_facts")
    if isinstance(nf, dict) and nf.get("planets"):
        return nf
    return None


def ensure_natal_facts_for_profile(
    db: Session,
    profile: db_models.AstroProfile,
    *,
    locale: str = "ru",
    display_name: str | None = None,
    access: str = "free",
    force: bool = False,
) -> dict[str, Any] | None:
    """Return validated natal_facts, generating + persisting when missing.

    Never raises for generation failure — returns None so portrait can form softly.
    """
    if profile.birth_date is None:
        return None

    if not force:
        existing = load_cached_natal_facts(db, profile.id)
        if existing is not None:
            try:
                return validate_natal_facts(
                    existing,
                    expected_mode=str(existing.get("mode") or "date_only"),
                )
            except Exception:
                logger.warning("ensure_natal_facts: cached invalid — regenerating", exc_info=True)

    try:
        available = build_available_input(
            birth_date=profile.birth_date,
            birth_time=None if profile.time_unknown else profile.birth_time,
            time_unknown=bool(profile.time_unknown),
            latitude=profile.latitude,
            longitude=profile.longitude,
            location_name=profile.location_name,
            timezone_name=profile.timezone_name,
            display_name=display_name,
            access=access,  # type: ignore[arg-type]
        )
        facts = generate_natal_facts(available_input=available, locale=locale)
        persist_natal_facts_on_profile(db, profile.id, facts)
        db.commit()
        return facts
    except Exception:
        logger.exception("ensure_natal_facts: generation failed for profile_id=%s", profile.id)
        try:
            db.rollback()
        except Exception:
            pass
        return None

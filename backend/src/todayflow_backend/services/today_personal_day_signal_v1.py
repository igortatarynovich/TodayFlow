"""Personal day signal selector: wires natal_activations + domain_verdicts + IL pack."""

from __future__ import annotations

from typing import Any


def select_personal_day_signal(
    foundation: dict[str, Any] | None,
) -> dict[str, Any] | None:
    """Return deterministic personal signal pack for My Day before LLM."""
    activations = list((foundation or {}).get("personal_natal_activations") or [])
    if not activations:
        return None

    from todayflow_backend.services.today_domain_verdicts_v1 import compute_domain_verdicts

    verdicts = compute_domain_verdicts(activations)

    main = activations[0]
    signal = {
        "transiting_planet": main.get("transiting_planet"),
        "aspect": main.get("aspect"),
        "natal_point": main.get("natal_point"),
        "orb_deg": main.get("orb_deg"),
        "strength": main.get("strength"),
        "domain": main.get("domain"),
        "text": main.get("text"),
    }

    il_pack = None
    try:
        from todayflow_backend.services.il4_surface_attach_v1 import (
            attach_from_celestial_ephemeris,
        )

        ce = (foundation or {}).get("celestial_events")
        if isinstance(ce, dict):
            il_pack = attach_from_celestial_ephemeris(ce, surface="today")
    except Exception:
        il_pack = None

    return {
        "contract_version": "personal_day_signal_v1",
        "main_signal": signal,
        "domain_verdicts": verdicts,
        "il_pack": il_pack,
    }

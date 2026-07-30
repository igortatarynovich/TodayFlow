"""Wave 2 Phase B — domain_verdicts via top_driver_v1 (not domain sum)."""

from __future__ import annotations

from typing import Any, Iterable

VERDICT_KEYS = ("calm", "charged", "friction", "open")
DOMAINS = ("work", "money", "relationships", "energy")

# Contract §2 — natal points / aliases that count for each domain.
DOMAIN_NATAL_POINTS: dict[str, frozenset[str]] = {
    "work": frozenset(
        {
            "sun",
            "mars",
            "saturn",
            "mc",
            "midheaven",
            "house_cusp_6",
            "house_cusp_10",
            "vi",
            "x",
        }
    ),
    "money": frozenset(
        {
            "venus",
            "jupiter",
            "pluto",
            "house_cusp_2",
            "house_cusp_8",
            "ii",
            "viii",
        }
    ),
    "relationships": frozenset(
        {
            "venus",
            "moon",
            "descendant",
            "dsc",
            "house_cusp_5",
            "house_cusp_7",
            "v",
            "vii",
        }
    ),
    "energy": frozenset(
        {
            "sun",
            "mars",
            "moon",
            "asc",
            "ascendant",
            "house_cusp_1",
            "house_cusp_6",
            "i",
            "vi",
        }
    ),
}

SLOW_PLANETS = frozenset({"saturn", "uranus", "neptune", "pluto"})

ASPECT_MAX_ORB: dict[str, float] = {
    "conjunction": 6.0,
    "trine": 6.0,
    "square": 6.0,
    "quincunx": 6.0,
    "sextile": 3.0,
    "opposition": 8.0,
}

DOMAIN_LABEL_RU = {
    "work": "Работа",
    "money": "Деньги",
    "relationships": "Отношения",
    "energy": "Энергия",
}

DOMAIN_QUIET_WHY_RU = {
    "work": "Поле ровное — без лишнего давления",
    "money": "Тише обычного — без резких ходов",
    "relationships": "Мягкий фон — без острых углов",
    "energy": "Ровный ритм — без всплесков",
}

VERDICT_LABEL_RU = {
    "calm": "спокойно",
    "charged": "заряжено",
    "friction": "трение",
    "open": "открыто",
}

_PLANET_RU = {
    "sun": "Солнце",
    "moon": "Луна",
    "mercury": "Меркурий",
    "venus": "Венера",
    "mars": "Марс",
    "jupiter": "Юпитер",
    "saturn": "Сатурн",
    "uranus": "Уран",
    "neptune": "Нептун",
    "pluto": "Плутон",
    "ascendant": "ASC",
    "asc": "ASC",
    "mc": "MC",
    "midheaven": "MC",
    "descendant": "DSC",
    "dsc": "DSC",
}

_ASPECT_RU = {
    "conjunction": "соединение",
    "sextile": "секстиль",
    "square": "квадрат",
    "trine": "трин",
    "quincunx": "квинконс",
    "opposition": "оппозиция",
}


def _norm(name: str | None) -> str:
    return (name or "").strip().lower().replace(" ", "_")


def _speed_factor(transiting_planet: str) -> float:
    return 0.3 if _norm(transiting_planet) in SLOW_PLANETS else 1.0


def valence_domain(
    domain: str,
    aspect: str,
    transiting_planet: str,
    natal_point: str,
) -> float:
    """Per-domain signed valence (contract §3). Draft tables; top_driver uses sign+magnitude."""
    asp = _norm(aspect)
    transit = _norm(transiting_planet)
    natal = _norm(natal_point)

    # Soft aspects
    if asp in ("trine", "sextile"):
        return 1.0
    if asp == "quincunx":
        return -0.5

    if domain == "work":
        if asp == "square" and natal == "mars":
            return 0.85  # pressure to act → charged
        if asp == "opposition" and natal in ("sun", "mc", "midheaven"):
            return -0.55  # career axis stretch → friction, not ban
        if asp in ("square", "opposition") and natal in ("saturn",):
            return -0.7
        if asp == "conjunction":
            if transit in ("venus", "jupiter"):
                return 0.8
            if transit in ("saturn", "mars", "pluto"):
                return -0.55 if transit == "saturn" else 0.75  # mars conj → charged drive
            return 0.0
        if asp in ("square", "opposition"):
            return -0.65
        return 0.0

    if domain == "money":
        if asp in ("trine", "sextile"):
            return 1.0
        if asp == "conjunction":
            if transit in ("venus", "jupiter"):
                return 1.0
            if transit in ("saturn", "pluto", "mars"):
                return -0.7
            return 0.0
        if asp in ("square", "opposition"):
            return -0.75
        return 0.0

    if domain == "relationships":
        if asp == "square" and natal == "venus":
            return -0.8
        if asp == "square" and natal == "moon":
            return -0.7
        if asp == "conjunction":
            if transit in ("venus", "jupiter"):
                return 1.0
            if transit in ("saturn", "mars", "pluto"):
                return -0.75
            return 0.0
        if asp in ("square", "opposition"):
            return -0.7
        return 0.0

    # energy
    if asp == "square" and natal == "mars":
        return 0.9
    if asp == "conjunction":
        if transit in ("venus", "jupiter"):
            return 0.8
        if transit in ("mars",):
            return 0.85
        if transit in ("saturn", "pluto"):
            return -0.65
        return 0.0
    if asp in ("square", "opposition"):
        return -0.6
    return 0.0


def activation_weight(
    *,
    domain: str,
    aspect: str,
    transiting_planet: str,
    natal_point: str,
    orb_deg: float,
) -> float:
    asp = _norm(aspect)
    max_orb = ASPECT_MAX_ORB.get(asp, 6.0)
    orb = max(0.0, float(orb_deg))
    proximity = max(0.0, 1.0 - (orb / max_orb)) if max_orb > 0 else 0.0
    return valence_domain(domain, aspect, transiting_planet, natal_point) * proximity * _speed_factor(
        transiting_planet
    )


def map_weight_to_verdict(weight: float, *, aspect: str | None = None) -> str:
    """Signed top weight → descriptive dictionary (contract §3.3)."""
    w = float(weight)
    mag = abs(w)
    if mag < 0.18:
        return "calm"
    # Soft support always reads as open when it wins the domain.
    if w > 0 and _norm(aspect) in ("trine", "sextile"):
        return "open"
    # Strong soft-ish support without soft aspect id (rare) → open.
    if w >= 0.85:
        return "open"
    if w > 0:
        return "charged"
    return "friction"


def why_short_for(
    transiting_planet: str,
    aspect: str,
    natal_point: str,
    domain: str | None = None,
) -> str:
    """Experiential why — no planet/aspect jargon (contract §3.3)."""
    from todayflow_backend.services.today_activation_copy_v1 import aspect_class_why_short

    _ = (transiting_planet, natal_point)  # signature kept for call sites
    return aspect_class_why_short(aspect, domain)


def natal_point_in_domain(natal_point: str, domain: str) -> bool:
    return _norm(natal_point) in DOMAIN_NATAL_POINTS.get(domain, frozenset())


def compute_domain_verdicts(
    activations: Iterable[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    activations items:
      id, transiting_planet, aspect, natal_point, orb_deg
    Returns domain_verdicts[4] in fixed order.
    """
    rows = list(activations)
    out: list[dict[str, Any]] = []
    for domain in DOMAINS:
        candidates: list[tuple[float, dict[str, Any]]] = []
        for act in rows:
            natal = str(act.get("natal_point") or "")
            if not natal_point_in_domain(natal, domain):
                continue
            w = activation_weight(
                domain=domain,
                aspect=str(act.get("aspect") or ""),
                transiting_planet=str(act.get("transiting_planet") or ""),
                natal_point=natal,
                orb_deg=float(act.get("orb_deg") or 0.0),
            )
            candidates.append((w, act))
        if not candidates:
            out.append(
                {
                    "domain": domain,
                    "verdict": "calm",
                    "why_short": DOMAIN_QUIET_WHY_RU.get(domain, "День без явного сдвига"),
                    "driver_ids": [],
                    "logic_source": "top_driver_v1",
                    "top_weight": 0.0,
                }
            )
            continue
        top_w, top_act = max(candidates, key=lambda pair: abs(pair[0]))
        driver_id = str(top_act.get("id") or "")
        out.append(
            {
                "domain": domain,
                "verdict": map_weight_to_verdict(
                    top_w, aspect=str(top_act.get("aspect") or "")
                ),
                "why_short": why_short_for(
                    str(top_act.get("transiting_planet") or ""),
                    str(top_act.get("aspect") or ""),
                    str(top_act.get("natal_point") or ""),
                    domain,
                ),
                "driver_ids": [driver_id] if driver_id else [],
                "logic_source": "top_driver_v1",
                "top_weight": round(top_w, 4),
            }
        )
    return out


def activations_from_transit_objects(transits: Iterable[Any]) -> list[dict[str, Any]]:
    """Deprecated alias — prefer today_natal_activations_v1.compute_natal_activations."""
    from todayflow_backend.services.today_natal_activations_v1 import compute_natal_activations

    rows = compute_natal_activations(transits)
    # Drop Wave2-only fields for callers that only need verdict geometry.
    return [
        {
            "id": r["id"],
            "transiting_planet": r["transiting_planet"],
            "aspect": r["aspect"],
            "natal_point": r["natal_point"],
            "orb_deg": r["orb_deg"],
        }
        for r in rows
    ]

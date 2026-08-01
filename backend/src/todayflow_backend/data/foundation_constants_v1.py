"""Foundation constants v1 — atomic lookup (astro + numerology).

Canon: docs/foundation_v1.md §2
Data: DATA/foundation_v1/

Locks:
  L1 — ruler (modern) + ruler_classical
  L2 — natural_houses list + natural_house_primary
  L3 — outer dignities calibrated=false (exaltation/detriment/fall not for formulas)
"""

from __future__ import annotations

import json
import logging
import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal

logger = logging.getLogger(__name__)

CONTRACT_VERSION = "foundation_constants_v1"
DEFAULT_DATA_ROOT = Path(__file__).resolve().parents[4] / "DATA"
ROOT = Path(os.getenv("TODAYFLOW_DATA_DIR", DEFAULT_DATA_ROOT)) / "foundation_v1"

RulerMode = Literal["modern", "classical"]


def _load_json(name: str) -> dict[str, Any]:
    path = ROOT / name
    if not path.is_file():
        logger.warning("foundation_constants_v1 missing %s", path)
        return {}
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    return data if isinstance(data, dict) else {}


@lru_cache(maxsize=1)
def meta() -> dict[str, Any]:
    return _load_json("meta.json")


@lru_cache(maxsize=1)
def signs_by_id() -> dict[str, dict[str, Any]]:
    rows = _load_json("signs.json").get("signs") or []
    return {str(r["id"]): r for r in rows if isinstance(r, dict) and r.get("id")}


@lru_cache(maxsize=1)
def planets_by_id() -> dict[str, dict[str, Any]]:
    rows = _load_json("planets.json").get("planets") or []
    return {str(r["id"]): r for r in rows if isinstance(r, dict) and r.get("id")}


@lru_cache(maxsize=1)
def houses_by_id() -> dict[int, dict[str, Any]]:
    rows = _load_json("houses.json").get("houses") or []
    out: dict[int, dict[str, Any]] = {}
    for r in rows:
        if isinstance(r, dict) and r.get("id") is not None:
            out[int(r["id"])] = r
    return out


@lru_cache(maxsize=1)
def aspects_by_id() -> dict[str, dict[str, Any]]:
    rows = _load_json("aspects.json").get("aspects") or []
    return {str(r["id"]): r for r in rows if isinstance(r, dict) and r.get("id")}


@lru_cache(maxsize=1)
def dignities_by_planet() -> dict[str, dict[str, Any]]:
    payload = _load_json("dignities.json")
    out: dict[str, dict[str, Any]] = {}
    for r in list(payload.get("calibrated") or []) + list(payload.get("reference_only") or []):
        if isinstance(r, dict) and r.get("planet"):
            out[str(r["planet"])] = r
    return out


@lru_cache(maxsize=1)
def moon_phases_by_id() -> dict[str, dict[str, Any]]:
    rows = _load_json("moon_phases.json").get("phases") or []
    return {str(r["id"]): r for r in rows if isinstance(r, dict) and r.get("id")}


@lru_cache(maxsize=1)
def numbers_by_value() -> dict[int, dict[str, Any]]:
    rows = _load_json("numerology.json").get("numbers") or []
    out: dict[int, dict[str, Any]] = {}
    for r in rows:
        if isinstance(r, dict) and r.get("value") is not None:
            out[int(r["value"])] = r
    return out


def sign_ruler(sign_id: str, *, mode: RulerMode = "modern") -> str | None:
    """L1: modern by default; classical for house_rulers / profections."""
    row = signs_by_id().get(str(sign_id).lower())
    if not row:
        return None
    if mode == "classical":
        return str(row.get("ruler_classical") or row.get("ruler") or "") or None
    return str(row.get("ruler") or "") or None


def aspect_character(aspect_id: str) -> str | None:
    row = aspects_by_id().get(str(aspect_id).lower())
    if not row:
        return None
    return str(row.get("character") or "") or None


def calibrated_dignity(planet_id: str) -> dict[str, Any] | None:
    """L3: only calibrated rows (Sun…Saturn). Outers return None for formula use."""
    row = dignities_by_planet().get(str(planet_id).lower())
    if not row or not row.get("calibrated"):
        return None
    return row


def retrograde_general_ru() -> str:
    return str(meta().get("retrograde_general_ru") or "")


def validate_foundation_constants_v1() -> list[str]:
    errors: list[str] = []
    if meta().get("contract_version") != CONTRACT_VERSION:
        errors.append("meta.contract_version mismatch")
    if len(signs_by_id()) != 12:
        errors.append(f"signs count={len(signs_by_id())} expected 12")
    if "quincunx" in aspects_by_id():
        errors.append("quincunx must stay out of aspects pack")
    for sid, row in signs_by_id().items():
        if not row.get("ruler") or not row.get("ruler_classical"):
            errors.append(f"sign {sid} missing ruler fields")
        if " " in str(row.get("ruler") or "") or "(" in str(row.get("ruler") or ""):
            errors.append(f"sign {sid} ruler not atomic: {row.get('ruler')}")
    for pid, row in planets_by_id().items():
        houses = row.get("natural_houses")
        if not isinstance(houses, list):
            errors.append(f"planet {pid} natural_houses must be list")
        dual = {"mercury", "venus", "mars", "jupiter", "saturn"}
        if pid in dual and len(houses or []) != 2:
            errors.append(f"planet {pid} expected 2 natural_houses, got {houses}")
    for pid in ("uranus", "neptune", "pluto"):
        d = dignities_by_planet().get(pid)
        if d and d.get("calibrated"):
            errors.append(f"outer {pid} must be calibrated=false")
    if not numbers_by_value().get(7):
        errors.append("numerology missing 7")
    return errors

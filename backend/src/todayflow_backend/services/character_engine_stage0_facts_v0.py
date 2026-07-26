"""Character Engine Stage 0 — deterministic facts pack (no personality prose).

Canon: CHARACTER_ENGINE_SCHEMA_CONTRACTS_V0 · Architecture Impact D2/D3.
Assembler over existing calculators — not a new astrology engine.

ID semantics (v1): fact_id fingerprints authority+calc_version. Same meaning under a
new calculator version → new fact_id. For cross-version sense, use fact_type+normalized_key
(fact_key), which is not the public fact_id. Authority competition uses slot_key=fact_type
so Swiss displaces bridge for the same body even when signs disagree.
"""

from __future__ import annotations

import hashlib
import json
from datetime import date, datetime, timezone
from typing import Any

from todayflow_backend.services.character_engine_ids_v0 import make_fact_id
from todayflow_backend.services.natal_facts_contract_v1 import sun_sign_from_date

STAGE0_VERSION = "character_engine_stage0_facts_v0"
SWISS_CALC_VERSION = "swiss_ephe_v1"
NUM_CALC_VERSION = "num_v1"
CATALOG_CALC_VERSION = "catalog_v0"
DATE_SUN_CALC_VERSION = "sun_from_date_v1"
BRIDGE_CALC_VERSION = "natal_facts_bridge_v1"

_AUTHORITY_RANK = {
    "swiss": 40,
    "deterministic_numerology": 30,
    "catalog": 20,
    "bridge_natal_facts_llm": 10,
}

_WATER = frozenset({"cancer", "scorpio", "pisces"})
_FIRE = frozenset({"aries", "leo", "sagittarius"})
_EARTH = frozenset({"taurus", "virgo", "capricorn"})
_AIR = frozenset({"gemini", "libra", "aquarius"})


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _norm_sign(value: Any) -> str | None:
    if value is None:
        return None
    s = str(value).strip().lower()
    return s or None


def _norm_body(value: Any) -> str | None:
    if value is None:
        return None
    s = str(value).strip().lower().replace(" ", "_")
    aliases = {"sun": "sun", "moon": "moon", "asc": "ascendant", "ascendant": "ascendant", "rising": "ascendant"}
    return aliases.get(s, s) or None


def fact_key(*, fact_type: str, normalized_key: str) -> str:
    """Semantic key for a specific value (stable across calculator versions; not fact_id)."""
    return f"{fact_type.strip().lower()}|{normalized_key.strip().lower()}"


def slot_key(*, fact_type: str) -> str:
    """Authority-competition slot: one winner per fact_type (Swiss beats bridge even if signs differ)."""
    return fact_type.strip().lower()


def _full_natal_capable(capability: dict[str, Any] | None) -> bool:
    if not isinstance(capability, dict):
        return False
    mode = str(capability.get("natal_mode") or "").strip().lower()
    if mode == "full":
        return True
    return bool(capability.get("has_birth_time")) and bool(capability.get("has_birth_place"))


def _parse_birth_date(value: Any) -> date | None:
    if isinstance(value, date):
        return value
    if not value:
        return None
    try:
        return date.fromisoformat(str(value)[:10])
    except ValueError:
        return None


def _candidate(
    *,
    fact_type: str,
    normalized_key: str,
    value: Any,
    authority: str,
    calc_version: str,
    capability_required: str,
    confidence: str,
    source_system: str,
    input_fingerprint: str,
    display_key: str | None = None,
    computed_at: str,
) -> dict[str, Any]:
    fid = make_fact_id(
        fact_type=fact_type,
        normalized_key=normalized_key,
        authority=authority,
        calc_version=calc_version,
    )
    row: dict[str, Any] = {
        "fact_id": fid,
        "fact_type": fact_type,
        "fact_key": fact_key(fact_type=fact_type, normalized_key=normalized_key),
        "slot_key": slot_key(fact_type=fact_type),
        "normalized_key": normalized_key,
        "value": value,
        "authority": authority,
        "calc_version": calc_version,
        "capability_required": capability_required,
        "confidence": confidence,
        "provenance": {
            "source_system": source_system,
            "input_fingerprint": input_fingerprint,
            "computed_at": computed_at,
        },
    }
    if display_key:
        row["display_key"] = display_key
    return row


def _merge_candidates(candidates: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Dedupe by slot_key (fact_type); higher authority wins. Swiss never loses to bridge."""
    best: dict[str, dict[str, Any]] = {}
    diagnostics: list[dict[str, Any]] = []
    for row in candidates:
        key = str(row["slot_key"])
        prev = best.get(key)
        if prev is None:
            best[key] = row
            continue
        prev_rank = _AUTHORITY_RANK.get(str(prev["authority"]), 0)
        new_rank = _AUTHORITY_RANK.get(str(row["authority"]), 0)
        if new_rank > prev_rank:
            diagnostics.append(
                {
                    "code": "fact_superseded",
                    "slot_key": key,
                    "fact_key": row["fact_key"],
                    "kept_authority": row["authority"],
                    "dropped_authority": prev["authority"],
                    "dropped_fact_key": prev["fact_key"],
                }
            )
            best[key] = row
        else:
            diagnostics.append(
                {
                    "code": "fact_duplicate_dropped",
                    "slot_key": key,
                    "fact_key": prev["fact_key"],
                    "kept_authority": prev["authority"],
                    "dropped_authority": row["authority"],
                    "dropped_fact_key": row["fact_key"],
                }
            )
    # Stable order by slot_key for output independence from input order.
    ordered = [best[k] for k in sorted(best.keys())]
    return ordered, diagnostics


def _from_swiss_positions(
    positions: list[Any],
    *,
    input_fingerprint: str,
    computed_at: str,
    allow_angles: bool,
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for item in positions or []:
        if not isinstance(item, dict):
            continue
        # Live caches vary: Swiss uses `body`; natal_facts-shaped rows use `name`.
        body = _norm_body(
            item.get("body") or item.get("id") or item.get("planet") or item.get("name")
        )
        sign = _norm_sign(item.get("sign"))
        if not body or not sign:
            continue
        if body in {"ascendant", "mc", "ic", "descendant"} and not allow_angles:
            continue
        fact_type = f"planet_sign:{body}" if body not in {"ascendant", "mc", "ic", "descendant"} else f"angle_sign:{body}"
        out.append(
            _candidate(
                fact_type=fact_type,
                normalized_key=sign,
                value={"body": body, "sign": sign, **({k: item[k] for k in ("degree", "house") if k in item})},
                authority="swiss",
                calc_version=SWISS_CALC_VERSION,
                capability_required="full_natal" if body in {"ascendant", "mc", "ic", "descendant"} else "date_only",
                confidence="high",
                source_system="swiss",
                input_fingerprint=input_fingerprint,
                display_key=body,
                computed_at=computed_at,
            )
        )
    return out


def _normalize_swiss_positions(positions: Any) -> list[Any]:
    """Accept list rows or dict keyed by body name (legacy ChartResponse shape)."""
    if isinstance(positions, list):
        return positions
    if isinstance(positions, dict):
        out: list[Any] = []
        for key, value in positions.items():
            if not isinstance(value, dict):
                continue
            row = dict(value)
            if not (row.get("body") or row.get("name") or row.get("id") or row.get("planet")):
                row["name"] = key
            out.append(row)
        return out
    return []


def _normalize_swiss_houses(houses: Any) -> tuple[list[Any], list[Any]]:
    """Return (house_cusp_rows, angle_rows_from_houses_dict).

    Live caches use either list[{house,sign}] or dict with keys house_N / N / Asc / MC.
    """
    if isinstance(houses, list):
        return houses, []
    if not isinstance(houses, dict):
        return [], []

    cusp_rows: list[Any] = []
    angle_rows: list[Any] = []
    angle_alias = {
        "asc": "ascendant",
        "ascendant": "ascendant",
        "mc": "mc",
        "ic": "ic",
        "dsc": "descendant",
        "descendant": "descendant",
    }
    for key, value in houses.items():
        if not isinstance(value, dict):
            continue
        raw_key = str(key).strip().lower()
        if raw_key in angle_alias:
            sign = _norm_sign(value.get("sign"))
            if sign:
                angle_rows.append(
                    {
                        "body": angle_alias[raw_key],
                        "sign": sign,
                        **({k: value[k] for k in ("degree", "longitude", "absolute_longitude") if k in value}),
                    }
                )
            continue
        house_num: int | None = None
        if raw_key.startswith("house_"):
            try:
                house_num = int(raw_key.split("_", 1)[1])
            except ValueError:
                house_num = None
        else:
            try:
                house_num = int(raw_key)
            except ValueError:
                house_num = None
        if house_num is None:
            continue
        cusp_rows.append(
            {
                "house": house_num,
                "sign": value.get("sign"),
                **({k: value[k] for k in ("degree", "longitude") if k in value}),
            }
        )
    return cusp_rows, angle_rows


def _from_swiss_houses(
    houses: list[Any],
    *,
    input_fingerprint: str,
    computed_at: str,
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for item in houses or []:
        if not isinstance(item, dict):
            continue
        try:
            house = int(item.get("house") or item.get("number"))
        except (TypeError, ValueError):
            continue
        if not (1 <= house <= 12):
            continue
        sign = _norm_sign(item.get("sign"))
        if not sign:
            continue
        out.append(
            _candidate(
                fact_type=f"house_cusp_sign:{house}",
                normalized_key=sign,
                value={"house": house, "sign": sign},
                authority="swiss",
                calc_version=SWISS_CALC_VERSION,
                capability_required="full_natal",
                confidence="high",
                source_system="swiss",
                input_fingerprint=input_fingerprint,
                display_key=f"house_{house}",
                computed_at=computed_at,
            )
        )
    return out


def _from_bridge_natal_facts(
    natal_facts: dict[str, Any],
    *,
    input_fingerprint: str,
    computed_at: str,
    allow_angles: bool,
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for item in natal_facts.get("planets") or []:
        if not isinstance(item, dict):
            continue
        body = _norm_body(item.get("id") or item.get("body"))
        sign = _norm_sign(item.get("sign"))
        if not body or not sign:
            continue
        out.append(
            _candidate(
                fact_type=f"planet_sign:{body}",
                normalized_key=sign,
                value={"body": body, "sign": sign},
                authority="bridge_natal_facts_llm",
                calc_version=BRIDGE_CALC_VERSION,
                capability_required="date_only",
                confidence="medium",
                source_system="natal_facts_bridge",
                input_fingerprint=input_fingerprint,
                display_key=body,
                computed_at=computed_at,
            )
        )
    if allow_angles:
        angles = natal_facts.get("angles") if isinstance(natal_facts.get("angles"), dict) else {}
        for angle_key in ("ascendant", "mc", "ic", "descendant"):
            raw = angles.get(angle_key)
            sign = _norm_sign(raw.get("sign") if isinstance(raw, dict) else raw)
            if not sign:
                continue
            out.append(
                _candidate(
                    fact_type=f"angle_sign:{angle_key}",
                    normalized_key=sign,
                    value={"body": angle_key, "sign": sign},
                    authority="bridge_natal_facts_llm",
                    calc_version=BRIDGE_CALC_VERSION,
                    capability_required="full_natal",
                    confidence="medium",
                    source_system="natal_facts_bridge",
                    input_fingerprint=input_fingerprint,
                    display_key=angle_key,
                    computed_at=computed_at,
                )
            )
        for item in natal_facts.get("houses") or []:
            if not isinstance(item, dict):
                continue
            try:
                house = int(item.get("house"))
            except (TypeError, ValueError):
                continue
            sign = _norm_sign(item.get("sign"))
            if not sign or not (1 <= house <= 12):
                continue
            out.append(
                _candidate(
                    fact_type=f"house_cusp_sign:{house}",
                    normalized_key=sign,
                    value={"house": house, "sign": sign},
                    authority="bridge_natal_facts_llm",
                    calc_version=BRIDGE_CALC_VERSION,
                    capability_required="full_natal",
                    confidence="medium",
                    source_system="natal_facts_bridge",
                    input_fingerprint=input_fingerprint,
                    display_key=f"house_{house}",
                    computed_at=computed_at,
                )
            )
    return out


def _from_numerology(
    numerology: dict[str, Any],
    *,
    input_fingerprint: str,
    computed_at: str,
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    mapping = {
        "life_path": "life_path_number",
        "expression": "expression_number",
        "soul_urge": "soul_urge_number",
        "personality": "personality_number",
    }
    for src, fact_type in mapping.items():
        raw = numerology.get(src)
        if raw is None:
            continue
        try:
            number = int(raw)
        except (TypeError, ValueError):
            continue
        out.append(
            _candidate(
                fact_type=fact_type,
                normalized_key=str(number),
                value=number,
                authority="deterministic_numerology",
                calc_version=NUM_CALC_VERSION,
                capability_required="date_only" if src == "life_path" else "name",
                confidence="high",
                source_system="numerology",
                input_fingerprint=input_fingerprint,
                display_key=src,
                computed_at=computed_at,
            )
        )
    return out


def _from_catalog(
    catalog_facts: dict[str, Any],
    *,
    input_fingerprint: str,
    computed_at: str,
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for key, value in sorted((catalog_facts or {}).items(), key=lambda kv: str(kv[0])):
        if value is None or value == "":
            continue
        norm = str(value).strip().lower()
        if not norm:
            continue
        out.append(
            _candidate(
                fact_type=f"catalog:{key}",
                normalized_key=norm,
                value=value,
                authority="catalog",
                calc_version=CATALOG_CALC_VERSION,
                capability_required="date_only",
                confidence="medium",
                source_system="catalog",
                input_fingerprint=input_fingerprint,
                display_key=str(key),
                computed_at=computed_at,
            )
        )
    return out


def build_character_engine_facts_pack_v0(
    *,
    profile_fingerprint: str,
    swiss_chart: dict[str, Any] | None = None,
    numerology: dict[str, Any] | None = None,
    catalog_facts: dict[str, Any] | None = None,
    natal_facts_bridge: dict[str, Any] | None = None,
    capability: dict[str, Any] | None = None,
    birth_date: Any = None,
    input_fingerprint: str | None = None,
) -> dict[str, Any]:
    """Assemble RawFact list. No LLM. No personality claims."""
    computed_at = _now_iso()
    cap = dict(capability or {})
    allow_angles = _full_natal_capable(cap)
    fp = (input_fingerprint or profile_fingerprint or "unknown").strip() or "unknown"

    missing_inputs: list[dict[str, str]] = []
    if not birth_date and not (swiss_chart or natal_facts_bridge or numerology):
        missing_inputs.append({"key": "birth_date", "reason": "no_sources"})

    candidates: list[dict[str, Any]] = []

    # Deterministic sun from date (catalog-rank; Swiss sun supersedes when present).
    bd = _parse_birth_date(birth_date)
    if bd is not None:
        sun = sun_sign_from_date(bd)
        candidates.append(
            _candidate(
                fact_type="planet_sign:sun",
                normalized_key=sun,
                value={"body": "sun", "sign": sun},
                authority="catalog",
                calc_version=DATE_SUN_CALC_VERSION,
                capability_required="date_only",
                confidence="high",
                source_system="sun_from_date",
                input_fingerprint=fp,
                display_key="sun",
                computed_at=computed_at,
            )
        )
    if isinstance(swiss_chart, dict):
        positions = _normalize_swiss_positions(swiss_chart.get("positions"))
        houses, house_angles = _normalize_swiss_houses(swiss_chart.get("houses"))
        if house_angles and allow_angles:
            # Asc/MC sometimes live only under houses dict (natal_facts-shaped cache).
            positions = list(positions) + list(house_angles)
        candidates.extend(
            _from_swiss_positions(
                positions,
                input_fingerprint=fp,
                computed_at=computed_at,
                allow_angles=allow_angles,
            )
        )
        if allow_angles:
            candidates.extend(
                _from_swiss_houses(houses, input_fingerprint=fp, computed_at=computed_at)
            )
        elif houses or house_angles:
            missing_inputs.append({"key": "houses", "reason": "capability_not_full_natal"})

    if isinstance(numerology, dict):
        candidates.extend(_from_numerology(numerology, input_fingerprint=fp, computed_at=computed_at))

    if isinstance(catalog_facts, dict):
        candidates.extend(_from_catalog(catalog_facts, input_fingerprint=fp, computed_at=computed_at))

    if isinstance(natal_facts_bridge, dict):
        candidates.extend(
            _from_bridge_natal_facts(
                natal_facts_bridge,
                input_fingerprint=fp,
                computed_at=computed_at,
                allow_angles=allow_angles,
            )
        )

    if not allow_angles:
        for key in ("ascendant", "houses", "mc"):
            if not any(m["key"] == key for m in missing_inputs):
                missing_inputs.append({"key": key, "reason": "capability_not_full_natal"})

    raw_facts, dedupe_diag = _merge_candidates(candidates)

    # Strip internal helper fields not in public RawFact schema (fact_key/normalized_key kept in diagnostics only).
    public_facts: list[dict[str, Any]] = []
    for row in raw_facts:
        public = {
            "fact_id": row["fact_id"],
            "fact_type": row["fact_type"],
            "value": row["value"],
            "authority": row["authority"],
            "calc_version": row["calc_version"],
            "capability_required": row["capability_required"],
            "confidence": row["confidence"],
            "provenance": row["provenance"],
        }
        if row.get("display_key"):
            public["display_key"] = row["display_key"]
        public_facts.append(public)

    pack_fingerprint = hashlib.sha256(
        json.dumps(
            [{"fact_id": f["fact_id"], "fact_type": f["fact_type"]} for f in public_facts],
            sort_keys=True,
            ensure_ascii=False,
        ).encode("utf-8")
    ).hexdigest()[:24]

    natal_mode = "full" if allow_angles else ("date_only" if bd or public_facts else "none")
    out_capability = {
        "natal_mode": natal_mode,
        "has_name": bool(cap.get("has_name")),
        "has_birth_time": bool(cap.get("has_birth_time")),
        "has_birth_place": bool(cap.get("has_birth_place")),
    }

    return {
        "stage": 0,
        "stage_version": STAGE0_VERSION,
        "profile_fingerprint": profile_fingerprint,
        "input_fact_set_version": f"facts_{pack_fingerprint}",
        "calc_authority": {
            "swiss": SWISS_CALC_VERSION,
            "numerology": NUM_CALC_VERSION,
            "catalogs": CATALOG_CALC_VERSION,
        },
        "capability": out_capability,
        "raw_facts": public_facts,
        "missing_inputs": sorted(missing_inputs, key=lambda m: m["key"]),
        "diagnostics": {
            "dedupe": dedupe_diag,
            "fact_keys": [row["fact_key"] for row in raw_facts],
            "id_semantics": "fact_id_includes_calc_version_v1",
        },
        "generated_at": computed_at,
    }


def element_for_sign(sign: str | None) -> str | None:
    s = _norm_sign(sign)
    if not s:
        return None
    if s in _FIRE:
        return "fire"
    if s in _EARTH:
        return "earth"
    if s in _AIR:
        return "air"
    if s in _WATER:
        return "water"
    return None

#!/usr/bin/env python3
"""Validate fixtures and DATA/reference machine records against reference_machine_contract_v1."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator, ValidationError

REPO = Path(__file__).resolve().parents[1]
SCHEMA_PATH = REPO / "docs/schemas/reference_machine_contract_v1.schema.json"
FIXTURES_DIR = REPO / "docs/schemas/fixtures"
TAROT_MAJOR_MACHINE_DIR = REPO / "DATA/reference/tarot/machine"
NUMEROLOGY_MACHINE_DIR = REPO / "DATA/reference/numerology/machine"
ASTROLOGY_MACHINE_DIR = REPO / "DATA/reference/astrology/machine"

VALID_FIXTURES = [
    FIXTURES_DIR / "reference_machine_contract_v1.tarot.valid.json",
    FIXTURES_DIR / "reference_machine_contract_v1.numerology.valid.json",
]

INVALID_FIXTURES = [
    FIXTURES_DIR / "reference_machine_contract_v1.invalid_mixed_content.json",
    FIXTURES_DIR / "reference_machine_contract_v1.invalid_vector_range.json",
    FIXTURES_DIR / "reference_machine_contract_v1.invalid_missing_confidence.json",
    FIXTURES_DIR / "reference_machine_contract_v1.invalid_tempo_enum.json",
    FIXTURES_DIR / "reference_machine_contract_v1.invalid_extra_machine_field.json",
]

EXPECTED_TAROT_MAJOR_COUNT = 22
EXPECTED_NUMEROLOGY_CORE_COUNT = 9
EXPECTED_NUMEROLOGY_MASTER_COUNT = 3
EXPECTED_NUMEROLOGY_PERSONAL_CYCLE_COUNT = 9
EXPECTED_NUMEROLOGY_MACHINE_COUNT = (
    EXPECTED_NUMEROLOGY_CORE_COUNT
    + EXPECTED_NUMEROLOGY_MASTER_COUNT
    + 3 * EXPECTED_NUMEROLOGY_PERSONAL_CYCLE_COUNT
)
EXPECTED_ASTROLOGY_SIGN_COUNT = 12
EXPECTED_ASTROLOGY_PLANET_COUNT = 10
EXPECTED_ASTROLOGY_HOUSE_COUNT = 12
EXPECTED_ASTROLOGY_ASPECT_COUNT = 5
EXPECTED_ASTROLOGY_MACHINE_COUNT = (
    EXPECTED_ASTROLOGY_SIGN_COUNT
    + EXPECTED_ASTROLOGY_PLANET_COUNT
    + EXPECTED_ASTROLOGY_HOUSE_COUNT
    + EXPECTED_ASTROLOGY_ASPECT_COUNT
)
ASTROLOGY_ATOMIC_ENTITY_TYPES = frozenset({"ZodiacSign", "Planet", "House", "Aspect"})
FORBIDDEN_ASTROLOGY_ENTITY_CODE_PREFIXES = (
    "astrology.planet_in_sign.",
    "astrology.planet_in_house.",
    "astrology.transit.",
    "astrology.aspect_pair.",
    "astrology.foundation.",
)
MAJOR_ASPECT_IDS = ("conjunction", "sextile", "square", "trine", "opposition")
ZODIAC_SIGN_IDS = (
    "aries",
    "taurus",
    "gemini",
    "cancer",
    "leo",
    "virgo",
    "libra",
    "scorpio",
    "sagittarius",
    "capricorn",
    "aquarius",
    "pisces",
)
PLANET_IDS = (
    "sun",
    "moon",
    "mercury",
    "venus",
    "mars",
    "jupiter",
    "saturn",
    "uranus",
    "neptune",
    "pluto",
)


def _expected_astrology_entity_codes() -> set[str]:
    codes = {f"astrology.sign.{s}" for s in ZODIAC_SIGN_IDS}
    codes |= {f"astrology.planet.{p}" for p in PLANET_IDS}
    codes |= {f"astrology.house.{i:02d}" for i in range(1, EXPECTED_ASTROLOGY_HOUSE_COUNT + 1)}
    codes |= {f"astrology.aspect.{a}" for a in MAJOR_ASPECT_IDS}
    return codes


def _validate_astrology_atomic_record(payload: dict) -> str | None:
    entity_code = payload.get("entity_code", "")
    for prefix in FORBIDDEN_ASTROLOGY_ENTITY_CODE_PREFIXES:
        if str(entity_code).startswith(prefix):
            return f"forbidden composite entity_code: {entity_code!r}"
    entity_type = payload.get("entity_type")
    if entity_type not in ASTROLOGY_ATOMIC_ENTITY_TYPES:
        return f"entity_type must be atomic, got {entity_type!r}"
    return None


def _validate_paths(validator: Draft202012Validator, paths: list[Path], *, label: str) -> int:
    for path in sorted(paths):
        payload = json.loads(path.read_text(encoding="utf-8"))
        try:
            validator.validate(payload)
        except ValidationError as e:
            print(f"{label} failed ({path.relative_to(REPO)}): {e.message}", file=sys.stderr)
            return 1
    return 0


def main() -> int:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)

    if _validate_paths(validator, VALID_FIXTURES, label="Valid fixture") != 0:
        return 1

    for path in INVALID_FIXTURES:
        payload = json.loads(path.read_text(encoding="utf-8"))
        try:
            validator.validate(payload)
        except ValidationError:
            continue
        print(f"Invalid fixture unexpectedly passed ({path.name}).", file=sys.stderr)
        return 1

    tarot_paths = sorted(TAROT_MAJOR_MACHINE_DIR.glob("*.json"))
    if len(tarot_paths) != EXPECTED_TAROT_MAJOR_COUNT:
        print(
            f"Expected {EXPECTED_TAROT_MAJOR_COUNT} tarot major machine drafts in "
            f"{TAROT_MAJOR_MACHINE_DIR.relative_to(REPO)}, found {len(tarot_paths)}.",
            file=sys.stderr,
        )
        return 1

    if _validate_paths(validator, tarot_paths, label="Tarot major machine draft") != 0:
        return 1

    entity_codes = [json.loads(p.read_text(encoding="utf-8"))["entity_code"] for p in tarot_paths]
    expected_codes = {f"tarot.major.{i:02d}" for i in range(EXPECTED_TAROT_MAJOR_COUNT)}
    missing = expected_codes - set(entity_codes)
    extra = set(entity_codes) - expected_codes
    if missing or extra:
        print(f"Tarot entity_code mismatch. missing={sorted(missing)} extra={sorted(extra)}", file=sys.stderr)
        return 1

    numerology_paths = sorted(NUMEROLOGY_MACHINE_DIR.glob("*.json"))
    if len(numerology_paths) != EXPECTED_NUMEROLOGY_MACHINE_COUNT:
        print(
            f"Expected {EXPECTED_NUMEROLOGY_MACHINE_COUNT} numerology machine drafts in "
            f"{NUMEROLOGY_MACHINE_DIR.relative_to(REPO)}, found {len(numerology_paths)}.",
            file=sys.stderr,
        )
        return 1

    if _validate_paths(validator, numerology_paths, label="Numerology machine draft") != 0:
        return 1

    numerology_codes = [json.loads(p.read_text(encoding="utf-8"))["entity_code"] for p in numerology_paths]
    expected_numerology = {f"numerology.core.{i}" for i in range(1, EXPECTED_NUMEROLOGY_CORE_COUNT + 1)}
    expected_numerology |= {f"numerology.master.{n}" for n in (11, 22, 33)}
    for prefix in ("personal_day", "personal_month", "personal_year"):
        expected_numerology |= {
            f"numerology.{prefix}.{i}" for i in range(1, EXPECTED_NUMEROLOGY_PERSONAL_CYCLE_COUNT + 1)
        }
    missing_num = expected_numerology - set(numerology_codes)
    extra_num = set(numerology_codes) - expected_numerology
    if missing_num or extra_num:
        print(
            f"Numerology entity_code mismatch. missing={sorted(missing_num)} extra={sorted(extra_num)}",
            file=sys.stderr,
        )
        return 1

    astro_paths = sorted(ASTROLOGY_MACHINE_DIR.glob("*.json"))
    if len(astro_paths) != EXPECTED_ASTROLOGY_MACHINE_COUNT:
        print(
            f"Expected {EXPECTED_ASTROLOGY_MACHINE_COUNT} atomic astrology machine drafts in "
            f"{ASTROLOGY_MACHINE_DIR.relative_to(REPO)}, found {len(astro_paths)}.",
            file=sys.stderr,
        )
        return 1

    for path in astro_paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        atomic_err = _validate_astrology_atomic_record(payload)
        if atomic_err:
            print(f"Astrology atomic gate failed ({path.relative_to(REPO)}): {atomic_err}", file=sys.stderr)
            return 1
        try:
            validator.validate(payload)
        except ValidationError as e:
            print(f"Astrology machine draft failed ({path.relative_to(REPO)}): {e.message}", file=sys.stderr)
            return 1

    astro_codes = [json.loads(p.read_text(encoding="utf-8"))["entity_code"] for p in astro_paths]
    expected_astro = _expected_astrology_entity_codes()
    missing_astro = expected_astro - set(astro_codes)
    extra_astro = set(astro_codes) - expected_astro
    if missing_astro or extra_astro:
        print(
            f"Astrology entity_code mismatch. missing={sorted(missing_astro)} extra={sorted(extra_astro)}",
            file=sys.stderr,
        )
        return 1

    print(
        "reference_machine_contract_v1 schema: OK "
        f"({len(VALID_FIXTURES)} fixtures, {len(INVALID_FIXTURES)} rejected, "
        f"{len(tarot_paths)} tarot major drafts, {len(numerology_paths)} numerology drafts, "
        f"{len(astro_paths)} astrology atomic drafts)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

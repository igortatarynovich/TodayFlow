#!/usr/bin/env python3
"""Validate Character Engine fixtures against docs/schemas/character_engine_v1.schema.json."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator, ValidationError

REPO = Path(__file__).resolve().parents[1]
SCHEMA_PATH = REPO / "docs/schemas/character_engine_v1.schema.json"
VALID_PATH = REPO / "docs/schemas/fixtures/character_engine_v1.valid.json"
FORMING_PATH = REPO / "docs/schemas/fixtures/character_engine_v1.forming.valid.json"
INVALID_PATH = REPO / "docs/schemas/fixtures/character_engine_v1.invalid_ready_missing_cascade.json"


def main() -> int:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)

    for path, label in (
        (VALID_PATH, "ready valid"),
        (FORMING_PATH, "forming valid"),
    ):
        instance = json.loads(path.read_text(encoding="utf-8"))
        try:
            validator.validate(instance)
        except ValidationError as e:
            print(f"{label} fixture failed: {e.message}", file=sys.stderr)
            return 1

    invalid = json.loads(INVALID_PATH.read_text(encoding="utf-8"))
    try:
        validator.validate(invalid)
        print("Invalid ready-without-cascade unexpectedly passed.", file=sys.stderr)
        return 1
    except ValidationError:
        pass

    print("character_engine_v1 schema: OK (ready+forming pass, invalid rejected).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

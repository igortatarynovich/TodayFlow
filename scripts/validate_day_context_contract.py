#!/usr/bin/env python3
"""Validate fixtures against docs/schemas/day_context_v0.schema.json (CI + local)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator, ValidationError

REPO = Path(__file__).resolve().parents[1]
SCHEMA_PATH = REPO / "docs/schemas/day_context_v0.schema.json"
VALID_PATH = REPO / "docs/schemas/fixtures/day_context_v0.valid.json"
INVALID_PATH = REPO / "docs/schemas/fixtures/day_context_v0.invalid_missing_user_core.json"


def main() -> int:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)

    valid = json.loads(VALID_PATH.read_text(encoding="utf-8"))
    try:
        validator.validate(valid)
    except ValidationError as e:
        print(f"Valid fixture failed: {e.message}", file=sys.stderr)
        return 1

    invalid = json.loads(INVALID_PATH.read_text(encoding="utf-8"))
    bad = False
    try:
        validator.validate(invalid)
        bad = True
    except ValidationError:
        pass
    if bad:
        print("Invalid fixture unexpectedly passed schema validation.", file=sys.stderr)
        return 1

    print("day_context_v0 schema: OK (valid fixture passes, invalid rejected).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

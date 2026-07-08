#!/usr/bin/env python3
"""Validate fixtures against compact_user_model JSON schemas (CI + local)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator, ValidationError

REPO = Path(__file__).resolve().parents[1]
SCHEMAS = REPO / "docs/schemas"
FIXTURES = SCHEMAS / "fixtures"


def _validate_pair(
    *,
    schema_name: str,
    valid_name: str,
    invalid_name: str,
    label: str,
) -> int:
    schema_path = SCHEMAS / schema_name
    valid_path = FIXTURES / valid_name
    invalid_path = FIXTURES / invalid_name

    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)

    valid = json.loads(valid_path.read_text(encoding="utf-8"))
    try:
        validator.validate(valid)
    except ValidationError as e:
        print(f"{label}: valid fixture failed: {e.message}", file=sys.stderr)
        return 1

    invalid = json.loads(invalid_path.read_text(encoding="utf-8"))
    rejected = False
    try:
        validator.validate(invalid)
        rejected = True
    except ValidationError:
        pass
    if rejected:
        print(f"{label}: invalid fixture unexpectedly passed.", file=sys.stderr)
        return 1

    print(f"{label}: OK (valid passes, invalid rejected).")
    return 0


def main() -> int:
    exit_code = 0
    pairs = [
        (
            "compact_user_model_v0.schema.json",
            "compact_user_model_v0.valid.json",
            "compact_user_model_v0.invalid_missing_identity.json",
            "compact_user_model_v0",
        ),
        (
            "compact_user_model_v1.schema.json",
            "compact_user_model_v1.valid.json",
            "compact_user_model_v1.invalid_missing_recommendations.json",
            "compact_user_model_v1",
        ),
    ]
    for schema_name, valid_name, invalid_name, label in pairs:
        exit_code = max(
            exit_code,
            _validate_pair(
                schema_name=schema_name,
                valid_name=valid_name,
                invalid_name=invalid_name,
                label=label,
            ),
        )
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())

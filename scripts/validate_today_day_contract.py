#!/usr/bin/env python3
"""Validate fixtures against docs/schemas/today_day_v1.schema.json (CI + local)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator, ValidationError

REPO = Path(__file__).resolve().parents[1]
SCHEMA_PATH = REPO / "docs/schemas/today_day_v1.schema.json"
VALID_PATH = REPO / "docs/schemas/fixtures/today_day_v1.valid.json"
INVALID_PATH = REPO / "docs/schemas/fixtures/today_day_v1.invalid_wrong_sphere_count.json"


def _extra_feedback_unique_ids(instance: object) -> list[str]:
    errs: list[str] = []
    if not isinstance(instance, dict):
        return ["root must be an object"]
    fqs = instance.get("feedback_questions")
    if isinstance(fqs, list):
        ids = [x.get("id") for x in fqs if isinstance(x, dict)]
        if len(ids) != len(set(ids)):
            errs.append("feedback_questions: duplicate id")
    spheres = instance.get("spheres")
    if isinstance(spheres, list):
        sids = [x.get("id") for x in spheres if isinstance(x, dict)]
        if len(sids) != len(set(sids)):
            errs.append("spheres: duplicate id")
    return errs


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
    extra = _extra_feedback_unique_ids(valid)
    if extra:
        for m in extra:
            print(m, file=sys.stderr)
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

    print("today_day_v1 schema: OK (valid fixture passes, invalid rejected).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

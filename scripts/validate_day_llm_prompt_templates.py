#!/usr/bin/env python3
"""Validate DATA/reference/day/llm/prompt_templates.json (P1.10)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
REGISTRY_PATH = REPO / "DATA/reference/day/llm/prompt_templates.json"

sys.path.insert(0, str(REPO / "backend/src"))

from todayflow_backend.data.day_llm_prompt_template_loader import (  # noqa: E402
    DAY_LLM_PROMPT_TEMPLATE_REGISTRY_CONTRACT,
)
from todayflow_backend.data.day_llm_prompt_template_validator import (  # noqa: E402
    validate_day_llm_prompt_template_registry_payload,
)


def main() -> int:
    if not REGISTRY_PATH.is_file():
        print(f"ERROR: registry not found: {REGISTRY_PATH}", file=sys.stderr)
        return 1

    with REGISTRY_PATH.open(encoding="utf-8") as handle:
        payload = json.load(handle)

    if payload.get("contract_version") != DAY_LLM_PROMPT_TEMPLATE_REGISTRY_CONTRACT:
        print(
            f"ERROR: expected contract_version={DAY_LLM_PROMPT_TEMPLATE_REGISTRY_CONTRACT!r}",
            file=sys.stderr,
        )
        return 1

    errors = validate_day_llm_prompt_template_registry_payload(payload)
    if errors:
        for err in errors:
            print(f"ERROR: {err}", file=sys.stderr)
        return 1

    print(f"OK: {len(payload['templates'])} prompt templates validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

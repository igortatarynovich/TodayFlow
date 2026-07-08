"""Load DayModel LLM prompt template registry (P1.10)."""

from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Any

from todayflow_backend.data.day_llm_prompt_template_validator import (
    validate_day_llm_prompt_template_registry_payload,
)
from todayflow_backend.data.reference_machine_loader import DATA_ROOT

DAY_LLM_PROMPT_TEMPLATE_REGISTRY_CONTRACT = "day_llm_prompt_template_registry_v1"
DAY_LLM_PROMPT_TEMPLATE_REGISTRY_PATH = (
    DATA_ROOT / "reference" / "day" / "llm" / "prompt_templates.json"
)


class DayLlmPromptTemplateRegistryError(Exception):
    """Raised when the prompt template registry is missing or invalid."""


def clear_day_llm_prompt_template_registry_cache() -> None:
    load_day_llm_prompt_template_registry.cache_clear()


@lru_cache(maxsize=1)
def load_day_llm_prompt_template_registry() -> dict[str, Any]:
    path = Path(
        os.getenv(
            "TODAYFLOW_DAY_LLM_PROMPT_TEMPLATE_REGISTRY",
            DAY_LLM_PROMPT_TEMPLATE_REGISTRY_PATH,
        )
    )
    if not path.is_file():
        raise DayLlmPromptTemplateRegistryError(
            f"day LLM prompt template registry not found: {path}"
        )
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    _validate_registry(payload)
    return payload


def _validate_registry(payload: dict[str, Any]) -> None:
    if payload.get("contract_version") != DAY_LLM_PROMPT_TEMPLATE_REGISTRY_CONTRACT:
        raise DayLlmPromptTemplateRegistryError(
            f"expected contract_version={DAY_LLM_PROMPT_TEMPLATE_REGISTRY_CONTRACT!r}, "
            f"got {payload.get('contract_version')!r}"
        )
    errors = validate_day_llm_prompt_template_registry_payload(payload)
    if errors:
        raise DayLlmPromptTemplateRegistryError("; ".join(errors[:5]))


def get_prompt_template(
    template_id: str,
    registry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    reg = registry if registry is not None else load_day_llm_prompt_template_registry()
    template = reg.get("templates", {}).get(template_id)
    if template is None:
        raise DayLlmPromptTemplateRegistryError(f"prompt template not found: {template_id!r}")
    return dict(template)


def default_template_id_for_surface(
    surface: str,
    registry: dict[str, Any] | None = None,
) -> str | None:
    reg = registry if registry is not None else load_day_llm_prompt_template_registry()
    matches = [
        template_id
        for template_id, template in reg.get("templates", {}).items()
        if template.get("surface") == surface and template.get("status") == "active"
    ]
    if len(matches) == 1:
        return matches[0]
    return matches[0] if matches else None

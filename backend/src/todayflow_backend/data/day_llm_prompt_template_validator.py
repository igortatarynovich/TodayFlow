"""Validate DayModel LLM prompt template registry (P1.10)."""

from __future__ import annotations

from typing import Any

ALLOWED_TEMPLATE_STATUSES = frozenset({"draft", "review", "active"})

REQUIRED_TEMPLATE_FIELDS = frozenset(
    {
        "template_id",
        "template_version",
        "surface",
        "purpose",
        "status",
        "locale",
        "system_instructions",
        "task_instructions",
    }
)


def validate_day_llm_prompt_template_registry_payload(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    templates = payload.get("templates")
    if not isinstance(templates, dict) or not templates:
        errors.append("templates must be a non-empty object")
        return errors

    seen_ids: set[str] = set()
    for key, template in templates.items():
        if not isinstance(template, dict):
            errors.append(f"template {key!r} must be object")
            continue
        template_id = template.get("template_id")
        if not template_id:
            errors.append(f"template {key!r} missing template_id")
            continue
        if template_id != key:
            errors.append(f"template key {key!r} != template_id {template_id!r}")
        if template_id in seen_ids:
            errors.append(f"duplicate template_id: {template_id!r}")
        seen_ids.add(template_id)

        for field in REQUIRED_TEMPLATE_FIELDS:
            if field not in template:
                errors.append(f"template {template_id!r} missing {field}")

        status = template.get("status")
        if status not in ALLOWED_TEMPLATE_STATUSES:
            errors.append(f"template {template_id!r} invalid status: {status!r}")

        for text_field in ("system_instructions", "task_instructions", "purpose"):
            value = template.get(text_field)
            if not isinstance(value, str) or not value.strip():
                errors.append(f"template {template_id!r} {text_field} must be non-empty string")

    return errors

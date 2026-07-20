"""Versioned LLM prompt registry for TodayFlow.

Prompts live here so they can evolve with Day Engine / PIM without burying
multi-kilobyte strings inside service monoliths. Registry metadata tracks
prompt_id → version for generation_logs and learning.
"""

from todayflow_backend.prompts.registry_v1 import (
    PROMPT_REGISTRY_CONTRACT,
    get_prompt,
    list_prompt_ids,
    prompt_registry_snapshot,
)

__all__ = [
    "PROMPT_REGISTRY_CONTRACT",
    "get_prompt",
    "list_prompt_ids",
    "prompt_registry_snapshot",
]

"""Prompt registry v1 — versioned ids for learning / generation_logs.

Each prompt_id maps to a version string and a builder that returns system text
for a locale. Evolving a prompt means bumping its version and updating the
builder module — services call ``get_prompt`` instead of hardcoding strings.
"""

from __future__ import annotations

from typing import Any, Callable

from todayflow_backend.prompts import day_disclosure_v1, profile_disclosure_v1

PROMPT_REGISTRY_CONTRACT = "prompt_registry_v1"
PROMPT_REGISTRY_VERSION = "1.0.0"

PromptBuilder = Callable[[str], str]

_REGISTRY: dict[str, dict[str, Any]] = {
    # Day disclosure — multi-step per surface
    "day.guide.funnel.interp.v1": {
        "version": "1.0.0",
        "surface": "guide",
        "step": "interpretation",
        "builder": day_disclosure_v1.guide_interp_system,
    },
    "day.guide.funnel.core.v1": {
        "version": "1.0.0",
        "surface": "guide",
        "step": "core_text",
        "builder": day_disclosure_v1.guide_core_system,
    },
    "day.guide.funnel.satellites.v1": {
        "version": "1.0.0",
        "surface": "guide",
        "step": "satellites",
        "builder": day_disclosure_v1.guide_satellites_system,
    },
    "day.day_layer.funnel.personalize.v1": {
        "version": "1.0.0",
        "surface": "day_layer",
        "step": "personalize",
        "builder": day_disclosure_v1.day_layer_personalize_system,
    },
    "day.day_layer.funnel.render.v1": {
        "version": "1.0.0",
        "surface": "day_layer",
        "step": "render",
        "builder": day_disclosure_v1.day_layer_render_system,
    },
    "day.spheres.funnel.map.v1": {
        "version": "1.0.0",
        "surface": "spheres",
        "step": "map",
        "builder": day_disclosure_v1.spheres_map_system,
    },
    "day.spheres.funnel.render.v1": {
        "version": "1.0.0",
        "surface": "spheres",
        "step": "render",
        "builder": day_disclosure_v1.spheres_render_system,
    },
    "day.evening.funnel.reflect.v1": {
        "version": "1.0.0",
        "surface": "evening",
        "step": "reflect",
        "builder": day_disclosure_v1.evening_reflect_system,
    },
    "day.evening.funnel.render.v1": {
        "version": "1.0.0",
        "surface": "evening",
        "step": "render",
        "builder": day_disclosure_v1.evening_render_system,
    },
    "day.deepen.funnel.expand.v1": {
        "version": "1.0.0",
        "surface": "deepen",
        "step": "expand",
        "builder": day_disclosure_v1.deepen_expand_system,
    },
    "day.deepen.funnel.render.v1": {
        "version": "1.0.0",
        "surface": "deepen",
        "step": "render",
        "builder": day_disclosure_v1.deepen_render_system,
    },
    # Profile disclosure layers
    "profile.identity.v1": {
        "version": "1.0.0",
        "surface": "profile",
        "step": "identity",
        "builder": profile_disclosure_v1.identity_system,
    },
    "profile.styles.v1": {
        "version": "1.0.0",
        "surface": "profile",
        "step": "styles",
        "builder": profile_disclosure_v1.styles_system,
    },
    "profile.patterns.v1": {
        "version": "1.1.0",
        "surface": "profile",
        "step": "patterns",
        "builder": profile_disclosure_v1.patterns_system,
    },
    "profile.spheres.v1": {
        "version": "1.0.0",
        "surface": "profile",
        "step": "spheres",
        "builder": profile_disclosure_v1.spheres_system,
    },
}


def list_prompt_ids() -> list[str]:
    return sorted(_REGISTRY.keys())


def get_prompt(prompt_id: str, *, locale: str = "ru") -> tuple[str, str]:
    """Returns (system_prompt, version). Raises KeyError if unknown."""
    entry = _REGISTRY[prompt_id]
    builder: PromptBuilder = entry["builder"]
    return builder(locale), str(entry["version"])


def prompt_registry_snapshot() -> dict[str, Any]:
    return {
        "contract_version": PROMPT_REGISTRY_CONTRACT,
        "registry_version": PROMPT_REGISTRY_VERSION,
        "prompts": {
            pid: {
                "version": meta["version"],
                "surface": meta["surface"],
                "step": meta["step"],
            }
            for pid, meta in _REGISTRY.items()
        },
    }

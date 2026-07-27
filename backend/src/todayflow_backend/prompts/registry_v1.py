"""Prompt registry v1 — versioned ids for learning / generation_logs.

Each prompt_id maps to a version string and a builder that returns system text
for a locale. Evolving a prompt means bumping its version and updating the
builder module — services call ``get_prompt`` instead of hardcoding strings.
"""

from __future__ import annotations

from typing import Any, Callable

from todayflow_backend.prompts import (
    character_engine_stage2_v1,
    character_engine_stage3_v1,
    character_engine_stage4_v1,
    day_disclosure_v1,
    natal_decode_depth_v1,
    natal_facts_v1,
    personality_v1,
    profile_disclosure_v1,
    profile_spheres_synthesis_v1,
)

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
    # Profile disclosure layers — DEPRECATED live SoT after CHARACTER_ENGINE_PUBLISH_READY.
    # Kept for evals / rollback only; runtime gated in funnel + generate_personality.
    "profile.identity.v1": {
        "version": "1.2.0",
        "surface": "profile",
        "step": "identity",
        "builder": profile_disclosure_v1.identity_system,
        "deprecated": "character_engine_v1",
    },
    "profile.styles.v1": {
        "version": "1.1.0",
        "surface": "profile",
        "step": "styles",
        "builder": profile_disclosure_v1.styles_system,
        "deprecated": "character_engine_v1",
    },
    "profile.patterns.v1": {
        "version": "1.1.0",
        "surface": "profile",
        "step": "patterns",
        "builder": profile_disclosure_v1.patterns_system,
        "deprecated": "character_engine_v1",
    },
    "profile.spheres.v1": {
        "version": "1.0.0",
        "surface": "profile",
        "step": "spheres",
        "builder": profile_disclosure_v1.spheres_system,
        "deprecated": "character_engine_v1",
    },
    "profile.chart_reading.v1": {
        "version": "1.0.0",
        "surface": "profile",
        "step": "chart_reading",
        "builder": profile_disclosure_v1.chart_reading_system,
        "deprecated": "character_engine_v1",
    },
    # Per-sphere synthesis — DEPRECATED as personality generator after CE cutover.
    "profile.spheres.synthesis.v1": {
        "version": "1.0.0",
        "deprecated": "character_engine_v1",
        "surface": "profile",
        "step": "spheres_synthesis",
        "builder": profile_spheres_synthesis_v1.synthesis_system,
    },
    # Generation Contract: natal_facts (LLM structured chart JSON)
    "profile.natal_facts.v1": {
        "version": "1.0.0",
        "surface": "profile",
        "step": "natal_facts",
        "builder": natal_facts_v1.natal_facts_system,
    },
    # Generation Contract: personality — DEPRECATED live SoT after CE PUBLISH_READY.
    "profile.personality.v1": {
        "version": "1.0.0",
        "surface": "profile",
        "step": "personality",
        "builder": personality_v1.personality_system,
        "deprecated": "character_engine_v1",
    },
    # Character Engine Stage 2 — Identity Core (LLM-first; structural validation in code)
    "profile.character_engine.stage2.v1": {
        "version": "1.1.1",
        "surface": "character_engine",
        "step": "identity_core",
        "builder": character_engine_stage2_v1.character_engine_stage2_system,
    },
    # Character Engine Stage 3 — Internal Engine + tensions (expand Identity Core only)
    "profile.character_engine.stage3.v1": {
        "version": "1.0.1",
        "surface": "character_engine",
        "step": "internal_engine",
        "builder": character_engine_stage3_v1.character_engine_stage3_system,
    },
    # Character Engine Stage 4 — scenes · potential · blind spots
    "profile.character_engine.stage4.v1": {
        "version": "1.0.0",
        "surface": "character_engine",
        "step": "life_bundle",
        "builder": character_engine_stage4_v1.character_engine_stage4_system,
    },
    # Natal Decode Depth — opt-in; not personality SoT
    "profile.natal_decode_depth.v1": {
        "version": "1.0.1",
        "surface": "profile_depth",
        "step": "natal_decode",
        "builder": natal_decode_depth_v1.natal_decode_depth_system,
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

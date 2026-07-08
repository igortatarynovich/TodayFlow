"""B1.1 — Load Evolution CD reference (Evolution Engine owned entities)."""

from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Any

from todayflow_backend.data.evolution_cd_validator import (
    CANONICAL_STAGE_ORDER,
    EVOLUTION_CD_V1_CONTRACT,
    EVOLUTION_PATH_THEME_V1_KEYS,
    EVOLUTION_STAGE_V1_KEYS,
    STAGE_GATE_V1_KEYS,
    validate_evolution_cd_v1,
)
from todayflow_backend.data.reference_machine_loader import DATA_ROOT

EVOLUTION_CD_PATH = DATA_ROOT / "reference" / "evolution" / "evolution_cd_v1.json"


class EvolutionCdError(Exception):
    """Raised when evolution CD is missing or invalid."""


def clear_evolution_cd_cache() -> None:
    load_evolution_cd_v1.cache_clear()


@lru_cache(maxsize=1)
def load_evolution_cd_v1() -> dict[str, Any]:
    path = Path(os.getenv("TODAYFLOW_EVOLUTION_CD_PATH", EVOLUTION_CD_PATH))
    if not path.is_file():
        raise EvolutionCdError(f"evolution CD not found: {path}")
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    errors = validate_evolution_cd_v1(payload)
    if errors:
        raise EvolutionCdError("; ".join(errors[:8]))
    return payload


def get_evolution_stage(code: str, cd: dict[str, Any] | None = None) -> dict[str, Any]:
    registry = cd if cd is not None else load_evolution_cd_v1()
    stages = registry.get("evolution_stages") or {}
    entry = stages.get(code)
    if not isinstance(entry, dict):
        raise EvolutionCdError(f"evolution stage not found: {code!r}")
    return dict(entry)


def get_evolution_path_theme(
    code: str,
    cd: dict[str, Any] | None = None,
) -> dict[str, Any]:
    registry = cd if cd is not None else load_evolution_cd_v1()
    themes = registry.get("evolution_path_themes") or {}
    entry = themes.get(code)
    if not isinstance(entry, dict):
        raise EvolutionCdError(f"evolution path theme not found: {code!r}")
    return dict(entry)


def get_stage_gate(gate_id: str, cd: dict[str, Any] | None = None) -> dict[str, Any]:
    registry = cd if cd is not None else load_evolution_cd_v1()
    for gate in registry.get("stage_gates") or []:
        if isinstance(gate, dict) and gate.get("gate_id") == gate_id:
            return dict(gate)
    raise EvolutionCdError(f"stage gate not found: {gate_id!r}")


def list_evolution_stages_ordered(cd: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    registry = cd if cd is not None else load_evolution_cd_v1()
    stages = registry.get("evolution_stages") or {}
    return [dict(stages[code]) for code in CANONICAL_STAGE_ORDER if code in stages]


def list_evolution_path_themes(cd: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    registry = cd if cd is not None else load_evolution_cd_v1()
    themes = registry.get("evolution_path_themes") or {}
    return [dict(themes[code]) for code in sorted(themes.keys())]


def list_stage_gates_ordered(cd: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    registry = cd if cd is not None else load_evolution_cd_v1()
    gates = registry.get("stage_gates") or []
    return [dict(g) for g in gates if isinstance(g, dict)]


def get_next_stage_code(code: str) -> str | None:
    if code not in CANONICAL_STAGE_ORDER:
        return None
    index = CANONICAL_STAGE_ORDER.index(code)
    if index >= len(CANONICAL_STAGE_ORDER) - 1:
        return None
    return CANONICAL_STAGE_ORDER[index + 1]


def get_stage_gate_for_transition(
    from_stage: str,
    to_stage: str,
    cd: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    for gate in list_stage_gates_ordered(cd):
        if gate.get("from_stage") == from_stage and gate.get("to_stage") == to_stage:
            return gate
    return None


def get_stage_gate_from_current_stage(
    current_stage: str,
    cd: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    next_stage = get_next_stage_code(current_stage)
    if next_stage is None:
        return None
    return get_stage_gate_for_transition(current_stage, next_stage, cd)

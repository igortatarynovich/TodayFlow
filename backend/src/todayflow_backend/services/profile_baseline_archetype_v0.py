"""Single SoT: life_path → baseline.archetype_seed (Profile calc).

Used by CoreProfileService._build_baseline and portrait_why_v0 projection.
Not a new engine — shared deterministic mapping only.
"""

from __future__ import annotations

from typing import Any

# life_path buckets → Title Case seed (machine id in Snapshot / API).
_LIFE_PATH_ARCHETYPE: dict[int, str] = {
    1: "Architect",
    8: "Architect",
    22: "Architect",
    2: "Harmonizer",
    6: "Harmonizer",
    11: "Harmonizer",
    3: "Explorer",
    5: "Explorer",
    21: "Explorer",
    4: "Sage",
    7: "Sage",
    9: "Sage",
    33: "Sage",
}

DEFAULT_ARCHETYPE_SEED = "Observer"


def archetype_seed_from_life_path(life_path: Any) -> str:
    """Map reduced life_path number → archetype_seed. Default Observer."""
    try:
        lp = int(life_path)
    except (TypeError, ValueError):
        return DEFAULT_ARCHETYPE_SEED
    return _LIFE_PATH_ARCHETYPE.get(lp, DEFAULT_ARCHETYPE_SEED)

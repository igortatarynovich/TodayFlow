"""Reference helpers for numerology calculations."""

from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Dict, Set

# Monorepo: DATA/ at repository root (parents: data → … → backend → repo root).
DEFAULT_DATA_ROOT = Path(__file__).resolve().parents[4] / "DATA"
DATA_FILE = Path(os.getenv("TODAYFLOW_DATA_DIR", DEFAULT_DATA_ROOT)) / "numerology.json"


@lru_cache(maxsize=1)
def _load_reference() -> dict:
    with DATA_FILE.open(encoding="utf-8") as handle:
        return json.load(handle)


def letters() -> Dict[str, int]:
    """Return mapping of letter -> numeric value."""
    return _load_reference().get("letters", {})


@lru_cache(maxsize=1)
def vowels() -> Set[str]:
    return {letter.upper() for letter in _load_reference().get("vowels", [])}


def master_numbers() -> Set[int]:
    return set(_load_reference().get("master_numbers", []))

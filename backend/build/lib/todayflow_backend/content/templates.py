"""Loader for paragraph templates defined in CONTENT/."""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Iterable, List

from todayflow_backend.core.config import settings


@dataclass(frozen=True)
class TextVariant:
    variant_id: str
    # text removed - now loaded from i18n layer


@dataclass(frozen=True)
class ParagraphTemplate:
    paragraph_id: str
    section: str
    sub_block: str
    meaning_type: str
    primary_axes: List[str]
    secondary_axes: List[str]
    modulators: List[str]
    lite_allowed: bool
    variants: List[TextVariant]
    layer: str = "observation"
    confidence_level: str = "medium"

    @classmethod
    def from_dict(cls, data: dict) -> "ParagraphTemplate":
        # Variants now only contain variant_id (no text - loaded from i18n)
        variants = []
        for variant in data.get("variants", []):
            if isinstance(variant, dict):
                variant_id = variant.get("variant_id")
            else:
                variant_id = variant  # Handle case where variant is just a string ID
            if variant_id:
                variants.append(TextVariant(variant_id=variant_id))
        return cls(
            paragraph_id=data["paragraph_id"],
            section=data["section"],
            sub_block=data["sub_block"],
            meaning_type=data["meaning_type"],
            primary_axes=data.get("primary_axes", []),
            secondary_axes=data.get("secondary_axes", []),
            modulators=data.get("modulators", []),
            lite_allowed=data.get("lite_allowed", False),
            variants=variants,
            layer=data.get("layer", "observation"),
            confidence_level=data.get("confidence_level", "medium"),
        )


def _load_templates_from_path(path: Path) -> List[ParagraphTemplate]:
    templates: List[ParagraphTemplate] = []
    with path.open(encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line:
                continue
            data = json.loads(line)
            templates.append(ParagraphTemplate.from_dict(data))
    return templates


@lru_cache(maxsize=1)
def load_templates(path: Path | None = None) -> List[ParagraphTemplate]:
    # Prefer meta file (no text), fallback to full file for backward compatibility
    meta_path = settings.paragraph_templates_meta_path
    if meta_path.exists():
        return _load_templates_from_path(meta_path)
    target = path or settings.paragraph_templates_path
    return _load_templates_from_path(target)


def iter_lite_allowed(templates: Iterable[ParagraphTemplate]) -> Iterable[ParagraphTemplate]:
    return (tpl for tpl in templates if tpl.lite_allowed)

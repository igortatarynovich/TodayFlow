"""Profile meaning polish — natal decode binds sky theses to IL-4 packs.

Not public JSON. Not CE / identity_core overwrite. Not personality_v1 inject.
SoT: docs/profile/PROFILE_MEANING_POLISH_V1.md · TODAY_MEANING_POLISH_V1.md (mirror).
"""

from __future__ import annotations

from typing import Any, Mapping

from todayflow_backend.services.il4_editorial_consume_v1 import fill_empty_slot, pack_present

POLISH_INSTRUCTION_RU = (
    "PROFILE_IL4_DECODE: когда во входе есть IL4_MEANING, pattern_thesis и section.thesis "
    "формулируют те же леммы / construction из пакета — не выбирают новую астрологию "
    "из natal_pack рядом с пакетом. Identity Core остаётся Character Engine — не переписывай. "
    "because_core связывает секцию с ядром, не заменяет IL4_MEANING. "
    "day_hooks — жесты на сейчас, не сюжет IL-4. Не озвучивай dropped."
)

POLISH_INSTRUCTION_EN = (
    "PROFILE_IL4_DECODE: when IL4_MEANING is present, pattern_thesis and section.thesis "
    "phrase the same lemmas / construction from the pack — do not choose new astrology "
    "from natal_pack beside the pack. Identity Core stays Character Engine — do not rewrite it. "
    "because_core links the section to the core; it does not replace IL4_MEANING. "
    "day_hooks are moves for now, not the IL-4 plot. Do not voice dropped constructions."
)


def polish_instruction(*, locale: str = "ru") -> str:
    loc = str(locale or "ru").strip().split("-")[0].lower()
    return POLISH_INSTRUCTION_EN if loc == "en" else POLISH_INSTRUCTION_RU


def augment_decode_system(system: str, pack: Any, *, locale: str = "ru") -> str:
    if not pack_present(pack):
        return system
    extra = polish_instruction(locale=locale)
    base = system or ""
    if extra in base:
        return base
    return f"{base.rstrip()}\n\n{extra}\n"


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def reject_invalid_decode(output: Any, pack: Mapping[str, Any] | None) -> str | None:
    """Reject-invalid only. Does not rewrite copy. Does not touch identity_core."""
    if not pack_present(pack):
        return None
    if not isinstance(output, Mapping):
        return None
    sections = _as_list(output.get("sections"))
    has_thesis = any(
        isinstance(row, Mapping) and str(row.get("thesis") or "").strip() for row in sections
    )
    if not has_thesis:
        return "empty_decode_thesis"
    return None


def fill_empty_decode_theses(normalized: dict[str, Any], pack: Mapping[str, Any] | None) -> dict[str, Any]:
    """Fill empty pattern_thesis / section.thesis only. Never overwrite CE identity_core."""
    if not pack_present(pack) or pack is None:
        return normalized
    out = dict(normalized)
    out["pattern_thesis"] = fill_empty_slot(out.get("pattern_thesis"), pack)
    filled_sections: list[dict[str, Any]] = []
    for row in _as_list(out.get("sections")):
        item = dict(row) if isinstance(row, Mapping) else {}
        item["thesis"] = fill_empty_slot(item.get("thesis"), pack)
        filled_sections.append(item)
    out["sections"] = filled_sections
    return out

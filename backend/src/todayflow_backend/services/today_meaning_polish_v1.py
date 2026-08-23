"""Today meaning polish — native scenario binds astrology chorus to IL-4 packs.

Not public JSON. Not Today prompts as meaning SoT. Not post-LLM overwrite.
SoT: docs/today/TODAY_MEANING_POLISH_V1.md · TODAY_CONTENT_PIPELINE_V1.md I0.
"""

from __future__ import annotations

from typing import Any, Mapping

from todayflow_backend.services.il4_editorial_consume_v1 import fill_empty_slot, pack_present

POLISH_INSTRUCTION_RU = (
    "TODAY_IL4_CHORUS: когда во входе есть IL4_MEANING, голос interpretive_chorus.astrology "
    "формулирует те же леммы / construction из пакета — не выбирает новую астрологию. "
    "conflict и scenes строятся из DRAMATURGY_BRIEF. "
    "Карта / число / натал — по правилам хора, но не отменяют IL4_MEANING для астрологии."
)

POLISH_INSTRUCTION_EN = (
    "TODAY_IL4_CHORUS: when IL4_MEANING is present, interpretive_chorus.astrology "
    "phrases the same lemmas / construction from the pack — do not choose new astrology. "
    "conflict and scenes come from DRAMATURGY_BRIEF. "
    "Card / number / natal follow chorus rules but do not override IL4_MEANING for astrology."
)


def polish_instruction(*, locale: str = "ru") -> str:
    loc = str(locale or "ru").strip().split("-")[0].lower()
    return POLISH_INSTRUCTION_EN if loc == "en" else POLISH_INSTRUCTION_RU


def augment_native_system(system: str, pack: Any, *, locale: str = "ru") -> str:
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


def reject_invalid_native(output: Any, pack: Mapping[str, Any] | None) -> str | None:
    """Reject-invalid only. Does not rewrite copy."""
    if not pack_present(pack):
        return None
    if not isinstance(output, Mapping):
        return None
    chorus = _as_dict(output.get("interpretive_chorus"))
    astro = _as_list(chorus.get("astrology"))
    if not astro:
        return "empty_astrology_chorus"
    has_meaning = any(
        isinstance(row, Mapping) and str(row.get("human_meaning") or "").strip()
        for row in astro
    )
    if not has_meaning:
        return "empty_astrology_chorus"
    return None


def fill_empty_astrology_chorus(normalized: dict[str, Any], pack: Mapping[str, Any] | None) -> dict[str, Any]:
    """Fill empty astrology human_meaning only. Never overwrite non-empty prose."""
    if not pack_present(pack) or pack is None:
        return normalized
    out = dict(normalized)
    chorus = dict(_as_dict(out.get("interpretive_chorus")))
    astro = [dict(row) if isinstance(row, Mapping) else {} for row in _as_list(chorus.get("astrology"))]
    primary_text = fill_empty_slot("", pack)
    construction = ""
    lines = pack.get("lines") or []
    if lines and isinstance(lines[0], Mapping):
        construction = str(lines[0].get("construction") or "").strip()
    if not astro and primary_text:
        astro = [
            {
                "named_factor": construction or "sky",
                "human_meaning": primary_text,
                "link_to_conflict": "",
                "evidence_refs": [],
            }
        ]
    else:
        filled: list[dict[str, Any]] = []
        for row in astro:
            item = dict(row)
            item["human_meaning"] = fill_empty_slot(item.get("human_meaning"), pack)
            if not str(item.get("named_factor") or "").strip() and construction:
                item["named_factor"] = construction
            filled.append(item)
        astro = filled
    chorus["astrology"] = astro
    out["interpretive_chorus"] = chorus
    return out

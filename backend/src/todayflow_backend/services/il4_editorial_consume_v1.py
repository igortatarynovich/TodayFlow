"""IL-4 editorial consume — LLM phrases packs; it does not choose meaning.

Not public JSON. Not Today prompts as meaning SoT. Not lemma overwrite.
SoT: docs/astrology/IL4_EDITORIAL_CONSUME_V1.md
"""

from __future__ import annotations

from typing import Any, Mapping

CONSUME_INSTRUCTION_RU = (
    "IL4_MEANING: астрологический смысл уже выбран (леммы / construction / rank). "
    "Формулируй человеческим языком поверх этих лемм. "
    "Нельзя добавлять темы, менять леммы или решать, что значит Saturn □ Venus. "
    "Сюжет дня (Global / DRAMATURGY_BRIEF) не заменяй этим пакетом. "
    "Не озвучивай отказанные (dropped) конструкции."
)

CONSUME_INSTRUCTION_EN = (
    "IL4_MEANING: astrological meaning is already chosen (lemmas / construction / rank). "
    "Phrase in human language from those lemmas. "
    "Do not add themes, swap lemmas, or decide what Saturn square Venus means. "
    "Do not replace the day's plot (Global / DRAMATURGY_BRIEF) with this pack. "
    "Do not voice dropped constructions."
)

_REFUSED_BODIES = ("uranus", "neptune", "pluto")


def pack_present(pack: Any) -> bool:
    if not isinstance(pack, Mapping):
        return False
    lines = pack.get("lines")
    dropped = pack.get("dropped")
    return bool(lines) or bool(dropped)


def compact_meaning(pack: Mapping[str, Any] | None) -> dict[str, Any] | None:
    """Lemma-preserving compact for protected LLM prefix. Not user copy."""
    if not pack_present(pack):
        return None
    assert pack is not None
    lines_out: list[dict[str, Any]] = []
    for line in pack.get("lines") or []:
        if not isinstance(line, Mapping):
            continue
        jobs = line.get("jobs") if isinstance(line.get("jobs"), Mapping) else {}
        lines_out.append(
            {
                "rank": line.get("rank"),
                "band": line.get("band"),
                "construction": line.get("construction"),
                "jobs": {name: list(lemmas) for name, lemmas in jobs.items()},
                "text": line.get("text"),
            }
        )
    dropped_out: list[dict[str, Any]] = []
    for frame in pack.get("dropped") or []:
        if not isinstance(frame, Mapping):
            continue
        dropped_out.append(
            {
                "construction": frame.get("construction"),
                "status": frame.get("status"),
                "reason": frame.get("reason"),
            }
        )
    return {
        "surface": pack.get("surface"),
        "tone": pack.get("tone"),
        "meaning_source": pack.get("meaning_source") or "il3_themes",
        "lines": lines_out,
        "dropped": dropped_out,
    }


def protected_block(pack: Mapping[str, Any] | None, *, locale: str = "ru") -> str:
    compact = compact_meaning(pack)
    if compact is None:
        return ""
    import json

    label = (
        "=== IL4_MEANING (SoT: астрологический смысл уже выбран; формулируй, не выбирай) ==="
        if not str(locale).lower().startswith("en")
        else "=== IL4_MEANING (SoT: astrology meaning already chosen; phrase, do not choose) ==="
    )
    return f"{label}\n{json.dumps(compact, ensure_ascii=False, separators=(',', ':'))}\n"


def consume_instruction(*, locale: str = "ru") -> str:
    loc = str(locale or "ru").strip().split("-")[0].lower()
    return CONSUME_INSTRUCTION_EN if loc == "en" else CONSUME_INSTRUCTION_RU


def augment_system_prompt(system: str, pack: Any, *, locale: str = "ru") -> str:
    if not pack_present(pack):
        return system
    extra = consume_instruction(locale=locale)
    base = system or ""
    if extra in base:
        return base
    return f"{base.rstrip()}\n\n{extra}\n"


def fill_empty_slot(value: Any, pack: Mapping[str, Any] | None) -> str:
    """Fill empty only. Never overwrite. Uses pack primary `text` (internal / last resort)."""
    text = str(value or "").strip()
    if text:
        return text
    if not pack_present(pack) or pack is None:
        return text
    lines = pack.get("lines") or []
    if not lines or not isinstance(lines[0], Mapping):
        return text
    return str(lines[0].get("text") or "").strip()


def _blob(output: Any) -> str:
    if isinstance(output, str):
        return output.lower()
    try:
        import json

        return json.dumps(output, ensure_ascii=False).lower()
    except (TypeError, ValueError):
        return str(output or "").lower()


def _dropped_atoms(pack: Mapping[str, Any]) -> set[str]:
    found: set[str] = set()
    for frame in pack.get("dropped") or []:
        if not isinstance(frame, Mapping):
            continue
        hay = " ".join(
            str(frame.get(key) or "") for key in ("construction", "reason", "status")
        ).lower()
        for body in _REFUSED_BODIES:
            if body in hay:
                found.add(body)
    return found


def reject_invalid_output(output: Any, pack: Mapping[str, Any] | None) -> str | None:
    """Reject-invalid only. Does not rewrite copy."""
    if not pack_present(pack) or pack is None:
        return None
    blob = _blob(output)
    if not blob.strip():
        return "empty_output"
    if "llm_chose_meaning" in blob and "true" in blob:
        return "llm_chose_meaning"
    for body in _dropped_atoms(pack):
        if f"astro.object.{body}" in blob or f"named_factor\": \"{body}" in blob:
            return f"voiced_refused_atom:{body}"
        if f'"{body}"' in blob and "interpretive_chorus" in blob:
            return f"voiced_refused_atom:{body}"
    if isinstance(output, Mapping):
        echoed = output.get("il4_expression_pack")
        if isinstance(echoed, Mapping) and echoed.get("lines"):
            src_text = [str(line.get("text") or "") for line in (pack.get("lines") or []) if isinstance(line, Mapping)]
            out_text = [
                str(line.get("text") or "")
                for line in (echoed.get("lines") or [])
                if isinstance(line, Mapping)
            ]
            if out_text and src_text and out_text != src_text:
                return "mutated_pack_lemmas"
    return None

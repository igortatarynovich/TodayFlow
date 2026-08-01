#!/usr/bin/env python3
"""Rebuild DATA/reference/tarot/card_base_v1/cards.json from knowledge_v1 + deck identity.

Canon: docs/tarot/TAROT_CARD_BASE_V1.md · docs/foundation_v1.md §3

Major KB rows have a distinct `reversed.central` sentence + atomic `themes`.
Minor KB rows historically stuffed semicolon-blobs into both `central` and
`themes[0]` — the old builder concatenated them into
``blob — blob; more``, which leaked into product. This rebuild atomicizes
tags and never re-appends theme text already present in central.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DECK = ROOT / "DATA" / "astrology_reference" / "tarot_full_deck.json"
KB = ROOT / "DATA" / "reference" / "tarot" / "knowledge_v1" / "cards.json"
OUT = ROOT / "DATA" / "reference" / "tarot" / "card_base_v1" / "cards.json"

_TYPO_FIXES = (
    ("парanoia", "паранойя"),
    ("paranoia", "паранойя"),
)


def _fix_typos(text: str) -> str:
    out = text
    for bad, good in _TYPO_FIXES:
        out = out.replace(bad, good)
    return out


def atomic_tags(items: list | None, *, limit: int = 5) -> list[str]:
    """Split semicolon-blobs into short tags; dedupe; strip trailing punctuation."""
    out: list[str] = []
    seen: set[str] = set()
    for item in items or []:
        raw = _fix_typos(str(item or "").strip())
        if not raw:
            continue
        parts = re.split(r"\s*;\s*", raw)
        for part in parts:
            tag = part.strip().strip(".").strip()
            if not tag:
                continue
            key = tag.casefold()
            if key in seen:
                continue
            seen.add(key)
            out.append(tag)
            if len(out) >= limit:
                return out
    return out


def _is_blob_central(central: str, theme_atoms: list[str]) -> bool:
    """True when central is not a distinct sentence but a themes dump (minor pattern)."""
    if not central:
        return True
    if ";" in central:
        return True
    if theme_atoms and central.casefold() == theme_atoms[0].casefold():
        return True
    return False


def build_upright_meaning(arch: str, light_atoms: list[str], deck_upright: str) -> str:
    arch = _fix_typos(arch.strip())
    if arch and light_atoms:
        extras = [a for a in light_atoms[:3] if a.casefold() not in arch.casefold()]
        meaning = (arch + " — " if extras else arch) + ("; ".join(extras) if extras else "")
    elif arch:
        meaning = arch
    elif light_atoms:
        meaning = "; ".join(light_atoms[:3])
    else:
        meaning = str(deck_upright or "Канонический смысл карты.").strip()
    meaning = meaning.strip()
    if meaning and not meaning.endswith("."):
        meaning += "."
    return meaning


def build_reversed_meaning(rev: dict, theme_atoms: list[str]) -> str:
    central = _fix_typos(str(rev.get("central") or "").strip())
    if not _is_blob_central(central, theme_atoms):
        # Major path: distinct sentence; append only novel theme atoms.
        extras = [a for a in theme_atoms[:2] if a.casefold() not in central.casefold()]
        meaning = central
        if extras:
            meaning = f"{meaning} — {'; '.join(extras)}"
    elif theme_atoms:
        # Minor path: synthesize short scene from atomic tags (no central—themes glue).
        meaning = "; ".join(theme_atoms[:3])
    else:
        meaning = "Перевернутое положение усиливает тень архетипа."
    meaning = meaning.strip()
    if meaning and not meaning.endswith("."):
        meaning += "."
    return meaning


def main() -> None:
    deck = json.loads(DECK.read_text(encoding="utf-8"))
    kb = json.loads(KB.read_text(encoding="utf-8"))
    kb_by = {int(c["card_id"]): c for c in kb["cards"]}
    cards = []
    for row in deck:
        cid = int(row["id"])
        k = kb_by.get(cid, {})
        name_ru = str(k.get("name_ru") or row.get("name_ru") or row.get("name") or f"#{cid}")
        ctype = str(row.get("type") or ("major" if cid <= 21 else "minor"))
        light = k.get("light") or []
        shadow = k.get("shadow") or []
        rev = k.get("reversed") if isinstance(k.get("reversed"), dict) else {}

        up_kw = atomic_tags(k.get("upright_themes") or light or row.get("keywords") or [], limit=5)
        rev_kw = atomic_tags(
            k.get("reversed_themes") or rev.get("themes") or shadow,
            limit=5,
        )

        arch = str(k.get("central_archetype") or "").strip()
        up_meaning = build_upright_meaning(arch, up_kw, str(row.get("upright") or ""))
        rev_meaning = build_reversed_meaning(rev, rev_kw)

        cards.append(
            {
                "id": cid,
                "name_ru": name_ru,
                "type": ctype,
                "upright": {"base_meaning": up_meaning, "keywords": up_kw},
                "reversed": {"base_meaning": rev_meaning, "keywords": rev_kw},
            }
        )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "contract_version": "card_base_v1",
        "locale": "ru",
        "card_count": len(cards),
        "cards": cards,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT} ({len(cards)} cards)")


if __name__ == "__main__":
    main()

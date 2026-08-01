#!/usr/bin/env python3
"""Rebuild DATA/reference/tarot/card_base_v1/cards.json from knowledge_v1 + deck identity."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DECK = ROOT / "DATA" / "astrology_reference" / "tarot_full_deck.json"
KB = ROOT / "DATA" / "reference" / "tarot" / "knowledge_v1" / "cards.json"
OUT = ROOT / "DATA" / "reference" / "tarot" / "card_base_v1" / "cards.json"


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
        up_kw = [
            str(x)
            for x in (k.get("upright_themes") or light or row.get("keywords") or [])
            if str(x).strip()
        ][:5]
        rev = k.get("reversed") if isinstance(k.get("reversed"), dict) else {}
        rev_kw = [
            str(x)
            for x in (k.get("reversed_themes") or rev.get("themes") or shadow)
            if str(x).strip()
        ][:5]
        arch = str(k.get("central_archetype") or "").strip()
        up_meaning = arch
        if light:
            up_meaning = (arch + " — " if arch else "") + "; ".join(str(x) for x in light[:3])
        if up_meaning and not up_meaning.endswith("."):
            up_meaning += "."
        rev_central = str(rev.get("central") or "").strip()
        rev_meaning = rev_central
        if rev.get("themes"):
            extra = "; ".join(str(x) for x in rev["themes"][:2] if str(x).strip())
            if extra and extra not in rev_meaning:
                rev_meaning = (rev_meaning + " — " if rev_meaning else "") + extra
        if rev_meaning and not rev_meaning.endswith("."):
            rev_meaning += "."
        if not rev_meaning:
            rev_meaning = "Перевернутое положение усиливает тень архетипа."
        if not up_meaning:
            up_meaning = str(row.get("upright") or "Канонический смысл карты.").strip()
            if not up_meaning.endswith("."):
                up_meaning += "."
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

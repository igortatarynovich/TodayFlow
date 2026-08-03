"""Fixed-4 DomainLens wire ids (ScreenFlow v3.1).

Canon: docs/today/TODAY_SCREEN_SCENARIO_V3.md §0.6 · docs/foundation/DOMAIN_MAGNITUDE_V1.md
Wire SoT: work · money · relationships · energy

Legacy triad (relationships / money_work / family) is accepted on read only via
normalize_domains_present / expand_legacy_domain_lenses — never written.
"""

from __future__ import annotations

from typing import Any

DOMAIN_WIRE_IDS: tuple[str, ...] = ("work", "money", "relationships", "energy")

# Product scene sphere → wire DomainLens id
SPHERE_TO_WIRE: dict[str, str] = {
    "work_decisions": "work",
    "work": "work",
    "career": "work",
    "money": "money",
    "finances": "money",
    "money_work": "money",
    "relationships": "relationships",
    "communication": "relationships",
    "love": "relationships",
    "family": "relationships",
    "home": "relationships",
    "energy_body": "energy",
    "energy": "energy",
    "body": "energy",
    "health": "energy",
    "creativity": "energy",
    "rest_travel": "energy",
}

WIRE_DOMAIN_TO_SPHERES: dict[str, tuple[str, ...]] = {
    "work": ("work_decisions",),
    "money": ("money",),
    "relationships": ("relationships", "communication", "home"),
    "energy": ("energy_body", "creativity", "rest_travel"),
}

# head_topic / intent keywords → wire domain
TOPIC_TO_DOMAIN: dict[str, str] = {
    "love": "relationships",
    "dialogue": "relationships",
    "relationships": "relationships",
    "близость": "relationships",
    "отношен": "relationships",
    "общен": "relationships",
    "контакт": "relationships",
    "family": "relationships",
    "семья": "relationships",
    "дом": "relationships",
    "money": "money",
    "деньг": "money",
    "финанс": "money",
    "career": "work",
    "работ": "work",
    "дела": "work",
    "work": "work",
    "body": "energy",
    "energy": "energy",
    "энерг": "energy",
    "тело": "energy",
    "здоров": "energy",
}

LEGACY_WIRE_ALIASES: dict[str, tuple[str, ...]] = {
    "money_work": ("work", "money"),
    "family": ("relationships",),
}


def sphere_to_wire(sphere: str | None) -> str | None:
    key = str(sphere or "").strip().lower()
    if not key:
        return None
    if key in DOMAIN_WIRE_IDS:
        return key
    return SPHERE_TO_WIRE.get(key)


def normalize_domain_id(raw: str | None) -> str | None:
    """Map a single id (legacy or new) to one primary wire id."""
    key = str(raw or "").strip().lower()
    if not key:
        return None
    if key in DOMAIN_WIRE_IDS:
        return key
    aliases = LEGACY_WIRE_ALIASES.get(key)
    if aliases:
        return aliases[0]
    return SPHERE_TO_WIRE.get(key)


def normalize_domains_present(ids: list[Any] | None) -> list[str]:
    """Expand legacy triad ids into fixed-4; dedupe preserving wire order."""
    seen: set[str] = set()
    out: list[str] = []
    for raw in ids or []:
        key = str(raw or "").strip().lower()
        if not key:
            continue
        expanded = LEGACY_WIRE_ALIASES.get(key) or ((key,) if key in DOMAIN_WIRE_IDS else ())
        if not expanded:
            mapped = normalize_domain_id(key)
            expanded = (mapped,) if mapped else ()
        for did in expanded:
            if did in DOMAIN_WIRE_IDS and did not in seen:
                seen.add(did)
                out.append(did)
    return [d for d in DOMAIN_WIRE_IDS if d in seen]


def expand_legacy_domain_lenses(domains: dict[str, Any] | None) -> dict[str, Any]:
    """Prefer fixed-4 keys; fold money_work/family when new keys absent."""
    src = domains if isinstance(domains, dict) else {}
    out: dict[str, Any] = {}
    for did in DOMAIN_WIRE_IDS:
        if did in src and isinstance(src.get(did), dict):
            out[did] = src[did]
    mw = src.get("money_work")
    if isinstance(mw, dict):
        if "work" not in out:
            out["work"] = mw
        if "money" not in out:
            out["money"] = mw
    fam = src.get("family")
    if isinstance(fam, dict) and "relationships" not in out:
        out["relationships"] = fam
    return out

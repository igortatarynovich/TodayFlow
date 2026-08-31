"""Personal Day Semantic Proof — V2 IL as interpretation engine for transits.

Runs representative transit facts through the pure IL-2/3/4 pipeline
without LLM involvement, and measures Coverage / Distinctiveness /
Boundedness / Usefulness.

V2 changes:
- directionality (transiting vs natal object ids)
- outer planets (Uranus/Neptune/Pluto) merged into default catalog
- natal house context added to transit_to_natal facts

Usage: cd /opt/TodayFlow/backend && .venv/bin/python scripts/personal_day_semantic_proof_v1.py
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))

from todayflow_backend.knowledge.il2_composition_v1 import load_objects
from todayflow_backend.knowledge.il3_interpretation_v1 import SkyFact, interpret
from todayflow_backend.knowledge.il4_expression_v1 import express


@dataclass(frozen=True)
class Probe:
    label: str
    construction: str
    parts: tuple[str, ...]
    expected: str = "composed"  # composed | refused


# Representative transit constructions. The last item is a natal-house-aware tuple:
# (transiting_id, natal_id, aspect_id, natal_house_id).
TRANSIT_TO_NATAL_PROBES: list[Probe] = [
    Probe("Saturn □ Moon, Moon H4", "transit_to_natal", ("astro.object.saturn", "astro.object.moon", "astro.aspect.square", "astro.house.04")),
    Probe("Mars □ Venus, Venus H7", "transit_to_natal", ("astro.object.mars", "astro.object.venus", "astro.aspect.square", "astro.house.07")),
    Probe("Jupiter △ Sun, Sun H10", "transit_to_natal", ("astro.object.jupiter", "astro.object.sun", "astro.aspect.trine", "astro.house.10")),
    Probe("Venus ☌ Moon, Moon H2", "transit_to_natal", ("astro.object.venus", "astro.object.moon", "astro.aspect.conjunction", "astro.house.02")),
    Probe("Mercury ☍ Saturn, Saturn H6", "transit_to_natal", ("astro.object.mercury", "astro.object.saturn", "astro.aspect.opposition", "astro.house.06")),
    Probe("Uranus ☌ Sun, Sun H1", "transit_to_natal", ("astro.object.uranus", "astro.object.sun", "astro.aspect.conjunction", "astro.house.01")),
    Probe("Neptune □ Mercury, Mercury H3", "transit_to_natal", ("astro.object.neptune", "astro.object.mercury", "astro.aspect.square", "astro.house.03")),
    Probe("Pluto △ Venus, Venus H5", "transit_to_natal", ("astro.object.pluto", "astro.object.venus", "astro.aspect.trine", "astro.house.05")),
    Probe("Saturn □ Sun, Sun H10", "transit_to_natal", ("astro.object.saturn", "astro.object.sun", "astro.aspect.square", "astro.house.10")),
    Probe("Mars □ Sun, Sun H1", "transit_to_natal", ("astro.object.mars", "astro.object.sun", "astro.aspect.square", "astro.house.01")),
    Probe("Jupiter ☌ Moon, Moon H4", "transit_to_natal", ("astro.object.jupiter", "astro.object.moon", "astro.aspect.conjunction", "astro.house.04")),
    Probe("Venus □ Mars, Mars H1", "transit_to_natal", ("astro.object.venus", "astro.object.mars", "astro.aspect.square", "astro.house.01")),
    Probe("Mercury △ Venus, Venus H7", "transit_to_natal", ("astro.object.mercury", "astro.object.venus", "astro.aspect.trine", "astro.house.07")),
    Probe("Mars ☌ Mars, Mars H1", "transit_to_natal", ("astro.object.mars", "astro.object.mars", "astro.aspect.conjunction", "astro.house.01")),
    Probe("Saturn ☌ Venus, Venus H10", "transit_to_natal", ("astro.object.saturn", "astro.object.venus", "astro.aspect.conjunction", "astro.house.10")),
    Probe("Jupiter □ Saturn, Saturn H6", "transit_to_natal", ("astro.object.jupiter", "astro.object.saturn", "astro.aspect.square", "astro.house.06")),
    Probe("Venus ☌ Sun, Sun H5", "transit_to_natal", ("astro.object.venus", "astro.object.sun", "astro.aspect.conjunction", "astro.house.05")),
    Probe("Mercury □ Moon, Moon H4", "transit_to_natal", ("astro.object.mercury", "astro.object.moon", "astro.aspect.square", "astro.house.04")),
    Probe("Mars △ Venus, Venus H7", "transit_to_natal", ("astro.object.mars", "astro.object.venus", "astro.aspect.trine", "astro.house.07")),
    Probe("Jupiter ☌ Jupiter, Jupiter H9", "transit_to_natal", ("astro.object.jupiter", "astro.object.jupiter", "astro.aspect.conjunction", "astro.house.09")),
    Probe("Saturn △ Mars, Mars H1", "transit_to_natal", ("astro.object.saturn", "astro.object.mars", "astro.aspect.trine", "astro.house.01")),
    Probe("Venus △ Saturn, Saturn H11", "transit_to_natal", ("astro.object.venus", "astro.object.saturn", "astro.aspect.trine", "astro.house.11")),
    Probe("Mercury ☌ Mercury, Mercury H3", "transit_to_natal", ("astro.object.mercury", "astro.object.mercury", "astro.aspect.conjunction", "astro.house.03")),
    Probe("Mars ☍ Saturn, Saturn H6", "transit_to_natal", ("astro.object.mars", "astro.object.saturn", "astro.aspect.opposition", "astro.house.06")),
    Probe("Jupiter □ Moon, Moon H4", "transit_to_natal", ("astro.object.jupiter", "astro.object.moon", "astro.aspect.square", "astro.house.04")),
    Probe("Saturn ☌ Moon, Moon H4", "transit_to_natal", ("astro.object.saturn", "astro.object.moon", "astro.aspect.conjunction", "astro.house.04")),
    Probe("Venus □ Moon, Moon H8", "transit_to_natal", ("astro.object.venus", "astro.object.moon", "astro.aspect.square", "astro.house.08")),
    Probe("Mercury △ Sun, Sun H10", "transit_to_natal", ("astro.object.mercury", "astro.object.sun", "astro.aspect.trine", "astro.house.10")),
    Probe("Mars ☌ Jupiter, Jupiter H9", "transit_to_natal", ("astro.object.mars", "astro.object.jupiter", "astro.aspect.conjunction", "astro.house.09")),
    Probe("Saturn ☍ Jupiter, Jupiter H12", "transit_to_natal", ("astro.object.saturn", "astro.object.jupiter", "astro.aspect.opposition", "astro.house.12")),
]

TRANSIT_THROUGH_HOUSE_PROBES: list[Probe] = [
    Probe("Saturn through 10", "transit_through_house", ("astro.object.saturn", "astro.house.10")),
    Probe("Jupiter through 7", "transit_through_house", ("astro.object.jupiter", "astro.house.07")),
    Probe("Mars through 1", "transit_through_house", ("astro.object.mars", "astro.house.01")),
    Probe("Venus through 2", "transit_through_house", ("astro.object.venus", "astro.house.02")),
    Probe("Uranus through 7", "transit_through_house", ("astro.object.uranus", "astro.house.07")),
]


def run_probe(catalog: dict[str, dict[str, Any]], probe: Probe) -> dict[str, Any]:
    fact = SkyFact(probe.construction, probe.parts)
    themes = interpret(catalog, [fact])
    surface = "today"
    pack = express(themes, surface)
    line = pack.lines[0] if pack.lines else None
    frame = themes.themes[0].frame if themes.themes else None
    dropped = pack.dropped[0] if pack.dropped else None

    return {
        "label": probe.label,
        "construction": probe.construction,
        "parts": probe.parts,
        "expected": probe.expected,
        "status": frame.status if frame else (dropped.status if dropped else "unknown"),
        "reason": frame.reason if frame else (dropped.reason if dropped else None),
        "text": line.text if line else None,
        "jobs": line.jobs if line else None,
        "subject_jobs": line.subject_jobs if line else None,
        "modifier_jobs": line.modifier_jobs if line else None,
        "transiting_object_id": line.transiting_object_id if line else None,
        "natal_object_id": line.natal_object_id if line else None,
    }


def distinctiveness_score(results: list[dict[str, Any]]) -> dict[str, Any]:
    """How many unique produced texts vs how many probes?"""
    composed = [r for r in results if r["status"] == "composed"]
    texts = [r["text"] for r in composed]
    unique = len(set(texts))
    total = len(composed)
    return {
        "composed_count": total,
        "unique_texts": unique,
        "redundancy_ratio": round((total - unique) / total, 3) if total else 0,
    }


def boundedness_check(results: list[dict[str, Any]]) -> dict[str, Any]:
    """Check that composed texts only contain canon lemmas and job labels."""
    composed = [r for r in results if r["status"] == "composed"]
    leaked = 0
    for r in composed:
        text = r["text"] or ""
        # Look for words that would imply an invented interpretation rather than
        # atom lemma assembly. The allowed labels are: transiting, target, relation,
        # context, what, how, where, orientation, plus the atom lemmas themselves.
        if any(word in text for word in ["because", "so", "therefore", "feels like", "means", "leads to"]):
            leaked += 1
    return {"suspected_leaks": leaked, "composed_count": len(composed)}


def main() -> int:
    catalog = load_objects()
    print(f"Loaded {len(catalog)} IL objects (merged main + outers)")
    for obj_id in ("astro.object.uranus", "astro.object.neptune", "astro.object.pluto"):
        print(f"  {obj_id}: {'present' if obj_id in catalog else 'missing'}")

    all_probes = TRANSIT_TO_NATAL_PROBES + TRANSIT_THROUGH_HOUSE_PROBES
    results = [run_probe(catalog, p) for p in all_probes]

    # Coverage
    composed = [r for r in results if r["status"] == "composed"]
    refused = [r for r in results if r["status"] == "refused"]
    expected_refused = [r for r in results if r["expected"] == "refused"]
    unexpected_refused = [r for r in results if r["expected"] == "composed" and r["status"] == "refused"]
    unexpected_composed = [r for r in results if r["expected"] == "refused" and r["status"] == "composed"]

    coverage = {
        "total": len(all_probes),
        "composed": len(composed),
        "refused": len(refused),
        "expected_refused": len(expected_refused),
        "unexpected_refused": len(unexpected_refused),
        "unexpected_composed": len(unexpected_composed),
        "coverage_rate": round(len(composed) / len(all_probes), 3),
    }

    print("\n=== COVERAGE ===")
    for k, v in coverage.items():
        print(f"  {k}: {v}")

    print("\n=== DISTINCTIVENESS ===")
    for k, v in distinctiveness_score(results).items():
        print(f"  {k}: {v}")

    print("\n=== BOUNDEDNESS ===")
    for k, v in boundedness_check(results).items():
        print(f"  {k}: {v}")

    print("\n=== DETAILED RESULTS ===")
    for r in results:
        status_marker = "OK" if r["status"] == r["expected"] else "MISMATCH"
        print(f"\n[{status_marker}] {r['label']} ({r['status']})")
        if r["reason"]:
            print(f"  reason: {r['reason']}")
        if r["text"]:
            print(f"  text: {r['text']}")
            print(f"  subject_jobs: {r['subject_jobs']}")
            print(f"  modifier_jobs: {r['modifier_jobs']}")
            print(f"  transiting_id: {r['transiting_object_id']}")
            print(f"  natal_id: {r['natal_object_id']}")

    print("\n=== REFUSED (missing atoms) ===")
    for r in refused:
        print(f"  {r['label']}: {r['reason']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

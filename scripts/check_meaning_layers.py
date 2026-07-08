"""Utility to audit paragraph templates for layer coverage."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

CONTENT_PATH = Path(__file__).resolve().parents[1] / "CONTENT" / "paragraph_templates_v1.meta.jsonl"
REQUIRED_LAYERS = ["observation", "interpretation", "context"]


def load_templates(path: Path) -> list[dict]:
    templates: list[dict] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            templates.append(json.loads(line))
    return templates


def audit_layers(templates: list[dict]) -> tuple[dict, dict]:
    layer_counts: defaultdict[str, int] = defaultdict(int)
    meaning_layers: defaultdict[tuple[str, str, str], set[str]] = defaultdict(set)
    for tpl in templates:
        layer = tpl.get("layer", "observation")
        layer_counts[layer] += 1
        key = (tpl["section"], tpl["sub_block"], tpl["meaning_type"])
        meaning_layers[key].add(layer)
    return layer_counts, meaning_layers


def main() -> None:
    templates = load_templates(CONTENT_PATH)
    layer_counts, meaning_layers = audit_layers(templates)

    print("Layer counts:")
    for layer in REQUIRED_LAYERS:
        print(f"  {layer}: {layer_counts.get(layer, 0)}")

    missing = []
    for key, layers in meaning_layers.items():
        missing_layers = [layer for layer in REQUIRED_LAYERS if layer not in layers]
        if missing_layers:
            missing.append((key, missing_layers))

    print(f"\nMeanings missing layers: {len(missing)}")
    for (section, sub_block, meaning), missing_layers in missing[:20]:
        print(
            f"  {section} / {sub_block} / {meaning}: missing {', '.join(missing_layers)}"
        )

    if missing:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

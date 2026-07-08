#!/usr/bin/env python3
"""Validate catalog configuration for TodayFlow."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG_DIR = ROOT / "CONTENT" / "catalog"


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SystemExit(f"Missing catalog file: {path}")


def main() -> int:
    products_data = load_json(CATALOG_DIR / "products.json")
    product_ids = {item["id"] for item in products_data.get("products", [])}

    if not product_ids:
        print("[catalog] No products defined", file=sys.stderr)
        return 1

    missing: list[str] = []

    # navigation
    nav_data = load_json(CATALOG_DIR / "navigation.json")
    for column in nav_data.get("columns", []):
        for section in column.get("sections", []):
            for item in section.get("items", []):
                pid = item.get("product_id")
                if pid and pid not in product_ids:
                    missing.append(f"navigation::{column['slug']}::{section['slug']} -> {pid}")

    # recommendations
    rec_data = load_json(CATALOG_DIR / "recommendations.json")
    for card in rec_data.get("cards", []):
        pid = card.get("product_id")
        if pid and pid not in product_ids:
            missing.append(f"recommendations -> {pid}")

    if missing:
        print("[catalog] Unknown product references detected:")
        for ref in missing:
            print(f" - {ref}")
        return 1

    print(f"[catalog] OK - {len(product_ids)} products, {len(missing)} issues")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

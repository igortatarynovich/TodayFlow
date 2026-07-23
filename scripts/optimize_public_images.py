#!/usr/bin/env python3
"""Optimize TodayFlow public raster images for product surfaces.

Usage:
  python3 scripts/optimize_public_images.py
  python3 scripts/optimize_public_images.py path/to/file.png

Defaults: max edge 1024px, WebP q=80, strip metadata. Deletes source PNG when
writing a sibling .webp unless --keep-source.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_IMAGES = ROOT / "frontend" / "public" / "images"

# Product slots → max long edge (CSS display is much smaller; 2x retina budget).
PRESETS: dict[str, int] = {
    "archetypes": 1024,  # Profile Recognition arch/circle
    "hero": 1280,  # section / journal / practices heroes
    "today-ritual-entry": 1440,  # ASSET_SPEC 2:1 entry
    "banners": 1600,
    "default": 1024,
}

TARGET_BYTES = 350_000  # soft cap ~350KB; lower quality if still over


def max_edge_for(path: Path) -> int:
    for part, edge in PRESETS.items():
        if part in path.parts:
            return edge
    return PRESETS["default"]


def optimize_one(src: Path, *, keep_source: bool, quality: int) -> Path | None:
    if src.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp"}:
        return None
    if src.name.startswith("."):
        return None

    im = Image.open(src)
    im = im.convert("RGB")
    edge = max_edge_for(src)
    w, h = im.size
    scale = min(1.0, edge / max(w, h))
    if scale < 1.0:
        im = im.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)

    dest = src.with_suffix(".webp")
    q = quality
    while q >= 55:
        im.save(dest, "WEBP", quality=q, method=6)
        if dest.stat().st_size <= TARGET_BYTES or q <= 55:
            break
        q -= 5

    if not keep_source and src.resolve() != dest.resolve() and src.suffix.lower() != ".webp":
        src.unlink()

    return dest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="*", type=Path)
    parser.add_argument("--keep-source", action="store_true")
    parser.add_argument("--quality", type=int, default=80)
    args = parser.parse_args()

    targets: list[Path] = []
    if args.paths:
        for p in args.paths:
            p = p if p.is_absolute() else (Path.cwd() / p)
            if p.is_dir():
                targets.extend(sorted(p.rglob("*")))
            else:
                targets.append(p)
    else:
        for folder in ("archetypes", "hero", "today-ritual-entry", "banners"):
            d = PUBLIC_IMAGES / folder
            if d.is_dir():
                targets.extend(sorted(d.rglob("*")))

    wrote = 0
    for src in targets:
        if not src.is_file():
            continue
        if src.suffix.lower() == ".webp" and src.stat().st_size <= TARGET_BYTES:
            continue
        out = optimize_one(src, keep_source=args.keep_source, quality=args.quality)
        if out:
            wrote += 1
            print(f"{src.name} → {out.name} ({out.stat().st_size / 1024:.0f}KB, {Image.open(out).size})")
    print(f"done: {wrote} file(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

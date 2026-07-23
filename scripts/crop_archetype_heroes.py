#!/usr/bin/env python3
"""Crop archetype masters into 4:5 hero portraits for the Profile arch frame.

Focus tuples: (center_x, center_y, zoom)
  - center in 0..1 of source
  - zoom >= 1.0 (1 = largest 4:5 window that fits; higher = tighter on face)

Usage:
  python3 scripts/crop_archetype_heroes.py
  python3 scripts/crop_archetype_heroes.py --dry-run
"""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "frontend" / "public" / "images" / "archetypes"
IOS_DIR = ROOT / "ios" / "TodayFlow" / "TodayFlow" / "Resources" / "archetypes"

# 4:5 product arch slot
OUT_W, OUT_H = 820, 1024
TARGET_RATIO = OUT_W / OUT_H  # 0.8

# Per-slug face/bust focus for arch fill (object-fit cover equivalent baked in).
FOCI: dict[str, tuple[float, float, float]] = {
    "pravitel": (0.50, 0.26, 1.35),
    "tvorets": (0.36, 0.34, 1.45),
    "mudrets": (0.48, 0.30, 1.40),
    "geroi": (0.50, 0.22, 1.55),
    "buntar": (0.38, 0.30, 1.45),
    "liubovnik": (0.55, 0.32, 1.55),
    "liubovnik_f": (0.50, 0.30, 1.40),
    "liubovnik_m": (0.50, 0.30, 1.40),
    "iskatel": (0.30, 0.38, 1.50),
    "zabotlivyi": (0.55, 0.34, 1.55),
    "nevinnyi": (0.50, 0.28, 1.45),
    "shut": (0.50, 0.24, 1.60),
    "mag": (0.52, 0.30, 1.50),
    "slavnyi_malyi": (0.48, 0.30, 1.45),
}


def crop_window(w: int, h: int, cx: float, cy: float, zoom: float) -> tuple[int, int, int, int]:
    """Return (left, top, right, bottom) for a 4:5 crop around focus."""
    # Max 4:5 window that fits in source
    if w / h >= TARGET_RATIO:
        base_h = float(h)
        base_w = base_h * TARGET_RATIO
    else:
        base_w = float(w)
        base_h = base_w / TARGET_RATIO

    crop_w = base_w / max(zoom, 1.0)
    crop_h = base_h / max(zoom, 1.0)

    # Clamp crop to source
    crop_w = min(crop_w, float(w))
    crop_h = min(crop_h, float(h))
    # Keep ratio
    if crop_w / crop_h > TARGET_RATIO:
        crop_w = crop_h * TARGET_RATIO
    else:
        crop_h = crop_w / TARGET_RATIO

    center_x = cx * w
    center_y = cy * h
    left = center_x - crop_w / 2
    top = center_y - crop_h / 2
    left = max(0.0, min(left, w - crop_w))
    top = max(0.0, min(top, h - crop_h))
    right = left + crop_w
    bottom = top + crop_h
    return int(round(left)), int(round(top)), int(round(right)), int(round(bottom))


def process_one(src: Path, *, quality: int, dry_run: bool) -> Path | None:
    slug = src.stem
    focus = FOCI.get(slug, (0.5, 0.30, 1.35))
    cx, cy, zoom = focus
    im = Image.open(src).convert("RGB")
    box = crop_window(im.width, im.height, cx, cy, zoom)
    if dry_run:
        print(f"{src.name}: {im.size} → crop {box} focus=({cx},{cy},{zoom})")
        return None
    cropped = im.crop(box).resize((OUT_W, OUT_H), Image.Resampling.LANCZOS)
    dest = src  # overwrite product webp in place
    cropped.save(dest, "WEBP", quality=quality, method=6)
    print(f"{src.name}: {im.size} → {OUT_W}x{OUT_H} ({dest.stat().st_size / 1024:.0f}KB) focus=({cx},{cy},{zoom})")
    return dest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--quality", type=int, default=82)
    parser.add_argument("--skip-ios", action="store_true")
    args = parser.parse_args()

    targets = sorted(SRC_DIR.glob("*.webp"))
    wrote = 0
    for src in targets:
        if src.name.startswith("."):
            continue
        out = process_one(src, quality=args.quality, dry_run=args.dry_run)
        if out:
            wrote += 1
            if not args.skip_ios and IOS_DIR.is_dir():
                ios_dest = IOS_DIR / out.name
                ios_dest.write_bytes(out.read_bytes())

    print(f"done: {wrote} cropped")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

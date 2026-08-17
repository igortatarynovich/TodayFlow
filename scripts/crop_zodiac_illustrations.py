#!/usr/bin/env python3
"""Slice the zodiac sheet into per-sign illustrations for the product UI.

Source: docs/design/assets/image.png (3×4 celestial portraits on black).
Outputs:
  - docs/design/assets/zodiac/{slug}.png     — master crops (RGBA)
  - frontend/public/images/zodiac/{slug}.webp — square app assets (transparent bg)

Not the line-symbol SVGs in public/images/icons/zodiac/ — those stay for
pills/masks. These are painterly portraits (avatars, cards, hero plates).

Usage:
  python3 scripts/crop_zodiac_illustrations.py
  python3 scripts/crop_zodiac_illustrations.py --dry-run
"""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs" / "design" / "assets" / "image.png"
MASTER_DIR = ROOT / "docs" / "design" / "assets" / "zodiac"
PUBLIC_DIR = ROOT / "frontend" / "public" / "images" / "zodiac"

# Sheet is 1536×1024 → 4 cols × 3 rows (last row gets remainder pixels).
COLS = 4
ROWS = 3
SIGNS = [
    "aries",
    "taurus",
    "gemini",
    "cancer",
    "leo",
    "virgo",
    "libra",
    "scorpio",
    "sagittarius",
    "capricorn",
    "aquarius",
    "pisces",
]

# Square product plate (avatar / card face).
OUT_SIZE = 640
WEBP_QUALITY = 82


def cell_boxes(width: int, height: int) -> list[tuple[int, int, int, int]]:
    col_w = width // COLS
    row_h = height // ROWS
    boxes: list[tuple[int, int, int, int]] = []
    for r in range(ROWS):
        top = r * row_h
        bottom = height if r == ROWS - 1 else (r + 1) * row_h
        for c in range(COLS):
            left = c * col_w
            right = width if c == COLS - 1 else (c + 1) * col_w
            boxes.append((left, top, right, bottom))
    return boxes


def knock_out_black(im: Image.Image) -> Image.Image:
    """Turn near-black sheet background into soft alpha; keep navy ink in art."""
    rgba = im.convert("RGBA")
    out = []
    for r, g, b, a in rgba.getdata():
        mx = r if r >= g and r >= b else (g if g >= b else b)
        mn = r if r <= g and r <= b else (g if g <= b else b)
        chroma = mx - mn
        # Pure / near-black plate only (low luminance + low chroma).
        if mx <= 10 and chroma <= 8:
            out.append((r, g, b, 0))
        elif mx < 36 and chroma <= 14:
            t = (mx - 10) / 26.0
            out.append((r, g, b, max(0, min(a, int(round(255 * t))))))
        else:
            out.append((r, g, b, a))
    rgba.putdata(out)
    return rgba


def to_square(im: Image.Image, size: int) -> Image.Image:
    """Pad to square on transparent, then scale to product size."""
    w, h = im.size
    side = max(w, h)
    canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    canvas.paste(im, ((side - w) // 2, (side - h) // 2), im)
    if side == size:
        return canvas
    return canvas.resize((size, size), Image.Resampling.LANCZOS)


def process(*, dry_run: bool) -> None:
    if not SOURCE.is_file():
        raise SystemExit(f"missing source sheet: {SOURCE}")

    sheet = Image.open(SOURCE).convert("RGBA")
    boxes = cell_boxes(*sheet.size)
    assert len(boxes) == len(SIGNS)

    if not dry_run:
        MASTER_DIR.mkdir(parents=True, exist_ok=True)
        PUBLIC_DIR.mkdir(parents=True, exist_ok=True)

    for slug, box in zip(SIGNS, boxes):
        crop = sheet.crop(box)
        cut = knock_out_black(crop)
        plate = to_square(cut, OUT_SIZE)
        master_path = MASTER_DIR / f"{slug}.png"
        public_path = PUBLIC_DIR / f"{slug}.webp"
        print(
            f"{slug}: crop={box[2]-box[0]}x{box[3]-box[1]} → "
            f"{OUT_SIZE}x{OUT_SIZE} webp"
        )
        if dry_run:
            continue
        cut.save(master_path, "PNG", optimize=True)
        plate.save(public_path, "WEBP", quality=WEBP_QUALITY, method=6)

    print(f"masters → {MASTER_DIR}")
    print(f"public  → {PUBLIC_DIR}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    process(dry_run=args.dry_run)


if __name__ == "__main__":
    main()

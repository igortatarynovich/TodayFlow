#!/usr/bin/env python3
"""Slice docs/design/assets/numbers.png into per-digit icons (1–9).

Outputs:
  docs/design/assets/numbers/{1-9}.png
  frontend/public/images/icons/numbers/{1-9}.webp

No 0 on the sheet — product falls back to text for unknown digits.

Usage:
  python3 scripts/crop_numbers_sheet.py
  python3 scripts/crop_numbers_sheet.py --dry-run
"""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SHEET = ROOT / "docs" / "design" / "assets" / "numbers.png"
MASTER_DIR = ROOT / "docs" / "design" / "assets" / "number-glyphs"
PUBLIC_DIR = ROOT / "frontend" / "public" / "images" / "icons" / "numbers"

# Content bboxes from sheet scan (inclusive pixel coords).
DIGIT_BOXES: dict[str, tuple[int, int, int, int]] = {
    "1": (100, 75, 270, 485),
    "2": (380, 70, 685, 490),
    "3": (770, 70, 1070, 490),
    "4": (1130, 70, 1480, 490),
    "5": (30, 545, 315, 940),
    "6": (330, 540, 625, 940),
    "7": (640, 545, 905, 940),
    "8": (920, 545, 1215, 940),
    "9": (1230, 540, 1510, 940),
}

OUT_SIZE = 384
WEBP_Q = 86
PAD_RATIO = 0.08


def knock_out_black(im: Image.Image) -> Image.Image:
    rgba = im.convert("RGBA")
    out = []
    for r, g, b, a in rgba.getdata():
        mx = r if r >= g and r >= b else (g if g >= b else b)
        mn = r if r <= g and r <= b else (g if g <= b else b)
        chroma = mx - mn
        if mx <= 8 and chroma <= 6:
            out.append((r, g, b, 0))
        elif mx < 28 and chroma <= 12:
            t = (mx - 8) / 20.0
            out.append((r, g, b, max(0, min(a, int(round(255 * t))))))
        else:
            out.append((r, g, b, a))
    rgba.putdata(out)
    return rgba


def content_bbox(im: Image.Image, *, alpha_min: int = 20) -> tuple[int, int, int, int] | None:
    px = im.load()
    w, h = im.size
    xs: list[int] = []
    ys: list[int] = []
    for y in range(0, h, 1):
        for x in range(0, w, 1):
            if px[x, y][3] >= alpha_min:
                xs.append(x)
                ys.append(y)
    if not xs:
        return None
    return min(xs), min(ys), max(xs) + 1, max(ys) + 1


def to_square(im: Image.Image, size: int) -> Image.Image:
    box = content_bbox(im)
    if box is None:
        return Image.new("RGBA", (size, size), (0, 0, 0, 0))
    cropped = im.crop(box)
    w, h = cropped.size
    pad = int(round(max(w, h) * PAD_RATIO))
    side = max(w, h) + pad * 2
    canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    canvas.paste(cropped, ((side - w) // 2, (side - h) // 2), cropped)
    return canvas.resize((size, size), Image.Resampling.LANCZOS)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not SHEET.is_file():
        raise SystemExit(f"missing sheet: {SHEET}")

    src = Image.open(SHEET).convert("RGBA")
    if not args.dry_run:
        MASTER_DIR.mkdir(parents=True, exist_ok=True)
        PUBLIC_DIR.mkdir(parents=True, exist_ok=True)

    for digit, (x0, y0, x1, y1) in DIGIT_BOXES.items():
        cut = knock_out_black(src.crop((x0, y0, x1, y1)))
        plate = to_square(cut, OUT_SIZE)
        print(f"{digit}: {plate.size[0]}x{plate.size[1]}")
        if args.dry_run:
            continue
        plate.save(MASTER_DIR / f"{digit}.png", "PNG", optimize=True)
        plate.save(PUBLIC_DIR / f"{digit}.webp", "WEBP", quality=WEBP_Q, method=6)

    print(f"masters → {MASTER_DIR}")
    print(f"public  → {PUBLIC_DIR}")


if __name__ == "__main__":
    main()

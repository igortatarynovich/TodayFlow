#!/usr/bin/env python3
"""Slice docs/design/assets/celestial-kit-sheet.png into chart + decor accents.

Outputs:
  frontend/public/images/icons/angles/{asc,dsc,mc,ic}.webp
  frontend/public/images/icons/zodiac-orbs/{aries…pisces}.webp
  frontend/public/images/decorative/kit/{cardinal-ring,nebula-orb,stars,flares…}.webp
  docs/design/assets/celestial-kit/…

Skips neon-duplicate planets (PlanetIcon photos already ship) and house wedges
(geometry doesn't fit current circular house chips).

Usage:
  python3 scripts/crop_celestial_kit_sheet.py
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "docs" / "design" / "assets"
SHEET_CANDIDATES = [
    ASSETS / "celestial-kit-sheet.png",
    ASSETS / "image copy.png",
]
MASTER = ASSETS / "celestial-kit"
PUBLIC = ROOT / "frontend" / "public" / "images"

ANGLE_CENTERS = {
    "asc": (992, 458),
    "dsc": (1135, 458),
    "mc": (1064, 392),
    "ic": (1064, 538),
}

ZODIAC = [
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

DECOS = {
    "cardinal-ring": ((40, 40, 320, 320), 320, 0.02),
    "nebula-orb": ((1080, 60, 1380, 320), 256, 0.04),
    "star-gold": ((1188, 348, 1288, 448), 96, 0.06),
    "star-silver": ((1290, 348, 1390, 448), 96, 0.06),
    "flare-gold": ((1380, 820, 1480, 960), 128, 0.05),
    "flare-ring": ((1380, 920, 1520, 1010), 128, 0.05),
    "orbit-planet": ((1100, 780, 1280, 980), 192, 0.04),
    "lens-nested": ((1240, 800, 1400, 980), 192, 0.04),
}


def resolve_sheet() -> Path:
    for p in SHEET_CANDIDATES:
        if p.is_file():
            if p.name == "image copy.png":
                dst = ASSETS / "celestial-kit-sheet.png"
                if not dst.exists():
                    shutil.move(str(p), str(dst))
                return dst
            return p
    raise SystemExit("missing celestial-kit-sheet.png")


def knock(src: Image.Image) -> Image.Image:
    rgba = src.convert("RGBA")
    out = []
    for r, g, b, a in rgba.getdata():
        mx = max(r, g, b)
        mn = min(r, g, b)
        chroma = mx - mn
        if mx <= 8 and chroma <= 6:
            out.append((r, g, b, 0))
        elif mx < 22 and chroma <= 10:
            t = (mx - 8) / 14.0
            out.append((r, g, b, max(0, min(a, int(round(255 * t))))))
        else:
            out.append((r, g, b, a))
    rgba.putdata(out)
    return rgba


def content_bbox(src: Image.Image, alpha_min: int = 18):
    px = src.load()
    w, h = src.size
    xs: list[int] = []
    ys: list[int] = []
    for y in range(h):
        for x in range(w):
            if px[x, y][3] >= alpha_min:
                xs.append(x)
                ys.append(y)
    if not xs:
        return None
    return min(xs), min(ys), max(xs) + 1, max(ys) + 1


def to_square(src: Image.Image, size: int, pad_ratio: float = 0.06) -> Image.Image:
    cut = knock(src)
    box = content_bbox(cut)
    if not box:
        return Image.new("RGBA", (size, size), (0, 0, 0, 0))
    cropped = cut.crop(box)
    w, h = cropped.size
    pad = int(round(max(w, h) * pad_ratio))
    side = max(w, h) + pad * 2
    canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    canvas.paste(cropped, ((side - w) // 2, (side - h) // 2), cropped)
    return canvas.resize((size, size), Image.Resampling.LANCZOS)


def circular_angle(im: Image.Image, cx: int, cy: int, r: int = 34, out_size: int = 128) -> Image.Image:
    pad = 4
    crop = knock(im.crop((cx - r - pad, cy - r - pad, cx + r + pad, cy + r + pad)))
    mask = Image.new("L", crop.size, 0)
    draw = ImageDraw.Draw(mask)
    ox = oy = r + pad
    draw.ellipse((ox - r, oy - r, ox + r, oy + r), fill=255)
    alpha = crop.split()[-1]
    crop.putalpha(Image.composite(alpha, Image.new("L", crop.size, 0), mask))
    return crop.resize((out_size, out_size), Image.Resampling.LANCZOS)


def save(master: Path, public: Path, plate: Image.Image, *, dry_run: bool) -> None:
    print(f"  → {public.name}")
    if dry_run:
        return
    master.parent.mkdir(parents=True, exist_ok=True)
    public.parent.mkdir(parents=True, exist_ok=True)
    plate.save(master, "PNG", optimize=True)
    plate.save(public, "WEBP", quality=88, method=6)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    sheet = resolve_sheet()
    im = Image.open(sheet).convert("RGBA")
    print(f"sheet: {sheet}")

    for slug, (cx, cy) in ANGLE_CENTERS.items():
        plate = circular_angle(im, cx, cy)
        save(MASTER / "angles" / f"{slug}.png", PUBLIC / "icons/angles" / f"{slug}.webp", plate, dry_run=args.dry_run)

    x0, y0, x1, y1 = 28, 338, 522, 522
    cols, rows = 6, 2
    cw = (x1 - x0) // cols
    rh = (y1 - y0) // rows
    for r in range(rows):
        for c in range(cols):
            slug = ZODIAC[r * cols + c]
            inset = 4
            cell = (
                x0 + c * cw + inset,
                y0 + r * rh + inset,
                x0 + (c + 1) * cw - inset if c < cols - 1 else x1 - inset,
                y0 + (r + 1) * rh - inset if r < rows - 1 else y1 - inset,
            )
            plate = to_square(im.crop(cell), 160, pad_ratio=0.02)
            # circular soft mask
            mask = Image.new("L", plate.size, 0)
            ImageDraw.Draw(mask).ellipse((2, 2, plate.size[0] - 3, plate.size[1] - 3), fill=255)
            a = plate.split()[-1]
            plate.putalpha(Image.composite(a, Image.new("L", plate.size, 0), mask))
            save(
                MASTER / "zodiac-orbs" / f"{slug}.png",
                PUBLIC / "icons/zodiac-orbs" / f"{slug}.webp",
                plate,
                dry_run=args.dry_run,
            )

    for slug, (box, size, pad) in DECOS.items():
        plate = to_square(im.crop(box), size, pad_ratio=pad)
        save(
            MASTER / "decorative" / f"{slug}.png",
            PUBLIC / "decorative/kit" / f"{slug}.webp",
            plate,
            dry_run=args.dry_run,
        )

    print("done")


if __name__ == "__main__":
    main()

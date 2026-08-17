#!/usr/bin/env python3
"""Slice gold zodiac glyph sheet + planet photo sheets into app icons.

Sources:
  docs/design/assets/zodiac-metal-glyphs-sheet.png  (3D silver/gold glyphs; preferred)
  docs/design/assets/zodiac-glyphs-sheet.png        (legacy framed seals)
  docs/design/assets/planets-sheet.png
  docs/design/assets/mercury-pluto-sheet.png

Outputs:
  frontend/public/images/icons/zodiac/{slug}.webp
  frontend/public/images/icons/planets/{slug}.webp
  docs/design/assets/zodiac-glyphs/{slug}.png
  docs/design/assets/planets/{slug}.png

Usage:
  python3 scripts/crop_celestial_icon_sheets.py
  python3 scripts/crop_celestial_icon_sheets.py --dry-run
  python3 scripts/crop_celestial_icon_sheets.py --zodiac-only
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "docs" / "design" / "assets"

ZODIAC_SHEET_CANDIDATES = [
    ASSETS / "zodiac-metal-glyphs-sheet.png",
    ASSETS / "image copy.png",
    ASSETS / "zodiac-glyphs-sheet.png",
]
PLANET_SHEET_CANDIDATES = [
    ASSETS / "planets-sheet.png",
    ASSETS / "image copy 2.png",
]
MERCURY_PLUTO_SHEET_CANDIDATES = [
    ASSETS / "mercury-pluto-sheet.png",
]

ZODIAC_MASTER = ASSETS / "zodiac-glyphs"
PLANET_MASTER = ASSETS / "planets"
ZODIAC_PUBLIC = ROOT / "frontend" / "public" / "images" / "icons" / "zodiac"
PLANET_PUBLIC = ROOT / "frontend" / "public" / "images" / "icons" / "planets"

ZODIAC_SIGNS = [
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

PLANET_WINDOWS: dict[str, tuple[int, int, int, int]] = {
    "sun": (10, 40, 440, 500),
    "moon": (430, 140, 675, 440),
    "venus": (660, 140, 945, 440),
    "earth": (935, 130, 1260, 460),
    "mars": (1250, 145, 1535, 445),
    "jupiter": (10, 485, 465, 960),
    "saturn": (460, 480, 920, 960),
    "uranus": (910, 485, 1270, 960),
    "neptune": (1260, 500, 1535, 900),
}

ZODIAC_OUT = 320
PLANET_OUT = 512
WEBP_Q = 86


def resolve_sheet(candidates: list[Path]) -> Path:
    for p in candidates:
        if p.is_file():
            return p
    raise SystemExit(f"missing sheet; tried: {', '.join(str(p) for p in candidates)}")


def resolve_sheet_optional(candidates: list[Path]) -> Path | None:
    for p in candidates:
        if p.is_file():
            return p
    return None


def sheet_has_alpha(im: Image.Image, *, sample_step: int = 8) -> bool:
    """True when a meaningful share of sampled pixels is already transparent."""
    rgba = im.convert("RGBA")
    w, h = rgba.size
    px = rgba.load()
    clear = 0
    n = 0
    for y in range(0, h, sample_step):
        for x in range(0, w, sample_step):
            n += 1
            if px[x, y][3] == 0:
                clear += 1
    return n > 0 and (clear / n) >= 0.15


def scrub_alpha_fringe(im: Image.Image, *, floor: int = 8) -> Image.Image:
    """Zero near-invisible leftover matte from background knockout."""
    rgba = im.convert("RGBA")
    out = []
    for r, g, b, a in rgba.getdata():
        out.append((r, g, b, 0) if a < floor else (r, g, b, a))
    rgba.putdata(out)
    return rgba


def knock_out_light(im: Image.Image) -> Image.Image:
    rgba = im.convert("RGBA")
    out = []
    for r, g, b, a in rgba.getdata():
        mx = r if r >= g and r >= b else (g if g >= b else b)
        mn = r if r <= g and r <= b else (g if g <= b else b)
        chroma = mx - mn
        if mn >= 228 and chroma <= 18:
            out.append((r, g, b, 0))
        elif mn >= 200 and chroma <= 22:
            t = (228 - mn) / 28.0
            out.append((r, g, b, max(0, min(a, int(round(255 * t))))))
        else:
            out.append((r, g, b, a))
    rgba.putdata(out)
    return rgba


def knock_out_black(im: Image.Image) -> Image.Image:
    rgba = im.convert("RGBA")
    out = []
    for r, g, b, a in rgba.getdata():
        mx = r if r >= g and r >= b else (g if g >= b else b)
        mn = r if r <= g and r <= b else (g if g <= b else b)
        chroma = mx - mn
        if mx <= 8 and chroma <= 6:
            out.append((r, g, b, 0))
        elif mx < 28 and chroma <= 10:
            t = (mx - 8) / 20.0
            out.append((r, g, b, max(0, min(a, int(round(255 * t))))))
        else:
            out.append((r, g, b, a))
    rgba.putdata(out)
    return rgba


def content_bbox(im: Image.Image, *, alpha_min: int = 24) -> tuple[int, int, int, int] | None:
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


def to_square(im: Image.Image, size: int, *, pad_ratio: float = 0.06) -> Image.Image:
    box = content_bbox(im)
    if box is None:
        return Image.new("RGBA", (size, size), (0, 0, 0, 0))
    cropped = im.crop(box)
    w, h = cropped.size
    pad = int(round(max(w, h) * pad_ratio))
    side = max(w, h) + pad * 2
    canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    canvas.paste(cropped, ((side - w) // 2, (side - h) // 2), cropped)
    return canvas.resize((size, size), Image.Resampling.LANCZOS)


def cell_boxes(width: int, height: int, cols: int, rows: int) -> list[tuple[int, int, int, int]]:
    col_w = width // cols
    row_h = height // rows
    boxes: list[tuple[int, int, int, int]] = []
    for r in range(rows):
        top = r * row_h
        bottom = height if r == rows - 1 else (r + 1) * row_h
        for c in range(cols):
            left = c * col_w
            right = width if c == cols - 1 else (c + 1) * col_w
            boxes.append((left, top, right, bottom))
    return boxes


def save_pair(master: Path, public: Path, im: Image.Image, *, dry_run: bool) -> None:
    print(f"  → {public.name} ({im.size[0]}x{im.size[1]})")
    if dry_run:
        return
    master.parent.mkdir(parents=True, exist_ok=True)
    public.parent.mkdir(parents=True, exist_ok=True)
    im.save(master, "PNG", optimize=True)
    im.save(public, "WEBP", quality=WEBP_Q, method=6)


def process_zodiac(sheet: Path, *, dry_run: bool) -> None:
    print(f"zodiac sheet: {sheet}")
    src = Image.open(sheet).convert("RGBA")
    transparent = sheet_has_alpha(src)
    print(f"  alpha sheet: {transparent}")
    for slug, box in zip(ZODIAC_SIGNS, cell_boxes(*src.size, 4, 3)):
        cut = src.crop(box)
        cut = scrub_alpha_fringe(cut) if transparent else knock_out_light(cut)
        plate = to_square(cut, ZODIAC_OUT, pad_ratio=0.08)
        save_pair(
            ZODIAC_MASTER / f"{slug}.png",
            ZODIAC_PUBLIC / f"{slug}.webp",
            plate,
            dry_run=dry_run,
        )


def process_planets(sheet: Path, *, dry_run: bool) -> None:
    print(f"planet sheet: {sheet}")
    src = Image.open(sheet).convert("RGBA")
    for slug, (x0, y0, x1, y1) in PLANET_WINDOWS.items():
        cut = knock_out_black(src.crop((x0, y0, x1, y1)))
        pad = 0.02 if slug in {"sun", "saturn"} else 0.05
        plate = to_square(cut, PLANET_OUT, pad_ratio=pad)
        save_pair(
            PLANET_MASTER / f"{slug}.png",
            PLANET_PUBLIC / f"{slug}.webp",
            plate,
            dry_run=dry_run,
        )


def fg_bbox(
    im: Image.Image,
    *,
    x0: int,
    y0: int,
    x1: int,
    y1: int,
    thr: int = 12,
) -> tuple[int, int, int, int] | None:
    px = im.load()
    xs: list[int] = []
    ys: list[int] = []
    for y in range(y0, y1):
        for x in range(x0, x1):
            r, g, b, a = px[x, y]
            if a > 20 and max(r, g, b) > thr:
                xs.append(x)
                ys.append(y)
    if not xs:
        return None
    return min(xs), min(ys), max(xs) + 1, max(ys) + 1


def process_mercury_pluto(sheet: Path, *, dry_run: bool) -> None:
    """Left = Mercury, right = Pluto on a two-body black sheet."""
    print(f"mercury/pluto sheet: {sheet}")
    src = Image.open(sheet).convert("RGBA")
    w, h = src.size
    mid = w // 2
    for slug, left, right in (("mercury", 0, mid), ("pluto", mid, w)):
        box = fg_bbox(src, x0=left, y0=0, x1=right, y1=h)
        if box is None:
            raise SystemExit(f"no content for {slug} on {sheet}")
        x0, y0, x1, y1 = box
        pad = 8
        cut = knock_out_black(
            src.crop((max(0, x0 - pad), max(0, y0 - pad), min(w, x1 + pad), min(h, y1 + pad)))
        )
        plate = to_square(cut, PLANET_OUT, pad_ratio=0.05)
        save_pair(
            PLANET_MASTER / f"{slug}.png",
            PLANET_PUBLIC / f"{slug}.webp",
            plate,
            dry_run=dry_run,
        )


def maybe_rename_sheets(*, dry_run: bool) -> None:
    pairs = [
        (ASSETS / "image copy 2.png", ASSETS / "planets-sheet.png"),
        (ASSETS / "image copy.png", ASSETS / "zodiac-metal-glyphs-sheet.png"),
    ]
    for src, dst in pairs:
        if src.is_file() and not dst.exists():
            print(f"rename {src.name} → {dst.name}")
            if not dry_run:
                shutil.move(str(src), str(dst))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--skip-rename", action="store_true")
    parser.add_argument("--zodiac-only", action="store_true")
    args = parser.parse_args()

    if not args.skip_rename:
        maybe_rename_sheets(dry_run=args.dry_run)

    zodiac_sheet = resolve_sheet(ZODIAC_SHEET_CANDIDATES)
    process_zodiac(zodiac_sheet, dry_run=args.dry_run)
    if args.zodiac_only:
        print("done")
        return

    planet_sheet = resolve_sheet(PLANET_SHEET_CANDIDATES)
    process_planets(planet_sheet, dry_run=args.dry_run)

    mp_sheet = resolve_sheet_optional(MERCURY_PLUTO_SHEET_CANDIDATES)
    if mp_sheet:
        process_mercury_pluto(mp_sheet, dry_run=args.dry_run)

    print("done")


if __name__ == "__main__":
    main()

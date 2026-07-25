#!/usr/bin/env python3
"""Build optimized Tarot web assets from licensed masters.

Masters: assets-source/tarot/masters/white-witchcore/
Output:  frontend/public/images/cards/tarot/web/
Manifest: frontend/public/images/cards/tarot/web/manifest.json
          (+ copy for typed import: frontend/src/data/tarotWebManifest.json)

Sizes (3:5): 384×640, 576×960, 768×1280
Formats: AVIF (preferred) + WebP (fallback)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
MASTERS = ROOT / "assets-source" / "tarot" / "masters" / "white-witchcore"
OUT = ROOT / "frontend" / "public" / "images" / "cards" / "tarot" / "web"
MANIFEST_PUBLIC = OUT / "manifest.json"
MANIFEST_SRC = ROOT / "frontend" / "src" / "data" / "tarotWebManifest.json"

SIZES = (
    (384, 640),
    (576, 960),
    (768, 1280),
)

SUITS = (
    ("Suit of Wands", "wands"),
    ("Suit of Cups", "cups"),
    ("Suit of Swords", "swords"),
    ("Suit of Pentacles", "pentacles"),
)


def deck_key(deck_index: int) -> str:
    return f"{deck_index:02d}"


def resize_cover(im: Image.Image, size: tuple[int, int]) -> Image.Image:
    """Resize to exact size keeping 3:5; masters are already 3:5."""
    target_w, target_h = size
    rgb = im.convert("RGBA")
    # High-quality downsample
    return rgb.resize((target_w, target_h), Image.Resampling.LANCZOS)


def write_variants(im: Image.Image, stem: str, rel_dir: Path) -> dict[str, dict[str, str]]:
    """Write avif+webp for each size; return manifest entry paths (web-relative)."""
    out: dict[str, dict[str, str]] = {}
    dest_dir = OUT / rel_dir
    dest_dir.mkdir(parents=True, exist_ok=True)
    for w, h in SIZES:
        sized = resize_cover(im, (w, h))
        label = f"{w}x{h}"
        avif_name = f"{stem}-{label}.avif"
        webp_name = f"{stem}-{label}.webp"
        avif_path = dest_dir / avif_name
        webp_path = dest_dir / webp_name
        # AVIF via Pillow (libavif)
        sized.save(avif_path, format="AVIF", quality=62, speed=4)
        sized.save(webp_path, format="WEBP", quality=78, method=6)
        prefix = "" if rel_dir == Path(".") else f"{rel_dir.as_posix()}/"
        out[label] = {
            "avif": f"{prefix}{avif_name}",
            "webp": f"{prefix}{webp_name}",
            "width": w,
            "height": h,
        }
    return out


def load_master(path: Path) -> Image.Image:
    if not path.is_file():
        raise FileNotFoundError(path)
    return Image.open(path)


def main() -> int:
    if not MASTERS.is_dir():
        print(f"ERROR: masters missing at {MASTERS}", file=sys.stderr)
        print("Place White Witchcore deck under assets-source/tarot/masters/white-witchcore/", file=sys.stderr)
        return 1

    OUT.mkdir(parents=True, exist_ok=True)
    cards: list[dict] = []

    # Back
    back_im = load_master(MASTERS / "Back Design.png")
    back_variants = write_variants(back_im, "back", Path("."))
    print("back ok")

    # Major 0..21
    for i in range(22):
        src = MASTERS / "Major Arcana" / f"{i}.png"
        im = load_master(src)
        variants = write_variants(im, deck_key(i), Path("faces"))
        cards.append(
            {
                "deck_index": i,
                "id": f"major_{i}",
                "type": "major",
                "source": f"Major Arcana/{i}.png",
                "variants": variants,
            }
        )
        print(f"major {i} ok")

    # Minors 22..77
    deck_index = 22
    for suit_folder, suit_slug in SUITS:
        for rank in range(1, 15):
            src = MASTERS / suit_folder / f"{rank}.png"
            im = load_master(src)
            variants = write_variants(im, deck_key(deck_index), Path("faces"))
            cards.append(
                {
                    "deck_index": deck_index,
                    "id": f"{suit_slug}_{rank}",
                    "type": "minor",
                    "suit": suit_slug,
                    "rank": rank,
                    "source": f"{suit_folder}/{rank}.png",
                    "variants": variants,
                }
            )
            print(f"minor {deck_index} ({suit_slug}/{rank}) ok")
            deck_index += 1

    if len(cards) != 78:
        print(f"ERROR: expected 78 cards, got {len(cards)}", file=sys.stderr)
        return 1

    manifest = {
        "version": "1.0.0",
        "deck": "white-witchcore",
        "aspect_ratio": "3:5",
        "sizes": [{"width": w, "height": h, "label": f"{w}x{h}"} for w, h in SIZES],
        "formats": ["avif", "webp"],
        "public_base": "/images/cards/tarot/web",
        "back": {"variants": back_variants},
        "cards": cards,
    }

    MANIFEST_PUBLIC.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    MANIFEST_SRC.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_SRC.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {MANIFEST_PUBLIC}")
    print(f"wrote {MANIFEST_SRC}")
    print("done")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

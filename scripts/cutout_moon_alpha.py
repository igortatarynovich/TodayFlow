#!/usr/bin/env python3
"""Cut out solid black background from moon_no_background via edge flood-fill + feather.

Do NOT use a global near-black luminance threshold (destroys maria / soft halo).
Mask = connected background from image edges, then contour feathering → lossless WebP alpha.
"""

from __future__ import annotations

import argparse
from collections import deque
from pathlib import Path

from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SRC = ROOT / "frontend" / "public" / "images" / "cosmic" / "moon_no_background.png"
DEFAULT_DEST = ROOT / "frontend" / "public" / "images" / "cosmic" / "moon_cutout.webp"


def is_bg(r: int, g: int, b: int, *, max_rgb: int = 28) -> bool:
    """Edge-seeded background: near-black / very dark flat plate only."""
    return r <= max_rgb and g <= max_rgb and b <= max_rgb


def flood_background_mask(im: Image.Image, *, max_rgb: int = 28) -> Image.Image:
    """Return L mask: 0 = background (transparent), 255 = keep (opaque)."""
    rgba = im.convert("RGBA")
    w, h = rgba.size
    px = rgba.load()
    bg = [[False] * w for _ in range(h)]
    q: deque[tuple[int, int]] = deque()

    def try_seed(x: int, y: int) -> None:
        r, g, b, _ = px[x, y]
        if is_bg(r, g, b, max_rgb=max_rgb) and not bg[y][x]:
            bg[y][x] = True
            q.append((x, y))

    for x in range(w):
        try_seed(x, 0)
        try_seed(x, h - 1)
    for y in range(h):
        try_seed(0, y)
        try_seed(w - 1, y)

    while q:
        x, y = q.popleft()
        for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if nx < 0 or ny < 0 or nx >= w or ny >= h or bg[ny][nx]:
                continue
            r, g, b, _ = px[nx, ny]
            if is_bg(r, g, b, max_rgb=max_rgb):
                bg[ny][nx] = True
                q.append((nx, ny))

    mask = Image.new("L", (w, h), 255)
    mp = mask.load()
    for y in range(h):
        for x in range(w):
            if bg[y][x]:
                mp[x, y] = 0
    return mask


def cutout(
    src: Path,
    dest: Path,
    *,
    max_edge: int = 1024,
    feather: float = 1.6,
    max_rgb: int = 28,
) -> Path:
    im = Image.open(src).convert("RGBA")
    w, h = im.size
    scale = min(1.0, max_edge / max(w, h))
    if scale < 1.0:
        im = im.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)

    hard = flood_background_mask(im, max_rgb=max_rgb)
    # Feather only softens the silhouette; does not re-threshold maria.
    soft = hard.filter(ImageFilter.GaussianBlur(radius=feather))

    out = im.copy()
    out.putalpha(soft)
    dest.parent.mkdir(parents=True, exist_ok=True)
    out.save(dest, "WEBP", lossless=True, method=6)
    return dest


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--src", type=Path, default=DEFAULT_SRC)
    p.add_argument("--dest", type=Path, default=DEFAULT_DEST)
    p.add_argument("--max-edge", type=int, default=1024)
    p.add_argument("--feather", type=float, default=1.6)
    p.add_argument("--max-rgb", type=int, default=28)
    p.add_argument("--delete-source", action="store_true")
    args = p.parse_args()

    dest = cutout(args.src, args.dest, max_edge=args.max_edge, feather=args.feather, max_rgb=args.max_rgb)
    print(f"wrote {dest} ({dest.stat().st_size} bytes)")
    if args.delete_source and args.src.exists() and args.src.resolve() != dest.resolve():
        args.src.unlink()
        print(f"deleted {args.src}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

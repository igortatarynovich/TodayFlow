# Decorative UI Assets

Transparent SVG (and cosmic WebP washes) used **over** product surfaces — not as heroes.

## Rules

- Opacity typically **2–8%** (light) / slightly higher in dark theme via CSS.
- Never compete with archetype portraits or primary copy.
- Prefer stroke-only SVGs with `currentColor` (gold ink via parent `color`).
- Atmosphere layer loads images via **CSS `background-image`**, not `<img>`.

## SVG set

| File | Use |
|------|-----|
| `orbit.svg` | Concentric / elliptical orbits |
| `divider.svg` | Thin gold section divider |
| `compass.svg` | ASC / direction motif |
| `north-star.svg` | MC / peak / vector |
| `solar-rays.svg` | Sun accent |
| `vignette.svg` | Soft frame for illustration wells |

## Motifs (ProfileAtmosphere)

`why` · `insight` · `effort` · `bridge` · `natal` — see `ProfileAtmosphere.tsx`.

Wash plates (landscape **1200×800**, `background-size: cover`):

| File | Motif |
|------|--------|
| `cosmic/zodiac_wash.webp` | why |
| `cosmic/eclipse_wash.webp` | insight |
| `cosmic/stars.webp` | effort |
| `cosmic/moon_wash.webp` + `moon_orb.webp` | bridge |
| `cosmic/celestial_wash.webp` | natal |

Do **not** use portrait 682×1024 plates (`moon.webp`, `eclipse.webp`, `moon_cutout.webp`) as block backgrounds — wrong crop. Orbs/icons only via square cutouts (`moon_orb.webp`).

Do **not** ship multi‑MB PNG sources to the client; use optimized WebP under `/images/cosmic/`.

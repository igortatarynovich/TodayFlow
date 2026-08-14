# Planet icons

- `{slug}.webp` — photo planets **512×512**, transparent:
  - main sheet: `docs/design/assets/planets-sheet.png` (sun, moon, venus, earth, mars, jupiter, saturn, uranus, neptune)
  - supplement: `docs/design/assets/mercury-pluto-sheet.png` (mercury, pluto)
- `{slug}.svg` — tintable line seals (fallback / tooling)

`PlanetIcon` prefers WebP for all ten traditional chart bodies.

Rebuild:

```bash
python3 scripts/crop_celestial_icon_sheets.py
```

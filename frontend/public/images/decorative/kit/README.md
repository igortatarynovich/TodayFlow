# Celestial kit accents

Cropped from `docs/design/assets/celestial-kit-sheet.png`.

| Path | Use |
|------|-----|
| `icons/angles/{asc,dsc,mc,ic}.webp` | Natal wheel angle badges · profile ASC/MC glyphs |
| `icons/zodiac-orbs/{sign}.webp` | Natal wheel zodiac ring (dark neon glass orbs) |
| `decorative/kit/*.webp` | Atmosphere accents (stars, flares, rings, nebula orb) |

Gold seal zodiac (`icons/zodiac/`) and planet photos (`icons/planets/`) stay the primary product icons elsewhere.

Rebuild:

```bash
python3 scripts/crop_celestial_kit_sheet.py
```

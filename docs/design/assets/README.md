# Celestial icon masters

- `numbers.png` → digit icons 1–9 → `frontend/public/images/icons/numbers/*.webp`
  (`python3 scripts/crop_numbers_sheet.py`)
- `zodiac-glyphs-sheet.png` → gold zodiac seals → `frontend/public/images/icons/zodiac/*.webp`
- `planets-sheet.png` → planet photos → `frontend/public/images/icons/planets/*.webp`
- `mercury-pluto-sheet.png` → mercury + pluto photos
- `celestial-kit-sheet.png` → chart angles, neon zodiac orbs, decor accents
  (`python3 scripts/crop_celestial_kit_sheet.py`)
- Cropped PNG masters: `zodiac-glyphs/`, `planets/`, `number-glyphs/`, `celestial-kit/`

```bash
python3 scripts/crop_celestial_icon_sheets.py
python3 scripts/crop_numbers_sheet.py
python3 scripts/crop_celestial_kit_sheet.py
```

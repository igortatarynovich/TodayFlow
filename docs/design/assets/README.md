# Celestial icon masters

- `numbers.png` → digit icons 1–9 → `frontend/public/images/icons/numbers/*.webp`
  (`python3 scripts/crop_numbers_sheet.py`)
- `zodiac-glyphs-sheet.png` → gold zodiac seals → `frontend/public/images/icons/zodiac/*.webp`
- `planets-sheet.png` → planet photos → `frontend/public/images/icons/planets/*.webp`
- `mercury-pluto-sheet.png` → mercury + pluto photos
- `celestial-kit-sheet.png` → chart angles, neon zodiac orbs, decor accents
  (`python3 scripts/crop_celestial_kit_sheet.py`)
- `ui-kit-form-sheet.png` → **form / layout reference** (glass cards, pills, chips, radial/linear metrics, planet-as-sphere). Colors are illustrative; product mood owns palette.
- Cropped PNG masters: `zodiac-glyphs/`, `planets/`, `number-glyphs/`, `celestial-kit/`

```bash
python3 scripts/crop_celestial_icon_sheets.py
python3 scripts/crop_numbers_sheet.py
python3 scripts/crop_celestial_kit_sheet.py
```

## Form kit — reuse vs create

| Primitive (form) | Status |
| --- | --- |
| Planet sphere (photo fills disc) | Reuse assets + `PlanetIcon fit="cover"` / natal SVG `slice` |
| Zodiac chip / orb | Reuse seals + neon orbs; size to band (not kit neon palette) |
| Angle badges ASC/DSC/MC/IC | Reuse kit crops |
| Number discs 1–9 | Reuse |
| Star / flare / nebula accents | Reuse `decorative/kit` |
| Glass card / surface ladder | Reuse `DsCard` glass + `DsGlassCard` / `DsSurface` |
| Pill buttons / chips | Reuse `DsButton`, `DsPill`, `DsChipGroup`, `DsTag` |
| List row (planet + text + chevron) | Compose from existing row patterns |
| Radial % ring | Partial — `DsRailWidgets` has progress ring; generalize if needed |
| Dot meter (n of 5) | Create thin primitive |
| Spectrum slider / window bar | Create (mood colors via day tokens) |
| Star-centered divider | Create (can use kit star asset) |
| Quote / highlight card | Partial — `DsQuote` / `DsQuoteTile`; align glass treatment |
| Tarot rounded tile | Reuse ritual card chrome; radius to match kit |
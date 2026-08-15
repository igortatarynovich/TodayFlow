# Celestial icon masters

- `numbers.png` → digit icons 1–9 → `frontend/public/images/icons/numbers/*.webp`
  (`python3 scripts/crop_numbers_sheet.py`)
- `zodiac-metal-glyphs-sheet.png` → 3D silver/gold glyphs (Today planet+sign) → `frontend/public/images/icons/zodiac/*.webp`
- `zodiac-glyphs-sheet.png` → legacy framed gold seals (fallback source)
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

## Form kit — closed SoT (FOUNDATION_UI §15.8)

Form from `ui-kit-form-sheet.png`; color from `--tf-*` / `--day-*`.

| Layer | Exports |
| --- | --- |
| Surface | `DsSurface` tones `none\|subtle\|solid\|glass\|accent` |
| Card shell | `DsCard` (pad/gap on tone; legacy `variant` → tone alias) |
| Primitives | `DsChip`, `DsFab`, `DsRadialMeter`, `DsDotMeter`, `DsSpectrum`, `DsMetric`, `DsStarDivider`, `DsAvatar`, `DsButton`… |
| Visual (only feature import path) | `DsPlanet`, `DsZodiac`, `DsNumber`, `DsTarotFace`, `DsAngle` |
| Compositions | `DsHeroBlock`, `DsWindowCard`, `DsMetricCard`, `DsActionCard`, `DsListRow` |

Gate: `scripts/check_ds_style_gate.py` + `scripts/ds_form_kit_zone_allowlist.json`.
Pilot: Today day brief (no local `TodayDayBrief.module.css`).

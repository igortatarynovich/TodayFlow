# Zodiac portrait illustrations

Painterly celestial portraits for large plates / hero art (`ZodiacIllustration`).

**Not** the gold seal icons in `../icons/zodiac/` — those power `ZodiacIcon` everywhere.

## Naming

```text
{slug}.webp   # lowercase latin: aries … pisces
```

Product files are **640×640** square WebP with knocked-out black sheet background (RGBA).

Re-slice anytime from the master sheet:

```bash
python3 scripts/crop_zodiac_illustrations.py
```

| Slug | RU |
|------|-----|
| `aries` | Овен |
| `taurus` | Телец |
| `gemini` | Близнецы |
| `cancer` | Рак |
| `leo` | Лев |
| `virgo` | Дева |
| `libra` | Весы |
| `scorpio` | Скорпион |
| `sagittarius` | Стрелец |
| `capricorn` | Козерог |
| `aquarius` | Водолей |
| `pisces` | Рыбы |

- Masters (RGBA PNG crops): `docs/design/assets/zodiac/`
- Source sheet: `docs/design/assets/image.png`
- Registry: `frontend/src/lib/visualIdentity/registry.ts` → `zodiacIllustrationSrc` / `zodiacIllustrationPath`
- UI helper: `ZodiacIllustration` (portrait + glyph fallback)

## Weight

Target ~100–140KB WebP per sign. Re-run the crop script after replacing the sheet.

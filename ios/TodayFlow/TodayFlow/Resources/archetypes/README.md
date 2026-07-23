# Archetype hero illustrations

Premium portrait art for Profile Recognition Hero (arch / circle frame).

**Not** the line-symbol SVGs in `../icons/archetypes/` — those stay for pills, masks, and small slots.

## Naming

```text
{slug}.webp   # lowercase latin slug (Pearson RU transliteration)
```

Product files are **4:5 hero crops** (820×1024) focused on face/bust for the arch.
Re-crop from masters anytime:

```bash
python3 scripts/crop_archetype_heroes.py
```

Focus points live in that script (`FOCI`). Masters may be re-dropped as full scenes; the crop step is required before ship.

| Slug | Pearson RU | Product seed |
|------|------------|--------------|
| `pravitel` | Правитель | architect |
| `tvorets` | Творец | creator |
| `mudrets` | Мудрец | sage |
| `geroi` | Герой | strategist |
| `buntar` | Бунтарь | catalyst |
| `liubovnik` | Любовник | harmonizer |
| `iskatel` | Искатель | seeker, explorer |
| `zabotlivyi` | Заботливый | guardian |
| `mag` | Маг | mentor |
| `nevinnyi` | Невинный | visionary |
| `slavnyi_malyi` | Славный малый | observer |
| `shut` | Шут | (direct slug / jester alias) |

Optional gendered lover variants: `liubovnik_f` · `liubovnik_m` (default seed uses `liubovnik`).

Registry SoT: `frontend/src/lib/visualIdentity/registry.ts` · iOS: `Resources/archetypes/` + `ArchetypeIllustration.swift`.

## Weight & size

```bash
python3 scripts/optimize_public_images.py frontend/public/images/archetypes
python3 scripts/crop_archetype_heroes.py
```

Target after crop: **820×1024 WebP**, typically **~55–110KB** (soft cap 350KB).

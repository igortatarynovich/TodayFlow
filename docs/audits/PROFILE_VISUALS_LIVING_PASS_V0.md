# Profile visuals — portrait seed fix + living atmosphere (v0)

**Date:** 2026-07-26  
**Status:** LIVE

## Problem

Profile felt “без картинок”: WebP assets were fine (`/images/archetypes/*.webp` → 200), but:

1. Legacy hero could pass CE/display titles into `ArchetypeHeroVisual` (no illustration resolve → symbol plate).
2. Journey surfaces skipped when only `identity_core` existed (no Why/Effort imagery path).
3. Forming gate treated `< 9` spheres as forming (CE ships 7).
4. Scene atmospheres at ~5–7% opacity were effectively invisible.
5. Effort spheres were text-only (accent dots).

## Fix

| Change | File |
|--------|------|
| Illustration seed = `baseline.archetype_seed` only | `ProfileV2SystemScreen` Legacy + Recognition |
| Journey opens on `identity_core` | `buildProfileJourneyProjection` |
| Forming: identity / CE applied / ≥3 spheres | `profilePortraitForming` |
| Atmosphere opacity ~0.14–0.18 | `profileAtmosphere.module.css` |
| Hero `MotionDrift` | Recognition + Legacy |
| Sphere planet/element motifs | `ProfileEffortScene` |
| iOS QuickMap art seed from baseline | `ProfileQuickMapView` |

## Inventory (reuse, not invent)

- Portraits: `/images/archetypes/*.webp`
- Icons: `/images/icons/{archetypes,zodiac,planets,elements}/*.svg`
- Cosmic washes: `/images/cosmic/*` · decorative: `/images/decorative/*`
- Motion kit: `MotionDrift` / `MotionSettle` / `MotionPulse` / ProfileMotion reveal

## Architecture impact

- **SoT before/after:** unchanged for copy. Visual seed remains `baseline.archetype_seed`; CE `recognition_label` is title-only.
- **Public contract changed?** no
- **Migration required?** no
- **Canon:** aligns with `TODAYFLOW_FOUNDATION_UI` §1 / §7 (Hero Large + Drift)

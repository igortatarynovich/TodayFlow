# Profile v1 — Block Freeze Matrix

**Stage:** [PROFILE_E2E_RECONSTRUCTION.md](../PROFILE_E2E_RECONSTRUCTION.md) § Profile v1 Freeze Checklist  
**Surface SoT:** `frontend/src/components/profile/v2/ProfileV2SystemScreen.tsx` (+ `ProfileV2SkySection`, `ProfilePortalDeepSection`, `ProfileChartSection`)  
**Block map (context):** [PROFILE_E2E_BLOCK_MAP.md](./PROFILE_E2E_BLOCK_MAP.md)  
**Date:** 2026-07-21  
**Rule:** только блоки, реально рисуемые в production Profile V2. Target-блоки из block map **не** в матрице.

> Status: `PASS` · `FAIL` · `MISSING`  
> Freeze columns: passport · capture (4 proofs) · Snapshot→API→UI · eligibility-before-LLM · checklist § blocked

---

## Production inventory (code)

| # | `block_id` | UI location | User-facing meaning | Calc / LLM |
|---|------------|-------------|---------------------|------------|
| 1 | `hero_chrome` | topMeta + hero eyebrow/title | «Личный профиль» · заголовок | static copy |
| 2 | `birth_data_cta` | topMeta button | открыть данные рождения | action |
| 3 | `portrait_forming` | forming banner | портрет ещё складывается | status |
| 4 | `hero_quote` | hero blockquote | суть «кто я» | LLM `identity_core` (+ archetype label) |
| 5 | `hero_pills` | hero pills | якоря (знаки / стихия) | calc |
| 6 | `evidence_aside` | hero aside | почему такой портрет · уровень наблюдения | client depth mirror |
| 7 | `identity_archetype` | Identity card | архетип | calc `baseline` / display |
| 8 | `identity_astro` | Identity card | солнце · луна (факты) | calc anchors |
| 9 | `character_strengthens` | Character | что усиливает | LLM `strengths` (+ FE mix risk) |
| 10 | `character_drains` | Character | что истощает | LLM `growth_zones` (+ FE mix risk) |
| 11 | `character_helps` | Character | что помогает | LLM `helps` (patterns step) |
| 12 | `character_decisions` | Character | как решаю | LLM `decision_style` (styles) |
| 13 | `character_patterns` | Character «что повторяется» | подтверждённые повторы | LLM `recurring_patterns` |
| 14 | `character_forming` | Character «как складывается» | сейчас = `living_changes` или taxonomy | LLM / taxonomy |
| 15 | `direction_mission` | Direction | направление | LLM `life_mission` (patterns) |
| 16 | `life_spheres` | Direction sphere cards | проявления в сферах | LLM synthesis (+ cues kitchen) |
| 17 | `evidence_zone` | Evidence section | то же обоснование + next step · CTA Maps | client + link |
| 18 | `sources_sky` | Sources · sky | натальные якоря / роли | calc + natal preview |
| 19 | `sources_portal` | Sources · deep portal | полная карта / numerology | calc natal API |

Nav-only (`ProfileV2MobileDepthJump` / depth rail) — не content-блоки Freeze.

---

## Block Freeze Matrix

| `block_id` | Passport | Capture 4 proofs | Snap→API→UI | Eligibility before LLM | Freeze §§ blocked | Overall | Notes |
|------------|----------|------------------|-------------|------------------------|-------------------|---------|-------|
| `hero_chrome` | MISSING | MISSING | PASS (static) | n/a | 1.1 · 5.1 | **FAIL** | Static; needs thin passport or fold into shell |
| `birth_data_cta` | MISSING | MISSING | PASS | n/a | 1.1 · 5.1 | **FAIL** | Action; Voice CTA value |
| `portrait_forming` | MISSING | partial Case A | PASS | n/a (no LLM) | 1.1 · 5.1 | **FAIL** | Must not fake ready quote |
| `hero_quote` | via `identity` | **PASS** Case A | **PASS** | via `identity` | — | **PASS** | Covered by `identity` unit |
| `hero_pills` | MISSING | MISSING | PASS | n/a | 1.1 | **FAIL** | Calc labels |
| `evidence_aside` | MISSING | FAIL depth Case B | FAIL (`PROJECTION`) | n/a | 1 · 2 · 4 · 5 | **FAIL** | depth under-count vs `source_depth` |
| `identity_archetype` | MISSING | MISSING | PASS | n/a | 1.1 | **FAIL** | Calc |
| `identity_astro` | MISSING | MISSING | PASS | n/a | 1.1 | **FAIL** | Calc |
| `character_strengthens` | via `identity` | **PASS** Case A | **PASS** contract-only | via `identity` | — | **PASS** | Covered by `identity` unit |
| `character_drains` | via `identity` | **PASS** Case A | **PASS** contract-only | via `identity` | — | **PASS** | same |
| `character_helps` | **APPROVED** | **PASS** A/B/C (shared packs) | **PASS** contract-only | **PASS** = patterns gate | — | **PASS** | [PROFILE_CAPTURE_CHARACTER_HELPS_FREEZE_ABC.md](./PROFILE_CAPTURE_CHARACTER_HELPS_FREEZE_ABC.md) |
| `character_decisions` | MISSING | partial A/B | partial | styles always-on | 1 · 3 | **FAIL** | styles passport TBD |
| `character_patterns` | **APPROVED** | **PASS** A/B/C Freeze packs | **PASS** | **PASS** living gate | — | **PASS** | [PROFILE_CAPTURE_CHARACTER_PATTERNS_FREEZE_ABC.md](./PROFILE_CAPTURE_CHARACTER_PATTERNS_FREEZE_ABC.md) |
| `character_forming` | MISSING | MISSING | FAIL purpose | — | 1 · 5 · `BLOCK_PURPOSE` | **FAIL** | Label «как складывается» ← `living_changes` |
| `direction_mission` | **APPROVED** | **PASS** A/B/C (shared packs) | **PASS** contract-only | **PASS** = patterns gate | — | **PASS** | [PROFILE_CAPTURE_DIRECTION_MISSION_FREEZE_ABC.md](./PROFILE_CAPTURE_DIRECTION_MISSION_FREEZE_ABC.md) |
| `life_spheres` | **APPROVED** | **PASS** A/B/C Freeze packs | **PASS** | **PASS** independent of patterns | — | **PASS** | [PROFILE_CAPTURE_LIFE_SPHERES_FREEZE_ABC.md](./PROFILE_CAPTURE_LIFE_SPHERES_FREEZE_ABC.md) |
| `evidence_zone` | MISSING | FAIL | FAIL | n/a | 1 · 4 · 5 | **FAIL** | Dup aside + Maps CTA |
| `sources_sky` | MISSING | MISSING | partial | n/a | 1.1 · 5 | **FAIL** | Calc / natal |
| `sources_portal` | MISSING | MISSING | partial | n/a | 1.1 · 6 | **FAIL** | Deep chart |

Legend: PASS only with proven 4 proofs. Remaining FAIL rows still block Profile v1 Freeze Checklist.

---

## Close order

| Done | Block | Notes |
|------|-------|-------|
| 1 | `identity` | hero_quote · strengthens · drains |
| 2 | `life_spheres` | love · money · decisions synthesis |
| 3 | `character_patterns` | birth vs longitudinal boundary |
| 4 | `character_helps` | same gate · contract-only UI |
| 5 | `direction_mission` | same gate · contract-only Direction |
| *paused* | `character_decisions` | **PAUSED** — journey SoT first: [PROFILE_PRODUCT_SURFACE_CANON.md](../PROFILE_PRODUCT_SURFACE_CANON.md) |

Do not start next Freeze block until Product Surface Canon §5 DoD (Steps 1–2 human metrics). Freeze PASS ≠ «меня поняли / понятно почему».

---

## Active close log

| Date | Block | Action | Result |
|------|-------|--------|--------|
| 2026-07-21 | `identity` | Passport · gate · profile voice · FE contract-only · Case A 4 proofs | **PASS** — [PROFILE_CAPTURE_IDENTITY_FREEZE_A.md](./PROFILE_CAPTURE_IDENTITY_FREEZE_A.md) |
| 2026-07-21 | `life_spheres` | Canonical passport · A/B/C captures · FE visible spheres · day/kitchen bans | **PASS** — [PROFILE_CAPTURE_LIFE_SPHERES_FREEZE_ABC.md](./PROFILE_CAPTURE_LIFE_SPHERES_FREEZE_ABC.md) |
| 2026-07-21 | `character_patterns` | Living gate · prompt · FE contract-only · A/B/C proofs | **PASS** — [PROFILE_CAPTURE_CHARACTER_PATTERNS_FREEZE_ABC.md](./PROFILE_CAPTURE_CHARACTER_PATTERNS_FREEZE_ABC.md) |
| 2026-07-21 | `character_helps` | Shared patterns gate · FE contract-only · A/B/C proofs | **PASS** — [PROFILE_CAPTURE_CHARACTER_HELPS_FREEZE_ABC.md](./PROFILE_CAPTURE_CHARACTER_HELPS_FREEZE_ABC.md) |
| 2026-07-21 | `direction_mission` | Shared patterns gate · FE contract-only · A/B/C proofs | **PASS** — [PROFILE_CAPTURE_DIRECTION_MISSION_FREEZE_ABC.md](./PROFILE_CAPTURE_DIRECTION_MISSION_FREEZE_ABC.md) |
| *paused* | `character_decisions` | Paused for journey Steps 1–2 (узнал себя · понял почему) | — |

### Generation / content units

| `block_id` | Overall |
|------------|---------|
| **`identity`** | **PASS** |
| **`life_spheres`** | **PASS** |
| **`character_patterns`** | **PASS** |
| **`character_helps`** | **PASS** |
| **`direction_mission`** | **PASS** |

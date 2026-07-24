# Profile · Foundation QA (production Quick Map)

**Дата:** 2026-07-03  
**Статус:** **code-side pass** · manual shape scroll — optional  
**Prod route:** `/profile` → `ProfileWebScreen` + `ProfileQuickMapScreen` (`WEB_LAUNCH_MIN_PROFILE`) · legacy `?view=v0` → `ProfileV0Screen`  
**Источники:** [TODAYFLOW_FOUNDATION_UI.md](../TODAYFLOW_FOUNDATION_UI.md) §9 · [PROFILE_SCREEN_MASTER.md](../profile/PROFILE_SCREEN_MASTER.md) §10

---

## Foundation §9 vs Quick Map

| Foundation | Quick Map код | Статус |
|------------|---------------|--------|
| Hero Large §1.1 | `HeroLarge` · 120px symbol · profile geometry · fade | **done** |
| Surfaces B/C | `SurfaceInsight` panels · resume grid · framework cards | **done** |
| Surface D Portal | `ProfilePortalDeepSection` · portal geometry + dark tone | **done** |
| Motion DS-4 | `ProfileMotionStagger` on portrait stack | **done** |
| Symbols | Archetype 12/12 · Zodiac/Planet/Element in framework & chart | **done** |
| Typography | `--tf-type-*` on shell · `--orbit-text-*` aliased globally | **done** |
| Colors | `--tf-page` · `--tf-ink` · insight surfaces | **done** |

**Figma v0 (2026-07-03):** [TODAYFLOW_FOUNDATION_UI](https://www.figma.com/design/pWdevqQqOi6wvoVc6hFWHa) — Cover + §8 pages + `TF /` variables. **Open:** formal «дорого/нет» on Cover · Hero size annotations polish · swap symbol placeholders → exported SVGs.

---

## PROFILE_SCREEN_MASTER · prod mapping

| Master layer | Quick Map component | Foundation entity |
|--------------|---------------------|-------------------|
| Hero Scene | `HeroLarge` | Surface A |
| Portrait insights | strengthen/drain/decision/perceived/thrive/mission | Surface B |
| Framework | anchors + cards | Surface B |
| Life spheres | `ProfileLifeSection` | Surface B (love/money variants) |
| Living Maps | `ProfileLivingMapsSection` | Maps preview |
| Portal | `ProfilePortalDeepSection` + chart | Surface D |
| v0-only layers | `?view=v0` only (Why · Numbers · Compass…) | Phase 2 v0 |

**Note:** Master §8 implementation map описывает **v0**; production IA = Quick Map (PM-1). v0 остаётся для depth QA и taxonomy audit.

---

## Manual QA hooks

| Test | How |
|------|-----|
| **§10 #2 · shapes only** | `NEXT_PUBLIC_PROFILE_SHAPE_AUDIT=1` → Quick Map или v0 (`.pageShapeAudit`) |
| **§10 #1 · scroll anchors** | Hero symbol → panels → maps → portal slit → Today CTA |
| Automated | `ProfileQuickMapScreen.test.tsx` · `HeroLarge.test.tsx` · `ProfileLifeSection` integration |

---

## Gaps (not blocking Foundation code sign-off)

| Gap | Owner |
|-----|--------|
| v0 Phase 2 visual entities (Monument · Duality · Compass) | Profile v0 pass |
| Insight taxonomy / origin vs application mix | [PROFILE_V0_CONTENT_INSIGHT_AUDIT.md](./PROFILE_V0_CONTENT_INSIGHT_AUDIT.md) |
| iOS Quick Map full parity | [IOS_TODAYFLOW_STATUS.md](./IOS_TODAYFLOW_STATUS.md) |
| Figma formal Foundation sign-off | Design |

---

## Verdict

**Foundation code sign-off:** ✅ для production Profile Quick Map.  
**Next product track:** Today Screen Master (unblocked после Figma или parallel web slice).

---

## Figma build runbook (TODAYFLOW_FOUNDATION_UI)

**Status (2026-07-03 PM):** **v0 BUILT** — [file](https://www.figma.com/design/pWdevqQqOi6wvoVc6hFWHa) · MCP `plugin-figma-figma`. **Next:** design review Cover · import real symbol SVGs · annotate Hero frames.

### Step 0 · create file

```
/figma-create-new-file design TODAYFLOW_FOUNDATION_UI
```

→ `file_key` + `file_url` in drafts.

### Step 1 · pages (§8 canon)

| Page | Content |
|------|---------|
| **Cover** | Textless premium composition — Hero L + Surface B + Portal slit (shapes only, no lorem) |
| **01 Hero** | 390× frames: Large (88dvh ref ~680px) · Medium (52dvh) · Small (200px) — annotated symbol 120/80/48 |
| **02 Symbols** | 4×3 grids: Archetype 12 · Zodiac 12 · Element 4 · Planet 10 |
| **03 Geometry** | G1–G5 primitives + Profile / Today / Portal compositions |
| **04 Surfaces** | A Hero · B Insight 28px · C Action bar · D Portal 232px · N Number — **textless** |
| **05 Typography** | Display 40 · Hero 33 · Section 20 · Body 15 · Caption 10–11 |
| **06 Colors** | 12 swatches from `todayflow-foundation.css` §6 |
| **07 Reference** | Profile Quick Map wireframe — shapes only |

### Step 2 · variables (from code)

| Token | Hex / value |
|-------|-------------|
| `--tf-page` | `#f3efe8` |
| `--tf-page-cream` | `#fff9f5` |
| `--tf-ink` | `#1a1510` |
| `--tf-ink-soft` | `#5b4630` |
| `--tf-body` | `#475569` |
| `--tf-caption` | `#9a8468` |
| `--tf-accent-numerology` | `#4a3270` |
| `--tf-accent-action` | `#8f6b3a` |
| `--tf-on-dark` | `#faf8f5` |

Typography: Playfair Display (display/hero/section) · Inter (body/caption).

### Step 3 · sign-off gates

- [ ] Cover passes «дорого/нет» without text
- [ ] Hero L/M/S labeled on **390** frame
- [ ] Surfaces A–D textless mocks match code radii/shadows

**Skills order:** `figma-generate-library` (tokens) → `figma-generate-design` (screens) → `figma-use` (incremental edits).

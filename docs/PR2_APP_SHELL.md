# PR-2: Production App Shell

**Status:** **ACCEPTED / CLOSED** (2026-07-21)  
**Canon:** [TODAYFLOW_FOUNDATION_UI.md](./TODAYFLOW_FOUNDATION_UI.md) · [PRODUCT_TRUTH_FIRST.md](./PRODUCT_TRUTH_FIRST.md) · [EXPLAINABLE_COMPUTATION_AND_INTERPRETATION.md](explainability/EXPLAINABLE_COMPUTATION_AND_INTERPRETATION.md)  
**Code base:** `ProductWebShellLayout` → `ProductWebAppShell` → `DsAppShell`  
**Tracker:** Product Page Standard v1 → PR-2 shell honesty  

> Shell answers for structure only. It does not invent product blocks, recommendations, percentages, or decorative rails.  
> **После CLOSED:** к App Shell возвращаемся только за багфиксами. Следующая крупная работа — [PR-3 Today Production Surface](./archive/PR3_TODAY_PRODUCTION_SURFACE.md) (сначала `day_story_v1` explainable-контракт, не Figma).

---

## 0. Закрытый класс UI-проблем (канон)

После PR-2 **запрещено** (нарушение канона, не «стиль»):

1. Резервировать место под отсутствующий rail (empty column for symmetry).
2. Использовать title/subtitle как содержимое rail.
3. Создавать filler-панели ради композиции.
4. Делать отдельный loading-layout вне App Shell для in-app страниц.
5. Проектировать разные shell для разных разделов.
6. Использовать декоративные helper-панели без источника данных.

**Архитектурный итог:** rail — элемент **данных**, не композиции. Loading / Empty / Error — часть shell/page standard. Profile — **структурный** эталон (не redesign смысла). Today content не входил в scope PR-2.

---

## 1. Shell contract

```
App Shell
├── Sidebar (desktop) / Mobile tab bar
├── Optional page header (screen-owned title/actions)
├── Main content
└── Context rail — only when real content exists
```

| Concern | Rule |
|---------|------|
| Width | Main uses DS gutters / `mainWide`. Foundation `--tf-*` inside content. No phone-width column on desktop. |
| Nav | One `appNavConfig` for sidebar + mobile tabs |
| Header | Page-level only; global orbit Header hidden on product chrome |
| Rail appear when | Active session · action context · saved state · continuation · contract-backed extra info |
| Rail absent | `rail={null\|undefined}` → single-track main (no reserved empty column) |
| States | Shared loading / empty / partial / error in main; shell never fakes ready |
| Auth / onboarding | Outside AppShell (`/`, `/auth*`, `/onboarding*`) |
| Theme toggle | Removed until a real control exists |

### Config API (`ProductWebShellConfig`)

- `rail?: ReactNode` — truthy only with a block passport; otherwise omit
- `fullMain` — only when the page draws its own columns **and** does not use shell rail
- **Forbidden:** fallback `DsRailPanel(title/subtitle)` echo

### Block passport (required to migrate)

| Field | Question |
|-------|----------|
| Block | Name |
| Route | Path |
| Component | React entry |
| Source | Endpoint or local trusted store |
| Contract fields | Response / model fields |
| Appear when | Condition |
| Loading / Ready / Empty / Partial / Error | UI per state |
| Primary action | What the user can do |
| No-data | Honest empty / hide |
| Foundation surface | A / B / C / D / N or none |

No source or appear-when → block stays in **Violations**, not auto-migrated.

---

## 2. Route map (from code)

| Route | Screen | Layout / shell | Sources (short) | Rail policy |
|-------|--------|----------------|-----------------|-------------|
| `/today` | Composition default; ritual `?full=1` | AppShell + `TodayWebDashboard` | `/today/*`, contract, narrative | Rail only with real streak/timeline/practice data — no synthetic weekly wave |
| `/profile` | `ProfileV2SystemScreen` | AppShell + `ProfileWebScreen` | core-profile, CUM, natal, morning-ritual | Anchors only if `railAnchors.length > 0`; else no rail |
| `/tarot` hub | `TarotHubMain` | AppShell + `TarotShell` | local session | `null` (step `-1`) |
| `/tarot/question\|spread\|result` | funnel | + `TarotRail` | draw / context APIs | Stepper only; day-tags only if passed |
| `/practices` | `PracticesV2SystemScreen` | AppShell + `PracticesWebScreen` | `/practices*` | Progress rail only when real progress/streak |
| Natal | `/profile?section=chart` | inside Profile | `GET /natal-chart/` | same as Profile |
| Numerology tools | no hub | AppShell + `ProductPageScreen` | `POST /numerology/*` | no filler rail |
| `/compatibility` | `CompatibilityWebHub` | AppShell + `CompatibilityWebScreen` | astro-data, compare | Local history only; no decorative how-to/quote |
| History | `/journal`, `/practices/history`, `/tracking/*` | AppShell + page wrappers | journal / practices / tracking | no title-echo rail |
| `/account/settings` | settings | AppShell + `ProductPageScreen` | profile, auth | no filler rail |
| Onboarding | value-first / core | **no** AppShell | guest draft, core-setup | — |
| Auth | `AuthWebScreen` | chrome without sidebar | login / magic / reset | — |

**Primary nav (real):** Today · Profile · Compatibility · Tarot · Practices — `frontend/src/lib/appNavConfig.ts`  
**Sidebar footer:** Settings → `/account/settings` (real)

---

## 3. Violations registry

| ID | Where | Issue | PR-2 disposition |
|----|-------|-------|------------------|
| V1 | `ProductPageScreen` | Rail always = title/subtitle echo | **Fixed** — rail optional |
| V2 | `dsLayouts` desktop grid | Empty column reserved for symmetry | **Fixed** — 2-track only when rail present |
| V3 | `ProfileWebScreen` | Empty anchors → subtitle hint; Compat link as filler | **Fixed** — anchors-only rail |
| V4 | Today weekly rail | Synthetic wave bars | **Fixed** in rail-honesty pass — omit synthetic weekly |
| V5 | Today contract | Fallback contract without UI mark | Deferred (content / PR-3); do not invent UI here |
| V6 | Practices POD | `catalog_fallback` in hero slot | Keep label honesty; no new POD invent; rail separate |
| V7 | Compatibility rail | Decorative how-to + quote | **Fixed** — history-only rail |
| V8 | Theme toggle | Decorative empty control | **Fixed** — removed |
| V9 | Loading Today/Profile | Outside AppShell chrome jump | Profile loading/guest in AppShell; Today loading in shell when wrapped |
| V10 | Dual `.tf-shell` meaning | Foundation 52rem vs product full-bleed | Documented; product chrome overrides under `data-product-web-shell` |

---

## 4. Nav / rail action registry

### Sidebar + mobile tabs

| ID | Href | Real? |
|----|------|-------|
| today | `/today` | yes |
| profile | `/profile` | yes |
| compatibility | `/compatibility` | yes |
| tarot | `/tarot` | yes |
| practices | `/practices` | yes |
| settings (footer) | `/account/settings` | yes |

### Rail sources (allowed)

| Screen | Allowed rail content | Forbidden |
|--------|----------------------|-----------|
| Tarot funnel | Stepper from path | Invented day tags without props |
| Profile | Map anchors from built model | Subtitle echo, “опоры”, fake links-only column |
| Practices | Streak / weekly from `/practices/progress` | Open-day filler bars as personal rhythm without data |
| Compatibility | Local pair history (`readRelationshipMapCircles`) | How-to list, quote filler |
| Today | Real timeline / practice / streak from API | Synthetic weekly wave, generic Utro/Den/Vecher as “personal” without sky data |

---

## 5. Profile reference passports (confirmed only)

### P1 · Profile V2 system screen

| Field | Value |
|-------|-------|
| Block | Profile quick map / V2 |
| Route | `/profile` |
| Component | `ProfileV2SystemScreen` via `ProfileWebScreen` |
| Source | `GET /account/core-profile`, CUM, natal preview, morning-ritual |
| Appear when | Authenticated + `WEB_LAUNCH_MIN_PROFILE` + setup complete enough for V2 |
| Loading | AppShell + center spinner |
| Ready | V2 zones |
| Empty / setup | Setup section / notices + CTA |
| Partial | Missing gender / incomplete notices; CUM optional |
| Error | Preview error + reload |
| Primary action | Setup, expand chart, links to Today / settings |
| No-data | EmptyState / omit cards without symbols |
| Foundation surface | Product V2 canvas (Hero Large retrofit out of scope) |

### P2 · Profile rail anchors

| Field | Value |
|-------|-------|
| Block | Context rail — map anchors |
| Route | `/profile` |
| Component | `ProfileWebScreen` rail |
| Source | `railAnchors` from page builders (core profile / V2 live context) |
| Appear when | `railAnchors.length > 0` |
| No-data | **No rail column** |
| Foundation surface | none (chrome) |

### P3 · Guest profile gate

| Field | Value |
|-------|-------|
| Block | Guest gate |
| Route | `/profile` |
| Component | `ProductPageScreen` guest or Profile guest path |
| Source | auth session |
| Appear when | unauthenticated |
| Primary action | Login / create |
| No-data | Gate message + CTA |

### P4 · Natal deep (inside Profile)

| Field | Value |
|-------|-------|
| Block | Sky / natal chart |
| Route | `/profile?section=chart` |
| Component | `ProfileV2SkySection` / chart sections |
| Source | `GET /natal-chart/?include_interpretations=true` |
| Appear when | Authed + chart section / expand |
| Error | previewError + reload |
| No-data | Setup CTA if incomplete; ASC honesty for unknown time |

---

## 6. Implementation notes

- Prefer existing `ProductWebAppShell`; do not create per-screen shells.
- After hub migration, remove local wrappers that only duplicated shell config.
- PR-3 owns Today content / DailyState — not this document’s shell work.

---

## 7. Definition of done

- [x] This map + contract + Profile passports
- [x] No reserved empty rail track
- [x] No ProductPageScreen / Profile filler rail
- [x] Theme toggle removed
- [x] Profile structural honesty
- [x] Tarot hub rail-off; funnel stepper preserved
- [x] Hub rail honesty (Practices, Compatibility, Today) — see code
- [x] Secondary `ProductPageScreen` consumers inherit optional rail

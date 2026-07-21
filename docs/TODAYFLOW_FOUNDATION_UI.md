# TODAYFLOW_FOUNDATION_UI

**Статус:** **ACTIVE** — канон визуала **всего сервиса** (web · iOS · Android).  
**Версия:** 0.2 (2026-06-02).  
**Владелец:** Design + Product.

**Figma-файл:** [TODAYFLOW_FOUNDATION_UI](https://www.figma.com/design/pWdevqQqOi6wvoVc6hFWHa) · `file_key` `pWdevqQqOi6wvoVc6hFWHa` *(Cover v1 — living portal + orbit; design iteration, не sign-off)*.

**Главный тест Profile (и всего продукта):**

> Убрать весь текст. Осталась только композиция. **Выглядит ли дорого?**  
> Пока **нет** → не открываем Today · не CD · не Love · не новые docs.

**Код:** `frontend/src/styles/todayflow-foundation.css` — подключён в `globals.css` · классы `.tf-shell` / `.tf-shell-grid-2`.

**Экран Profile:** [PROFILE_SCREEN_MASTER.md](./PROFILE_SCREEN_MASTER.md) — **заморожен** до sign-off §8 здесь.

---

## 0. Что это / чего это не

| Это | Не это |
|-----|--------|
| Визуальные **примитивы** продукта | Design system компонентов (Button, Input…) |
| Поверхности · герои · символы · геометрия | [PROFILE_SCREEN_MASTER.md](./PROFILE_SCREEN_MASTER.md) · [TODAYFLOW_FOUNDATION_UI.md](./TODAYFLOW_FOUNDATION_UI.md) §2 Symbols |
| Один Figma-источник правды | Moodboard 100 UI · «TodayFlow is…» |

**Порядок:** Foundation UI (Figma) → Profile снова → Today.

**Product Truth First:** визуал не опережает продукт. Нет backend-источника / нет реальных данных — нет заполненного production-блока. Канон: [PRODUCT_TRUTH_FIRST.md](./PRODUCT_TRUTH_FIRST.md).

---

## 1. Hero System

Три **фиксированных** шаблона. Любой экран использует **один** из них — не собирает Hero с нуля.

### 1.1 Hero Large *(Profile — эталон)*

| Параметр | Значение |
|----------|----------|
| Canvas | 390 × **min(88dvh, 720px)** |
| Content max-width | **336px** |
| Padding | 56 top · 24 sides · 64 bottom |
| Bottom radius | **36px** |
| Fade | 45% height · transparent → `--tf-page` |

| Элемент | Size | Weight / font role |
|---------|------|-------------------|
| Archetype symbol | **120 × 120** | stroke 1.5px · `--tf-ink-soft` |
| Name | **33px** | Hero · 700 |
| Pillar gap | **24–32px** | — |
| Zodiac icon | **24px** | Symbol |
| Life Path digit | **32px** | 800 · `--tf-accent-numerology` |
| Archetype caps | **12px** | Caption · tracking 0.16em |
| Pillar label | **10px** | Caption |
| Digest *(optional)* | **15px** | Body · max 2 lines |

**Figma frame:** `Hero / Large / Profile`.

### 1.2 Hero Medium *(Today theme · Calendar month)*

| Параметр | Значение |
|----------|----------|
| Height | **min(52dvh, 420px)** |
| Symbol | **80 × 80** |
| Name / Title | **26px** · Hero |
| Subline | **15px** · Body · 1 line |
| Pillars | **optional** · icon 20px |

**Figma frame:** `Hero / Medium / Today-Theme`.

### 1.3 Hero Small *(секция · Compatibility header)*

| Параметр | Значение |
|----------|----------|
| Height | **200px** fixed |
| Symbol | **48 × 48** |
| Title | **20px** · Section |
| Meta row | **11px** · Caption |

**Figma frame:** `Hero / Small / Section`.

### 1.4 Hero — запрещено

Случайные высоты · 4-й размер «на глаз» · текст > 40% площади · S/W chips в Large.

---

## 2. Symbol System

**Закрытый список.** Только эти семейства — **никаких** случайных иконок (lucide, emoji, stock).

| Family | Count | Use | Asset |
|--------|-------|-----|-------|
| **Archetype** | 12–16 seeds | Hero Large primary | `ArchetypeSymbol` SVG |
| **Zodiac** | 12 | Pillars · Deep Dive | `ZodiacIcon` |
| **Element** | 4 | Atmosphere bg · chips | `ElementAtmosphere` |
| **Planet** | 10 | Deep Dive · Today transit | `PlanetIcon` SVG set |
| **Life Path** | 1–9 (+ master 11/22/33) | Digit typography, not icon | **type** only |
| **Tarot** | 78 | Tarot screen only | отдельный пул · **не** в Profile Hero |

**Размеры symbol slot:**

| Slot | px |
|------|-----|
| XL | 120 |
| L | 80 |
| M | 48 |
| S | 24 |

**Stroke:** 1.25px (S) · 1.5px (M–XL) · color `--tf-ink-soft` / on-dark `--tf-on-dark`.

**Figma pages:** `Symbols / Archetype` · `Zodiac` · `Element` · `Planet` · grid 4×3 each.

**Код:** `frontend/src/lib/visualIdentity/registry.ts` — единый реестр id → component.

---

## 3. Geometry System

Продуктовый слой **под** символами — один стиль на Profile, Today, Compat, Deep Dive, Tarot.

### 3.1 Primitives *(нарисовать в Figma)*

| ID | Описание | Spec |
|----|----------|------|
| **G1 Circle** | мягкое кольцо | stroke 1px · opacity 0.12–0.2 |
| **G2 Orbit** | 1–3 эллиптические дуги | stroke 1px · dash optional |
| **G3 Grid** | 20×20 или 24×24 | line 1px · opacity 0.04 |
| **G4 Connector** | линия узел–узел | 1–2px · 45°/90° only |
| **G5 Radial fade** | vignette | как Profile hero fade |

### 3.2 Emphasis levels

| Level | Opacity | Use |
|-------|---------|-----|
| `soft` | 0.06–0.10 | Hero Large bg |
| `medium` | 0.12–0.18 | Insight cards |
| `strong` | 0.22–0.30 | Portal only |

### 3.3 Placement rules

- Geometry **никогда** не конкурирует с symbol XL.
- Max **1** strong layer на экран.
- Deep Dive: grid + orbits · Today: orbit only · Profile Hero: soft sacred.

**Figma page:** `Geometry / Primitives` + 3 composed examples (Profile / Today / Portal).

**Код:** `SacredGeometryBackdrop` + `FoundationGeometryLayers` — `emphasis` + optional `preset` (`profile` | `today` | `portal`) + `tone` для Surface D. Figma art — замена SVG-слоёв без смены API.

**Code (2026-07-03):** G1–G5 в `foundation/geometry/` · Hero L/S → `profile` · Hero M → `today` · Portal → `portal` + `tone="dark"` · iOS `FoundationGeometryView.swift`.

---

## 4. Surface System

**Поверхности**, не React-компоненты.

### Surface A · Hero

| Token | Value |
|-------|-------|
| Background | element atmosphere OR `--tf-page-hero` gradient |
| Border | none |
| Shadow | none |
| Radius | bottom **36px** only |
| Text on surface | `--tf-on-hero` |

### Surface B · Insight

| Token | Value |
|-------|-------|
| Background | `rgba(255,253,249,0.88)` |
| Radius | **28px** |
| Shadow | `0 14px 48px rgba(91,67,35,0.06)` |
| Padding | 22 × 21 |
| Variants | `insight-neutral` · `insight-love` *(soft blush)* · `insight-money` *(grid)* |

### Surface C · Action

| Token | Value |
|-------|-------|
| Background | transparent |
| Accent | **3px** left bar `--tf-accent-action` |
| Radius | 0 |
| Shadow | none |

### Surface D · Portal

| Token | Value |
|-------|-------|
| Background | gradient `#12101c → #0f1419` |
| Min-height | **232px** |
| Radius | **24px** |
| Shadow | `0 24px 64px rgba(15,12,24,0.35)` |
| Geometry | **strong** |
| Text | `--tf-on-dark` |

### Surface N · Number Object *(Profile only)*

| Token | Value |
|-------|-------|
| Background | gradient light violet → cream |
| Radius | **32px** |
| Ring | 120px diameter |
| Shadow | elevated · single per screen |

**Figma page:** `Surfaces / A–D + N` — swatches + 390px mock **без текста** (lorem запрещён — только формы).

---

## 5. Typography Hierarchy

**Пять ролей** — жёсткие px на 390 viewport. Один шрифт display, один body.

| Role | Font | Size | Line | Weight | Use |
|------|------|------|------|--------|-----|
| **Display** | Playfair Display | **40px** | 1.15 | 600 | marketing · empty states |
| **Hero** | Playfair Display | **33px** | 1.08 | 700 | Hero Large name |
| **Section** | Playfair Display | **20px** | 1.2 | 600 | card titles · Portal title 26px* |
| **Body** | Inter | **15px** | 1.55 | 400 | digest · insight values |
| **Caption** | Inter | **10–11px** | 1.35 | 600 | labels · pillars · caps |

*Portal title = Section + 6px (26px) — исключение, зафиксировать одним токеном `--tf-type-portal-title`.*

**Запрещено:** всё Body 15px · три serif на одном экране · Inter для Hero name.

**Figma page:** `Typography / Scale` — specimen RU + EN.

**Свести с кодом:** `--orbit-text-*` → aliases на `--tf-type-*` в `globals.css` (DS-10); новый код — только `--tf-type-*`.

---

## 6. Colors

**Минимальный набор** — не расширять до 40 swatches.

| Token | Hex | Role |
|-------|-----|------|
| `--tf-page` | `#f3efe8` | Profile page *(warm parchment)* |
| `--tf-page-cream` | `#fff9f5` | Today default |
| `--tf-ink` | `#1a1510` | primary text |
| `--tf-ink-soft` | `#5b4630` | symbols |
| `--tf-body` | `#475569` | secondary text |
| `--tf-caption` | `#9a8468` | labels |
| `--tf-accent-numerology` | `#4a3270` | LP digit |
| `--tf-accent-action` | `#8f6b3a` | Action bar |
| `--tf-on-dark` | `#faf8f5` | Portal |
| `--tf-insight-love-bg` | blush gradient | Surface B variant |
| `--tf-insight-money-grid` | `#6b5344` @ 4% | Surface B variant |

**Figma page:** `Colors / Core` — 10 chips + on-surface pairs.

---

## 7. Layout shell *(весь продукт)*

**Ошибка:** узкая «колонка телефона» на ноутбуке. **Правило:** mobile-first ≠ phone-width на desktop.

| Token | Значение | Смысл |
|-------|----------|--------|
| `--tf-shell-max` | **52rem (832px)** | ширина product column на **всех** устройствах |
| `--tf-shell-gutter` | `clamp(1.25rem, 4vw, 2rem)` | боковые поля |
| `--tf-shell-gap` | `clamp(2rem, 5vw, 2.75rem)` | между секциями |
| `--tf-shell-readable` | **36rem** | длинный текст внутри shell |
| `--tf-breakpoint-lg` | **56.25rem (900px)** | 2 колонки (Numbers+Name · Love+Money) |

| Viewport | Поведение |
|----------|-----------|
| **&lt; 900px** | одна колонка · full width в gutter |
| **≥ 900px** | shell до 832px по центру · 2-col bands где уместно |
| **Native** | те же токены в Swift/Kotlin · не отдельный «десктоп-дизайн» |

**Запрещено:** `max-width: 26rem` на product screens · случайные `820px` / `760px` в компонентах.

**Продукт ведёт пользователя:** секция = вопрос → визуальный якорь → **полный** ответ → CTA раскрытия. Не список label+число без meaning.

---

## 8. Figma file structure

```
TODAYFLOW_FOUNDATION_UI
├── Cover (test: composition without text)
├── 01 Hero (Large / Medium / Small)
├── 02 Symbols (Archetype · Zodiac · Element · Planet)
├── 03 Geometry (G1–G5 · 3 compositions)
├── 04 Surfaces (A · B · C · D · N — textless mocks)
├── 05 Typography
├── 06 Colors
└── 07 Reference · Profile wireframe (no copy, shapes only)
```

---

## 9. Sign-off checklist

**Code implementation (2026-07-03):** DS-2 HeroLarge · DS-3 surfaces · DS-4 motion · DS-1 lite archetype SVG · `--tf-*` tokens in `todayflow-foundation.css`. **Figma v0 (2026-07-03):** [file](https://www.figma.com/design/pWdevqQqOi6wvoVc6hFWHa) — Cover · Hero · Symbols · Geometry · Surfaces · Typography · Colors · Platforms; variables `TF / *`.

- [x] Hero L/M/S — frames on **390** (`01 Hero`: Large 680 · Medium 420 · Small 200; symbols 120/80/48) *(size annotations — polish pass)*
- [x] Hero L — code §1.1 (`88dvh`, 120px symbol, 36px radius, fade 45%) — `HeroLarge.tsx` + iOS
- [x] Hero M — code §1.2 + Today day-anchor (`HeroMedium.tsx` + iOS `HeroMediumView`)
- [x] Hero S — code §1.3 + Compatibility headers (`HeroSmall.tsx` · hub · exploration · dynamics · iOS `HeroSmallView`)
- [x] Symbol grid — Planet 10/10 · Zodiac 12/12 · Element 4/4 · Archetype 12/12 SVG *(+ unknown fallback; Tarot отдельно)*
- [x] Geometry — 5 primitives + 3 примера композиции (`FoundationGeometryLayers` · profile / today / portal)
- [x] Surfaces A–D — Profile Quick Map on `ProfileSurface` / `SurfaceInsight` / portal *(textless premium test — manual)*
- [x] Typography — `--tf-type-*` roles in foundation CSS · legacy `--orbit-text-*` aliased in `globals.css` (DS-10)
- [x] Colors — ≤12 core tokens in `todayflow-foundation.css`
- [ ] Profile «без текста» frame — **pass** дорого/нет *(Cover v1: `Cover / TodayFlow — Living Portal` — portal + 10 systems + convergence; **design review**, не gate)*

**Code sign-off (2026-07-03):** all checklist items except Figma frames — see [status/PROFILE_FOUNDATION_QA.md](./status/PROFILE_FOUNDATION_QA.md).

**После ✓:** обновить `todayflow-foundation.css` · рефактор `profileV0.module.css` на `--tf-*` · QA [PROFILE_SCREEN_MASTER.md](./PROFILE_SCREEN_MASTER.md).

---

## 10. Explicitly paused

| | |
|---|---|
| Today Screen Master | **unblocked (code)** — Figma Foundation frames still open · см. [TODAY_CANON_VS_CODE_DIFF.md](./status/TODAY_CANON_VS_CODE_DIFF.md) |
| Love / Money / CD / data | |
| Новые product docs | |
| Profile feature code | только hotfix · не новые карточки |

---

*Сначала Figma foundation. Потом Profile снова проходит тест «без текста».*

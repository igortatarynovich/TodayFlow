# TODAYFLOW_FOUNDATION_UI

**Статус:** **ACTIVE** — канон визуала **всего сервиса** (web · iOS · Android).  
**Версия:** 0.3 (2026-08-03).  
**Владелец:** Design + Product.

**Figma-файл:** [TODAYFLOW_FOUNDATION_UI](https://www.figma.com/design/pWdevqQqOi6wvoVc6hFWHa) · `file_key` `pWdevqQqOi6wvoVc6hFWHa` *(Cover v1 — living portal + orbit; design iteration, не sign-off; Figma не используется как обязательный источник правды — см. §11.7)*.

**Главный тест Profile (и всего продукта):**

> Убрать весь текст. Осталась только композиция. **Выглядит ли дорого?**  
> Пока **нет** → не открываем Today · не CD · не Love · не новые docs.

**Код:** `frontend/src/styles/todayflow-foundation.css` — подключён в `globals.css` · классы `.tf-shell` / `.tf-shell-grid-2`.

**Экран Profile:** [PROFILE_SCREEN_MASTER.md](profile/PROFILE_SCREEN_MASTER.md) — **заморожен** до sign-off §9 здесь.

---

## 0. Что это / чего это не

| Это | Не это |
|-----|--------|
| Визуальные **примитивы** продукта | Design system компонентов (Button, Input…) |
| Поверхности · герои · символы · геометрия | [PROFILE_SCREEN_MASTER.md](profile/PROFILE_SCREEN_MASTER.md) · §2 Symbols |
| Один Figma-источник правды *(исторически; см. §8, §11.7)* | Moodboard 100 UI · «TodayFlow is…» |

**Порядок:** Foundation UI (канон + код) → Profile снова → Today. Figma не в рабочем контуре (§11.7).

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

*Figma не участвует в разработке (см. §11.7) — раздел сохранён как исторический артефакт первой итерации канона, не как рабочий процесс.*

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

**После ✓:** обновить `todayflow-foundation.css` · рефактор `profileV0.module.css` на `--tf-*` · QA [PROFILE_SCREEN_MASTER.md](profile/PROFILE_SCREEN_MASTER.md).

---

## 10. Explicitly paused

| | |
|---|---|
| Today Screen Master | **unblocked (code)** — Figma Foundation frames still open · см. [TODAY_CANON_VS_CODE_DIFF.md](./status/TODAY_CANON_VS_CODE_DIFF.md) |
| Love / Money / CD / data | |
| Новые product docs | |
| Profile feature code | только hotfix · не новые карточки |

---

## 11. Day Atmosphere System

**Статус:** канон смысла; контракты — §12 (реализованы и покрыты тестами); UI-wiring — §13. Раздел новый (main на 2026-08-03 не содержал дневного слоя); заменяет собой WIP `productMoodTheme.ts` / `mood-themes.css` / `dayPhaseAtmosphere.ts` с ветки `design/profile-journey-premium` как **источник смысла** — тот код остаётся как справочный материал по токенам/паттерну, не как канон.

### 11.0 Принцип

День меняет **атмосферу** TodayFlow, а не его **личность**. Карточки, типографика, навигация, размеры, CTA, форма интерактивных компонентов и информационная иерархия — стабильны и не входят в контур этого раздела. Пользователь узнаёт TodayFlow даже без фона.

Меняются только: (1) фон, (2) декоративный слой, (3) интенсивность света/контраста, (4) едва заметное движение.

**Запрещено:** оформлять интерфейс буквально под конкретный транзит («Луна в Тельце», «Марс в квадрате») или под отдельный знак — это плодит десятки несогласованных тем. День сначала сводится к небольшому набору характеристик, из которых **движок дня** выбирает один из 8 режимов ниже — LLM/движок не возвращает произвольные цвета или CSS.

### 11.1 Три независимых слоя атмосферы — не путать

На ветке `design/profile-journey-premium` уже существуют два слоя, оба управляются часами. Day Atmosphere — третий, управляется **сюжетом дня**, не часами.

| Слой | Атрибут | Драйвер | Что меняет | Статус |
|------|---------|---------|-------------|--------|
| **Mood** | `data-mood` (`calm` / `focus` / `night` / `clarity`) | время суток + ручной pin | палитра `--tf-*` (ink, accent), независимо от appearance | существует (WIP-ветка), `productMoodTheme.ts` |
| **Day-phase** | `data-day-phase` (`morning` / `day` / `evening` / `night`) | время суток, сейчас scoped на `[data-atmosphere="today"]` | процедурная текстура фона (лучи утром, звёзды ночью) | существует (WIP-ветка), `day-phase-atmosphere.css` |
| **Day Atmosphere** *(этот раздел)* | `data-day-mode` (8 значений, §11.3) + `data-day-intensity` | **сюжет дня** от движка (см. §11.5), не часы | фон-композиция, декор, свет/контраст, motion | контракт §12 · UI §13 |

Day Atmosphere **не заменяет** Mood и Day-phase и **не выбирает тему по знаку/элементу** (это зона `ElementAtmosphere`, отдельная и статичная). Три слоя комбинируются: Mood задаёт базовую палитру ink/accent, Day-phase — который час дня подсвечивает Today, Day Atmosphere — какой сюжет у дня в целом. При конфликте токенов приоритет: Day Atmosphere → Day-phase → Mood (сюжет дня важнее часов).

### 11.2 Оси, из которых собирается режим (внутренние, не CSS)

Эти оси — язык движка для выбора режима, они не превращаются в токены напрямую:

- температура — холодная / нейтральная / тёплая;
- интенсивность — тихая / умеренная / высокая;
- темп — замедленный / ровный / динамичный;
- структура — мягкая / собранная / хаотичная;
- направление — внутрь / наружу;
- эмоциональный тон — спокойный / напряжённый / вдохновляющий / восстанавливающий / интроспективный.

### 11.3 Восемь режимов

| # | Режим | Оси (темп./интенс./темп/структура/направление/тон) | Для каких дней | Ощущение |
|---|-------|------------------------------------------------------|-----------------|----------|
| 1 | **Grounded** | тёплая / тихая / замедл. / собранная / внутрь / спокойный | устойчивые, практичные, медленные | надёжность, материальность |
| 2 | **Flow** | нейтр.-холодная / тихая / замедл. / мягкая / внутрь | чувствительные, интуитивные, эмоциональные | глубина, восприимчивость, плавность |
| 3 | **Radiance** | тёплая / умеренная / динамичная / собранная / наружу | яркие, социальные, творческие, уверенные | открытость, желание проявляться |
| 4 | **Momentum** | тёплая-интенс. / высокая / динамичная / собранная / наружу | быстрые, активные, решительные | импульс и концентрация, не тревожность |
| 5 | **Clarity** | холодная / умеренная / ровный / собранная / внутрь | рациональные, планирование, анализ | порядок, чистота, собранность |
| 6 | **Tension** | холодная-тёмная / высокая / ровный / хаотичная / внутрь | конфликтные, нестабильные, перегруженные | собранность и защита, не опасность |
| 7 | **Renewal** | нейтральная-светлая / тихая / замедл. / мягкая / наружу | завершение, отдых, новое начало | облегчение, пространство для начала |
| 8 | **Depth** | холодная / тихая / замедл. / мягкая / внутрь / интроспективный | сон, подсознание, уединение, пауза без цели что-то решить | тишина, погружение, отсутствие срочности |

**Depth vs соседи:** в отличие от Grounded — не про устойчивость и дела, в отличие от Clarity — не про анализ и решения, в отличие от Tension — без конфликта. Ближайший сосед — Flow, но Flow восприимчив и эмоционально проницаем наружу-к-миру, Depth — закрыт и обращён внутрь, ближе к тишине сна, чем к течению чувств.

### 11.4 Что регулирует каждый режим

1. **Главный фон** — три уровня: базовый цвет, большой размытый градиент, локальное свечение за контентом. Свечение стоит ниже и почти не движется для тихих режимов (Grounded, Depth), смещается вверх и контрастнее для активных (Momentum, Radiance).
2. **Декоративный слой** — отдельно от фона, под контентом: линии, дуги, световые пятна, частицы, полупрозрачные формы. Не находится под текстом, не снижает читаемость.
3. **Акцентная подсветка** — можно менять halo вокруг темы дня, тон ScreenFlow-индикатора, подсветку выбранных chips, тон разделителей. **Нельзя** менять цвета CTA/error/success/warning ежедневно — их значение должно быть постоянным.
4. **Motion** — только атмосферный: цикл 15–40 сек, смещение на несколько px, никаких быстрых бесконечных частиц, обязателен `prefers-reduced-motion`, останавливается или упрощается вне активного экрана.

### 11.5 Как движок выбирает режим — приоритет

1. Общий эмоциональный сюжет дня.
2. Уровень интенсивности.
3. Доминирующее качество/элемент дня.
4. Время суток (день ↔ Day-phase, см. §11.1).
5. Персональная поправка пользователя (аналог pin в Mood).

Движок **не** выбирает режим только по положению Луны — иначе оформление слишком примитивно отражает содержание дня.

### 11.6 Контракт движка (типы — §12)

Движок выдаёт **ограниченную конфигурацию**, не цвета и не CSS:

```
visual_mode: grounded | flow | radiance | momentum | clarity | tension | renewal | depth
intensity: 0..1
warmth: 0..1
motion: none | low
contrast: soft | medium | strong
decor_variant: <per-mode id>
time_phase: morning | day | evening | night   // сверяется с Day-phase, не дублирует его логику
```

Frontend преобразует эту конфигурацию в дизайн-токены (§11.8 / §12.3) детерминированно — без свободной генерации цвета. Единственная точка входа для недоверенного вывода: `resolveDayAtmosphere()` (§12.2).

### 11.7 Figma и время суток

Figma не используется в разработке — не источник правды, не рабочий процесс (см. правку §0 и §8). Day Atmosphere специфицируется только кодом и этим документом.

Одна тема дня естественно развивается по времени суток через **уже существующий** `data-day-phase` — утро больше света и воздуха, день — максимум контраста, вечер — глубже фон и локальное свечение, ночь — тёмная версия той же темы, а не отдельный случайный дизайн. Day Atmosphere не переопределяет эту логику, а работает поверх неё через `time_phase` в контракте (§11.6) как сверочный, а не порождающий параметр.

### 11.8 Токены (имена зафиксированы, значения — в §12/13)

Расширение существующих `--tf-*` / `--section-*`, не новая система:

- `--day-bg-base`
- `--day-bg-glow-primary`
- `--day-bg-glow-secondary`
- `--day-decor-color`
- `--day-decor-opacity`
- `--day-accent-soft`
- `--day-motion-duration`
- `--day-motion-distance`
- `--day-surface-tint`

Применяются через `html[data-day-mode="…"]`, по аналогии с `html[data-atmosphere="…"]` (`SectionAtmosphereBridge`) и `[data-mood="…"]`. Компонент-мост — `DayAtmosphereBridge`, ставится рядом с `SectionAtmosphereBridge` в shell, не в каждой странице отдельно.

### 11.9 Что остаётся стабильным (напоминание из §0/§7)

Структура экранов · типографика (§5) · размеры карточек (§4) · цвета ошибок/успеха/предупреждений · основные CTA (§4 Surface C) · логика навигации · форма интерактивных компонентов · информационная иерархия.

### 11.10 Следующие шаги

- §12 «Day Atmosphere — Contracts» — **готово**, см. ниже.
- §13 «Day Atmosphere — Implementation» (не в этом документе): `DayAtmosphereBridge.tsx`, `day-atmosphere.css` (реальные CSS-правила из значений §12.3), миграция полезного из WIP-ветки, dark-вариант палитры, реальные SVG/CSS для decor-вариантов.

---

## 12. Day Atmosphere — Contracts

**Статус:** реализовано и покрыто тестами. **Код:** `frontend/src/lib/dayAtmosphere.ts` · тесты `frontend/src/lib/__tests__/dayAtmosphere.test.ts` (18/18 green, 100% line/func coverage на модуль). Чистые функции — без React, без DOM (кроме pin-хелперов), без CSS-файла и без Bridge-компонента: это осознанно оставлено §13.

### 12.1 Типы

```ts
type DayVisualMode =
  | "grounded" | "flow" | "radiance" | "momentum"
  | "clarity" | "tension" | "renewal" | "depth";

type DayMotion = "none" | "low";
type DayContrast = "soft" | "medium" | "strong";
type DayTimePhase = "morning" | "day" | "evening" | "night";

interface DayAtmosphereContract {
  visual_mode: DayVisualMode;
  intensity: number;   // 0..1, clamped
  warmth: number;      // 0..1, clamped
  motion: DayMotion;
  contrast: DayContrast;
  decor_variant: string;   // closed per-mode set, §11.3 × 2 variants
  time_phase: DayTimePhase; // сверочный, не порождающий (§11.7)
}
```

Это ровно контракт из §11.6 — движок дня не может вернуть ничего сверх этих полей.

### 12.2 `resolveDayAtmosphere()` — единственная точка входа для чужого вывода

Чистая функция `resolveDayAtmosphere(input?)`: принимает **частичный и не доверенный** объект (выход движка) плюс опциональный `pinnedMode` (аналог pin в `productMoodTheme`), возвращает **полный закрытый** `DayAtmosphereContract`. Правила отказоустойчивости:

- неизвестный/битый `visual_mode` → откат на `clarity` (нейтральный дефолт), не exception;
- `pinnedMode` побеждает над `visual_mode` от движка;
- `intensity`/`warmth` — клэмп в 0..1, `NaN` → дефолт;
- неизвестный `decor_variant` → первый вариант из пары для данного режима (`DAY_MODE_DECOR_VARIANTS`);
- неизвестный `contrast`/`motion`/`time_phase` → соответствующий дефолт.

Всё это закрыто тестами: fallback на мусорный `visual_mode`, приём всех 8 легальных режимов, клэмп чисел, победа pin, отказ от левого `decor_variant`, отказ от левых `contrast`/`motion`/`time_phase`.

### 12.3 Токены — `dayAtmosphereTokens()`

Отдельная чистая функция `dayAtmosphereTokens(contract)` детерминированно превращает контракт в объект `--day-*` (имена — из §11.8, light-палитра черновая, dark и точная художественная доводка — §13):

- база (`--day-bg-base`, `--day-bg-glow-primary/secondary`, `--day-decor-color`, `--day-accent-soft`, `--day-surface-tint`) берётся по `visual_mode` из фиксированной таблицы на 8 записей;
- `--day-decor-opacity` — из `intensity` × диапазон, заданный `contrast` (soft/medium/strong);
- `--day-motion-duration`/`--day-motion-distance` — из `intensity` и профиля режима (тихие режимы двигаются медленнее и меньше, чем активные при той же интенсивности), **зажаты в границах 15–40 сек** (§11.4) и обнуляются при `motion: "none"`.

Тестами закрыто: полный набор ключей на все 8 режимов, детерминированность (одинаковый вход → одинаковый выход), обнуление motion-токенов при `motion: "none"`, попадание длительности в 15–40s на всех режимах и интенсивностях, монотонный рост opacity с ростом intensity.

### 12.4 Manual pin

`readDayModePin()` / `writeDayModePin()` — зеркало `readMoodPin`/`writeMoodPin` из `productMoodTheme.ts`, свой storage-ключ `todayflow_day_mode_pin_v1`, тот же контракт «испорченное хранилище не должно ронять приложение».

---

*Документ (§11) → контракты (§12, готово) → реализация (§13, следующий шаг). Figma нигде не участвует.*

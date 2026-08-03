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
| Визуальные **примитивы** продукта **+ закрытые React DS-компоненты** (`DsButton`/`DsCard`/`DsTypography`/`DsForm`, §15) — единственный легальный путь; ad-hoc CSS-кнопки/карточки поверх токенов запрещены | Произвольная стилизация мимо `design-system/*` · новый параллельный namespace токенов |
| Поверхности · герои · символы · геометрия | [PROFILE_SCREEN_MASTER.md](profile/PROFILE_SCREEN_MASTER.md) · §2 Symbols |
| Один Figma-источник правды *(исторически; см. §8, §11.7)* | Moodboard 100 UI · «TodayFlow is…» |

*(до 2026-08-03 здесь стояло «Design system компонентов — не это»; снято §14.5 / закрыто §15 — DS уже существует в `frontend/src/design-system/`, проблема была в необязательности его использования, не в его отсутствии.)*

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
| Background | `var(--tf-surface-insight-bg)` — light `rgba(255,253,249,0.88)` · dark `rgba(30,26,36,0.92)` (см. `todayflow-foundation.css` `[data-theme="dark"]`) |
| Radius | **28px** (`--tf-surface-insight-radius`) |
| Shadow | `var(--tf-surface-insight-shadow)` |
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

**Статус:** канон смысла; контракты — §12; UI first pass — §13. Раздел новый (main на 2026-08-03 не содержал дневного слоя); заменяет собой WIP `productMoodTheme.ts` / `mood-themes.css` / `dayPhaseAtmosphere.ts` с ветки `design/profile-journey-premium` как **источник смысла** — тот код остаётся как справочный материал по токенам/паттерну, не как канон.

### 11.0 Принцип

День меняет **атмосферу** TodayFlow, а не его **личность**. Карточки, типографика, навигация, размеры, CTA, форма интерактивных компонентов и информационная иерархия — стабильны и не входят в контур этого раздела. Пользователь узнаёт TodayFlow даже без фона.

Меняются только: (1) фон, (2) декоративный слой, (3) интенсивность света/контраста, (4) едва заметное движение.

**Запрещено:** оформлять интерфейс буквально под конкретный транзит («Луна в Тельце», «Марс в квадрате») или под отдельный знак — это плодит десятки несогласованных тем. День сначала сводится к небольшому набору характеристик, из которых **движок дня** выбирает один из 8 режимов ниже — LLM/движок не возвращает произвольные цвета или CSS.

### 11.1 Три независимых слоя атмосферы — не путать

| Слой | Атрибут | Драйвер | Что меняет | Статус |
|------|---------|---------|-------------|--------|
| **Section** | `data-atmosphere` | **роут** | мягкий route-пресет; **на product routes уступает Day Atmosphere**, когда `data-day-mode` задан | route-atmosphere |
| **Mood** | `data-mood` | время + pin | ink/accent (WIP) | `productMoodTheme.ts` |
| **Day-phase** | `data-day-phase` | часы на `/today` | процедурная текстура | WIP |
| **Day Atmosphere** | `data-day-mode` (8) | **сюжет дня** | фон, декор, motion · **сквозной шелл** (sidebar/frame) на всех product routes | §12–§13 |

**Продуктовый SoT (2026-08-03):** на app shell день один — не выделяем разделы отдельными dark/void темами (Tarot immersive dark снят). Экранные акты Today = плоские glass Block как Glance (без ActShell-матрёшки). Totem color / heatmap mood — не шелл.

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
3. **Акцентная подсветка** — можно менять halo вокруг темы дня, тон ScreenFlow-индикатора (dots через `--day-decor-color` / `--day-accent-soft` / `--day-surface-tint`), подсветку выбранных chips, тон разделителей. **Нельзя** менять цвета CTA/error/success/warning ежедневно — их значение должно быть постоянным. Форма chrome (dots only; без ordinals / labeled act strip / Назад·Далее) — [SCREEN_FLOW_V1 §1.5](foundation/SCREEN_FLOW_V1.md); меняется только тон.
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

Типографика (§5) · размеры карточек вне Day Atmosphere surface (§4) · цвета ошибок/успеха/предупреждений · основные CTA (§4 Surface C) · логика навигации ScreenFlow (порядок актов) · форма интерактивных компонентов вне атмосферы.

**Исключение — Glance / Day Atmosphere surface:** каркас первого viewport Today **может** менять плотность и композицию под full-bleed атмосферу дня (стекло-блоки §16, sparse chrome; прогресс = ScreenFlow dots + свайп, не gauge и не ряд названий актов) — см. [TODAY_SCREEN_SCENARIO_V3](./today/TODAY_SCREEN_SCENARIO_V3.md) Экран 0. Jobs смысла акта (тон / nearest / teaser / no Plot facts) не меняются; меняется только показ. Это сознательный SoT-сдвиг относительно ранней формулировки «иерархия всегда стабильна».

### 11.10 Следующие шаги

- §12 «Day Atmosphere — Contracts» — **готово**, см. ниже.
- §13 «Day Atmosphere — Implementation» — **visible product pass** (engine nest + shell paint + Glance IA); backlog в §13.4.

---

## 12. Day Atmosphere — Contracts

**Статус:** реализовано и покрыто тестами. **Код:** `frontend/src/lib/dayAtmosphere.ts` · тесты `frontend/src/lib/__tests__/dayAtmosphere.test.ts`. Чистые функции — без React, без DOM (кроме pin-хелперов). CSS-файл и Bridge-компонент — §13.

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

`readDayModePin()` / `writeDayModePin()` — зеркало `readMoodPin`/`writeMoodPin` из `productMoodTheme.ts`, свой storage-ключ `todayflow_day_mode_pin_v1` (`DAY_MODE_PIN_STORAGE_KEY`), тот же контракт «испорченное хранилище не должно ронять приложение».

---

## 13. Day Atmosphere — Implementation

**Статус:** visible product pass — BE nest `day_atmosphere` из сюжета дня · bridge потребляет nest · shell/`--day-*` фон · decor layer · Glance glass-hero IA. Dark-appearance палитры и полный набор 16 polished SVG — backlog (§13.4).

### 13.1 Код

| Файл | Роль |
|------|------|
| `frontend/src/styles/day-atmosphere.css` | Статическая light-палитра на 8 `html[data-day-mode="…"]`, значения = `DAY_MODE_BASE_TOKENS` из §12.3. `:root` — нейтральный fallback до гидратации. `prefers-reduced-motion` зануляет motion-токены через `!important` — побеждает даже инлайн-стили от моста. Product shell читает `--day-bg-*` / decor. |
| `frontend/src/components/DayAtmosphereBridge.tsx` | Мост: `data-day-mode` + инлайн `--day-*` на `documentElement`. Читает pin + `day_atmosphere` из Today payload; pin побеждает. Скоуп — `isAppProductRoute`. |
| `backend/.../day_atmosphere_v1.py` | Детерминированный mapper `thesis.mode` → closed `DayAtmosphereContract` (без LLM-цветов); nest на today wire. |
| `frontend/src/components/DayAtmosphereDecor.tsx` | Decor layer по `decor_variant` / `data-day-mode`. |
| `frontend/src/components/__tests__/DayAtmosphereBridge.test.tsx` | Bridge + engine nest + pin. |

**Wiring** (`frontend/src/app/layout.tsx`): импорт `@/styles/day-atmosphere.css` рядом с `section-atmosphere.css`; `<DayAtmosphereBridge />` рядом с `<SectionAtmosphereBridge />` в том же `<Suspense>`.

### 13.2 Почему статика (CSS) + инлайн (JS) вместе

Базовая палитра режима фиксирована на 8 значений → живёт в CSS по `data-day-mode`, работает уже на SSR/до гидратации. Но `intensity` / `contrast` / `motion` от движка — непрерывные, не одно из 8 состояний → их не закодировать статическими CSS-блоками; мост считает `dayAtmosphereTokens()` и пишет их инлайн на `documentElement.style`. Мост пишет туда же и базовые токены (не только динамические) — так `dayAtmosphere.ts` остаётся единственным источником истины, а CSS-файл — просто safety-фолбэк, если JS ещё не отработал.

### 13.3 Проверено

- `jest` — контракт `dayAtmosphere.test.ts` + мост `DayAtmosphereBridge.test.tsx`.
- `dayAtmosphere.ts` / `DayAtmosphereBridge.tsx` / `layout.tsx` — без новых type errors по модулю.
- Diff в `layout.tsx`: импорт CSS + импорт моста + одна JSX-строка; существующие `day-phase-atmosphere` / `mood-themes` на feature-ветке не тронуты.

### 13.4 Backlog

- Dark-appearance значения палитры (`data-theme="dark"` × `data-day-mode`) — day-mode пока не имеет полной dark-пары; `color-scheme` для Tension/Depth не выставляется при светлом `data-theme`.
- Decor-ассеты: полный набор 16 polished SVG (`DAY_MODE_DECOR_VARIANTS`) — сейчас art seed = `public/images/backgrounds/{1–5}.png` mapped to 8 `visual_mode` via `--day-bg-art` (tension/renewal/depth reuse nearest seed until dedicated assets).
- Plot photo-wash vs day-mode — дальнейшее подчинение phase-hero day-токенам (избежать тройной атмосферы).

---

## 14. Design System Audit (2026-08-03)

**Статус:** аудит, не канон. Основание для §15 (канон примитивов / токенов / dark-контраста). Проверено на `design/profile-journey-premium` (`fa48d9a`+); числа ниже пересчитаны по дереву `frontend/src`, не скопированы из чужого прогона без сверки.

### 14.1 Симптом

В тёмной теме: светлые карточки со светлым (нечитаемым) текстом; разные кнопки/баннеры/размеры блоков. Это не один CSS-баг — следствие отсутствия *обязательного* единого слоя токенов + примитивов.

### 14.2 Токены — семь параллельных систем вместо одной

Уникальные custom properties по префиксу (скан `frontend/src`, 2026-08-03):

| Namespace | Уник. props | Dark-aware файлы (есть `data-theme="dark"` и префикс) | Заметка |
|-----------|-------------:|------------------------------------------------------:|---------|
| `--tf-*` (`todayflow-foundation.css`, канон §4/§6) | **149** | 18 | полный блок `[data-theme="dark"]` — **единственный полно покрытый** |
| `--orbit-*` | 97 | 2 | legacy |
| `--todayflow-*` | 36 | 2 | legacy / marketing |
| `--tdp-*` (приватный Today) | 23 | 2 | оверрайд вручную в каждом файле |
| `--section-*` | 17 | **1** (`section-atmosphere.css` `[data-theme="dark"]`, §17a) | route-atmosphere; ink/panel alias `--tf-*` |
| `--day-*` (§11–§13) | 9 | 1* | dark backlog §13.4 (*файл моста/CSS упоминает, палитры dark нет) |
| `--product-*` | 7 | n/a | **layout** (radius/max-width/eyebrow), не цвета — dark-пара не требуется; при правке файла можно оставить как есть |

Семантика дублируется: «ink» = `--tf-ink` / `--orbit-color-ink` / `--todayflow-color-ink-warm`; «surface» = `--tf-surface` / `--orbit-color-surface` / `--todayflow-surface` / `--tdp-surface`. Синхронность не гарантирована.

**Вывод (на момент аудита):** экраны на `--section-*` / `--product-*` не адаптировались под dark. **§17a:** `--section-*` получил dark-пару + light atmosphere washes gated `:not([data-theme="dark"])`. **§17b pass 1:** топ-экраны с solid `#fff` → `var(--tf-surface)`. `--product-*` уточнено как layout (не color gap). `--tdp-*` хрупок: где забыли ручной оверрайд — ломается контраст.

### 14.3 Механизм бага (светлый текст на светлой карточке)

~**19** из **74** `.module.css` задают фон хардкодом `#fff` / `white` / `#ffffff` (не через `--tf-surface` / Surface B). Среди них: `profileV0`, `profileV2System`, `practicesV2System`, `practicesV2History`, `practicesStateCycle`, `PracticesPage`, `challenges`, `TodayCompositionSurface` (частично), `TodayPersonalizedProductSection`, `TodayEveningProductClose`, `productWebScreens`, `ProductJourneyScene`, плюс несколько `design-system/*` (включая `dsPrimitives.module.css` — primary button `color: #fff`).

Типичный паттерн: фон **не** подписан на `data-theme="dark"`, а цвет текста наследует dark-aware `--tf-ink` → в dark ink светлеет, карточка остаётся `#fff` → нечитаемо.

### 14.4 Примитивы — слой есть, обязательности нет

В репозитории **уже есть** зачаток DS:

| Примитив | Код | Проблема |
|----------|-----|----------|
| Button | `design-system/primitives/DsButton.tsx` (variants: primary/secondary/ghost/destructive/icon) | adoption частичная; десятки экранов всё ещё свои `.actionButton` / `.submitButton` / ad-hoc CTA |
| Card / surface | `DsCard.tsx` + Surface A–N в §4 | Surface B в каноне с хардкод `rgba(255,253,249,0.88)` без dark-пары; многие экраны игнорируют и пишут `#fff` |
| Type | `DsTypography.tsx` + §5 `--tf-type-*` | параллельно живёт `--orbit-text-*` (частично alias) |
| Form | `DsForm.tsx` | узкое использование |
| Auth buttons | `OAuthButtons.tsx` | отдельный кейс, не общий Button |

То есть проблема **не** «кнопки нет совсем», а: (1) примитив не канонизирован как *единственный* путь, (2) локальные кнопки/баннеры разрешены по факту, (3) сами DS-примитивы местами хардкодят светлые значения (`#fff` на primary).

**Radius:** 20+ хардкод-значений + массовый pill `999px`, при том что §4 уже фиксирует Surface-радиусы (24/28/36). Шкала `--tf-ds-radius-*` / `--tf-ds-space-*` в foundation есть — код её не обязан использовать.

### 14.5 Конфликт с §0 — **закрыт в §15**

§0 переписан: Foundation UI = токены + **обязательные** React-примитивы; ad-hoc CSS поверх `#fff` — запрещён.

### 14.6 Что решает §15

1. **Один namespace-победитель:** `--tf-*`. Остальные (`--orbit-*`, `--todayflow-*`, `--section-*`, `--product-*`, `--tdp-*`) — legacy-алиасы / deprecation. `--day-*` — отдельный атмосферный слой (§11).
2. **Закрытые контракты примитивов:** `DsButton` / `DsCard` / Typography / Form — обязательны; Banner — гэп (§15.5).
3. **Единая шкала** radius + spacing (`--tf-ds-*`).
4. **Dark-контракт surfaces** + запрет `#fff` как фона карточки.
5. **Migration checklist** — вход в §17.

**Не входит в §15:** массовая правка всех 74 module.css (это §17). Не входит полная dark-палитра `--day-*` (остаётся §13.4).

### 14.7 Рекомендуемый scope первого прохода §15 → §17

Не «весь продукт за один PR». Минимальный полезный срез:

1. §15 канон (токены + примитивы + запреты) — **готово**.
2. §17a — foundation: починить хардкод в `dsPrimitives.module.css` + dark для Surface B / `--tf-surface*` / алиасы `--section-*` где дешево — **готово**.
3. §17b — вычистить хардкод `#fff` в топ-баговых экранах (Profile v0/v2, Practices, Challenges, ключевые Today composition surfaces) — **pass 1 готово**; остаток: декоративные highlights + вне списка.
4. §17c — запретить новые ad-hoc buttons в review (lint/checklist); постепенно свести CTA на `DsButton`.

---

## 15. Design System Canon

**Статус:** канон; реализация — §17 (по фазам §14.7). Отвечает на пять пунктов §14.6 и снимает конфликт §0/§14.5. Не переизобретает примитивы — они уже есть в `frontend/src/design-system/`; канонизирует их как обязательные и фиксирует, что именно в них нужно починить.

### 15.1 Namespace — победитель `--tf-*`

`--tf-*` (`todayflow-foundation.css`) — единственный источник цвета/поверхности/тени с полным `[data-theme="dark"]`-покрытием (§14.2). Остальные — **legacy**, новый код на них ссылаться не должен:

| Namespace | Статус | Путь миграции |
|-----------|--------|---------------|
| `--orbit-*` | legacy | alias на `--tf-*` там, где 1:1 соответствие есть (`--orbit-color-ink` → `--tf-ink` и т. п.); удаление — отдельный тикет, не в этом проходе |
| `--todayflow-*` | legacy (marketing) | не трогать вне marketing-страниц; новые product-экраны — только `--tf-*` |
| `--tdp-*` | legacy, приватный Today | не копировать в новые компоненты; существующий уже держит свой dark-оверрайд, трогаем только если меняем сам файл |
| `--section-*` | сохраняется для route-atmosphere (§11.1), но получает dark-пару (§17a) | не убирать — другая ось, не дублирует ink/surface |
| `--product-*` | legacy | заменить на `--tf-*` при следующей правке файла, который его использует |
| `--day-*` | отдельный атмосферный слой (§11), не участвует в этом namespace-споре | без изменений |

**Правило:** новый компонент/экран не создаёт новых custom properties для ink/surface/border/shadow — только читает `--tf-*` (напрямую или через DS-примитив).

### 15.2 Обязательные примитивы — уже существующий `frontend/src/design-system/`

Не создаём заново. Канонизируем:

| Примитив | Экспорт | Варианты | Правило |
|----------|---------|----------|---------|
| **Button** | `DsButton` (`design-system/primitives/DsButton.tsx`) | `primary · secondary · ghost · destructive · icon` × `size: sm · md · block` | Единственный способ сделать CTA/кнопку. Новый `.actionButton`/`.submitButton`-класс в `.module.css` — запрещён (см. §17c) |
| **Card / Surface** | `DsCard` (+ `DsStatusBadge`) | `standard · glass · orbital · feature · dark · insight · elevated · outline · card` × `size: default · compact` — соответствуют Surface A–N §4 и `card--*` в Figma-карте (`figmaMap.ts`). **`compact`** = Surface B pad/radius (§16.3) для Today Block-панелей | Контентная/интерактивная карточка — только через `DsCard`, не `<div className={styles.card}>` с собственным CSS. Today Block: `variant="glass" size="compact"` — без `!important`-override в потребителе |
| **Typography** | `DsTypography` (`DsDisplayTitle`/`DsHeadline`/`DsTitle`/`DsSubtitle`/`DsBody`/`DsCaption`/…) | соответствует ролям §5 | Новый `font-size` вне `--tf-type-*` — запрещён |
| **Form** | `DsForm` (`DsTextField`/`DsSearchField`/`DsCheckbox`/`DsChipField`/`DsClassifier`) | — | Инпуты — только отсюда |
| **Banner** | — **нет примитива** | — | Гэп, не входит в этот проход. Существующие реализации (§14) остаются как есть до отдельного контракта — не изобретаем форму без опоры на реальные кейсы (backlog, см. §15.5) |

Живой каталог — `/design-system` (`DsCatalog.tsx`), Figma-имена → код — `design-system/registry/figmaMap.ts`. Оба уже существуют; структуру не ломаем.

### 15.3 Известные баги внутри самих примитивов — чинить первыми (§17a)

`dsPrimitives.module.css` сам нарушает правило §15.1 — хардкод-литералы без токена, в т.ч. в **дефолтном** варианте `DsCard`:

| Селектор | Строка (на `21ee896`) | Сейчас | Чем заменить |
|----------|----------------------:|--------|--------------|
| `.card` *(дефолтный `variant="card"`)* | 157 | `background: #fff` | `background: var(--tf-surface, #fff)` |
| `.cardInsight` | 345 | `background: #fff` | `background: var(--tf-surface-insight-bg, var(--tf-surface, #fff))` |
| `.elevated` | 138 | `background: #fff` | `background: var(--tf-surface, #fff)` |
| `.checkbox` | 445 | `background: #fff` | `background: var(--tf-surface, #fff)` *(не `--tf-page`: чекбокс сидит на surface-карточке; `--tf-page` в dark почти совпадает с фоном страницы)* |
| `.btnPrimary` / `.btnDestructive` / `.pill` | 33, 284, 200 | `color: #fff` | оставить в этом проходе — текст на насыщенном accent-фоне; `--tf-on-dark` при следующей правке файла, не блокер |

Починка четырёх фонов в одном файле чинит dark-контраст везде, где уже используется `DsCard` — раньше остальной миграции.

### 15.4 Radius / spacing — используем существующую шкалу, не создаём новую

`--tf-ds-space-*` и `--tf-ds-radius-*` уже существуют в `todayflow-foundation.css`. Правило: любой новый `border-radius`/`padding` в `.module.css` — через эти токены. Единственное официально разрешённое исключение — `border-radius: 999px` (pill/chip), не оборачивается в токен.

### 15.5 Явные гэпы (не в этом проходе)

- **Banner-примитив** — нет контракта, нет решения по форме; нужен отдельный проход по существующим реализациям, прежде чем проектировать API.
- **Dark-пара для `--section-*`** — **готово** (§17a): `html[data-theme="dark"]` в `section-atmosphere.css`; light route washes через `:not([data-theme="dark"])`.
- **`--day-*` dark-палитра** — остаётся backlog §13.4, не расширяется этим разделом.

### 15.6 §17a — статус *(перенумеровано с §16a — см. §16/§17 ниже)*

- **§17a Slice 0–2 (готово):** `dsPrimitives` surfaces · Surface B insight dark · `--section-*` dark pair.
- **§17b pass 1 (готово):** solid `background: #fff` → `var(--tf-surface, #fff)` на топ-экранах (Practices/Challenges/Profile v2/Today composition/product web layouts + profileV0 gradient stops). ~63 solid + card-wash gradients.
- **`--product-*`:** уточнено — это layout-токены (radius/content-max), не палитра; dark-пара не нужна.
- **Остаток §17b:** декоративные `#fff` в border/box-shadow/orb highlights; оставшиеся хардкоды вне топ-списка; ручной QA dark на Profile/Practices/Challenges.
- **§17c:** запрет новых ad-hoc CTA / lint checklist. **Today Response pass:** `TodayTapWidget` → `DsButton` (ad-hoc `.tapBtn` removed).

---

## 16. Today Screen — Block Composition

**Статус:** канон реализован (Glance…Response Block + domain icons §16.6). Отвечает на запрос «подача должна быть красиво разбита на блоки, легко читаться» — независимо от точного контента экрана. Не заменяет и не меняет [TODAY_SCREEN_SCENARIO_V3](today/TODAY_SCREEN_SCENARIO_V3.md) (SoT содержания каждого из 6 шагов ScreenFlow) — этот раздел только про то, **как** любой из шести шагов визуально организован. Навигационный chrome (свайп/цифры) — не здесь, см. [SCREEN_FLOW_V1 §1.5](foundation/SCREEN_FLOW_V1.md).

### 16.1 Проблема, зафиксированная в коде

`TodayGlanceAct.tsx` (шаг 0) сейчас — непрерывный вертикальный поток: один `themeBlock` (эйброу + заголовок + абзац), затем `metaRow` как инлайн-строка текста через точку («14:20 · Label», без карточки), затем плоский `<ul>` тизеров с «·» вместо иконок. Нет визуальной группировки, нет панелей, нет единой сетки отступов между смысловыми блоками.

### 16.2 Паттерн «Block» — единица подачи

Один блок = **закрытая единица информации**, всегда в одном порядке:

1. **Eyebrow** — маленький, приглушённый лейбл, что это за блок (уже есть как стиль в `TodayGlanceAct.module.css` `.eyebrow` — формализуется здесь, не переизобретается).
2. **Primary** — одно главное значение блока, крупно (роль **Section** или **Hero**, §5) — короткая фраза, время, статус-слово. Не абзац.
3. **Detail** *(опционально)* — одна строка/абзац пояснения, приглушённый тон (роль **Body**/**Caption**, §5).

Блок — это `DsCard` (`variant="glass"` **`size="compact"`**, `--tf-ds-glass`/`--tf-ds-glass-on-dark` + Day Atmosphere tint) поверх Day Atmosphere фона (§11–§13): полупрозрачная поверхность, а не сплошная заливка — атмосфера дня должна читаться сквозь панель, не исчезать под ней. Плотность Surface B (pad/radius) живёт в примитиве (`dsPrimitives.module.css` `.cardSizeCompact`), не в consumer `!important`.

### 16.3 Сетка и ритм

- Отступ **между** блоками — единый токен, не «на глаз»: `--tf-ds-space-5` (1.25rem) как база, `--tf-ds-space-6` (1.5rem) на широких экранах — те же токены, что уже в foundation (§15.4), новых не создаём.
- Внутренний padding блока — `--tf-ds-space-4`–`--tf-ds-space-5` (соответствует Surface B §4: 22×21) — через `DsCard size="compact"`, не локальный override.
- Radius блока — `--tf-surface-insight-radius` (28px) через тот же `compact`, не хардкод.
- **2×2 сетка** (как «Статус по сферам» на референсе) — это частный случай Block: eyebrow на уровне секции, дальше N мини-блоков без вложенного padding друг в друга (иконка + label + Primary-значение, без Detail).

### 16.3.1 Решение: `size="compact"` вместо consumer overrides

При first pass Glance временно перебивал pad/radius/фон `glass` через `!important` в `TodayGlanceAct.module.css`. Это закрыто: `DsCard` принимает `size="compact"`; комбинация `.cardGlass.cardSizeCompact` задаёт Surface B + `--tf-ds-glass` (+ `--day-surface-tint` если задан). Дальнейшие шаги ScreenFlow (§16.4) используют тот же API — без копирования override в пять файлов.

### 16.4 Применимость — все 6 шагов, не только Glance

Паттерн Block — общая визуальная грамматика для Glance / Plot / Symbols / Reading / Move / Response. Контент каждого шага (что именно показывается) не меняется — меняется только то, что любой фрагмент контента заворачивается в Block вместо голого абзаца/инлайн-строки. Это делает шаги визуально семьёй, даже когда состав полей на каждом разный (см. TODAY_SCREEN_SCENARIO_V3 §0.2 «один дом на сущность»).

### 16.5 Явно не меняется

- Состав и honest-omit правила контента (TODAY_SCREEN_SCENARIO_V3 — не трогается).
- Цвета CTA/error/success/warning (§0/§4).
- Навигационная механика (свайп/keyboard/analytics) — SCREEN_FLOW_V1 §1.1–§1.4, §1.7–§1.9 без изменений.

### 16.6 Domain icons (закрыто)

Сетка сфер `work / money / relationships / energy` (`DomainKey` в `todayDomainVerdicts.ts` — тот же словарь, что контракт):

| Domain | Icon | Источник |
|--------|------|----------|
| `work` | `IconBriefcase` | **новый** в `DsIcons.tsx` (тот же stroke-стиль 24×24 / 1.5) |
| `money` | `IconWalletCards` | уже был |
| `relationships` | `IconHeart` | уже был |
| `energy` | `IconActivity` | уже был |

Карта: `TODAY_DOMAIN_ICON_MAP` (`as const` + `satisfies`, рядом с `DS_NAV_ICON_MAP`). **Primary consumer:** Reading sphere-главы (`sphere-{domain}` в `TodayPersonalizedProductSection`) — иконка рядом с kicker. `TodayVerdictStripSlot` остаётся Wave2/test consumer (тот же map); неизвестный/legacy domain → без иконки, без падения.

### 16.7 Решённые ранее

- `metaRow`/nearest vs тизеры — **Glance:** nearest = отдельный Block («Ближайшее окно»); texture Block eyebrow = «Тема дня».

---

## 17. Design System Migration (module.css)

**Статус:** backlog, не начато полностью. Содержимое прежнего §16 (миграция module.css) переехало сюда под новым номером — конфликта с только что добавленным §16 (Today Block Composition) не осталось. Детали готовности — §15.6.

- **§17a** — foundation: dark-пара `--product-*` уточнена как layout (не нужна); Surface B / `dsPrimitives` / `--section-*` dark — см. §15.6 (готово Slice 0–2).
- **§17b** — топ-баговые экраны с хардкод `#fff` вне `DsCard` (pass 1 готово; остаток: декоративные highlights + вне списка + ручной QA dark).
- **§17c** — запрет ad-hoc CTA в ревью; постепенный перевод на `DsButton` (**Today Response** `TodayTapWidget` — done).

---

*Документ (§11) → контракты (§12) → реализация first pass (§13) → аудит (§14) → канон дизайн-системы (§15) → Today block-подача (§16, канон, реализация следующим шагом) → миграция module.css (§17, backlog). Figma нигде не участвует, кроме `figmaMap.ts` как справочной таблицы имён.*

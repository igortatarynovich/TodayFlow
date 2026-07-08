# Orbit Design System

Orbit Design System реализует slowlife-эстетику и Visual Narrative Convention для TodayFlow.

## Основные принципы

- **Slowlife-ритм**: крупные поля, дыхание между блоками, мягкие fade-анимации
- **Пастельная палитра**: кремовые, выцветшие кораллы, водянистые бирюзовые, песок
- **Paper grain**: тонкий слой текстуры для ощущения журнала/артбука
- **Мягкие капсулы**: вместо жёстких кнопок — капсулы с мягким контуром
- **Типографика**: спокойный гротеск + лёгкий скрипт для акцентов

## Компоненты

### MeaningCard

Базовая единица чтения интерпретации. Поддерживает три слоя: Observation, Interpretation, Context.

```tsx
import { MeaningCard } from '@/components/orbit';

<MeaningCard
  label="Emotional Patterns"
  badge="Step 2/5"
  layer="observation"
  heading="Observation"
  body="Your emotional responses tend to..."
  navLabel="Step 2 of 5"
  onPrev={() => {}}
  onNext={() => {}}
/>
```

**Props:**
- `label` (string) - название секции
- `badge` (string?) - бейдж (например, "Step 2/5")
- `locked` (boolean?) - заблокирован ли контекст
- `layer` ("observation" | "interpretation" | "context"?) - слой интерпретации
- `heading` (string?) - заголовок блока
- `body` (ReactNode) - содержимое блока
- `navLabel` (string?) - метка навигации
- `prevLabel` (string?) - текст кнопки "Назад"
- `nextLabel` (string?) - текст кнопки "Вперёд"
- `onPrev` (() => void?) - обработчик "Назад"
- `onNext` (() => void?) - обработчик "Вперёд"
- `disablePrev` (boolean?) - отключить "Назад"
- `disableNext` (boolean?) - отключить "Вперёд"
- `footnote` (ReactNode?) - сноска
- `cta` (ReactNode?) - призыв к действию

### OrientationRail

Ориентационная рейка для навигации по секциям. Поддерживает мантры.

```tsx
import { OrientationRail } from '@/components/orbit';

<OrientationRail
  sectionLabel="Emotional Patterns"
  metaLabel="Loop A"
  stepLabel="Step 2 of 5"
  mantra="Pause · Sense · Integrate"
  action={<button>Unlock Full</button>}
/>
```

**Props:**
- `sectionLabel` (string) - название секции
- `metaLabel` (string?) - мета-информация (Loop A/B/C)
- `stepLabel` (string?) - шаг (Step 2/5)
- `statusLabel` (string?) - статус (Complete, In review)
- `mantra` (string?) - мантра (Pause · Sense · Integrate)
- `action` (ReactNode?) - действие (CTA кнопка)

### MethodContextCapsule

Показывает откуда берутся смыслы: Sun/Moon/Rising карточки, оси A1-A7, Trace Hint.

```tsx
import { MethodContextCapsule } from '@/components/orbit';

<MethodContextCapsule
  anchorCards={[
    { label: "Sun", sign: "Aries", element: "fire", modality: "cardinal", themes: ["identity", "expression"] },
    { label: "Moon", sign: "Cancer", element: "water", modality: "cardinal", themes: ["emotions", "nurturing"] },
    { label: "Rising", sign: "Libra", element: "air", modality: "cardinal", themes: ["relationships", "balance"] }
  ]}
  axisHighlights={[
    { axisId: "A1", label: "Identity Orientation", value: 65, range: "outer", description: "Externally oriented" },
    { axisId: "A2", label: "Emotional Processing", value: -45, range: "inner", description: "Private processing" }
  ]}
  traceHint="Observation → Interpretation → Context строятся на Internal Model"
  showUnlockHint={true}
/>
```

**Props:**
- `anchorCards` (AnchorCard[]?) - карточки Sun/Moon/Rising
- `axisHighlights` (AxisHighlight[]?) - топ-3 оси с визуализацией диапазона
- `traceHint` (string | ReactNode?) - подсказка о методе
- `showUnlockHint` (boolean?) - показать подсказку о разблокировке в Full

### PracticeCapsule

Карточка практики: Tarot rituals, Guided Check-ins, Numerology prompts.

```tsx
import { PracticeCapsule } from '@/components/orbit';

<PracticeCapsule
  type="tarot"
  title="Card of the Day"
  description="Today's guidance focuses on..."
  metadata={{ date: "2024-01-15", card: "The Sun" }}
  steps={[
    "Draw your card",
    "Reflect on the meaning",
    "Set your intention"
  ]}
  cta={{ label: "Draw Card", onClick: () => {} }}
/>
```

**Props:**
- `type` ("tarot" | "check-in" | "numerology" | "ritual" | "mantra") - тип практики
- `title` (string) - заголовок
- `description` (string?) - описание
- `icon` (ReactNode?) - иконка
- `steps` (string[]?) - шаги практики
- `cta` ({ label: string, href?: string, onClick?: () => void }?) - призыв к действию
- `metadata` ({ date?: string, card?: string, number?: string, ritual?: string }?) - метаданные

### ActionFooter

Футер с действиями: Upgrade, Download PDF, Download ICS.

```tsx
import { ActionFooter } from '@/components/orbit';

<ActionFooter
  actions={[
    { label: "Upgrade to Full", variant: "primary", onClick: () => {} },
    { label: "Download PDF", variant: "secondary", href: "/download/pdf" },
    { label: "Download ICS", variant: "ghost", onClick: () => {} }
  ]}
/>
```

**Props:**
- `actions` (ActionItem[]) - массив действий
  - `label` (string) - текст действия
  - `href` (string?) - ссылка
  - `onClick` (() => void?) - обработчик клика
  - `variant` ("primary" | "secondary" | "ghost"?) - вариант стиля
  - `icon` (ReactNode?) - иконка
  - `disabled` (boolean?) - отключено ли действие

## CSS Утилиты

### Типографика

- `.orbit-display` - для Observation (крупный текст)
- `.orbit-display-sm` - для Observation (средний)
- `.orbit-body` - для Interpretation (основной текст)
- `.orbit-body-sm` - для Interpretation (малый)
- `.orbit-soft` - для Context (мягкий текст)
- `.orbit-accent` - для акцентов (скрипт)
- `.orbit-mantra` - для мантр

### CTA Капсулы

- `.orbit-cta-capsule` - базовая капсула
- `.orbit-cta-capsule--primary` - основная капсула

## Цветовая палитра

### Основные цвета
- `--orbit-color-page` - фон страницы (warm cream)
- `--orbit-color-card` - фон карточек
- `--orbit-color-card-warm` - тёплый белый
- `--orbit-color-mist` - песочный туман
- `--orbit-color-sage` - sage wash

### Акценты
- `--orbit-color-coral` - выцветший коралл
- `--orbit-color-turquoise` - водянистый бирюзовый
- `--orbit-color-sand` - песок
- `--orbit-color-apricot` - тёплый абрикос

### Семантические
- `--orbit-color-ink` - основной текст
- `--orbit-color-muted` - приглушённый текст
- `--orbit-color-border` - границы
- `--orbit-color-highlight` - выделение

## Spacing

- `--orbit-space-xs` - 6px
- `--orbit-space-sm` - 12px
- `--orbit-space-md` - 18px
- `--orbit-space-2` - 24px
- `--orbit-space-lg` - 32px
- `--orbit-space-xl` - 48px

## Shadows

- `--orbit-shadow-soft` - мягкая тень
- `--orbit-shadow-medium` - средняя тень
- `--orbit-shadow-warm` - тёплая тень
- `--orbit-shadow-card` - тень карточки

## Transitions

- `--orbit-transition-fast` - 150ms
- `--orbit-transition-base` - 300ms
- `--orbit-transition-slow` - 400ms
- `--orbit-transition-ritual` - 500ms

## Примеры использования

### Observation Block

```tsx
<MeaningCard
  layer="observation"
  label="Emotional Patterns"
  heading="Your emotional baseline"
  body={
    <p className="orbit-display-sm">
      You tend to process emotions internally before expressing them outwardly.
    </p>
  }
/>
```

### Interpretation Block

```tsx
<MeaningCard
  layer="interpretation"
  label="Emotional Patterns"
  heading="What this means"
  body={
    <p className="orbit-body">
      This pattern suggests that you value emotional privacy and prefer to 
      understand your feelings before sharing them with others.
    </p>
  }
/>
```

### Context Block (Full only)

```tsx
<MeaningCard
  layer="context"
  label="Emotional Patterns"
  locked={false}
  body={
    <p className="orbit-soft">
      You usually notice this around work situations—when decisions touch 
      your values, the pattern becomes tangible.
    </p>
  }
/>
```

### Orientation Rail с мантрой

```tsx
<OrientationRail
  sectionLabel="Emotional Patterns"
  stepLabel="Step 2 of 5"
  mantra="Pause · Sense · Integrate"
  action={
    <button className="orbit-cta-capsule orbit-cta-capsule--primary">
      Unlock Context
    </button>
  }
/>
```

### Method Context с Anchor Cards и Axes

```tsx
<MethodContextCapsule
  anchorCards={[
    { label: "Sun", sign: "Aries", element: "fire", modality: "cardinal" },
    { label: "Moon", sign: "Cancer", element: "water", modality: "cardinal" },
    { label: "Rising", sign: "Libra", element: "air", modality: "cardinal" }
  ]}
  axisHighlights={[
    { axisId: "A1", label: "Identity Orientation", value: 65, range: "outer" },
    { axisId: "A2", label: "Emotional Processing", value: -45, range: "inner" },
    { axisId: "A3", label: "Decision Making", value: 30, range: "balanced" }
  ]}
  traceHint="These insights are built from your birth chart data through our Internal Model."
  showUnlockHint={true}
/>
```

### Practice Capsule для Tarot

```tsx
<PracticeCapsule
  type="tarot"
  title="Daily Card"
  description="Today's card invites you to reflect on your emotional patterns."
  metadata={{ date: "2024-01-15", card: "The Sun" }}
  steps={[
    "Take a deep breath",
    "Draw your card",
    "Reflect on the meaning",
    "Set your intention"
  ]}
  cta={{ label: "Draw Card", onClick: () => {} }}
/>
```

### Action Footer

```tsx
<ActionFooter
  actions={[
    { label: "Upgrade to Full", variant: "primary", onClick: () => {} },
    { label: "Download PDF", variant: "secondary", href: "/download/pdf" },
    { label: "Add to Calendar", variant: "ghost", onClick: () => {} }
  ]}
/>
```


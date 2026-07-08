# Icons Directory

## Structure

```
icons/
├── zodiac/         # 12 signs — premium line set (P0)
├── planets/        # sun..pluto — same stroke (P0)
├── archetypes/     # sage, explorer, … — symbols not characters (P0)
├── elements/       # fire, earth, air, water — patterns/illustrations (P0)
├── geometry/       # orbits, grids, nodes — sacred geometry library (P0 product layer)
├── astrology/      # Legacy aliases (sun, moon, rising)
├── tarot/          # Tarot-related icons
├── practices/      # Practice type icons
└── categories/     # Category icons
```

**Profile UI:** drop purchased SVGs into `zodiac/`, `planets/`, `archetypes/`, `elements/`, then set `VISUAL_ASSET_MODE = "asset"` in `frontend/src/lib/visualIdentity/registry.ts`. See [docs/TODAYFLOW_FOUNDATION_UI.md](../../../docs/TODAYFLOW_FOUNDATION_UI.md) §2 Symbols.

---

## Astrology Icons (`/astrology/`)

### Required
- **sun.svg** - Sun symbol (☉)
  - Sizes: 24x24px, 32x32px, 48x48px
  - Usage: Sun sign display
- **moon.svg** - Moon symbol (☽)
  - Sizes: 24x24px, 32x32px, 48x48px
  - Usage: Moon sign display
- **rising.svg** - Ascendant symbol (↑)
  - Sizes: 24x24px, 32x32px, 48x48px
  - Usage: Rising sign display

### Planet Icons (Optional, can be added later)
- `mercury.svg`, `venus.svg`, `mars.svg`, `jupiter.svg`, `saturn.svg`, `uranus.svg`, `neptune.svg`, `pluto.svg`
- Size: 24x24px base (SVG scalable)

### Style Guidelines
- Line-based, minimal
- Consistent stroke width (1.5-2px)
- Clean, geometric shapes
- Color: Use CSS `currentColor` for flexibility

---

## Tarot Icons (`/tarot/`)

### Required
- **tarot-card.svg** - Generic tarot card icon
  - Size: 64x64px base (3:5 ratio)
  - Usage: Tarot section, card placeholders
- **tarot-back.svg** - Card back design
  - Size: 64x64px base (3:5 ratio)
  - Usage: Card back display
- **tarot-spread.svg** - Spread layout icon
  - Size: 48x48px
  - Usage: Spread selection UI

### Style Guidelines
- Minimal, symbolic
- Consistent with card aesthetic
- Can use simple geometric shapes

---

## Practice Icons (`/practices/`)

### Required
- **meditation.svg** - Meditation icon
  - Size: 32x32px base
  - Usage: Meditation practices
- **breathing.svg** - Breathing icon
  - Size: 32x32px base
  - Usage: Breathing practices
- **gratitude.svg** - Gratitude icon
  - Size: 32x32px base
  - Usage: Gratitude journal, practices
- **journal.svg** - Journal icon
  - Size: 32x32px base
  - Usage: Journal entries
- **focus.svg** - Focus icon
  - Size: 32x32px base
  - Usage: Focus practices
- **reflection.svg** - Reflection icon
  - Size: 32x32px base
  - Usage: Reflection practices

### Style Guidelines
- Functional, recognizable
- Minimal line art
- Consistent visual language

---

## Category Icons (`/categories/`)

### Required
- **category-emotions.svg** - Emotions category
  - Size: 24x24px
  - Usage: Emotion category filter
- **category-focus.svg** - Focus category
  - Size: 24x24px
  - Usage: Focus category filter
- **category-reflection.svg** - Reflection category
  - Size: 24x24px
  - Usage: Reflection category filter
- **category-meditations.svg** - Meditations category
  - Size: 24x24px
  - Usage: Meditations category filter
- **category-breathing.svg** - Breathing category
  - Size: 24x24px
  - Usage: Breathing category filter

### Style Guidelines
- Very minimal
- Distinct enough to differentiate categories
- Consistent size and stroke width

---

## General Icon Guidelines

- **Format**: SVG (always, for scalability)
- **Color**: Use `currentColor` or `fill="none" stroke="currentColor"` for CSS color control
- **ViewBox**: Standardize viewBox (e.g., "0 0 24 24")
- **Optimization**: Remove unnecessary paths, optimize SVG code
- **Accessibility**: Include `<title>` tags for screen readers
- **Naming**: Use kebab-case, descriptive names

### SVG Template Example

```svg
<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <title>Sun Icon</title>
  <circle cx="12" cy="12" r="5" stroke="currentColor" stroke-width="1.5"/>
  <!-- More paths -->
</svg>
```


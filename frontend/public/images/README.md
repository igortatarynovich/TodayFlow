# Images Directory Structure

This directory contains all static images, icons, banners, and backgrounds for the TodayFlow application.

## Directory Structure

```
images/
├── hero/              # Hero section backgrounds
├── icons/             # Icon set (tarot, astrology, practices)
├── cards/             # Card images (tarot, patterns, practices)
├── avatars/           # User avatars and profile images
├── backgrounds/       # Page backgrounds and patterns
├── banners/           # Promotional banners and CTAs
├── logos/             # Brand logos and marks
├── patterns/          # Decorative patterns and textures
└── placeholders/      # Placeholder images for loading states
```

## Image Requirements

### General Guidelines

- **Format**: WebP (primary), PNG (with transparency), SVG (icons/illustrations)
- **Optimization**: All images should be optimized for web
- **Responsive**: Provide multiple sizes for responsive design
- **Naming**: Use kebab-case, descriptive names (e.g., `hero-meditation-bg.webp`)

---

## 1. Hero Images (`/hero/`)

### Main Hero Background
- **File**: `hero-main-background.webp`
- **Size**: 1920x1080px (desktop), 1200x800px (tablet), 800x600px (mobile)
- **Usage**: Main landing page hero section
- **Style**: Soft, meditative, minimal gradient overlay
- **Format**: WebP, JPG fallback

### Secondary Hero Backgrounds
- **File**: `hero-discover.webp`, `hero-practices.webp`, `hero-daily.webp`
- **Size**: 1600x900px (desktop), 1200x675px (tablet)
- **Usage**: Section hero backgrounds
- **Style**: Subtle, consistent with main hero aesthetic

---

## 2. Icons (`/icons/`)

### Astrology Icons
- **Files**: `sun.svg`, `moon.svg`, `rising.svg`, `planets/*.svg`
- **Size**: 24x24px, 32x32px, 48x48px (multiple sizes)
- **Format**: SVG (scalable)
- **Style**: Minimal, line-based, consistent stroke width

### Tarot Icons
- **Files**: `tarot-card.svg`, `tarot-back.svg`, `tarot-spread.svg`
- **Size**: 64x64px base, scalable SVG
- **Format**: SVG
- **Style**: Simple, symbolic

### Practice Icons
- **Files**: `meditation.svg`, `breathing.svg`, `gratitude.svg`, `journal.svg`
- **Size**: 32x32px base, scalable SVG
- **Format**: SVG
- **Style**: Minimal, functional

### Category Icons
- **Files**: `category-emotions.svg`, `category-focus.svg`, `category-reflection.svg`
- **Size**: 24x24px base
- **Format**: SVG

---

## 3. Card Images (`/cards/`)

### Tarot Card Covers
- **File**: `tarot-card-back.webp`
- **Size**: 300x500px (card ratio 3:5)
- **Usage**: Tarot card back side
- **Format**: WebP, optimized
- **Style**: Elegant, minimal, "hand-ink frame" aesthetic

### Pattern Cards
- **Files**: `pattern-a1.webp`, `pattern-a2.webp`, etc. (A1-A7)
- **Size**: 400x300px
- **Usage**: Pattern visualization cards
- **Format**: WebP
- **Style**: Abstract, symbolic

### Practice Cards
- **Files**: `practice-meditation.webp`, `practice-breathing.webp`
- **Size**: 400x300px
- **Usage**: Practice preview cards
- **Format**: WebP

---

## 4. Avatars (`/avatars/`)

### Default Avatar
- **File**: `avatar-default.svg`
- **Size**: 64x64px, 128x128px
- **Format**: SVG (scalable)
- **Usage**: Default user avatar

### Zodiac Avatars (optional)
- **Files**: `avatar-aries.svg`, `avatar-taurus.svg`, etc.
- **Size**: 64x64px base
- **Format**: SVG
- **Usage**: Zodiac sign representations

---

## 5. Backgrounds (`/backgrounds/`)

### Page Backgrounds
- **Files**: `bg-page-light.webp`, `bg-page-warm.webp`
- **Size**: 1920x1080px, tileable
- **Format**: WebP
- **Usage**: Subtle page backgrounds
- **Style**: Very subtle texture, warm tones

### Pattern Backgrounds
- **Files**: `bg-pattern-dots.svg`, `bg-pattern-grid.svg`
- **Size**: Tileable (SVG)
- **Format**: SVG
- **Usage**: Subtle decorative patterns

### Gradient Overlays
- **Files**: `overlay-gradient-warm.svg`, `overlay-gradient-soft.svg`
- **Size**: SVG (scalable)
- **Format**: SVG
- **Usage**: Overlay effects on hero sections

---

## 6. Banners (`/banners/`)

### CTA Banners
- **Files**: `banner-cta-subscribe.webp`, `banner-cta-register.webp`
- **Size**: 1200x300px (desktop), 800x200px (mobile)
- **Format**: WebP
- **Usage**: Call-to-action banners
- **Style**: Subtle, not overwhelming

### Promotional Banners
- **Files**: `banner-promo-feature.webp`
- **Size**: 1600x400px (desktop)
- **Format**: WebP

---

## 7. Logos (`/logos/`)

### Main Logo
- **File**: `logo-todayflow.svg`
- **Size**: Scalable SVG, min 120x40px
- **Format**: SVG (primary), PNG (fallback)
- **Variants**: 
  - `logo-todayflow-light.svg` (for dark backgrounds)
  - `logo-todayflow-dark.svg` (for light backgrounds)

### Logo Mark (icon only)
- **File**: `logo-mark.svg`
- **Size**: 32x32px, 48x48px, 64x64px
- **Format**: SVG
- **Usage**: Favicon, app icon, small spaces

### Favicon
- **File**: `favicon.ico`, `favicon-16x16.png`, `favicon-32x32.png`
- **Size**: 16x16px, 32x32px, 180x180px (Apple touch icon)
- **Format**: ICO, PNG
- **Usage**: Browser favicon

---

## 8. Patterns (`/patterns/`)

### Decorative Patterns
- **Files**: `pattern-grain.svg`, `pattern-noise.svg`
- **Size**: Tileable SVG
- **Format**: SVG
- **Usage**: Subtle texture overlays (grain effect)
- **Opacity**: Very low (5-10%)

### Border Patterns
- **Files**: `border-frame.svg`, `border-divider.svg`
- **Size**: Scalable SVG
- **Format**: SVG
- **Usage**: Card borders, section dividers

---

## 9. Placeholders (`/placeholders/`)

### Loading Placeholders
- **Files**: `placeholder-card.webp`, `placeholder-avatar.webp`
- **Size**: Match target dimensions
- **Format**: WebP
- **Usage**: Skeleton loaders, loading states
- **Style**: Blurred, low-opacity versions

### Empty State Illustrations
- **Files**: `empty-practices.svg`, `empty-journal.svg`, `empty-tarot.svg`
- **Size**: 200x200px (scalable)
- **Format**: SVG
- **Usage**: Empty state illustrations
- **Style**: Simple, friendly, minimal

---

## Responsive Image Strategy

### Breakpoints
- **Mobile**: < 768px
- **Tablet**: 768px - 1024px
- **Desktop**: > 1024px

### Image Sizes
- **Thumbnails**: 150x150px
- **Cards**: 300x200px (mobile), 400x300px (desktop)
- **Hero**: 800x600px (mobile), 1920x1080px (desktop)
- **Banners**: 800x200px (mobile), 1600x400px (desktop)

### Naming Convention for Responsive
- `image-name-mobile.webp` (mobile)
- `image-name-tablet.webp` (tablet)
- `image-name-desktop.webp` (desktop)
- Or use `srcset` in Next.js Image component

---

## Next.js Image Optimization

All images should use Next.js `Image` component:

```tsx
import Image from 'next/image';

<Image
  src="/images/hero/hero-main-background.webp"
  alt="Hero background"
  width={1920}
  height={1080}
  priority // for above-the-fold images
  placeholder="blur" // if blur placeholder available
/>
```

---

## File Naming Convention

- Use kebab-case: `hero-main-background.webp`
- Include size if multiple variants: `icon-sun-24.svg`, `icon-sun-32.svg`
- Include variant: `logo-light.svg`, `logo-dark.svg`
- Be descriptive: `practice-meditation-card.webp`

---

## Priority List

### High Priority (Needed Now)
1. ✅ Hero main background (already exists: `hero-meditation.png`)
2. Tarot card back cover
3. Default avatar
4. Logo SVG
5. Favicon set
6. Astrology icons (sun, moon, rising)

### Medium Priority
1. Practice category icons
2. Pattern card images
3. Empty state illustrations
4. Background patterns

### Low Priority (Can be added later)
1. Zodiac avatars
2. Promotional banners
3. Pattern decorative images

---

## Notes

- All images should align with the "slowlife aesthetic": soft, warm, minimal
- Avoid heavy decorative elements
- Prefer subtle textures over bold patterns
- Maintain consistency in color palette (warm tones, muted colors)
- Use SVG for icons and simple illustrations
- Use WebP for photographs and complex images
- Provide fallbacks (PNG/JPG) for older browsers


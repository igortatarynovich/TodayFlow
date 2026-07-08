# Image Specifications Summary

Quick reference guide for image requirements across the application.

## Priority Levels

### 🔴 High Priority (Create First)
1. **Tarot deck (Waite-Smith PNGs)** — `public/images/cards/tarot/` (192×320px, see layout below)
2. **Default avatar** - `avatars/avatar-default.svg` (64x64px)
3. **Logo SVG** - `logos/logo-todayflow.svg` (scalable)
4. **Favicon set** - `logos/favicon.*` (16x16, 32x32, 180x180px)
5. **Astrology icons** - `icons/astrology/*.svg` (sun, moon, rising, 24-48px)

### 🟡 Medium Priority
1. **Practice icons** - `icons/practices/*.svg` (32x32px)
2. **Category icons** - `icons/categories/*.svg` (24x24px)
3. **Empty state illustrations** - `placeholders/empty-*.svg` (200x200px)
4. **Hero background optimization** - Current `hero-meditation.png` → WebP

### 🟢 Low Priority (Can Wait)
1. Pattern card images
2. Practice card previews
3. Zodiac avatars
4. Promotional banners
5. Background patterns

---

## Tarot deck layout (`public/images/cards/tarot/`)

Source of truth: `frontend/src/lib/tarotCardAssets.ts`. Full deck = **79 PNG files** (78 faces + back).

```
tarot/
  Back_web.png
  Major Arcana/
    0.png … 21.png          # The Fool … The World
  Suit of Wands/
    1.png … 14.png
  Suit of Cups/
    1.png … 14.png
  Suit of Swords/
    1.png … 14.png
  Suit of Pentacles/
    1.png … 14.png
  tarot_cards_metadata.json
```

If PNGs are missing locally, `TarotCardImage` and `CardVisual` show text/emoji fallbacks — no broken-image icons.

---

| Type | Desktop | Tablet | Mobile | Format |
|------|---------|--------|--------|--------|
| Hero Background | 1920x1080 | 1200x800 | 800x600 | WebP |
| Tarot Card | 300x500 | 300x500 | 250x417 | WebP |
| Practice Card | 400x300 | 350x263 | 300x225 | WebP |
| Banner CTA | 1200x300 | 1000x250 | 800x200 | WebP |
| Avatar | 128x128 | 96x96 | 64x64 | SVG |
| Icon (Large) | 48x48 | 40x40 | 32x32 | SVG |
| Icon (Small) | 24x24 | 24x24 | 24x24 | SVG |
| Logo | 120x40 | 100x33 | 80x27 | SVG |
| Favicon | 32x32 | 32x32 | 32x32 | PNG/ICO |

---

## Format Guidelines

### Use WebP for:
- Photographs
- Complex images
- Card images
- Backgrounds
- Banners

### Use SVG for:
- Icons (all icons should be SVG)
- Logos
- Illustrations
- Patterns
- Simple graphics

### Use PNG for:
- Favicons (fallback)
- Images requiring transparency (if WebP not available)

---

## Color Palette Reference

All images should align with the slowlife aesthetic:

- **Background**: #FAF9F7 (warm light gray)
- **Card**: #FFFFFF (white)
- **Card Warm**: #FEFCF9 (warm white)
- **Mist**: #F8F6F3 (very light gray)
- **Primary Accent**: Deep graphite/ink tones
- **Secondary Accent**: Bronze/copper (#B87333)
- **Muted**: #6B7280 (slate gray)

---

## Optimization Checklist

- [ ] Images compressed for web
- [ ] WebP format used (with fallbacks)
- [ ] SVG icons optimized (paths cleaned)
- [ ] Appropriate file sizes (< 200KB for large images)
- [ ] Responsive sizes provided (or srcset)
- [ ] Alt text prepared for accessibility
- [ ] Lazy loading considered (below-fold images)

---

## Next Steps

1. Create high-priority images first
2. Test images in actual components
3. Optimize file sizes
4. Add responsive variants if needed
5. Document any deviations from specs


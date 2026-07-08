# Card Images

## Structure

```
cards/
├── tarot/        # Tarot card images
├── patterns/     # Pattern visualization cards
└── practices/    # Practice preview cards
```

---

## Tarot Cards (`/tarot/`)

Фронтенд подключает ассеты из кода (`src/lib/tarotCardAssets.ts`):

- **Рубашка:** `Back_web.png` в корне `tarot/` (192×320, тот же визуал на вебе и в iOS через `WEB_BASE_URL`).
- **Старшие арканы (id 0…21 из API):** `Major Arcana/0.png` … `Major Arcana/21.png`.
- **Младшие арканы:** папки `Suit of Wands`, `Suit of Cups`, `Suit of Swords`, `Suit of Pentacles` с файлами `1.png`…`14.png` — в UI пока не сопоставлены (в API только major); при добавлении младших в бэкенд расширить `tarotCardFaceSrc`.

Рекомендуем позже переименовать файлы без пробелов (например `tarot-card-back.webp`) и по возможности **WebP** для меньшего веса.

---

## Pattern Cards (`/patterns/`)

### Required
- Pattern visualization cards for A1-A7 axes:
  - `pattern-a1.webp` - Ориентация идентичности
  - `pattern-a2.webp` - Эмоциональная обработка
  - `pattern-a3.webp` - Принятие решений
  - `pattern-a4.webp` - Стабильность и изменения
  - `pattern-a5.webp` - Ориентация контроля
  - `pattern-a6.webp` - Реляционная ориентация
  - `pattern-a7.webp` - Управление энергией

- **Size**: 400x300px (4:3 ratio)
- **Usage**: Pattern cards on Discover page
- **Style**: 
  - Abstract, symbolic
  - Represent the essence of each pattern
  - Minimal, elegant
  - Consistent visual language
- **Format**: WebP
- **Note**: These can be added later if needed, pattern cards work fine without images

---

## Practice Cards (`/practices/`)

### Optional
- Practice preview images:
  - `practice-meditation.webp`
  - `practice-breathing.webp`
  - `practice-gratitude.webp`
  - etc.

- **Size**: 400x300px (4:3 ratio)
- **Usage**: Practice card previews (optional enhancement)
- **Style**: 
  - Calm, meditative
  - Related to practice theme
  - Not distracting
- **Format**: WebP
- **Note**: Practices work fine without images, these are optional enhancements

---

## General Guidelines

- **Aspect Ratios**: Maintain consistent ratios across card types
- **Optimization**: All images should be web-optimized
- **File Size**: Keep under 100KB per image when possible
- **Responsive**: Consider providing 2x versions for retina displays
- **Naming**: Use descriptive, kebab-case names


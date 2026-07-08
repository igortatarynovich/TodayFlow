# Background Images and Patterns

## Page Backgrounds

### Main Page Background
- **Files**: `bg-page-light.webp`, `bg-page-warm.webp`
- **Size**: 1920x1080px, tileable
- **Usage**: Subtle page backgrounds (optional, current CSS colors work fine)
- **Format**: WebP
- **Style**: 
  - Very subtle texture
  - Warm tones (#FAF9F7 palette)
  - Not distracting
  - Seamlessly tileable
- **Note**: Currently using CSS background colors, images are optional enhancement

## Pattern Backgrounds (SVG)

### Grain/Noise Pattern
- **File**: `pattern-grain.svg`
- **Size**: Tileable SVG (100x100px repeat)
- **Usage**: Subtle grain overlay (currently implemented via CSS `body::before`)
- **Opacity**: 5-10% when applied
- **Style**: Paper-like texture, very subtle
- **Format**: SVG

### Grid Pattern (Optional)
- **File**: `pattern-grid.svg`
- **Size**: Tileable SVG
- **Usage**: Subtle grid overlay (if needed)
- **Format**: SVG

## Gradient Overlays

### Hero Overlays
- **Files**: 
  - `overlay-gradient-warm.svg`
  - `overlay-gradient-soft.svg`
- **Size**: SVG (scalable, full coverage)
- **Usage**: Overlay effects on hero sections (currently using CSS gradients)
- **Format**: SVG
- **Note**: Currently using CSS gradients, SVG overlays optional

## Guidelines

- **Subtlety**: Backgrounds should never distract from content
- **Performance**: Keep file sizes small
- **Tileability**: Patterns should tile seamlessly
- **Color Consistency**: Match brand palette (#FAF9F7, warm tones)
- **Current Implementation**: Most backgrounds are CSS-based, images are optional enhancements


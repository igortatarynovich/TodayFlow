# Logos and Branding

## Required Files

### 1. Main Logo
- **File**: `logo-todayflow.svg`
- **Size**: Scalable SVG
- **Minimum Size**: 120x40px (for header)
- **Usage**: Main logo in header, footer, landing page
- **Format**: SVG (primary), PNG fallback
- **Variants**:
  - `logo-todayflow.svg` - Default (dark text on light background)
  - `logo-todayflow-light.svg` - Light version (for dark backgrounds)
  - `logo-todayflow-dark.svg` - Dark version (for light backgrounds)

### 2. Logo Mark (Icon Only)
- **File**: `logo-mark.svg`
- **Sizes**: 
  - 32x32px (favicon, small spaces)
  - 48x48px (app icons)
  - 64x64px (larger displays)
- **Usage**: 
  - Favicon
  - App icon
  - Small logo spaces
  - Loading states
- **Format**: SVG (scalable)

### 3. Favicon Set
- **Files**:
  - `favicon.ico` - Traditional favicon (16x16px, 32x32px, 48x48px)
  - `favicon-16x16.png` - 16x16px PNG
  - `favicon-32x32.png` - 32x32px PNG
  - `apple-touch-icon.png` - 180x180px (iOS)
  - `favicon.svg` - Modern SVG favicon (browser support)

### 4. Social Media Assets (Optional)
- **Files**:
  - `og-image.jpg` - 1200x630px (Open Graph)
  - `twitter-card.jpg` - 1200x600px (Twitter Card)
  - `social-icon.svg` - For social media profiles

## Style Guidelines

- **Aesthetic**: Align with "slowlife" brand
- **Typography**: If includes text, use brand font
- **Colors**: Use brand palette (warm tones, muted colors)
- **Simplicity**: Clean, minimal, recognizable
- **Scalability**: Must work at very small sizes (favicon)

## Usage in Code

```tsx
// Header
<Image src="/images/logos/logo-todayflow.svg" alt="TodayFlow" width={120} height={40} />

// Favicon (in layout.tsx or _document.tsx)
<link rel="icon" href="/images/logos/favicon.ico" />
<link rel="icon" type="image/svg+xml" href="/images/logos/favicon.svg" />
<link rel="apple-touch-icon" href="/images/logos/apple-touch-icon.png" />
```


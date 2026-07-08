# Avatar Images

## Required

### Default Avatar
- **File**: `avatar-default.svg`
- **Sizes**: 
  - 64x64px (standard)
  - 128x128px (large profile)
- **Usage**: Default user avatar when no custom avatar is set
- **Format**: SVG (scalable)
- **Style**: 
  - Simple, friendly
  - Generic person silhouette or initial placeholder
  - Consistent with brand aesthetic

### Avatar Placeholder (Initials)
- **Usage**: Generated from user's first letter of email
- **Note**: Currently implemented in code, no image needed

## Optional (Future)

### Zodiac Sign Avatars
- **Files**: `avatar-aries.svg`, `avatar-taurus.svg`, etc. (12 signs)
- **Size**: 64x64px base
- **Usage**: Optional zodiac sign representation for users
- **Format**: SVG
- **Style**: Minimal, symbolic representation of each sign

## Guidelines

- **Format**: SVG preferred for scalability
- **Style**: Minimal, clean, not distracting
- **Size**: Always square aspect ratio
- **Fallback**: Code should handle missing images gracefully


repo: igortatarynovich/TodayFlow
branch: main

## Last sync
date: 2026-08-08T17:51:07Z

### Updated in this project
- Read tokens, typography and component source under `frontend/src/design-system/`, `frontend/src/styles/`, `frontend/src/components/`.
- Copied real icon sets (zodiac, planets, elements, archetypes), decorative SVGs, tarot card art, archetype illustrations and cosmic imagery from `frontend/public/images/`.
- Built token CSS, foundation specimen cards, 12 component families, and two UI kits (marketing landing page, Today product screen) from the real source.

## Screen map
| Design system screen | Repo files |
|---|---|
| tokens/colors.css, typography.css, spacing.css, effects.css | frontend/src/styles/todayflow-foundation.css, frontend/src/styles/globals/01-tokens-base.css |
| components/primitives/* | frontend/src/design-system/primitives/* |
| components/patterns/* | frontend/src/design-system/patterns/* |
| components/icons/DsIcons | frontend/src/design-system/icons/DsIcons.tsx |
| ui_kits/marketing-site | frontend/src/components/product-ui/ProductWebLanding.tsx, productWebLandingContent.ts |
| ui_kits/product-app | frontend/src/components/today/*, frontend/src/design-system/patterns/DsChrome.tsx |
| assets/icons, assets/tarot, assets/illustrations, assets/imagery | frontend/public/images/icons/*, frontend/public/images/cards/tarot/*, frontend/public/images/archetypes/*, frontend/public/images/cosmic/* |

# TodayFlow Design System

TodayFlow is a daily-guidance app blending astrology, tarot, numerology and short reflective practices into one personal "Today" ritual — a morning theme, a focus, and an evening close, remembered day to day rather than reset each time. The company runs two connected surfaces on the same Next.js codebase: **todayflow.today** (marketing/editorial) and **todayflow.app** (the signed-in product — Today, Profile, Tarot, Compatibility, Practices). Native iOS/Android clients mirror the same product model.

Source: [github.com/igortatarynovich/TodayFlow](https://github.com/igortatarynovich/TodayFlow) (`frontend/` Next.js app, `backend/` FastAPI, `astro/` Swiss-Ephemeris microservice, `docs/` product canon). Explore it directly for anything this system simplifies — full component source, the astrology/numerology content model, and the bilingual (RU-primary, EN-fallback) copy system all live there.

**Note on language:** the live product's primary copy is Russian, with English fallback strings in code. This design system is written in English (using those fallback strings) for portability; real screens should be checked against `frontend/src/lib/i18n` for exact RU copy.

**Note on fonts:** `tokens/fonts.css` loads the same Google Fonts families the product self-hosts via `next/font/google` (Instrument Serif, Playfair Display, Cormorant Garamond, Lora, Manrope, Inter, Caveat) through a CDN `@import` rather than shipped font files — swap in self-hosted `@font-face` files if you need offline builds.

**Note on the logo:** no logo file was found in the source repo (its own `logos/README.md` lists one as still-required). Every screen here renders the wordmark "TodayFlow" in the display serif instead of a mark — replace with a real logo file when the brand ships one.

## Content fundamentals

- **Voice:** second person, warm and direct, never mystical-vague. Copy names the mechanism ("Mercury's angle favors writing before calling") rather than hiding behind horoscope-speak.
- **Structure over prophecy:** the product explicitly avoids "prediction" framing — Today is described as "not a prediction, a story that remembers yesterday." Interpretive copy separates **Observation → Interpretation → Context** as three distinct trust layers.
- **No invented testimonials.** Product docs explicitly ban fake reviews with invented names/titles — "why people come back" copy is written as product reasoning, not social proof.
- **Casing:** sentence case almost everywhere; uppercase is reserved for small eyebrow/label chips and primary button text (letter-spaced).
- **Emoji:** none in UI copy. The only non-Latin glyphs are astrological symbols (☉ ☽) referenced in docs, rendered as line icons, not emoji.
- **Mantras:** short italic script-font phrases ("Pause · Sense · Integrate") appear as rare accents in footers/rail navigation — never as body copy.

## Visual foundations

- **Palette:** warm parchment/cream surfaces (`--tf-page`, `--tf-page-cream`), a five-role ink system (primary / secondary / quiet / accent / action — deliberately capped at five, never a sixth), one gold accent (`--tf-accent-gold`) for CTAs and highlights, and one warm peach→terracotta gradient reserved for the Today capsule CTA. Semantic colors (gift/trap/grow/alert/error) are muted, never saturated.
- **Type:** serif display family (Instrument Serif / Playfair Display / Cormorant Garamond) for titles and editorial moments, a calm sans (Manrope/Inter) for body copy, and a script accent (Caveat) used only for mantras.
- **Backgrounds:** flat warm color, not photography-led. A very faint (3% opacity) repeating paper-grain texture sits over page backgrounds (never over cards) for a journal/artbook feel. No aggressive gradients outside the one CTA gradient; no illustrated patterns.
- **Imagery:** real product photography is soft-focus, warm-toned "meditation/journal" lifestyle shots (see `assets/imagery/`), plus a dedicated cosmic/celestial image set (moon, nebula, star field, zodiac map) and painterly archetype portraits (Sage, Creator, Hero, Seeker…) used in Profile/Discover.
- **Motion:** slow and rare — 150–420ms, ease-out/ease-in-out only, fade + slide-up, no bounce or spring.
- **Hover/press:** primary buttons lift 1px and gain a soft gold glow on hover; no color inversion. No distinct press/shrink treatment is defined in source — buttons rely on the hover lift plus native `:active` opacity.
- **Corners:** soft throughout — 16–40px radii for cards, full pill (`999px`) capsules for every button and chip. No sharp corners anywhere in the UI.
- **Cards:** warm-white or cream fill, 1px hairline border (`--tf-border-ink`/`--tf-border-gold`), soft warm shadow (never a hard drop shadow), no colored left-border accent except the one intentional "feature" card variant and callout rails (see below).
- **Callouts:** thin 3px left rail + soft tint wash, toned by meaning (insight/practice/help/avoid) — this is the system's one "rail" motif, used specifically for interpretive copy, not as a generic card decoration.
- **Transparency/blur:** glass surfaces (backdrop-blur + translucent white) appear specifically for "Today block" panels sitting over atmospheric backgrounds — not used generally.
- **Dark mode:** a genuine dark theme exists for the evening/"close of day" and Profile-journey moments — deep near-black surfaces, gold remains the only warm accent.
- **Day Atmosphere moods:** the mobile Today flow uses 8 mood-driven radial-gradient backgrounds (Grounded, Flow, Radiance, Momentum, Clarity, Renewal, Tension, Depth — the last two dark-surface) scaled by time-of-day intensity factors, with frosted glass cards on top. See `tokens/day-atmosphere.css` and `components/patterns/DsRitual.jsx`.

## Iconography

- **No icon font.** Icons are hand-authored inline SVGs, 1.5px stroke, `currentColor`, on a 24×24 viewBox — see `components/icons/DsIcons.jsx` for the nav/domain glyph set.
- **Real purchased/product icon sets** are shipped as flat SVG files, copied verbatim into `assets/icons/`: zodiac signs (12), planets (10), classical elements (4), and personality archetypes (13) — all `currentColor`, swappable.
- **No emoji, no unicode glyphs as icons** in the product UI.
- **Tarot** ships real card art (major arcana + card back) — see `assets/tarot/`.
- **Illustrations:** painterly archetype portraits (webp) — see `assets/illustrations/archetypes/`.

## Intentional additions

- `DsIconButton` — a small circular icon-only button variant; the source only defines pill buttons, but avatar/settings triggers in real screens are circular, so this wraps that pattern explicitly.

## Index

- `styles.css` — the single global stylesheet entry point (imports everything below).
- `tokens/` — colors, typography, spacing, effects (shadow/motion/grain), fonts.
- `assets/` — icons (zodiac, planets, elements, archetypes), decorative SVGs, tarot card art, archetype illustrations, cosmic/hero imagery.
- `guidelines/` — foundation specimen cards (Colors, Type, Spacing, Brand) shown in the Design System tab.
- `components/primitives/` — DsButton, DsCard, DsTypography, DsCallout, DsForm.
- `components/patterns/` — DsChrome (nav/sidebar/header), DsMobile (ritual gates, tab bar), DsTiles, DsRailWidgets, DsThemePanel, DsRitual (mood backgrounds, glass cards, carousel nav, chip groups — from the mobile Today flow prototype).
- `components/icons/` — DsIcons, the hand-drawn glyph set.
- `components/layouts/` — DsLayouts (marketing page/section shells, app shell).
- `ui_kits/marketing-site/` — recreation of the todayflow.today landing page.
- `ui_kits/product-app/` — recreation of the signed-in Today + Tarot product screens.
- `SKILL.md` — Claude-Code-compatible skill wrapper for this design system.

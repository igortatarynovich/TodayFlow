# Handoff: TodayFlow Design System

## Overview
Full design-system handoff for TodayFlow, a daily-guidance app (astrology, tarot, numerology, reflective practices). Covers marketing site (todayflow.today) and product app (todayflow.app) surfaces, plus native iOS/Android parity notes.

## About the Design Files
The files in this bundle are **design references built in HTML/JSX** — component specimens and screen recreations showing intended look, tokens, and behavior. They are not production code to import as-is. The task is to **recreate these designs in TodayFlow's existing codebase** (Next.js frontend — see `github.md` for the source repo) using its established libraries and patterns, matching this system pixel-for-pixel.

`.jsx` files under `components/` and `ui_kits/` use a custom template runtime (`x-import`, `dc-import`, `.d.ts` prop contracts) specific to this design tool — treat them as **prop/behavior specs**, not importable React source. Rebuild each as a real component in the target stack.

## Fidelity
**High-fidelity.** Final colors, typography, spacing, radii, shadows, and motion timings are all defined as tokens (see below) and used consistently across every specimen and screen.

## Source of truth
Real repo: `github.com/igortatarynovich/TodayFlow` (`frontend/` Next.js, `backend/` FastAPI, `astro/` Swiss-Ephemeris microservice, `docs/`). Check `frontend/src/lib/i18n` for exact Russian copy — this system's text uses the English fallback strings for portability.

## Design Tokens
All tokens are plain CSS custom properties in `tokens/` (imported by `styles.css`):
- `tokens/colors.css` — warm parchment surfaces, 5-role ink system (primary/secondary/quiet/accent/action — never a 6th), one gold accent, peach→terracotta CTA gradient, semantic colors, callout rails/washes, heatmap intensities, full dark-theme override block (`[data-theme="dark"]`).
- `tokens/typography.css` — serif display stack (Instrument Serif / Playfair Display / Cormorant Garamond), sans body (Manrope/Inter), script accent (Caveat); full size/line-height/weight scale.
- `tokens/spacing.css` — spacing scale, radii (16–40px cards, 100px pill), shell/sidebar/rail widths, breakpoints.
- `tokens/effects.css` — shadows (soft/warm, never hard), motion durations/easings (150–420ms, ease-out/ease-in-out only, no bounce), paper-grain overlay (`.tf-grain`, 3% opacity, page backgrounds only — never cards).
- `tokens/fonts.css` — Google Fonts `@import` for all typefaces (swap for self-hosted `@font-face` in production/offline builds — the live product self-hosts via `next/font/google`).

## Components
- `components/primitives/` — Button, Card, Typography, Callout, Form. Each has a `.d.ts` prop contract, `.jsx` reference implementation, `.prompt.md` notes, and a `.card.html` live specimen.
- `components/patterns/` — Chrome (nav/sidebar/header), Mobile (ritual gates, tab bar), Tiles, RailWidgets, ThemePanel, Ritual (mood backgrounds, glass cards, carousel nav, chip groups).
- `components/icons/` — DsIcons, hand-drawn 24×24 stroke glyph set (1.5px stroke, currentColor).
- `components/layouts/` — marketing page/section shells, app shell.
Read each `.prompt.md` alongside its `.d.ts` for intended props, states, and usage notes before reimplementing.

## Screens
- `ui_kits/marketing-site/index.html` + `LandingPage.jsx` — todayflow.today landing page recreation.
- `ui_kits/product-app/index.html` + `TodayScreen.jsx` — signed-in Today product screen recreation.

## Visual & Content Rules (see `design-system-readme.md` for full detail)
- Voice: second person, warm, direct — names the mechanism, never vague horoscope-speak. No invented testimonials.
- Sentence case everywhere except eyebrow labels and primary button text (uppercase, letter-spaced).
- No emoji, no icon fonts — inline SVG only.
- Flat warm backgrounds, no photography-led heroes, no aggressive gradients outside the one CTA gradient.
- Cards: warm-white/cream fill, 1px hairline border, soft warm shadow, soft radii — no colored left-border accents except callouts and one feature-card variant.
- Motion: slow, rare, fade + slide-up only.
- 8 mood-driven "Day Atmosphere" radial-gradient backgrounds for the mobile Today flow — see `tokens/day-atmosphere.css` and `components/patterns/DsRitual.jsx`.

## Assets
- `assets/icons/` — zodiac (12), planets (10), elements (4), archetypes (13) SVGs, `currentColor`, swappable.
- `assets/decorative/` — compass, divider, north-star, orbit, solar-rays, vignette SVGs.
- `assets/illustrations/archetypes/` — painterly archetype portraits (webp).
- `assets/imagery/` and `assets/tarot/` — cosmic/hero imagery and tarot card art (webp/png).
- No logo file exists in the source repo yet — every screen renders the wordmark "TodayFlow" in the display serif as a placeholder.

## Files in this package
```
design-system-readme.md   full design-system documentation (source of truth for rules above)
github.md                  source repo reference (repo, branch, sync history)
styles.css                 global stylesheet entry point
tokens/                    all design tokens
components/                primitive + pattern component specs
guidelines/                foundation specimen pages (colors, type, spacing, brand)
ui_kits/                    full-page screen recreations (marketing site, product app)
```

# Handoff: TodayFlow — «Today» daily-flow redesign

## Overview
Redesign of the `/today` daily ritual: a 12-step guided flow (greeting → day setup → the existing "Поток дня" story → closing the day) plus a real Day Atmosphere (8 modes × time-of-day) driving background/decor across the flow. Goal: make opening the app itself feel like the reward, on top of the existing content.

## About the design file
`prototype/TodayFlow-Potok-Dnya.dc.html` is an **HTML design reference** — a clickable prototype, not production code. It is now built directly against the **TodayFlow Design System** (the canonicalized token + component library, attached to this project) rather than ad-hoc hex approximations — the CSS custom properties referenced below (`--tf-mood-*`, `--tf-accent-gold-600`, `--tf-glass-*`, `--tf-font-display`/`--tf-font-body`) are the design system's real tokens and should map 1:1 to production. Implement this in the existing Next.js/React app (`frontend/src/`), using the existing design-system primitives (`DsButton`, `DsCard`, and the newer `DsRitual` pattern set — `DsMoodBackground`, `DsGlassCard`, `DsCarouselDots/Arrow`, `DsChipGroup`, `DsHabitStreakRow`, `DsBottomTabBar` — which the design system now documents specifically for this mobile Today-ritual flow) wherever a primitive already covers the job — per `docs/TODAYFLOW_FOUNDATION_UI.md` §15, ad-hoc CSS buttons/cards are prohibited in this codebase.

Open the HTML file directly in a browser to click through all 12 steps and both demo controls (atmosphere mode row, time-of-day row) above the phone frame — those two rows are prototype-only scaffolding, not part of the real UI.

## Fidelity
**High-fidelity for layout, step order, copy, interaction logic, AND tokens.** The prototype now consumes the design system's actual CSS custom properties directly (no hardcoded hex standing in for tokens) — colors, radii, and type all resolve through `--tf-*` variables at render time. One remaining gap:
1. Three image slots (welcome hero photo, practice photo, tarot card art) are drag-and-drop placeholders in the prototype — real assets come from existing `/images/backgrounds/` and the tarot asset pipeline (`build-tarot-assets.py` / `frontend/public/images/cards/`).

## Screens / steps (in order)
1. **Приветствие (Welcome)** — full-bleed photo, greeting ("Добрый день, {name}"), a compact glass card summarizing today's energy (2 mood tags + reason + 3 "good for" chips — NOT a paragraph), CTA "Начать день" → step 2. No dots/arrows shown (single explicit CTA is the only way forward).
2. **Приоритет** — "Что тебе сейчас важнее всего?" — 6 two-line info-cards (label + sub-label) in a 2-col grid, single-select. Secondary link "Разобрать тему (сферу) точнее →" (unwired — flag as TODO/next iteration).
3. **Обещание** — "Какое обещание ты хочешь дать себе сегодня?" — 3 selectable long-text rows + "Написать своё" (opens a free-text field — currently a placeholder box, needs a real `DsTextField`).
4. **Сделай день своим** — 3 category cards (Практика / Аскеза / Привычка). Tapping a category expands an inline accordion of 3 concrete options (single-select per category, persists as a short label on the card). Below that, a **"Твой прогресс"** tracker: 3 rows (name, kind, current streak, 7-day dot history) — this needs real backend-tracked habit/practice/ascesis data, the prototype uses static example rows.
5. **Поток дня** — existing timeline content (see `TODAY_SCREEN_SCENARIO_V3` if it covers this act already). Each time-anchored row is tap-to-expand (accordion reveals a "why/what for" detail line); phase markers (УТРО/ВЕЧЕР) are not expandable.
6. **Число дня (ritual)** — closed state: a ring of 9 unlabeled circular slots arranged evenly (CSS trig positioning, not SVG) around a 220×220 area, tap any → reveals the actual number/value regardless of which slot was tapped (the tap is a ritual gesture, not a real random pick). Reveal cascades automatically: value card (immediate) → "Значение" card (+700ms) → "Опора дня" card (+1500ms), each fading in.
7. **Карта дня (ritual)** — same pattern: closed state shows 3 stacked card-back rectangles (deck), tap anywhere on the deck → reveals card art (image slot, correct 3:5 tall aspect — do not let this become a landscape crop) → cascades to "Значение" then a **"Для тебя сегодня"** block that cross-references the day's number (personalization: "При числе дня 8 (Управленец) эта карта — …"). This cross-referencing pattern (tarot × numerology × user profile) should generalize — check if `character_engine` / `compatibility` services already expose a combine-signals hook.
8. **Цвет дня** — color swatch circle + name + intensity + 4 labeled rows (в одежде / аксессуар / сколько / лучше избегать). This step existed in the old flow and must not be dropped — it was accidentally lost once during this session's iteration.
9. **Фокус дня** — title + "В приоритете" / "Лучше избегать" two-card pair.
10. **Практика дня (gift)** — full-bleed photo, framed explicitly as a gift/help, not a generic list item: eyebrow "Практика дня · подарок на сегодня", a specific named practice ("5 минут тишины") with instructions, one CTA ("Начать практику · 5 минут") that toggles to a "started" confirmed state, plus a secondary link to configure other practices/habits.
11. **Переход к итогу (recap)** — a connecting frame before closing: recaps what was set earlier (priority / promise / practice started), so "Закрыть день" doesn't feel disconnected from the rest of the flow.
12. **Закрыть день** — day-summary line → "Закрыть день" CTA → inline outcome picker (Получилось/Частично/Не получилось, single-select, no modal/bottom-sheet duplicating the same copy twice) → confirmation checkmark line.

## Interactions & behavior (explicit product decisions made this session)
- Navigation is **bidirectional**: swipe (pointer down/up delta >60px), left/right arrow buttons anchored to the phone frame (not per-step content, so they don't drift vertically with content height), and tapping a pagination dot jumps directly to that step.
- Pagination dots are **grouped into 3 visual clusters** with a gap between them, matching 3 acts: "Оформим день" (steps 2–4), the existing "Поток дня" narrative (steps 5–9), "Итог" (steps 11–12). Welcome (step 1) has no dots — its only exit is the CTA.
- Every step must fill its available vertical space without a large empty void before the bottom nav — content that doesn't naturally fill the screen uses `margin: auto 0` on its wrapper (auto-margin vertical centering — safe with `overflow-y: auto`, unlike `justify-content: center` which can clip overflowing content).
- Chip/card selection after choosing both fields in a two-part question **auto-advances** (no separate "continue" button) — see the original heart/mood pattern discussion; currently only applied within single-question steps.
- The bottom service nav (Я сегодня / Моя карта / Совместимость / Таро / Практики) is **always visible**, including on full-bleed photo steps (Welcome, Practice) — it sits outside the scrollable content area, not inside it.
- "Число дня" and "Карта дня" are **rituals**, not static info cards: closed/hidden state → single tap draws → staged auto-reveal (value → meaning → personalized context), each stage fading in over ~700ms increments.

## Day Atmosphere (background system)
This is the existing `frontend/src/lib/dayAtmosphere.ts` contract (`docs/TODAYFLOW_FOUNDATION_UI.md` §11–§13), now canonicalized in the design system as `tokens/day-atmosphere.css` plus the `DsRitual` pattern's `DsMoodBackground`/`DsGlassCard` components. The prototype consumes those tokens directly (8 moods × a simple time-of-day intensity multiplier — morning ×1.15, day ×1, evening ×0.92, night ×0.8 — applied as a CSS `filter: saturate()/brightness()` stand-in for the real continuous `dayAtmosphereTokens()` computation). Two moods (tension, depth) are dark-background — ink/surface flip to light-on-dark; the other six stay dark-ink-on-light. Wire this to the REAL bridge (`DayAtmosphereBridge`) and `resolveDayAtmosphere()` engine output instead of the prototype's demo mode/phase buttons — those buttons exist only so the design could be reviewed across all 8×4 states in one file.

## Design tokens referenced
- Mood backgrounds: `--tf-mood-<mood>-bg`, `--tf-mood-<mood>-glow-a`, `--tf-mood-<mood>-glow-b`, `--tf-mood-<mood>-decor` for each of the 8 moods (grounded/flow/radiance/momentum/clarity/renewal/tension/depth), plus `--tf-glass-surface-light/dark`, `--tf-glass-border-light/dark`, `--tf-glass-blur` — see `tokens/day-atmosphere.css`.
- Core palette: `--tf-ink`, `--tf-ink-secondary`, `--tf-ink-quiet`, `--tf-on-dark`, `--tf-accent-gold`, `--tf-accent-gold-600`, `--tf-surface-warm`, `--tf-border` — see `tokens/colors.css`.
- Typography: `--tf-font-display` (Instrument Serif / Playfair Display / Cormorant Garamond) for titles, `--tf-font-body` (Manrope / Inter) for body copy — see `tokens/typography.css`.
- Radius: `--tf-radius-lg` (20px) for cards, `--tf-radius-pill` (100px) for chips/buttons/dots — see `tokens/spacing.css`. Glass cards use a fixed 22px radius matching the `DsGlassCard` pattern component.
- Spacing: prototype still uses raw px for this mobile-shell layout (the `--tf-space-*` scale is tuned for marketing/desktop density) — developer should sanity-check against `--tf-space-*` where it fits.

## Assets
- Welcome photo, Practice photo, Tarot card art: drag-and-drop placeholders in the prototype (`<image-slot>` custom element, prototype-only tooling) — replace with real assets from `/images/backgrounds/` and the tarot pipeline.
- No hand-drawn SVGs used; all decorative shapes are CSS (circles, stripes, radial gradients).

## Files in this handoff
- `prototype/TodayFlow-Potok-Dnya.dc.html` — the full interactive prototype (open directly in a browser).
- `screenshots/` — static captures of the welcome screen and steps 2–6 (priority, promise, own-day, flow timeline, number ritual) for quick reference without opening the HTML.
- This README.

## Known gaps / explicitly flagged as unresolved in the design session
- "Разобрать тему (сферу) точнее" link (step 2) has no destination screen yet.
- "Написать своё" free-text (step 3) is a visual placeholder, not a real input.
- The habit/practice/ascesis tracker (step 4) uses static example data — needs real backend-tracked streak data.
- Day Atmosphere transition between acts is a basic CSS `transition`, not a true crossfade — revisit if it looks janky on real gradients in-browser.

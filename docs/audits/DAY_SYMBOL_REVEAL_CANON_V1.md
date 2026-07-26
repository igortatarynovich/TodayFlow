# Day Symbol Reveal Canon v1

**Status:** accepted — overlay + prebake clarified 2026-07-26

## Decisions

1. **Card** — system prebakes card identity at day assemble (`ensure_symbols_prebaked`); ritual reveal opens it (`POST /today/symbols/card/reveal`). Client pick is theater.
2. **Number** — system-calculated and prebaked from the user’s local date; revealed only by explicit action (`POST /today/symbols/number/reveal`).
3. **Registration gate** — after the first full personal result, CTA reason: «сохранить сегодняшний день и продолжить вечером».
4. **Weight** — card and number **complement** the base day story; they do **not** replace it and must **not** reassemble `day_story` / `day_scenario` (DAY_LIFECYCLE_V1 assemble-once).
5. **Date** — canonical day key is the user’s local date + timezone (client-supplied on reveal; stored on `day_symbol_states`).
6. **After reveal** — UI shows how this card/number may land on *this already assembled* day; `story_refresh_required` stays false (`symbol_overlay_only`). Content already on screen must not disappear.

## Server SoT

- Table: `day_symbol_states`
- Service: `day_symbol_state_v1` (`ensure_symbols_prebaked` on pre-warm)
- API: `/today/symbols/state`, `/card/reveal`, `/number/reveal`, `/claim`
- GET never creates/reveals/mutates.
- Morning / Today / Tarot / Numerology read the same reveal state (identity redacted until reveal).
- Day story fingerprint **excludes** revealed card/number (mood/goals/profile may still invalidate).

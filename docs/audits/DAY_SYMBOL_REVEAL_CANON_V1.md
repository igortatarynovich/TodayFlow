# Day Symbol Reveal Canon v1

**Status:** accepted product decisions for P0 leak closure (2026-07-20)

## Decisions

1. **Card** — user selects one of closed cards (`POST /today/symbols/card/reveal` with `card_id`).
2. **Number** — system-calculated from the user’s local date; revealed only by explicit action (`POST /today/symbols/number/reveal`).
3. **Registration gate** — after the first full personal result, CTA reason: «сохранить сегодняшний день и продолжить вечером».
4. **Weight** — card and number complement the base day story; they do not replace it.
5. **Date** — canonical day key is the user’s local date + timezone (client-supplied on reveal; stored on `day_symbol_states`).

## Server SoT

- Table: `day_symbol_states`
- Service: `day_symbol_state_v1`
- API: `/today/symbols/state`, `/card/reveal`, `/number/reveal`, `/claim`
- GET never creates/reveals/mutates.
- Morning / Today / Tarot / Numerology read the same reveal state.

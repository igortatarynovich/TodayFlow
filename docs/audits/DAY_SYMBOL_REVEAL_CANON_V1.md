# Day Symbol Reveal Canon v1

**Status:** accepted — overlay + prebake clarified 2026-07-26 · **hook_reveal layers** 2026-08-01

## Decisions

1. **Card** — system prebakes card identity **and orientation** at day assemble (`ensure_symbols_prebaked`); ritual reveal opens it (`POST /today/symbols/card/reveal`). Client pick is theater.
2. **Number** — system-calculated and prebaked from the user’s local date; revealed only by explicit action (`POST /today/symbols/number/reveal`).
3. **Registration gate** — after the first full personal result, CTA reason: «сохранить сегодняшний день и продолжить вечером».
4. **Weight** — card and number **complement** the base day story; they do **not** replace it and must **not** reassemble `day_story` / `day_scenario` (DAY_LIFECYCLE_V1 assemble-once).
5. **Date** — canonical day key is the user’s local date + timezone (client-supplied on reveal; stored on `day_symbol_states`).
6. **After reveal** — UI shows how this card/number may land on *this already assembled* day; `story_refresh_required` stays false (`symbol_overlay_only`). Content already on screen must not disappear.
7. **Color** — not a third reveal click; may still ride card reveal on API (`color_hook_reveal` / props). **Presentation house = Move only** (identity + intensity soft/bright + apply/avoid) — not Symbols. See [TODAY_SCREEN_SCENARIO_V3](../today/TODAY_SCREEN_SCENARIO_V3.md) v3.1.
8. **Ritual clicks** for card/number stay — ritual ≠ friction. Symbols·A keeps revealed content visible; Symbols·B (astro + full timeline) appends below — revealed never disappears.

## Product arc (Today)

```text
Сводка дня (2 сек) → Ритуал крючков → Раскрытие → Инструкция → Результат → Plot/Reading/Move
```

Glance (Screen 0) = short day overview — **not** four spheres as hero. Hooks (color / card / number) = center of daily return.

## `hook_reveal` layers (SoT)

```text
hook_reveal {
  kind: card | number | color
  identity: …                    # card: { id, orientation: upright|reversed }
  base: { meaning, keywords? }   # static lookup — never LLM
  bridge_to_day: string | null   # chorus / props only
  bridge_status: ok | unavailable
  personal_angle: string | omit  # deep only; gen atop bridge
  instruction: string | null     # gen atop base+bridge; not a second bridge
  instruction_status: ok | unavailable
  result_loop: tap | none
}
```

| Layer | Source | Rule |
|-------|--------|------|
| **base** | `card_base_v1` / `number_base_v1` / `COLOR_CATALOG_V1` | Static. Lookup only. Same bank for every tarot surface. |
| **bridge_to_day** | **Sole SoT:** `interpretive_chorus.day_card` / `.day_number` / `props.color.link_to_conflict` | Explainer must **not** invent a parallel bridge. |
| **personal_angle** | Gen when `profile_depth=deep` and `bridge_status=ok` | Omit otherwise. |
| **instruction** | Gen atop base+bridge when bridge ok | Not a rewrite of base. |

### Bridge-fail UX (acceptance)

When identity+base resolve but bridge is missing/failed:

- Show **identity + base** (honest stable fact).
- Explicit copy: **«Не удалось раскрыть день для этой карты/числа/цвета.»** (or transport «Не удалось загрузить.»).
- **No** silent empty under base; **no** calm/fallback prose; **no** explainer as spare bridge.

## Card base — one deck system-wide

- **78 cards × upright + reversed** — one bank (`card_base_v1`).
- Lookup: `(card_id, orientation)`.
- Consumers: day hooks, morning ritual, question spreads, library — **not** separate meaning dictionaries.
- Prebake orientation from the same deck (stable digest); FE must not force `upright`.

See [TAROT_CARD_BASE_V1.md](../tarot/TAROT_CARD_BASE_V1.md).

## Number / color base

- `number_base_v1` — values 1–9, masters **11/22/33** in use, karmic debts 13/14/16/19 as lookup; **44** documented `in_use=false` (see [NUMBER_BASE_V1.md](../numerology/NUMBER_BASE_V1.md)). Explainer + FE rhythm must not invent digit meaning outside this bank. Bogus FE key `20` removed (never emitted by BE `_reduce`).
- Color — `COLOR_CATALOG_V1.symbolic_property` (+ apply) as base; bridge = `props.color.link_to_conflict`.

## Server SoT

- Table: `day_symbol_states`
- Service: `day_symbol_state_v1` (`ensure_symbols_prebaked` on pre-warm)
- Projector: `hook_reveal_v1` (base lookup + chorus/props → bridge)
- API: `/today/symbols/state`, `/card/reveal`, `/number/reveal`, `/claim`
- GET never creates/reveals/mutates.
- Morning / Today / Tarot / Numerology read the same reveal state (identity redacted until reveal).
- Day story fingerprint **excludes** revealed card/number (mood/goals/profile may still invalidate).

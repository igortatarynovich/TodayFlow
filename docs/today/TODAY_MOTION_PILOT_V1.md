# Today — Motion as attention hierarchy (pilot)

**Status:** PILOT canon for **Today only** — not app-wide until TapWidget pilot proves the pattern.  
**Pairs with:** [TODAY_WAVE2_CONTRACT_V1.md](./TODAY_WAVE2_CONTRACT_V1.md) · [TODAY_WAVE2_EXECUTION_PLAN.md](./TODAY_WAVE2_EXECUTION_PLAN.md)

## Principles added

1. **Live-now is its own weak class.** GlanceTimeline “current time inside a window” is not “new result” and not “incomplete action”. Priority **below** all others (indicator, never accent).
2. **Motion always has a static equivalent.** Color / badge / icon carry meaning; breathe/glow only amplify. `prefers-reduced-motion` = turn off one CSS layer, not a second product path.
3. **Persistence lives beside `day_facts_v1`.** Use `today_ui_state` keyed by `day_facts_id`. Tap done = `tap_event_v1` exists.

```text
today_ui_state {
  day_facts_id: string
  hero_seen: bool
  card_opened: bool
  insight_seen: { [insight_id]: bool }
}
```

## Arbitration (priority high → low)

1. Incomplete user action (`attention`)
2. New personal result
3. State change / content reveal (`new`)
4. Live indicators & reward (never compete; self-extinguish)

## Today element table

| Element | Class | Trigger | User should | Accent duration | Clears when | Priority | Reduced-motion |
|---------|-------|---------|-------------|-----------------|-------------|----------|----------------|
| Act 1 hero theme | new | `hero_seen = false` | read theme | one enter ~1–1.5s | shown | 3 | static color accent |
| Act 2 card/number closed | attention | `card_opened = false` | open | breathe 4–8s loop | opened | 2 | static “new” badge |
| Act 2 card/number opened | completed → idle | open transition | — | confirm ~0.6–1s | transition done | — | static check |
| Personal insight (`why_personal`, deep only) | new | `insight_seen[id] = false` | read | one enter ~2–3s | seen | 3 | static atypical frame |
| GlanceTimeline active window | active (live) | now ∈ window | notice “now” | while in window | window ends | 4 | static “сейчас” |
| VerdictStrip | idle | — | scan | none | — | — | — |
| TapWidget / evening check-in | attention | in `practice_or_promise.window` (or evening) AND no tap yet | one tap | breathe 4–8s | `tap_event_v1` | **1** | static nav badge |
| TapWidget after answer | completed | event written | — | ~0.6–1s | reaction ends | — | static “учли” |

**Arbitration example:** evening, card still closed + check-in pending → only TapWidget breathes (1); card shows static “new”. After check-in, card may breathe (2) if still closed.

## Accessibility

- Breathe (scale ~1→1.01→1, soft glow) on 4–8s cycle — WCAG 2.3.1 safe by construction.
- Insight light-wave: **one** pass, never more often than once / ≥4s; no flicker loop.
- Real protection = static carrier of meaning + optional motion layer.

## Profile boundary

Profile / Core: at most one-shot `new` (e.g. unread Decode badge). **Never** attention-breathe.  
Today is the only surface allowed ambient breathe (daily / living layer).

## Pilot decision

**Pilot element: TapWidget (class 1, evening check-in).**

Reasons: already Phase A of Wave 2; one trigger / one action / one clear event; validates persistence + reduced-motion on the simplest case before card/insight.

After pilot: either promote this doc to app-wide motion canon (with explicit Profile inherit list) or revise classes from what failed on Tap.

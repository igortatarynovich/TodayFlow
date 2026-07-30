# Today — Motion as attention hierarchy

**Status:** **Today-only canon** (D.3 closed 2026-07-30). Not app-wide.  
**Pairs with:** [TODAY_WAVE2_CONTRACT_V1.md](./TODAY_WAVE2_CONTRACT_V1.md) · [TODAY_WAVE2_EXECUTION_PLAN.md](./TODAY_WAVE2_EXECUTION_PLAN.md)

## Principles

1. **Live-now is its own weak class.** GlanceTimeline “current time inside a window” is not “new result” and not “incomplete action”. Priority **below** all others (indicator, never accent).
2. **Motion always has a static equivalent.** Color / badge / icon carry meaning; breathe/glow only amplify. `prefers-reduced-motion` = turn off one CSS layer, not a second product path.
3. **Tap completion SoT is `tap_event_v1`.** Optional `today_ui_state` (hero/card/insight seen) stays beside `day_facts_id` when those surfaces get motion — not required for proven Tap + live-now.

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

| Element | Class | Status | Trigger | Accent | Clears when | Priority | Reduced-motion |
|---------|-------|--------|---------|--------|-------------|----------|----------------|
| TapWidget | attention | **PROVEN** | prompt present AND no tap yet | breathe ~6s | `tap_event_v1` | **1** | inset accent + static dot |
| TapWidget after answer | completed | **PROVEN** | event written | ~0.7s confirm | reaction ends | — | static “учли” |
| GlanceTimeline / nearest live | active (live) | **PROVEN** | now ∈ ±45m window | static «сейчас» | window ends | 4 | same static label |
| VerdictStrip | idle | **PROVEN** | — | none (valence color only) | — | — | — |
| Act 1 hero theme | new | backlog | `hero_seen = false` | one enter ~1–1.5s | shown | 3 | static color accent |
| Act 2 card/number closed | attention | backlog | `card_opened = false` | breathe 4–8s | opened | 2 | static “new” badge |
| Personal insight (`why_personal`) | new | backlog | `insight_seen[id] = false` | one enter ~2–3s | seen | 3 | static atypical frame |

**Arbitration:** if Tap attention is live, no other Today element may breathe. Live-now never competes.

## Accessibility

- Breathe (scale ~1→1.01→1, soft glow) on 4–8s cycle — WCAG 2.3.1 safe by construction.
- Insight light-wave (when built): **one** pass, never more often than once / ≥4s; no flicker loop.
- Real protection = static carrier of meaning + optional motion layer.

## Profile / other surfaces

Profile / Core: at most one-shot `new` (e.g. unread Decode badge). **Never** attention-breathe.  
Practices / ScreenFlow / Compat / Tarot: **out of scope** until a separate motion retro. ScreenFlow step change is navigation, not attention motion.

Today is the only product surface allowed ambient breathe (daily / living layer).

---

## D.3 retrospective (2026-07-30)

**Pilot element was TapWidget (class 1).** Code evidence:

| Check | Result |
|-------|--------|
| Attention breathe until tap | Yes — `tapAttention` / `tapBreathe` 6s; `data-tap-attention` |
| Clears on `tap_event_v1` | Yes — attention = `!answered` after POST |
| Completed confirm pulse | Yes — `tapCompleted` / `tapConfirm` ~0.7s |
| Reduced-motion static path | Yes — animation off; inset bar + dot |
| Live-now weak class (Glance) | Yes — «сейчас» / `data-live`; no breathe |
| VerdictStrip stays idle | Yes — valence color/sign only |
| Full `today_ui_state` hero/card/insight | **Not built** — deferred backlog rows above |

**Decision:** **Revise, do not promote app-wide.**

- Keep this doc as **Today-only** motion canon.
- Mark Tap + live-now + Verdict idle as **proven**.
- Leave hero/card/insight motion as **backlog** (optional; not a Wave 2 gate).
- Do **not** inherit attention-breathe on Profile or Practices.

**Next (D.4):** optional Act 4 if/then copy from `scenes[].recommended_action` — only if still needed after A–C; not blocked on motion.

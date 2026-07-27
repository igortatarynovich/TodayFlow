# Today Depth Layer (subscriber optional deepen)

**Status:** ACCEPTED (product principle · contract draft)  
**Date:** 2026-07-27  
**Parent:** [UNDERSTANDING_PROGRESS_AND_DEPTH_CANON.md](./UNDERSTANDING_PROGRESS_AND_DEPTH_CANON.md) · [PRODUCT_AVAILABILITY_MATRIX.md](./PRODUCT_AVAILABILITY_MATRIX.md) §3.2  
**Related:** existing `POST /today/narrative` surface `deepen` · DE-8 `depth_level`

## Architecture impact

```markdown
## Architecture impact
- **SoT before:** Free/Paid both get full Today day pack; deepen API exists but is not framed as
  optional subscriber layer; no explicit “never hide base day” Today rule for deepen topics
- **SoT after:** Base day = full for Free and Paid. Subscription adds an **optional second layer**
  the user chooses (franker tips / deeper analysis on a topic). Never grey-locks base content.
- **Public contract changed?** no (yet) — deepen topics may extend later (`intimacy` etc.)
- **Migration required?** no for principle; API/UI follow-up is a separate slice
- **Canon updated?** yes — this note + Availability Matrix §3.2 + Understanding Progress §4
- **Backward compatible?** yes — additive layer only
```

## Principle (locked)

1. **Full day for everyone with access to Today** — Free and Trial/Paid see a complete day story (scenes, do/avoid, spheres, symbols). Nothing essential is hidden behind a lock.
2. **Subscription = optional extra layer** — after the day is already useful, the user may deepen a topic they care about (money, intimacy/sex, relationships, work…).
3. **User chooses the focus** — not a second automatic plot competing with `day_story`.
4. **Depth kinds** (examples, not exclusives): more frank practical tips · deeper analysis · sharper `do` / `avoid` / `what_to_say` (or gesture). Still person-not-system voice.
5. **Trial = Paid depth** for this layer (same as Profile L3 rule).

## Forbidden

- Grey lock-cards on base Today chapters/scenes for Free  
- Chopping the day pack so Free feels incomplete  
- A second independent “premium day story” that replaces Free meaning  
- Paywall on reading the base conflict / scenes / primary action  

## Allowed

- Soft CTA: «Хотите глубже в деньги / близость / …?» with clear value  
- Free can see that deepen exists and what it unlocks; generating the **extra** pack is Trial/Paid  
- Existing DE-8 volume (`quick` / `normal` / `deep`) stays orthogonal (length), not a substitute for topic deepen  

## Topic menu (v1 draft)

| Topic id | User-facing job | Notes |
|----------|-----------------|-------|
| `money` | Практичнее про деньги / риск / решение | Aligns with domain `money_work` |
| `intimacy` | Откровеннее про близость / секс / тело | New vs current deepen enum (`love|money|career|family`); may reuse Profile tips DNA |
| `love` | Глубже про отношения / формулировки | Existing deepen topic |
| `career` | Глубже про работу / одно решение | Existing deepen topic |
| `family` | Глубже про дом / близкий круг | Existing deepen topic |

v1 ship set can be **2–4** of these; product picks the first menu. Default recommendation may follow active day spheres, but the user may override.

## Contract sketch (follow-up impl)

| Piece | Rule |
|-------|------|
| Base | `GET /today/contract` + day_story — **same** for Free and Paid |
| Offer | UI after day pack: topic chips (optional) |
| Gate | Trial/Paid: run deepen pack for chosen topic. Free: show value CTA → subscribe/trial (base day untouched) |
| Payload | Additive nest or narrative surface — **not** overwrite of `day_story.story` / scenes |
| Voice | Person-not-system; practical; no clinical diagnosis |

## Non-goals (this note)

- Hiding day_scenario chapters  
- Changing sphere auto-selection SoT  
- Implementing Stripe/UI in this doc alone  

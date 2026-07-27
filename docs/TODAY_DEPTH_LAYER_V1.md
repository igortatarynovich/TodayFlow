# Today Depth Layer (subscriber optional deepen)

**Status:** ACCEPTED · **impl step 1–3 LANDED** (gate · contract offer · FE picker)  
**Date:** 2026-07-27  
**Parent:** [UNDERSTANDING_PROGRESS_AND_DEPTH_CANON.md](./UNDERSTANDING_PROGRESS_AND_DEPTH_CANON.md) · [PRODUCT_AVAILABILITY_MATRIX.md](./PRODUCT_AVAILABILITY_MATRIX.md) §3.2  
**Related:** existing `POST /today/narrative` surface `deepen` · DE-8 `depth_level`  
**Code:** `today_depth_layer_v1.py` · gate in `api/today.py` `POST /narrative`

## Architecture impact

```markdown
## Architecture impact
- **SoT before:** deepen available to any signed-in user; no intimacy topic; no Free CTA shape
- **SoT after:** Free deepen → soft CTA payload (depth_layer.access=cta); Trial/Paid generates;
  topics include intimacy; base day unchanged
- **Public contract changed?** yes (additive) — `GET /today/contract.depth_layer`;
  deepen payload may include `depth_layer`; Free deepen → CTA (no LLM)
- **Migration required?** no — FE should render offer/CTA; picker UI = step 3
- **Canon updated?** yes — this note + SCREEN_CONTRACTS §3.3
- **Backward compatible?** yes — additive field; Free deepen text becomes CTA copy
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

## Contract sketch

| Piece | Rule | Status |
|-------|------|--------|
| Base | `GET /today/contract` + day_story — **same** for Free and Paid | unchanged |
| Topics | `money` · `intimacy` · `love` · `career` · `family` · `full_day` | **step 1** |
| Gate | Trial/Paid generate; Free → CTA payload | **step 1** |
| Offer menu | chips in `depth_layer.menu` | **step 1–2** (deepen response + `GET /today/contract`) |
| Today contract nest | expose offer without calling deepen | **step 2** |
| FE picker | chips after day pack | **step 3** |
| Payload | Additive `depth_layer` · **not** overwrite day_story | **step 1** |

## Non-goals (this note)

- Hiding day_scenario chapters  
- Changing sphere auto-selection SoT  
- Implementing Stripe/UI in this doc alone  

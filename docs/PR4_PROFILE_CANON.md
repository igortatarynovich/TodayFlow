# PR-4 Profile Canon (surface)

**Status:** **CLOSED** — slice 4.1 accepted (2026-07-21)  
**Version:** 1.2 (2026-07-21)  
**Code:** `frontend/src/components/profile/v2/` · `frontend/src/lib/profilePage/buildProfileV2LiveContext.ts`  
**Content pipeline:** [PROFILE_CONTENT_CANON_V1.md](./PROFILE_CONTENT_CANON_V1.md) (C3 — generation; this doc is UI/IA boundaries)  
**Screen legacy:** [PROFILE_SCREEN_MASTER.md](./PROFILE_SCREEN_MASTER.md) — v0 visual master; **production IA supersedes** Living-Maps-as-Profile-half (see §7 note there).
**Next stage:** [PROFILE_E2E_RECONSTRUCTION.md](./PROFILE_E2E_RECONSTRUCTION.md) — E2E + **Profile v1 Freeze Checklist** (ship-gate before Canon) · [audits/PROFILE_AS_SOURCE_CONSUMPTION_AUDIT.md](./audits/PROFILE_AS_SOURCE_CONSUMPTION_AUDIT.md).  
**Depth / missing data / subscription:** [UNDERSTANDING_PROGRESS_AND_DEPTH_CANON.md](./UNDERSTANDING_PROGRESS_AND_DEPTH_CANON.md).

> Profile is the identity source for Today, Tracking, Compatibility, Tarot.  
> It answers only: **Who is this person?**
>
> **Canon principle:** not max features — **existing functions finished.** Freeze = can ship.

---

## Product principle (platform, not Profile-only)

> **Интерфейс показывает не максимум данных, а максимум понимания.**  
> *(UI shows maximum understanding, not maximum data.)*

Kitchen may hold dozens of calculated parameters, weights, conflicts, confidence, limitations, derived claims, and full trace.  
The screen shows only what helps the person understand themselves better.  
Everything else stays internal and improves interpretation quality — it does not fill the viewport.

Aligns with [EXPLAIN_MEANING_NOT_MECHANISM.md](./EXPLAIN_MEANING_NOT_MECHANISM.md): never dump mechanism; show meaning.

---

## Hierarchy (не новое правило)

**Umbrella (platform-wide, выше модулей):**  
[EXPLAINABLE_COMPUTATION_AND_INTERPRETATION.md](./EXPLAINABLE_COMPUTATION_AND_INTERPRETATION.md)

Дочерние: [PRODUCT_TRUTH_FIRST.md](./PRODUCT_TRUTH_FIRST.md) · [EXPLAINABLE_INTERPRETATION.md](./EXPLAINABLE_INTERPRETATION.md) · Voice canon.

**PR-4 не создаёт отдельный production gate.**  
PR-4 **применяет** уже действующий umbrella-канон к поверхности Profile — так же, как он обязателен для Today, Tarot, Numerology, Compatibility, Goals, Practices, аскез и **любых будущих разделов**.

| При конфликте | Побеждает |
|---------------|-----------|
| Локальное решение Profile / Screen Master / Figma / «красивый CTA» | **Umbrella** |
| PR-4 IA (who-you-are vs Today/Tracking) | PR-4 *внутри* umbrella (границы экрана) |
| Content Canon C3 (generation) | Umbrella + Content; UI не ослабляет цепочку |

---

## Platform production gate (обязателен для каждого блока Profile)

Для **каждого** endpoint · промпта · контракта · UI-блока на Profile:

1. известен **источник**;
2. **расчёт** детерминирован и версионирован, где применимо;
3. **интерпретация** следует из evidence и ruleset;
4. понятен **практический смысл** (для identity — «что это говорит о человеке»; не day agenda);
5. **финальный текст** не добавляет нового смысла сверх структуры;
6. сохраняются **confidence**, **limitations** и **trace** (кухня; UI может показывать мягко);
7. команда может объяснить, **почему** пользователь получил именно этот вывод.

> Нет объяснимого происхождения, расчёта и практического назначения — элемент **не** в production.  
> Нет исключений для «просто красивого CTA», если CTA несёт или изображает смысловой вывод.

Единые текстовые нормы ([EXPLAINABLE_INTERPRETATION.md](./EXPLAINABLE_INTERPRETATION.md)): не выдумывать факты; не выбирать сферу без основания; не выдавать общий совет за персональный; не повторять смысл; снижать конкретность при слабых данных; связывать совет с наблюдаемым паттерном.

---

## 0. Hard rule (PR-4 surface — поверх umbrella)

Каждый Profile-блок дополнительно обязан отвечать:

> Что это говорит о человеке?

Если ответ — «что происходит сегодня» или «что делать сегодня» — блок **не** на Profile (→ Today / Tracking), даже если у него есть полная explainable-цепочка.

**Ban:** user-facing **«Сегодня»** в production Profile V2 copy (имя продукта «Today» в journey gate/CTA допустимо; day-state content — нет).

---

## 1. Data by origin (не по визуальным секциям)

| Layer | Meaning | Examples | On Profile | Umbrella step |
|-------|---------|----------|------------|---------------|
| **Identity** | Нельзя изменить (факты + расчёты) | Natal anchors, numerology, archetype, signatures | Yes — core | источник + расчёт |
| **Interpretation** | Что система поняла | Decision style, strengths, limits, patterns, direction | Yes — Snapshot / contract | интерпретация |
| **Evidence** | Почему так считает | `source_depth`, honesty, what strengthens portrait | Yes — short; **not** KPI ring | confidence / limitations |
| **Deep Sources** | Полная астрология | Houses, aspects, full chart | Collapsed / «Исследовать глубже» | расчёт + limitations |
| **Day state** | Сегодня | Stone, day supports, mood/energy, main step | **Forbidden** → Today | — |
| **Week / Maps** | День за днём | My Days, Living Maps, week rhythm | **Forbidden** → `/maps/*`, `/tracking/*` | — |
| **Slow evolution** | Месяцы / гипотезы | Confirmed themes, 30d shift | **Out of 4.1** | — |

```text
Identity → Interpretation → Evidence
Identity → Deep Sources (collapsed)
Profile Snapshot ──read──► Today / Tracking / Compat / Tarot
Today / Tracking ──do not write day UI──► Profile
```

---

## 2. Allow / deny (production V2)

### Allow (только с полной цепочкой umbrella)

- Hero: who you are from Snapshot/facts (quote, pills, archetype)
- Identity facts: archetype, Sun/Moon/ASC/life path, element — labels from calculation; **no invented role prose**
- Interpretation: strengths, drains, stable contract helps, decision style, patterns, mission, spheres from contract/QuickMap
- Evidence: honesty from `source_depth` / observation maturity
- Deep Sources: signature strip; role text **only** from existing framework/card body; full natal behind disclosure
- Thin **navigation** CTA: «Карты и наблюдения» → Maps (no embedded meaning product)
- Journey gate: first-Today unlock (not day content)

### Deny

- Day symbols / morning-ritual on Profile
- «Сегодняшние…» / «обновлено сегодня» badges
- My Days · Living Maps · «Мои карты» · mood/energy on Profile scroll
- «Главный шаг» / day recommendations as Profile meaning
- Fabricated % rings / unexplained confidence KPI
- Nested natal product open on first paint
- Hardcoded interpretive blurbs without Snapshot/card evidence (umbrella: текст не добавляет смысл)

---

## 3. Natal as source (2A) — inside Profile, person first

Natal chart **belongs on Profile**. It is **not** a separate product or route.

It must **not** become a second app inside Profile — and we do **not** lead with natal then wrap a portrait around it.

### Order (обязателен)

```text
1. Кто ты          — identity + interpretation (personality, decisions, helps, obstacles)
2. Почему так      — signatures, archetypes, key symbols, base numbers, natal supports
3. Натальная карта — structured source block inside (2), not a wall of houses/planets
```

Default Sources / natal block:

1. **Four main anchors** when known: Sun · Moon · ASC · MC (omit ASC/MC when time unknown — limitations, no invention)
2. Archetypes / key symbols that actually feed the portrait
3. Planetary accents that shape the profile (not every body)
4. **Houses that form the portrait** (typically a few) — not all twelve by default
5. **Aspects that matter for this profile** — not every aspect in the chart
6. Affordance: «Показать подробнее» / «Исследовать глубже» → rest of chart, remaining houses, deeper aspects

Kitchen may compute full chart; UI shows progressive understanding. Role prose only from evidence (framework/card) — otherwise calculated label only.

### 3.1 Post–4.1 UI polish (natal organization)

Slice 4.1 removed day contamination and demoted open nested natal.  
**Next UI pass** (after or alongside consumption audit): implement progressive disclosure so Sources is a beautiful organized identity foundation — not an ephemeris dump.

---

## 4. Mapping

| PR-4 surface | Content Canon | Umbrella |
|--------------|---------------|----------|
| Identity | Facts + calculated (§0) | источник → расчёт |
| Interpretation | §4.1–4.2 Snapshot fields | интерпретация → (практический смысл личности) |
| Evidence | `source_depth` + honesty | confidence / limitations |
| Deep Sources | Natal attach | расчёт + omit/partial без выдумки |

Modules read Snapshot/facts — not day ritual via Profile UI.

---

## 5. Exit criteria — slice 4.1

1. Default `/profile` has no day symbols, week continuity, Living Maps product, or «Главный шаг».
2. No user-facing «Сегодня» in Profile V2 copy.
3. This doc + Screen Master / tracker updated; **umbrella explicitly parent of PR-4**.
4. Natal = Identity/Deep Sources, not open nested product on first paint.
5. Evidence explains confidence in words / `source_depth`, not KPI ring.
6. No invented signature-role copy without evidence field.
7. Slow-evolution **not** in this slice.

---

## 6. Out of scope for 4.1 / next stages

| Stage | Focus |
|-------|--------|
| **4.1 CLOSED** | Boundaries: who-you-are only; day/maps out; umbrella applied |
| **Next — Source consumption** | [PROFILE_AS_SOURCE_CONSUMPTION_AUDIT.md](./audits/PROFILE_AS_SOURCE_CONSUMPTION_AUDIT.md): Today/Compat/Tarot/Guidance read Snapshot; no competing personality |
| **Then — Natal organization UI** | §3 progressive disclosure on Profile (anchors → accents → show more) |
| Later | Slow evolution UI · C3 LLM quality · Snapshot-on-read jobs |

---

## Changelog

| Date | Change |
|------|--------|
| 2026-07-21 | v1.0 — PR-4.1 surface canon |
| 2026-07-21 | v1.1 — umbrella hierarchy: PR-4 applies platform gate; conflict → umbrella wins; no invented source roles |
| 2026-07-21 | v1.2 — CLOSED 4.1; person-first natal; max understanding principle; next = consumption audit |

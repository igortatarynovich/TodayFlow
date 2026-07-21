# PR-3: Today Production Surface

**Status:** IN PROGRESS — Composition honesty pass (soft why + strengthen)  
**Canon:** [PRODUCT_TRUTH_FIRST.md](./PRODUCT_TRUTH_FIRST.md) · [EXPLAINABLE_COMPUTATION_AND_INTERPRETATION.md](./EXPLAINABLE_COMPUTATION_AND_INTERPRETATION.md) · [EXPLAINABLE_INTERPRETATION.md](./EXPLAINABLE_INTERPRETATION.md) · [audits/EXPLAINABLE_GENERATION_AUDIT_REGISTRY_V0.md](./audits/EXPLAINABLE_GENERATION_AUDIT_REGISTRY_V0.md) · [rfc/RFC_DAILY_STATE_V0.md](./rfc/RFC_DAILY_STATE_V0.md) · [PR3_TODAY_BLOCKS_REGISTRY.md](./PR3_TODAY_BLOCKS_REGISTRY.md)

> Не начинать с Figma. Сначала модель и explainable-контракт, затем независимые блоки Today, затем surface.

---

## Порядок (жёстко)

1. **Исправить `day_story_v1` по аудиту** — **DONE (backend)**  
2. **Контракт Today как набор независимых блоков** — **ACTIVE** ([PR3_TODAY_BLOCKS_REGISTRY.md](./PR3_TODAY_BLOCKS_REGISTRY.md))  
3. **FE domain honesty** — **DONE** (`isDomainLensPresent`)  
4. **Composition honesty** — **DONE this pass**  
   - Soft «почему» из `derived_claims` / `practice_recommendation.reason` (не limitations)  
   - Strengthen только из `practice_recommendation`  
   - Убраны competing synthesis tags на product reading  
5. **Типографика / motion** — только после smoke на prod.

---

## Production path (канон Surface)

```
App Shell (PR-2 CLOSED)
└── TodayWebDashboard layout=composition
    └── TodayCompositionSurface  ← единственный production voice при day_story
```

| Mode | Query | Status |
|------|-------|--------|
| Composition | default (`full` unset) | **Production Surface** |
| Ritual | `?full=1` | supplementary / ritual spine |
| Experience | `?experience=1` | legacy; not Surface target |

**Rail:** только данные (streak / weekly / timeline) — правило PR-2. Overview hero/tags/practices grid в composition не рендерятся.

---

## Block gate

Каждый блок: почему появился · что понял за 10–20с · что сделать сегодня.  
Подробности: [PR3_TODAY_BLOCKS_REGISTRY.md](./PR3_TODAY_BLOCKS_REGISTRY.md).

---

## Границы

| Делаем | Не делаем |
|--------|-----------|
| Trace и honesty для day_story | Redesign App Shell (закрыт в PR-2) |
| Блок-паспорта из реальных API | Фиктивные рекомендации / проценты |
| Surface поверх подтверждённых блоков | Независимые «камень/цвет дня» вне DailyState path |
| Profile отдельно | Смешивать Profile WIP в Today deploy |

**App Shell:** закрыт в [PR2_APP_SHELL.md](./PR2_APP_SHELL.md) — Today Surface садится только в него.

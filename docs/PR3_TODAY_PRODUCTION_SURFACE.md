# PR-3: Today Production Surface

**Status:** IN PROGRESS — day_story explainable + FE domain honesty; Composition path next polish  
**Canon:** [PRODUCT_TRUTH_FIRST.md](./PRODUCT_TRUTH_FIRST.md) · [EXPLAINABLE_COMPUTATION_AND_INTERPRETATION.md](./EXPLAINABLE_COMPUTATION_AND_INTERPRETATION.md) · [EXPLAINABLE_INTERPRETATION.md](./EXPLAINABLE_INTERPRETATION.md) · [audits/EXPLAINABLE_GENERATION_AUDIT_REGISTRY_V0.md](./audits/EXPLAINABLE_GENERATION_AUDIT_REGISTRY_V0.md) · [rfc/RFC_DAILY_STATE_V0.md](./rfc/RFC_DAILY_STATE_V0.md) · [PR3_TODAY_BLOCKS_REGISTRY.md](./PR3_TODAY_BLOCKS_REGISTRY.md)

> Не начинать с Figma. Сначала модель и explainable-контракт, затем независимые блоки Today, затем surface.

---

## Порядок (жёстко)

1. **Исправить `day_story_v1` по аудиту** — **DONE (backend)**  
   evidence · confidence · limitations · claim map · trace · phrase gate · domain partial  
   Code: `day_story_interpretation_v1.py`, `day_story_phrase_gate_v1.py`, `day_story_v1.py` (prompt v1.2).

2. **Контракт Today как набор независимых блоков** — **DRAFT**  
   [PR3_TODAY_BLOCKS_REGISTRY.md](./PR3_TODAY_BLOCKS_REGISTRY.md)

3. **FE domain honesty** — **DONE**  
   `isDomainLensPresent` + skip absent in sphere / glance / composition / spine / narrative / literary.

4. **Today Production Surface** — next  
   Default `/today` = Composition inside App Shell (`TodayCompositionSurface`).  
   Escape hatches only: `?full=1` ritual · `?experience=1` legacy experience.  
   Soft “почему” from user-facing claim meaning (not kitchen limitations) — optional.

5. **Типографика / motion** — только после контракта и структуры.

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

---

## Границы

| Делаем | Не делаем |
|--------|-----------|
| Trace и honesty для day_story | Redesign App Shell (закрыт в PR-2) |
| Блок-паспорта из реальных API | Фиктивные рекомендации / проценты |
| Surface поверх подтверждённых блоков | Независимые «камень/цвет дня» вне DailyState path |

**Связь с Phase N:** [DAILY_INTERPRETATION_ENGINE_PHASE.md](./DAILY_INTERPRETATION_ENGINE_PHASE.md) / DailyState — стратегический SoT дня; PR-3 начинается с починки текущего `day_story_v1`, не ждёт полного DailyState UI.

**App Shell:** закрыт в [PR2_APP_SHELL.md](./PR2_APP_SHELL.md) — Today Surface садится только в него.

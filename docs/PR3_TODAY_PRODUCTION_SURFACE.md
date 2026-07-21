# PR-3: Today Production Surface

**Status:** PLANNED — next major product slice after [PR-2 App Shell](./PR2_APP_SHELL.md) (**CLOSED**)  
**Canon:** [PRODUCT_TRUTH_FIRST.md](./PRODUCT_TRUTH_FIRST.md) · [EXPLAINABLE_COMPUTATION_AND_INTERPRETATION.md](./EXPLAINABLE_COMPUTATION_AND_INTERPRETATION.md) · [EXPLAINABLE_INTERPRETATION.md](./EXPLAINABLE_INTERPRETATION.md) · [audits/EXPLAINABLE_GENERATION_AUDIT_REGISTRY_V0.md](./audits/EXPLAINABLE_GENERATION_AUDIT_REGISTRY_V0.md) · [rfc/RFC_DAILY_STATE_V0.md](./rfc/RFC_DAILY_STATE_V0.md)

> Не начинать с Figma. Сначала модель и explainable-контракт, затем независимые блоки Today, затем surface.

---

## Порядок (жёстко)

1. **Исправить `day_story_v1` по аудиту**  
   evidence · confidence · limitations · claim map · trace  
   (реестр: [EXPLAINABLE_GENERATION_AUDIT_REGISTRY_V0.md](./audits/EXPLAINABLE_GENERATION_AUDIT_REGISTRY_V0.md) — P0 day_story).

2. **Контракт Today как набор независимых блоков**  
   У каждого блока: Source · Contract fields · Appear when · Loading / Ready / Empty / Partial / Error · Primary action · No-data.  
   Без источника — блок не проектируется.

3. **Today Production Surface**  
   Один пользовательский путь / один набор существующих контрактов внутри [PR-2 App Shell](./PR2_APP_SHELL.md).  
   Не весь Today «заново»; не DailyState UI раньше RFC.

4. **Типографика / motion** — только после контракта и структуры.

---

## Границы

| Делаем | Не делаем |
|--------|-----------|
| Trace и honesty для day_story | Redesign App Shell (закрыт в PR-2) |
| Блок-паспорта из реальных API | Фиктивные рекомендации / проценты |
| Surface поверх подтверждённых блоков | Независимые «камень/цвет дня» вне DailyState path |

**Связь с Phase N:** [DAILY_INTERPRETATION_ENGINE_PHASE.md](./DAILY_INTERPRETATION_ENGINE_PHASE.md) / DailyState — стратегический SoT дня; PR-3 начинается с починки текущего `day_story_v1`, не ждёт полного DailyState UI.

**App Shell:** закрыт в [PR2_APP_SHELL.md](./PR2_APP_SHELL.md) — Today Surface садится только в него.

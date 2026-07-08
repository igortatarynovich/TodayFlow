# Daily Navigation Model

**Статус:** принято (продуктовое ядро).  
**Версия:** 1.0 (2026-06-22).  
**Владелец:** Product + Engineering.

**Роль:** зафиксировать **что TodayFlow продаёт** и **как система работает каждый день** — не как Q&A и не как набор esoteric модулей.

**Связь:** [CORE_USER_LOOP.md](./CORE_USER_LOOP.md) (Theme → Action → Progress) · [TODAY_PRODUCT_MODEL.md](./TODAY_PRODUCT_MODEL.md) · [INTENT_MODEL_V1.md](./INTENT_MODEL_V1.md) · [SCREEN_CONTRACTS_V1.md](./SCREEN_CONTRACTS_V1.md) · [CORE_PRODUCT_CANON.md](./CORE_PRODUCT_CANON.md).

---

## 1. Что продаёт TodayFlow

Не астрология. Не нумерология. Не «ответы на вопросы».

TodayFlow продаёт **три вещи**:

| Продукт | Что получает человек |
|---------|----------------------|
| **Ясность** | понимание, что происходит и почему |
| **Направление** | куда держать фокус в периоде и сегодня |
| **Ежедневная рефлексия** | короткий цикл: осознать → сделать шаг → заметить прогресс |

Астрология, нумерология, таро, совместимость — **язык и инструменты**, не продукт.

Пользователь **чаще не формулирует вопрос**. Он **открывает приложение** — утром Today, в Profile «как я устроен», в Compatibility «как мы вместе».

**Центр системы** — ежедневная потребность в **ориентире**, не в Question Registry.

---

## 2. Продуктовое ядро: ICA

Love, Future, Career, Purpose — **контентные проекции** и deep routes. **Не ядро.**

Ядро — четыре слоя, которые пользователь получает **каждый день**:

| Слой | Вопрос | Продуктовая функция |
|------|--------|---------------------|
| **Identity** | Кто этот человек? | Стабильная карта: паттерны, сильные стороны, зоны внимания |
| **Current Context** | Что происходит **сейчас**? | День, период, состояние, активация личности |
| **Guidance** | Что это **значит** для меня? | Интерпретация контекста через Identity |
| **Action** | Что делать **дальше**? | Один (или мало) конкретных шагов — не «предназначение», а **следующий шаг** |

```
Identity  →  кто я (Profile, Reference)
Context   →  что сейчас (DayModel, state, cycles)
Guidance  →  что значит (interpretation через Identity)
Action    →  что делать (Today, Practices)
```

**Progress** (из [CORE_USER_LOOP.md](./CORE_USER_LOOP.md)) — след после Action: «продвигаюсь ли я?» — замыкает дневной цикл.

---

## 3. Каноническая pipeline (не Question → Answer)

```
Profile          — Identity (стабильная карта)
      ↓
Current Context  — день, период, состояние, пары, история сигналов
      ↓
Guidance         — смысл для этого человека в этом контексте
      ↓
Action           — фокус, avoid, следующий шаг
      ↓
Surface          — Today · Profile · Compatibility · Reports · Practices
```

**Reference Layer** питает Identity.  
**Interpretation Engines** — projection внутри Guidance (не финальный UX).  
**Answer Assembler** — собирает Guidance + Action по [SCREEN_CONTRACTS_V1.md](./SCREEN_CONTRACTS_V1.md) для needs, **без** обязательного `question_id`.

### Связь с Theme → Action → Progress

| Core User Loop | ICA |
|----------------|-----|
| Theme | Context + Guidance (что важно сейчас и почему) |
| Action | Action |
| Progress | след шага + обратная связь в следующий Context |

---

## 4. Что нужно человеку **каждый день** (4 опоры)

Не tier-1 «вопросы». **Ежедневные потребности в ориентире:**

| # | Потребность | ICA | Today блок | `need_id` (см. Need Registry) |
|---|-------------|-----|------------|-------------------------------|
| 1 | **На чём сфокусироваться** | Context + Guidance | Focus, Theme, spheres | `need_daily_focus` |
| 2 | **Чего избегать** | Context + Guidance | Avoid, risk, limits | `need_daily_opportunity_risk` |
| 3 | **Что со мной сейчас** | Identity × Context | Theme + Brief + «почему так» | `need_self_understanding` × daily activation |
| 4 | **Как двигаться вперёд** | Action | Action, micro-win | `decide_action` через Action block |

Примеры блока 3 (Profile + Today):

- почему сейчас раздражительность выше;
- почему хочется замедлиться;
- почему тянет к переменам.

**Не** глобальное предназначение каждый день — только **следующий шаг**.

---

## 5. Экраны = ответ на жизненный вопрос (не на tool)

| Surface | Вопрос пользователя | ICA dominant | Не является |
|---------|---------------------|--------------|-------------|
| **Today** | Что сегодня важно **лично для меня**? | Context → Guidance → Action | гороскоп на день; Q&A |
| **Profile** | Как я **устроен**? | Identity | CRM; стена натала |
| **Compatibility** | Как я **взаимодействую** с другими? | Identity × 2 → Guidance (пара) | только entertainment score |
| **Reports** | Какие **закономерности** в моей жизни? | Identity + long Context | разовый PDF без связи с Today |
| **Practices** | Что **поможет мне сейчас**? | Action + stabilize | отдельный wellness-продукт |
| **Questions Hub** | *(опционально)* явный текст | тот же ICA pipeline | **центр продукта** |

Depth routes (Love OS, Money OS, …) — углубление **той же** ICA-линии, не отдельные «корни продукта».

---

## 6. Question Registry — периферия, не центр

**Question Registry** — артефакт **чат-интерфейса** (Questions Hub, будущий AI-консультант):

- `explicit_question` → classify → `need_id` → тот же Assembler.

Пользователь **не** начинает день с «Почему мне тяжело?» — он открывает **Today**.

| Модель | Центр | Ритм |
|--------|-------|------|
| Chat-bot / Q&A | Question | sporadic |
| **TodayFlow** | Daily orientation (ICA) | **daily habit** |

Нужды из [INTENT_MODEL_V1.md](./INTENT_MODEL_V1.md) остаются валидны как каталог **потребностей**, но **первичный inference** — `surface_open` и `surface_block`, не `explicit_question`.

---

## 7. Стек документов (иерархия)

```
Daily Navigation Model     ← этот документ (зачем и ядро ICA)
        ↓
Need Registry              ← каталог потребностей (включая daily 4)
        ↓
Intent Registry            ← как продукт закрывает need
        ↓
Answer Contract            ← mandatory Guidance + Action elements
        ↓
Engine Projection Specs    ← сырые срезы для Guidance
        ↓
Question Registry          ← только Hub / AI (optional)
```

---

## 8. Definition of Done (daily product)

- [ ] Открытие **Today** без текста закрывает daily 4 (§4) — review по [SCREEN_CONTRACTS_V1.md](./SCREEN_CONTRACTS_V1.md).
- [ ] Profile читается как **Identity**, не как список полей.
- [ ] Compatibility result = Guidance для пары + Action, не trait dump.
- [ ] Progress виден в дневном цикле ([CORE_USER_LOOP.md](./CORE_USER_LOOP.md)).
- [ ] Questions Hub не единственный путь к value; metrics: DAU Today > Questions submissions.

---

## 9. Changelog

| Дата | Изменение |
|------|-----------|
| 2026-06-22 | v1.0 — ICA kernel, Profile→Context→Guidance→Action, daily 4, screen map, Question Registry demoted |

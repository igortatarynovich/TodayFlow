# Ядро персонализации: Today (контракт, события, prompt)

**Статус:** канон для реализации Today после утреннего ритуала.  
**Связь:** [PERSONAL_INTELLIGENCE_LAYER.md](pim/PERSONAL_INTELLIGENCE_LAYER.md) (общий контур), [PERSONAL_INTELLIGENCE_LAYER.md](pim/PERSONAL_INTELLIGENCE_LAYER.md) (PIL: refinement, retrieval, evaluation), [CORE_PRODUCT_CANON.md](archive/CORE_PRODUCT_CANON.md) (продукт).  
**Паритет:** один контракт и один словарь событий для **web и iOS**.

---

## Порядок работы (обязательный)

1. **Утвердить JSON-контракт Today** (этот документ, раздел ниже).  
2. **Утвердить список tracking events** (раздел «События»).  
3. **Переписать backend prompt** под structured JSON (валидация схемы, отказ при невалидном ответе или санитизация по правилам версии).  
4. **Переделать экран Today** (web, затем iOS) под этот контракт.  
5. **Guidance и Compatibility** — по той же логике (отдельные контракты + те же принципы событий и сборки контекста).

Пункты 1–2 — документ здесь; пункты 3–5 — код и UI, не расширять scope без обновления этого файла.

---

## Шаг 1. JSON-контракт ответа API после ритуала (Today)

Корень ответа — объект. Рекомендуется поле **`contract_version`** (строка, например `"today_day_v1"`) для эволюции без ломки клиентов.

**Машиночитаемая схема:** [docs/schemas/today_day_v1.schema.json](./schemas/today_day_v1.schema.json) (JSON Schema draft 2020-12). В CI проверяются валидная и заведомо невалидная фикстуры: `scripts/validate_today_day_contract.py`.

### Пример целевой формы

```json
{
  "contract_version": "today_day_v1",
  "core_message": {
    "title": "string",
    "text": "string",
    "risk": "string",
    "best_move": "string"
  },
  "spheres": [
    {
      "id": "work",
      "title": "Работа",
      "score": 78,
      "status": "strong",
      "why": "string",
      "do": "string",
      "avoid": "string",
      "question": "string"
    }
  ],
  "action_options": [
    {
      "id": "close_task",
      "title": "Закрыть одну задачу",
      "why": "string",
      "estimated_minutes": 20,
      "creates": "focus_session"
    }
  ],
  "support": {
    "recommended": "practice | goal | habit | ascetic | none",
    "title": "string",
    "reason": "string",
    "cta": "string"
  },
  "feedback_questions": [
    {
      "id": "accuracy",
      "question": "Это про тебя?",
      "options": ["да", "частично", "нет"]
    }
  ]
}
```

### Правила и ограничения

| Поле | Правило |
|------|--------|
| `core_message.*` | Все четыре ключа обязательны; строки непустые после trim (или явное соглашение «пустая строка = нет блока» — тогда фиксировать в версии контракта). |
| `spheres` | Массив из **ровно 3** элементов для текущего Today-триада: `id` ∈ `work`, `love`, `money` (каждый **ровно один раз**). `title` — локализованная подпись. `score` — целое 0–100. `status` ∈ `strong`, `weak`, `neutral` (согласовано со `score` и правилами ранжирования на бэке). |
| `action_options` | Ровно **3** варианта, если иное не зафиксировано в `contract_version`. `estimated_minutes` — положительное целое. `creates` — машинный тег следующего шага в продукте; стартовый набор: `focus_session` (расширяется списком в этом же документе при появлении новых потоков). |
| `support.recommended` | Одно из: `practice`, `goal`, `habit`, `ascetic`, `none`. |
| `feedback_questions` | Массив из **1–3** коротких вопросов; каждый с уникальным `id` в рамках ответа. `options` — массив строк (минимум 2 варианта). |

**Миграция с текущего бэка:** сегодня в коде часто используются строковый `core_message`, массив строк `action_options` и `sphere_triad` с полем `stance`. Новый контракт **заменяет** эту форму для Today; до переключения версии допустим параллельный эндпоинт или флаг, но канон для нового UI — структура из этого раздела.

---

## Шаг 2. События, которые учат систему (tracking)

Имена типов — **snake_case**, стабильные между платформами.

| `event_type` | Когда |
|--------------|--------|
| `tarot_selected` | Пользователь выбрал карту в ритуале. При уже загруженном **guide** за день — в payload добавляется **`generation_id`** (веб `withOptionalGuideGenerationId` / `narrativeGenerationIds.guide`, iOS `generationLogId` из `todayGuideNarrative`). |
| `tarot_session_started` | Открыта question-first воронка Tarot (Hero → concern). `payload.session_id`, `payload.surface`: `tarot_hub`. |
| `tarot_question_domain_selected` | Выбран домен вопроса. `payload.concern_domain`, `payload.session_id`. |
| `tarot_question_refined` | Уточнение формулировки. `payload.refinement_id`, `payload.concern_domain`, `payload.session_id`. |
| `tarot_spread_selected` | Выбран расклад по смыслу вопроса. `payload.spread_id`, `payload.question_text`, `payload.session_id`. |
| `tarot_question_submitted` | Финальная формулировка вопроса перед ритуалом. `payload.question_text`, `payload.concern_domain`, `payload.refinement_id`. |
| `tarot_reading_resonance` | *(legacy)* Ответ «насколько откликается». Заменён на `tarot_reading_follow_up` в question-first result. |
| `tarot_reading_follow_up` | Чип после расклада («Отпустить», «Понять…»). `payload.chip_id`, `chip_label`, `concern_domain`, **`generation_id`**. |
| `tarot_deepen_started` | Переход Today / карта дня → расклад с якорной картой. `payload.source`: `today` \| `card_of_day`; `payload.card_id`, `payload.orientation`, `payload.spread_id` (обычно `three_cards`). |
| `number_selected` | Выбрано число дня / life path в контексте ритуала. |
| `mood_selected` | Выбрано настроение / состояние. |
| `head_topic_selected` | Выбрана главная тема дня (голова дня / акцент). |
| `sphere_opened` | Открыта детальная карточка сферы. |
| `sphere_feedback` | Ответ на вопрос по сфере или явное согласие/несогласие с формулировкой. |
| `action_option_selected` | Выбран один из `action_options`. |
| `focus_started` | Запущен фокус / таймер по выбранному шагу. |
| `focus_completed` | Фокус завершён (успех или явное закрытие как «сделано»). |
| `support_selected` | Пользователь принял рекомендацию support (переход по CTA или эквивалент). |
| `goal_created` | Создана цель из потока дня. |
| `habit_created` | Создана привычка из потока дня. |
| `practice_completed` | Завершена практика, предложенная из support или дня. |
| `evening_reflection_submitted` | Отправлен вечерний ответ / рефлексия (в т.ч. «совпало / не совпало»). |
| `today_narrative_depth_changed` | Пользователь сменил **глубину** нарратива дня (DE-8: quick / normal / deep) на экране Today или в настройках аккаунта. `payload.depth_level`, опционально `payload.source`: `today_page` (веб Today), `account_settings` (веб `/account/settings`), `today_depth_strip` (iOS Today), `profile_settings` (iOS форма настроек в профиле). |
| `today_guide_why_opened` | Раскрыт блок **«Почему так?»** под короткой сводкой дня в ритуале (веб `TodayRitualFlow`, iOS `TodayRitualFlowView`). `payload.surface`: `ritual_day_summary`; при наличии ответа guide — **`generation_id`** (тот же контракт, что у других событий поверхности guide). |
| `today_day_history_first_visible` | Блок **DE-9** `day_history` впервые попал в зону видимости (веб `IntersectionObserver` в `TodayDayHistoryStrip`; iOS `onAppear` по размещению). `payload.surface`: `ritual_after_callout` или `your_day_spheres`; опционально **`generation_id`** guide. |

**Payload (общие требования):** каждое событие должно позволять привязку к **`day_key` / дате**, при наличии — к **`generation_id`** (id строки `generation_logs` от `POST /today/narrative` для соответствующего surface), и ссылку на сущность (`sphere_id`, `action_option_id`, `feedback_question_id` и т.д.). На вебе в `/meaning/events` для шагов ритуала после «Главного» в payload передаётся `generation_id` (guide). Конкретные поля JSON события задаются в OpenAPI / схеме ingestion при реализации.

**Ритуал Today (основная цепочка шагов, паритет клиентов):** после успешного шага state-machine клиент шлёт:
- `number_selected` — `payload.revealed: true`, `payload.numerology_value` (строка цифры дня в UI); на iOS дополнительно `quality_score` в теле surface-события (как в `trackTodaySurfaceEvent`). Если за день уже есть ответ **guide**, в payload добавляется **`generation_id`** (веб `guideGenerationId` в `executeRitualSpineAnalytics`, iOS `generationLogId` из `todayGuideNarrative`, Android `guideGenerationId` в `executeRitualSpineAnalytics`).
- `mood_selected` — `payload.mood_id`, `payload.source: "today_ritual"` когда выбор из блока чек-ина ритуала (веб `executeRitualSpineAnalytics`, iOS `applySpineEffects`, Android `executeRitualSpineAnalytics` при подключении транспорта). При уже загруженном guide — тот же опциональный **`generation_id`**, что и для `number_selected`.
- `today_guide_why_opened` — только при **раскрытии** (не при сворачивании); см. таблицу выше.

---

## Шаг 3. Prompt optimizer (что собираем перед запросом к API)

Минимальный ритуальный контекст **недостаточен**. Перед вызовом генерации Today система собирает **bundle контекста**, включающий:

1. **Ритуал сегодня:** карта (таро), число, настроение.  
2. **Актуальная тема:** в т.ч. `head_topic` / акцент дня, если выбран.  
3. **История реакций:** недавние `feedback_questions` + ответы, агрегированные сигналы точности и «сработало».  
4. **Активные цели:** открытые цели пользователя, релевантные дню (сжато).  
5. **Паттерны пользователя:** краткие теги/резюме из слоя паттернов (не сырой лог).  
6. **Стиль ответа:** предпочтения длины, прямоты, тона (из профиля и прошлого фидбека).

**Правило:** лимиты по токенам, приоритет свежего дня; при переполнении отбрасывать в порядке: старая история → детали нерелевантных целей → длинные цитаты.

---

## Версионирование

Любое изменение обязательных полей, enum или семантики событий — новая **`contract_version`** и явное упоминание в changelog этого файла (краткий список внизу документа).

### Changelog

- **today_day_v1** — контракт и список событий в этом документе; машиночитаемая схема `docs/schemas/today_day_v1.schema.json` и CI job `today-contract-schema` (`scripts/validate_today_day_contract.py`).
- **2026-05-04** — уточнён payload ритуала для `number_selected` / `mood_selected` (`source: today_ritual`); выравнивание с единым reducer + `analyticsHint` на web/iOS/Android scaffold.
- **2026-05-04** — тип `today_narrative_depth_changed` (смена DE-8 на экране Today / в профиле); вес в кольце Mind в `RING_EVENT_WEIGHTS`.
- **2026-05-04** — тип `today_guide_why_opened` (раскрытие «Почему так?» в сводке ритуала); вес в кольце Mind в `RING_EVENT_WEIGHTS`.
- **2026-05-04** — опциональный `generation_id` в `number_selected` / `mood_selected` из хребта ритуала, если guide за день уже получен (повторное прохождение шагов).
- **2026-05-04** — опциональный `generation_id` в `tarot_selected`; тип `today_day_history_first_visible` + вес в кольце Mind в `RING_EVENT_WEIGHTS`.

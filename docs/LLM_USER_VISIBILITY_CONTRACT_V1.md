# LLM User Visibility Contract v1

**Статус:** принято как продуктовый закон (implementation gate для всех AI-экранов).  
**Версия:** 1.1 (2026-07-23).  
**Владелец:** Product + Engineering.  
**Область:** Profile · Today · Compatibility · Tarot · Numerology · любой будущий AI-экран.  
**Связь:** [PROFILE_CONTENT_CANON_V1.md](./PROFILE_CONTENT_CANON_V1.md) · [SCREEN_CONTRACTS_V1.md](./SCREEN_CONTRACTS_V1.md) · [PR4_PROFILE_CANON.md](./PR4_PROFILE_CANON.md) · Profile Journey V2 (`ProfileV2SystemScreen`) — первый контур аудита, не единственный.

---

## 0. Главный принцип

**Дизайн управляет порядком чтения, но не уничтожает глубину продукта.**

Это не UI-документ про «показать больше текста». Это правило **управления доступностью знаний**, уже оплаченных вычислениями.

LLM не генерирует скрытый технический материал для «красоты экрана».  
Каждый полезный вывод, созданный на основании данных пользователя, должен иметь полный жизненный цикл:

1. **генерация** → 2. **хранение** → 3. **использование** в системе → 4. **пользовательская поверхность**.

На поверхности он должен:

1. иметь **доступное место** в продукте;
2. быть **видимым** сразу **или** явно доступным через раскрытие / детальный экран;
3. быть **обнаруживаемым** — пользователь естественным образом понимает, что более глубокий уровень существует;
4. сохранять **уникальный смысл**, даже если UI объединяет повторы.

Сокращение ради чистоты экрана без пути к полной формулировке — **нарушение контракта**.

**Decorative UI (атмосфера, constellation art, motion) не заменяет текстовую глубину.**  
Красивый редизайн не имеет права экономить на содержании ради «чистого» экрана.

---

## 0.1 Обнаруживаемость (Discoverability)

Доступность без обнаруживаемости — формальное выполнение контракта.

Если `identity_core` (или любой L2/L3 блок) существует в payload, но пользователь никогда не понимает, что его можно открыть, — **практически контракт нарушен**.

Обязательное правило:

> Пользователь должен естественным образом обнаруживать существование более глубокого уровня.

Примеры допустимых сигналов (не исчерпывающий список):

- явная CTA «Подробнее» / «Почему так» / «Открыть основания» рядом с L1;
- интерактивный узел constellation / proof card с affordance клика;
- прогрессивный fold Explore с видимым заголовком и состоянием «есть ещё»;
- честный empty state, если глубины ещё нет (не молчаливое отсутствие секции).

Скрытый жест, невидимый overflow, debug-only URL — **не** считаются обнаруживаемостью.

---

## 1. Модель доступа (не «всё сразу»)

```
обзор → история / объяснение → доказательства → полный разбор
```

Это соответствует тому, как человек реально исследует себя — не «коротко или длинно», а уровни смысла.

| Уровень | Роль | Что видит пользователь |
|---------|------|-------------------------|
| **L1 Primary** | Обзор / история | Архетип, recognition, главное напряжение/сила, вектор, мост в Today |
| **L2 Expanded** | Объяснение | Полная интерпретация, why, проявления, сила/тень, практика, связанные источники |
| **L3 Detail** | Доказательства / факторы | Солнце/Луна/ASC/MC, дома, аспекты, планеты, число пути, вклад фактора в вывод |

Нельзя показывать всё одновременно. Обязательна **полнота доступа** + **обнаруживаемость** при сохранённой иерархии.

### 1.1 L1 — главное (Primary)

На основном AI-экране (для Profile Journey):

- архетип;
- главное объяснение (recognition / why synthesis);
- сильная сторона / напряжение (insight);
- вектор развития (effort);
- мост в Today (bridge).

Это **история пользователя**, не база данных.

### 1.2 L2 — полный смысловой разбор (Expanded)

Каждый главный вывод раскрывается в:

- полная интерпретация;
- почему сделан такой вывод;
- как проявляется;
- сильное проявление;
- теневое проявление;
- практическое значение;
- связанные источники.

Поверхности: **«Подробнее»**, expandable-секция, отдельный экран.  
**Не** маленький tooltip.

### 1.3 L3 — все исходные факторы (Detail)

Доступны:

- Солнце, Луна, ASC, MC;
- дома, аспекты, планеты;
- число пути и другие рассчитанные системы;
- вклад каждого фактора в итоговый вывод.

Constellation — красивый вход; **каждый узел интерактивен** и ведёт к полному объяснению.

---

## 2. Реестр LLM-выводов (structured object)

Для каждого ответа модели хранится не только `title` + короткий `summary`, а полный структурированный объект (минимум):

| Поле | Назначение |
|------|------------|
| `id` | Стабильный идентификатор вывода |
| `domain` | profile / today / compatibility / tarot / numerology / … |
| `section` | recognition / why / insight / effort / … |
| `headline` | Короткий заголовок для L1 |
| `summary` | Краткое резюме для L1 |
| `full_interpretation` | Полный текст L2 |
| `why_it_matters` | Почему это важно |
| `strength_expression` | Сильное проявление |
| `shadow_expression` | Теневое проявление |
| `growth_direction` | Вектор / практика |
| `daily_expression` | Как звучит в Today (если применимо) |
| `evidence[]` | Пользовательские / живые доказательства |
| `source_facts[]` | Детерминированные факты (знаки, LP, …) |
| `confidence` | Уверенность / скромность формулировки |
| `generation_version` | Версия промпта / схемы для воспроизведения |

UI не обязан выводить все поля рядом.  
**Ни одно полезное поле нельзя получить от LLM, сохранить и затем нигде не показать.**

Если поле **используется** downstream (Today, Compatibility, тон ответов), но не имеет surface — это отдельный долг: либо surface, либо явный `internal_only` без пользовательской ценности (редко).

---

## 3. Статусы полей на экране

Для каждого generated field обязателен один статус:

| Статус | Смысл |
|--------|--------|
| `visible_primary` | Виден сразу на основном экране |
| `visible_expanded` | Доступен при раскрытии («Подробнее» / expandable) |
| `visible_detail` | Доступен на детальном экране / deep natal / node detail |
| `internal_only` | Только служебное поле **без** пользовательской интерпретации |

Если текст имеет **пользовательскую ценность**, статус `internal_only` **запрещён**.

Допустимые `internal_only` примеры: `source_fields` machine keys, projection `role`, raw prompt ids — при условии, что смысл уже выражен в user-facing полях.

---

## 4. Acceptance gates

Готово только когда:

1. Для каждого пользовательского LLM-поля существует UI surface.
2. Ни одно поле не обрезается без возможности раскрытия.
3. `line-clamp` / ellipsis допускается **только** вместе с «Показать полностью» (или эквивалентом).
4. Наличие длинного текста не ломает layout.
5. Все доказательства доступны из связанного вывода.
6. Повторяющиеся выводы объединяются, но не удаляются без сохранения уникального смысла.
7. Пользователь открывает полный контент **последовательно** в продукте — не через admin/debug.
8. При отсутствии данных UI честно показывает отсутствие, а не скрывает секцию без объяснения.
9. Версия генерации хранится (`generation_version` / contract version), чтобы выводы можно было воспроизвести и сравнить.
10. Экспорт содержит полный набор пользовательских интерпретаций, а не только краткий экранный текст.
11. **Discoverability:** для каждого `visible_expanded` / `visible_detail` поля на L1 есть естественный сигнал, что глубина существует (CTA, affordance узла, видимый fold) — не «секретный» жест.
12. Матрица аудита заполняет колонки generate / store / **use** / show — зависимости между модулями не теряются.

---

## 5. Аудит сейчас (Profile Journey V2) — матрица

Снимок кода на 2026-07-23. Первый контур применения закона; те же статусы обязательны для Today / Compatibility / Tarot при следующих аудитах.

Статусы: **OK** · **Partial** · **Gap** · **Missing** · **Violation**.

| Вывод | Где генерируется | Где хранится | Где используется | Где показывается | Уровень | Статус |
|-------|------------------|--------------|------------------|------------------|---------|--------|
| Архетип (display name) | baseline seed + registry | Snapshot baseline | Profile, product chrome, iOS hero | Recognition hero | Primary | OK |
| Recognition line | LLM `profile_contract_v1` | Snapshot | Journey L1; quality gates | Recognition | Primary | OK |
| **Identity core** | LLM step 1 | Snapshot | Quality/evals; QuickMap `identitySummary`; **слабо в Journey** | Не на Journey L1 | — | **Missing** surface + **Gap** discoverability |
| Why title + anchors | Deterministic `portrait_why_v0` | Ephemeral read | Journey Why | Why cards + synthesis | Primary | OK |
| Honesty line | Deterministic why | Ephemeral | Journey Why | Why | Primary | OK |
| Insight title + body | Remix → `insight_nodes_v0` | Ephemeral | Journey Insight; feeds effort | Insight | Primary | OK |
| Insight help / restore | Contract `helps` / strengths | Snapshot + ephemeral | Insight; Effort vector source | Insight | Primary | OK |
| Living evidence quotes | Living enrich | Ephemeral | Insight adjacent context | Insight (если есть) | Primary | Partial |
| **Сила / тень как L2 блоки** | `strengths` / `growth_zones` | Snapshot | Remix в insight; Explore lists | Сжато в L1 insight | Expanded | **Gap** (нет «Подробнее») |
| Effort vector | From insight help | Ephemeral | Journey Effort | Effort | Primary | OK |
| Bridge line | Deterministic | Ephemeral | Journey → Today CTA | Bridge | Primary | OK |
| Life mission | LLM | Snapshot | Explore | Explore | Expanded | OK · Partial discoverability |
| Decision / relationship / money | LLM | Snapshot | Explore progressive; legacy traits | Explore | Expanded | Partial discoverability |
| **Living changes** | LLM / enrich | Snapshot | Framework lead (QuickMap); **не V2** | — | — | **Missing** |
| Sphere titles | LLM spheres | Snapshot | Effort chips; Explore | Effort / Explore | Primary | OK |
| Sphere how / need / risk / turns_on | LLM | Snapshot | Explore details | Explore `<details>` | Expanded | Partial |
| **Sphere turns_off / helps** | LLM | Snapshot | Legacy life section only | **V2 Explore нет** | — | **Missing** |
| Framework anchors | Client natal knowledge | Client | Constellation; QuickMap | Constellation | Detail entry | OK entry |
| **Framework full body** | Client | Client | Только hint ≤120 | Silent `…` | — | **Violation** (truncation без раскрытия) |
| Constellation → full explanation | — | — | Узлы не ведут в detail | Non-interactive | Detail | **Gap** discoverability + access |
| Grounded labels | Why / insight | Ephemeral | Insight list | Insight | Primary | OK |
| source_fields / fact_keys | Projector | Ephemeral | Provenance machine | Не UI | Internal | OK as keys; Gap user provenance |
| Live Evidence pack | `buildProfileV2LiveContext` | Client-only | **Computed, unused** | Не смонтирован | — | **Missing** |
| Natal houses / aspects / planets | Astro engines | Preview | Deep natal; practices | Deep when expanded | Detail | OK when expanded |
| Contract / generation version | Funnel | Snapshot | Quality / reproduce | Не surfaced | Internal | Gap UX gate 9 |
| Profile export full set | — | — | — | — | — | Not verified · likely Gap gate 10 |

### 5.1 Приоритет реализации (максимум ценности / минимум UI)

Согласованный порядок:

1. **Вернуть `identity_core` в Journey** — Primary или Expanded с явным discoverability (не «мертвый» payload).
2. **Полноценный L2 для Insight** — «Подробнее» с полной силой/тенью/why/практикой (не tooltip).
3. **Интерактивные узлы Constellation** — полный framework body + путь в основания (убрать silent `…`).

Далее: sphere `turns_off`/`helps`, Live Evidence pack, truncation policy на всех AI-экранах, экспорт.

---

## 6. Правило для реализации

- Новый LLM-field в промпте / schema → одновременно: статус visibility + UI surface + **use** (кто читает) + discoverability + строка в матрице + тест.
- Рефактор «укоротить экран» без `visible_expanded` / `visible_detail` пути и без сигнала обнаружения — **запрещён**.
- Decorative UI **не заменяет** текстовую глубину.
- Контракт применяется к **любому** новому AI-экрану по умолчанию; Profile — первый аудит, не исключение.

---

## 7. Вне scope этого контракта

- Служебные machine ids, raw prompts, debug traces (если смысл уже в user fields).
- Админские / eval-only экраны как единственный путь доступа к пользовательскому тексту.

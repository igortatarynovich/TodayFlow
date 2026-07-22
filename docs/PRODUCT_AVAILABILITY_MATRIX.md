# Product Availability Matrix

**Статус:** DRAFT TARGET — **gate перед любыми изменениями Profile / Today**  
**Роль:** отправная точка продукта. API · генерация · UI — **следствия** этой таблицы, не наоборот.  
**Владелец:** Product  
**Связь:** [PRODUCT_DATA_INTAKE.md](./PRODUCT_DATA_INTAKE.md) · [PRODUCT_CAPABILITY_CONTRACTS.md](./PRODUCT_CAPABILITY_CONTRACTS.md) · [PRODUCT_GENERATION_CONTRACTS.md](./PRODUCT_GENERATION_CONTRACTS.md) (**ядро генерации**) · Understanding Progress · Compat · Voice  


**Не путать:** это не архитектурный engine/registry и не очередной «канон пайплайна». Это матрица **состояний пользователя → доступность**.

---

## Freeze

До **APPROVED** этой матрицы (слой 0 intake + слои 1–3 + Open decisions):

```text
⛔ не менять IA / блоки Profile production UI
⛔ не менять IA / блоки Today production UI
⛔ не добавлять новые LLM-поверхности Profile / Today
⛔ не добавлять новые публичные формы birth data вне PRODUCT_DATA_INTAKE (1A / 1B / 2)
✅ можно: править только код, который реализует уже принятую строку матрицы / intake
✅ можно: дополнять эту таблицу фактами code-truth и открытыми решениями
```

---

## Слой 0 — Ввод данных (ровно 2 способа)

**SoT:** [PRODUCT_DATA_INTAKE.md](./PRODUCT_DATA_INTAKE.md)

| # | Кто | Точка входа | Результат |
|---|-----|-------------|-----------|
| **1A** | Новый, без аккаунта | Игровая совместимость → персональная совместимость двух людей | Profile A + Profile B → preview → email → аккаунт |
| **1B** | Новый, без аккаунта | Построить мой профиль / карту | 1 профиль → preview → email → аккаунт |
| **2** | Авторизован | Добавить профиль | Новый профиль в аккаунте, без email |

Правила слоя 0:

- нет отдельных анкет Profile / Compat / Natal / Today — только сохранённые профили;
- частичные данные → доступность по **слою 1**, не полный блок;
- регистрация **привязывает** профили, не создаёт их заново;
- совместимость ссылается на `profile_a_id` / `profile_b_id`.

---

## Словарь доступа (продукт ↔ код)

| Продукт (эта матрица) | Код сегодня | Примечание |
|----------------------|-------------|------------|
| **Guest** | `user is None` + local `guestAccessLimits` | Не billing-enum |
| **Free** | `subscription_level=free` → `insight_depth_tier=free` | Зарегистрирован, не платит |
| **Trial** | **целевой** целостный опыт; в Stripe = `status=trialing` на плане | Canon: trial ≠ обрезанный free. Open decision: длительность / какой plan |
| **Paid** | billing `lite`/`pro` → insight `pro`/`premium` | Маркетинг: Plus / Pro. Глубина, не «второй продукт» |

Правило глубины: [UNDERSTANDING_PROGRESS](./UNDERSTANDING_PROGRESS_AND_DEPTH_CANON.md) — подписка меняет **глубину**, не наличие базового ответа.

Легенда ячеек: **TARGET** = решение продукта · **CODE** = как сейчас в репо · **Δ** = расхождение, которое надо закрыть после APPROVED.

---

## Слой 1 — Данные рождения → доступность

| Состояние данных | Что открывается (TARGET) | Что скрывается / запрещено | Что объясняем пользователю |
|------------------|--------------------------|----------------------------|----------------------------|
| **Нет регистрации** | Landing, демо, примеры, guest-лимиты Tarot/Compat/Practices | Любая персонализация по наталу / Snapshot | «Создайте профиль, чтобы получить персональный анализ.» |
| **Зарегистрирован, без даты** | Онбординг / setup | Персональный Profile, персональный Today, персональная Compatibility, персональный Tarot-контекст | «Добавьте дату рождения, чтобы построить основу профиля.» |
| **Только дата** | Базовый профиль · базовый Today · нумерология даты · натал без домов (планеты по знакам, часть аспектов) · циклы даты | Ascendant · дома · MC/IC · house-based сферы · house-based транзиты · именная нумерология (если нет имени) | «Время рождения откроет Асцендент, дома и жизненные сферы.» |
| **Дата + место, без времени** | Практически то же, что «только дата». Место можно сохранить | Всё, что зависит от времени. **Запрет:** видимость «более точной» карты из-за места | «Без времени рождения невозможно определить дома и Асцендент. Место понадобится вместе со временем.» |
| **Дата + время + место** | Полная натальная карта · полный структурный профиль · точные транзиты / углы | Только именная нумерология (если нет имени) | «Добавьте имя, если хотите отдельный анализ имени — на карту оно не влияет.» |
| **Полные birth data + имя** | Всё из строки выше + Expression / Soul Urge / Personality | — | — |

**Главное правило слоя 1:** отсутствие поля отключает **только** зависимые выводы.

### Code-truth слоя 1 (срез 2026-07-22)

| Правило | CODE |
|---------|------|
| Hard readiness | `astro_birth_date` + `numerology_life_path` → `is_ready` (`core_profile._hard_missing_fields`) |
| Soft unlocks в `missing_fields` | `first_name`, `gender`, `astro_birth_time`, `astro_location_name` (место только если время известно) |
| ASC/дома без времени | Engine + natal response strip; UI ещё имеет Δ (wheel ASC=0, soft copy) |
| Имя | Опционально в core-setup; date-only numerology без Expression/Soul/Personality |
| Timezone с setup | Часто не пишется → Δ точной карты |

---

## Слой 2 — Экран × доступ

| Экран | Guest | Free | Trial | Paid |
|-------|-------|------|-------|------|
| **Landing** | ✅ основной вход | — (redirect) | — | — |
| **Profile** | Демо / teaser · CTA регистрация | **Базовый** по данным слоя 1 | **Полный** по данным слоя 1 | **Полный** + глубина (почему / как проявляется / longitudinal) |
| **Today** | Демо / guest first-today draft | **Базовый** день (без house-based, без premium life-context) | **Полный** день по имеющимся данным | **Полный** + глубина narrative / memory |
| **Compatibility** | Пример / teaser · лимит проверок | Ограничено (truncate, без premium dynamics) | Полностью по данным пары | Полностью + premium layers |
| **Tarot** | Пример · лимит спредов | База (ограниченная глубина контекста) | Полностью | Полностью |

### Code Δ слоя 2 (не скрывать)

| Ячейка | TARGET | CODE сегодня |
|--------|--------|--------------|
| Guest Profile | Демо | Auth gate — полного демо-Profile на `/profile` нет |
| Guest Today | Демо | Guest gate **или** `GuestFirstTodayScreen` при draft |
| Guest Compat | Пример + лимит | ✅ local limit 4 · API tier `guest` |
| Guest Tarot | Пример + лимит | ✅ local limit 1 · public draw |
| Free Profile/Today | Базовый | Фактически почти полный UI; глубина режется insight tier в narrative / spheres / compat, не «базовый экран» |
| Trial = полный | Целостный опыт | Stripe `trialing` = entitlements плана; отдельного product-trial tier нет |
| Paid = глубина | Не серые замки | Частично: insight `pro`/`premium`; Compat paid; practices caps |

---

## Слой 3 — Блок → данные → источник → kind → API → зачем

Заполняется **по одному блоку**. Нет строки → блока нет в production.

Колонки:

| Поле | Вопрос |
|------|--------|
| **Блок** | Что видит пользователь |
| **Данные** | Минимальное состояние слоя 1 (+ living, если нужно) |
| **Доступ** | Guest / Free / Trial / Paid |
| **Источник** | endpoint / local / calc |
| **Kind** | `deterministic` · `llm` · `hybrid` |
| **Appear when** | условие показа |
| **Hide when** | честный omit |
| **Зачем** | ценность блока для человека |

### 3.1 Profile — первый уровень (TARGET pack)

| Блок | Данные | Доступ | Источник | Kind | Appear when | Hide when | Зачем |
|------|--------|--------|----------|------|-------------|-----------|-------|
| Кто ты (`recognition_line`) | ≥ дата + готовый contract | Free+ | `GET /account/core-profile` → `profile_contract_v1.recognition_line` | llm (identity step) | `recognition_line` non-empty | нет даты / forming без текста | Узнавание с первого взгляда |
| 3 особенности (решения / близость / трение) | ≥ дата + styles/growth | Free+ | `decision_style` · `relationship_style` · `growth_zones[0]` | llm → reshape UI | каждый слот отдельно | слот пуст | Три наблюдаемых черты |
| Противоречие | ≥ дата + insight node | Free+ | `insight_nodes_v0.nodes[0]` | deterministic from contract | title+insight | нет node | Главное напряжение |
| Что помогает | ≥ дата + help/effort | Free+ | `effort_vector_v0` ‖ `helps[0]` | deterministic | non-empty | пусто | Один практический вывод |
| CTA полный профиль | любой ready base | Free+ | UI | — | есть тело полного профиля | нет тела | Переход в глубину |
| CTA Today | ready base | Free+ | UI → `/today` | — | всегда на L1 | — | Дневная петля |
| Асцендент / дома (в полном профиле) | дата+время+место | Trial/Paid глубина; структура — при данных | `GET /natal-chart/` | deterministic | `houses_available` / not `time_unknown` | нет времени или места | Пространственная карта жизни |
| Нумерология имени | имя + система | Free+ как слой | numerology expression/soul/personality | deterministic | имя usable | нет имени | Отдельный слой самопрезентации |
| «Почему портрет такой» / kitchen sources | — | **не на L1** | — | — | — | всегда скрыто с L1 | Кухня ≠ продукт |

### 3.2 Today — каркас (TARGET; детализация после APPROVED слоя 2)

| Блок | Данные | Доступ | Источник | Kind | Hide when | Зачем |
|------|--------|--------|----------|------|-----------|-------|
| Главное сообщение дня | ≥ дата | Free+ | `/today/contract` · day_story | hybrid | нет базы | «Что происходит сегодня» |
| Primary action | ≥ дата | Free+ | contract `primary_action` | hybrid | пусто | Один шаг |
| Domain lenses (relations / money / family) | ≥ дата; **без house-claims** если нет времени | Free+ base · Paid depth | contract domains | hybrid | house-based claim без домов | Рыночные линзы дня |
| Week / phase | циклы даты; транзиты полной карты только при полном natal | Trial/Paid для полной персонализации | week/cycle APIs (уточнить строки после APPROVED) | hybrid | house-transit без домов | Горизонт как у CHANI |
| Practice / reflection | каталог + personalization caps | Guest limited · Free capped · Paid fuller | practices APIs | mixed | personalized overflow | Закрепить день |
| Guest demo day | нет аккаунта | Guest | local draft / demo | deterministic+copy | — | Ценность до регистрации |

### 3.3 Compatibility · Tarot (сводка; детали в своих канонах)

| Блок / поверхность | Данные | Guest | Free | Trial/Paid | Kind | Канон деталей |
|--------------------|--------|-------|------|------------|------|----------------|
| Compat teaser | знаки / пример | ✅ лимит | truncate | full | hybrid | COMPATIBILITY_CONTENT_CANON_V1 |
| Compat full bond-style | birth data пары | — | ограничено | full | hybrid | + `compatibility_access_v0` |
| Tarot draw | колода | ✅ 1 spread | auth draws | full context | hybrid | Tarot routes |
| Tarot personal context | profile/today link | — | limited | full | llm/hybrid | — |

---

## Open decisions (блокируют APPROVED)

Пока не закрыты — матрица остаётся DRAFT.

1. **Trial:** длительность · привязка к Stripe plan · что остаётся после окончания (ровно Paid vs откат к Free base).  
2. **Free Profile/Today «базовый»:** какие блоки L1 остаются на Free, а какие — только Trial/Paid depth (сейчас UI почти не режет).  
3. **Guest Profile демо:** нужен ли публичный teaser Profile без auth, или только Landing examples.  
4. **Plus (`lite`) vs Pro:** одна колонка Paid или две глубины в слое 2/3.  
5. **Имя в онбординге:** спрашиваем сразу или только как unlock CTA.  
6. **Timezone:** обязателен ли IANA TZ при времени+месте до показа ASC (honesty gate).

---

## Порядок работы после APPROVED

1. Закрыть Open decisions (Product).  
2. Дописать слой 3 для **каждого** production-блока Profile → Today → Compat → Tarot.  
3. Capability Resolver — [PRODUCT_CAPABILITY_CONTRACTS.md](./PRODUCT_CAPABILITY_CONTRACTS.md).  
4. Generation Contracts (deps graph) — [PRODUCT_GENERATION_CONTRACTS.md](./PRODUCT_GENERATION_CONTRACTS.md).  
5. Только затем: wiring · gates · UI — **строго по контрактам**.  
4. Любой новый блок без строки слоя 3 = не реализуется.

---

## Changelog

| Date | Change |
|------|--------|
| 2026-07-22 | v0.1 DRAFT — три слоя; freeze Profile/Today; code Δ; open decisions |
| 2026-07-22 | v0.2 — слой 0 Intake (ровно 2 способа) → PRODUCT_DATA_INTAKE |
| 2026-07-22 | v0.3 — pointer → PRODUCT_CAPABILITY_CONTRACTS (L1/L2/L3 API) |

# Product Availability Matrix

**Статус:** **APPROVED (Profile)** · Today / Compat / Tarot слой 3 — каркас (детализация после Profile wiring)  
**Роль:** отправная точка продукта. API · генерация · UI — **следствия** этой таблицы, не наоборот.  
**Владелец:** Product  
**Связь:** [audits/FULL_USER_PATH_CANON_V1.md](./audits/FULL_USER_PATH_CANON_V1.md) · [PRODUCT_DATA_INTAKE.md](./PRODUCT_DATA_INTAKE.md) · [PRODUCT_CAPABILITY_CONTRACTS.md](./PRODUCT_CAPABILITY_CONTRACTS.md) · [PRODUCT_GENERATION_CONTRACTS.md](./PRODUCT_GENERATION_CONTRACTS.md) · [PRODUCT_DATA_PROVIDERS.md](./PRODUCT_DATA_PROVIDERS.md) · Understanding Progress · Compat · Voice  

**Не путать:** это не architectural engine/registry. Это матрица **состояний пользователя → доступность блоков**.

**Факты карты (MVP):** SoT = LLM `natal_facts` ([PRODUCT_DATA_PROVIDERS](./PRODUCT_DATA_PROVIDERS.md)). Swiss / local ephemeris — **legacy read**, не SoT продукта. Интерпретация **не** пересчитывает карту.

---

## Режим подачи (сквозь продукт)

Суть не в формулировке полей и не в чеклисте «почему».  
Суть в **как подаём информацию** — каждая поверхность ведёт человека через **свою историю**:

| Поверхность | Режим подачи | Человек читает |
|-------------|--------------|----------------|
| **Profile** | История **человека** | Кто я: опоры, характер, напряжения, рост — сверху вниз, постепенно |
| **Today** | История **дня** | Какой сегодня день и что из него следует (символы, карта, число, действия, сферы, практика) |
| **Compatibility** | История **отношений / встречи** | Что происходит между людьми и событиями связи — не два отдельных портрета рядом |
| **Tarot** | **Поиск ответа** | Вопрос → расклад → смысл ответа в жизни; не каталог карт |

Правила режима:

1. UI и промпт **служат истории поверхности**, а не витрине независимых виджетов.  
2. Блоки — главы одной истории; пустая глава не рисуется (omit + ценность следующего шага).  
3. Авторский стиль практики один; меняется **сюжет** (я / день / мы / ответ), не личность рассказчика.  
4. Facts + catalog дают материал; Implementation пишет историю поверхности.

Связь: [TODAYFLOW_VOICE_CANON](./content/TODAYFLOW_VOICE_CANON.md) · Generation Contracts (один Implementation на историю экрана).

---

## Freeze

Пока Profile **не wired** по слою 3.1:

```text
⛔ не менять IA / блоки Profile production UI «на глаз»
⛔ не менять IA / блоки Today production UI
⛔ не добавлять новые LLM-поверхности Profile / Today вне строк матрицы
⛔ не добавлять публичные формы birth data вне PRODUCT_DATA_INTAKE (1A / 1B / 2)
✅ можно: код, который реализует уже принятую строку 3.1 / intake / natal_facts
✅ можно: дополнять code-truth Δ в этой таблице
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

| Продукт | Код сегодня | Решение (APPROVED Profile) |
|---------|-------------|----------------------------|
| **Guest** | `user is None` + `guestAccessLimits` | Без персонального `/profile`; ценность на Landing + 1A/1B preview |
| **Free** | `subscription_level=free` | L1 base + L2 structure **если данные есть**; **без** deep L3 packs |
| **Trial** | Stripe `trialing` на плане | = Paid depth на время trial (целостный опыт). Длительность / plan — billing ops, не блокер матрицы блоков |
| **Paid** | `lite`/`pro` → insight tiers | Одна колонка **Paid** в слое 2/3: глубина L3; Plus vs Pro = caps внутри Paid, не второй продукт |

Правило глубины: [UNDERSTANDING_PROGRESS](./UNDERSTANDING_PROGRESS_AND_DEPTH_CANON.md) — подписка меняет **глубину**, не наличие базового ответа при данных.

Легенда: **TARGET** = продукт · **CODE** = репо · **Δ** = закрыть при wiring.

---

## Слой 1 — Данные рождения → доступность

### 1.0 Поле → что даёт / что теряется

| Поле | Что даёт системе | Что даёт продукту | Без поля |
|------|------------------|-------------------|----------|
| **Имя** | Именная нумерология (Expression / Soul Urge / Personality) при канонической системе | Слой самопрезентации / мотивации / внешнего образа | Натал **не** страдает. Omit слой «Нумерология имени» + CTA |
| **Дата** | Солнце, планеты по знакам, часть аспектов, life path, birthday number, циклы даты; `natal_facts` mode `date_only` | Базовый профиль, нумерологическое ядро, Today без house-claims | Нет персонального Profile / Today / Compat / Tarot-контекста |
| **Время** | ASC, дома, MC/IC/DSC, точная Луна, углы, house-based транзиты; `natal_facts` mode `full` **только вместе с местом** | Внешнее проявление, сферы через дома, карьерная ось | Нельзя ASC/дома/MC; Луна/часть аспектов менее точны |
| **Место** | lat/lon/TZ → корректный UTC и углы/дома | Нужно **вместе со временем** | Время без места **не** использовать для ASC/домов; сохранить место на будущее без видимости «большей точности» |

**Главное правило:** отсутствие поля отключает **только** зависимые выводы, не весь профиль.

### 1.1 Состояния → открыто / скрыто / copy

| Состояние данных | Что открывается | Что скрывается / запрещено | Что объясняем (Voice) |
|------------------|-----------------|----------------------------|------------------------|
| **Нет регистрации** | Landing, демо, guest-лимиты Tarot/Compat/Practices, 1A/1B preview | Персональный `/profile`, полный Snapshot | «Соберите профиль, чтобы получить персональный разбор.» |
| **Зарегистрирован, без даты** | Онбординг / setup | Profile · Today · Compat · Tarot-контекст | «Добавьте дату рождения, чтобы построить основу профиля.» |
| **Только дата** | Базовый Profile (L1) · базовый Today · нумерология даты · планеты по знакам / часть аспектов · циклы | ASC · дома · MC/IC · house-based сферы/транзиты · именная нумерология (если нет имени) | «Дата создаёт астрологическую и нумерологическую основу. Время рождения откроет Асцендент, дома и жизненные сферы.» |
| **Дата + место, без времени** | То же, что «только дата». Место **сохраняем** | Всё от времени. **Запрет** показывать «более точную» карту из-за места | «Без времени нельзя определить дома и Асцендент. Место понадобится вместе со временем.» |
| **Дата + время, без места** | То же, что «только дата» для углов | ASC/дома/MC — **не** считать по «голому» времени | «Чтобы рассчитать Асцендент и дома, укажите место рождения — нужны координаты и часовой пояс.» |
| **Дата + время + место** | Полная карта · L2 structural profile · точные транзиты/углы | Только именная нумерология (если нет имени) | «Добавьте имя для отдельного разбора имени — на натальную карту оно не влияет.» |
| **Полные birth + имя** | Всё выше + Expression / Soul Urge / Personality | — | — |

### 1.2 Code-truth (срез; wiring закрывает Δ)

| Правило | CODE |
|---------|------|
| Hard readiness | `astro_birth_date` + `numerology_life_path` → `is_ready` |
| Soft missing | `first_name`, `gender`, `astro_birth_time`, `astro_location_name` (место если время известно) |
| Facts MVP | `POST /profile/natal-facts` · `profile.natal_facts.v1` |
| Имя | Optional; без Expression/Soul/Personality если нет имени |
| Δ | Legacy funnel `identity/styles/patterns` ещё пишет Snapshot; TARGET = слоты 3.1 + Generation Contracts |

---

## Слой 2 — Экран × доступ (APPROVED Profile)

| Экран | Guest | Free | Trial | Paid |
|-------|-------|------|-------|------|
| **Landing** | ✅ основной вход | redirect если auth | — | — |
| **Profile** | **Нет** полного `/profile`. Preview в 1B / Landing | **L1 + L2 structure** по данным слоя 1; **без** deep L3 | = Paid depth | L1+L2+L3 depth (+ living later) |
| **Today** | Preview / gate (не полный день) | Базовый день; **без** house-based claims | Полный по данным | Полный + depth |
| **Compatibility** | Teaser + лимит · gated preview 1A | Ограничено | Full по данным пары | Full + premium layers |
| **Tarot** | Лимит | База | Full | Full |

### Profile Free vs Trial/Paid (одно правило)

| Слой смысла | Free | Trial / Paid |
|-------------|------|--------------|
| **L1** identity / sun / element / date numerology / catalog keys | ✅ если поля заполнены | ✅ |
| **L2** ASC, дома, structural styles (emotional, decision, relationship, work, money, home) | ✅ **если** date+time+place; иначе omit + CTA | ✅ при тех же данных |
| **L3** deep helps, conflict patterns, practical «что делать», longitudinal | ❌ omit / soft CTA trial | ✅ |

### Глубина: до регистрации → после аккаунта → после подписки

Одна ось доступа (не вторая интерпретация):

| Момент | Кто | Что видит | Что уже построено |
|--------|-----|-----------|-------------------|
| **До регистрации** | Guest | Preview 1A/1B / Landing — ценность и узнавание, **не** полный `/profile` | Draft facts + preview interpretation; bind при email |
| **После регистрации** | Free | L1 + L2 по данным; шапка и структура; **без** deep L3 reveal | Полный результат в `slots` (включая L3), UI режет `revealed` |
| **После подписки / trial** | Trial = Paid depth | L1+L2+L3: helps, практические выводы, глубокие паттерны | **Тот же** сохранённый профиль — только раскрытие |

Правила:

1. Данные (дата/время/место/имя) задают **что можно вычислить**.  
2. Тариф задаёт **что можно показать**.  
3. Промпты facts + interpretation строят **полный** пакет по данным; Guest/Free/Trial не запускают «другую личность».  
4. До регистрации глубина = **preview**, не урезанный production Profile.

### Code Δ слоя 2

| Ячейка | TARGET | CODE |
|--------|--------|------|
| Guest Profile | Нет полного `/profile` | ✅ auth gate; ценность 1B preview |
| Free Profile | L1+L2 data-gated; L3 **в результате**, reveal Trial+ | ✅ `data_eligible` ⊇ L3; `revealed` без L3 на Free; UI читает `revealed_slots` |
| Trial = Paid depth | Целостный; тот же saved profile | ✅ `resolve_access_tier` (`trialing` → trial); не вторая интерпретация |

---

## Слой 3 — Блок → данные → contract → hide → copy

**Правило экрана:** сначала слоты матрицы → затем Generation Contract с `allowed_output` → ответ **только** в слоты. Нет строки → блока нет в production.

### Колонки 3.1

| Поле | Вопрос |
|------|--------|
| **Блок** | Что видит человек (RU) |
| **Данные** | Минимум слоя 1 |
| **Доступ** | Guest / Free / Trial / Paid |
| **Facts** | Ключи `natal_facts` / catalog / none |
| **contract_id** | Generation Contracts |
| **Kind** | `llm` · `catalog` · `ui` |
| **Appear when** | Условие показа |
| **Hide when** | Честный omit |
| **Copy если нет** | Voice: что откроется |
| **Зачем** | Ценность |

### 3.1 Profile — слоты (APPROVED TARGET)

#### Композиция экрана (чтение сверху вниз)

```text
┌─ ШАПКА (fixed facts) ─────────────────────────────────────┐
│  Узнавание · Солнце/стихия/numerology_core · Соответствия │
│  (+ нумерология имени, если имя есть)                     │
│  = вся стабильная информация из birth data + каталога     │
└───────────────────────────────────────────────────────────┘
        ↓ постепенно раскрываем человека
┌─ СТРУКТУРА (если full natal) ─────────────────────────────┐
│  ASC / дома / MC/IC                                       │
└───────────────────────────────────────────────────────────┘
        ↓
┌─ ИНТЕРПРЕТАЦИЯ (personality layers) ──────────────────────┐
│  эмоции → решения → отношения → работа → деньги → дом     │
│  → сильные стороны → напряжения/рост                      │
└───────────────────────────────────────────────────────────┘
        ↓
┌─ ПРАКТИКА / ГЛУБИНА (L3 reveal) ──────────────────────────┐
│  helps / «что делать» — Trial+                            │
└───────────────────────────────────────────────────────────┘
        + Limitations/CTA данных там, где слот скрыт из-за ввода
        + CTA Today внизу при ready base
```

**Правила композиции**

1. **Шапка** = вся **фиксированная** информация: то, что однозначно следует из даты (± имя) и каталога, не «мнение на сегодня».
2. **Соответствия в шапке** — можно и нужно показывать знак/число в **других культурах и гороскопах** (китайский, ведический ярлык, тибетский и т.п.), **только** если есть ключ в **накопленной базе знаний / каталоге**. Lookup по дате/знаку — **код**, не LLM. Нет ключа → блок не рисуем, без догадок.
3. **Нет данных → нет блока.** Вместо заглушки — omit + одна фраза из слоя 1.1 / `user_messages`: что откроется после ввода или на что влияет отсутствие.
4. **Раскрытие сверху вниз:** сначала фиксированная опора (шапка), затем структура карты, затем слои характера, затем практика. Не прыгать к L3/helps раньше узнавания и опор.
5. Тариф **не** меняет порядок и не выкидывает слои из сохранённого результата — только reveal нижних глубинных слотов.
6. **Не спрашивать модель** «какой знак 13 февраля» / «чей год 1990» — это справочник; модель пишет смысл только из уже полученных keys + `natal_facts`.

Поток данных:

```text
available_input → natal_facts (LLM) → calculated_facts + unavailable
  → contracts: base_astrology? · name_numerology? · natal_chart? · personality · growth?
  → UI кладёт только non-null allowed/revealed fields, сверху вниз по таблице
```

| Блок | Данные | Доступ | Facts | contract_id | Kind | Appear when | Hide when | Copy если нет | Зачем |
|------|--------|--------|-------|-------------|------|-------------|-----------|---------------|-------|
| **Узнавание** (`identity_summary`) · *шапка* | ≥ дата | Free+ | sun / life_path / element… | `personality` | llm | non-empty | нет даты / forming | «Добавьте дату рождения, чтобы увидеть основу профиля.» | Узнать себя с первого взгляда |
| **Солнце · стихия · numerology_core** · *шапка* | ≥ дата | Free+ | sun_sign, element, life_path, birthday… | `base_astrology` (+ date numbers in facts) | llm + facts | keys present | нет даты | — (блок с датой) | Базовые опоры карты и чисел |
| **Соответствия** (камень/цвет · **знак в других культурах/гороскопах**) · *шапка* | ≥ дата + catalog keys | Free+ | catalog via sun/sign/number keys | `base_astrology` | catalog | keys present | нет keys в каталоге | omit без выдумки; при partial — CTA только на отсутствующий ввод, не на «пустой каталог» | Мягкий культурный слой: один знак — разные традиции |
| **Нумерология имени** · *шапка, optional* | имя + дата | Free+ | name numbers | `name_numerology` | llm | имя usable | нет имени | «Добавьте имя для разбора имени — на натальную карту не влияет.» | Самопрезентация / мотивация |
| **Структура карты** (ASC, дома, MC/IC) | дата+время+место | Free+ (структура); deep copy Trial+ | angles, houses | `natal_chart` | llm on facts | `natal_facts.mode=full` | нет времени **или** места | Время без места: «Укажите место…». Без времени: «Время откроет Асцендент и дома.» | Пространственная карта жизни |
| **Эмоции** (`emotional_style`) | ≥ дата; house-based только full | Free+ | moon, water…; house moon only if full | `personality` | llm | non-null | insufficient facts → null | omit | Как чувствует и защищается |
| **Решения** (`decision_style`) | ≥ дата | Free+ | mercury/mars/modality… | `personality` | llm | non-null | null | omit | Как принимает решения |
| **Отношения** (`relationship_style`) | ≥ дата; 7th/DSC только full | Free+ | venus…; houses if full | `personality` / `relationships` | llm | non-null | null / no house facts for house-claims | Без времени не показывать house-based близость | Близость и трение |
| **Работа / реализация** | ≥ дата; MC/10th только full | Free+ structure | saturn/MC… | `personality` / `career` | llm | non-null | house-claims without full | «Время и место откроют карьерную ось (MC).» | Реализация |
| **Деньги** | ≥ дата; 2/8 только full | Free+ | venus… | `personality` / `money` | llm | non-null | house-claims without full | omit house-money | Деньги и ресурсы |
| **Дом / безопасность** | full natal | Free+ если full | IC/4th/moon | `personality` | llm | full mode | нет full | «Время и место откроют ось дома и корней.» | База безопасности |
| **Сильные стороны** (`strengths` / `core_strengths`) | ≥ дата | Free+ | dominants / harmonious | `personality` | llm | non-empty array | empty | omit | На что опираться |
| **Напряжения / рост** (`internal_tensions`, `growth_zones`, `blind_spots`) | ≥ дата | Free+ L2 list; **deep pattern text** Trial+ | hard aspects, clashes | `personality` | llm | non-empty | empty | omit | Где конфликт и рост |
| **Что помогает** (`helps[]`) | L3: следствие выводов; living optional | **Trial / Paid** | prior claims only | `growth` | llm | non-empty + Trial+ | Free: omit; нет оснований → null | Free: «В trial откроются конкретные опоры.» | Практический следующий шаг |
| **Limitations + CTA данных** | любой partial | Free+ | `unavailable_facts` | — (UI from facts meta) | ui | always if unavailable non-empty | полный набор + имя | Конкретные фразы слоя 1.1 | Честность и следующий ввод |
| **CTA Today** | ready base (≥ дата) | Free+ | — | — | ui | `is_ready` | нет даты | — | Дневная петля |
| **CTA полный профиль / глубина** | есть L2/L3 тело | Free+ | — | — | ui | есть скрытые слоты | нет тела | — | Раскрыть карту |
| Kitchen / «почему система» / eligibility | — | **никогда** | — | — | — | — | всегда | — | Не продукт |

**Запрет:** показывать ASC/дома/MC или house-based текст, если факты в `unavailable_facts` или mode ≠ `full`.  
**Запрет:** показывать пустой блок шапки/интерпретации «на будущее» без CTA ценности.  
**Запрет:** выдумывать соответствия других гороскопов без catalog key.
### 3.1 Code Δ (не SoT)

| TARGET slot | CODE сегодня |
|-------------|--------------|
| Capability Resolver | ✅ `services/capability_resolver_v0.py` · `POST /profile/natal-facts` → `capability` |
| `identity_summary` | adapter ← `recognition_line` / `identity_core` (legacy Δ) |
| styles | adapter ← contract styles fields |
| helps L3 gated | ✅ omit on Free via `profile_slots.allowed` / adapter |
| natal structure | ✅ mode `full` only; precise `unavailable_facts` reasons |
| Wiring UI | следующий slice — слот за слотом по этой таблице |

### 3.2 Today — каркас (не APPROVED детально)

| Блок | Данные | Доступ | Источник | Kind | Hide when | Зачем |
|------|--------|--------|----------|------|-----------|-------|
| Главное сообщение дня | ≥ дата | Free+ | `/today/contract` · day_story | hybrid | нет базы | Смысл дня |
| Primary action | ≥ дата | Free+ | `primary_action` | hybrid | пусто | Один шаг |
| Domain lenses | ≥ дата; без house-claims без full natal | Free+ / Paid depth | contract domains | hybrid | house-claim без домов | Линзы дня |
| **Цвет / камень / запах / талисман дня** | день + астро-события дня + профиль пользователя | Free+ (depth по access) | `today` / day_story interpretation | **llm on day facts** | нет day context / нет профиля | Якорь дня — **рекомендация на сегодня**, не справочник |
| Guest / gate | нет аккаунта | Guest | preview / auth | ui | — | Ценность до bind |

#### Profile «камень/цвет» ≠ Today «цвет/запах дня»

| | **Шапка Profile** | **Символ дня (Today)** |
|--|--------------------|-------------------------|
| Что | Камень/цвет **знака** (и др. традиции) | Цвет / запах / камень / талисман **этого дня** |
| Откуда | **Каталог / база знаний** по ключу знака | **Интерпретация дня**: календарный день + астро-события + профиль |
| Меняется? | Нет (пока тот же birth/sign) | Каждый день |
| Можно ли взять «из базы» одним lookup? | Да | **Нет** — это рекомендация под день и человека |
| Промпт | Не нужен для ключа; LLM опционально для смысла знака | Нужен качественный **today / day_story** prompt на day facts + profile slice |

**Запрет:** выдавать «цвет дня» = `catalog[sun_sign]` или ротацию пресетов без дня/событий/профиля.  
**Запрет:** плодить независимые генераторы «камень дня» / «запах дня» вне контракта Today.  
**CODE Δ:** `celestial_events_builder._DAILY_SYMBOL_PRESETS` — legacy preset table; TARGET = производное от day interpretation, не отдельный SoT.

#### Today day pack — рассказ о дне (TARGET)

Не чеклист «обязательных почему».  
Символы, карта, число, сферы, практика и цели — **естественное продолжение** одной истории о дне: сначала характер дня, затем что из него следует для человека.

**Цель ответа:** качество · уникальность под этого человека и этот день · **устойчивый авторский стиль** практика (таро + астрология + нумерология). Не другой автор каждый раз; не шаблонный гороскоп.

| Слой в рассказе | Как входит в текст | Входы |
|-----------------|--------------------|-------|
| **Какой это день** | Характер, тон, что день несёт | дата, астро-события дня, профиль |
| **Цвет · запах · камень** | Продолжение дня: зачем они здесь и что усилят сегодня | day + events + profile |
| **Карта (если открыта)** | Как карта звучит *в этом* дне | draw + day narrative + profile |
| **Число (если открыто)** | Как число звучит *в этом* дне | number + day narrative + profile |
| **Делать / не делать** | Практический вывод из всей истории дня | вся сборка |
| **Сферы** | Что активнее сегодня — из той же истории | day + profile facts |
| **Практика · цели** | Что укрепит день и какие цели уместны | day + profile / intent |

#### Когда какой промпт (момент → Implementation)

Разделение с Profile: факты карты и портрет **не** пересчитываются ради Today.

```text
[Один раз / при смене birth]     catalog lookups
                                 + fact prompt `natal_facts`           → facts на профиле
                                 + interpretation `personality`…       → портрет (слоты 3.1)

[Утро / открытие Today]          собрать day facts (события, дата)
                                 + profile slice (уже сохранённый)
                                 → **today / day_story prompt**        → рассказ о дне
                                   (характер → символы → do/avoid → сферы → практика → цели)

[Когда пользователь открыл
 карту и/или число в ритуале]    те же day facts + draw/number
                                 → **тот же today Implementation**
                                   (refresh / enrich day_story)        → карта и число
                                                                       вплетены в уже
                                                                       рассказанный день
```

| Момент | Что вызываем | Чего не делаем |
|--------|--------------|----------------|
| Claim / birth save | `natal_facts` → `personality` (+ related) | Не пишем «цвет дня» |
| GET `/today/contract` (база дня) | `day_story` / contract `today` Implementation | Не новый fact-prompt карты; не preset-only символы |
| После reveal карты / числа | refresh того же `today` Implementation с новыми ritual inputs | Отдельный «промпт только про карту» вне дня |
| Смена тарифа | только reveal depth | Второй interpretation «для paid» |

**CODE сейчас:** `DAY_STORY_PROMPT_VER` = `day-story-v1.2-literary-editor` · wire `day_story_wire_v1` · optional enrich after ritual.  
**TARGET:** один авторский Implementation `today` с полным day pack; карта/число — продолжение того же текста при refresh.

**Запрет:** отдельные микро-промпты «почему цвет» / «почему карта» как чеклист; символ или карта вне истории дня; скачок стиля между блоками; смена автора при каждом запросе.

### 3.3 Compatibility · Tarot (сводка)

| Поверхность | Guest | Free | Trial/Paid | Kind |
|-------------|-------|------|------------|------|
| Compat teaser / 1A gated | ✅ лимит | truncate | full | hybrid |
| Tarot | ✅ лимит | base | full | hybrid |

---

## Closed decisions (Profile APPROVED)

| # | Решение |
|---|---------|
| 1 | **Trial** = Paid depth на время `trialing`. Длительность/plan — billing; не блокирует слоты 3.1. |
| 2 | **Free Profile** = L1 + L2 data-gated; **без** deep L3 (`helps` depth, conflict patterns, «что делать»). |
| 3 | **Guest Profile** = нет полного `/profile`; Landing + 1A/1B preview. |
| 4 | **Plus vs Pro** = одна колонка Paid; отличие = caps/depth knobs, не вторая IA. |
| 5 | **Имя** = optional в 1B (спрашиваем в welcome); без имени профиль работает; слой имени — omit + CTA. |
| 6 | **Timezone** = для показа ASC/домов нужен resolve места → lat/lon/TZ; без TZ/места углы не показывать (honesty). |
| 7 | **Шапка Profile** = вся фиксированная информация (узнавание · солнце/стихия/числа · соответствия культур/гороскопов · имя если есть). Не дневная интерпретация. |
| 8 | **Пустой блок не рисуем** — только omit + ценность следующего ввода (слой 1.1 / `user_messages`). |
| 9 | **Порядок экрана** = сверху вниз: шапка → структура → интерпретация → L3 практика. Постепенное раскрытие человека. |
| 10 | **База знаний / каталог** = накопление детерминированных ключей (знак по дате, год в культурах, камень/цвет…). LLM **не** переспрашиваем об этом каждый раз. Нет ключа → omit. |
| 11 | **Глубина доступа:** Guest = preview до регистрации; Free = L1+L2 reveal; Trial/Paid = +L3 reveal. Один interpretation-результат; тариф не запускает вторую личность. |
| 12 | **Цвет/запах/камень дня** = рекомендация Today из (день + астро-события + профиль), не catalog lookup знака. Profile-соответствия знака остаются в базе знаний. |
| 13 | **Today day pack** = одна история дня (не чеклист «обязательных почему»). Цель: качество, уникальность, авторский стиль. Карта/число — продолжение дня при том же `today` Implementation. |
| 14 | **Режим подачи:** Profile = история человека · Today = история дня · Compatibility = история отношений/событий · Tarot = поиск ответа. Не витрина блоков. |

---

## Порядок после Profile APPROVED

1. Capability Resolver в коде (`available_input` → mode → `unavailable_facts`).  
2. Production path: `natal_facts` → `personality` (+ optional `name_numerology` / `natal_chart` / `growth`) → persist → UI **только** слоты 3.1.  
3. Legacy `profile.identity|styles|patterns` — temporary adapter / Δ, не наращивать как SoT.  
4. Wire UI слот за слотом по 3.1.  
5. Затем детализировать Today / Compat слой 3.  
6. Блок без строки слоя 3 = не реализуется.

---

## Changelog

| Date | Change |
|------|--------|
| 2026-07-22 | v0.1 DRAFT — три слоя; freeze; open decisions |
| 2026-07-22 | v0.2 — слой 0 Intake |
| 2026-07-22 | v0.3 — Capability Contracts pointer |
| 2026-07-22 | **v1.0 APPROVED (Profile)** — поле→copy слой 1; Free/Trial/Guest слой 2; полная таблица слотов 3.1; closed decisions; facts SoT = `natal_facts` LLM |
| 2026-07-22 | CODE: Capability Resolver + natal_facts `capability` pack + matrix adapter (без UI IA) |
| 2026-07-22 | CODE: time-without-place preserved; Free/Trial = disclosure not second interpretation; Profile UI reads `revealed_slots` + `user_messages` |
| 2026-07-22 | ACCEPTANCE: `tests/test_profile_matrix_31_acceptance.py` — 6 payloads + contradiction rules (gated∈slots, data-omit∉slots) |
| 2026-07-23 | **Composition lock:** шапка = fixed facts (+ multi-tradition catalog); empty→omit+CTA; reveal top→bottom |
| 2026-07-23 | **Knowledge base:** deterministic catalog lookups (sign/year/traditions); LLM must not re-ask; providers §0 |
| 2026-07-23 | Depth axis explicit: Guest preview → Free L1+L2 → Trial/Paid +L3; same interpretation |
| 2026-07-23 | Day color/scent ≠ profile catalog: today recommendation from day+events+profile |
| 2026-07-23 | Today day pack = narrative continuity + prompt timing; goal quality/uniqueness/author voice |
| 2026-07-23 | **Presentation mode:** Profile/Today/Compat/Tarot = story kinds (decision #14) |

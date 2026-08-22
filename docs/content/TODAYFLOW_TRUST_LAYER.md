# TodayFlow Trust Layer — brand language & copywriting

**Статус:** ACCEPTED — публичная концепция бренда (не внутренняя особенность Interpretation Library).  
**Версия:** 1.3 (2026-08-17).  
**Владелец:** Product + Content.  
**Принять в работу:** реклама (бриф §6) · App Store / about / press. Лендинг — **бренд-поверхность** (не kicker `#trust`).

**Связь:** [TODAYFLOW_VOICE_CANON.md](./TODAYFLOW_VOICE_CANON.md) (in-product голос) · [EXPLAINABLE_COMPUTATION_AND_INTERPRETATION.md](../explainability/EXPLAINABLE_COMPUTATION_AND_INTERPRETATION.md) · [EXPLAIN_MEANING_NOT_MECHANISM.md](../explainability/EXPLAIN_MEANING_NOT_MECHANISM.md) · [foundation_v1.md](../foundation_v1.md) §1.4.1 (факты NASA/JPL) · [INTERPRETATION_LIBRARY_V1.md](../astrology/INTERPRETATION_LIBRARY_V1.md) (методика слоёв, не бренд-SoT) · [PRODUCT_TRUTH_FIRST.md](../PRODUCT_TRUTH_FIRST.md)

---

## Architecture impact

- **SoT before:** provenance / multi-school Canon жили как внутренняя методика IL (§6). NASA/JPL — runtime footnote (Swiss) и «кандидат Horizons». Лендинг говорил про память дней (Guest Story dual CTA), не про две опоры доверия.
- **SoT after:** публичный **Trust Layer** = язык бренда. Две опоры коммуникации: (1) точность астрономических данных, (2) глубина интерпретации как нормализованное пересечение исторических слоёв с provenance. IL остаётся lookup смысла, не единственным местом этой мысли. Лендинг **строится на locked line**, а не носит её как slogan.
- **Public contract changed?** no — JSON / generation не меняются. Меняется **разрешённый** маркетинговый язык и **порядок** лендинга (тезис до инструментов).
- **Migration required?** no runtime. Landing H1 = locked three beats. Dual hero CTA retired. Ads use §6.
- **Canon updated?** this doc · Voice Canon §0.08 · Unified §0 · Foundation §1.4.1 · IL pointer · explainability indexes · Guest Story P0 landing-narrative supersession.
- **Backward compatible?** yes — in-product Voice Canon §0 («не говорит о себе») остаётся для Profile / Today / Tarot / Compatibility body. Guest path Landing → `/demo/today` → invite **сохраняется**.

---

## 0. Зачем это публично

Внутри Interpretation Library проявляется полезная вещь:

> TodayFlow Canon — **не одна усреднённая астрология**, а нормализованное пересечение исторически разных слоёв, где provenance позволяет знать происхождение каждого утверждения.

Это не «фича библиотеки». Это **основа копирайтинга и доверия**.  
Кухня (JSON claims, `evidence_tier`, Swiss flags) пользователю в Today не показывается. **Следствие** кухни — можно честно сказать рынку, на чём стоит продукт.

Два разных вопроса, которые нельзя склеивать:

| Вопрос рынка | Ответ TodayFlow |
|--------------|-----------------|
| Откуда числа на небе? | Астрономический слой. Точные эфемериды NASA/JPL **там, где они фактически источник или верификация**. |
| Откуда смысл? | Canon собирает и нормализует разные исторические слои и школы, сохраняя происхождение и степень подтверждённости. Не выдаёт одну современную трактовку за единственную «астрологическую истину». |

Третий удар линии — уже существующее обещание продукта: смысл собирается **для этого человека**, не как общий гороскоп.

---

## 1. Locked line (концепция)

Английская формула **зафиксирована** как идея позиционирования. Каденцию RU/локалей можно полировать; **смысл трёх ударов — нет**.

```text
Precise astronomical data.
Centuries of astrological interpretation.
One personal perspective.
```

**RU (рабочая, не шаблон-клише):**

```text
Точные астрономические данные.
Столетия астрологической интерпретации.
Один личный взгляд.
```

Три удара = три уровня доверия. Не сжимать в «мы точнее гороскопов» и не делать NASA поручителем смысла.

| Удар | Уровень доверия | Что обещаем | Чего не обещаем |
|------|-----------------|-------------|-----------------|
| Precise astronomical data | **Точность** | Положения тел считаются по астрономическим эфемеридам NASA/JPL (через Swiss Ephemeris) | NASA «подтвердила гороскоп» · партнёрство · live API Horizons · «без округлений» как абсолют |
| Centuries of interpretation | **Глубина** | Canon держит слои традиции различимыми; не одна модная школа | Полный каталог уже в приложении · «одна школа, которой доверяли задолго до нас» |
| One personal perspective | **Человечность** | Personal Model / Profile / Today — смысл для человека | «Единственно верная астрология» · «прочитано человеком, а не алгоритмом» |

---

## 2. Две опоры коммуникации

### 2.1 Точность исходных данных (астрономия)

Положение небесных тел — **астрономический** слой. Смысл сюда не подмешивается.

Публично можно говорить о точных астрономических данных NASA/JPL **только** в той роли, которая есть в коде и каноне геометрии. Факты: [foundation_v1.md](../foundation_v1.md) §1.4.1.

**Сейчас LIVE:** Swiss Ephemeris (`FLG_SWIEPH`, `pyswisseph`, файлы `astro/ephe`). По документации Astrodienst сжатые файлы Swiss воспроизводят **NASA JPL Development Ephemeris DE431** (для `pyswisseph >= 2.10`: линейка Swiss 2.00+, DE431). Это и есть честная формула «данные NASA/JPL».

**Не LIVE:** NASA/JPL Horizons API — кандидат на независимую сверку позиций; **не wired**. Нельзя писать «мы берём координаты из Horizons».

**Не этот слой:** NASA Photojournal / LRO-карты Луны в UI — визуальный identity, не источник положений. Нельзя смешивать «фото NASA» и «точность эфемерид» как одно доказательство.

### 2.2 Глубина интерпретации (Canon)

TodayFlow не выдаёт одну современную трактовку за единственно существующую астрологическую истину.

Canon:

- собирает **исторически разные** слои и школы (classical · traditional · psychological · professional);
- **нормализует** утверждения (свои lemmas), а не усредняет авторов в кашу;
- сохраняет **происхождение** каждого утверждения (автор, издание, locus, paraphrase);
- хранит **степень подтверждённости** (`core` / `supported` / `school_specific` / `editorial`).

Методика и схема — [INTERPRETATION_LIBRARY_V1.md](../astrology/INTERPRETATION_LIBRARY_V1.md) §6.  
Публичный язык — этот документ. Не тащить в рекламу имена JSON-полей.

**Честность статуса (Truth First):** IL-1 in progress; объекты `draft`, ничего `active`. Бренд обещает **метод** (слои + provenance), не «в приложении уже полный многовековой канон с витриной источников». Астрономический удар можно утверждать как live. Интерпретационный — как устройство знания и направление продукта, без фальшивой готовности каталога.

---

## 3. Что можно и нельзя писать

### Можно (landing · ads · about · press)

- Точные положения планет считаются по эфемеридам NASA JPL (Swiss Ephemeris / DE431).
- Астрономия и астрология у нас **разведены**: небо — факт; смысл — Canon слоёв.
- Мы не выдаём одну современную школу за всю традицию.
- Утверждения смысла имеют происхождение и разную степень опоры; спорное одной школы не становится «астрология говорит».
- Locked line (§1) и её локальные ритмические варианты.

### Нельзя

| Запрет | Почему |
|--------|--------|
| «Powered by NASA» / «NASA-certified» / логотип как endorsement | нет партнёрства; NASA не толкует карту |
| «Мы запрашиваем NASA Horizons» | API не wired |
| «NASA подтвердила ваш гороскоп» | смешение астрономии и смысла |
| «Единственно верная / научная астрология» · «фундамент — наука» | Canon против одной истины; астрономия ≠ поручитель смысла |
| «Прочитана человеком, а не алгоритмом» | запрет кухни; продукт не живой астролог в чате |
| «Небо не лжёт» как обещание смысла | точны положения, не «небо сказало, что делать» |
| «Усреднили все школы в один правильный текст» | противоположность provenance |
| «Полная библиотека веков уже в Today» | IL ещё draft |
| Кухня в рекламе: `evidence_tier`, Swiss flags, «алгоритм выбрал» | Trust Layer ≠ mechanism dump |
| Фото NASA как доказательство точности позиций | другой слой (identity) |

NASA/JPL в копирайте = **источник астрономических положений** (или будущая верификация, когда Horizons реально включат). Никогда = источник трактовки.

---

## 4. Поверхности (не путать с Voice Canon §0)

| Поверхность | Trust Layer | Voice Canon «не говорит о себе» |
|-------------|-------------|----------------------------------|
| **Landing · реклама · App Store · about · press** | **да** — две опоры + locked line | исключение: здесь бренд **имеет право** назвать опоры доверия |
| Profile · Today · Compatibility · Tarot · email/push **body** | нет как самопрезентация системы | **да, жёстко** — текст о человеке и смысле дня, не о NASA и не о Canon |

Маркетинг говорит, **на чём стоит** продукт.  
Экран дня говорит, **что это значит для человека**.  
Не тащить «данные NASA» в совет «сегодня пауза перед договором».

Связь с [EXPLAIN_MEANING_NOT_MECHANISM.md](../explainability/EXPLAIN_MEANING_NOT_MECHANISM.md): на acquisition можно назвать два слоя доверия (небо / традиция / личный взгляд). Нельзя вываливать scores, registry, «алгоритм».

---

## 5. Лендинг = бренд-поверхность

Концепция **locked**. Не подменять north star Personal Model. Trust Layer объясняет **опоры знания**; Personal Model остаётся тем, **для кого** собирается взгляд.

Лендинг — не Guest Story merchandising с Trust как kicker. Принцип как у Co-Star: **имя + манифест в первом экране**, «что это» **до** инструментов, главы продукта после тезиса. Не клонировать Co-Star (нет фейковых отзывов, нет «algorithmically generate», нет Powered by NASA).

| Экран | Роль |
|-------|------|
| **Hero** | Locked three beats = **H1**. Манифест (NASA JPL = эфемериды; Canon = метод). Луна = живой астрономический объект (фаза правда, yaw от курсора без смены фазы). Один primary CTA → `/demo/today`. |
| **#trust** | «Что это» — три опоры редакционно, не sparkle-tiles |
| **#today** | Один личный взгляд / continuity как продукт |
| **#compatibility** | Полная глава (L1), не dual-CTA в hero |
| **#tarot / #practices** | Вторичные инструменты после тезиса |
| **#cta** | Закрытие. Без invented testimonials |

Live copy: `frontend/src/components/product-ui/productWebLandingContent.ts`.

| Поверхность | Статус |
|-------------|--------|
| **Лендинг** | **CODE** — бренд-первый порядок · H1 = locked line · Moon signature · footer. Guest path demo→invite сохранён. Dual hero CTA и `#why` сняты. |
| **Реклама** | бриф §6 — использовать, не изобретать NASA-партнёрство |
| About / press-kit | тот же каркас, без overclaim IL |

---

## 6. Рекламный бриф (короткие варианты)

Смысл трёх ударов не менять. Каденцию можно короче. Запреты §3 обязательны в любом креативе.

### Locked (основной)

```text
EN  Precise astronomical data. Centuries of astrological interpretation. One personal perspective.
RU  Точные астрономические данные. Столетия астрологической интерпретации. Один личный взгляд.
```

### Короче (баннер / сторис)

```text
EN  NASA JPL sky data. Centuries of interpretation. One personal view.
RU  Данные неба NASA JPL. Столетия интерпретации. Один личный взгляд.
```

«NASA JPL sky data» = эфемериды положений. Не логотип NASA, не «NASA-certified».

### Ещё короче (одна строка)

```text
EN  The sky is astronomy. The meaning is tradition. The view is yours.
RU  Небо — астрономия. Смысл — традиция. Взгляд — твой.
```

### Не использовать в рекламе

Powered by NASA · NASA-certified · Horizons · «научная астрология» · «единственно верная школа» · «полная библиотека веков уже в приложении».

---

## Changelog

| Date | Change |
|------|--------|
| 2026-08-17 | v1.0 — public Trust Layer: two pillars + locked line; NASA/JPL claims bounded to live Swiss/DE431; copy slice opened for landing/ads |
| 2026-08-17 | v1.1 — landing `#trust` + ads brief §6; interpretation still method, not a finished catalog claim |
| 2026-08-17 | v1.2 — landing is the brand surface (Co-Star principle): H1 = locked line, thesis before tools, Moon signature; dual hero CTA retired |
| 2026-08-17 | v1.3 — RU landing copy: three trust levels (точность / глубина / человечность) as editorial reading of locked beats; warmer pillar titles; rejected pack lines stay in §3 |

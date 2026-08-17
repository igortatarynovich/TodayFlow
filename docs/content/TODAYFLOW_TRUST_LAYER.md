# TodayFlow Trust Layer — brand language & copywriting

**Статус:** ACCEPTED — публичная концепция бренда (не внутренняя особенность Interpretation Library).  
**Версия:** 1.0 (2026-08-17).  
**Владелец:** Product + Content.  
**Принять в работу:** лендинг · реклама · App Store / about / press. Следующий execution slice — копирайт этих поверхностей (трекер).

**Связь:** [TODAYFLOW_VOICE_CANON.md](./TODAYFLOW_VOICE_CANON.md) (in-product голос) · [EXPLAINABLE_COMPUTATION_AND_INTERPRETATION.md](../explainability/EXPLAINABLE_COMPUTATION_AND_INTERPRETATION.md) · [EXPLAIN_MEANING_NOT_MECHANISM.md](../explainability/EXPLAIN_MEANING_NOT_MECHANISM.md) · [foundation_v1.md](../foundation_v1.md) §1.4.1 (факты NASA/JPL) · [INTERPRETATION_LIBRARY_V1.md](../astrology/INTERPRETATION_LIBRARY_V1.md) (методика слоёв, не бренд-SoT) · [PRODUCT_TRUTH_FIRST.md](../PRODUCT_TRUTH_FIRST.md)

---

## Architecture impact

- **SoT before:** provenance / multi-school Canon жили как внутренняя методика IL (§6). NASA/JPL — runtime footnote (Swiss) и «кандидат Horizons». Лендинг говорил про память дней, не про две опоры доверия.
- **SoT after:** публичный **Trust Layer** = язык бренда. Две опоры коммуникации: (1) точность астрономических данных, (2) глубина интерпретации как нормализованное пересечение исторических слоёв с provenance. IL остаётся lookup смысла, не единственным местом этой мысли.
- **Public contract changed?** no — JSON / generation не меняются. Меняется **разрешённый** маркетинговый язык.
- **Migration required?** no runtime. Copy pass: landing + ads (открытый slice).
- **Canon updated?** this doc · Voice Canon §0.08 · Unified §0 · Foundation §1.4.1 · IL pointer · explainability indexes.
- **Backward compatible?** yes — in-product Voice Canon §0 («не говорит о себе») остаётся для Profile / Today / Tarot / Compatibility body.

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

Три удара = три разных обещания. Не сжимать в «мы точнее гороскопов» и не делать NASA поручителем смысла.

| Удар | Что обещаем | Чего не обещаем |
|------|-------------|-----------------|
| Precise astronomical data | Положения тел считаются по астрономическим эфемеридам NASA/JPL (через Swiss Ephemeris) | NASA «подтвердила гороскоп» · партнёрство · live API Horizons |
| Centuries of interpretation | Canon держит слои традиции различимыми; не одна модная школа | Полный каталог уже в приложении · UI с цитатами Валенса на каждом Today |
| One personal perspective | Personal Model / Profile / Today — смысл для человека | «Единственно верная астрология» |

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
| «Единственно верная / научная астрология» | Canon как раз против одной истины |
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

## 5. Копирайтинг — принять в работу

Концепция **locked**. Следующий slice — написать, не оставлять только в docs:

1. **Лендинг** (`productWebLandingContent` / hero + why) — один экран или блок, который держит три удара, не ломая текущее обещание «история, которая помнит вчера».
2. **Реклама** — короткие варианты locked line (EN/RU); запреты §3 обязательны в брифе.
3. About / press-kit — тот же каркас, без overclaim IL.

Не подменять этим north star Personal Model. Trust Layer объясняет **опоры знания**; Personal Model остаётся тем, **для кого** собирается взгляд.

---

## Changelog

| Date | Change |
|------|--------|
| 2026-08-17 | v1.0 — public Trust Layer: two pillars + locked line; NASA/JPL claims bounded to live Swiss/DE431; copy slice opened for landing/ads |

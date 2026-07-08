# Правила качества i18n текстов

**Версия:** 1.0.0  
**Дата:** 2025-01-03  
**Статус:** Активные правила

---

## Жёсткие правила (без исключений)

### 1. INT/CON тексты

❌ **Запрещено:**
- Короче 50 символов
- Менее 10 слов
- Звучать как мета-лейбл
- Одна фраза без контекста

✅ **Обязательно:**
- Минимум 1 полноценное предложение (15-20 слов)
- Описание переживания, не лейбл
- Контекст и смысл

**Примеры:**

❌ Плохо:
```
"You may notice emotional shutdown under overload"
```

✅ Хорошо:
```
"When things become overwhelming, your system may reduce emotional input. This quieting isn't emptiness — it's a way of preserving function until capacity returns."
```

---

### 2. Daily-слой

❌ **Запрещено:**
- "your patterns show"
- "this reflects"
- "you may notice" (допустимо редко, не как шаблон)
- Аналитический тон

✅ **Обязательно:**
- Контакт, не анализ
- Короткие, человечные тексты
- Прямое описание
- Без мета-объяснений

**Daily — это контакт, не теория.**

---

### 3. "You may notice"

**Цель:** <40% текстов с "you may notice"

**Где оставить:**
- Аналитические тексты (EP/RL/CR базовые описания)
- ~40-50% аналитики

**Где убрать:**
- Daily-слой (почти полностью)
- INT/CON (заменить на прямые описания)
- Короткие тексты

**Примеры замены:**

❌ Было:
```
"You may notice recovery through pacing"
```

✅ Стало:
```
"Recovery comes when the pace slows and demands soften."
```

---

### 4. Семантические повторы

**Правило:** Одна мысль не должна появляться >3-4 раз во всём файле.

**Семантический реестр:**
- `DEFENSE_OVERTHINKING` — мышление как защита
- `DEFENSE_WITHDRAWAL` — отстранение
- `DEFENSE_CONTROL` — контроль, самокритика
- `DEFENSE_PEOPLE_PLEASING` — угодничество
- `DEFENSE_SHUTDOWN` — эмоциональное отключение
- `DEFENSE_ACTIVATION` — быстрая активация

**В разных разделах мысль раскрывается под другим углом, а не повторяется.**

---

## Правило: Человеческий понятный язык

### Принцип
Все тексты должны быть написаны человеческим понятным языком, без абстрактных/мистических фраз.

### ❌ ИЗБЕГАТЬ (абстрактные/мистические фразы):
- "your system", "your nervous system"
- "emotional access", "restore equilibrium"
- "integrate what happened", "metabolize emotion"
- "inner balance", "inner sorting", "inner space"
- "felt safety", "emotional carryover"
- "recalibrate", "regulate"
- "processing stage", "emotional atmosphere"

### ✅ ИСПОЛЬЗОВАТЬ (человеческий язык):
- "you", "you feel", "you need"
- "taking time", "stepping away", "giving yourself space"
- "when things are calm", "when pressure builds"
- "talking about it", "writing it down"
- "feeling better", "feeling overwhelmed"
- "the mood", "how people feel"
- "feel balanced", "feel safe"
- "make sense of", "figure things out"
- "space for yourself", "time alone"
- "carrying stress", "built-up feelings"

### Примеры замен:

**❌ "your system is reducing input"**
✅ "you're reducing input"

**❌ "emotional access can narrow"**
✅ "your feelings can become harder to reach"

**❌ "restore equilibrium"**
✅ "feel balanced"

**❌ "emotional atmosphere"**
✅ "the mood"

**❌ "nervous system processes"**
✅ "you process"

**❌ "integrate what happened"**
✅ "make sense of what happened"

**❌ "inner sorting"**
✅ "figuring things out"

**❌ "felt safety"**
✅ "feeling safe"

---

## Стилевые принципы

### Для аналитики (EP/RL/CR/MS)

✅ Допустимо:
- "You may notice" (в меру)
- Описательный тон
- Контекст и объяснения

❌ Избегать:
- Мета-лейблы
- Слишком короткие INT/CON
- Повторы смысла

### Для Daily-слоя

✅ Допустимо:
- Прямые описания
- Мягкие утверждения
- Наблюдения без модальности
- Контактный тон

❌ Избегать:
- "You may notice"
- Мета-объяснения
- Аналитический тон
- Ссылки на "паттерны", "оси"

---

## Проверка качества

Используйте скрипт:
```bash
python3 scripts/analyze_i18n_quality.py
```

Проверяет:
1. Длину INT/CON текстов
2. Распределение "you may notice"
3. Семантические повторы
4. Мета-лейблы

---

## Применение

Эти правила применяются ко всем текстам при:
- Создании новых текстов
- Переформулировке существующих текстов
- Исправлении любых текстов в проекте

---

**См. также:**
- `docs/i18n/Translation_Guide.md` — правила мультиязычности
- `docs/TODAY_LANGUAGE_V1.md` — язык и качество копирайта Today


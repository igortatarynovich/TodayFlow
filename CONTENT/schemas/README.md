# JSON Schemas для Content System

JSON схемы для валидации структуры контента в Content System.

## Назначение

Схемы обеспечивают:
- Валидацию структуры JSON файлов
- Проверку обязательных полей
- Проверку типов данных
- Документацию форматов

## Доступные схемы

### moon_phase.schema.json
Схема для фаз Луны (`forecasts/moon_phases.json`).

**Обязательные поля:**
- `phase_id` - уникальный идентификатор
- `name` - название фазы
- `human_text` - человеческий текст

**Опциональные поля:**
- `themes` - семантические темы
- `guidance` - семантическое руководство

---

### daily_template.schema.json
Схема для daily templates (`daily/daily_templates.json`).

**Обязательные поля:**
- `template_id` - уникальный идентификатор
- `type` - тип шаблона (AFFIRMATION, DIGEST, FOCUS, etc.)
- `text` - исходный текст
- `human_text` - человеческий текст

**Опциональные поля:**
- `category` - категория
- `pattern` - паттерн (для PATTERN_TODAY)
- `practice_type` - тип практики (для PRACTICE)
- `instructions` - инструкции (для PRACTICE)

---

### ritual.schema.json
Схема для ритуалов (`rituals/rituals.json`).

**Обязательные поля:**
- `ritual_id` - уникальный идентификатор
- `title` - название ритуала
- `human_text` - человеческий текст

**Опциональные поля:**
- `intention` - намерение
- `instructions` - пошаговые инструкции (массив строк)
- `notes` - дополнительные заметки

## Использование

### Валидация с помощью скрипта

```bash
python3 scripts/validate_with_schema.py
```

### Валидация в Python

```python
import json
import jsonschema
from pathlib import Path

# Загрузить схему
with open('CONTENT/schemas/moon_phase.schema.json') as f:
    schema = json.load(f)

# Загрузить данные
with open('CONTENT/forecasts/moon_phases.json') as f:
    data = json.load(f)

# Валидировать
try:
    jsonschema.validate(instance=data, schema=schema)
    print("Валидация пройдена!")
except jsonschema.ValidationError as e:
    print(f"Ошибка валидации: {e.message}")
```

## Установка зависимостей

Для использования схем требуется `jsonschema`:

```bash
pip install jsonschema
```

## Расширение

Для добавления новых схем:

1. Создайте файл `*.schema.json` в директории `CONTENT/schemas/`
2. Определите структуру согласно JSON Schema Draft 7
3. Добавьте валидацию в `scripts/validate_with_schema.py`
4. Обновите эту документацию

## Стандарт

Схемы используют JSON Schema Draft 7:
- http://json-schema.org/draft-07/schema#


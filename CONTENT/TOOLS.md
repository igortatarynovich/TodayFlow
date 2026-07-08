# Инструменты для работы с Content System

## Скрипты

### 1. Миграция контента

**`scripts/migrate_to_content_system.py`**

Переносит контент из i18n в Content System с применением Human Layer.

```bash
python3 scripts/migrate_to_content_system.py
```

**Возможности:**
- Извлечение контента из i18n/en.json и i18n/app.en.json
- Применение Human Layer для преобразования текстов
- Сохранение в структурированный формат Content System

**Примеры миграции:**
- Moon phases (8 элементов)
- Daily templates (можно ограничить количество для теста)

---

### 2. Валидация контента

**`scripts/validate_content.py`**

Проверяет структуру контента, качество human_text и соответствие стандартам.

```bash
python3 scripts/validate_content.py
```

**Проверки:**
- Валидность JSON
- Наличие обязательных полей (human_text, идентификаторы)
- Качество human_text (длина, абстрактные фразы)
- Соответствие структуре

**Вывод:**
- Ошибки (критические проблемы)
- Предупреждения (рекомендации)

---

### 3. Генерация сводки

**`scripts/generate_content_summary.py`**

Создает отчет о количестве элементов контента и структуре.

```bash
python3 scripts/generate_content_summary.py
```

**Статистика:**
- Количество файлов по категориям
- Количество элементов контента
- Типы контента

---

### 4. Валидация со схемами

**`scripts/validate_with_schema.py`**

Валидирует контент с использованием JSON схем.

```bash
python3 scripts/validate_with_schema.py
```

**Требования:**
- `jsonschema` (установить: `pip install jsonschema`)

**Проверки:**
- Соответствие JSON Schema
- Обязательные поля
- Типы данных
- Форматы значений

---

### 5. Улучшение через Human Layer

**`scripts/enhance_human_layer.py`**

Добавляет human_text к элементам контента, которые еще не имеют его.

```bash
# Dry-run (без изменений)
python3 scripts/enhance_human_layer.py

# Применить изменения
python3 scripts/enhance_human_layer.py --apply
```

**Возможности:**
- Автоматическое добавление human_text
- Режим dry-run для проверки
- Обработка всех файлов контента

---

## Human Layer

### Использование в Python

```python
from CONTENT.human_layer.human_layer import transform_text, generate_human_text, process_content_item

# Преобразование текста
text = "Your system needs to recalibrate."
human_text = transform_text(text)
# Результат: "You need to adjust."

# Генерация из семантики
semantic = {
    "themes": "Fine-tuning strategy, securing resources",
    "guidance": "Check details, expectations, and resources"
}
human_text = generate_human_text(semantic)

# Обработка элемента контента
item = {
    "phase_id": "waxing_gibbous",
    "themes": "Fine-tuning strategy, securing resources",
    "guidance": "Check details, expectations, and resources"
}
processed = process_content_item(item)
# Результат: item с добавленным human_text
```

### API

**`transform_text(text: str) -> str`**
- Преобразует текст, убирая абстрактные фразы

**`generate_human_text(semantic_fields: Dict, base_text: Optional[str] = None) -> str`**
- Генерирует human_text из семантических полей

**`process_content_item(item: Dict) -> Dict`**
- Обрабатывает элемент контента, добавляя human_text

---

## JSON Schemas

JSON схемы для валидации находятся в `CONTENT/schemas/`:

- `moon_phase.schema.json` - схема для фаз Луны
- `daily_template.schema.json` - схема для daily templates
- `ritual.schema.json` - схема для ритуалов

Подробнее: `CONTENT/schemas/README.md`

---

## Интеграция

### В коде приложения

```python
import sys
from pathlib import Path

# Добавляем Human Layer в путь
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "CONTENT" / "human_layer"))

from human_layer import process_content_item

# Использование
content_item = load_from_json("forecasts/moon_phases.json")
processed = process_content_item(content_item)
```

---

## Примеры использования

### Миграция контента

```bash
# Миграция всех типов контента
python3 scripts/migrate_to_content_system.py
```

### Валидация перед коммитом

```bash
# Проверка качества контента
python3 scripts/validate_content.py
```

### Генерация отчета

```bash
# Статистика по контенту
python3 scripts/generate_content_summary.py
```

---

## Расширение

### Добавление новых типов контента

1. Создайте структуру в соответствующей директории
2. Добавьте примеры в миграционный скрипт
3. Обновите валидатор при необходимости

### Улучшение Human Layer

1. Добавьте новые замены в `REPLACEMENTS`
2. Улучшите логику `generate_human_text`
3. Обновите примеры в `examples.md`


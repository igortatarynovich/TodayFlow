# Rituals Content

## Структура

Файл `rituals.json` содержит ритуалы для пользователей.

## Формат

Каждый объект содержит:
- **Идентификатор:**
  - `ritual_id` - уникальный идентификатор ритуала
  
- **Семантические поля** (для логики системы):
  - `title` - название ритуала
  - `intention` - намерение (семантическая информация)
  - `instructions` - список инструкций (пошаговые действия)
  - `notes` - примечания (когда использовать, с чем сочетается)
  
- **Human Layer** (для пользователя):
  - `human_text` - человеческий текст, преобразованный из семантики

## Human Layer

Human Layer преобразует:
- `intention` + `instructions` + `notes` → `human_text`
- Объединяет семантические элементы в связный текст
- Делает язык человечным и понятным
- Добавляет контекст использования

## Пример использования

```javascript
// Получить контент для ритуала
const ritual = rituals.find(r => r.ritual_id === ritualId);

// Для логики системы:
const intention = ritual.intention;
const instructions = ritual.instructions;
const notes = ritual.notes;

// Для пользователя (Human Layer):
const text = ritual.human_text;
```

## Миграция из i18n

Данные из `i18n/app.en.json`:
- `ritual.{ritual_id}.title` → `title`
- `ritual.{ritual_id}.intention` → `intention`
- `ritual.{ritual_id}.instructions.{N}` → `instructions[]`
- `ritual.{ritual_id}.notes` → `notes`
- `human_text` создается через Human Layer


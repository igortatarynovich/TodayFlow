# Forecasts Content

## Структура

Файлы содержат контент для прогнозов:
- `moon_phases.json` - фазы Луны
- (в будущем: `transits.json`, `planetary.json`, etc.)

## Формат

Каждый объект содержит:
- **Семантические поля** (для логики системы):
  - `phase_id` / `transit_id` / etc. - идентификатор
  - `name` - название (может быть использовано в UI через i18n)
  - `themes` - темы (семантическая информация)
  - `guidance` - инструкция (семантическая инструкция)
  
- **Human Layer** (для пользователя):
  - `human_text` - человеческий текст, преобразованный из семантики

## Human Layer

Human Layer преобразует:
- `themes` + `guidance` → `human_text`
- Убирает абстрактные термины
- Делает язык человечным и понятным
- Использует контекст фазы/транзита

## Пример использования

```javascript
// Получить контент для фазы Луны
const moonPhase = moonPhases.find(p => p.phase_id === currentPhase);

// Для логики системы:
const themes = moonPhase.themes;
const guidance = moonPhase.guidance;

// Для пользователя (Human Layer):
const text = moonPhase.human_text;
```

## Миграция из i18n

Данные из `i18n/app.en.json`:
- `moon_phase.{phase}.name` → `name`
- `moon_phase.{phase}.themes` → `themes`
- `moon_phase.{phase}.guidance` → `guidance`
- `human_text` создается через Human Layer


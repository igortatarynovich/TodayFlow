#!/usr/bin/env python3
"""
Human Layer - преобразование семантики в человеческий текст

Преобразует семантические поля (themes, guidance, description, etc.)
в человеческий, понятный текст.
"""

from typing import Dict, Any, Optional, Iterable, Tuple
import re


class HumanLayer:
    """Human Layer система для преобразования семантики в человеческий текст."""

    # Фразы для замены (абстрактные → человеческие)
    # ВАЖНО:
    # - порядок важен (длинные и специфичные фразы — выше)
    # - для одиночных слов используем границы слова (\b), чтобы не ломать составные слова
    STRICT_REPLACEMENTS: list[tuple[str, str, bool]] = [
        ("guidance", "what to do", True),
        ("themes", "main focus", True),
        ("intention", "goal", True),
        ("explore", "look at", True),
        ("navigate", "deal with", True),
        ("hold space for", "allow time for", False),
        ("activate", "start", True),
        ("embody", "use", True),
    ]

    REPLACEMENTS: list[tuple[str, str, bool]] = [
        # Системные абстракции (длинные фразы первыми)
        ("your system needs to", "you need to", False),
        ("your system may", "you may", False),
        ("your system is", "you are", False),
        ("your system", "you", False),
        ("nervous system", "your body and mind", False),
        ("emotional system", "your emotions", False),

        # Абстрактные действия / корпоративный жаргон
        ("integrate what happened", "make sense of what happened", False),
        ("restore equilibrium", "find balance", False),
        ("build capacity", "build strength", False),
        ("resource allocation", "how you spend your time and energy", False),
        ("systems and expectations", "your plans and expectations", False),
        ("prepare the stage", "get ready to share it", False),
        ("visibility", "being seen", False),

        # Одиночные слова (границы слова)
        ("audit", "review", True),
        ("evaluate", "review", True),
        ("recalibrate", "adjust", True),
        ("optimize", "improve", True),
        ("fine-tune", "adjust", True),
        ("metabolize", "process", True),

        # Эмоциональные/абстрактные конструкции
        ("emotional access", "understanding your emotions", False),
        ("inner balance", "balance", False),
        ("emotional atmosphere", "the mood around you", False),
        ("felt safety", "feeling safe", False),

        # Мистические фразы
        ("align your energy", "focus your attention", False),
        ("your energy", "your attention", False),
    ]

    # Русские замены (для app.ru.json и похожих текстов)
    # Формат: (что ищем, на что меняем, использовать ли границы слова)
    RU_REPLACEMENTS: list[tuple[str, str, bool]] = [
        # Самые проблемные и непонятные обороты
        ("аудируй", "проверь", True),
        ("аудит", "проверка", True),
        ("системы и ожидания", "твои планы и ожидания", False),
        ("готовь сцену", "подготовься показать это", False),
        ("к видимости", "так, чтобы это стало заметно", False),

        # Корпоративные/абстрактные глаголы
        ("перекалибруй", "подстрой", True),
        ("оптимизируй", "улучши", True),
        ("интегрируй", "осмысли", True),
        ("метаболизируй", "перевари", True),
        ("рефрейм", "посмотри иначе", True),
        ("рефреймь", "посмотри иначе", True),

        # Уточнения смысла
        ("восстанови равновесие", "верни баланс", False),
        ("энергию", "внимание", True),
        ("выравнивай энергию", "сфокусируйся", False),
    ]

    def __init__(self, strict: bool = False) -> None:
        self._compiled_replacements = self._compile_rules(self.REPLACEMENTS)
        self._compiled_ru_replacements = self._compile_rules(self.RU_REPLACEMENTS)
        self.strict = strict
        self._compiled_strict_replacements = self._compile_rules(self.STRICT_REPLACEMENTS)

    def _compile_rules(self, rules: Iterable[tuple[str, str, bool]]) -> list[tuple[re.Pattern[str], str]]:
        compiled: list[tuple[re.Pattern[str], str]] = []
        for old, new, use_word_boundaries in rules:
            # Если это одиночное слово — защищаемся от замен внутри других слов.
            if use_word_boundaries:
                pattern = re.compile(rf"\b{re.escape(old)}\b", re.IGNORECASE)
            else:
                pattern = re.compile(re.escape(old), re.IGNORECASE)
            compiled.append((pattern, new))
        return compiled

    def _normalize_punctuation(self, text: str) -> str:
        # Часто в контенте встречаются `;` как разделитель мыслей — делаем из этого предложения.
        text = re.sub(r"\s*;\s*", ". ", text)
        # Убираем повторяющиеся точки
        text = re.sub(r"\.{2,}", ".", text)
        return text

    def _looks_russian(self, text: str) -> bool:
        # Достаточно встретить любую кириллицу
        return bool(re.search(r"[А-Яа-яЁё]", text))
    
    def transform_text(self, text: str) -> str:
        """
        Преобразует текст, убирая абстрактные/мистические фразы.
        
        Args:
            text: Исходный текст
            
        Returns:
            Преобразованный человеческий текст
        """
        if not text or not isinstance(text, str):
            return text

        result = text
        # Нормализуем пунктуацию до замен
        result = self._normalize_punctuation(result)

        # Применяем замены (case-insensitive). Порядок важен.
        if self._looks_russian(result):
            for pattern, replacement in self._compiled_ru_replacements:
                result = pattern.sub(replacement, result)

        for pattern, replacement in self._compiled_replacements:
            result = pattern.sub(replacement, result)

        if self.strict:
            for pattern, replacement in self._compiled_strict_replacements:
                result = pattern.sub(replacement, result)

        # Исправляем двойные слова (например, "your your" -> "your")
        result = re.sub(r"\b(your|you|the|a|an|to|of)\s+\1\b", r"\1", result, flags=re.IGNORECASE)

        # Убираем множественные пробелы
        result = re.sub(r'\s+', ' ', result).strip()

        # Капитализируем первое слово, если нужно
        if result and result[0].islower():
            result = result[0].upper() + result[1:]

        return result
    
    def generate_human_text(
        self,
        semantic_fields: Dict[str, Any],
        base_text: Optional[str] = None
    ) -> str:
        """
        Генерирует human_text из семантических полей.
        
        Args:
            semantic_fields: Словарь с семантическими полями
                (themes, guidance, description, intention, etc.)
            base_text: Базовый текст для преобразования (опционально)
            
        Returns:
            Human-readable текст
        """
        # Если есть base_text, используем его как основу
        if base_text:
            return self.transform_text(base_text)
        
        # Собираем текст из семантических полей
        parts = []
        
        # Порядок приоритета полей
        field_order = ['description', 'guidance', 'themes', 'intention', 'summary']
        
        for field in field_order:
            if field in semantic_fields and semantic_fields[field]:
                value = semantic_fields[field]
                if isinstance(value, str):
                    parts.append(value)
                elif isinstance(value, list):
                    parts.append(', '.join(str(v) for v in value))
        
        if not parts:
            # Если ничего не найдено, пробуем все поля
            for key, value in semantic_fields.items():
                if isinstance(value, str) and value:
                    parts.append(value)
                    break
        
        if not parts:
            return ""
        
        # Объединяем части
        combined = ' '.join(parts)
        
        # Преобразуем
        result = self.transform_text(combined)
        
        # Добавляем контекст, если текст слишком короткий
        if len(result) < 50 and len(parts) > 1:
            # Пытаемся создать более связный текст
            result = self._enhance_text(parts)
        
        return result
    
    def _enhance_text(self, parts: list[str]) -> str:
        """Улучшает текст, добавляя связи между частями."""
        if not parts:
            return ""

        if len(parts) == 1:
            return self.transform_text(parts[0])

        # Соединяем как предложения; защищаемся от пустых и дублирующих частей
        cleaned: list[str] = []
        for p in parts:
            if not p:
                continue
            t = self.transform_text(p)
            if not t:
                continue
            if cleaned and cleaned[-1].rstrip(".") == t.rstrip("."):
                continue
            cleaned.append(t.rstrip("."))
        return ". ".join(cleaned) + "."
    
    def process_content_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Обрабатывает элемент контента, добавляя human_text.
        
        Args:
            item: Элемент контента (словарь)
            
        Returns:
            Элемент контента с добавленным human_text
        """
        item = item.copy()
        
        # Если human_text уже есть, преобразуем его
        if 'human_text' in item and item['human_text']:
            item['human_text'] = self.transform_text(item['human_text'])
            return item
        
        # Если human_text нет, генерируем из семантических полей
        semantic_fields = {
            k: v for k, v in item.items()
            if k not in ['human_text', 'template_id', 'id', 'spread_id', 'ritual_id']
        }
        
        # Используем description или text как базовый текст
        base_text = item.get('description') or item.get('text') or item.get('guidance')
        
        human_text = self.generate_human_text(semantic_fields, base_text)
        
        if human_text:
            item['human_text'] = human_text
        
        return item
    


# Глобальный экземпляр
human_layer = HumanLayer(strict=True)


def transform_text(text: str) -> str:
    """Удобная функция для преобразования текста."""
    return human_layer.transform_text(text)


def generate_human_text(semantic_fields: Dict[str, Any], base_text: Optional[str] = None) -> str:
    """Удобная функция для генерации human_text."""
    return human_layer.generate_human_text(semantic_fields, base_text)


def process_content_item(item: Dict[str, Any]) -> Dict[str, Any]:
    """Удобная функция для обработки элемента контента."""
    return human_layer.process_content_item(item)


if __name__ == '__main__':
    # Примеры использования
    print("Human Layer - Примеры использования\n")

    # Пример 1: Простая трансформация
    example1 = "Your system needs to recalibrate and restore equilibrium."
    result1 = transform_text(example1)
    print(f"Пример 1:")
    print(f"  До: {example1}")
    print(f"  После: {result1}\n")

    # Пример 2: Генерация из семантических полей
    semantic = {
        "themes": "Fine-tuning strategy, securing resources",
        "guidance": "Audit systems and expectations; prepare the stage for visibility."
    }
    result2 = generate_human_text(semantic)
    print(f"Пример 2:")
    print(f"  Семантика: {semantic}")
    print(f"  Human text: {result2}\n")

    # Пример 3: Обработка элемента контента
    content_item = {
        "phase_id": "waxing_gibbous",
        "themes": "Fine-tuning strategy, securing resources",
        "guidance": "Audit systems and expectations; prepare the stage for visibility."
    }
    result3 = process_content_item(content_item)
    print(f"Пример 3:")
    print(f"  До: {content_item}")
    print(f"  После: {result3}")
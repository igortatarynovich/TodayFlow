"""Генератор аффирмаций под потребности пользователя через AI."""

from typing import List, Optional, Dict, Any
import logging

from todayflow_backend.core.config import settings
from todayflow_backend.core.text_quality import contains_dead_pattern, is_meaningful_sentence
from todayflow_backend.core.user_context import get_user_context

logger = logging.getLogger(__name__)

AFFIRMATION_SYSTEM_PROMPT = """Ты — генератор точных персонализированных аффирмаций для TodayFlow.

ТВОЯ ГЛАВНАЯ ЦЕЛЬ:
Собрать фразы, которые звучат как личная внутренняя опора пользователя, а не как общий мотивационный плакат.

СТИЛЬ АФФИРМАЦИЙ:
- Только настоящее время.
- Только первое лицо ("Я...", "Мне...", "Мой...").
- Конкретика вместо абстракций.
- Учитывай натальную карту/профиль, если они даны.
- Не повторяй одну конструкцию.

СТРУКТУРА:
- Каждая аффирмация — это одно предложение (до 20 слов).
- В каждой аффирмации должен быть один конкретный фокус: действие, состояние или граница.

ВЕРНИ: JSON массив строк с аффирмациями (1-3 штуки):
["аффирмация 1", "аффирмация 2", "аффирмация 3"]

СТРОГО ЗАПРЕЩЕНО:
- Шаблоны: "вселенная на моей стороне", "всё будет хорошо", "просто доверься", "я успешен".
- Пустые фразы без фокуса и без личной конкретики.
"""


def _fallback_affirmations(needs: str, user_context: Dict[str, Any], count: int) -> List[str]:
    natal = user_context.get("natal_chart") or {}
    sun = natal.get("sun_sign")
    moon = natal.get("moon_sign")
    anchor = f"с моими {sun}/{moon}" if sun and moon else "в моем темпе"
    by_need = {
        "money": [
            f"Я спокойно называю цену своего труда и выбираю решения, которые усиливают доход {anchor}.",
            "Я держу финансовый фокус на одном приоритете и не размениваю внимание на шум.",
            "Я замечаю реальные точки роста и действую через конкретные договоренности, а не через тревогу.",
        ],
        "love": [
            f"Я говорю о чувствах прямо и бережно, сохраняя уважение к себе {anchor}.",
            "Я выбираю отношения, где есть ясность, контакт и взаимные действия.",
            "Я удерживаю границы и открытость одновременно, без крайностей и самообмана.",
        ],
        "work": [
            "Я завершаю ключевую задачу дня до новых входящих и возвращаю себе контроль над ритмом.",
            f"Я работаю через приоритеты и факт результата, а не через спешку {anchor}.",
            "Я фиксирую договоренности письменно и экономлю энергию на важное.",
        ],
        "health": [
            "Я поддерживаю тело через простой режим: вода, дыхание, короткая пауза восстановления.",
            f"Я слышу сигнал усталости вовремя и выбираю бережный темп {anchor}.",
            "Я делаю минимум, который стабилизирует самочувствие уже сегодня.",
        ],
    }
    pool = by_need.get((needs or "").lower(), [
        f"Я сохраняю внутренний фокус {anchor} и двигаюсь через один понятный шаг.",
        "Я выбираю ясность вместо перегруза и возвращаю внимание к главному.",
        "Я действую в своем ритме и фиксирую результат дня конкретно.",
    ])
    return pool[:count]


def _sanitize_affirmations(values: List[str], *, count: int) -> List[str]:
    result: List[str] = []
    for value in values:
        if not isinstance(value, str):
            continue
        text = value.strip()
        if not text:
            continue
        if contains_dead_pattern(text):
            continue
        ok, _ = is_meaningful_sentence(text, min_words=5)
        if not ok:
            continue
        if len(text.split()) > 20:
            continue
        if not text.lower().startswith(("я ", "я,", "мне ", "мой ", "моя ", "моё ", "мои ")):
            continue
        result.append(text)
    return result[:count]


def generate_affirmations(
    user,
    db,
    needs: str,  # "money", "love", "calm", "work", "health" и т.д.
    target_date: Optional[str] = None,
    count: int = 3
) -> List[str]:
    """
    Генерирует персонализированные аффирмации под потребности пользователя.
    Учитывает его натальную карту, психологический профиль, нумерологию.
    """
    if not settings.openai_api_key:
        logger.warning("OpenAI API key not set, cannot generate affirmations")
        return []
    
    try:
        import openai
    except ImportError:
        logger.warning("OpenAI library not available")
        return []
    
    if not target_date:
        from datetime import date
        target_date = date.today().isoformat()
    
    # Собираем контекст пользователя
    try:
        user_context = get_user_context(user, target_date, db, needs=needs)
    except Exception as e:
        logger.warning(f"Failed to get user context for affirmations: {e}", exc_info=True)
        user_context = {"needs": needs}
    
    # Строим промпт
    needs_map = {
        "money": "деньги, финансовая стабильность, изобилие",
        "love": "любовь, отношения, близость, романтика",
        "calm": "спокойствие, умиротворение, баланс, гармония",
        "work": "работа, карьера, профессиональный рост, достижения",
        "health": "здоровье, энергия, тело, самочувствие",
        "relationship": "отношения, общение, связи с людьми",
        "creativity": "творчество, вдохновение, самовыражение",
        "spirituality": "духовность, смысл, связь с высшим"
    }
    needs_description = needs_map.get(needs.lower(), needs) if needs else "общее благополучие и гармония"
    
    prompt_parts = [
        f"Потребность пользователя: {needs_description}",
        f"Количество аффирмаций: {count}",
        "",
        "=== ИНДИВИДУАЛЬНОСТЬ ПОЛЬЗОВАТЕЛЯ ===",
    ]
    
    # Натальная карта
    if user_context.get("natal_chart"):
        natal = user_context["natal_chart"]
        natal_info = []
        if natal.get("sun_sign"):
            natal_info.append(f"Солнце в {natal['sun_sign']} — его суть, идентичность")
        if natal.get("moon_sign"):
            natal_info.append(f"Луна в {natal['moon_sign']} — его эмоциональная природа")
        if natal.get("ascendant"):
            natal_info.append(f"Асцендент в {natal['ascendant']} — как он проявляется")
        if natal_info:
            prompt_parts.append("\n".join(natal_info))
            prompt_parts.append("Используй это, чтобы говорить про ЕГО уникальность.")
    
    # Психологический профиль
    if user_context.get("profile"):
        profile = user_context["profile"]
        if profile.get("axes"):
            prompt_parts.append(f"Психологический профиль: {profile['axes']} — как он обрабатывает эмоции")
        if profile.get("modulators"):
            prompt_parts.append(f"Модуляторы: {profile['modulators']} — как он реагирует")
    
    # Нумерология
    if user_context.get("numerology"):
        num = user_context["numerology"]
        num_info = []
        if num.get("life_path"):
            num_info.append(f"Число жизненного пути: {num['life_path']} — его путь")
        if num.get("day_number"):
            num_info.append(f"Число дня: {num['day_number']} — энергия дня")
        if num_info:
            prompt_parts.append(" | ".join(num_info))
    
    prompt_parts.extend([
        "",
        "=== ЗАДАНИЕ ===",
        f"Сгенерируй {count} глубоких, персонализированных аффирмаций, которые:",
        "",
        "1. ПОКАЗЫВАЮТ ЕГО ЦЕННОСТЬ:",
        f"   - 'Я уже готов получить {needs_description}'",
        "   - 'Я достоин всего, чего хочу'",
        "   - 'Моя уникальность — это моя сила'",
        "",
        "2. ПОДСТРАИВАЮТ 'ВСЕЛЕННУЮ':",
        f"   - 'Всё складывается для {needs_description}'",
        "   - 'Вселенная на моей стороне'",
        "   - 'Момент уже наступил'",
        "",
        "3. ДАЮТ УВЕРЕННОСТЬ И НАДЕЖДУ:",
        "   - Не 'я хочу', а 'я уже имею' или 'я готов получить'",
        "   - Не 'я буду', а 'я есть' или 'всё есть'",
        "   - Не 'я надеюсь', а 'я знаю' или 'всё происходит'",
        "",
        "4. УЧИТЫВАЮТ ЕГО ИНДИВИДУАЛЬНОСТЬ:",
        "   - Используй его натальную карту (солнце, луна, асцендент)",
        "   - Используй его психологический профиль",
        "   - Говори про КОНКРЕТНОГО человека, не про абстракцию",
        "",
        "ВАЖНО: Каждая аффирмация должна быть глубокой, запоминающейся, вызывать 'да, это про меня'.",
        "",
        "Верни только JSON массив строк, без markdown и пояснений:",
    ])
    
    user_prompt = "\n".join(prompt_parts)
    
    try:
        client = openai.OpenAI(api_key=settings.openai_api_key)
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": AFFIRMATION_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.8,
            max_tokens=500,
        )
        
        content = (resp.choices[0].message.content or "").strip()
        if not content:
            return []
        
        # Парсим JSON
        import json
        import re
        
        # Убираем markdown code block если есть
        m = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", content)
        if m:
            content = m.group(1).strip()
        
        try:
            affirmations = json.loads(content)
            if isinstance(affirmations, list):
                # Фильтруем и нормализуем
                result = []
                for aff in affirmations:
                    if isinstance(aff, str) and aff.strip():
                        result.append(aff.strip())
                sanitized = _sanitize_affirmations(result, count=count)
                if sanitized:
                    return sanitized
        except json.JSONDecodeError:
            # Пытаемся извлечь строки вручную
            lines = [line.strip() for line in content.split('\n') if line.strip()]
            result = []
            for line in lines:
                # Убираем кавычки и лишние символы
                cleaned = line.strip('"\'[]').strip()
                if cleaned and len(cleaned) > 10:  # Минимальная длина
                    result.append(cleaned)
            sanitized = _sanitize_affirmations(result, count=count)
            if sanitized:
                return sanitized
        
        return _fallback_affirmations(needs, user_context if isinstance(user_context, dict) else {}, count)
    except Exception as e:
        logger.warning(f"OpenAI API error generating affirmations: {e}", exc_info=True)
        return _fallback_affirmations(needs, user_context if isinstance(user_context, dict) else {}, count)

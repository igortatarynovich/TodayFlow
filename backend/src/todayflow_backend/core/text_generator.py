"""Forecast text generator for legacy forecast surfaces.

Current canonical pipeline is generation-first:
request -> plan/context -> generation -> safety validation -> response.
The validator is no longer responsible for meaning or voice shaping.
"""

from __future__ import annotations

import random
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass

from todayflow_backend.core.content_loader import (
    load_lexicon,
    load_practices
)
from todayflow_backend.core.llm_openai_compatible import is_llm_chat_configured
from todayflow_backend.core.day_meaning import DayMeaning
from todayflow_backend.data.quality_gate import (
    validate_daily_forecast,
    QualityGateResult
)


@dataclass
class GenerationRequest:
    """Запрос на генерацию прогноза."""
    forecast_type: str  # daily_grounded, workday_focus, etc.
    layers: List[str]  # L1, L2, L3, etc.
    context: Optional[str] = None  # work, relationship, money, body
    trigger: Optional[str] = None  # из Lexicon
    emotion: Optional[str] = None  # из Lexicon
    reaction: Optional[str] = None  # из Lexicon
    locale: str = "ru"
    style: Optional[Dict[str, Any]] = None  # длина, структура


@dataclass
class GenerationPlan:
    """План генерации (JSON структура)."""
    theme: Dict[str, Any]  # фраза из Lexicon для theme
    notice: List[Dict[str, Any]]  # фразы из Lexicon для notice
    scene: List[Dict[str, Any]]  # фразы из Lexicon для scene
    micro_action: Dict[str, Any]  # фраза из Lexicon для micro_action
    markers: Dict[str, List[str]]  # body, social, domestic, micro_action
    layers: List[str]  # какие слои использовать


@dataclass
class GeneratedForecast:
    """Сгенерированный прогноз."""
    blocks: Dict[str, Any]  # theme, notice, scene, micro_action
    markers: Dict[str, List[str]]
    tags: List[str]
    quality: Dict[str, Any]  # score, violations
    plan: Optional[GenerationPlan] = None  # исходный план


class TextPlanner:
    """Planner: создаёт структуру и выбирает элементы из Lexicon."""
    
    def __init__(self):
        self._lexicon_cache = None
        self._dictionaries_cache = None
    
    def _load_lexicon(self) -> Dict:
        """Загружает Lexicon (с кешированием)."""
        if self._lexicon_cache is None:
            self._lexicon_cache = load_lexicon()
        return self._lexicon_cache
    
    def _load_dictionaries(self) -> Dict:
        """Загружает словари маркеров."""
        if self._dictionaries_cache is None:
            from todayflow_backend.data.content_system import load_dictionary
            
            self._dictionaries_cache = {
                'body': load_dictionary("body_markers"),
                'social': load_dictionary("social_markers"),
                'domestic': load_dictionary("domestic_details"),
                'micro_action': load_dictionary("micro_actions")
            }
        return self._dictionaries_cache
    
    def create_plan(self, request: GenerationRequest) -> GenerationPlan:
        """Создаёт план генерации на основе запроса."""
        try:
            lexicon = self._load_lexicon()
            dictionaries = self._load_dictionaries()
        except Exception as e:
            raise ValueError(f"Ошибка загрузки данных: {str(e)}")
        
        phrases = lexicon.get('phrases', [])
        if not phrases:
            raise ValueError("Lexicon пуст - нет фраз для генерации")
        
        # Фильтруем фразы по типу прогноза и слоям
        filtered_phrases = [
            p for p in phrases
            if request.forecast_type in p.get('forecast_types', [])
            and any(layer in p.get('layers', []) for layer in request.layers)
        ]
        
        if not filtered_phrases:
            # Fallback: только по типу прогноза
            filtered_phrases = [
                p for p in phrases
                if request.forecast_type in p.get('forecast_types', [])
            ]
        
        # Дополнительная фильтрация по контексту, триггеру, эмоции, реакции
        if request.context:
            filtered_phrases = [
                p for p in filtered_phrases
                if p.get('context') == request.context
            ]
            # Если после фильтрации по контексту ничего не осталось, откатываем фильтр
            if not filtered_phrases:
                filtered_phrases = [
                    p for p in phrases
                    if request.forecast_type in p.get('forecast_types', [])
                    and any(layer in p.get('layers', []) for layer in request.layers)
                ]
        
        if request.trigger:
            filtered_phrases = [
                p for p in filtered_phrases
                if p.get('trigger') == request.trigger
            ]
        
        if request.emotion:
            filtered_phrases = [
                p for p in filtered_phrases
                if p.get('emotion') == request.emotion
            ]
        
        if request.reaction:
            filtered_phrases = [
                p for p in filtered_phrases
                if p.get('reaction') == request.reaction
            ]
        
        # Выбираем фразы для каждой части структуры
        theme_phrases = [
            p for p in filtered_phrases
            if 'theme' in p.get('structure_parts', [])
        ]
        notice_phrases = [
            p for p in filtered_phrases
            if 'notice' in p.get('structure_parts', [])
        ]
        scene_phrases = [
            p for p in filtered_phrases
            if 'scene' in p.get('structure_parts', [])
        ]
        micro_action_phrases = [
            p for p in filtered_phrases
            if 'micro_action' in p.get('structure_parts', [])
        ]
        
        # Fallback: если нет фраз для конкретной части, используем любые подходящие
        if not theme_phrases:
            theme_phrases = filtered_phrases[:5] if filtered_phrases else []
        if not notice_phrases:
            notice_phrases = filtered_phrases[:5] if filtered_phrases else []
        if not scene_phrases:
            scene_phrases = filtered_phrases[:5] if filtered_phrases else []
        if not micro_action_phrases:
            micro_action_phrases = filtered_phrases[:5] if filtered_phrases else []
        
        # Если всё ещё нет фраз, используем любые из Lexicon
        if not filtered_phrases:
            filtered_phrases = phrases[:20] if phrases else []
            theme_phrases = filtered_phrases[:5]
            notice_phrases = filtered_phrases[:5]
            scene_phrases = filtered_phrases[:5]
            micro_action_phrases = filtered_phrases[:5]
        
        # Выбираем случайные фразы
        theme_phrase = random.choice(theme_phrases) if theme_phrases else None
        notice_phrases_selected = random.sample(notice_phrases, min(2, len(notice_phrases))) if len(notice_phrases) >= 2 else (notice_phrases if notice_phrases else [])
        scene_phrases_selected = random.sample(scene_phrases, min(2, len(scene_phrases))) if len(scene_phrases) >= 2 else (scene_phrases if scene_phrases else [])
        micro_action_phrase = random.choice(micro_action_phrases) if micro_action_phrases else None
        
        # Выбираем маркеры из словарей
        body_markers = random.sample(dictionaries['body'], min(1, len(dictionaries['body'])))
        social_markers = random.sample(dictionaries['social'], min(1, len(dictionaries['social'])))
        domestic_markers = random.sample(dictionaries['domestic'], min(1, len(dictionaries['domestic'])))
        micro_action_markers = random.sample(dictionaries['micro_action'], min(1, len(dictionaries['micro_action'])))
        
        return GenerationPlan(
            theme={'phrase': theme_phrase} if theme_phrase else {},
            notice=[{'phrase': p} for p in notice_phrases_selected],
            scene=[{'phrase': p} for p in scene_phrases_selected],
            micro_action={'phrase': micro_action_phrase} if micro_action_phrase else {},
            markers={
                'body': body_markers,
                'social': social_markers,
                'domestic': domestic_markers,
                'micro_action': micro_action_markers
            },
            layers=request.layers
        )


class TextWriter:
    """Writer: превращает план в текст. При OPENAI_API_KEY — использует LLM."""
    
    def __init__(self):
        self._lexicon_cache = None
    
    def _load_lexicon(self) -> Dict:
        """Загружает Lexicon (с кешированием)."""
        if self._lexicon_cache is None:
            self._lexicon_cache = load_lexicon()
        return self._lexicon_cache
    
    def write_forecast(
        self, 
        plan: GenerationPlan, 
        request: GenerationRequest,
        user=None,
        db=None,
        target_date: Optional[str] = None
    ) -> GeneratedForecast:
        """Превращает план в текст прогноза. Если настроен LLM — генерирует блоки."""
        blocks: Dict[str, Any] = {}
        use_llm = is_llm_chat_configured()
        user_context = None
        
        # Собираем контекст пользователя, если доступны user и db
        # ВАЖНО: Контекст пользователя (особенно натальная карта) критичен для качественной генерации
        if use_llm and user and db and target_date:
            try:
                from todayflow_backend.core.user_context import get_user_context
                # Передаём потребности пользователя (context из request)
                needs = request.context if hasattr(request, 'context') else None
                user_context = get_user_context(user, target_date, db, needs=needs)
                
                # Логируем, если натальная карта не найдена (это важное предупреждение)
                if not user_context.get("natal_chart"):
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(f"User {user.id} has no natal chart - forecasts will be less personalized")
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Failed to get user context: {e}", exc_info=True)
                # Продолжаем без контекста, но генерация будет менее персонализированной
        
        if use_llm:
            from todayflow_backend.core.ai_client import generate_forecast_blocks
            plan_dict = {
                "theme": plan.theme,
                "notice": plan.notice,
                "scene": plan.scene,
                "micro_action": plan.micro_action,
                "markers": plan.markers,
            }
            request_dict = {
                "forecast_type": request.forecast_type,
                "context": request.context or "",
                "locale": request.locale,
                "date": target_date or "",
            }
            llm_blocks = generate_forecast_blocks(plan_dict, request_dict, user_context)
            if llm_blocks:
                blocks = {
                    "theme": llm_blocks["theme"],
                    "notice": llm_blocks["notice"],
                    "scene": llm_blocks["scene"],
                    "micro_action": llm_blocks["micro_action"],
                }
        if not blocks:
            # Lexicon-only: извлекаем тексты из фраз
            theme_text = plan.theme.get('phrase', {}).get('text', '') if plan.theme.get('phrase') else ''
            if not theme_text:
                theme_text = 'Этот день складывается лучше, если заранее решить, что здесь главное, и не отдавать лучшие часы случайным задачам.'
            notice_texts = [
                item.get('phrase', {}).get('text', '')
                for item in plan.notice
                if item.get('phrase') and item.get('phrase', {}).get('text')
            ]
            if not notice_texts:
                notice_texts = ['Проверь, не уходит ли внимание в мелочи вместо того, что действительно должно продвинуться сегодня.']
            scene_texts = [
                item.get('phrase', {}).get('text', '')
                for item in plan.scene
                if item.get('phrase') and item.get('phrase', {}).get('text')
            ]
            if not scene_texts:
                scene_texts = ['И в рабочих, и в личных вопросах сегодня полезнее короткие договоренности с понятным сроком, чем длинные обсуждения без решения.']
            micro_action_text = plan.micro_action.get('phrase', {}).get('text', '') if plan.micro_action.get('phrase') else ''
            if not micro_action_text:
                micro_action_text = 'Запиши, что именно должно сдвинуться сегодня, и закрой первый шаг по этому в ближайшие 30 минут.'
            blocks = {
                "theme": theme_text,
                "notice": notice_texts,
                "scene": scene_texts,
                "micro_action": micro_action_text,
            }
        forecast = {
            "blocks": blocks,
            "markers": plan.markers,
            "tags": [request.context] if request.context else [],
        }
        return GeneratedForecast(
            blocks=forecast["blocks"],
            markers=forecast["markers"],
            tags=forecast["tags"],
            quality={"score": 0.0, "violations": []},
            plan=plan,
        )


class TextGenerator:
    """Генератор текстов — объединяет Planner и Writer."""
    
    def __init__(self):
        self.planner = TextPlanner()
        self.writer = TextWriter()
    
    def generate_from_meaning(
        self,
        day_meaning,
        user_context: Optional[Dict] = None,
        locale: str = "ru",
        validate: bool = True,
    ) -> GeneratedForecast:
        """
        Генерирует прогноз из смыслового состояния дня (DayMeaning).
        
        Правильный пайплайн:
        1. DayMeaning (источник смысла)
        2. Интерпретационный фокус
        3. Подбор лексикона
        4. Сборка текста через ИИ
        """
        # 1. Определяем интерпретационный фокус на основе DayMeaning
        interpretation_focus = self._select_interpretation_focus(day_meaning)
        
        # 2. Подбираем лексикон на основе смысла (не наоборот)
        lexicon_entries = self._select_lexicon_for_meaning(day_meaning, interpretation_focus)
        
        # 3. Собираем текст через ИИ (если доступен)
        if is_llm_chat_configured() and user_context is not None:
            from todayflow_backend.core.ai_client import generate_forecast_from_meaning
            
            forecast_blocks = generate_forecast_from_meaning(
                day_meaning=day_meaning.to_dict(),
                interpretation_focus=interpretation_focus,
                lexicon_entries=lexicon_entries,
                user_context=user_context,
                locale=locale
            )
            
            if forecast_blocks:
                return GeneratedForecast(
                    blocks=forecast_blocks,
                    markers={},  # TODO: извлечь из day_meaning
                    tags=[day_meaning.focus_area] if day_meaning.focus_area != "general" else [],
                    quality={"score": 1.0, "violations": []},
                    plan=None
                )
        
        # 4. Fallback: собираем из лексикона (без ИИ)
        return self._assemble_from_lexicon(day_meaning, interpretation_focus, lexicon_entries, locale)
    
    def _select_interpretation_focus(self, day_meaning) -> Dict[str, Any]:
        """Выбирает интерпретационный фокус на основе DayMeaning."""
        # Определяем, где проявляется состояние дня
        focus_area = day_meaning.focus_area
        direction = day_meaning.interpretation_direction
        intensity = day_meaning.intensity
        
        # Анализируем астрологическое состояние для уточнения фокуса
        tensions = day_meaning.astro_state.tensions
        resources = day_meaning.astro_state.resources
        
        return {
            "area": focus_area,
            "direction": direction,
            "intensity": intensity,
            "tension_count": len(tensions),
            "resource_count": len(resources),
            "key_tensions": tensions[:2] if tensions else [],
            "key_resources": resources[:2] if resources else [],
        }
    
    def _select_lexicon_for_meaning(self, day_meaning, interpretation_focus: Dict) -> Dict[str, Any]:
        """Подбирает лексикон на основе смысла дня, а не наоборот.
        
        Использует новые поля лексикона:
        - source (astrology/numerology/tarot/general)
        - interpretation_direction (tension/release/transition/fixation/neutral)
        - focus_area (work/body/dialogue/home/relationship/money/general)
        - compatible_with (список совместимых состояний/транзитов)
        - function (normalize/explain/guide)
        - explains (что объясняет фраза)
        """
        lexicon = self.planner._load_lexicon()
        phrases = lexicon.get('phrases', [])
        
        # Извлекаем параметры из DayMeaning
        direction = day_meaning.interpretation_direction if hasattr(day_meaning, 'interpretation_direction') else interpretation_focus.get("direction", "neutral")
        area = day_meaning.focus_area if hasattr(day_meaning, 'focus_area') else interpretation_focus.get("area", "general")
        
        # Определяем источник (если есть транзиты - астрология, если нумерология - нумерология)
        source = "general"
        if day_meaning.astro_state and day_meaning.astro_state.transits:
            source = "astrology"
        elif day_meaning.numerology_context:
            source = "numerology"
        if day_meaning.archetype:
            source = "tarot"  # Если есть таро, приоритет таро
        
        # Собираем совместимые состояния для проверки compatible_with
        compatible_states = []
        if direction:
            compatible_states.append(f"{direction}_days")
        if area and area != "general":
            compatible_states.append(f"{area}_focus")
        # Добавляем транзиты (упрощенно - по планетам)
        if day_meaning.astro_state and day_meaning.astro_state.transits:
            for transit in day_meaning.astro_state.transits[:3]:  # Берем первые 3
                if isinstance(transit, dict):
                    planet = transit.get("planet", "").lower()
                    if planet:
                        compatible_states.append(f"{planet}_transits")
        
        compatible_phrases = []
        for phrase in phrases:
            score = 0  # Оценка совместимости
            
            # 1. Проверяем источник (если указан)
            phrase_source = phrase.get("source")
            if phrase_source:
                if phrase_source == source:
                    score += 3  # Высокий приоритет совпадению источника
                elif phrase_source == "general":
                    score += 1  # Общие фразы подходят всегда
                else:
                    continue  # Несовместимый источник - пропускаем
            
            # 2. Проверяем направление интерпретации
            phrase_direction = phrase.get("interpretation_direction")
            if phrase_direction:
                if phrase_direction == direction:
                    score += 2
                elif direction == "neutral" or phrase_direction == "neutral":
                    score += 0.5  # Нейтральные совместимы с любыми
                else:
                    continue  # Несовместимое направление
            
            # 3. Проверяем фокусную область
            phrase_area = phrase.get("focus_area")
            if phrase_area:
                if isinstance(phrase_area, list):
                    if area in phrase_area:
                        score += 2
                    elif "general" in phrase_area:
                        score += 0.5
                    elif area == "general":
                        score += 0.5
                    else:
                        continue  # Несовместимая область
                elif phrase_area == area or phrase_area == "general" or area == "general":
                    score += 2
            
            # 4. Проверяем compatible_with
            phrase_compatible = phrase.get("compatible_with", [])
            if phrase_compatible:
                matches = sum(1 for state in compatible_states if state in phrase_compatible)
                if matches > 0:
                    score += matches * 1.5
                # Если нет совпадений, но есть общие состояния - не исключаем, но снижаем приоритет
            
            # 5. Проверяем функцию (для разнообразия выбираем разные функции)
            phrase_function = phrase.get("function", "normalize")
            # Это используется для баланса, не для фильтрации
            
            # Fallback: если фраза не имеет новых полей, используем старые
            if not phrase_source and not phrase_direction and not phrase_area:
                # Старая фраза - проверяем по старым полям
                phrase_emotion = phrase.get("emotion", "")
                phrase_context = phrase.get("context", "")
                
                # Сопоставляем emotion с direction
                emotion_to_direction = {
                    "tension": "tension",
                    "irritability": "tension",
                    "anxiety": "tension",
                    "fatigue": "tension",
                    "calm": "release",
                    "relief": "release",
                    "numbness": "fixation",
                }
                if phrase_emotion in emotion_to_direction:
                    if emotion_to_direction[phrase_emotion] == direction:
                        score += 1
                
                # Сопоставляем context с area
                context_to_area = {
                    "work": "work",
                    "relationship": "relationship",
                    "body": "body",
                    "home": "home",
                }
                if phrase_context in context_to_area:
                    if context_to_area[phrase_context] == area or area == "general":
                        score += 1
            
            if score > 0:
                compatible_phrases.append((phrase, score))
        
        # Сортируем по score и выбираем лучшие
        compatible_phrases.sort(key=lambda x: x[1], reverse=True)
        selected_phrases = [p[0] for p in compatible_phrases[:10]]  # Берем топ-10
        
        # Если нет совместимых фраз, берём любые (fallback)
        if not selected_phrases:
            selected_phrases = phrases[:10]
        
        # Распределяем по структуре, учитывая function
        normalize_phrases = [p for p in selected_phrases if p.get("function") == "normalize"]
        explain_phrases = [p for p in selected_phrases if p.get("function") == "explain"]
        guide_phrases = [p for p in selected_phrases if p.get("function") == "guide"]
        
        # Если нет фраз с function, используем все
        if not normalize_phrases and not explain_phrases and not guide_phrases:
            normalize_phrases = selected_phrases
        
        return {
            "theme": (normalize_phrases[:1] or explain_phrases[:1] or selected_phrases[:1]) if selected_phrases else [],
            "notice": (normalize_phrases[:2] or explain_phrases[:2] or selected_phrases[:2]) if len(selected_phrases) > 1 else [],
            "scene": (guide_phrases[:2] or selected_phrases[:2]) if len(selected_phrases) > 2 else [],
            "micro_action": (guide_phrases[-1] if guide_phrases else selected_phrases[-1]) if selected_phrases else None,
        }
    
    def _assemble_from_lexicon(
        self,
        day_meaning,
        interpretation_focus: Dict,
        lexicon_entries: Dict,
        locale: str
    ) -> GeneratedForecast:
        """Собирает прогноз из лексикона без ИИ (fallback)."""
        theme_phrase = lexicon_entries.get("theme", [{}])[0] if lexicon_entries.get("theme") else {}
        notice_phrases = lexicon_entries.get("notice", [])
        scene_phrases = lexicon_entries.get("scene", [])
        micro_action_phrase = lexicon_entries.get("micro_action", {})
        
        blocks = {
            "theme": theme_phrase.get("text", "День читается лучше, если заранее решить, что здесь главное, и не отдавать лучшие силы случайным делам."),
            "notice": [p.get("text", "") for p in notice_phrases if p.get("text")],
            "scene": [p.get("text", "") for p in scene_phrases if p.get("text")],
            "micro_action": micro_action_phrase.get("text", "Назови один приоритет дня и убери одну задачу, которая только создает занятость, но не двигает результат.") if isinstance(micro_action_phrase, dict) else "Назови один приоритет дня и убери одну задачу, которая только создает занятость, но не двигает результат.",
        }
        
        return GeneratedForecast(
            blocks=blocks,
            markers={},
            tags=[day_meaning.focus_area] if day_meaning.focus_area != "general" else [],
            quality={"score": 0.5, "violations": []},
            plan=None
        )
    
    def generate(
        self,
        request: GenerationRequest,
        validate: bool = True,
        user=None,
        db=None,
        target_date: Optional[str] = None
    ) -> GeneratedForecast:
        """Генерирует прогноз по запросу."""
        # 1. Planner создаёт план
        plan = self.planner.create_plan(request)
        
        # 2. Writer превращает план в текст (с контекстом пользователя, если доступен)
        forecast = self.writer.write_forecast(plan, request, user=user, db=db, target_date=target_date)
        
        # 3. Safety validation checks only payload health, not writing style.
        if validate:
            from todayflow_backend.data.content_system import _quality_gate_sets
            body_markers, social_markers, domestic_markers, micro_action_markers, banned_words, tags_allow_list = _quality_gate_sets()
            
            forecast_dict = {
                'blocks': forecast.blocks,
                'markers': forecast.markers,
                'tags': forecast.tags
            }
            
            qg_result = validate_daily_forecast(
                forecast_dict,
                body_markers=body_markers,
                social_markers=social_markers,
                domestic_markers=domestic_markers,
                micro_action_markers=micro_action_markers,
                banned_words=banned_words,
                tags_allow_list=tags_allow_list
            )
            
            # Обновляем качество
            forecast.quality = {
                'score': 1.0 if qg_result.ok else 0.7,
                'violations': qg_result.errors,
                'ok': qg_result.ok
            }
        
        return forecast

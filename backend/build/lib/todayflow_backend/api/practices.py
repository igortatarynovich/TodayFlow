"""Practices API endpoints."""

import logging
from datetime import datetime, date, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi import Request as FastAPIRequest
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func

from todayflow_backend.api.auth import get_optional_user, require_user
from todayflow_backend.core import models
from todayflow_backend.i18n import request_locale, translate
from todayflow_backend.db.session import get_session
from todayflow_backend.db.models import User, PracticeUsage, Subscription
from todayflow_backend.services.subscription_level import get_subscription_level
from todayflow_backend.core.content_loader import load_asceticisms, load_affirmations

router = APIRouter(prefix="/practices", tags=["practices"])


class PracticeResponse(BaseModel):
    id: str
    title: str
    description: str
    category: str  # "meditation", "breathing", "gratitude", "affirmation", "ritual"
    practice_type: Optional[str] = None  # "micro_daily", "awareness_check", "pattern_based", "compensatory", "domain_bridge", "weekly_reflection", "cycle_based", "guided_sequence"
    duration_minutes: Optional[int] = None
    difficulty: str  # "beginner", "intermediate", "advanced"
    is_free: bool
    is_personalized: bool
    personalized_reason: Optional[str] = None  # Почему эта практика рекомендована
    access_level: str  # "free", "lite", "pro"
    tags: List[str] = []
    # Персонализация
    target_axis: Optional[str] = None  # A1-A7
    target_modulator: Optional[str] = None  # M1-M4
    pattern_type: Optional[str] = None  # "observation", "action", "reflection"
    # Мосты между доменами
    source_domain: Optional[str] = None
    target_domain: Optional[str] = None
    # Циклы
    cycle_type: Optional[str] = None  # "lunar", "weekly", "monthly", "transition"
    trigger_phase: Optional[str] = None
    # Серии
    sequence_id: Optional[str] = None
    step_number: Optional[int] = None
    total_steps: Optional[int] = None


class PracticeStep(BaseModel):
    step_number: int
    title: str
    description: str
    duration_minutes: Optional[int] = None
    instructions: List[str] = []
    questions: Optional[List[str]] = None


class PracticeDetailResponse(PracticeResponse):
    instructions: List[str] = []
    prompt: Optional[str] = None  # Для awareness check и reflection
    questions: Optional[List[str]] = []  # Для weekly reflection
    audio_url: Optional[str] = None
    related_practices: List[str] = []
    steps: Optional[List[PracticeStep]] = None  # Для guided sequences


class SequenceProgressResponse(BaseModel):
    sequence_id: str
    sequence_title: str
    total_steps: int
    completed_steps: int
    current_step: Optional[int] = None
    started_at: Optional[datetime] = None
    last_completed_at: Optional[datetime] = None
    is_completed: bool


class PracticeUsageResponse(BaseModel):
    practice_id: str
    completed_at: datetime


class PracticeLimitsResponse(BaseModel):
    subscription_level: str  # "free", "lite", "pro"
    personalized_limit: int  # Лимит персонализированных практик в неделю
    used_this_week: int  # Использовано персонализированных практик на этой неделе
    remaining_this_week: int  # Осталось персонализированных практик на этой неделе
    week_start: date  # Начало текущей недели


class PracticeHistoryItem(BaseModel):
    id: int
    practice_id: str
    practice_title: Optional[str] = None
    category: Optional[str] = None
    completed_at: datetime
    is_personalized: bool
    sequence_id: Optional[str] = None
    step_number: Optional[int] = None


class PracticeHistoryResponse(BaseModel):
    history: List[PracticeHistoryItem]
    total: int


class CategoryProgress(BaseModel):
    category: str
    total_completed: int
    personalized_completed: int


class PracticeProgressResponse(BaseModel):
    total_completed: int
    personalized_completed: int
    general_completed: int
    by_category: List[CategoryProgress]
    current_streak_days: int  # Текущая серия дней подряд
    longest_streak_days: int  # Самая длинная серия дней подряд
    weeks_active: int  # Количество недель с активностью


# Общие практики для гостей
GENERAL_PRACTICES = [
    {
        "id": "breathing-4-7-8",
        "title": "Дыхание 4-7-8",
        "description": "Классическая техника дыхания для успокоения нервной системы",
        "category": "breathing",
        "duration_minutes": 5,
        "difficulty": "beginner",
        "is_free": True,
        "is_personalized": False,
        "access_level": "free",
        "tags": ["успокоение", "фокус", "быстро"],
        "instructions": [
            "Сядьте удобно или лягте",
            "Вдохните через нос на 4 счета",
            "Задержите дыхание на 7 счетов",
            "Выдохните через рот на 8 счетов",
            "Повторите цикл 4-8 раз"
        ]
    },
    {
        "id": "body-scan",
        "title": "Сканирование тела",
        "description": "Медитация осознанности через последовательное внимание к частям тела",
        "category": "meditation",
        "duration_minutes": 10,
        "difficulty": "beginner",
        "is_free": True,
        "is_personalized": False,
        "access_level": "free",
        "tags": ["осознанность", "расслабление"],
        "instructions": [
            "Лягте удобно",
            "Начните с пальцев ног, медленно перемещая внимание вверх",
            "Замечайте ощущения в каждой части тела без оценки",
            "Завершите на макушке головы"
        ]
    },
    {
        "id": "gratitude-list",
        "title": "Список благодарности",
        "description": "Запишите 3-5 вещей, за которые вы благодарны сегодня",
        "category": "gratitude",
        "duration_minutes": 5,
        "difficulty": "beginner",
        "is_free": True,
        "is_personalized": False,
        "access_level": "free",
        "tags": ["благодарность", "письмо"],
        "instructions": [
            "Возьмите лист бумаги или откройте заметки",
            "Запишите 3-5 вещей, за которые вы благодарны",
            "Почувствуйте эмоции благодарности",
            "Прочитайте список вслух"
        ]
    },
    {
        "id": "box-breathing",
        "title": "Квадратное дыхание",
        "description": "Равномерное дыхание для концентрации и баланса",
        "category": "breathing",
        "duration_minutes": 3,
        "difficulty": "beginner",
        "is_free": True,
        "is_personalized": False,
        "access_level": "free",
        "tags": ["концентрация", "баланс"],
        "instructions": [
            "Вдох на 4 счета",
            "Задержка на 4 счета",
            "Выдох на 4 счета",
            "Пауза на 4 счета",
            "Повторите 4-6 циклов"
        ]
    },
    {
        "id": "morning-intention",
        "title": "Утреннее намерение",
        "description": "Установите намерение на день",
        "category": "affirmation",
        "duration_minutes": 3,
        "difficulty": "beginner",
        "is_free": True,
        "is_personalized": False,
        "access_level": "free",
        "tags": ["намерение", "утро"],
        "instructions": [
            "Сядьте спокойно",
            "Спросите себя: 'Что важно для меня сегодня?'",
            "Сформулируйте одно намерение",
            "Повторите его 3 раза вслух"
        ]
    },
    {
        "id": "loving-kindness-meditation",
        "title": "Медитация любящей доброты",
        "description": "Практика метта-медитации для развития сострадания",
        "category": "meditation",
        "duration_minutes": 15,
        "difficulty": "intermediate",
        "is_free": True,
        "is_personalized": False,
        "access_level": "free",
        "tags": ["сострадание", "любовь", "медитация"],
        "instructions": [
            "Сядьте удобно с закрытыми глазами",
            "Начните с пожелания счастья себе",
            "Затем пожелайте счастья близкому человеку",
            "Пожелайте счастья нейтральному человеку",
            "Пожелайте счастья всем живым существам"
        ]
    },
    {
        "id": "alternate-nostril-breathing",
        "title": "Попеременное дыхание ноздрями",
        "description": "Нади Шодхана пранаяма для баланса энергии",
        "category": "breathing",
        "duration_minutes": 5,
        "difficulty": "beginner",
        "is_free": True,
        "is_personalized": False,
        "access_level": "free",
        "tags": ["баланс", "энергия", "дыхание"],
        "instructions": [
            "Сядьте удобно, выпрямите спину",
            "Закройте правую ноздрю большим пальцем",
            "Вдохните через левую ноздрю на 4 счета",
            "Закройте левую ноздрю безымянным пальцем",
            "Выдохните через правую ноздрю на 4 счета",
            "Вдохните через правую на 4 счета",
            "Выдохните через левую на 4 счета",
            "Повторите цикл 5-10 раз"
        ]
    },
    {
        "id": "walking-meditation",
        "title": "Медитация при ходьбе",
        "description": "Осознанная ходьба для соединения тела и ума",
        "category": "meditation",
        "duration_minutes": 10,
        "difficulty": "beginner",
        "is_free": True,
        "is_personalized": False,
        "access_level": "free",
        "tags": ["движение", "осознанность", "медитация"],
        "instructions": [
            "Найдите тихое место для ходьбы",
            "Идите медленно, обращая внимание на каждый шаг",
            "Замечайте ощущения в стопах",
            "Следите за дыханием",
            "Если ум отвлекся, мягко верните внимание к ходьбе"
        ]
    },
    {
        "id": "kapalabhati-breathing",
        "title": "Капалабхати (Огненное дыхание)",
        "description": "Очищающая дыхательная техника для энергии и ясности",
        "category": "breathing",
        "duration_minutes": 3,
        "difficulty": "intermediate",
        "is_free": True,
        "is_personalized": False,
        "access_level": "free",
        "tags": ["энергия", "очищение", "дыхание"],
        "instructions": [
            "Сядьте с прямой спиной",
            "Сделайте глубокий вдох",
            "Быстро и резко выдыхайте через нос, втягивая живот",
            "Вдох происходит пассивно",
            "Начните с 20 выдохов, затем отдохните",
            "Повторите 3 раунда"
        ]
    },
    {
        "id": "mindful-eating",
        "title": "Осознанное питание",
        "description": "Практика внимательности во время еды",
        "category": "meditation",
        "duration_minutes": 10,
        "difficulty": "beginner",
        "is_free": True,
        "is_personalized": False,
        "access_level": "free",
        "tags": ["осознанность", "питание", "медитация"],
        "instructions": [
            "Перед едой сделайте паузу и посмотрите на пищу",
            "Замечайте цвета, текстуру, запах",
            "Первый кусок ешьте медленно, полностью ощущая вкус",
            "Жуйте тщательно, обращая внимание на ощущения",
            "Делайте паузы между кусочками"
        ]
    },
    {
        "id": "deep-breathing-relaxation",
        "title": "Глубокое дыхание для расслабления",
        "description": "Простая техника для снятия напряжения",
        "category": "breathing",
        "duration_minutes": 5,
        "difficulty": "beginner",
        "is_free": True,
        "is_personalized": False,
        "access_level": "free",
        "tags": ["расслабление", "успокоение", "дыхание"],
        "instructions": [
            "Лягте или сядьте удобно",
            "Положите одну руку на грудь, другую на живот",
            "Вдохните глубоко через нос на 4 счета",
            "Задержите дыхание на 4 счета",
            "Медленно выдохните через рот на 6 счетов",
            "Повторите 8-10 раз"
        ]
    }
]

# Персонализированные практики с привязкой к паттернам
# Эти практики доступны только для зарегистрированных пользователей
PERSONALIZED_PRACTICES = [
    # ========== MICRO DAILY PRACTICES (Daily Hook) ==========
    {
        "id": "micro-question-focus",
        "title": "1 вопрос для фокусировки",
        "description": "Короткий вопрос для концентрации внимания на важном",
        "category": "focus",
        "practice_type": "micro_daily",
        "duration_minutes": 1,
        "difficulty": "beginner",
        "is_free": False,
        "access_level": "lite",
        "tags": ["микро", "фокус", "быстро"],
        "instructions": [
            "Задайте себе один вопрос: 'Что самое важное для меня прямо сейчас?'",
            "Дайте себе 30 секунд на ответ",
            "Сфокусируйтесь на этом"
        ],
        "prompt": "Что самое важное для меня прямо сейчас?"
    },
    {
        "id": "micro-reaction-observe",
        "title": "30 секунд наблюдения за реакцией",
        "description": "Короткая практика осознанности для наблюдения за своими реакциями",
        "category": "meditation",
        "practice_type": "micro_daily",
        "duration_minutes": 1,
        "difficulty": "beginner",
        "is_free": False,
        "access_level": "lite",
        "tags": ["микро", "осознанность", "наблюдение"],
        "instructions": [
            "Вспомните последнюю ситуацию, которая вызвала у вас реакцию",
            "Наблюдайте за своими ощущениями в теле 30 секунд",
            "Заметьте, что происходит без оценки"
        ]
    },
    {
        "id": "micro-conscious-action",
        "title": "Одно осознанное действие сегодня",
        "description": "Выберите одно действие и выполните его с полным вниманием",
        "category": "meditation",
        "practice_type": "micro_daily",
        "duration_minutes": 2,
        "difficulty": "beginner",
        "is_free": False,
        "access_level": "lite",
        "tags": ["микро", "осознанность", "действие"],
        "instructions": [
            "Выберите одно простое действие (например, выпить чай, пройтись)",
            "Выполните его медленно и с полным вниманием",
            "Замечайте каждое движение и ощущение"
        ]
    },
    
    # ========== AWARENESS CHECK PRACTICES ==========
    {
        "id": "awareness-delayed-emotional-response",
        "title": "Где я отреагировал не сразу",
        "description": "Обрати внимание на ситуации, где ты понял, что что-то почувствовал, уже после того, как разговор или событие закончились.",
        "category": "emotional",
        "practice_type": "awareness_check",
        "duration_minutes": 2,
        "difficulty": "beginner",
        "is_free": False,
        "access_level": "lite",
        "target_axis": "A2",  # Emotional Processing - Delayed Emotional Response
        "pattern_type": "observation",
        "tags": ["наблюдение", "эмоции", "задержка реакции", "daily hook"],
        "prompt": "Сегодня обрати внимание на ситуации, где ты понял, что что-то почувствовал, уже после того, как разговор или событие закончились. Не нужно ничего делать — просто замечай."
    },
    {
        "id": "awareness-decision-process",
        "title": "Осознанное наблюдение: процесс принятия решений",
        "description": "Обрати внимание сегодня, как ты принимаешь решения",
        "category": "focus",
        "practice_type": "awareness_check",
        "duration_minutes": None,
        "difficulty": "beginner",
        "is_free": False,
        "access_level": "lite",
        "target_axis": "A3",  # Decision Making
        "pattern_type": "observation",
        "tags": ["наблюдение", "решения"],
        "prompt": "Обрати внимание сегодня, как ты принимаешь решения. Что происходит первым: интуиция или анализ?"
    },
    {
        "id": "awareness-control-tendency",
        "title": "Осознанное наблюдение: стремление к контролю",
        "description": "Обрати внимание сегодня, где ты пытаешься контролировать ситуацию",
        "category": "breathing",
        "practice_type": "awareness_check",
        "duration_minutes": None,
        "difficulty": "beginner",
        "is_free": False,
        "access_level": "lite",
        "target_axis": "A5",  # Control Orientation
        "pattern_type": "observation",
        "tags": ["наблюдение", "контроль"],
        "prompt": "Обрати внимание сегодня, где ты пытаешься контролировать ситуацию или других людей. Замечай это без осуждения."
    },
    
    # ========== PATTERN-BASED PRACTICES (Observation) ==========
    {
        "id": "pattern-a1-observation",
        "title": "Наблюдение: ориентация идентичности",
        "description": "Заметь, откуда ты черпаешь чувство себя: изнутри или извне",
        "category": "meditation",
        "practice_type": "pattern_based",
        "duration_minutes": 3,
        "difficulty": "beginner",
        "is_free": False,
        "access_level": "lite",
        "target_axis": "A1",
        "pattern_type": "observation",
        "tags": ["паттерн", "наблюдение", "идентичность"],
        "instructions": [
            "В течение дня замечай моменты, когда ты ищешь подтверждение извне",
            "Или моменты, когда ты опираешься на внутреннее чувство",
            "Просто наблюдай, без оценки"
        ]
    },
    {
        "id": "pattern-a2-observation",
        "title": "Наблюдение: обработка эмоций",
        "description": "Заметь, как ты обрабатываешь эмоции: держишь внутри или выражаешь",
        "category": "emotional",
        "practice_type": "pattern_based",
        "duration_minutes": 3,
        "difficulty": "beginner",
        "is_free": False,
        "access_level": "lite",
        "target_axis": "A2",
        "pattern_type": "observation",
        "tags": ["паттерн", "наблюдение", "эмоции"],
        "instructions": [
            "Когда возникает эмоция, заметь, что ты с ней делаешь",
            "Держишь внутри или сразу выражаешь?",
            "Наблюдай без попытки изменить"
        ]
    },
    
    # ========== PATTERN-BASED PRACTICES (Action) ==========
    {
        "id": "pattern-a2-delayed-micro-pause",
        "title": "Пауза перед ответом",
        "description": "В следующем эмоционально значимом диалоге сделай паузу в 5–10 секунд перед ответом. Не чтобы сказать «правильно», а чтобы дать эмоциям догнать мысль.",
        "category": "focus",
        "practice_type": "micro_daily",
        "duration_minutes": 2,
        "difficulty": "beginner",
        "is_free": False,
        "access_level": "lite",
        "target_axis": "A2",  # Emotional Processing - Delayed Emotional Response
        "pattern_type": "action",
        "tags": ["микро-действие", "пауза", "эмоции", "привычка"],
        "instructions": [
            "В следующем эмоционально значимом диалоге сделай паузу в 5–10 секунд перед ответом",
            "Не чтобы сказать «правильно», а чтобы дать эмоциям догнать мысль",
            "Заметь, что изменилось в твоей реакции"
        ]
    },
    {
        "id": "pattern-a5-action-space",
        "title": "Действие: дать себе пространство",
        "description": "Дай себе пространство перед реакцией, вместо немедленного контроля",
        "category": "breathing",
        "practice_type": "compensatory",
        "duration_minutes": 2,
        "difficulty": "intermediate",
        "is_free": False,
        "access_level": "lite",
        "target_axis": "A5",
        "pattern_type": "action",
        "tags": ["компенсаторная", "действие", "контроль"],
        "instructions": [
            "Когда чувствуешь желание контролировать, остановись",
            "Сделай шаг назад (буквально или метафорически)",
            "Дай ситуации пространство развернуться"
        ]
    },
    
    # ========== PATTERN-BASED PRACTICES (Reflection) ==========
    {
        "id": "weekly-reflection-delayed-emotional-response",
        "title": "Что я понял позже",
        "description": "Еженедельная рефлексия о задержанных эмоциональных реакциях. Переводит паттерн из «я такой» в «я понимаю, как это работает».",
        "category": "reflection",
        "practice_type": "weekly_reflection",
        "duration_minutes": 5,
        "difficulty": "beginner",
        "is_free": False,
        "access_level": "lite",
        "target_axis": "A2",  # Emotional Processing - Delayed Emotional Response
        "cycle_type": "weekly",
        "tags": ["рефлексия", "неделя", "эмоции", "weekly anchor"],
        "questions": [
            "Где сегодня я понял свои чувства с задержкой?",
            "Что я сделал, когда понял?",
            "Что помогло бы мне заметить это раньше?"
        ],
        "instructions": [
            "Выдели 5 минут в спокойной обстановке",
            "Ответь на 3 вопроса письменно или мысленно",
            "Без оценки, просто наблюдение и понимание"
        ]
    },
    
    # ========== COMPENSATORY PRACTICES (Complete sets for all axes) ==========
    
    # A1 — Identity Orientation
    {
        "id": "compensatory-a1-inner-grounding",
        "title": "Заземление во внутреннем",
        "description": "Короткое дыхание + внимание к внутреннему ощущению себя. Для тех, кто ищет внешнего подтверждения.",
        "category": "breathing",
        "practice_type": "compensatory",
        "duration_minutes": 3,
        "difficulty": "beginner",
        "is_free": False,
        "access_level": "lite",
        "target_axis": "A1",
        "tags": ["компенсаторная", "дыхание", "идентичность", "снижение напряжения"],
        "instructions": [
            "Сядь удобно и закрой глаза",
            "Сделай 5 глубоких вдохов через нос и выдохов через рот",
            "Обрати внимание на внутреннее ощущение себя",
            "Дай этому ощущению быть достаточным, без внешнего подтверждения",
            "Продолжай дышать спокойно ещё 2 минуты"
        ]
    },
    
    # A2 — Emotional Processing (уже есть, оставляем)
    {
        "id": "compensatory-a2-delayed-emotional-unloading",
        "title": "Разгрузка накопленного",
        "description": "Короткое дыхание + внимание к телу. Эта практика не про анализ, а про освобождение того, что не успело выйти.",
        "category": "breathing",
        "practice_type": "compensatory",
        "duration_minutes": 3,
        "difficulty": "beginner",
        "is_free": False,
        "access_level": "lite",
        "target_axis": "A2",
        "tags": ["компенсаторная", "дыхание", "разгрузка", "снижение напряжения"],
        "instructions": [
            "Сядь удобно и закрой глаза",
            "Сделай 5 глубоких вдохов через нос и выдохов через рот",
            "Обрати внимание на тело: где есть напряжение?",
            "Дай этому месту пространство, не пытаясь изменить",
            "Продолжай дышать спокойно ещё 2 минуты"
        ]
    },
    
    # A3 — Decision Making
    {
        "id": "compensatory-a3-decision-release",
        "title": "Освобождение от анализа",
        "description": "Короткое дыхание + отпускание необходимости анализировать. Для тех, кто склонен к избыточному анализу.",
        "category": "breathing",
        "practice_type": "compensatory",
        "duration_minutes": 3,
        "difficulty": "beginner",
        "is_free": False,
        "access_level": "lite",
        "target_axis": "A3",
        "tags": ["компенсаторная", "дыхание", "решения", "снижение напряжения"],
        "instructions": [
            "Сядь удобно и закрой глаза",
            "Сделай 5 глубоких вдохов через нос и выдохов через рот",
            "Обрати внимание на ум: где он пытается анализировать?",
            "Дай уму отдохнуть от анализа на 3 минуты",
            "Продолжай дышать спокойно"
        ]
    },
    
    # A4 — Stability vs Change
    {
        "id": "compensatory-a4-stability-grounding",
        "title": "Заземление в стабильности",
        "description": "Короткое дыхание + создание точки стабильности. Для тех, кто ищет перемен и чувствует нестабильность.",
        "category": "breathing",
        "practice_type": "compensatory",
        "duration_minutes": 3,
        "difficulty": "beginner",
        "is_free": False,
        "access_level": "lite",
        "target_axis": "A4",
        "tags": ["компенсаторная", "дыхание", "стабильность", "снижение напряжения"],
        "instructions": [
            "Сядь удобно и закрой глаза",
            "Сделай 5 глубоких вдохов через нос и выдохов через рот",
            "Обрати внимание на ощущение стабильности в теле",
            "Создай одну точку стабильности: ритм дыхания",
            "Продолжай дышать в этом ритме ещё 2 минуты"
        ]
    },
    
    # A5 — Control Orientation (уже есть, улучшим)
    {
        "id": "compensatory-a5-adaptation",
        "title": "Адаптация вместо контроля",
        "description": "Короткое дыхание + отпускание контроля. Для тех, кто склонен контролировать.",
        "category": "breathing",
        "practice_type": "compensatory",
        "duration_minutes": 3,
        "difficulty": "beginner",
        "is_free": False,
        "access_level": "lite",
        "target_axis": "A5",
        "tags": ["компенсаторная", "дыхание", "контроль", "адаптация", "снижение напряжения"],
        "instructions": [
            "Сядь удобно и закрой глаза",
            "Сделай 5 глубоких вдохов через нос и выдохов через рот",
            "Обрати внимание на тело: где есть напряжение от контроля?",
            "Отпусти контроль над дыханием — пусть оно идёт само",
            "Продолжай дышать спокойно ещё 2 минуты"
        ]
    },
    
    # A6 — Relational Orientation
    {
        "id": "compensatory-a6-boundary-space",
        "title": "Пространство для себя",
        "description": "Короткое дыхание + создание внутреннего пространства. Для тех, кто ищет связи и чувствует перегрузку от близости.",
        "category": "breathing",
        "practice_type": "compensatory",
        "duration_minutes": 3,
        "difficulty": "beginner",
        "is_free": False,
        "access_level": "lite",
        "target_axis": "A6",
        "tags": ["компенсаторная", "дыхание", "отношения", "границы", "снижение напряжения"],
        "instructions": [
            "Сядь удобно и закрой глаза",
            "Сделай 5 глубоких вдохов через нос и выдохов через рот",
            "Обрати внимание на внутреннее пространство",
            "Создай границу: это моё пространство, здесь только я",
            "Продолжай дышать спокойно ещё 2 минуты"
        ]
    },
    
    # A7 — Energy Management
    {
        "id": "compensatory-a7-energy-restoration",
        "title": "Восстановление энергии",
        "description": "Короткое дыхание + сохранение энергии. Для тех, кто расходует энергию широко и чувствует усталость.",
        "category": "breathing",
        "practice_type": "compensatory",
        "duration_minutes": 3,
        "difficulty": "beginner",
        "is_free": False,
        "access_level": "lite",
        "target_axis": "A7",
        "tags": ["компенсаторная", "дыхание", "энергия", "усталость", "снижение напряжения"],
        "instructions": [
            "Сядь удобно и закрой глаза",
            "Сделай 5 глубоких вдохов через нос и выдохов через рот",
            "Обрати внимание на уровень энергии в теле",
            "Дай энергии восстановиться через спокойное дыхание",
            "Продолжай дышать спокойно ещё 2 минуты"
        ]
    },
    
    # ========== DOMAIN BRIDGE PRACTICES ==========
    {
        "id": "bridge-emotions-relationships",
        "title": "Мост: эмоции → отношения",
        "description": "Как ты сегодня входишь в контакт с другими",
        "category": "emotional",
        "practice_type": "domain_bridge",
        "duration_minutes": 5,
        "difficulty": "intermediate",
        "is_free": False,
        "access_level": "pro",
        "source_domain": "emotional",
        "target_domain": "relationships",
        "tags": ["мост", "эмоции", "отношения"],
        "instructions": [
            "Вспомни последний контакт с другим человеком",
            "Как твои эмоции повлияли на этот контакт?",
            "Что ты не сказал, но почувствовал?"
        ],
        "prompt": "Что ты не сказал в последнем контакте, но почувствовал?"
    },
    {
        "id": "bridge-delayed-emotions-relationships",
        "title": "Мост: задержанная реакция → отношения",
        "description": "Этот паттерн особенно заметен в ситуациях близости, где партнёр ждёт реакции сразу, а ты понимаешь себя позже.",
        "category": "emotional",
        "practice_type": "domain_bridge",
        "duration_minutes": 5,
        "difficulty": "intermediate",
        "is_free": False,
        "access_level": "pro",
        "source_domain": "emotional",
        "target_domain": "relationships",
        "target_axis": "A2",
        "tags": ["мост", "эмоции", "отношения", "близость"],
        "instructions": [
            "Вспомни последнюю ситуацию близости, где партнёр ждал твоей реакции сразу",
            "Что ты почувствовал в моменте?",
            "Что ты понял позже?",
            "Как это повлияло на контакт?"
        ],
        "prompt": "Где в отношениях ты понял свои чувства с задержкой? Как это повлияло на близость?"
    },
    {
        "id": "bridge-delayed-emotions-work-money",
        "title": "Мост: задержанная реакция → работа/деньги",
        "description": "Задержанная реакция может давать ощущение «я понял, что это было слишком, уже после решения».",
        "category": "focus",
        "practice_type": "domain_bridge",
        "duration_minutes": 5,
        "difficulty": "intermediate",
        "is_free": False,
        "access_level": "pro",
        "source_domain": "emotional",
        "target_domain": "money",
        "target_axis": "A2",
        "tags": ["мост", "эмоции", "деньги", "работа", "решения"],
        "instructions": [
            "Вспомни последнее важное решение (работа, деньги, ответственность)",
            "Что ты почувствовал в моменте принятия решения?",
            "Что ты понял позже?",
            "Как задержанная реакция повлияла на решение?"
        ],
        "prompt": "Где ты понял, что решение было слишком, уже после того, как его принял? Как это влияет на ответственность?"
    },
    
    # ========== DOMAIN BRIDGE PRACTICES (Complete sets for all axes) ==========
    
    # A1 — Identity Orientation → Relationships
    {
        "id": "bridge-a1-identity-relationships",
        "title": "Мост: идентичность → отношения",
        "description": "Как твоя ориентация на внутреннее или внешнее влияет на отношения.",
        "category": "emotional",
        "practice_type": "domain_bridge",
        "duration_minutes": 5,
        "difficulty": "intermediate",
        "is_free": False,
        "access_level": "pro",
        "source_domain": "emotional",
        "target_domain": "relationships",
        "target_axis": "A1",
        "tags": ["мост", "идентичность", "отношения"],
        "instructions": [
            "Вспомни последний контакт с другим человеком",
            "Откуда ты черпал чувство себя в этом контакте: изнутри или извне?",
            "Как это повлияло на контакт?"
        ],
        "prompt": "Где в отношениях ты ищешь внешнего подтверждения? Как это влияет на близость?"
    },
    
    # A1 — Identity Orientation → Money/Work
    {
        "id": "bridge-a1-identity-work",
        "title": "Мост: идентичность → работа/деньги",
        "description": "Как твоя ориентация на внутреннее или внешнее влияет на решения о работе и деньгах.",
        "category": "focus",
        "practice_type": "domain_bridge",
        "duration_minutes": 5,
        "difficulty": "intermediate",
        "is_free": False,
        "access_level": "pro",
        "source_domain": "emotional",
        "target_domain": "money",
        "target_axis": "A1",
        "tags": ["мост", "идентичность", "работа", "деньги"],
        "instructions": [
            "Вспомни последнее решение о работе или деньгах",
            "Откуда ты черпал уверенность: из внутреннего чувства или внешнего подтверждения?",
            "Как это повлияло на решение?"
        ],
        "prompt": "Где в работе и деньгах ты ищешь внешнего подтверждения? Как это влияет на решения?"
    },
    
    # A3 — Decision Making → Relationships
    {
        "id": "bridge-a3-decisions-relationships",
        "title": "Мост: решения → отношения",
        "description": "Как твой способ принятия решений (интуиция или анализ) влияет на отношения.",
        "category": "emotional",
        "practice_type": "domain_bridge",
        "duration_minutes": 5,
        "difficulty": "intermediate",
        "is_free": False,
        "access_level": "pro",
        "source_domain": "emotional",
        "target_domain": "relationships",
        "target_axis": "A3",
        "tags": ["мост", "решения", "отношения"],
        "instructions": [
            "Вспомни последнее решение в отношениях",
            "Что происходило первым: интуиция или анализ?",
            "Как это повлияло на отношения?"
        ],
        "prompt": "Где в отношениях ты полагаешься на интуицию, а где на анализ? Как это влияет на близость?"
    },
    
    # A3 — Decision Making → Money/Work
    {
        "id": "bridge-a3-decisions-work",
        "title": "Мост: решения → работа/деньги",
        "description": "Как твой способ принятия решений (интуиция или анализ) влияет на решения о работе и деньгах.",
        "category": "focus",
        "practice_type": "domain_bridge",
        "duration_minutes": 5,
        "difficulty": "intermediate",
        "is_free": False,
        "access_level": "pro",
        "source_domain": "emotional",
        "target_domain": "money",
        "target_axis": "A3",
        "tags": ["мост", "решения", "работа", "деньги"],
        "instructions": [
            "Вспомни последнее важное решение о работе или деньгах",
            "Что происходило первым: интуиция или анализ?",
            "Как это повлияло на решение?"
        ],
        "prompt": "Где в работе и деньгах ты полагаешься на интуицию, а где на анализ? Как это влияет на решения?"
    },
    
    # A4 — Stability vs Change → Relationships
    {
        "id": "bridge-a4-stability-relationships",
        "title": "Мост: стабильность/перемены → отношения",
        "description": "Как твоё стремление к стабильности или переменам влияет на отношения.",
        "category": "emotional",
        "practice_type": "domain_bridge",
        "duration_minutes": 5,
        "difficulty": "intermediate",
        "is_free": False,
        "access_level": "pro",
        "source_domain": "emotional",
        "target_domain": "relationships",
        "target_axis": "A4",
        "tags": ["мост", "стабильность", "перемены", "отношения"],
        "instructions": [
            "Вспомни последнюю ситуацию в отношениях",
            "Что ты искал: стабильность или перемены?",
            "Как это повлияло на отношения?"
        ],
        "prompt": "Где в отношениях ты ищешь стабильности, а где перемен? Как это влияет на близость?"
    },
    
    # A4 — Stability vs Change → Money/Work
    {
        "id": "bridge-a4-stability-work",
        "title": "Мост: стабильность/перемены → работа/деньги",
        "description": "Как твоё стремление к стабильности или переменам влияет на решения о работе и деньгах.",
        "category": "focus",
        "practice_type": "domain_bridge",
        "duration_minutes": 5,
        "difficulty": "intermediate",
        "is_free": False,
        "access_level": "pro",
        "source_domain": "emotional",
        "target_domain": "money",
        "target_axis": "A4",
        "tags": ["мост", "стабильность", "перемены", "работа", "деньги"],
        "instructions": [
            "Вспомни последнее решение о работе или деньгах",
            "Что ты искал: стабильность или перемены?",
            "Как это повлияло на решение?"
        ],
        "prompt": "Где в работе и деньгах ты ищешь стабильности, а где перемен? Как это влияет на решения?"
    },
    
    # A5 — Control Orientation → Relationships
    {
        "id": "bridge-a5-control-relationships",
        "title": "Мост: контроль → отношения",
        "description": "Как твоё стремление к контролю или адаптации влияет на отношения.",
        "category": "emotional",
        "practice_type": "domain_bridge",
        "duration_minutes": 5,
        "difficulty": "intermediate",
        "is_free": False,
        "access_level": "pro",
        "source_domain": "emotional",
        "target_domain": "relationships",
        "target_axis": "A5",
        "tags": ["мост", "контроль", "адаптация", "отношения"],
        "instructions": [
            "Вспомни последнюю ситуацию в отношениях",
            "Где ты пытался контролировать?",
            "Где ты адаптировался?",
            "Как это повлияло на отношения?"
        ],
        "prompt": "Где в отношениях ты пытаешься контролировать? Как это влияет на близость?"
    },
    
    # A5 — Control Orientation → Money/Work
    {
        "id": "bridge-a5-control-work",
        "title": "Мост: контроль → работа/деньги",
        "description": "Как твоё стремление к контролю или адаптации влияет на решения о работе и деньгах.",
        "category": "focus",
        "practice_type": "domain_bridge",
        "duration_minutes": 5,
        "difficulty": "intermediate",
        "is_free": False,
        "access_level": "pro",
        "source_domain": "emotional",
        "target_domain": "money",
        "target_axis": "A5",
        "tags": ["мост", "контроль", "адаптация", "работа", "деньги"],
        "instructions": [
            "Вспомни последнее решение о работе или деньгах",
            "Где ты пытался контролировать?",
            "Где ты адаптировался?",
            "Как это повлияло на решение?"
        ],
        "prompt": "Где в работе и деньгах ты пытаешься контролировать? Как это влияет на решения?"
    },
    
    # A6 — Relational Orientation → Relationships
    {
        "id": "bridge-a6-relationships-close",
        "title": "Мост: автономия/близость → отношения",
        "description": "Как твоя ориентация на автономию или связь влияет на отношения.",
        "category": "emotional",
        "practice_type": "domain_bridge",
        "duration_minutes": 5,
        "difficulty": "intermediate",
        "is_free": False,
        "access_level": "pro",
        "source_domain": "emotional",
        "target_domain": "relationships",
        "target_axis": "A6",
        "tags": ["мост", "отношения", "автономия", "близость"],
        "instructions": [
            "Вспомни последнюю ситуацию в отношениях",
            "Что было важнее: автономия или связь?",
            "Как это повлияло на контакт?"
        ],
        "prompt": "Где в отношениях тебе важнее автономия, а где связь? Как это влияет на близость?"
    },
    
    # A6 — Relational Orientation → Money/Work
    {
        "id": "bridge-a6-relationships-work",
        "title": "Мост: отношения → работа/деньги",
        "description": "Как твоя ориентация на автономию или связь влияет на решения о работе и деньгах.",
        "category": "focus",
        "practice_type": "domain_bridge",
        "duration_minutes": 5,
        "difficulty": "intermediate",
        "is_free": False,
        "access_level": "pro",
        "source_domain": "emotional",
        "target_domain": "money",
        "target_axis": "A6",
        "tags": ["мост", "отношения", "автономия", "близость", "работа", "деньги"],
        "instructions": [
            "Вспомни последнее решение о работе или деньгах",
            "Что было важнее: автономия или связь?",
            "Как это повлияло на решение?"
        ],
        "prompt": "Где в работе и деньгах тебе важнее автономия, а где связь? Как это влияет на решения?"
    },
    
    # A7 — Energy Management → Relationships
    {
        "id": "bridge-a7-energy-relationships",
        "title": "Мост: энергия → отношения",
        "description": "Как твоё управление энергией (экономно или широко) влияет на отношения.",
        "category": "emotional",
        "practice_type": "domain_bridge",
        "duration_minutes": 5,
        "difficulty": "intermediate",
        "is_free": False,
        "access_level": "pro",
        "source_domain": "emotional",
        "target_domain": "relationships",
        "target_axis": "A7",
        "tags": ["мост", "энергия", "усталость", "отношения"],
        "instructions": [
            "Вспомни последнюю ситуацию в отношениях",
            "Как ты расходовал энергию: экономно или широко?",
            "Как это повлияло на отношения?"
        ],
        "prompt": "Где в отношениях ты расходуешь энергию широко? Как это влияет на близость и усталость?"
    },
    
    # A7 — Energy Management → Money/Work
    {
        "id": "bridge-a7-energy-work",
        "title": "Мост: энергия → работа/деньги",
        "description": "Как твоё управление энергией (экономно или широко) влияет на решения о работе и деньгах.",
        "category": "focus",
        "practice_type": "domain_bridge",
        "duration_minutes": 5,
        "difficulty": "intermediate",
        "is_free": False,
        "access_level": "pro",
        "source_domain": "emotional",
        "target_domain": "money",
        "target_axis": "A7",
        "tags": ["мост", "энергия", "усталость", "работа", "деньги"],
        "instructions": [
            "Вспомни последнее решение о работе или деньгах",
            "Как ты расходовал энергию: экономно или широко?",
            "Как это повлияло на решение?"
        ],
        "prompt": "Где в работе и деньгах ты расходуешь энергию широко? Как это влияет на решения и усталость?"
    },
    
    # ========== AWARENESS CHECK PRACTICES (Complete sets for all axes) ==========
    
    # A1 — Identity Orientation (Inner-driven ←→ Outer-driven)
    {
        "id": "awareness-a1-identity-source",
        "title": "Откуда я черпаю чувство себя",
        "description": "Обрати внимание сегодня, откуда ты черпаешь чувство себя: изнутри или извне.",
        "category": "meditation",
        "practice_type": "awareness_check",
        "duration_minutes": 2,
        "difficulty": "beginner",
        "is_free": False,
        "access_level": "lite",
        "target_axis": "A1",
        "pattern_type": "observation",
        "tags": ["наблюдение", "идентичность", "daily hook"],
        "prompt": "Сегодня обрати внимание, откуда ты черпаешь чувство себя: из внутреннего ощущения или из внешнего подтверждения? Просто замечай, без оценки."
    },
    
    # A3 — Decision Making (Intuitive ←→ Analytical) - уже есть, но улучшим
    {
        "id": "awareness-a3-decision-process",
        "title": "Как я принимаю решения",
        "description": "Обрати внимание сегодня, как ты принимаешь решения: что происходит первым — интуиция или анализ?",
        "category": "focus",
        "practice_type": "awareness_check",
        "duration_minutes": 2,
        "difficulty": "beginner",
        "is_free": False,
        "access_level": "lite",
        "target_axis": "A3",
        "pattern_type": "observation",
        "tags": ["наблюдение", "решения", "daily hook"],
        "prompt": "Обрати внимание сегодня, как ты принимаешь решения. Что происходит первым: интуиция или анализ? Просто замечай свой процесс."
    },
    
    # A4 — Stability vs Change (Stability-seeking ←→ Change-seeking)
    {
        "id": "awareness-a4-stability-change",
        "title": "Что я ищу: стабильность или перемены",
        "description": "Обрати внимание сегодня, что ты ищешь: предсказуемость и стабильность или перемены и новизну.",
        "category": "reflection",
        "practice_type": "awareness_check",
        "duration_minutes": 2,
        "difficulty": "beginner",
        "is_free": False,
        "access_level": "lite",
        "target_axis": "A4",
        "pattern_type": "observation",
        "tags": ["наблюдение", "стабильность", "перемены", "daily hook"],
        "prompt": "Сегодня обрати внимание, что ты ищешь: предсказуемость и стабильность или перемены и новизну? Замечай свои реакции на рутину и новое."
    },
    
    # A5 — Control Orientation (Adaptive ←→ Directive) - уже есть, но улучшим
    {
        "id": "awareness-a5-control-tendency",
        "title": "Где я пытаюсь контролировать",
        "description": "Обрати внимание сегодня, где ты пытаешься контролировать ситуацию или других людей.",
        "category": "breathing",
        "practice_type": "awareness_check",
        "duration_minutes": 2,
        "difficulty": "beginner",
        "is_free": False,
        "access_level": "lite",
        "target_axis": "A5",
        "pattern_type": "observation",
        "tags": ["наблюдение", "контроль", "daily hook"],
        "prompt": "Обрати внимание сегодня, где ты пытаешься контролировать ситуацию или других людей. Замечай это без осуждения."
    },
    
    # A6 — Relational Orientation (Independent ←→ Bond-oriented)
    {
        "id": "awareness-a6-relational-need",
        "title": "Что важнее: автономия или связь",
        "description": "Обрати внимание сегодня, что для тебя важнее в отношениях: автономия и независимость или связь и близость.",
        "category": "emotional",
        "practice_type": "awareness_check",
        "duration_minutes": 2,
        "difficulty": "beginner",
        "is_free": False,
        "access_level": "lite",
        "target_axis": "A6",
        "pattern_type": "observation",
        "tags": ["наблюдение", "отношения", "автономия", "близость", "daily hook"],
        "prompt": "Сегодня обрати внимание, что для тебя важнее в отношениях: автономия и независимость или связь и близость? Замечай свои реакции на близость и дистанцию."
    },
    
    # A7 — Energy Management (Conservative ←→ Expansive)
    {
        "id": "awareness-a7-energy-use",
        "title": "Как я расходую энергию",
        "description": "Обрати внимание сегодня, как ты расходуешь энергию: осторожно и экономно или широко и интенсивно.",
        "category": "focus",
        "practice_type": "awareness_check",
        "duration_minutes": 2,
        "difficulty": "beginner",
        "is_free": False,
        "access_level": "lite",
        "target_axis": "A7",
        "pattern_type": "observation",
        "tags": ["наблюдение", "энергия", "усталость", "daily hook"],
        "prompt": "Сегодня обрати внимание, как ты расходуешь энергию: осторожно и экономно или широко и интенсивно? Замечай моменты усталости и подъёма."
    },
    
    # ========== MICRO DAILY PRACTICES (Complete sets for all axes) ==========
    
    # A1 — Identity Orientation
    {
        "id": "micro-a1-inner-check",
        "title": "Момент внутренней опоры",
        "description": "В течение дня найди один момент, когда ты можешь опереться на внутреннее чувство себя, не ища внешнего подтверждения.",
        "category": "meditation",
        "practice_type": "micro_daily",
        "duration_minutes": 2,
        "difficulty": "beginner",
        "is_free": False,
        "access_level": "lite",
        "target_axis": "A1",
        "pattern_type": "action",
        "tags": ["микро-действие", "идентичность", "привычка"],
        "instructions": [
            "В течение дня найди один момент, когда ты ищешь внешнего подтверждения",
            "Остановись на 30 секунд",
            "Спроси себя: что я чувствую внутри, без внешней оценки?",
            "Дай этому внутреннему чувству быть достаточным"
        ]
    },
    
    # A3 — Decision Making
    {
        "id": "micro-a3-decision-pause",
        "title": "Пауза перед решением",
        "description": "Перед следующим решением сделай паузу и заметь, что происходит: интуиция или анализ.",
        "category": "focus",
        "practice_type": "micro_daily",
        "duration_minutes": 2,
        "difficulty": "beginner",
        "is_free": False,
        "access_level": "lite",
        "target_axis": "A3",
        "pattern_type": "action",
        "tags": ["микро-действие", "решения", "привычка"],
        "instructions": [
            "Перед следующим решением (даже маленьким) сделай паузу на 10 секунд",
            "Заметь, что происходит первым: интуитивное ощущение или анализ вариантов",
            "Не нужно менять процесс, просто заметь",
            "Прими решение как обычно"
        ]
    },
    
    # A4 — Stability vs Change
    {
        "id": "micro-a4-small-change",
        "title": "Одно маленькое изменение",
        "description": "Если ты ищешь стабильности — попробуй одно маленькое изменение. Если ищешь перемен — создай одну точку стабильности.",
        "category": "focus",
        "practice_type": "micro_daily",
        "duration_minutes": 2,
        "difficulty": "beginner",
        "is_free": False,
        "access_level": "lite",
        "target_axis": "A4",
        "pattern_type": "action",
        "tags": ["микро-действие", "стабильность", "перемены", "привычка"],
        "instructions": [
            "Если ты ищешь стабильности — попробуй одно маленькое изменение (другой маршрут, другой порядок действий)",
            "Если ищешь перемен — создай одну точку стабильности (ритуал, повторяющееся действие)",
            "Заметь, что изменилось в ощущении"
        ]
    },
    
    # A5 — Control Orientation
    {
        "id": "micro-a5-release-control",
        "title": "Отпустить контроль на 5 минут",
        "description": "Выбери одну ситуацию, которую ты пытаешься контролировать, и отпусти контроль на 5 минут.",
        "category": "breathing",
        "practice_type": "micro_daily",
        "duration_minutes": 2,
        "difficulty": "beginner",
        "is_free": False,
        "access_level": "lite",
        "target_axis": "A5",
        "pattern_type": "action",
        "tags": ["микро-действие", "контроль", "привычка"],
        "instructions": [
            "Выбери одну ситуацию, которую ты пытаешься контролировать",
            "Отпусти контроль на 5 минут",
            "Просто наблюдай, что происходит",
            "Заметь, что изменилось"
        ]
    },
    
    # A6 — Relational Orientation
    {
        "id": "micro-a6-connection-moment",
        "title": "Момент связи или автономии",
        "description": "Если ты ищешь автономии — создай один момент связи. Если ищешь связи — дай себе один момент автономии.",
        "category": "emotional",
        "practice_type": "micro_daily",
        "duration_minutes": 2,
        "difficulty": "beginner",
        "is_free": False,
        "access_level": "lite",
        "target_axis": "A6",
        "pattern_type": "action",
        "tags": ["микро-действие", "отношения", "автономия", "близость", "привычка"],
        "instructions": [
            "Если ты ищешь автономии — создай один момент связи (короткий разговор, сообщение)",
            "Если ищешь связи — дай себе один момент автономии (время наедине с собой)",
            "Заметь, что изменилось в ощущении"
        ]
    },
    
    # A7 — Energy Management
    {
        "id": "micro-a7-energy-check",
        "title": "Проверка энергии",
        "description": "В течение дня трижды остановись и проверь свой уровень энергии: сколько осталось, как ты его используешь.",
        "category": "focus",
        "practice_type": "micro_daily",
        "duration_minutes": 2,
        "difficulty": "beginner",
        "is_free": False,
        "access_level": "lite",
        "target_axis": "A7",
        "pattern_type": "action",
        "tags": ["микро-действие", "энергия", "усталость", "привычка"],
        "instructions": [
            "В течение дня трижды остановись (утром, днём, вечером)",
            "Проверь свой уровень энергии по шкале от 1 до 10",
            "Заметь, как ты его используешь: экономно или широко",
            "Не нужно менять, просто заметь"
        ]
    },
    
    # ========== WEEKLY REFLECTION (Complete sets for all axes) ==========
    
    # A1 — Identity Orientation
    {
        "id": "weekly-reflection-a1-identity",
        "title": "Еженедельная рефлексия: откуда я черпаю себя",
        "description": "3 вопроса о том, откуда ты черпаешь чувство себя: изнутри или извне.",
        "category": "reflection",
        "practice_type": "weekly_reflection",
        "duration_minutes": 5,
        "difficulty": "beginner",
        "is_free": False,
        "access_level": "lite",
        "target_axis": "A1",
        "cycle_type": "weekly",
        "tags": ["рефлексия", "неделя", "идентичность", "weekly anchor"],
        "questions": [
            "Где на этой неделе я искал внешнего подтверждения?",
            "Где я опирался на внутреннее чувство себя?",
            "Что помогло бы мне больше опираться на внутреннее?"
        ],
        "instructions": [
            "Выдели 5 минут в спокойной обстановке",
            "Ответь на 3 вопроса письменно или мысленно",
            "Без оценки, просто наблюдение и понимание"
        ]
    },
    
    # A3 — Decision Making
    {
        "id": "weekly-reflection-a3-decisions",
        "title": "Еженедельная рефлексия: как я принимаю решения",
        "description": "3 вопроса о том, как ты принимаешь решения: интуиция или анализ.",
        "category": "reflection",
        "practice_type": "weekly_reflection",
        "duration_minutes": 5,
        "difficulty": "beginner",
        "is_free": False,
        "access_level": "lite",
        "target_axis": "A3",
        "cycle_type": "weekly",
        "tags": ["рефлексия", "неделя", "решения", "weekly anchor"],
        "questions": [
            "Какие решения я принял на этой неделе?",
            "Что происходило первым: интуиция или анализ?",
            "Что помогло бы мне принимать решения более эффективно?"
        ],
        "instructions": [
            "Выдели 5 минут в спокойной обстановке",
            "Ответь на 3 вопроса письменно или мысленно",
            "Без оценки, просто наблюдение и понимание"
        ]
    },
    
    # A4 — Stability vs Change
    {
        "id": "weekly-reflection-a4-stability-change",
        "title": "Еженедельная рефлексия: стабильность и перемены",
        "description": "3 вопроса о том, что ты ищешь: стабильность или перемены.",
        "category": "reflection",
        "practice_type": "weekly_reflection",
        "duration_minutes": 5,
        "difficulty": "beginner",
        "is_free": False,
        "access_level": "lite",
        "target_axis": "A4",
        "cycle_type": "weekly",
        "tags": ["рефлексия", "неделя", "стабильность", "перемены", "weekly anchor"],
        "questions": [
            "Где на этой неделе я искал стабильности?",
            "Где я искал перемен?",
            "Что помогло бы мне найти баланс между стабильностью и переменами?"
        ],
        "instructions": [
            "Выдели 5 минут в спокойной обстановке",
            "Ответь на 3 вопроса письменно или мысленно",
            "Без оценки, просто наблюдение и понимание"
        ]
    },
    
    # A5 — Control Orientation
    {
        "id": "weekly-reflection-a5-control",
        "title": "Еженедельная рефлексия: контроль и адаптация",
        "description": "3 вопроса о том, где ты пытаешься контролировать и где адаптируешься.",
        "category": "reflection",
        "practice_type": "weekly_reflection",
        "duration_minutes": 5,
        "difficulty": "beginner",
        "is_free": False,
        "access_level": "lite",
        "target_axis": "A5",
        "cycle_type": "weekly",
        "tags": ["рефлексия", "неделя", "контроль", "адаптация", "weekly anchor"],
        "questions": [
            "Где на этой неделе я пытался контролировать ситуацию?",
            "Где я адаптировался и следовал за ситуацией?",
            "Что помогло бы мне больше адаптироваться вместо контроля?"
        ],
        "instructions": [
            "Выдели 5 минут в спокойной обстановке",
            "Ответь на 3 вопроса письменно или мысленно",
            "Без оценки, просто наблюдение и понимание"
        ]
    },
    
    # A6 — Relational Orientation
    {
        "id": "weekly-reflection-a6-relationships",
        "title": "Еженедельная рефлексия: автономия и связь",
        "description": "3 вопроса о том, что для тебя важнее в отношениях: автономия или связь.",
        "category": "reflection",
        "practice_type": "weekly_reflection",
        "duration_minutes": 5,
        "difficulty": "beginner",
        "is_free": False,
        "access_level": "lite",
        "target_axis": "A6",
        "cycle_type": "weekly",
        "tags": ["рефлексия", "неделя", "отношения", "автономия", "близость", "weekly anchor"],
        "questions": [
            "Где на этой неделе мне нужна была автономия?",
            "Где мне нужна была связь и близость?",
            "Что помогло бы мне найти баланс между автономией и близостью?"
        ],
        "instructions": [
            "Выдели 5 минут в спокойной обстановке",
            "Ответь на 3 вопроса письменно или мысленно",
            "Без оценки, просто наблюдение и понимание"
        ]
    },
    
    # A7 — Energy Management
    {
        "id": "weekly-reflection-a7-energy",
        "title": "Еженедельная рефлексия: управление энергией",
        "description": "3 вопроса о том, как ты расходуешь энергию: экономно или широко.",
        "category": "reflection",
        "practice_type": "weekly_reflection",
        "duration_minutes": 5,
        "difficulty": "beginner",
        "is_free": False,
        "access_level": "lite",
        "target_axis": "A7",
        "cycle_type": "weekly",
        "tags": ["рефлексия", "неделя", "энергия", "усталость", "weekly anchor"],
        "questions": [
            "Как я расходовал энергию на этой неделе: экономно или широко?",
            "Где я чувствовал усталость или перегрузку?",
            "Что помогло бы мне лучше управлять энергией?"
        ],
        "instructions": [
            "Выдели 5 минут в спокойной обстановке",
            "Ответь на 3 вопроса письменно или мысленно",
            "Без оценки, просто наблюдение и понимание"
        ]
    },
    
    # Общая рефлексия (уже есть, оставляем)
    {
        "id": "weekly-reflection-patterns",
        "title": "Еженедельная рефлексия: твои паттерны",
        "description": "3 вопроса для размышления о своих паттернах за неделю",
        "category": "reflection",
        "practice_type": "weekly_reflection",
        "duration_minutes": 10,
        "difficulty": "intermediate",
        "is_free": False,
        "access_level": "lite",
        "cycle_type": "weekly",
        "tags": ["рефлексия", "неделя", "паттерны"],
        "questions": [
            "Какие паттерны я заметил в себе на этой неделе?",
            "Что помогало мне справляться с трудностями?",
            "Что я хочу изменить или развить на следующей неделе?"
        ],
        "instructions": [
            "Выдели 10 минут в спокойной обстановке",
            "Ответь на 3 вопроса письменно или мысленно",
            "Без оценки, просто наблюдение и понимание"
        ]
    },
    
    # ========== GUIDED SEQUENCES ==========
    {
        "id": "sequence-emotional-awareness-week",
        "title": "Неделя осознанности эмоций",
        "description": "7-дневная серия практик для развития эмоциональной осознанности",
        "category": "emotional",
        "practice_type": "guided_sequence",
        "duration_minutes": None,
        "difficulty": "intermediate",
        "is_free": False,
        "access_level": "lite",
        "sequence_id": "emotional-awareness-week",
        "step_number": None,
        "total_steps": 7,
        "target_axis": "A2",
        "tags": ["серия", "эмоции", "неделя"],
        "instructions": [
            "Эта серия состоит из 7 практик, по одной на каждый день",
            "Каждый день ты будешь получать новую практику",
            "Выполняй их последовательно для максимального эффекта"
        ],
        "steps": [
            {
                "step_number": 1,
                "title": "День 1: Наблюдение за эмоциями",
                "description": "Замечай свои эмоции в течение дня без оценки",
                "duration_minutes": 5,
                "instructions": [
                    "В течение дня замечай, когда возникает эмоция",
                    "Просто отметь её: 'Я чувствую...'",
                    "Не пытайся изменить или оценить"
                ]
            },
            {
                "step_number": 2,
                "title": "День 2: Пауза перед реакцией",
                "description": "Создавай паузу между эмоцией и реакцией",
                "duration_minutes": 3,
                "instructions": [
                    "Когда возникает эмоция, сделай паузу",
                    "Сделай 3 глубоких вдоха",
                    "Только потом реагируй"
                ]
            },
            {
                "step_number": 3,
                "title": "День 3: Именование эмоций",
                "description": "Учись точно называть свои эмоции",
                "duration_minutes": 5,
                "instructions": [
                    "Когда чувствуешь эмоцию, попробуй назвать её точно",
                    "Не просто 'плохо' или 'хорошо'",
                    "Попробуй: 'тревога', 'радость', 'раздражение', 'спокойствие'"
                ]
            },
            {
                "step_number": 4,
                "title": "День 4: Телесные ощущения",
                "description": "Замечай, где в теле живут эмоции",
                "duration_minutes": 5,
                "instructions": [
                    "Когда возникает эмоция, обрати внимание на тело",
                    "Где ты её чувствуешь? В груди? В животе? В горле?",
                    "Просто наблюдай без оценки"
                ]
            },
            {
                "step_number": 5,
                "title": "День 5: Принятие эмоций",
                "description": "Практика принятия эмоций без сопротивления",
                "duration_minutes": 7,
                "instructions": [
                    "Когда возникает эмоция, попробуй не сопротивляться",
                    "Скажи себе: 'Это нормально чувствовать это'",
                    "Дай эмоции быть, не пытайся её изменить"
                ]
            },
            {
                "step_number": 6,
                "title": "День 6: Выражение эмоций",
                "description": "Найди безопасный способ выразить эмоцию",
                "duration_minutes": 10,
                "instructions": [
                    "Выбери одну эмоцию дня",
                    "Найди способ её выразить: написать, сказать, нарисовать",
                    "Вырази её безопасно и честно"
                ]
            },
            {
                "step_number": 7,
                "title": "День 7: Интеграция",
                "description": "Рефлексия о неделе эмоциональной осознанности",
                "duration_minutes": 10,
                "instructions": [
                    "Вспомни всю неделю",
                    "Что ты заметил о своих эмоциях?",
                    "Что изменилось? Что осталось прежним?"
                ],
                "questions": [
                    "Что я узнал о своих эмоциях за эту неделю?",
                    "Какая практика была самой полезной?",
                    "Что я хочу продолжить делать?"
                ]
            }
        ]
    },
    {
        "id": "sequence-control-release-week",
        "title": "Неделя отпускания контроля",
        "description": "7-дневная серия для работы с паттерном контроля",
        "category": "breathing",
        "practice_type": "guided_sequence",
        "duration_minutes": None,
        "difficulty": "intermediate",
        "is_free": False,
        "access_level": "lite",
        "sequence_id": "control-release-week",
        "step_number": None,
        "total_steps": 7,
        "target_axis": "A5",
        "tags": ["серия", "контроль", "неделя"],
        "instructions": [
            "Эта серия поможет тебе работать с паттерном контроля",
            "Каждый день новая практика для постепенного отпускания"
        ],
        "steps": [
            {
                "step_number": 1,
                "title": "День 1: Замечание контроля",
                "description": "Замечай, где ты пытаешься контролировать",
                "duration_minutes": 5,
                "instructions": [
                    "В течение дня замечай моменты контроля",
                    "Контроль ситуаций, людей, себя",
                    "Просто отмечай без осуждения"
                ]
            },
            {
                "step_number": 2,
                "title": "День 2: Одна вещь без контроля",
                "description": "Выбери одну вещь и не контролируй её сегодня",
                "duration_minutes": 3,
                "instructions": [
                    "Выбери одну небольшую вещь",
                    "Сегодня не контролируй её",
                    "Позволь ей быть такой, какая она есть"
                ]
            },
            {
                "step_number": 3,
                "title": "День 3: Дыхание вместо контроля",
                "description": "Когда чувствуешь желание контролировать, дыши",
                "duration_minutes": 5,
                "instructions": [
                    "Когда возникает желание контролировать",
                    "Остановись и сделай 5 глубоких вдохов",
                    "Дай себе пространство"
                ]
            },
            {
                "step_number": 4,
                "title": "День 4: Адаптация вместо контроля",
                "description": "Попробуй адаптироваться вместо контроля",
                "duration_minutes": 5,
                "instructions": [
                    "Вместо попытки контролировать ситуацию",
                    "Попробуй адаптироваться к ней",
                    "Что произойдет, если ты просто последуешь?"
                ]
            },
            {
                "step_number": 5,
                "title": "День 5: Доверие процессу",
                "description": "Практика доверия естественному процессу",
                "duration_minutes": 7,
                "instructions": [
                    "Выбери одну ситуацию",
                    "Попробуй довериться естественному процессу",
                    "Не вмешивайся, просто наблюдай"
                ]
            },
            {
                "step_number": 6,
                "title": "День 6: Отпускание результата",
                "description": "Практика отпускания контроля результата",
                "duration_minutes": 5,
                "instructions": [
                    "Сделай что-то, не контролируя результат",
                    "Сделай всё, что можешь, и отпусти",
                    "Дай результату быть таким, каким он будет"
                ]
            },
            {
                "step_number": 7,
                "title": "День 7: Рефлексия",
                "description": "Размышление о неделе отпускания контроля",
                "duration_minutes": 10,
                "instructions": [
                    "Вспомни всю неделю",
                    "Где тебе было легко отпускать контроль?",
                    "Где было сложно? Что ты узнал?"
                ],
                "questions": [
                    "Что я узнал о своём паттерне контроля?",
                    "Какие ситуации были самыми сложными?",
                    "Что я хочу продолжать практиковать?"
                ]
            }
        ]
    }
]


def get_week_start(target_date: date = None) -> date:
    """
    Получить начало недели (понедельник) для указанной даты.
    Если дата не указана, используется сегодняшняя дата.
    """
    if target_date is None:
        target_date = date.today()
    
    # Понедельник = 0, воскресенье = 6
    days_since_monday = target_date.weekday()
    week_start = target_date - timedelta(days=days_since_monday)
    return week_start


def count_personalized_practices_this_week(user: User, db: Session, week_start: date = None) -> int:
    """
    Подсчитать количество персонализированных практик, использованных пользователем на текущей неделе.
    """
    if week_start is None:
        week_start = get_week_start()
    
    week_end = week_start + timedelta(days=6)
    
    count = db.query(func.count(PracticeUsage.id)).filter(
        PracticeUsage.user_id == user.id,
        PracticeUsage.is_personalized == True,
        PracticeUsage.week_start == week_start
    ).scalar()
    
    return count or 0


def get_practice_limits(user: User, db: Session) -> dict:
    """
    Получить информацию о лимитах практик для пользователя.
    """
    subscription_level = get_subscription_level(user, db)
    week_start = get_week_start()
    used_this_week = count_personalized_practices_this_week(user, db, week_start)
    
    # Определяем лимиты по подписке
    limits = {
        "free": 1,   # 1 персонализированная практика в неделю
        "lite": 4,   # 4 персонализированные практики в неделю
        "pro": 9999  # Неограниченно (большое число для простоты)
    }
    
    personalized_limit = limits.get(subscription_level, 1)
    remaining = max(0, personalized_limit - used_this_week)
    
    return {
        "subscription_level": subscription_level,
        "personalized_limit": personalized_limit,
        "used_this_week": used_this_week,
        "remaining_this_week": remaining,
        "week_start": week_start
    }


@router.get("/limits", response_model=PracticeLimitsResponse)
async def get_practice_limits_endpoint(
    user: User = Depends(require_user),
    db: Session = Depends(get_session),
):
    """
    Получить информацию о лимитах практик для текущего пользователя.
    """
    
    limits = get_practice_limits(user, db)
    return PracticeLimitsResponse(**limits)


@router.post("/{practice_id}/complete", response_model=PracticeUsageResponse)
async def complete_practice(
    practice_id: str,
    user: User = Depends(require_user),
    db: Session = Depends(get_session),
):
    """
    Отметить практику как выполненную.
    Автоматически отслеживает использование для контроля лимитов.
    """
    
    # Проверяем, существует ли практика
    practice = next((p for p in GENERAL_PRACTICES if p["id"] == practice_id), None)
    if not practice:
        raise HTTPException(status_code=404, detail="Practice not found")
    
    # Определяем, была ли практика персонализированной
    # Для этого нужно проверить, была ли она рекомендована как персонализированная
    # Пока используем простую логику: если практика не free, считаем её персонализированной
    is_personalized = practice.get("is_personalized", False) or practice.get("access_level") != "free"
    
    # Если практика персонализированная, проверяем лимиты
    if is_personalized:
        limits = get_practice_limits(user, db)
        if limits["remaining_this_week"] <= 0:
            raise HTTPException(
                status_code=403,
                detail=f"Достигнут лимит персонализированных практик на эту неделю ({limits['personalized_limit']}). Обновите подписку для большего количества практик."
            )
    
    # Создаем запись об использовании
    week_start = get_week_start()
    usage = PracticeUsage(
        user_id=user.id,
        practice_id=practice_id,
        completed_at=datetime.utcnow(),
        week_start=week_start,
        is_personalized=is_personalized
    )
    
    db.add(usage)
    db.commit()
    db.refresh(usage)
    
    return PracticeUsageResponse(
        practice_id=practice_id,
        completed_at=usage.completed_at
    )


@router.get("/current", response_model=PracticeResponse)
async def get_current_practice(
    request: FastAPIRequest,
    user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_session),
):
    """
    Получить главную практику для текущего момента.
    Один момент → одна практика.
    Для auth - персонализированная на основе паттерна и дня.
    Для guest - общая практика.
    """
    from todayflow_backend.services.lite_reports import LiteReportService
    from datetime import date
    
    locale = request_locale(request)
    
    if user:
        # Персонализированная практика для auth пользователя
        try:
            lite_service = LiteReportService()
            lite_report = lite_service._get_latest_report(user)
            
            if lite_report and lite_report.internal_model:
                axes = lite_report.internal_model.axes or []
                if axes:
                    # Выбираем доминирующую ось
                    dominant_axis = sorted(axes, key=lambda x: abs(x.value), reverse=True)[0]
                    
                    # Определяем день пользователя (отсчет от регистрации)
                    today = date.today()
                    registration_date = user.created_at.date() if user.created_at else today
                    diff_days = (today - registration_date).days + 1
                    user_day = min(max(diff_days, 1), 7)  # Ограничиваем 1-7 днями
                    
                    # Выбираем практику для дня и паттерна
                    all_practices = GENERAL_PRACTICES + PERSONALIZED_PRACTICES
                    practice = select_practice_for_day(user_day, dominant_axis.axis_id, all_practices, user)
                    
                    if practice:
                        practice_copy = practice.copy()
                        practice_copy["is_personalized"] = True
                        practice_copy["personalized_reason"] = f"Рекомендовано на основе твоего паттерна {dominant_axis.axis_id} и сегодняшнего фокуса"
                        practice_copy["target_axis"] = dominant_axis.axis_id
                        return practice_copy
            
            # Fallback: общая практика
            general_practice = GENERAL_PRACTICES[0].copy() if GENERAL_PRACTICES else None
            if general_practice:
                general_practice["is_personalized"] = False
                return general_practice
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"Error getting personalized practice: {e}")
    
    # Для guest или если не удалось получить персонализированную
    general_practice = GENERAL_PRACTICES[0].copy() if GENERAL_PRACTICES else None
    if general_practice:
        general_practice["is_personalized"] = False
        return general_practice
    
    raise HTTPException(status_code=404, detail=translate("practices.errors.notFound", locale=locale))


@router.get("/short-alternatives", response_model=List[PracticeResponse])
async def get_short_alternatives(
    request: FastAPIRequest,
    user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_session),
):
    """
    Получить 2-3 короткие альтернативные практики (fallback).
    """
    # Ищем короткие практики (micro_daily, до 5 минут)
    general_practices = [
        {**p, "is_personalized": False} for p in GENERAL_PRACTICES
        if p.get("practice_type") in ["micro_daily", "awareness_check"]
        and (p.get("duration_minutes") is None or p.get("duration_minutes", 0) <= 5)
    ]
    
    personalized_practices = [
        {**p, "is_personalized": True} for p in (PERSONALIZED_PRACTICES if user else [])
        if p.get("practice_type") in ["micro_daily", "awareness_check"]
        and (p.get("duration_minutes") is None or p.get("duration_minutes", 0) <= 5)
    ]
    
    short_practices = general_practices + personalized_practices
    
    # Возвращаем максимум 3
    return short_practices[:3]


@router.get("", response_model=List[PracticeResponse])
@router.get("/", response_model=List[PracticeResponse])
async def get_practices(
    category: Optional[str] = None,
    limit: Optional[int] = None,
    user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_session),
):
    """
    Получить список практик (для архива/категорий).
    Для гостей - общие практики.
    Для зарегистрированных - персонализированные рекомендации с учетом текущего периода и карты дня.
    """
    practices = []
    
    if user:
        # Проверяем лимиты для персонализированных практик
        limits = get_practice_limits(user, db)
        
        # Если лимит исчерпан, возвращаем только бесплатные практики
        if limits["remaining_this_week"] <= 0 and limits["subscription_level"] != "pro":
            practices = [p for p in GENERAL_PRACTICES.copy() if p.get("is_free", True)]
            if category:
                practices = [p for p in practices if p["category"] == category]
            if limit:
                practices = practices[:limit]
            return practices
        
        # Персонализированные практики для зарегистрированных пользователей
        practices = get_personalized_practices(user, db, category, limit, limits)
    else:
        # Общие практики для гостей
        practices = GENERAL_PRACTICES.copy()
        if category:
            practices = [p for p in practices if p["category"] == category]
        if limit:
            practices = practices[:limit]
    
    return practices


def select_pattern_for_day1(internal_model) -> Optional[dict]:
    """
    Выбрать паттерн для Day 1 (эталонный поток).
    Правило: паттерн с наибольшим абсолютным значением.
    Если несколько равны → выбираем A2 (Emotional Processing) как наиболее понятный.
    """
    if not internal_model or not internal_model.axes:
        return None
    
    # Находим паттерн с наибольшим абсолютным значением
    max_axis = max(internal_model.axes, key=lambda a: abs(a.value))
    
    axis_names = {
        "A1": "Ориентация идентичности",
        "A2": "Эмоциональная обработка",
        "A3": "Принятие решений",
        "A4": "Стабильность и изменения",
        "A5": "Ориентация контроля",
        "A6": "Реляционная ориентация",
        "A7": "Управление энергией",
    }
    
    return {
        "axis_id": max_axis.axis_id,
        "value": max_axis.value,
        "name": axis_names.get(max_axis.axis_id, max_axis.axis_id),
        "is_positive": max_axis.value > 0,
    }


def select_practice_for_day(
    day: int,
    pattern_axis_id: str,
    all_practices: List[dict],
    user: Optional[User] = None
) -> Optional[dict]:
    """
    Выбрать практику для конкретного дня согласно эталонному потоку.
    
    Day 1: awareness_check или micro_daily (purpose: awareness, entry_state: NEW)
    Day 2: pattern_based или micro_daily (purpose: action, entry_state: PATTERN_RECOGNIZED)
    Day 3: micro_daily или pattern_based (purpose: integration, entry_state: PATTERN_APPLIED)
    """
    # Фильтруем практики по паттерну
    pattern_practices = [
        p for p in all_practices
        if p.get("target_axis") == pattern_axis_id
    ]
    
    if not pattern_practices:
        return None
    
    if day == 1:
        # Day 1: awareness_check или micro_daily
        candidates = [
            p for p in pattern_practices
            if p.get("practice_type") in ["awareness_check", "micro_daily"]
            and p.get("pattern_type") == "observation"
        ]
        if not candidates:
            # Fallback: любая awareness_check или micro_daily
            candidates = [
                p for p in pattern_practices
                if p.get("practice_type") in ["awareness_check", "micro_daily"]
            ]
        if candidates:
            practice = candidates[0].copy()
            practice["purpose"] = "awareness"
            practice["entry_state"] = "NEW"
            practice["exit_state"] = "PATTERN_RECOGNIZED"
            return practice
    
    elif day == 2:
        # Day 2: pattern_based или micro_daily (action)
        candidates = [
            p for p in pattern_practices
            if p.get("practice_type") in ["pattern_based", "micro_daily"]
            and p.get("pattern_type") == "action"
        ]
        if not candidates:
            # Fallback: любая pattern_based или micro_daily
            candidates = [
                p for p in pattern_practices
                if p.get("practice_type") in ["pattern_based", "micro_daily"]
            ]
        if candidates:
            practice = candidates[0].copy()
            practice["purpose"] = "action"
            practice["entry_state"] = "PATTERN_RECOGNIZED"
            practice["exit_state"] = "PATTERN_APPLIED"
            return practice
    
    elif day == 3:
        # Day 3: micro_daily или pattern_based (integration)
        candidates = [
            p for p in pattern_practices
            if p.get("practice_type") in ["micro_daily", "pattern_based"]
            and p.get("pattern_type") == "action"
        ]
        if not candidates:
            # Fallback: любая micro_daily или pattern_based
            candidates = [
                p for p in pattern_practices
                if p.get("practice_type") in ["micro_daily", "pattern_based"]
            ]
        if candidates:
            practice = candidates[0].copy()
            practice["purpose"] = "integration"
            practice["entry_state"] = "PATTERN_APPLIED"
            practice["exit_state"] = "REAL_WORLD_EFFECT"
            return practice
    
    return None


def get_personalized_practices(
    user: User,
    db: Session,
    category: Optional[str] = None,
    limit: Optional[int] = None,
    limits: Optional[dict] = None
) -> List[dict]:
    """
    Получить персонализированные практики на основе данных пользователя.
    Использует Internal Model (оси и модуляторы), текущий период (лунные фазы) и карту дня для подбора практик.
    """
    from todayflow_backend.services.lite_reports import LiteReportService
    
    if limits is None:
        limits = get_practice_limits(user, db)
    
    # Начинаем с общих практик
    all_practices = GENERAL_PRACTICES.copy()
    personalized = []
    
    # Ограничиваем количество персонализированных практик в зависимости от лимита
    max_personalized = limits["remaining_this_week"] if limits["subscription_level"] != "pro" else None
    
    # Проверяем, нужна ли weekly reflection (раз в неделю, например, в понедельник)
    today = date.today()
    is_weekly_reflection_day = today.weekday() == 0  # Понедельник
    
    # Получаем lite report для доступа к Internal Model
    try:
        lite_service = LiteReportService()
        lite_report = lite_service._get_latest_report(user)
        
        if lite_report and lite_report.internal_model:
            axes = lite_report.internal_model.axes or []
            modulators = lite_report.internal_model.modulators or []
            
            # Определяем доминирующие оси и модуляторы
            dominant_axes = sorted(axes, key=lambda x: abs(x.value), reverse=True)[:3]
            dominant_modulators = sorted(modulators, key=lambda x: abs(x.value), reverse=True)[:2]
            
            # Получаем текущий период (лунные фазы)
            moon_phase = None
            try:
                from todayflow_backend.services.lunar import LunarService
                lunar_service = LunarService()
                moon_phase_response = lunar_service.current_phase()
                moon_phase = moon_phase_response.current_phase if moon_phase_response else None
            except Exception:
                pass
            
            # Получаем карту дня
            tarot_card = None
            try:
                from todayflow_backend.services.tarot import TarotService
                tarot_service = TarotService()
                tarot_draw = tarot_service.get_daily_draw(user)
                tarot_card = tarot_draw.card if tarot_draw else None
            except Exception:
                pass
            
            # Проверяем наличие Full Report для domain bridges
            has_full_report = False
            try:
                from todayflow_backend.services.full_reports import FullReportService
                full_service = FullReportService()
                full_report = full_service._get_latest_report(user)
                has_full_report = full_report is not None
            except Exception:
                pass
            
            selected_practices = []
            reasons_list = []
            
            # 1. Daily Hook - Микро-практика дня (всегда одна)
            micro_practices = [p for p in PERSONALIZED_PRACTICES if p.get("practice_type") == "micro_daily"]
            if micro_practices and (max_personalized is None or max_personalized > 0):
                # Выбираем случайную микро-практику
                import random
                selected_micro = random.choice(micro_practices)
                selected_micro = selected_micro.copy()
                selected_micro["is_personalized"] = True
                selected_micro["personalized_reason"] = "Микро-практика дня для формирования привычки"
                selected_practices.append(selected_micro)
                if max_personalized is not None:
                    max_personalized -= 1
            
            # 2. Awareness Check - Осознанное наблюдение (привязано к доминирующему паттерну)
            if dominant_axes and (max_personalized is None or max_personalized > 0):
                main_axis = dominant_axes[0]
                awareness_practices = [
                    p for p in PERSONALIZED_PRACTICES 
                    if p.get("practice_type") == "awareness_check" 
                    and p.get("target_axis") == main_axis.axis_id
                ]
                if awareness_practices:
                    selected_awareness = awareness_practices[0].copy()
                    selected_awareness["is_personalized"] = True
                    axis_name = {
                        "A1": "ориентации идентичности",
                        "A2": "эмоциональной обработки",
                        "A3": "принятия решений",
                        "A4": "стабильности и изменений",
                        "A5": "контроля",
                        "A6": "отношений",
                        "A7": "управления энергией",
                    }.get(main_axis.axis_id, "паттернов")
                    selected_awareness["personalized_reason"] = f"Осознанное наблюдение для паттерна {axis_name}"
                    selected_practices.append(selected_awareness)
                    reasons_list.append(f"паттерн {axis_name}")
                    if max_personalized is not None:
                        max_personalized -= 1
            
            # 3. Pattern-based practices - Практики для конкретных паттернов (по 1 на каждый доминирующий паттерн)
            for axis in dominant_axes[:2]:  # Берем топ-2 паттерна
                if max_personalized is not None and max_personalized <= 0:
                    break
                
                # Ищем практики для этого паттерна (разные типы: observation, action, reflection)
                pattern_practices = [
                    p for p in PERSONALIZED_PRACTICES
                    if p.get("practice_type") == "pattern_based"
                    and p.get("target_axis") == axis.axis_id
                ]
                
                if pattern_practices:
                    # Выбираем одну практику (приоритет: observation > action > reflection)
                    for pattern_type in ["observation", "action", "reflection"]:
                        matching = [p for p in pattern_practices if p.get("pattern_type") == pattern_type]
                        if matching:
                            selected = matching[0].copy()
                            selected["is_personalized"] = True
                            axis_name = {
                                "A1": "ориентации идентичности",
                                "A2": "эмоциональной обработки",
                                "A3": "принятия решений",
                                "A4": "стабильности и изменений",
                                "A5": "контроля",
                                "A6": "отношений",
                                "A7": "управления энергией",
                            }.get(axis.axis_id, "паттернов")
                            selected["personalized_reason"] = f"Практика для паттерна {axis_name}"
                            selected_practices.append(selected)
                            if max_personalized is not None:
                                max_personalized -= 1
                            break
            
            # 4. Compensatory practices - Компенсаторные практики для напряженных паттернов
            # Находим паттерны с экстремальными значениями (близко к -100 или +100)
            stressed_patterns = [a for a in dominant_axes if abs(a.value) > 70]
            for pattern in stressed_patterns[:1]:  # Берем один самый напряженный
                if max_personalized is not None and max_personalized <= 0:
                    break
                
                compensatory_practices = [
                    p for p in PERSONALIZED_PRACTICES
                    if p.get("practice_type") == "compensatory"
                    and p.get("target_axis") == pattern.axis_id
                ]
                
                if compensatory_practices:
                    selected_comp = compensatory_practices[0].copy()
                    selected_comp["is_personalized"] = True
                    axis_name = {
                        "A1": "ориентации идентичности",
                        "A2": "эмоциональной обработки",
                        "A3": "принятия решений",
                        "A4": "стабильности и изменений",
                        "A5": "контроля",
                        "A6": "отношений",
                        "A7": "управления энергией",
                    }.get(pattern.axis_id, "паттернов")
                    selected_comp["personalized_reason"] = f"Компенсаторная практика для напряженного паттерна {axis_name}"
                    selected_practices.append(selected_comp)
                    if max_personalized is not None:
                        max_personalized -= 1
            
            # 5. Domain Bridges - Мосты между доменами (только для Pro с Full Report)
            if has_full_report and limits["subscription_level"] == "pro":
                bridge_practices = [
                    p for p in PERSONALIZED_PRACTICES
                    if p.get("practice_type") == "domain_bridge"
                ]
                if bridge_practices and (max_personalized is None or max_personalized > 0):
                    selected_bridge = bridge_practices[0].copy()
                    selected_bridge["is_personalized"] = True
                    selected_bridge["personalized_reason"] = "Практика-мост между доменами жизни"
                    selected_practices.append(selected_bridge)
                    if max_personalized is not None:
                        max_personalized -= 1
            
            # 6. Weekly Reflection - Еженедельная рефлексия (раз в неделю, в понедельник)
            if is_weekly_reflection_day and (max_personalized is None or max_personalized > 0):
                reflection_practices = [
                    p for p in PERSONALIZED_PRACTICES
                    if p.get("practice_type") == "weekly_reflection"
                ]
                if reflection_practices:
                    selected_reflection = reflection_practices[0].copy()
                    selected_reflection["is_personalized"] = True
                    selected_reflection["personalized_reason"] = "Еженедельная рефлексия о твоих паттернах"
                    selected_practices.append(selected_reflection)
                    if max_personalized is not None:
                        max_personalized -= 1
            
            # 7. Cycle-based practices - Практики на основе лунных фаз
            if moon_phase and (max_personalized is None or max_personalized > 0):
                cycle_practices = [
                    p for p in PERSONALIZED_PRACTICES
                    if p.get("practice_type") == "cycle_based"
                    and (p.get("trigger_phase") == moon_phase.id or p.get("trigger_phase") is None)
                ]
                if cycle_practices:
                    selected_cycle = cycle_practices[0].copy()
                    selected_cycle["is_personalized"] = True
                    selected_cycle["personalized_reason"] = f"Практика для текущей фазы луны ({moon_phase.name})"
                    selected_practices.append(selected_cycle)
                    if max_personalized is not None:
                        max_personalized -= 1
            
            # 8. Guided Sequences - Серии практик (рекомендуем только если пользователь еще не начал серию)
            # Проверяем, есть ли активные серии для доминирующих паттернов
            if dominant_axes and (max_personalized is None or max_personalized > 0):
                # Проверяем прогресс по существующим сериям
                active_sequences = db.query(PracticeUsage).filter(
                    PracticeUsage.user_id == user.id,
                    PracticeUsage.sequence_id.isnot(None)
                ).distinct(PracticeUsage.sequence_id).all()
                
                active_sequence_ids = {u.sequence_id for u in active_sequences if u.sequence_id}
                
                # Ищем серии для доминирующих паттернов, которые еще не начаты
                for axis in dominant_axes[:1]:  # Берем только топ-1 паттерн для серий
                    sequence_practices = [
                        p for p in PERSONALIZED_PRACTICES
                        if p.get("practice_type") == "guided_sequence"
                        and p.get("target_axis") == axis.axis_id
                        and p.get("sequence_id") not in active_sequence_ids
                    ]
                    
                    if sequence_practices:
                        selected_sequence = sequence_practices[0].copy()
                        selected_sequence["is_personalized"] = True
                        axis_name = {
                            "A1": "ориентации идентичности",
                            "A2": "эмоциональной обработки",
                            "A3": "принятия решений",
                            "A4": "стабильности и изменений",
                            "A5": "контроля",
                            "A6": "отношений",
                            "A7": "управления энергией",
                        }.get(axis.axis_id, "паттернов")
                        selected_sequence["personalized_reason"] = f"7-дневная серия для работы с паттерном {axis_name}"
                        selected_practices.append(selected_sequence)
                        if max_personalized is not None:
                            max_personalized -= 1
                        break  # Рекомендуем только одну серию за раз
            
            # Добавляем выбранные персонализированные практики
            personalized.extend(selected_practices)
            
            # Также добавляем общие практики с пометкой персонализации на основе категорий
            # (для обратной совместимости и дополнительных рекомендаций)
            axis_practices_map = {
                "A1": ["breathing", "meditation"],
                "A2": ["gratitude", "emotional"],
                "A3": ["focus", "meditation"],
                "A4": ["desires", "manifestation"],
                "A5": ["breathing", "focus"],
                "A6": ["gratitude", "emotional"],
                "A7": ["breathing", "meditation"],
            }
            
            recommended_categories = set()
            for axis in dominant_axes:
                if axis.axis_id in axis_practices_map:
                    recommended_categories.update(axis_practices_map[axis.axis_id])
            
            # Добавляем общие практики с пометкой персонализации
            for practice in all_practices:
                if practice["category"] in recommended_categories:
                    practice_copy = practice.copy()
                    practice_copy["is_personalized"] = True
                    if reasons_list:
                        practice_copy["personalized_reason"] = f"Сегодня тебе подойдёт на основе {', '.join(reasons_list[:2])}"
                    else:
                        practice_copy["personalized_reason"] = "Рекомендовано на основе ваших паттернов"
                    personalized.append(practice_copy)
                else:
                    practice_copy = practice.copy()
                    practice_copy["is_personalized"] = False
                    personalized.append(practice_copy)
            
            # Сортируем: персонализированные первыми
            personalized.sort(key=lambda x: (not x.get("is_personalized", False), x.get("title", "")))
        else:
            # Если нет Internal Model, добавляем только общие практики
            for practice in all_practices:
                practice_copy = practice.copy()
                practice_copy["is_personalized"] = False
                personalized.append(practice_copy)
    except Exception as e:
        # В случае ошибки возвращаем общие практики
        import logging
        logging.error(f"Error personalizing practices: {e}")
        for practice in all_practices:
            practice_copy = practice.copy()
            practice_copy["is_personalized"] = False
            personalized.append(practice_copy)
    
    if category:
        personalized = [p for p in personalized if p["category"] == category]
    if limit:
        personalized = personalized[:limit]
    
    return personalized


@router.get("/progress", response_model=PracticeProgressResponse)
async def get_practice_progress(
    user: User = Depends(require_user),
    db: Session = Depends(get_session),
):
    """
    Получить статистику прогресса по практикам.
    """
    # Получаем все практики для маппинга ID -> категория
    all_practices = {p["id"]: p for p in GENERAL_PRACTICES + PERSONALIZED_PRACTICES}
    
    # Все завершенные практики
    all_usages = db.query(PracticeUsage).filter(PracticeUsage.user_id == user.id).all()
    
    total_completed = len(all_usages)
    personalized_completed = sum(1 for u in all_usages if u.is_personalized)
    general_completed = total_completed - personalized_completed
    
    # Прогресс по категориям
    category_counts = {}
    for usage in all_usages:
        practice = all_practices.get(usage.practice_id, {})
        category = practice.get("category", "other")
        if category not in category_counts:
            category_counts[category] = {"total": 0, "personalized": 0}
        category_counts[category]["total"] += 1
        if usage.is_personalized:
            category_counts[category]["personalized"] += 1
    
    by_category = [
        CategoryProgress(
            category=cat,
            total_completed=counts["total"],
            personalized_completed=counts["personalized"],
        )
        for cat, counts in category_counts.items()
    ]
    by_category.sort(key=lambda x: x.total_completed, reverse=True)
    
    # Вычисляем серии дней (streaks)
    if all_usages:
        # Группируем по датам
        dates = sorted(set(u.completed_at.date() for u in all_usages), reverse=True)
        
        # Текущая серия
        current_streak = 0
        today = date.today()
        yesterday = today - timedelta(days=1)
        
        if dates and dates[0] == today:
            current_streak = 1
            for i in range(1, len(dates)):
                expected_date = today - timedelta(days=i)
                if dates[i] == expected_date:
                    current_streak += 1
                else:
                    break
        elif dates and dates[0] == yesterday:
            # Если последняя практика была вчера, проверяем цепочку
            current_streak = 1
            for i in range(1, len(dates)):
                expected_date = yesterday - timedelta(days=i)
                if dates[i] == expected_date:
                    current_streak += 1
                else:
                    break
        
        # Самая длинная серия
        longest_streak = 1
        if len(dates) > 1:
            streak = 1
            for i in range(1, len(dates)):
                if dates[i-1] - dates[i] == timedelta(days=1):
                    streak += 1
                    longest_streak = max(longest_streak, streak)
                else:
                    streak = 1
    else:
        current_streak = 0
        longest_streak = 0
    
    # Количество недель с активностью
    week_starts = set(u.week_start for u in all_usages)
    weeks_active = len(week_starts)
    
    return PracticeProgressResponse(
        total_completed=total_completed,
        personalized_completed=personalized_completed,
        general_completed=general_completed,
        by_category=by_category,
        current_streak_days=current_streak,
        longest_streak_days=longest_streak,
        weeks_active=weeks_active,
    )


@router.get("/asceticisms")
async def get_asceticisms(
    user: Optional[User] = Depends(get_optional_user),
):
    """Получить список аскез."""
    try:
        asceticisms_data = load_asceticisms()
        asceticisms = asceticisms_data.get("asceticisms", [])
        return [
            {
                "id": a.get("id"),
                "title": a.get("title"),
                "description": a.get("description"),
            }
            for a in asceticisms
        ]
    except Exception as e:
        logging.error(f"Error loading asceticisms: {e}")
        return []


@router.get("/affirmations")
async def get_affirmations(
    needs: Optional[str] = None,  # Потребности: "money", "love", "calm", "work", "health"
    generate: bool = False,  # Генерировать через AI или вернуть из лексикона
    user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_session),
):
    """
    Получить аффирмации.
    Если generate=true и needs указан — генерирует персонализированные аффирмации через AI.
    Иначе возвращает аффирмации из лексикона (с фильтрацией по needs, если указан).
    """
    # Если запрошена генерация через AI и есть потребности и пользователь
    if generate and needs and user:
        try:
            from todayflow_backend.core.affirmation_generator import generate_affirmations
            from datetime import date
            generated = generate_affirmations(user, db, needs, target_date=date.today().isoformat(), count=3)
            if generated:
                # Возвращаем в формате, совместимом с существующим API
                return [
                    {"id": f"generated_{i}", "text": aff}
                    for i, aff in enumerate(generated)
                ]
        except Exception as e:
            logging.error(f"Error generating affirmations: {e}", exc_info=True)
            # Fallback к лексикону
    
    # Возвращаем из лексикона (существующая логика)
    try:
        affirmations_data = load_affirmations()
        affirmations = affirmations_data.get("affirmations", [])
        
        # Если указаны потребности, фильтруем по тегам/категориям
        if needs:
            needs_tags = {
                "money": ["деньги", "изобилие", "финансы", "богатство"],
                "love": ["любовь", "отношения", "романтика", "близость"],
                "calm": ["спокойствие", "баланс", "гармония", "умиротворение"],
                "work": ["работа", "карьера", "достижения", "успех"],
                "health": ["здоровье", "энергия", "тело", "самочувствие"],
            }
            relevant_tags = needs_tags.get(needs.lower(), [])
            if relevant_tags:
                filtered = []
                for a in affirmations:
                    tags = a.get("tags", []) or []
                    text = (a.get("text", "") or a.get("title", "")).lower()
                    if any(tag.lower() in text for tag in relevant_tags) or any(tag in tags for tag in relevant_tags):
                        filtered.append(a)
                if filtered:
                    affirmations = filtered
        
        return [
            {
                "id": a.get("id"),
                "title": a.get("title", a.get("text", "")),
                "text": a.get("text", a.get("title", "")),
                "goal": a.get("goal"),
                "direction": a.get("direction"),
                "tags": a.get("tags", []) or [],
            }
            for a in affirmations
        ]
    except Exception as e:
        logging.error(f"Error loading affirmations: {e}")
        return []


@router.get("/history", response_model=PracticeHistoryResponse)
async def get_practice_history(
    limit: Optional[int] = 50,
    offset: Optional[int] = 0,
    user: User = Depends(require_user),
    db: Session = Depends(get_session),
):
    """
    Получить историю выполненных практик пользователя.
    """
    # Получаем все практики для маппинга ID -> название
    all_practices = {p["id"]: p for p in GENERAL_PRACTICES + PERSONALIZED_PRACTICES}
    
    # Запрос истории использования
    usages = (
        db.query(PracticeUsage)
        .filter(PracticeUsage.user_id == user.id)
        .order_by(PracticeUsage.completed_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    
    history_items = []
    for usage in usages:
        practice = all_practices.get(usage.practice_id, {})
        history_items.append(
            PracticeHistoryItem(
                id=usage.id,
                practice_id=usage.practice_id,
                practice_title=practice.get("title"),
                category=practice.get("category"),
                completed_at=usage.completed_at,
                is_personalized=usage.is_personalized,
                sequence_id=usage.sequence_id,
                step_number=usage.step_number,
            )
        )
    
    total = db.query(func.count(PracticeUsage.id)).filter(PracticeUsage.user_id == user.id).scalar()
    
    return PracticeHistoryResponse(
        history=history_items,
        total=total or 0,
    )


@router.get("/{practice_id}", response_model=PracticeDetailResponse)
async def get_practice_detail(
    practice_id: str,
    user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_session)
):
    """Получить детальную информацию о практике."""
    # Ищем в общих практиках
    practice = next((p for p in GENERAL_PRACTICES if p["id"] == practice_id), None)
    
    # Если не найдено, ищем в персонализированных
    if not practice:
        practice = next((p for p in PERSONALIZED_PRACTICES if p["id"] == practice_id), None)
    
    if not practice:
        raise HTTPException(status_code=404, detail="Practice not found")
    
    # Проверяем доступ
    if practice.get("access_level") != "free" and not user:
        raise HTTPException(status_code=403, detail="Authentication required")
    
    # Проверяем подписку для lite/pro практик
    if user and practice.get("access_level") in ["lite", "pro"]:
        subscription_level = get_subscription_level(user, db)
        if practice.get("access_level") == "pro" and subscription_level != "pro":
            raise HTTPException(
                status_code=403,
                detail="Эта практика доступна только для Pro подписки"
            )
        elif practice.get("access_level") == "lite" and subscription_level == "free":
            # Проверяем лимиты для персонализированных практик
            limits = get_practice_limits(user, db)
            if limits["remaining_this_week"] <= 0:
                raise HTTPException(
                    status_code=403,
                    detail=f"Достигнут лимит персонализированных практик на эту неделю ({limits['personalized_limit']}). Обновите подписку для большего количества практик."
                )
    
    response = PracticeDetailResponse(**practice)
    return response


@router.get("/categories/list")
async def get_categories():
    """Получить список категорий практик."""
    return {
        "categories": [
            {"id": "meditation", "name": "Медитации", "icon": "🧘"},
            {"id": "breathing", "name": "Дыхание", "icon": "🌬️"},
            {"id": "gratitude", "name": "Благодарность", "icon": "🙏"},
            {"id": "affirmation", "name": "Аффирмации", "icon": "✨"},
            {"id": "ritual", "name": "Ритуалы", "icon": "🔮"},
            {"id": "reflection", "name": "Рефлексия", "icon": "💭"},
            {"id": "emotional", "name": "Эмоции", "icon": "❤️"},
            {"id": "focus", "name": "Фокус", "icon": "🎯"},
        ]
    }


@router.get("/interpretation-bundle")
async def get_interpretation_bundle(
    user: User = Depends(require_user),
    db: Session = Depends(get_session),
    day: Optional[int] = None,
):
    """
    Получить Interpretation Bundle для конкретного дня пользователя.
    Bundle = набор смыслов + практик, собранных под конкретное состояние пользователя.
    
    Если day не указан, вычисляется автоматически от первого визита пользователя.
    """
    from todayflow_backend.services.lite_reports import LiteReportService
    
    # Вычисляем день пользователя (отсчет от регистрации)
    if day is None:
        # Вычисляем день от created_at пользователя
        if user.created_at:
            today = date.today()
            registration_date = user.created_at.date() if isinstance(user.created_at, datetime) else user.created_at
            diff_days = (today - registration_date).days + 1  # +1 потому что день 1 - это день регистрации
            day = min(max(diff_days, 1), 7)  # Ограничиваем 1-7 днями
        else:
            day = 1  # По умолчанию день 1
    
    # Получаем Lite Report для Internal Model
    lite_report_service = LiteReportService()
    try:
        lite_report = lite_report_service._get_latest_report(user)
    except Exception:
        lite_report = None
    
    if not lite_report or not lite_report.internal_model:
        # Возвращаем пустой bundle вместо 404, чтобы фронтенд мог обработать это корректно
        from todayflow_backend.core import models
        return {
            "day": day,
            "practice": None,
            "meanings": [],
            "pattern": None,
        }
    
    # Выбираем паттерн для Day 1 (если день 1-3, используем тот же паттерн)
    pattern = select_pattern_for_day1(lite_report.internal_model)
    if not pattern:
        # Возвращаем пустой bundle вместо 404
        return {
            "bundle_id": f"empty-day{day}",
            "pattern_axis": None,
            "day": day,
            "pattern": None,
            "practice": None,
            "meanings": [],
            "interpretation": None,
            "cta": None,
        }
    
    # Выбираем практику для дня
    all_practices = GENERAL_PRACTICES + PERSONALIZED_PRACTICES
    practice_raw = select_practice_for_day(day, pattern["axis_id"], all_practices, user)
    
    # Формируем Interpretation Bundle (базовая структура)
    bundle = {
        "bundle_id": f"pattern-{pattern['axis_id'].lower()}-day{day}",
        "pattern_axis": pattern["axis_id"],
        "day": day,
        "pattern": {
            "axis_id": pattern["axis_id"],
            "name": pattern["name"],
            "value": pattern["value"],
            "is_positive": pattern["is_positive"],
        },
    }
    
    # Добавляем интерпретацию в зависимости от дня (нужно для personalized_reason)
    interpretation_text = None
    if day == 1:
        interpretation_text = f"Сегодня тебе важно обратить внимание на то, как ты обычно реагируешь в ситуациях. Это связано с твоей {pattern['name'].lower()}."
        bundle["interpretation"] = {
            "facet": "awareness",
            "text": interpretation_text,
            "max_sentences": 2,
        }
        bundle["cta"] = {
            "after_completion": "Как это связано с паттернами →",
            "target": "#patterns",
        }
    elif day == 2:
        interpretation_text = f"Это не случайно. Это повторяющаяся схема. Твоя {pattern['name'].lower()} проявляется в разных ситуациях."
        bundle["interpretation"] = {
            "facet": "application",
            "text": interpretation_text,
            "max_sentences": 3,
        }
        bundle["cta"] = {
            "after_completion": "Попробуй применить в реальной ситуации →",
            "target": "/practices",
        }
    elif day == 3:
        interpretation_text = f"Попробуй сегодня применить практику в реальной ситуации: общении, решении или реакции."
        bundle["interpretation"] = {
            "facet": "integration",
            "text": interpretation_text,
            "max_sentences": 2,
        }
        bundle["cta"] = {
            "after_completion": "Что ты заметил? →",
            "target": "/journal",
        }
    else:
        interpretation_text = f"Продолжай работать с паттерном {pattern['name'].lower()}."
        bundle["interpretation"] = {
            "facet": "general",
            "text": interpretation_text,
            "max_sentences": 2,
        }
        bundle["cta"] = {
            "after_completion": "Продолжить →",
            "target": "/practices",
        }
    
    # Форматируем practice для ответа (соответствует типу InterpretationBundle)
    if practice_raw:
        practice = {
            "id": practice_raw.get("id", ""),
            "title": practice_raw.get("title", ""),
            "description": practice_raw.get("description", ""),
            "category": practice_raw.get("category", ""),
            "duration_minutes": practice_raw.get("duration_minutes"),
            "difficulty": practice_raw.get("difficulty", "beginner"),
            "is_free": practice_raw.get("is_free", False),
            "access_level": practice_raw.get("access_level", "lite"),
            "tags": practice_raw.get("tags", []),
            "personalized_reason": practice_raw.get("personalized_reason") or interpretation_text,
        }
        bundle["practice"] = practice
    
    return bundle


@router.get("/sequences", response_model=List[PracticeResponse])
async def get_sequences(
    user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_session),
):
    """
    Получить список доступных guided sequences (серий практик).
    """
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    sequences = [
        p for p in PERSONALIZED_PRACTICES 
        if p.get("practice_type") == "guided_sequence"
    ]
    
    # Проверяем подписку для фильтрации
    subscription_level = get_subscription_level(user, db)
    sequences = [
        s for s in sequences 
        if s.get("access_level") == "free" or 
        (s.get("access_level") == "lite" and subscription_level in ["lite", "pro"]) or
        (s.get("access_level") == "pro" and subscription_level == "pro")
    ]
    
    return sequences


@router.get("/sequences/{sequence_id}", response_model=PracticeDetailResponse)
async def get_sequence_detail(
    sequence_id: str,
    user: User = Depends(require_user),
    db: Session = Depends(get_session),
):
    """
    Получить детальную информацию о guided sequence.
    """
    sequence = next(
        (p for p in PERSONALIZED_PRACTICES 
         if p.get("sequence_id") == sequence_id and p.get("practice_type") == "guided_sequence"),
        None
    )
    
    if not sequence:
        raise HTTPException(status_code=404, detail="Sequence not found")
    
    # Проверяем доступ
    subscription_level = get_subscription_level(user, db)
    if sequence.get("access_level") == "pro" and subscription_level != "pro":
        raise HTTPException(status_code=403, detail="Эта серия доступна только для Pro подписки")
    
    response = PracticeDetailResponse(**sequence)
    return response


@router.get("/sequences/{sequence_id}/progress", response_model=SequenceProgressResponse)
async def get_sequence_progress(
    sequence_id: str,
    user: User = Depends(require_user),
    db: Session = Depends(get_session),
):
    """
    Получить прогресс пользователя по guided sequence.
    """
    # Проверяем, что sequence существует
    sequence = next(
        (p for p in PERSONALIZED_PRACTICES 
         if p.get("sequence_id") == sequence_id and p.get("practice_type") == "guided_sequence"),
        None
    )
    
    if not sequence:
        raise HTTPException(status_code=404, detail="Sequence not found")
    
    # Получаем все записи об использовании практик из этой серии
    usages = db.query(PracticeUsage).filter(
        PracticeUsage.user_id == user.id,
        PracticeUsage.sequence_id == sequence_id
    ).order_by(PracticeUsage.completed_at.asc()).all()
    
    completed_steps = len(usages)
    total_steps = sequence.get("total_steps", 0)
    current_step = completed_steps + 1 if completed_steps < total_steps else None
    is_completed = completed_steps >= total_steps
    
    started_at = usages[0].completed_at if usages else None
    last_completed_at = usages[-1].completed_at if usages else None
    
    return SequenceProgressResponse(
        sequence_id=sequence_id,
        sequence_title=sequence.get("title", ""),
        total_steps=total_steps,
        completed_steps=completed_steps,
        current_step=current_step,
        started_at=started_at,
        last_completed_at=last_completed_at,
        is_completed=is_completed
    )


@router.post("/sequences/{sequence_id}/steps/{step_number}/complete", response_model=PracticeUsageResponse)
async def complete_sequence_step(
    sequence_id: str,
    step_number: int,
    user: User = Depends(require_user),
    db: Session = Depends(get_session),
):
    """
    Отметить шаг guided sequence как выполненный.
    """
    # Проверяем, что sequence существует
    sequence = next(
        (p for p in PERSONALIZED_PRACTICES 
         if p.get("sequence_id") == sequence_id and p.get("practice_type") == "guided_sequence"),
        None
    )
    
    if not sequence:
        raise HTTPException(status_code=404, detail="Sequence not found")
    
    # Проверяем, что шаг существует
    steps = sequence.get("steps", [])
    step = next((s for s in steps if s.get("step_number") == step_number), None)
    
    if not step:
        raise HTTPException(status_code=404, detail="Step not found")
    
    # Проверяем, что предыдущие шаги выполнены (кроме первого)
    if step_number > 1:
        previous_usages = db.query(PracticeUsage).filter(
            PracticeUsage.user_id == user.id,
            PracticeUsage.sequence_id == sequence_id,
            PracticeUsage.step_number < step_number
        ).count()
        
        if previous_usages < step_number - 1:
            raise HTTPException(
                status_code=400,
                detail="Необходимо выполнить предыдущие шаги последовательно"
            )
    
    # Проверяем лимиты для персонализированных практик
    limits = get_practice_limits(user, db)
    if limits["remaining_this_week"] <= 0 and limits["subscription_level"] != "pro":
        raise HTTPException(
            status_code=403,
            detail=f"Достигнут лимит персонализированных практик на эту неделю ({limits['personalized_limit']}). Обновите подписку для большего количества практик."
        )
    
    # Создаем запись об использовании
    week_start = get_week_start()
    usage = PracticeUsage(
        user_id=user.id,
        practice_id=f"{sequence_id}-step-{step_number}",
        completed_at=datetime.utcnow(),
        week_start=week_start,
        is_personalized=True,
        sequence_id=sequence_id,
        step_number=step_number
    )
    
    db.add(usage)
    db.commit()
    db.refresh(usage)
    
    return PracticeUsageResponse(
        practice_id=f"{sequence_id}-step-{step_number}",
        completed_at=usage.completed_at
    )

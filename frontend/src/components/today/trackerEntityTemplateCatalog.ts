/**
 * Шаблоны мастера целей/привычек и подписи фильтров аскез (`/tracking/calendar`).
 * iOS: при нативном мастере — те же смыслы (паритет с этим файлом или общий API).
 */

import type { FlowPracticesChromeLocale } from "./flowPracticesMainTabChrome";
import type { AsceticCategoryFilter, TrackerTemplateGroup } from "@/app/tracking/calendar/trackerEntityCatalog";

const GOAL_TEMPLATE_GROUPS_RU: TrackerTemplateGroup[] = [
  {
    category: { id: "rhythm", label: "Ритм и энергия", description: "Стабильный темп дня без выгорания" },
    items: [
      { title: "5 из 7 дней: утренний чек состояния + 5 минут дыхания", hint: "Мягкий вход в день" },
      { title: "Ежедневно: 1 ключевая задача + 1 короткая практика", hint: "Минимум, который реально удержать" },
      { title: "До конца периода: закрывать день вечерним ритуалом 4 раза", hint: "Завершение без телефона в постели" },
      { title: "3 дня подряд ложиться до полуночи", hint: "Восстановление базы" },
      { title: "Каждый будний день — 25 минут глубокого фокуса", hint: "Один таймер, без переключений" },
    ],
  },
  {
    category: { id: "focus", label: "Фокус и ясность", description: "Меньше шума, больше внимания к важному" },
    items: [
      { title: "4 блока по 45 мин в неделю без соцсетей", hint: "Телефон в другой комнате" },
      { title: "Каждый день: список из 3 приоритетов до 10:00", hint: "Только три пункта" },
      { title: "5 дней: начинать работу с самой неприятной задачи", hint: "Eat the frog" },
      { title: "Неделя без новостей после 20:00", hint: "Спокойный вечер" },
      { title: "Завершить один «висящий» проект до конца периода", hint: "Довести до черты" },
    ],
  },
  {
    category: { id: "body", label: "Тело и восстановление", description: "Сон, движение, базовый уход" },
    items: [
      { title: "10 000 шагов 5 дней в неделю", hint: "Прогулка как якорь" },
      { title: "Стакан воды сразу после пробуждения — 7 дней подряд", hint: "Простой триггер" },
      { title: "3 тренировки за период любой длительности", hint: "Без давления на результат" },
      { title: "Неделя без кофе после 14:00", hint: "Мягкий сон" },
      { title: "Каждый вечер 10 минут растяжки", hint: "Снять зажим" },
    ],
  },
  {
    category: { id: "emotion", label: "Эмоции и опора", description: "Регуляция и самоподдержка" },
    items: [
      { title: "4 вечерних рефлексии за период без пропусков", hint: "3 строки: факт — чувство — вывод" },
      { title: "Каждый день назвать вслух одну благодарность", hint: "Микро-практика" },
      { title: "Неделя: перед ответом в конфликте — пауза на 3 вдоха", hint: "Снижение импульсивности" },
      { title: "Довести один стрик заботы о себе до 5 дней", hint: "Маленький ритуал" },
      { title: "Записать 5 ситуаций, где справился(лась), и прочитать в пятницу", hint: "Укрепление самоэффективности" },
    ],
  },
  {
    category: { id: "growth", label: "Рост и обучение", description: "Навыки и знания без перегруза" },
    items: [
      { title: "30 минут чтения/уроков 5 дней из 7", hint: "Таймер, не страницы" },
      { title: "Закончить один модуль курса до конца периода", hint: "Конкретный модуль" },
      { title: "Каждый день 15 минут языка", hint: "Приложение или карточки" },
      { title: "Написать конспект одной идеи и применить на практике", hint: "От знания к действию" },
      { title: "Разобрать один рабочий процесс и упростить его", hint: "Меньше трения" },
    ],
  },
  {
    category: { id: "relations", label: "Люди и границы", description: "Контакт и защита ресурса" },
    items: [
      { title: "3 осознанных разговора по 20 минут без телефона", hint: "Присутствие" },
      { title: "Неделя: один вечер без рабочих сообщений после 19:00", hint: "Граница" },
      { title: "Один раз честно сказать «нет» запросу, который перегружает", hint: "Маленькая практика границ" },
      { title: "Написать близкому короткое сообщение поддержки каждый день", hint: "Связь" },
    ],
  },
];

const GOAL_TEMPLATE_GROUPS_EN: TrackerTemplateGroup[] = [
  {
    category: { id: "rhythm", label: "Rhythm & energy", description: "Steady daily pace without burnout" },
    items: [
      { title: "5 of 7 days: morning check-in + 5 minutes breathing", hint: "Gentle start to the day" },
      { title: "Daily: 1 key task + 1 short practice", hint: "A minimum you can actually keep" },
      { title: "By period end: evening close-out ritual 4 times", hint: "No phone in bed" },
      { title: "3 nights in a row: lights out by midnight", hint: "Rebuild your baseline" },
      { title: "Every weekday — 25 minutes deep focus", hint: "One timer, no switching" },
    ],
  },
  {
    category: { id: "focus", label: "Focus & clarity", description: "Less noise, more attention to what matters" },
    items: [
      { title: "Four 45-minute blocks per week without socials", hint: "Phone in another room" },
      { title: "Daily: list 3 priorities before 10:00", hint: "Only three bullets" },
      { title: "5 days: start with the hardest task", hint: "Eat the frog" },
      { title: "One week: no news after 8:00 pm", hint: "Calm evening" },
      { title: "Ship one hanging project by period end", hint: "Cross the finish line" },
    ],
  },
  {
    category: { id: "body", label: "Body & recovery", description: "Sleep, movement, basic care" },
    items: [
      { title: "10,000 steps 5 days a week", hint: "Walking as an anchor" },
      { title: "Glass of water after waking — 7 days straight", hint: "Simple trigger" },
      { title: "3 workouts this period, any length", hint: "No performance pressure" },
      { title: "One week: no coffee after 2:00 pm", hint: "Gentler sleep" },
      { title: "Every evening 10 minutes stretching", hint: "Release tension" },
    ],
  },
  {
    category: { id: "emotion", label: "Emotions & grounding", description: "Regulation and self-support" },
    items: [
      { title: "4 evening reflections this period, no skips", hint: "3 lines: fact — feeling — takeaway" },
      { title: "Daily: say one gratitude out loud", hint: "Micro-practice" },
      { title: "One week: in conflict, pause for 3 breaths before answering", hint: "Less impulsivity" },
      { title: "Grow one self-care streak to 5 days", hint: "Small ritual" },
      { title: "Write 5 moments you handled well; read them on Friday", hint: "Build self-efficacy" },
    ],
  },
  {
    category: { id: "growth", label: "Growth & learning", description: "Skills and knowledge without overload" },
    items: [
      { title: "30 minutes reading/lessons 5 of 7 days", hint: "Timer, not page count" },
      { title: "Finish one course module by period end", hint: "A concrete module" },
      { title: "Daily 15 minutes of language", hint: "App or flashcards" },
      { title: "Summarize one idea and apply it", hint: "From knowledge to action" },
      { title: "Simplify one workflow end to end", hint: "Less friction" },
    ],
  },
  {
    category: { id: "relations", label: "People & boundaries", description: "Connection and protecting bandwidth" },
    items: [
      { title: "Three mindful 20-minute chats without your phone", hint: "Presence" },
      { title: "One week: one evening with no work messages after 7:00 pm", hint: "A boundary" },
      { title: "Once say an honest no to an ask that overloads you", hint: "Small boundary practice" },
      { title: "Send someone close a short supportive message every day", hint: "Connection" },
    ],
  },
];

const HABIT_TEMPLATE_GROUPS_RU: TrackerTemplateGroup[] = [
  {
    category: { id: "morning", label: "Утро", description: "Старт дня" },
    items: [
      { title: "Стакан воды после подъёма", hint: "30 секунд" },
      { title: "2 минуты планирования дня", hint: "Три задачи" },
      { title: "Свет и окно — сразу после будильника", hint: "Регуляция циркад" },
      { title: "Короткая зарядка 7 минут", hint: "Любимый комплекс" },
      { title: "Аффирмация или намерение вслух", hint: "Одна фраза" },
    ],
  },
  {
    category: { id: "body_habit", label: "Тело", description: "Движение и сон" },
    items: [
      { title: "Прогулка 20+ минут", hint: "Без подкаста — только шаги" },
      { title: "Лечь в одно время ±30 мин", hint: "Якорь сна" },
      { title: "Один приём пищи без экрана", hint: "Осознанность" },
      { title: "Растяжка перед сном", hint: "5–10 минут" },
      { title: "Лестница вместо лифта (где безопасно)", hint: "Микродвижение" },
    ],
  },
  {
    category: { id: "mind", label: "Фокус и цифра", description: "Внимание и экран" },
    items: [
      { title: "Первый час дня без соцсетей", hint: "Режим «не беспокоить»" },
      { title: "Один Pomodoro без переключений", hint: "25 минут" },
      { title: "Инбокс нуля — раз в день 15 минут", hint: "Не весь день в почте" },
      { title: "Телефон вне спальни на ночь", hint: "Зарядка в коридоре" },
      { title: "Очистить рабочий стол / одну папку", hint: "Микро-порядок" },
    ],
  },
  {
    category: { id: "care", label: "Забота", description: "Ресурс и эмоции" },
    items: [
      { title: "Дневник: 3 строки вечером", hint: "Факт — чувство — завтра" },
      { title: "5 минут дыхания", hint: "Таймер" },
      { title: "Сказать «спасибо» кому-то конкретно", hint: "Текст или голос" },
      { title: "10 минут на хобби без цели", hint: "Радость" },
      { title: "Прогулка без цели", hint: "Только идти" },
    ],
  },
  {
    category: { id: "home", label: "Быт", description: "Окружение" },
    items: [
      { title: "10 минут уборки таймером", hint: "Один угол" },
      { title: "Вынести мусор / разгрузить посудомойку", hint: "Микрозадача" },
      { title: "Подготовить одежду на завтра", hint: "Вечером" },
      { title: "Проветривание + влажная уборка стола", hint: "Среда = голова" },
    ],
  },
  {
    category: { id: "social", label: "Связь", description: "Люди" },
    items: [
      { title: "Одно сообщение близкому", hint: "Не деловое" },
      { title: "Позвонить родителю / другу 10 минут", hint: "Голос" },
      { title: "Поблагодарить коллегу за конкретику", hint: "Письмо или устно" },
    ],
  },
];

const HABIT_TEMPLATE_GROUPS_EN: TrackerTemplateGroup[] = [
  {
    category: { id: "morning", label: "Morning", description: "Start the day" },
    items: [
      { title: "Glass of water after waking", hint: "30 seconds" },
      { title: "2 minutes to plan the day", hint: "Three tasks" },
      { title: "Light and window right after the alarm", hint: "Circadian cue" },
      { title: "Short 7-minute workout", hint: "A routine you like" },
      { title: "Affirmation or intention out loud", hint: "One phrase" },
    ],
  },
  {
    category: { id: "body_habit", label: "Body", description: "Movement and sleep" },
    items: [
      { title: "Walk 20+ minutes", hint: "No podcast—just steps" },
      { title: "Same bedtime ±30 minutes", hint: "Sleep anchor" },
      { title: "One meal without a screen", hint: "Mindful eating" },
      { title: "Stretch before bed", hint: "5–10 minutes" },
      { title: "Stairs instead of elevator (when safe)", hint: "Micro-movement" },
    ],
  },
  {
    category: { id: "mind", label: "Focus & screens", description: "Attention and devices" },
    items: [
      { title: "First hour of day without socials", hint: "Do-not-disturb mode" },
      { title: "One Pomodoro without switching", hint: "25 minutes" },
      { title: "Inbox zero once a day, 15 minutes", hint: "Not all day in email" },
      { title: "Phone out of the bedroom at night", hint: "Charge in the hall" },
      { title: "Clear desk or one folder", hint: "Micro-tidy" },
    ],
  },
  {
    category: { id: "care", label: "Care", description: "Energy and emotions" },
    items: [
      { title: "Journal: 3 lines in the evening", hint: "Fact — feeling — tomorrow" },
      { title: "5 minutes breathing", hint: "Use a timer" },
      { title: "Say thanks to someone specific", hint: "Text or voice" },
      { title: "10 minutes on a hobby with no goal", hint: "Joy" },
      { title: "Aimless walk", hint: "Just move" },
    ],
  },
  {
    category: { id: "home", label: "Home", description: "Environment" },
    items: [
      { title: "10 minutes cleaning on a timer", hint: "One corner" },
      { title: "Take out trash / empty dishwasher", hint: "Micro-task" },
      { title: "Lay out clothes for tomorrow", hint: "Evening prep" },
      { title: "Air the room + wipe your desk", hint: "Space supports focus" },
    ],
  },
  {
    category: { id: "social", label: "Connection", description: "People" },
    items: [
      { title: "One message to someone close", hint: "Not work-related" },
      { title: "Call a parent or friend for 10 minutes", hint: "Voice" },
      { title: "Thank a colleague for something specific", hint: "Email or in person" },
    ],
  },
];

const ASCETIC_CATEGORY_FILTERS_RU: AsceticCategoryFilter[] = [
  {
    category: { id: "all", label: "Все", description: "Полный список из каталога" },
    keywords: [],
  },
  {
    category: { id: "focus", label: "Фокус", description: "Внимание и отвлечения" },
    keywords: [
      "фокус",
      "концентрац",
      "внимание",
      "отвлеч",
      "соцсет",
      "экран",
      "телефон",
      "уведомлен",
      "digital",
      "информац",
      "focus",
      "concentrat",
      "attention",
      "distract",
      "social",
      "screen",
      "phone",
      "notif",
    ],
  },
  {
    category: { id: "energy", label: "Энергия", description: "Движение и бодрость" },
    keywords: [
      "энерг",
      "актив",
      "движен",
      "утро",
      "сон",
      "устал",
      "восстанов",
      "energy",
      "active",
      "movement",
      "morning",
      "sleep",
      "tired",
      "recover",
    ],
  },
  {
    category: { id: "calm", label: "Спокойствие", description: "Стресс и баланс" },
    keywords: [
      "спокой",
      "баланс",
      "тревог",
      "стресс",
      "дыхан",
      "медитац",
      "расслаб",
      "пауз",
      "calm",
      "balance",
      "anxiet",
      "stress",
      "breath",
      "meditat",
      "relax",
      "pause",
    ],
  },
  {
    category: { id: "discipline", label: "Дисциплина", description: "Контроль и привычки" },
    keywords: [
      "дисциплин",
      "контрол",
      "самоконтрол",
      "сила воли",
      "ограничен",
      "отказ",
      "правил",
      "disciplin",
      "control",
      "willpower",
      "limit",
      "rule",
      "habit",
    ],
  },
  {
    category: { id: "body_asc", label: "Тело и еда", description: "Физические ограничения" },
    keywords: [
      "еда",
      "пищ",
      "сахар",
      "кофе",
      "алкогол",
      "вода",
      "тело",
      "сон",
      "пост",
      "food",
      "sugar",
      "coffee",
      "alcohol",
      "water",
      "body",
      "sleep",
      "fast",
    ],
  },
  {
    category: { id: "connection", label: "Связь с собой", description: "Осознанность" },
    keywords: [
      "осознан",
      "себя",
      "потребност",
      "рефлекс",
      "дневник",
      "тишин",
      "молчан",
      "mindful",
      "self",
      "need",
      "journal",
      "quiet",
      "silence",
      "reflect",
    ],
  },
  {
    category: { id: "social_asc", label: "Люди и границы", description: "Общение и изоляция" },
    keywords: [
      "люди",
      "общен",
      "границ",
      "новост",
      "чат",
      "звонок",
      "молчан",
      "people",
      "social",
      "boundar",
      "news",
      "chat",
      "call",
      "silent",
    ],
  },
  {
    category: { id: "growth_asc", label: "Рост", description: "Обучение и потребление" },
    keywords: [
      "чтен",
      "сериал",
      "игр",
      "новост",
      "покуп",
      "потреблен",
      "read",
      "show",
      "game",
      "news",
      "shop",
      "consum",
    ],
  },
];

const ASCETIC_CATEGORY_FILTERS_EN: AsceticCategoryFilter[] = [
  {
    category: { id: "all", label: "All", description: "Full catalog list" },
    keywords: [],
  },
  {
    category: { id: "focus", label: "Focus", description: "Attention and distractions" },
    keywords: ASCETIC_CATEGORY_FILTERS_RU[1]!.keywords,
  },
  {
    category: { id: "energy", label: "Energy", description: "Movement and vitality" },
    keywords: ASCETIC_CATEGORY_FILTERS_RU[2]!.keywords,
  },
  {
    category: { id: "calm", label: "Calm", description: "Stress and balance" },
    keywords: ASCETIC_CATEGORY_FILTERS_RU[3]!.keywords,
  },
  {
    category: { id: "discipline", label: "Discipline", description: "Control and habits" },
    keywords: ASCETIC_CATEGORY_FILTERS_RU[4]!.keywords,
  },
  {
    category: { id: "body_asc", label: "Body & food", description: "Physical limits" },
    keywords: ASCETIC_CATEGORY_FILTERS_RU[5]!.keywords,
  },
  {
    category: { id: "connection", label: "Inner connection", description: "Mindfulness" },
    keywords: ASCETIC_CATEGORY_FILTERS_RU[6]!.keywords,
  },
  {
    category: { id: "social_asc", label: "People & boundaries", description: "Social life and isolation" },
    keywords: ASCETIC_CATEGORY_FILTERS_RU[7]!.keywords,
  },
  {
    category: { id: "growth_asc", label: "Growth", description: "Learning and consumption" },
    keywords: ASCETIC_CATEGORY_FILTERS_RU[8]!.keywords,
  },
];

export function getGoalTemplateGroups(locale: FlowPracticesChromeLocale): TrackerTemplateGroup[] {
  return locale === "ru" ? GOAL_TEMPLATE_GROUPS_RU : GOAL_TEMPLATE_GROUPS_EN;
}

export function getHabitTemplateGroups(locale: FlowPracticesChromeLocale): TrackerTemplateGroup[] {
  return locale === "ru" ? HABIT_TEMPLATE_GROUPS_RU : HABIT_TEMPLATE_GROUPS_EN;
}

export function getAsceticCategoryFilters(locale: FlowPracticesChromeLocale): AsceticCategoryFilter[] {
  return locale === "ru" ? ASCETIC_CATEGORY_FILTERS_RU : ASCETIC_CATEGORY_FILTERS_EN;
}

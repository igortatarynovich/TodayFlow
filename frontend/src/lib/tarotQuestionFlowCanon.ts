/**
 * Tarot Question-First flow — canon: SCREEN_CONTRACTS_V1 §6.4–§6.8
 * Product unit = user question, not deck format.
 */

export type TarotConcernDomain =
  | "relationships"
  | "work"
  | "money"
  | "family"
  | "growth"
  | "decision"
  | "conflict"
  | "inner_state"
  | "other";

export type TarotFlowStep = "hero" | "concern" | "refine" | "spread";

export type TarotConcernOption = {
  id: TarotConcernDomain;
  emoji: string;
  label: string;
  hint: string;
};

export type TarotRefinementOption = {
  id: string;
  label: string;
  questionSeed: string;
};

export type TarotSpreadOffer = {
  spreadId: string;
  title: string;
  subtitle: string;
  /** What questions this spread answers — not card count. */
  answersQuestions: string;
  cardCount: number;
  /** Position labels for ritual pick (RU). */
  positionLabels: string[];
  recommendedFor: TarotConcernDomain[];
};

export const TAROT_QUESTION_FLOW_COPY = {
  heroTitle: "У каждого вопроса есть несколько сторон",
  heroBody:
    "Иногда достаточно посмотреть на ситуацию под другим углом. Карты помогают увидеть то, что легко упустить, когда эмоции слишком сильны.",
  heroCta: "Разобраться с тем, что волнует",
  heroSecondary: "Карта дня",
  concernStep: "Шаг 1 из 3",
  concernTitle: "Что сейчас занимает твои мысли?",
  concernBody: "Выбери близкую тему — или сформулируй свой вопрос ниже.",
  concernCustomLabel: "Написать свой вопрос",
  concernCustomPlaceholder: "Например: стоит ли менять работу?",
  refineStep: "Шаг 2 из 3",
  refineTitle: "Сегодня тебя больше волнует…",
  spreadStep: "Шаг 3 из 3",
  spreadTitle: "Какой взгляд нужен сейчас?",
  spreadBody: "Каждый расклад отвечает на свои вопросы — не про количество карт.",
  back: "Назад",
  continue: "Дальше",
  skipRefine: "Пропустить уточнение",
  resetFlow: "Начать сначала",
  submitRitual: "К ритуалу →",
  cardOfDayHintPrefix: "Карта дня уже выбрана —",
  openLink: "Открыть →",
} as const;

export const TAROT_CONCERN_OPTIONS: TarotConcernOption[] = [
  { id: "relationships", emoji: "❤️", label: "Отношения", hint: "Близость, пара, чувства" },
  { id: "work", emoji: "💼", label: "Работа", hint: "Карьера, роль, направление" },
  { id: "money", emoji: "💰", label: "Деньги", hint: "Ресурс, решения, стабильность" },
  { id: "family", emoji: "🏡", label: "Семья", hint: "Родные, дом, границы" },
  { id: "growth", emoji: "🌱", label: "Саморазвитие", hint: "Рост, смысл, путь" },
  { id: "decision", emoji: "🧭", label: "Важное решение", hint: "Выбор, развилка" },
  { id: "conflict", emoji: "⚡", label: "Конфликт", hint: "Напряжение, спор, застревание" },
  { id: "inner_state", emoji: "🕊", label: "Внутреннее состояние", hint: "Настроение, опора, усталость" },
  { id: "other", emoji: "✨", label: "Другое", hint: "Своя формулировка" },
];

export const TAROT_REFINEMENTS: Record<TarotConcernDomain, TarotRefinementOption[]> = {
  relationships: [
    { id: "specific_person", label: "Конкретный человек", questionSeed: "Что сейчас важно понять в отношениях с этим человеком?" },
    { id: "relationships_general", label: "Отношения вообще", questionSeed: "Какой новый взгляд поможет мне в теме близости прямо сейчас?" },
    { id: "ex_partner", label: "Бывший партнёр", questionSeed: "Что мне важно увидеть в истории с бывшим партнёром?" },
    { id: "new_person", label: "Новый человек", questionSeed: "Как лучше понять то, что происходит с новым человеком?" },
    { id: "two_people", label: "Выбор между двумя людьми", questionSeed: "Какой взгляд поможет мне честнее увидеть выбор между двумя людьми?" },
  ],
  work: [
    { id: "stay_or_leave", label: "Остаться или уйти", questionSeed: "Стоит ли менять работу — или сначала что-то прояснить здесь?" },
    { id: "direction", label: "Куда двигаться", questionSeed: "Какое направление в работе сейчас заслуживает внимания?" },
    { id: "team_conflict", label: "Конфликт на работе", questionSeed: "Как лучше пройти текущее напряжение на работе?" },
    { id: "burnout", label: "Усталость и выгорание", questionSeed: "Что поможет вернуть ясность, когда работа выматывает?" },
  ],
  money: [
    { id: "big_purchase", label: "Крупная трата или вложение", questionSeed: "Какой взгляд поможет принять решение о деньгах спокойнее?" },
    { id: "stability", label: "Стабильность и страх", questionSeed: "Где сейчас реальная опора в теме денег, а где тревога?" },
    { id: "income_change", label: "Изменить доход", questionSeed: "Что важно учесть, если я хочу изменить свой доход?" },
  ],
  family: [
    { id: "parent", label: "Родитель или старшие", questionSeed: "Что сейчас важно понять в отношениях с родителями или старшими?" },
    { id: "child", label: "Ребёнок", questionSeed: "Какой взгляд поможет мне быть ближе к ребёнку без давления?" },
    { id: "home", label: "Дом и быт", questionSeed: "Что дома требует честного взгляда прямо сейчас?" },
    { id: "boundaries", label: "Границы в семье", questionSeed: "Где в семье мне нужны более ясные границы?" },
  ],
  growth: [
    { id: "direction", label: "Куда расти", questionSeed: "Какой следующий шаг в саморазвитии сейчас уместен?" },
    { id: "block", label: "Что мешает", questionSeed: "Что мешает мне двигаться вперёд в росте?" },
    { id: "purpose", label: "Смысл и предназначение", questionSeed: "Какой новый угол поможет увидеть свой путь яснее?" },
  ],
  decision: [
    { id: "two_options", label: "Два варианта", questionSeed: "Как честнее сравнить два варианта, между которыми я выбираю?" },
    { id: "timing", label: "Срок и момент", questionSeed: "Сейчас время действовать — или лучше дать ситуации день?" },
    { id: "fear", label: "Страх ошибиться", questionSeed: "Что я боюсь потерять, откладывая это решение?" },
  ],
  conflict: [
    { id: "with_person", label: "Конфликт с человеком", questionSeed: "Как лучше увидеть конфликт с этим человеком?" },
    { id: "inner", label: "Внутренний конфликт", questionSeed: "Какие части меня сейчас тянут в разные стороны?" },
    { id: "stuck", label: "Застрял и не могу сдвинуться", questionSeed: "Что поможет выйти из застревания без резких шагов?" },
  ],
  inner_state: [
    { id: "anxiety", label: "Тревога", questionSeed: "Что сейчас питает мою тревогу — и что может её смягчить?" },
    { id: "emptiness", label: "Пустота или апатия", questionSeed: "Что поможет вернуть контакт с собой, когда внутри пусто?" },
    { id: "overwhelm", label: "Перегруз", questionSeed: "Какой один взгляд поможет при перегрузе?" },
    { id: "need_rest", label: "Нужен покой", questionSeed: "Что сейчас действительно восстановит, а не отвлечёт?" },
  ],
  other: [
    { id: "custom", label: "Сформулирую сам", questionSeed: "" },
  ],
};

export const TAROT_SPREAD_OFFERS: TarotSpreadOffer[] = [
  {
    spreadId: "one_card",
    title: "Одна карта",
    subtitle: "Быстрый взгляд",
    answersQuestions: "Когда нужен один честный фокус — без длинного разбора.",
    cardCount: 1,
    positionLabels: ["Фокус"],
    recommendedFor: ["inner_state", "other", "decision"],
  },
  {
    spreadId: "three_cards",
    title: "Три карты",
    subtitle: "Линия ситуации",
    answersQuestions: "Что привело сюда, что происходит сейчас и куда может пойти следующий шаг.",
    cardCount: 3,
    positionLabels: ["Прошлое", "Настоящее", "Следующий шаг"],
    recommendedFor: ["relationships", "work", "decision", "conflict", "other"],
  },
  {
    spreadId: "guidance_relationship_five",
    title: "Любовный",
    subtitle: "Пять карт",
    answersQuestions: "Что ты чувствуешь, что между вами, где риск и что лучше сделать.",
    cardCount: 5,
    positionLabels: ["Ты", "Другой", "Между вами", "Риск", "Шаг"],
    recommendedFor: ["relationships"],
  },
  {
    spreadId: "guidance_choice_two",
    title: "Решение",
    subtitle: "Шесть карт",
    answersQuestions: "Сравнение двух путей: что даёт каждый, где риск и лучший следующий шаг.",
    cardCount: 6,
    positionLabels: ["A — даёт", "A — риск", "B — даёт", "B — риск", "Важно", "Шаг"],
    recommendedFor: ["decision", "work", "money"],
  },
  {
    spreadId: "guidance_work_money",
    title: "Деньги",
    subtitle: "Пять карт",
    answersQuestions: "Где реальность, где страх, что сработает и какой практический шаг на этой неделе.",
    cardCount: 5,
    positionLabels: ["Реальность", "Страх", "Сработает", "Риск", "Шаг"],
    recommendedFor: ["money", "work"],
  },
  {
    spreadId: "guidance_inner_conflict",
    title: "Конфликт",
    subtitle: "Пять карт",
    answersQuestions: "Чего ты хочешь, чего боишься, что подавляешь и как выйти из застревания.",
    cardCount: 5,
    positionLabels: ["Хочешь", "Боишься", "Подавляешь", "Если не менять", "Выход"],
    recommendedFor: ["conflict", "inner_state"],
  },
  {
    spreadId: "alignment_cross",
    title: "Внутреннее состояние",
    subtitle: "Четыре карты",
    answersQuestions: "Как сейчас связаны ум, сердце, тело и что из этого — действие.",
    cardCount: 4,
    positionLabels: ["Ум", "Сердце", "Тело", "Интеграция"],
    recommendedFor: ["inner_state", "growth"],
  },
  {
    spreadId: "guidance_deep_eight",
    title: "Предназначение",
    subtitle: "Полное исследование",
    answersQuestions: "Суть, роли, скрытое, риск, возможность, совет и первый реальный шаг.",
    cardCount: 8,
    positionLabels: ["Суть", "Твоя роль", "Другой фактор", "Скрытое", "Риск", "Шанс", "Совет", "Шаг"],
    recommendedFor: ["growth", "decision", "other"],
  },
];

export function getSpreadOffer(spreadId: string): TarotSpreadOffer | undefined {
  return TAROT_SPREAD_OFFERS.find((s) => s.spreadId === spreadId);
}

export function rankSpreadOffersForConcern(domain: TarotConcernDomain | null): TarotSpreadOffer[] {
  if (!domain) return [...TAROT_SPREAD_OFFERS];
  const scored = TAROT_SPREAD_OFFERS.map((offer) => {
    let score = 0;
    if (offer.recommendedFor.includes(domain)) score += 1;
    if (offer.spreadId !== "one_card" && offer.spreadId !== "three_cards") score += 1;
    return { offer, score };
  });
  scored.sort((a, b) => b.score - a.score);
  return scored.map((s) => s.offer);
}

export function composeTarotQuestion(params: {
  concernDomain: TarotConcernDomain | null;
  refinementId: string | null;
  customQuestion: string;
}): string {
  const custom = params.customQuestion.trim();
  if (custom) return custom;

  const domain = params.concernDomain;
  if (!domain) return "Какой новый взгляд поможет мне сейчас?";

  const refinements = TAROT_REFINEMENTS[domain];
  const picked = refinements.find((r) => r.id === params.refinementId);
  if (picked?.questionSeed) return picked.questionSeed;

  const concern = TAROT_CONCERN_OPTIONS.find((c) => c.id === domain);
  if (concern) {
    return `Какой новый взгляд поможет мне в теме «${concern.label.toLowerCase()}» прямо сейчас?`;
  }
  return "Какой новый взгляд поможет мне сейчас?";
}

export function buildTarotRitualHref(params: {
  spreadId: string;
  question: string;
  concernDomain?: TarotConcernDomain | null;
  refinementId?: string | null;
}): string {
  const search = new URLSearchParams();
  if (params.question.trim()) search.set("question", params.question.trim());
  if (params.concernDomain) search.set("domain", params.concernDomain);
  if (params.refinementId) search.set("refinement", params.refinementId);
  const q = search.toString();
  return `/tarot/spread/${encodeURIComponent(params.spreadId)}${q ? `?${q}` : ""}`;
}

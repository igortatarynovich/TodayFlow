/** Scenario presentation skins — one engine, many atmospheres (serious + playful). */

export type ScenarioTone = "romantic" | "dramatic" | "playful" | "office" | "domestic" | "calm" | "vacation";

export type ToneMode = "serious" | "playful";

export type SubscoreKey = "attraction" | "stability" | "conflicts" | "sexuality";

export type ScenarioDimensionLabel = {
  key: SubscoreKey;
  emoji: string;
  label: string;
};

export type ScenarioSkin = {
  id: string;
  emoji: string;
  title: string;
  hook: string;
  tone: ScenarioTone;
  toneMode: ToneMode;
  /** Poster headline on analyze / result */
  poster: string;
  posterSubtitle: string;
  href: string;
  dimensionLabels: ScenarioDimensionLabel[];
  /** Other scenario ids for return-loop carousel */
  continuationIds: string[];
};

const DEFAULT_DIMENSIONS: ScenarioDimensionLabel[] = [
  { key: "attraction", emoji: "✨", label: "Притяжение" },
  { key: "stability", emoji: "🤝", label: "Стабильность" },
  { key: "conflicts", emoji: "⚔", label: "Конфликты" },
  { key: "sexuality", emoji: "🔥", label: "Интимность" },
];

const PLAYFUL_SCENARIO_IDS = new Set([
  "living_together",
  "vacation",
  "partner_in_crime",
  "after_wine",
  "home_renovation",
  "best_friends",
  "rule_breaker",
]);

function withToneMode(s: Omit<ScenarioSkin, "toneMode"> & { toneMode?: ToneMode }): ScenarioSkin {
  return {
    ...s,
    toneMode: s.toneMode ?? (PLAYFUL_SCENARIO_IDS.has(s.id) ? "playful" : "serious"),
  };
}

export const COMPATIBILITY_PLAYFUL_SCENARIOS: ScenarioSkin[] = [
  withToneMode({
    id: "after_wine",
    emoji: "🍷",
    title: "После бокала вина",
    hook: "Кто первым говорит лишнее — и кто потом всё объясняет",
    tone: "playful",
    toneMode: "playful",
    poster: "После бокала вина",
    posterSubtitle: "Честность, флирт, споры и смешные решения — когда фильтры ослабевают.",
    href: "/compatibility/analyze?series=after_wine",
    dimensionLabels: [
      { key: "attraction", emoji: "😏", label: "Флирт" },
      { key: "conflicts", emoji: "🙊", label: "Лишняя правда" },
      { key: "stability", emoji: "🍷", label: "Уют вечера" },
      { key: "sexuality", emoji: "✨", label: "Искра" },
    ],
    continuationIds: ["partner_in_crime", "best_friends", "rule_breaker", "love"],
  }),
  withToneMode({
    id: "home_renovation",
    emoji: "🔨",
    title: "Ремонт квартиры",
    hook: "Плитка, сроки, нервы — кто сдаётся первым",
    tone: "domestic",
    toneMode: "playful",
    poster: "Ремонт квартиры",
    posterSubtitle: "Стресс-тест пары: выбор плитки три недели vs «и так сойдёт».",
    href: "/compatibility/analyze?series=home_renovation",
    dimensionLabels: [
      { key: "conflicts", emoji: "🧱", label: "Нервы" },
      { key: "stability", emoji: "📐", label: "План ремонта" },
      { key: "attraction", emoji: "🎨", label: "Вкус" },
      { key: "sexuality", emoji: "😮‍💨", label: "Выживание" },
    ],
    continuationIds: ["living_together", "money_together", "rule_breaker", "after_wine"],
  }),
  withToneMode({
    id: "best_friends",
    emoji: "😂",
    title: "Лучшие друзья",
    hook: "Если вы не пара — а опора, подколы и ревность к другим",
    tone: "playful",
    toneMode: "playful",
    poster: "Лучшие друзья",
    posterSubtitle: "Дружба без романтики — но с химией и своими правилами.",
    href: "/compatibility/analyze?series=best_friends",
    dimensionLabels: [
      { key: "stability", emoji: "🤝", label: "Опора" },
      { key: "attraction", emoji: "😄", label: "Лёгкость" },
      { key: "conflicts", emoji: "👀", label: "Ревность" },
      { key: "sexuality", emoji: "🚫", label: "Граница" },
    ],
    continuationIds: ["partner_in_crime", "after_wine", "vacation", "office"],
  }),
  withToneMode({
    id: "rule_breaker",
    emoji: "🕵",
    title: "Кто нарушит правила",
    hook: "Кто первым нарушит «мы так решили»",
    tone: "playful",
    toneMode: "playful",
    poster: "Кто нарушит правила",
    posterSubtitle: "Игровой сценарий: ставки приняты, дисциплина под вопросом.",
    href: "/compatibility/analyze?series=rule_breaker",
    dimensionLabels: [
      { key: "conflicts", emoji: "⏰", label: "Опоздания" },
      { key: "stability", emoji: "📜", label: "Договорённости" },
      { key: "attraction", emoji: "🎭", label: "Азарт" },
      { key: "sexuality", emoji: "😈", label: "Дерзость" },
    ],
    continuationIds: ["partner_in_crime", "office", "living_together", "after_wine"],
  }),
];

export const COMPATIBILITY_PRIMARY_SCENARIOS: ScenarioSkin[] = [
  withToneMode({
    id: "love",
    emoji: "❤️",
    title: "Любовь",
    hook: "Насколько легко строить эмоциональную близость",
    tone: "romantic",
    poster: "Любовь",
    posterSubtitle: "Притяжение, нежность и то, что для каждого значит «быть рядом».",
    href: "/compatibility/analyze?topic=love",
    dimensionLabels: [
      { key: "attraction", emoji: "💫", label: "Притяжение" },
      { key: "stability", emoji: "🤍", label: "Близость" },
      { key: "conflicts", emoji: "🌊", label: "Эмоциональные волны" },
      { key: "sexuality", emoji: "🔥", label: "Страсть" },
    ],
    continuationIds: ["living_together", "conflict_style", "sex", "vacation"],
  }),
  withToneMode({
    id: "living_together",
    emoji: "🏡",
    title: "Living Together",
    hook: "Кто съест чужой йогурт и кто контролирует термostat",
    tone: "domestic",
    poster: "Living Together",
    posterSubtitle: "Быт, границы и ритм двоих — без иллюзий про «идеальный дом».",
    href: "/compatibility/analyze?series=living_together",
    dimensionLabels: [
      { key: "stability", emoji: "🏠", label: "Быт и ритм" },
      { key: "conflicts", emoji: "🧦", label: "Мелкие войны" },
      { key: "attraction", emoji: "☕", label: "Уют рядом" },
      { key: "sexuality", emoji: "🛋", label: "Тепло дома" },
    ],
    continuationIds: ["money_together", "conflict_style", "partner_in_crime", "love"],
  }),
  withToneMode({
    id: "office",
    emoji: "💼",
    title: "Office Compatibility",
    hook: "Reply All, дедлайны и кто раздражается на встречи",
    tone: "office",
    poster: "Office Compatibility",
    posterSubtitle: "Роли, темп и давление — когда вы не только пара, но и команда.",
    href: "/compatibility/analyze?series=office",
    dimensionLabels: [
      { key: "stability", emoji: "📋", label: "Надёжность" },
      { key: "conflicts", emoji: "📧", label: "Рабочие трения" },
      { key: "attraction", emoji: "🎯", label: "Синергия" },
      { key: "sexuality", emoji: "⚡", label: "Энергия" },
    ],
    continuationIds: ["business", "conflict_style", "apocalypse", "work"],
  }),
  withToneMode({
    id: "sex",
    emoji: "🔥",
    title: "Sexual Dynamics",
    hook: "Кто инициирует, кто быстрее открывается",
    tone: "romantic",
    poster: "Sexual Dynamics",
    posterSubtitle: "Секс, желание, темп и согласие — прямо про тело и динамику пары.",
    href: "/compatibility/analyze?topic=sex",
    dimensionLabels: [
      { key: "sexuality", emoji: "🔥", label: "Химия" },
      { key: "attraction", emoji: "💫", label: "Притяжение" },
      { key: "conflicts", emoji: "🌙", label: "Напряжение" },
      { key: "stability", emoji: "🤍", label: "Доверие" },
    ],
    continuationIds: ["love", "conflict_style", "living_together", "vacation"],
  }),
  withToneMode({
    id: "apocalypse",
    emoji: "⚡",
    title: "Apocalypse",
    hook: "Что будет, если жизнь резко станет сложной",
    tone: "dramatic",
    poster: "Apocalypse",
    posterSubtitle:
      "Не про конец света — про увольнение, болезнь, переезд, потерю денег или сильный стресс.",
    href: "/compatibility/analyze?series=apocalypse",
    dimensionLabels: [
      { key: "stability", emoji: "🤝", label: "Поддержка" },
      { key: "conflicts", emoji: "⚔", label: "Конфликт под стрессом" },
      { key: "attraction", emoji: "🧠", label: "Совместные решения" },
      { key: "sexuality", emoji: "💪", label: "Восстановление" },
    ],
    continuationIds: ["conflict_style", "money_together", "living_together", "office"],
  }),
  withToneMode({
    id: "vacation",
    emoji: "✈",
    title: "Vacation Together",
    hook: "Кто собирает чемодан за три дня и кто опаздывает в аэропорт",
    tone: "vacation",
    poster: "Vacation Together",
    posterSubtitle: "Отдых, свобода и ожидания — когда вы вне привычного ритма.",
    href: "/compatibility/analyze?series=vacation",
    dimensionLabels: [
      { key: "attraction", emoji: "🌴", label: "Лёгкость" },
      { key: "stability", emoji: "🗺", label: "Совместный план" },
      { key: "conflicts", emoji: "⏰", label: "Темп и опоздания" },
      { key: "sexuality", emoji: "✨", label: "Искра в поездке" },
    ],
    continuationIds: ["partner_in_crime", "living_together", "love", "travel"],
  }),
  withToneMode({
    id: "money_together",
    emoji: "💰",
    title: "Money Together",
    hook: "Кто копит, кто тратит и кто боится рисков",
    tone: "calm",
    poster: "Money Together",
    posterSubtitle: "Ресурсы, приоритеты и страхи — почти всегда про безопасность.",
    href: "/compatibility/analyze?series=money_together",
    dimensionLabels: [
      { key: "stability", emoji: "🏦", label: "Финансовая опора" },
      { key: "conflicts", emoji: "💸", label: "Споры о тратах" },
      { key: "attraction", emoji: "🎯", label: "Общие цели" },
      { key: "sexuality", emoji: "🛡", label: "Чувство защиты" },
    ],
    continuationIds: ["living_together", "business", "apocalypse", "parenting"],
  }),
  withToneMode({
    id: "parenting",
    emoji: "👶",
    title: "Parenting",
    hook: "Кто мягче, кто строже и как принимаются решения о детях",
    tone: "calm",
    poster: "Parenting",
    posterSubtitle: "Дети усиливают всё — усталость, ответственность и разные модели «как правильно».",
    href: "/compatibility/analyze?series=parenting",
    dimensionLabels: [
      { key: "stability", emoji: "🤱", label: "Опора" },
      { key: "conflicts", emoji: "📏", label: "Разные правила" },
      { key: "attraction", emoji: "💞", label: "Союз родителей" },
      { key: "sexuality", emoji: "🌙", label: "Близость после детей" },
    ],
    continuationIds: ["living_together", "conflict_style", "money_together", "love"],
  }),
  withToneMode({
    id: "conflict_style",
    emoji: "🎭",
    title: "Conflict Style",
    hook: "Кто замолкает, кто хлопает дверью и кто приходит мириться",
    tone: "calm",
    poster: "Conflict Style",
    posterSubtitle: "Как проходит ссора — и что помогает не застревать в одном сценарии.",
    href: "/compatibility/analyze?series=conflict_style",
    dimensionLabels: [
      { key: "conflicts", emoji: "🌪", label: "Острота ссор" },
      { key: "stability", emoji: "🕊", label: "Примирение" },
      { key: "attraction", emoji: "💬", label: "Честность" },
      { key: "sexuality", emoji: "🔥", label: "Страсть после ссоры" },
    ],
    continuationIds: ["love", "living_together", "apocalypse", "office"],
  }),
  withToneMode({
    id: "partner_in_crime",
    emoji: "🎮",
    title: "Partner in Crime",
    hook: "Кто предложит авантюру — и кто потом всё исправит",
    tone: "playful",
    poster: "Partner in Crime",
    posterSubtitle: "Самая весёлая серия: риск, азарт и «ну а что если?»",
    href: "/compatibility/analyze?series=partner_in_crime",
    dimensionLabels: [
      { key: "attraction", emoji: "🎲", label: "Азарт" },
      { key: "stability", emoji: "🛟", label: "Кто спасает" },
      { key: "conflicts", emoji: "😅", label: "Последствия" },
      { key: "sexuality", emoji: "✨", label: "Искра приключений" },
    ],
    continuationIds: ["vacation", "living_together", "office", "love"],
  }),
];

export const COMPATIBILITY_ALL_SCENARIOS: ScenarioSkin[] = [
  ...COMPATIBILITY_PRIMARY_SCENARIOS,
  ...COMPATIBILITY_PLAYFUL_SCENARIOS.filter((p) => !COMPATIBILITY_PRIMARY_SCENARIOS.some((s) => s.id === p.id)),
];

const TOPIC_TO_SCENARIO: Record<string, string> = {
  love: "love",
  living_together: "living_together",
  living: "living_together",
  work: "office",
  sex: "sex",
  money: "money_together",
  parenting: "parenting",
  travel: "vacation",
  conflicts: "conflict_style",
  communication: "conflict_style",
  friendship: "best_friends",
  emotional: "love",
  growth: "love",
};

const SKIN_BY_ID = new Map(COMPATIBILITY_ALL_SCENARIOS.map((s) => [s.id, s]));

export function resolveScenarioId(params: {
  topic?: string | null;
  series?: string | null;
  reading?: string | null;
}): string {
  if (params.series && SKIN_BY_ID.has(params.series)) return params.series;
  if (params.topic) {
    const mapped = TOPIC_TO_SCENARIO[params.topic];
    if (mapped) return mapped;
  }
  return "love";
}

export function getScenarioSkin(id: string): ScenarioSkin {
  return SKIN_BY_ID.get(id) ?? SKIN_BY_ID.get("love")!;
}

export function getContinuationScenarios(currentId: string): ScenarioSkin[] {
  const skin = getScenarioSkin(currentId);
  return skin.continuationIds
    .map((id) => SKIN_BY_ID.get(id))
    .filter((s): s is ScenarioSkin => Boolean(s))
    .slice(0, 6);
}

export function scoreLabelRu(score: number): string {
  if (score >= 82) return "Сильная связь";
  if (score >= 68) return "Хороший потенциал";
  if (score >= 58) return "Нужна настройка";
  return "Сложная динамика";
}

export function defaultDimensions(): ScenarioDimensionLabel[] {
  return DEFAULT_DIMENSIONS;
}

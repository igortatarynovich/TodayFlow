/** Theme-scoped metric labels — hero ring caption per scenario. */

type Band = "high" | "mid" | "low";

function band(score: number): Band {
  if (score >= 82) return "high";
  if (score >= 68) return "mid";
  if (score >= 58) return "low";
  return "low";
}

const SCENARIO_SCORE_LABELS: Record<string, Record<Band, string>> = {
  love: {
    high: "Сильная близость",
    mid: "Хороший потенциал любви",
    low: "Нужна настройка чувств",
  },
  sex: {
    high: "Сильная химия",
    mid: "Химия с нюансами",
    low: "Телесный слой требует внимания",
  },
  office: {
    high: "Сильная рабочая синергия",
    mid: "Работаете, но с трением",
    low: "Сложная командная динамика",
  },
  living_together: {
    high: "Быт держит",
    mid: "Быт с настройкой",
    low: "Дом может быть полем битвы",
  },
  vacation: {
    high: "Dream team в пути",
    mid: "Отпуск выживете",
    low: "Лучше раздельные маршруты",
  },
  money_together: {
    high: "Финансовый союз",
    mid: "Деньги — зона договорённостей",
    low: "Деньги — зона риска",
  },
  parenting: {
    high: "Сильная родительская команда",
    mid: "Родительство с компромиссами",
    low: "Разные модели воспитания",
  },
  conflict_style: {
    high: "Ссоры не застревают",
    mid: "Конфликты управляемы",
    low: "Жёсткий конфликтный цикл",
  },
  apocalypse: {
    high: "Держитесь в кризисе",
    mid: "Кризис — стресс-тест",
    low: "Под давлением — хрупко",
  },
};

const DEFAULT_LABELS: Record<Band, string> = {
  high: "Сильная связь",
  mid: "Хороший потенциал",
  low: "Нужна настройка",
};

export function scenarioScoreLabelRu(scenarioId: string, score: number): string {
  const table = SCENARIO_SCORE_LABELS[scenarioId] ?? DEFAULT_LABELS;
  const b = band(score);
  return table[b] ?? DEFAULT_LABELS[b];
}

export function funnelSectionTitle(scenarioId: string | null | undefined): string {
  if (!scenarioId) return "Сферы (легкость без усилий)";
  const titles: Record<string, string> = {
    love: "Любовь — где вы сильны и где трёт",
    sex: "Интимность — показатели по теме",
    office: "Работа и команда — ваши метрики",
    living_together: "Быт вместе — ключевые сферы",
    vacation: "Отпуск — что важно для вас двоих",
    money_together: "Деньги — сферы без иллюзий",
    parenting: "Родительство — где совпадаете",
    conflict_style: "Конфликты — ваши показатели",
    apocalypse: "Кризис — стресс-тест пары",
  };
  return titles[scenarioId] ?? "Сферы по выбранной теме";
}

export function dimensionsSectionTitle(scenarioId: string, isPlayful: boolean): string {
  if (isPlayful) return "Статистика по сценарию";
  const titles: Record<string, string> = {
    love: "Любовь — четыре показателя",
    sex: "Интимность — четыре показателя",
    office: "Офис — четыре показателя",
    living_together: "Быт — четыре показателя",
    vacation: "Отпуск — четыре показателя",
    money_together: "Деньги — четыре показателя",
    parenting: "Родительство — четыре показателя",
    conflict_style: "Конфликты — четыре показателя",
    apocalypse: "Кризис — четыре показателя",
  };
  return titles[scenarioId] ?? "Показатели по теме";
}

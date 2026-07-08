import type { FlowPracticesChromeLocale } from "@/components/today/flowPracticesMainTabChrome";
import { t } from "@/lib/i18n";

export type CompatibilityRelationMode = "romantic" | "family" | "parent_child" | "business";

export type CompatWebModeSpec = {
  id: "love" | "family" | "office" | "parenting";
  scenarioId: string;
  relationMode: CompatibilityRelationMode;
  emoji: string;
  title: string;
  hint: string;
};

export type CompatibilityWebChrome = {
  pageTitle: string;
  pageSubtitle: string;
  railReadTitle: string;
  railReadWorks: string;
  railReadFriction: string;
  railReadStep: string;
  railHint: string;
  railHistoryTitle: string;
  railHistoryEmpty: string;
  railQuote: string;
  hubContextEyebrow: string;
  hubLoginHint: string;
  hubLoginCta: string;
  hubNeedSecondHint: string;
  hubAddPersonCta: string;
  hubPairEyebrow: string;
  hubProfile1Aria: string;
  hubProfile2Aria: string;
  hubAddOption: string;
  hubManageCircle: string;
  hubCalculateLoading: string;
  hubCalculateCta: string;
  resultTabsAria: string;
  resultScoreTitle: string;
  resultDimensionsTitle: string;
  resultWorks: string;
  resultFails: string;
  resultFriction: string;
  resultPotential: string;
  resultNextStep: string;
  resultDeepSummary: string;
  resultMainThought: string;
  resultDeepTitle: string;
  resultShare: string;
  resultSave: string;
  potentialHigh: string;
  potentialMedium: string;
  potentialLow: string;
  scenarioLove: string;
  scenarioOffice: string;
  scenarioFamily: string;
  modes: CompatWebModeSpec[];
  scenarioTabs: Array<{ id: string; label: string }>;
};

export function compatibilityWebChromeBundle(locale: FlowPracticesChromeLocale): CompatibilityWebChrome {
  const loc = locale === "ru" ? "ru" : "en";
  const tr = (key: string, defaultRu: string, defaultEn?: string) =>
    t(key, loc === "ru" ? defaultRu : (defaultEn ?? defaultRu), undefined, loc);

  const modes: CompatWebModeSpec[] =
    loc === "ru"
      ? [
          { id: "love", scenarioId: "love", relationMode: "romantic", emoji: "♥", title: "Любовь", hint: "Романтика и чувства" },
          { id: "family", scenarioId: "living_together", relationMode: "family", emoji: "⌂", title: "Семья", hint: "Родственные узы" },
          { id: "office", scenarioId: "office", relationMode: "business", emoji: "◆", title: "Работа", hint: "Деловое партнёрство" },
          { id: "parenting", scenarioId: "parenting", relationMode: "parent_child", emoji: "◎", title: "Родитель/ребёнок", hint: "Дети и родители" },
        ]
      : [
          { id: "love", scenarioId: "love", relationMode: "romantic", emoji: "♥", title: "Love", hint: "Romance and feelings" },
          { id: "family", scenarioId: "living_together", relationMode: "family", emoji: "⌂", title: "Family", hint: "Family bonds" },
          { id: "office", scenarioId: "office", relationMode: "business", emoji: "◆", title: "Work", hint: "Business partnership" },
          { id: "parenting", scenarioId: "parenting", relationMode: "parent_child", emoji: "◎", title: "Parent/child", hint: "Children and parents" },
        ];

  return {
    pageTitle: tr("compat.web.pageTitle", "Совместимость", "Compatibility"),
    pageSubtitle: tr(
      "compat.web.pageSubtitle",
      "Динамика связи — не приговор, а карта для разговора и выбора.",
      "Relationship dynamics are a map for conversation and choice — not a verdict.",
    ),
    railReadTitle: tr("compat.web.rail.readTitle", "Как читать результат", "How to read the result"),
    railReadWorks: tr("compat.web.rail.works", "Что работает", "What works"),
    railReadFriction: tr("compat.web.rail.friction", "Зоны трения", "Friction zones"),
    railReadStep: tr("compat.web.rail.step", "Один шаг", "One step"),
    railHint: tr(
      "compat.web.rail.hint",
      "Выбери контекст связи и двух людей — расчёт покажет опоры и зоны настройки.",
      "Pick a relationship context and two people — the reading shows supports and tuning zones.",
    ),
    railHistoryTitle: tr("compat.web.rail.history", "История", "History"),
    railHistoryEmpty: tr(
      "compat.web.rail.historyEmpty",
      "Здесь появятся недавние пары после первого расчёта.",
      "Recent pairs will appear here after your first reading.",
    ),
    railQuote: tr(
      "compat.web.rail.quote",
      "«Звёзды лишь указывают путь, но идём по нему мы сами».",
      "“The stars point the way, but we walk it ourselves.”",
    ),
    hubContextEyebrow: tr("compat.web.hub.context", "Контекст связи", "Relationship context"),
    hubLoginHint: tr(
      "compat.web.hub.loginHint",
      "Войди, чтобы выбрать людей из своего круга и сохранять историю расчётов.",
      "Sign in to pick people from your circle and save reading history.",
    ),
    hubLoginCta: tr("compat.web.hub.loginCta", "Войти", "Sign in"),
    hubNeedSecondHint: tr(
      "compat.web.hub.needSecond",
      "Добавь второго человека в круг — партнёра, друга или коллегу.",
      "Add a second person to your circle — partner, friend, or colleague.",
    ),
    hubAddPersonCta: tr("compat.web.hub.addPerson", "Добавить человека", "Add person"),
    hubPairEyebrow: tr("compat.web.hub.pair", "Пара", "Pair"),
    hubProfile1Aria: tr("compat.web.hub.profile1Aria", "Первый человек", "First person"),
    hubProfile2Aria: tr("compat.web.hub.profile2Aria", "Второй человек", "Second person"),
    hubAddOption: tr("compat.web.hub.addOption", "+ Добавить", "+ Add"),
    hubManageCircle: tr("compat.web.hub.manageCircle", "Управлять кругом людей", "Manage people circle"),
    hubCalculateLoading: tr("compat.web.hub.calculateLoading", "Собираю разбор…", "Building reading…"),
    hubCalculateCta: tr("compat.web.hub.calculateCta", "Рассчитать →", "Calculate →"),
    resultTabsAria: tr("compat.web.result.tabsAria", "Сценарий связи", "Relationship scenario"),
    resultScoreTitle: tr("compat.web.result.score", "Общий счёт", "Overall score"),
    resultDimensionsTitle: tr("compat.web.result.dimensions", "Измерения", "Dimensions"),
    resultWorks: tr("compat.web.result.works", "Что работает", "What works"),
    resultFails: tr("compat.web.result.fails", "Что не работает", "What doesn't work"),
    resultFriction: tr("compat.web.result.friction", "Где трение", "Where friction shows up"),
    resultPotential: tr("compat.web.result.potential", "Потенциал", "Potential"),
    resultNextStep: tr("compat.web.result.nextStep", "Следующий шаг", "Next step"),
    resultDeepSummary: tr("compat.web.result.deepSummary", "Глубже и уточнение", "Go deeper"),
    resultMainThought: tr("compat.web.result.mainThought", "Главная мысль", "Main thought"),
    resultDeepTitle: tr("compat.web.result.deepTitle", "Глубокий разбор", "Deep dive"),
    resultShare: tr("compat.web.result.share", "Поделиться", "Share"),
    resultSave: tr("compat.web.result.save", "Сохранить", "Save"),
    potentialHigh: tr("compat.web.potential.high", "ВЫСОКИЙ", "HIGH"),
    potentialMedium: tr("compat.web.potential.medium", "СРЕДНИЙ", "MEDIUM"),
    potentialLow: tr("compat.web.potential.low", "НИЗКИЙ", "LOW"),
    scenarioLove: tr("compat.web.scenario.love", "Любовь", "Love"),
    scenarioOffice: tr("compat.web.scenario.office", "Работа", "Work"),
    scenarioFamily: tr("compat.web.scenario.family", "Семья", "Family"),
    modes,
    scenarioTabs: [
      { id: "love", label: tr("compat.web.scenario.love", "Любовь", "Love") },
      { id: "office", label: tr("compat.web.scenario.office", "Работа", "Work") },
      { id: "living_together", label: tr("compat.web.scenario.family", "Семья", "Family") },
    ],
  };
}

export function potentialLabelFromScore(score: number, locale: FlowPracticesChromeLocale): string {
  const c = compatibilityWebChromeBundle(locale);
  if (score >= 70) return c.potentialHigh;
  if (score >= 45) return c.potentialMedium;
  return c.potentialLow;
}

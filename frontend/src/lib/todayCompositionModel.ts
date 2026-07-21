import type { MorningRitualData } from "@/components/today/todayPageUtils";
import type { TodayContractV1, TodayContractDomainId } from "@/lib/todayContract";
import { isDomainLensPresent } from "@/lib/todayContract";
import { buildTodayNarrativeV1 } from "@/lib/todayNarrativeFromContract";
import {
  buildCentralDayThought,
  extractThemeShort,
  isRuUserFacingText,
  resolveTodayThemeHeadline,
} from "@/lib/todaySynthesisTextPolicy";
import type { DayEngagementState } from "@/lib/todayDayEngagement";
import { buildTodayExperienceTheme } from "@/components/today/todayExperienceModel";
import {
  guideCanonicalPrimaryStepLine,
  parseCoreMessageForUi,
} from "@/components/today/todayGuideActionable";

const DOMAIN_ORDER: TodayContractDomainId[] = ["money_work", "relationships", "family"];

const DOMAIN_SPHERE_LABEL: Record<TodayContractDomainId, string> = {
  money_work: "Работа",
  relationships: "Отношения",
  family: "Дом и семья",
};

export type TodayInfluenceCard = {
  id: string;
  kind: "tarot" | "number" | "moon" | "color" | "stone";
  label: string;
  title: string;
  detail?: string;
  pickable?: boolean;
};

export type TodaySphereItem = {
  id: string;
  sphere: string;
  comment: string;
};

export type TodayCautionItem = {
  id: string;
  area: string;
  comment: string;
};

export type TodayStrengthenTool = {
  id: "practice" | "affirmation" | "meditation" | "asceticism" | "intention";
  label: string;
  title: string;
  detail: string;
  duration?: string;
};

export type TodayDayAction = {
  id: "goal" | "practice" | "asceticism" | "habit";
  label: string;
  description: string;
  href?: string;
};

export type TodayGrowthStep = {
  id: string;
  title: string;
  body: string;
  state: "past" | "current" | "future";
};

export type TodayCompositionViewModel = {
  hero: {
    centralThought: string;
    themeShort: string;
    themeHeadline: string;
    tagline: string;
  };
  whyInfluences: TodayInfluenceCard[];
  influences: TodayInfluenceCard[];
  supported: TodaySphereItem[];
  caution: TodayCautionItem[];
  strengthen: TodayStrengthenTool[];
  actions: TodayDayAction[];
  growthArc: TodayGrowthStep[];
  /** Для вечернего закрытия и цели дня */
  focusTitle: string;
};

class TextRegistry {
  private seen = new Set<string>();

  claim(raw: string | null | undefined): string | null {
    const t = raw?.replace(/\s+/g, " ").trim();
    if (!t) return null;
    const key = t.toLowerCase();
    if (this.seen.has(key)) return null;
    this.seen.add(key);
    const normalized = t.replace(/[.!?]+$/, "");
    return `${normalized}.`;
  }

  has(raw: string | null | undefined): boolean {
    const t = raw?.replace(/\s+/g, " ").trim().toLowerCase();
    return Boolean(t && this.seen.has(t));
  }
}

function firstSentence(text: string): string {
  const m = text.match(/^[^.!?]+[.!?]?/);
  return (m?.[0] ?? text).trim();
}

function buildInfluences(input: {
  cardName: string | null;
  cardMeaning: string | null;
  numerologyValue: string | null;
  numerologyMeaning: string | null;
  morningRitualData: MorningRitualData | null;
  colorLine?: string | null;
  stoneLine?: string | null;
}): TodayInfluenceCard[] {
  const out: TodayInfluenceCard[] = [];

  if (input.cardName && input.cardName !== "—") {
    const detail = input.cardMeaning?.trim();
    out.push({
      id: "tarot",
      kind: "tarot",
      label: "Карта дня",
      title: input.cardName,
      detail: detail && isRuUserFacingText(detail) ? detail : undefined,
      pickable: true,
    });
  }

  if (input.numerologyValue && input.numerologyValue !== "—") {
    const detail = input.numerologyMeaning?.trim();
    out.push({
      id: "number",
      kind: "number",
      label: "Число дня",
      title: input.numerologyValue,
      detail: detail && isRuUserFacingText(detail) ? detail : undefined,
      pickable: true,
    });
  }

  const lunar = input.morningRitualData?.celestial_events?.lunar_phase;
  if (lunar?.name) {
    out.push({
      id: "moon",
      kind: "moon",
      label: "Луна",
      title: lunar.name,
      detail: lunar.themes?.trim() || undefined,
    });
  }

  if (input.stoneLine?.trim()) {
    out.push({
      id: "stone",
      kind: "stone",
      label: "Камень дня",
      title: input.stoneLine.trim(),
    });
  }

  if (input.colorLine?.trim()) {
    out.push({
      id: "color",
      kind: "color",
      label: "Цвет дня",
      title: input.colorLine.trim(),
    });
  }

  return out;
}

function buildSupported(contract: TodayContractV1, registry: TextRegistry): TodaySphereItem[] {
  const items: TodaySphereItem[] = [];
  for (const id of DOMAIN_ORDER) {
    const domain = contract.domains[id];
    if (!isDomainLensPresent(domain)) continue;
    const comment = registry.claim(domain.opportunity?.trim() || domain.status?.trim());
    if (!comment) continue;
    items.push({ id, sphere: DOMAIN_SPHERE_LABEL[id], comment });
  }
  return items.slice(0, 4);
}

function buildCaution(contract: TodayContractV1, registry: TextRegistry): TodayCautionItem[] {
  const items: TodayCautionItem[] = [];
  for (const id of DOMAIN_ORDER) {
    const domain = contract.domains[id];
    if (!isDomainLensPresent(domain)) continue;
    const risk = registry.claim(domain.risk?.trim());
    if (!risk) continue;
    items.push({ id, area: DOMAIN_SPHERE_LABEL[id], comment: risk });
  }
  return items.slice(0, 3);
}

function buildAffirmation(themeHeadline: string, cardName: string | null): string {
  const essence = themeHeadline.replace(/^Сегодня[:\s—-]*/i, "").replace(/[.!?]+$/, "");
  if (cardName && cardName !== "—") {
    return `Сегодня я держу ритм — ${essence.toLowerCase()}, опираясь на «${cardName}».`;
  }
  return `Сегодня я двигаюсь в своём ритме — ${essence.toLowerCase()}.`;
}

function buildStrengthen(
  contract: TodayContractV1,
  registry: TextRegistry,
  themeHeadline: string,
  cardName: string | null,
  numberValue: string | null,
  caution: TodayCautionItem[],
): TodayStrengthenTool[] {
  const growth = registry.claim(contract.personal_growth.development_point?.trim());
  const firstRisk = caution[0]?.comment.replace(/[.!?]+$/, "") ?? null;

  const practiceTitle = growth ? firstSentence(growth) : "Пять минут тишины без экрана.";
  const affirmation = buildAffirmation(themeHeadline, cardName);

  return [
    {
      id: "practice",
      label: "Практика дня",
      title: practiceTitle,
      detail: "Небольшое действие, которое лучше всего соответствует сегодняшнему состоянию.",
      duration: "5 мин",
    },
    {
      id: "affirmation",
      label: "Аффирмация дня",
      title: affirmation,
      detail: "Прочитай вслух или сохрани как якорь.",
    },
    {
      id: "meditation",
      label: "Медитация дня",
      title: "Три минуты спокойного дыхания",
      detail: growth
        ? `Сфокусируйся на одной мысли: ${firstSentence(growth).replace(/[.!?]+$/, "")}.`
        : "Следи за вдохом и выдохом — без задач и экрана.",
      duration: "3 мин",
    },
    {
      id: "asceticism",
      label: "Аскеза дня",
      title: firstRisk ? `Сегодня без ${firstRisk.toLowerCase()}` : "Сегодня без лишней срочности",
      detail: "Небольшое осознанное ограничение, подходящее именно этому дню.",
    },
    {
      id: "intention",
      label: "Намерение дня",
      title:
        registry.claim(contract.primary_action?.trim()) ??
        "Один понятный шаг, который захочется завершить к вечеру.",
      detail: numberValue && numberValue !== "—" ? `Число ${numberValue} поддерживает это намерение.` : "Зафиксируй или прими предложенное.",
    },
  ];
}

function buildActions(): TodayDayAction[] {
  return [
    { id: "goal", label: "Поставить цель", description: "Один шаг, который захочется завершить к вечеру." },
    { id: "practice", label: "Выбрать практику", description: "Короткое действие под сегодняшний ритм." },
    { id: "asceticism", label: "Начать аскезу", description: "Осознанное ограничение на сегодня.", href: "/practices" },
    { id: "habit", label: "Добавить привычку", description: "Закрепи то, что уже работает.", href: "/habits" },
  ];
}

function buildGrowthArc(isFirstToday: boolean): TodayGrowthStep[] {
  return [
    {
      id: "today",
      title: "Сегодня",
      body: isFirstToday ? "Первый день" : "Твой ритм",
      state: "current",
    },
    {
      id: "tomorrow",
      title: "Завтра",
      body: "Связь со вчерашним днём",
      state: "future",
    },
    {
      id: "week",
      title: "Через неделю",
      body: "Первые закономерности",
      state: "future",
    },
    {
      id: "month",
      title: "Через месяц",
      body: "Персональные карты",
      state: "future",
    },
    {
      id: "year",
      title: "Через год",
      body: "Личная история",
      state: "future",
    },
  ];
}

export function applyEngagementToViewModel(
  vm: TodayCompositionViewModel,
  engagement: DayEngagementState,
): TodayCompositionViewModel {
  if (!engagement.tarotPickedName && !engagement.numberConfirmed && !engagement.dayGoal) {
    return vm;
  }

  const cardName = engagement.tarotPickedName ?? vm.influences.find((i) => i.kind === "tarot")?.title ?? null;
  const strengthen = vm.strengthen.map((tool) => {
    if (tool.id === "affirmation" && cardName) {
      return {
        ...tool,
        title: buildAffirmation(vm.hero.themeHeadline, cardName),
        detail: "Ты выбрал карту — аффирмация подстроилась под неё.",
      };
    }
    if (tool.id === "practice" && engagement.practiceStarted) {
      return { ...tool, detail: "Практика запущена — вернись к ней в течение дня." };
    }
    if (tool.id === "intention" && engagement.dayGoal) {
      return { ...tool, title: engagement.dayGoal, detail: "Твоя цель на сегодня." };
    }
    return tool;
  });

  const influences = vm.influences.map((inf) => {
    if (inf.kind === "tarot" && engagement.tarotPickedName) {
      return { ...inf, title: engagement.tarotPickedName, detail: "Ты выбрал эту карту как якорь дня." };
    }
    if (inf.kind === "number" && engagement.numberConfirmed) {
      return { ...inf, detail: inf.detail ?? "Число подтверждено как символ дня." };
    }
    return inf;
  });

  return {
    ...vm,
    strengthen,
    influences,
    focusTitle: engagement.dayGoal ?? vm.focusTitle,
  };
}

/** Overlay catalog practice from GET /practices/current onto the strengthen practice card. */
export function applyRecommendedPracticeToStrengthen(
  tools: TodayStrengthenTool[],
  practice: { id: string; title: string; description: string; duration_minutes?: number } | null | undefined,
  options?: { lowEnergy?: boolean },
): TodayStrengthenTool[] {
  if (!practice?.title?.trim()) return tools;

  return tools.map((tool) => {
    if (tool.id !== "practice") return tool;
    const detail = practice.description?.trim() || tool.detail;
    return {
      ...tool,
      title: practice.title.trim(),
      detail: options?.lowEnergy ? `${detail} Сегодня — мягкий темп.` : detail,
      duration: practice.duration_minutes ? `${practice.duration_minutes} мин` : tool.duration,
    };
  });
}

export function buildTodayCompositionViewModel(input: {
  contract: TodayContractV1;
  cardName: string | null;
  cardMeaning: string | null;
  numerologyValue: string | null;
  numerologyMeaning: string | null;
  morningRitualData: MorningRitualData | null;
  colorLine?: string | null;
  stoneLine?: string | null;
  isFirstToday?: boolean;
}): TodayCompositionViewModel {
  const registry = new TextRegistry();
  const narrative = buildTodayNarrativeV1(input.contract);

  const themeHeadline = resolveTodayThemeHeadline(input.contract);
  const centralThought = buildCentralDayThought(input.contract);
  const themeShort = extractThemeShort(input.contract, themeHeadline);
  const tagline =
    registry.claim(narrative.mainThought.subline) ??
    registry.claim(input.contract.personal_growth.development_point) ??
    registry.claim(narrative.manifestations[0]?.line) ??
    "Сегодня лучше двигаться последовательно, чем быстро.";

  const influences = buildInfluences(input);
  const whyInfluences = influences.filter((i) => i.detail || i.kind === "moon");
  const supported = buildSupported(input.contract, registry);
  const caution = buildCaution(input.contract, registry);
  const strengthen = buildStrengthen(
    input.contract,
    registry,
    themeHeadline,
    input.cardName,
    input.numerologyValue,
    caution,
  );

  const focusTitle =
    registry.claim(input.contract.primary_action?.trim()) ??
    supported[0]?.comment ??
    tagline.replace(/[.!?]+$/, "");

  return {
    hero: { centralThought, themeShort, themeHeadline, tagline },
    whyInfluences,
    influences,
    supported,
    caution,
    strengthen,
    actions: buildActions(),
    growthArc: buildGrowthArc(Boolean(input.isFirstToday)),
    focusTitle,
  };
}

/** Подмешивает LLM guide (headline, core_message, primary step) поверх contract-based VM. */
export function applyGuideNarrativeToCompositionViewModel(
  vm: TodayCompositionViewModel,
  guideNarrativePayload: Record<string, unknown> | null | undefined,
): TodayCompositionViewModel {
  if (!guideNarrativePayload) return vm;

  const theme = buildTodayExperienceTheme(guideNarrativePayload, vm.hero.themeHeadline);
  const core = parseCoreMessageForUi(guideNarrativePayload);
  const tagline =
    (core?.kind === "structured" ? core.body : core?.kind === "paragraphs" ? core.paragraphs[0] : null) ||
    theme.meta ||
    vm.hero.tagline;

  const primaryAction = guideCanonicalPrimaryStepLine(
    guideNarrativePayload,
    [vm.focusTitle, vm.strengthen.find((t) => t.id === "intention")?.title ?? ""],
    vm.focusTitle,
  );

  const themeHeadline = theme.headline.trim() || vm.hero.themeHeadline;
  const themeShort =
    themeHeadline.length > 48 ? `${themeHeadline.slice(0, 45).trim()}…` : themeHeadline;

  const strengthen = vm.strengthen.map((tool) =>
    tool.id === "intention"
      ? { ...tool, title: primaryAction, detail: "Один шаг на сегодня." }
      : tool,
  );

  return {
    ...vm,
    hero: {
      ...vm.hero,
      themeHeadline,
      centralThought: themeHeadline,
      themeShort,
      tagline,
    },
    focusTitle: primaryAction,
    strengthen,
  };
}

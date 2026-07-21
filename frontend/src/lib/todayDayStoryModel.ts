import type { MorningRitualData } from "@/components/today/todayPageUtils";
import { getTodayTarotCardRu } from "@/components/today/todayTarotCardsRu";
import type { TodayContractV1 } from "@/lib/todayContract";
import { isDomainLensPresent } from "@/lib/todayContract";
import type { DayEngagementState } from "@/lib/todayDayEngagement";
import { isLowEnergyMood } from "@/lib/todayDayDialogue";
import {
  buildTodayDaySpine,
  type TodaySkyCard,
} from "@/lib/todayDaySpine";
import { resolveTodayDayColorGuide, type TodayDayColorGuide } from "@/lib/todayDayColorGuide";
import { buildTodaySphereFocus, type TodaySphereFocus } from "@/lib/todayDaySphereFocus";
import { resolveTodayRitualPhase, type TodayRitualPhase } from "@/lib/todayRitualGate";
import {
  buildTodayDayGreeting,
  resolveTodayDayPhase,
  type TodayDayGreeting,
  type TodayDayPhase,
} from "@/lib/todayDayGreeting";
import type {
  TodayCompositionViewModel,
  TodayInfluenceCard,
  TodayStrengthenTool,
} from "@/lib/todayCompositionModel";
import {
  dayStoryEveningPrompt,
  dayStoryWhyLines,
  hasAuthoritativeDayStory,
} from "@/lib/todayContractMapper";
import { parseDayLayerPayload } from "@/components/today/todayRitualSignals";
import { buildEveningPrompt } from "@/lib/todayUnifiedSynthesis";
import type { TodayContractDomainId } from "@/lib/todayContract";
import type { TodaySphereFocusCard } from "@/lib/todayDaySphereFocus";

export type TodayGlanceCard = {
  id: string;
  sphere: string;
  comment: string;
  tone: "strong" | "helpful";
};

export type TodayInfluenceStory = TodayInfluenceCard & {
  impactLine: string;
  storyLine: string;
};

export type TodayRitualImpact = {
  title: string;
  headline: string;
  body: string;
};

export type TodayDayStoryViewModel = TodayCompositionViewModel & {
  phase: TodayDayPhase;
  ritualPhase: TodayRitualPhase;
  isEveningSurface: boolean;
  personalizedReady: boolean;
  greeting: TodayDayGreeting;
  pulseLabel: string;
  pulse: string;
  glance: { supported: TodayGlanceCard[]; helpful: TodayGlanceCard[] };
  sphereFocus: TodaySphereFocus;
  colorGuide: TodayDayColorGuide | null;
  whyStory: string[];
  astroContext: TodayInfluenceStory[];
  skyCards: TodaySkyCard[];
  tarotImpact: TodayRitualImpact | null;
  numberImpact: TodayRitualImpact | null;
  strengthenLinked: TodayStrengthenTool[];
  strengthenPreview: TodayStrengthenTool[];
  dayContinuityNote: string;
  eveningQuestion: string | null;
  eveningReflectionPrompt: string | null;
  ritualUnlockHint: string | null;
  ritualTransformBanner: string | null;
};

function buildWhyStoryFromContract(contract: TodayContractV1): string[] {
  return dayStoryWhyLines(contract);
}

function firstSentence(text: string): string {
  const trimmed = text.trim();
  if (!trimmed) return "";
  const match = trimmed.match(/^[^.!?]+[.!?]?/);
  return (match?.[0] ?? trimmed).trim();
}

function buildGlanceCards(
  contract: TodayContractV1,
  sphereFocus: TodaySphereFocus,
): TodayDayStoryViewModel["glance"] {
  const peak = sphereFocus.cards.find((card) => card.role === "peak");
  const caution = sphereFocus.cards.find((card) => card.role === "caution");

  const supportedComment =
    peak?.body != null
      ? firstSentence(peak.body)
      : isDomainLensPresent(contract.domains.relationships)
        ? firstSentence(contract.domains.relationships.opportunity ?? "")
        : "";
  const helpfulComment =
    caution?.body != null
      ? firstSentence(caution.body)
      : isDomainLensPresent(contract.domains.money_work)
        ? firstSentence(contract.domains.money_work.risk ?? "")
        : "";

  return {
    supported: supportedComment
      ? [{ id: "supported", sphere: peak?.sphere ?? "Поддержано", comment: supportedComment, tone: "strong" as const }]
      : [],
    helpful: helpfulComment
      ? [{ id: "helpful", sphere: caution?.sphere ?? "Внимание", comment: helpfulComment, tone: "helpful" as const }]
      : [],
  };
}

function buildTarotImpactFromSpine(
  cardId: number,
  cardName: string,
  body: string | null,
): TodayRitualImpact {
  const card = getTodayTarotCardRu(cardId);
  return {
    title: card?.nameRu ?? cardName,
    headline: "Символ дня",
    body: body ?? card?.bodyRu ?? "Карта открывает другой слой смысла — не повторяя общую тему.",
  };
}

function buildNumberImpactFromSpine(numerologyValue: string, body: string | null): TodayRitualImpact {
  return {
    title: `Число ${numerologyValue}`,
    headline: "Ритм дня",
    body: body ?? `Число ${numerologyValue} задаёт темп — не тему, а способ прожить день.`,
  };
}

function buildStrengthenLinked(
  tools: TodayStrengthenTool[],
  input: {
    cardName: string | null;
    cardId: number | null;
    numerologyValue: string | null;
    thesis: string;
    weakLabel: string | null;
    ritualComplete: boolean;
    lowEnergy: boolean;
  },
): TodayStrengthenTool[] {
  if (!input.ritualComplete) return [];
  // PR-3: keep API-backed copy; do not invent titles from card/theme.
  return tools.filter((tool) => !(input.lowEnergy && tool.id === "asceticism"));
}

function buildStrengthenPreview(tools: TodayStrengthenTool[]): TodayStrengthenTool[] {
  // Show recommendation copy as-is before ritual; do not invent lock fillers.
  return tools;
}

function buildRitualTransformBanner(input: {
  tarotPicked: boolean;
  numberConfirmed: boolean;
  personalizedReady: boolean;
}): string | null {
  if (input.personalizedReady) {
    return "День собран: карта, число и практики настроены под тебя.";
  }
  if (input.numberConfirmed) {
    return "Число подтверждено — осталось собрать практику и обещание.";
  }
  if (input.tarotPicked) {
    return "Карта выбрана — символ дня меняет практику, аффирмацию и вечерний вопрос.";
  }
  return null;
}

function buildDayContinuityNote(isFirstToday: boolean): string {
  if (isFirstToday) {
    return "Сегодня — первая страница. Завтра посмотрим, что изменилось после твоих шагов.";
  }
  return "Сегодня ты уже добавил новую страницу в свою историю. Завтра мы посмотрим, что изменилось после сегодняшних решений.";
}

function skyCardsToAstroContext(cards: TodaySkyCard[]): TodayInfluenceStory[] {
  return cards.map((c) => ({
    id: c.id,
    kind: c.id === "moon" ? "moon" : c.id === "tarot" ? "tarot" : c.id === "number" ? "number" : "color",
    label: c.label,
    title: c.title,
    detail: c.story,
    impactLine: c.label,
    storyLine: c.story,
  }));
}

export function buildTodayDayStoryViewModel(input: {
  base: TodayCompositionViewModel;
  contract: TodayContractV1;
  userName?: string | null;
  yesterdayClosed: boolean;
  todayOpened: boolean;
  isFirstToday?: boolean;
  dateISO: string;
  cardName: string | null;
  cardMeaning: string | null;
  tarotMainId?: number | null;
  numerologyValue: string | null;
  numerologyMeaning: string | null;
  morningRitualData: MorningRitualData | null;
  colorLine?: string | null;
  stoneLine?: string | null;
  sunSignLabel?: string | null;
  engagement: DayEngagementState;
  now?: Date;
}): TodayDayStoryViewModel {
  const phase = resolveTodayDayPhase(input.now?.getHours());
  const isEveningSurface = phase === "evening" || phase === "night";

  const ritualPhase = resolveTodayRitualPhase(input.engagement);
  const personalizedReady = ritualPhase === "complete";
  const pickedCardName = input.engagement.tarotPickedName ?? input.cardName;
  const pickedCardId = input.engagement.tarotPickedId ?? input.tarotMainId ?? null;
  const tarotPicked = Boolean(input.engagement.tarotPickedName);

  const spine = buildTodayDaySpine({
    contract: input.contract,
    morningRitualData: input.morningRitualData,
    moodId: input.engagement.morningMoodId,
    dayGoal: input.engagement.dayGoal,
    cardId: pickedCardId,
    cardName: pickedCardName,
    numerologyValue: input.numerologyValue,
    numerologyMeaning: input.numerologyMeaning,
    colorLine: input.colorLine,
    stoneLine: input.stoneLine,
    sunSignLabel: input.sunSignLabel,
    ritualComplete: personalizedReady,
    tarotPicked,
  });

  const greeting = buildTodayDayGreeting({
    phase,
    userName: input.userName,
    tagline: spine.thesis,
    yesterdayClosed: input.yesterdayClosed,
    todayOpened: input.todayOpened,
    isEveningSurface,
    isFirstToday: input.isFirstToday,
  });

  const sphereFocus = buildTodaySphereFocus(input.contract);
  const glance = buildGlanceCards(input.contract, sphereFocus);
  const apiColor = input.morningRitualData?.celestial_events?.daily_symbols?.color;
  const colorGuide = resolveTodayDayColorGuide({
    name: input.colorLine ?? apiColor?.name,
    api: apiColor,
  });
  const pulseLabel = "Энергия дня";

  const tarotImpact =
    pickedCardName && ritualPhase !== "tarot_pending" && pickedCardId != null
      ? buildTarotImpactFromSpine(
          pickedCardId,
          pickedCardName,
          tarotPicked ? spine.tarotBody : null,
        )
      : null;

  const numberImpact =
    personalizedReady && input.numerologyValue && input.numerologyValue !== "—"
      ? buildNumberImpactFromSpine(input.numerologyValue, spine.numberBody)
      : null;

  const strengthenLinked = buildStrengthenLinked(input.base.strengthen, {
    cardName: pickedCardName,
    cardId: pickedCardId,
    numerologyValue: input.numerologyValue,
    thesis: spine.thesis,
    weakLabel: sphereFocus.cards.find((c) => c.role === "caution")?.sphere ?? null,
    ritualComplete: personalizedReady,
    lowEnergy: isLowEnergyMood(input.engagement.morningMoodId),
  });

  const strengthenPreview = buildStrengthenPreview(input.base.strengthen);

  const tarotCard = pickedCardId != null ? getTodayTarotCardRu(pickedCardId) : undefined;
  const eveningQuestion = personalizedReady
    ? buildEveningPrompt({ dateISO: input.dateISO, tarotCard })
    : null;
  const eveningReflectionPrompt =
    (hasAuthoritativeDayStory(input.contract) ? dayStoryEveningPrompt(input.contract) : null) ??
    spine.eveningLine;

  const hero = {
    ...input.base.hero,
    centralThought: spine.thesis,
    themeShort: spine.themeShort,
  };

  return {
    ...input.base,
    hero,
    phase,
    ritualPhase,
    isEveningSurface,
    personalizedReady,
    greeting,
    pulseLabel,
    pulse: spine.pulse,
    glance,
    sphereFocus,
    colorGuide,
    whyStory: buildWhyStoryFromContract(input.contract),
    astroContext: skyCardsToAstroContext(spine.skyCards),
    skyCards: spine.skyCards,
    tarotImpact,
    numberImpact,
    strengthenLinked,
    strengthenPreview,
    dayContinuityNote: buildDayContinuityNote(Boolean(input.isFirstToday)),
    eveningQuestion,
    eveningReflectionPrompt,
    ritualUnlockHint: spine.ritualUnlockHint,
    ritualTransformBanner: buildRitualTransformBanner({
      tarotPicked,
      numberConfirmed: input.engagement.numberConfirmed,
      personalizedReady,
    }),
  };
}

function narrativeField(payload: Record<string, unknown> | null | undefined, key: string): string | null {
  if (!payload) return null;
  const v = payload[key];
  return typeof v === "string" && v.trim() ? v.trim() : null;
}

function sphereCardDomainId(card: TodaySphereFocusCard): TodayContractDomainId | null {
  const match = card.id.match(/^(?:peak2?|caution)-(money_work|relationships|family)$/);
  return match ? (match[1] as TodayContractDomainId) : null;
}

function scenarioTieInForCard(
  tieIns: Record<string, unknown>,
  card: TodaySphereFocusCard,
): string | null {
  const domain = sphereCardDomainId(card);
  if (!domain) return null;
  if (domain === "relationships") {
    return narrativeField(tieIns as Record<string, unknown>, "love");
  }
  if (domain === "family") {
    return narrativeField(tieIns as Record<string, unknown>, "family");
  }
  if (card.role === "caution") {
    return (
      narrativeField(tieIns as Record<string, unknown>, "money") ??
      narrativeField(tieIns as Record<string, unknown>, "career")
    );
  }
  return narrativeField(tieIns as Record<string, unknown>, "career");
}

/** Подмешивает day_layer / spheres / evening поверх contract + guide story. */
export function applySupplementaryNarrativesToDayStory(
  story: TodayDayStoryViewModel,
  contract: TodayContractV1,
  input: {
    dayLayerPayload?: Record<string, unknown> | null;
    spheresPayload?: Record<string, unknown> | null;
    eveningPayload?: Record<string, unknown> | null;
  },
): TodayDayStoryViewModel {
  if (hasAuthoritativeDayStory(contract)) return story;

  let next = story;

  const dayLayer = parseDayLayerPayload(input.dayLayerPayload);
  if (dayLayer.nudgeMessage) {
    next = { ...next, pulse: dayLayer.nudgeMessage };
  } else {
    const thesisReminder = narrativeField(input.spheresPayload, "thesis_reminder");
    if (thesisReminder) {
      next = { ...next, pulse: thesisReminder };
    }
  }

  const tieInsRaw = input.spheresPayload?.scenario_tie_ins;
  if (tieInsRaw && typeof tieInsRaw === "object" && !Array.isArray(tieInsRaw)) {
    const tieIns = tieInsRaw as Record<string, unknown>;
    const sphereFocus = {
      ...next.sphereFocus,
      cards: next.sphereFocus.cards.map((card) => {
        const tieIn = scenarioTieInForCard(tieIns, card);
        if (!tieIn) return card;
        return card.role === "caution"
          ? { ...card, body: tieIn, releaseLine: card.releaseLine ?? tieIn }
          : { ...card, body: tieIn };
      }),
    };
    next = {
      ...next,
      sphereFocus,
      glance: buildGlanceCards(contract, sphereFocus),
    };
  }

  if (dayLayer.questionPrompt && next.personalizedReady) {
    next = { ...next, eveningQuestion: dayLayer.questionPrompt };
  }

  const eveningClosure =
    narrativeField(input.eveningPayload, "closure_invitation") ??
    narrativeField(input.eveningPayload, "outlook_preamble") ??
    narrativeField(input.eveningPayload, "panel_intro");
  if (eveningClosure) {
    next = { ...next, eveningReflectionPrompt: eveningClosure };
  }

  return next;
}

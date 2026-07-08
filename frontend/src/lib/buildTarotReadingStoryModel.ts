import type { TarotAnswerV1 } from "@/lib/tarotAnswerContract";
import type { GuidanceReadingResult } from "@/components/guidance/GuidanceStructuredResult";
import type { TarotConcernDomain } from "@/lib/tarotQuestionFlowCanon";
import { buildTarotNextRoutes } from "@/lib/buildTarotNextRoutes";
import { stripTarotAppendFromExplanation } from "@/components/guidance/guidanceResultChrome";
import { getTodayTarotCardRu } from "@/components/today/todayTarotCardsRu";
import {
  cleanTarotCardMeaning,
  dedupeSentences,
  formatTarotCardCount,
  humanizeTarotPositionLabel,
  sanitizeTarotStoryText,
} from "@/lib/tarotReadingStorySanitize";

export type TarotStoryCard = {
  id: string;
  positionLabel: string;
  cardName: string;
  storyLine: string;
  cardId?: number | null;
  orientation?: string;
  faceSrc?: string | null;
  isReversed?: boolean;
};

export type TarotStoryAction = {
  id: "clarify" | "save" | "compatibility" | "today" | "goal" | "practice" | "return";
  label: string;
  description?: string;
  href?: string;
  disabled?: boolean;
  onClick?: () => void;
};

export type TarotReadingResonance = "very" | "partial" | "none";

export type TarotFollowUpChip = {
  id: string;
  label: string;
};

export type TarotCardInsight = {
  positionLabel: string;
  cardNameRu: string;
  cardId: number;
  orientation: string;
  line: string;
};

export type TarotReadingStoryModel = {
  question: string;
  mainAnswer: string;
  storyNarrative: string | null;
  cardInsights: TarotCardInsight[];
  insights: {
    holding: string | null;
    shifting: string | null;
    attention: string | null;
  };
  todaySuggestion: string | null;
  followUpPrompt: string | null;
  followUpChips: TarotFollowUpChip[];
  actions: TarotStoryAction[];
  isClarification?: boolean;
};

export type TarotSpreadStoryInput = {
  question?: string | null;
  spreadTitle: string;
  cards: Array<{
    cardId: number;
    englishName: string;
    orientation: "upright" | "reversed" | string;
    position: string | { id: string; title: string; prompt?: string | null };
    meaning: string;
    uprightText?: string;
    reversedText?: string;
  }>;
  reading?: {
    meaning?: string | null;
    manifestation?: string | null;
    caution?: string | null;
    next_step?: string | null;
    synthesis_why?: string | null;
    actions_today?: string[] | null;
    self_question?: string | null;
    profile_lens?: string | null;
    profile_lens_applied?: boolean | null;
    insight_holding?: string | null;
    insight_shifting?: string | null;
    insight_attention?: string | null;
    today_suggestion?: string | null;
    follow_up_prompt?: string | null;
    follow_up_chips?: TarotFollowUpChip[] | null;
    card_insights?: Array<{
      position_label: string;
      card_name_ru: string;
      card_id: number;
      orientation: string;
      line: string;
    }> | null;
  } | null;
  profileIdentity?: string | null;
  concernDomain?: TarotConcernDomain | string | null;
  locale: "ru" | "en";
  saveHref?: string | null;
  clarifyAvailable?: boolean;
  onClarify?: () => void;
  showCompatibility?: boolean;
};

function localizeCardName(cardId: number | null | undefined, englishName: string, locale: "ru" | "en"): string {
  if (locale === "ru" && cardId != null) {
    const ru = getTodayTarotCardRu(cardId);
    if (ru?.nameRu) return ru.nameRu;
  }
  return englishName;
}

function buildCardStoryLine(
  cardId: number | null | undefined,
  meaning: string,
  orientation: string,
  locale: "ru" | "en",
  uprightText?: string,
  reversedText?: string,
): string {
  const cleaned = cleanTarotCardMeaning(meaning);
  if (cleaned.length >= 24) return cleaned;

  if (locale === "ru" && cardId != null) {
    const ru = getTodayTarotCardRu(cardId);
    if (ru) {
      const orientLine = orientation === "reversed" ? ru.riskRu || ru.bodyRu : ru.bodyRu || ru.leadRu;
      if (orientLine) return sanitizeTarotStoryText(orientLine);
    }
  }

  const fallback = orientation === "reversed" ? reversedText : uprightText;
  if (fallback?.trim()) return sanitizeTarotStoryText(fallback);
  return cleaned;
}

function buildMainAnswerFromParts(parts: Array<string | null | undefined>): string {
  return dedupeSentences(parts.filter(Boolean) as string[]);
}

function defaultFollowUpChips(locale: "ru" | "en", concernDomain?: string | null): TarotFollowUpChip[] {
  const isRu = locale === "ru";
  const domain = (concernDomain || "").toLowerCase();

  const chip = (id: string, ru: string, en: string) => ({ id, label: isRu ? ru : en });

  const byDomain: Record<string, TarotFollowUpChip[]> = {
    relationships: [
      chip("let_go", "Отпустить", "Let go"),
      chip("understand", "Понять, что произошло", "Understand what happened"),
      chip("clarity_feelings", "Понять свои чувства", "Understand my feelings"),
      chip("stop_waiting", "Перестать ждать", "Stop waiting"),
      chip("unsure", "Пока не знаю", "Not sure yet"),
    ],
    work: [
      chip("stay_clarity", "Понять, стоит ли оставаться", "See if I should stay"),
      chip("change_direction", "Сменить направление", "Change direction"),
      chip("rest_first", "Сначала восстановиться", "Rest first"),
      chip("one_step", "Сделать один шаг", "Take one step"),
      chip("unsure", "Пока не знаю", "Not sure yet"),
    ],
    money: [
      chip("keep", "Сохранить то, что уже есть", "Keep what I have"),
      chip("income", "Увеличить доход", "Increase income"),
      chip("worry_less", "Перестать постоянно переживать из-за денег", "Worry less about money"),
      chip("delayed_step", "Сделать шаг, который давно откладываю", "Take a step I've been delaying"),
      chip("unsure", "Пока не могу определить", "Can't tell yet"),
    ],
    family: [
      chip("boundaries", "Прояснить границы", "Clarify boundaries"),
      chip("soft_talk", "Мягкий разговор", "A gentle talk"),
      chip("distance", "Взять дистанцию", "Take distance"),
      chip("care_self", "Позаботиться о себе", "Care for myself"),
      chip("unsure", "Пока не знаю", "Not sure yet"),
    ],
    decision: [
      chip("choose_a", "Ближе вариант А", "Closer to option A"),
      chip("choose_b", "Ближе вариант Б", "Closer to option B"),
      chip("need_time", "Нужно время", "Need time"),
      chip("fear_named", "Назвать страх", "Name the fear"),
      chip("unsure", "Пока не знаю", "Not sure yet"),
    ],
    conflict: [
      chip("speak_up", "Сказать прямо", "Speak up"),
      chip("pause", "Взять паузу", "Take a pause"),
      chip("see_other", "Увидеть другую сторону", "See the other side"),
      chip("protect_self", "Защитить себя", "Protect myself"),
      chip("unsure", "Пока не знаю", "Not sure yet"),
    ],
    growth: [
      chip("next_step", "Следующий шаг", "Next step"),
      chip("slow_down", "Замедлиться", "Slow down"),
      chip("trust_inner", "Довериться внутреннему", "Trust my inner voice"),
      chip("new_angle", "Новый взгляд", "A new angle"),
      chip("unsure", "Пока не знаю", "Not sure yet"),
    ],
    inner_state: [
      chip("rest", "Отдохнуть", "Rest"),
      chip("name_feeling", "Назвать чувство", "Name the feeling"),
      chip("one_kindness", "Одна доброта к себе", "One kindness to myself"),
      chip("support", "Попросить опору", "Ask for support"),
      chip("unsure", "Пока не знаю", "Not sure yet"),
    ],
  };

  if (byDomain[domain]) return byDomain[domain];

  return [
    chip("clarity", "Стало понятнее", "Clearer now"),
    chip("same", "Пока без изменений", "No change yet"),
    chip("new_questions", "Появились новые вопросы", "New questions"),
    chip("need_time", "Нужно время", "Need time"),
  ];
}

function buildActions(params: {
  locale: "ru" | "en";
  clarifyAvailable?: boolean;
  onClarify?: () => void;
  saveHref?: string | null;
  saveLabel?: string | null;
  showCompatibility?: boolean;
}): TarotStoryAction[] {
  const { locale, clarifyAvailable, onClarify, saveHref, saveLabel, showCompatibility = true } = params;
  const isRu = locale === "ru";

  const actions: TarotStoryAction[] = [
    {
      id: "clarify",
      label: isRu ? "Задать уточняющий вопрос" : "Ask a clarifying question",
      description: isRu
        ? "Одна дополнительная карта — если хочется сузить фокус."
        : "One more card if you want to narrow the focus.",
      disabled: !clarifyAvailable,
      onClick: onClarify,
    },
    {
      id: "save",
      label: saveLabel || (isRu ? "Сохранить вывод" : "Save this reading"),
      description: isRu ? "Зафиксируй мысль, пока она свежая." : "Capture the insight while it's fresh.",
      href: saveHref || "/journal",
    },
  ];

  if (showCompatibility) {
    actions.push({
      id: "compatibility",
      label: isRu ? "Открыть совместимость с этим человеком" : "Open compatibility with this person",
      description: isRu ? "Посмотри динамику пары, если вопрос про отношения." : "Explore pair dynamics if this is about someone.",
      href: "/compatibility",
    });
  }

  return actions;
}

export function buildTarotReadingStoryFromGuidance(
  result: GuidanceReadingResult,
  locale: "ru" | "en",
  options?: {
    clarifyAvailable?: boolean;
    onClarify?: () => void;
    showCompatibility?: boolean;
  },
): TarotReadingStoryModel {
  const explanation = stripTarotAppendFromExplanation(result.answer.explanation);
  const mainAnswer = buildMainAnswerFromParts([
    result.interpretation?.summary,
    result.interpretation?.core_insight,
    result.answer.forecast,
    explanation,
    result.answer.clarity,
  ]);

  const storyNarrative =
    result.interpretation?.why_outline?.trim() ||
    buildMainAnswerFromParts(result.tarot_cards.map((c) => c.meaning).slice(0, 3)) ||
    null;

  const todaySuggestion =
    result.answer.today?.trim() ||
    result.interpretation?.action?.trim() ||
    null;

  const isRu = locale === "ru";
  const followUpPrompt =
    result.interpretation?.action?.trim() ||
    (isRu ? "Что тебе сейчас хочется больше?" : "What do you want most right now?");

  const saveHref = result.flow_bridge?.href || "/journal";

  const cardInsights: TarotCardInsight[] = result.tarot_cards.map((card, idx) => ({
    positionLabel: humanizeTarotPositionLabel(card.position, card.position_id, card.position_prompt, locale),
    cardNameRu: localizeCardName(card.card_id, card.name, locale),
    cardId: card.card_id ?? idx,
    orientation: card.orientation,
    line: buildCardStoryLine(card.card_id, card.meaning, card.orientation, locale),
  }));

  return {
    question: result.question.trim(),
    mainAnswer,
    storyNarrative,
    cardInsights,
    insights: {
      holding: result.interpretation?.core_insight?.trim() || null,
      shifting: result.interpretation?.profile_bridge?.trim() || null,
      attention: result.answer.decision?.trim() || null,
    },
    todaySuggestion,
    followUpPrompt,
    followUpChips: defaultFollowUpChips(locale, result.lane === "love" ? "relationships" : result.lane),
    isClarification: Boolean(result.is_clarification),
    actions: buildActions({
      locale,
      clarifyAvailable: options?.clarifyAvailable,
      onClarify: options?.onClarify,
      saveHref,
      saveLabel: result.flow_bridge?.label || null,
      showCompatibility: options?.showCompatibility ?? true,
    }),
  };
}

export function buildTarotReadingStoryFromAnswer(
  input: TarotSpreadStoryInput & { tarotAnswer: TarotAnswerV1 },
): TarotReadingStoryModel {
  const answer = input.tarotAnswer;
  const mainAnswer = sanitizeTarotStoryText(answer.main_answer?.trim() || "");
  const storyNarrative =
    answer.story_narrative?.trim() ||
    answer.new_angle?.trim() ||
    input.reading?.synthesis_why?.trim() ||
    null;

  const todaySuggestion =
    answer.today_suggestion?.trim() ||
    answer.next_step?.trim() ||
    input.reading?.today_suggestion?.trim() ||
    null;

  const followUpPrompt =
    answer.follow_up_prompt?.trim() ||
    input.reading?.follow_up_prompt?.trim() ||
    (input.locale === "ru" ? "Что тебе сейчас хочется больше?" : "What do you want most right now?");

  const followUpChips =
    answer.follow_up_chips?.filter((c) => c.id && c.label) ||
    input.reading?.follow_up_chips?.filter((c) => c.id && c.label) ||
    defaultFollowUpChips(input.locale, input.concernDomain);

  const cardInsights: TarotCardInsight[] =
    input.reading?.card_insights?.map((c) => ({
      positionLabel: c.position_label,
      cardNameRu: c.card_name_ru,
      cardId: c.card_id,
      orientation: c.orientation,
      line: sanitizeTarotStoryText(c.line),
    })) ||
    input.cards.map((card, idx) => {
      const positionTitle = typeof card.position === "string" ? card.position : card.position.title;
      const positionId = typeof card.position === "string" ? card.position : card.position.id;
      const positionPrompt = typeof card.position === "string" ? null : card.position.prompt;
      return {
        positionLabel: humanizeTarotPositionLabel(positionTitle, positionId, positionPrompt, input.locale),
        cardNameRu: localizeCardName(card.cardId, card.englishName, input.locale),
        cardId: card.cardId,
        orientation: card.orientation,
        line: buildCardStoryLine(card.cardId, card.meaning, card.orientation, input.locale, card.uprightText, card.reversedText),
      };
    });

  return {
    question: (answer.question_text || input.question || "").trim(),
    mainAnswer,
    storyNarrative: storyNarrative ? sanitizeTarotStoryText(storyNarrative) : null,
    cardInsights,
    insights: {
      holding: answer.insights?.holding?.trim() || input.reading?.insight_holding?.trim() || null,
      shifting: answer.insights?.shifting?.trim() || answer.new_angle?.trim() || input.reading?.insight_shifting?.trim() || null,
      attention: answer.insights?.attention?.trim() || answer.risk?.trim() || answer.attention?.trim() || input.reading?.insight_attention?.trim() || null,
    },
    todaySuggestion: todaySuggestion ? sanitizeTarotStoryText(todaySuggestion) : null,
    followUpPrompt,
    followUpChips,
    actions: buildTarotNextRoutes({
      locale: input.locale,
      concernDomain: input.concernDomain,
      saveHref: input.saveHref,
    }),
  };
}

export function buildTarotReadingStoryFromSpread(input: TarotSpreadStoryInput): TarotReadingStoryModel {
  const mainAnswer = sanitizeTarotStoryText(input.reading?.meaning?.trim() || "");

  const storyNarrative = input.reading?.synthesis_why?.trim()
    ? sanitizeTarotStoryText(input.reading.synthesis_why)
    : null;

  const todaySuggestion =
    input.reading?.today_suggestion?.trim() ||
    input.reading?.actions_today?.[0]?.trim() ||
    input.reading?.next_step?.trim() ||
    null;

  const followUpPrompt =
    input.reading?.follow_up_prompt?.trim() ||
    (input.locale === "ru" ? "Что тебе сейчас хочется больше?" : "What do you want most right now?");

  const followUpChips =
    input.reading?.follow_up_chips?.filter((c) => c.id && c.label) ||
    defaultFollowUpChips(input.locale, input.concernDomain);

  const cardInsights: TarotCardInsight[] =
    input.reading?.card_insights?.map((c) => ({
      positionLabel: c.position_label,
      cardNameRu: c.card_name_ru,
      cardId: c.card_id,
      orientation: c.orientation,
      line: sanitizeTarotStoryText(c.line),
    })) ||
    input.cards.map((card, idx) => {
      const positionTitle = typeof card.position === "string" ? card.position : card.position.title;
      const positionId = typeof card.position === "string" ? card.position : card.position.id;
      const positionPrompt = typeof card.position === "string" ? null : card.position.prompt;
      return {
        positionLabel: humanizeTarotPositionLabel(positionTitle, positionId, positionPrompt, input.locale),
        cardNameRu: localizeCardName(card.cardId, card.englishName, input.locale),
        cardId: card.cardId,
        orientation: card.orientation,
        line: buildCardStoryLine(card.cardId, card.meaning, card.orientation, input.locale, card.uprightText, card.reversedText),
      };
    });

  return {
    question: input.question?.trim() || (input.locale === "ru" ? "Твой вопрос" : "Your question"),
    mainAnswer,
    storyNarrative,
    cardInsights,
    insights: {
      holding: input.reading?.insight_holding?.trim() || null,
      shifting: input.reading?.insight_shifting?.trim() || null,
      attention: input.reading?.insight_attention?.trim() || null,
    },
    todaySuggestion: todaySuggestion ? sanitizeTarotStoryText(todaySuggestion) : null,
    followUpPrompt,
    followUpChips,
    actions: buildTarotNextRoutes({
      locale: input.locale,
      concernDomain: input.concernDomain,
      saveHref: input.saveHref,
    }),
  };
}

// Kept for journey/events — card metadata without surfacing encyclopedia UI.
export function buildTarotStoryCardsFromSpread(input: TarotSpreadStoryInput): TarotStoryCard[] {
  return input.cards.map((card, idx) => {
    const positionTitle = typeof card.position === "string" ? card.position : card.position.title;
    const positionId = typeof card.position === "string" ? card.position : card.position.id;
    const positionPrompt = typeof card.position === "string" ? null : card.position.prompt;
    return {
      id: `${positionId}-${card.cardId}-${idx}`,
      positionLabel: humanizeTarotPositionLabel(positionTitle, positionId, positionPrompt, input.locale),
      cardName: localizeCardName(card.cardId, card.englishName, input.locale),
      storyLine: buildCardStoryLine(
        card.cardId,
        card.meaning,
        card.orientation,
        input.locale,
        card.uprightText,
        card.reversedText,
      ),
      cardId: card.cardId,
      orientation: card.orientation,
      isReversed: card.orientation === "reversed",
    };
  });
}

export function formatTarotSpreadLine(spreadTitle: string, cardCount: number, locale: "ru" | "en"): string {
  return `${spreadTitle} · ${formatTarotCardCount(cardCount || 1, locale)}`;
}

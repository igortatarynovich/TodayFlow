import type { FlowPracticesChromeLocale } from "@/components/today/flowPracticesMainTabChrome";
import { t } from "@/lib/i18n";

export type TarotReadingStoryChrome = {
  questionEyebrow: string;
  mainAnswerEyebrow: string;
  mainAnswerKicker: string;
  storyEyebrow: string;
  storyKicker: string;
  symbolsKicker: string;
  cardsEyebrow: string;
  insightHoldingTitle: string;
  insightShiftingTitle: string;
  insightAttentionTitle: string;
  todayEyebrow: string;
  followUpThanks: string;
  nextEyebrow: string;
  clarificationBadge: string;
  answerFirstLead: string;
  choiceCompareKicker: string;
  whyDetailsSummary: string;
};

export function tarotReadingStoryChromeBundle(locale: FlowPracticesChromeLocale): TarotReadingStoryChrome {
  const loc = locale === "ru" ? "ru" : "en";
  const tr = (key: string, defaultRu: string, defaultEn?: string) =>
    t(key, loc === "ru" ? defaultRu : (defaultEn ?? defaultRu), undefined, loc);

  return {
    questionEyebrow: tr("tarot.story.questionEyebrow", "Твой вопрос", "Your question"),
    mainAnswerEyebrow: "",
    mainAnswerKicker: tr("tarot.story.mainAnswerKicker", "Ответ на вопрос", "Answer"),
    storyEyebrow: "",
    storyKicker: tr("tarot.story.storyKicker", "Как это связано с вопросом", "How it connects to your question"),
    symbolsKicker: tr("tarot.story.symbolsKicker", "Что показывают карты", "What the cards show"),
    cardsEyebrow: tr("tarot.story.cardsEyebrow", "Что говорят карты", "What the cards say"),
    insightHoldingTitle: tr("tarot.story.insightHolding", "Сейчас самое сложное", "What's hardest now"),
    insightShiftingTitle: tr("tarot.story.insightShifting", "То, что уже начинает меняться", "What's already shifting"),
    insightAttentionTitle: tr("tarot.story.insightAttention", "Попробуй заметить", "Try to notice"),
    todayEyebrow: tr("tarot.story.todayEyebrow", "Что сделать", "What to do"),
    followUpThanks: tr("tarot.story.followUpThanks", "Спасибо — это помогает точнее слышать тебя", "Thank you — this helps us listen better"),
    nextEyebrow: tr("tarot.story.nextEyebrow", "Дальше", "What next"),
    clarificationBadge: tr("tarot.story.clarificationBadge", "Уточнение", "Clarification"),
    answerFirstLead: tr(
      "tarot.story.answerFirstLead",
      "Ответ → шаг → почему",
      "Answer → step → why",
    ),
    choiceCompareKicker: tr("tarot.story.choiceCompareKicker", "Два пути", "Two paths"),
    whyDetailsSummary: tr("tarot.story.whyDetailsSummary", "Показать разбор карт", "Show card analysis"),
  };
}

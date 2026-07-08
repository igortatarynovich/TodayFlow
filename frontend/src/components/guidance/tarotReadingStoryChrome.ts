import type { FlowPracticesChromeLocale } from "@/components/today/flowPracticesMainTabChrome";
import { t } from "@/lib/i18n";

export type TarotReadingStoryChrome = {
  questionEyebrow: string;
  mainAnswerEyebrow: string;
  storyEyebrow: string;
  cardsEyebrow: string;
  insightHoldingTitle: string;
  insightShiftingTitle: string;
  insightAttentionTitle: string;
  todayEyebrow: string;
  followUpThanks: string;
  nextEyebrow: string;
  clarificationBadge: string;
};

export function tarotReadingStoryChromeBundle(locale: FlowPracticesChromeLocale): TarotReadingStoryChrome {
  const loc = locale === "ru" ? "ru" : "en";
  const tr = (key: string, defaultRu: string, defaultEn?: string) =>
    t(key, loc === "ru" ? defaultRu : (defaultEn ?? defaultRu), undefined, loc);

  return {
    questionEyebrow: tr("tarot.story.questionEyebrow", "Твой вопрос", "Your question"),
    mainAnswerEyebrow: "",
    storyEyebrow: "",
    cardsEyebrow: tr("tarot.story.cardsEyebrow", "Что говорят карты", "What the cards say"),
    insightHoldingTitle: tr("tarot.story.insightHolding", "Сейчас самое сложное", "What's hardest now"),
    insightShiftingTitle: tr("tarot.story.insightShifting", "То, что уже начинает меняться", "What's already shifting"),
    insightAttentionTitle: tr("tarot.story.insightAttention", "Попробуй заметить", "Try to notice"),
    todayEyebrow: tr("tarot.story.todayEyebrow", "Что можно сделать сегодня", "One thing for today"),
    followUpThanks: tr("tarot.story.followUpThanks", "Спасибо — это помогает точнее слышать тебя", "Thank you — this helps us listen better"),
    nextEyebrow: tr("tarot.story.nextEyebrow", "Дальше", "What next"),
    clarificationBadge: tr("tarot.story.clarificationBadge", "Уточнение", "Clarification"),
  };
}

import type { FlowPracticesChromeLocale } from "@/components/today/flowPracticesMainTabChrome";
import { t } from "@/lib/i18n";

export type TarotWebHubChrome = {
  pageTitle: string;
  pageSubtitle: string;
  historyTitle: string;
  historyEmpty: string;
  historyOpenLink: string;
  lastQuestionLabel: string;
  openLink: string;
  spreadSectionTitle: string;
  spreadRecommended: string;
  questionPlaceholder: string;
  submitLabel: string;
};

export function tarotWebHubChromeBundle(locale: FlowPracticesChromeLocale): TarotWebHubChrome {
  const loc = locale === "ru" ? "ru" : "en";
  const tr = (key: string, defaultRu: string, defaultEn?: string) =>
    t(key, loc === "ru" ? defaultRu : (defaultEn ?? defaultRu), undefined, loc);

  return {
    pageTitle: tr("tarot.hub.pageTitle", "Таро", "Tarot"),
    pageSubtitle: tr("tarot.hub.pageSubtitle", "Новый угол зрения на вопрос.", "A fresh angle on your question."),
    historyTitle: tr("tarot.hub.historyTitle", "История раскладов", "Reading history"),
    historyEmpty: tr(
      "tarot.hub.historyEmpty",
      "После первого расклада здесь появятся краткие итоги.",
      "After your first reading, short summaries will appear here.",
    ),
    historyOpenLink: tr("tarot.hub.historyOpenLink", "Открыть историю →", "Open history →"),
    lastQuestionLabel: tr("tarot.hub.lastQuestionLabel", "Последний вопрос:", "Last question:"),
    openLink: tr("tarot.hub.openLink", "Открыть →", "Open →"),
    spreadSectionTitle: tr("tarot.hub.spreadSectionTitle", "Выбери расклад", "Choose a spread"),
    spreadRecommended: tr("tarot.hub.spreadRecommended", "Подходит к твоему вопросу", "Fits your question"),
    questionPlaceholder: tr("tarot.hub.questionPlaceholder", "Например: стоит ли менять работу?", "For example: should I change jobs?"),
    submitLabel: tr("tarot.hub.submitLabel", "К ритуалу →", "Continue to ritual →"),
  };
}

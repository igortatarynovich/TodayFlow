import type { FlowPracticesChromeLocale } from "@/components/today/flowPracticesMainTabChrome";
import { t } from "@/lib/i18n";

export type TarotWebHubChrome = {
  pageTitle: string;
  pageSubtitle: string;
  questionStepTitle: string;
  questionStepLead: string;
  directionStepTitle: string;
  directionStepLead: string;
  spreadStepTitle: string;
  spreadStepLead: string;
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
    pageSubtitle: tr(
      "tarot.hub.pageSubtitle",
      "Сначала вопрос и направление — потом расклад. Без стены карт.",
      "Question and direction first — then the spread. No card wall.",
    ),
    questionStepTitle: tr("tarot.hub.questionStepTitle", "Вопрос", "Question"),
    questionStepLead: tr(
      "tarot.hub.questionStepLead",
      "Сформулируй, что сейчас важно — коротко и честно.",
      "Name what matters now — short and honest.",
    ),
    directionStepTitle: tr("tarot.hub.directionStepTitle", "Направление", "Direction"),
    directionStepLead: tr(
      "tarot.hub.directionStepLead",
      "Тема задаёт угол чтения — не отдельный прогноз.",
      "The theme sets the reading angle — not a separate forecast.",
    ),
    spreadStepTitle: tr("tarot.hub.spreadStepTitle", "Расклад", "Spread"),
    spreadStepLead: tr(
      "tarot.hub.spreadStepLead",
      "Формат как шаги: сколько карт и какой фокус.",
      "Format as steps: how many cards and which focus.",
    ),
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

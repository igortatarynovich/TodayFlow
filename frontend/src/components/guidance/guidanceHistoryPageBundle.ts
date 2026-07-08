/**
 * Страница `/guidance/history`: хром + локаль для каталога + формат дат (паритет `ru-RU` / `en-US` с хабом Flow).
 */

import type { FlowPracticesChromeLocale } from "@/components/today/flowPracticesMainTabChrome";
import { guidanceHistoryChromeBundle, type GuidanceHistoryChromeBundle } from "@/components/guidance/guidanceHistoryChrome";

export type GuidanceHistoryPageBundle = {
  chrome: GuidanceHistoryChromeBundle;
  /** Для `guidanceSpreadTitle` / `guidanceTopicLabel` / `formatCardOrientation` (`catalog.ts`). */
  catalogLocale: FlowPracticesChromeLocale;
  formatHistoryDate: (value: string) => string;
};

export function guidanceHistoryPageBundle(locale: FlowPracticesChromeLocale): GuidanceHistoryPageBundle {
  const chrome = guidanceHistoryChromeBundle(locale);
  const dateTag = locale === "ru" ? "ru-RU" : "en-US";

  return {
    chrome,
    catalogLocale: locale,
    formatHistoryDate: (value: string) => {
      const d = new Date(value);
      if (Number.isNaN(d.getTime())) return value;
      return new Intl.DateTimeFormat(dateTag, { day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit" }).format(d);
    },
  };
}

/**
 * Всё, что нужно странице `/guidance` по локали: хром хаба, каталог мастера, подписи групп раскладов.
 * Один вызов — один источник `FlowPracticesChromeLocale` (паритет iOS: те же id и ключи i18n).
 */

import type { FlowPracticesChromeLocale } from "@/components/today/flowPracticesMainTabChrome";
import type { GuidanceSpreadSection } from "@/lib/guidance/catalog";
import { guidanceHubChromeBundle, guidanceHubSpreadSectionLabelsFromBundle, type GuidanceHubChromeBundle } from "@/components/guidance/guidanceHubChrome";
import { guidanceHubWizardCatalogBundle, type GuidanceHubWizardCatalogBundle } from "@/components/guidance/guidanceHubWizardCatalog";

export type GuidanceHubPageBundle = {
  chrome: GuidanceHubChromeBundle;
  wizardCatalog: GuidanceHubWizardCatalogBundle;
  spreadSectionLabels: Record<GuidanceSpreadSection, string>;
};

export function guidanceHubPageBundle(locale: FlowPracticesChromeLocale): GuidanceHubPageBundle {
  const chrome = guidanceHubChromeBundle(locale);
  return {
    chrome,
    wizardCatalog: guidanceHubWizardCatalogBundle(locale),
    spreadSectionLabels: guidanceHubSpreadSectionLabelsFromBundle(chrome),
  };
}

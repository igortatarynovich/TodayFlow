/**
 * Локализованные списки мастера `/guidance` (расклады, темы, чипы).
 * Источник строк — `localizedGuidance*` в `@/lib/guidance/catalog` / ключи `guidance.catalog.*` в i18n.
 * Нативный паритет: подписи и наборы опций в iOS (`GuidanceViewChrome` + те же смыслы id).
 */

import type { FlowPracticesChromeLocale } from "@/components/today/flowPracticesMainTabChrome";
import {
  localizedGuidanceClarificationGoals,
  localizedGuidanceIntimacyFocusOptions,
  localizedGuidanceOutcomeOptions,
  localizedGuidanceRelationshipRoleOptions,
  localizedGuidanceSpreadCatalog,
  localizedGuidanceTopicOptions,
} from "@/lib/guidance/catalog";

export type GuidanceHubWizardCatalogBundle = {
  spreadCatalog: ReturnType<typeof localizedGuidanceSpreadCatalog>;
  topicOptions: ReturnType<typeof localizedGuidanceTopicOptions>;
  outcomeOptions: ReturnType<typeof localizedGuidanceOutcomeOptions>;
  clarificationGoals: ReturnType<typeof localizedGuidanceClarificationGoals>;
  relationshipRoleOptions: ReturnType<typeof localizedGuidanceRelationshipRoleOptions>;
  intimacyFocusOptions: ReturnType<typeof localizedGuidanceIntimacyFocusOptions>;
};

export function guidanceHubWizardCatalogBundle(locale: FlowPracticesChromeLocale): GuidanceHubWizardCatalogBundle {
  const loc = locale;
  return {
    spreadCatalog: localizedGuidanceSpreadCatalog(loc),
    topicOptions: localizedGuidanceTopicOptions(loc),
    outcomeOptions: localizedGuidanceOutcomeOptions(loc),
    clarificationGoals: localizedGuidanceClarificationGoals(loc),
    relationshipRoleOptions: localizedGuidanceRelationshipRoleOptions(loc),
    intimacyFocusOptions: localizedGuidanceIntimacyFocusOptions(loc),
  };
}

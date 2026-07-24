/**
 * TodayFlow Design System — Product Web layer.
 * Canon tokens: `frontend/src/styles/todayflow-foundation.css` (--tf-* / --tf-ds-*)
 * Figma map: `design-system/registry/figmaMap.ts`
 * Live catalog: `/design-system`
 */

export { joinClass } from "@/design-system/utils/joinClass";
export { DS_FIGMA_MAP } from "@/design-system/registry/figmaMap";
export type { DsFigmaCategory } from "@/design-system/registry/figmaMap";

export { DsButton } from "@/design-system/primitives/DsButton";
export { DsCard, DsStatusBadge } from "@/design-system/primitives/DsCard";
export type { DsCardVariant } from "@/design-system/primitives/DsCard";
export {
  DsCheckbox,
  DsChipField,
  DsClassifier,
  DsSearchField,
  DsTextField,
} from "@/design-system/primitives/DsForm";
export {
  DsBody,
  DsCaption,
  DsDisplayTitle,
  DsEyebrow,
  DsHeadline,
  DsIconBadge,
  DsLabel,
  DsPill,
  DsSectionTitle,
  DsSubtitle,
  DsSurface,
  DsTag,
  DsTitle,
} from "@/design-system/primitives/DsTypography";

export { DsOrbitalViz, DsThemePanel, DsThemeViz } from "@/design-system/patterns/DsThemePanel";
export type { DsOrbitalNode } from "@/design-system/patterns/DsThemePanel";
export {
  DsFeatureTile,
  DsInsightTile,
  DsPracticeRow,
  DsQuoteTile,
  DsTagRow,
  DsThemeAsideRow,
} from "@/design-system/patterns/DsTiles";
export { DsAppSidebar, DsMarketingNav, DsPageHeader } from "@/design-system/patterns/DsChrome";
export {
  DsCtaBar,
  DsInsightRow,
  DsMobileShell,
  DsMobileTabBar,
  DsPulseCard,
  DsRitualGate,
  DsRitualGateSection,
} from "@/design-system/patterns/DsMobile";
export type { DsRitualGateKind } from "@/design-system/patterns/DsMobile";
export {
  DsRailPanel,
  DsStreakRing,
  DsTimeline,
  DsWeeklyBars,
} from "@/design-system/patterns/DsRailWidgets";
export type { DsTimelineEvent } from "@/design-system/patterns/DsRailWidgets";

export {
  DsAppShell,
  DsCompositionSlot,
  DsMarketingPage,
  DsMarketingSection,
} from "@/design-system/layouts/DsLayouts";

export { DsCatalog } from "@/design-system/catalog/DsCatalog";

export * from "@/design-system/icons/DsIcons";

export {
  MOTION,
  MotionDrift,
  MotionFlip,
  MotionPulse,
  MotionReveal,
  MotionSettle,
  usePrefersReducedMotion,
} from "@/design-system/motion";
export type { MotionEase } from "@/design-system/motion";

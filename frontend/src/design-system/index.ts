/**
 * TodayFlow Design System — Product Web layer.
 * Canon tokens: `frontend/src/styles/todayflow-foundation.css` (--tf-* / --tf-ds-*)
 * Form Kit: FOUNDATION_UI §15.8 · `docs/design/assets/ui-kit-form-sheet.png`
 * Figma map: `design-system/registry/figmaMap.ts`
 * Live catalog: `/design-system`
 */

export { joinClass } from "@/design-system/utils/joinClass";
export { DS_FIGMA_MAP } from "@/design-system/registry/figmaMap";
export type { DsFigmaCategory } from "@/design-system/registry/figmaMap";

export { DsButton } from "@/design-system/primitives/DsButton";
export { DsCard, DsStatusBadge, cardVariantToTone } from "@/design-system/primitives/DsCard";
export type { DsCardSize, DsCardVariant } from "@/design-system/primitives/DsCard";
export { DsSurface, legacySurfaceVariantToTone } from "@/design-system/primitives/DsSurface";
export type { DsSurfaceTone, DsSurfaceLegacyVariant } from "@/design-system/primitives/DsSurface";
export { DsChip, DsChipCluster } from "@/design-system/primitives/DsChip";
export type { DsChipVariant } from "@/design-system/primitives/DsChip";
export { DsFab } from "@/design-system/primitives/DsFab";
export type { DsFabSize } from "@/design-system/primitives/DsFab";
export {
  DsDotMeter,
  DsMetric,
  DsRadialMeter,
  DsSpectrum,
} from "@/design-system/primitives/DsMeters";
export { DsStarDivider } from "@/design-system/primitives/DsStarDivider";
export { DsAvatar } from "@/design-system/primitives/DsAvatar";
export type { DsAvatarSize } from "@/design-system/primitives/DsAvatar";
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
  DsTag,
  DsTitle,
} from "@/design-system/primitives/DsTypography";
export type { DsInkTone } from "@/design-system/primitives/DsTypography";
export {
  DsCallout,
  DsCapsule,
  DsEmph,
  DsQuote,
  DS_CALLOUT_LABEL_COPY,
} from "@/design-system/primitives/DsCallout";
export type {
  DsCalloutIcon,
  DsCalloutLabel,
  DsCalloutTone,
} from "@/design-system/primitives/DsCallout";

export {
  DsActionCard,
  DsHeroBlock,
  DsHeroFabArrow,
  DsListRow,
  DsMetricCard,
  DsWindowCard,
} from "@/design-system/compositions/DsBlocks";

export { DsPlanet, DsZodiac, DsNumber, DsTarotFace, DsAngle } from "@/design-system/visual";

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
  DsChipGroup,
  DsGlassCard,
  DsHabitStreakRow,
  DsMoodBackground,
  isDsRitualDarkMood,
} from "@/design-system/patterns/DsRitual";
export type { DsChipOption } from "@/design-system/patterns/DsRitual";
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

export { ScreenFlow, ScreenFlowStep, resolveScreenFlowEntryIndex } from "@/design-system/primitives/ScreenFlow";
export type {
  ScreenFlowAxis,
  ScreenFlowChangeReason,
  ScreenFlowStepStatus,
  ScreenFlowStepProps,
  ScreenFlowProps,
} from "@/design-system/primitives/ScreenFlow";

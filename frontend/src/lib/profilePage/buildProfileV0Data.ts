import type { CoreProfile } from "@/lib/types";
import { PROFILE_CHART_DEEP_PATH } from "@/lib/profileRoutes";
import type { Element } from "@/lib/zodiac-utils";
import { buildProfileV0TaxonomySlots } from "./buildProfileV0TaxonomyLayers";
import type {
  ProfileV0LoveCard,
  ProfileV0MoneyCard,
  ProfileV0SocialMirrorCard,
} from "./buildProfileV0SphereCards";
import {
  deriveCompassFromSlots,
  deriveHeaderFromSlots,
  deriveLoveFromSlots,
  deriveMoneyFromSlots,
  deriveNumbersFromSlots,
  deriveSocialMirrorFromSlots,
  deriveWhoFromSlots,
} from "./deriveProfileV0UiFromSlots";
import { buildProfileInsightCoverageReport, formatCoverageReportMarkdown } from "./profileInsightCoverageAudit";
import type { ProfileInsightCoverageReport, ProfileTaxonomyInsightSlot } from "./profileInsightTypes";

export type ProfileV0HeroQuality = {
  title: string;
  subtitle: string;
};

export type ProfileV0Header = {
  displayName: string;
  sunSign: string | null;
  sunSignDisplay: string | null;
  archetypeLabel: string;
  element: Element | null;
  lifePath: number | null;
  tagline: string | null;
  poeticCaption: string | null;
  intro: string | null;
  tension: string | null;
  lifeTheme: string | null;
  metaLine: string | null;
  qualities: ProfileV0HeroQuality[];
};

export type ProfileV0NumerologyRing = {
  id: string;
  value: string;
  label: string;
  /** Reference: что означает это число */
  meaning: string;
};

/** Раскрытие паттерна — полный текст, не обрезка UI */
export type ProfileV0NumberGuide = {
  id: string;
  title: string;
  value: string | null;
  body: string;
};

export type ProfileV0WhoCard = {
  archetypeLabel: string;
  whyManifest: string | null;
  whyInsights: string[];
  layerHint: string;
  runtimeGenerated: boolean;
};

export type ProfileV0NumberRow = {
  key: string;
  value: string;
  caption: string;
  blurb: string | null;
};

export type ProfileV0NumbersCard = {
  hero: ProfileV0NumberRow;
  /** Полный персональный инсайт (число пути) */
  coreInsight: string | null;
  /** Справочник: суть числа пути */
  referenceEssence: string | null;
  second: ProfileV0NumberRow | null;
  third: ProfileV0NumberRow | null;
  rings: ProfileV0NumerologyRing[];
  guides: ProfileV0NumberGuide[];
  expand: {
    whyHero: string;
    birthDay: ProfileV0NumberRow | null;
    togetherDigest: string | null;
  };
};

export type ProfileV0MovementCard = {
  title: string;
  mainText: string;
  rules: string[];
  recommendation: string;
};

export type { ProfileV0LoveCard, ProfileV0MoneyCard, ProfileV0SocialMirrorCard } from "./buildProfileV0SphereCards";

export type ProfileV0TaxonomyAudit = {
  slots: ProfileTaxonomyInsightSlot[];
  coverage: ProfileInsightCoverageReport;
};

export type ProfileV0ViewModel = {
  header: ProfileV0Header;
  who: ProfileV0WhoCard | null;
  numbers: ProfileV0NumbersCard | null;
  socialMirror: ProfileV0SocialMirrorCard | null;
  love: ProfileV0LoveCard | null;
  money: ProfileV0MoneyCard | null;
  action: ProfileV0MovementCard | null;
  deepDiveHref: string;
  /** Internal QA — not for UI */
  taxonomyAudit: ProfileV0TaxonomyAudit;
};

export type BuildProfileV0Input = {
  core: CoreProfile | null;
  displayName: string;
  moonRecoveryHint?: string | null;
  auditProfileLabel?: string;
};

export function buildProfileV0ViewModel({
  core,
  displayName,
  moonRecoveryHint,
  auditProfileLabel,
}: BuildProfileV0Input): ProfileV0ViewModel {
  const taxonomy = buildProfileV0TaxonomySlots({ core, moonRecoveryHint });
  const slots = taxonomy.allSlots;

  const profileLabel =
    auditProfileLabel ||
    [displayName, core?.baseline?.archetype_seed, core?.numerology?.life_path].filter(Boolean).join(" / ");

  const coverage = buildProfileInsightCoverageReport(profileLabel, slots);

  const love = deriveLoveFromSlots(slots);
  const money = deriveMoneyFromSlots(slots);
  const action = deriveCompassFromSlots(slots);

  return {
    header: deriveHeaderFromSlots(core, displayName, slots),
    who: deriveWhoFromSlots(core, slots),
    numbers: deriveNumbersFromSlots(core, slots),
    socialMirror: deriveSocialMirrorFromSlots(slots),
    love: love?.style ? love : null,
    money: money?.approach ? money : null,
    action: action && (action.mainText || action.rules.length > 0 || action.recommendation) ? action : null,
    deepDiveHref: PROFILE_CHART_DEEP_PATH,
    taxonomyAudit: { slots, coverage },
  };
}

export function runProfileTaxonomyAudit(input: BuildProfileV0Input): ProfileInsightCoverageReport {
  return buildProfileV0ViewModel(input).taxonomyAudit.coverage;
}

export { buildProfileV0TaxonomySlots, formatCoverageReportMarkdown };

import type { ProfileV0ViewModel } from "./buildProfileV0Data";
import type { ProfileTaxonomyInsightSlot } from "./profileInsightTypes";
import type { CompactUserModel, CoreProfile } from "@/lib/types";
import { profileCopyToBullets, profileCopyToTags } from "./profileCopyBullets";
import { textsOverlap } from "./profileContentLedger";
import { archetypeDisplayLabel } from "@/lib/visualIdentity/registry";
import { zodiacRuName } from "@/lib/zodiacKnowledge";
import { collectProfileV0UiStrings } from "./profileV0UiStringsAudit";
import { formatCumThemeLabel } from "./cumThemeLabels";
import { PROFILE_SPHERE_THRIVE_TAGS } from "./profileSphereCopy";
import {
  filterProfileCopyList,
  isUsableProfileCopy,
  profileContractMatchesLocale,
} from "./profileCopySafety";
import { getLocale } from "@/lib/i18n";

export type ProfileFrameworkAnchor = {
  id: string;
  label: string;
};

export type ProfileFrameworkCard = {
  id: string;
  title: string;
  anchor: string | null;
  body: string;
};

export type ProfileQuickMapViewModel = {
  pageLabel: string;
  archetype: string;
  identitySummary: string | null;
  strengthens: string[];
  drains: string[];
  decisionStyle: string | null;
  perceivedAs: string[];
  thriveAreas: string[];
  lifeMission: string | null;
  frameworkTitle: string;
  frameworkLead: string | null;
  frameworkAnchors: ProfileFrameworkAnchor[];
  frameworkCards: ProfileFrameworkCard[];
};

export type ProfileChartFrameworkInput = {
  sunAnchor: string | null;
  risingAnchor: string | null;
  mcAnchor: string | null;
  moonAnchor: string | null;
  cards: ProfileFrameworkCard[];
};

function slotText(slots: ProfileTaxonomyInsightSlot[], layer: string, categoryId: string): string | null {
  return slots.find((slot) => slot.layer === layer && slot.categoryId === categoryId)?.text ?? null;
}

function excludeOverlapping(items: string[], reserved: string[]): string[] {
  const blocked = reserved.map((item) => item.trim()).filter(Boolean);
  return items.filter((item) => !blocked.some((r) => textsOverlap(item, r)));
}

function buildThriveAreaTags(model: ProfileV0ViewModel): string[] {
  const { money } = model;
  const slots = model.taxonomyAudit.slots;
  return profileCopyToTags(
    [
      money?.workStyle ? PROFILE_SPHERE_THRIVE_TAGS.career : null,
      money?.approach ? PROFILE_SPHERE_THRIVE_TAGS.money : null,
      slotText(slots, "money", "growth_source"),
      slotText(slots, "compass", "skill"),
      slotText(slots, "compass", "amplify"),
    ],
    5,
  );
}

function mergeBullets(max: number, ...sources: Array<string | null | undefined>): string[] {
  const seen = new Set<string>();
  const out: string[] = [];

  for (const source of sources) {
    for (const bullet of profileCopyToBullets(source, max)) {
      const key = bullet.toLowerCase();
      if (seen.has(key)) continue;
      seen.add(key);
      out.push(bullet);
      if (out.length >= max) return out;
    }
  }

  return out;
}

export function buildProfileQuickMapViewModel(
  model: ProfileV0ViewModel,
  framework: ProfileChartFrameworkInput,
  cum?: CompactUserModel | null,
  profileContract?: CoreProfile["profile_contract_v1"] | null,
): ProfileQuickMapViewModel {
  const slots = model.taxonomyAudit.slots;
  const { header, who, numbers, socialMirror, money, action } = model;

  const identitySummary = header.intro ?? header.tagline ?? who?.whyManifest ?? null;
  const frameworkLeadRaw = who?.whyManifest ?? slotText(slots, "why", "formation");
  const frameworkLead =
    frameworkLeadRaw && identitySummary && textsOverlap(frameworkLeadRaw, identitySummary)
      ? null
      : frameworkLeadRaw;

  const reservedCopy = [
    identitySummary,
    frameworkLead,
    ...framework.cards.map((card) => card.body),
    ...collectProfileV0UiStrings(model).map((entry) => entry.text),
  ].filter((item): item is string => Boolean(item?.trim()));

  const strengthens = excludeOverlapping(
    mergeBullets(
      4,
      slotText(slots, "why", "helps"),
      slotText(slots, "hero", "main_strength"),
      action?.mainText,
      money?.helps,
    ),
    reservedCopy,
  );

  const drains = excludeOverlapping(
    mergeBullets(
      4,
      slotText(slots, "why", "breaks"),
      slotText(slots, "hero", "main_conflict"),
      slotText(slots, "corePattern", "trap"),
      action?.rules[0],
      money?.blocks,
    ),
    reservedCopy,
  );

  const decisionStyle =
    numbers?.guides.find((guide) => guide.id === "decisions")?.body?.trim() ||
    slotText(slots, "corePattern", "decisions") ||
    null;

  const perceivedFromMirror = socialMirror
    ? excludeOverlapping(
        mergeBullets(5, socialMirror.lead, ...socialMirror.observations),
        reservedCopy,
      )
    : [];

  const thriveAreas = buildThriveAreaTags(model);
  const lifeMission = header.lifeTheme ?? slotText(slots, "hero", "life_theme");

  const perceivedAs = excludeOverlapping(
    perceivedFromMirror.length > 0
      ? perceivedFromMirror
      : header.qualities.map((quality) => quality.subtitle).filter(Boolean).slice(0, 5),
    lifeMission ? [lifeMission] : [],
  );

  const frameworkAnchors: ProfileFrameworkAnchor[] = [
    framework.sunAnchor ? { id: "sun", label: framework.sunAnchor } : null,
    framework.risingAnchor ? { id: "rising", label: framework.risingAnchor } : null,
    framework.mcAnchor ? { id: "mc", label: framework.mcAnchor } : null,
    header.lifePath != null ? { id: "lp", label: `Число пути ${header.lifePath}` } : null,
    header.archetypeLabel ? { id: "archetype", label: `Архетип ${header.archetypeLabel}` } : null,
  ].filter((item): item is ProfileFrameworkAnchor => Boolean(item));

  return mergeProfileContractIntoQuickMap(
    mergeCumIntoQuickMap(
    {
      pageLabel: "Профиль",
      archetype: header.archetypeLabel,
      identitySummary,
      strengthens,
      drains,
      decisionStyle,
      perceivedAs,
      thriveAreas,
      lifeMission,
      frameworkTitle: "Почему портрет сложился так",
      frameworkLead,
      frameworkAnchors,
      frameworkCards: framework.cards,
    },
    cum,
    ),
    profileContract,
  );
}

function enrichFrameworkAnchorsFromIdentity(
  anchors: ProfileFrameworkAnchor[],
  identity: CompactUserModel["identity"] | undefined,
): ProfileFrameworkAnchor[] {
  if (!identity) return anchors;

  const labels = anchors.map((anchor) => anchor.label.toLowerCase());
  const hasMoon = labels.some((label) => label.includes("луна"));
  const hasRising = labels.some((label) => label.includes("асцендент"));
  const additions: ProfileFrameworkAnchor[] = [];

  const moonSign = identity.moon_sign?.trim();
  if (moonSign && !hasMoon) {
    additions.push({ id: "moon", label: `Луна в ${zodiacRuName(moonSign)}` });
  }

  const risingSign = identity.rising_sign?.trim();
  if (risingSign && !hasRising) {
    additions.push({ id: "rising", label: `Асцендент в ${zodiacRuName(risingSign)}` });
  }

  if (!additions.length) return anchors;

  const sunIndex = anchors.findIndex((anchor) => anchor.id === "sun");
  if (sunIndex >= 0) {
    return [...anchors.slice(0, sunIndex + 1), ...additions, ...anchors.slice(sunIndex + 1)];
  }
  return [...additions, ...anchors];
}

function mergeProfileContractIntoQuickMap(
  base: ProfileQuickMapViewModel,
  contract?: CoreProfile["profile_contract_v1"] | null,
): ProfileQuickMapViewModel {
  const locale = getLocale();
  if (!profileContractMatchesLocale(contract, locale)) {
    // Wrong-language or empty portrait — keep taxonomy / CUM layers, never paint EN on RU UI.
    return base;
  }

  const status = String(contract?.status || "").trim().toLowerCase();
  const portraitReady = status === "ready" && Boolean(contract?.identity_core?.trim());
  const portraitPartial =
    (status === "partial" || status === "forming") && Boolean(contract?.identity_core?.trim());

  // Forming with no LLM text yet → do not fall back to taxonomy/template portrait copy.
  if (!portraitReady && !portraitPartial) {
    if (status === "forming" || status === "partial" || !contract) {
      return {
        ...base,
        identitySummary: null,
        strengthens: [],
        drains: [],
        decisionStyle: null,
        perceivedAs: [],
        frameworkLead: null,
        lifeMission: null,
        thriveAreas: [],
      };
    }
    return base;
  }

  const identitySummary = (contract?.identity_core || "").trim();
  // Ready: prefer contract, allow non-overlapping base tags. Partial: contract-only (no silent mix-in).
  const allowBaseMix = portraitReady;
  const strengthens = filterProfileCopyList(
    [...(contract?.strengths ?? []), ...(allowBaseMix ? base.strengthens : [])],
    4,
    locale,
  );
  const drains = filterProfileCopyList(
    [...(contract?.growth_zones ?? []), ...(allowBaseMix ? base.drains : [])],
    4,
    locale,
  );
  const decisionStyleRaw = contract?.decision_style?.trim() || (allowBaseMix ? base.decisionStyle : null);
  const decisionStyle = isUsableProfileCopy(decisionStyleRaw, locale) ? decisionStyleRaw : null;
  const perceivedAs = filterProfileCopyList(
    [...(contract?.recurring_patterns ?? []), ...(allowBaseMix ? base.perceivedAs : [])],
    5,
    locale,
  );
  const frameworkLeadRaw = contract?.living_changes?.trim() || (allowBaseMix ? base.frameworkLead : null);
  const frameworkLead = isUsableProfileCopy(frameworkLeadRaw, locale) ? frameworkLeadRaw : null;
  const lifeMissionRaw = contract?.life_mission?.trim() || (allowBaseMix ? base.lifeMission : null);
  const lifeMission = isUsableProfileCopy(lifeMissionRaw, locale) ? lifeMissionRaw : null;
  const thriveAreas = filterProfileCopyList(
    [...(contract?.helps ?? []), ...(allowBaseMix ? base.thriveAreas : [])],
    4,
    locale,
  );

  return {
    ...base,
    identitySummary: isUsableProfileCopy(identitySummary, locale) ? identitySummary : base.identitySummary,
    strengthens: strengthens.length ? strengthens : base.strengthens,
    drains: drains.length ? drains : base.drains,
    decisionStyle: decisionStyle ?? base.decisionStyle,
    perceivedAs: perceivedAs.length ? perceivedAs : base.perceivedAs,
    frameworkLead: frameworkLead ?? base.frameworkLead,
    lifeMission: lifeMission ?? base.lifeMission,
    thriveAreas: thriveAreas.length ? thriveAreas : base.thriveAreas,
  };
}

function mergeCumIntoQuickMap(
  base: ProfileQuickMapViewModel,
  cum?: CompactUserModel | null,
): ProfileQuickMapViewModel {
  if (!cum) return base;

  const identity = cum.identity ?? {};
  const atomSummaries = (cum.knowledge_atoms_top_k ?? [])
    .map((atom) => atom.claim_summary?.trim() || atom.claim?.trim() || "")
    .filter(Boolean);

  const patternWorks = cum.behavioral_patterns?.works ?? [];
  const patternAvoid = cum.behavioral_patterns?.does_not_work ?? [];
  const identityStrengths = identity.strengths ?? [];
  const identityConstraints = identity.constraints ?? [];

  const strengthens = filterProfileCopyList(
    [...patternWorks, ...identityStrengths, ...base.strengthens, ...atomSummaries.slice(0, 2)],
    4,
  );
  const drains = filterProfileCopyList(
    [...patternAvoid, ...identityConstraints, ...base.drains],
    4,
  );

  const archetypeRaw = base.archetype?.trim() || identity.archetype?.trim() || "";
  const archetype = archetypeRaw ? archetypeDisplayLabel(archetypeRaw) : base.archetype;
  const identitySummaryRaw = base.identitySummary ?? identity.summary?.trim() ?? null;
  const identitySummary = isUsableProfileCopy(identitySummaryRaw) ? identitySummaryRaw : base.identitySummary;

  return {
    ...base,
    archetype,
    identitySummary,
    strengthens: strengthens.length ? strengthens : base.strengthens,
    drains: drains.length ? drains : base.drains,
    frameworkAnchors: enrichFrameworkAnchorsFromIdentity(base.frameworkAnchors, identity),
    perceivedAs: base.perceivedAs.length
      ? base.perceivedAs
      : filterProfileCopyList(atomSummaries.slice(0, 5), 5),
    thriveAreas: base.thriveAreas.length
      ? base.thriveAreas
      : profileCopyToTags(
          (cum.active_themes ?? []).map((theme) => formatCumThemeLabel(theme.id)).filter(Boolean),
          5,
        ),
  };
}

export function buildProfileChartFrameworkInput(input: {
  sunSignDisplay: string | null;
  risingSign: string | null;
  mcSign: string | null;
  lifePath: number | null;
  archetypeLabel: string;
  chartCards: ProfileFrameworkCard[];
}): ProfileChartFrameworkInput {
  const sunAnchor = input.sunSignDisplay ? `Солнце в ${zodiacRuName(input.sunSignDisplay)}` : null;
  const risingAnchor = input.risingSign ? `Асцендент в ${zodiacRuName(input.risingSign)}` : null;
  const mcAnchor = input.mcSign ? `MC в ${zodiacRuName(input.mcSign)}` : null;
  const moonAnchor = input.chartCards.find((card) => card.id === "moon")?.anchor ?? null;

  return {
    sunAnchor,
    risingAnchor,
    mcAnchor,
    moonAnchor,
    cards: input.chartCards,
  };
}

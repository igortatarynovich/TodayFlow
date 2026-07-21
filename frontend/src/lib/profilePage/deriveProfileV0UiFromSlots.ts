import type { CoreProfile } from "@/lib/types";
import { archetypeDisplayLabel } from "@/lib/visualIdentity/registry";
import { getLifePathEntry, getNameNumberEntry } from "@/lib/zodiacKnowledge";
import type { ProfileV0NumberGuide } from "./buildProfileV0Data";
import type {
  ProfileV0Header,
  ProfileV0MovementCard,
  ProfileV0NumberRow,
  ProfileV0NumbersCard,
  ProfileV0WhoCard,
} from "./buildProfileV0Data";
import { deriveMetaFromTaxonomy } from "./buildProfileV0TaxonomyLayers";
import type { ProfileTaxonomyInsightSlot } from "./profileInsightTypes";
import type {
  ProfileV0LoveCard,
  ProfileV0MoneyCard,
  ProfileV0SocialMirrorCard,
} from "./buildProfileV0SphereCards";
import { PROFILE_LIMITS } from "./profileScreenLimits";
import { withRealizationFrame, withRelationshipFrame } from "./profileSphereCopy";
import { compactProfileCopy } from "./truncateProfileCopy";

function slotText(slots: ProfileTaxonomyInsightSlot[], layer: string, categoryId: string): string | null {
  return slots.find((s) => s.layer === layer && s.categoryId === categoryId)?.text ?? null;
}

const HERO_QUALITY_LABELS = ["Способность", "Талант", "Устойчивость"] as const;

function heroQualitiesFromSlots(slots: ProfileTaxonomyInsightSlot[]): ProfileV0Header["qualities"] {
  const sources = [
    slotText(slots, "hero", "main_strength"),
    slotText(slots, "hero", "main_conflict"),
    slotText(slots, "hero", "life_theme"),
  ];

  return HERO_QUALITY_LABELS.flatMap((title, index) => {
    const raw = sources[index]?.trim();
    if (!raw) return [];
    const subtitle = raw.replace(/^Сильная сторона — /i, "").trim();
    return [{ title, subtitle: compactProfileCopy(subtitle, PROFILE_LIMITS.heroQualitySubtitle) }];
  });
}

export function deriveHeaderFromSlots(
  core: CoreProfile | null,
  displayName: string,
  slots: ProfileTaxonomyInsightSlot[],
): ProfileV0Header {
  const meta = deriveMetaFromTaxonomy(core, displayName);
  const identity = slotText(slots, "hero", "identity");
  const conflict = slotText(slots, "hero", "main_conflict");
  const lifeTheme = slotText(slots, "hero", "life_theme");
  const introSource = identity;
  const intro = introSource ? compactProfileCopy(introSource, PROFILE_LIMITS.heroIntro) : null;

  return {
    displayName: meta.displayName,
    sunSign: meta.sunSign,
    sunSignDisplay: meta.sunSignDisplay,
    archetypeLabel: meta.archetypeLabel,
    element: meta.element,
    lifePath: meta.lifePath,
    tagline: identity,
    poeticCaption: meta.poeticCaption,
    intro,
    tension: conflict,
    lifeTheme,
    metaLine: meta.metaLine,
    qualities: heroQualitiesFromSlots(slots),
  };
}

export function deriveWhoFromSlots(
  core: CoreProfile | null,
  slots: ProfileTaxonomyInsightSlot[],
): ProfileV0WhoCard | null {
  const archetypeLabel = archetypeDisplayLabel(core?.baseline?.archetype_seed);
  const whyInsights = ["formation", "helps", "breaks"]
    .map((id) => slotText(slots, "why", id))
    .filter((t): t is string => Boolean(t));

  if (!archetypeLabel && !whyInsights.length) return null;

  return {
    archetypeLabel,
    whyManifest: whyInsights[0] ?? null,
    whyInsights,
    layerHint: "Потому что архетип, знак и число пути складываются в один сценарий.",
    runtimeGenerated: Boolean(core?.interpretation?.identity),
  };
}

export function deriveNumbersFromSlots(
  core: CoreProfile | null,
  slots: ProfileTaxonomyInsightSlot[],
): ProfileV0NumbersCard | null {
  const lifePath = core?.numerology?.life_path;
  if (lifePath == null) return null;

  const meta = deriveMetaFromTaxonomy(core, "");
  const driver = slotText(slots, "corePattern", "driver");
  const trap = slotText(slots, "corePattern", "trap");
  const recovery = slotText(slots, "corePattern", "recovery");
  const fear = slotText(slots, "corePattern", "fear");
  const decisions = slotText(slots, "corePattern", "decisions");

  const lpEntry = getLifePathEntry(lifePath);
  const coreInsight = driver?.trim() || lpEntry?.driver?.trim() || lpEntry?.essence?.trim() || null;
  const referenceEssence = lpEntry?.essence?.trim() || null;

  const hero: ProfileV0NumberRow = {
    key: "lp",
    value: String(lifePath),
    caption: meta.poeticCaption ?? lpEntry?.title ?? String(lifePath),
    blurb: coreInsight ? compactProfileCopy(coreInsight, PROFILE_LIMITS.numbersExpandLine) : null,
  };

  const second: ProfileV0NumberRow | null = trap
    ? { key: "trap", value: "◦", caption: "Под напряжением", blurb: compactProfileCopy(trap, PROFILE_LIMITS.numbersInsight) }
    : null;

  const third: ProfileV0NumberRow | null = decisions
    ? { key: "decisions", value: "◦", caption: "Решения", blurb: compactProfileCopy(decisions, PROFILE_LIMITS.numbersInsight) }
    : null;

  const birthDayRow: ProfileV0NumberRow | null =
    meta.birthDay != null && recovery
      ? {
          key: "bd",
          value: String(meta.birthDay),
          caption: "Ежедневный режим",
          blurb: compactProfileCopy(recovery, PROFILE_LIMITS.numbersInsight),
        }
      : null;

  const togetherParts = [fear].filter(Boolean);
  const togetherDigest = togetherParts.length
    ? compactProfileCopy(togetherParts.join(" "), PROFILE_LIMITS.numbersTogether)
    : null;

  const rings: ProfileV0NumbersCard["rings"] = [];
  const personalityNum = core?.numerology?.personality;
  const expressionNum = core?.numerology?.expression;
  const peEntry = getNameNumberEntry(personalityNum ?? undefined);
  const exEntry = getNameNumberEntry(expressionNum ?? undefined);

  if (personalityNum != null) {
    rings.push({
      id: "personality",
      value: String(personalityNum),
      label: "Число личности",
      meaning: peEntry?.personality?.trim() || "Как тебя считывают снаружи.",
    });
  }
  if (expressionNum != null) {
    rings.push({
      id: "expression",
      value: String(expressionNum),
      label: "Число имени",
      meaning: exEntry?.expression?.trim() || "Как имя задаёт твой стиль проявления.",
    });
  }
  if (meta.birthDay != null) {
    const bdMeaning =
      lpEntry?.reading?.[0]?.trim() ||
      "Микро-ритм дня рождения — как ты входишь в цикл каждый день.";
    rings.push({
      id: "birthday",
      value: String(meta.birthDay),
      label: "Число дня рождения",
      meaning: bdMeaning,
    });
  }

  const guides: ProfileV0NumberGuide[] = [
    {
      id: "lp",
      title: "Число пути",
      value: String(lifePath),
      body: [referenceEssence, coreInsight].filter(Boolean).join(" "),
    },
    ...rings.map((ring) => ({
      id: ring.id,
      title: ring.label,
      value: ring.value,
      body: ring.meaning,
    })),
    trap
      ? { id: "trap", title: "Под напряжением", value: null, body: trap }
      : null,
    decisions
      ? { id: "decisions", title: "Как принимаешь решения", value: null, body: decisions }
      : null,
    recovery
      ? { id: "recovery", title: "Ежедневный режим", value: birthDayRow?.value ?? null, body: recovery }
      : null,
    fear ? { id: "fear", title: "Что тормозит", value: null, body: fear } : null,
  ].filter((g): g is ProfileV0NumberGuide => Boolean(g?.body?.trim()));

  return {
    hero,
    coreInsight,
    referenceEssence,
    second,
    third,
    rings,
    guides,
    expand: {
      whyHero: "Это повторяющийся сценарий, который движет решениями. Раскрой слои, чтобы увидеть, как он проявляется.",
      birthDay: birthDayRow,
      togetherDigest,
    },
  };
}

export function deriveSocialMirrorFromSlots(slots: ProfileTaxonomyInsightSlot[]): ProfileV0SocialMirrorCard | null {
  const lead = slotText(slots, "socialMirror", "first_impression");
  const observations = ["after_knowing", "misread", "trust"]
    .map((id) => slotText(slots, "socialMirror", id))
    .filter((t): t is string => Boolean(t));

  if (!lead && !observations.length) return null;

  return {
    lead: lead ?? observations[0] ?? "",
    observations: lead ? observations : observations.slice(1),
    runtimeGenerated: true,
    expand: {
      firstImpression: slotText(slots, "socialMirror", "first_impression"),
      broadcast: slotText(slots, "socialMirror", "after_knowing"),
      blindSpot: slotText(slots, "socialMirror", "misread"),
    },
  };
}

export function deriveLoveFromSlots(slots: ProfileTaxonomyInsightSlot[]): ProfileV0LoveCard | null {
  const loves = slotText(slots, "love", "loves");
  const seeks = slotText(slots, "love", "seeks");
  if (!loves && !seeks) return null;

  const strength = slotText(slots, "love", "strengthens");
  const watchout = slotText(slots, "love", "destroys") ?? slotText(slots, "love", "fears");

  return {
    style: withRelationshipFrame(loves ?? seeks ?? ""),
    whatMatters: seeks && loves !== seeks ? seeks : "",
    strength: strength ?? "",
    watchout: watchout ?? "",
    runtimeGenerated: true,
    expand: {
      needs: seeks,
      mistakes: slotText(slots, "love", "fears"),
      redFlags: slotText(slots, "love", "destroys"),
    },
  };
}

export function deriveMoneyFromSlots(slots: ProfileTaxonomyInsightSlot[]): ProfileV0MoneyCard | null {
  const earning = slotText(slots, "money", "earning_style");
  const growth = slotText(slots, "money", "growth_source");
  if (!earning && !growth) return null;

  return {
    approach: withRealizationFrame(earning ?? growth ?? ""),
    helps: slotText(slots, "money", "catalyst") ?? "",
    blocks: slotText(slots, "money", "risk") ?? slotText(slots, "money", "blind_spot") ?? "",
    workStyle: growth ?? "",
    runtimeGenerated: true,
    expand: {
      workStyle: growth,
      motivation: slotText(slots, "money", "catalyst"),
      risk: slotText(slots, "money", "risk"),
    },
  };
}

export function deriveCompassFromSlots(slots: ProfileTaxonomyInsightSlot[]): ProfileV0MovementCard | null {
  const amplify = slotText(slots, "compass", "amplify");
  const avoid = slotText(slots, "compass", "avoid");
  const skill = slotText(slots, "compass", "skill");
  const check = slotText(slots, "compass", "check_soon");
  const energy = slotText(slots, "compass", "energy_direction");

  if (!amplify && !avoid && !skill && !check && !energy) return null;

  const rules = [avoid, skill, energy].filter((t): t is string => Boolean(t));

  return {
    title: "Двигаться через понятный ритм",
    mainText: amplify ?? energy ?? "",
    rules,
    recommendation: check ?? "",
  };
}

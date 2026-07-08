import type { CoreProfile } from "@/lib/types";
import { lifePathPoeticTitle } from "@/lib/visualIdentity/lifePathTitles";
import {
  getLifePathEntry,
  getNameNumberEntry,
  getZodiacEntry,
  resolveZodiacSignId,
  type LifePathEntry,
  type ZodiacKnowledgeEntry,
} from "@/lib/zodiacKnowledge";
import { getElement, normalizeZodiacSign, type Element } from "@/lib/zodiac-utils";
import type { ProfileInsightLayer } from "./profileInsightBudget";
import { ProfileInsightSlotRegistry } from "./profileInsightSlotRegistry";
import type { ProfileTaxonomyInsightSlot, ProfileV0TaxonomyPayload } from "./profileInsightTypes";
import { PROFILE_LIMITS } from "./profileScreenLimits";
import { withRealizationFrame, withRelationshipFrame } from "./profileSphereCopy";
import { compactProfileCopy, firstSentence } from "./truncateProfileCopy";

const EMPTY_RHYTHM = "Ритм проявится после сборки";

function trim(s: string | null | undefined): string {
  return (s ?? "").trim();
}

function trimList(items: string[] | null | undefined, max: number): string[] {
  if (!items?.length) return [];
  return items.map((s) => s.trim()).filter(Boolean).slice(0, max);
}

function firstSentences(text: string, max: number): string {
  return text
    .split(/(?<=[.!?])\s+/)
    .filter(Boolean)
    .slice(0, max)
    .join(" ")
    .trim();
}

function signEntry(sunSign: string | null): ZodiacKnowledgeEntry | undefined {
  if (!sunSign) return undefined;
  const id = resolveZodiacSignId(sunSign, null);
  return id ? getZodiacEntry(id) : undefined;
}

function lpBullet(entry: LifePathEntry | undefined, field: "relationships" | "money_work", index: number): string | null {
  const list = entry?.[field];
  if (!list?.length) return null;
  return trim(list[index] ?? list[0]);
}

function reframeAsPerceived(raw: string): string {
  const t = raw.trim();
  if (/^со стороны/i.test(t)) {
    return t
      .replace(/^со стороны ты\s+считываешься как\s+/i, "Люди часто воспринимают тебя как ")
      .replace(/^со стороны ты\s+/i, "Люди часто воспринимают тебя как ");
  }
  if (/^ты проявляешься/i.test(t)) return t.replace(/^ты проявляешься\s+/i, "Ты транслируешь ");
  if (/^внутри тебе/i.test(t)) return t.replace(/^внутри тебе\s+/i, "За внешним образом ");
  return t;
}

function digitalRoot1to9(n: number): number {
  let x = Math.abs(Math.trunc(n));
  while (x > 9) x = String(x).split("").reduce((acc, d) => acc + Number(d), 0);
  return x === 0 ? 1 : x;
}

function birthDayNumber(birthDate: string | null | undefined): number | null {
  const m = birthDate?.match(/^(\d{4})-(\d{2})-(\d{2})/);
  if (!m) return null;
  return digitalRoot1to9(Number(m[3]));
}

function resolveElement(sunSign: string | null, sunElement: string | null | undefined): Element | null {
  const fromApi = sunElement?.trim();
  if (fromApi) {
    const map: Record<string, Element> = { fire: "Fire", earth: "Earth", air: "Air", water: "Water" };
    const hit = map[fromApi.toLowerCase()];
    if (hit) return hit;
  }
  const slug = sunSign ? normalizeZodiacSign(sunSign) : null;
  return slug ? getElement(slug) : null;
}

function sunSignDisplayName(sunSign: string | null): string | null {
  if (!sunSign) return null;
  const id = resolveZodiacSignId(sunSign, null);
  return id ? getZodiacEntry(id)?.ruName || sunSign : sunSign;
}

function claim(
  reg: ProfileInsightSlotRegistry,
  layer: ProfileInsightLayer,
  categoryId: string,
  raw: string | null | undefined,
  sourceKey: string,
  sourceKind: "reference" | "llm" | "computed" = "reference",
  maxChars = 240,
) {
  return reg.claimSlot({ layer, categoryId, raw, sourceKind, sourceKey, maxChars });
}

export type BuildTaxonomyInput = {
  core: CoreProfile | null;
  moonRecoveryHint?: string | null;
};

export function buildProfileV0TaxonomySlots(input: BuildTaxonomyInput): ProfileV0TaxonomyPayload {
  const { core, moonRecoveryHint } = input;
  const reg = new ProfileInsightSlotRegistry();
  const interp = core?.interpretation;
  const sunSign = trim(core?.astro?.sun_sign);
  const sign = signEntry(sunSign);
  const lifePath = core?.numerology?.life_path ?? null;
  const lpEntry = getLifePathEntry(lifePath ?? undefined);
  const identity = trim(interp?.identity);
  const strengths = trimList(interp?.strengths, 3);
  const watchouts = trimList(interp?.watchouts, 2);
  const lifeAreas = interp?.life_areas;
  const peEntry = getNameNumberEntry(core?.numerology?.personality ?? undefined);
  const exEntry = getNameNumberEntry(core?.numerology?.expression ?? undefined);

  const identityRaw = identity || lpEntry?.essence || null;

  claim(reg, "hero", "identity", identityRaw, identity ? "interpretation.identity" : "life_path.essence", identity ? "llm" : "reference", PROFILE_LIMITS.heroTagline);
  claim(reg, "hero", "main_strength", strengths[0] ? `Сильная сторона — ${strengths[0]}.` : lpEntry?.plus_side?.[0] ? `Сильная сторона — ${lpEntry.plus_side[0]}.` : sign?.strengths?.[0] ? `Сильная сторона — ${sign.strengths[0]}.` : null, strengths[0] ? "interpretation.strengths[0]" : "life_path.plus_side[0]", strengths[0] ? "llm" : "reference", PROFILE_LIMITS.sphereLine);
  claim(reg, "hero", "main_conflict", watchouts[0] ? `Напряжение — ${watchouts[0]}.` : lpEntry?.minus_side?.[0] ? `Риск — ${lpEntry.minus_side[0]}.` : lpEntry?.main_fear ? `Страх — ${firstSentence(lpEntry.main_fear)}` : null, watchouts[0] ? "interpretation.watchouts[0]" : "life_path.minus_side[0]", watchouts[0] ? "llm" : "reference", PROFILE_LIMITS.sphereLine);
  claim(reg, "hero", "life_theme", lpEntry?.life_theme || null, "life_path.life_theme", "reference", PROFILE_LIMITS.whyInsightLine);

  claim(reg, "why", "formation", lpEntry?.pattern, "life_path.pattern", "reference", PROFILE_LIMITS.whyInsightLine);
  claim(reg, "why", "helps", lpEntry?.growth, "life_path.growth", "reference", PROFILE_LIMITS.whyInsightLine);
  claim(reg, "why", "breaks", lpEntry?.minus_side?.[0] ? `Ломается там, где включается ${lpEntry.minus_side[0].toLowerCase()}.` : lpEntry?.main_fear ? `Цена паттерна — ${firstSentence(lpEntry.main_fear)}` : watchouts[0] ? `Ломается, когда ${watchouts[0].toLowerCase()}.` : null, "life_path.minus_side[0]", "reference", PROFILE_LIMITS.whyInsightLine);

  claim(reg, "corePattern", "driver", lpEntry?.driver, "life_path.driver", "reference", PROFILE_LIMITS.numbersInsight);
  claim(reg, "corePattern", "fear", lpEntry?.main_fear, "life_path.main_fear", "reference", PROFILE_LIMITS.numbersInsight);
  claim(reg, "corePattern", "trap", lpEntry?.minus_side?.[0] ? `Ловушка — ${lpEntry.minus_side[0]}.` : lpEntry?.watchouts?.[0] ? `Ловушка — ${lpEntry.watchouts[0]}.` : null, "life_path.minus_side[0]", "reference", PROFILE_LIMITS.numbersInsight);
  claim(reg, "corePattern", "decisions", lifeAreas?.decisions || sign?.decisions || lpEntry?.reading?.[0] || null, lifeAreas?.decisions ? "interpretation.life_areas.decisions" : "sign.decisions", lifeAreas?.decisions ? "llm" : "reference", PROFILE_LIMITS.numbersInsight);
  claim(reg, "corePattern", "recovery", moonRecoveryHint || (lifeAreas?.body && lifeAreas.body !== EMPTY_RHYTHM ? lifeAreas.body : null) || core?.baseline?.rhythm_style || null, moonRecoveryHint ? "moon_recovery_hint" : "interpretation.life_areas.body", moonRecoveryHint ? "computed" : lifeAreas?.body ? "llm" : "reference", PROFILE_LIMITS.numbersInsight);

  const personalityRaw = peEntry?.personality?.trim();
  const expressionRaw = exEntry?.expression?.trim();
  claim(reg, "socialMirror", "first_impression", personalityRaw ? reframeAsPerceived(personalityRaw) : sign?.portrait || null, personalityRaw ? "name_number.personality" : "sign.portrait", "reference", PROFILE_LIMITS.socialMirrorLine);
  claim(reg, "socialMirror", "after_knowing", expressionRaw ? reframeAsPerceived(expressionRaw) : sign?.communication || sign?.intimacy || null, expressionRaw ? "name_number.expression" : "sign.communication", "reference", PROFILE_LIMITS.socialMirrorLine);
  claim(reg, "socialMirror", "misread", sign?.watchouts?.[0] ? `Можешь казаться ${sign.watchouts[0]}, даже когда внутри всё иначе.` : sign?.minusSide?.[0] ? `Иногда считывают ${sign.minusSide[0]} сильнее, чем ты хочешь.` : null, "sign.watchouts[0]", "reference", PROFILE_LIMITS.socialMirrorLine);
  claim(reg, "socialMirror", "trust", sign?.friendship || sign?.support || (sign?.likes?.length ? `Доверие растёт, когда есть ${sign.likes.slice(0, 2).join(" и ")}.` : null), sign?.friendship ? "sign.friendship" : "sign.likes", "reference", PROFILE_LIMITS.socialMirrorLine);

  claim(reg, "love", "seeks", sign?.intimacy || (sign?.likes?.length ? `Ищешь ${sign.likes.slice(0, 2).join(" и ")}.` : null) || lpBullet(lpEntry, "relationships", 0), sign?.intimacy ? "sign.intimacy" : "life_path.relationships[0]", "reference", PROFILE_LIMITS.sphereLine);
  claim(reg, "love", "fears", sign?.hurts?.[0] ? `Боишься, когда ${sign.hurts[0]}.` : lpEntry?.main_fear ? `Страх в близости — ${firstSentence(lpEntry.main_fear)}` : null, sign?.hurts?.[0] ? "sign.hurts[0]" : "life_path.main_fear", "reference", PROFILE_LIMITS.sphereLine);
  claim(reg, "love", "loves", lifeAreas?.love ? withRelationshipFrame(lifeAreas.love) : sign?.love || sign?.conflict || null, lifeAreas?.love ? "interpretation.life_areas.love" : "sign.love", lifeAreas?.love ? "llm" : "reference", PROFILE_LIMITS.sphereMain);
  claim(reg, "love", "destroys", sign?.dislikes?.length ? `Разрушает ${sign.dislikes.slice(0, 2).join(" и ")}.` : lpBullet(lpEntry, "relationships", 2), sign?.dislikes?.length ? "sign.dislikes" : "life_path.relationships[2]", "reference", PROFILE_LIMITS.sphereLine);
  claim(reg, "love", "strengthens", lpEntry?.relationship_strengthens || null, "life_path.relationship_strengthens", "reference", PROFILE_LIMITS.sphereLine);

  claim(reg, "money", "growth_source", lpBullet(lpEntry, "money_work", 0) || lifeAreas?.career || sign?.career || null, lpEntry ? "life_path.money_work[0]" : "interpretation.life_areas.career", lifeAreas?.career ? "llm" : "reference", PROFILE_LIMITS.sphereLine);
  claim(reg, "money", "earning_style", lifeAreas?.money ? withRealizationFrame(lifeAreas.money) : sign?.money || sign?.work || null, lifeAreas?.money ? "interpretation.life_areas.money" : "sign.money", lifeAreas?.money ? "llm" : "reference", PROFILE_LIMITS.sphereMain);
  claim(reg, "money", "risk", lpBullet(lpEntry, "money_work", 2) || (sign?.watchouts?.[1] ? `Риск — ${sign.watchouts[1]}.` : null), "life_path.money_work[2]", "reference", PROFILE_LIMITS.sphereLine);
  claim(reg, "money", "blind_spot", lpEntry?.minus_side?.[1] ? `Слепая зона — ${lpEntry.minus_side[1]}.` : watchouts[1] ? `Слепая зона — ${watchouts[1]}.` : sign?.decisions || null, "life_path.minus_side[1]", "reference", PROFILE_LIMITS.sphereLine);
  claim(reg, "money", "catalyst", sign?.strengths?.[1] ? `Ускоряет ${sign.strengths[1]}.` : lpEntry?.plus_side?.[1] ? `Ускоряет ${lpEntry.plus_side[1]}.` : null, sign?.strengths?.[1] ? "sign.strengths[1]" : "life_path.plus_side[1]", "reference", PROFILE_LIMITS.sphereLine);

  // Deferred until action/reference layer — avoid overlap with manifestation / plus_side.
  claim(reg, "compass", "amplify", null, "deferred:action_layer", "reference", PROFILE_LIMITS.movementMain);
  claim(reg, "compass", "avoid", lpEntry?.minus_side?.[1] ? `Избегай ${lpEntry.minus_side[1].toLowerCase()}.` : sign?.watchouts?.[1] ? `Избегай ${sign.watchouts[1].toLowerCase()}.` : null, "life_path.minus_side[1]", "reference", PROFILE_LIMITS.movementRule);
  // Deferred until Today/action layer — decisions already live in corePattern.
  claim(reg, "compass", "energy_direction", null, "deferred:action_layer", "reference", PROFILE_LIMITS.movementMain);
  claim(reg, "compass", "skill", lpEntry?.lesson || lpEntry?.growth, "life_path.lesson", "reference", PROFILE_LIMITS.movementRule);
  claim(reg, "compass", "check_soon", lifeAreas?.career ? `Проверь: ${firstSentence(lifeAreas.career)}` : moonRecoveryHint ? `Проверь: ${firstSentence(moonRecoveryHint)}` : lifeAreas?.body || null, lifeAreas?.career ? "interpretation.life_areas.career" : "moon_recovery_hint", lifeAreas?.career ? "llm" : "computed", PROFILE_LIMITS.movementRecommendation);

  const allSlots = reg.getSlots();
  const layerIds: ProfileInsightLayer[] = ["hero", "why", "corePattern", "socialMirror", "love", "money", "compass"];
  return { layers: layerIds.map((layer) => ({ layer, slots: allSlots.filter((s) => s.layer === layer) })), allSlots };
}

export function deriveMetaFromTaxonomy(core: CoreProfile | null, displayName: string) {
  const sunSign = trim(core?.astro?.sun_sign);
  const lifePath = core?.numerology?.life_path ?? null;
  return {
    displayName,
    sunSign: sunSign || null,
    sunSignDisplay: sunSignDisplayName(sunSign || null),
    archetypeLabel: core?.baseline?.archetype_seed?.trim() || "Личный архетип",
    element: resolveElement(sunSign || null, core?.astro?.sun_element),
    lifePath,
    metaLine: [sunSignDisplayName(sunSign || null), lifePath != null ? `Число пути ${lifePath}` : null].filter(Boolean).join(" · ") || null,
    poeticCaption: lifePath != null ? lifePathPoeticTitle(lifePath) : null,
    birthDay: birthDayNumber(core?.numerology?.birth_date),
  };
}

export type { ProfileTaxonomyInsightSlot };

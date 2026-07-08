import type { CoreProfile } from "@/lib/types";
import {
  getLifePathEntry,
  getNameNumberEntry,
  getZodiacEntry,
  resolveZodiacSignId,
  type LifePathEntry,
  type ZodiacKnowledgeEntry,
} from "@/lib/zodiacKnowledge";
import { PROFILE_INSIGHT_BUDGET } from "./profileInsightBudget";
import { PROFILE_LIMITS } from "./profileScreenLimits";
import type { ProfileContentLedger } from "./profileContentLedger";
import { withRealizationFrame, withRelationshipFrame } from "./profileSphereCopy";
import { compactProfileCopy, firstSentence } from "./truncateProfileCopy";

const MIN_RICH_TEXT = 28;

function trim(s: string | null | undefined): string {
  return (s ?? "").trim();
}

function isRich(s: string | null | undefined): boolean {
  return trim(s).length >= MIN_RICH_TEXT;
}

function firstSentences(text: string, max: number): string {
  return text
    .split(/(?<=[.!?])\s+/)
    .filter(Boolean)
    .slice(0, max)
    .join(" ")
    .trim();
}

function pick(...candidates: (string | null | undefined)[]): string {
  for (const c of candidates) {
    const t = trim(c);
    if (isRich(t)) return t;
  }
  for (const c of candidates) {
    const t = trim(c);
    if (t) return t;
  }
  return "";
}

function claimLine(ledger: ProfileContentLedger, raw: string, max: number): string | null {
  const line = compactProfileCopy(firstSentence(raw), max);
  return line && !ledger.hasOverlap(line) ? line : null;
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

export type ProfileV0LoveCard = {
  style: string;
  whatMatters: string;
  strength: string;
  watchout: string;
  runtimeGenerated: boolean;
  expand: {
    needs: string | null;
    mistakes: string | null;
    redFlags: string | null;
  };
};

export type ProfileV0MoneyCard = {
  approach: string;
  helps: string;
  blocks: string;
  workStyle: string;
  runtimeGenerated: boolean;
  expand: {
    workStyle: string | null;
    motivation: string | null;
    risk: string | null;
  };
};

export type ProfileV0SocialMirrorCard = {
  lead: string;
  observations: string[];
  runtimeGenerated: boolean;
  expand: {
    firstImpression: string | null;
    broadcast: string | null;
    blindSpot: string | null;
  };
};

function reframeAsPerceived(raw: string): string {
  const t = raw.trim();
  if (!t) return t;
  if (/^со стороны/i.test(t)) {
    return t.replace(/^со стороны ты\s+/i, "Люди часто воспринимают тебя как ");
  }
  if (/^ты проявляешься/i.test(t)) {
    return t.replace(/^ты проявляешься\s+/i, "Ты транслируешь ");
  }
  if (/^внутри тебе/i.test(t)) {
    return t.replace(/^внутри тебе\s+/i, "За внешним образом ");
  }
  return t;
}

export function buildSocialMirrorCard(
  core: CoreProfile | null,
  ledger: ProfileContentLedger,
): ProfileV0SocialMirrorCard | null {
  const sunSign = trim(core?.astro?.sun_sign);
  const sign = signEntry(sunSign);
  const expression = core?.numerology?.expression ?? null;
  const personality = core?.numerology?.personality ?? null;
  const nameEntry = getNameNumberEntry(expression ?? undefined);
  const peEntry = getNameNumberEntry(personality ?? undefined);

  const personalityRaw = peEntry?.personality?.trim() || null;
  const expressionRaw = nameEntry?.expression?.trim() || null;
  const soulRaw = nameEntry?.soul_urge?.trim() || null;

  if (!sign && !personalityRaw && !expressionRaw) return null;

  const observationPool: Array<string | null | undefined> = [
    personalityRaw ? reframeAsPerceived(personalityRaw) : null,
    expressionRaw ? reframeAsPerceived(expressionRaw) : null,
    sign?.portrait ? `С первого взгляда ${firstSentence(sign.portrait).replace(/^.*?—\s*/u, "")}` : null,
    sign?.communication ? `В общении ${firstSentence(sign.communication).charAt(0).toLowerCase()}${firstSentence(sign.communication).slice(1)}` : null,
    sign?.strengths?.[0] ? `Чаще всего замечают ${sign.strengths[0]}.` : null,
    sign?.attraction ? firstSentence(sign.attraction) : null,
    soulRaw ? reframeAsPerceived(soulRaw) : null,
  ];

  const observations = ledger
    .claimMany(observationPool, PROFILE_INSIGHT_BUDGET.socialMirror - 1, 20)
    .map((line) => compactProfileCopy(line, PROFILE_LIMITS.socialMirrorLine));

  const leadRaw =
    ledger.claimFirst([
      personalityRaw ? reframeAsPerceived(personalityRaw) : null,
      sign?.portrait ? firstSentence(sign.portrait) : null,
      expressionRaw ? reframeAsPerceived(expressionRaw) : null,
    ], 20) ?? "Ты создаёшь впечатление человека, которого нужно чуть больше времени, чтобы понять.";

  const firstImpression = ledger.claimFirst([
    sign?.portrait ? firstSentence(sign.portrait) : null,
    sign?.strengths?.slice(0, 2).join(" и ") ? `Первым делом бросается в глаза ${sign.strengths.slice(0, 2).join(" и ")}.` : null,
  ]);

  const broadcast = ledger.claimFirst([
    expressionRaw ? reframeAsPerceived(expressionRaw) : null,
    sign?.communication ? firstSentence(sign.communication) : null,
  ]);

  const blindSpot = ledger.claimFirst([
    sign?.watchouts?.[0] ? `Можешь казаться ${sign.watchouts[0]}, даже когда внутри всё иначе.` : null,
    sign?.minusSide?.[0] ? `Иногда считывают ${sign.minusSide[0]} сильнее, чем ты сам этого хочешь.` : null,
    sign?.hurts?.[0] ? `Болезненно, когда люди видят в тебе только ${sign.hurts[0]}.` : null,
  ]);

  return {
    lead: compactProfileCopy(leadRaw, PROFILE_LIMITS.socialMirrorLead),
    observations,
    runtimeGenerated: Boolean(sign || nameEntry || peEntry),
    expand: {
      firstImpression: firstImpression
        ? compactProfileCopy(firstImpression, PROFILE_LIMITS.sphereExpandDetail)
        : null,
      broadcast: broadcast ? compactProfileCopy(broadcast, PROFILE_LIMITS.sphereExpandDetail) : null,
      blindSpot: blindSpot ? compactProfileCopy(blindSpot, PROFILE_LIMITS.sphereExpandDetail) : null,
    },
  };
}

export function buildLoveCard(core: CoreProfile | null, ledger: ProfileContentLedger): ProfileV0LoveCard | null {
  const sunSign = trim(core?.astro?.sun_sign);
  const sign = signEntry(sunSign);
  const lifeAreas = core?.interpretation?.life_areas;
  const llmLove = trim(lifeAreas?.love);
  const lp = getLifePathEntry(core?.numerology?.life_path ?? undefined);

  if (!sign && !isRich(llmLove)) return null;

  const styleRaw =
    ledger.claimFirst([
      sign?.conflict ? `В близости ${sign.conflict.charAt(0).toLowerCase()}${sign.conflict.slice(1)}` : null,
      sign?.hurts?.[0] ? `Болезненная зона — ${sign.hurts[0]}.` : null,
      sign?.intimacy,
      llmLove,
      lpBullet(lp, "relationships", 1),
    ]) ?? pick(sign?.intimacy, lpBullet(lp, "relationships", 0));

  const whatMattersRaw =
    ledger.claimFirst([
      sign?.likes?.length ? `Тебе важны: ${sign.likes.slice(0, 3).join(", ")}.` : null,
      sign?.intimacy,
      lpBullet(lp, "relationships", 2),
    ]) ?? pick(sign?.intimacy, lpBullet(lp, "relationships", 1));

  const watchoutRaw =
    ledger.claimFirst([
      sign?.watchouts?.[0] ? `Зона внимания — ${sign.watchouts[0]}.` : null,
      sign?.hurts?.[0] ? `Болезненно, когда ${sign.hurts[0]}.` : null,
      lp?.minus_side?.[0] ? `Риск — ${lp.minus_side[0]}.` : null,
    ]) ?? pick(sign?.watchouts?.[0] ? `Зона внимания — ${sign.watchouts[0]}.` : null);

  const needs = ledger.claimFirst([sign?.friendship, trim(lifeAreas?.sex), lpBullet(lp, "relationships", 3)]);
  const mistakes = ledger.claimFirst([sign?.conflict, lpBullet(lp, "relationships", 0)]);
  const redFlags = sign?.dislikes?.length
    ? ledger.claim(`Для тебя red flag — ${sign.dislikes.slice(0, 3).join(", ")}.`)
    : sign?.hurts?.length
      ? ledger.claim(sign.hurts.slice(0, 2).join(" · "))
      : null;

  return {
    style: withRelationshipFrame(compactProfileCopy(firstSentence(styleRaw), PROFILE_LIMITS.sphereMain)),
    whatMatters: compactProfileCopy(firstSentence(whatMattersRaw), PROFILE_LIMITS.sphereLine),
    strength: compactProfileCopy(
      firstSentence(
        pick(
          sign?.plusSide?.[0] ? `Сильная сторона — ${sign.plusSide[0]}.` : null,
          sign?.strengths?.[0] ? `В отношениях проявляется ${sign.strengths[0]}.` : null,
        ),
      ),
      PROFILE_LIMITS.sphereLine,
    ),
    watchout: compactProfileCopy(firstSentence(watchoutRaw), PROFILE_LIMITS.sphereLine),
    runtimeGenerated: isRich(llmLove),
    expand: {
      needs: needs ? compactProfileCopy(firstSentence(needs), PROFILE_LIMITS.sphereExpandDetail) : null,
      mistakes: mistakes ? compactProfileCopy(firstSentence(mistakes), PROFILE_LIMITS.sphereExpandDetail) : null,
      redFlags: redFlags ? compactProfileCopy(firstSentence(redFlags), PROFILE_LIMITS.sphereExpandDetail) : null,
    },
  };
}

export function buildMoneyCard(core: CoreProfile | null, ledger: ProfileContentLedger): ProfileV0MoneyCard | null {
  const sunSign = trim(core?.astro?.sun_sign);
  const sign = signEntry(sunSign);
  const lifeAreas = core?.interpretation?.life_areas;
  const llmMoney = trim(lifeAreas?.money);
  const llmCareer = trim(lifeAreas?.career);
  const lp = getLifePathEntry(core?.numerology?.life_path ?? undefined);

  if (!sign && !isRich(llmMoney) && !isRich(llmCareer)) return null;

  const approachRaw =
    ledger.claimFirst([
      lp?.main_fear ? `Главный страх в деньгах — ${lp.main_fear}.` : null,
      sign?.money,
      sign?.career,
      llmMoney,
      llmCareer,
      lpBullet(lp, "money_work", 0),
    ]) ?? pick(llmMoney, sign?.money, lpBullet(lp, "money_work", 0));

  const motivation = ledger.claimFirst([sign?.work, lpBullet(lp, "money_work", 1)]);
  const risk = ledger.claimFirst([
    sign?.decisions,
    sign?.watchouts?.[2] ? `Риск — ${sign.watchouts[2]}.` : null,
    lpBullet(lp, "money_work", 2),
  ]);

  const workStyle = pick(sign?.work, sign?.career, llmCareer);

  return {
    approach: withRealizationFrame(compactProfileCopy(firstSentence(approachRaw), PROFILE_LIMITS.sphereMain)),
    helps: compactProfileCopy(
      firstSentence(
        pick(
          sign?.work,
          lpBullet(lp, "money_work", 1),
          sign?.plusSide?.[1] ? `Усиливает ${sign.plusSide[1]}.` : null,
        ),
      ),
      PROFILE_LIMITS.sphereLine,
    ),
    blocks: compactProfileCopy(
      firstSentence(
        pick(
          sign?.watchouts?.[1] ? `Тормозит ${sign.watchouts[1]}.` : null,
          lp?.minus_side?.[1] ? `Мешает ${lp.minus_side[1]}.` : null,
        ),
      ),
      PROFILE_LIMITS.sphereLine,
    ),
    workStyle,
    runtimeGenerated: isRich(llmMoney) || isRich(llmCareer),
    expand: {
      workStyle: workStyle ? compactProfileCopy(firstSentence(workStyle), PROFILE_LIMITS.sphereExpandDetail) : null,
      motivation: motivation ? compactProfileCopy(firstSentence(motivation), PROFILE_LIMITS.sphereExpandDetail) : null,
      risk: risk ? compactProfileCopy(firstSentence(risk), PROFILE_LIMITS.sphereExpandDetail) : null,
    },
  };
}

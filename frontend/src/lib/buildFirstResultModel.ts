import { buildNameInsight, type NameInsightModel } from "@/lib/interpretation/buildNameInsight";
import { limitationsFromNatalFacts } from "@/lib/natalFacts";
import type { GuestProfileDraft } from "@/lib/guestProfileDraft";
import {
  buildDimensionWhyExplanation,
  buildDominantWhyExplanation,
  buildGlobalWhySummary,
} from "@/lib/interpretation/buildDomainWhyExplanation";
import { buildKeyInfluences } from "@/lib/interpretation/buildKeyInfluences";
import { generateBirthMetadataCandidates } from "@/lib/interpretation/generateBirthMetadataCandidates";
import { generateObservationCandidates } from "@/lib/interpretation/generateObservationCandidates";
import type { RecognitionSelectionAudit } from "@/lib/interpretation/onboardingRecognitionTypes";
import type { PortraitCardType } from "@/lib/interpretation/portraitDimensions";
import { resolveBirthSignals } from "@/lib/interpretation/resolveBirthSignals";
import { resolveDomainWhyContext } from "@/lib/interpretation/resolveBirthMetadata";
import {
  buildMiniPortraitBullets,
  pickDominantTrait,
  pickOverflowSurprise,
  rankPortraitInsightCards,
  splitVisibleAndMore,
  type RankedPortraitCard,
} from "@/lib/interpretation/rankPortraitInsights";

export type FirstResultPortraitCard = {
  id: string;
  icon: string;
  title: string;
  body: string;
  cardType: PortraitCardType;
  whyExplanation: string;
};

export type FirstResultModel = {
  displayName: string;
  heroTitle: string;
  heroSubtitle: string;
  keyInfluences: ReturnType<typeof buildKeyInfluences>;
  globalWhySummary: string;
  dominantTrait: {
    headline: string;
    supporting: string[];
    whyExplanation: string;
  };
  miniPortrait: string[];
  portraitCards: FirstResultPortraitCard[];
  moreObservations: FirstResultPortraitCard[];
  surprise: {
    label: string;
    body: string;
    whyExplanation: string;
  } | null;
  closingMessage: string;
  refineHint: string;
  nameInsight: NameInsightModel | null;
  saveCtaLabel: string;
  refineCtaLabel: string;
  limitationsLabels: string[];
  audit: RecognitionSelectionAudit;
};

function supportingLines(
  dominantId: string,
  candidates: ReturnType<typeof generateObservationCandidates>,
): string[] {
  return candidates
    .filter((c) => c.id !== dominantId && (c.lens === "strengthens" || c.lens === "recovery"))
    .sort((a, b) => b.score - a.score)
    .slice(0, 2)
    .map((c) =>
      c.text
        .replace(/^Ты сильнее там, где\s+/i, "")
        .replace(/^Тебе помогает помнить:\s*/i, "")
        .replace(/^Быстрее восстанавливаешься, когда\s+/i, "")
        .trim(),
    );
}

function mapPortraitCard(card: RankedPortraitCard, whyCtx: ReturnType<typeof resolveDomainWhyContext>): FirstResultPortraitCard {
  return {
    id: card.id,
    icon: card.dimensionIcon,
    title: card.dimensionTitle,
    body: card.displayBody,
    cardType: card.cardType,
    whyExplanation: buildDimensionWhyExplanation(card.dimensionId, card.evidence, whyCtx),
  };
}

export function buildFirstResultModel(
  draft: GuestProfileDraft,
  refDate: Date = new Date(),
): FirstResultModel {
  const displayName = draft.first_name.trim();
  const signals = resolveBirthSignals(draft, refDate);
  const whyCtx = resolveDomainWhyContext(draft, refDate);

  const baseCandidates = generateObservationCandidates(signals);
  const metadataCandidates = generateBirthMetadataCandidates(whyCtx);
  const candidates = [...baseCandidates, ...metadataCandidates].sort(
    (a, b) => b.score - a.score || a.id.localeCompare(b.id),
  );

  const portraitPool = rankPortraitInsightCards(candidates);
  const { visible, more } = splitVisibleAndMore(portraitPool);

  const visibleTexts = visible.map((c) => c.text);
  const dominant = pickDominantTrait(candidates, visibleTexts);
  const excludeForEach = dominant ? [...visibleTexts, dominant.text] : visibleTexts;

  const miniPortrait = buildMiniPortraitBullets(candidates, excludeForEach);

  const usedIds = new Set([...portraitPool.map((c) => c.id)]);
  if (dominant) usedIds.add(dominant.id);
  const surpriseRaw = pickOverflowSurprise(candidates, usedIds, [
    ...excludeForEach,
    ...miniPortrait,
  ]);

  const portraitCards = visible.map((card) => mapPortraitCard(card, whyCtx));
  const moreObservations = more.map((card) => mapPortraitCard(card, whyCtx));

  const audit: RecognitionSelectionAudit = {
    candidateCount: candidates.length,
    selectedIds: [
      ...portraitCards.map((c) => c.id),
      ...moreObservations.map((c) => c.id),
      ...(dominant ? [dominant.id] : []),
      ...(surpriseRaw ? [surpriseRaw.id] : []),
    ],
    selections: portraitPool.map((c) => ({
      id: c.id,
      lens: c.lens,
      score: c.score,
      evidence: c.evidence,
    })),
  };

  return {
    displayName,
    heroTitle: `${displayName}, я уже вижу первые линии.`,
    heroSubtitle:
      "Сейчас скажу главное. Остальное — если захочешь развернуть.",
    keyInfluences: buildKeyInfluences(draft),
    globalWhySummary: buildGlobalWhySummary(whyCtx),
    dominantTrait: {
      headline:
        dominant?.text ??
        "Ты начинаешь с понимания общей картины, а уже потом переходишь к действиям.",
      supporting: dominant ? supportingLines(dominant.id, candidates) : [],
      whyExplanation: buildDominantWhyExplanation(whyCtx),
    },
    miniPortrait,
    portraitCards,
    moreObservations,
    surprise: surpriseRaw
      ? {
          label: "Одна деталь, которая может удивить",
          body: surpriseRaw.text,
          whyExplanation: buildGlobalWhySummary(whyCtx),
        }
      : null,
    closingMessage:
      "Это начало узнавания. Сохрани профиль через email — карта останется с тобой. Уточнить время и место можно сейчас или позже.",
    refineHint:
      "Без точного времени Асцендент и дома ещё закрыты. Уточнение добавит глубину — сохранение закрепит основу.",
    nameInsight: buildNameInsight(displayName),
    saveCtaLabel: "Сохранить профиль",
    refineCtaLabel: "Уточнить время и место",
    limitationsLabels: limitationsFromNatalFacts(draft.natal_facts),
    audit,
  };
}

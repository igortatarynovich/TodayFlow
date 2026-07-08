import { normText, textSimilarity } from "@/lib/interpretation/formatRecognitionText";
import {
  inferObservationThemes,
  isTooSimilarToAny,
  registerThemes,
} from "@/lib/interpretation/dedupeObservations";
import { frameForCardType } from "@/lib/interpretation/generateBirthMetadataCandidates";
import type { ObservationCandidate } from "@/lib/interpretation/onboardingRecognitionTypes";
import { MIN_RECOGNITION_SCORE } from "@/lib/interpretation/onboardingRecognitionTypes";
import {
  PORTRAIT_DIMENSIONS,
  PORTRAIT_POOL_TARGET,
  PORTRAIT_VISIBLE_COUNT,
  type PortraitCardType,
  type PortraitDimensionId,
} from "@/lib/interpretation/portraitDimensions";

function dimensionScore(candidate: ObservationCandidate, dimensionId: PortraitDimensionId): number {
  const spec = PORTRAIT_DIMENSIONS.find((d) => d.id === dimensionId);
  if (!spec) return 0;

  let score = candidate.score;
  if (spec.preferredLens === candidate.lens) score *= 1.25;

  if (
    spec.preferredReferenceKeys?.some((key) =>
      candidate.evidence.some((ev) => ev.referenceKey.includes(key.split("[")[0] ?? key)),
    )
  ) {
    score *= 1.35;
  }

  if (inferObservationThemes(candidate.text).has(spec.themeFocus)) score *= 1.2;

  return score;
}

export type RankedPortraitCard = ObservationCandidate & {
  dimensionId: PortraitDimensionId;
  dimensionIcon: string;
  dimensionTitle: string;
  cardType: PortraitCardType;
  displayBody: string;
};

function passesDedupe(
  candidate: ObservationCandidate,
  selectedTexts: string[],
  usedThemes: Set<string>,
  dimensionTheme: string,
): boolean {
  if (isTooSimilarToAny(candidate.text, selectedTexts, 0.36)) return false;

  for (const theme of Array.from(inferObservationThemes(candidate.text))) {
    if (theme === dimensionTheme) continue;
    if (usedThemes.has(theme)) return false;
  }
  return true;
}

export function rankPortraitInsightCards(candidates: ObservationCandidate[]): RankedPortraitCard[] {
  const eligible = candidates.filter(
    (c) => c.score >= MIN_RECOGNITION_SCORE && c.evidence.length > 0 && c.text.trim().length >= 18,
  );

  const selected: RankedPortraitCard[] = [];
  const selectedTexts: string[] = [];
  const usedThemes = new Set<string>();

  for (const spec of PORTRAIT_DIMENSIONS) {
    const best = [...eligible]
      .filter((c) => !selected.some((s) => s.id === c.id))
      .filter((c) => passesDedupe(c, selectedTexts, usedThemes, spec.themeFocus))
      .sort((a, b) => dimensionScore(b, spec.id) - dimensionScore(a, spec.id))[0];

    if (!best) continue;

    selected.push({
      ...best,
      dimensionId: spec.id,
      dimensionIcon: spec.icon,
      dimensionTitle: spec.title,
      cardType: spec.cardType,
      displayBody: frameForCardType(spec.cardType, best.text),
    });
    selectedTexts.push(best.text);
    registerThemes(best.text, usedThemes);
    if (selected.length >= PORTRAIT_POOL_TARGET) break;
  }

  if (selected.length < PORTRAIT_VISIBLE_COUNT) {
    for (const spec of PORTRAIT_DIMENSIONS) {
      if (selected.some((s) => s.dimensionId === spec.id)) continue;
      const best = [...eligible]
        .filter((c) => !selected.some((s) => s.id === c.id))
        .filter((c) => !isTooSimilarToAny(c.text, selectedTexts, 0.42))
        .sort((a, b) => dimensionScore(b, spec.id) - dimensionScore(a, spec.id))[0];
      if (!best) continue;

      selected.push({
        ...best,
        dimensionId: spec.id,
        dimensionIcon: spec.icon,
        dimensionTitle: spec.title,
        cardType: spec.cardType,
        displayBody: frameForCardType(spec.cardType, best.text),
      });
      selectedTexts.push(best.text);
      if (selected.length >= PORTRAIT_VISIBLE_COUNT) break;
    }
  }

  return selected;
}

export function splitVisibleAndMore(cards: RankedPortraitCard[]): {
  visible: RankedPortraitCard[];
  more: RankedPortraitCard[];
} {
  const visible = cards.slice(0, PORTRAIT_VISIBLE_COUNT);
  const visibleIds = new Set(visible.map((c) => c.id));
  const more = cards.filter((c) => !visibleIds.has(c.id));
  return { visible, more };
}

export function pickDominantTrait(
  candidates: ObservationCandidate[],
  excludeTexts: string[],
): ObservationCandidate | null {
  const fromLifePath = candidates
    .filter(
      (c) =>
        c.evidence.some(
          (e) =>
            e.referenceKey.includes("life_path.pattern") ||
            e.referenceKey.includes("life_path.life_theme") ||
            e.referenceKey.includes("life_path.essence"),
        ) && !isTooSimilarToAny(c.text, excludeTexts, 0.32),
    )
    .sort((a, b) => b.score - a.score)[0];

  if (fromLifePath) return fromLifePath;

  return (
    candidates
      .filter((c) => c.lens === "noticed_by_others" && !isTooSimilarToAny(c.text, excludeTexts, 0.32))
      .sort((a, b) => b.score - a.score)[0] ?? null
  );
}

export function pickOverflowSurprise(
  candidates: ObservationCandidate[],
  usedIds: Set<string>,
  excludeTexts: string[],
): ObservationCandidate | null {
  return (
    candidates
      .filter(
        (c) =>
          !usedIds.has(c.id) &&
          c.score >= MIN_RECOGNITION_SCORE &&
          !isTooSimilarToAny(c.text, excludeTexts, 0.34) &&
          (c.evidence.some((e) => e.referenceKey.includes("paradox")) ||
            c.evidence.some((e) => e.referenceKey.includes("reading")) ||
            c.lens === "tension"),
      )
      .sort((a, b) => b.score - a.score)[0] ?? null
  );
}

export function cardsAreDistinct(cards: RankedPortraitCard[]): boolean {
  for (let i = 0; i < cards.length; i++) {
    for (let j = i + 1; j < cards.length; j++) {
      if (textSimilarity(cards[i].text, cards[j].text) > 0.45) return false;
    }
  }
  return true;
}

export function buildMiniPortraitBullets(candidates: ObservationCandidate[], excludeTexts: string[]): string[] {
  return candidates
    .filter((c) => c.lens === "noticed_by_others" && !isTooSimilarToAny(c.text, excludeTexts, 0.4))
    .slice(0, 3)
    .map((c) => c.text);
}

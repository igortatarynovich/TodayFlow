/**
 * Кольца прогресса: тексты из `src/data/rewardRings.ru.json` (локаль / будущий CMS).
 * Список `reward_rings_earned` приходит с `/today` и совпадает с `compute_reward_rings_earned` на бэкенде.
 */

import rewardRingsRu from "@/data/rewardRings.ru.json";

export type RewardRingTier = {
  id: string;
  order: number;
  tierKey: string;
  minEvolutionIndex: number;
  titleRu: string;
  collectViaRu: string;
  grantsRu: string[];
  futureMerchRu: string;
};

export type RewardRingsCopy = {
  locale: string;
  intro: string;
  ringsIntroShort: string;
  rankLabel: string;
  growthIndexLabel: string;
  growthScaleHint: string;
  progressToNextRing: string;
  segmentPartLabel: string;
  progressMaxedShort: string;
  earnChannelsTitle: string;
  earnChannelToday: string;
  earnChannelTrackers: string;
  earnChannelGoals: string;
  earnChannelHabits: string;
  earnChannelAscetics: string;
  earnChannelPractices: string;
  earnChannelJournal: string;
  merchFootnote: string;
  allComplete: string;
  detailsSummary: string;
  nextGrantsTitle: string;
  nextSectionEyebrow: string;
  collectedLabel: string;
  todayStripTitle: string;
  todayStripSubtitle: string;
  todayStripCta: string;
  todayStripProgressWord: string;
  inAppLabel: string;
  earnedSuffix: string;
  nextSuffix: string;
  archetypeInSystemLabel: string;
  howIndexWorksLink: string;
  scoresBreakdownTitle: string;
  scoresBreakdownHint: string;
  scoreDisciplineLabel: string;
  scoreReflectionLabel: string;
  scoreEnergyLabel: string;
  scoreMindLabel: string;
  profilePageTitle: string;
  profileBirthDataButton: string;
  profileContourEyebrow: string;
  profileContourBody: string;
  indexPeakExplainer: string;
  helpHubLinkLabel: string;
  helpNavLabel: string;
  levelStripAria: string;
  profileHeaderAchievementsCta: string;
  achievementsPageIntro: string;
  achievementsHintTitle: string;
  achievementsHintP1: string;
  achievementsHintRingsProgress: string;
  achievementsSectionIndex: string;
  achievementsSectionContour: string;
  achievementsSectionStreaks: string;
  achievementsSectionSeals: string;
  streakDailyLabel: string;
  streakWeeklyLabel: string;
  streakHabitLabel: string;
  streakAsceticLabel: string;
  streakTarotLabel: string;
  achievementsFooterRingsLink: string;
  achievementsUnavailableHint: string;
  achievementsOpenTodayLink: string;
};

const catalog = rewardRingsRu as RewardRingsCopy & { tiers: RewardRingTier[] };

export const REWARD_RINGS_COPY: RewardRingsCopy = {
  locale: catalog.locale,
  intro: catalog.intro,
  ringsIntroShort: catalog.ringsIntroShort,
  rankLabel: catalog.rankLabel,
  growthIndexLabel: catalog.growthIndexLabel,
  growthScaleHint: catalog.growthScaleHint,
  progressToNextRing: catalog.progressToNextRing,
  segmentPartLabel: catalog.segmentPartLabel,
  progressMaxedShort: catalog.progressMaxedShort,
  earnChannelsTitle: catalog.earnChannelsTitle,
  earnChannelToday: catalog.earnChannelToday,
  earnChannelTrackers: catalog.earnChannelTrackers,
  earnChannelGoals: catalog.earnChannelGoals,
  earnChannelHabits: catalog.earnChannelHabits,
  earnChannelAscetics: catalog.earnChannelAscetics,
  earnChannelPractices: catalog.earnChannelPractices,
  earnChannelJournal: catalog.earnChannelJournal,
  merchFootnote: catalog.merchFootnote,
  allComplete: catalog.allComplete,
  detailsSummary: catalog.detailsSummary,
  nextGrantsTitle: catalog.nextGrantsTitle,
  nextSectionEyebrow: catalog.nextSectionEyebrow,
  collectedLabel: catalog.collectedLabel,
  todayStripTitle: catalog.todayStripTitle,
  todayStripSubtitle: catalog.todayStripSubtitle,
  todayStripCta: catalog.todayStripCta,
  todayStripProgressWord: catalog.todayStripProgressWord,
  inAppLabel: catalog.inAppLabel,
  earnedSuffix: catalog.earnedSuffix,
  nextSuffix: catalog.nextSuffix,
  archetypeInSystemLabel: catalog.archetypeInSystemLabel,
  howIndexWorksLink: catalog.howIndexWorksLink,
  scoresBreakdownTitle: catalog.scoresBreakdownTitle,
  scoresBreakdownHint: catalog.scoresBreakdownHint,
  scoreDisciplineLabel: catalog.scoreDisciplineLabel,
  scoreReflectionLabel: catalog.scoreReflectionLabel,
  scoreEnergyLabel: catalog.scoreEnergyLabel,
  scoreMindLabel: catalog.scoreMindLabel,
  profilePageTitle: catalog.profilePageTitle,
  profileBirthDataButton: catalog.profileBirthDataButton,
  profileContourEyebrow: catalog.profileContourEyebrow,
  profileContourBody: catalog.profileContourBody,
  indexPeakExplainer: catalog.indexPeakExplainer,
  helpHubLinkLabel: catalog.helpHubLinkLabel,
  helpNavLabel: catalog.helpNavLabel,
  levelStripAria: catalog.levelStripAria,
  profileHeaderAchievementsCta: catalog.profileHeaderAchievementsCta,
  achievementsPageIntro: catalog.achievementsPageIntro,
  achievementsHintTitle: catalog.achievementsHintTitle,
  achievementsHintP1: catalog.achievementsHintP1,
  achievementsHintRingsProgress: catalog.achievementsHintRingsProgress,
  achievementsSectionIndex: catalog.achievementsSectionIndex,
  achievementsSectionContour: catalog.achievementsSectionContour,
  achievementsSectionStreaks: catalog.achievementsSectionStreaks,
  achievementsSectionSeals: catalog.achievementsSectionSeals,
  streakDailyLabel: catalog.streakDailyLabel,
  streakWeeklyLabel: catalog.streakWeeklyLabel,
  streakHabitLabel: catalog.streakHabitLabel,
  streakAsceticLabel: catalog.streakAsceticLabel,
  streakTarotLabel: catalog.streakTarotLabel,
  achievementsFooterRingsLink: catalog.achievementsFooterRingsLink,
  achievementsUnavailableHint: catalog.achievementsUnavailableHint,
  achievementsOpenTodayLink: catalog.achievementsOpenTodayLink,
};

export const REWARD_RING_TIERS: RewardRingTier[] = [...catalog.tiers].sort((a, b) => a.order - b.order);

export type RingState = {
  tier: RewardRingTier;
  earned: boolean;
  isNext: boolean;
};

function earnedIdsFromApi(rewardRingsEarned: string[] | null | undefined): Set<string> | null {
  if (!Array.isArray(rewardRingsEarned)) return null;
  return new Set(rewardRingsEarned);
}

function tierEarned(tier: RewardRingTier, evolutionIndex: number, earnedSet: Set<string> | null): boolean {
  if (earnedSet) return earnedSet.has(tier.id);
  const safe = Math.max(0, Math.min(100, Math.round(evolutionIndex)));
  return safe >= tier.minEvolutionIndex;
}

export function getRewardRingStates(
  evolutionIndex: number,
  rewardRingsEarned?: string[] | null,
): RingState[] {
  const sorted = [...REWARD_RING_TIERS].sort((a, b) => a.order - b.order);
  const earnedSet = earnedIdsFromApi(rewardRingsEarned ?? undefined);
  const firstLockedIdx = sorted.findIndex((tier) => !tierEarned(tier, evolutionIndex, earnedSet));
  return sorted.map((tier, i) => ({
    tier,
    earned: tierEarned(tier, evolutionIndex, earnedSet),
    isNext: firstLockedIdx >= 0 && i === firstLockedIdx,
  }));
}

export function getNextRewardRing(
  evolutionIndex: number,
  rewardRingsEarned?: string[] | null,
): RewardRingTier | null {
  return getRewardRingStates(evolutionIndex, rewardRingsEarned).find((s) => s.isNext)?.tier ?? null;
}

function clampEvolution(evolutionIndex: number): number {
  return Math.max(0, Math.min(100, Math.round(evolutionIndex)));
}

/** Последнее по порядку кольцо, уже «зажжённое» по правилам earned. */
export function getHighestEarnedRingTier(
  evolutionIndex: number,
  rewardRingsEarned?: string[] | null,
): RewardRingTier {
  const states = getRewardRingStates(evolutionIndex, rewardRingsEarned);
  const earned = states.filter((s) => s.earned);
  if (!earned.length) return REWARD_RING_TIERS[0];
  return earned[earned.length - 1].tier;
}

/** Визуал полоски и «солнца» кольца по уровню (1…7). */
export function getTierProgressVisual(tierOrder: number): {
  stripGradient: string;
  ringBackground: string;
  ringShadow: string;
  ringBorder: string;
} {
  const o = Math.min(7, Math.max(1, tierOrder));
  const table: Record<number, { stripGradient: string; ringBackground: string; ringShadow: string; ringBorder: string }> = {
    1: {
      stripGradient: "linear-gradient(90deg, #787f87 0%, #b8c0c9 55%, #e2e8f0 100%)",
      ringBackground: "radial-gradient(circle at 32% 28%, #ffffff 0%, #cbd5e1 45%, #64748b 92%)",
      ringShadow: "0 0 0 2px rgba(255,255,255,0.95), 0 0 14px rgba(100, 116, 139, 0.35)",
      ringBorder: "1px solid rgba(148, 163, 184, 0.5)",
    },
    2: {
      stripGradient: "linear-gradient(90deg, #6d5f52 0%, #a89078 50%, #d4c4b0 100%)",
      ringBackground: "radial-gradient(circle at 32% 28%, #fffaf5 0%, #d6c4b0 42%, #8a745f 90%)",
      ringShadow: "0 0 0 2px rgba(255,255,255,0.95), 0 0 16px rgba(138, 116, 95, 0.38)",
      ringBorder: "1px solid rgba(168, 144, 120, 0.55)",
    },
    3: {
      stripGradient: "linear-gradient(90deg, #5c5548 0%, #9d8b6f 48%, #d2bc96 100%)",
      ringBackground: "radial-gradient(circle at 32% 28%, #fff9ed 0%, #e8d5b8 40%, #b8956a 88%)",
      ringShadow: "0 0 0 2px rgba(255,255,255,0.95), 0 0 18px rgba(184, 149, 106, 0.42)",
      ringBorder: "1px solid rgba(201, 166, 107, 0.55)",
    },
    4: {
      stripGradient: "linear-gradient(90deg, #8b5a2a 0%, #c9a66b 45%, #f0dcaa 100%)",
      ringBackground: "radial-gradient(circle at 32% 28%, #fff8ea 0%, #e8c896 38%, #b87a2e 88%)",
      ringShadow: "0 0 0 2px rgba(255,255,255,0.95), 0 0 20px rgba(184, 122, 46, 0.45)",
      ringBorder: "1px solid rgba(201, 139, 74, 0.6)",
    },
    5: {
      stripGradient: "linear-gradient(90deg, #7c3aed 0%, #c4b5fd 40%, #fef3c7 100%)",
      ringBackground: "radial-gradient(circle at 32% 28%, #faf5ff 0%, #ddd6fe 35%, #7c3aed 88%)",
      ringShadow: "0 0 0 2px rgba(255,255,255,0.95), 0 0 22px rgba(124, 58, 237, 0.4)",
      ringBorder: "1px solid rgba(167, 139, 250, 0.65)",
    },
    6: {
      stripGradient: "linear-gradient(90deg, #4a3728 0%, #b45309 42%, #fbbf24 100%)",
      ringBackground: "radial-gradient(circle at 32% 28%, #fffbeb 0%, #fcd34d 36%, #b45309 88%)",
      ringShadow: "0 0 0 2px rgba(255,255,255,0.95), 0 0 22px rgba(180, 83, 9, 0.48)",
      ringBorder: "1px solid rgba(251, 191, 36, 0.65)",
    },
    7: {
      stripGradient: "linear-gradient(90deg, #1e1b4b 0%, #6366f1 38%, #e9d5ff 92%)",
      ringBackground: "radial-gradient(circle at 32% 28%, #faf5ff 0%, #c4b5fd 34%, #4338ca 90%)",
      ringShadow: "0 0 0 2px rgba(255,255,255,0.95), 0 0 24px rgba(67, 56, 202, 0.5)",
      ringBorder: "1px solid rgba(165, 180, 252, 0.7)",
    },
  };
  return table[o]!;
}

export type ProgressToNextRing = {
  safeIndex: number;
  prevThreshold: number;
  nextThreshold: number | null;
  nextTier: RewardRingTier | null;
  /** Доля пути между prev и next порогом, 0–100 */
  pctInSegment: number;
  isMax: boolean;
};

/** Прогресс по порогам только от текущего индекса (без списка колец с бэкенда). */
function getProgressToNextRingIndexOnly(evolutionIndex: number): ProgressToNextRing {
  const safeIndex = clampEvolution(evolutionIndex);
  const byThreshold = [...REWARD_RING_TIERS].sort((a, b) => a.minEvolutionIndex - b.minEvolutionIndex);
  let prevThreshold = byThreshold[0].minEvolutionIndex;
  let nextTier: RewardRingTier | null = null;
  let nextThreshold: number | null = null;

  for (let i = 1; i < byThreshold.length; i += 1) {
    const t = byThreshold[i];
    if (safeIndex < t.minEvolutionIndex) {
      nextTier = t;
      nextThreshold = t.minEvolutionIndex;
      prevThreshold = byThreshold[i - 1].minEvolutionIndex;
      break;
    }
    prevThreshold = t.minEvolutionIndex;
  }

  if (nextThreshold === null) {
    return {
      safeIndex,
      prevThreshold: byThreshold[byThreshold.length - 1].minEvolutionIndex,
      nextThreshold: null,
      nextTier: null,
      pctInSegment: 100,
      isMax: true,
    };
  }

  const span = Math.max(1, nextThreshold - prevThreshold);
  const pctInSegment = Math.max(0, Math.min(100, Math.round(((safeIndex - prevThreshold) / span) * 100)));
  return {
    safeIndex,
    prevThreshold,
    nextThreshold,
    nextTier,
    pctInSegment,
    isMax: false,
  };
}

/**
 * Прогресс до следующего **ещё не заработанного** кольца.
 * Если передан `reward_rings_earned` с `/today`, отрезок считается от предыдущего кольца к следующему
 * в лестнице, даже при просадке текущего индекса.
 */
export function getProgressToNextRing(evolutionIndex: number, rewardRingsEarned?: string[] | null): ProgressToNextRing {
  const earnedSet = earnedIdsFromApi(rewardRingsEarned ?? undefined);
  if (earnedSet === null || earnedSet.size === 0) {
    return getProgressToNextRingIndexOnly(evolutionIndex);
  }

  const safeIndex = clampEvolution(evolutionIndex);
  const states = getRewardRingStates(evolutionIndex, rewardRingsEarned);
  const nextState = states.find((s) => s.isNext);
  const byOrder = [...REWARD_RING_TIERS].sort((a, b) => a.order - b.order);

  if (!nextState) {
    const last = byOrder[byOrder.length - 1];
    return {
      safeIndex,
      prevThreshold: last.minEvolutionIndex,
      nextThreshold: null,
      nextTier: null,
      pctInSegment: 100,
      isMax: true,
    };
  }

  const nextTier = nextState.tier;
  const idx = byOrder.findIndex((t) => t.id === nextTier.id);
  const prevTier = idx > 0 ? byOrder[idx - 1]! : byOrder[0]!;
  const prevThreshold = prevTier.minEvolutionIndex;
  const nextThreshold = nextTier.minEvolutionIndex;
  const span = Math.max(1, nextThreshold - prevThreshold);
  const pctInSegment = Math.max(0, Math.min(100, Math.round(((safeIndex - prevThreshold) / span) * 100)));
  return {
    safeIndex,
    prevThreshold,
    nextThreshold,
    nextTier,
    pctInSegment,
    isMax: false,
  };
}

export type StreakTier = {
  key: string;
  title: string;
  targetDays: number;
};

export type EvolutionTier = {
  key: string;
  title: string;
  minIndex: number;
};

export const STREAK_TIERS: StreakTier[] = [
  { key: "spark", title: "Spark", targetDays: 7 },
  { key: "flame", title: "Flame", targetDays: 21 },
  { key: "radiance", title: "Radiance", targetDays: 40 },
  { key: "solar_cycle", title: "Solar Cycle", targetDays: 90 },
  { key: "lunar_master", title: "Lunar Master", targetDays: 180 },
  { key: "inner_architect", title: "Inner Architect", targetDays: 365 },
];

export const EVOLUTION_TIERS: EvolutionTier[] = [
  { key: "seeker", title: "Seeker", minIndex: 0 },
  { key: "initiate", title: "Initiate", minIndex: 38 },
  { key: "observer", title: "Observer", minIndex: 50 },
  { key: "alchemist", title: "Alchemist", minIndex: 62 },
  { key: "oracle", title: "Oracle", minIndex: 70 },
  { key: "architect", title: "Architect", minIndex: 78 },
  { key: "sage", title: "Sage", minIndex: 85 },
];

type StreakProgress = {
  currentTier: StreakTier;
  nextTier: StreakTier | null;
  progressPct: number;
  daysInTier: number;
  daysToNext: number;
};

type EvolutionProgress = {
  currentTier: EvolutionTier;
  nextTier: EvolutionTier | null;
  progressPct: number;
  currentXp: number;
  nextXp: number;
  totalXp: number;
};

function clampPct(value: number): number {
  return Math.max(0, Math.min(100, Math.round(value)));
}

export function getStreakProgress(days: number): StreakProgress {
  const safeDays = Math.max(0, Math.floor(days));
  const tiers = STREAK_TIERS;
  const first = tiers[0];
  let current = first;
  let next: StreakTier | null = first;

  for (let i = 0; i < tiers.length; i += 1) {
    const tier = tiers[i];
    if (safeDays >= tier.targetDays) {
      current = tier;
      next = tiers[i + 1] || null;
    } else {
      next = tier;
      break;
    }
  }

  if (!next) {
    return {
      currentTier: current,
      nextTier: null,
      progressPct: 100,
      daysInTier: safeDays - current.targetDays,
      daysToNext: 0,
    };
  }

  const tierStart = current === next ? 0 : current.targetDays;
  const tierSpan = Math.max(1, next.targetDays - tierStart);
  const progressPct = clampPct(((safeDays - tierStart) / tierSpan) * 100);

  return {
    currentTier: current,
    nextTier: next,
    progressPct,
    daysInTier: Math.max(0, safeDays - tierStart),
    daysToNext: Math.max(0, next.targetDays - safeDays),
  };
}

export function getEvolutionProgress(evolutionIndex: number): EvolutionProgress {
  const safeIndex = Math.max(0, Math.min(100, Math.round(evolutionIndex)));
  const tiers = EVOLUTION_TIERS;
  let current = tiers[0];
  let next: EvolutionTier | null = null;

  for (let i = 0; i < tiers.length; i += 1) {
    const tier = tiers[i];
    if (safeIndex >= tier.minIndex) {
      current = tier;
      next = tiers[i + 1] || null;
    } else {
      next = tier;
      break;
    }
  }

  const currentFloor = current.minIndex;
  const nextCap = next?.minIndex ?? 100;
  const range = Math.max(1, nextCap - currentFloor);
  const progressPct = next ? clampPct(((safeIndex - currentFloor) / range) * 100) : 100;

  const totalXp = safeIndex * 100;
  const currentXp = currentFloor * 100;
  const nextXp = nextCap * 100;

  return {
    currentTier: current,
    nextTier: next,
    progressPct,
    currentXp,
    nextXp,
    totalXp,
  };
}

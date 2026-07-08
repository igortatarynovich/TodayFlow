export type RewardSeal = {
  code: string;
  title: string;
  strength: number;
};

export type RewardMilestone = {
  name: string;
  target_days: number;
  status: "done" | "next";
  days_left: number;
};

export type RewardsSnapshot = {
  archetype_seed?: string | null;
  archetype_level: string;
  archetype_progress?: {
    current: string;
    next: string | null;
    progress_pct: number;
    requirements: {
      evolution_min: number;
      daily_streak_min: number;
      reflection_min: number;
    };
  };
  streaks: {
    daily_current: number;
    weekly_current: number;
    habit_best: number;
    ascetic_best: number;
    tarot_current: number;
  };
  scores: {
    mind: number;
    energy: number;
    discipline: number;
    reflection: number;
  };
  evolution_index: number;
  /** Максимальный достигнутый индекс (кольца считаются по пику, не по текущему дню) */
  reward_evolution_index_peak?: number;
  /** Id колец, собранных по индексу эволюции; с бэкенда `/today` для мерча и единого источника правды */
  reward_rings_earned?: string[];
  seals: RewardSeal[];
  message: string;
};

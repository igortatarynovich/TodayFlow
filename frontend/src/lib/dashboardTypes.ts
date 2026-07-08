export type Practice = {
  id: string;
  title: string;
  description: string;
  category: string;
  duration_minutes?: number;
  difficulty: string;
  is_free: boolean;
  is_personalized: boolean;
  personalized_reason?: string;
  access_level: string;
  tags: string[];
  target_axis?: string;
};

export type Challenge = {
  id: string;
  title: string;
  description: string;
  duration: number;
  goal: string;
  challenge_type?: "tracker" | "ascetic" | "goal" | "habit";
  icon?: string;
  color?: string;
};

export type ChallengeParticipation = {
  id: number;
  challenge_id: string;
  started_at: string;
  completed_at?: string;
  current_day: number;
  is_active: boolean;
  challenge?: Challenge;
  current_streak_days?: number;
  longest_streak_days?: number;
};

export type DailyTask = {
  id: string;
  title: string;
  duration?: string;
  completed: boolean;
};

export type NumerologyDailyInsight = {
  date: string;
  number: {
    title: string;
    value: number;
    reduced_value: number;
    is_master: boolean;
    summary: string;
  };
};


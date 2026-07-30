import type {
  FusionResponse,
  MorningRitualData,
  PracticeResponse,
  TodayCycleData,
} from "@/components/today/todayPageUtils";
import type { TodayWebPractice } from "@/components/product-ui/TodayWebDashboard";
import type { DsTimelineEvent } from "@/design-system";

/**
 * Right-rail day timeline.
 *
 * Morning `celestial_events.sky_aspects` / `personal_transits` have titles but
 * **no clock**. Inventing DEFAULT_TIMES (07:30 / 11:15 / …) made a decorative
 * fake timeline that contradicted Glance nearest honesty.
 *
 * SoT for timed day marks is Wave 2 `glance_timeline` (exact-time). Until the
 * rail is wired to that payload with real `time_local`, return empty.
 */
export function buildTodayWebTimeline(_morning?: MorningRitualData | null): DsTimelineEvent[] {
  return [];
}

/**
 * Weekly rhythm for Today rail. Returns null when there is no real per-day signal
 * (PR-2: no synthetic wave bars).
 */
export function buildTodayWebWeeklyActivity(input: {
  dailySteps: Array<{ done: boolean }>;
  fusion?: FusionResponse | null;
}): number[] | null {
  const steps = input.dailySteps;
  if (steps.length >= 7) {
    return steps.slice(-7).map((step) => (step.done ? 1 : 0));
  }
  if (steps.length > 0) {
    const padded = Array.from({ length: 7 }, (_, index) => {
      const step = steps[index];
      return step ? (step.done ? 1 : 0) : 0;
    });
    // Only surface when at least one real done step exists.
    return padded.some((v) => v > 0) ? padded : null;
  }
  return null;
}

export function buildTodayWebStreak(todayData: TodayCycleData): number {
  return todayData.rewards?.streaks?.daily_current ?? 0;
}

export function buildTodayWebPractices(input: {
  quickPractice?: PracticeResponse | null;
  practiceCompleted?: boolean;
  actionPlan?: string[];
}): TodayWebPractice[] {
  const fromPlan = (input.actionPlan ?? []).slice(0, 3).map((title, index) => ({
    id: `plan-${index}`,
    title,
    durationLabel: undefined,
    completed: input.practiceCompleted && index === 0,
  }));

  if (fromPlan.length >= 2) return fromPlan;

  if (input.quickPractice) {
    return [
      {
        id: String(input.quickPractice.id),
        title: input.quickPractice.title,
        durationLabel: input.quickPractice.duration_minutes
          ? `${input.quickPractice.duration_minutes} мин`
          : undefined,
        completed: input.practiceCompleted,
      },
      ...fromPlan.filter((item) => item.title !== input.quickPractice?.title),
    ];
  }

  return fromPlan;
}

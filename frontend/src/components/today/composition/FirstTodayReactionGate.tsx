"use client";

import { useState } from "react";
import { OnboardingChipStep } from "@/components/onboarding/OnboardingChipStep";
import { useMeaningRuntime } from "@/hooks/useMeaningRuntime";
import {
  INTENT_CHIP_OPTIONS,
  REALITY_CHIP_OPTIONS,
  buildOnboardingEventIdempotencyKey,
  hasOnboardingIntent,
  hasOnboardingReality,
  readOnboardingContext,
  saveIntentTheme,
  saveRealityState,
  todayDayKey,
  type IntentTheme,
  type RealityState,
} from "@/lib/onboardingContext";

type Props = {
  /** Called once both chips are saved for today. */
  onComplete?: () => void;
};

/**
 * First Today reaction gate (placement C): intent + reality chips inside Today,
 * before ritual / personalized reveal — biases generation without adding funnel steps.
 */
export function FirstTodayReactionGate({ onComplete }: Props) {
  const { trackMeaningEvent } = useMeaningRuntime();
  const dayKey = todayDayKey();
  const initial = readOnboardingContext();
  const [intent, setIntent] = useState<IntentTheme | null>(initial.intent_theme ?? null);
  const [reality, setReality] = useState<RealityState | null>(initial.reality_state ?? null);
  const [phase, setPhase] = useState<"intent" | "reality">(
    hasOnboardingIntent(initial, dayKey) ? "reality" : "intent",
  );
  const [submitting, setSubmitting] = useState(false);

  const finishIfReady = (nextIntent: IntentTheme | null, nextReality: RealityState | null) => {
    if (!nextIntent || !nextReality) return;
    onComplete?.();
  };

  const onSelectIntent = (theme: IntentTheme) => {
    if (submitting) return;
    setSubmitting(true);
    setIntent(theme);
    saveIntentTheme(theme, dayKey);
    trackMeaningEvent({
      event_type: "onboarding_intent_selected",
      event_source: "today",
      quality_score: 1,
      local_date: dayKey,
      payload: { theme, day_key: dayKey, placement: "first_today" },
      idempotency_key: buildOnboardingEventIdempotencyKey("onboarding_intent_selected", theme, dayKey),
      refreshRings: false,
    });
    setPhase("reality");
    setSubmitting(false);
  };

  const onSelectReality = (state: RealityState) => {
    if (submitting) return;
    setSubmitting(true);
    setReality(state);
    saveRealityState(state, dayKey);
    trackMeaningEvent({
      event_type: "onboarding_reality_selected",
      event_source: "today",
      quality_score: 1,
      local_date: dayKey,
      payload: { state, day_key: dayKey, placement: "first_today" },
      idempotency_key: buildOnboardingEventIdempotencyKey("onboarding_reality_selected", state, dayKey),
      refreshRings: false,
    });
    setSubmitting(false);
    finishIfReady(intent ?? readOnboardingContext().intent_theme ?? null, state);
  };

  if (phase === "intent") {
    return (
      <div data-testid="first-today-reaction-gate-intent">
        <OnboardingChipStep
          stepLabel="Перед Today · Фокус"
          title="Что тебе сейчас важнее всего?"
          body="Один выбор — и день подстроится под твой приоритет. Без лишних шагов до этого."
          options={INTENT_CHIP_OPTIONS}
          selectedSlug={intent}
          submitting={submitting}
          onSelect={onSelectIntent}
        />
      </div>
    );
  }

  return (
    <div data-testid="first-today-reaction-gate-reality">
      <OnboardingChipStep
        stepLabel="Перед Today · Состояние"
        title="Как ты сегодня?"
        body="Короткая реакция — Today учтёт ритм, а не только карту."
        options={REALITY_CHIP_OPTIONS}
        selectedSlug={reality}
        submitting={submitting}
        onSelect={onSelectReality}
      />
    </div>
  );
}

export function firstTodayReactionComplete(dayKey = todayDayKey()): boolean {
  const ctx = readOnboardingContext();
  return hasOnboardingIntent(ctx, dayKey) && hasOnboardingReality(ctx, dayKey);
}

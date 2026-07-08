"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { LoadingSpinner } from "@/components/orbit";
import { useAuth } from "@/lib/useAuth";
import { fetchCoreProfileCached } from "@/lib/coreProfileCache";
import { buildAuthHref } from "@/lib/authRedirect";
import { FIRST_TODAY_PATH, hasCompletedFirstToday } from "@/lib/firstTodayState";
import { ONBOARDING_CORE_PATH } from "@/lib/coreSetup";
import { useMeaningRuntime } from "@/hooks/useMeaningRuntime";
import {
  INTENT_CHIP_OPTIONS,
  buildOnboardingEventIdempotencyKey,
  hasOnboardingIntent,
  readOnboardingContext,
  saveIntentTheme,
  todayDayKey,
  type IntentTheme,
} from "@/lib/onboardingContext";
import { OnboardingChipStep } from "@/components/onboarding/OnboardingChipStep";
import { OnboardingAuthGate, OnboardingProductLoading } from "@/components/onboarding/OnboardingProductShell";
import { OnboardingWebScreen } from "@/components/product-ui/OnboardingWebScreen";

export function IntentOnboardingFlow() {
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const router = useRouter();
  const { trackMeaningEvent } = useMeaningRuntime();
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [selected, setSelected] = useState<IntentTheme | null>(null);

  useEffect(() => {
    if (authLoading) return;
    if (!isAuthenticated) {
      setLoading(false);
      return;
    }

    fetchCoreProfileCached()
      .then((core) => {
        if (!core?.is_ready) {
          router.replace(ONBOARDING_CORE_PATH);
          return;
        }
        const ctx = readOnboardingContext();
        if (ctx.intent_theme) setSelected(ctx.intent_theme);
        if (hasOnboardingIntent(ctx) && ctx.reality_state) {
          router.replace(hasCompletedFirstToday() ? "/today" : FIRST_TODAY_PATH);
          return;
        }
        if (hasOnboardingIntent(ctx)) {
          router.replace("/onboarding/reality");
        }
      })
      .finally(() => setLoading(false));
  }, [authLoading, isAuthenticated, router]);

  const handleSelect = (theme: IntentTheme) => {
    if (submitting) return;
    setSelected(theme);
    setSubmitting(true);
    const dayKey = todayDayKey();
    saveIntentTheme(theme, dayKey);
    trackMeaningEvent({
      event_type: "onboarding_intent_selected",
      event_source: "onboarding",
      quality_score: 1,
      local_date: dayKey,
      payload: { theme, day_key: dayKey },
      idempotency_key: buildOnboardingEventIdempotencyKey("onboarding_intent_selected", theme, dayKey),
      refreshRings: false,
    });
    router.push("/onboarding/reality");
  };

  if (authLoading || loading) {
    return (
      <OnboardingProductLoading>
        <LoadingSpinner size="lg" />
      </OnboardingProductLoading>
    );
  }

  if (!isAuthenticated) {
    return (
      <OnboardingAuthGate
        title="Сначала войди в аккаунт"
        body="Чтобы выбрать фокус дня, нужен аккаунт с базовыми данными рождения."
        loginHref={buildAuthHref("login", "/onboarding/intent")}
        signupHref={buildAuthHref("signup", "/onboarding/intent")}
      />
    );
  }

  return (
    <OnboardingWebScreen
      step={2}
      title="Что тебе сейчас важнее всего?"
      lead="Выбери один вариант — Today подстроит тему и главный шаг под твой приоритет."
    >
      <OnboardingChipStep
        stepLabel="Шаг 2 из 3 · Фокус"
        title="Что тебе сейчас важнее всего?"
        body="Выбери один вариант — Today подстроит тему и главный шаг под твой приоритет."
        options={INTENT_CHIP_OPTIONS}
        selectedSlug={selected}
        submitting={submitting}
        onSelect={handleSelect}
        hideHeader
      />
    </OnboardingWebScreen>
  );
}

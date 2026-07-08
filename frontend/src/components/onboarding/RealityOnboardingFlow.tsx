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
  REALITY_CHIP_OPTIONS,
  buildOnboardingEventIdempotencyKey,
  hasOnboardingIntent,
  hasOnboardingReality,
  readOnboardingContext,
  saveRealityState,
  todayDayKey,
  type RealityState,
} from "@/lib/onboardingContext";
import { OnboardingChipStep } from "@/components/onboarding/OnboardingChipStep";
import { OnboardingAuthGate, OnboardingProductLoading } from "@/components/onboarding/OnboardingProductShell";
import { OnboardingWebScreen } from "@/components/product-ui/OnboardingWebScreen";

export function RealityOnboardingFlow() {
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const router = useRouter();
  const { trackMeaningEvent } = useMeaningRuntime();
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [selected, setSelected] = useState<RealityState | null>(null);

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
        if (!hasOnboardingIntent(ctx)) {
          router.replace("/onboarding/intent");
          return;
        }
        if (ctx.reality_state) setSelected(ctx.reality_state);
        if (hasOnboardingReality(ctx)) {
          router.replace(hasCompletedFirstToday() ? "/today" : FIRST_TODAY_PATH);
        }
      })
      .finally(() => setLoading(false));
  }, [authLoading, isAuthenticated, router]);

  const handleSelect = (state: RealityState) => {
    if (submitting) return;
    setSelected(state);
    setSubmitting(true);
    const dayKey = todayDayKey();
    const ctx = readOnboardingContext();
    saveRealityState(state, dayKey);
    trackMeaningEvent({
      event_type: "onboarding_reality_selected",
      event_source: "onboarding",
      quality_score: 1,
      local_date: dayKey,
      payload: { reality_state: state, intent_theme: ctx.intent_theme ?? null, day_key: dayKey },
      idempotency_key: buildOnboardingEventIdempotencyKey("onboarding_reality_selected", state, dayKey),
      refreshRings: false,
    });
    router.push(hasCompletedFirstToday() ? "/today" : FIRST_TODAY_PATH);
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
        body="Один короткий выбор — и откроем твой первый персональный Today."
        loginHref={buildAuthHref("login", "/onboarding/reality")}
        signupHref={buildAuthHref("signup", "/onboarding/reality")}
      />
    );
  }

  return (
    <OnboardingWebScreen
      step={3}
      title="Какой сейчас день по ощущениям?"
      lead="Ещё один тап — и соберём твой первый Today с учётом фокуса и текущего состояния."
    >
      <OnboardingChipStep
        stepLabel="Шаг 3 из 3 · Состояние"
        title="Какой сейчас день по ощущениям?"
        body="Ещё один тап — и соберём твой первый Today с учётом фокуса и текущего состояния."
        options={REALITY_CHIP_OPTIONS}
        selectedSlug={selected}
        submitting={submitting}
        onSelect={handleSelect}
        hideHeader
      />
    </OnboardingWebScreen>
  );
}

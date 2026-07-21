"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { LoadingSpinner } from "@/components/orbit";
import { useAuth } from "@/lib/useAuth";
import { fetchCoreProfileCached } from "@/lib/coreProfileCache";
import { getJson } from "@/lib/api";
import type { CoreProfile, UserSettings } from "@/lib/types";
import { useCoreSetupFlow } from "@/hooks/useCoreSetupFlow";
import { ONBOARDING_CORE_PATH } from "@/lib/coreSetup";
import { buildAuthHref } from "@/lib/authRedirect";
import { OnboardingWebScreen } from "@/components/product-ui/OnboardingWebScreen";
import { OnboardingHeroSection } from "@/components/onboarding/OnboardingHeroSection";
import { ProfileSetupSection } from "@/components/profile/ProfileSetupSection";

function OnboardingLoadingScreen() {
  return (
    <main className="orbit-page todayflow-serene" style={{ background: "#f6f5f2", minHeight: "100vh" }}>
      <div
        style={{
          minHeight: "60vh",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          flexDirection: "column",
          gap: "0.85rem",
        }}
      >
        <LoadingSpinner size="lg" />
        <p className="orbit-body-sm" style={{ margin: 0, color: "#475569" }}>
          Открываем создание профиля…
        </p>
      </div>
    </main>
  );
}

export function CoreOnboardingFlow() {
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [coreProfile, setCoreProfile] = useState<CoreProfile | null>(null);

  const {
    setupForm,
    setSetupForm,
    buildStage,
    setupError,
    setupMessage,
    isBuilding,
    currentBuildState,
    hasResolvedBirthplace,
    buildSteps,
    hydrateSetupForm,
    resetSetupFlow,
    handleCoreSetupSubmit,
  } = useCoreSetupFlow({
    warmNatalPreview: false,
    onCoreProfileUpdated: setCoreProfile,
  });

  useEffect(() => {
    if (authLoading) return;
    if (!isAuthenticated) {
      setLoading(false);
      return;
    }

    Promise.all([
      fetchCoreProfileCached().catch(() => null),
      getJson<UserSettings>("/account/profile").catch(() => null),
    ])
      .then(([core, profile]) => {
        setCoreProfile(core);
        hydrateSetupForm(profile, core);
        if (core?.is_ready) {
          router.replace("/onboarding/intent");
        }
      })
      .finally(() => setLoading(false));
  }, [authLoading, isAuthenticated, hydrateSetupForm, router]);

  if (authLoading || loading) {
    return <OnboardingLoadingScreen />;
  }

  if (!isAuthenticated) {
    const loginHref = buildAuthHref("login", ONBOARDING_CORE_PATH);
    return (
      <OnboardingWebScreen
        step={1}
        title="Сначала собери свой Today"
        lead="Мы мягко спросим имя и дату рождения, покажем первый разбор — и попросим email, чтобы сохранить. Без парольной регистрации."
      >
        <div style={{ display: "grid", gap: "0.85rem", justifyItems: "center" }}>
          <Link href={buildAuthHref("signup", ONBOARDING_CORE_PATH)} className="orbit-button orbit-button-primary">
            Создать мой Today
          </Link>
          <Link href={loginHref} className="orbit-body-sm" style={{ color: "#78716c", textDecoration: "underline" }}>
            Уже есть аккаунт? Войти
          </Link>
        </div>
      </OnboardingWebScreen>
    );
  }

  const showSetupFlow = buildStage !== "idle" || !coreProfile?.is_ready;

  return (
    <OnboardingWebScreen
      step={1}
      title="Расскажи о себе"
      lead="На основе этих данных мы создадим твою персональную натальную карту и настроим поток синтеза."
      footer={
        <>
          Нажимая кнопку, вы соглашаетесь с{" "}
          <Link href="/privacy" style={{ color: "var(--tf-accent-gold-600)" }}>
            Политикой конфиденциальности
          </Link>
          . Ваши данные зашифрованы.
        </>
      }
    >
      {showSetupFlow ? <OnboardingHeroSection buildSteps={buildSteps} /> : null}
      {showSetupFlow ? (
        <ProfileSetupSection
          variant="onboarding"
          currentBuildState={currentBuildState}
          buildStage={buildStage}
          isBuilding={isBuilding}
          setupForm={setupForm}
          hasResolvedBirthplace={hasResolvedBirthplace}
          setupError={setupError}
          setupMessage={setupMessage}
          onFinishSetupFlow={() => router.push("/onboarding/intent")}
          onReopenSetupForm={() => {
            resetSetupFlow();
          }}
          onSubmit={handleCoreSetupSubmit}
          onFieldChange={(field, value) => setSetupForm((prev) => ({ ...prev, [field]: value }))}
          onLocationSelect={(item) =>
            setSetupForm((prev) => ({
              ...prev,
              location_name: (item.local_name || item.name || "").trim(),
              latitude: item.latitude,
              longitude: item.longitude,
            }))
          }
        />
      ) : null}
    </OnboardingWebScreen>
  );
}

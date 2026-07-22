"use client";

import { Suspense, useEffect, useMemo, useState } from "react";
import { enrichCircleItemsWithAstroProfiles } from "@/lib/accountAstroMeta";
import {
  CORE_PROFILE_UPDATED_EVENT,
  publishCoreProfileUpdate,
  type CoreProfileUpdatedDetail,
} from "@/lib/coreProfileCacheStorage";
import { fetchCoreProfileCached } from "@/lib/coreProfileCache";
import { fetchCompactUserModelCached } from "@/lib/compactUserModelCache";
import { ONBOARDING_CORE_PATH } from "@/lib/coreSetup";
import { canClaimGuestProfile, claimGuestProfileAfterAuth } from "@/lib/claimGuestProfile";
import { VALUE_FIRST_PATHS } from "@/lib/guestProfileDraft";
import {
  hasCompletedFirstToday,
  markProfileDepthUnlocked,
  readFirstTodayState,
} from "@/lib/firstTodayState";
import { getLocale } from "@/lib/i18n";
import { profileContractMatchesLocale } from "@/lib/profilePage/profileCopySafety";
import {
  hasOnboardingIntentRecorded,
  hasOnboardingRealityRecorded,
  readOnboardingContext,
  saveIntentTheme,
  saveRealityState,
} from "@/lib/onboardingContext";
import { ProfileFirstDayTeaser } from "@/components/profile/ProfileFirstDayTeaser";
import { useCoreSetupFlow } from "@/hooks/useCoreSetupFlow";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useAuth } from "@/lib/useAuth";
import { getJson, postJson, putJson } from "@/lib/api";
import type { AstroProfile, CoreProfile, CompactUserModel, UserSettings } from "@/lib/types";
import {
  buildQuickCompatibilityRoute,
  getCoreProfileCircle,
  getPrimaryProfileIdFromCore,
} from "@/lib/compatibilityRoutes";
import { ProfileHeroSection } from "@/components/profile/ProfileHeroSection";
import { ProfileSetupSection } from "@/components/profile/ProfileSetupSection";
import { parseProfileSection } from "@/components/profile/profileSections";
import { parseProfileView, PROFILE_CHART_SECTION_ID, PROFILE_LIFE_SPHERES_SECTION_ID } from "@/lib/profileRoutes";
import { ProfileV0Screen } from "@/components/profile/v0/ProfileV0Screen";
import { ProfileV2SystemScreen } from "@/components/profile/v2/ProfileV2SystemScreen";
import { ProfileWebScreen } from "@/components/product-ui/ProfileWebScreen";
import { ProductPageScreen } from "@/components/product-ui/ProductPageScreen";
import { productWebProfileMeta } from "@/lib/productWebUser";
import {
  buildProfileIdentityPills,
  buildProfileRailAnchors,
} from "@/lib/product-ui/profileWebFigmaHelpers";
import { WEB_LAUNCH_MIN_PROFILE } from "@/lib/webLaunchFlags";
import {
  SurfaceInsight,
  SurfaceInsightActions,
  SurfaceInsightBody,
  surfaceInsightStyles,
} from "@/components/foundation/SurfaceInsight";
import routeStyles from "./profileRoute.module.css";
import v0RouteStyles from "@/components/profile/v0/profileV0.module.css";
import "@/components/profile/editorial/profileEditorialRoute.css";
import "@/components/profile/editorial/profileEditorial.module.css";
import "@/components/profile/quickMap/profileQuickMap.module.css";
import { buildProfileV0ViewModel } from "@/lib/profilePage/buildProfileV0Data";
import {
  buildProfileChartFrameworkInput,
  buildProfileQuickMapViewModel,
} from "@/lib/profilePage/buildProfileQuickMapData";
import { buildProfileFrameworkCards } from "@/lib/profilePage/buildProfileFrameworkCards";
import { buildProfileLifeSpheresFromProfileData } from "@/lib/profilePage/profileLifeSpheres";
import {
  isProfilePortraitForming,
  profilePortraitFormingMessage,
} from "@/lib/profilePage/profilePortraitForming";
import { buildProfileV2LiveContext } from "@/lib/profilePage/buildProfileV2LiveContext";
import { listClosedDayContinuityRecords } from "@/lib/todayDayContinuity";
import type { NatalChartPreview } from "@/components/profile/profilePanelTypes";
import {
  buildLifeMapSections,
  buildRisingOverviewHint,
  getPlanetSignId,
  getRisingSignId,
  layerSignLabel,
  resolveMcSignLabel,
} from "@/lib/profilePage/buildProfilePlanetaryData";
import {
  getLifePathEntry,
  getMoonInSignEntry,
  getRisingSignEntry,
  getSunInSignEntry,
} from "@/lib/zodiacKnowledge";

type AstroProfilesResponse = {
  profiles: AstroProfile[];
};

function ProfileLoadingScreen() {
  return (
    <ProductPageScreen
      testId="profile-loading"
      title="Профиль"
      loading
      loadingLabel="Загрузка…"
      hideDatePill
    />
  );
}

function ProfileHubPageInner() {
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();
  const activeSection = parseProfileSection(searchParams.get("section"));
  const profileView = parseProfileView(searchParams.get("view"));
  const profileDepthRequested = searchParams.get("depth") === "1";
  const [profileDepthUnlocked, setProfileDepthUnlocked] = useState(false);
  const [journeyChecked, setJourneyChecked] = useState(false);
  const [coreProfile, setCoreProfile] = useState<CoreProfile | null>(null);
  const [compactUserModel, setCompactUserModel] = useState<CompactUserModel | null>(null);
  const [astroProfiles, setAstroProfiles] = useState<AstroProfile[]>([]);
  const [forceSetup, setForceSetup] = useState(false);
  const [focusArea, setFocusArea] = useState<string | null>(null);
  const [queryChecked, setQueryChecked] = useState(false);
  const [claimChecked, setClaimChecked] = useState(false);
  const [loading, setLoading] = useState(true);

  const {
    setupForm,
    setSetupForm,
    buildStage,
    setBuildStage,
    setupError,
    setupMessage,
    setSetupMessage,
    natalPreview,
    previewError,
    isBuilding,
    currentBuildState,
    hasResolvedBirthplace,
    buildSteps,
    hydrateSetupForm,
    resetSetupFlow,
    handleCoreSetupSubmit,
    loadNatalPreview,
  } = useCoreSetupFlow({
    warmNatalPreview: true,
    onCoreProfileUpdated: setCoreProfile,
    onAstroProfilesUpdated: setAstroProfiles,
  });

  useEffect(() => {
    if (!WEB_LAUNCH_MIN_PROFILE || typeof window === "undefined") return;
    if (!hasOnboardingIntentRecorded()) saveIntentTheme("focus");
    if (!hasOnboardingRealityRecorded()) saveRealityState("stable");
  }, []);

  useEffect(() => {
    if (authLoading || claimChecked) return;
    // Guests have no profile to claim — resolve the gate so the login/CTA screen shows
    // instead of an infinite loading spinner.
    if (!isAuthenticated) {
      setClaimChecked(true);
      return;
    }
    if (!canClaimGuestProfile()) {
      setClaimChecked(true);
      return;
    }

    void (async () => {
      try {
        const claim = await claimGuestProfileAfterAuth();
        if (claim.status === "needs_refine") {
          router.replace(claim.refinePath);
          return;
        }
        if (claim.status === "ready") {
          const core = await fetchCoreProfileCached({ force: true });
          if (core) setCoreProfile(core);
        }
      } catch {
        // Claim can fail independently; profile still renders with setup CTA.
      } finally {
        setClaimChecked(true);
      }
    })();
  }, [isAuthenticated, authLoading, claimChecked, router]);

  useEffect(() => {
    if (typeof window === "undefined") return;
    setProfileDepthUnlocked(readFirstTodayState().profile_depth_unlocked === true);
    setJourneyChecked(true);
  }, []);

  useEffect(() => {
    if (profileDepthRequested && !profileDepthUnlocked) {
      markProfileDepthUnlocked();
      setProfileDepthUnlocked(true);
    }
  }, [profileDepthRequested, profileDepthUnlocked]);

  useEffect(() => {
    if (typeof window === "undefined") return;
    const params = new URLSearchParams(window.location.search);
    if (params.get("setup") === "core") {
      router.replace(ONBOARDING_CORE_PATH);
      return;
    }
    setFocusArea(params.get("focus"));
    if (params.get("focus") === "numerology" && !params.get("section")) {
      params.set("section", "chart");
      window.history.replaceState({}, "", `${window.location.pathname}?${params.toString()}`);
    }
    setQueryChecked(true);
  }, [router]);

  useEffect(() => {
    if (!isAuthenticated) {
      setLoading(false);
      return;
    }

    Promise.all([
      fetchCoreProfileCached().catch(() => null),
      fetchCompactUserModelCached().catch(() => null),
      getJson<UserSettings>("/account/profile").catch(() => null),
      getJson<AstroProfilesResponse>("/account/astro-data").catch(() => null),
    ])
      .then(async ([core, cum, profile, astroData]) => {
        const safeProfiles = Array.isArray(astroData?.profiles) ? astroData.profiles : [];
        const hasAstroBase = safeProfiles.length > 0 || Boolean(core?.astro?.profile_id);
        let nextCore = core;
        const uiLocale = getLocale();
        // UI is RU but stored portrait/settings are EN → sync locale and republish portrait once.
        if (
          nextCore &&
          !uiLocale.toLowerCase().startsWith("en") &&
          !profileContractMatchesLocale(nextCore.profile_contract_v1, uiLocale)
        ) {
          try {
            if (profile && String(profile.locale || "").toLowerCase().startsWith("en")) {
              await putJson<UserSettings>("/account/profile", { locale: uiLocale });
            }
            const refreshed = await postJson<CoreProfile>("/account/core-profile/refresh", {});
            if (refreshed) {
              nextCore = refreshed;
              publishCoreProfileUpdate(refreshed);
            }
          } catch {
            /* display filters still hide EN copy */
          }
        }
        setCoreProfile(nextCore);
        setCompactUserModel(cum);
        setAstroProfiles(safeProfiles);
        hydrateSetupForm(profile, nextCore);
        if ((nextCore?.is_ready || hasAstroBase) && !forceSetup) {
          await loadNatalPreview();
        }
      })
      .finally(() => setLoading(false));
  }, [isAuthenticated, forceSetup, hydrateSetupForm, loadNatalPreview]);

  useEffect(() => {
    if (!isAuthenticated || typeof window === "undefined") return;
    const onCoreUpdate = (ev: Event) => {
      const ce = ev as CustomEvent<CoreProfileUpdatedDetail>;
      if (ce.detail?.astroProfileId != null) return;
      if (ce.detail?.profile) setCoreProfile(ce.detail.profile);
    };
    window.addEventListener(CORE_PROFILE_UPDATED_EVENT, onCoreUpdate);
    return () => window.removeEventListener(CORE_PROFILE_UPDATED_EVENT, onCoreUpdate);
  }, [isAuthenticated]);

  const profileCircleItems = useMemo(() => {
    const base = getCoreProfileCircle(coreProfile);
    return enrichCircleItemsWithAstroProfiles(base, astroProfiles);
  }, [coreProfile, astroProfiles]);

  const hasAstroProfileBase = astroProfiles.length > 0 || Boolean(coreProfile?.astro?.profile_id);
  const profileIncomplete = !coreProfile?.is_ready && !hasAstroProfileBase;
  const showSetupFlow = forceSetup || buildStage !== "idle";

  useEffect(() => {
    if (!isAuthenticated || loading || !queryChecked || !journeyChecked || !claimChecked || forceSetup || showSetupFlow || profileIncomplete) return;
    if (!WEB_LAUNCH_MIN_PROFILE) {
      if (!hasOnboardingIntentRecorded()) {
        router.replace("/onboarding/intent");
        return;
      }
      if (!hasOnboardingRealityRecorded()) {
        router.replace("/onboarding/reality");
      }
    }
  }, [
    isAuthenticated,
    loading,
    queryChecked,
    journeyChecked,
    claimChecked,
    forceSetup,
    showSetupFlow,
    profileIncomplete,
    router,
  ]);

  useEffect(() => {
    if (WEB_LAUNCH_MIN_PROFILE) return;
    if (!isAuthenticated || loading || !queryChecked || forceSetup || buildStage !== "idle") return;
    if (profileIncomplete) {
      router.replace(ONBOARDING_CORE_PATH);
    }
  }, [isAuthenticated, loading, queryChecked, forceSetup, buildStage, profileIncomplete, router]);

  useEffect(() => {
    if (typeof window === "undefined" || !queryChecked || showSetupFlow) return;
    const targetId =
      activeSection === "chart"
        ? PROFILE_CHART_SECTION_ID
        : activeSection === "spheres"
          ? PROFILE_LIFE_SPHERES_SECTION_ID
          : null;
    if (!targetId) return;
    window.setTimeout(() => {
      document.getElementById(targetId)?.scrollIntoView({ behavior: "smooth", block: "start" });
    }, 180);
  }, [activeSection, queryChecked, showSetupFlow]);

  if (authLoading || loading || !queryChecked || !journeyChecked || !claimChecked || (!WEB_LAUNCH_MIN_PROFILE && profileIncomplete && !forceSetup && buildStage === "idle")) {
    return <ProfileLoadingScreen />;
  }

  if (!isAuthenticated) {
    return (
      <ProductPageScreen
        testId="profile-guest-gate"
        title="Профиль"
        subtitle="Профиль открывается после мягкой регистрации: имя, дата рождения, первый разбор — и email, чтобы сохранить."
      >
        <div style={{ display: "grid", gap: "0.85rem", justifyItems: "start" }}>
          <Link href={`${VALUE_FIRST_PATHS.welcome}?fresh=1`} className="orbit-button orbit-button-primary">
            Построить мой профиль
          </Link>
          <Link href="/auth?mode=login" className="orbit-body-sm" style={{ color: "#78716c", textDecoration: "underline" }}>
            Уже есть аккаунт? Войти
          </Link>
        </div>
      </ProductPageScreen>
    );
  }

  const lifePath = coreProfile?.numerology?.life_path;
  const displayName =
    coreProfile?.person?.display_name?.trim() ||
    [coreProfile?.person?.first_name, setupForm.first_name].find((n) => n?.trim()) ||
    "Ты";
  const primaryCircleProfileId = getPrimaryProfileIdFromCore(coreProfile);
  const romanticCompatibilityRoute = buildQuickCompatibilityRoute({
    profiles: profileCircleItems,
    primaryProfileId: primaryCircleProfileId,
    preferred: "romantic",
  });
  const hasRomanticCompatibilityPair = romanticCompatibilityRoute.href.startsWith("/compatibility");
  const lifePathLayer = getLifePathEntry(lifePath);
  const sunLayer = getSunInSignEntry(getPlanetSignId(natalPreview, "Sun", coreProfile?.astro?.sun_sign));
  const moonLayer = getMoonInSignEntry(getPlanetSignId(natalPreview, "Moon"));
  const risingSignId = getRisingSignId(natalPreview);
  const risingLayer = risingSignId ? getRisingSignEntry(risingSignId) : undefined;
  const risingSign = risingLayer?.ruTitle || null;
  const risingHint = buildRisingOverviewHint(risingLayer, Boolean(risingSignId));

  const moonNarrativeLine = moonLayer?.bullets?.[0]?.trim() || "";

  const lifeMapSections = buildLifeMapSections(natalPreview).map((item) =>
    item.house === 7
      ? {
          ...item,
          routeTitle: hasRomanticCompatibilityPair ? "К совместимости" : "К кругу людей",
          href: hasRomanticCompatibilityPair ? romanticCompatibilityRoute.href : "/account/profiles",
        }
      : item,
  );

  const profileV0Model = buildProfileV0ViewModel({
    core: coreProfile,
    displayName,
    moonRecoveryHint: moonNarrativeLine || null,
  });

  const mcSign = resolveMcSignLabel(natalPreview);
  const frameworkCards = buildProfileFrameworkCards({
    sunLayer,
    moonLayer,
    risingLayer,
    risingSign,
    risingHint,
    mcSign,
    sunSignDisplay: profileV0Model.header.sunSignDisplay,
    lifePath: profileV0Model.header.lifePath,
    lifePathBody: lifePathLayer?.essence ?? lifePathLayer?.driver ?? null,
    archetypeLabel: profileV0Model.header.archetypeLabel,
    archetypeBody: profileV0Model.who?.whyManifest ?? profileV0Model.header.intro,
  });

  const profileQuickMapModel = buildProfileQuickMapViewModel(
    profileV0Model,
    buildProfileChartFrameworkInput({
      sunSignDisplay: profileV0Model.header.sunSignDisplay,
      risingSign,
      mcSign,
      lifePath: profileV0Model.header.lifePath,
      archetypeLabel: profileV0Model.header.archetypeLabel,
      chartCards: frameworkCards,
    }),
    compactUserModel,
    coreProfile?.profile_contract_v1,
  );
  const profileLifeSpheres = buildProfileLifeSpheresFromProfileData(natalPreview, coreProfile);
  const profileV2Live = buildProfileV2LiveContext({
    coreProfile,
    cum: compactUserModel,
    thriveAreas: profileQuickMapModel.thriveAreas,
    localClosedDays: listClosedDayContinuityRecords(21).length,
  });

  const isProfileQuickMap = !showSetupFlow;
  const showProfileV0 = profileView === "v0" || !WEB_LAUNCH_MIN_PROFILE;
  const showProfileQuickMap = isProfileQuickMap && WEB_LAUNCH_MIN_PROFILE && profileView !== "v0";
  const deepChartExpanded = activeSection === "chart" || focusArea === "numerology";

  const showProfileTeaser =
    !WEB_LAUNCH_MIN_PROFILE && isProfileQuickMap && hasCompletedFirstToday() && !profileDepthUnlocked;
  const onboardingCtx = readOnboardingContext();

  return (
    <ProfileWebScreen
      variant={showProfileQuickMap ? "v2" : "default"}
      displayName={displayName}
      coreProfile={coreProfile}
      profileMeta={productWebProfileMeta(coreProfile)}
      identityPills={
        showProfileQuickMap
          ? buildProfileIdentityPills(profileQuickMapModel.frameworkAnchors, coreProfile)
          : undefined
      }
      railAnchors={
        showProfileQuickMap ? [] : buildProfileRailAnchors(profileQuickMapModel.frameworkAnchors)
      }
      rail={undefined}
      compatibilityHref={hasRomanticCompatibilityPair ? romanticCompatibilityRoute.href : "/compatibility"}
    >
      <div
        className={
          showProfileV0
            ? `orbit-hero-content-container ${v0RouteStyles.profileV0RouteContainer}`
            : showProfileQuickMap
              ? undefined
              : "orbit-hero-content-container todayflow-main-container"
        }
        style={showProfileQuickMap || showProfileV0 ? undefined : { display: "grid", gap: "1rem" }}
      >
          {showSetupFlow ? (
            <ProfileHeroSection buildSteps={buildSteps} />
          ) : null}

          {showSetupFlow ? (
            <ProfileSetupSection
              currentBuildState={currentBuildState}
              buildStage={buildStage}
              isBuilding={isBuilding}
              setupForm={setupForm}
              hasResolvedBirthplace={hasResolvedBirthplace}
              setupError={setupError}
              setupMessage={setupMessage}
              onFinishSetupFlow={() => {
                resetSetupFlow();
                setForceSetup(false);
                setSetupMessage(null);
              }}
              onReopenSetupForm={() => {
                resetSetupFlow();
                setForceSetup(true);
                setSetupMessage(null);
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
          ) : (
            <>
              {coreProfile?.missing_fields?.includes("gender") ? (
                <SurfaceInsight variant="warm" data-testid="profile-gender-notice">
                  <SurfaceInsightBody>
                    Чтобы тексты на «ты» в сервисе звучали естественно, уточни обращение в{" "}
                    <Link href="/account/settings" className={surfaceInsightStyles.linkAccent}>
                      настройках аккаунта
                    </Link>
                    .
                  </SurfaceInsightBody>
                </SurfaceInsight>
              ) : null}
              {showProfileTeaser ? (
                <ProfileFirstDayTeaser
                  model={profileV0Model}
                  intentTheme={onboardingCtx.intent_theme}
                  realityState={onboardingCtx.reality_state}
                  onOpenFullPortrait={() => {
                    markProfileDepthUnlocked();
                    setProfileDepthUnlocked(true);
                  }}
                />
              ) : showProfileQuickMap ? (
                <ProfileV2SystemScreen
                  model={profileQuickMapModel}
                  live={profileV2Live}
                  coreProfile={coreProfile}
                  identityPills={buildProfileIdentityPills(profileQuickMapModel.frameworkAnchors, coreProfile)}
                  onOpenBirthData={() => setForceSetup(true)}
                  lifeSpheres={profileLifeSpheres}
                  portraitForming={isProfilePortraitForming(coreProfile)}
                  portraitFormingMessage={profilePortraitFormingMessage(coreProfile)}
                  deepExpanded={deepChartExpanded}
                  deep={{
                    natalPreview,
                    coreNumerology: coreProfile?.numerology,
                    previewError,
                    onReloadPreview: loadNatalPreview,
                    lifeMapSections,
                  }}
                  notices={
                    <>
                      {profileIncomplete ? (
                        <SurfaceInsight
                          variant="warm"
                          className={routeStyles.noticeSpaced}
                          data-testid="profile-incomplete-notice"
                        >
                          <SurfaceInsightBody>
                            Карта ещё не сохранена в аккаунте. Уточни место и время рождения — тогда профиль соберётся
                            полностью.
                          </SurfaceInsightBody>
                          <SurfaceInsightActions>
                            <Link href="/onboarding/refine?after=save" className="orbit-button orbit-button-primary orbit-button-sm">
                              Дополнить карту
                            </Link>
                            <button
                              type="button"
                              className="orbit-button orbit-button-secondary orbit-button-sm"
                              onClick={() => setForceSetup(true)}
                            >
                              Ввести данные здесь
                            </button>
                          </SurfaceInsightActions>
                        </SurfaceInsight>
                      ) : null}
                    </>
                  }
                />
              ) : (
                <ProfileV0Screen model={profileV0Model} onOpenBirthData={() => setForceSetup(true)} />
              )}
            </>
          )}
      </div>
    </ProfileWebScreen>
  );
}

export default function ProfileHubPage() {
  return (
    <Suspense fallback={<ProfileLoadingScreen />}>
      <ProfileHubPageInner />
    </Suspense>
  );
}

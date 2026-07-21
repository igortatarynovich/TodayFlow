"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { practicesExperienceChromeBundle, type FlowPracticesChromeLocale } from "@/components/today/flowPracticesMainTabChrome";
import { practicesV2Copy } from "@/components/practices/v2/practicesV2SystemCopy";
import {
  PracticesV2SystemScreen,
  type PracticesV2ProgramCard,
  type PracticesV2QuickItem,
  type PracticesV2Tab,
} from "@/components/practices/v2/PracticesV2SystemScreen";
import { LoadingSpinner } from "@/components/orbit";
import { PracticesWebScreen } from "@/components/product-ui/PracticesWebScreen";
import { getJson } from "@/lib/api";
import { fetchCoreProfileCached } from "@/lib/coreProfileCache";
import { isGuestPracticeAllowed } from "@/lib/guestAccessStore";
import { getLocale } from "@/lib/i18n";
import { buildPracticesV2LiveContext } from "@/lib/practicesPage/buildPracticesV2LiveContext";
import {
  matchesPracticeSearch,
  PRACTICE_BACKEND_CATEGORY_IDS,
  programCardsFromCatalog,
  quickItemsFromCatalog,
  practiceStepsCount,
  progressSummaryFromApi,
  type PracticeCatalogItem,
  type PracticeCategoryOption,
  type PracticeLimitsSnapshot,
} from "@/lib/practicesPage/practicesCatalogModel";
import {
  productWebDisplayName,
  productWebProfileMeta,
  productWebUserInitial,
} from "@/lib/productWebUser";
import type { CoreProfile, PracticeHistoryResponse, PracticeProgressResponse } from "@/lib/types";
import { useAuth } from "@/lib/useAuth";
import styles from "@/app/practices/PracticesPage.module.css";

function formatDuration(minutes: number | undefined, minutesShort: string): string {
  if (minutes == null) return "—";
  return `${minutes} ${minutesShort}`;
}

function buildCategoryTabs(
  categories: PracticeCategoryOption[],
  allLabel: string,
): PracticesV2Tab[] {
  return [
    { id: "all", label: allLabel, tone: "dark" },
    ...categories.map((category, index) => ({
      id: category.id,
      label: category.name,
      tone: index === 0 ? ("gold" as const) : undefined,
    })),
  ];
}

export default function PracticesPage() {
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const locale: FlowPracticesChromeLocale = getLocale() === "ru" ? "ru" : "en";
  const pc = useMemo(() => practicesExperienceChromeBundle(locale), [locale]);
  const v2Copy = useMemo(() => practicesV2Copy(locale), [locale]);
  const sortLocale = locale === "ru" ? "ru" : "en";

  const [loading, setLoading] = useState(true);
  const [practices, setPractices] = useState<PracticeCatalogItem[]>([]);
  const [currentPractice, setCurrentPractice] = useState<PracticeCatalogItem | null>(null);
  const [coreProfile, setCoreProfile] = useState<CoreProfile | null>(null);
  const [progress, setProgress] = useState<PracticeProgressResponse | null>(null);
  const [history, setHistory] = useState<PracticeHistoryResponse | null>(null);
  const [limits, setLimits] = useState<PracticeLimitsSnapshot | null>(null);
  const [categories, setCategories] = useState<PracticeCategoryOption[]>([]);
  const [sequences, setSequences] = useState<PracticeCatalogItem[]>([]);
  const [shortAlternatives, setShortAlternatives] = useState<PracticeCatalogItem[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [catalogStatus, setCatalogStatus] = useState<"loaded" | "empty" | "failed">("loaded");
  const [catalogTab, setCatalogTab] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");

  const loadPractices = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const categoryParam =
        catalogTab !== "all" && PRACTICE_BACKEND_CATEGORY_IDS.has(catalogTab)
          ? `?category=${encodeURIComponent(catalogTab)}`
          : "";

      const catalogResult = await getJson<PracticeCatalogItem[]>(`/practices${categoryParam || "/"}`)
        .then((data) => ({ ok: true as const, data }))
        .catch((err) => {
          console.error("Practices catalog failed", err);
          return { ok: false as const, data: [] as PracticeCatalogItem[] };
        });

      const [currentResult, categoriesResult, shortAltResult] = await Promise.all([
        getJson<PracticeCatalogItem>("/practices/current")
          .then((data) => ({ ok: true as const, data }))
          .catch((err) => {
            console.error("Practices current failed", err);
            return { ok: false as const, data: null as PracticeCatalogItem | null };
          }),
        getJson<{ categories: PracticeCategoryOption[] }>("/practices/categories/list")
          .then((data) => ({ ok: true as const, data }))
          .catch((err) => {
            console.error("Practices categories failed", err);
            return { ok: false as const, data: { categories: [] as PracticeCategoryOption[] } };
          }),
        getJson<PracticeCatalogItem[]>("/practices/short-alternatives")
          .then((data) => ({ ok: true as const, data }))
          .catch((err) => {
            console.error("Practices short-alternatives failed", err);
            return { ok: false as const, data: [] as PracticeCatalogItem[] };
          }),
      ]);

      if (!catalogResult.ok) {
        setCatalogStatus("failed");
        setPractices([]);
        setCurrentPractice(null);
        setError(v2Copy.catalogLoadFailed);
      } else {
        const catalogPool = isAuthenticated
          ? catalogResult.data
          : catalogResult.data.filter((practice) => isGuestPracticeAllowed(practice));

        const sorted = [...catalogPool].sort((a, b) => {
          if (a.is_personalized !== b.is_personalized) return a.is_personalized ? -1 : 1;
          return a.title.localeCompare(b.title, sortLocale);
        });

        setPractices(sorted);
        setCatalogStatus(sorted.length === 0 ? "empty" : "loaded");
        // Never promote catalog[0] into "current" — that looks personal when it isn't.
        setCurrentPractice(currentResult.data);
        setError(null);
      }

      setCategories(categoriesResult.data.categories ?? []);
      setShortAlternatives(
        isAuthenticated
          ? shortAltResult.data
          : shortAltResult.data.filter((practice) => isGuestPracticeAllowed(practice)),
      );

      if (isAuthenticated) {
        const [progressResp, historyResp, limitsResp, sequencesResp] = await Promise.all([
          getJson<PracticeProgressResponse>("/practices/progress").catch((err) => {
            console.error("Practices progress failed", err);
            return null;
          }),
          getJson<PracticeHistoryResponse>("/practices/history?limit=100").catch((err) => {
            console.error("Practices history failed", err);
            return null;
          }),
          getJson<PracticeLimitsSnapshot>("/practices/limits").catch((err) => {
            console.error("Practices limits failed", err);
            return null;
          }),
          getJson<PracticeCatalogItem[]>("/practices/sequences").catch((err) => {
            console.error("Practices sequences failed", err);
            return [];
          }),
        ]);
        setProgress(progressResp);
        setHistory(historyResp);
        setLimits(limitsResp);
        setSequences(sequencesResp);
      } else {
        setProgress(null);
        setHistory(null);
        setLimits(null);
        setSequences([]);
      }
    } catch (err) {
      console.error("Error loading practices:", err);
      setCatalogStatus("failed");
      setError(pc.practicesCatalogLoadError);
    } finally {
      setLoading(false);
    }
  }, [catalogTab, isAuthenticated, sortLocale, pc.practicesCatalogLoadError, v2Copy.catalogLoadFailed]);

  useEffect(() => {
    void loadPractices();
  }, [loadPractices]);

  useEffect(() => {
    if (!isAuthenticated) {
      setCoreProfile(null);
      return;
    }
    void fetchCoreProfileCached()
      .then(setCoreProfile)
      .catch((err) => console.error("Failed to load core profile for practices", err));
  }, [isAuthenticated]);

  const filteredPractices = useMemo(() => {
    return practices.filter((practice) => matchesPracticeSearch(practice, searchQuery));
  }, [practices, searchQuery]);

  const tabs = useMemo(
    () => buildCategoryTabs(categories, v2Copy.tabAll),
    [categories, v2Copy.tabAll],
  );

  const programCards = useMemo((): PracticesV2ProgramCard[] => {
    const useSequences =
      isAuthenticated && sequences.length > 0 && catalogTab === "all" && !searchQuery.trim();
    const source = useSequences ? sequences : filteredPractices;
    return programCardsFromCatalog(source, {
      locale,
      minutesShort: v2Copy.minutesShort,
      max: 3,
      preferSequences: false,
    });
  }, [filteredPractices, sequences, isAuthenticated, catalogTab, searchQuery, v2Copy.minutesShort, locale]);

  const quickItems = useMemo((): PracticesV2QuickItem[] => {
    const excludeIds = new Set(programCards.map((card) => card.id));
    const altPool =
      shortAlternatives.length > 0
        ? shortAlternatives
        : filteredPractices.filter((practice) => !excludeIds.has(practice.id));
    return quickItemsFromCatalog(altPool, {
      locale,
      minutesShort: v2Copy.minutesShort,
      max: 3,
      excludeIds,
    });
  }, [programCards, shortAlternatives, filteredPractices, v2Copy.minutesShort, locale]);

  const practiceOfDay = useMemo(() => {
    if (currentPractice) {
      const recommendationSource: "personalized" | "current" = currentPractice.is_personalized
        ? "personalized"
        : "current";
      return {
        title: currentPractice.title,
        description:
          currentPractice.personalized_reason?.trim() || currentPractice.description,
        minutes: currentPractice.duration_minutes ?? null,
        steps: practiceStepsCount(currentPractice),
        href: `/practices/${currentPractice.id}`,
        recommendationSource,
      };
    }

    const fallback = filteredPractices[0] ?? practices[0];
    if (!fallback) return null;
    return {
      title: fallback.title,
      description: fallback.description,
      minutes: fallback.duration_minutes ?? null,
      steps: practiceStepsCount(fallback),
      href: `/practices/${fallback.id}`,
      recommendationSource: "catalog_fallback" as const,
    };
  }, [currentPractice, filteredPractices, practices]);

  const heroPrimaryHref = practiceOfDay?.href ?? "/practices";
  const heroSecondaryHref = "#practices-v2-library";
  const heroDurationSuffix = practiceOfDay?.minutes
    ? `${practiceOfDay.minutes} ${v2Copy.minutesShort.toUpperCase()}`
    : null;
  const heroBody =
    practiceOfDay?.recommendationSource === "catalog_fallback"
      ? "Рекомендуем начать с этой практики — она из каталога, не персональная подборка."
      : currentPractice?.personalized_reason?.trim() ||
        currentPractice?.description?.trim() ||
        v2Copy.heroBodyFallback;

  const activeProgramsCount = sequences.length > 0 ? sequences.length : null;

  const live = useMemo(
    () =>
      buildPracticesV2LiveContext({
        progress,
        history: history?.history ?? [],
      }),
    [progress, history],
  );

  const progressSummary = useMemo(
    () => progressSummaryFromApi(progress, categories, locale),
    [progress, categories, locale],
  );

  const displayName = productWebDisplayName(coreProfile, null);
  const userInitial = productWebUserInitial(coreProfile, null);
  const statusLabel = productWebProfileMeta(coreProfile);

  const monthLabel = new Intl.DateTimeFormat(locale === "ru" ? "ru-RU" : "en-US", {
    month: "long",
  }).format(new Date());

  if (authLoading || loading) {
    return (
      <PracticesWebScreen
        variant="v2"
        locale={locale}
        title={pc.practicesCatalogPageTitle}
        subtitle={pc.practicesCatalogPageSubtitle}
        coreProfile={coreProfile}
      >
        <div className={styles.loaderWrap}>
          <LoadingSpinner size="lg" />
        </div>
      </PracticesWebScreen>
    );
  }

  return (
    <PracticesWebScreen
      variant="v2"
      locale={locale}
      title={pc.practicesCatalogPageTitle}
      subtitle={pc.practicesCatalogPageSubtitle}
      coreProfile={coreProfile}
      displayName={displayName}
      activePractices={activeProgramsCount ?? 0}
      streakDays={live.streakDays}
      showProgressRail={(progress?.total_completed ?? 0) > 0 || live.streakDays > 0}
      weeklyRhythm={
        (progress?.total_completed ?? 0) > 0
          ? live.weekCells.map((cell) => (cell.closed ? 1 : 0))
          : []
      }
    >
      {error && catalogStatus !== "failed" ? (
        <div className={styles.errorBanner} role="alert">
          {error}
        </div>
      ) : null}
      <PracticesV2SystemScreen
        locale={locale}
        displayName={displayName}
        userInitial={userInitial}
        statusLabel={statusLabel}
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        tabs={tabs.length > 1 ? tabs : [{ id: "all", label: v2Copy.tabAll, tone: "dark" }]}
        activeTabId={catalogTab}
        onTabChange={setCatalogTab}
        heroBody={heroBody}
        heroEyebrowSuffix={heroDurationSuffix}
        heroPrimaryHref={heroPrimaryHref}
        heroSecondaryHref={heroSecondaryHref}
        practiceOfDay={practiceOfDay}
        programCards={programCards}
        quickItems={quickItems}
        live={live}
        monthLabel={monthLabel}
        progressSummary={progressSummary}
        limitsRemaining={limits?.remaining_this_week ?? null}
        showGuestProgressHint={!isAuthenticated}
        emptyLibraryMessage={pc.practicesCatalogEmptyFilter}
        catalogFailed={catalogStatus === "failed"}
        onRetryCatalog={() => void loadPractices()}
      />
    </PracticesWebScreen>
  );
}

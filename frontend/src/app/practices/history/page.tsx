"use client";

import { useEffect, useMemo, useState } from "react";
import { PracticesV2HistoryScreen } from "@/components/practices/v2/PracticesV2HistoryScreen";
import { practicesV2HistoryCopy } from "@/components/practices/v2/practicesV2HistoryCopy";
import { LoadingSpinner } from "@/components/orbit";
import { PracticesWebScreen } from "@/components/product-ui/PracticesWebScreen";
import {
  practicesExperienceChromeBundle,
  type FlowPracticesChromeLocale,
} from "@/components/today/flowPracticesMainTabChrome";
import { getJson } from "@/lib/api";
import { getLocale } from "@/lib/i18n";
import {
  categoryLabelFromOptions,
  progressSummaryFromApi,
  type PracticeCategoryOption,
} from "@/lib/practicesPage/practicesCatalogModel";
import type { PracticeHistoryResponse, PracticeProgressResponse } from "@/lib/types";
import { useAuth } from "@/lib/useAuth";
import styles from "@/app/practices/PracticesPage.module.css";

export default function PracticesHistoryPage() {
  const locale: FlowPracticesChromeLocale = getLocale() === "ru" ? "ru" : "en";
  const pc = useMemo(() => practicesExperienceChromeBundle(locale), [locale]);
  const historyCopy = useMemo(() => practicesV2HistoryCopy(locale), [locale]);
  const dateLocaleTag = locale === "ru" ? "ru-RU" : "en-US";
  const { isAuthenticated, isLoading: authLoading } = useAuth();

  const [loading, setLoading] = useState(true);
  const [history, setHistory] = useState<PracticeHistoryResponse | null>(null);
  const [progress, setProgress] = useState<PracticeProgressResponse | null>(null);
  const [categories, setCategories] = useState<PracticeCategoryOption[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (authLoading) return;

    if (!isAuthenticated) {
      setError(historyCopy.authRequired);
      setLoading(false);
      return;
    }

    const loadData = async () => {
      try {
        const [hist, prog, categoriesResp] = await Promise.all([
          getJson<PracticeHistoryResponse>("/practices/history?limit=100"),
          getJson<PracticeProgressResponse>("/practices/progress").catch(() => null),
          getJson<{ categories: PracticeCategoryOption[] }>("/practices/categories/list").catch(() => ({
            categories: [],
          })),
        ]);
        setHistory(hist);
        setProgress(prog);
        setCategories(categoriesResp.categories ?? []);
      } catch (err) {
        console.error("Failed to load practice history", err);
        setError(err instanceof Error ? err.message : pc.practicesHistoryLoadFailed);
      } finally {
        setLoading(false);
      }
    };

    void loadData();
  }, [
    authLoading,
    isAuthenticated,
    historyCopy.authRequired,
    pc.practicesHistoryLoadFailed,
  ]);

  const progressSummary = useMemo(
    () => progressSummaryFromApi(progress, categories, locale),
    [progress, categories, locale],
  );

  const categoryLabel = useMemo(
    () => (categoryId: string | null | undefined) =>
      categoryId ? categoryLabelFromOptions(categoryId, categories, locale) : "—",
    [categories, locale],
  );

  if (authLoading || loading) {
    return (
      <PracticesWebScreen variant="v2" locale={locale} title={historyCopy.pageTitle} subtitle={historyCopy.pageSubtitle}>
        <div className={styles.loaderWrap}>
          <LoadingSpinner size="lg" />
        </div>
      </PracticesWebScreen>
    );
  }

  if (error) {
    return (
      <PracticesWebScreen variant="v2" locale={locale} title={historyCopy.pageTitle} subtitle={historyCopy.pageSubtitle}>
        <div className={styles.errorBanner} role="alert">
          {error}
        </div>
      </PracticesWebScreen>
    );
  }

  return (
    <PracticesWebScreen variant="v2" locale={locale} title={historyCopy.pageTitle} subtitle={historyCopy.pageSubtitle}>
      <PracticesV2HistoryScreen
        locale={locale}
        progressSummary={progressSummary}
        currentStreakDays={progress?.current_streak_days ?? 0}
        history={history?.history ?? []}
        historyTotal={history?.total ?? 0}
        categoryLabel={categoryLabel}
        dateLocaleTag={dateLocaleTag}
      />
    </PracticesWebScreen>
  );
}

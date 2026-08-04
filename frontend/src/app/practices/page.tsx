"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { practicesExperienceChromeBundle, type FlowPracticesChromeLocale } from "@/components/today/flowPracticesMainTabChrome";
import { practicesStateCycleCopy } from "@/components/practices/stateCycle/practicesStateCycleCopy";
import {
  PracticesStateCycleScreen,
  type StateCycleContinue,
  type StateCycleMyItem,
  type StateCyclePracticeCard,
  type StateCycleTodayRail,
} from "@/components/practices/stateCycle/PracticesStateCycleScreen";
import { LoadingSpinner } from "@/components/orbit";
import { PracticesWebScreen } from "@/components/product-ui/PracticesWebScreen";
import { getJson, isRequestAborted } from "@/lib/api";
import { fetchCoreProfileCached } from "@/lib/coreProfileCache";
import { isGuestPracticeAllowed } from "@/lib/guestAccessStore";
import { getLocale } from "@/lib/i18n";
import { buildPracticesV2LiveContext } from "@/lib/practicesPage/buildPracticesV2LiveContext";
import {
  inferPracticeFormat,
  practiceCardTitle,
  practiceMatchesFormat,
  practiceMatchesNeed,
  rankPracticesForNeed,
  type PracticeFormatId,
  type PracticeNeedId,
} from "@/lib/practicesPage/practicesCanon";
import { readPracticeSessionDraft } from "@/lib/practicesPage/practiceSessionDraft";
import {
  type PracticeCatalogItem,
  type PracticeLimitsSnapshot,
} from "@/lib/practicesPage/practicesCatalogModel";
import { productWebDisplayName } from "@/lib/productWebUser";
import type { CoreProfile, PracticeHistoryResponse, PracticeProgressResponse } from "@/lib/types";
import { fetchTodayContractV1 } from "@/lib/todayContract";
import { useAuth } from "@/lib/useAuth";
import styles from "@/app/practices/PracticesPage.module.css";

const RECOMMEND_IMAGE = "/images/praktiki_banner.png";

function toCard(practice: PracticeCatalogItem, imageUrl?: string | null): StateCyclePracticeCard {
  const cardTitle = practiceCardTitle(practice);
  const technical = practice.title?.trim() || "";
  const reason = practice.personalized_reason?.trim() || "";
  const desc = practice.description?.trim() || "";
  let description = reason || desc;
  if (!reason && technical && cardTitle !== technical) {
    description = description ? `${technical}. ${description}` : technical;
  }
  return {
    id: practice.id,
    href: `/practices/${practice.id}?run=1`,
    title: cardTitle,
    description,
    minutes: practice.duration_minutes ?? null,
    formatId: inferPracticeFormat(practice),
    imageUrl: imageUrl ?? null,
  };
}

function pickPoolForNeed(
  pool: PracticeCatalogItem[],
  need: PracticeNeedId,
  format: PracticeFormatId | null,
): PracticeCatalogItem[] {
  let list = pool;
  if (format) {
    const byFormat = list.filter((p) => practiceMatchesFormat(p, format));
    if (byFormat.length > 0) list = byFormat;
  }
  const byNeed = list.filter((p) => practiceMatchesNeed(p, need));
  if (byNeed.length > 0) list = byNeed;
  return rankPracticesForNeed(list, need);
}

export default function PracticesPage() {
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const locale: FlowPracticesChromeLocale = getLocale() === "ru" ? "ru" : "en";
  const pc = useMemo(() => practicesExperienceChromeBundle(locale), [locale]);
  const copy = useMemo(() => practicesStateCycleCopy(locale), [locale]);
  const sortLocale = locale === "ru" ? "ru" : "en";

  const [loading, setLoading] = useState(true);
  const [practices, setPractices] = useState<PracticeCatalogItem[]>([]);
  const [currentPractice, setCurrentPractice] = useState<PracticeCatalogItem | null>(null);
  const [coreProfile, setCoreProfile] = useState<CoreProfile | null>(null);
  const [progress, setProgress] = useState<PracticeProgressResponse | null>(null);
  const [history, setHistory] = useState<PracticeHistoryResponse | null>(null);
  const [limits, setLimits] = useState<PracticeLimitsSnapshot | null>(null);
  const [shortAlternatives, setShortAlternatives] = useState<PracticeCatalogItem[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [catalogStatus, setCatalogStatus] = useState<"loaded" | "empty" | "failed">("loaded");
  const [activeNeed, setActiveNeed] = useState<PracticeNeedId>("calm");
  const [activeFormat, setActiveFormat] = useState<PracticeFormatId | null>(null);
  const [todayRail, setTodayRail] = useState<StateCycleTodayRail | null>(null);
  const [continueSession, setContinueSession] = useState<StateCycleContinue | null>(null);

  useEffect(() => {
    const syncDraft = () => {
      const draft = readPracticeSessionDraft();
      if (!draft || draft.elapsedSeconds <= 0) {
        setContinueSession(null);
        return;
      }
      const total = Math.max(1, Math.round(draft.durationMinutes));
      const done = Math.min(total, Math.floor(draft.elapsedSeconds / 60));
      setContinueSession({
        href: `/practices/${draft.practiceId}?run=1`,
        title: draft.title,
        minutesDone: done,
        minutesTotal: total,
      });
    };
    syncDraft();
    window.addEventListener("focus", syncDraft);
    return () => window.removeEventListener("focus", syncDraft);
  }, [loading]);

  const loadPractices = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const catalogResult = await getJson<PracticeCatalogItem[]>(`/practices/`)
        .then((data) => ({ ok: true as const, data }))
        .catch((err) => {
          console.error("Practices catalog failed", err);
          return { ok: false as const, data: [] as PracticeCatalogItem[] };
        });

      const [currentResult, shortAltResult] = await Promise.all([
        getJson<PracticeCatalogItem>("/practices/current")
          .then((data) => ({ ok: true as const, data }))
          .catch((err) => {
            console.error("Practices current failed", err);
            return { ok: false as const, data: null as PracticeCatalogItem | null };
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
        setError(copy.catalogFailed);
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
        setCurrentPractice(currentResult.data);
        setError(null);
      }

      setShortAlternatives(
        isAuthenticated
          ? shortAltResult.data
          : shortAltResult.data.filter((practice) => isGuestPracticeAllowed(practice)),
      );

      if (isAuthenticated) {
        const [progressResp, historyResp, limitsResp] = await Promise.all([
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
        ]);
        setProgress(progressResp);
        setHistory(historyResp);
        setLimits(limitsResp);
      } else {
        setProgress(null);
        setHistory(null);
        setLimits(null);
      }
    } catch (err) {
      console.error("Error loading practices:", err);
      setCatalogStatus("failed");
      setError(pc.practicesCatalogLoadError);
    } finally {
      setLoading(false);
    }
  }, [isAuthenticated, sortLocale, pc.practicesCatalogLoadError, copy.catalogFailed]);

  useEffect(() => {
    if (authLoading) return;
    void loadPractices();
  }, [authLoading, loadPractices]);

  useEffect(() => {
    if (!isAuthenticated) {
      setCoreProfile(null);
      return;
    }
    void fetchCoreProfileCached()
      .then(setCoreProfile)
      .catch((err) => console.error("Failed to load core profile for practices", err));
  }, [isAuthenticated]);

  useEffect(() => {
    if (!isAuthenticated) {
      setTodayRail(null);
      return;
    }
    let cancelled = false;
    void fetchTodayContractV1()
      .then((contract) => {
        if (cancelled) return;
        const story = contract.day_story;
        const mood = story?.theme || story?.headline_anchor || null;
        const goal = story?.today_move || story?.direction || null;
        const practiceDone = story?.practice_recommendation?.text || null;
        setTodayRail({
          mood: typeof mood === "string" && mood.trim() ? mood.trim() : null,
          goal: typeof goal === "string" && goal.trim() ? goal.trim() : null,
          practiceDone:
            typeof practiceDone === "string" && practiceDone.trim() ? practiceDone.trim() : null,
        });
      })
      .catch((err) => {
        if (!isRequestAborted(err)) {
          console.error("Failed to load today contract for practices rail", err);
        }
        if (!cancelled) setTodayRail(null);
      });
    return () => {
      cancelled = true;
    };
  }, [isAuthenticated]);

  const filteredPool = useMemo(
    () => pickPoolForNeed(practices, activeNeed, activeFormat),
    [practices, activeNeed, activeFormat],
  );

  const recommended = useMemo((): StateCyclePracticeCard | null => {
    if (currentPractice && practiceMatchesNeed(currentPractice, activeNeed)) {
      return toCard(currentPractice, RECOMMEND_IMAGE);
    }
    if (currentPractice && !activeFormat) {
      // Prefer current when format filter off — still honest "recommended now"
      return toCard(currentPractice, RECOMMEND_IMAGE);
    }
    const first = filteredPool[0] ?? practices[0];
    return first ? toCard(first, RECOMMEND_IMAGE) : null;
  }, [currentPractice, filteredPool, practices, activeNeed, activeFormat]);

  const momentCards = useMemo((): StateCyclePracticeCard[] => {
    const exclude = new Set(recommended ? [recommended.id] : []);
    const altPool =
      shortAlternatives.length > 0
        ? pickPoolForNeed(shortAlternatives, activeNeed, activeFormat)
        : filteredPool;
    return altPool
      .filter((p) => !exclude.has(p.id))
      .slice(0, 8)
      .map((p) => toCard(p));
  }, [shortAlternatives, filteredPool, recommended, activeNeed, activeFormat]);

  const practiceOfDay = useMemo((): {
    card: StateCyclePracticeCard | null;
    source: "personalized" | "current" | "catalog_fallback" | null;
  } => {
    if (currentPractice) {
      return {
        card: toCard(currentPractice),
        source: currentPractice.is_personalized ? "personalized" : "current",
      };
    }
    const fallback = practices[0];
    if (!fallback) return { card: null, source: null };
    return { card: toCard(fallback), source: "catalog_fallback" };
  }, [currentPractice, practices]);

  const myItems = useMemo((): StateCycleMyItem[] => {
    const rows = history?.history ?? [];
    if (rows.length === 0) return [];
    const seen = new Set<string>();
    const out: StateCycleMyItem[] = [];
    for (const row of rows) {
      if (!row.practice_id || seen.has(row.practice_id)) continue;
      seen.add(row.practice_id);
      out.push({
        id: row.practice_id,
        href: `/practices/${row.practice_id}`,
        title: row.practice_title || row.practice_id,
      });
      if (out.length >= 5) break;
    }
    return out;
  }, [history]);

  const live = useMemo(
    () =>
      buildPracticesV2LiveContext({
        progress,
        history: history?.history ?? [],
      }),
    [progress, history],
  );

  const displayName = productWebDisplayName(coreProfile, null);

  if (authLoading || loading) {
    return (
      <PracticesWebScreen
        variant="v2"
        locale={locale}
        title={copy.pageTitle}
        subtitle={copy.pageSubtitle}
        coreProfile={coreProfile}
        rail={null}
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
      title={copy.pageTitle}
      subtitle={copy.pageSubtitle}
      coreProfile={coreProfile}
      displayName={displayName}
      activePractices={limits?.used_this_week ?? 0}
      streakDays={live.streakDays}
      showProgressRail={false}
      rail={null}
    >
      {error && catalogStatus !== "failed" ? (
        <div className={styles.errorBanner} role="alert">
          {error}
        </div>
      ) : null}
      <PracticesStateCycleScreen
        locale={locale}
        activeNeed={activeNeed}
        onNeedChange={setActiveNeed}
        activeFormat={activeFormat}
        onFormatChange={setActiveFormat}
        recommended={recommended}
        continueSession={continueSession}
        momentCards={momentCards}
        practiceOfDay={practiceOfDay.card}
        practiceOfDaySource={practiceOfDay.source}
        myItems={myItems}
        todayRail={todayRail}
        catalogFailed={catalogStatus === "failed"}
        onRetryCatalog={() => void loadPractices()}
      />
    </PracticesWebScreen>
  );
}

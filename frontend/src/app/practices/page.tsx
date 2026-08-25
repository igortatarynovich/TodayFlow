"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { type FlowPracticesChromeLocale } from "@/components/today/flowPracticesMainTabChrome";
import { practicesStateCycleCopy } from "@/components/practices/stateCycle/practicesStateCycleCopy";
import {
  PracticesStateCycleScreen,
  type StateCycleContinue,
  type StateCycleMyItem,
  type StateCyclePracticeCard,
  type StateCycleTodayRail,
} from "@/components/practices/stateCycle/PracticesStateCycleScreen";
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
/** Hub only needs a few unique recent practices for «Мои». */
const HISTORY_LIMIT = 20;

/** In-memory catalog so a return visit paints without waiting on the network. */
let catalogMemory: PracticeCatalogItem[] | null = null;

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

function sortCatalog(pool: PracticeCatalogItem[], sortLocale: string): PracticeCatalogItem[] {
  return [...pool].sort((a, b) => {
    if (a.is_personalized !== b.is_personalized) return a.is_personalized ? -1 : 1;
    return a.title.localeCompare(b.title, sortLocale);
  });
}

export default function PracticesPage() {
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const locale: FlowPracticesChromeLocale = getLocale() === "ru" ? "ru" : "en";
  const copy = useMemo(() => practicesStateCycleCopy(locale), [locale]);
  const sortLocale = locale === "ru" ? "ru" : "en";

  const [catalogRaw, setCatalogRaw] = useState<PracticeCatalogItem[]>(() => catalogMemory ?? []);
  const [currentPractice, setCurrentPractice] = useState<PracticeCatalogItem | null>(null);
  const [coreProfile, setCoreProfile] = useState<CoreProfile | null>(null);
  const [progress, setProgress] = useState<PracticeProgressResponse | null>(null);
  const [history, setHistory] = useState<PracticeHistoryResponse | null>(null);
  const [limits, setLimits] = useState<PracticeLimitsSnapshot | null>(null);
  const [shortAlternativesRaw, setShortAlternativesRaw] = useState<PracticeCatalogItem[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [catalogStatus, setCatalogStatus] = useState<"pending" | "loaded" | "empty" | "failed">(
    () => (catalogMemory ? (catalogMemory.length === 0 ? "empty" : "loaded") : "pending"),
  );
  const [activeNeed, setActiveNeed] = useState<PracticeNeedId>("calm");
  const [activeFormat, setActiveFormat] = useState<PracticeFormatId | null>(null);
  const [todayRail, setTodayRail] = useState<StateCycleTodayRail | null>(null);
  const [continueSession, setContinueSession] = useState<StateCycleContinue | null>(null);

  const practices = useMemo(() => {
    const pool = isAuthenticated
      ? catalogRaw
      : catalogRaw.filter((practice) => isGuestPracticeAllowed(practice));
    return sortCatalog(pool, sortLocale);
  }, [catalogRaw, isAuthenticated, sortLocale]);

  const shortAlternatives = useMemo(
    () =>
      isAuthenticated
        ? shortAlternativesRaw
        : shortAlternativesRaw.filter((practice) => isGuestPracticeAllowed(practice)),
    [shortAlternativesRaw, isAuthenticated],
  );

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
  }, []);

  const loadCatalogExtras = useCallback(async () => {
    const [currentResult, shortAltResult] = await Promise.all([
      getJson<PracticeCatalogItem>("/practices/current")
        .then((data) => data)
        .catch((err) => {
          console.error("Practices current failed", err);
          return null as PracticeCatalogItem | null;
        }),
      getJson<PracticeCatalogItem[]>("/practices/short-alternatives")
        .then((data) => data)
        .catch((err) => {
          console.error("Practices short-alternatives failed", err);
          return [] as PracticeCatalogItem[];
        }),
    ]);
    setCurrentPractice(currentResult);
    setShortAlternativesRaw(shortAltResult);
  }, []);

  /** In-memory catalog only — do not wait on /current (lite report) or the spinner stays up. */
  const loadCatalogShell = useCallback(async () => {
    setError(null);
    try {
      const data = await getJson<PracticeCatalogItem[]>(`/practices/`);
      catalogMemory = data;
      setCatalogRaw(data);
      setCatalogStatus(data.length === 0 ? "empty" : "loaded");
      setError(null);
    } catch (err) {
      console.error("Practices catalog failed", err);
      if (!catalogMemory) {
        setCatalogStatus("failed");
        setCatalogRaw([]);
        setCurrentPractice(null);
        setError(copy.catalogFailed);
      }
    }
    void loadCatalogExtras();
  }, [copy.catalogFailed, loadCatalogExtras]);

  const loadAuthExtras = useCallback(async () => {
    const [progressResp, historyResp, limitsResp] = await Promise.all([
      getJson<PracticeProgressResponse>("/practices/progress").catch((err) => {
        console.error("Practices progress failed", err);
        return null;
      }),
      getJson<PracticeHistoryResponse>(`/practices/history?limit=${HISTORY_LIMIT}`).catch((err) => {
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
  }, []);

  useEffect(() => {
    void loadCatalogShell();
  }, [loadCatalogShell]);

  // Auth extras after session settles — never hold the full-page spinner.
  useEffect(() => {
    if (authLoading) return;
    if (!isAuthenticated) {
      setProgress(null);
      setHistory(null);
      setLimits(null);
      return;
    }
    let cancelled = false;
    void loadAuthExtras().then(() => {
      if (cancelled) return;
    });
    return () => {
      cancelled = true;
    };
  }, [authLoading, isAuthenticated, loadAuthExtras]);

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

  const retryAll = useCallback(() => {
    void loadCatalogShell().then(() => {
      if (isAuthenticated) void loadAuthExtras();
    });
  }, [loadCatalogShell, loadAuthExtras, isAuthenticated]);

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
        onRetryCatalog={retryAll}
      />
    </PracticesWebScreen>
  );
}

"use client";

import { Suspense, useState, useEffect, useCallback, useRef, useMemo } from "react";
import { useSearchParams, useRouter, usePathname } from "next/navigation";
import { useAuth } from "@/lib/useAuth";
import { ApiError, getJson, postJson, putJson } from "@/lib/api";
import { useToast } from "@/components/ToastProvider";
import { lineDone } from "./trackingRhythm";
import { toIsoLocalDate } from "./calendarHeatmapModel";
import { TrackerView } from "./TrackerView";
import { getLocale } from "@/lib/i18n";
import { flowTrackerChromeBundle } from "@/components/today/flowPracticesMainTabChrome";
import { ProductAuxWebScreen } from "@/components/product-ui/ProductAuxWebScreen";
import pl from "@/design-system/layouts/productPageLayout.module.css";
import type { TrackerTier } from "./trackerSpec";
import type { TrackerEntityKind } from "./trackerEntityCatalog";

type CalendarDay = {
  date: string;
  activities: {
    practice?: { completed: boolean; count?: number; state_scale?: number; note?: string };
    affirmation?: { completed: boolean; state_scale?: number; note?: string };
    asceticism?: { completed: boolean; state_scale?: number; note?: string };
    diary?: { completed: boolean; note?: string };
    ritual?: { completed: boolean };
    daily_signals?: {
      completed: boolean;
      signals_count?: number;
      ritual_feedback?: string | null;
      quick_decision_answer?: string | null;
      question_of_day_answer?: string | null;
    };
    goal?: { completed: boolean; count?: number; titles?: string[] };
    habits?: { completed: boolean; count?: number; names?: string[] };
    state_phases?: {
      completed: boolean;
      filled: number;
      of: number;
      morning: boolean;
      day: boolean;
      evening: boolean;
      full_day: boolean;
    };
  };
  mood?: number;
  streak: Record<string, number>;
};

type CalendarGoalTrack = {
  id: number;
  title: string;
  scope: string;
  completed: boolean;
  week_start: string;
  step_dates: string[];
};

type CalendarHabitTrack = {
  id: number;
  name: string;
  target_frequency: string;
  target_per_period: number;
  is_active: boolean;
  completed_dates: string[];
};

type CalendarAsceticTrack = {
  asceticism_id: string;
  title?: string | null;
  contract_status?: string | null;
  entries: { date: string; completed: boolean }[];
};

type CalendarData = {
  days: CalendarDay[];
  streaks: Record<string, number>;
  stats: Record<string, { total: number; completed: number; percentage: number }>;
  month_summary?: {
    from: string;
    to: string;
    total_days: number;
    days_full_state_checkins: number;
    days_with_goal_step: number;
    days_with_habits: number;
  } | null;
  goal_tracks?: CalendarGoalTrack[];
  habit_tracks?: CalendarHabitTrack[];
  ascetic_tracks?: CalendarAsceticTrack[];
};

function CalendarTrackerPageContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const pathname = usePathname();
  const { isAuthenticated, isLoading: authLoading, profile } = useAuth();
  const toast = useToast();
  const flowLocale = getLocale() === "ru" ? "ru" : "en";
  const flowChrome = flowTrackerChromeBundle(flowLocale);
  const [loading, setLoading] = useState(true);
  const [calendarRefreshing, setCalendarRefreshing] = useState(false);
  const [calendarData, setCalendarData] = useState<CalendarData | null>(null);
  const [logging, setLogging] = useState<Record<string, boolean>>({});

  const [heatmapMonth, setHeatmapMonth] = useState(() => {
    const d = new Date();
    return { y: d.getFullYear(), m: d.getMonth() };
  });

  const calendarEverLoaded = useRef(false);

  const todayIso = toIsoLocalDate(new Date());

  const heatmapTier: TrackerTier = profile?.insight_depth_tier ?? "free";

  const createRaw = searchParams.get("create");
  const urlOpenCreate: TrackerEntityKind | null =
    createRaw === "goal" || createRaw === "habit" || createRaw === "ascetic" ? createRaw : null;
  const clearUrlCreate = useCallback(() => {
    router.replace(pathname || "/tracking/calendar", { scroll: false });
  }, [router, pathname]);

  const loadCalendar = useCallback(
    async (opts?: { silentOverlay?: boolean }) => {
      try {
        if (!calendarEverLoaded.current) setLoading(true);
        else if (opts?.silentOverlay) setCalendarRefreshing(true);
        const end = new Date();
        const rollStart = new Date();
        rollStart.setDate(end.getDate() - 29);
        const viewFirst = new Date(heatmapMonth.y, heatmapMonth.m, 1);
        const fromD = new Date(Math.min(rollStart.getTime(), viewFirst.getTime()));
        const fromIso = toIsoLocalDate(fromD);
        const toIso = toIsoLocalDate(end);

        const data = await getJson<CalendarData>(`/tracking/calendar?from_date=${fromIso}&to_date=${toIso}`);
        setCalendarData(data);
        calendarEverLoaded.current = true;
      } catch (err) {
        console.error("Error loading calendar:", err);
      } finally {
        setLoading(false);
        setCalendarRefreshing(false);
      }
    },
    [heatmapMonth],
  );

  useEffect(() => {
    if (!isAuthenticated) return;
    void loadCalendar({ silentOverlay: calendarEverLoaded.current });
  }, [isAuthenticated, loadCalendar]);

  const handleGoalStep = async (goalId: number, date: string) => {
    const key = `goal-${goalId}-${date}`;
    if (logging[key]) return;
    const already = calendarData?.goal_tracks?.find((g) => g.id === goalId)?.step_dates.includes(date);
    if (already) {
      toast.error(flowChrome.trackingToastGoalStepDuplicate);
      return;
    }
    try {
      setLogging((prev) => ({ ...prev, [key]: true }));
      await postJson(`/tracking/weekly-goals/${goalId}/step`, { date });
      await loadCalendar();
    } catch (err) {
      console.error("Error saving goal step:", err);
      toast.error(flowChrome.trackingToastGoalStepError);
    } finally {
      setLogging((prev) => ({ ...prev, [key]: false }));
    }
  };

  const handleHabitToggle = async (habitId: number, date: string, completed: boolean) => {
    const key = `habit-${habitId}-${date}`;
    if (logging[key]) return;
    try {
      setLogging((prev) => ({ ...prev, [key]: true }));
      await postJson(`/habits/${habitId}/entries`, { date, completed });
      await loadCalendar();
    } catch (err) {
      console.error("Error saving habit:", err);
      toast.error(flowChrome.trackingToastHabitSaveError);
    } finally {
      setLogging((prev) => ({ ...prev, [key]: false }));
    }
  };

  const handleGoalRename = async (goalId: number, title: string) => {
    const t = title.trim();
    if (!t) {
      toast.error(flowChrome.trackingToastGoalNameEmpty);
      return;
    }
    try {
      await putJson(`/tracking/weekly-goals/${goalId}`, { title: t });
      await loadCalendar();
      toast.success(flowChrome.trackingToastGoalRenameSuccess);
    } catch (err) {
      console.error("Error renaming goal:", err);
      toast.error(err instanceof ApiError ? err.message : flowChrome.trackingToastGoalRenameError);
    }
  };

  const handleGoalComplete = async (goalId: number) => {
    try {
      await putJson(`/tracking/weekly-goals/${goalId}`, { completed: true });
      await loadCalendar();
      toast.success(flowChrome.trackingToastGoalCompleteSuccess);
    } catch (err) {
      console.error("Error completing goal:", err);
      toast.error(err instanceof ApiError ? err.message : flowChrome.trackingToastGoalCompleteError);
    }
  };

  const handleHabitUpdate = async (habitId: number, patch: { name?: string; is_active?: boolean }) => {
    try {
      await putJson(`/habits/${habitId}`, patch);
      await loadCalendar();
      if (patch.name !== undefined) toast.success(flowChrome.trackingToastHabitRenameSuccess);
      else if (patch.is_active === false) toast.success(flowChrome.trackingToastHabitPaused);
      else if (patch.is_active === true) toast.success(flowChrome.trackingToastHabitActive);
    } catch (err) {
      console.error("Error updating habit:", err);
      toast.error(err instanceof ApiError ? err.message : flowChrome.trackingToastHabitUpdateError);
    }
  };

  const handleAsceticLog = async (asceticismId: string, date: string, completed: boolean) => {
    const key = `ascetic-${asceticismId}-${date}`;
    if (logging[key]) return;
    try {
      setLogging((prev) => ({ ...prev, [key]: true }));
      await postJson("/tracking/calendar/log", {
        date,
        activity_type: "asceticism",
        activity_id: asceticismId,
        completed,
      });
      await loadCalendar();
    } catch (err) {
      console.error("Error logging ascetic:", err);
      toast.error(flowChrome.trackingToastAsceticLogError);
    } finally {
      setLogging((prev) => ({ ...prev, [key]: false }));
    }
  };

  const handlePracticeToggle = async (date: string) => {
    const key = `practice-${date}`;
    if (logging[key]) return;
    const day = calendarData?.days.find((d) => d.date === date);
    const isCompleted = day ? lineDone(day, "practice") : false;
    if (isCompleted) {
      toast.error(flowChrome.trackingToastPracticeUncheckBlocked);
      return;
    }
    try {
      setLogging((prev) => ({ ...prev, [key]: true }));
      await postJson("/tracking/calendar/log", {
        date,
        activity_type: "practice",
        completed: true,
      });
      await loadCalendar();
    } catch (err) {
      console.error("Error logging practice:", err);
      toast.error(flowChrome.trackingToastPracticeSaveError);
    } finally {
      setLogging((prev) => ({ ...prev, [key]: false }));
    }
  };

  const goalCountWeek = useMemo(
    () => {
      const tracks = calendarData?.goal_tracks ?? [];
      return tracks.filter((g) => {
        if (g.completed) return false;
        const sc = (g.scope || "week").toLowerCase();
        return sc === "week";
      }).length;
    },
    [calendarData?.goal_tracks],
  );
  const goalCountMonth = useMemo(
    () => {
      const tracks = calendarData?.goal_tracks ?? [];
      return tracks.filter((g) => {
        if (g.completed) return false;
        const sc = (g.scope || "week").toLowerCase();
        return sc === "month";
      }).length;
    },
    [calendarData?.goal_tracks],
  );

  if (authLoading || (loading && !calendarData)) {
    return (
      <ProductAuxWebScreen
        title={flowChrome.trackingCalendarPageTitle}
        loading
        loadingLabel={flowChrome.trackingCalendarPageIntro}
      />
    );
  }

  if (!isAuthenticated) {
    return (
      <ProductAuxWebScreen
        title={flowChrome.trackingCalendarPageTitle}
        guest={{
          message: flowChrome.trackingCalendarLoginPrompt,
          ctaHref: "/auth?redirect=/tracking/calendar",
          ctaLabel: flowLocale === "ru" ? "Войти" : "Sign in",
        }}
      />
    );
  }

  const goalTracks = calendarData?.goal_tracks ?? [];
  const habitTracks = calendarData?.habit_tracks ?? [];
  const asceticTracks = calendarData?.ascetic_tracks ?? [];

  return (
    <ProductAuxWebScreen
      testId="tracking-calendar-page"
      eyebrow={flowChrome.trackingCalendarPageEyebrow}
      title={flowChrome.trackingCalendarPageTitle}
      subtitle={flowChrome.trackingCalendarPageIntro}
      railTitle={flowLocale === "ru" ? "Календарь практик" : "Practice calendar"}
      railHint={
        flowLocale === "ru"
          ? "Цели, привычки и аскезы на одной шкале — отметки прямо в календаре."
          : "Goals, habits, and ascetics on one timeline — mark progress in the calendar."
      }
      contentClassName={`${pl.content} ${pl.legacyHost}`}
    >
      {calendarData ? (
        <TrackerView
          allDays={calendarData.days}
          stats={calendarData.stats}
          goalTracks={goalTracks}
          habitTracks={habitTracks}
          asceticTracks={asceticTracks}
          todayIso={todayIso}
          logging={logging}
          onGoalStep={(id, d) => void handleGoalStep(id, d)}
          onHabitToggle={(id, d, c) => void handleHabitToggle(id, d, c)}
          onPracticeToggle={(d) => void handlePracticeToggle(d)}
          onAsceticLog={(aid, d, c) => void handleAsceticLog(aid, d, c)}
          onReloadCalendar={() => void loadCalendar()}
          onGoalRename={(id, t) => void handleGoalRename(id, t)}
          onGoalComplete={(id) => void handleGoalComplete(id)}
          onHabitUpdate={(id, p) => void handleHabitUpdate(id, p)}
          urlOpenCreate={urlOpenCreate}
          onConsumedUrlCreate={clearUrlCreate}
          goalCountWeek={goalCountWeek}
          goalCountMonth={goalCountMonth}
          heatmapMonth={heatmapMonth}
          onHeatmapMonthChange={(y, m) => setHeatmapMonth({ y, m })}
          heatmapTier={heatmapTier}
          calendarRefreshing={calendarRefreshing}
        />
      ) : (
        <p className={pl.hubCardDesc}>{flowChrome.trackingCalendarEmptyState}</p>
      )}
    </ProductAuxWebScreen>
  );
}

function CalendarPageSuspenseFallback() {
  const locale = getLocale() === "ru" ? "ru" : "en";
  const flowChrome = flowTrackerChromeBundle(locale);
  return (
    <ProductAuxWebScreen
      title={flowChrome.trackingCalendarPageTitle}
      loading
      loadingLabel={flowChrome.trackingCalendarPageIntro}
    />
  );
}

export default function CalendarTrackerPage() {
  return (
    <Suspense fallback={<CalendarPageSuspenseFallback />}>
      <CalendarTrackerPageContent />
    </Suspense>
  );
}

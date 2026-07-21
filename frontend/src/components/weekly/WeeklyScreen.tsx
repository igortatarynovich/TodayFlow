"use client";

import { Suspense, useEffect, useState } from "react";
import Link from "next/link";
import { PROFILE_CHART_DEEP_PATH } from "@/lib/profileRoutes";
import { OrientationRail, MeaningCard, LoadingSpinner } from "@/components/orbit";
import { deleteJson, getJson, postJson, putJson } from "@/lib/api";
import { t } from "@/lib/i18n";
import { useToastContext } from "@/components/ToastProvider";
import type { AccountProfile, WeeklyInsightResponse, TransitFeedResponse, PlanetaryTimeline } from "@/lib/types";
import { formatHabitMapStatsLine } from "@/components/today/flowPracticesMainTabChrome";
import { ProductAuxWebScreen } from "@/components/product-ui/ProductAuxWebScreen";
import pl from "@/design-system/layouts/productPageLayout.module.css";

type FusionResponse = {
  scores: {
    energy: number;
    emotional_balance: number;
    focus: number;
  };
};

type WeekPoint = {
  date: string;
  energy: number;
  emotional_balance: number;
  focus: number;
};

type HabitOverviewItem = {
  habit_id: number;
  current_streak_days: number;
  completion_rate: number;
};

type AsceticContract = {
  id: number;
  streak_days: number;
};

type CycleInsights = {
  tracked_days: number;
  fertile_window_days: number;
  ovulation_days: number;
};

type CycleEntry = {
  date: string;
  period_intensity: string | null;
  ovulation: boolean;
  fertile_window: boolean;
};

type RiskDay = {
  date: string;
  level: "low" | "medium" | "high";
  score: number;
  reasons: string[];
  action: string;
  actionHref: string;
};

type WeeklyGoal = {
  id: number;
  week_start: string;
  title: string;
  completed: boolean;
  progress_days?: number;
  last_progress_date?: string | null;
};

export default function WeeklyPage() {
  return (
    <Suspense
      fallback={
        <ProductAuxWebScreen
          title={t("dashboard.weekly.title", "Недельный фокус")}
          loading
          loadingLabel={t("dashboard.suspenseFallback", "Загрузка недельного фокуса…")}
        />
      }
    >
      <WeeklyContent />
    </Suspense>
  );
}

function WeeklyContent() {
  const toast = useToastContext();
  const [profile, setProfile] = useState<AccountProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [authMissing, setAuthMissing] = useState(false);
  const [weeklyInsight, setWeeklyInsight] = useState<WeeklyInsightResponse | null>(null);
  const [transitFeed, setTransitFeed] = useState<TransitFeedResponse | null>(null);
  const [planetEvents, setPlanetEvents] = useState<PlanetaryTimeline | null>(null);
  const [weekPoints, setWeekPoints] = useState<WeekPoint[]>([]);
  const [habitOverview, setHabitOverview] = useState<HabitOverviewItem[]>([]);
  const [asceticContracts, setAsceticContracts] = useState<AsceticContract[]>([]);
  const [cycleWeek, setCycleWeek] = useState<CycleInsights | null>(null);
  const [cycleEntriesWeek, setCycleEntriesWeek] = useState<CycleEntry[]>([]);
  const [selectedRiskDate, setSelectedRiskDate] = useState<string>("");
  const [weeklyGoals, setWeeklyGoals] = useState<WeeklyGoal[]>([]);
  const [newWeeklyGoal, setNewWeeklyGoal] = useState("");
  const [creatingGoal, setCreatingGoal] = useState(false);
  const [goalBusyId, setGoalBusyId] = useState<number | null>(null);
  const [showContent, setShowContent] = useState(false);
  const [showExtendedAnalysis, setShowExtendedAnalysis] = useState(false);

  useEffect(() => {
    const token = typeof window !== "undefined" ? localStorage.getItem("todayflow_token") : null;
    if (!token) {
      setAuthMissing(true);
      setLoading(false);
      return;
    }

    const bootstrap = async () => {
      try {
        const today = new Date().toISOString().split("T")[0];
        const weekDates = Array.from({ length: 7 }, (_, idx) => shiftDate(today, -(6 - idx)));
        const weekStart = getWeekStart(today);
        const [me, insight, feed, events, habits, contracts, cycle, cycleEntries, goals, fusionByDay] = await Promise.all([
          getJson<AccountProfile>("/auth/me").catch(() => null),
          getJson<WeeklyInsightResponse>("/celestial/weekly-insight").catch(() => null),
          getJson<TransitFeedResponse>("/celestial/transit-feed").catch(() => null),
          getJson<PlanetaryTimeline>("/celestial/planet-events?limit=6").catch(() => null),
          getJson<HabitOverviewItem[]>("/habits/overview/summary").catch(() => []),
          getJson<AsceticContract[]>("/tracking/ascetic-contracts?status_filter=active").catch(() => []),
          getJson<CycleInsights>(`/calendar/cycle/insights?from_date=${shiftDate(today, -6)}&to_date=${today}`).catch(() => null),
          getJson<CycleEntry[]>(`/calendar/cycle?from_date=${shiftDate(today, -6)}&to_date=${today}`).catch(() => []),
          getJson<WeeklyGoal[]>(`/tracking/weekly-goals?week_start=${weekStart}`).catch(() => []),
          Promise.all(
            weekDates.map((date) =>
              getJson<FusionResponse>(`/tracking/fusion/${date}`)
                .then((payload) => ({ date, ...payload.scores }))
                .catch(() => null),
            ),
          ),
        ]);
        setProfile(me);
        setWeeklyInsight(insight);
        setTransitFeed(feed);
        setPlanetEvents(events);
        setHabitOverview(habits);
        setAsceticContracts(contracts);
        setCycleWeek(cycle);
        setCycleEntriesWeek(cycleEntries);
        setWeeklyGoals(goals);
        setWeekPoints(fusionByDay.filter(Boolean) as WeekPoint[]);
      } catch (err) {
        console.error("Failed to load weekly data", err);
        toast.error(t("dashboard.weekly.errors.loadFailed", "Не удалось загрузить недельный фокус"));
      } finally {
        setLoading(false);
        setTimeout(() => setShowContent(true), 100);
      }
    };

    bootstrap();
  }, [toast]);

  if (loading) {
    return (
      <ProductAuxWebScreen
        title={t("dashboard.weekly.title", "Недельный фокус")}
        loading
        loadingLabel={t("dashboard.weekly.loading", "Загрузка недельного фокуса…")}
      />
    );
  }

  if (authMissing) {
    return (
      <ProductAuxWebScreen
        title={t("dashboard.auth.title", "Недельный фокус")}
        subtitle={t("dashboard.auth.subtitle", "Войди в аккаунт, чтобы увидеть недельный ритм, цели и персональные сигналы периода.")}
        guest={{
          message: t("dashboard.auth.subtitle", "Войди в аккаунт, чтобы увидеть недельный ритм, цели и персональные сигналы периода."),
          ctaHref: "/auth?mode=login",
          ctaLabel: t("dashboard.auth.login", "Войти"),
        }}
      />
    );
  }

  const weekAvg = weekPoints.length
    ? {
        energy: Math.round(weekPoints.reduce((sum, item) => sum + item.energy, 0) / weekPoints.length),
        emotional_balance: Math.round(weekPoints.reduce((sum, item) => sum + item.emotional_balance, 0) / weekPoints.length),
        focus: Math.round(weekPoints.reduce((sum, item) => sum + item.focus, 0) / weekPoints.length),
      }
    : null;
  const avgHabitRate = habitOverview.length
    ? Math.round(habitOverview.reduce((sum, item) => sum + item.completion_rate, 0) / habitOverview.length)
    : null;
  const maxHabitStreak = habitOverview.length
    ? Math.max(...habitOverview.map((item) => item.current_streak_days))
    : 0;
  const maxAsceticStreak = asceticContracts.length
    ? Math.max(...asceticContracts.map((item) => item.streak_days))
    : 0;
  const weeklyGuidance = buildWeeklyGuidance(weekAvg, avgHabitRate, maxHabitStreak, maxAsceticStreak);
  const riskDays = weekPoints.map((point) =>
    evaluateRiskDay(
      point,
      cycleEntriesWeek.find((entry) => entry.date === point.date) || null,
      avgHabitRate,
      maxHabitStreak,
      maxAsceticStreak,
    ),
  );
  const selectedRisk = riskDays.find((item) => item.date === selectedRiskDate) || riskDays[riskDays.length - 1] || null;
  const suggestedWeeklyGoals = buildSuggestedWeeklyGoals({
    weekAvg,
    avgHabitRate,
    maxHabitStreak,
    maxAsceticStreak,
    riskDays,
    cycleWeek,
  });
  const availableSuggestions = suggestedWeeklyGoals
    .filter((title) => !weeklyGoals.some((goal) => goal.title.trim().toLowerCase() === title.trim().toLowerCase()))
    .slice(0, Math.max(0, 3 - weeklyGoals.length));
  const sortedWeeklyGoals = [...weeklyGoals].sort((a, b) => {
    if (a.completed !== b.completed) return a.completed ? 1 : -1;
    const aScore = scoreGoalForRisk(a.title, selectedRisk);
    const bScore = scoreGoalForRisk(b.title, selectedRisk);
    if (aScore !== bScore) return bScore - aScore;
    return a.title.localeCompare(b.title, "ru-RU");
  });
  const topPriorityGoal = sortedWeeklyGoals.find((goal) => !goal.completed) || null;
  const todayIso = new Date().toISOString().split("T")[0];

  const handleCreateWeeklyGoal = async () => {
    const title = newWeeklyGoal.trim();
    if (!title || creatingGoal || weeklyGoals.length >= 3) return;
    try {
      setCreatingGoal(true);
      const created = await postJson<WeeklyGoal>("/tracking/weekly-goals", {
        week_start: getWeekStart(new Date().toISOString().split("T")[0]),
        title,
      });
      setWeeklyGoals((prev) => [...prev, created]);
      setNewWeeklyGoal("");
    } catch (error: any) {
      toast.error(error?.message || "Не удалось создать цель недели");
    } finally {
      setCreatingGoal(false);
    }
  };

  const handleAddSuggestedGoals = async () => {
    if (!availableSuggestions.length || creatingGoal || weeklyGoals.length >= 3) return;
    try {
      setCreatingGoal(true);
      const weekStart = getWeekStart(new Date().toISOString().split("T")[0]);
      const createdGoals: WeeklyGoal[] = [];
      for (const title of availableSuggestions) {
        const created = await postJson<WeeklyGoal>("/tracking/weekly-goals", {
          week_start: weekStart,
          title,
        });
        createdGoals.push(created);
      }
      setWeeklyGoals((prev) => [...prev, ...createdGoals]);
    } catch (error: any) {
      toast.error(error?.message || "Не удалось добавить предложенные цели");
    } finally {
      setCreatingGoal(false);
    }
  };

  const handleToggleWeeklyGoal = async (goal: WeeklyGoal) => {
    try {
      setGoalBusyId(goal.id);
      const updated = await putJson<WeeklyGoal>(`/tracking/weekly-goals/${goal.id}`, {
        completed: !goal.completed,
      });
      setWeeklyGoals((prev) => prev.map((item) => (item.id === goal.id ? updated : item)));
    } catch (error: any) {
      toast.error(error?.message || "Не удалось обновить цель");
    } finally {
      setGoalBusyId(null);
    }
  };

  const handleDeleteWeeklyGoal = async (goalId: number) => {
    try {
      setGoalBusyId(goalId);
      await deleteJson(`/tracking/weekly-goals/${goalId}`);
      setWeeklyGoals((prev) => prev.filter((item) => item.id !== goalId));
    } catch (error: any) {
      toast.error((error as any)?.message || "Не удалось удалить цель");
    } finally {
      setGoalBusyId(null);
    }
  };

  const handleStepPriorityGoalToday = async () => {
    if (!topPriorityGoal || goalBusyId !== null) return;
    if (topPriorityGoal.completed || topPriorityGoal.last_progress_date === todayIso) return;
    try {
      setGoalBusyId(topPriorityGoal.id);
      const updated = await postJson<WeeklyGoal>(`/tracking/weekly-goals/${topPriorityGoal.id}/step`, { date: todayIso });
      setWeeklyGoals((prev) => prev.map((item) => (item.id === topPriorityGoal.id ? updated : item)));
    } catch (error: any) {
      toast.error(error?.message || "Не удалось отметить шаг по цели");
    } finally {
      setGoalBusyId(null);
    }
  };

  return (
    <ProductAuxWebScreen
      testId="weekly-focus-page"
      title={t("dashboard.weekly.title", "Недельный фокус")}
      subtitle={t(
        "dashboard.weekly.description",
        "Обзор недели: главное за период и понятные шаги на ближайшие дни.",
      )}
      railTitle={weeklyGuidance ? t("dashboard.weekly.title", "Недельный фокус") : undefined}
      railHint={weeklyGuidance ?? undefined}
      contentClassName={`${pl.content} ${pl.legacyHost}`}
    >
      <section className="orbit-hero-content-block">
        <div className="orbit-hero-content-container">

          {/* Weekly Insight Card */}
          <section 
            className="orbit-card" 
            style={{ 
              background: "rgba(255, 255, 255, 0.95)", 
              boxShadow: "0 4px 16px rgba(0, 0, 0, 0.08)",
              opacity: showContent ? 1 : 0,
              transform: showContent ? "translateY(0)" : "translateY(30px)",
              transition: "opacity 0.8s ease 0.2s, transform 0.8s ease 0.2s"
            }}
          >
            <OrientationRail
              sectionLabel="Недельный фокус"
              metaLabel={weeklyInsight?.insight.phase_name || "Эта неделя"}
              stepLabel={weeklyInsight?.insight.axis_label || "Личная картина недели"}
            />
            {weeklyInsight ? (
              <div style={{ marginTop: "var(--orbit-space-lg)" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "var(--orbit-space-md)", flexWrap: "wrap", gap: "var(--orbit-space-md)" }}>
                  <h2 className="orbit-display-sm" style={{ margin: 0, flex: 1 }}>
                    {weeklyInsight.insight.title}
                  </h2>
                  {weeklyInsight.insight.keywords && weeklyInsight.insight.keywords.length > 0 && (
                    <div style={{ display: "flex", flexWrap: "wrap", gap: "var(--orbit-space-xs)" }}>
                      {weeklyInsight.insight.keywords.slice(0, 3).map((keyword, idx) => (
                        <span key={idx} className="orbit-badge-xs" style={{ margin: 0 }}>
                          {keyword}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
                <div style={{ 
                  padding: "var(--orbit-space-xl)",
                  background: "linear-gradient(135deg, var(--orbit-color-mist) 0%, rgba(245, 243, 240, 0.8) 100%)",
                  borderRadius: "var(--orbit-radius-md)",
                  marginBottom: "var(--orbit-space-md)",
                  border: "1px solid var(--orbit-color-border-light)"
                }}>
                  <p className="orbit-body" style={{ marginBottom: "var(--orbit-space-md)", lineHeight: 1.7 }}>
                    {weeklyInsight.insight.summary}
                  </p>
                  {weeklyInsight.insight.cta && (
                    <div style={{ 
                      paddingTop: "var(--orbit-space-md)", 
                      borderTop: "1px solid var(--orbit-color-border-light)",
                      marginTop: "var(--orbit-space-md)"
                    }}>
                      <p className="orbit-body-sm" style={{ fontStyle: "italic", color: "var(--orbit-color-ink)" }}>
                        {weeklyInsight.insight.cta}
                      </p>
                    </div>
                  )}
                </div>
                {weeklyInsight.next_phase && (
                  <div style={{ 
                    padding: "var(--orbit-space-md)", 
                    border: "1px solid var(--orbit-color-border)", 
                    borderRadius: "var(--orbit-radius-sm)",
                    background: "var(--orbit-color-card-warm)"
                  }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "var(--orbit-space-sm)" }}>
                      <div>
                        <p className="orbit-body-sm orbit-text-muted" style={{ marginBottom: "var(--orbit-space-xs)" }}>
                          Следующая фаза
                        </p>
                        <p className="orbit-body" style={{ fontWeight: 600, margin: 0 }}>
                          {weeklyInsight.next_phase.name}
                        </p>
                      </div>
                      <div style={{ textAlign: "right" }}>
                        <p className="orbit-body-sm orbit-text-muted" style={{ marginBottom: "var(--orbit-space-xs)" }}>
                          Через
                        </p>
                        <p className="orbit-body" style={{ fontWeight: 600, margin: 0 }}>
                          {weeklyInsight.next_phase.in_days} {weeklyInsight.next_phase.in_days === 1 ? "день" : weeklyInsight.next_phase.in_days < 5 ? "дня" : "дней"}
                        </p>
                      </div>
                    </div>
                  </div>
                )}
                <div style={{ marginTop: "var(--orbit-space-md)", display: "flex", gap: "var(--orbit-space-sm)", flexWrap: "wrap" }}>
                  <Link href="/today" className="orbit-button orbit-button-secondary orbit-button-sm">
                    Дневной обзор →
                  </Link>
                  <Link href="/lunar/today" className="orbit-button orbit-button-secondary orbit-button-sm">
                    Небесные события →
                  </Link>
                </div>
              </div>
            ) : (
              <div style={{ marginTop: "var(--orbit-space-lg)" }}>
                <div style={{ 
                  padding: "var(--orbit-space-xl)",
                  background: "var(--orbit-color-mist)",
                  borderRadius: "var(--orbit-radius-md)",
                  textAlign: "center"
                }}>
                <p className="orbit-body-sm orbit-text-muted" style={{ marginBottom: "var(--orbit-space-md)" }}>
                  {t("dashboard.weekly.insight.noData", "Недельный фокус появится после заполнения профиля.")}
                </p>
                  <Link href="/onboarding/core" className="orbit-button orbit-button-primary">
                    {t("dashboard.weekly.insight.createChart", "Собрать профиль")}
                  </Link>
                </div>
              </div>
            )}
          </section>

          <section
            className="orbit-card"
            style={{
              background: "rgba(255, 255, 255, 0.95)",
              boxShadow: "0 4px 16px rgba(0, 0, 0, 0.08)",
              marginTop: "var(--orbit-space-xl)",
              opacity: showContent ? 1 : 0,
              transform: showContent ? "translateY(0)" : "translateY(30px)",
              transition: "opacity 0.8s ease 0.25s, transform 0.8s ease 0.25s",
            }}
          >
            <OrientationRail
              sectionLabel={t("dashboard.weekly.rhythm.section", "Недельный ритм")}
              metaLabel={t("dashboard.weekly.rhythm.meta", "7 дней")}
              stepLabel={t("dashboard.weekly.rhythm.step", "Состояние и устойчивость")}
            />
            <h2 className="orbit-display-sm" style={{ marginBottom: "var(--orbit-space-xs)" }}>Карта ритма недели</h2>
            <p className="orbit-body-sm orbit-text-muted">
              Срез по состоянию, дисциплине и циклу за последние 7 дней.
            </p>

            <div style={{ marginTop: "var(--orbit-space-md)", display: "grid", gap: "var(--orbit-space-md)" }}>
              {weekPoints.length ? (
                <>
                  <MetricTrendRow label="Энергия" color="#0ea5e9" values={weekPoints.map((item) => item.energy)} />
                  <MetricTrendRow label="Баланс" color="#14b8a6" values={weekPoints.map((item) => item.emotional_balance)} />
                  <MetricTrendRow label="Фокус" color="#f59e0b" values={weekPoints.map((item) => item.focus)} />
                  <div style={{ display: "grid", gridTemplateColumns: "repeat(7, minmax(0, 1fr))", gap: "6px", color: "var(--orbit-color-text-muted)", fontSize: "0.72rem" }}>
                    {weekPoints.map((item) => (
                      <span key={`week-label-${item.date}`} style={{ textAlign: "center" }}>
                        {new Date(item.date + "T12:00:00").toLocaleDateString("ru-RU", { weekday: "short" })}
                      </span>
                    ))}
                  </div>
                </>
              ) : (
                <p className="orbit-body-sm orbit-text-muted">Недостаточно данных состояния за неделю.</p>
              )}
            </div>

            <div style={{ marginTop: "var(--orbit-space-md)", display: "grid", gap: "var(--orbit-space-sm)", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))" }}>
              <MeaningCard label="Средняя энергия" body={weekAvg ? String(weekAvg.energy) : "-"} />
              <MeaningCard label="Средний баланс" body={weekAvg ? String(weekAvg.emotional_balance) : "-"} />
              <MeaningCard
                label="Карта привычек"
                body={
                  habitOverview.length
                    ? formatHabitMapStatsLine("ru", maxHabitStreak)
                    : "нет данных"
                }
              />
              <MeaningCard label="Стрик недели" body={String(Math.max(maxHabitStreak, maxAsceticStreak))} />
              <MeaningCard label="Овуляция (7д)" body={cycleWeek ? String(cycleWeek.ovulation_days) : "-"} />
              <MeaningCard label="Фертильные дни (7д)" body={cycleWeek ? String(cycleWeek.fertile_window_days) : "-"} />
            </div>

            <div style={{ marginTop: "var(--orbit-space-md)", border: "1px solid var(--orbit-color-border)", borderRadius: "var(--orbit-radius-sm)", padding: "var(--orbit-space-md)", background: "var(--orbit-color-mist)" }}>
              <p className="orbit-body-sm" style={{ fontWeight: 600, marginBottom: "var(--orbit-space-sm)" }}>
                Дни риска: выбери день и проверь причину
              </p>
              {riskDays.length ? (
                <>
                  <div style={{ display: "grid", gridTemplateColumns: "repeat(7, minmax(0, 1fr))", gap: "6px" }}>
                    {riskDays.map((day) => (
                      <button
                        key={`risk-day-${day.date}`}
                        type="button"
                        onClick={() => setSelectedRiskDate(day.date)}
                        style={{
                          borderRadius: "8px",
                          border: selectedRisk?.date === day.date ? "2px solid #0f172a" : "1px solid #cbd5e1",
                          background: day.level === "high" ? "#fee2e2" : day.level === "medium" ? "#fef3c7" : "#dcfce7",
                          color: "#0f172a",
                          fontSize: "0.76rem",
                          padding: "0.35rem 0.15rem",
                          fontWeight: 700,
                          cursor: "pointer",
                        }}
                      >
                        {new Date(day.date + "T12:00:00").toLocaleDateString("ru-RU", { weekday: "short" })}
                      </button>
                    ))}
                  </div>
                  {selectedRisk && (
                    <div style={{ marginTop: "var(--orbit-space-sm)", borderRadius: "8px", border: "1px solid #dbe4ee", background: "#fff", padding: "0.7rem" }}>
                      <div style={{ display: "flex", justifyContent: "space-between", gap: "0.55rem", alignItems: "center", flexWrap: "wrap" }}>
                        <span className="orbit-body-sm" style={{ fontWeight: 700 }}>
                          {new Date(selectedRisk.date + "T12:00:00").toLocaleDateString("ru-RU", { weekday: "long", day: "numeric", month: "short" })}
                        </span>
                        <span className="orbit-body-xs" style={{ borderRadius: "999px", padding: "0.1rem 0.5rem", border: "1px solid #cbd5e1", background: "#f8fafc" }}>
                          Риск {selectedRisk.level === "high" ? "высокий" : selectedRisk.level === "medium" ? "средний" : "низкий"} ({selectedRisk.score})
                        </span>
                      </div>
                      <ul style={{ margin: "0.45rem 0 0 1rem" }}>
                        {selectedRisk.reasons.map((reason) => (
                          <li key={reason} className="orbit-body-sm">{reason}</li>
                        ))}
                      </ul>
                      <p className="orbit-body-sm" style={{ marginTop: "0.4rem", color: "var(--orbit-color-text-muted)" }}>
                        Действие дня: {selectedRisk.action}
                      </p>
                      {topPriorityGoal && (
                        <p className="orbit-body-sm" style={{ marginTop: "0.35rem", color: "#0f172a", fontWeight: 600 }}>
                          Приоритетная цель: {topPriorityGoal.title}
                        </p>
                      )}
                      <div style={{ marginTop: "0.45rem", display: "flex", gap: "0.45rem", flexWrap: "wrap" }}>
                        <Link href={selectedRisk.actionHref} className="orbit-button orbit-button-secondary orbit-button-sm">
                          Выполнить действие
                        </Link>
                        {topPriorityGoal && (
                          <button
                            type="button"
                            onClick={handleStepPriorityGoalToday}
                            disabled={
                              goalBusyId !== null ||
                              topPriorityGoal.completed ||
                              topPriorityGoal.last_progress_date === todayIso
                            }
                            className="orbit-button orbit-button-secondary orbit-button-sm"
                          >
                            {topPriorityGoal.completed
                              ? "Цель уже выполнена"
                              : topPriorityGoal.last_progress_date === todayIso
                              ? "Шаг уже отмечен сегодня"
                              : goalBusyId === topPriorityGoal.id
                              ? "..."
                              : "Сделал шаг по цели"}
                          </button>
                        )}
                      </div>
                    </div>
                  )}
                </>
              ) : (
                <p className="orbit-body-sm orbit-text-muted" style={{ margin: 0 }}>
                  Для анализа риска нужны хотя бы 2-3 дня отметок состояния.
                </p>
              )}
            </div>

            <div style={{ marginTop: "var(--orbit-space-md)", border: "1px solid var(--orbit-color-border)", borderRadius: "var(--orbit-radius-sm)", padding: "var(--orbit-space-md)", background: "#fff" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: "0.6rem", flexWrap: "wrap" }}>
                <p className="orbit-body-sm" style={{ fontWeight: 700, margin: 0 }}>
                  Цели недели
                </p>
                <span className="orbit-body-xs orbit-text-muted">{weeklyGoals.filter((item) => item.completed).length}/{weeklyGoals.length || 0} выполнено</span>
              </div>
              <div style={{ marginTop: "0.55rem", border: "1px solid #e2e8f0", borderRadius: "8px", padding: "0.55rem", background: "#f8fafc" }}>
                <p className="orbit-body-xs orbit-text-muted" style={{ margin: 0 }}>
                  Подсказка на неделю
                </p>
                <div style={{ marginTop: "0.35rem", display: "flex", gap: "0.35rem", flexWrap: "wrap" }}>
                  {availableSuggestions.length ? (
                    availableSuggestions.map((goal) => (
                      <span key={`suggested-goal-${goal}`} className="orbit-badge-xs orbit-badge-xs--muted" style={{ margin: 0 }}>
                        {goal}
                      </span>
                    ))
                  ) : (
                    <span className="orbit-body-xs orbit-text-muted">Все предложения уже добавлены или достигнут лимит.</span>
                  )}
                </div>
                <div style={{ marginTop: "0.45rem" }}>
                  <button
                    type="button"
                    onClick={handleAddSuggestedGoals}
                    disabled={creatingGoal || !availableSuggestions.length || weeklyGoals.length >= 3}
                    className="orbit-button orbit-button-secondary orbit-button-sm"
                  >
                    {creatingGoal ? "..." : "Добавить предложенные"}
                  </button>
                </div>
              </div>
              <div style={{ marginTop: "0.55rem", display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
                <input
                  value={newWeeklyGoal}
                  onChange={(event) => setNewWeeklyGoal(event.target.value)}
                  placeholder={weeklyGoals.length >= 3 ? "Лимит 3 цели на неделю" : "Новая цель недели"}
                  disabled={creatingGoal || weeklyGoals.length >= 3}
                  style={{
                    flex: "1 1 260px",
                    border: "1px solid #cbd5e1",
                    borderRadius: "8px",
                    padding: "0.45rem 0.55rem",
                    fontSize: "0.9rem",
                    background: "#fff",
                  }}
                />
                <button
                  type="button"
                  onClick={handleCreateWeeklyGoal}
                  disabled={creatingGoal || !newWeeklyGoal.trim() || weeklyGoals.length >= 3}
                  className="orbit-button orbit-button-secondary orbit-button-sm"
                >
                  {creatingGoal ? "..." : "Добавить"}
                </button>
              </div>
              <div style={{ marginTop: "0.6rem", display: "grid", gap: "0.45rem" }}>
                {sortedWeeklyGoals.length ? (
                  sortedWeeklyGoals.map((goal, index) => (
                    <div
                      key={goal.id}
                      style={{
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "space-between",
                        gap: "0.55rem",
                        border: "1px solid #e2e8f0",
                        borderRadius: "8px",
                        padding: "0.45rem 0.55rem",
                        background: goal.completed ? "#f0fdf4" : "#f8fafc",
                      }}
                    >
                      <label style={{ display: "flex", alignItems: "center", gap: "0.45rem", flex: 1, cursor: "pointer" }}>
                        <input
                          type="checkbox"
                          checked={goal.completed}
                          disabled={goalBusyId === goal.id}
                          onChange={() => handleToggleWeeklyGoal(goal)}
                        />
                        <span className="orbit-body-sm" style={{ textDecoration: goal.completed ? "line-through" : "none", color: "#334155" }}>
                          {goal.title}
                        </span>
                        {!goal.completed && index === 0 && (
                          <span className="orbit-badge-xs" style={{ margin: 0 }}>
                            приоритет сегодня
                          </span>
                        )}
                      </label>
                      <button
                        type="button"
                        onClick={() => handleDeleteWeeklyGoal(goal.id)}
                        disabled={goalBusyId === goal.id}
                        className="orbit-button orbit-button-secondary orbit-button-sm"
                      >
                        удалить
                      </button>
                    </div>
                  ))
                ) : (
                  <p className="orbit-body-sm orbit-text-muted" style={{ margin: 0 }}>
                    Добавь 1-3 цели на неделю и отслеживай выполнение здесь.
                  </p>
                )}
              </div>
            </div>

            <div
              style={{
                marginTop: "var(--orbit-space-md)",
                border: "1px solid var(--orbit-color-border)",
                borderRadius: "var(--orbit-radius-sm)",
                background: "var(--orbit-color-card-warm)",
                padding: "var(--orbit-space-md)",
              }}
            >
              <p className="orbit-body-sm" style={{ margin: 0, lineHeight: 1.65 }}>{weeklyGuidance}</p>
            </div>
            <div style={{ marginTop: "var(--orbit-space-md)", display: "flex", gap: "var(--orbit-space-sm)", flexWrap: "wrap" }}>
              <Link href="/today" className="orbit-button orbit-button-secondary orbit-button-sm">Открыть Сегодня</Link>
              <Link href="/cycle" className="orbit-button orbit-button-secondary orbit-button-sm">Открыть цикл</Link>
              <Link href="/habits" className="orbit-button orbit-button-secondary orbit-button-sm">Карта привычек</Link>
              <Link href="/weekly/integration" className="orbit-button orbit-button-secondary orbit-button-sm">Открыть интеграцию недели</Link>
              <button
                type="button"
                className="orbit-button orbit-button-secondary orbit-button-sm"
                onClick={() => setShowExtendedAnalysis((prev) => !prev)}
              >
                {showExtendedAnalysis ? "Скрыть расширенный анализ" : "Показать расширенный анализ"}
              </button>
            </div>
          </section>

          {showExtendedAnalysis && (
            <>
              {/* Transit Feed */}
              <section 
                className="orbit-card" 
                style={{ 
                  background: "rgba(255, 255, 255, 0.95)", 
                  boxShadow: "0 4px 16px rgba(0, 0, 0, 0.08)", 
                  marginTop: "var(--orbit-space-xl)",
                  opacity: showContent ? 1 : 0,
                  transform: showContent ? "translateY(0)" : "translateY(30px)",
                  transition: "opacity 0.8s ease 0.3s, transform 0.8s ease 0.3s"
                }}
              >
            <OrientationRail
              sectionLabel="Транзиты недели"
              metaLabel="Сейчас"
              stepLabel="Активные влияния"
            />
            <h2 className="orbit-display-sm">{t("dashboard.weekly.transits.title", "Активные транзиты")}</h2>
            <p className="orbit-body-sm orbit-text-muted">
              {t(
                "dashboard.weekly.transits.description",
                "Текущие транзиты и их влияние на твой недельный ритм через натальную карту."
              )}
            </p>

            {(transitFeed?.events && transitFeed.events.length > 0) || (planetEvents?.upcoming && planetEvents.upcoming.length > 0) ? (
              <div style={{ marginTop: "var(--orbit-space-md)", display: "flex", flexDirection: "column", gap: "var(--orbit-space-md)" }}>
                {(transitFeed?.events || planetEvents?.upcoming || []).slice(0, 6).map((event, idx) => {
                  const eventDate = new Date(event.timestamp);
                  const isToday = eventDate.toDateString() === new Date().toDateString();
                  const isUpcoming = eventDate > new Date();
                  return (
                    <div 
                      key={idx} 
                      style={{ 
                        padding: "var(--orbit-space-md)",
                        border: isToday ? "2px solid var(--orbit-color-primary-accent)" : "1px solid var(--orbit-color-border)",
                        borderRadius: "var(--orbit-radius-sm)",
                        background: isToday ? "var(--orbit-color-mist)" : "var(--orbit-color-card-warm)",
                        transition: "all 0.2s ease"
                      }}
                    >
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "start", marginBottom: "var(--orbit-space-xs)", flexWrap: "wrap", gap: "var(--orbit-space-xs)" }}>
                        <div style={{ display: "flex", alignItems: "center", gap: "var(--orbit-space-sm)" }}>
                          <span className="orbit-body" style={{ fontWeight: 600, fontSize: "1.1rem" }}>{event.planet}</span>
                          {isToday && (
                            <span className="orbit-badge-xs" style={{ margin: 0, background: "var(--orbit-color-primary-accent)", color: "white" }}>
                              Сегодня
                            </span>
                          )}
                          {isUpcoming && !isToday && (
                            <span className="orbit-badge-xs orbit-badge-xs--muted" style={{ margin: 0 }}>
                              Скоро
                            </span>
                          )}
                        </div>
                        <span className="orbit-body-sm orbit-text-muted" style={{ whiteSpace: "nowrap" }}>
                          {eventDate.toLocaleDateString("ru-RU", { day: "numeric", month: "long" })}
                        </span>
                      </div>
                      <p className="orbit-body" style={{ fontWeight: 500, marginBottom: "var(--orbit-space-xs)" }}>
                        {event.event_type}
                      </p>
                      {event.description && (
                        <p className="orbit-body-sm orbit-text-muted" style={{ marginTop: "var(--orbit-space-xs)", lineHeight: 1.6 }}>
                          {event.description}
                        </p>
                      )}
                      {event.keywords && event.keywords.length > 0 && (
                        <div style={{ display: "flex", flexWrap: "wrap", gap: "var(--orbit-space-xs)", marginTop: "var(--orbit-space-sm)" }}>
                          {event.keywords.map((keyword, kIdx) => (
                            <span key={kIdx} className="orbit-badge-xs orbit-badge-xs--muted" style={{ margin: 0 }}>
                              {keyword}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            ) : (
              <div style={{ 
                marginTop: "var(--orbit-space-md)", 
                padding: "var(--orbit-space-xl)", 
                background: "var(--orbit-color-mist)", 
                borderRadius: "var(--orbit-radius-sm)",
                textAlign: "center"
              }}>
                <p className="orbit-body-sm orbit-text-muted" style={{ marginBottom: "var(--orbit-space-md)" }}>
                  {t("dashboard.weekly.transits.noData", "Нет активных транзитов на данный момент.")}
                </p>
                <Link href="/lunar/today" className="orbit-button orbit-button-secondary orbit-button-sm">
                  Посмотреть небесные события →
                </Link>
              </div>
            )}
              </section>

              {/* Solar System Strip */}
              <section 
                className="orbit-card" 
                style={{ 
                  background: "rgba(255, 255, 255, 0.95)", 
                  boxShadow: "0 4px 16px rgba(0, 0, 0, 0.08)", 
                  marginTop: "var(--orbit-space-xl)",
                  opacity: showContent ? 1 : 0,
                  transform: showContent ? "translateY(0)" : "translateY(30px)",
                  transition: "opacity 0.8s ease 0.4s, transform 0.8s ease 0.4s"
                }}
              >
            <OrientationRail
              sectionLabel="Планетарная картина"
              metaLabel="Обзор"
              stepLabel="Текущие окна"
            />
            <h2 className="orbit-display-sm">{t("dashboard.weekly.solar.title", "Текущие планетарные позиции")}</h2>
            <p className="orbit-body-sm orbit-text-muted">
              {t(
                "dashboard.weekly.solar.description",
                "Визуальный слой недели: где сейчас стоят ключевые планеты и какие окна внимания они открывают."
              )}
            </p>

            {planetEvents?.windows && planetEvents.windows.length > 0 ? (
              <div style={{ marginTop: "var(--orbit-space-md)", display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "var(--orbit-space-md)" }}>
                {planetEvents.windows.slice(0, 4).map((window, idx) => {
                  const startDate = new Date(window.start_timestamp);
                  const endDate = new Date(window.end_timestamp);
                  const isActive = window.status === "active";
                  return (
                    <div 
                      key={idx} 
                      style={{ 
                        padding: "var(--orbit-space-md)",
                        border: isActive ? "2px solid var(--orbit-color-primary-accent)" : "1px solid var(--orbit-color-border)",
                        borderRadius: "var(--orbit-radius-sm)",
                        background: isActive ? "var(--orbit-color-mist)" : "var(--orbit-color-card-warm)",
                        transition: "all 0.2s ease",
                        display: "flex",
                        flexDirection: "column"
                      }}
                    >
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "start", marginBottom: "var(--orbit-space-xs)", flexWrap: "wrap", gap: "var(--orbit-space-xs)" }}>
                        <div>
                          <span className="orbit-body" style={{ fontWeight: 600, fontSize: "1.1rem" }}>{window.planet}</span>
                          {window.label && (
                            <span className="orbit-body-sm orbit-text-muted" style={{ marginLeft: "var(--orbit-space-xs)", display: "block", marginTop: "var(--orbit-space-xxs)" }}>
                              {window.label}
                            </span>
                          )}
                        </div>
                        <span className={`orbit-badge-xs ${isActive ? "" : "orbit-badge-xs--muted"}`} style={{ margin: 0 }}>
                          {isActive ? "Активно" : "Скоро"}
                        </span>
                      </div>
                      {window.description && (
                        <p className="orbit-body-sm" style={{ marginTop: "var(--orbit-space-xs)", lineHeight: 1.6, flex: 1 }}>
                          {window.description}
                        </p>
                      )}
                      {window.keywords && window.keywords.length > 0 && (
                        <div style={{ display: "flex", flexWrap: "wrap", gap: "var(--orbit-space-xs)", marginTop: "var(--orbit-space-sm)" }}>
                          {window.keywords.map((keyword, kIdx) => (
                            <span key={kIdx} className="orbit-badge-xs orbit-badge-xs--muted" style={{ margin: 0 }}>
                              {keyword}
                            </span>
                          ))}
                        </div>
                      )}
                      <p className="orbit-body-xs orbit-text-muted" style={{ marginTop: "var(--orbit-space-sm)", paddingTop: "var(--orbit-space-xs)", borderTop: "1px solid var(--orbit-color-border-light)" }}>
                        {startDate.toLocaleDateString("ru-RU", { day: "numeric", month: "short" })} - {endDate.toLocaleDateString("ru-RU", { day: "numeric", month: "short" })}
                      </p>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div style={{ 
                marginTop: "var(--orbit-space-md)", 
                padding: "var(--orbit-space-xl)", 
                background: "var(--orbit-color-mist)", 
                borderRadius: "var(--orbit-radius-sm)",
                textAlign: "center"
              }}>
                <p className="orbit-body-sm orbit-text-muted" style={{ marginBottom: "var(--orbit-space-md)" }}>
                  {t("dashboard.weekly.solar.noData", "Нет активных планетарных окон на данный момент.")}
                </p>
                <div style={{ display: "flex", gap: "var(--orbit-space-sm)", justifyContent: "center", flexWrap: "wrap" }}>
                  <Link href="/today" className="orbit-button orbit-button-secondary orbit-button-sm">
                    Дневной обзор →
                  </Link>
                  <Link href="/lunar/today" className="orbit-button orbit-button-secondary orbit-button-sm">
                    Небесные события →
                  </Link>
                </div>
              </div>
            )}
              </section>

              {/* Navigation */}
              <section className="orbit-card" style={{ background: "rgba(255, 255, 255, 0.95)", boxShadow: "0 4px 16px rgba(0, 0, 0, 0.08)", marginTop: "var(--orbit-space-xl)" }}>
            <OrientationRail
              sectionLabel={t("dashboard.weekly.nav.section", "Куда идти дальше")}
              metaLabel={t("dashboard.weekly.nav.meta", "Следующие экраны")}
            />
            <div className="orbit-card-grid" style={{ gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", marginTop: "var(--orbit-space-md)" }}>
              <Link href="/profile" className="orbit-card orbit-card-link">
                <h3 className="orbit-display-xs">{t("dashboard.weekly.nav.dashboard", "Профиль")}</h3>
                <p className="orbit-body-sm orbit-text-muted">{t("dashboard.weekly.nav.dashboardDesc", "Твоя опора")}</p>
              </Link>
              <Link href="/today" className="orbit-card orbit-card-link">
                <h3 className="orbit-display-xs">{t("dashboard.weekly.nav.daily", "Сегодня")}</h3>
                <p className="orbit-body-sm orbit-text-muted">{t("dashboard.weekly.nav.dailyDesc", "Дневной поток")}</p>
              </Link>
              <Link href={PROFILE_CHART_DEEP_PATH} className="orbit-card orbit-card-link">
                <h3 className="orbit-display-xs">{t("dashboard.weekly.nav.birthChart", "Натальная карта")}</h3>
                <p className="orbit-body-sm orbit-text-muted">{t("dashboard.weekly.nav.birthChartDesc", "Глубже в основу")}</p>
              </Link>
              <Link href="/catalog" className="orbit-card orbit-card-link">
                <h3 className="orbit-display-xs">{t("dashboard.weekly.nav.explore", "Сервисы")}</h3>
                <p className="orbit-body-sm orbit-text-muted">{t("dashboard.weekly.nav.exploreDesc", "Куда углубиться")}</p>
              </Link>
            </div>
              </section>
            </>
          )}
        </div>
      </section>
    </ProductAuxWebScreen>
  );
}

function evaluateRiskDay(
  point: WeekPoint,
  cycleEntry: CycleEntry | null,
  avgHabitRate: number | null,
  maxHabitStreak: number,
  maxAsceticStreak: number,
): RiskDay {
  let score = 0;
  const reasons: string[] = [];

  if (point.energy < 40) {
    score += 2;
    reasons.push("Низкая энергия");
  } else if (point.energy < 50) {
    score += 1;
    reasons.push("Энергия ниже комфортного диапазона");
  }
  if (point.emotional_balance < 45) {
    score += 2;
    reasons.push("Эмоциональный фон просел");
  }
  if (point.focus < 45) {
    score += 1;
    reasons.push("Фокус ослаблен");
  }

  if (cycleEntry?.period_intensity === "heavy") {
    score += 2;
    reasons.push("Высокая интенсивность цикла");
  } else if (cycleEntry?.period_intensity === "medium") {
    score += 1;
    reasons.push("Средняя нагрузка по циклу");
  }
  if (cycleEntry?.fertile_window) {
    score += 1;
    reasons.push("Фертильное окно: повышена чувствительность");
  }

  if ((avgHabitRate || 0) < 55) {
    score += 1;
    reasons.push("Низкая консистентность привычек");
  }
  if (Math.max(maxHabitStreak, maxAsceticStreak) < 3) {
    score += 1;
    reasons.push("Короткие стрики по дисциплине");
  }

  const level: "low" | "medium" | "high" = score >= 6 ? "high" : score >= 3 ? "medium" : "low";
  const action =
    level === "high"
      ? "Сделай день проще: 1 ключевая задача + 1 короткая восстановительная практика."
      : level === "medium"
      ? "Держи управляемый темп: 2 фокус-блока и один чек-ин состояния."
      : "Поддерживай ритм: закрепи результат и зафиксируй наблюдение вечером.";
  const actionHref = level === "high" ? "/practices" : level === "medium" ? "/tracking/progress" : "/tracking/ritual";

  if (!reasons.length) {
    reasons.push("Стабильные метрики состояния");
  }

  return { date: point.date, level, score, reasons, action, actionHref };
}

function shiftDate(isoDate: string, deltaDays: number): string {
  const [y, m, d] = isoDate.split("-").map(Number);
  const date = new Date(y, (m || 1) - 1, d || 1);
  date.setDate(date.getDate() + deltaDays);
  return date.toISOString().split("T")[0];
}

function getWeekStart(isoDate: string): string {
  const [y, m, d] = isoDate.split("-").map(Number);
  const date = new Date(y, (m || 1) - 1, d || 1);
  const day = date.getDay();
  const diff = day === 0 ? -6 : 1 - day;
  date.setDate(date.getDate() + diff);
  return date.toISOString().split("T")[0];
}

function MetricTrendRow({ label, color, values }: { label: string; color: string; values: number[] }) {
  return (
    <div style={{ display: "grid", gap: "6px" }}>
      <span className="orbit-body-sm" style={{ fontWeight: 600 }}>{label}</span>
      <div style={{ display: "grid", gridTemplateColumns: `repeat(${values.length || 1}, minmax(0, 1fr))`, gap: "6px", alignItems: "end", minHeight: "40px" }}>
        {values.map((value, idx) => (
          <span
            key={`${label}-${idx}`}
            title={String(value)}
            style={{
              height: `${Math.max(8, Math.min(100, value))}%`,
              background: color,
              borderRadius: "5px 5px 0 0",
              opacity: 0.9,
              display: "block",
            }}
          />
        ))}
      </div>
    </div>
  );
}

function buildSuggestedWeeklyGoals({
  weekAvg,
  avgHabitRate,
  maxHabitStreak,
  maxAsceticStreak,
  riskDays,
  cycleWeek,
}: {
  weekAvg: { energy: number; emotional_balance: number; focus: number } | null;
  avgHabitRate: number | null;
  maxHabitStreak: number;
  maxAsceticStreak: number;
  riskDays: RiskDay[];
  cycleWeek: CycleInsights | null;
}): string[] {
  const items: string[] = [];
  const highRiskDays = riskDays.filter((day) => day.level === "high").length;
  const mediumRiskDays = riskDays.filter((day) => day.level === "medium").length;

  if (weekAvg && (weekAvg.energy < 50 || highRiskDays >= 2)) {
    items.push("5 из 7 дней: утренний energy check + 5 минут дыхания.");
  }
  if (weekAvg && (weekAvg.emotional_balance < 50 || mediumRiskDays >= 3)) {
    items.push("4 вечерних рефлексии за неделю без пропусков.");
  }
  if ((avgHabitRate || 0) < 60 || Math.max(maxHabitStreak, maxAsceticStreak) < 4) {
    items.push("Довести один стрик до 5 дней подряд.");
  }
  if (cycleWeek && cycleWeek.fertile_window_days > 0) {
    items.push("В фертильные дни: щадящий темп и один осознанный чек-ин состояния.");
  }
  if (items.length < 2) {
    items.push("Ежедневно: 1 ключевая задача + 1 короткая практика.");
  }
  if (items.length < 3) {
    items.push("До конца недели: закрывать день вечерним ритуалом.");
  }

  return items.slice(0, 3);
}

function scoreGoalForRisk(goalTitle: string, selectedRisk: RiskDay | null): number {
  if (!selectedRisk) return 0;
  const text = goalTitle.toLowerCase();
  let score = 0;

  if (selectedRisk.level === "high" && hasAny(text, ["дых", "восстанов", "щад", "ритуал", "пауза"])) score += 3;
  if (selectedRisk.level === "medium" && hasAny(text, ["фокус", "чек", "блок", "дневник", "прогресс"])) score += 3;
  if (selectedRisk.level === "low" && hasAny(text, ["результат", "приоритет", "задача", "стрик"])) score += 2;

  if (selectedRisk.reasons.some((reason) => reason.toLowerCase().includes("энерг")) && hasAny(text, ["энерг", "дых", "пауза", "восстанов"])) score += 2;
  if (selectedRisk.reasons.some((reason) => reason.toLowerCase().includes("фокус")) && hasAny(text, ["фокус", "задач", "блок"])) score += 2;
  if (selectedRisk.reasons.some((reason) => reason.toLowerCase().includes("эмо")) && hasAny(text, ["рефлекс", "дневник", "ритуал", "чек"])) score += 2;
  if (selectedRisk.reasons.some((reason) => reason.toLowerCase().includes("цикл")) && hasAny(text, ["щад", "восстанов", "дых", "мягк"])) score += 1;

  return score;
}

function hasAny(text: string, needles: string[]): boolean {
  return needles.some((needle) => text.includes(needle));
}

function buildWeeklyGuidance(
  weekAvg: { energy: number; emotional_balance: number; focus: number } | null,
  avgHabitRate: number | null,
  maxHabitStreak: number,
  maxAsceticStreak: number,
): string {
  if (!weekAvg) {
    return "Начни с ежедневной отметки состояния и одной привычки 3 дня подряд.";
  }
  if (weekAvg.energy < 45 || weekAvg.emotional_balance < 45) {
    return "Неделя проживалась в щадящем режиме. На следующей неделе держи короткие рабочие блоки, фиксируй 2 чек-ина состояния в день и усиливай восстановительные практики.";
  }
  if ((avgHabitRate || 0) < 55 && Math.max(maxHabitStreak, maxAsceticStreak) < 3) {
    return "Состояние в ресурсе, но дисциплина нестабильна. Сфокусируйся на 1-2 привычках и цели на стрик 3-5 дней без расширения нагрузки.";
  }
  return "Ритм недели устойчивый. Сохраняй текущую структуру дня, добавь один амбициозный приоритет и закрепляй результаты вечерним завершением.";
}

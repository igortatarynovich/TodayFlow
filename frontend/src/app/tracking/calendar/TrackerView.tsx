"use client";

import Link from "next/link";
import { useState, useEffect, useRef, useCallback, useMemo, type CSSProperties, type ReactNode } from "react";
import { computeMarks, lineDone, type LineId } from "./trackingRhythm";
import { sliceLastNDaysSorted } from "./trackerCompute";
import {
  FREE_LIMITS,
  type AsceticCategoryTone,
  type GoalCategoryTone,
  type HabitCategoryTone,
  type PracticeCategoryTone,
  type ScreenHeroKind,
} from "./entityTrackerSpec";
import {
  type CalendarGoalTrackIn,
  type CalendarHabitTrackIn,
  type CalendarAsceticTrackIn,
  computeScreenHero,
  categorySummaryLines,
  buildAttentionItems,
  buildBestItems,
  computeGoalEntityStatus,
  computeHabitEntityStatus,
  computeAsceticEntityStatus,
  countActiveTracks,
} from "./entityTrackerCompute";
import { DEFAULT_TRACKER_TIER, type TrackerTier } from "./trackerSpec";
import { CalendarHeatmap } from "./CalendarHeatmap";
import { EntityCreateWizard } from "./EntityCreateWizard";
import type { TrackerEntityKind } from "./trackerEntityCatalog";
import { getLocale } from "@/lib/i18n";
import {
  flowTrackerChromeBundle,
  practicesExperienceChromeBundle,
  type FlowPracticesChromeLocale,
  type FlowTrackerChromeBundle,
} from "@/components/today/flowPracticesMainTabChrome";

function formatIsoShort(iso: string, locale: FlowPracticesChromeLocale) {
  return new Date(iso + "T12:00:00").toLocaleDateString(locale === "ru" ? "ru-RU" : "en-US", {
    day: "numeric",
    month: "short",
  });
}

function templateReplace(s: string, vars: Record<string, string | number>) {
  return Object.keys(vars).reduce((acc, k) => acc.replaceAll(`{{${k}}}`, String(vars[k])), s);
}

export type CalendarDayView = {
  date: string;
  activities: {
    practice?: { completed?: boolean; count?: number };
    goal?: { completed?: boolean };
    habits?: { completed?: boolean; count?: number };
    asceticism?: { completed?: boolean };
  };
};

type Props = {
  allDays: CalendarDayView[];
  stats: Record<string, { total: number; completed: number; percentage: number }>;
  goalTracks: CalendarGoalTrackIn[];
  habitTracks: CalendarHabitTrackIn[];
  asceticTracks: CalendarAsceticTrackIn[];
  todayIso: string;
  logging: Record<string, boolean>;
  onGoalStep: (goalId: number, date: string) => void;
  onHabitToggle: (habitId: number, date: string, completed: boolean) => void;
  onPracticeToggle: (date: string) => void;
  onAsceticLog: (asceticismId: string, date: string, completed: boolean) => void;
  onReloadCalendar: () => void;
  goalCountWeek: number;
  goalCountMonth: number;
  /** Открыть мастер создания из query ?create=goal|habit|ascetic */
  urlOpenCreate?: TrackerEntityKind | null;
  onConsumedUrlCreate?: () => void;
  onGoalRename?: (goalId: number, title: string) => void | Promise<void>;
  onGoalComplete?: (goalId: number) => void | Promise<void>;
  onHabitUpdate?: (habitId: number, patch: { name?: string; is_active?: boolean }) => void | Promise<void>;
  heatmapTier?: TrackerTier;
  heatmapMonth: { y: number; m: number };
  onHeatmapMonthChange: (year: number, monthIndex: number) => void;
  /** Тихая подгрузка при смене месяца (без полноэкранного спиннера) */
  calendarRefreshing?: boolean;
};

function dayMarkForGoal(goal: CalendarGoalTrackIn, iso: string): "done" | "miss" {
  return goal.step_dates.includes(iso) ? "done" : "miss";
}

function dayMarkForHabit(h: CalendarHabitTrackIn, iso: string): "done" | "miss" {
  return h.completed_dates.includes(iso) ? "done" : "miss";
}

function dayMarkForAscetic(
  a: CalendarAsceticTrackIn,
  iso: string,
): "done" | "miss" | "warn" {
  const hit = a.entries.find((e) => e.date === iso);
  if (!hit) return "miss";
  return hit.completed ? "done" : "warn";
}

function asceticRowInteractive(a: CalendarAsceticTrackIn): boolean {
  const st = (a.contract_status || "").toLowerCase();
  return !st || st === "active";
}

function EntityDayStrip({
  days,
  todayIsoStr,
  getMark,
  canToggle,
  onToggleDay,
  loggingKey,
  logging,
  formatDayTitle,
}: {
  days: { date: string }[];
  todayIsoStr: string;
  getMark: (iso: string) => "done" | "miss" | "warn";
  canToggle: (iso: string) => boolean;
  onToggleDay?: (iso: string) => void;
  loggingKey?: (iso: string) => string;
  logging: Record<string, boolean>;
  formatDayTitle: (iso: string) => string;
}) {
  return (
    <div style={{ overflowX: "auto", marginTop: "0.45rem", paddingBottom: "4px" }}>
      <div style={{ display: "flex", gap: "0.2rem", minWidth: "min-content", alignItems: "center" }}>
        {days.map((day) => {
          const mark = getMark(day.date);
          const sym = mark === "done" ? "●" : mark === "warn" ? "⚠" : "○";
          const color = mark === "done" ? "#b58b4f" : mark === "warn" ? "#c45c26" : "#c9c2b8";
          const isToday = day.date === todayIsoStr;
          const key = loggingKey ? loggingKey(day.date) : "";
          const busy = key ? !!logging[key] : false;
          const base: CSSProperties = {
            width: "1.38rem",
            height: "1.38rem",
            flexShrink: 0,
            display: "grid",
            placeItems: "center",
            fontSize: mark === "warn" ? "0.82rem" : "0.92rem",
            borderRadius: "6px",
            border: isToday ? "2px solid #c89d62" : "1px solid rgba(201,168,115,0.28)",
            background: isToday ? "rgba(201, 166, 108, 0.12)" : "rgba(255,255,255,0.9)",
            color,
          };
          if (!canToggle(day.date) || !onToggleDay) {
            return (
              <span key={day.date} style={{ ...base, cursor: "default" }} title={formatDayTitle(day.date)}>
                {sym}
              </span>
            );
          }
          return (
            <button
              key={day.date}
              type="button"
              className="flow-lux-day"
              title={formatDayTitle(day.date)}
              disabled={busy}
              onClick={() => onToggleDay(day.date)}
              style={{
                ...base,
                cursor: busy ? "wait" : "pointer",
                opacity: busy ? 0.55 : 1,
              }}
            >
              {busy ? "…" : sym}
            </button>
          );
        })}
      </div>
    </div>
  );
}

function CategoryAccordion({
  title,
  subtitle,
  defaultOpen,
  children,
}: {
  title: string;
  subtitle: string;
  defaultOpen?: boolean;
  children: ReactNode;
}) {
  return (
    <details
      open={defaultOpen}
      className="orbit-card todayflow-panel flow-lux-accordion"
      style={{
        marginBottom: "0.75rem",
        border: "1px solid rgba(198, 166, 119, 0.34)",
        borderRadius: "14px",
        padding: "0.35rem 0.75rem",
        background: "linear-gradient(180deg, rgba(255,255,255,0.97) 0%, rgba(255,248,236,0.92) 100%)",
        transition: "box-shadow 220ms ease, border-color 220ms ease, transform 200ms ease",
      }}
    >
      <summary
        style={{
          cursor: "pointer",
          fontWeight: 700,
          color: "#5f4323",
          padding: "0.45rem 0",
          listStylePosition: "outside",
        }}
      >
        <span style={{ display: "block" }}>
          {title}
          <span className="orbit-body-xs" style={{ display: "block", fontWeight: 500, color: "#8a7760", marginTop: "0.2rem" }}>
            {subtitle}
          </span>
        </span>
      </summary>
      <div style={{ padding: "0.25rem 0 0.65rem" }}>{children}</div>
    </details>
  );
}

export function TrackerView({
  allDays,
  stats,
  goalTracks,
  habitTracks,
  asceticTracks,
  todayIso,
  logging,
  onGoalStep,
  onHabitToggle,
  onPracticeToggle,
  onAsceticLog,
  onReloadCalendar,
  goalCountWeek,
  goalCountMonth,
  urlOpenCreate = null,
  onConsumedUrlCreate,
  onGoalRename,
  onGoalComplete,
  onHabitUpdate,
  heatmapTier = DEFAULT_TRACKER_TIER,
  heatmapMonth,
  onHeatmapMonthChange,
  calendarRefreshing = false,
}: Props) {
  const [wizardOpen, setWizardOpen] = useState(false);
  const [wizardKind, setWizardKind] = useState<TrackerEntityKind | null>(null);
  const openWizard = useCallback((kind?: TrackerEntityKind | null) => {
    setWizardKind(kind ?? null);
    setWizardOpen(true);
  }, []);

  const urlCreateHandled = useRef(false);
  useEffect(() => {
    if (!urlOpenCreate) {
      urlCreateHandled.current = false;
      return;
    }
    if (urlCreateHandled.current) return;
    urlCreateHandled.current = true;
    openWizard(urlOpenCreate);
    onConsumedUrlCreate?.();
  }, [urlOpenCreate, onConsumedUrlCreate, openWizard]);

  const [editingGoalId, setEditingGoalId] = useState<number | null>(null);
  const [goalTitleDraft, setGoalTitleDraft] = useState("");
  const [goalRenameBusy, setGoalRenameBusy] = useState(false);
  const [editingHabitId, setEditingHabitId] = useState<number | null>(null);
  const [habitNameDraft, setHabitNameDraft] = useState("");
  const [habitRenameBusy, setHabitRenameBusy] = useState(false);

  const locale: FlowPracticesChromeLocale = getLocale() === "ru" ? "ru" : "en";
  const fc = flowTrackerChromeBundle(locale);
  const pc = practicesExperienceChromeBundle(locale);
  const formatDay = useCallback((iso: string) => formatIsoShort(iso, locale), [locale]);

  const goalCategoryLine = useCallback(
    (tone: GoalCategoryTone) =>
      ({
        empty: fc.trackingCategoryGoalEmpty,
        mixed: fc.trackingCategoryGoalMixed,
        strong: fc.trackingCategoryGoalStrong,
        weak: fc.trackingCategoryGoalWeak,
        overloaded: fc.trackingCategoryGoalOverloaded,
      })[tone],
    [fc],
  );
  const habitCategoryLine = useCallback(
    (tone: HabitCategoryTone) =>
      ({
        empty: fc.trackingCategoryHabitEmpty,
        strong: fc.trackingCategoryHabitStrong,
        mixed: fc.trackingCategoryHabitMixed,
        weak: fc.trackingCategoryHabitWeak,
      })[tone],
    [fc],
  );
  const asceticCategoryLine = useCallback(
    (tone: AsceticCategoryTone) =>
      ({
        empty: fc.trackingCategoryAsceticEmpty,
        strong: fc.trackingCategoryAsceticStrong,
        mixed: fc.trackingCategoryAsceticMixed,
        weak: fc.trackingCategoryAsceticWeak,
      })[tone],
    [fc],
  );
  const practiceCategoryLine = useCallback(
    (tone: PracticeCategoryTone) =>
      ({
        empty: fc.trackingCategoryPracticeEmpty,
        active: fc.trackingCategoryPracticeActive,
        ignored: fc.trackingCategoryPracticeIgnored,
        neutral: fc.trackingCategoryPracticeNeutral,
      })[tone],
    [fc],
  );

  const goalEntityStatusLabel = useCallback(
    (st: string) => {
      const m: Record<string, string> = {
        active_progress: fc.trackingStatusGoalActiveProgress,
        unstable: fc.trackingStatusGoalUnstable,
        stalled: fc.trackingStatusGoalStalled,
        completed: fc.trackingStatusGoalCompleted,
      };
      return m[st] ?? st;
    },
    [fc],
  );
  const habitEntityStatusLabel = useCallback(
    (st: string) => {
      const m: Record<string, string> = {
        active: fc.trackingStatusHabitActive,
        unstable: fc.trackingStatusHabitUnstable,
        dropped: fc.trackingStatusHabitDropped,
      };
      return m[st] ?? st;
    },
    [fc],
  );
  const asceticEntityStatusLabel = useCallback(
    (st: string) => {
      const m: Record<string, string> = {
        holding: fc.trackingStatusAsceticHolding,
        breaks: fc.trackingStatusAsceticBreaks,
        failed: fc.trackingStatusAsceticFailed,
        stopped: fc.trackingStatusAsceticStopped,
      };
      return m[st] ?? st;
    },
    [fc],
  );

  const days30 = sliceLastNDaysSorted(allDays, 30, todayIso);
  const dayObjs = days30.map((d) => ({ date: d.date }));

  const prPct = Math.round(stats.practice?.percentage ?? 0);
  const heroKind = computeScreenHero(goalTracks, habitTracks, asceticTracks, prPct, todayIso);
  const hero = useMemo(() => {
    const table: Record<ScreenHeroKind, { title: string; sub: string }> = {
      empty: { title: fc.trackingScreenHeroEmptyTitle, sub: fc.trackingScreenHeroEmptySub },
      in_flow: { title: fc.trackingScreenHeroInFlowTitle, sub: fc.trackingScreenHeroInFlowSub },
      unstable: { title: fc.trackingScreenHeroUnstableTitle, sub: fc.trackingScreenHeroUnstableSub },
      dropped: { title: fc.trackingScreenHeroDroppedTitle, sub: fc.trackingScreenHeroDroppedSub },
      overloaded: { title: fc.trackingScreenHeroOverloadedTitle, sub: fc.trackingScreenHeroOverloadedSub },
    };
    return table[heroKind];
  }, [fc, heroKind]);
  const cat = categorySummaryLines(goalTracks, habitTracks, asceticTracks, prPct, todayIso, fc);
  const attention = buildAttentionItems(goalTracks, habitTracks, asceticTracks, todayIso, fc, 3);
  const best = buildBestItems(goalTracks, habitTracks, asceticTracks, todayIso, fc, 2);
  const overloadCount = countActiveTracks(goalTracks, habitTracks, asceticTracks);
  const softLimit =
    goalTracks.filter((g) => !g.completed).length > FREE_LIMITS.goals ||
    habitTracks.filter((h) => h.is_active).length > FREE_LIMITS.habits ||
    asceticTracks.filter((a) => {
      const st = (a.contract_status || "").toLowerCase();
      return st !== "paused" && st !== "completed";
    }).length > FREE_LIMITS.ascetics;

  const practiceMarks = computeMarks(days30, "practice" as LineId);
  const todayRow = allDays.find((d) => d.date === todayIso);
  const practiceTodayDone = todayRow ? lineDone(todayRow, "practice") : false;

  const [markOpen, setMarkOpen] = useState(false);
  const [markSaved, setMarkSaved] = useState(false);

  return (
    <>
      <style jsx>{`
        @media (hover: hover) and (pointer: fine) {
          :global(.flow-lux-hero:hover) {
            box-shadow: 0 18px 48px rgba(110, 80, 45, 0.12) !important;
          }
          :global(.flow-lux-stat:hover) {
            transform: translateY(-1px);
            box-shadow: 0 10px 26px rgba(95, 70, 40, 0.08);
          }
          :global(.flow-lux-pill:hover:not(:disabled)) {
            filter: brightness(1.03);
            transform: translateY(-0.5px);
          }
          :global(.flow-lux-link:hover) {
            filter: brightness(1.04);
            transform: translateY(-0.5px);
          }
          :global(.flow-lux-accordion:hover) {
            box-shadow: 0 12px 32px rgba(100, 75, 40, 0.08);
          }
        }
        :global(.flow-lux-hero) {
          transition: box-shadow 240ms ease, transform 200ms ease;
        }
        :global(.flow-lux-stat) {
          transition: transform 200ms ease, box-shadow 220ms ease, border-color 200ms ease;
        }
        :global(.flow-lux-pill) {
          transition: transform 160ms ease, filter 200ms ease, box-shadow 200ms ease, opacity 200ms ease;
          box-shadow: 0 6px 16px rgba(100, 70, 40, 0.12);
        }
        :global(.flow-lux-pill.flow-lux-pill--ghost) {
          box-shadow: 0 4px 12px rgba(90, 70, 45, 0.06);
        }
        :global(.flow-lux-link) {
          transition: transform 160ms ease, filter 200ms ease, box-shadow 200ms ease;
          box-shadow: 0 6px 18px rgba(100, 70, 40, 0.12);
        }
        :global(.flow-lux-day) {
          transition: transform 140ms ease, border-color 200ms ease, background 200ms ease, opacity 200ms ease;
        }
        @media (hover: hover) and (pointer: fine) {
          :global(.flow-lux-day:hover:not(:disabled)) {
            transform: scale(1.05);
          }
        }
      `}</style>
      <div
        className="orbit-card todayflow-panel flow-lux-hero"
        style={{
          marginBottom: "1rem",
          padding: "1.2rem 1.3rem",
          borderRadius: "18px",
          border: "1px solid rgba(198, 166, 119, 0.42)",
          background: "linear-gradient(155deg, rgba(255,252,246,0.99) 0%, rgba(255,236,210,0.88) 100%)",
          boxShadow: "0 12px 36px rgba(120, 90, 50, 0.08)",
        }}
      >
        <p className="orbit-body-xs" style={{ margin: "0 0 0.42rem", color: "#8f6e43", textTransform: "uppercase", letterSpacing: "0.08em", fontWeight: 700 }}>
          {fc.trackingViewFlowTodayEyebrow}
        </p>
        <h2 className="orbit-display-xs" style={{ margin: 0, color: "#5f4323" }}>
          {hero.title}
        </h2>
        <p className="orbit-body-sm" style={{ margin: "0.55rem 0 0", color: "#5c4a32", lineHeight: 1.55 }}>
          {hero.sub}
        </p>
        {overloadCount > 7 ? (
          <p className="orbit-body-xs" style={{ margin: "0.55rem 0 0", color: "#a65c2e", fontWeight: 600 }}>
            {fc.trackingViewLimitsHint}
          </p>
        ) : null}
        {softLimit && overloadCount <= 7 ? (
          <p className="orbit-body-xs" style={{ margin: "0.45rem 0 0", color: "#8a7760", lineHeight: 1.45 }}>
            {templateReplace(fc.trackingViewFreeSoftLimitHint, {
              goals: FREE_LIMITS.goals,
              habits: FREE_LIMITS.habits,
              ascetics: FREE_LIMITS.ascetics,
            })}
          </p>
        ) : null}
      </div>

      <div
        className="orbit-card todayflow-panel"
        style={{
          marginBottom: "1rem",
          padding: "0.9rem 1rem",
          borderRadius: "16px",
          border: "1px solid rgba(198, 166, 119, 0.38)",
          background: "linear-gradient(165deg, rgba(255,252,248,0.99) 0%, rgba(255,244,228,0.9) 100%)",
          boxShadow: "0 8px 28px rgba(100, 75, 42, 0.06)",
        }}
      >
        <p className="orbit-body-sm" style={{ margin: 0, color: "#5f4323", fontWeight: 700 }}>
          {fc.trackingViewAddToTrackerTitle}
        </p>
        <p className="orbit-body-xs" style={{ margin: "0.4rem 0 0.65rem", color: "#7a6242", lineHeight: 1.45 }}>
          {fc.trackingViewAddToTrackerBody}
        </p>
        <div style={{ display: "flex", flexWrap: "wrap", gap: "0.45rem" }}>
          <button
            type="button"
            className="flow-lux-pill"
            onClick={() => openWizard("goal")}
            style={{
              padding: "0.42rem 0.85rem",
              borderRadius: "10px",
              border: "1px solid rgba(155, 118, 70, 0.55)",
              background: "linear-gradient(120deg,#d3b178,#bf975f)",
              color: "#fff8ee",
              fontWeight: 700,
              fontSize: "0.82rem",
              cursor: "pointer",
            }}
          >
            {fc.trackingViewAddGoalCta}
          </button>
          <button
            type="button"
            className="flow-lux-pill"
            onClick={() => openWizard("habit")}
            style={{
              padding: "0.42rem 0.85rem",
              borderRadius: "10px",
              border: "1px solid rgba(155, 118, 70, 0.55)",
              background: "linear-gradient(120deg,#d3b178,#bf975f)",
              color: "#fff8ee",
              fontWeight: 700,
              fontSize: "0.82rem",
              cursor: "pointer",
            }}
          >
            {fc.trackingViewAddHabitCta}
          </button>
          <button
            type="button"
            className="flow-lux-pill"
            onClick={() => openWizard("ascetic")}
            style={{
              padding: "0.42rem 0.85rem",
              borderRadius: "10px",
              border: "1px solid rgba(155, 118, 70, 0.55)",
              background: "linear-gradient(120deg,#d3b178,#bf975f)",
              color: "#fff8ee",
              fontWeight: 700,
              fontSize: "0.82rem",
              cursor: "pointer",
            }}
          >
            {fc.trackingViewAddAsceticCta}
          </button>
          <button
            type="button"
            className="flow-lux-pill flow-lux-pill--ghost"
            onClick={() => openWizard(null)}
            style={{
              padding: "0.42rem 0.85rem",
              borderRadius: "10px",
              border: "1px solid rgba(195, 154, 92, 0.45)",
              background: "rgba(255,250,242,0.95)",
              color: "#6d4f29",
              fontWeight: 600,
              fontSize: "0.82rem",
              cursor: "pointer",
            }}
          >
            {fc.trackingViewWizardFromTypeStep}
          </button>
        </div>
      </div>

      <CalendarHeatmap
        todayIso={todayIso}
        viewYear={heatmapMonth.y}
        viewMonthIndex={heatmapMonth.m}
        onViewMonthChange={onHeatmapMonthChange}
        days={allDays}
        goalTracks={goalTracks}
        habitTracks={habitTracks}
        asceticTracks={asceticTracks}
        tier={heatmapTier}
        isRefreshing={calendarRefreshing}
      />

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(148px, 1fr))",
          gap: "0.6rem",
          marginBottom: "1rem",
        }}
      >
        {(
          [
            [fc.goalsNavTitle, cat.goals.headline, goalCategoryLine(cat.goals.tone)],
            [fc.habitsTitle, cat.habits.headline, habitCategoryLine(cat.habits.tone)],
            [fc.asceticsTitle, cat.ascetics.headline, asceticCategoryLine(cat.ascetics.tone)],
            [pc.navPractices, cat.practices.headline, practiceCategoryLine(cat.practices.tone)],
          ] as const
        ).map(([title, head, cap]) => (
          <div
            key={title}
            className="flow-lux-stat"
            style={{
              padding: "0.72rem 0.8rem",
              borderRadius: "12px",
              border: "1px solid rgba(201, 168, 115, 0.35)",
              background: "rgba(255,255,255,0.92)",
            }}
          >
            <p className="orbit-body-xs" style={{ margin: 0, color: "#8a6f49", fontWeight: 700 }}>
              {title}
            </p>
            <p className="orbit-body-sm" style={{ margin: "0.22rem 0 0", color: "#5f4323", fontWeight: 600, lineHeight: 1.35 }}>
              {head}
            </p>
            <p className="orbit-body-xs" style={{ margin: "0.2rem 0 0", color: "#8a7760", lineHeight: 1.35 }}>
              {cap}
            </p>
          </div>
        ))}
      </div>

      {attention.length > 0 ? (
        <div
          className="orbit-card todayflow-panel"
          style={{
            marginBottom: "1rem",
            padding: "0.85rem 1rem",
            borderRadius: "14px",
            border: "1px solid rgba(196, 92, 38, 0.35)",
            background: "rgba(255, 248, 242, 0.95)",
          }}
        >
          <p className="orbit-body-xs" style={{ margin: "0 0 0.45rem", color: "#a65c2e", fontWeight: 700, textTransform: "uppercase" }}>
            {fc.trackingViewAttentionSectionTitle}
          </p>
          <ul style={{ margin: 0, paddingLeft: "1.1rem", color: "#5f4323", lineHeight: 1.55 }}>
            {attention.map((a) => (
              <li key={`${a.kind}-${a.id}`} className="orbit-body-sm">
                <strong>
                  {a.kind === "goal" ? fc.goalSheetTitle : a.kind === "habit" ? fc.habitSheetTitle : fc.asceticNavTitle}
                </strong>{" "}
                «{a.name}» — {a.line}
              </li>
            ))}
          </ul>
        </div>
      ) : null}

      {best.length > 0 ? (
        <div
          className="orbit-card todayflow-panel"
          style={{
            marginBottom: "1rem",
            padding: "0.85rem 1rem",
            borderRadius: "14px",
            border: "1px solid rgba(90, 122, 78, 0.35)",
            background: "rgba(248, 255, 248, 0.9)",
          }}
        >
          <p className="orbit-body-xs" style={{ margin: "0 0 0.45rem", color: "#5a7a4e", fontWeight: 700, textTransform: "uppercase" }}>
            {fc.trackingViewBestSectionTitle}
          </p>
          <ul style={{ margin: 0, paddingLeft: "1.1rem", color: "#5f4323", lineHeight: 1.55 }}>
            {best.map((b) => (
              <li key={`${b.kind}-${b.id}`} className="orbit-body-sm">
                <strong>
                  {b.kind === "goal" ? fc.goalSheetTitle : b.kind === "habit" ? fc.habitSheetTitle : fc.asceticNavTitle}
                </strong>{" "}
                «{b.name}» — {b.line}
              </li>
            ))}
          </ul>
        </div>
      ) : null}

      <div
        className="orbit-card todayflow-panel"
        style={{
          marginBottom: "1rem",
          padding: "0.85rem 1rem",
          borderRadius: "14px",
          border: "1px solid rgba(184, 134, 11, 0.28)",
          background: "rgba(255, 250, 242, 0.96)",
        }}
      >
        <div style={{ display: "flex", flexWrap: "wrap", alignItems: "center", justifyContent: "space-between", gap: "0.65rem" }}>
          <p className="orbit-body-sm" style={{ margin: 0, color: "#5f4323", maxWidth: "32rem", lineHeight: 1.5 }}>
            {fc.trackingViewTodayLinkHint}
          </p>
          <Link
            href="/today"
            className="flow-lux-link"
            style={{
              padding: "0.45rem 0.95rem",
              borderRadius: "10px",
              background: "linear-gradient(120deg,#d3b178,#bf975f)",
              color: "#fff8ee",
              fontWeight: 600,
              textDecoration: "none",
              fontSize: "0.88rem",
            }}
          >
            {fc.trackingViewOpenTodayLink}
          </Link>
        </div>
      </div>

      <p className="orbit-body-xs" style={{ margin: "0 0 0.5rem", color: "#8a7760" }}>
        {fc.trackingViewLast30DaysLegend}
      </p>

      <CategoryAccordion title={fc.goalsNavTitle} subtitle={cat.goals.headline + " · " + goalCategoryLine(cat.goals.tone)} defaultOpen>
        {!goalTracks.length ? (
          <p className="orbit-body-sm" style={{ color: "#7a6242" }}>
            {fc.trackingViewEmptyGoalsLead}{" "}
            <button
              type="button"
              onClick={() => openWizard("goal")}
              style={{ border: "none", background: "none", padding: 0, color: "#8a6332", fontWeight: 700, cursor: "pointer", textDecoration: "underline" }}
            >
              {fc.trackingViewCreateHereCta}
            </button>
            .
          </p>
        ) : (
          goalTracks.map((g) => {
            const st = computeGoalEntityStatus(g, todayIso);
            return (
              <div
                key={g.id}
                style={{
                  marginBottom: "0.85rem",
                  paddingBottom: "0.85rem",
                  borderBottom: "1px solid rgba(201, 168, 115, 0.22)",
                }}
              >
                <div style={{ display: "flex", flexWrap: "wrap", justifyContent: "space-between", gap: "0.35rem", alignItems: "baseline" }}>
                  {editingGoalId === g.id ? (
                    <div style={{ flex: "1 1 220px", display: "grid", gap: "0.35rem" }}>
                      <input
                        value={goalTitleDraft}
                        onChange={(e) => setGoalTitleDraft(e.target.value)}
                        className="orbit-body-sm"
                        style={{
                          width: "100%",
                          padding: "0.35rem 0.5rem",
                          borderRadius: "8px",
                          border: "1px solid rgba(195, 154, 92, 0.45)",
                          color: "#5f4323",
                          background: "#fffdf9",
                        }}
                        aria-label={fc.trackingViewGoalNameAriaLabel}
                      />
                      <div style={{ display: "flex", flexWrap: "wrap", gap: "0.35rem" }}>
                        <button
                          type="button"
                          disabled={goalRenameBusy || !goalTitleDraft.trim()}
                          onClick={async () => {
                            if (!onGoalRename) return;
                            setGoalRenameBusy(true);
                            try {
                              await onGoalRename(g.id, goalTitleDraft);
                              setEditingGoalId(null);
                            } finally {
                              setGoalRenameBusy(false);
                            }
                          }}
                          style={{
                            padding: "0.3rem 0.55rem",
                            borderRadius: "8px",
                            border: "1px solid rgba(155, 118, 70, 0.55)",
                            background: "linear-gradient(120deg,#d3b178,#bf975f)",
                            color: "#fff8ee",
                            fontWeight: 600,
                            fontSize: "0.78rem",
                            cursor: goalRenameBusy ? "wait" : "pointer",
                            opacity: goalRenameBusy ? 0.7 : 1,
                          }}
                        >
                          {goalRenameBusy ? "…" : fc.actionSave}
                        </button>
                        <button
                          type="button"
                          disabled={goalRenameBusy}
                          onClick={() => setEditingGoalId(null)}
                          style={{
                            padding: "0.3rem 0.55rem",
                            borderRadius: "8px",
                            border: "1px solid rgba(195, 154, 92, 0.45)",
                            background: "transparent",
                            color: "#6d4f29",
                            fontWeight: 600,
                            fontSize: "0.78rem",
                            cursor: "pointer",
                          }}
                        >
                          {fc.actionCancel}
                        </button>
                      </div>
                    </div>
                  ) : (
                    <p className="orbit-body-sm" style={{ margin: 0, fontWeight: 700, color: "#5f4323" }}>
                      {g.title}
                    </p>
                  )}
                  <span className="orbit-body-xs" style={{ color: "#8a7760" }}>
                    {fc.trackingViewGoalStatusPrefix} {goalEntityStatusLabel(st)}
                    {g.completed ? fc.trackingViewGoalCompletedSuffix : ""}
                    {!g.completed && editingGoalId !== g.id && onGoalRename ? (
                      <>
                        {" · "}
                        <button
                          type="button"
                          onClick={() => {
                            setEditingGoalId(g.id);
                            setGoalTitleDraft(g.title);
                          }}
                          style={{ border: "none", background: "none", padding: 0, color: "#8a6332", fontWeight: 700, cursor: "pointer", textDecoration: "underline" }}
                        >
                          {fc.trackingViewRenameTitleLink}
                        </button>
                      </>
                    ) : null}
                    {!g.completed && editingGoalId !== g.id && onGoalComplete ? (
                      <>
                        {" · "}
                        <button
                          type="button"
                          onClick={() => {
                            if (
                              typeof window !== "undefined" &&
                              !window.confirm(fc.trackingViewCompleteGoalConfirm)
                            ) {
                              return;
                            }
                            void onGoalComplete(g.id);
                          }}
                          style={{ border: "none", background: "none", padding: 0, color: "#8a6332", fontWeight: 700, cursor: "pointer", textDecoration: "underline" }}
                        >
                          {fc.completeGoal}
                        </button>
                      </>
                    ) : null}
                  </span>
                </div>
                <EntityDayStrip
                  days={dayObjs}
                  todayIsoStr={todayIso}
                  getMark={(iso) => dayMarkForGoal(g, iso)}
                  canToggle={(iso) => !g.completed && editingGoalId !== g.id}
                  logging={logging}
                  formatDayTitle={formatDay}
                  loggingKey={(iso) => `goal-${g.id}-${iso}`}
                  onToggleDay={
                    g.completed
                      ? undefined
                      : (iso) => {
                          if (dayMarkForGoal(g, iso) === "done") return;
                          onGoalStep(g.id, iso);
                        }
                  }
                />
              </div>
            );
          })
        )}
      </CategoryAccordion>

      <CategoryAccordion title={fc.habitsTitle} subtitle={cat.habits.headline + " · " + habitCategoryLine(cat.habits.tone)}>
        {!habitTracks.length ? (
          <p className="orbit-body-sm" style={{ color: "#7a6242" }}>
            {fc.trackingViewEmptyHabitsLead}{" "}
            <button
              type="button"
              onClick={() => openWizard("habit")}
              style={{ border: "none", background: "none", padding: 0, color: "#8a6332", fontWeight: 700, cursor: "pointer", textDecoration: "underline" }}
            >
              {fc.trackingViewCreateHereCta}
            </button>
            .
          </p>
        ) : (
          habitTracks.map((h) => {
            const st = computeHabitEntityStatus(h, todayIso);
            return (
              <div
                key={h.id}
                style={{
                  marginBottom: "0.85rem",
                  paddingBottom: "0.85rem",
                  borderBottom: "1px solid rgba(201, 168, 115, 0.22)",
                }}
              >
                <div style={{ display: "flex", flexWrap: "wrap", justifyContent: "space-between", gap: "0.35rem", alignItems: "baseline" }}>
                  {editingHabitId === h.id ? (
                    <div style={{ flex: "1 1 220px", display: "grid", gap: "0.35rem" }}>
                      <input
                        value={habitNameDraft}
                        onChange={(e) => setHabitNameDraft(e.target.value)}
                        className="orbit-body-sm"
                        style={{
                          width: "100%",
                          padding: "0.35rem 0.5rem",
                          borderRadius: "8px",
                          border: "1px solid rgba(195, 154, 92, 0.45)",
                          color: "#5f4323",
                          background: "#fffdf9",
                        }}
                        aria-label={fc.trackingViewHabitNameAriaLabel}
                      />
                      <div style={{ display: "flex", flexWrap: "wrap", gap: "0.35rem" }}>
                        <button
                          type="button"
                          disabled={habitRenameBusy || !habitNameDraft.trim()}
                          onClick={async () => {
                            if (!onHabitUpdate) return;
                            setHabitRenameBusy(true);
                            try {
                              await onHabitUpdate(h.id, { name: habitNameDraft.trim() });
                              setEditingHabitId(null);
                            } finally {
                              setHabitRenameBusy(false);
                            }
                          }}
                          style={{
                            padding: "0.3rem 0.55rem",
                            borderRadius: "8px",
                            border: "1px solid rgba(155, 118, 70, 0.55)",
                            background: "linear-gradient(120deg,#d3b178,#bf975f)",
                            color: "#fff8ee",
                            fontWeight: 600,
                            fontSize: "0.78rem",
                            cursor: habitRenameBusy ? "wait" : "pointer",
                            opacity: habitRenameBusy ? 0.7 : 1,
                          }}
                        >
                          {habitRenameBusy ? "…" : fc.actionSave}
                        </button>
                        <button
                          type="button"
                          disabled={habitRenameBusy}
                          onClick={() => setEditingHabitId(null)}
                          style={{
                            padding: "0.3rem 0.55rem",
                            borderRadius: "8px",
                            border: "1px solid rgba(195, 154, 92, 0.45)",
                            background: "transparent",
                            color: "#6d4f29",
                            fontWeight: 600,
                            fontSize: "0.78rem",
                            cursor: "pointer",
                          }}
                        >
                          {fc.actionCancel}
                        </button>
                      </div>
                    </div>
                  ) : (
                    <p className="orbit-body-sm" style={{ margin: 0, fontWeight: 700, color: "#5f4323" }}>
                      {h.name}
                      {!h.is_active ? (
                        <span className="orbit-body-xs" style={{ color: "#a09078", fontWeight: 500 }}>
                          {" "}
                          {fc.trackingViewHabitPausedSuffix}
                        </span>
                      ) : null}
                    </p>
                  )}
                  <span className="orbit-body-xs" style={{ color: "#8a7760", textAlign: "right" }}>
                    {habitEntityStatusLabel(st)}
                    {onHabitUpdate && editingHabitId !== h.id ? (
                      <>
                        {" · "}
                        <button
                          type="button"
                          onClick={() => {
                            setEditingHabitId(h.id);
                            setHabitNameDraft(h.name);
                          }}
                          style={{ border: "none", background: "none", padding: 0, color: "#8a6332", fontWeight: 700, cursor: "pointer", textDecoration: "underline" }}
                        >
                          {fc.trackingViewRenameTitleLink}
                        </button>
                        {" · "}
                        <button
                          type="button"
                          onClick={() => void onHabitUpdate(h.id, { is_active: !h.is_active })}
                          style={{ border: "none", background: "none", padding: 0, color: "#8a6332", fontWeight: 700, cursor: "pointer", textDecoration: "underline" }}
                        >
                          {h.is_active ? fc.trackingViewHabitPauseCta : fc.trackingViewHabitResumeCta}
                        </button>
                      </>
                    ) : null}
                  </span>
                </div>
                <EntityDayStrip
                  days={dayObjs}
                  todayIsoStr={todayIso}
                  getMark={(iso) => dayMarkForHabit(h, iso)}
                  canToggle={() => h.is_active && editingHabitId !== h.id}
                  logging={logging}
                  formatDayTitle={formatDay}
                  loggingKey={(iso) => `habit-${h.id}-${iso}`}
                  onToggleDay={
                    h.is_active && editingHabitId !== h.id
                      ? (iso) => {
                          const done = dayMarkForHabit(h, iso) === "done";
                          onHabitToggle(h.id, iso, !done);
                        }
                      : undefined
                  }
                />
              </div>
            );
          })
        )}
      </CategoryAccordion>

      <CategoryAccordion title={fc.asceticsTitle} subtitle={cat.ascetics.headline + " · " + asceticCategoryLine(cat.ascetics.tone)}>
        {!asceticTracks.length ? (
          <p className="orbit-body-sm" style={{ color: "#7a6242" }}>
            {fc.trackingViewEmptyAsceticsLead}{" "}
            <button
              type="button"
              onClick={() => openWizard("ascetic")}
              style={{ border: "none", background: "none", padding: 0, color: "#8a6332", fontWeight: 700, cursor: "pointer", textDecoration: "underline" }}
            >
              {fc.trackingViewContractHereCta}
            </button>
            .
          </p>
        ) : (
          asceticTracks.map((a) => {
            const st = computeAsceticEntityStatus(a, todayIso);
            return (
              <div
                key={a.asceticism_id}
                style={{
                  marginBottom: "0.85rem",
                  paddingBottom: "0.85rem",
                  borderBottom: "1px solid rgba(201, 168, 115, 0.22)",
                }}
              >
                <div style={{ display: "flex", flexWrap: "wrap", justifyContent: "space-between", gap: "0.35rem", alignItems: "baseline" }}>
                  <p className="orbit-body-sm" style={{ margin: 0, fontWeight: 700, color: "#5f4323" }}>
                    {a.title || a.asceticism_id}
                  </p>
                  <span className="orbit-body-xs" style={{ color: "#8a7760" }}>
                    {asceticEntityStatusLabel(st)}
                    {asceticRowInteractive(a) ? (
                      <span style={{ marginLeft: "0.35rem", color: "#8a7760" }}>{fc.trackingViewAsceticsHintTapDays}</span>
                    ) : null}
                  </span>
                </div>
                <EntityDayStrip
                  days={dayObjs}
                  todayIsoStr={todayIso}
                  getMark={(iso) => dayMarkForAscetic(a, iso)}
                  canToggle={(iso) => asceticRowInteractive(a) && iso <= todayIso}
                  logging={logging}
                  formatDayTitle={formatDay}
                  loggingKey={(iso) => `ascetic-${a.asceticism_id}-${iso}`}
                  onToggleDay={
                    asceticRowInteractive(a)
                      ? (iso) => {
                          const mark = dayMarkForAscetic(a, iso);
                          onAsceticLog(a.asceticism_id, iso, mark !== "done");
                        }
                      : undefined
                  }
                />
              </div>
            );
          })
        )}
      </CategoryAccordion>

      <CategoryAccordion title={pc.navPractices} subtitle={cat.practices.headline + " · " + practiceCategoryLine(cat.practices.tone)}>
        <p className="orbit-body-xs" style={{ margin: "0 0 0.5rem", color: "#7a6242", lineHeight: 1.45 }}>
          {fc.trackingViewPracticeAggregatedIntro}
        </p>
        <div style={{ display: "flex", flexWrap: "wrap", alignItems: "center", gap: "0.5rem" }}>
          <span className="orbit-body-sm" style={{ fontWeight: 700, color: "#5f4323" }}>
            {pc.navPractices}
          </span>
        </div>
        <EntityDayStrip
          days={dayObjs}
          todayIsoStr={todayIso}
          getMark={(iso) => {
            const i = days30.findIndex((d) => d.date === iso);
            const m = i >= 0 ? practiceMarks[i] : "miss";
            return m === "done" ? "done" : m === "warn" ? "warn" : "miss";
          }}
          canToggle={(iso) => {
            const d = days30.find((x) => x.date === iso);
            return d ? !lineDone(d, "practice") : true;
          }}
          logging={logging}
          formatDayTitle={formatDay}
          loggingKey={(iso) => `practice-${iso}`}
          onToggleDay={(iso) => onPracticeToggle(iso)}
        />
        <p className="orbit-body-xs" style={{ margin: "0.35rem 0 0", color: "#8a7760" }}>
          {fc.trackingViewPracticeAggregatedFootnote}
        </p>
      </CategoryAccordion>

      <MarkTodayModal
        open={markOpen}
        onClose={() => setMarkOpen(false)}
        flowChrome={fc}
        formatDayLabel={formatDay}
        todayIso={todayIso}
        practiceTodayDone={practiceTodayDone}
        goalTracks={goalTracks}
        habitTracks={habitTracks}
        asceticTracks={asceticTracks}
        logging={logging}
        onGoalStep={onGoalStep}
        onHabitToggle={onHabitToggle}
        onPracticeToggle={onPracticeToggle}
        onAsceticLog={onAsceticLog}
        onOpenCreateWizard={(k) => {
          setMarkOpen(false);
          openWizard(k ?? null);
        }}
        onSaved={() => {
          setMarkSaved(true);
          setTimeout(() => setMarkSaved(false), 2500);
        }}
      />

      <EntityCreateWizard
        open={wizardOpen}
        onClose={() => {
          setWizardOpen(false);
          setWizardKind(null);
        }}
        todayIso={todayIso}
        onCreated={() => void onReloadCalendar()}
        goalCountWeek={goalCountWeek}
        goalCountMonth={goalCountMonth}
        initialKind={wizardKind ?? undefined}
      />

      <button
        type="button"
        onClick={() => setMarkOpen(true)}
        style={{
          position: "fixed",
          bottom: "max(1.25rem, env(safe-area-inset-bottom))",
          right: "max(1.25rem, env(safe-area-inset-right))",
          zIndex: 50,
          padding: "0.75rem 1.2rem",
          borderRadius: "999px",
          border: "1px solid rgba(155, 120, 70, 0.55)",
          background: "linear-gradient(120deg,#d3b178,#bf975f)",
          color: "#fff8ee",
          fontWeight: 700,
          fontSize: "0.95rem",
          cursor: "pointer",
          boxShadow: "0 8px 28px rgba(120, 90, 45, 0.28)",
        }}
      >
        {heroKind === "empty" ? fc.trackingMarkTodayFabEmpty : markSaved ? fc.trackingMarkTodayAfterSave : fc.trackingMarkTodayFab}
      </button>

      <div style={{ height: "5rem" }} aria-hidden />
    </>
  );
}

function MarkTodayModal({
  open,
  onClose,
  flowChrome,
  formatDayLabel,
  todayIso,
  practiceTodayDone,
  goalTracks,
  habitTracks,
  asceticTracks,
  logging,
  onGoalStep,
  onHabitToggle,
  onPracticeToggle,
  onAsceticLog,
  onOpenCreateWizard,
  onSaved,
}: {
  open: boolean;
  onClose: () => void;
  flowChrome: FlowTrackerChromeBundle;
  formatDayLabel: (iso: string) => string;
  todayIso: string;
  practiceTodayDone: boolean;
  goalTracks: CalendarGoalTrackIn[];
  habitTracks: CalendarHabitTrackIn[];
  asceticTracks: CalendarAsceticTrackIn[];
  logging: Record<string, boolean>;
  onGoalStep: (goalId: number, date: string) => void;
  onHabitToggle: (habitId: number, date: string, completed: boolean) => void;
  onPracticeToggle: (date: string) => void;
  onAsceticLog: (asceticismId: string, date: string, completed: boolean) => void;
  onOpenCreateWizard: (kind?: TrackerEntityKind | null) => void;
  onSaved: () => void;
}) {
  if (!open) return null;

  return (
    <div
      role="dialog"
      aria-modal
      style={{
        position: "fixed",
        inset: 0,
        zIndex: 60,
        background: "rgba(40, 32, 24, 0.45)",
        display: "grid",
        placeItems: "center",
        padding: "1rem",
      }}
      onClick={onClose}
    >
      <div
        className="orbit-card"
        style={{
          maxWidth: "420px",
          width: "100%",
          maxHeight: "90vh",
          overflowY: "auto",
          padding: "1.15rem 1.25rem",
          borderRadius: "16px",
          background: "#fffdf9",
          border: "1px solid rgba(198, 166, 119, 0.4)",
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <h3 className="orbit-body" style={{ margin: "0 0 0.5rem", color: "#5f4323" }}>
          {flowChrome.trackingMarkTodayModalTitle}
        </h3>
        <p className="orbit-body-sm" style={{ margin: "0 0 1rem", color: "#7a6242" }}>
          {formatDayLabel(todayIso)} {flowChrome.trackingViewMarkTodayPromptAfterDate}
        </p>

        <p className="orbit-body-xs" style={{ margin: "0 0 0.35rem", fontWeight: 700, color: "#8a6f49" }}>
          {flowChrome.goalsNavTitle}
        </p>
        <ul style={{ margin: "0 0 0.75rem", padding: 0, listStyle: "none" }}>
          {goalTracks.filter((g) => !g.completed).length === 0 ? (
            <li className="orbit-body-sm" style={{ color: "#8a7760" }}>
              {flowChrome.trackingViewNoActiveItemsLead}{" "}
              <button
                type="button"
                onClick={() => onOpenCreateWizard("goal")}
                style={{ border: "none", background: "none", padding: 0, color: "#8a6332", fontWeight: 700, cursor: "pointer", textDecoration: "underline" }}
              >
                {flowChrome.trackingViewCreateGoalCta}
              </button>
            </li>
          ) : (
            goalTracks
              .filter((g) => !g.completed)
              .map((g) => {
                const done = g.step_dates.includes(todayIso);
                const key = `goal-${g.id}-${todayIso}`;
                return (
                  <li key={g.id} style={{ marginBottom: "0.45rem" }}>
                    <label style={{ display: "flex", alignItems: "center", gap: "0.5rem", cursor: logging[key] ? "wait" : "pointer" }}>
                      <input
                        type="checkbox"
                        checked={done}
                        disabled={logging[key] || done}
                        onChange={() => {
                          if (!done) {
                            onGoalStep(g.id, todayIso);
                            onSaved();
                          }
                        }}
                      />
                      <span style={{ color: "#5f4323" }}>{g.title}</span>
                    </label>
                  </li>
                );
              })
          )}
        </ul>

        <p className="orbit-body-xs" style={{ margin: "0 0 0.35rem", fontWeight: 700, color: "#8a6f49" }}>
          {flowChrome.habitsTitle}
        </p>
        <ul style={{ margin: "0 0 0.75rem", padding: 0, listStyle: "none" }}>
          {habitTracks.filter((h) => h.is_active).length === 0 ? (
            <li className="orbit-body-sm" style={{ color: "#8a7760" }}>
              {flowChrome.trackingViewNoActiveItemsLead}{" "}
              <button
                type="button"
                onClick={() => onOpenCreateWizard("habit")}
                style={{ border: "none", background: "none", padding: 0, color: "#8a6332", fontWeight: 700, cursor: "pointer", textDecoration: "underline" }}
              >
                {flowChrome.trackingViewCreateHabitCta}
              </button>
            </li>
          ) : (
            habitTracks
              .filter((h) => h.is_active)
              .map((h) => {
                const done = h.completed_dates.includes(todayIso);
                const key = `habit-${h.id}-${todayIso}`;
                return (
                  <li key={h.id} style={{ marginBottom: "0.45rem" }}>
                    <label style={{ display: "flex", alignItems: "center", gap: "0.5rem", cursor: logging[key] ? "wait" : "pointer" }}>
                      <input
                        type="checkbox"
                        checked={done}
                        disabled={logging[key]}
                        onChange={() => {
                          onHabitToggle(h.id, todayIso, !done);
                          onSaved();
                        }}
                      />
                      <span style={{ color: "#5f4323" }}>{h.name}</span>
                    </label>
                  </li>
                );
              })
          )}
        </ul>

        <p className="orbit-body-xs" style={{ margin: "0 0 0.35rem", fontWeight: 700, color: "#8a6f49" }}>
          {flowChrome.practiceTitle}
        </p>
        <ul style={{ margin: "0 0 0.75rem", padding: 0, listStyle: "none" }}>
          <li style={{ marginBottom: "0.45rem" }}>
            <label style={{ display: "flex", alignItems: "center", gap: "0.5rem", cursor: logging[`practice-${todayIso}`] ? "wait" : "pointer" }}>
              <input
                type="checkbox"
                checked={practiceTodayDone}
                disabled={practiceTodayDone || logging[`practice-${todayIso}`]}
                onChange={() => {
                  onPracticeToggle(todayIso);
                  onSaved();
                }}
              />
              <span style={{ color: "#5f4323" }}>{flowChrome.trackingViewSystemPracticeToday}</span>
            </label>
          </li>
        </ul>

        <p className="orbit-body-xs" style={{ margin: "0 0 0.35rem", fontWeight: "700", color: "#8a6f49" }}>
          {flowChrome.asceticsTitle}
        </p>
        <ul style={{ margin: "0 0 0.75rem", padding: 0, listStyle: "none" }}>
          {asceticTracks.filter(asceticRowInteractive).length === 0 ? (
            <li className="orbit-body-sm" style={{ color: "#8a7760" }}>
              {flowChrome.trackingViewNoActiveItemsLead}{" "}
              <button
                type="button"
                onClick={() => onOpenCreateWizard("ascetic")}
                style={{ border: "none", background: "none", padding: 0, color: "#8a6332", fontWeight: 700, cursor: "pointer", textDecoration: "underline" }}
              >
                {flowChrome.trackingViewCreateAsceticCta}
              </button>
            </li>
          ) : (
            asceticTracks
              .filter(asceticRowInteractive)
              .map((a) => {
                const mark = dayMarkForAscetic(a, todayIso);
                const done = mark === "done";
                const key = `ascetic-${a.asceticism_id}-${todayIso}`;
                return (
                  <li key={a.asceticism_id} style={{ marginBottom: "0.45rem" }}>
                    <label style={{ display: "flex", alignItems: "center", gap: "0.5rem", cursor: logging[key] ? "wait" : "pointer" }}>
                      <input
                        type="checkbox"
                        checked={done}
                        disabled={logging[key]}
                        onChange={() => {
                          onAsceticLog(a.asceticism_id, todayIso, !done);
                          onSaved();
                        }}
                      />
                      <span style={{ color: "#5f4323" }}>{a.title || a.asceticism_id}</span>
                    </label>
                  </li>
                );
              })
          )}
        </ul>

        <button
          type="button"
          onClick={onClose}
          style={{
            marginTop: "0.25rem",
            width: "100%",
            padding: "0.5rem",
            borderRadius: "10px",
            border: "1px solid rgba(195, 154, 92, 0.45)",
            background: "rgba(255,250,242,0.95)",
            color: "#6d4f29",
            cursor: "pointer",
          }}
        >
          {flowChrome.close}
        </button>
      </div>
    </div>
  );
}

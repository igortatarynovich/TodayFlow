"use client";

import { useMemo, useState, useEffect, type ReactNode } from "react";
import { LoadingSpinner } from "@/components/orbit";
import { HEATMAP_CELL_BG } from "./heatmapTokens";
import { getLocale } from "@/lib/i18n";
import { flowTrackerChromeBundle, practicesExperienceChromeBundle } from "@/components/today/flowPracticesMainTabChrome";
import {
  type HeatmapFilterMode,
  type HeatmapCellKind,
  type CalendarGoalTrackLike,
  type CalendarHabitTrackLike,
  type CalendarAsceticTrackLike,
  buildMonthWeekGrid,
  cellKindForDay,
  buildDayDrilldown,
  heatmapInsightUnderMap,
  activeGoalList,
  activeHabitList,
  activeAsceticList,
} from "./calendarHeatmapModel";
import type { CalendarDayLite } from "./trackingRhythm";
import type { TrackerTier } from "./trackerSpec";

function bgForKind(kind: HeatmapCellKind): string {
  switch (kind) {
    case "no_data":
      return HEATMAP_CELL_BG.noData;
    case "intensity_0":
      return HEATMAP_CELL_BG.intensity0;
    case "intensity_low":
      return HEATMAP_CELL_BG.intensityLow;
    case "intensity_mid":
      return HEATMAP_CELL_BG.intensityMid;
    case "intensity_high":
      return HEATMAP_CELL_BG.intensityHigh;
    case "entity_done":
      return HEATMAP_CELL_BG.entityDone;
    case "entity_miss":
      return HEATMAP_CELL_BG.entityMiss;
    default:
      return HEATMAP_CELL_BG.noData;
  }
}

type EntityPick = { type: "goal" | "habit" | "ascetic"; id: string } | null;

function monthKey(y: number, m: number): number {
  return y * 12 + m;
}

function shiftMonth(y: number, m: number, delta: number): { y: number; m: number } {
  const d = new Date(y, m + delta, 1);
  return { y: d.getFullYear(), m: d.getMonth() };
}

type Props = {
  todayIso: string;
  /** Текущий отображаемый месяц (0 = январь) */
  viewYear: number;
  viewMonthIndex: number;
  /** Смена месяца карты → родитель перезагружает календарь */
  onViewMonthChange: (year: number, monthIndex: number) => void;
  days: CalendarDayLite[];
  goalTracks: CalendarGoalTrackLike[];
  habitTracks: CalendarHabitTrackLike[];
  asceticTracks: CalendarAsceticTrackLike[];
  tier?: TrackerTier;
  /** Фоновая подгрузка диапазона при смене месяца */
  isRefreshing?: boolean;
};

export function CalendarHeatmap({
  todayIso,
  viewYear,
  viewMonthIndex,
  days,
  goalTracks,
  habitTracks,
  asceticTracks,
  onViewMonthChange,
  tier: tierProp = "free",
  isRefreshing = false,
}: Props) {
  const localeTag = getLocale() === "ru" ? "ru" : "en";
  const fc = useMemo(() => flowTrackerChromeBundle(localeTag), [localeTag]);
  const pc = useMemo(() => practicesExperienceChromeBundle(localeTag), [localeTag]);
  const weekLabels = useMemo(() => [...fc.weekdayFallback], [fc]);

  const legendForKind = (kind: HeatmapCellKind): string => {
    switch (kind) {
      case "no_data":
        return fc.heatmapLegendNoData;
      case "intensity_0":
        return fc.heatmapLegendIntensity0;
      case "intensity_low":
        return fc.heatmapLegendIntensityLow;
      case "intensity_mid":
        return fc.heatmapLegendIntensityMid;
      case "intensity_high":
        return fc.heatmapLegendIntensityHigh;
      case "entity_done":
        return fc.heatmapLegendEntityDone;
      case "entity_miss":
        return fc.heatmapLegendEntityMiss;
      default:
        return "";
    }
  };

  const [mode, setMode] = useState<HeatmapFilterMode>("all");
  const [selectedGoals, setSelectedGoals] = useState<Set<number>>(new Set());
  const [selectedHabits, setSelectedHabits] = useState<Set<number>>(new Set());
  const [selectedAscetics, setSelectedAscetics] = useState<Set<string>>(new Set());
  const [entityScope, setEntityScope] = useState<"aggregate" | "one">("aggregate");
  const [entityPick, setEntityPick] = useState<EntityPick>(null);
  const [drillDate, setDrillDate] = useState<string | null>(null);
  const [animateIn, setAnimateIn] = useState(false);

  useEffect(() => {
    setAnimateIn(false);
    const t = requestAnimationFrame(() => setAnimateIn(true));
    return () => cancelAnimationFrame(t);
  }, [mode, entityScope, entityPick, viewYear, viewMonthIndex, selectedGoals, selectedHabits, selectedAscetics]);

  const weeks = useMemo(() => buildMonthWeekGrid(viewYear, viewMonthIndex), [viewYear, viewMonthIndex]);

  const selectedGoalIds = mode === "goals" && selectedGoals.size > 0 ? selectedGoals : null;
  const selectedHabitIds = mode === "habits" && selectedHabits.size > 0 ? selectedHabits : null;
  const selectedAsceticIds = mode === "ascetics" && selectedAscetics.size > 0 ? selectedAscetics : null;

  const entityForCell: EntityPick =
    entityScope === "one" && entityPick && mode !== "all" && mode !== "practices" ? entityPick : null;

  const flatCells = useMemo(() => {
    const out: { date: string | null; kind: HeatmapCellKind; inMonth: boolean; idx: number }[] = [];
    let idx = 0;
    for (const row of weeks) {
      for (const c of row) {
        if (!c.date) {
          out.push({ date: null, kind: "no_data", inMonth: false, idx: idx++ });
          continue;
        }
        const kind = cellKindForDay(
          c.date,
          todayIso,
          mode,
          entityForCell,
          goalTracks,
          habitTracks,
          asceticTracks,
          days,
          selectedGoalIds,
          selectedHabitIds,
          selectedAsceticIds,
        );
        out.push({ date: c.date, kind, inMonth: c.inMonth, idx: idx++ });
      }
    }
    return out;
  }, [
    weeks,
    todayIso,
    mode,
    entityForCell,
    goalTracks,
    habitTracks,
    asceticTracks,
    days,
    selectedGoalIds,
    selectedHabitIds,
    selectedAsceticIds,
  ]);

  const insight = useMemo(
    () => heatmapInsightUnderMap(mode, tierProp, flatCells, todayIso, fc),
    [mode, tierProp, flatCells, todayIso, fc],
  );

  const tierLabel =
    tierProp === "premium" ? "PREMIUM" : tierProp === "pro" ? "PRO" : "FREE";

  const monthTitle = useMemo(
    () =>
      new Date(viewYear, viewMonthIndex, 1).toLocaleDateString(localeTag === "ru" ? "ru-RU" : "en-US", {
        month: "long",
        year: "numeric",
      }),
    [viewYear, viewMonthIndex, localeTag],
  );

  const nowNav = new Date();
  const nowKY = monthKey(nowNav.getFullYear(), nowNav.getMonth());
  const viewKY = monthKey(viewYear, viewMonthIndex);
  const canGoNext = viewKY < nowKY;
  const atCurrentMonth = viewKY === nowKY;

  const drill = drillDate
    ? buildDayDrilldown(drillDate, todayIso, goalTracks, habitTracks, asceticTracks, days, fc)
    : null;

  const modeTabs: { id: HeatmapFilterMode; label: string }[] = useMemo(
    () => [
      { id: "all", label: fc.heatmapModeAll },
      { id: "habits", label: fc.habitsTitle },
      { id: "goals", label: fc.goalsNavTitle },
      { id: "ascetics", label: fc.asceticsTitle },
      { id: "practices", label: pc.navPractices },
    ],
    [fc, pc],
  );

  const toggleId = (set: Set<number>, id: number, next: (s: Set<number>) => void) => {
    const n = new Set(set);
    if (n.has(id)) n.delete(id);
    else n.add(id);
    next(n);
  };

  const toggleAsc = (set: Set<string>, id: string, next: (s: Set<string>) => void) => {
    const n = new Set(set);
    if (n.has(id)) n.delete(id);
    else n.add(id);
    next(n);
  };

  return (
    <div
      className="orbit-card todayflow-panel todayflow-heatmap"
      aria-busy={isRefreshing}
      style={{
        marginBottom: "1.1rem",
        padding: "1rem 1.05rem",
        borderRadius: "16px",
        border: "1px solid rgba(198, 166, 119, 0.38)",
        background: "linear-gradient(165deg, rgba(255,252,248,0.99) 0%, rgba(255,244,228,0.9) 100%)",
        position: "relative",
      }}
    >
      <div style={{ display: "flex", flexWrap: "wrap", alignItems: "baseline", justifyContent: "space-between", gap: "0.5rem" }}>
        <div style={{ flex: "1 1 200px" }}>
          <p className="orbit-body-xs" style={{ margin: 0, color: "#8f6e43", letterSpacing: "0.06em", textTransform: "uppercase" }}>
            {fc.monthMapTitle}
          </p>
          <div style={{ display: "flex", flexWrap: "wrap", alignItems: "center", gap: "0.45rem", marginTop: "0.35rem" }}>
            <button
              type="button"
              aria-label={fc.heatmapPrevMonthA11y}
              disabled={isRefreshing}
              onClick={() => {
                const { y, m } = shiftMonth(viewYear, viewMonthIndex, -1);
                onViewMonthChange(y, m);
              }}
              style={{
                width: "2rem",
                height: "2rem",
                borderRadius: "10px",
                border: "1px solid rgba(195, 154, 92, 0.45)",
                background: isRefreshing ? "rgba(245,240,232,0.6)" : "rgba(255,250,242,0.95)",
                color: isRefreshing ? "#b5a896" : "#6d4f29",
                cursor: isRefreshing ? "not-allowed" : "pointer",
                fontSize: "1rem",
                lineHeight: 1,
              }}
            >
              ←
            </button>
            <h3 className="orbit-body" style={{ margin: 0, color: "#5f4323", fontWeight: 700 }}>
              {monthTitle.charAt(0).toUpperCase() + monthTitle.slice(1)}
            </h3>
            {isRefreshing ? (
              <span style={{ display: "inline-flex", alignItems: "center" }} aria-hidden>
                <LoadingSpinner size="sm" />
              </span>
            ) : null}
            <button
              type="button"
              aria-label={fc.heatmapNextMonthA11y}
              disabled={!canGoNext || isRefreshing}
              onClick={() => {
                if (!canGoNext) return;
                const { y, m } = shiftMonth(viewYear, viewMonthIndex, 1);
                onViewMonthChange(y, m);
              }}
              style={{
                width: "2rem",
                height: "2rem",
                borderRadius: "10px",
                border: "1px solid rgba(195, 154, 92, 0.45)",
                background: canGoNext && !isRefreshing ? "rgba(255,250,242,0.95)" : "rgba(245,240,232,0.6)",
                color: canGoNext && !isRefreshing ? "#6d4f29" : "#b5a896",
                cursor: canGoNext && !isRefreshing ? "pointer" : "not-allowed",
                fontSize: "1rem",
                lineHeight: 1,
              }}
            >
              →
            </button>
            {!atCurrentMonth ? (
              <button
                type="button"
                disabled={isRefreshing}
                onClick={() => onViewMonthChange(nowNav.getFullYear(), nowNav.getMonth())}
                style={{
                  padding: "0.35rem 0.65rem",
                  borderRadius: "8px",
                  border: "1px solid rgba(195, 154, 92, 0.4)",
                  background: "transparent",
                  color: isRefreshing ? "#b5a896" : "#8a6332",
                  fontWeight: 600,
                  fontSize: "0.75rem",
                  cursor: isRefreshing ? "not-allowed" : "pointer",
                }}
              >
                {fc.heatmapJumpToCurrentMonth}
              </button>
            ) : null}
          </div>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: "0.35rem" }}>
          <span className="orbit-body-xs" style={{ color: "#8a7760" }}>
            {fc.heatmapInsightPrefix} ({tierLabel})
          </span>
        </div>
      </div>

      <p className="orbit-body-xs" style={{ margin: "0.5rem 0 0.65rem", color: "#7a6242", lineHeight: 1.45 }}>
        {fc.heatmapMapExplainer}
      </p>

      <div style={{ display: "flex", flexWrap: "wrap", gap: "0.35rem", marginBottom: "0.65rem" }}>
        {modeTabs.map((t) => (
          <button
            key={t.id}
            type="button"
            onClick={() => {
              setMode(t.id);
              setEntityScope("aggregate");
              setEntityPick(null);
            }}
            style={{
              padding: "0.35rem 0.7rem",
              borderRadius: "999px",
              border:
                mode === t.id ? "1px solid rgba(155, 118, 70, 0.75)" : "1px solid rgba(195, 154, 92, 0.35)",
              background: mode === t.id ? "linear-gradient(120deg,#d3b178,#bf975f)" : "rgba(255,250,242,0.95)",
              color: mode === t.id ? "#fff8ee" : "#6d4f29",
              fontWeight: 600,
              fontSize: "0.78rem",
              cursor: "pointer",
            }}
          >
            {t.label}
          </button>
        ))}
      </div>

      {mode === "goals" && activeGoalList(goalTracks).length > 0 ? (
        <EntityCheckboxRow title={fc.heatmapFilterGoalsRowTitle}>
          {activeGoalList(goalTracks).map((g) => (
            <label key={g.id} style={{ display: "inline-flex", alignItems: "center", gap: "0.25rem", marginRight: "0.65rem", fontSize: "0.78rem", color: "#5f4323" }}>
              <input
                type="checkbox"
                checked={selectedGoals.size === 0 || selectedGoals.has(g.id)}
                onChange={() => {
                  if (selectedGoals.size === 0) {
                    const all = new Set(activeGoalList(goalTracks).map((x) => x.id));
                    all.delete(g.id);
                    setSelectedGoals(all);
                  } else {
                    toggleId(selectedGoals, g.id, setSelectedGoals);
                  }
                }}
              />
              {g.title}
            </label>
          ))}
          <button
            type="button"
            className="orbit-body-xs"
            style={{ marginLeft: "0.25rem", border: "none", background: "none", color: "#8a6332", cursor: "pointer", textDecoration: "underline" }}
            onClick={() => setSelectedGoals(new Set())}
          >
            {fc.heatmapSelectAllShort}
          </button>
        </EntityCheckboxRow>
      ) : null}

      {mode === "habits" && activeHabitList(habitTracks, null).length > 0 ? (
        <EntityCheckboxRow title={fc.habitsTitle}>
          {activeHabitList(habitTracks, null).map((h) => (
            <label key={h.id} style={{ display: "inline-flex", alignItems: "center", gap: "0.25rem", marginRight: "0.65rem", fontSize: "0.78rem", color: "#5f4323" }}>
              <input
                type="checkbox"
                checked={selectedHabits.size === 0 || selectedHabits.has(h.id)}
                onChange={() => {
                  if (selectedHabits.size === 0) {
                    const all = new Set(activeHabitList(habitTracks, null).map((x) => x.id));
                    all.delete(h.id);
                    setSelectedHabits(all);
                  } else {
                    toggleId(selectedHabits, h.id, setSelectedHabits);
                  }
                }}
              />
              {h.name}
            </label>
          ))}
          <button
            type="button"
            className="orbit-body-xs"
            style={{ marginLeft: "0.25rem", border: "none", background: "none", color: "#8a6332", cursor: "pointer", textDecoration: "underline" }}
            onClick={() => setSelectedHabits(new Set())}
          >
            {fc.heatmapSelectAllShort}
          </button>
        </EntityCheckboxRow>
      ) : null}

      {mode === "ascetics" && activeAsceticList(asceticTracks).length > 0 ? (
        <EntityCheckboxRow title={fc.asceticsTitle}>
          {activeAsceticList(asceticTracks).map((a) => (
            <label
              key={a.asceticism_id}
              style={{ display: "inline-flex", alignItems: "center", gap: "0.25rem", marginRight: "0.65rem", fontSize: "0.78rem", color: "#5f4323" }}
            >
              <input
                type="checkbox"
                checked={selectedAscetics.size === 0 || selectedAscetics.has(a.asceticism_id)}
                onChange={() => {
                  if (selectedAscetics.size === 0) {
                    const all = new Set(activeAsceticList(asceticTracks).map((x) => x.asceticism_id));
                    all.delete(a.asceticism_id);
                    setSelectedAscetics(all);
                  } else {
                    toggleAsc(selectedAscetics, a.asceticism_id, setSelectedAscetics);
                  }
                }}
              />
              {a.title || a.asceticism_id}
            </label>
          ))}
          <button
            type="button"
            className="orbit-body-xs"
            style={{ marginLeft: "0.25rem", border: "none", background: "none", color: "#8a6332", cursor: "pointer", textDecoration: "underline" }}
            onClick={() => setSelectedAscetics(new Set())}
          >
            {fc.heatmapSelectAllShort}
          </button>
        </EntityCheckboxRow>
      ) : null}

      {mode !== "all" && mode !== "practices" ? (
        <div style={{ marginBottom: "0.55rem", display: "flex", flexWrap: "wrap", gap: "0.5rem", alignItems: "center" }}>
          <span className="orbit-body-xs" style={{ color: "#8a7760" }}>
            {fc.heatmapRowModeLabel}
          </span>
          <button
            type="button"
            onClick={() => {
              setEntityScope("aggregate");
              setEntityPick(null);
            }}
            style={{
              padding: "0.28rem 0.55rem",
              fontSize: "0.75rem",
              borderRadius: "8px",
              border: "1px solid rgba(195, 154, 92, 0.4)",
              background: entityScope === "aggregate" ? "rgba(201, 166, 108, 0.25)" : "transparent",
              cursor: "pointer",
              color: "#5f4323",
            }}
          >
            {fc.heatmapRowModeAggregate}
          </button>
          <button
            type="button"
            onClick={() => setEntityScope("one")}
            style={{
              padding: "0.28rem 0.55rem",
              fontSize: "0.75rem",
              borderRadius: "8px",
              border: "1px solid rgba(195, 154, 92, 0.4)",
              background: entityScope === "one" ? "rgba(201, 166, 108, 0.25)" : "transparent",
              cursor: "pointer",
              color: "#5f4323",
            }}
          >
            {fc.heatmapRowModeOneEntity}
          </button>
          {entityScope === "one" ? (
            <select
              value={entityPick ? `${entityPick.type}|${entityPick.id}` : ""}
              onChange={(e) => {
                const v = e.target.value;
                if (!v) {
                  setEntityPick(null);
                  return;
                }
                const bar = v.indexOf("|");
                const tp = v.slice(0, bar);
                const id = v.slice(bar + 1);
                setEntityPick({ type: tp as "goal" | "habit" | "ascetic", id });
              }}
              style={{
                fontSize: "0.78rem",
                padding: "0.3rem 0.45rem",
                borderRadius: "8px",
                border: "1px solid rgba(195, 154, 92, 0.45)",
                color: "#5f4323",
                background: "#fffdf9",
                maxWidth: "220px",
              }}
            >
              <option value="">{fc.heatmapEntityPickPlaceholder}</option>
              {mode === "goals"
                ? activeGoalList(goalTracks).map((g) => (
                    <option key={g.id} value={`goal|${g.id}`}>
                      {g.title}
                    </option>
                  ))
                : null}
              {mode === "habits"
                ? activeHabitList(habitTracks, null).map((h) => (
                    <option key={h.id} value={`habit|${h.id}`}>
                      {h.name}
                    </option>
                  ))
                : null}
              {mode === "ascetics"
                ? activeAsceticList(asceticTracks).map((a) => (
                    <option key={a.asceticism_id} value={`ascetic|${a.asceticism_id}`}>
                      {a.title || a.asceticism_id}
                    </option>
                  ))
                : null}
            </select>
          ) : null}
        </div>
      ) : null}

      {entityScope === "one" && !entityPick && mode !== "all" && mode !== "practices" ? (
        <p className="orbit-body-xs" style={{ margin: "0 0 0.5rem", color: "#a65c2e" }}>
          {fc.heatmapEntityPickHint}
        </p>
      ) : null}

      <div
        style={{
          opacity: isRefreshing ? 0.72 : 1,
          transition: "opacity 0.2s ease",
          pointerEvents: isRefreshing ? "none" : "auto",
        }}
      >
      <div style={{ display: "grid", gridTemplateColumns: "repeat(7, minmax(0, 1fr))", gap: "5px", marginBottom: "0.35rem" }}>
        {weekLabels.map((w) => (
          <div key={w} className="orbit-body-xs" style={{ textAlign: "center", color: "#9a8b78", fontWeight: 600 }}>
            {w}
          </div>
        ))}
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: "5px" }}>
        {weeks.map((row, wi) => (
          <div key={wi} style={{ display: "grid", gridTemplateColumns: "repeat(7, minmax(0, 1fr))", gap: "5px" }}>
            {row.map((cell, ci) => {
              const flat = flatCells[wi * 7 + ci];
              const kind = flat?.kind ?? "no_data";
              const bg = bgForKind(kind);
              const delay = animateIn ? (flat?.idx ?? 0) * 22 : 0;
              return (
                <button
                  key={ci}
                  type="button"
                  disabled={!cell.date || cell.date > todayIso}
                  onClick={() => cell.date && cell.date <= todayIso && setDrillDate(cell.date)}
                  title={cell.date ? `${cell.date}: ${legendForKind(kind)}` : ""}
                  style={{
                    aspectRatio: "1",
                    minHeight: "28px",
                    maxHeight: "44px",
                    borderRadius: "6px",
                    border: "1px solid rgba(120, 90, 50, 0.12)",
                    background: bg,
                    cursor: cell.date && cell.date <= todayIso ? "pointer" : "default",
                    padding: 0,
                    opacity: animateIn ? 1 : 0,
                    transform: animateIn ? "scale(1)" : "scale(0.88)",
                    transition: "opacity 0.32s ease, transform 0.32s ease, box-shadow 0.15s ease",
                    transitionDelay: `${delay}ms`,
                    boxShadow: "inset 0 1px 0 rgba(255,255,255,0.35)",
                  }}
                  onMouseEnter={(e) => {
                    if (cell.date && cell.date <= todayIso) {
                      e.currentTarget.style.boxShadow = `0 0 0 2px ${HEATMAP_CELL_BG.hoverRing}`;
                    }
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.boxShadow = "inset 0 1px 0 rgba(255,255,255,0.35)";
                  }}
                />
              );
            })}
          </div>
        ))}
      </div>

      <div style={{ display: "flex", flexWrap: "wrap", gap: "0.65rem", marginTop: "0.75rem" }}>
        {(mode === "practices" || entityScope === "one"
          ? (["no_data", "entity_miss", "entity_done"] as HeatmapCellKind[])
          : (["no_data", "intensity_0", "intensity_low", "intensity_mid", "intensity_high"] as HeatmapCellKind[])
        ).map((k) => (
          <span key={k} className="orbit-body-xs" style={{ display: "inline-flex", alignItems: "center", gap: "0.28rem", color: "#7a6242" }}>
            <span style={{ width: "12px", height: "12px", borderRadius: "3px", background: bgForKind(k), border: "1px solid rgba(0,0,0,0.06)" }} />
            {legendForKind(k)}
          </span>
        ))}
      </div>
      </div>

      <div
        style={{
          marginTop: "0.85rem",
          padding: "0.65rem 0.75rem",
          borderRadius: "10px",
          background: "rgba(255,252,247,0.95)",
          border: "1px solid rgba(210, 184, 140, 0.35)",
        }}
      >
        <p className="orbit-body-xs" style={{ margin: "0 0 0.25rem", color: "#8a6f49", fontWeight: 700 }}>
          {fc.heatmapUnderMapEyebrowPrefix} ({tierLabel})
        </p>
        <p className="orbit-body-sm" style={{ margin: 0, color: "#5c4a32", lineHeight: 1.55 }}>
          {insight}
        </p>
      </div>

      {drill && drillDate ? (
        <div
          role="dialog"
          aria-modal
          style={{
            position: "fixed",
            inset: 0,
            zIndex: 70,
            background: "rgba(40, 32, 24, 0.45)",
            display: "grid",
            placeItems: "center",
            padding: "1rem",
          }}
          onClick={() => setDrillDate(null)}
        >
          <div
            className="orbit-card"
            style={{
              maxWidth: "360px",
              width: "100%",
              padding: "1.1rem 1.2rem",
              borderRadius: "14px",
              background: "#fffdf9",
              border: "1px solid rgba(198, 166, 119, 0.45)",
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <p className="orbit-body-xs" style={{ margin: "0 0 0.2rem", color: "#8a6f49" }}>
              {fc.heatmapDrillDayEyebrow}
            </p>
            <h4 className="orbit-body" style={{ margin: "0 0 0.75rem", color: "#5f4323" }}>
              {new Date(drillDate + "T12:00:00").toLocaleDateString(localeTag === "ru" ? "ru-RU" : "en-US", {
                day: "numeric",
                month: "long",
                year: "numeric",
              })}
            </h4>
            <ul style={{ margin: "0 0 0.75rem", paddingLeft: "1.05rem", color: "#5f4323", lineHeight: 1.6 }} className="orbit-body-sm">
              <li>
                {fc.heatmapDrillHabitsLinePrefix} {drill.habitsDone}/{drill.habitsTotal || "—"}
              </li>
              <li>
                {fc.heatmapDrillGoalsLinePrefix} {drill.goalsDone}/{drill.goalsTotal || "—"}
              </li>
              <li>
                {fc.heatmapDrillAsceticsLinePrefix} {drill.asceticsDone}/{drill.asceticsTotal || "—"}
              </li>
              <li>
                {fc.heatmapDrillPracticeLabel}{" "}
                {drill.practiceDone ? fc.heatmapDrillPracticeDone : fc.heatmapDrillPracticeNo}
              </li>
              <li style={{ marginTop: "0.35rem", listStyle: "none", marginLeft: "-1rem", color: "#7a6242" }}>
                {fc.heatmapDrillTotalsPrefix} {drill.allDone}/{drill.allTotal || "—"}
              </li>
            </ul>
            <p className="orbit-body-sm" style={{ margin: 0, color: "#6d4f29", fontStyle: "italic", lineHeight: 1.5 }}>
              {drill.caption}
            </p>
            <button
              type="button"
              onClick={() => setDrillDate(null)}
              style={{
                marginTop: "1rem",
                width: "100%",
                padding: "0.45rem",
                borderRadius: "10px",
                border: "1px solid rgba(195, 154, 92, 0.45)",
                background: "rgba(255,250,242,0.95)",
                color: "#6d4f29",
                cursor: "pointer",
              }}
            >
              {fc.close}
            </button>
          </div>
        </div>
      ) : null}
    </div>
  );
}

function EntityCheckboxRow({ title, children }: { title: string; children: ReactNode }) {
  return (
    <div style={{ marginBottom: "0.55rem", padding: "0.45rem 0.5rem", borderRadius: "10px", background: "rgba(255,255,255,0.65)", border: "1px dashed rgba(201, 168, 115, 0.35)" }}>
      <p className="orbit-body-xs" style={{ margin: "0 0 0.35rem", color: "#8a7760", fontWeight: 600 }}>
        {title}
      </p>
      <div style={{ display: "flex", flexWrap: "wrap", alignItems: "center", gap: "0.25rem 0" }}>{children}</div>
    </div>
  );
}

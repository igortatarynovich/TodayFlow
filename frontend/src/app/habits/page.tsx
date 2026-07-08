"use client";


import { useCallback, useEffect, useMemo, useState } from "react";
import { DsBody, DsButton } from "@/design-system";
import { ProductPageScreen } from "@/components/product-ui/ProductPageScreen";
import pl from "@/design-system/layouts/productPageLayout.module.css";
import v2 from "@/design-system/layouts/productV2Surface.module.css";
import { useToast } from "@/components/ToastProvider";
import { getJson, postJson } from "@/lib/api";
import { useAuth } from "@/lib/useAuth";
import { getLocale } from "@/lib/i18n";
import { flowTrackerChromeBundle, formatHabitMapStatsLine } from "@/components/today/flowPracticesMainTabChrome";
import {
  buildHabitDayStory,
  buildHabitMapObservation,
  buildHabitMapRows,
  countHabitMapMarks,
  HABIT_CELL_MISSED,
  HABIT_MAP_WINDOW_DAYS,
  habitWeaveColor,
  type HabitMapEntry,
  type HabitMapOverviewItem,
  type HabitMapSelectedCell,
} from "@/lib/habitMapModel";
import { habitMapCopy } from "@/lib/habitMapCopy";
import { shiftDateISO } from "@/lib/moodMapModel";

function tpl(s: string, vars: Record<string, string | number>) {
  return s.replace(/\{\{(\w+)\}\}/g, (_, k) => String(vars[k] ?? ""));
}

type Habit = {
  id: number;
  name: string;
  category: string | null;
  target_frequency: string;
  target_per_period: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
};

export default function HabitsPage() {
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const toast = useToast();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [creating, setCreating] = useState(false);
  const [habits, setHabits] = useState<Habit[]>([]);
  const [overview, setOverview] = useState<HabitMapOverviewItem[]>([]);
  const [entriesByHabit, setEntriesByHabit] = useState<Record<number, HabitMapEntry[]>>({});
  const [newHabitName, setNewHabitName] = useState("");
  const [newHabitCategory, setNewHabitCategory] = useState("");
  const [selectedCell, setSelectedCell] = useState<HabitMapSelectedCell | null>(null);

  const locale = getLocale() === "ru" ? "ru" : "en";
  const fc = useMemo(() => flowTrackerChromeBundle(locale), [locale]);
  const mapCopy = habitMapCopy(locale);
  const dateLocaleTag = locale === "ru" ? "ru-RU" : "en-US";

  const today = useMemo(() => new Date().toISOString().split("T")[0], []);

  const loadData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const [habitsData, overviewData] = await Promise.all([
        getJson<Habit[]>("/habits"),
        getJson<HabitMapOverviewItem[]>("/habits/overview/summary"),
      ]);

      const fromDate = shiftDateISO(today, -(HABIT_MAP_WINDOW_DAYS - 1));
      const entriesData = await Promise.all(
        habitsData.map((habit) =>
          getJson<HabitMapEntry[]>(`/habits/${habit.id}/entries?from_date=${fromDate}&to_date=${today}`).catch(() => []),
        ),
      );

      const nextEntriesByHabit: Record<number, HabitMapEntry[]> = {};
      habitsData.forEach((habit, index) => {
        nextEntriesByHabit[habit.id] = entriesData[index];
      });

      setHabits(habitsData);
      setOverview(overviewData);
      setEntriesByHabit(nextEntriesByHabit);
    } catch (err: unknown) {
      const e = err as { message?: string };
      setError(e?.message || fc.habitsMapLoadErrorFallback);
    } finally {
      setLoading(false);
    }
  }, [today, fc]);

  useEffect(() => {
    if (!isAuthenticated) return;
    loadData();
  }, [isAuthenticated, loadData]);

  const habitRows = useMemo(
    () => buildHabitMapRows(habits, entriesByHabit, overview, today),
    [habits, entriesByHabit, overview, today],
  );

  const observation = useMemo(
    () => buildHabitMapObservation(habits, entriesByHabit, overview, locale),
    [habits, entriesByHabit, overview, locale],
  );

  const totalMarks = useMemo(() => countHabitMapMarks(entriesByHabit), [entriesByHabit]);

  const selectedStory = useMemo(() => {
    if (!selectedCell) return null;
    const habit = habits.find((item) => item.id === selectedCell.habitId);
    if (!habit) return null;
    const entry = entriesByHabit[habit.id]?.find((item) => item.date === selectedCell.dateISO) ?? null;
    return buildHabitDayStory(habit, selectedCell.dateISO, entry, locale, habits, entriesByHabit);
  }, [selectedCell, habits, entriesByHabit, locale]);

  const handleCreateHabit = async () => {
    if (!newHabitName.trim()) return;
    try {
      setCreating(true);
      await postJson("/habits", {
        name: newHabitName.trim(),
        category: newHabitCategory.trim() || null,
        target_frequency: "daily",
        target_per_period: 1,
      });
      setNewHabitName("");
      setNewHabitCategory("");
      await loadData();
    } catch (err: unknown) {
      const e = err as { message?: string };
      toast.error(e?.message || fc.habitsMapCreateErrorFallback);
    } finally {
      setCreating(false);
    }
  };

  const handleCheckHabitToday = async (habitId: number) => {
    try {
      await postJson(`/habits/${habitId}/entries`, { date: today, completed: true });
      await loadData();
    } catch (err: unknown) {
      const e = err as { message?: string };
      toast.error(e?.message || fc.habitsMapCheckErrorFallback);
    }
  };

  const todayCompletedCount = useMemo(
    () =>
      habits.filter((habit) =>
        entriesByHabit[habit.id]?.some((entry) => entry.date === today && entry.completed),
      ).length,
    [entriesByHabit, habits, today],
  );

  const strongestHabit = useMemo(() => {
    if (overview.length === 0) return null;
    return [...overview].sort((a, b) => b.current_streak_days - a.current_streak_days)[0];
  }, [overview]);

  if (authLoading || loading) {
    return (
      <ProductPageScreen
        testId="habits-map-page"
        title={fc.habitsMapPageTitle}
        loading
        loadingLabel={locale === "ru" ? "Загрузка карты привычек…" : "Loading habit map…"}
      />
    );
  }

  if (!isAuthenticated) {
    return (
      <ProductPageScreen
        testId="habits-map-page"
        title={fc.habitsMapPageTitle}
        guest={{
          message: fc.habitsMapLoginLead,
          ctaHref: "/auth?redirect=/habits",
          ctaLabel: fc.trackingProgressHubLoginCta,
        }}
      />
    );
  }

  return (
    <ProductPageScreen
      testId="habits-map-page"
      eyebrow={fc.habitsMapEyebrow}
      title={fc.habitsMapHeroTitle}
      subtitle={totalMarks > 0 ? fc.habitsMapHeroBody : fc.habitsMapEmptyList}
      contentClassName={`${pl.content} ${pl.legacyHost}`}
    >
      <section className={pl.panel}>
        <div className={pl.grid2}>
          <div>
            <div style={{ display: "flex", gap: "0.45rem", flexWrap: "wrap", marginTop: "0.25rem" }}>
              <DsButton href="/today" size="sm">
                {fc.habitsMapLinkToday}
              </DsButton>
              <DsButton href="/maps/mood" variant="secondary" size="sm">
                {mapCopy.linkMood}
              </DsButton>
              <DsButton href="/maps/energy" variant="secondary" size="sm">
                {mapCopy.linkEnergy}
              </DsButton>
              <DsButton href="/flow" variant="secondary" size="sm">
                {fc.habitsMapLinkTrackingHub}
              </DsButton>
            </div>
          </div>

          <div className={pl.panel} style={{ padding: "0.9rem" }}>
            <p className={v2.eyebrow}>{fc.habitsMapTodaySnapshotEyebrow}</p>
            <p className={v2.sectionTitle} style={{ marginTop: "0.35rem" }}>
              {tpl(fc.habitsMapTodayProgress, { done: todayCompletedCount, total: habits.length })}
            </p>
            <DsBody size="sm" muted className={pl.bodyMtSm}>
              {strongestHabit
                ? tpl(fc.habitsMapStrongestRhythm, {
                    name: strongestHabit.name,
                    days: strongestHabit.current_streak_days,
                  })
                : fc.habitsMapStrongestRhythmEmpty}
            </DsBody>
          </div>
        </div>
      </section>

        {observation ? (
          <section className={pl.panel}>
            <p className={v2.eyebrow}>{mapCopy.observationEyebrow}</p>
            <DsBody className={pl.bodyMtSm}>{observation.text}</DsBody>
          </section>
        ) : null}

        <section className={pl.panel}>
          <p className={v2.eyebrow}>{mapCopy.selectedDayEyebrow}</p>
          <DsBody className={pl.bodyMtMd}>{selectedStory ?? mapCopy.selectedDayEmpty}</DsBody>
        </section>

        <div className={pl.grid2}>
          <div className={pl.panel}>
            <h2 className={v2.sectionTitle}>{fc.habitsMapAddSectionTitle}</h2>
            <div className={pl.formStack} style={{ marginTop: "0.75rem" }}>
              <input
                value={newHabitName}
                onChange={(e) => setNewHabitName(e.target.value)}
                placeholder={fc.habitsMapNamePlaceholder}
                className={pl.fieldInput}
              />
              <input
                value={newHabitCategory}
                onChange={(e) => setNewHabitCategory(e.target.value)}
                placeholder={fc.habitsMapCategoryPlaceholder}
                className={pl.fieldInput}
              />
              <DsButton onClick={handleCreateHabit} disabled={creating || !newHabitName.trim()}>
                {creating ? fc.habitsMapAddCreating : fc.habitsMapAddCta}
              </DsButton>
            </div>
          </div>

          <div className={pl.panel}>
            <h2 className={v2.sectionTitle}>{fc.habitsMapHowToReadTitle}</h2>
            <div className={pl.formStack} style={{ marginTop: "0.75rem" }}>
              <div className={pl.panel} style={{ padding: "0.85rem" }}>
                <DsBody size="sm" muted>
                  {mapCopy.howToReadGridLine}
                </DsBody>
              </div>
              <div className={pl.panel} style={{ padding: "0.85rem" }}>
                <DsBody size="sm" muted>
                  {fc.habitsMapHowToReadLine2}
                </DsBody>
              </div>
            </div>
          </div>
        </div>

        {error ? (
          <div className={pl.panel}>
            <DsBody size="sm">{error}</DsBody>
          </div>
        ) : null}

        <section className={pl.formStack}>
          {habits.length === 0 ? (
            <div className={pl.emptyState}>
              <DsBody size="sm" muted>
                {fc.habitsMapEmptyList}
              </DsBody>
            </div>
          ) : (
            habitRows.map((row) => {
              const todayDone = entriesByHabit[row.habitId]?.some((entry) => entry.date === today && entry.completed);
              const weaveColor = habitWeaveColor(row.habitId, row.category);

              return (
                <article key={row.habitId} className={pl.panel}>
                  <div style={{ display: "grid", gap: "0.8rem", gridTemplateColumns: "1fr auto", alignItems: "start" }}>
                    <div>
                      <div style={{ display: "flex", gap: "0.45rem", flexWrap: "wrap", alignItems: "center" }}>
                        <h3 className={v2.sectionTitle} style={{ margin: 0 }}>
                          {row.name}
                        </h3>
                        <span className={v2.chip}>{row.category || fc.habitsMapNoCategory}</span>
                      </div>
                      <DsBody size="sm" muted className={pl.bodyMtSm}>
                        {row.currentStreakDays > 0
                          ? formatHabitMapStatsLine(locale, row.currentStreakDays)
                          : fc.habitsMapStatsPending}
                      </DsBody>

                      <div
                        style={{
                          marginTop: "0.8rem",
                          display: "grid",
                          gridTemplateColumns: "repeat(7, minmax(0, 1fr))",
                          gap: "0.28rem",
                          maxWidth: "420px",
                        }}
                        role="grid"
                        aria-label={row.name}
                      >
                        {row.cells.map((cell) => {
                          const selected =
                            selectedCell?.habitId === row.habitId && selectedCell.dateISO === cell.dateISO;
                          const title = cell.completed
                            ? `${cell.dateISO} — ${row.name}`
                            : new Date(`${cell.dateISO}T12:00:00`).toLocaleDateString(dateLocaleTag);
                          return (
                            <button
                              key={`${row.habitId}-${cell.dateISO}`}
                              type="button"
                              role="gridcell"
                              disabled={!cell.completed}
                              onClick={() =>
                                cell.completed &&
                                setSelectedCell({ habitId: row.habitId, dateISO: cell.dateISO })
                              }
                              title={title}
                              style={{
                                width: "100%",
                                aspectRatio: "1 / 1",
                                borderRadius: "5px",
                                border: selected
                                  ? "2px solid rgba(91, 67, 53, 0.65)"
                                  : "1px solid rgba(166, 124, 58, 0.12)",
                                background: cell.color,
                                cursor: cell.completed ? "pointer" : "default",
                                opacity: cell.isFuture ? 0.45 : 1,
                                padding: 0,
                              }}
                            />
                          );
                        })}
                      </div>

                      <ul
                        style={{
                          display: "flex",
                          flexWrap: "wrap",
                          gap: "0.55rem 0.9rem",
                          margin: "0.65rem 0 0",
                          padding: 0,
                          listStyle: "none",
                        }}
                      >
                        <li style={{ display: "inline-flex", alignItems: "center", gap: "0.35rem", fontSize: "0.78rem", color: "#7c6241" }}>
                          <span aria-hidden style={{ width: "0.75rem", height: "0.75rem", borderRadius: "4px", background: weaveColor }} />
                          {mapCopy.legendMarked}
                        </li>
                        <li style={{ display: "inline-flex", alignItems: "center", gap: "0.35rem", fontSize: "0.78rem", color: "#9a8468" }}>
                          <span aria-hidden style={{ width: "0.75rem", height: "0.75rem", borderRadius: "4px", background: HABIT_CELL_MISSED }} />
                          {mapCopy.legendEmpty}
                        </li>
                      </ul>
                    </div>

                    <DsButton variant="secondary" onClick={() => handleCheckHabitToday(row.habitId)} disabled={todayDone}>
                      {todayDone ? fc.habitsMapMarkedToday : fc.habitsMapMarkToday}
                    </DsButton>
                  </div>
                </article>
              );
            })
          )}
        </section>

        <section className={pl.panel}>
          <h2 className={v2.sectionTitle}>{fc.habitsMapSummary30Title}</h2>
          <div className={pl.formStack} style={{ marginTop: "0.75rem" }}>
            {overview.length === 0 ? (
              <DsBody size="sm" muted>
                {fc.habitsMapSummary30Empty}
              </DsBody>
            ) : (
              overview.map((item) => (
                <div
                  key={item.habit_id}
                  className={pl.panel}
                  style={{
                    padding: "0.85rem 0.95rem",
                    display: "grid",
                    gridTemplateColumns: "1fr auto",
                    gap: "0.75rem",
                    alignItems: "center",
                  }}
                >
                  <strong>{item.name}</strong>
                  <DsBody size="sm" muted>
                    {formatHabitMapStatsLine(locale, item.current_streak_days)}
                  </DsBody>
                </div>
              ))
            )}
          </div>
        </section>
    </ProductPageScreen>
  );
}

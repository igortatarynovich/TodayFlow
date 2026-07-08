"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";
import { DsButton } from "@/design-system";
import { ProductPageScreen } from "@/components/product-ui/ProductPageScreen";
import pl from "@/design-system/layouts/productPageLayout.module.css";
import { useToast } from "@/components/ToastProvider";
import { deleteJson, getJson, postJson, putJson } from "@/lib/api";
import { useAuth } from "@/lib/useAuth";

type CalendarEvent = {
  id: number;
  title: string;
  date: string;
  time: string | null;
  is_all_day: boolean;
  color: string | null;
  category: string | null;
  description: string | null;
  repeat_type: string | null;
  reminder_minutes: number | null;
};

type CalendarNote = {
  id: number;
  date: string;
  event_id: number | null;
  note_text: string;
};

type MenstrualCycle = {
  id: number;
  date: string;
  cycle_day: number | null;
  period_intensity: string | null;
  ovulation: boolean;
  fertile_window: boolean;
  symptoms: Record<string, unknown> | null;
};

type TrackerDay = {
  date: string;
  activities: {
    practice?: { completed: boolean };
    affirmation?: { completed: boolean };
    asceticism?: { completed: boolean };
    diary?: { completed: boolean };
    ritual?: { completed: boolean };
  };
  mood?: number;
  streak: Record<string, number>;
};

type TrackerData = {
  days: TrackerDay[];
  streaks: Record<string, number>;
  stats: Record<string, { total: number; completed: number; percentage: number }>;
};

type UnifiedCalendarResponse = {
  days: Array<{
    date: string;
    events: CalendarEvent[];
    notes: CalendarNote[];
    cycle?: MenstrualCycle | null;
    activities: TrackerDay["activities"];
    mood?: number;
    streaks: Record<string, number>;
  }>;
  streaks: Record<string, number>;
  stats: Record<string, { total: number; completed: number; percentage: number }>;
};

function shiftMonth(date: Date, amount: number) {
  const next = new Date(date);
  next.setMonth(next.getMonth() + amount);
  return next;
}

function getMonthRange(baseDate: Date) {
  const year = baseDate.getFullYear();
  const month = baseDate.getMonth();
  const firstDay = new Date(year, month, 1);
  const lastDay = new Date(year, month + 1, 0);
  return {
    from: firstDay.toISOString().split("T")[0],
    to: lastDay.toISOString().split("T")[0],
  };
}

function getMonthDays(baseDate: Date) {
  const year = baseDate.getFullYear();
  const month = baseDate.getMonth();
  const firstDay = new Date(year, month, 1);
  const lastDay = new Date(year, month + 1, 0);
  const days: Date[] = [];

  const jsWeekday = firstDay.getDay();
  const mondayOffset = (jsWeekday + 6) % 7;

  for (let index = mondayOffset - 1; index >= 0; index -= 1) {
    days.push(new Date(year, month, -index));
  }

  for (let day = 1; day <= lastDay.getDate(); day += 1) {
    days.push(new Date(year, month, day));
  }

  while (days.length < 42) {
    const nextDay = days.length - (mondayOffset + lastDay.getDate()) + 1;
    days.push(new Date(year, month + 1, nextDay));
  }

  return days;
}

function isToday(date: Date) {
  return date.toDateString() === new Date().toDateString();
}

function sameMonth(date: Date, baseDate: Date) {
  return date.getMonth() === baseDate.getMonth() && date.getFullYear() === baseDate.getFullYear();
}

export default function CalendarOrganizerPage() {
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const toast = useToast();

  const [loading, setLoading] = useState(true);
  const [currentDate, setCurrentDate] = useState(new Date());
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split("T")[0]);
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [notes, setNotes] = useState<CalendarNote[]>([]);
  const [cycles, setCycles] = useState<MenstrualCycle[]>([]);
  const [trackerData, setTrackerData] = useState<TrackerData | null>(null);
  const [cycleTrackingEnabled, setCycleTrackingEnabled] = useState(true);
  const [showTrackerLayer, setShowTrackerLayer] = useState(true);

  const [eventTitle, setEventTitle] = useState("");
  const [eventTime, setEventTime] = useState("");
  const [eventCategory, setEventCategory] = useState("");
  const [editingEventId, setEditingEventId] = useState<number | null>(null);
  const [noteText, setNoteText] = useState("");
  const [savingEvent, setSavingEvent] = useState(false);
  const [savingNote, setSavingNote] = useState(false);

  const monthDays = useMemo(() => getMonthDays(currentDate), [currentDate]);

  const loadCalendarData = useCallback(async () => {
    try {
      setLoading(true);
      const { from, to } = getMonthRange(currentDate);
      const unifiedData = await getJson<UnifiedCalendarResponse>(
        `/calendar/unified?from_date=${from}&to_date=${to}&include_cycle=${cycleTrackingEnabled}&include_tracker=true`,
      ).catch(() => null);

      if (unifiedData) {
        const nextEvents: CalendarEvent[] = [];
        const nextNotes: CalendarNote[] = [];
        const nextCycles: MenstrualCycle[] = [];
        const trackerDays: TrackerDay[] = [];

        unifiedData.days.forEach((day) => {
          nextEvents.push(...day.events);
          nextNotes.push(...day.notes);
          if (day.cycle) nextCycles.push(day.cycle);
          trackerDays.push({
            date: day.date,
            activities: day.activities,
            mood: day.mood,
            streak: day.streaks,
          });
        });

        setEvents(nextEvents);
        setNotes(nextNotes);
        setCycles(nextCycles);
        setTrackerData({
          days: trackerDays,
          streaks: unifiedData.streaks,
          stats: unifiedData.stats,
        });
      } else {
        setEvents([]);
        setNotes([]);
        setCycles([]);
        setTrackerData(null);
      }
    } catch (err) {
      console.error("Error loading calendar data:", err);
      toast.error("Не удалось загрузить календарь");
      setEvents([]);
      setNotes([]);
      setCycles([]);
      setTrackerData(null);
    } finally {
      setLoading(false);
    }
  }, [currentDate, cycleTrackingEnabled, toast]);

  useEffect(() => {
    if (!isAuthenticated) return;
    loadCalendarData();
  }, [isAuthenticated, loadCalendarData]);

  const selectedDayEvents = useMemo(() => events.filter((event) => event.date === selectedDate), [events, selectedDate]);
  const selectedDayNote = useMemo(() => notes.find((note) => note.date === selectedDate) || null, [notes, selectedDate]);
  const selectedDayCycle = useMemo(() => cycles.find((cycle) => cycle.date === selectedDate) || null, [cycles, selectedDate]);
  const selectedDayTracker = useMemo(() => trackerData?.days.find((day) => day.date === selectedDate) || null, [trackerData, selectedDate]);

  useEffect(() => {
    if (selectedDayNote) {
      setNoteText(selectedDayNote.note_text);
    } else {
      setNoteText("");
    }
  }, [selectedDayNote]);

  const handleSelectEvent = (event: CalendarEvent) => {
    setEditingEventId(event.id);
    setEventTitle(event.title);
    setEventTime(event.time || "");
    setEventCategory(event.category || "");
  };

  const resetEventForm = () => {
    setEditingEventId(null);
    setEventTitle("");
    setEventTime("");
    setEventCategory("");
  };

  const saveEvent = async () => {
    if (!eventTitle.trim()) return;
    setSavingEvent(true);
    try {
      const payload = {
        title: eventTitle.trim(),
        date: selectedDate,
        time: eventTime || null,
        is_all_day: !eventTime,
        category: eventCategory.trim() || null,
      };

      if (editingEventId) {
        await putJson(`/calendar/events/${editingEventId}`, payload);
      } else {
        await postJson("/calendar/events", payload);
      }

      resetEventForm();
      await loadCalendarData();
    } catch (err) {
      console.error("Error saving event:", err);
      toast.error("Не удалось сохранить событие");
    } finally {
      setSavingEvent(false);
    }
  };

  const deleteEvent = async (eventId: number) => {
    if (!confirm("Удалить событие?")) return;
    try {
      await deleteJson(`/calendar/events/${eventId}`);
      if (editingEventId === eventId) resetEventForm();
      await loadCalendarData();
    } catch (err) {
      console.error("Error deleting event:", err);
      toast.error("Не удалось удалить событие");
    }
  };

  const saveNote = async () => {
    if (!noteText.trim()) return;
    setSavingNote(true);
    try {
      if (selectedDayNote) {
        await deleteJson(`/calendar/notes/${selectedDayNote.id}`);
      }
      await postJson("/calendar/notes", {
        date: selectedDate,
        note_text: noteText.trim(),
      });
      await loadCalendarData();
    } catch (err) {
      console.error("Error saving note:", err);
      toast.error("Не удалось сохранить запись");
    } finally {
      setSavingNote(false);
    }
  };

  const deleteNote = async () => {
    if (!selectedDayNote) return;
    if (!confirm("Удалить запись?")) return;
    try {
      await deleteJson(`/calendar/notes/${selectedDayNote.id}`);
      setNoteText("");
      await loadCalendarData();
    } catch (err) {
      console.error("Error deleting note:", err);
      toast.error("Не удалось удалить запись");
    }
  };

  if (authLoading || loading) {
    return (
      <ProductPageScreen testId="calendar-page" title="Личный календарь" loading loadingLabel="Загрузка…" />
    );
  }

  if (!isAuthenticated) {
    return (
      <ProductPageScreen
        testId="calendar-page"
        title="Личный календарь"
        guest={{
          message: "Войди, чтобы собирать события, записи дня, слой цикла и карты ритма в одном календаре.",
          ctaHref: "/auth?redirect=/calendar",
          ctaLabel: "Войти",
        }}
      />
    );
  }

  return (
    <ProductPageScreen
      testId="calendar-page"
      eyebrow="Calendar Hub"
      title="Календарь периода без перегрузки"
      subtitle="Один экран для месяца: события, запись дня, слой цикла и следы привычек. Сначала видишь ритм периода, затем открываешь конкретный день."
      contentClassName={`${pl.content} ${pl.legacyHost}`}
      mainWide
    >
      <div style={{ display: "flex", gap: "0.45rem", flexWrap: "wrap" }}>
        <DsButton href="/today" size="sm">
          К Today
        </DsButton>
        <DsButton href="/cycle" variant="secondary" size="sm">
          Цикл
        </DsButton>
        <DsButton href="/habits" variant="secondary" size="sm">
          Карта привычек
        </DsButton>
      </div>

      <div style={{ display: "grid", gap: "var(--orbit-space-lg)" }}>
        <section className={pl.panel}>
          <div style={{ display: "flex", gap: "0.45rem", flexWrap: "wrap", marginBottom: "0.7rem" }}>
            <button type="button" className="orbit-button orbit-button-secondary orbit-button-sm" onClick={() => setCurrentDate(shiftMonth(currentDate, -1))}>
              ←
            </button>
            <button type="button" className="orbit-button orbit-button-secondary orbit-button-sm" onClick={() => setCurrentDate(new Date())}>
              Сегодня
            </button>
            <button type="button" className="orbit-button orbit-button-secondary orbit-button-sm" onClick={() => setCurrentDate(shiftMonth(currentDate, 1))}>
              →
            </button>
          </div>
          <p className="orbit-body-sm" style={{ margin: 0, color: "#5f4323", fontWeight: 700 }}>
            {currentDate.toLocaleDateString("ru-RU", { month: "long", year: "numeric" })}
          </p>
          <div style={{ display: "grid", gap: "0.4rem", marginTop: "0.7rem" }}>
            <label className="orbit-body-xs" style={{ display: "flex", gap: "0.5rem", alignItems: "center", color: "#6f5c45" }}>
              <input type="checkbox" checked={cycleTrackingEnabled} onChange={(e) => setCycleTrackingEnabled(e.target.checked)} />
              Показать слой цикла
            </label>
            <label className="orbit-body-xs" style={{ display: "flex", gap: "0.5rem", alignItems: "center", color: "#6f5c45" }}>
              <input type="checkbox" checked={showTrackerLayer} onChange={(e) => setShowTrackerLayer(e.target.checked)} />
              Показать карту ритма
            </label>
          </div>
        </section>

        {trackerData?.streaks && Object.keys(trackerData.streaks).length > 0 && (
          <section style={{ display: "grid", gap: "0.75rem", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))" }}>
            {[
              { id: "practice", label: "Практики" },
              { id: "affirmation", label: "Аффирмации" },
              { id: "asceticism", label: "Аскезы" },
              { id: "diary", label: "Дневник" },
              { id: "ritual", label: "Ритуал" },
            ].map((item) => {
              const streak = trackerData.streaks[item.id] || 0;
              const stat = trackerData.stats[item.id];
              return (
                <div key={item.id} className="orbit-card" style={{ padding: "0.85rem" }}>
                  <p className="orbit-body-xs" style={{ margin: 0, color: "#8f6e43", textTransform: "uppercase", letterSpacing: "0.08em" }}>
                    {item.label}
                  </p>
                  <p className="orbit-body" style={{ margin: "0.35rem 0 0", color: "#352515", fontWeight: 700 }}>
                    {streak} дн.
                  </p>
                  <p className="orbit-body-xs" style={{ margin: "0.3rem 0 0", color: "#64748b" }}>
                    {stat
                      ? `${stat.completed} из ${stat.total} дней с отметкой`
                      : "История только начинается"}
                  </p>
                </div>
              );
            })}
          </section>
        )}

        <section style={{ display: "grid", gap: "var(--orbit-space-lg)", gridTemplateColumns: "minmax(0, 1.55fr) minmax(320px, 0.9fr)" }}>
          <div className="orbit-card" style={{ padding: "0.9rem", overflowX: "auto" }}>
            <div style={{ minWidth: "720px" }}>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(7, 1fr)", marginBottom: "0.35rem" }}>
                {["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"].map((day) => (
                  <div key={day} style={{ padding: "0.5rem", textAlign: "center", color: "#8f6e43", fontWeight: 700, fontSize: "0.82rem" }}>
                    {day}
                  </div>
                ))}
              </div>

              <div style={{ display: "grid", gridTemplateColumns: "repeat(7, 1fr)", gap: "0.45rem" }}>
                {monthDays.map((day) => {
                  const dayDateStr = day.toISOString().split("T")[0];
                  const dayEvents = events.filter((event) => event.date === dayDateStr);
                  const dayNote = notes.find((note) => note.date === dayDateStr);
                  const dayCycle = cycles.find((cycle) => cycle.date === dayDateStr);
                  const trackerDay = trackerData?.days.find((tracker) => tracker.date === dayDateStr) || null;
                  const selected = selectedDate === dayDateStr;
                  const monthMatch = sameMonth(day, currentDate);

                  return (
                    <button
                      key={dayDateStr}
                      type="button"
                      onClick={() => setSelectedDate(dayDateStr)}
                      style={{
                        minHeight: "118px",
                        padding: "0.6rem",
                        textAlign: "left",
                        borderRadius: "16px",
                        border: selected ? "2px solid #c89d62" : isToday(day) ? "2px solid #e0c28e" : "1px solid #ece4d8",
                        background: trackerDay && showTrackerLayer ? "rgba(244,249,255,0.95)" : "#fffdf9",
                        opacity: monthMatch ? 1 : 0.56,
                        cursor: "pointer",
                      }}
                    >
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.45rem" }}>
                        <span style={{ color: monthMatch ? "#352515" : "#9aa3ad", fontWeight: selected || isToday(day) ? 700 : 500 }}>
                          {day.getDate()}
                        </span>
                        <div style={{ display: "flex", gap: "0.2rem", alignItems: "center" }}>
                          {dayCycle && cycleTrackingEnabled && <span style={{ fontSize: "0.72rem" }}>🩸</span>}
                          {trackerDay?.activities.practice?.completed && showTrackerLayer && <span style={{ fontSize: "0.72rem" }}>✦</span>}
                        </div>
                      </div>
                      {dayEvents.slice(0, 2).map((event) => (
                        <div
                          key={event.id}
                          style={{
                            fontSize: "0.72rem",
                            padding: "0.18rem 0.45rem",
                            marginBottom: "0.2rem",
                            background: event.color || "#b58b4f",
                            color: "#fff",
                            borderRadius: "999px",
                            overflow: "hidden",
                            textOverflow: "ellipsis",
                            whiteSpace: "nowrap",
                          }}
                        >
                          {event.time ? `${event.time} ` : ""}
                          {event.title}
                        </div>
                      ))}
                      {dayNote && (
                        <p className="orbit-body-xs" style={{ margin: "0.25rem 0 0", color: "#6b7280", lineHeight: 1.4 }}>
                          📝 {dayNote.note_text.slice(0, 20)}
                          {dayNote.note_text.length > 20 ? "…" : ""}
                        </p>
                      )}
                    </button>
                  );
                })}
              </div>
            </div>
          </div>

          <aside className="orbit-card" style={{ padding: "1rem", alignSelf: "start", position: "sticky", top: "84px" }}>
            <h2 className="orbit-heading-2" style={{ marginBottom: "0.45rem", fontSize: "1.08rem", color: "#5f4323" }}>
              {new Date(`${selectedDate}T12:00:00`).toLocaleDateString("ru-RU", { weekday: "long", day: "numeric", month: "long" })}
            </h2>

            <div style={{ display: "grid", gap: "0.75rem" }}>
              <div style={{ padding: "0.85rem", borderRadius: "16px", background: "#fffdf9", border: "1px solid #ece4d8" }}>
                <p className="orbit-body-xs" style={{ margin: 0, color: "#8f6e43", textTransform: "uppercase", letterSpacing: "0.08em" }}>
                  Событие дня
                </p>
                <div style={{ display: "grid", gap: "0.45rem", marginTop: "0.6rem" }}>
                  <input
                    value={eventTitle}
                    onChange={(e) => setEventTitle(e.target.value)}
                    placeholder="Название события"
                    className="orbit-input"
                  />
                  <input value={eventTime} onChange={(e) => setEventTime(e.target.value)} type="time" className="orbit-input" />
                  <input
                    value={eventCategory}
                    onChange={(e) => setEventCategory(e.target.value)}
                    placeholder="Категория"
                    className="orbit-input"
                  />
                  <div style={{ display: "flex", gap: "0.45rem", flexWrap: "wrap" }}>
                    <button type="button" onClick={saveEvent} disabled={savingEvent || !eventTitle.trim()} className="orbit-button orbit-button-primary orbit-button-sm">
                      {editingEventId ? "Обновить" : "Сохранить"}
                    </button>
                    {editingEventId && (
                      <button type="button" onClick={resetEventForm} className="orbit-button orbit-button-secondary orbit-button-sm">
                        Сбросить
                      </button>
                    )}
                  </div>
                </div>
                <div style={{ display: "grid", gap: "0.4rem", marginTop: "0.7rem" }}>
                  {selectedDayEvents.length === 0 ? (
                    <p className="orbit-body-xs" style={{ margin: 0, color: "#64748b" }}>
                      На этот день событий пока нет.
                    </p>
                  ) : (
                    selectedDayEvents.map((event) => (
                      <div key={event.id} style={{ display: "flex", gap: "0.35rem", alignItems: "center" }}>
                        <button type="button" onClick={() => handleSelectEvent(event)} className="orbit-button orbit-button-secondary orbit-button-sm" style={{ flex: 1, justifyContent: "flex-start" }}>
                          {event.time ? `${event.time} ` : ""}
                          {event.title}
                        </button>
                        <button type="button" onClick={() => deleteEvent(event.id)} className="orbit-button orbit-button-secondary orbit-button-sm">
                          ×
                        </button>
                      </div>
                    ))
                  )}
                </div>
              </div>

              <div style={{ padding: "0.85rem", borderRadius: "16px", background: "#fffdf9", border: "1px solid #ece4d8" }}>
                <p className="orbit-body-xs" style={{ margin: 0, color: "#8f6e43", textTransform: "uppercase", letterSpacing: "0.08em" }}>
                  Запись дня
                </p>
                <textarea
                  value={noteText}
                  onChange={(e) => setNoteText(e.target.value)}
                  placeholder="О чем этот день, что важно запомнить, что почувствовалось?"
                  style={{
                    width: "100%",
                    minHeight: "110px",
                    marginTop: "0.6rem",
                    padding: "0.85rem 0.95rem",
                    borderRadius: "16px",
                    border: "1px solid #ece4d8",
                    background: "#ffffff",
                    color: "#334155",
                    resize: "vertical",
                  }}
                />
                <div style={{ display: "flex", gap: "0.45rem", flexWrap: "wrap", marginTop: "0.6rem" }}>
                  <button type="button" onClick={saveNote} disabled={savingNote || !noteText.trim()} className="orbit-button orbit-button-primary orbit-button-sm">
                    Сохранить запись
                  </button>
                  {selectedDayNote && (
                    <button type="button" onClick={deleteNote} className="orbit-button orbit-button-secondary orbit-button-sm">
                      Удалить
                    </button>
                  )}
                </div>
              </div>

              {cycleTrackingEnabled && (
                <div style={{ padding: "0.85rem", borderRadius: "16px", background: "#fffdf9", border: "1px solid #ece4d8" }}>
                  <p className="orbit-body-xs" style={{ margin: 0, color: "#8f6e43", textTransform: "uppercase", letterSpacing: "0.08em" }}>
                    Слой цикла
                  </p>
                  {selectedDayCycle ? (
                    <div style={{ display: "grid", gap: "0.35rem", marginTop: "0.6rem" }}>
                      <p className="orbit-body-xs" style={{ margin: 0, color: "#475569" }}>
                        День цикла: {selectedDayCycle.cycle_day ?? "—"}
                      </p>
                      <p className="orbit-body-xs" style={{ margin: 0, color: "#475569" }}>
                        Интенсивность: {selectedDayCycle.period_intensity || "нет"}
                      </p>
                      <p className="orbit-body-xs" style={{ margin: 0, color: "#475569" }}>
                        {selectedDayCycle.ovulation ? "Овуляция" : "Без овуляции"} • {selectedDayCycle.fertile_window ? "фертильное окно" : "обычный день"}
                      </p>
                    </div>
                  ) : (
                    <p className="orbit-body-xs" style={{ margin: "0.6rem 0 0", color: "#64748b" }}>
                      На эту дату слой цикла не заполнен.
                    </p>
                  )}
                </div>
              )}

              {showTrackerLayer && (
                <div style={{ padding: "0.85rem", borderRadius: "16px", background: "#fffdf9", border: "1px solid #ece4d8" }}>
                  <p className="orbit-body-xs" style={{ margin: 0, color: "#8f6e43", textTransform: "uppercase", letterSpacing: "0.08em" }}>
                    Следы дня
                  </p>
                  {selectedDayTracker ? (
                    <div style={{ display: "grid", gap: "0.45rem", marginTop: "0.6rem" }}>
                      {typeof selectedDayTracker.mood === "number" && (
                        <p className="orbit-body-xs" style={{ margin: 0, color: "#475569" }}>
                          Настроение: {selectedDayTracker.mood}/5
                        </p>
                      )}
                      <div style={{ display: "flex", gap: "0.35rem", flexWrap: "wrap" }}>
                        {selectedDayTracker.activities.practice?.completed && <span>🧘</span>}
                        {selectedDayTracker.activities.affirmation?.completed && <span>✨</span>}
                        {selectedDayTracker.activities.asceticism?.completed && <span>🔥</span>}
                        {selectedDayTracker.activities.diary?.completed && <span>📝</span>}
                        {selectedDayTracker.activities.ritual?.completed && <span>🌙</span>}
                      </div>
                    </div>
                  ) : (
                    <p className="orbit-body-xs" style={{ margin: "0.6rem 0 0", color: "#64748b" }}>
                      На этот день активности не отмечены.
                    </p>
                  )}
                  <Link href={`/tracking/calendar?date=${selectedDate}`} className="orbit-button orbit-button-secondary orbit-button-sm" style={{ marginTop: "0.6rem", textDecoration: "none", display: "inline-flex" }}>
                    Открыть карту дня
                  </Link>
                </div>
              )}
            </div>
          </aside>
        </section>
      </div>
    </ProductPageScreen>
  );
}

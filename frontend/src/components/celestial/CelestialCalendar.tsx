"use client";

import React, { useState, useMemo } from "react";
import type { PlanetEvent } from "@/lib/types";

interface CelestialCalendarProps {
  events: PlanetEvent[];
}

const PLANET_COLORS: Record<string, string> = {
  "Sun": "#FFD700",
  "Moon": "#C0C0C0",
  "Mercury": "#8C7853",
  "Venus": "#FFC649",
  "Mars": "#FF6B6B",
  "Jupiter": "#FFA500",
  "Saturn": "#FAD5A5",
  "Uranus": "#4FD0E7",
  "Neptune": "#4166F5",
  "Pluto": "#8B008B",
};

export function CelestialCalendar({ events }: CelestialCalendarProps) {
  const [selectedMonth, setSelectedMonth] = useState(new Date());
  const [filterPlanet, setFilterPlanet] = useState<string | null>(null);
  const [filterType, setFilterType] = useState<string | null>(null);

  // Группируем события по датам
  const eventsByDate = useMemo(() => {
    const grouped: Record<string, PlanetEvent[]> = {};
    events.forEach((event) => {
      const date = new Date(event.timestamp).toISOString().split("T")[0];
      if (!grouped[date]) {
        grouped[date] = [];
      }
      grouped[date].push(event);
    });
    return grouped;
  }, [events]);

  // Фильтруем события
  const filteredEvents = useMemo(() => {
    return events.filter((event) => {
      if (filterPlanet && event.planet !== filterPlanet) return false;
      if (filterType && !event.event_type.toLowerCase().includes(filterType.toLowerCase())) return false;
      return true;
    });
  }, [events, filterPlanet, filterType]);

  // Получаем уникальные планеты и типы событий
  const planets = useMemo(() => {
    const unique = Array.from(new Set(events.map((e) => e.planet))).sort();
    return unique;
  }, [events]);

  const eventTypes = useMemo(() => {
    const unique = Array.from(new Set(events.map((e) => e.event_type))).sort();
    return unique;
  }, [events]);

  // Генерируем календарную сетку для выбранного месяца
  const calendarDays = useMemo(() => {
    const year = selectedMonth.getFullYear();
    const month = selectedMonth.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const daysInMonth = lastDay.getDate();
    const startingDayOfWeek = firstDay.getDay();

    const days: Array<{ date: Date; events: PlanetEvent[] }> = [];

    // Пустые ячейки для дней до начала месяца
    for (let i = 0; i < startingDayOfWeek; i++) {
      days.push({ date: new Date(year, month, -i), events: [] });
    }

    // Дни месяца
    for (let day = 1; day <= daysInMonth; day++) {
      const date = new Date(year, month, day);
      const dateStr = date.toISOString().split("T")[0];
      const dayEvents = filteredEvents.filter((event) => {
        const eventDate = new Date(event.timestamp).toISOString().split("T")[0];
        return eventDate === dateStr;
      });
      days.push({ date, events: dayEvents });
    }

    return days;
  }, [selectedMonth, filteredEvents]);

  const monthNames = [
    "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
    "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
  ];

  const weekDays = ["Вс", "Пн", "Вт", "Ср", "Чт", "Пт", "Сб"];

  const changeMonth = (delta: number) => {
    setSelectedMonth(new Date(selectedMonth.getFullYear(), selectedMonth.getMonth() + delta, 1));
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "var(--orbit-space-lg)" }}>
      {/* Фильтры */}
      <div style={{ display: "flex", flexDirection: "column", gap: "var(--orbit-space-md)" }}>
        <div style={{ display: "flex", flexWrap: "wrap", gap: "var(--orbit-space-sm)" }}>
          <select
            value={filterPlanet || ""}
            onChange={(e) => setFilterPlanet(e.target.value || null)}
            className="orbit-input"
            style={{ minWidth: "150px" }}
          >
            <option value="">Все планеты</option>
            {planets.map((planet) => (
              <option key={planet} value={planet}>
                {planet}
              </option>
            ))}
          </select>
          <select
            value={filterType || ""}
            onChange={(e) => setFilterType(e.target.value || null)}
            className="orbit-input"
            style={{ minWidth: "150px" }}
          >
            <option value="">Все типы</option>
            {eventTypes.map((type) => (
              <option key={type} value={type}>
                {type}
              </option>
            ))}
          </select>
          {(filterPlanet || filterType) && (
            <button
              onClick={() => {
                setFilterPlanet(null);
                setFilterType(null);
              }}
              className="orbit-button orbit-button-secondary orbit-button-xs"
            >
              Сбросить
            </button>
          )}
        </div>
      </div>

      {/* Календарь */}
      <div className="orbit-card" style={{ padding: "var(--orbit-space-lg)" }}>
        {/* Навигация по месяцам */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "var(--orbit-space-md)" }}>
          <button
            onClick={() => changeMonth(-1)}
            className="orbit-button orbit-button-secondary orbit-button-xs"
          >
            ←
          </button>
          <h3 className="orbit-display-xs">
            {monthNames[selectedMonth.getMonth()]} {selectedMonth.getFullYear()}
          </h3>
          <button
            onClick={() => changeMonth(1)}
            className="orbit-button orbit-button-secondary orbit-button-xs"
          >
            →
          </button>
        </div>

        {/* Заголовки дней недели */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(7, 1fr)", gap: "var(--orbit-space-xs)", marginBottom: "var(--orbit-space-xs)" }}>
          {weekDays.map((day) => (
            <div key={day} className="orbit-body-xs orbit-text-muted" style={{ textAlign: "center", fontWeight: 600 }}>
              {day}
            </div>
          ))}
        </div>

        {/* Дни календаря */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(7, 1fr)", gap: "var(--orbit-space-xs)" }}>
          {calendarDays.map((day, idx) => {
            const isCurrentMonth = day.date.getMonth() === selectedMonth.getMonth();
            const isToday = day.date.toDateString() === new Date().toDateString();
            const dayNumber = day.date.getDate();

            return (
              <div
                key={idx}
                style={{
                  minHeight: "80px",
                  padding: "var(--orbit-space-xs)",
                  border: isToday ? "2px solid var(--orbit-color-primary)" : "1px solid var(--orbit-color-border)",
                  borderRadius: "var(--orbit-radius-sm)",
                  background: isCurrentMonth ? "white" : "var(--orbit-color-mist)",
                  opacity: isCurrentMonth ? 1 : 0.5,
                  display: "flex",
                  flexDirection: "column",
                  gap: "2px",
                }}
              >
                <div className="orbit-body-xs" style={{ fontWeight: isToday ? 600 : 400 }}>
                  {isCurrentMonth ? dayNumber : ""}
                </div>
                <div style={{ display: "flex", flexDirection: "column", gap: "2px", flex: 1, overflow: "hidden" }}>
                  {day.events.slice(0, 2).map((event, eventIdx) => (
                    <div
                      key={eventIdx}
                      title={`${event.planet}: ${event.event_type}`}
                      style={{
                        fontSize: "10px",
                        padding: "2px 4px",
                        borderRadius: "2px",
                        background: PLANET_COLORS[event.planet] || "var(--orbit-color-slate)",
                        color: "white",
                        overflow: "hidden",
                        textOverflow: "ellipsis",
                        whiteSpace: "nowrap",
                        cursor: "pointer",
                      }}
                    >
                      {event.planet}
                    </div>
                  ))}
                  {day.events.length > 2 && (
                    <div className="orbit-body-xs orbit-text-muted" style={{ fontSize: "10px" }}>
                      +{day.events.length - 2}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Список событий выбранного месяца */}
      {filteredEvents.length > 0 && (
        <div className="orbit-card" style={{ padding: "var(--orbit-space-lg)" }}>
          <h3 className="orbit-display-xs" style={{ marginBottom: "var(--orbit-space-md)" }}>
            События {monthNames[selectedMonth.getMonth()]}
          </h3>
          <div style={{ display: "flex", flexDirection: "column", gap: "var(--orbit-space-md)" }}>
            {filteredEvents
              .filter((event) => {
                const eventDate = new Date(event.timestamp);
                return (
                  eventDate.getMonth() === selectedMonth.getMonth() &&
                  eventDate.getFullYear() === selectedMonth.getFullYear()
                );
              })
              .map((event, idx) => (
                <div
                  key={idx}
                  style={{
                    padding: "var(--orbit-space-md)",
                    border: "1px solid var(--orbit-color-border)",
                    borderRadius: "var(--orbit-radius-sm)",
                    borderLeft: `4px solid ${PLANET_COLORS[event.planet] || "var(--orbit-color-slate)"}`,
                  }}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "start", marginBottom: "var(--orbit-space-xs)" }}>
                    <div style={{ display: "flex", alignItems: "center", gap: "var(--orbit-space-sm)" }}>
                      <div
                        style={{
                          width: "12px",
                          height: "12px",
                          borderRadius: "50%",
                          background: PLANET_COLORS[event.planet] || "var(--orbit-color-slate)",
                        }}
                      />
                      <span className="orbit-body" style={{ fontWeight: 600 }}>
                        {event.planet}
                      </span>
                    </div>
                    <span className="orbit-body-sm orbit-text-muted">
                      {new Date(event.timestamp).toLocaleDateString("ru-RU", {
                        day: "numeric",
                        month: "long",
                        hour: "2-digit",
                        minute: "2-digit",
                      })}
                    </span>
                  </div>
                  <p className="orbit-body-sm" style={{ marginBottom: "var(--orbit-space-xs)" }}>
                    {event.event_type}
                  </p>
                  {event.description && (
                    <p className="orbit-body-xs orbit-text-muted">{event.description}</p>
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
              ))}
          </div>
        </div>
      )}
    </div>
  );
}


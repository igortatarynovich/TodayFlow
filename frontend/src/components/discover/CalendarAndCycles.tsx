"use client";

import type { WeeklyInsightResponse } from "@/lib/types";

interface CalendarAndCyclesProps {
  weeklyInsight: WeeklyInsightResponse | null;
}

export function CalendarAndCycles({ weeklyInsight }: CalendarAndCyclesProps) {
  if (!weeklyInsight) return null;

  return (
    <section style={{
      marginBottom: "var(--orbit-space-3xl)",
      paddingTop: "var(--orbit-space-2xl)",
      paddingBottom: "var(--orbit-space-2xl)"
    }}>
      <h2 className="orbit-display-sm" style={{
        fontSize: "clamp(1.5rem, 3vw, 2rem)",
        marginBottom: "var(--orbit-space-lg)",
        color: "#0f172a",
        fontWeight: 500
      }}>
        Календарь и циклы
      </h2>
      <p className="orbit-body-sm orbit-text-muted" style={{
        marginBottom: "var(--orbit-space-lg)",
        lineHeight: 1.6
      }}>
        Твой личный ритм и текущий период
      </p>
      
      <div style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))",
        gap: "var(--orbit-space-lg)"
      }}>
        {/* Лунная фаза */}
        <div className="orbit-card" style={{
          padding: "var(--orbit-space-lg)",
          background: "#ffffff",
          border: "1px solid #e5e0d8"
        }}>
          <div style={{
            display: "flex",
            alignItems: "center",
            gap: "var(--orbit-space-sm)",
            marginBottom: "var(--orbit-space-md)"
          }}>
            <div style={{ fontSize: "1.5rem" }}>🌙</div>
            <h3 className="orbit-body" style={{
              fontWeight: 600,
              color: "#0f172a"
            }}>
              Лунная фаза
            </h3>
          </div>
          <p className="orbit-body-sm" style={{
            color: "#334155",
            marginBottom: "var(--orbit-space-sm)",
            fontWeight: 500
          }}>
            {weeklyInsight.insight.phase_name}
          </p>
          {weeklyInsight.next_phase && (
            <p className="orbit-body-xs orbit-text-muted" style={{
              lineHeight: 1.6
            }}>
              Следующая фаза: {weeklyInsight.next_phase.name} через {weeklyInsight.next_phase.in_days} {weeklyInsight.next_phase.in_days === 1 ? 'день' : weeklyInsight.next_phase.in_days < 5 ? 'дня' : 'дней'}
            </p>
          )}
        </div>

        {/* Текущий период */}
        <div className="orbit-card" style={{
          padding: "var(--orbit-space-lg)",
          background: "#fefcf9",
          border: "1px solid #b87333"
        }}>
          <div style={{
            display: "flex",
            alignItems: "center",
            gap: "var(--orbit-space-sm)",
            marginBottom: "var(--orbit-space-md)"
          }}>
            <div style={{ fontSize: "1.5rem" }}>📅</div>
            <h3 className="orbit-body" style={{
              fontWeight: 600,
              color: "#0f172a"
            }}>
              Текущий период
            </h3>
          </div>
          <p className="orbit-body-sm" style={{
            color: "#334155",
            marginBottom: "var(--orbit-space-sm)",
            fontWeight: 500
          }}>
            {weeklyInsight.insight.title}
          </p>
          {weeklyInsight.insight.summary && (
            <p className="orbit-body-xs orbit-text-muted" style={{
              lineHeight: 1.6
            }}>
              {weeklyInsight.insight.summary}
            </p>
          )}
          {weeklyInsight.insight.axis_label && (
            <p className="orbit-body-xs orbit-text-muted" style={{
              lineHeight: 1.6,
              marginTop: "var(--orbit-space-sm)",
              fontStyle: "italic"
            }}>
              Связано с: {weeklyInsight.insight.axis_label}
            </p>
          )}

          {/* Следующий переход */}
          {weeklyInsight.next_phase && (
            <div className="orbit-card" style={{
              padding: "var(--orbit-space-lg)",
              background: "#ffffff",
              border: "1px solid #e5e0d8"
            }}>
              <div style={{
                display: "flex",
                alignItems: "center",
                gap: "var(--orbit-space-sm)",
                marginBottom: "var(--orbit-space-md)"
              }}>
                <div style={{ fontSize: "1.5rem" }}>➡️</div>
                <h3 className="orbit-body" style={{
                  fontWeight: 600,
                  color: "#0f172a"
                }}>
                  Следующий переход
                </h3>
              </div>
              <p className="orbit-body-sm" style={{
                color: "#334155",
                marginBottom: "var(--orbit-space-sm)",
                fontWeight: 500
              }}>
                {weeklyInsight.next_phase.name}
              </p>
              <p className="orbit-body-xs orbit-text-muted" style={{
                lineHeight: 1.6
              }}>
                {new Date(weeklyInsight.next_phase.date).toLocaleDateString('ru-RU', { day: 'numeric', month: 'long' })}
              </p>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}


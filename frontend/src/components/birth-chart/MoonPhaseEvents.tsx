"use client";

import { OrientationRail } from "@/components/orbit";
import { t } from "@/lib/i18n";
import type { MoonPhaseResponse } from "@/lib/types";

interface MoonPhaseEventsProps {
  moonPhase: MoonPhaseResponse | null;
  showResults: boolean;
}

export function MoonPhaseEvents({ moonPhase, showResults }: MoonPhaseEventsProps) {
  if (!moonPhase) return null;

  return (
    <section 
      className="orbit-hero-content-block"
      style={{
        paddingTop: "var(--orbit-space-4xl)",
        paddingBottom: "var(--orbit-space-2xl)",
        opacity: showResults ? 1 : 0,
        transform: showResults ? "translateY(0)" : "translateY(30px)",
        transition: "opacity 0.8s ease, transform 0.8s ease"
      }}
    >
      <div className="orbit-hero-content-container" style={{ gridTemplateColumns: "1fr 1fr", gap: "var(--orbit-space-xl)", maxWidth: "800px" }}>
        <div className="orbit-card" style={{
          opacity: showResults ? 1 : 0,
          transform: showResults ? "translateY(0)" : "translateY(20px)",
          transition: "opacity 0.8s ease 0.1s, transform 0.8s ease 0.1s"
        }}>
          <OrientationRail
            sectionLabel={t("moonPhase.events.currentPhase", "ЛУННАЯ ФАЗА")}
            metaLabel={t("moonPhase.events.current", "Текущая")}
          />
          <div style={{ marginTop: "var(--orbit-space-md)" }}>
            <h3 className="orbit-display-xs" style={{ marginBottom: "var(--orbit-space-xs)" }}>
              {moonPhase.current?.name || "Новолуние"}
            </h3>
            <p className="orbit-body-sm orbit-text-muted">
              День {moonPhase.current?.cycle_day || 0} цикла
            </p>
            {moonPhase.next_phase && (
              <p className="orbit-body-sm" style={{ marginTop: "var(--orbit-space-sm)", color: "var(--orbit-color-slate)" }}>
                Следующая фаза: <strong>{moonPhase.next_phase.name}</strong> через {moonPhase.next_phase.in_days} {moonPhase.next_phase.in_days === 1 ? "день" : moonPhase.next_phase.in_days < 5 ? "дня" : "дней"}
              </p>
            )}
          </div>
        </div>

        <div className="orbit-card" style={{
          opacity: showResults ? 1 : 0,
          transform: showResults ? "translateY(0)" : "translateY(20px)",
          transition: "opacity 0.8s ease 0.2s, transform 0.8s ease 0.2s"
        }}>
          <OrientationRail
            sectionLabel={t("moonPhase.events.upcoming", "ГРЯДУЩИЕ СОБЫТИЯ")}
            metaLabel={t("moonPhase.events.nearest", "Ближайшие")}
          />
          <div style={{ marginTop: "var(--orbit-space-md)" }}>
            <p className="orbit-body-sm orbit-text-muted">
              {new Date().toLocaleDateString("ru-RU", { 
                weekday: "long", 
                year: "numeric", 
                month: "long", 
                day: "numeric" 
              })}
            </p>
            <p className="orbit-body-sm" style={{ marginTop: "var(--orbit-space-sm)", color: "var(--orbit-color-slate)" }}>
              Благоприятное время для новых начинаний и планирования
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}


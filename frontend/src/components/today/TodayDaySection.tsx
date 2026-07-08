"use client";

import Link from "next/link";
import { SectionGlyph } from "@/components/orbit/SectionGlyph";
import { DaySectionHeader, PhaseCard, PhaseEmptyState } from "@/components/today/TodaySectionPrimitives";
import { PhaseStateCheckIn, QuickJournalEntry, QuickStateTracker } from "@/components/today/TodayQuickActions";
import { formatDayJournalMoreEntriesCta, RITUAL_COPY } from "@/components/today/todayRitualCopy";
import { stagePanelStyle, type TodayCycleData } from "@/components/today/todayPageUtils";

type TodayDaySectionProps = {
  todayData: TodayCycleData;
  expanded: boolean;
  onToggleExpanded: () => void;
  onReloadToday: () => void;
};

export function TodayDaySection({ todayData, expanded, onToggleExpanded, onReloadToday }: TodayDaySectionProps) {
  const visibleEntries = todayData.day_journal_entries.slice(0, 2);
  const hiddenEntriesCount = Math.max(0, todayData.day_journal_entries.length - visibleEntries.length);

  return (
    <section id="checkin-section" className="todayflow-reveal" style={{ marginBottom: "var(--orbit-space-3xl)" }}>
      <style jsx>{`
        @media (max-width: 768px) {
          .today-day-intention {
            padding: 0.72rem 0.8rem !important;
            margin-bottom: 0.75rem !important;
          }

          .today-day-log-wrap {
            margin: 0.85rem 0 !important;
          }

          .today-day-log-grid {
            gap: 0.55rem !important;
          }

          .today-day-log-details {
            padding: 0.7rem 0.75rem !important;
          }

          .today-day-log-details :global(.orbit-button),
          .today-day-log-wrap :global(.orbit-button) {
            width: 100%;
            justify-content: center;
          }
        }
      `}</style>
      <div className="todayflow-stage" style={stagePanelStyle(todayData.day_completed, expanded)}>
        <DaySectionHeader icon={<SectionGlyph type="day" size="lg" />} title={RITUAL_COPY.daySectionTitle} done={todayData.day_completed} expanded={expanded} onToggle={onToggleExpanded} />

        {expanded ? (
          <div>
            <div
              style={{
                marginBottom: "var(--orbit-space-md)",
                padding: "0.75rem 0.85rem",
                borderRadius: "14px",
                background: "rgba(255,255,255,0.88)",
                border: "1px solid rgba(202, 177, 137, 0.22)",
              }}
            >
              <p className="orbit-body-xs" style={{ margin: 0, color: "#8a6f49", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.06em" }}>
                {RITUAL_COPY.dayStepLogicEyebrow}
              </p>
              <p className="orbit-body-xs" style={{ margin: "0.35rem 0 0", color: "#6a5132", lineHeight: 1.55 }}>
                {RITUAL_COPY.dayStepLogicBody}
              </p>
            </div>
            {todayData.day_connection?.morning_intention ? (
              <div
                className="today-day-intention"
                style={{
                  marginBottom: "var(--orbit-space-md)",
                  padding: "0.8rem 0.95rem",
                  borderRadius: "14px",
                  background: "rgba(255, 248, 235, 0.96)",
                  border: "1px solid rgba(202, 177, 137, 0.28)",
                }}
              >
                <p className="orbit-body-xs" style={{ margin: 0, color: "#8a6f49", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.06em" }}>
                  {RITUAL_COPY.dayIntentionEyebrow}
                </p>
                <p className="orbit-body-sm" style={{ margin: "0.35rem 0 0", color: "#5e4222", lineHeight: 1.6 }}>
                  &ldquo;{todayData.day_connection.morning_intention}&rdquo;
                </p>
              </div>
            ) : null}

            <PhaseStateCheckIn
              date={todayData.date}
              phase="day"
              title={RITUAL_COPY.dayPhaseCheckInTitle}
              hint={RITUAL_COPY.dayPhaseCheckInHint}
              onSaved={onReloadToday}
            />

            <div className="today-day-log-wrap" style={{ margin: "var(--orbit-space-lg) 0" }}>
            <PhaseCard title={RITUAL_COPY.dayPhaseJournalTitle} subtitle={RITUAL_COPY.dayPhaseJournalSubtitle}>
                <div className="today-day-log-grid" style={{ display: "grid", gap: "var(--orbit-space-sm)" }}>
                  <QuickStateTracker date={todayData.date} onTrackerCreated={onReloadToday} />
                  <QuickJournalEntry date={todayData.date} onEntryCreated={onReloadToday} />
                </div>
                {visibleEntries.length > 0 ? (
                  <details
                    className="today-day-log-details"
                    style={{
                      marginTop: "var(--orbit-space-md)",
                      padding: "0.75rem 0.8rem",
                      borderRadius: "14px",
                      background: "rgba(255,255,255,0.82)",
                      border: "1px solid rgba(202, 177, 137, 0.24)",
                    }}
                  >
                    <summary className="orbit-body-sm" style={{ cursor: "pointer", color: "#5f4323", fontWeight: 700 }}>
                      {RITUAL_COPY.dayJournalFixedSummary}
                    </summary>
                    <div style={{ marginTop: "0.65rem", display: "flex", flexDirection: "column", gap: "var(--orbit-space-sm)" }}>
                      {visibleEntries.map((entry: any) => (
                        <div key={entry.id} style={{ padding: "var(--orbit-space-md)", background: "rgba(255, 252, 247, 0.95)", borderRadius: "8px", border: "1px solid rgba(202, 177, 137, 0.24)" }}>
                          <p className="orbit-body-sm" style={{ color: "#8a6f49", marginBottom: "var(--orbit-space-xs)" }}>
                            {entry.type === "observation"
                              ? RITUAL_COPY.dayJournalTypeObservation
                              : entry.type === "gratitude"
                                ? RITUAL_COPY.dayJournalTypeGratitude
                                : RITUAL_COPY.dayJournalTypeInsight}
                          </p>
                          <p className="orbit-body" style={{ color: "#6a5132" }}>{entry.content}</p>
                        </div>
                      ))}
                      {hiddenEntriesCount > 0 ? (
                        <Link href="/journal" className="orbit-button orbit-button-secondary orbit-button-sm" style={{ textDecoration: "none", alignSelf: "flex-start" }}>
                          {formatDayJournalMoreEntriesCta(hiddenEntriesCount)}
                        </Link>
                      ) : null}
                    </div>
                  </details>
                ) : null}
              </PhaseCard>
            </div>
          </div>
        ) : null}

        {expanded && !todayData.day_trackers.length && !todayData.day_journal_entries.length ? (
          <PhaseEmptyState text={RITUAL_COPY.dayEmptyNoMarkers} />
        ) : null}
      </div>
    </section>
  );
}

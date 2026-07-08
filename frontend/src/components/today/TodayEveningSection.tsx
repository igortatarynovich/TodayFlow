"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { getJson } from "@/lib/api";
import { SectionGlyph } from "@/components/orbit/SectionGlyph";
import { DaySectionHeader, PhaseEmptyState, inlineAreaStyle } from "@/components/today/TodaySectionPrimitives";
import { stagePanelStyle, type TodayCycleData } from "@/components/today/todayPageUtils";
import { PhaseStateCheckIn } from "@/components/today/TodayQuickActions";
import { LoadingSpinner } from "@/components/orbit";
import { narrativeString } from "@/lib/todayNarrativeApi";
import {
  formatEveningOutlookGoalStepsChip,
  formatEveningOutlookHabitsChip,
  RITUAL_COPY,
} from "@/components/today/todayRitualCopy";

type DayOutlookPhaseDetail = {
  phase: string;
  empty?: boolean;
  mood_scale?: number | null;
  energy_scale?: number | null;
  stress_scale?: number | null;
  has_note?: boolean;
};

type DayOutlookPayload = {
  date: string;
  paragraphs: string[];
  phases: Record<string, boolean>;
  signals: Record<string, unknown>;
  phase_details?: DayOutlookPhaseDetail[];
};

const PHASE_GLYPH: Record<string, string> = {
  morning: "☀",
  day: "◉",
  evening: "☽",
};

function PhaseScaleDots({ label, value }: { label: string; value: number | null | undefined }) {
  const n = typeof value === "number" && value >= 1 && value <= 5 ? value : null;
  return (
    <div style={{ marginTop: "0.28rem" }}>
      <p className="orbit-body-xs" style={{ margin: "0 0 0.2rem", color: "#9a7b52", letterSpacing: "0.04em", fontSize: "0.65rem", textTransform: "uppercase" }}>
        {label}
      </p>
      <div style={{ display: "flex", gap: "3px", justifyContent: "center" }}>
        {[1, 2, 3, 4, 5].map((i) => (
          <span
            key={i}
            aria-hidden
            style={{
              width: "7px",
              height: "7px",
              borderRadius: "50%",
              background: n !== null && i <= n ? "linear-gradient(145deg, #c9a227, #8b5a2b)" : "rgba(148, 124, 96, 0.22)",
              boxShadow: n !== null && i <= n ? "0 0 0 1px rgba(255,250,240,0.9)" : "none",
            }}
          />
        ))}
      </div>
    </div>
  );
}

function EveningDayOutlook({ date, tick, outlookPreamble }: { date: string; tick: number; outlookPreamble?: string }) {
  const [data, setData] = useState<DayOutlookPayload | null>(null);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    getJson<DayOutlookPayload>(`/tracking/day-outlook/${date}`)
      .then((d) => {
        if (!cancelled) {
          setData(d);
          setErr(null);
        }
      })
      .catch(() => {
        if (!cancelled) setErr(RITUAL_COPY.eveningOutlookLoadError);
      });
    return () => {
      cancelled = true;
    };
  }, [date, tick]);

  if (err) {
    return <p className="orbit-body-xs" style={{ color: "#b45309" }}>{err}</p>;
  }
  if (!data) {
    return <p className="orbit-body-xs" style={{ color: "#8a6f49" }}>{RITUAL_COPY.eveningOutlookLoading}</p>;
  }

  const signals = data.signals || {};
  const hasIntention = Boolean(signals.morning_intention);
  const hasDc = Boolean(signals.day_connection);
  const goalSteps = Number(signals.goal_steps) || 0;
  const habitsDone = Number(signals.habits_done) || 0;

  const phaseOrder = ["morning", "day", "evening"] as const;
  const details: DayOutlookPhaseDetail[] =
    Array.isArray(data.phase_details) && data.phase_details.length >= 3
      ? data.phase_details
      : phaseOrder.map((phase) => ({
          phase,
          empty: !Boolean(data.phases?.[phase]),
          mood_scale: null,
          energy_scale: null,
          stress_scale: null,
          has_note: false,
        }));

  return (
    <div
      style={{
        marginBottom: "var(--orbit-space-lg)",
        borderRadius: "22px",
        border: "1px solid rgba(201, 168, 115, 0.42)",
        background: "linear-gradient(165deg, rgba(255, 253, 248, 0.99) 0%, rgba(252, 244, 228, 0.88) 45%, rgba(255, 250, 242, 0.97) 100%)",
        boxShadow: "0 18px 42px -28px rgba(90, 60, 30, 0.35), inset 0 1px 0 rgba(255, 255, 255, 0.85)",
        overflow: "hidden",
      }}
    >
      <div
        style={{
          padding: "1.1rem 1.15rem 0.85rem",
          borderBottom: "1px solid rgba(201, 168, 115, 0.2)",
          background: "linear-gradient(90deg, rgba(255, 248, 235, 0.5) 0%, transparent 55%)",
        }}
      >
        <p className="orbit-body-xs" style={{ margin: 0, color: "#a67c3a", fontWeight: 700, letterSpacing: "0.1em", textTransform: "uppercase" }}>
          {RITUAL_COPY.eveningOutlookSummaryEyebrow}
        </p>
        <h3 className="orbit-heading-3" style={{ margin: "0.35rem 0 0", fontSize: "1.15rem", color: "#3d2a18", fontWeight: 700 }}>
          {RITUAL_COPY.eveningOutlookMapTitle}
        </h3>
        <p className="orbit-body-xs" style={{ margin: "0.45rem 0 0", color: "#6a5132", lineHeight: 1.62, maxWidth: "36rem" }}>
          {outlookPreamble || RITUAL_COPY.eveningOutlookPreambleDefault}
        </p>
      </div>

      <div style={{ padding: "1rem 1rem 0.25rem", position: "relative" }}>
        <svg width="100%" height="28" viewBox="0 0 360 28" preserveAspectRatio="none" aria-hidden style={{ display: "block", opacity: 0.85 }}>
          <defs>
            <linearGradient id={`evening-map-grad-${date}`} x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="rgba(200, 154, 92, 0.35)" />
              <stop offset="50%" stopColor="rgba(184, 134, 11, 0.55)" />
              <stop offset="100%" stopColor="rgba(200, 154, 92, 0.35)" />
            </linearGradient>
          </defs>
          <path
            d="M 48 18 Q 120 4, 180 14 T 312 18"
            fill="none"
            stroke={`url(#evening-map-grad-${date})`}
            strokeWidth="2.2"
            strokeLinecap="round"
          />
        </svg>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(3, minmax(0, 1fr))",
            gap: "0.35rem",
            marginTop: "-0.5rem",
            position: "relative",
            zIndex: 1,
          }}
        >
          {details.map((row) => {
            const hasCheckin =
              row.empty === false ? true : row.empty === true ? false : Boolean(data.phases?.[row.phase]);
            const empty = !hasCheckin;
            const label =
              row.phase === "morning"
                ? RITUAL_COPY.eveningOutlookPhaseMorning
                : row.phase === "day"
                  ? RITUAL_COPY.eveningOutlookPhaseDay
                  : row.phase === "evening"
                    ? RITUAL_COPY.eveningOutlookPhaseEvening
                    : row.phase;
            const g = PHASE_GLYPH[row.phase] || "○";
            return (
              <div key={row.phase} style={{ textAlign: "center", padding: "0 0.2rem" }}>
                <div
                  style={{
                    width: "min(100%, 76px)",
                    aspectRatio: "1",
                    maxWidth: "76px",
                    margin: "0 auto",
                    borderRadius: "50%",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontSize: "1.45rem",
                    lineHeight: 1,
                    boxSizing: "border-box",
                    ...(empty
                      ? {
                          border: "2px dashed rgba(148, 124, 96, 0.45)",
                          background: "rgba(255, 252, 247, 0.5)",
                          color: "rgba(120, 100, 72, 0.55)",
                        }
                      : {
                          border: "2px solid rgba(184, 134, 11, 0.55)",
                          background: "radial-gradient(circle at 35% 28%, rgba(255, 252, 245, 0.95) 0%, rgba(252, 232, 198, 0.55) 48%, rgba(232, 200, 150, 0.35) 100%)",
                          boxShadow: "inset 0 1px 0 rgba(255,255,255,0.75), 0 8px 18px -12px rgba(90, 60, 30, 0.35)",
                          color: "#5c3d1a",
                        }),
                  }}
                >
                  {g}
                </div>
                <p className="orbit-body-xs" style={{ margin: "0.45rem 0 0", fontWeight: 700, color: "#5f4323", letterSpacing: "0.03em" }}>
                  {label}
                </p>
                {empty ? (
                  <p className="orbit-body-xs" style={{ margin: "0.25rem 0 0", color: "#948264", lineHeight: 1.45 }}>
                    {RITUAL_COPY.eveningPhaseNoCheckinYet}
                  </p>
                ) : (
                  <div style={{ marginTop: "0.15rem" }}>
                    <PhaseScaleDots label={RITUAL_COPY.eveningScaleMoodLabel} value={row.mood_scale} />
                    <PhaseScaleDots label={RITUAL_COPY.eveningScaleEnergyLabel} value={row.energy_scale} />
                    <PhaseScaleDots label={RITUAL_COPY.eveningScaleStressLabel} value={row.stress_scale} />
                    {row.has_note ? (
                      <p className="orbit-body-xs" style={{ margin: "0.35rem 0 0", color: "#7a6242", fontStyle: "italic" }}>
                        {RITUAL_COPY.eveningPhaseHasNote}
                      </p>
                    ) : null}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      <div style={{ padding: "0.65rem 1.1rem 1rem", display: "flex", flexWrap: "wrap", gap: "0.4rem", justifyContent: "center" }}>
        {hasDc ? (
          <span className="orbit-body-xs" style={{ padding: "0.28rem 0.55rem", borderRadius: "999px", background: "rgba(255, 248, 235, 0.95)", border: "1px solid rgba(201, 168, 115, 0.35)", color: "#6a5132" }}>
            {RITUAL_COPY.eveningChipDayLine}
          </span>
        ) : null}
        {hasIntention ? (
          <span className="orbit-body-xs" style={{ padding: "0.28rem 0.55rem", borderRadius: "999px", background: "rgba(255, 248, 235, 0.95)", border: "1px solid rgba(201, 168, 115, 0.35)", color: "#6a5132" }}>
            {RITUAL_COPY.eveningChipIntentionSaved}
          </span>
        ) : null}
        {goalSteps > 0 ? (
          <span className="orbit-body-xs" style={{ padding: "0.28rem 0.55rem", borderRadius: "999px", background: "rgba(255, 248, 235, 0.95)", border: "1px solid rgba(201, 168, 115, 0.35)", color: "#6a5132" }}>
            {formatEveningOutlookGoalStepsChip(goalSteps)}
          </span>
        ) : null}
        {habitsDone > 0 ? (
          <span className="orbit-body-xs" style={{ padding: "0.28rem 0.55rem", borderRadius: "999px", background: "rgba(255, 248, 235, 0.95)", border: "1px solid rgba(201, 168, 115, 0.35)", color: "#6a5132" }}>
            {formatEveningOutlookHabitsChip(habitsDone)}
          </span>
        ) : null}
      </div>

      <div
        style={{
          padding: "0.85rem 1.15rem 1.1rem",
          borderTop: "1px solid rgba(201, 168, 115, 0.18)",
          background: "rgba(255, 255, 255, 0.35)",
        }}
      >
        <p className="orbit-body-xs" style={{ margin: "0 0 0.5rem", color: "#a67c3a", fontWeight: 700, letterSpacing: "0.06em", textTransform: "uppercase" }}>
          {RITUAL_COPY.eveningTextSectionEyebrow}
        </p>
        <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
          {data.paragraphs.map((p, i) => (
            <p key={i} className="orbit-body-sm" style={{ margin: 0, color: "#5e4222", lineHeight: 1.62 }}>
              {p}
            </p>
          ))}
        </div>
        <div style={{ marginTop: "0.85rem" }}>
          <Link href={`/tracking/calendar?date=${date}`} className="orbit-button orbit-button-secondary orbit-button-sm" style={{ textDecoration: "none" }}>
            {RITUAL_COPY.eveningOpenCalendarCta}
          </Link>
        </div>
      </div>
    </div>
  );
}

type EveningObservations = {
  noticed: string;
  hardest: string;
  easier_than_expected: string;
};

type TodayEveningSectionProps = {
  eveningNarrative?: Record<string, unknown> | null;
  eveningNarrativeLoading?: boolean;
  todayData: TodayCycleData;
  expanded: boolean;
  eveningCustomPhrase: string;
  eveningMarkedDone: boolean;
  eveningObservations: EveningObservations;
  eveningReflectionInput: string;
  eveningSaving: boolean;
  onToggleExpanded: () => void;
  onEveningCustomPhraseChange: (value: string) => void;
  onEveningMarkedDoneChange: (value: boolean) => void;
  onEveningObservationChange: (field: keyof EveningObservations, value: string) => void;
  onEveningReflectionChange: (value: string) => void;
  onSaveEvening: () => void;
  onRefreshBlock: () => void;
  onEveningPhaseSaved?: () => void;
};

export function TodayEveningSection({
  eveningNarrative = null,
  eveningNarrativeLoading = false,
  todayData,
  expanded,
  eveningCustomPhrase,
  eveningMarkedDone,
  eveningObservations,
  eveningReflectionInput,
  eveningSaving,
  onToggleExpanded,
  onEveningCustomPhraseChange,
  onEveningMarkedDoneChange,
  onEveningObservationChange,
  onEveningReflectionChange,
  onSaveEvening,
  onRefreshBlock,
  onEveningPhaseSaved,
}: TodayEveningSectionProps) {
  const [outlookTick, setOutlookTick] = useState(0);
  const panelIntro = narrativeString(eveningNarrative?.panel_intro);
  const outlookPreamble = narrativeString(eveningNarrative?.outlook_preamble);
  const closureInvite = narrativeString(eveningNarrative?.closure_invitation);

  return (
    <section id="closing-section" className="todayflow-reveal">
      <style jsx>{`
        @media (max-width: 768px) {
          .today-evening-close-card,
          .today-evening-outlook-details,
          .today-evening-extra-details {
            padding: 0.85rem 0.85rem !important;
          }

          .today-evening-actions {
            display: grid !important;
            grid-template-columns: 1fr !important;
          }

          .today-evening-actions :global(.orbit-button) {
            width: 100%;
            justify-content: center;
          }
        }
      `}</style>
      <div className="todayflow-stage" style={stagePanelStyle(todayData.evening_completed, expanded)}>
        <DaySectionHeader icon={<SectionGlyph type="evening" size="lg" />} title={RITUAL_COPY.eveningSectionTitle} done={todayData.evening_completed} expanded={expanded} onToggle={onToggleExpanded} />

        {expanded ? (
          <div>
            {eveningNarrativeLoading ? (
              <div
                style={{
                  marginBottom: "var(--orbit-space-md)",
                  display: "flex",
                  alignItems: "center",
                  gap: "0.6rem",
                  padding: "0.65rem 0.75rem",
                  borderRadius: "12px",
                  background: "rgba(255, 250, 242, 0.95)",
                  border: "1px solid rgba(202, 177, 137, 0.35)",
                }}
              >
                <LoadingSpinner size="sm" />
                <p className="orbit-body-sm" style={{ margin: 0, color: "#6a5132" }}>{RITUAL_COPY.eveningNarrativePreparing}</p>
              </div>
            ) : null}
            {panelIntro ? (
              <p
                className="orbit-body-sm"
                style={{
                  margin: "0 0 var(--orbit-space-md)",
                  color: "#5e4222",
                  lineHeight: 1.65,
                  display: "-webkit-box",
                  WebkitLineClamp: 5,
                  WebkitBoxOrient: "vertical",
                  overflow: "hidden",
                }}
              >
                {panelIntro}
              </p>
            ) : null}
            <div className="today-evening-close-card" style={{ background: "linear-gradient(135deg, #e3c48d 0%, #c89a5c 100%)", borderRadius: "12px", padding: "var(--orbit-space-lg)", color: "#fff9f0", marginBottom: "var(--orbit-space-lg)" }}>
              <p className="orbit-body-sm" style={{ margin: 0, color: "rgba(255,249,240,0.9)" }}>{RITUAL_COPY.eveningClosureCardTitle}</p>
              <textarea
                value={eveningCustomPhrase}
                onChange={(e) => onEveningCustomPhraseChange(e.target.value)}
                placeholder={RITUAL_COPY.eveningClosingPhrasePlaceholder}
                style={{ width: "100%", marginTop: "0.5rem", minHeight: "72px", padding: "var(--orbit-space-sm)", borderRadius: "8px", border: "1px solid rgba(255,249,240,0.45)", background: "rgba(255,249,240,0.15)", color: "#fffdf8", fontFamily: "inherit", fontSize: "0.95rem", resize: "vertical" }}
              />
              <label style={{ display: "flex", alignItems: "center", gap: "0.55rem", marginTop: "0.65rem", cursor: "pointer", color: "#fffdf8" }}>
                <input type="checkbox" checked={eveningMarkedDone} onChange={(e) => onEveningMarkedDoneChange(e.target.checked)} style={{ width: "18px", height: "18px" }} />
                {RITUAL_COPY.eveningMarkedDoneCheckbox}
              </label>
              {eveningMarkedDone ? (
                <p className="orbit-body-xs" style={{ margin: "0.4rem 0 0", color: "rgba(255,249,240,0.92)" }}>{RITUAL_COPY.eveningMarkedDoneEncouragement}</p>
              ) : null}
            </div>

            <PhaseStateCheckIn
              date={todayData.date}
              phase="evening"
              title={RITUAL_COPY.checkInTitle}
              hint={RITUAL_COPY.eveningPhaseCheckInHint}
              onSaved={() => {
                onEveningPhaseSaved?.();
                setOutlookTick((t) => t + 1);
              }}
            />

            <details
              className="today-evening-outlook-details"
              style={{
                marginBottom: "var(--orbit-space-lg)",
                borderRadius: "16px",
                border: "1px solid rgba(202, 177, 137, 0.28)",
                background: "rgba(255,252,247,0.92)",
                padding: "0.85rem 0.95rem",
              }}
            >
              <summary
                className="orbit-body-sm"
                style={{ cursor: "pointer", color: "#5f4323", fontWeight: 700 }}
              >
                {RITUAL_COPY.eveningOpenStateMapSummary}
              </summary>
              <div style={{ marginTop: "0.75rem" }}>
                <EveningDayOutlook date={todayData.date} tick={outlookTick} outlookPreamble={outlookPreamble || undefined} />
              </div>
            </details>

            <div style={{ marginBottom: "var(--orbit-space-lg)" }}>
              <h3 className="orbit-heading-3" style={{ margin: "0 0 var(--orbit-space-sm)", fontSize: "1rem" }}>{RITUAL_COPY.eveningReflectionTitle}</h3>
              <textarea value={eveningReflectionInput} onChange={(e) => onEveningReflectionChange(e.target.value)} placeholder={RITUAL_COPY.eveningReflectionPlaceholder} style={{ ...inlineAreaStyle, minHeight: "110px" }} />
            </div>

            <details
              className="today-evening-extra-details"
              style={{
                marginBottom: "var(--orbit-space-lg)",
                borderRadius: "16px",
                border: "1px solid rgba(202, 177, 137, 0.24)",
                background: "rgba(255,252,247,0.9)",
                padding: "0.85rem 0.95rem",
              }}
            >
              <summary
                className="orbit-body-sm"
                style={{ cursor: "pointer", color: "#5f4323", fontWeight: 700 }}
              >
                {RITUAL_COPY.eveningExtraDetailsSummary}
              </summary>
              <div style={{ marginTop: "0.75rem" }}>
                {closureInvite ? (
                  <p className="orbit-body-sm" style={{ margin: "0 0 var(--orbit-space-sm)", color: "#6a5132", lineHeight: 1.6 }}>
                    {closureInvite}
                  </p>
                ) : null}
                <div style={{ display: "grid", gap: "var(--orbit-space-sm)" }}>
                  <textarea value={eveningObservations.noticed} onChange={(e) => onEveningObservationChange("noticed", e.target.value)} placeholder={RITUAL_COPY.eveningObsPlaceholderNoticed} style={inlineAreaStyle} />
                  <textarea value={eveningObservations.hardest} onChange={(e) => onEveningObservationChange("hardest", e.target.value)} placeholder={RITUAL_COPY.eveningObsPlaceholderHardest} style={inlineAreaStyle} />
                  <textarea value={eveningObservations.easier_than_expected} onChange={(e) => onEveningObservationChange("easier_than_expected", e.target.value)} placeholder={RITUAL_COPY.eveningObsPlaceholderEasier} style={inlineAreaStyle} />
                </div>
              </div>
            </details>

            <div className="today-evening-actions" style={{ display: "flex", gap: "var(--orbit-space-sm)", flexWrap: "wrap", marginBottom: "var(--orbit-space-lg)" }}>
              <button type="button" className="orbit-button orbit-button-primary orbit-button-sm" onClick={onSaveEvening} disabled={eveningSaving}>
                {eveningSaving ? RITUAL_COPY.formSavingShort : RITUAL_COPY.eveningSaveSummaryCta}
              </button>
              <button type="button" className="orbit-button orbit-button-secondary orbit-button-sm" onClick={onRefreshBlock}>
                {RITUAL_COPY.eveningRefreshBlockCta}
              </button>
            </div>

            {todayData.evening && todayData.evening.completed && todayData.evening.closing_phrase_text ? (
              <div style={{ background: "linear-gradient(135deg, #e3c48d 0%, #c89a5c 100%)", borderRadius: "12px", padding: "var(--orbit-space-lg)", marginBottom: "var(--orbit-space-lg)", color: "#fff9f0", textAlign: "center" }}>
                <p className="orbit-body" style={{ color: "rgba(255,249,240,0.96)", margin: 0, fontStyle: "italic", fontSize: "1.125rem", marginBottom: "var(--orbit-space-xs)" }}>
                  &ldquo;{todayData.evening.closing_phrase_text}&rdquo;
                </p>
                <p className="orbit-body-sm" style={{ color: "rgba(255,249,240,0.92)", margin: 0 }}>{RITUAL_COPY.eveningCompletedCheckLine}</p>
              </div>
            ) : null}

            {todayData.day_connection?.morning_intention ? (
              <details style={{ marginTop: "var(--orbit-space-lg)", paddingTop: "var(--orbit-space-lg)", borderTop: "1px solid #e0e0e0" }}>
                <summary className="orbit-body-sm" style={{ cursor: "pointer", color: "#5f4323", fontWeight: 700 }}>
                  {RITUAL_COPY.eveningDayStartLinkSummary}
                </summary>
                <div style={{ marginTop: "var(--orbit-space-md)" }}>
                  <div style={{ background: "rgba(255, 247, 233, 0.96)", borderRadius: "12px", padding: "var(--orbit-space-lg)", marginBottom: "var(--orbit-space-md)", borderLeft: "4px solid #c89a5c" }}>
                    <p className="orbit-body-sm" style={{ color: "#8a6f49", marginBottom: "var(--orbit-space-xs)" }}>{RITUAL_COPY.eveningMorningIntentionRecall}</p>
                    <p className="orbit-body" style={{ color: "#5e4222", fontStyle: "italic", lineHeight: "1.6" }}>&ldquo;{todayData.day_connection.morning_intention}&rdquo;</p>
                  </div>

                  {todayData.day_connection.evening_observations ? (
                    <div style={{ background: "rgba(255, 252, 247, 0.95)", borderRadius: "12px", padding: "var(--orbit-space-lg)", marginBottom: "var(--orbit-space-md)", border: "1px solid rgba(202, 177, 137, 0.32)" }}>
                      <p className="orbit-body-sm" style={{ color: "#8a6f49", marginBottom: "var(--orbit-space-sm)", fontWeight: "600" }}>{RITUAL_COPY.eveningObservationsHeading}</p>
                      {todayData.day_connection.evening_observations.noticed ? (
                        <p className="orbit-body" style={{ color: "#6a5132", marginBottom: "var(--orbit-space-xs)" }}>
                          <strong>{RITUAL_COPY.eveningObsStrongNoticed}</strong> {todayData.day_connection.evening_observations.noticed}
                        </p>
                      ) : null}
                      {todayData.day_connection.evening_observations.hardest ? (
                        <p className="orbit-body" style={{ color: "#6a5132", marginBottom: "var(--orbit-space-xs)" }}>
                          <strong>{RITUAL_COPY.eveningObsStrongHardest}</strong> {todayData.day_connection.evening_observations.hardest}
                        </p>
                      ) : null}
                      {todayData.day_connection.evening_observations.easier_than_expected ? (
                        <p className="orbit-body" style={{ color: "#6a5132" }}>
                          <strong>{RITUAL_COPY.eveningObsStrongEasier}</strong> {todayData.day_connection.evening_observations.easier_than_expected}
                        </p>
                      ) : null}
                    </div>
                  ) : null}

                  {todayData.day_connection.evening_reflection ? (
                    <div style={{ background: "rgba(255, 247, 233, 0.96)", borderRadius: "12px", padding: "var(--orbit-space-lg)", marginBottom: "var(--orbit-space-md)", borderLeft: "4px solid #c89a5c" }}>
                      <p className="orbit-body-sm" style={{ color: "#8a6f49", marginBottom: "var(--orbit-space-xs)", fontWeight: "600" }}>{RITUAL_COPY.eveningReflectionBlockHeading}</p>
                      <p className="orbit-body" style={{ color: "#6a5132", lineHeight: "1.6" }}>{todayData.day_connection.evening_reflection}</p>
                    </div>
                  ) : null}

                  {todayData.day_connection.connection_thread ? (
                    <div style={{ background: "linear-gradient(135deg, rgba(229, 198, 143, 0.2) 0%, rgba(205, 171, 117, 0.2) 100%)", borderRadius: "12px", padding: "var(--orbit-space-lg)", border: "1px solid rgba(202, 177, 137, 0.45)" }}>
                      <p className="orbit-body-sm" style={{ color: "#9b7848", marginBottom: "var(--orbit-space-xs)", fontWeight: "600" }}>{RITUAL_COPY.eveningThreadBlockHeading}</p>
                      <p className="orbit-body" style={{ color: "#6a5132", fontStyle: "italic", lineHeight: "1.6" }}>{todayData.day_connection.connection_thread}</p>
                    </div>
                  ) : null}
                </div>
              </details>
            ) : null}
          </div>
        ) : null}

        {expanded && !todayData.evening ? <PhaseEmptyState text={RITUAL_COPY.eveningEmptyClosingHint} /> : null}
      </div>
    </section>
  );
}

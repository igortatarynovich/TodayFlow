"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { logActiveJTBDAction } from "@/lib/jtbdFeedback";
import { summaryChipStyle } from "@/components/today/TodaySectionPrimitives";
import type { DayQuestionCard, PracticeResponse } from "@/components/today/todayPageUtils";
import { RewardContourBadge } from "@/components/rewards/RewardContourBadge";
import { LoadingSpinner } from "@/components/orbit";
import { narrativeString, narrativeStringArray } from "@/lib/todayNarrativeApi";
import type { WeeklyGoal } from "@/components/today/todayPageUtils";
import type { WeeklyPatternMap } from "@/components/today/todayPageUtils";
import type { TrackerEntityKind } from "@/app/tracking/calendar/trackerEntityCatalog";
import {
  formatWeeklyPatternRecommendation,
  formatWorkingLayerMiniDecisionCaption,
  formatWorkingLayerPracticeDurationHint,
  formatWorkingLayerTimerButton,
  RITUAL_COPY,
  workingLayerRingImpactForDecision,
  workingLayerRingImpactForQuestion,
} from "@/components/today/todayRitualCopy";

type TodayWorkingLayerSectionProps = {
  dayNarrative?: Record<string, unknown> | null;
  dayNarrativeLoading?: boolean;
  nudge: { level: "low" | "medium" | "high"; message: string; ctaHref: string; ctaLabel: string };
  quickPractice: PracticeResponse | null;
  timerSeconds: number;
  timerRunning: boolean;
  practiceCompleted: boolean;
  practiceCompleting: boolean;
  currentQuickDecision: "yes" | "no" | "unclear" | null;
  currentQuestionAnswer: string | null;
  onOpenSection: (section: "morning" | "day" | "evening") => void;
  onSetTimerRunning: (value: boolean | ((prev: boolean) => boolean)) => void;
  onResetTimer: () => void;
  onCompleteQuickPractice: () => void;
  onReloadToday: () => void;
  onSaveQuickDecision: (value: "yes" | "no" | "unclear") => Promise<void> | void;
  onSaveQuestionOfDay: (value: string) => Promise<void> | void;
  formatTimer: (totalSeconds: number) => string;
  personalInsight: { title: string; message: string; chips: string[] };
  dailyReward: { title: string; message: string; level: "bronze" | "silver" | "gold"; badges?: string[] };
  questionOfDay: DayQuestionCard;
  weeklyGoal: WeeklyGoal | null;
  onOpenEntityWizard: (kind: TrackerEntityKind) => void;
  weeklyPatternMap: WeeklyPatternMap;
};

export function TodayWorkingLayerSection({
  dayNarrative = null,
  dayNarrativeLoading = false,
  nudge,
  quickPractice,
  timerSeconds,
  timerRunning,
  practiceCompleted,
  practiceCompleting,
  currentQuickDecision,
  currentQuestionAnswer,
  onOpenSection,
  onSetTimerRunning,
  onResetTimer,
  onCompleteQuickPractice,
  onReloadToday,
  onSaveQuickDecision,
  onSaveQuestionOfDay,
  formatTimer,
  personalInsight,
  dailyReward,
  questionOfDay,
  weeklyGoal,
  onOpenEntityWizard,
  weeklyPatternMap,
}: TodayWorkingLayerSectionProps) {
  const [decisionAnswer, setDecisionAnswer] = useState<"yes" | "no" | "unclear" | null>(currentQuickDecision);
  const [questionAnswer, setQuestionAnswer] = useState<string | null>(currentQuestionAnswer);
  const [decisionPending, setDecisionPending] = useState(false);
  const [questionPending, setQuestionPending] = useState(false);

  useEffect(() => {
    setDecisionAnswer(currentQuickDecision);
  }, [currentQuickDecision]);

  useEffect(() => {
    setQuestionAnswer(currentQuestionAnswer);
  }, [currentQuestionAnswer]);

  const decisionText =
    decisionAnswer === "yes"
      ? RITUAL_COPY.workingLayerDecisionAckYes
      : decisionAnswer === "no"
        ? RITUAL_COPY.workingLayerDecisionAckNo
        : decisionAnswer === "unclear"
          ? RITUAL_COPY.workingLayerDecisionAckUnclear
          : null;

  const apiNudge = narrativeString(dayNarrative?.nudge_message);
  const nudgeLine = apiNudge || nudge.message;
  const miniCaption = narrativeString(dayNarrative?.mini_decision_caption)?.trim() || "";
  const questionPrompt = narrativeString(dayNarrative?.question_of_day_prompt) || questionOfDay.prompt;
  const insightTitle = narrativeString(dayNarrative?.personal_insight_title) || personalInsight.title;
  const insightBody = narrativeString(dayNarrative?.personal_insight_body) || personalInsight.message;
  const insightChips = narrativeStringArray(dayNarrative?.personal_insight_chips, personalInsight.chips);
  const recsFromApi = Array.isArray(dayNarrative?.recommendations)
    ? (dayNarrative!.recommendations as unknown[]).map((x) => (typeof x === "string" ? x.trim() : "")).filter(Boolean)
    : [];
  const nudgeCta = narrativeString(dayNarrative?.nudge_cta_label) || nudge.ctaLabel;

  return (
    <section style={{ marginBottom: "var(--orbit-space-2xl)" }}>
      <style jsx>{`
        @media (max-width: 768px) {
          .today-working-card {
            padding: 0.9rem 0.85rem !important;
          }

          .today-working-action-row {
            display: grid !important;
            grid-template-columns: 1fr !important;
          }

          .today-working-action-row :global(.orbit-button),
          .today-working-action-row :global(a) {
            width: 100%;
            justify-content: center;
          }

          .today-working-grid {
            grid-template-columns: 1fr !important;
          }

          .today-working-reward {
            grid-template-columns: 1fr !important;
          }
        }
      `}</style>
      <div style={{ display: "grid", gap: "0.85rem" }}>
        {dayNarrativeLoading ? (
          <div
            className="todayflow-panel todayflow-section-panel"
            style={{
              border: "1px solid rgba(202, 177, 137, 0.32)",
              borderRadius: "18px",
              padding: "0.75rem 1rem",
              background: "rgba(255,250,242,0.92)",
              display: "flex",
              alignItems: "center",
              gap: "0.65rem",
            }}
          >
            <LoadingSpinner size="sm" />
            <p className="orbit-body-sm" style={{ margin: 0, color: "#6a5132" }}>{RITUAL_COPY.workingLayerDayStepLoading}</p>
          </div>
        ) : null}

        {nudgeLine ? (
          <div
            className="todayflow-panel todayflow-section-panel today-working-card"
            style={{
              border: "1px solid rgba(202, 177, 137, 0.34)",
              borderRadius: "20px",
              padding: "var(--orbit-space-lg)",
              background: "linear-gradient(160deg, rgba(255,252,246,0.98) 0%, rgba(255,244,224,0.95) 100%)",
              boxShadow: "0 14px 30px rgba(112, 82, 40, 0.12)",
            }}
          >
            <p className="orbit-body-sm" style={{ margin: 0, color: "#5e4222", lineHeight: 1.65 }}>
              {nudgeLine}
            </p>
            {recsFromApi.length > 0 ? (
              <details
                style={{
                  marginTop: "0.7rem",
                  padding: "0.75rem 0.8rem",
                  borderRadius: "14px",
                  background: "rgba(255,255,255,0.65)",
                  border: "1px solid rgba(201,168,115,0.18)",
                }}
              >
                <summary className="orbit-body-xs" style={{ cursor: "pointer", color: "#8a6f49", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.06em" }}>
                  {RITUAL_COPY.workingLayerNudgeRecsSummary}
                </summary>
                <ul className="orbit-body-xs" style={{ margin: "0.6rem 0 0", paddingLeft: "1.1rem", color: "#6a5132", lineHeight: 1.55 }}>
                  {recsFromApi.slice(0, 4).map((line, i) => (
                    <li key={i}>{line}</li>
                  ))}
                </ul>
              </details>
            ) : null}
          </div>
        ) : null}

        <div
          className="todayflow-panel todayflow-section-panel today-working-card"
          style={{
            border: "1px solid rgba(202, 177, 137, 0.38)",
            borderRadius: "20px",
            padding: "var(--orbit-space-lg)",
            background: "linear-gradient(165deg, rgba(255,255,255,0.98) 0%, rgba(255,248,236,0.92) 100%)",
            boxShadow: "0 12px 26px rgba(112, 82, 40, 0.1)",
          }}
        >
          <div style={{ display: "flex", justifyContent: "space-between", gap: "0.75rem", alignItems: "flex-start", flexWrap: "wrap" }}>
            <div style={{ flex: "1 1 220px", minWidth: 0 }}>
              <h2 className="orbit-heading-2" style={{ margin: 0, fontSize: "1.1rem" }}>
                {RITUAL_COPY.workingLayerExtraStepTitle}
              </h2>
              <p className="orbit-body-sm" style={{ margin: "0.45rem 0 0", color: "#5e4222", lineHeight: 1.62 }}>
                {RITUAL_COPY.workingLayerExtraStepLead}
              </p>
              {miniCaption ? (
                <p className="orbit-body-xs" style={{ margin: "0.5rem 0 0", color: "#7a6242", lineHeight: 1.55, fontStyle: "italic" }}>
                  {formatWorkingLayerMiniDecisionCaption(miniCaption)}
                </p>
              ) : null}
            </div>
          </div>

          <div className="today-working-action-row" style={{ marginTop: "0.45rem", display: "flex", gap: "0.45rem", flexWrap: "wrap" }}>
            {[
              { id: "yes", label: RITUAL_COPY.workingLayerQuickDecisionYes },
              { id: "no", label: RITUAL_COPY.workingLayerQuickDecisionNo },
              { id: "unclear", label: RITUAL_COPY.workingLayerQuickDecisionUnclear },
            ].map((item) => (
              <button
                key={item.id}
                type="button"
                className={`orbit-button orbit-button-sm ${decisionAnswer === item.id ? "orbit-button-primary" : "orbit-button-secondary"}`}
                disabled={decisionPending}
                aria-pressed={decisionAnswer === item.id}
                onClick={async () => {
                  const selected = item.id as "yes" | "no" | "unclear";
                  setDecisionAnswer(selected);
                  setDecisionPending(true);
                  try {
                    await onSaveQuickDecision(selected);
                    void logActiveJTBDAction("today_quick_decision_answered", {
                      answer: item.id,
                      source_surface: "today_quick_decision",
                    }).catch((error) => {
                      console.error("Failed to log quick decision", error);
                    });
                  } finally {
                    setDecisionPending(false);
                  }
                }}
              >
                {item.label}
              </button>
            ))}
          </div>

          {decisionText ? (
            <details
              style={{
                marginTop: "0.8rem",
                padding: "0.8rem 0.9rem",
                borderRadius: "16px",
                background: "rgba(255,248,235,0.96)",
                border: "1px solid rgba(201,168,115,0.24)",
              }}
            >
              <summary className="orbit-body-xs" style={{ cursor: "pointer", color: "#a67c3a", fontWeight: 700, letterSpacing: "0.04em", textTransform: "uppercase" }}>
                {RITUAL_COPY.workingLayerHintSummary}
              </summary>
              <p className="orbit-body-sm" style={{ margin: "0.45rem 0 0", color: "#5f4323", lineHeight: 1.6 }}>
                {decisionText}
              </p>
              <p className="orbit-body-xs" style={{ margin: "0.35rem 0 0", color: "#8a6c45", lineHeight: 1.55 }}>
                {workingLayerRingImpactForDecision(decisionAnswer)}
              </p>
            </details>
          ) : null}
        </div>

        <div
          className="todayflow-panel todayflow-section-panel today-working-card"
          style={{
            border: "1px solid rgba(202, 177, 137, 0.34)",
            borderRadius: "20px",
            padding: "var(--orbit-space-lg)",
            background: "linear-gradient(160deg, rgba(255,255,255,0.97) 0%, rgba(255,249,240,0.91) 100%)",
          }}
        >
          <div style={{ display: "flex", justifyContent: "space-between", gap: "0.75rem", alignItems: "flex-start", flexWrap: "wrap" }}>
            <div style={{ flex: "1 1 220px", minWidth: 0 }}>
              <h2 className="orbit-heading-2" style={{ margin: 0, fontSize: "1.1rem" }}>
                {RITUAL_COPY.workingLayerPracticeTitle}
              </h2>
              <p className="orbit-body-xs" style={{ margin: "0.35rem 0 0", color: "#7a6242", lineHeight: 1.6 }}>
                {RITUAL_COPY.workingLayerPracticeSubtitle}
              </p>
            </div>
            <span className="orbit-body-xs" style={summaryChipStyle}>{RITUAL_COPY.workingLayerPracticeChip}</span>
          </div>

          <div style={{ marginTop: "0.85rem", padding: "0.95rem", borderRadius: "16px", background: "rgba(255,248,235,0.96)", border: "1px solid rgba(201,168,115,0.24)" }}>
            {quickPractice ? (
              <>
                <p className="orbit-body-sm" style={{ margin: 0, color: "#5f4323", fontWeight: 700 }}>
                  {quickPractice.title}
                </p>
                {quickPractice.description ? (
                  <p className="orbit-body-sm" style={{ margin: "0.4rem 0 0", color: "#6a5132", lineHeight: 1.62 }}>
                    {quickPractice.description}
                  </p>
                ) : null}
                {quickPractice.duration_minutes ? (
                  <p className="orbit-body-xs" style={{ margin: "0.35rem 0 0", color: "#8a6f49" }}>
                    {formatWorkingLayerPracticeDurationHint(quickPractice.duration_minutes)}
                  </p>
                ) : null}
                <div className="today-working-action-row" style={{ marginTop: "0.75rem", display: "flex", gap: "0.45rem", flexWrap: "wrap" }}>
                  <button
                    type="button"
                    className="orbit-button orbit-button-secondary orbit-button-sm"
                    onClick={() => onSetTimerRunning((prev) => !prev)}
                    disabled={timerSeconds <= 0 || practiceCompleted}
                  >
                    {formatWorkingLayerTimerButton(timerRunning ? "pause" : "start", formatTimer(timerSeconds))}
                  </button>
                  <button
                    type="button"
                    className="orbit-button orbit-button-primary orbit-button-sm"
                    onClick={onCompleteQuickPractice}
                    disabled={practiceCompleting || practiceCompleted}
                  >
                    {practiceCompleted
                      ? RITUAL_COPY.workingLayerPracticeDone
                      : practiceCompleting
                        ? RITUAL_COPY.workingLayerPracticeCompleting
                        : RITUAL_COPY.workingLayerPracticeMarkDone}
                  </button>
                  <button type="button" className="orbit-button orbit-button-secondary orbit-button-sm" onClick={onResetTimer}>
                    {RITUAL_COPY.workingLayerTimerReset}
                  </button>
                </div>
              </>
            ) : (
              <>
                <p className="orbit-body-sm" style={{ margin: 0, color: "#6a5132", lineHeight: 1.62 }}>
                  {RITUAL_COPY.workingLayerPracticeMissing}
                </p>
                <div className="today-working-action-row" style={{ marginTop: "0.65rem", display: "flex", gap: "0.45rem", flexWrap: "wrap" }}>
                  <Link href="/practices" className="orbit-button orbit-button-secondary orbit-button-sm" style={{ textDecoration: "none", display: "inline-flex" }}>
                    {RITUAL_COPY.workingLayerPracticeCatalogCta}
                  </Link>
                </div>
              </>
            )}
          </div>
        </div>

        <div
          className="todayflow-panel todayflow-section-panel today-working-card"
          style={{
            border: "1px solid rgba(202, 177, 137, 0.34)",
            borderRadius: "18px",
            padding: "var(--orbit-space-lg)",
            background: "rgba(255,255,255,0.92)",
          }}
        >
          <div style={{ display: "flex", justifyContent: "space-between", gap: "0.75rem", alignItems: "flex-start", flexWrap: "wrap" }}>
            <div style={{ flex: "1 1 220px", minWidth: 0 }}>
              <h2 className="orbit-heading-2" style={{ margin: 0, fontSize: "1.1rem" }}>
                {RITUAL_COPY.workingLayerWeeklyFocusTitle}
              </h2>
              <p className="orbit-body-xs" style={{ margin: "0.35rem 0 0", color: "#7a6242", lineHeight: 1.6 }}>
                {RITUAL_COPY.workingLayerWeeklyFocusSubtitle}
              </p>
            </div>
            <span className="orbit-body-xs" style={summaryChipStyle}>{RITUAL_COPY.workingLayerWeeklyFocusChip}</span>
          </div>

          <div className="today-working-grid" style={{ marginTop: "0.85rem", display: "grid", gap: "0.75rem", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))" }}>
            <div style={{ padding: "0.95rem", borderRadius: "16px", background: "rgba(255,248,235,0.96)", border: "1px solid rgba(201,168,115,0.24)" }}>
              <p className="orbit-body-xs" style={{ margin: 0, color: "#8a6f49", textTransform: "uppercase", letterSpacing: "0.08em" }}>
                {RITUAL_COPY.workingLayerWeeklyFocusTitle}
              </p>
              <p className="orbit-body-sm" style={{ margin: "0.4rem 0 0", color: "#5f4323", fontWeight: 700 }}>
                {weeklyGoal?.title || RITUAL_COPY.workingLayerWeeklyGoalUnset}
              </p>
              <p className="orbit-body-sm" style={{ margin: "0.4rem 0 0", color: "#6a5132", lineHeight: 1.62 }}>
                {weeklyGoal
                  ? weeklyGoal.completed
                    ? RITUAL_COPY.workingLayerWeeklyGoalClosed
                    : weeklyGoal.last_progress_date
                      ? RITUAL_COPY.workingLayerWeeklyGoalInProgress
                      : RITUAL_COPY.workingLayerWeeklyGoalHasFocus
                  : RITUAL_COPY.workingLayerWeeklyGoalEmpty}
              </p>
            </div>

            <div style={{ padding: "0.95rem", borderRadius: "16px", background: "rgba(255,255,255,0.84)", border: "1px solid rgba(201,168,115,0.24)" }}>
              <p className="orbit-body-xs" style={{ margin: 0, color: "#8a6f49", textTransform: "uppercase", letterSpacing: "0.08em" }}>
                {RITUAL_COPY.workingLayerQuickAddTitle}
              </p>
              <div className="today-working-action-row" style={{ marginTop: "0.55rem", display: "flex", gap: "0.45rem", flexWrap: "wrap" }}>
                <button type="button" className="orbit-button orbit-button-secondary orbit-button-sm" onClick={() => onOpenEntityWizard("goal")}>
                  {RITUAL_COPY.workingLayerEntityGoal}
                </button>
                <button type="button" className="orbit-button orbit-button-secondary orbit-button-sm" onClick={() => onOpenEntityWizard("habit")}>
                  {RITUAL_COPY.workingLayerEntityHabit}
                </button>
                <button type="button" className="orbit-button orbit-button-secondary orbit-button-sm" onClick={() => onOpenEntityWizard("ascetic")}>
                  {RITUAL_COPY.workingLayerEntityAscetic}
                </button>
              </div>
              <p className="orbit-body-xs" style={{ margin: "0.55rem 0 0", color: "#7a6242", lineHeight: 1.55 }}>
                {RITUAL_COPY.workingLayerWizardOpensOverlay}
              </p>
            </div>
          </div>
          <div
            className="today-working-reward"
            style={{
              marginTop: "0.75rem",
              padding: "0.95rem",
              borderRadius: "16px",
              background: "rgba(255,255,255,0.82)",
              border: "1px solid rgba(201,168,115,0.24)",
              display: "grid",
              gap: "0.5rem",
              gridTemplateColumns: "auto 1fr",
              alignItems: "start",
            }}
          >
            <RewardContourBadge level={dailyReward.level} />
            <div style={{ minWidth: 0 }}>
              <p className="orbit-body-xs" style={{ margin: 0, color: "#8a6f49", textTransform: "uppercase", letterSpacing: "0.08em" }}>
                {RITUAL_COPY.workingLayerDailyTrailTitle}
              </p>
              <p className="orbit-body-sm" style={{ margin: "0.35rem 0 0", color: "#5f4323", fontWeight: 700 }}>
                {dailyReward.title}
              </p>
              <p className="orbit-body-sm" style={{ margin: "0.4rem 0 0", color: "#6a5132", lineHeight: 1.65 }}>
                {dailyReward.message}
              </p>
              {dailyReward.badges && dailyReward.badges.length > 0 ? (
                <div style={{ marginTop: "0.45rem", display: "flex", flexWrap: "wrap", gap: "0.3rem" }}>
                  {dailyReward.badges.slice(0, 4).map((b) => (
                    <span key={b} className="orbit-body-xs" style={summaryChipStyle}>
                      {b}
                    </span>
                  ))}
                </div>
              ) : null}
              <p className="orbit-body-sm" style={{ margin: "0.45rem 0 0", color: "#5f4323", fontWeight: 700 }}>{insightTitle}</p>
              <p className="orbit-body-sm" style={{ margin: "0.35rem 0 0", color: "#6a5132", lineHeight: 1.6 }}>{insightBody}</p>
              {insightChips.length > 0 ? (
                <div style={{ marginTop: "0.45rem", display: "flex", flexWrap: "wrap", gap: "0.35rem" }}>
                  {insightChips.map((c, i) => (
                    <span key={`${i}-${c}`} className="orbit-body-xs" style={summaryChipStyle}>
                      {c}
                    </span>
                  ))}
                </div>
              ) : null}
            </div>
          </div>
        </div>

        <div
          className="todayflow-panel todayflow-section-panel today-working-card"
          style={{
            border: "1px solid rgba(202, 177, 137, 0.34)",
            borderRadius: "20px",
            padding: "var(--orbit-space-lg)",
            background: "linear-gradient(165deg, rgba(255,255,255,0.97) 0%, rgba(255,247,234,0.91) 100%)",
          }}
        >
          <div style={{ display: "flex", justifyContent: "space-between", gap: "0.75rem", alignItems: "flex-start", flexWrap: "wrap" }}>
            <div style={{ flex: "1 1 240px", minWidth: 0 }}>
              <h2 className="orbit-heading-2" style={{ margin: 0, fontSize: "1.1rem" }}>
                {RITUAL_COPY.workingLayerUnderstandYouTitle}
              </h2>
              <p className="orbit-body-xs" style={{ margin: "0.4rem 0 0", color: "#7a6242", lineHeight: 1.6 }}>
                {RITUAL_COPY.workingLayerUnderstandYouSubtitle}
              </p>
              <p className="orbit-body-sm" style={{ margin: "0.55rem 0 0", color: "#5f4323", fontWeight: 700 }}>
                {questionPrompt}
              </p>
            </div>
            <span className="orbit-body-xs" style={summaryChipStyle}>{RITUAL_COPY.workingLayerOptionalChip}</span>
          </div>

          <div className="today-working-action-row" style={{ marginTop: "0.85rem", display: "flex", gap: "0.45rem", flexWrap: "wrap" }}>
            {questionOfDay.options.map((option) => (
              <button
                key={option.id}
                type="button"
                className={`orbit-button orbit-button-sm ${questionAnswer === option.id ? "orbit-button-primary" : "orbit-button-secondary"}`}
                disabled={questionPending}
                onClick={async () => {
                  setQuestionAnswer(option.id);
                  setQuestionPending(true);
                  try {
                    await onSaveQuestionOfDay(option.id);
                    void logActiveJTBDAction("today_profile_signal_answered", {
                      answer: option.id,
                      label: option.label,
                      source_surface: "today_profile_signal",
                    }).catch((error) => {
                      console.error("Failed to log profile signal", error);
                    });
                  } finally {
                    setQuestionPending(false);
                  }
                }}
              >
                {option.label}
              </button>
            ))}
          </div>

          {questionAnswer ? (
            <div style={{ marginTop: "0.8rem", padding: "0.95rem", borderRadius: "16px", background: "rgba(255,248,235,0.96)", border: "1px solid rgba(201,168,115,0.24)" }}>
              <p className="orbit-body-sm" style={{ margin: 0, color: "#6a5132", lineHeight: 1.65 }}>
                {questionOfDay.options.find((option) => option.id === questionAnswer)?.response}
              </p>
              <p className="orbit-body-xs" style={{ margin: "0.35rem 0 0", color: "#8a6c45", lineHeight: 1.55 }}>
                {workingLayerRingImpactForQuestion(questionAnswer)}
              </p>
            </div>
          ) : null}

          <div className="today-working-action-row" style={{ marginTop: "0.75rem", display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
            {nudge.ctaHref.startsWith("#") ? (
              <button
                type="button"
                className="orbit-button orbit-button-secondary orbit-button-sm"
                onClick={() => {
                  if (nudge.ctaHref === "#meaning-section") onOpenSection("morning");
                  if (nudge.ctaHref === "#checkin-section") onOpenSection("day");
                  if (nudge.ctaHref === "#closing-section") onOpenSection("evening");
                }}
              >
                {nudgeCta}
              </button>
            ) : (
              <Link href={nudge.ctaHref} className="orbit-button orbit-button-secondary orbit-button-sm" style={{ textDecoration: "none" }}>
                {nudgeCta}
              </Link>
            )}
          </div>
        </div>

        <div
          className="todayflow-panel todayflow-section-panel today-working-card"
          style={{
            border: "1px solid rgba(202, 177, 137, 0.34)",
            borderRadius: "20px",
            padding: "var(--orbit-space-lg)",
            background: "linear-gradient(165deg, rgba(255,255,255,0.97) 0%, rgba(255,249,239,0.9) 100%)",
          }}
        >
          <div style={{ display: "flex", justifyContent: "space-between", gap: "0.75rem", alignItems: "flex-start", flexWrap: "wrap" }}>
            <div style={{ flex: "1 1 240px", minWidth: 0 }}>
              <h2 className="orbit-heading-2" style={{ margin: 0, fontSize: "1.1rem" }}>
                {RITUAL_COPY.workingLayerWeeklyStateMapTitle}
              </h2>
              <p className="orbit-body-xs" style={{ margin: "0.4rem 0 0", color: "#7a6242", lineHeight: 1.6 }}>
                {RITUAL_COPY.workingLayerWeeklyStateMapBody}
              </p>
            </div>
            <span className="orbit-body-xs" style={summaryChipStyle}>
              {weeklyPatternMap.moodTrend === "up"
                ? RITUAL_COPY.workingLayerTrendUp
                : weeklyPatternMap.moodTrend === "down"
                  ? RITUAL_COPY.workingLayerTrendDown
                  : RITUAL_COPY.workingLayerTrendFlat}
            </span>
          </div>

          <div className="today-working-grid" style={{ marginTop: "0.7rem", display: "grid", gap: "0.65rem", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))" }}>
            <div style={{ padding: "0.75rem", borderRadius: "14px", background: "rgba(255,248,235,0.9)", border: "1px solid rgba(201,168,115,0.22)" }}>
              <p className="orbit-body-xs" style={{ margin: 0, color: "#8a6f49", fontWeight: 700 }}>{RITUAL_COPY.workingLayerAvgStateLabel}</p>
              <p className="orbit-body-sm" style={{ margin: "0.25rem 0 0", color: "#5f4323", fontWeight: 700 }}>
                {weeklyPatternMap.avgStateScale != null
                  ? `${weeklyPatternMap.avgStateScale}/5`
                  : RITUAL_COPY.workingLayerInsufficientData}
              </p>
            </div>
            <div style={{ padding: "0.75rem", borderRadius: "14px", background: "rgba(255,248,235,0.9)", border: "1px solid rgba(201,168,115,0.22)" }}>
              <p className="orbit-body-xs" style={{ margin: 0, color: "#8a6f49", fontWeight: 700 }}>{RITUAL_COPY.workingLayerTrackedDaysLabel}</p>
              <p className="orbit-body-sm" style={{ margin: "0.25rem 0 0", color: "#5f4323", fontWeight: 700 }}>
                {weeklyPatternMap.trackedDays} / 7
              </p>
            </div>
            <div style={{ padding: "0.75rem", borderRadius: "14px", background: "rgba(255,248,235,0.9)", border: "1px solid rgba(201,168,115,0.22)" }}>
              <p className="orbit-body-xs" style={{ margin: 0, color: "#8a6f49", fontWeight: 700 }}>{RITUAL_COPY.workingLayerJournalDaysLabel}</p>
              <p className="orbit-body-sm" style={{ margin: "0.25rem 0 0", color: "#5f4323", fontWeight: 700 }}>
                {weeklyPatternMap.journalDays} / 7
              </p>
            </div>
          </div>

          {weeklyPatternMap.improvements.length > 0 ? (
            <div style={{ marginTop: "0.7rem" }}>
              {weeklyPatternMap.improvements.slice(0, 2).map((item, idx) => (
                <p key={`imp-${idx}`} className="orbit-body-xs" style={{ margin: "0.2rem 0 0", color: "#166534", lineHeight: 1.55 }}>
                  + {item}
                </p>
              ))}
            </div>
          ) : null}
          {weeklyPatternMap.regressions.length > 0 ? (
            <div style={{ marginTop: "0.35rem" }}>
              {weeklyPatternMap.regressions.slice(0, 2).map((item, idx) => (
                <p key={`reg-${idx}`} className="orbit-body-xs" style={{ margin: "0.2rem 0 0", color: "#991b1b", lineHeight: 1.55 }}>
                  - {item}
                </p>
              ))}
            </div>
          ) : null}

          <p className="orbit-body-sm" style={{ margin: "0.7rem 0 0", color: "#5f4323", lineHeight: 1.6 }}>
            {formatWeeklyPatternRecommendation(weeklyPatternMap.recommendation)}
          </p>
        </div>
      </div>
    </section>
  );
}

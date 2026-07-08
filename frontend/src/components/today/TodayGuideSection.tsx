"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import type {
  DayEnergySummary,
  DayFocusSummary,
  DayQuestionCard,
  DayRiskSummary,
  TodayFlowTab,
} from "@/components/today/todayPageUtils";
import { narrativeString, narrativeStringArray } from "@/lib/todayNarrativeApi";
import { INSIGHT_PAYWALL_COPY, type InsightDepthTier } from "@/lib/insightDepth";
import { LoadingSpinner } from "@/components/orbit";
import { ProgressContoursRow } from "@/components/rewards/ProgressContoursRow";
import { TodayDayLogicCallout } from "@/components/today/TodayDayLogicCallout";
import { formatGuideDayProgressLine, RITUAL_COPY, rhythmTierLabelForScore } from "@/components/today/todayRitualCopy";
import {
  guideCanonicalPrimaryStepLine,
  parseDayEngineBriefFromGuide,
  parseDayModelBriefFromGuide,
} from "@/components/today/todayGuideActionable";

type DailyStep = { key: string; label: string; done: boolean };

function normalizePhrase(s: string) {
  return s
    .toLowerCase()
    .replace(/\s+/g, " ")
    .replace(/[«»"""'']/g, "")
    .trim();
}

/** Не показываем profile_prism, если он дублирует уже показанный заголовок/подзаголовок (разные источники: API нарратива и гороскоп). */
function visibleProfilePrism(prismRaw: string | null | undefined, headline: string, subline: string): string | null {
  const prism = prismRaw?.trim();
  if (!prism) return null;
  const p = normalizePhrase(prism);
  const h = normalizePhrase(headline);
  const sl = normalizePhrase(subline);
  const combo = normalizePhrase(`${headline} ${subline}`);
  if (!p) return null;
  if (h && (p === h || (h.length >= 14 && p.startsWith(h.slice(0, Math.min(h.length, 80)))))) return null;
  if (sl && (p === sl || (sl.length >= 14 && p.startsWith(sl.slice(0, Math.min(sl.length, 80)))))) return null;
  if (combo.length >= 20 && combo.includes(p)) return null;
  const first = (t: string) => normalizePhrase(t.split(/[.!?]\s/)[0] || t);
  const p0 = first(prism);
  const h0 = first(headline);
  if (p0 && h0 && p0 === h0 && p0.length >= 12) return null;
  return prism;
}

export function TodayGuideSection({
  narrativePayload,
  narrativeLoading,
  formattedDate,
  rewardRings,
  lunarSnapshot,
  profilePrismLine,
  guideHeadline,
  guideSubline,
  energySummary,
  focusSummary,
  riskSummary,
  energyScore,
  focusScore,
  moodToday,
  actionPlan,
  criticalLimits,
  nextAction,
  onNextAction,
  onSelectTab,
  onOpenTarotTab,
  questionOfDay,
  currentQuestionAnswer,
  onSaveQuestionOfDay,
  insightDepthTier,
  progressPercent,
  completedSteps,
  dailyStepsCount,
  dailySteps,
  journeyFlow,
}: {
  insightDepthTier: InsightDepthTier;
  narrativePayload: Record<string, unknown> | null;
  narrativeLoading: boolean;
  formattedDate: string;
  rewardRings?: { evolutionIndex: number; rewardRingsEarned?: string[] | null } | null;
  lunarSnapshot?: { phaseName: string; cycleDay?: number; themes?: string | null } | null;
  profilePrismLine?: string | null;
  guideHeadline: string;
  guideSubline: string;
  energySummary: DayEnergySummary;
  focusSummary: DayFocusSummary;
  riskSummary: DayRiskSummary;
  energyScore: number;
  focusScore: number;
  moodToday: string;
  actionPlan: string[];
  criticalLimits: string[];
  nextAction: { label: string; href: string; message: string };
  onNextAction: (href: string) => void;
  onSelectTab: (tab: TodayFlowTab) => void;
  onOpenTarotTab: () => void;
  questionOfDay: DayQuestionCard;
  currentQuestionAnswer: string | null;
  onSaveQuestionOfDay: (value: string) => Promise<void> | void;
  progressPercent: number;
  completedSteps: number;
  dailyStepsCount: number;
  dailySteps: DailyStep[];
  journeyFlow: {
    title: string;
    body: string;
    primaryCta: { label: string; href: string };
    secondaryCta?: { label: string; href: string } | null;
  };
}) {
  const apiHeadline = narrativeString(narrativePayload?.headline) || guideHeadline;
  const apiSubline = narrativeString(narrativePayload?.subline) || guideSubline;
  const profilePrismVisible = visibleProfilePrism(profilePrismLine, apiHeadline, apiSubline || "");
  const apiEnergyLine = narrativeString(narrativePayload?.energy_line) || `${energySummary.label} (${energySummary.score}) — ${energySummary.guidance}`;
  const apiFocusLine = narrativeString(narrativePayload?.focus_line) || focusSummary.label;
  const apiRiskLine = narrativeString(narrativePayload?.risk_line) || riskSummary.label;
  const apiRiskDetail = narrativeString(narrativePayload?.risk_detail) || riskSummary.detail;
  const apiDo = narrativeStringArray(narrativePayload?.do_items, actionPlan);
  const apiAvoid = narrativeStringArray(narrativePayload?.avoid_items, criticalLimits);
  const apiPatternInsight = narrativeString(narrativePayload?.pattern_insight);
  const apiLifeContextInsight = narrativeString(narrativePayload?.life_context_insight);
  const dayEngineBrief = useMemo(
    () =>
      narrativePayload && typeof narrativePayload === "object"
        ? parseDayEngineBriefFromGuide(narrativePayload)
        : null,
    [narrativePayload],
  );
  const dayModelBrief = useMemo(
    () =>
      narrativePayload && typeof narrativePayload === "object"
        ? parseDayModelBriefFromGuide(narrativePayload)
        : null,
    [narrativePayload],
  );
  const [questionAnswer, setQuestionAnswer] = useState<string | null>(currentQuestionAnswer);
  const [questionPending, setQuestionPending] = useState(false);
  const primaryAction = guideCanonicalPrimaryStepLine(narrativePayload, apiDo, RITUAL_COPY.guidePrimaryDoFallback);
  const nPrimary = normalizePhrase(primaryAction);
  const secondaryActions = [
    ...apiDo.filter((d) => normalizePhrase(d) !== nPrimary).slice(0, 2),
    ...apiAvoid.filter((a) => normalizePhrase(a) !== nPrimary).slice(0, 2),
  ].slice(0, 3);
  const emotionalRings = [
    {
      label: RITUAL_COPY.guideEmotionalRingLove,
      score: Math.max(30, Math.min(100, Math.round((energyScore * 0.6 + focusScore * 0.4) / 1))),
    },
    { label: RITUAL_COPY.guideEmotionalRingFocus, score: Math.max(25, Math.min(100, focusScore)) },
    {
      label: RITUAL_COPY.guideEmotionalRingMoney,
      score: Math.max(20, Math.min(100, Math.round((focusScore * 0.7 + 20) / 1))),
    },
    { label: RITUAL_COPY.guideEmotionalRingState, score: Math.max(25, Math.min(100, energyScore)) },
  ];
  const miniFlow = [
    { key: "water", label: RITUAL_COPY.guideMiniFlowWater, done: completedSteps >= 1 },
    { key: "movement", label: RITUAL_COPY.guideMiniFlowMovement, done: completedSteps >= 1 },
    { key: "reflection", label: RITUAL_COPY.guideMiniFlowReflection, done: completedSteps >= 2 },
    { key: "focus", label: RITUAL_COPY.guideMiniFlowFocusSession, done: completedSteps >= 2 },
  ];

  useEffect(() => {
    setQuestionAnswer(currentQuestionAnswer);
  }, [currentQuestionAnswer]);

  const stepToTab = (key: string): TodayFlowTab => {
    if (key === "meaning") return "morning";
    if (key === "focus") return "day";
    if (key === "closing") return "evening";
    return "guide";
  };

  return (
    <section style={{ marginBottom: "var(--orbit-space-xl)" }}>
      <style jsx>{`
        .today-guide-card {
          transition: transform 180ms ease, box-shadow 220ms ease, border-color 220ms ease;
        }
        @media (hover: hover) and (pointer: fine) {
          .today-guide-card:hover {
            transform: translateY(-1px);
            box-shadow: 0 16px 30px rgba(115, 84, 43, 0.12) !important;
          }
        }
        .today-guide-secondary-details summary {
          list-style: none;
        }
        .today-guide-secondary-details summary::-webkit-details-marker {
          display: none;
        }
      `}</style>
      <div
        className="orbit-card todayflow-panel today-guide-card"
        style={{
          padding: "1.05rem",
          borderRadius: "22px",
          marginBottom: "0.9rem",
          background: "linear-gradient(155deg, rgba(255,255,255,0.98) 0%, rgba(255,245,228,0.94) 100%)",
          border: "1px solid rgba(201,168,115,0.34)",
          boxShadow: "0 16px 34px rgba(110, 80, 38, 0.12)",
        }}
      >
        <p className="orbit-body-xs" style={{ margin: 0, color: "#8a6c45", textTransform: "uppercase", letterSpacing: "0.08em", fontWeight: 700 }}>
          {RITUAL_COPY.guidePanelEyebrowToday}
        </p>
        <p className="orbit-body-sm" style={{ margin: "0.25rem 0 0", color: "#6a5132", fontWeight: 600 }}>
          {formattedDate}
        </p>
        <h2 className="orbit-display-sm" style={{ margin: "0.5rem 0 0", color: "#352515", lineHeight: 1.28 }}>
          {apiHeadline}
        </h2>
        {apiSubline ? (
          <p className="orbit-body-sm" style={{ margin: "0.45rem 0 0", color: "#6a5132", lineHeight: 1.62 }}>
            {apiSubline}
          </p>
        ) : null}
        <TodayDayLogicCallout variant="guide" dayEngineBrief={dayEngineBrief} dayModelBrief={dayModelBrief} />
        {narrativeLoading && !narrativePayload ? (
          <div style={{ marginTop: "0.5rem", display: "flex", alignItems: "center", gap: "0.45rem" }}>
            <LoadingSpinner size="sm" />
            <p className="orbit-body-xs" style={{ margin: 0, color: "#8a6c45" }}>{RITUAL_COPY.guideNarrativeRefiningLine}</p>
          </div>
        ) : null}
        <div style={{ marginTop: "0.7rem", display: "flex", gap: "0.5rem", flexWrap: "wrap", alignItems: "center" }}>
          <button type="button" className="orbit-button orbit-button-primary orbit-button-sm" onClick={() => onSelectTab("day")}>
            {RITUAL_COPY.guidePrimaryNavigateCta}
          </button>
          <button type="button" className="orbit-button orbit-button-secondary orbit-button-sm" onClick={() => onNextAction(journeyFlow.primaryCta.href)}>
            {RITUAL_COPY.guideWhyTodayCta}
          </button>
          {rewardRings ? (
            <ProgressContoursRow evolutionIndex={rewardRings.evolutionIndex} rewardRingsEarned={rewardRings.rewardRingsEarned} />
          ) : null}
        </div>
      </div>

      <details className="today-guide-secondary-details" style={{ marginBottom: "0.85rem" }}>
        <summary
          className="orbit-card todayflow-panel"
          style={{
            padding: "0.85rem 1rem",
            borderRadius: "20px",
            background: "linear-gradient(165deg, rgba(255,252,248,0.98) 0%, rgba(255,245,236,0.95) 100%)",
            border: "1px solid rgba(201,168,115,0.32)",
            boxShadow: "0 8px 20px rgba(115, 84, 43, 0.08)",
            cursor: "pointer",
          }}
        >
          <p className="orbit-body-xs" style={{ margin: 0, color: "#8a6c45", textTransform: "uppercase", letterSpacing: "0.08em", fontWeight: 700 }}>
            {RITUAL_COPY.guideAdditionalDisclosureTitle}
          </p>
          <p className="orbit-body-xs" style={{ margin: "0.35rem 0 0", color: "#6a5132", lineHeight: 1.5, fontWeight: 600 }}>
            {RITUAL_COPY.guideAdditionalDisclosureSubtitleWeb}
          </p>
        </summary>
        <div style={{ marginTop: "0.75rem", display: "grid", gap: "0.85rem" }}>
          <div
            className="orbit-card todayflow-panel today-guide-card"
            style={{
              padding: "1rem",
              borderRadius: "20px",
              marginBottom: 0,
              background: "linear-gradient(165deg, rgba(255,255,255,0.97) 0%, rgba(255,248,236,0.92) 100%)",
              border: "1px solid rgba(201,168,115,0.28)",
              boxShadow: "0 12px 28px rgba(116, 86, 43, 0.1)",
            }}
          >
        <p className="orbit-body-xs" style={{ margin: 0, color: "#8a6c45", textTransform: "uppercase", letterSpacing: "0.07em", fontWeight: 700 }}>
          {RITUAL_COPY.guideEmotionalRingsSectionTitle}
        </p>
        <div style={{ marginTop: "0.7rem", display: "grid", gap: "0.55rem", gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))" }}>
          {emotionalRings.map((ring) => (
            <button
              key={ring.label}
              type="button"
              onClick={() => onSelectTab("spheres")}
              style={{
                textAlign: "left",
                borderRadius: "14px",
                padding: "0.7rem 0.75rem",
                border: "1px solid rgba(201,168,115,0.26)",
                background: "rgba(255,252,247,0.95)",
                cursor: "pointer",
              }}
            >
              <p className="orbit-body-xs" style={{ margin: 0, color: "#8a6c45", fontWeight: 700 }}>{ring.label}</p>
              <p className="orbit-body-sm" style={{ margin: "0.25rem 0 0", color: "#5f4323", fontWeight: 700, lineHeight: 1.45 }}>
                {rhythmTierLabelForScore(ring.score)}
              </p>
              <p className="orbit-body-xs" style={{ margin: "0.2rem 0 0", color: "#7a6242", lineHeight: 1.45 }}>
                {RITUAL_COPY.heroScoreFootnote(ring.score)}
              </p>
            </button>
          ))}
        </div>
        <p className="orbit-body-xs" style={{ margin: "0.6rem 0 0", color: "#7a6242", lineHeight: 1.5 }}>
          {RITUAL_COPY.guideOpenSphereForDetailHint}
        </p>
      </div>

      <div
        className="orbit-card todayflow-panel today-guide-card"
        style={{
          padding: "1rem",
          borderRadius: "20px",
          marginBottom: 0,
          background: "linear-gradient(165deg, rgba(255,255,255,0.96) 0%, rgba(255,250,241,0.92) 100%)",
          border: "1px solid rgba(201,168,115,0.26)",
          boxShadow: "0 10px 24px rgba(115, 84, 43, 0.09)",
        }}
      >
        <p className="orbit-body-xs" style={{ margin: 0, color: "#8a6c45", textTransform: "uppercase", letterSpacing: "0.07em", fontWeight: 700 }}>
          {RITUAL_COPY.guideWhatToDoTodayTitle}
        </p>
        <p className="orbit-body-sm" style={{ margin: "0.4rem 0 0", color: "#5f4323", lineHeight: 1.6, fontWeight: 700 }}>
          {primaryAction}
        </p>
        <div style={{ marginTop: "0.55rem", display: "grid", gap: "0.35rem" }}>
          {secondaryActions.map((item, idx) => (
            <p key={`${item}-${idx}`} className="orbit-body-xs" style={{ margin: 0, color: "#6a5132", lineHeight: 1.55 }}>
              - {item}
            </p>
          ))}
        </div>
        <div style={{ marginTop: "0.65rem", display: "flex", flexWrap: "wrap", gap: "0.45rem" }}>
          {nextAction.href.startsWith("#") ? (
            <button type="button" className="orbit-button orbit-button-primary orbit-button-sm" onClick={() => onNextAction(nextAction.href)}>
              {nextAction.label}
            </button>
          ) : (
            <Link href={nextAction.href} className="orbit-button orbit-button-primary orbit-button-sm" style={{ textDecoration: "none" }}>
              {nextAction.label}
            </Link>
          )}
          <button type="button" className="orbit-button orbit-button-secondary orbit-button-sm" onClick={() => onSelectTab("day")}>
            {RITUAL_COPY.guideOpenDayStepCta}
          </button>
        </div>
      </div>

      <div
        className="orbit-card todayflow-panel today-guide-card"
        style={{
          padding: "1rem",
          borderRadius: "20px",
          marginBottom: 0,
          background: "linear-gradient(170deg, rgba(255,255,255,0.95) 0%, rgba(255,248,235,0.9) 100%)",
          border: "1px solid rgba(201,168,115,0.24)",
        }}
      >
        <p className="orbit-body-xs" style={{ margin: 0, color: "#8a6c45", textTransform: "uppercase", letterSpacing: "0.07em", fontWeight: 700 }}>
          {RITUAL_COPY.guideShortQuestionAboutYouTitle}
        </p>
        <p className="orbit-body-sm" style={{ margin: "0.4rem 0 0", color: "#5f4323", fontWeight: 700, lineHeight: 1.55 }}>
          {questionOfDay.prompt}
        </p>
        <div style={{ marginTop: "0.65rem", display: "flex", gap: "0.45rem", flexWrap: "wrap" }}>
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
          <p className="orbit-body-xs" style={{ margin: "0.55rem 0 0", color: "#6a5132", lineHeight: 1.55 }}>
            {questionOfDay.options.find((option) => option.id === questionAnswer)?.response}
          </p>
        ) : null}
      </div>

      <div
        className="orbit-card todayflow-panel today-guide-card"
        style={{
          padding: "1rem",
          borderRadius: "20px",
          marginBottom: 0,
          background: "linear-gradient(160deg, rgba(255,255,255,0.95) 0%, rgba(255,246,232,0.9) 100%)",
          border: "1px solid rgba(201,168,115,0.24)",
        }}
      >
        <p className="orbit-body-xs" style={{ margin: 0, color: "#8a6c45", textTransform: "uppercase", letterSpacing: "0.07em", fontWeight: 700 }}>
          {RITUAL_COPY.guideMiniPlanTitle}
        </p>
        <div style={{ marginTop: "0.65rem", display: "grid", gap: "0.4rem" }}>
          {miniFlow.map((item) => (
            <p key={item.key} className="orbit-body-sm" style={{ margin: 0, color: item.done ? "#166534" : "#5f4323" }}>
              {item.done ? "☑" : "☐"} {item.label}
            </p>
          ))}
        </div>
        <div style={{ marginTop: "0.65rem", height: "6px", borderRadius: "999px", background: "rgba(201,168,115,0.16)", overflow: "hidden" }}>
          <div style={{ width: `${Math.max(8, progressPercent)}%`, height: "100%", background: "linear-gradient(90deg, rgba(201,168,115,0.92), rgba(160,128,80,0.95))" }} />
        </div>
        <p className="orbit-body-xs" style={{ margin: "0.45rem 0 0", color: "#7a6242" }}>
          {formatGuideDayProgressLine(progressPercent, completedSteps, dailyStepsCount)}
        </p>
        <Link href="/tracking/calendar" className="orbit-button orbit-button-secondary orbit-button-sm" style={{ marginTop: "0.6rem", textDecoration: "none" }}>
          {RITUAL_COPY.guideOpenFullCalendarCta}
        </Link>
      </div>

      <div
        className="orbit-card todayflow-panel today-guide-card"
        style={{
          padding: "1rem",
          borderRadius: "20px",
          marginBottom: 0,
          background: "linear-gradient(170deg, rgba(255,255,255,0.96) 0%, rgba(255,248,238,0.92) 100%)",
          border: "1px solid rgba(201,168,115,0.26)",
          boxShadow: "0 10px 24px rgba(116, 86, 43, 0.08)",
        }}
      >
        <p className="orbit-body-xs" style={{ margin: 0, color: "#8a6c45", textTransform: "uppercase", letterSpacing: "0.07em", fontWeight: 700 }}>
          {RITUAL_COPY.guideEmotionalTriggersTitle}
        </p>
        <div style={{ marginTop: "0.6rem", display: "grid", gap: "0.45rem", gridTemplateColumns: "repeat(auto-fit, minmax(190px, 1fr))" }}>
          <button type="button" onClick={onOpenTarotTab} className="orbit-button orbit-button-secondary orbit-button-sm" style={{ justifyContent: "flex-start" }}>
            {RITUAL_COPY.guideTriggerDayCard}
          </button>
          <Link href="/compatibility" className="orbit-button orbit-button-secondary orbit-button-sm" style={{ textDecoration: "none", justifyContent: "flex-start" }}>
            {RITUAL_COPY.guideTriggerRelationshipEnergy}
          </Link>
          <button type="button" onClick={() => onSelectTab("evening")} className="orbit-button orbit-button-secondary orbit-button-sm" style={{ justifyContent: "flex-start" }}>
            {RITUAL_COPY.guideTriggerQuickDiary}
          </button>
        </div>
      </div>
        </div>
      </details>

      {(insightDepthTier === "pro" || insightDepthTier === "premium" || insightDepthTier === "free") && (
        <details>
          <summary className="orbit-body-xs" style={{ cursor: "pointer", color: "#8a6c45", fontWeight: 700 }}>
            {RITUAL_COPY.guideShowDayDetailsSummary}
          </summary>
          <div style={{ marginTop: "0.6rem", display: "grid", gap: "0.4rem" }}>
            <p className="orbit-body-xs" style={{ margin: 0, color: "#6a5132" }}>
              {RITUAL_COPY.guideDetailEnergyPrefix} {apiEnergyLine}
            </p>
            <p className="orbit-body-xs" style={{ margin: 0, color: "#6a5132" }}>
              {RITUAL_COPY.guideDetailFocusPrefix} {apiFocusLine}
            </p>
            <p className="orbit-body-xs" style={{ margin: 0, color: "#6a5132" }}>
              {RITUAL_COPY.guideDetailRiskPrefix} {apiRiskLine}. {apiRiskDetail}
            </p>
            {profilePrismVisible ? <p className="orbit-body-xs" style={{ margin: 0, color: "#6a5132" }}>{profilePrismVisible}</p> : null}
            {lunarSnapshot?.phaseName ? (
              <p className="orbit-body-xs" style={{ margin: 0, color: "#6a5132" }}>
                {RITUAL_COPY.guideDetailMoonPrefix} {lunarSnapshot.phaseName}
              </p>
            ) : null}
            {apiPatternInsight ? <p className="orbit-body-xs" style={{ margin: 0, color: "#6a5132" }}>{apiPatternInsight}</p> : null}
            {apiLifeContextInsight ? <p className="orbit-body-xs" style={{ margin: 0, color: "#6a5132" }}>{apiLifeContextInsight}</p> : null}
          </div>
        </details>
      )}
    </section>
  );
}

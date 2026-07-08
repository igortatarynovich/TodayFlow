"use client";

import { useMemo } from "react";
import { TarotReadingStorySurface } from "@/components/guidance/TarotReadingStorySurface";
import {
  guidanceResultChromeBundle,
  guidanceResultShowCompatHint,
} from "@/components/guidance/guidanceResultChrome";
import type { FlowPracticesChromeLocale } from "@/components/today/flowPracticesMainTabChrome";
import { buildTarotReadingStoryFromGuidance } from "@/lib/buildTarotReadingStoryModel";
import { getLocale } from "@/lib/i18n";

export type GuidanceQuestionAssessment = {
  flags: {
    too_general: boolean;
    fortune_telling_tone: boolean;
    low_actionability: boolean;
    possible_repeat: boolean;
  };
  suggestion?: string | null;
  weak_reading_warning?: string | null;
};

export type GuidanceInterpretationContract = {
  summary: string;
  core_insight: string;
  profile_bridge: string;
  action: string;
  avoid: string;
  continue_hint: string;
  why_outline: string;
  position_weights_note: string;
};

export type GuidanceReadingResult = {
  generation_log_id: number | null;
  question: string;
  spread_id: string;
  lane: string;
  lane_title: string;
  profile_ready: boolean;
  answer: {
    clarity: string;
    explanation: string;
    forecast: string;
    decision: string;
    today: string;
  };
  suggested_route: {
    href: string;
    label: string;
    reason: string;
  };
  /** Явный мост в дневной Flow / OS (дополнительно к suggested_route). */
  flow_bridge?: {
    href: string;
    label: string;
    reason: string;
    kind: string;
  } | null;
  editorial?: {
    current_focus?: string;
    next_step?: string;
  } | null;
  is_clarification?: boolean;
  clarification_parent_log_id?: number | null;
  clarification_goal?: string | null;
  tarot_cards: Array<{
    name: string;
    orientation: string;
    position: string;
    position_id?: string | null;
    position_prompt?: string | null;
    meaning: string;
    card_id?: number | null;
    keywords?: string[] | null;
  }>;
  question_assessment?: GuidanceQuestionAssessment | null;
  interpretation?: GuidanceInterpretationContract | null;
};

type GuidanceStructuredResultProps = {
  result: GuidanceReadingResult;
  topicId: string | null;
  showSafetyBanner: boolean;
  clarifyAvailable: boolean;
  onClarifyCard: () => void;
  onNextStep: () => void | Promise<void>;
};

export function GuidanceStructuredResult({
  result,
  topicId,
  showSafetyBanner,
  clarifyAvailable,
  onClarifyCard,
  onNextStep,
}: GuidanceStructuredResultProps) {
  const locale: FlowPracticesChromeLocale = getLocale() === "ru" ? "ru" : "en";
  const gr = useMemo(() => guidanceResultChromeBundle(locale), [locale]);

  const showCompatHint = guidanceResultShowCompatHint(locale, topicId, result.lane, result.question);
  const storyModel = useMemo(() => {
    const base = buildTarotReadingStoryFromGuidance(result, locale, {
      clarifyAvailable,
      onClarify: onClarifyCard,
      showCompatibility: showCompatHint,
    });
    return {
      ...base,
      actions: base.actions.map((action) => {
        if (action.id === "save") {
          return {
            ...action,
            label: result.flow_bridge?.label || result.suggested_route.label || action.label,
            href: undefined,
            onClick: () => void onNextStep(),
          };
        }
        return action;
      }),
    };
  }, [result, locale, clarifyAvailable, onClarifyCard, showCompatHint, onNextStep]);

  return (
    <section style={{ display: "grid", gap: "1rem" }}>
      {result.question_assessment?.suggestion?.trim() || result.question_assessment?.weak_reading_warning?.trim() ? (
        <div
          className="orbit-card todayflow-inset-tight"
          style={{
            border: "1px solid rgba(59, 130, 246, 0.35)",
            background: "rgba(239, 246, 255, 0.5)",
          }}
        >
          <p className="todayflow-eyebrow" style={{ color: "#1d4ed8" }}>
            {gr.guidanceResultAssessmentEyebrow}
          </p>
          {result.question_assessment?.weak_reading_warning?.trim() ? (
            <p className="orbit-body-sm" style={{ margin: "0.45rem 0 0", color: "#1e3a5f", lineHeight: 1.65 }}>
              {result.question_assessment.weak_reading_warning.trim()}
            </p>
          ) : null}
          {result.question_assessment?.suggestion?.trim() ? (
            <p className="orbit-body-sm" style={{ margin: "0.45rem 0 0", color: "#334155", lineHeight: 1.65 }}>
              {result.question_assessment.suggestion.trim()}
            </p>
          ) : null}
        </div>
      ) : null}

      {showSafetyBanner ? (
        <div
          className="orbit-card todayflow-inset-tight"
          style={{
            border: "1px solid rgba(251, 191, 36, 0.45)",
            background: "rgba(254, 243, 199, 0.35)",
          }}
        >
          <p className="orbit-body-sm" style={{ margin: 0, color: "#713f12", lineHeight: 1.65 }}>
            {gr.guidanceResultSafetyBanner}
          </p>
        </div>
      ) : null}

      <TarotReadingStorySurface model={storyModel} locale={locale} />

      {!result.profile_ready ? (
        <p className="orbit-body-xs" style={{ margin: 0, color: "#b45309" }}>
          {gr.guidanceResultProfileIncompleteHint}
        </p>
      ) : null}
    </section>
  );
}

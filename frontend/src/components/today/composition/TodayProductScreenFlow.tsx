"use client";

import type { ReactNode } from "react";
import Link from "next/link";
import { ScreenFlow, ScreenFlowStep, TODAY_SCREEN_FLOW_AXIS } from "@/design-system/primitives/ScreenFlow";
import { joinClass } from "@/design-system/utils/joinClass";
import { TODAY_COMPOSITION_COPY as copy } from "@/components/today/composition/todayCompositionCopy";
import flowStyles from "@/components/today/composition/TodayProductScreenFlow.module.css";
import sfStyles from "@/design-system/primitives/ScreenFlow/ScreenFlow.module.css";
import {
  TodayAttributesFrame,
  TodayCloseFrame,
  TodayEnergyFlowFrame,
  TodayGreetingFrame,
  TodayInsightFrame,
  TodayPracticeFrame,
} from "@/components/today/composition/TodayStoryDeckFrames";
import type { ScreenFlowChangeReason } from "@/design-system/primitives/ScreenFlow";
import type { GlanceDailyFocusModel } from "@/lib/todayDailyFocus";
import type { TodayDayColorGuide } from "@/lib/todayDayColorGuide";
import type { TodayContractV1 } from "@/lib/todayContract";
import type { TapResponseCode } from "@/lib/todayTapWidget";

export type TodayProductScreenFlowProps = {
  dateISO: string;
  dateLabel: string;
  greetingSalutation: string;
  greetingHeadline: string | null;
  themeTitle: string;
  dayTexture?: string | null;
  themeLoading?: boolean;
  dailyFocus?: GlanceDailyFocusModel | null;
  energyLine?: string | null;
  energyCause?: string | null;
  colorGuide?: TodayDayColorGuide | null;
  moveDo?: string | null;
  moveAvoid?: string | null;
  /** Full «Главный сюжет» node for the theme+plot pane (not a short substitute). */
  plotSlot?: ReactNode;
  insightHeroText?: string | null;
  /** Extra insight body (dialogue); plot lives in Attributes now. */
  morningDialogue?: ReactNode;
  showSymbols: boolean;
  symbolsBody: ReactNode;
  showPersonalized: boolean;
  practiceTitle?: string | null;
  practiceMeta?: string | null;
  practiceActionLabel?: string;
  practiceCompleted?: boolean;
  practiceCompleting?: boolean;
  onPracticeAction?: () => void;
  contract: TodayContractV1;
  tapResponse?: TapResponseCode | null;
  onTapRecorded?: (response: TapResponseCode) => void;
  onOpenEvening: () => void;
  activeIndex: number;
  onIndexChange: (index: number, meta: { reason: ScreenFlowChangeReason }) => void;
  embeddedInWebDashboard?: boolean;
  topRowSection?: ReactNode;
  greetingSection?: ReactNode;
};

/**
 * Mockup story deck:
 * Greeting → Energy+Flow → [Symbols] → Attributes → Practice → Insight → Close
 */
export function todayScreenFlowStepCount(opts: {
  showSymbols: boolean;
  showPersonalized: boolean;
}): number {
  if (!opts.showPersonalized) {
    return 1 + (opts.showSymbols ? 1 : 0);
  }
  return 6 + (opts.showSymbols ? 1 : 0);
}

/** @deprecated use todayScreenFlowAttributesIndex */
export function todayScreenFlowReadingIndex(showSymbols: boolean): number {
  return todayScreenFlowAttributesIndex(showSymbols);
}

export function todayScreenFlowSymbolsIndex(): number {
  return 2;
}

export function todayScreenFlowAttributesIndex(showSymbols: boolean): number {
  return showSymbols ? 3 : 2;
}

export function todayScreenFlowPracticeIndex(showSymbols: boolean): number {
  return showSymbols ? 4 : 3;
}

export function todayScreenFlowInsightIndex(showSymbols: boolean): number {
  return showSymbols ? 5 : 4;
}

export function todayScreenFlowCloseIndex(showSymbols: boolean): number {
  return showSymbols ? 6 : 5;
}

export function TodayProductScreenFlow({
  dateISO,
  dateLabel,
  greetingSalutation,
  greetingHeadline,
  themeTitle,
  dayTexture = null,
  themeLoading = false,
  dailyFocus = null,
  energyLine = null,
  energyCause = null,
  colorGuide = null,
  moveDo = null,
  moveAvoid = null,
  plotSlot = null,
  insightHeroText = null,
  morningDialogue = null,
  showSymbols,
  symbolsBody,
  showPersonalized,
  practiceTitle = null,
  practiceMeta = null,
  practiceActionLabel = copy.practiceStart,
  practiceCompleted = false,
  practiceCompleting = false,
  onPracticeAction,
  contract,
  tapResponse = null,
  onTapRecorded,
  onOpenEvening,
  activeIndex,
  onIndexChange,
  embeddedInWebDashboard = false,
  topRowSection = null,
  greetingSection = null,
}: TodayProductScreenFlowProps) {
  const themeText = (dayTexture || "").trim() || null;
  const go = (index: number) => onIndexChange(index, { reason: "select" });

  const energyNextIndex = showSymbols ? todayScreenFlowSymbolsIndex() : todayScreenFlowAttributesIndex(false);
  const energyNextTitle = showSymbols ? copy.storyNext.symbols : copy.storyNext.attributes;
  const energyNextHint = showSymbols ? copy.storyNext.symbolsHint : copy.storyNext.attributesHint;

  return (
    <div data-testid="today-zone-foundation" className={flowStyles.foundation}>
      {!embeddedInWebDashboard ? topRowSection : null}
      {!embeddedInWebDashboard ? greetingSection : null}

      <ScreenFlow
        activeIndex={activeIndex}
        onIndexChange={onIndexChange}
        axis={TODAY_SCREEN_FLOW_AXIS}
        showChrome
        className={joinClass(flowStyles.screenFlowStory, sfStyles.storyBleed)}
        testId="today-screen-flow"
      >
        <ScreenFlowStep id="greeting" label="Приветствие" scrollable={false}>
          <TodayGreetingFrame
            salutation={greetingSalutation}
            dateLabel={dateLabel}
            headline={greetingHeadline}
            loading={themeLoading}
            onStart={() => go(1)}
          />
        </ScreenFlowStep>

        {showPersonalized ? (
          <ScreenFlowStep id="energy_flow" label={copy.pulseLabel} scrollable={false}>
            <TodayEnergyFlowFrame
              energyLine={energyLine}
              energyCause={energyCause}
              dateISO={dateISO}
              prioritize={dailyFocus?.prioritize}
              avoid={dailyFocus?.avoid}
              moveDo={moveDo}
              moveAvoid={moveAvoid}
              onGoNext={() => go(energyNextIndex)}
              nextTitle={energyNextTitle}
              nextHint={energyNextHint}
            />
          </ScreenFlowStep>
        ) : null}

        {showSymbols ? (
          <ScreenFlowStep id="symbols" label={copy.journey.openTitle} scrollable={false}>
            <div
              className={flowStyles.storyFrame}
              data-testid="today-zone-open-day"
              data-story-scroll="pane"
            >
              {symbolsBody}
            </div>
          </ScreenFlowStep>
        ) : null}

        {showPersonalized ? (
          <>
            <ScreenFlowStep id="attributes" label="Опора дня" scrollable={false}>
              <TodayAttributesFrame
                themeLabel={themeTitle || copy.journey.glanceThemeLabel}
                themeText={themeText}
                plotSlot={plotSlot}
                dailyFocus={dailyFocus}
                colorGuide={colorGuide}
                moveDo={moveDo}
                moveAvoid={moveAvoid}
                onGoNext={() => go(todayScreenFlowPracticeIndex(showSymbols))}
              />
            </ScreenFlowStep>

            <ScreenFlowStep id="practice" label="Практика дня" scrollable={false}>
              <TodayPracticeFrame
                title={practiceTitle}
                meta={practiceMeta}
                actionLabel={practiceActionLabel}
                completed={practiceCompleted}
                completing={practiceCompleting}
                onAction={() => onPracticeAction?.()}
                onGoNext={() => go(todayScreenFlowInsightIndex(showSymbols))}
                linkSlot={
                  <p className={flowStyles.practiceLink}>
                    <Link href="/practices" data-testid="today-setup-practices-link">
                      {copy.setupPracticesLink} →
                    </Link>
                  </p>
                }
              />
            </ScreenFlowStep>

            <ScreenFlowStep id="insight" label="Инсайт дня" scrollable={false}>
              <TodayInsightFrame
                heroText={insightHeroText}
                dialogue={morningDialogue}
                onGoNext={() => go(todayScreenFlowCloseIndex(showSymbols))}
              />
            </ScreenFlowStep>

            <ScreenFlowStep id="close" label="Вечер" scrollable={false}>
              <TodayCloseFrame
                contract={contract}
                dateISO={dateISO}
                tapResponse={tapResponse}
                onTapRecorded={onTapRecorded}
                onOpenEvening={onOpenEvening}
              />
            </ScreenFlowStep>
          </>
        ) : null}
      </ScreenFlow>
    </div>
  );
}

"use client";

import type { ComponentProps, ReactNode } from "react";
import { ScreenFlow, ScreenFlowStep, TODAY_SCREEN_FLOW_AXIS } from "@/design-system/primitives/ScreenFlow";
import { TodayActShell } from "@/components/today/composition/TodayActShell";
import { TodayActNav } from "@/components/today/composition/TodayActNav";
import { TodayGlanceAct } from "@/components/today/composition/TodayGlanceAct";
import { TodayPersonalizedProductSection } from "@/components/today/composition/TodayPersonalizedProductSection";
import { TodayScreenBlockStack } from "@/components/today/composition/TodayScreenBlock";
import { TODAY_COMPOSITION_COPY as copy } from "@/components/today/composition/todayCompositionCopy";
import { MotionReveal } from "@/design-system/motion/MotionReveal";
import { MOTION } from "@/design-system/motion/tokens";
import type { ScreenFlowChangeReason } from "@/design-system/primitives/ScreenFlow";

type PersonalizedProps = ComponentProps<typeof TodayPersonalizedProductSection>;

export type TodayProductScreenFlowProps = {
  dateISO: string;
  themeTitle: string;
  themeThesis?: string | null;
  /** Conflict why_arose texture for Glance hero (v3) */
  dayTexture?: string | null;
  themeLoading?: boolean;
  heroSection: ReactNode;
  /** Conflict narrative under photo — Plot Screen 1 (v3) */
  plotNarrativeSection?: ReactNode;
  pulseSection: ReactNode;
  glanceSection: ReactNode;
  morningDialogue: ReactNode;
  dayReadingReady: boolean;
  showSymbols: boolean;
  symbolsBody: ReactNode;
  showPersonalized: boolean;
  personalizedProps: Omit<PersonalizedProps, "asScreenFlowSteps" | "actFilter">;
  activeIndex: number;
  onIndexChange: (index: number, meta: { reason: ScreenFlowChangeReason }) => void;
  onSphereSelect?: (domain: string) => void;
  embeddedInWebDashboard?: boolean;
  topRowSection?: ReactNode;
  greetingSection?: ReactNode;
};

/** Phase 2b indices: Glance → Plot → [Symbols?] → Reading → Move → Response */
export function todayScreenFlowStepCount(opts: {
  showSymbols: boolean;
  showPersonalized: boolean;
}): number {
  return 2 + (opts.showSymbols ? 1 : 0) + (opts.showPersonalized ? 3 : 0);
}

export function todayScreenFlowReadingIndex(showSymbols: boolean): number {
  return showSymbols ? 3 : 2;
}

export function TodayProductScreenFlow({
  dateISO,
  themeTitle,
  themeThesis = null,
  dayTexture = null,
  themeLoading = false,
  heroSection,
  plotNarrativeSection = null,
  pulseSection,
  glanceSection,
  morningDialogue,
  dayReadingReady,
  showSymbols,
  symbolsBody,
  showPersonalized,
  personalizedProps,
  activeIndex,
  onIndexChange,
  onSphereSelect,
  embeddedInWebDashboard = false,
  topRowSection = null,
  greetingSection = null,
}: TodayProductScreenFlowProps) {
  const readingIndex = todayScreenFlowReadingIndex(showSymbols);
  const moveIndex = readingIndex + 1;
  const responseIndex = readingIndex + 2;

  const navItems = [
    { step: 0, label: copy.journey.actNavGlance },
    { step: 1, label: copy.journey.actNavPlot },
    ...(showSymbols ? [{ step: 2, label: copy.journey.actNavSymbols }] : []),
    ...(showPersonalized
      ? [
          { step: readingIndex, label: copy.journey.actNavReading },
          { step: moveIndex, label: copy.journey.actNavMove },
          { step: responseIndex, label: copy.journey.actNavBridge },
        ]
      : []),
  ];

  const teasers = [
    {
      id: "plot",
      label: copy.journey.actNavPlot,
      hook: copy.journey.teaserPlotHook,
      onSelect: () => onIndexChange(1, { reason: "select" as const }),
    },
    ...(showSymbols
      ? [
          {
            id: "symbols",
            label: copy.journey.actNavSymbols,
            hook: copy.journey.teaserSymbolsHook,
            onSelect: () => onIndexChange(2, { reason: "select" as const }),
          },
        ]
      : []),
    ...(showPersonalized
      ? [
          {
            id: "reading",
            label: copy.journey.actNavReading,
            hook: copy.journey.teaserReadingHook,
            onSelect: () => onIndexChange(readingIndex, { reason: "select" as const }),
          },
        ]
      : []),
  ];

  return (
    <div data-testid="today-zone-foundation">
      {!embeddedInWebDashboard ? topRowSection : null}
      {!embeddedInWebDashboard ? greetingSection : null}

      <TodayActNav
        items={navItems}
        activeIndex={activeIndex}
        onSelect={(index) => onIndexChange(index, { reason: "select" })}
      />

      <ScreenFlow
        activeIndex={activeIndex}
        onIndexChange={onIndexChange}
        axis={TODAY_SCREEN_FLOW_AXIS}
        showChrome
        testId="today-screen-flow"
      >
        <ScreenFlowStep id="glance" label={copy.journey.glanceTitle} scrollable>
          <TodayGlanceAct
            dateISO={dateISO}
            title={themeTitle}
            dayTexture={dayTexture}
            thesis={themeThesis}
            themeLoading={themeLoading}
            teasers={teasers}
            screenFlowStep={activeIndex}
            screenFlowStepCount={todayScreenFlowStepCount({
              showSymbols,
              showPersonalized,
            })}
            onSphereSelect={
              showPersonalized
                ? (domain) => {
                    onSphereSelect?.(domain);
                    onIndexChange(readingIndex, { reason: "select" });
                  }
                : undefined
            }
          />
        </ScreenFlowStep>

        <ScreenFlowStep id="plot" label={copy.journey.dayTitle} scrollable>
          <TodayActShell step={1} title={undefined} lead={null} accent="action" motif="today" testId="today-zone-act-plot">
            <TodayScreenBlockStack>
              <MotionReveal>{heroSection}</MotionReveal>
              {plotNarrativeSection ? <MotionReveal delayMs={MOTION.staggerMs}>{plotNarrativeSection}</MotionReveal> : null}
              {dayReadingReady ? (
                <>
                  <MotionReveal delayMs={MOTION.staggerMs * 2}>{pulseSection}</MotionReveal>
                  <MotionReveal delayMs={MOTION.staggerMs * 3}>{glanceSection}</MotionReveal>
                  {morningDialogue}
                </>
              ) : (
                morningDialogue
              )}
            </TodayScreenBlockStack>
          </TodayActShell>
        </ScreenFlowStep>

        {showSymbols ? (
          <ScreenFlowStep id="symbols" label={copy.journey.openTitle} scrollable>
            <TodayActShell step={2} title={undefined} lead={null} accent="sky" testId="today-zone-open-day">
              {symbolsBody}
            </TodayActShell>
          </ScreenFlowStep>
        ) : null}

        {showPersonalized ? (
          <>
            <ScreenFlowStep id="reading" label={copy.journey.actNavReading} scrollable>
              <TodayPersonalizedProductSection
                {...personalizedProps}
                actFilter="reading"
                asScreenFlowSteps
              />
            </ScreenFlowStep>
            <ScreenFlowStep id="move" label={copy.journey.actNavMove} scrollable>
              <TodayPersonalizedProductSection
                {...personalizedProps}
                actFilter="move"
                asScreenFlowSteps
              />
            </ScreenFlowStep>
            <ScreenFlowStep id="response" label={copy.journey.actNavBridge} scrollable>
              <TodayPersonalizedProductSection
                {...personalizedProps}
                actFilter="response"
                asScreenFlowSteps
              />
            </ScreenFlowStep>
          </>
        ) : null}
      </ScreenFlow>
    </div>
  );
}

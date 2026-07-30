"use client";

import type { ComponentProps, ReactNode } from "react";
import { ScreenFlow, ScreenFlowStep } from "@/design-system/primitives/ScreenFlow";
import { TodayActShell } from "@/components/today/composition/TodayActShell";
import { TodayActNav } from "@/components/today/composition/TodayActNav";
import { TodayGlanceAct } from "@/components/today/composition/TodayGlanceAct";
import { TodayPersonalizedProductSection } from "@/components/today/composition/TodayPersonalizedProductSection";
import { TODAY_COMPOSITION_COPY as copy } from "@/components/today/composition/todayCompositionCopy";
import { MotionReveal } from "@/design-system/motion/MotionReveal";
import { MOTION } from "@/design-system/motion/tokens";
import type { ScreenFlowChangeReason } from "@/design-system/primitives/ScreenFlow";

type PersonalizedProps = ComponentProps<typeof TodayPersonalizedProductSection>;

export type TodayProductScreenFlowProps = {
  dateISO: string;
  themeTitle: string;
  themeThesis?: string | null;
  themeLoading?: boolean;
  heroSection: ReactNode;
  pulseSection: ReactNode;
  glanceSection: ReactNode;
  morningDialogue: ReactNode;
  dayReadingReady: boolean;
  showSymbols: boolean;
  symbolsBody: ReactNode;
  showPersonalized: boolean;
  personalizedProps: Omit<PersonalizedProps, "asScreenFlowSteps">;
  activeIndex: number;
  onIndexChange: (index: number, meta: { reason: ScreenFlowChangeReason }) => void;
  embeddedInWebDashboard?: boolean;
  topRowSection?: ReactNode;
  greetingSection?: ReactNode;
};

export function TodayProductScreenFlow({
  dateISO,
  themeTitle,
  themeThesis = null,
  themeLoading = false,
  heroSection,
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
  embeddedInWebDashboard = false,
  topRowSection = null,
  greetingSection = null,
}: TodayProductScreenFlowProps) {
  const navItems = [
    { step: 0, label: copy.journey.actNavGlance },
    { step: 1, label: copy.journey.actNavPlot },
    ...(showSymbols ? [{ step: 2, label: copy.journey.actNavSymbols }] : []),
    ...(showPersonalized
      ? [{ step: 3, label: copy.journey.actNavReading }]
      : []),
  ];

  const teasers = [
    { id: "plot", label: copy.journey.actNavPlot, onSelect: () => onIndexChange(1, { reason: "select" as const }) },
    ...(showSymbols
      ? [{ id: "symbols", label: copy.journey.actNavSymbols, onSelect: () => onIndexChange(2, { reason: "select" as const }) }]
      : []),
    ...(showPersonalized
      ? [
          {
            id: "reading",
            label: copy.journey.actNavReading,
            onSelect: () => onIndexChange(showSymbols ? 3 : 2, { reason: "select" as const }),
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
        axis="x"
        showChrome
        testId="today-screen-flow"
      >
        <ScreenFlowStep id="glance" label={copy.journey.glanceTitle} scrollable>
          <TodayGlanceAct
            dateISO={dateISO}
            title={themeTitle}
            thesis={themeThesis}
            themeLoading={themeLoading}
            teasers={teasers}
          />
        </ScreenFlowStep>

        <ScreenFlowStep id="plot" label={copy.journey.dayTitle} scrollable>
          <TodayActShell step={1} title={undefined} lead={null} accent="action" motif="today" testId="today-zone-act-plot">
            <MotionReveal>{heroSection}</MotionReveal>
            {dayReadingReady ? (
              <>
                <MotionReveal delayMs={MOTION.staggerMs}>{pulseSection}</MotionReveal>
                <MotionReveal delayMs={MOTION.staggerMs * 2}>{glanceSection}</MotionReveal>
                {morningDialogue}
              </>
            ) : (
              morningDialogue
            )}
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
          <ScreenFlowStep id="personal" label={copy.journey.actNavReading} scrollable>
            <TodayPersonalizedProductSection {...personalizedProps} />
          </ScreenFlowStep>
        ) : null}
      </ScreenFlow>
    </div>
  );
}

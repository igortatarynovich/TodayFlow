"use client";

import type { ComponentProps, ReactNode } from "react";
import { ScreenFlow, ScreenFlowStep, TODAY_SCREEN_FLOW_AXIS } from "@/design-system/primitives/ScreenFlow";
import { TodayGlanceAct } from "@/components/today/composition/TodayGlanceAct";
import { TodayPersonalizedProductSection } from "@/components/today/composition/TodayPersonalizedProductSection";
import { TodayScreenBlockStack } from "@/components/today/composition/TodayScreenBlock";
import { TODAY_COMPOSITION_COPY as copy } from "@/components/today/composition/todayCompositionCopy";
import { MotionReveal } from "@/design-system/motion/MotionReveal";
import { MOTION } from "@/design-system/motion/tokens";
import type { ScreenFlowChangeReason } from "@/design-system/primitives/ScreenFlow";
import type { GlanceSphereChip } from "@/lib/todayGlanceSphereChips";

type PersonalizedProps = ComponentProps<typeof TodayPersonalizedProductSection>;

export type TodayProductScreenFlowProps = {
  dateISO: string;
  themeTitle: string;
  themeThesis?: string | null;
  /** Conflict why_arose texture for Glance hero (v3) */
  dayTexture?: string | null;
  themeLoading?: boolean;
  /** Glance ≤2 domain chips from Reading magnitude set */
  sphereChips?: GlanceSphereChip[];
  /** Pulse text for Glance «Энергия дня» */
  energyLine?: string | null;
  heroSection: ReactNode;
  /** Conflict narrative under photo — Plot Screen 1 (v3) */
  plotNarrativeSection?: ReactNode;
  /** @deprecated Pulse moved to Glance `energyLine`; kept for call-site compat. */
  pulseSection?: ReactNode;
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
  sphereChips = [],
  energyLine = null,
  heroSection,
  plotNarrativeSection = null,
  pulseSection: _pulseSection = null,
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
            sphereChips={sphereChips}
            energyLine={energyLine}
            teasers={teasers}
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
          <TodayScreenBlockStack testId="today-zone-act-plot">
            <MotionReveal>{heroSection}</MotionReveal>
            {plotNarrativeSection ? <MotionReveal delayMs={MOTION.staggerMs}>{plotNarrativeSection}</MotionReveal> : null}
            {dayReadingReady ? (
              <>
                <MotionReveal delayMs={MOTION.staggerMs * 2}>{glanceSection}</MotionReveal>
                {morningDialogue}
              </>
            ) : (
              morningDialogue
            )}
          </TodayScreenBlockStack>
        </ScreenFlowStep>

        {showSymbols ? (
          <ScreenFlowStep id="symbols" label={copy.journey.openTitle} scrollable>
            <div data-testid="today-zone-open-day">{symbolsBody}</div>
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

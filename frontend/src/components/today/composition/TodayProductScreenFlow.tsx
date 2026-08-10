"use client";

import { useEffect, type ReactNode } from "react";
import Link from "next/link";
import { ScreenFlow, ScreenFlowStep, TODAY_SCREEN_FLOW_AXIS } from "@/design-system/primitives/ScreenFlow";
import { joinClass } from "@/design-system/utils/joinClass";
import { TODAY_COMPOSITION_COPY as copy } from "@/components/today/composition/todayCompositionCopy";
import flowStyles from "@/components/today/composition/TodayProductScreenFlow.module.css";
import sfStyles from "@/design-system/primitives/ScreenFlow/ScreenFlow.module.css";
import {
  StoryNextAnchor,
  TodayCloseFrame,
  TodayEnergyFlowFrame,
  TodayGreetingFrame,
  TodayPracticeFrame,
} from "@/components/today/composition/TodayStoryDeckFrames";
import type { ScreenFlowChangeReason } from "@/design-system/primitives/ScreenFlow";
import type { GlanceDailyFocusModel } from "@/lib/todayDailyFocus";
import type { TodayDayColorGuide } from "@/lib/todayDayColorGuide";
import type { TodayContractV1 } from "@/lib/todayContract";
import type { TapResponseCode } from "@/lib/todayTapWidget";
import { fetchDayFacts } from "@/lib/todayDayFacts";
import type { HandoffWelcomeGlass } from "@/lib/todayHandoffWelcome";

/**
 * Handoff presentation v3.3 — Architecture A.
 * Welcome → Priority → Promise → Make yours → Поток дня →
 * [Число → Карта] → Цвет → Фокус → Практика → Recap → Close
 *
 * Content houses (Plot/Reading/…) stay in SCENARIO_V3 jobs; this file is frame cut only.
 */

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
  /** @deprecated plot lives in insight/recap slots under handoff */
  plotSlot?: ReactNode;
  insightHeroText?: string | null;
  /** Priority / dialogue slot (step «Приоритет»). */
  morningDialogue?: ReactNode;
  showSymbols: boolean;
  /** @deprecated split into numberBody / cardBody */
  symbolsBody?: ReactNode;
  numberBody?: ReactNode;
  cardBody?: ReactNode;
  showPersonalized: boolean;
  practiceTitle?: string | null;
  practiceMeta?: string | null;
  practiceActionLabel?: string;
  practiceCompleted?: boolean;
  practiceCompleting?: boolean;
  onPracticeAction?: () => void;
  /** Prefer gift practice UI when provided. */
  practiceBody?: ReactNode;
  promiseBody?: ReactNode;
  makeYoursBody?: ReactNode;
  focusBody?: ReactNode;
  colorBody?: ReactNode;
  recapBody?: ReactNode;
  welcomeGlass?: HandoffWelcomeGlass | null;
  contract: TodayContractV1;
  tapResponse?: TapResponseCode | null;
  onTapRecorded?: (response: TapResponseCode) => void;
  onOpenEvening: () => void;
  dayPromise?: string | null;
  onCloseOutcome?: (outcome: "done" | "partial" | "not_done") => void;
  activeIndex: number;
  onIndexChange: (index: number, meta: { reason: ScreenFlowChangeReason }) => void;
  embeddedInWebDashboard?: boolean;
  topRowSection?: ReactNode;
  greetingSection?: ReactNode;
};

export type TodayHandoffIndices = {
  welcome: number;
  priority: number;
  promise: number;
  makeYours: number;
  dayFlow: number;
  number: number;
  card: number;
  color: number;
  focus: number;
  practice: number;
  recap: number;
  close: number;
};

export function todayHandoffIndices(showSymbols: boolean): TodayHandoffIndices {
  if (showSymbols) {
    return {
      welcome: 0,
      priority: 1,
      promise: 2,
      makeYours: 3,
      dayFlow: 4,
      number: 5,
      card: 6,
      color: 7,
      focus: 8,
      practice: 9,
      recap: 10,
      close: 11,
    };
  }
  return {
    welcome: 0,
    priority: 1,
    promise: 2,
    makeYours: 3,
    dayFlow: 4,
    number: -1,
    card: -1,
    color: 5,
    focus: 6,
    practice: 7,
    recap: 8,
    close: 9,
  };
}

export function todayScreenFlowStepCount(opts: {
  showSymbols: boolean;
  showPersonalized: boolean;
}): number {
  if (!opts.showPersonalized) return 1;
  return opts.showSymbols ? 12 : 10;
}

/** Deepen / Reading target → Фокус дня */
export function todayScreenFlowReadingIndex(showSymbols: boolean): number {
  return todayHandoffIndices(showSymbols).focus;
}

export function todayScreenFlowSymbolsIndex(): number {
  return todayHandoffIndices(true).number;
}

/** After symbols → цвет */
export function todayScreenFlowAttributesIndex(showSymbols: boolean): number {
  return todayHandoffIndices(showSymbols).color;
}

export function todayScreenFlowPracticeIndex(showSymbols: boolean): number {
  return todayHandoffIndices(showSymbols).practice;
}

export function todayScreenFlowInsightIndex(showSymbols: boolean): number {
  return todayHandoffIndices(showSymbols).recap;
}

export function todayScreenFlowCloseIndex(showSymbols: boolean): number {
  return todayHandoffIndices(showSymbols).close;
}

function SlotStep({
  testId,
  eyebrow,
  title,
  children,
  nextTitle,
  nextHint,
  onNext,
}: {
  testId: string;
  eyebrow?: string;
  title?: string;
  children: ReactNode;
  nextTitle: string;
  nextHint?: string;
  onNext: () => void;
}) {
  return (
    <div className={flowStyles.storyFrame} data-testid={testId} data-story-scroll="pane">
      <div className={flowStyles.slotStack}>
        {eyebrow ? <p className={flowStyles.slotEyebrow}>{eyebrow}</p> : null}
        {title ? <h2 className={flowStyles.slotTitle}>{title}</h2> : null}
        <div className={flowStyles.slotBody}>{children}</div>
        <StoryNextAnchor title={nextTitle} hint={nextHint} onNext={onNext} />
      </div>
    </div>
  );
}

export function TodayProductScreenFlow({
  dateISO,
  dateLabel,
  greetingSalutation,
  greetingHeadline,
  themeLoading = false,
  energyLine = null,
  energyCause = null,
  showSymbols,
  symbolsBody = null,
  numberBody = null,
  cardBody = null,
  showPersonalized,
  practiceTitle = null,
  practiceMeta = null,
  practiceActionLabel = copy.practiceStart,
  practiceCompleted = false,
  practiceCompleting = false,
  onPracticeAction,
  practiceBody = null,
  promiseBody = null,
  makeYoursBody = null,
  focusBody = null,
  colorBody = null,
  recapBody = null,
  morningDialogue = null,
  welcomeGlass = null,
  contract,
  tapResponse = null,
  onTapRecorded,
  onOpenEvening,
  dayPromise = null,
  onCloseOutcome,
  activeIndex,
  onIndexChange,
  embeddedInWebDashboard = false,
  topRowSection = null,
  greetingSection = null,
}: TodayProductScreenFlowProps) {
  const go = (index: number) => onIndexChange(index, { reason: "select" });
  const idx = todayHandoffIndices(showSymbols);
  const showChrome = activeIndex > 0;
  // Handoff: Welcome excluded from dots; clusters = setup · story · end.
  // With symbols: 3 + 6 + 2; without number/card: 3 + 4 + 2.
  const handoffDotClusters = showSymbols ? [3, 6, 2] : [3, 4, 2];

  useEffect(() => {
    if (!dateISO) return;
    void fetchDayFacts(dateISO).catch(() => {
      /* pane owns failure UI */
    });
  }, [dateISO]);

  const numberSlot = numberBody ?? (showSymbols ? symbolsBody : null);
  const cardSlot = cardBody;

  return (
    <div data-testid="today-zone-foundation" className={flowStyles.foundation}>
      {!embeddedInWebDashboard ? topRowSection : null}
      {!embeddedInWebDashboard ? greetingSection : null}

      <ScreenFlow
        activeIndex={activeIndex}
        onIndexChange={onIndexChange}
        axis={TODAY_SCREEN_FLOW_AXIS}
        showChrome={showChrome}
        showFrameArrows={showChrome}
        dotStartIndex={1}
        dotClusters={showPersonalized ? handoffDotClusters : undefined}
        className={joinClass(flowStyles.screenFlowStory, sfStyles.storyBleed)}
        testId="today-screen-flow"
      >
        <ScreenFlowStep id="welcome" label="Приветствие" scrollable={false}>
          <TodayGreetingFrame
            salutation={greetingSalutation}
            dateLabel={dateLabel}
            headline={greetingHeadline}
            loading={themeLoading}
            moodPills={welcomeGlass?.moodPills}
            reasonLine={welcomeGlass?.reasonLine}
            activityTags={welcomeGlass?.activityTags}
            startHint={copy.storyNext.formDay}
            onStart={() => go(showPersonalized ? idx.priority : 0)}
          />
        </ScreenFlowStep>

        {showPersonalized ? (
          <>
            <ScreenFlowStep id="priority" label={copy.storyNext.priority} scrollable={false}>
              <SlotStep
                testId="today-frame-priority"
                eyebrow={copy.storyNext.priority}
                title={morningDialogue ? "Что сейчас ближе?" : undefined}
                nextTitle={copy.storyNext.promise}
                onNext={() => go(idx.promise)}
              >
                {morningDialogue}
              </SlotStep>
            </ScreenFlowStep>

            <ScreenFlowStep id="promise" label={copy.storyNext.promise} scrollable>
              <SlotStep
                testId="today-frame-promise"
                eyebrow={copy.storyNext.promise}
                title={copy.promiseTitle}
                nextTitle={copy.storyNext.makeYours}
                onNext={() => go(idx.makeYours)}
              >
                {promiseBody}
              </SlotStep>
            </ScreenFlowStep>

            <ScreenFlowStep id="make_yours" label={copy.storyNext.makeYours} scrollable>
              <SlotStep
                testId="today-frame-make-yours"
                eyebrow={copy.journey.moveTitle}
                title={copy.storyNext.makeYours}
                nextTitle={copy.storyNext.dayFlow}
                onNext={() => go(idx.dayFlow)}
              >
                {makeYoursBody}
              </SlotStep>
            </ScreenFlowStep>

            <ScreenFlowStep id="day_flow" label={copy.storyNext.dayFlow} scrollable={false}>
              <TodayEnergyFlowFrame
                energyLine={energyLine}
                energyCause={energyCause}
                dateISO={dateISO}
                active={activeIndex === idx.dayFlow}
                onGoNext={() => go(showSymbols ? idx.number : idx.color)}
                nextTitle={showSymbols ? copy.storyNext.number : copy.storyNext.color}
                nextHint={showSymbols ? copy.storyNext.numberHint : copy.storyNext.colorHint}
              />
            </ScreenFlowStep>

            {showSymbols ? (
              <>
                <ScreenFlowStep id="number" label={copy.storyNext.number} scrollable={false}>
                  <div
                    className={`${flowStyles.storyFrame} ${flowStyles.ritualFrame}`}
                    data-testid="today-frame-number"
                    data-story-scroll="pane"
                  >
                    {numberSlot}
                    <div className={flowStyles.slotFooter}>
                      <StoryNextAnchor
                        title={copy.storyNext.card}
                        onNext={() => go(idx.card)}
                      />
                    </div>
                  </div>
                </ScreenFlowStep>

                <ScreenFlowStep id="card" label={copy.storyNext.card} scrollable={false}>
                  <div
                    className={`${flowStyles.storyFrame} ${flowStyles.ritualFrame}`}
                    data-testid="today-frame-card"
                    data-story-scroll="pane"
                  >
                    {cardSlot}
                    <div className={flowStyles.slotFooter}>
                      <StoryNextAnchor
                        title={copy.storyNext.color}
                        onNext={() => go(idx.color)}
                      />
                    </div>
                  </div>
                </ScreenFlowStep>
              </>
            ) : null}

            <ScreenFlowStep id="color" label={copy.storyNext.color} scrollable={false}>
              <SlotStep
                testId="today-frame-color"
                eyebrow={copy.storyNext.color}
                nextTitle={copy.storyNext.focus}
                nextHint={copy.storyNext.focusHint}
                onNext={() => go(idx.focus)}
              >
                {colorBody}
              </SlotStep>
            </ScreenFlowStep>

            <ScreenFlowStep id="focus" label={copy.storyNext.focus} scrollable>
              <SlotStep
                testId="today-frame-focus"
                eyebrow={copy.storyNext.focus}
                nextTitle={copy.storyNext.practice}
                onNext={() => go(idx.practice)}
              >
                {focusBody}
              </SlotStep>
            </ScreenFlowStep>

            <ScreenFlowStep id="practice" label={copy.storyNext.practice} scrollable={false}>
              {practiceBody ? (
                <SlotStep
                  testId="today-frame-practice-gift"
                  eyebrow={copy.storyNext.practice}
                  nextTitle={copy.storyNext.recap}
                  nextHint={copy.storyNext.recapHint}
                  onNext={() => go(idx.recap)}
                >
                  {practiceBody}
                </SlotStep>
              ) : (
                <TodayPracticeFrame
                  title={practiceTitle}
                  meta={practiceMeta}
                  actionLabel={practiceActionLabel}
                  completed={practiceCompleted}
                  completing={practiceCompleting}
                  onAction={() => onPracticeAction?.()}
                  onGoNext={() => go(idx.recap)}
                  linkSlot={
                    <p className={flowStyles.practiceLink}>
                      <Link href="/practices" data-testid="today-setup-practices-link">
                        {copy.setupPracticesLink} →
                      </Link>
                    </p>
                  }
                />
              )}
            </ScreenFlowStep>

            <ScreenFlowStep id="recap" label={copy.storyNext.recap} scrollable={false}>
              <SlotStep
                testId="today-frame-recap"
                eyebrow={copy.storyNext.recap}
                title=""
                nextTitle={copy.storyNext.close}
                nextHint={copy.storyNext.closeHint}
                onNext={() => go(idx.close)}
              >
                {recapBody}
              </SlotStep>
            </ScreenFlowStep>

            <ScreenFlowStep id="close" label={copy.storyNext.close} scrollable={false}>
              <TodayCloseFrame
                contract={contract}
                dateISO={dateISO}
                tapResponse={tapResponse}
                onTapRecorded={onTapRecorded}
                onOpenEvening={onOpenEvening}
                dayPromise={dayPromise}
                onPickOutcome={onCloseOutcome}
              />
            </ScreenFlowStep>
          </>
        ) : null}
      </ScreenFlow>
    </div>
  );
}

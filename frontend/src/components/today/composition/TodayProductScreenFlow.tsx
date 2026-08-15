"use client";

import { useEffect, type ReactNode } from "react";
import { ScreenFlow, ScreenFlowStep, TODAY_SCREEN_FLOW_AXIS } from "@/design-system/primitives/ScreenFlow";
import { DsCaption, DsEyebrow, DsHeadline } from "@/design-system";
import { joinClass } from "@/design-system/utils/joinClass";
import layout from "@/design-system/compositions/dsCompositions.module.css";
import { TODAY_COMPOSITION_COPY as copy } from "@/components/today/composition/todayCompositionCopy";
import sfStyles from "@/design-system/primitives/ScreenFlow/ScreenFlow.module.css";
import { StoryNextAnchor } from "@/components/today/composition/TodayStoryDeckFrames";
import type { ScreenFlowChangeReason } from "@/design-system/primitives/ScreenFlow";
import type { TodayContractV1 } from "@/lib/todayContract";
import type { TapResponseCode } from "@/lib/todayTapWidget";
import { fetchDayFacts } from "@/lib/todayDayFacts";

/**
 * Today product cycle — four surfaces.
 * today → ritual → my_day → evening
 * Canon: docs/today/TODAY_PRODUCT_FLOW_V1.md
 */

export type TodayScreenFlowLayout = {
  showSymbols: boolean;
  showMyDay: boolean;
};

export type TodaySixBlockIndices = {
  today: number;
  ritual: number;
  myDay: number;
  evening: number;
  day: number;
  /** Removed — Global TODAY has no orientation frame */
  orientation: number;
  rituals: number;
  instruction: number;
  color: number;
  tasks: number;
  loop: number;
  /** @deprecated aliases → four-screen ids */
  welcome: number;
  number: number;
  card: number;
  focus: number;
  practice: number;
  close: number;
  priority: number;
  promise: number;
  makeYours: number;
  dayFlow: number;
  recap: number;
};

/** @deprecated name — use TodaySixBlockIndices */
export type TodayHandoffIndices = TodaySixBlockIndices;

export type TodayProductScreenFlowProps = {
  dateISO: string;
  dateLabel: string;
  showSymbols: boolean;
  showMyDay?: boolean;
  /** @deprecated ignored — first-today uses ConversationThread, not a 1-step collapse */
  showPersonalized?: boolean;
  dayBody?: ReactNode;
  /** @deprecated orientation folded; timeline lives on my_day */
  orientationBody?: ReactNode;
  numberBody?: ReactNode;
  cardBody?: ReactNode;
  /** @deprecated */
  symbolsBody?: ReactNode;
  myDayBody?: ReactNode;
  instructionBody?: ReactNode;
  /** @deprecated alias */
  focusBody?: ReactNode;
  colorBody?: ReactNode;
  tasksBody?: ReactNode;
  practiceBody?: ReactNode;
  practiceTitle?: string | null;
  practiceMeta?: string | null;
  practiceActionLabel?: string;
  practiceCompleted?: boolean;
  practiceCompleting?: boolean;
  onPracticeAction?: () => void;
  eveningBody?: ReactNode;
  promiseBody?: ReactNode;
  /** Ritual A→B: number hidden until the card is open */
  ritualCardOpen?: boolean;
  ritualNumberOpen?: boolean;
  /** Ritual C: compact card + number results (replaces pick UIs) */
  ritualResultBody?: ReactNode;
  loopOwnsClose?: boolean;
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

export function todayHandoffIndices(layout: TodayScreenFlowLayout): TodaySixBlockIndices {
  const showSymbols = Boolean(layout.showSymbols);
  const showMyDay = Boolean(layout.showMyDay);
  let n = 0;
  const today = n++;
  const ritual = showSymbols ? n++ : -1;
  const myDay = showMyDay ? n++ : -1;
  const evening = n++;
  return {
    today,
    ritual,
    myDay,
    evening,
    day: today,
    orientation: -1,
    rituals: ritual,
    instruction: myDay,
    color: myDay,
    tasks: myDay,
    loop: evening,
    welcome: today,
    number: ritual,
    card: ritual,
    focus: myDay,
    practice: myDay,
    close: evening,
    priority: -1,
    promise: evening,
    makeYours: myDay,
    dayFlow: today,
    recap: -1,
  };
}

export function todayScreenFlowStepCount(opts: {
  showSymbols: boolean;
  showMyDay?: boolean;
  /** @deprecated ignored */
  showPersonalized?: boolean;
}): number {
  return 1 + (opts.showSymbols ? 1 : 0) + (opts.showMyDay ? 1 : 0) + 1;
}

function layoutFromSymbols(showSymbols: boolean, showMyDay = true): TodayScreenFlowLayout {
  return { showSymbols, showMyDay };
}

export function todayScreenFlowReadingIndex(showSymbols: boolean, showMyDay = true): number {
  return todayHandoffIndices(layoutFromSymbols(showSymbols, showMyDay)).instruction;
}

export function todayScreenFlowSymbolsIndex(): number {
  return todayHandoffIndices({ showSymbols: true, showMyDay: false }).rituals;
}

export function todayScreenFlowAttributesIndex(showSymbols: boolean, showMyDay = true): number {
  return todayHandoffIndices(layoutFromSymbols(showSymbols, showMyDay)).color;
}

export function todayScreenFlowPracticeIndex(showSymbols: boolean, showMyDay = true): number {
  return todayHandoffIndices(layoutFromSymbols(showSymbols, showMyDay)).tasks;
}

export function todayScreenFlowInsightIndex(showSymbols: boolean, showMyDay = true): number {
  return todayHandoffIndices(layoutFromSymbols(showSymbols, showMyDay)).loop;
}

export function todayScreenFlowCloseIndex(showSymbols: boolean, showMyDay = true): number {
  return todayHandoffIndices(layoutFromSymbols(showSymbols, showMyDay)).loop;
}

function SlotStep({
  testId,
  eyebrow,
  title,
  children,
  nextTitle,
  nextHint,
  onNext,
  wide = false,
  hideNext = false,
  compactTop = false,
}: {
  testId: string;
  eyebrow?: string;
  title?: string;
  children: ReactNode;
  nextTitle: string;
  nextHint?: string;
  onNext: () => void;
  wide?: boolean;
  hideNext?: boolean;
  compactTop?: boolean;
}) {
  return (
    <div className={sfStyles.storyFrame} data-testid={testId} data-story-scroll="pane">
      <div
        className={joinClass(
          sfStyles.slotStack,
          wide ? sfStyles.slotStackWide : null,
          compactTop ? sfStyles.slotStackCompactTop : null,
        )}
      >
        {eyebrow ? <DsEyebrow>{eyebrow}</DsEyebrow> : null}
        {title ? <DsHeadline as="h2">{title}</DsHeadline> : null}
        <div className={sfStyles.slotBody}>{children}</div>
        {hideNext ? null : (
          <StoryNextAnchor title={nextTitle} hint={nextHint} onNext={onNext} />
        )}
      </div>
    </div>
  );
}

export function TodayProductScreenFlow({
  dateISO,
  showSymbols,
  showMyDay = false,
  symbolsBody = null,
  numberBody = null,
  cardBody = null,
  dayBody = null,
  myDayBody = null,
  instructionBody = null,
  focusBody = null,
  colorBody = null,
  tasksBody = null,
  practiceBody = null,
  eveningBody = null,
  promiseBody = null,
  ritualCardOpen = false,
  ritualNumberOpen = false,
  ritualResultBody = null,
  activeIndex,
  onIndexChange,
  embeddedInWebDashboard = false,
  topRowSection = null,
  greetingSection = null,
}: TodayProductScreenFlowProps) {
  const go = (index: number) => onIndexChange(index, { reason: "select" });
  const flowLayout = { showSymbols, showMyDay };
  const idx = todayHandoffIndices(flowLayout);
  const showChrome = activeIndex > 0;
  const extraDots = (showSymbols ? 1 : 0) + (showMyDay ? 1 : 0) + 1;
  const dotClusters = Array.from({ length: extraDots }, () => 1);
  const instruction = instructionBody ?? focusBody;
  const numberSlot = numberBody ?? (showSymbols ? symbolsBody : null);
  const cardSlot = cardBody;
  const composedMyDay =
    myDayBody ??
    (
      <>
        {instruction}
        {colorBody}
        {tasksBody ?? practiceBody}
      </>
    );
  const eveningSlot = eveningBody ?? promiseBody;

  const afterToday = showSymbols ? idx.ritual : showMyDay ? idx.myDay : idx.evening;
  const afterRitual = showMyDay ? idx.myDay : idx.evening;
  const afterMyDay = idx.evening;
  const ritualComplete = Boolean(ritualCardOpen && ritualNumberOpen && ritualResultBody);
  const ritualState = ritualNumberOpen ? "open" : ritualCardOpen ? "card" : "closed";
  const ritualEyebrow = ritualNumberOpen
    ? copy.ritualDoneEyebrow
    : ritualCardOpen
      ? copy.ritualStepNumber
      : copy.ritualStepCard;

  useEffect(() => {
    if (!dateISO) return;
    void fetchDayFacts(dateISO).catch(() => {
      /* pane owns failure UI */
    });
  }, [dateISO]);

  return (
    <div data-testid="today-zone-foundation" className={sfStyles.flowFoundation}>
      {!embeddedInWebDashboard ? topRowSection : null}
      {!embeddedInWebDashboard ? greetingSection : null}

      <ScreenFlow
        activeIndex={activeIndex}
        onIndexChange={onIndexChange}
        axis={TODAY_SCREEN_FLOW_AXIS}
        showChrome={showChrome}
        showFrameArrows={showChrome}
        dotStartIndex={1}
        dotClusters={dotClusters}
        className={sfStyles.storyBleed}
        testId="today-screen-flow"
      >
        <ScreenFlowStep id="today" label={copy.storyNext.day} scrollable>
          <SlotStep
            testId="today-frame-day"
            wide
            compactTop
            hideNext
            nextTitle={
              showSymbols
                ? copy.storyNext.rituals
                : showMyDay
                  ? copy.storyNext.myDay
                  : copy.storyNext.evening
            }
            nextHint={
              showSymbols
                ? copy.storyNext.ritualsHint
                : showMyDay
                  ? copy.storyNext.myDayHint
                  : copy.storyNext.eveningHint
            }
            onNext={() => go(afterToday)}
          >
            {dayBody}
          </SlotStep>
        </ScreenFlowStep>

        {showSymbols ? (
          <ScreenFlowStep id="ritual" label={copy.storyNext.rituals} scrollable>
            <div
              className={joinClass(sfStyles.storyFrame, sfStyles.ritualFrame)}
              data-testid="today-frame-rituals"
              data-ritual-state={ritualState}
              data-story-scroll="pane"
            >
              <div className={sfStyles.slotStack}>
                <DsEyebrow>{copy.storyNext.rituals}</DsEyebrow>
                <DsCaption>{ritualEyebrow}</DsCaption>
                <div
                  className={
                    ritualComplete
                      ? undefined
                      : ritualCardOpen && ritualNumberOpen
                        ? layout.pairGrid
                        : layout.stack
                  }
                >
                  {ritualComplete ? (
                    ritualResultBody
                  ) : (
                    <>
                      <div data-testid="today-frame-card">{cardSlot}</div>
                      {ritualCardOpen ? (
                        <div data-testid="today-frame-number">{numberSlot}</div>
                      ) : null}
                    </>
                  )}
                </div>
                <StoryNextAnchor
                  title={showMyDay ? copy.storyNext.myDay : copy.storyNext.evening}
                  hint={showMyDay ? copy.storyNext.myDayHint : copy.storyNext.eveningHint}
                  onNext={() => go(afterRitual)}
                />
              </div>
            </div>
          </ScreenFlowStep>
        ) : null}

        {showMyDay ? (
          <ScreenFlowStep id="my_day" label={copy.storyNext.myDay} scrollable>
            <SlotStep
              testId="today-frame-my-day"
              eyebrow={copy.storyNext.myDay}
              nextTitle={copy.storyNext.evening}
              nextHint={copy.storyNext.eveningHint}
              onNext={() => go(afterMyDay)}
            >
              {composedMyDay}
            </SlotStep>
          </ScreenFlowStep>
        ) : null}

        <ScreenFlowStep id="evening" label={copy.storyNext.evening} scrollable>
          <div className={sfStyles.storyFrame} data-testid="today-frame-evening" data-story-scroll="pane">
            <div className={sfStyles.slotStack}>
              <DsEyebrow>{copy.storyNext.evening}</DsEyebrow>
              <DsHeadline as="h2">{copy.eveningGratitudeTitle}</DsHeadline>
              <div className={sfStyles.slotBody}>{eveningSlot}</div>
            </div>
          </div>
        </ScreenFlowStep>
      </ScreenFlow>
    </div>
  );
}
